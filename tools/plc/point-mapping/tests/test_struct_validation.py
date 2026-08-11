"""Sanitized tests for DB/UDT-to-workbook structure validation."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd
from openpyxl import load_workbook


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from validation.struct_validation import validate_workbook_source_context  # noqa: E402


NESTED_DB_SOURCE = '''
DATA_BLOCK "ExampleBlock"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
STRUCT
  Outer : Struct
    Inner : Struct
      Value : Real;
    END_STRUCT;
  END_STRUCT;
END_STRUCT;
END_DATA_BLOCK
'''


def write_workbook(path: Path, rows: list[dict[str, object]]) -> None:
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(
            [{"sheet_name": "ExampleBlock", "db_name": "ExampleBlock", "enabled": True}]
        ).to_excel(writer, sheet_name="DB配置", index=False)
        pd.DataFrame(rows).to_excel(writer, sheet_name="ExampleBlock", index=False)


class StructValidationTests(unittest.TestCase):
    def test_sanitized_nested_source_matches_workbook_rows(self) -> None:
        rows = [
            {"名称": "Outer", "数据类型": "Struct", "偏移量": ""},
            {"名称": "Inner", "数据类型": "Struct", "偏移量": ""},
            {"名称": "Value", "数据类型": "Real", "偏移量": 0},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_source = root / "example.db"
            workbook = root / "example.xlsx"
            db_source.write_text(NESTED_DB_SOURCE, encoding="utf-8")
            write_workbook(workbook, rows)

            result = validate_workbook_source_context(workbook, db_source, None)

        self.assertTrue(result.ok, result.samples)
        self.assertEqual(result.summary["db_blocks"], 1)
        self.assertEqual(result.summary["workbook_rows"], 3)
        self.assertIn("Outer.Inner.Value", result.samples["nested_paths"])

    def test_partial_workbook_rows_are_rejected(self) -> None:
        rows = [
            {"名称": "Outer", "数据类型": "Struct", "偏移量": ""},
            {"名称": "Inner", "数据类型": "Struct", "偏移量": ""},
            {"名称": "Value", "数据类型": "Real", "偏移量": 0},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_source = root / "example.db"
            workbook = root / "example.xlsx"
            db_source.write_text(NESTED_DB_SOURCE, encoding="utf-8")
            write_workbook(workbook, rows)
            loaded = load_workbook(workbook)
            sheet = loaded["ExampleBlock"]
            sheet.delete_rows(4)
            loaded.save(workbook)

            result = validate_workbook_source_context(workbook, db_source, None)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.samples["errors"][0],
            "ExampleBlock: source row count 3 != workbook row count 2",
        )

    def test_missing_udt_source_reports_an_explicit_error(self) -> None:
        db_source_text = '''
DATA_BLOCK "ExampleBlock"
VERSION : 0.1
STRUCT
  External : ExampleType;
END_STRUCT;
END_DATA_BLOCK
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_source = root / "example.db"
            workbook = root / "example.xlsx"
            db_source.write_text(db_source_text, encoding="utf-8")
            write_workbook(
                workbook,
                [{"名称": "External", "数据类型": "ExampleType", "偏移量": 0}],
            )

            result = validate_workbook_source_context(workbook, db_source, None)

        self.assertFalse(result.ok)
        self.assertIn("missing UDT definition", result.samples["errors"][0])


if __name__ == "__main__":
    unittest.main()
