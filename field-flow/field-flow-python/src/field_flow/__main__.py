"""模块入口仅委托CLI；导入无IO。"""
from field_flow.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
