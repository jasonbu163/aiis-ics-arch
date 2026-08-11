# S7 虚拟 PLC

该工具运行本地 Snap7 兼容模拟器，用于只读开发检查。它消费显式提供的
`plc_points.yaml` 和可选模拟 profile，不连接物理 PLC，也不写入生产数据库。

公开基线的 `inputs/`、`outputs/` 保持为空。使用 `init-profile` 生成临时
profile，人工复核后显式传给 `dry-run` 或 `serve`：

```bash
uv run python plc/s7-virtual-plc/main.py init-profile \
  --profile-output /private/tmp/simulation-profile.xlsx
uv run python plc/s7-virtual-plc/main.py dry-run \
  --profile /private/tmp/simulation-profile.xlsx --rack 0 --slot 1
uv run python plc/s7-virtual-plc/main.py serve \
  --profile /private/tmp/simulation-profile.xlsx --rack 0 --slot 1 --port 1102
```

`PLC_SIM_PLC_KEY`、`PLC_SIM_RACK`、`PLC_SIM_SLOT` 标识模拟器合同；模拟器会
在接受 S7 会话前校验 called TSAP。开发阶段推荐使用 `1102` 端口。

该工具只能证明模拟器配置合同和读取路径，不能证明真实 CPU、现场网络、
连接数限制或 PLC 写入安全。
