"""
文件路径: /tools/plc/point-mapping/tests/test_cli_commands.py
功能描述: point-mapping CLI 命令面测试
主要功能:
    - 验证子命令 help 展示命令专属参数
    - 验证旧兼容入口已移除
    - 验证拼错子命令不会误入其他解析路径
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from cli.commands import main  # noqa: E402


class CliCommandTests(unittest.TestCase):
    def test_top_level_help_does_not_advertise_legacy_compatibility(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["-h"]), 0)

        help_text = stdout.getvalue()
        self.assertIn("generate-yaml", help_text)
        self.assertNotIn("Legacy compatibility", help_text)

    def test_generate_yaml_help_exposes_source_options(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as caught:
            main(["generate-yaml", "-h"])

        self.assertEqual(caught.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("--db-source", help_text)
        self.assertIn("--udt-source", help_text)
        self.assertIn("--db-workbook", help_text)
        self.assertIn("--overwrite", help_text)
        self.assertNotIn("--workbook ", help_text)

    def test_generate_yaml_refuses_existing_output_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "plc_points.yaml"
            output_path.write_text("existing: true\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "generate-yaml",
                        "--db-workbook",
                        str(Path(temp_dir) / "missing.xlsx"),
                        "--plc-points-output",
                        str(output_path),
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("output YAML already exists", stdout.getvalue())
        self.assertIn("pass --overwrite", stdout.getvalue())

    def test_generate_yaml_overwrite_replaces_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "DB.xlsx"
            output_path = Path(temp_dir) / "plc_points.yaml"
            output_path.write_text("existing: true\n", encoding="utf-8")
            with pd.ExcelWriter(workbook_path) as writer:
                pd.DataFrame(
                    [
                        {
                            "sheet_name": "DB_Test",
                            "db_name": "DB_Test",
                            "db_number": 28,
                            "group_name": "DB_Test",
                            "enabled": True,
                        }
                    ]
                ).to_excel(writer, sheet_name="DB配置", index=False)
                pd.DataFrame(
                    [{"名称": "ActTemp_Z1", "数据类型": "Int", "偏移量": 20}]
                ).to_excel(writer, sheet_name="DB_Test", index=False)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "generate-yaml",
                        "--db-workbook",
                        str(workbook_path),
                        "--plc-points-output",
                        str(output_path),
                        "--overwrite",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn('"event": "complete"', stdout.getvalue())
            self.assertIn("DB28_ActTemp_Z1_Int", output_path.read_text(encoding="utf-8"))

    def test_old_workbook_alias_is_rejected(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            main(["generate-yaml", "--workbook", "DB.xlsx"])

        self.assertEqual(caught.exception.code, 2)
        self.assertIn("unrecognized arguments: --workbook", stderr.getvalue())

    def test_positional_legacy_workbook_path_is_rejected(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            main(["DB.xlsx"])

        self.assertEqual(caught.exception.code, 2)
        self.assertIn("unknown command 'DB.xlsx'", stderr.getvalue())

    def test_misspelled_subcommands_do_not_fall_back_to_legacy_help(self) -> None:
        examples = [
            ("init-db-confi", "init-db-config"),
            ("init-workboo", "init-workbook"),
            ("genrate-yaml", "generate-yaml"),
        ]
        for misspelled_command, expected_command in examples:
            with self.subTest(misspelled_command=misspelled_command):
                stderr = StringIO()
                with redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
                    main([misspelled_command, "-h"])

                self.assertEqual(caught.exception.code, 2)
                error_text = stderr.getvalue()
                self.assertIn(f"unknown command '{misspelled_command}'", error_text)
                self.assertIn(expected_command, error_text)


if __name__ == "__main__":
    unittest.main()
