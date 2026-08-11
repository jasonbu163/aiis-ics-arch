"""
文件路径: /tools/plc/point-mapping/src-python/source_parser/tia.py
功能描述: 解析 TIA 导出的 DB/UDT 源文件
主要功能:
    - 读取 DATA_BLOCK 和 TYPE 结构声明
    - 识别内联 Struct、UDT 引用和数组展开行
    - 为 XLSX Struct 校验提供可比对的行序列
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


PRIMITIVE_TYPES = {
    "bool",
    "byte",
    "char",
    "dint",
    "dword",
    "int",
    "real",
    "string",
    "udint",
    "uint",
    "usint",
    "word",
}

_DATA_BLOCK_RE = re.compile(r'^DATA_BLOCK\s+"(?P<name>[^"]+)"', re.IGNORECASE)
_TYPE_RE = re.compile(r'^TYPE\s+"(?P<name>[^"]+)"', re.IGNORECASE)
_OPTIMIZED_RE = re.compile(r"S7_Optimized_Access\s*:=\s*'(?P<value>TRUE|FALSE)'", re.IGNORECASE)
_ATTR_RE = re.compile(r"\{[^}]*\}")
_ARRAY_RE = re.compile(
    r"^Array\[(?P<start>-?\d+)\.\.(?P<end>-?\d+)\]\s+of\s+(?P<element>.+)$",
    re.IGNORECASE,
)


@dataclass
class TiaField:
    name: str
    data_type: str
    comment: str = ""
    children: list["TiaField"] = field(default_factory=list)


@dataclass
class TiaBlock:
    name: str
    fields: list[TiaField] = field(default_factory=list)
    optimized_access: bool | None = None


@dataclass
class TiaSourceModel:
    db_blocks: dict[str, TiaBlock]
    udt_types: dict[str, TiaBlock]


@dataclass(frozen=True)
class SourceRowSpec:
    name: str
    data_type: str
    path: tuple[str, ...]
    kind: str


def parse_tia_sources(db_source_path: Path | None, udt_source_path: Path | None) -> TiaSourceModel:
    db_blocks = parse_db_source(db_source_path) if db_source_path else {}
    udt_types = parse_udt_source(udt_source_path) if udt_source_path else {}
    return TiaSourceModel(db_blocks=db_blocks, udt_types=udt_types)


def parse_db_source(path: Path) -> dict[str, TiaBlock]:
    return _parse_blocks(path, block_kind="db")


def parse_udt_source(path: Path) -> dict[str, TiaBlock]:
    return _parse_blocks(path, block_kind="udt")


def expand_block_rows(
    block: TiaBlock,
    udt_types: dict[str, TiaBlock],
) -> tuple[list[SourceRowSpec], list[str]]:
    rows: list[SourceRowSpec] = []
    warnings: list[str] = []
    _append_field_rows(block.fields, (), udt_types, rows, warnings)
    return rows, warnings


def normalize_type_name(value: object) -> str:
    text = str(value).strip().strip(";").strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    if text.casefold() == "struct":
        return "Struct"
    array_match = _ARRAY_RE.match(text)
    if array_match:
        element_type = normalize_type_name(array_match.group("element"))
        return f"Array[{array_match.group('start')}..{array_match.group('end')}] of {element_type}"
    canonical = {
        "bool": "Bool",
        "byte": "Byte",
        "char": "Char",
        "dint": "DInt",
        "dword": "DWord",
        "int": "Int",
        "real": "Real",
        "string": "String",
        "udint": "UDInt",
        "uint": "UInt",
        "usint": "USInt",
        "word": "Word",
    }
    return canonical.get(text.casefold(), text)


def _parse_blocks(path: Path, *, block_kind: str) -> dict[str, TiaBlock]:
    text = path.read_text(encoding="utf-8-sig")
    start_re = _DATA_BLOCK_RE if block_kind == "db" else _TYPE_RE
    end_token = "END_DATA_BLOCK" if block_kind == "db" else "END_TYPE"
    blocks: dict[str, TiaBlock] = {}
    current: TiaBlock | None = None
    stack: list[TiaBlock | TiaField] = []

    for raw_line in text.splitlines():
        line, comment = _split_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        start_match = start_re.match(stripped)
        if start_match:
            current = TiaBlock(name=start_match.group("name"))
            stack = [current]
            continue

        if current is None:
            continue

        optimized_match = _OPTIMIZED_RE.search(stripped)
        if optimized_match:
            current.optimized_access = optimized_match.group("value").casefold() == "true"
            continue

        if stripped.upper().startswith(end_token):
            blocks[current.name] = current
            current = None
            stack = []
            continue

        statement = stripped.rstrip(";").strip()
        if statement.upper() == "STRUCT":
            continue
        if statement.upper() == "END_STRUCT":
            if len(stack) > 1:
                stack.pop()
            continue
        if statement.upper().startswith("VERSION "):
            continue

        field_decl = _parse_field_declaration(stripped, comment)
        if field_decl is None:
            continue
        parent = stack[-1]
        if isinstance(parent, TiaBlock):
            parent.fields.append(field_decl)
        else:
            parent.children.append(field_decl)
        if field_decl.data_type == "Struct":
            stack.append(field_decl)

    return blocks


def _parse_field_declaration(line: str, comment: str) -> TiaField | None:
    without_attrs = _ATTR_RE.sub("", line).strip()
    if ":" not in without_attrs:
        return None
    name_part, type_part = without_attrs.split(":", 1)
    name = _normalize_identifier(name_part)
    data_type = normalize_type_name(type_part)
    if not name or not data_type:
        return None
    return TiaField(name=name, data_type=data_type, comment=comment.strip())


def _append_field_rows(
    fields: list[TiaField],
    parent_path: tuple[str, ...],
    udt_types: dict[str, TiaBlock],
    rows: list[SourceRowSpec],
    warnings: list[str],
) -> None:
    for field_item in fields:
        path = parent_path + (field_item.name,)
        if field_item.children or field_item.data_type == "Struct":
            rows.append(SourceRowSpec(field_item.name, "Struct", path, "struct"))
            _append_field_rows(field_item.children, path, udt_types, rows, warnings)
            continue

        array_range = parse_array_type(field_item.data_type)
        if array_range is not None:
            start, end, element_type = array_range
            rows.append(SourceRowSpec(field_item.name, field_item.data_type, path, "array"))
            step = 1 if end >= start else -1
            for index in range(start, end + step, step):
                element_name = f"{field_item.name}[{index}]"
                rows.append(SourceRowSpec(element_name, element_type, path + (f"[{index}]",), "array_element"))
            continue

        udt_block = udt_types.get(field_item.data_type)
        if udt_block is not None:
            rows.append(SourceRowSpec(field_item.name, field_item.data_type, path, "udt"))
            _append_field_rows(udt_block.fields, path, udt_types, rows, warnings)
            continue

        if _looks_like_udt(field_item.data_type):
            warnings.append(f"missing UDT definition for {'.'.join(path)}: {field_item.data_type}")
            rows.append(SourceRowSpec(field_item.name, field_item.data_type, path, "udt"))
            continue

        rows.append(SourceRowSpec(field_item.name, field_item.data_type, path, "scalar"))


def parse_array_type(data_type: str) -> tuple[int, int, str] | None:
    match = _ARRAY_RE.match(data_type)
    if not match:
        return None
    return int(match.group("start")), int(match.group("end")), normalize_type_name(match.group("element"))


def _split_comment(line: str) -> tuple[str, str]:
    if "//" not in line:
        return line, ""
    code, comment = line.split("//", 1)
    return code, comment


def _normalize_identifier(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    return text


def _looks_like_udt(data_type: str) -> bool:
    lower_type = data_type.casefold()
    if lower_type in PRIMITIVE_TYPES:
        return False
    if lower_type.startswith("array[") or lower_type.startswith("string["):
        return False
    return True
