"""
文件路径: /tools/plc/s7-virtual-plc/tests/test_word_support.py
功能描述: S7 虚拟 PLC Word 类型支持测试
主要功能:
    - 验证 Word 被当作无符号 16 位数值处理
    - 验证 Word 写入 DB 内存时使用 2 字节大端编码
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src-python"))

from core.loader import point_size  # noqa: E402
from core.models import NUMERIC_TYPES, TYPE_SIZES, VirtualPoint  # noqa: E402
from core.profile import default_simulated_value  # noqa: E402
from core.runtime import apply_numeric_type, write_value  # noqa: E402


class WordSupportTests(unittest.TestCase):
    def test_word_is_a_two_byte_numeric_type(self) -> None:
        self.assertIn("Word", NUMERIC_TYPES)
        self.assertEqual(TYPE_SIZES["Word"], 2)
        self.assertEqual(point_size({"type": "Word"}), 2)

    def test_word_values_are_clamped_to_unsigned_16_bit_range(self) -> None:
        point = self._point()

        self.assertEqual(apply_numeric_type(point, -1), 0)
        self.assertEqual(apply_numeric_type(point, 65535.4), 65535)
        self.assertEqual(apply_numeric_type(point, 70000), 65535)
        self.assertIsInstance(default_simulated_value(point, tick=0, started_at=0), int)

    def test_word_write_uses_big_endian_two_byte_storage(self) -> None:
        point = self._point(offset=4)
        memory = bytearray(8)

        write_value(memory, point, 0x1234)

        self.assertEqual(memory[4:6], b"\x12\x34")

    def _point(self, offset: int = 0) -> VirtualPoint:
        return VirtualPoint(
            name="DB28_StatusWord_Word",
            data_type="Word",
            offset=offset,
            db_number=28,
            group_name="DB_Test",
        )


if __name__ == "__main__":
    unittest.main()
