#!/usr/bin/env python3
"""
File Path: /tools/lineage-mapping-studio/main.py
Description: Thin Python command surface for the lineage mapping studio.
Main Features:
    - Adds src-python to the import path.
    - Delegates graph commands to src-python/cli/commands.py.
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
