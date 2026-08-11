# PLC 工具

PLC 工具组把审核过的工程输入转换为可选 Control Agent 使用的合同。它只做
离线准备，不连接真实 PLC，公开基线也不包含现场工作簿。

- `point-mapping/`：点位合同转换。
- `projection-mapping/`：字段到点位的复核。
- `snapshot-policy/`：raw/latest 策略转换。
- `s7-virtual-plc/`：本地模拟器支持。

每个工具的 `inputs/`、`outputs/` 为空。私有文件请放在独立工作区，运行转换
时显式传入路径。
