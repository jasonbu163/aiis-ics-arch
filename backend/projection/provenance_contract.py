"""
File Path: /backend/projection/provenance_contract.py
Description: Accepted PLC-to-production-line identity facts for Projection.
Main Features:
    - Shares the single-PLC B6 pilot identity across control and runtime paths
    - Keeps multi-PLC identity expansion behind the future C5.7 acceptance gate
"""
from __future__ import annotations


PILOT_PLC_DEVICE_IDENTITIES: dict[str, int] = {
    "PLC_1": 1,
}


def get_expected_device_id(plc_key: str) -> int | None:
    """Return the accepted production-line identity for the current pilot."""
    return PILOT_PLC_DEVICE_IDENTITIES.get(plc_key)
