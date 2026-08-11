#!/usr/bin/env python3
"""
文件路径: /tools/plc/snapshot-policy/main.py
功能描述: PLC 快照 raw 保留策略工具的薄 CLI 入口
"""
from __future__ import annotations

import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parent
SRC_PYTHON = TOOL_ROOT / "src-python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(SRC_PYTHON))

from cli.commands import main


if __name__ == "__main__":
    raise SystemExit(main())
