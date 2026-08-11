"""
文件路径: /tools/plc/s7-virtual-plc/tests/test_cli_contract.py
功能描述: S7 虚拟 PLC CLI 合同测试
主要功能:
    - 验证裸入口只显示帮助
    - 验证错误命令不会回退到默认启动
    - 验证 profile 初始化默认不覆盖已有文件
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = TOOL_ROOT / "main.py"


class CliContractTests(unittest.TestCase):
    def test_bare_entry_prints_help_without_starting(self) -> None:
        result = self._run()

        self.assertEqual(result.returncode, 0)
        self.assertIn("S7 virtual PLC tool.", result.stdout)
        self.assertIn("init-profile", result.stdout)
        self.assertNotIn("s7_virtual_plc started", result.stdout)

    def test_unknown_command_fails_with_suggestion(self) -> None:
        result = self._run("init-profle")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Did you mean 'init-profile'", result.stderr)

    def test_port_flag_without_explicit_action_does_not_start(self) -> None:
        result = self._run("--port", "1102")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit command required", result.stderr)
        self.assertNotIn("s7_virtual_plc started", result.stdout)

    def test_init_profile_requires_overwrite_for_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "plc_points.yaml"
            profile_path = temp_path / "simulation_profile.xlsx"
            config_path.write_text(self._minimal_config(), encoding="utf-8")

            first = self._run(
                "init-profile",
                "--config",
                str(config_path),
                "--profile-output",
                str(profile_path),
            )
            second = self._run(
                "init-profile",
                "--config",
                str(config_path),
                "--profile-output",
                str(profile_path),
            )
            third = self._run(
                "init-profile",
                "--config",
                str(config_path),
                "--profile-output",
                str(profile_path),
                "--overwrite",
            )

        self.assertEqual(first.returncode, 0)
        self.assertTrue(profile_path.name.endswith(".xlsx"))
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("pass --overwrite", second.stderr)
        self.assertEqual(third.returncode, 0)

    def test_legacy_init_flag_is_rejected(self) -> None:
        result = self._run("--init")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit command required", result.stderr)
        self.assertNotIn("init_profile status=ok", result.stdout)

    def test_dry_run_rejects_mismatched_identity_before_loading_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "plc_points.yaml"
            config_path.write_text(self._runtime_config(), encoding="utf-8")

            result = self._run(
                "dry-run",
                "--config",
                str(config_path),
                "--profile",
                str(temp_path / "missing.xlsx"),
                "--rack",
                "0",
                "--slot",
                "2",
                "--port",
                "1102",
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PLC_SIM_SLOT=2 does not match PLC_1 slot=1", result.stderr)
        self.assertNotIn("profile", result.stderr.lower())
        self.assertNotIn("traceback", result.stderr.lower())

    def test_init_profile_rejects_unknown_plc_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "plc_points.yaml"
            config_path.write_text(self._runtime_config(), encoding="utf-8")

            result = self._run(
                "init-profile",
                "--config",
                str(config_path),
                "--plc-key",
                "PLC_2",
                "--profile-output",
                str(temp_path / "simulation_profile.xlsx"),
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PLC key not found: PLC_2", result.stderr)

    def test_dry_run_rejects_invalid_port_before_loading_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "plc_points.yaml"
            config_path.write_text(self._runtime_config(), encoding="utf-8")

            result = self._run(
                "dry-run",
                "--config",
                str(config_path),
                "--profile",
                str(temp_path / "missing.xlsx"),
                "--rack",
                "0",
                "--slot",
                "1",
                "--port",
                "0",
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("S7 TCP port must be between 1 and 65535", result.stderr)
        self.assertNotIn("profile", result.stderr.lower())

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MAIN_PY), *args],
            cwd=TOOL_ROOT.parents[2],
            text=True,
            capture_output=True,
            check=False,
        )

    def _minimal_config(self) -> str:
        return """\
PLC_1:
  groups:
    - name: Test_DB
      db_number: 1
      start: 0
      size: 2
      points:
        - name: DB1_Test_Int
          source_name: Test_Int
          type: Int
          offset: 0
          desc: Test point
"""

    def _runtime_config(self) -> str:
        return """\
PLC_1:
  rack: 0
  slot: 1
  groups:
    - name: Test_DB
      db_number: 1
      start: 0
      size: 2
      points:
        - name: DB1_Test_Int
          source_name: Test_Int
          type: Int
          offset: 0
          desc: Test point
"""


if __name__ == "__main__":
    unittest.main()
