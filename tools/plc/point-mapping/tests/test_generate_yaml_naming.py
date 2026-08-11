"""Sanitized tests for deterministic PLC YAML naming."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from converter.converter import convert_excel_to_yaml  # noqa: E402


def write_workbook(path: Path, rows: list[dict[str, object]]) -> None:
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(
            [{
                "sheet_name": "Example_Data",
                "db_name": "Example_Data",
                "db_number": 7,
                "group_name": "Example_Data",
                "enabled": True,
            }]
        ).to_excel(writer, sheet_name="DB配置", index=False)
        pd.DataFrame(rows).to_excel(writer, sheet_name="Example_Data", index=False)


class GenerateYamlNamingTests(unittest.TestCase):
    def test_source_names_include_db_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workbook = root / "example.xlsx"
            output = root / "plc_points.yaml"
            write_workbook(
                workbook,
                [
                    {"名称": "StatusWord", "数据类型": "Word", "偏移量": 0},
                    {"名称": "Temperature", "数据类型": "Real", "偏移量": 2},
                ],
            )
            result = convert_excel_to_yaml(workbook, output, plc_ip="127.0.0.1")

        points = result["PLC_1"]["groups"][0]["points"]
        self.assertEqual({point["name"] for point in points}, {"DB7_StatusWord_Word", "DB7_Temperature_Real"})
        self.assertEqual(result["PLC_1"]["point_count"], 2)
        self.assertEqual(result["PLC_1"]["ip"], "127.0.0.1")

    def test_duplicate_generated_names_fall_back_to_addresses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workbook = root / "duplicate.xlsx"
            output = root / "plc_points.yaml"
            write_workbook(
                workbook,
                [
                    {"名称": "Value", "数据类型": "Real", "偏移量": 0},
                    {"名称": "Value", "数据类型": "Real", "偏移量": 4},
                ],
            )
            result = convert_excel_to_yaml(workbook, output)

        points = result["PLC_1"]["groups"][0]["points"]
        self.assertEqual({point["name"] for point in points}, {"DB7_B0_Real", "DB7_B4_Real"})

    def test_unsupported_rows_are_ignored_without_external_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workbook = root / "unsupported.xlsx"
            output = root / "plc_points.yaml"
            write_workbook(
                workbook,
                [
                    {"名称": "Value", "数据类型": "Real", "偏移量": 0},
                    {"名称": "Unknown", "数据类型": "Opaque", "偏移量": 4},
                ],
            )
            result = convert_excel_to_yaml(workbook, output)

        points = result["PLC_1"]["groups"][0]["points"]
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]["name"], "DB7_Value_Real")


if __name__ == "__main__":
    unittest.main()
