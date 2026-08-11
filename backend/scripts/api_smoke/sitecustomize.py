"""
文件路径: /backend/scripts/api_smoke/sitecustomize.py
功能描述: API 冒烟脚本运行路径引导
主要功能:
    - 将 backend 根目录加入 Python import path
    - 支持分类脚本从 backend 目录直接运行
"""
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
