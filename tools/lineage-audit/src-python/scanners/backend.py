"""
File Path: /tools/lineage-audit/src-python/scanners/backend.py
Description: Backend static scanners for FastAPI route to SQLAlchemy model evidence.
Main Features:
    - Scans SQLAlchemy model table metadata.
    - Traces route/service/crud references to model classes where statically visible.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from audit.common import normalize_path, read_text, rel, route_regex
from audit.constants import COMMON_CALLS
from audit.models import BackendFunction, BackendModel, BackendModelRef, BackendRoute, FrontendApi, ImportRef


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _literal_string_list(node: ast.AST | None) -> tuple[tuple[str, ...], str]:
    if isinstance(node, (ast.List, ast.Tuple)) and all(
        isinstance(item, ast.Constant) and isinstance(item.value, str) for item in node.elts
    ):
        return tuple(item.value for item in node.elts), "confirmed"
    return (), "manual_review"

def parse_model_tables(backend_root: Path) -> tuple[dict[str, list[str]], dict[str, BackendModel]]:
    table_by_module: dict[str, list[str]] = {}
    class_to_model: dict[str, BackendModel] = {}
    for path in sorted(backend_root.glob("**/*.py")):
        if "/models/" not in str(path) and path.name not in {"model.py"}:
            continue
        module = path.relative_to(backend_root).parts[0]
        model_file = rel(path)
        text = read_text(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            table_name = ""
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in stmt.targets)
                    and isinstance(stmt.value, ast.Constant)
                    and isinstance(stmt.value.value, str)
                ):
                    table_name = stmt.value.value
                    break
            if not table_name:
                continue
            table_by_module.setdefault(module, [])
            if table_name not in table_by_module[module]:
                table_by_module[module].append(table_name)
            class_to_model[node.name] = BackendModel(
                class_name=node.name,
                table_name=table_name,
                module=module,
                model_file=model_file,
            )
    return table_by_module, class_to_model


def backend_module_file(backend_root: Path, module_name: str) -> str:
    if module_name.startswith("app."):
        module_name = module_name[4:]
    candidate = backend_root / Path(*module_name.split("."))
    py_file = candidate.with_suffix(".py")
    if py_file.exists():
        return rel(py_file)
    init_file = candidate / "__init__.py"
    if init_file.exists():
        return rel(init_file)
    return ""


def relative_module_name(path: Path, backend_root: Path, module: str | None, level: int) -> str:
    if level <= 0:
        return module or ""
    rel_parts = path.resolve().relative_to(backend_root.resolve()).with_suffix("").parts
    package_parts = list(rel_parts[:-1])
    if level > 1:
        package_parts = package_parts[: -(level - 1)] if level - 1 <= len(package_parts) else []
    if module:
        package_parts.extend(module.split("."))
    return ".".join(["app", *package_parts])


def parse_file_imports(path: Path, backend_root: Path) -> dict[str, ImportRef]:
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError:
        return {}
    imports: dict[str, ImportRef] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module_name = relative_module_name(path, backend_root, node.module, node.level)
            file_path = backend_module_file(backend_root, module_name)
            if not file_path:
                continue
            for alias in node.names:
                local_name = alias.asname or alias.name
                imports[local_name] = ImportRef(file_path=file_path, symbol=alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                file_path = backend_module_file(backend_root, module_name)
                if not file_path:
                    continue
                local_name = alias.asname or module_name.split(".")[-1]
                imports[local_name] = ImportRef(file_path=file_path, symbol="")
    return imports


def parse_backend_function_index(backend_root: Path) -> dict[tuple[str, str], BackendFunction]:
    functions: dict[tuple[str, str], BackendFunction] = {}
    for path in sorted(backend_root.glob("**/*.py")):
        text = read_text(path)
        lines = text.splitlines()
        imports = parse_file_imports(path, backend_root)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        file_path = rel(path)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            end_lineno = getattr(node, "end_lineno", node.lineno)
            body = "\n".join(lines[node.lineno - 1 : end_lineno])
            functions[(file_path, node.name)] = BackendFunction(
                name=node.name,
                file_path=file_path,
                body=body,
                imports=imports,
            )
    return functions


def model_refs_from_text(
    text: str,
    class_to_model: dict[str, BackendModel],
    evidence_type: str,
    evidence_file: str,
    evidence_symbol: str,
    confidence: str,
) -> list[BackendModelRef]:
    refs: list[BackendModelRef] = []
    for class_name, model in class_to_model.items():
        if not re.search(rf"\b{re.escape(class_name)}\b", text):
            continue
        refs.append(
            BackendModelRef(
                model_class=class_name,
                table_name=model.table_name,
                module=model.module,
                model_file=model.model_file,
                evidence_type=evidence_type,
                evidence_file=evidence_file,
                evidence_symbol=evidence_symbol,
                confidence=confidence,
            )
        )
    return refs


def resolve_called_functions(
    body: str,
    current_file: str,
    imports: dict[str, ImportRef],
    function_index: dict[tuple[str, str], BackendFunction],
) -> list[tuple[str, str]]:
    resolved: list[tuple[str, str]] = []
    for symbol in parse_called_symbols(body):
        if "." in symbol:
            owner, method = symbol.split(".", 1)
            import_ref = imports.get(owner)
            if import_ref and (import_ref.file_path, method) in function_index:
                resolved.append((import_ref.file_path, method))
            continue
        if (current_file, symbol) in function_index:
            resolved.append((current_file, symbol))
            continue
        import_ref = imports.get(symbol)
        if import_ref and import_ref.symbol and (import_ref.file_path, import_ref.symbol) in function_index:
            resolved.append((import_ref.file_path, import_ref.symbol))
    return resolved


def collect_function_model_refs(
    file_path: str,
    function_name: str,
    function_index: dict[tuple[str, str], BackendFunction],
    class_to_model: dict[str, BackendModel],
    depth: int,
    seen: set[tuple[str, str]],
) -> list[BackendModelRef]:
    key = (file_path, function_name)
    if key in seen:
        return []
    seen.add(key)
    function = function_index.get(key)
    if not function:
        return []
    refs = model_refs_from_text(
        function.body,
        class_to_model,
        "service_or_crud_model_reference",
        function.file_path,
        function.name,
        "inferred",
    )
    if depth <= 0:
        return refs
    for next_file, next_function in resolve_called_functions(function.body, function.file_path, function.imports, function_index):
        refs.extend(
            collect_function_model_refs(
                next_file,
                next_function,
                function_index,
                class_to_model,
                depth - 1,
                seen,
            )
        )
    return refs


def dedupe_model_refs(refs: list[BackendModelRef]) -> tuple[BackendModelRef, ...]:
    by_model: dict[str, BackendModelRef] = {}
    for ref in refs:
        existing = by_model.get(ref.model_class)
        if not existing:
            by_model[ref.model_class] = ref
            continue
        if existing.confidence != "confirmed" and ref.confidence == "confirmed":
            by_model[ref.model_class] = ref
    return tuple(sorted(by_model.values(), key=lambda item: (item.module, item.model_class)))


def parse_router_vars(text: str, api_file: str) -> dict[str, dict[str, str | tuple[str, ...]]]:
    routers: dict[str, dict[str, str | tuple[str, ...]]] = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return routers
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        if _call_name(node.value.func) != "APIRouter":
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not targets:
            continue
        prefix = ""
        tags: tuple[str, ...] = ()
        tag_state = "manual_review"
        for keyword in node.value.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                prefix = keyword.value.value
            if keyword.arg == "tags":
                tags, tag_state = _literal_string_list(keyword.value)
        for router_var in targets:
            routers[router_var] = {
                "prefix": prefix,
                "tags": tags,
                "tag_evidence_file": api_file,
                "tag_evidence_symbol": f"{router_var}=APIRouter@L{node.lineno}",
                "tag_evidence_state": tag_state,
            }
    return routers


def parse_called_symbols(body: str) -> tuple[str, ...]:
    symbols: set[str] = set()
    for match in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", body):
        name = match.group(1)
        if name not in COMMON_CALLS:
            symbols.add(name)
    for match in re.finditer(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(", body):
        symbols.add(f"{match.group(1)}.{match.group(2)}")
    return tuple(sorted(symbols))


def parse_backend_routes(
    backend_root: Path,
    class_to_model: dict[str, BackendModel],
    function_index: dict[tuple[str, str], BackendFunction],
) -> list[BackendRoute]:
    routes: list[BackendRoute] = []
    api_files = [
        path
        for path in backend_root.glob("**/*.py")
        if path.name == "api.py" or "/api/" in str(path)
    ]
    for path in sorted(api_files):
        text = read_text(path)
        api_file = rel(path)
        routers = parse_router_vars(text, api_file)
        if not routers:
            continue
        imports = parse_file_imports(path, backend_root)
        module = path.relative_to(backend_root).parts[0]
        lines = text.splitlines()
        route_defs: list[dict[str, Any]] = []
        for line_index, line in enumerate(lines):
            decorator_match = re.search(
                r"@(\w+)\.(get|post|put|delete|patch)\s*\(\s*(['\"])(.*?)\3",
                line,
            )
            if not decorator_match:
                continue
            function = ""
            function_line = line_index + 1
            for candidate_index in range(line_index + 1, min(line_index + 15, len(lines))):
                function_match = re.search(r"\b(?:async\s+def|def)\s+(\w+)\s*\(", lines[candidate_index])
                if function_match:
                    function = function_match.group(1)
                    function_line = candidate_index
                    break
            if not function:
                continue
            route_defs.append({
                "decorator_line": line_index,
                "function_line": function_line,
                "router_var": decorator_match.group(1),
                "method": decorator_match.group(2).upper(),
                "path_part": decorator_match.group(4),
                "function": function,
            })

        for index, route_def in enumerate(route_defs):
            router_var = route_def["router_var"]
            method = route_def["method"]
            path_part = route_def["path_part"]
            function = route_def["function"]
            body_start_line = route_def["function_line"] + 1
            body_end_line = route_defs[index + 1]["decorator_line"] if index + 1 < len(route_defs) else len(lines)
            body = "\n".join(lines[body_start_line:body_end_line])
            router = routers.get(router_var)
            if not router:
                continue
            prefix = str(router["prefix"])
            full_path = normalize_path(f"{prefix}/{path_part}".replace("//", "/"))
            model_refs = model_refs_from_text(
                body,
                class_to_model,
                "route_model_reference",
                api_file,
                function,
                "confirmed",
            )
            for called_file, called_function in resolve_called_functions(body, api_file, imports, function_index):
                model_refs.extend(
                    collect_function_model_refs(
                        called_file,
                        called_function,
                        function_index,
                        class_to_model,
                        depth=2,
                        seen=set(),
                    )
                )
            inferred_models = dedupe_model_refs(model_refs)
            confidence = "confirmed" if any(ref.confidence == "confirmed" for ref in inferred_models) else ("inferred" if inferred_models else "manual_review")
            routes.append(
                BackendRoute(
                    module=module,
                    router_var=router_var,
                    function=function,
                    method=method,
                    path=full_path,
                    api_file=api_file,
                    router_tags=tuple(router["tags"]),
                    tag_evidence_file=str(router["tag_evidence_file"]),
                    tag_evidence_symbol=str(router["tag_evidence_symbol"]),
                    tag_evidence_state=str(router["tag_evidence_state"]),
                    called_symbols=parse_called_symbols(body),
                    model_refs=inferred_models,
                    confidence=confidence,
                )
            )
    return routes


def build_route_matches(frontend_apis: list[FrontendApi], backend_routes: list[BackendRoute]) -> dict[tuple[str, str], BackendRoute]:
    matches: dict[tuple[str, str], BackendRoute] = {}
    by_method = {}
    for route in backend_routes:
        by_method.setdefault(route.method, []).append(route)
    for api in frontend_apis:
        for route in by_method.get(api.method, []):
            if route_regex(route.path).match(normalize_path(api.path)):
                matches[(api.method, api.path)] = route
                break
    return matches


def needs_plc_candidate(usage: FrontendUsage, api: FrontendApi | None, route: BackendRoute | None) -> str:
    haystack = " ".join(
        [
            usage.source_file,
            usage.route_path,
            api.path if api else "",
            route.path if route else "",
            " ".join(ref.table_name for ref in route.model_refs) if route else "",
        ]
    ).lower()
    if any(token in haystack for token in ["monitor", "hmi", "plc_db_block", "temperature", "energy"]):
        return "yes"
    if any(token in haystack for token in ["plan", "performance", "quality", "equipment", "dashboard"]):
        return "manual_review"
    return "no"
