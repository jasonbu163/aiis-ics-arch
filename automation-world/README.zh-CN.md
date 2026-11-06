# Automation World

[English](README.md)

AW 统一管理现场采集与语义映射桌面工程。

| 工程 | 当前职责 | 维护方向 |
| --- | --- | --- |
| [CA](control-agent/README.zh-CN.md) | 迁入后的原 Control Agent，保持 raw/latest 数据库快照兼容合同 | 迁移验证后冻结，精确来源见任务 receipt |
| [DAA](data-acquisition-agent/README.zh-CN.md) | SQLite配置权威、采集/解码/诊断；继承的无界面入口已退役 | 后续采集功能的开发入口；新 AW API 尚未接入 |
| [SMA](semantic-mapping-agent/README.zh-CN.md) | 本地连接/材料/目标/规则/映射配置和纯预览，以及门禁下只读事实检查 | 消费CU公共UI源码；当前本地配置阶段关闭正常投递，交付状态归SMA PLAN |

CA 冻结不停止现有运行或切换生产链路。原 DTB TSS 完整保留；DAA/SMA 不依赖 CA/TSS checkout 或依赖目录。不持续覆盖同步两份源码。SMA 不包含客户设备/场景页、SQL/legacy Projection IPC 或跨仓帮助生成。

## 独立工程与配置

各应用在自身目录执行 `pnpm install --frozen-lockfile`、`pnpm build`、`cargo test --manifest-path src-tauri/Cargo.toml --locked`、`pnpm tauri dev`。普通`pnpm tauri dev`由各应用Tauri配置传递所需驱动features，启动连接/采集仍为停止。移动源码后依赖与target需重建，不能用旧绝对路径缓存作为运行证明。

| 工程 | identifier | dev / preview | env / localStorage |
| --- | --- | --- | --- |
| CA | com.aiis.ics.controlagent | 15190 / 14190 | 原 CONTROL_AGENT_* / 原keys |
| DAA | com.aiis.aw.dataacquisitionagent | 15191 / 14191 | DAA_* / daa.* |
| SMA | com.aiis.aw.semanticmappingagent | 15192 / 14192 | SMA_* / sma.* |

DAA/SMA只读取自身根`.env`或显式绝对`DAA_ENV_FILE` / `SMA_ENV_FILE`，不搜索父目录。绝对`DAA_PROFILE_DIR` / `SMA_PROFILE_DIR`选择独立本地数据。DAA的UI/Rust拥有`config.sqlite` / `runtime.sqlite`；普通YAML runtime/迁入及直库writer已退役，历史私有回执受保护。SMA Rust拥有`configuration.sqlite3`中的完整单文档及revision/CAS；技术启动JSON与`sma.*` UI偏好独立，均不能授权投递。Simulation、事实生产和内置帮助已退役。正常manual/start/resume/auto-start在HTTP/spawn前拒绝，旧偏好或HTTP gate开启也不能放行。配置维护/纯预览离线完成，显式只读HTTP检查仍受自身gate控制。真实配置和日志不提交。

## 演进与证据

截至2026-11-05，DAA受控本地阶段B和SMA清理/CU已获Owner接受；SMA本地配置/纯预览通过QA2、待终验。[事实provider](../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)和[typed业务provider](../contracts/published/http-api/business-integration-v1/README.zh-CN.md)通过隔离MySQL A+B验证，Owner终验及真实采用待定。DAA上传/ACK和SMA本地GET→POST执行/可靠投递尚未接通。当前任务和下一gate见[PLAN](PLAN.zh-CN.md)；[ARCH-AW-001](../plans/ARCH-AW-001-agent-foundation/spec.md)只拥有初始化历史，不承载后续全部工作。

CA 预览使用 `pnpm preview --strictPort`，在保留冻结源码的前提下使固定14190端口冲突时失败。DAA/SMA的dev/preview在自身Vite配置中固定strictPort。

DAA按普通`pnpm tauri dev`进入SQLite新版；[2026-10-30最终验收](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)确认阶段B在本次受控DS联调范围完成。DAA-003一次性YAML迁入现为历史能力，DAA-007已退出普通迁入链，新空profile保持空配置，私有回执及历史保留。业务配置由UI+SQLite管理。实际边界见[DAA README](data-acquisition-agent/README.zh-CN.md)，步骤见[联调手册](data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md)。历史证据限制和来源未明事项继续跟踪，阶段C、自动启动策略、Backend/SMA及真实现场另项。
