"""模块接入只读预检：literal声明、依赖、公开符号及最终对象冲突；不作为Python沙箱。"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
from types import SimpleNamespace

from app.module_contract import CORE_CONTRACT, LEGACY_MODULES, LEGACY_CORE_ERRORS, PUBLIC_SYMBOLS, LEGACY_PUBLIC_COMPATIBILITY, LEGACY_SETTINGS_COMPATIBILITY


class ModulePreflightError(RuntimeError):
    """定位明确的接入阻断；不携带配置或业务payload。"""

    def __init__(self, stage, module, identifier, location="", other=""):
        self.diagnostic = dict(stage=stage, module=module, identifier=identifier,
                               location=str(location), other_owner=other)
        super().__init__(json.dumps(self.diagnostic, ensure_ascii=False, sort_keys=True))


def _fail(stage, module, identifier, location="", other=""):
    raise ModulePreflightError(stage, module, identifier, location, other)


def validate_manifests(manifests, *, check_dependencies=True):
    """验证纯声明；runtime有向图与metadata闭包分别处理，保持原order。"""
    manifests = tuple(manifests)
    by_name = {}
    claimed = {field: {} for field in ("routers", "models_package", "permissions", "error_codes")}
    for manifest in manifests:
        name = manifest.name
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            _fail("manifest-name", str(name), "invalid_name")
        if name in by_name:
            _fail("manifest-name", name, "duplicate_name", other=name)
        by_name[name] = manifest
        if manifest.core_contract != CORE_CONTRACT:
            _fail("contract", name, str(manifest.core_contract), f"app/{name}/manifest.py")
        if type(manifest.enabled) is not bool or type(manifest.order) is not int:
            _fail("manifest-type", name, "enabled/order")
        for field in ("requires", "model_requires", "routers", "permissions", "exports", "error_codes"):
            values = getattr(manifest, field)
            if not isinstance(values, tuple) or any(not isinstance(v, str) or not v.strip() for v in values):
                _fail("manifest-type", name, field)
            if len(set(values)) != len(values):
                _fail("manifest-duplicate", name, field)
        for field in ("requires", "model_requires"):
            for dependency in getattr(manifest, field):
                if not re.fullmatch(r"[a-z][a-z0-9_]*", dependency) or dependency in {name, "user", "control_agent"}:
                    _fail("dependency-name", name, f"{field}:{dependency}")
        for field in ("routers", "exports"):
            for entry in getattr(manifest, field):
                if not re.fullmatch(rf"app\.{re.escape(name)}(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", entry):
                    _fail("declaration-owner", name, entry)
        if manifest.models_package is not None and (
            not isinstance(manifest.models_package, str)
            or not (manifest.models_package == f"app.{name}.models" or manifest.models_package.startswith(f"app.{name}.models."))
        ):
            _fail("declaration-owner", name, "models_package")
        for field in claimed:
            entries = (manifest.models_package,) if field == "models_package" and manifest.models_package else getattr(manifest, field, ())
            if field == "models_package" and not manifest.models_package:
                entries = ()
            for entry in entries:
                if field == "permissions" and entry in {"control-agent", "control-agent-read"}:
                    _fail("permission", name, entry, other="control_agent")
                if field == "permissions" and entry == "system" and name != "system":
                    _fail("permission", name, entry, other="user/system")
                if field == "error_codes" and not re.fullmatch(re.escape(name) + r"\.[a-z][a-z0-9_.]*", entry):
                    _fail("error-namespace", name, entry)
                other = claimed[field].get(entry)
                if other:
                    _fail(field, name, entry, other=other)
                claimed[field][entry] = name
    if not check_dependencies:
        return
    for manifest in manifests:
        for field in ("requires", "model_requires"):
            if field == "requires" and not manifest.enabled:
                continue
            for dependency in getattr(manifest, field):
                target = by_name.get(dependency)
                if target is None or (field == "requires" and not target.enabled) or (field == "model_requires" and not target.models_package):
                    _fail("dependency", manifest.name, f"{manifest.name} -> {dependency} ({field})")
    visited, active = set(), []

    def visit(name):
        if name in active:
            _fail("runtime-cycle", name, " -> ".join(active[active.index(name):] + [name]))
        if name in visited:
            return
        active.append(name)
        for dependency in by_name[name].requires:
            visit(dependency)
        active.pop()
        visited.add(name)

    for manifest in manifests:
        if manifest.enabled:
            visit(manifest.name)


_DEFAULTS = dict(enabled=True, order=100, routers=(), models_package=None, permissions=(),
                 core_contract=CORE_CONTRACT, requires=(), model_requires=(), exports=(), error_codes=())


@lru_cache(maxsize=512)
def _parse_source(text, filename):
    return ast.parse(text, filename=filename)


def _tree(path):
    # 以源码内容为key，别名追踪复用AST；文件修改后不会命中旧树。
    return _parse_source(path.read_text(encoding="utf-8"), str(path))


def _source_path(root, module):
    path = root.joinpath(*module.split("."))
    return path / "__init__.py" if path.is_dir() else path.with_suffix(".py")


def _absolute_import(node, source, root):
    module = node.module or ""
    if node.level:
        parts = list(source.relative_to(root).with_suffix("").parts)
        parts.pop()
        parts = parts[:len(parts) - node.level + 1]
        module = ".".join(parts + ([module] if module else []))
    return module


def _module_attribute_symbol(root, module, attribute, seen=None, before_line=None):
    """Python显式绑定优先；仅package未绑定名称时尝试literal子模块fallback。"""
    path = _source_path(root, module)
    if path.is_file():
        for node in reversed(_tree(path).body):
            if before_line is not None and node.lineno >= before_line:
                continue
            names = []
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                names = [node.name]
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                names = [target.id for target in (node.targets if isinstance(node, ast.Assign) else [node.target]) if isinstance(target, ast.Name)]
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.asname or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name) for alias in node.names]
            if attribute in names:
                resolved = _expression_symbol(root, path, ast.Name(id=attribute), seen, before_line)
                return resolved or module + ":" + attribute
        if path.name == "__init__.py" and _source_path(root, module + "." + attribute).is_file():
            return module + "." + attribute
    return module + ":" + attribute


def _import_from_symbol(root, source, node, name, seen=None):
    module = _absolute_import(node, source, root)
    # package初始化中的from . import x只能使用之前已执行的绑定，否则按子模块导入。
    before = node.lineno if _source_path(root, module) == source else None
    return _module_attribute_symbol(root, module, name, seen, before)


def read_source_manifests(root):
    """只解析源码，不导入任何manifest/settings/数据库。无manifest的目录跳过。"""
    result, diagnostics = [], []
    for path in sorted((root / "app").glob("*/manifest.py")):
        name = path.parent.name
        if name in {"user", "control_agent"}:
            continue
        assignments = [node for node in _tree(path).body if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "manifest" for t in node.targets)]
        if len(assignments) != 1 or not isinstance(assignments[0].value, ast.Call):
            _fail("manifest-literal", name, "manifest = ModuleManifest(...) required", path)
        call = assignments[0].value
        if not isinstance(call.func, ast.Name) or call.func.id != "ModuleManifest" or call.args:
            _fail("manifest-literal", name, "ModuleManifest keyword literals required", path)
        values = dict(_DEFAULTS)
        for keyword in call.keywords:
            try:
                value = ast.literal_eval(keyword.value)
            except (ValueError, TypeError):
                _fail("manifest-literal", name, keyword.arg, f"{path}:{keyword.value.lineno}")
            if keyword.arg not in _DEFAULTS and keyword.arg != "name":
                _fail("manifest-field", name, str(keyword.arg), path)
            values[keyword.arg] = value
        if values.get("name") != name:
            _fail("manifest-name", name, str(values.get("name")), path)
        result.append(SimpleNamespace(**values))
        diagnostics.append(dict(stage="manifest", module=name,
                                status="active" if values["enabled"] else "inactive",
                                core_contract="explicit" if any(k.arg == "core_contract" for k in call.keywords) else "legacy_default"))
    validate_manifests(result)
    return result, diagnostics


def _symbol_definition(root, symbol, seen=None):
    """跟踪literal薄重导出到原定义；不执行任何Python。"""
    seen = set() if seen is None else seen
    if symbol in seen:
        return None
    seen.add(symbol)
    module, _, attribute = symbol.partition(":")
    path = _source_path(root, module)
    if not path.is_file():
        return None
    if not attribute:
        return module, _tree(path), path
    for node in reversed(_tree(path).body):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == attribute:
            return module, node, path
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == attribute for t in targets):
                if isinstance(node.value, (ast.Name, ast.Attribute)):
                    alias = _expression_symbol(root, path, node.value)
                    if alias:
                        definition = _symbol_definition(root, alias, seen)
                        if definition:
                            return definition
                return module, node, path
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if (alias.asname or alias.name) == attribute:
                    return _symbol_definition(root, _import_from_symbol(root, path, node, alias.name), seen)
    fallback = _module_attribute_symbol(root, module, attribute)
    if fallback != symbol:
        return _symbol_definition(root, fallback, seen)
    return None


def _has_symbol(root, symbol):
    return _symbol_definition(root, symbol) is not None


def _expression_symbol(root, source, expression, seen=None, before_line=None):
    """解析literal名称/导入别名/薄赋值；供异常调用追踪，不执行代码。"""
    seen = set() if seen is None else seen
    if isinstance(expression, ast.Attribute):
        parent = _expression_symbol(root, source, expression.value, seen)
        if parent:
            return parent + "." + expression.attr if ":" in parent else _module_attribute_symbol(root, parent, expression.attr, seen)
    if not isinstance(expression, ast.Name) or (source, expression.id) in seen:
        return None
    seen.add((source, expression.id))
    module = ".".join(source.relative_to(root).with_suffix("").parts).removesuffix(".__init__")
    for node in reversed(_tree(source).body):
        if before_line is not None and node.lineno >= before_line:
            continue
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if (alias.asname or alias.name) == expression.id:
                    return _import_from_symbol(root, source, node, alias.name, seen)
        if isinstance(node, ast.Import):
            for alias in node.names:
                if (alias.asname or alias.name.split(".")[0]) == expression.id:
                    return alias.name if alias.asname else alias.name.split(".")[0]
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == expression.id:
            return module + ":" + node.name
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == expression.id for target in targets):
                return _expression_symbol(root, source, node.value, seen)
    return None


def _is_str_enum(root, source, node, seen=None):
    seen = set() if seen is None else seen
    key = (source, node.name)
    if key in seen:
        return False
    seen.add(key)
    for base in node.bases:
        symbol = _expression_symbol(root, source, base)
        if symbol == "enum:StrEnum":
            return True
        definition = _symbol_definition(root, symbol) if symbol else None
        if definition and isinstance(definition[1], ast.ClassDef) and _is_str_enum(root, definition[2], definition[1], seen):
            return True
    return False


def _error_argument_symbols(root, sources, source, argument, call, seen=None):
    """追踪异常工厂实参；不把泛型/无注解本身当成非法合同。"""
    seen = set() if seen is None else seen
    key = (source, getattr(argument, "lineno", 0), ast.unparse(argument) if argument else "")
    if key in seen:
        return None
    seen = seen | {key}
    symbol = _expression_symbol(root, source, argument)
    if symbol:
        return {symbol}
    if not isinstance(argument, ast.Name):
        return None
    for function in ast.walk(sources[source]):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) or not any(child is call for child in ast.walk(function)):
            continue
        positional = (*function.args.posonlyargs, *function.args.args)
        parameters = (*positional, *function.args.kwonlyargs)
        parameter = next((arg for arg in parameters if arg.arg == argument.id), None)
        if parameter is None:
            assignments = [node.value for node in ast.walk(function) if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.lineno < call.lineno and any(isinstance(target, ast.Name) and target.id == argument.id for target in (node.targets if isinstance(node, ast.Assign) else [node.target]))]
            if assignments:
                values = [_error_argument_symbols(root, sources, source, value, call, seen) for value in assignments]
                return set().union(*values) if all(values) else None
            continue
        module = ".".join(source.relative_to(root).with_suffix("").parts).removesuffix(".__init__")
        values, unresolved = [], False
        for caller_source, caller_tree in sources.items():
            for caller in ast.walk(caller_tree):
                if not isinstance(caller, ast.Call):
                    continue
                target = _expression_symbol(root, caller_source, caller.func)
                definition = _symbol_definition(root, target) if target else None
                if not definition or definition[0] != module or getattr(definition[1], "name", None) != function.name:
                    continue
                actual = next((keyword.value for keyword in caller.keywords if keyword.arg == parameter.arg), None)
                if actual is None and parameter in positional:
                    index = positional.index(parameter)
                    if index < len(caller.args):
                        actual = caller.args[index]
                    elif index >= len(positional) - len(function.args.defaults):
                        actual = function.args.defaults[index - len(positional) + len(function.args.defaults)]
                if actual is None and parameter in function.args.kwonlyargs:
                    actual = function.args.kw_defaults[function.args.kwonlyargs.index(parameter)]
                resolved = _error_argument_symbols(root, sources, caller_source, actual, caller, seen)
                if resolved:
                    values.append(resolved)
                else:
                    unresolved = True
        if values and not unresolved:
            return set().union(*values)
        # 外部调用无literal来源时，具体枚举注解可提供来源；泛型StrEnum本身不能定位owner。
        annotated = _expression_symbol(root, source, parameter.annotation) if parameter.annotation else None
        return {annotated} if annotated and not unresolved else None
    return None


def _inactive_runtime_source(root, source, manifest):
    relative = source.relative_to(root / "app" / manifest.name)
    return not manifest.enabled and "models" not in relative.parts and relative.as_posix() not in {"__init__.py", "manifest.py"}


def _used_error_enums(root, manifests):
    """以实际BusinessException参数识别错误枚举，类名不赋予错误/领域状态语义。"""
    result = set()
    sources = {source: _tree(source) for manifest in manifests for source in sorted((root / "app" / manifest.name).rglob("*.py"))}
    for manifest in manifests:
        for source in sorted((root / "app" / manifest.name).rglob("*.py")):
            tree = _tree(source)
            inactive_runtime = _inactive_runtime_source(root, source, manifest)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                symbol = _expression_symbol(root, source, node.func)
                if symbol != "common.exceptions:BusinessException":
                    definition = _symbol_definition(root, symbol) if symbol else None
                    if not definition or definition[0] != "common.exceptions" or getattr(definition[1], "name", None) != "BusinessException":
                        continue
                argument = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "error_code"), None)
                members = _error_argument_symbols(root, sources, source, argument, node)
                if not members:
                    if inactive_runtime:
                        continue
                    _fail("error-source", manifest.name, ast.unparse(argument) if argument else "missing error_code", f"{source.relative_to(root)}:{node.lineno}")
                for member in members:
                    module, _, attribute = member.partition(":")
                    definition = _symbol_definition(root, module + ":" + (attribute.rsplit(".", 1)[0] if "." in attribute else attribute))
                    if definition and isinstance(definition[1], ast.ClassDef) and _is_str_enum(root, definition[2], definition[1]):
                        result.add((definition[0], definition[1].name))
                    elif not inactive_runtime:
                        _fail("error-source", manifest.name, member, f"{source.relative_to(root)}:{node.lineno}")
    return result


def _is_model_symbol(root, symbol, target):
    """R3：仅models_package下原SQLAlchemy映射实体，文件位置不改变分类。"""
    definition = _symbol_definition(root, symbol)
    if definition is None or not target.models_package:
        return False
    module, node, path = definition
    if not (module == target.models_package or module.startswith(target.models_package + ".")) or not isinstance(node, ast.ClassDef):
        return False
    bases = {ast.unparse(base) for base in node.bases}
    imported_base = {alias.asname or alias.name for entry in _tree(path).body
                     if isinstance(entry, ast.ImportFrom) and entry.module in {"database", "database.base"}
                     for alias in entry.names if alias.name == "Base"}
    return bool(bases & imported_base) and any(
        isinstance(entry, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__tablename__" for t in entry.targets)
        for entry in node.body)


def _class_schema(node):
    for statement in node.body:
        if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__table_args__" for t in statement.targets):
            dictionaries = [statement.value] if isinstance(statement.value, ast.Dict) else [x for x in getattr(statement.value, "elts", ()) if isinstance(x, ast.Dict)]
            for dictionary in dictionaries:
                for key, value in zip(dictionary.keys, dictionary.values):
                    if isinstance(key, ast.Constant) and key.value == "schema":
                        return ast.literal_eval(value)
    return None


def check_source(project_root):
    """检查literal import/相对import、表和字符串关系，不读取env或触发任何外部I/O。"""
    root = Path(project_root).resolve()
    if not (root / "app/__init__.py").is_file():
        _fail("project-root", "app", "missing app package", root)
    manifests, diagnostics = read_source_manifests(root)
    owners = {m.name: m for m in manifests}
    tables, classes, model_references = {}, {}, []
    used_error_enums = _used_error_enums(root, manifests)
    core_error_path = root / "common/error_codes.py"
    errors = {}
    if core_error_path.is_file():
        for node in ast.walk(_tree(core_error_path)):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                errors[node.value.value] = "Core"
    for manifest in manifests:
        for export in manifest.exports:
            if not _has_symbol(root, export):
                _fail("export", manifest.name, export, root / "app" / manifest.name / "manifest.py")
        local_errors = set()
        for source in sorted((root / "app" / manifest.name).rglob("*.py")):
            relative = source.relative_to(root)
            is_model = "models" in relative.parts
            # disabled API/service未执行；入口和metadata仍需检查。
            tree = _tree(source)
            location = lambda n: f"{relative}:{n.lineno}"
            settings_names = {alias.asname or alias.name for entry in ast.walk(tree)
                              if isinstance(entry, ast.ImportFrom) and entry.module == "settings"
                              for alias in entry.names if alias.name == "settings"}
            dynamic_names = {alias.asname or alias.name for entry in ast.walk(tree)
                             if isinstance(entry, ast.ImportFrom) and entry.module in {"importlib", "builtins"}
                             for alias in entry.names if alias.name in {"import_module", "__import__", "exec", "eval"}}
            for entry in ast.walk(tree):
                if isinstance(entry, ast.Attribute) and isinstance(entry.value, ast.Name) and entry.value.id in settings_names:
                    allowed_settings = {"BACKEND_MOCK_ENABLED", *LEGACY_SETTINGS_COMPATIBILITY.get(manifest.name, ())}
                    if entry.attr not in allowed_settings:
                        _fail("private-setting", manifest.name, entry.attr, location(entry))

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = ast.unparse(node.func)
                    if func_name in {"__import__", "exec", "eval", "importlib.import_module", "import_module", *dynamic_names} or func_name.endswith(".import_module"):
                        _fail("unsupported-dynamic-import", manifest.name, func_name, location(node))
                    if is_model and func_name.rsplit(".", 1)[-1] == "Table" and node.args:
                        try:
                            table_name = ast.literal_eval(node.args[0])
                            schema = next((ast.literal_eval(k.value) for k in node.keywords if k.arg == "schema"), None)
                        except (ValueError, TypeError):
                            _fail("table-literal", manifest.name, "Table", location(node))
                        identity = f"{schema}.{table_name}" if schema else table_name
                        if identity in tables:
                            _fail("table", manifest.name, identity, location(node), tables[identity])
                        tables[identity] = manifest.name
                    if is_model and func_name.endswith(("ForeignKey", "relationship")) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        model_references.append((manifest.name, func_name.rsplit(".", 1)[-1], node.args[0].value, location(node)))
                if isinstance(node, ast.ClassDef):
                    if is_model:
                        for statement in node.body:
                            if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__tablename__" for t in statement.targets):
                                module = ".".join(relative.with_suffix("").parts).removesuffix(".__init__")
                                classes[module + "." + node.name] = manifest.name
                                table = ast.literal_eval(statement.value)
                                schema = _class_schema(node)
                                table = f"{schema}.{table}" if schema else table
                                if table in tables:
                                    _fail("table", manifest.name, table, location(statement), tables[table])
                                tables[table] = manifest.name
                    module = ".".join(relative.with_suffix("").parts).removesuffix(".__init__")
                    if _is_str_enum(root, source, node) and ((module, node.name) in used_error_enums or any(isinstance(entry, ast.Assign) and isinstance(entry.value, ast.Constant) and entry.value.value in manifest.error_codes for entry in node.body)):
                        for statement in node.body:
                            if isinstance(statement, ast.Assign):
                                try:
                                    value = ast.literal_eval(statement.value)
                                except (ValueError, TypeError):
                                    _fail("error-value", manifest.name, node.name, location(statement))
                                if not isinstance(value, str) or (not re.fullmatch(re.escape(manifest.name) + r"\.[a-z][a-z0-9_.]*", value) and LEGACY_CORE_ERRORS.get(value) != manifest.name):
                                    _fail("error-namespace", manifest.name, str(value), location(statement))
                                if value in errors:
                                    _fail("error-value", manifest.name, value, location(statement), errors[value])
                                errors[value] = manifest.name
                                if value not in LEGACY_CORE_ERRORS:
                                    local_errors.add(value)
                imports = []
                if isinstance(node, ast.ImportFrom):
                    module = _absolute_import(node, source, root)
                    imports = [(module, alias.name) for alias in node.names]
                elif isinstance(node, ast.Import):
                    imports = [(alias.name, None) for alias in node.names]
                for module, attribute in imports:
                    parts = module.split(".")
                    if parts[0] in {"database", "common", "core", "projection", "settings"} or module.startswith(("app.user", "app.control_agent", "app.module_")):
                        symbol = module + (":" + attribute if attribute else "")
                        allowed = attribute in PUBLIC_SYMBOLS.get(module, ()) or (module, attribute) == ("settings", "settings")
                        if not allowed and symbol not in LEGACY_PUBLIC_COMPATIBILITY.get(manifest.name, ()):
                            _fail("private-core-import", manifest.name, symbol, location(node))

                    if module == "common.data_keys" and manifest.name not in LEGACY_MODULES:
                        _fail("legacy-dependency", manifest.name, module, location(node))
                    if parts[0] != "app" or len(parts) < 2 or parts[1] in {manifest.name, "module_registry", "module_contract", "user", "control_agent"}:
                        continue
                    target_name = parts[1]
                    target = owners.get(target_name)
                    symbol = module + (":" + attribute if attribute else "")
                    field = "model_requires" if target is not None and _is_model_symbol(root, symbol, target) else "requires"
                    if _inactive_runtime_source(root, source, manifest) and field == "requires":
                        continue
                    if target_name not in getattr(manifest, field):
                        _fail("undeclared-dependency", manifest.name, f"{field}:{target_name}", location(node))
                    if target is None or attribute is None or symbol not in target.exports:
                        _fail("private-import", manifest.name, symbol, location(node), target_name)
        if local_errors != set(manifest.error_codes):
            _fail("error-declaration", manifest.name, str(sorted(local_errors ^ set(manifest.error_codes))))
    # 显式Core模型也参与FK/relationship owner解析，但不作为普通requires目标。
    for boundary in ("user", "control_agent"):
        for source in (root / "app" / boundary / "models").glob("*.py"):
            for node in ast.walk(_tree(source)):
                if isinstance(node, ast.ClassDef):
                    for statement in node.body:
                        if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__tablename__" for t in statement.targets):
                            module = ".".join(source.relative_to(root).with_suffix("").parts).removesuffix(".__init__")
                            classes[module + "." + node.name] = boundary
                            table = ast.literal_eval(statement.value)
                            if table in tables:
                                _fail("table", boundary, table, f"{source}:{statement.lineno}", tables[table])
                            tables[table] = boundary
    for name, kind, target, location in model_references:
        if kind == "ForeignKey":
            other = tables.get(target.rsplit(".", 1)[0])
        else:
            # 限定原定义优先；裸名/SQLAlchemy后缀仅在唯一class时解析，绝不以后扫owner覆盖。
            definition = _symbol_definition(root, target.rsplit(".", 1)[0] + ":" + target.rsplit(".", 1)[-1]) if "." in target else None
            canonical = definition[0] + "." + definition[1].name if definition and isinstance(definition[1], ast.ClassDef) else target
            candidates = [key for key in classes if key == canonical or key.endswith("." + canonical)]
            if len(candidates) > 1:
                _fail("model-target", name, target + " (ambiguous)", location)
            other = classes.get(candidates[0]) if candidates else None
        if other is None:
            _fail("model-target", name, target, location)
        if other not in {name, "user", "control_agent"} and other not in owners[name].model_requires:
            _fail("undeclared-model-dependency", name, f"{target} -> {other}", location)
    return diagnostics


def check_routes(app):
    """核对组合后的实际method/path；参数名差异同形，静态/参数合法共存。"""
    found = {}
    for route in app.routes:
        if not hasattr(route, "methods"):
            continue
        path = re.sub(r"\{[^{}]+\}", "{}", route.path).rstrip("/") or "/"
        endpoint = getattr(route, "endpoint", None)
        owner = getattr(endpoint, "__module__", "framework")
        for method in sorted(route.methods or ()):
            key = (method, path)
            if key in found:
                _fail("http-route", owner, f"{method} {path}", route.path, found[key])
            found[key] = owner
    return found


def check_model_objects(manifests):
    """metadata加载后核对class/Table定义owner及exports真实可解析。"""
    from importlib import import_module
    from database import Base
    mapped_tables = {}
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        table = mapper.local_table
        owner = cls.__module__
        identity = (table.schema, table.name)
        previous = mapped_tables.get(identity)
        if previous and previous[0] is not cls:
            _fail("model-object", owner, str(identity), other=previous[1])
        mapped_tables[identity] = (cls, owner)
    for manifest in manifests:
        for export in manifest.exports:
            if not manifest.enabled and not _is_model_symbol(Path(__file__).resolve().parent.parent, export, manifest):
                continue
            module, _, attribute = export.partition(":")
            target = import_module(module)
            try:
                for part in attribute.split("."):
                    target = getattr(target, part)
            except AttributeError:
                _fail("export-object", manifest.name, export)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    if args.project_root is None or not args.check_only:
        parser.print_help()
        return 0
    try:
        diagnostics = check_source(args.project_root)
    except (ModulePreflightError, SyntaxError) as exc:
        print(json.dumps(getattr(exc, "diagnostic", dict(stage="syntax", error_type=type(exc).__name__)), ensure_ascii=False, sort_keys=True))
        return 1
    for diagnostic in diagnostics:
        print(json.dumps(diagnostic, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
