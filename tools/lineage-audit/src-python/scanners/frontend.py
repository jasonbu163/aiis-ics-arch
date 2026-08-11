"""
File Path: /tools/lineage-audit/src-python/scanners/frontend.py
Description: Frontend static scanners for routes, API clients, component links and mock signals.
Main Features:
    - Scans Vue routes and API client definitions.
    - Scans frontend source API usage and local mock/static signals.
"""
from __future__ import annotations

import re
from pathlib import Path

from audit.common import normalize_path, read_text, rel
from audit.constants import STATIC_DATA_PATTERNS
from audit.models import ComponentLink, FrontendApi, FrontendRoute, FrontendUsage, MockFinding


PRODUCTION_SOURCE_SUFFIXES = (".vue", ".js", ".mjs", ".ts")
EXCLUDED_SOURCE_PARTS = {"__tests__", "fixture", "fixtures", "mock", "mocks"}


def is_production_source(path: Path) -> bool:
    """Keep static inventories scoped to production Vue source candidates."""
    if path.suffix not in PRODUCTION_SOURCE_SUFFIXES:
        return False
    if any(part.lower() in EXCLUDED_SOURCE_PARTS for part in path.parts):
        return False
    name = path.name.lower()
    return not (".test." in name or ".spec." in name or name.startswith("mock."))


def collect_production_files(frontend_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    return sorted({
        path
        for pattern in patterns
        for path in frontend_root.glob(pattern)
        if is_production_source(path)
    })


def list_frontend_source_files(frontend_root: Path) -> list[Path]:
    roots = (
        "app/**/views/**/*",
        "app/**/components/**/*",
        "pages/**/*",
        "layouts/**/*",
        "views/**/*",
        "components/**/*",
        "store/**/*",
    )
    return collect_production_files(frontend_root, roots)


def list_frontend_api_files(frontend_root: Path) -> list[Path]:
    return [
        path
        for path in collect_production_files(frontend_root, ("api/**/*", "app/**/api/**/*"))
        if path.suffix in {".js", ".mjs", ".ts"}
    ]


def frontend_api_module(path: Path, frontend_root: Path) -> str:
    parts = path.relative_to(frontend_root).parts
    if len(parts) >= 4 and parts[0] == "app" and parts[2] == "api":
        return parts[1]
    return path.stem

def resolve_frontend_path(raw_expr: str, constants: dict[str, str]) -> tuple[str, str]:
    expr = raw_expr.strip()
    confidence = "confirmed"
    if "," in expr:
        expr = expr.split(",", 1)[0].strip()
    if expr.startswith(("'", '"')) and expr.endswith(("'", '"')):
        return normalize_path(expr[1:-1]), confidence
    if expr.startswith("`") and expr.endswith("`"):
        template = expr[1:-1]

        def replace_var(match: re.Match[str]) -> str:
            name = match.group(1).strip()
            if name in constants:
                return constants[name]
            return "{param}"

        return normalize_path(re.sub(r"\$\{([^}]+)\}", replace_var, template)), confidence
    if expr in constants:
        return normalize_path(constants[expr]), confidence
    return normalize_path(expr), "manual_review"


def parse_frontend_api_file(path: Path, frontend_root: Path) -> list[FrontendApi]:
    text = read_text(path)
    module = frontend_api_module(path, frontend_root)
    constants = {
        match.group(1): match.group(2)
        for match in re.finditer(r"\b(?:const|let|var)\s+(\w+)\s*=\s*['\"]([^'\"]+)['\"]", text)
    }
    apis: list[FrontendApi] = []

    export_patterns = [
        re.compile(
            r"export\s+(?:async\s+)?function\s+(\w+)(?:\s*<[^>{}\n]+>)?\s*\([^)]*\)\s*(?::\s*[^={\n]+)?\s*\{",
            re.MULTILINE,
        ),
        re.compile(
            r"export\s+const\s+(\w+)(?:\s*:\s*[^\n]+?)?\s*=\s*(?:async\s*)?(?:<[^>{}\n]+>\s*)?\([^)]*\)\s*(?::\s*[^=;\n]+)?\s*=>\s*\{?",
            re.MULTILINE,
        ),
    ]
    matches: list[tuple[int, str]] = []
    for pattern in export_patterns:
        for match in pattern.finditer(text):
            matches.append((match.start(), match.group(1)))
    matches.sort()

    for index, (start, function_name) in enumerate(matches):
        end = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        body = text[start:end]
        request_match = re.search(
            r"request\.(get|post|put|delete|patch)(?:\s*<[^()\n]+>)?\s*\(\s*([^)\n]+)",
            body,
            re.IGNORECASE,
        )
        if not request_match:
            continue
        method = request_match.group(1).upper()
        raw_expr = request_match.group(2).strip()
        path_template, confidence = resolve_frontend_path(raw_expr, constants)
        apis.append(
            FrontendApi(
                module=module,
                function=function_name,
                method=method,
                path=path_template,
                raw_path_expr=raw_expr,
                api_file=rel(path),
                confidence=confidence,
            )
        )
    return apis


def parse_frontend_routes(router_path: Path) -> list[FrontendRoute]:
    text = read_text(router_path)
    frontend_root = router_path.parent.parent
    routes: list[FrontendRoute] = []

    def flush(current: dict[str, str]) -> None:
        component = current.get("component", "")
        if not component:
            return
        route_path = current.get("path", "")
        if route_path != "/login" and not route_path.startswith("/"):
            route_path = "/" + route_path
        routes.append(
            FrontendRoute(
                route_path=route_path,
                route_name=current.get("name", ""),
                component_path=rel(frontend_root / component),
                permission=current.get("permission", ""),
                title_key=current.get("titleKey", ""),
            )
        )

    current: dict[str, str] = {}
    for line in text.splitlines():
        path_match = re.search(r"\bpath:\s*['\"]([^'\"]+)['\"]", line)
        if path_match:
            flush(current)
            current = {"path": path_match.group(1)}
            continue
        if not current:
            continue
        name_match = re.search(r"\bname:\s*['\"]([^'\"]+)['\"]", line)
        if name_match:
            current["name"] = name_match.group(1)
        component_match = re.search(r"component:\s*\(\)\s*=>\s*import\(['\"]@/([^'\"]+)['\"]\)", line)
        if component_match:
            current["component"] = component_match.group(1)
        for key in ("permission", "titleKey"):
            meta_match = re.search(rf"\b{key}:\s*['\"]([^'\"]+)['\"]", line)
            if meta_match:
                current[key] = meta_match.group(1)
    flush(current)
    return routes


def parse_frontend_manifest_routes(frontend_root: Path) -> list[FrontendRoute]:
    routes: list[FrontendRoute] = []

    def flush(manifest_path: Path, current: dict[str, str]) -> None:
        component = current.get("component", "")
        if not component:
            return
        component_path = manifest_path.parent / component
        route_path = current.get("path", "")
        if route_path and not route_path.startswith("/"):
            route_path = "/" + route_path
        routes.append(
            FrontendRoute(
                route_path=route_path,
                route_name=current.get("name", ""),
                component_path=rel(component_path),
                permission=current.get("permission", ""),
                title_key=current.get("titleKey", ""),
            )
        )

    for manifest_path in sorted({
        *frontend_root.glob("app/*/manifest.js"),
        *frontend_root.glob("app/*/manifest.mjs"),
        *frontend_root.glob("app/*/manifest.ts"),
    }):
        text = read_text(manifest_path)
        current: dict[str, str] = {}
        for line in text.splitlines():
            path_match = re.search(r"\bpath:\s*['\"]([^'\"]+)['\"]", line)
            if path_match:
                flush(manifest_path, current)
                current = {"path": path_match.group(1)}
                continue
            if not current:
                continue
            name_match = re.search(r"\bname:\s*['\"]([^'\"]+)['\"]", line)
            if name_match:
                current["name"] = name_match.group(1)
            component_match = re.search(r"component:\s*\(\)\s*=>\s*import\(['\"]\.\/([^'\"]+)['\"]\)", line)
            if component_match:
                current["component"] = component_match.group(1)
            for key in ("permission", "titleKey"):
                meta_match = re.search(rf"\b{key}:\s*['\"]([^'\"]+)['\"]", line)
                if meta_match:
                    current[key] = meta_match.group(1)
        flush(manifest_path, current)
    return routes


def extract_meta(meta: str, key: str) -> str:
    match = re.search(rf"{key}:\s*['\"]([^'\"]+)['\"]", meta)
    return match.group(1) if match else ""


def classify_frontend_source(path: Path) -> str:
    parts = path.parts
    if "layouts" in parts:
        return "layout"
    if "pages" in parts:
        return "standalone_page"
    if "views" in parts:
        return "page_or_page_component"
    if "app" in parts and "components" in parts:
        return "module_component"
    if "components" in parts:
        return "shared_component"
    if "store" in parts:
        return "store"
    if "utils" in parts:
        return "utility"
    return "frontend_source"


def find_route_for_source(source_file: str, routes: list[FrontendRoute]) -> tuple[str, str]:
    for route in routes:
        if source_file == route.component_path:
            return route.route_path, route.route_name
    source = source_file.replace("\\", "/")
    for route in routes:
        route_dir = str(Path(route.component_path).parent).replace("\\", "/")
        if "/views/" in source and source.startswith(route_dir + "/"):
            return route.route_path, route.route_name
    return "", ""


def to_kebab_case(name: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"-\1", name).lower()


def resolve_component_import(import_source: str, source_path: Path, frontend_root: Path) -> Path | None:
    if import_source.startswith("@/"):
        candidate = frontend_root / import_source[2:]
    elif import_source.startswith("."):
        candidate = source_path.parent / import_source
    else:
        return None
    candidates = [candidate]
    if candidate.suffix == "":
        candidates.extend([candidate.with_suffix(".vue"), candidate / "index.vue"])
    for item in candidates:
        if item.exists() and item.suffix == ".vue":
            return item.resolve()
    return None


def extract_component_props(tag_body: str) -> tuple[str, ...]:
    props: set[str] = set()
    for match in re.finditer(r"(?:^|\s)(?::|v-bind:)?([A-Za-z_][\w-]*)\s*=", tag_body):
        prop_name = match.group(1)
        if prop_name not in {"class", "style", "key", "ref"}:
            props.add(prop_name)
    return tuple(sorted(props))


def parse_component_links(frontend_root: Path, routes: list[FrontendRoute]) -> list[ComponentLink]:
    links: list[ComponentLink] = []
    source_files = [path for path in list_frontend_source_files(frontend_root) if path.suffix == ".vue"]
    for path in sorted(source_files):
        text = read_text(path)
        source_rel = rel(path)
        route_path, route_name = find_route_for_source(source_rel, routes)
        imports: dict[str, Path] = {}
        for match in re.finditer(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", text):
            component_path = resolve_component_import(match.group(2), path, frontend_root)
            if component_path:
                imports[match.group(1)] = component_path

        for component_name, child_path in imports.items():
            tag_names = {component_name, to_kebab_case(component_name)}
            matched_props: set[str] = set()
            used = False
            for tag_name in tag_names:
                for tag_match in re.finditer(rf"<\s*{re.escape(tag_name)}\b([^>]*)>", text, re.DOTALL):
                    used = True
                    matched_props.update(extract_component_props(tag_match.group(1)))
            if not used:
                continue
            links.append(
                ComponentLink(
                    parent_file=source_rel,
                    parent_kind=classify_frontend_source(path),
                    parent_route_path=route_path,
                    parent_route_name=route_name,
                    child_component=component_name,
                    child_file=rel(child_path),
                    props=tuple(sorted(matched_props)),
                )
            )
    return links


def parse_frontend_usages(frontend_root: Path, routes: list[FrontendRoute]) -> tuple[list[FrontendUsage], list[MockFinding]]:
    usages: list[FrontendUsage] = []
    findings: list[MockFinding] = []
    source_files = list_frontend_source_files(frontend_root)
    for path in sorted(source_files):
        text = read_text(path)
        source_rel = rel(path)
        route_path, route_name = find_route_for_source(source_rel, routes)
        imported_functions: dict[str, str] = {}
        namespace_imports: dict[str, str] = {}
        for match in re.finditer(r"import\s+\{([^}]+)\}\s+from\s+['\"]@/api/([^'\"]+)['\"]", text):
            module = Path(match.group(2)).stem
            for raw_name in match.group(1).split(","):
                name = raw_name.strip().split(" as ")[-1].strip()
                if name:
                    imported_functions[name] = module
        for match in re.finditer(r"import\s+\{([^}]+)\}\s+from\s+['\"]@/app/([^/]+)/api(?:/index)?['\"]", text):
            module = match.group(2)
            for raw_name in match.group(1).split(","):
                name = raw_name.strip().split(" as ")[-1].strip()
                if name:
                    imported_functions[name] = module
        for match in re.finditer(r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]@/api/([^'\"]+)['\"]", text):
            namespace_imports[match.group(1)] = Path(match.group(2)).stem
        for match in re.finditer(r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]@/app/([^/]+)/api(?:/index)?['\"]", text):
            namespace_imports[match.group(1)] = match.group(2)

        for function_name, module in imported_functions.items():
            if re.search(rf"\b{re.escape(function_name)}\s*\(", text):
                usages.append(
                    FrontendUsage(
                        source_file=source_rel,
                        source_kind=classify_frontend_source(path),
                        route_path=route_path,
                        route_name=route_name,
                        api_module=module,
                        api_function=function_name,
                    )
                )
        for namespace, module in namespace_imports.items():
            for match in re.finditer(rf"\b{re.escape(namespace)}\.(\w+)\s*\(", text):
                usages.append(
                    FrontendUsage(
                        source_file=source_rel,
                        source_kind=classify_frontend_source(path),
                        route_path=route_path,
                        route_name=route_name,
                        api_module=module,
                        api_function=match.group(1),
                    )
                )
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("import ", "//")):
                continue
            for pattern, reason in STATIC_DATA_PATTERNS:
                if pattern.search(stripped):
                    findings.append(
                        MockFinding(
                            source_file=source_rel,
                            line=line_no,
                            reason=reason,
                            snippet=stripped[:180],
                        )
                    )
                    break
    return usages, findings
