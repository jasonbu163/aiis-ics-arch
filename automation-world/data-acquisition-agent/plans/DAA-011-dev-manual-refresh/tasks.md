Task ID: DAA-011
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r1 QA1 两项返工与增量自检已完成，交新的 fresh-context Verification 复验
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# 项目 dev 人工操作指南开发记录

## 1. 批准依据与实施面

Human Owner 批准的 [DAA-011 r1](spec.md) 登记后 SHA-256 为 `674c0880f1e700f2d4104458f7a096c56f36565b791bf59a5552e1604c0551d1`。Development 在正式工作树 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 实施。HEAD 只用于定位工作树；候选包含本来就未提交的文件变化，精确版本以下列文件 SHA 为准。

本角色写入两份既有手册和本 `tasks.md`：

| 文件 | 实施前 SHA-256 | 本次候选 SHA-256 |
| --- | --- | --- |
| `STAGE_C_GUIDE.md` | `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a` | `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58` |
| `STAGE_C_GUIDE.zh-CN.md` | `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769` | `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065` |

两份手册在 Development 开始时均已是 dirty 状态。本次以当时完整工作树文件作为基线，只替换顶部过时提示、增加当前项目 dev 说明和历史分区提示；`m01-launch` 起的历史内容逐字节保留。并行任务的其他 dirty 文件不属于本角色写入面。

## 2. 实施与源码依据

| 需求 | 完成情况 |
| --- | --- |
| R01 / AC01 | 两种项目 dev 运行方式、API `8000`、Web `5190`、MySQL `3307`、模拟 S7 `31281` 和端口覆盖说明放在手册开头。启动文档链接指向仓库 `INITIALIZATION`。 |
| R02 / AC01–02 | 两个 `.env` 的 profile 选择使用绝对路径模板，说明进程变量优先级、空目录初始化与兼容配置复用；DS 与 DAA 均使用 `pnpm tauri dev`。按单实例、DB21、三点及 1000ms 组给出 DS 导入、地址/命名/策略确认、版本加载，再到 DAA 导入、分组、激活及本地历史核对的步骤。 |
| R03 / AC03 | 当前步骤结束于本地历史。新版 `/samples`、相同接口处理实时与补传、测试来源与机器凭据、`committed` / `created` / `duplicate`、Web 核对及恢复用例明确留给 DAA-010 后续范围。 |
| R04 / AC04 | 旧 B-RUN-01 环境在新标题下标为历史，说明专用服务及容器已退役；原地址、正文、命令、证据约束和已有锚点保留。 |

静态走读了 [DS 导入面板](../../../device-simulator/src/app/simulator/components/SourceImportPanel.vue)、[DS 点位页面](../../../device-simulator/src/app/simulator/views/points/index.vue)、[DS 导入默认值](../../../device-simulator/runtime/src/services/source_import.rs)、[DS 策略编辑器](../../../device-simulator/src/app/simulator/components/PolicyEditor.vue)、[DAA 导入面板](../../src/app/plc/components/SourceImportPanel.vue)、[DAA 组操作](../../src/console/composables/useLocalAcquisitionConsole.ts)、中英文 locale、[受控样例](../../src-tauri/tests/fixtures/source-import-minimal/minimal.db)和 [UDT](../../src-tauri/tests/fixtures/source-import-minimal/minimal.udt)。该样例标准布局、初值及运行顺序也与原 [M01 表和操作](../../STAGE_C_GUIDE.zh-CN.md#m01-launch)核对；导入样例的初值由操作者在 DS 显式设置。项目 v2 API、回执及 machine Bearer 以[公开合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)为依据；当前 DAA `/batches` 路径见 [HTTP 适配器](../../src-tauri/src/infrastructure/facts_http.rs)。

## 3. Development 自检

执行日期为 2026-11-11，环境为 macOS 工作树。下列检查均为 Development 自检，不是独立 Verification：

| 命令 | 结果 |
| --- | --- |
| `python3 /private/tmp/daa011-r1-guide-baseline-1es8eomg/verify_docs.py` | exit 0。两份手册新增部分共 30 个本地链接及锚点可达，4 个 zsh 代码块通过 `zsh -n`；必要端口、profile 键、样例、v2 路径和回执词齐全；旧后缀与实施前基线逐字节一致。 |
| `git diff --check -- automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md` | exit 0。 |
| `shasum -a 256 automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md automation-world/data-acquisition-agent/plans/DAA-011-dev-manual-refresh/spec.md` | exit 0，结果见第 1 节。 |
| `git status --short -- automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md automation-world/data-acquisition-agent/plans/DAA-011-dev-manual-refresh` | exit 0。两份手册为 `M`，任务目录为 `??`，与本次工作树交付形式一致。 |

英文 `m01-launch` 及后续字节为 22515，SHA-256 `7dbafc2ad934b2e50f52241d71cc22e837a407a33c94fca9914d195a17514536`；中文后缀为 20130 字节，SHA-256 `476b0732673347a25ec01b2cc44cf08b63e2b5d1ba3cc7d8b7bed21fa6d1f916`。自检未执行 UI 或启动命令，也未进行 HTTP、数据库、Docker、PLC 或任何实际采集。此文档任务未更改运行代码，未重复构建或阶段 B 测试。

## 4. 临时资源与交接限制

Development 创建 `/private/tmp/daa011-r1-guide-baseline-1es8eomg`，包含两份实施前手册和 `verify_docs.py`。它只用于对照已经存在的工作树文件及静态检查；保留至独立核验结束，由协调方确认无证据依赖后清理。基线及后缀摘要、命令与结果已记录在本文件。

未修改 SQLite、`.env`、旧 profile、数据库卷、其它任务记录、代码或本任务 `spec.md`；未清理旧归档。当前源代码仍使用旧版上传适配器，DAA-010 新版实现、项目环境实际人工采样、新版上报及完整阶段 C 均不由本文档自检证明。请 fresh-context Verification 按 r1 四项 AC 检查候选、历史基线和当前权威来源，并单独记录 verdict 与剩余限制。

## 5. QA1 返工与重新交接

独立 [QA1](checklist.md) 的 `qa_failed` 保留。F-QA1-001 指出两语手册在新版适配后的登记和写入步骤缺少实际联调获准条件；F-QA1-002 指出首次交接候选把历史资源写成已退役，但任务持久记录不足以佐证该组资源状态。第 2 节 R04 中“专用服务及容器已退役”保留为首次交接时的描述，本次撤销这一未证实结论。

返工仅调整两语手册开头、上报接续段和历史区导语。上报段明确 DAA-010 完成新版适配且实际联调获准后再登记与写入；历史导语保留 `18281`、旧专用服务、容器、路径和命令的追溯说明，并引导当前操作者使用前面的项目 dev 步骤。旧 `m01-launch` 起的内容保持原字节。

| 文件 | QA1 候选 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| `STAGE_C_GUIDE.md` | `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58` | `9df1cd0a8b08372caad39d4b9ae5e62f68490864850b17a7801a314e13a2fe84` |
| `STAGE_C_GUIDE.zh-CN.md` | `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065` | `892b83f79cd0f8e24f7751e802f1567d697cc4f244c23b4a977f5b720b9ad95c` |

增量自检于 2026-11-11 执行。`python3 /private/tmp/daa011-r1-guide-baseline-1es8eomg/verify_docs.py` 退出 0，新增段落 30 处链接和锚点、4 个 `zsh -n` 检查及两份历史后缀原字节比对均通过。`git diff --check -- automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md` 退出 0。`shasum -a 256` 确认两份返工候选及 QA1 checklist，后者保持 `17435cda1293ac7d788e7eb321d64f3612e9f65f9532c1af978b0de00420fb7c`。

另以 `python3 -` 在内存中将各手册的三个返工片段逐一还原为 QA1 文字，重算得到上表两个 QA1 摘要，退出 0。该对照说明每份手册仅变更了上述三个片段。

正式工作树、受控范围和第 4 节限制不变。临时基线 `/private/tmp/daa011-r1-guide-baseline-1es8eomg` 继续供新 fresh-context Verification 对照，复验和 Human Owner 最终验收后由协调方按资源依赖处置。请独立复验精确 r1 及两个 QA1 发现，重新记录 verdict。
