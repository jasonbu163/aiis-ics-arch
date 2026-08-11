#!/usr/bin/env python3
"""
文件路径: /tools/plc/point-mapping/main.py
功能描述: point-mapping 工具的薄 CLI 入口
"""
from __future__ import annotations

from pathlib import Path
import sys


TOOL_ROOT = Path(__file__).resolve().parent
PYTHON_SRC = TOOL_ROOT / "src-python"
if str(PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(PYTHON_SRC))

from cli.commands import main


if __name__ == "__main__":
    raise SystemExit(main())
