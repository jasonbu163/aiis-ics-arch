# AIIS ICS Architecture 工具

本目录保存 Core 与项目团队可复用的离线优先工程工具。工具只处理显式提供
的源文件，不主动获取项目数据、不连接 PLC/数据库服务，也不发布生成物。

## 工具分组

- `lineage-audit/`：界面到数据源的静态证据清单。
- `lineage-mapping-studio/`：本地可视化复核 lineage 证据。
- `plc/point-mapping/`：复核后的工作簿转 PLC 合同。
- `plc/projection-mapping/`：PLC 到 projection 的映射复核。
- `plc/snapshot-policy/`：raw/latest 快照策略转换。
- `plc/s7-virtual-plc/`：开发检查用本地模拟器。

各工具的 `inputs/` 和 `outputs/` 默认为空。`config/` 中的 YAML 只是脱敏的
结构示例，不是现场合同。工作簿、点位表、映射、日志和生成报告必须放在
公开源码树之外。

## 本地检查

```bash
uv lock --check
uv run python -m compileall -q lineage-audit lineage-mapping-studio plc
uv run pytest -q
```

需要输入的测试请使用单独审核过的 fixture 目录。
