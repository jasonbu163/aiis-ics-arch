"""
File Path: /tools/lineage-audit/src-python/audit/models.py
Description: Shared lineage audit data models.
Main Features:
    - Defines frontend/backend scanner DTOs.
    - Defines aggregate audit state.
"""
from __future__ import annotations

from dataclasses import dataclass, field

class ToolError(RuntimeError):
    """Raised for expected tool failures."""


@dataclass(frozen=True)
class FrontendRoute:
    route_path: str
    route_name: str
    component_path: str
    permission: str
    title_key: str


@dataclass(frozen=True)
class FrontendApi:
    module: str
    function: str
    method: str
    path: str
    raw_path_expr: str
    api_file: str
    confidence: str


@dataclass(frozen=True)
class FrontendUsage:
    source_file: str
    source_kind: str
    route_path: str
    route_name: str
    api_module: str
    api_function: str


@dataclass(frozen=True)
class ComponentLink:
    parent_file: str
    parent_kind: str
    parent_route_path: str
    parent_route_name: str
    child_component: str
    child_file: str
    props: tuple[str, ...]


@dataclass(frozen=True)
class BackendModel:
    class_name: str
    table_name: str
    module: str
    model_file: str


@dataclass(frozen=True)
class BackendModelRef:
    model_class: str
    table_name: str
    module: str
    model_file: str
    evidence_type: str
    evidence_file: str
    evidence_symbol: str
    confidence: str


@dataclass(frozen=True)
class ImportRef:
    file_path: str
    symbol: str


@dataclass(frozen=True)
class BackendFunction:
    name: str
    file_path: str
    body: str
    imports: dict[str, ImportRef]


@dataclass(frozen=True)
class BackendRoute:
    module: str
    router_var: str
    function: str
    method: str
    path: str
    api_file: str
    router_tags: tuple[str, ...]
    tag_evidence_file: str
    tag_evidence_symbol: str
    tag_evidence_state: str
    called_symbols: tuple[str, ...]
    model_refs: tuple[BackendModelRef, ...]
    confidence: str


@dataclass(frozen=True)
class MockFinding:
    source_file: str
    line: int
    reason: str
    snippet: str


@dataclass
class AuditState:
    frontend_routes: list[FrontendRoute] = field(default_factory=list)
    frontend_apis: list[FrontendApi] = field(default_factory=list)
    frontend_usages: list[FrontendUsage] = field(default_factory=list)
    component_links: list[ComponentLink] = field(default_factory=list)
    backend_routes: list[BackendRoute] = field(default_factory=list)
    mock_findings: list[MockFinding] = field(default_factory=list)
    table_by_module: dict[str, list[str]] = field(default_factory=dict)
    class_to_model: dict[str, BackendModel] = field(default_factory=dict)
    route_matches: dict[tuple[str, str], BackendRoute] = field(default_factory=dict)
