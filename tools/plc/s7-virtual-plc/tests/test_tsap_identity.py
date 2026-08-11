"""
File Path: /tools/plc/s7-virtual-plc/tests/test_tsap_identity.py
Description: S7 virtual PLC identity validation tests
Main Features:
    - Verifies rack/slot identity resolution against the selected PLC contract
    - Verifies unknown PLC keys fail closed instead of falling back
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from core.identity import resolve_virtual_plc_identity  # noqa: E402
from core.loader import load_virtual_areas  # noqa: E402


class TsapIdentityTests(unittest.TestCase):
    def test_matching_contract_creates_expected_called_tsap(self) -> None:
        identity = resolve_virtual_plc_identity(
            plc_key="PLC_1",
            plc_config={"rack": 0, "slot": 1},
            rack_value="0",
            slot_value="1",
            port=1102,
        )

        self.assertEqual(identity.plc_key, "PLC_1")
        self.assertEqual(identity.rack, 0)
        self.assertEqual(identity.slot, 1)
        self.assertEqual(identity.port, 1102)
        self.assertEqual(identity.expected_called_tsap, 0x0101)

    def test_missing_rack_or_slot_fails_closed(self) -> None:
        for rack_value, slot_value in ((None, "1"), ("0", None)):
            with self.subTest(rack_value=rack_value, slot_value=slot_value):
                with self.assertRaisesRegex(ValueError, "PLC_SIM_(RACK|SLOT)"):
                    resolve_virtual_plc_identity(
                        plc_key="PLC_1",
                        plc_config={"rack": 0, "slot": 1},
                        rack_value=rack_value,
                        slot_value=slot_value,
                        port=1102,
                    )

    def test_out_of_range_rack_or_slot_fails_closed(self) -> None:
        for rack_value, slot_value in (("8", "1"), ("0", "32"), ("-1", "1"), ("0", "nope")):
            with self.subTest(rack_value=rack_value, slot_value=slot_value):
                with self.assertRaises(ValueError):
                    resolve_virtual_plc_identity(
                        plc_key="PLC_1",
                        plc_config={"rack": 0, "slot": 1},
                        rack_value=rack_value,
                        slot_value=slot_value,
                        port=1102,
                    )

    def test_contract_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match PLC_1"):
            resolve_virtual_plc_identity(
                plc_key="PLC_1",
                plc_config={"rack": 0, "slot": 1},
                rack_value="0",
                slot_value="2",
                port=1102,
            )

    def test_missing_yaml_rack_or_slot_fails_closed(self) -> None:
        for plc_config in ({"slot": 1}, {"rack": 0}):
            with self.subTest(plc_config=plc_config):
                with self.assertRaisesRegex(ValueError, "PLC_1 (rack|slot) is required"):
                    resolve_virtual_plc_identity(
                        plc_key="PLC_1",
                        plc_config=plc_config,
                        rack_value="0",
                        slot_value="1",
                        port=1102,
                    )

    def test_invalid_port_fails_closed(self) -> None:
        for port in (None, "invalid", 0, 65536):
            with self.subTest(port=port):
                with self.assertRaises(ValueError):
                    resolve_virtual_plc_identity(
                        plc_key="PLC_1",
                        plc_config={"rack": 0, "slot": 1},
                        rack_value="0",
                        slot_value="1",
                        port=port,
                    )

    def test_unknown_plc_key_does_not_fall_back_to_first_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "plc_points.yaml"
            config_path.write_text(
                """\
PLC_1:
  rack: 0
  slot: 1
  groups:
    - name: Test_DB
      db_number: 1
      start: 0
      size: 2
      points: []
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "PLC key not found: PLC_2"):
                load_virtual_areas(config_path, "PLC_2")


if __name__ == "__main__":
    unittest.main()
