"""
文件路径: /tools/plc/snapshot-policy/tests/test_cli_contract.py
功能描述: PLC 快照策略工具 CLI 合同测试
主要功能:
    - 验证裸入口只显示帮助
    - 验证错误命令不会回退到默认生成
    - 验证 v2 raw/latest 策略 YAML 生成
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import yaml


TOOL_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = TOOL_ROOT / "main.py"


class SnapshotPolicyCliTests(unittest.TestCase):
    def test_bare_entry_prints_help_without_writing(self) -> None:
        result = self._run()

        self.assertEqual(result.returncode, 0)
        self.assertIn("PLC snapshot policy tool.", result.stdout)
        self.assertIn("init-workbook", result.stdout)
        self.assertIn("generate-yaml", result.stdout)
        self.assertNotIn("snapshot_policy_start", result.stdout)

    def test_unknown_command_fails_with_suggestion(self) -> None:
        result = self._run("init-workboo")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Did you mean 'init-workbook'", result.stderr)

    def test_init_workbook_requires_overwrite_for_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            plc_points_path = temp_path / "plc_points.yaml"
            workbook_path = temp_path / "plc_snapshot_policy.xlsx"
            plc_points_path.write_text(self._minimal_config(), encoding="utf-8")

            first = self._run(
                "init-workbook",
                "--plc-points",
                str(plc_points_path),
                "--workbook-output",
                str(workbook_path),
            )
            second = self._run(
                "init-workbook",
                "--plc-points",
                str(plc_points_path),
                "--workbook-output",
                str(workbook_path),
            )
            third = self._run(
                "init-workbook",
                "--plc-points",
                str(plc_points_path),
                "--workbook-output",
                str(workbook_path),
                "--overwrite",
            )

        self.assertEqual(first.returncode, 0)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("pass --overwrite", second.stderr)
        self.assertEqual(third.returncode, 0)

    def test_generate_yaml_emits_v2_raw_latest_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            plc_points_path = temp_path / "plc_points.yaml"
            workbook_path = temp_path / "plc_snapshot_policy.xlsx"
            policy_path = temp_path / "plc_snapshot_policy.yaml"
            plc_points_path.write_text(self._minimal_config(), encoding="utf-8")

            init_result = self._run(
                "init-workbook",
                "--plc-points",
                str(plc_points_path),
                "--workbook-output",
                str(workbook_path),
            )
            generate_result = self._run(
                "generate-yaml",
                "--plc-points",
                str(plc_points_path),
                "--workbook",
                str(workbook_path),
                "--policy-output",
                str(policy_path),
            )

            payload = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

        self.assertEqual(init_result.returncode, 0)
        self.assertEqual(generate_result.returncode, 0)
        plc = payload["PLC_1"]
        self.assertEqual(plc["snapshot_policy_version"], 2)
        self.assertEqual(plc["point_count"], 2)
        self.assertEqual(plc["raw_point_count"], 1)
        self.assertEqual(plc["latest_point_count"], 2)
        first_point = plc["groups"][0]["points"][0]
        self.assertNotIn("plc_key", first_point)
        self.assertEqual(first_point["desc"], "温度")
        self.assertIn("raw_enabled", first_point)
        self.assertIn("raw_policy", first_point)
        self.assertIn("latest_enabled", first_point)
        self.assertNotIn("history_enabled", first_point)
        self.assertNotIn("policy", first_point)

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
      size: 4
      points:
        - name: DB1_Temperature_Int
          source_name: Temperature
          type: Int
          offset: 0
          desc: 温度
        - name: DB1_Status_Word
          source_name: Status
          type: Word
          offset: 2
          desc: Status word
"""


if __name__ == "__main__":
    unittest.main()
