# Automation World

[English](README.md)

AW 统一管理现场采集与语义映射桌面工程。

| 工程 | 当前职责 | 维护方向 |
| --- | --- | --- |
| [CA](control-agent/README.zh-CN.md) | 迁入后的原 Control Agent，保持 raw/latest 数据库快照兼容合同 | 迁移验证后冻结，精确来源见任务 receipt |
| [DAA](data-acquisition-agent/README.zh-CN.md) | SQLite配置权威、采集/解码/诊断；继承的无界面入口已退役 | 后续采集功能的开发入口；新 AW API 尚未接入 |
| [SMA](semantic-mapping-agent/README.zh-CN.md) | 只读 HTTP 事实、API材料、目标API、值规则、映射预览与运行诊断 | 消费 CU 公共 UI 源码；依赖兼容 Backend HTTP 合同，交付状态归 SMA PLAN |

CA 冻结不停止现有运行或切换生产链路。原 DTB TSS 完整保留；DAA/SMA 不依赖 CA/TSS checkout 或依赖目录。不持续覆盖同步两份源码。SMA 不包含客户设备/场景页、SQL/legacy Projection IPC 或跨仓帮助生成。

## 独立工程与配置

各应用在自身目录执行 `pnpm install --frozen-lockfile`、`pnpm build`、`cargo test --manifest-path src-tauri/Cargo.toml --locked`、`pnpm tauri dev`。DAA 用 `pnpm tauri:dev` 可开启继承驱动编译，外部门禁仍由配置控制。移动源码后依赖与target需重建，不能用旧绝对路径缓存作为运行证明。

| 工程 | identifier | dev / preview | env / localStorage |
| --- | --- | --- | --- |
| CA | com.aiis.ics.controlagent | 15190 / 14190 | 原 CONTROL_AGENT_* / 原keys |
| DAA | com.aiis.aw.dataacquisitionagent | 15191 / 14191 | DAA_* / daa.* |
| SMA | com.aiis.aw.semanticmappingagent | 15192 / 14192 | SMA_* / sma.* |

DAA/SMA 只读取自身根 `.env` 或显式绝对 `DAA_ENV_FILE` / `SMA_ENV_FILE`；不搜索cwd/parent/root.env。相对DAA YAML锚定自身根，日志/输出归独立identifier的本机data目录；SMA startup JSON归本机app-data。显式绝对 `DAA_PROFILE_DIR` / `SMA_PROFILE_DIR` 可用于临时验证。真实配置、日志、输出不提交。SMA Backend默认空且HTTP gate关闭；Simulation/Mapping首启auto-start=false，不迁移CA/TSS旧偏好。DAA的YAML仅为一次性来源，SQLite配置/本地历史见下文；JSON仍承担SMA既有技术启动偏好，SMA映射存储不在本变更中。

## 演进与证据

当前是S2工程前置初始化。S1配置/事实/映射回执和业务API合同、新AW事实上传、业务闭环、后续shared UI/集成目标由独立任务处理。工程可启动不代表这些目标已接通。当前任务和下一gate见 [PLAN](PLAN.zh-CN.md)，唯一 owning bundle 在根 [ARCH-AW-001](../plans/ARCH-AW-001-agent-foundation/spec.md)。

CA 预览使用 `pnpm preview --strictPort`，在保留冻结源码的前提下使固定14190端口冲突时失败。DAA/SMA的dev/preview在自身Vite配置中固定strictPort。

DAA按普通`pnpm tauri dev`进入SQLite新版；[2026-10-30最终验收](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)确认阶段B在本次受控DS联调范围完成。DAA-003一次性YAML迁入现为历史能力，DAA-007已退出普通迁入链，新空profile保持空配置，私有回执及历史保留。业务配置由UI+SQLite管理。实际边界见[DAA README](data-acquisition-agent/README.zh-CN.md)，步骤见[联调手册](data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md)。历史证据限制和来源未明事项继续跟踪，阶段C、自动启动策略、Backend/SMA及真实现场另项。
