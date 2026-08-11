"""
File Path: /tools/plc/s7-virtual-plc/tests/test_runtime_identity_cli.py
Description: Runtime identity CLI and configuration priority tests
Main Features:
    - Verifies dry-run and serve expose the same explicit PLC identity inputs
    - Verifies simulator settings resolve CLI, OS environment, then tool .env values
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from cli.commands import build_parser  # noqa: E402
from core.config import resolve_setting  # noqa: E402


class RuntimeIdentityCliTests(unittest.TestCase):
    def test_dry_run_and_serve_accept_the_same_explicit_identity_options(self) -> None:
        parser = build_parser()
        for command in ("dry-run", "serve"):
            with self.subTest(command=command):
                args = parser.parse_args([command, "--rack", "0", "--slot", "1", "--port", "1102"])
                self.assertEqual(args.rack, "0")
                self.assertEqual(args.slot, "1")
                self.assertEqual(args.port, 1102)

    def test_setting_priority_is_cli_then_os_environment_then_tool_env(self) -> None:
        name = "PLC_SIM_RACK"
        tool_env = {name: "1"}
        operating_system = {name: "2"}

        self.assertEqual(resolve_setting(name, "3", environment=operating_system, tool_values=tool_env), "3")
        self.assertEqual(resolve_setting(name, None, environment=operating_system, tool_values=tool_env), "2")
        self.assertEqual(resolve_setting(name, None, environment={}, tool_values=tool_env), "1")
        self.assertIsNone(resolve_setting(name, None, environment={name: ""}, tool_values={name: ""}))


if __name__ == "__main__":
    unittest.main()
