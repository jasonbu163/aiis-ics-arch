"""
File Path: /tools/plc/s7-virtual-plc/src-python/core/identity.py
Description: Virtual PLC rack/slot identity resolution
Main Features:
    - Resolves a simulator-owned PLC identity from explicit rack and slot values
    - Validates the identity against the selected plc_points.yaml contract
    - Calculates the expected COTP called TSAP for strict handshake validation
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MAX_RACK = 7
MAX_SLOT = 31


@dataclass(frozen=True)
class VirtualPlcIdentity:
    """Resolved simulator identity used by dry-run and the resident server."""

    plc_key: str
    rack: int
    slot: int
    port: int
    expected_called_tsap: int


def expected_called_tsap(rack: int, slot: int) -> int:
    """Build the remote TSAP with the same formula used by the Control Agent."""

    return 0x0100 + rack * 0x20 + slot


def resolve_virtual_plc_identity(
    *,
    plc_key: str,
    plc_config: dict[str, Any],
    rack_value: str | int | None,
    slot_value: str | int | None,
    port: str | int | None,
) -> VirtualPlcIdentity:
    """Validate one simulator identity against its selected PLC contract."""

    rack = _parse_tsap_field(rack_value, "PLC_SIM_RACK", MAX_RACK)
    slot = _parse_tsap_field(slot_value, "PLC_SIM_SLOT", MAX_SLOT)
    configured_rack = _parse_tsap_field(plc_config.get("rack"), f"{plc_key} rack", MAX_RACK)
    configured_slot = _parse_tsap_field(plc_config.get("slot"), f"{plc_key} slot", MAX_SLOT)

    if rack != configured_rack:
        raise ValueError(f"PLC_SIM_RACK={rack} does not match {plc_key} rack={configured_rack}")
    if slot != configured_slot:
        raise ValueError(f"PLC_SIM_SLOT={slot} does not match {plc_key} slot={configured_slot}")
    parsed_port = _parse_port(port)

    return VirtualPlcIdentity(
        plc_key=plc_key,
        rack=rack,
        slot=slot,
        port=parsed_port,
        expected_called_tsap=expected_called_tsap(rack, slot),
    )


def _parse_tsap_field(value: str | int | None, label: str, maximum: int) -> int:
    if value is None or not str(value).strip():
        raise ValueError(f"{label} is required")
    try:
        parsed = int(str(value).strip(), 10)
    except ValueError as exc:
        raise ValueError(f"{label} must be a decimal integer") from exc
    if not 0 <= parsed <= maximum:
        raise ValueError(f"{label} must be between 0 and {maximum}")
    return parsed


def _parse_port(value: str | int | None) -> int:
    if value is None or not str(value).strip():
        raise ValueError("PLC_SIM_PORT is required")
    try:
        parsed = int(str(value).strip(), 10)
    except ValueError as exc:
        raise ValueError("PLC_SIM_PORT must be a decimal integer") from exc
    if not 1 <= parsed <= 65535:
        raise ValueError(f"S7 TCP port must be between 1 and 65535, got {parsed}")
    return parsed
