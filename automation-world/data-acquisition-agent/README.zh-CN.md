# AIIS Data Acquisition Agent

[English](README.md) · [使用手册](USER_GUIDE.zh-CN.md) · [任务计划](PLAN.zh-CN.md)

DAA 是独立的现场采集程序：从 PLC 或模拟器读取点位，先保存本机样本，再按配置上报到后端。采集和上报分别控制。完整操作、合成示例、两种手测及故障处理见[使用手册](USER_GUIDE.zh-CN.md)。后端来源登记、第三方发送和读取见[采集数据通用指南](../../docs/acquisition-data-guide.zh-CN.md)。

## 启动

在仓库根目录运行：

```sh
cd automation-world/data-acquisition-agent
pnpm install --frozen-lockfile
pnpm tauri dev
```

依赖安装后，从 DAA 工程目录用 `pnpm tauri dev` 启动。普通 Tauri 配置已传递 S7 驱动 feature，无需另填。采集和上报默认停止；工作台可分别开启下次启动时自动运行。保存或激活配置本身不会连接或启动。

## 配置权威与启动

源码开发读取本应用根 `.env`；需要时由使用者仅在文件不存在时手工复制 `.env.example`，已有文件先核对、不覆盖。`DAA_PROFILE_DIR` 选择独立存储根：非空进程值优先于所选 `.env` 的非空值，否则使用应用默认目录；高级 `DAA_ENV_FILE` 可显式选择可读文件，错误不回退。路径须为绝对字面路径，不展开 `~` 或环境变量。空值不是空目录。各应用 profile 分开；开发或构建不会自动隔离数据。安装版 `.env` 发现与分发不在此合同内。

PLC、点位、组和存储配置由 UI 与本机 SQLite 管理。旧 YAML 自动迁入、直库 writer 和旧运行入口已退役；普通启动不读取旧 YAML。正常进程无需额外配置读取许可；高级进程变量 `DAA_PLC_READ_ALLOWED` 若显式设置为 false、空白或非法值则阻止读取，所选 `.env` 中的同名旧键不覆盖该限制。

已有兼容 profile 可继续使用，但切换前必须核对实际目录。新空 profile 采用 config2/runtime4；冷态 runtime2/3 按原条件只支持本地采集和历史，不自动升级上报。保留原配置、样本、journal 和凭据；身份、时间或 schema 不符时按提示停止，勿手工修改原库。详见[使用手册](USER_GUIDE.zh-CN.md#1-启动并确认目录)和[本地存储说明](src-tauri/src/infrastructure/local_store/README.zh-CN.md)。

## 状态与边界

[DAA-007 r2](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) 于 2026-10-30 获 Human Owner 验收，阶段 B 仅在该受控 DS 联调范围内完成；历史 checkpoint 缺失和来源未明事项仍按原任务记录。DAA-010 样本上报与 DAA-013 多 PLC 身份的具体版本和核验状态见 [DAA 计划](PLAN.zh-CN.md)。此次手册不改变 DAA-010 r5 的独立失败记录、Windows 原生待验证状态、完整阶段 C 或实际环境采用的各自 gate。

本地样本、上报队列和可靠回执保留在所选 profile；只有与样本匹配的可靠回执才能确认上报。真实设备、实际数据库迁移、部署和生产运行按各自授权办理。
