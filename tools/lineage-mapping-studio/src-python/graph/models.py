"""
File Path: /tools/lineage-mapping-studio/src-python/graph/models.py
Description: Shared graph models and small value helpers.
Main Features:
  - Defines graph node and edge DTOs.
  - Provides stable node and edge ID helpers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ToolError(Exception):
    """Expected command failure for JSON Lines reporting."""


@dataclass(frozen=True)
class GraphNode:
    id: str
    kind: str
    title: str
    subtitle: str = ""
    evidence: str = ""


@dataclass(frozen=True)
class GraphEdge:
    id: str
    source: str
    target: str
    label: str
    evidence: str = ""


def value(raw: Any) -> str:
    if raw is None:
        return ""
    return str(raw).strip()


def split_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(";") if item.strip()]


def node_id(kind: str, raw: Any) -> str:
    return f"{kind}:{value(raw) or 'unknown'}"


def add_node(nodes: dict[str, GraphNode], node: GraphNode) -> None:
    nodes.setdefault(node.id, node)


def add_edge(edges: dict[str, GraphEdge], source: str, target: str, label: str, evidence: str = "") -> None:
    edge_id = f"{source}->{target}:{label}"
    edges.setdefault(edge_id, GraphEdge(edge_id, source, target, label, evidence))


def node_to_dict(node: GraphNode | dict[str, Any]) -> dict[str, Any]:
    if isinstance(node, dict):
        return node
    return {
        "id": node.id,
        "kind": node.kind,
        "title": node.title,
        "subtitle": node.subtitle,
        "evidence": node.evidence,
    }
