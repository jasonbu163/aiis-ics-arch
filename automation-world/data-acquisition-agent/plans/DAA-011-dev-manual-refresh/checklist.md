Task ID: DAA-011
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 AC01-AC04 passed for the exact r1 bilingual guides; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-011 r1 独立文档核验 · QA1

## 候选与环境

2026-11-11（Asia/Shanghai）。命名 Verification `/root/daa011_dev_manual_verification` 在 fresh context 接收精确 Development handoff。查阅根及适用范围的项目契约、README/PLAN、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、角色入口及完整的 [批准 spec](spec.md) 和 [Development tasks](tasks.md)，按 `project-governance` 与 `aiis` 核对文档和工业边界。正式未提交工作树 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。环境 Darwin arm64、Python 3.9.6、zsh 5.9。实际候选由工作树文件摘要确定。

| 输入 | 独立重算的 SHA-256 |
| --- | --- |
| Human Owner 批准登记后的 spec | `674c0880f1e700f2d4104458f7a096c56f36565b791bf59a5552e1604c0551d1` |
| Development handoff tasks | `abe26d746b851d28b5124b85936c5516885749f1f326f3f53a9792e368eea021` |
| [英文候选](../../STAGE_C_GUIDE.md) | `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58` |
| [中文候选](../../STAGE_C_GUIDE.zh-CN.md) | `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065` |
| 英文实施前原件 | `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a` |
| 中文实施前原件 | `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769` |

## 验收标准与发现

| 验收项 | 结果与独立证据 |
| --- | --- |
| AC01 当前入口、环境和归档 | 通过。两语开头均将当前流程限定在 DS → DAA → 本地 SQLite。双语初始化链接可定位到 `database-only` 加宿主机源码运行和 dev Compose 两节；对照 [database-only](../../../../docker-compose.database-only.yml)、[dev Compose](../../../../docker-compose.dev.yml) 和 [Vite](../../../../frontend-js/vite.config.js)，默认项目 API 8000、MySQL 3307、Web 5190 各司其职，31281 为本例 S7 端口；手册提示按实际端口核对。分别对照 [DAA 选择器](../../src-tauri/src/config/mod.rs#L19) 与 [DS 选择器](../../../device-simulator/src-tauri/src/config/bootstrap.rs#L41)，非空进程 profile 优先，自身根 `.env` 分开，DAA 可另选 `DAA_ENV_FILE`。绝对路径模板、空目录准备、两条 `pnpm tauri dev`、已有兼容配置复用与原 `.local` 数据保留对称。DAA 常规进程未设置读门禁时可由界面显式读，进程显式禁止仍生效，详见手册所链 README；本次未读取实际环境。 |
| AC02 DS → DAA → SQLite 走读 | 通过，静态。DS 的 [导入面板](../../../device-simulator/src/app/simulator/components/SourceImportPanel.vue#L15)、[策略页](../../../device-simulator/src/app/simulator/views/policies/index.vue#L16)与[版本加载页](../../../device-simulator/src/app/simulator/views/instances/index.vue)支持所列顺序。DS/DAA 的 S7 源码与 rack 0、slot 1、Calling TSAP 256、Called TSAP 257 相符；`MinimalImport` 为明确非优化的 [DB](../../src-tauri/tests/fixtures/source-import-minimal/minimal.db)，引用 [UDT](../../src-tauri/tests/fixtures/source-import-minimal/minimal.udt)。按[共享 word 对齐规则](../../../shared/tia-import-core/src/layout.rs#L8)独立推算：DB21 长 8 字节，`payload.ready` BOOL 0.0、`payload.count` INT 2、`payload.temperature` REAL 4；DS 显式填 `false`、`0`、`12.5`，保持、允许读、无写 owner，另确认初值/策略、保存版本、停机加载、启动。DAA 的[导入面板](../../src/app/plc/components/SourceImportPanel.vue)、[点位页](../../src/app/plc/views/points/index.vue#L97)和[本地历史](../../src/components/console/LocalHistoryPanel.vue#L15)支持确认偏移、三点批量启用到同一 1000 ms 组、保存并激活、连接后采约 5 秒再暂停。历史支持按 PLC/组/时间筛选，DB21 是结果列；打开 DB21 的样本详情检查三个值和质量。两语均保持上报停止。 |
| AC03 新版接续 | **未通过：F-QA1-001。** 其余接口与链接符合：DAA 当前[适配器](../../src-tauri/src/infrastructure/facts_http.rs#L5)仍用 `/batches`，[DAA-010 r2](../DAA-010-sample-facts-upload/spec.md)仍为 draft。[v2 合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)、[后端路由](../../../../backend/app/plc_facts/api/v2.py#L98)与 [ARCH-ACQ-003 r2 Owner 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)支持 API 8000 的 `POST /api/v1/integration/plc-facts/samples`、一个来源/PLC/DB 的完整样本、实时与补传共用、登记来源与机器 Bearer、`committed` 加 `created` 或 `duplicate`。Web 5190 的实时数据与采集历史在[模块清单](../../../../frontend-js/src/app/acquisition-data/manifest.js#L8)可定位。验收限指定 dev 的 provider 和 Web；无 DAA 端到端上报事实。 |
| AC04 历史与双语 | **未通过：F-QA1-002。** 两语历史分区醒目，`18281` 留在 B-RUN-01 历史上下文，旧命令、留存约束及锚点的实际字节保留。相对链接、脚本语法、双语配置与启动命令、差异边界通过下表检查。 |

### F-QA1-001：新版写入接续缺少明确授权条件

[R03](spec.md#L31)要求 DAA-010 完成适配且「获准联调」后才登记测试来源和机器凭据、向项目 dev 发送样本。[中文手册第 82 行](../../STAGE_C_GUIDE.zh-CN.md#L82)写「完成新版适配并明确联调范围后」，[英文同段](../../STAGE_C_GUIDE.md#L82)写 “implements the new adapter and the joint-test scope is established”。范围明确不表示获准实际登记或写入。请在两语操作段明确实际联调须已获批准，再执行相关动作；保留现有本地流程、合同和后续故障用例边界。

### F-QA1-002：历史分区把资源状态写成已完成退役

[中文手册第 5、86 行](../../STAGE_C_GUIDE.zh-CN.md#L5)及[英文对应段](../../STAGE_C_GUIDE.md#L5)把专用服务和测试容器写成已退役。两份指南所链的 [DAA-008 运行记录](../DAA-008-reliable-facts-upload/tasks.md#L649)末尾只持久记录到 `needs_owner_m02`，没有这些资源退役的收尾记录。协调方转交了 Human Owner 停用旧测试服务及容器的指示、早前只读的确认样本观察和端口未监听的观察；这些不构成对整组服务及测试容器已退役的持久证据，本轮亦未检查运行状态。保留“历史记录”、`18281` 及原文，明确该环境只用于追溯、不用于本手册的当前操作；若继续声称具体资源已退役，须给出相应收尾依据。本项不否定已批准规格关于历史可靠确认的描述，也不要求本轮重新操作旧环境。

## 实际命令、边界与资源

| 命令 | 结果 |
| --- | --- |
| `git rev-parse HEAD`、`git branch --show-current`、`uname -sm`、`zsh --version`、`python3 --version`；`shasum -a 256 <spec> <tasks> <正式候选两份> <基线两份>` | 均退出 0，环境和六个摘要见上。实施前原件摘要亦与 [DAA-008 历史 Development 记录](../DAA-008-reliable-facts-upload/tasks.md#L632)及[原独立核验](../DAA-008-reliable-facts-upload/checklist.md#L666)相符。 |
| 对每语执行 `diff -u /private/tmp/daa011-r1-guide-baseline-1es8eomg/<手册> automation-world/data-acquisition-agent/<手册>`，再以 Python 字节分割和 `difflib.SequenceMatcher(..., autojunk=False)` 比较 | diff 均退出 1，属于有预期文本差异。两份各只有一个修改区：共同第 1–4 行不变，原第 5 行替换为候选第 5–86 行，其余原字节不变。含 `<a id="m01-launch"></a>` 的后缀英文 22,515 字节、SHA `7dbafc2ad934b2e50f52241d71cc22e837a407a33c94fca9914d195a17514536`；中文 20,130 字节、SHA `476b0732673347a25ec01b2cc44cf08b63e2b5d1ba3cc7d8b7bed21fa6d1f916`。 |
| 独立 `python3 -B -`（stdin 检查，不调用 Development helper），解析两份完整手册及 spec/tasks 的相对路径、标题 slug 和显式 HTML 锚点，逐个将两份手册的 shell 代码块通过 stdin 传给 `/bin/zsh -n` | 退出 0。共 68 处相对链接（两语各 21、spec 14、tasks 12）和 8 个 zsh 块（含历史）通过。新增两个 dotenv 模板和两个 zsh 块两语内容一致。检查仅针对正式工作树；provider 合同及验收记录当前可达，但其路径尚未进入 Git index，本轮不推定已提交。 |
| `git diff --check -- automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md` 与定向 `git status --short` | 退出 0。两份手册为 `M`，本 task bundle 为 `??`；仓库已有大量其他 dirty 路径，本任务差异以实施前原件限定。DAA 的 PLAN/目录索引在读入时仍显示 draft，交协调方按真实 gate 同步。 |

本轮只写本 checklist。未运行项目启动命令、应用构建、自动测试、网络、PLC、HTTP、数据库、Docker 或阶段 B 验证；未打开或修改真实 `.env`、profile、SQLite、历史、归档及其他任务。此核验不证明当前原生运行、实际上传、完整 Stage C、现场或生产。

QA1 已在 stdin 中以「候选前 4 行（含行尾）＋以下对应原提示行的 UTF-8 字节＋两个 LF＋候选从 `m01-launch` 起的后缀」独立重建原件，两份都与临时原件逐字节相等，重算值均等于上表。以下只作为精确反向差异留存，不是当前操作：

```text
**B-RUN-01 preparation is complete under DAA-008 r4. The Owner can perform M01.** Collect briefly in the isolated profiles, pause collection and hand off the source material. Wait for the backend adoption receipt before M02. Runtime verification and final acceptance are recorded separately. [Approval](plans/DAA-008-reliable-facts-upload/spec.md#r4-b01-f7-owner-approval) · [Readiness record and run details](plans/DAA-008-reliable-facts-upload/tasks.md)
```

```text
**DAA-008 r4 的 B-RUN-01 已完成准备，当前由 Owner 执行 M01。** 先在隔离 profile 短采样，暂停采集后交接来源材料，等待后端采用收据再进入 M02。运行验证及最终验收单独记录。 [批准记录](plans/DAA-008-reliable-facts-upload/spec.md#r4-b01-f7-owner-approval) · [就绪记录与运行细则](plans/DAA-008-reliable-facts-upload/tasks.md)
```

本轮证据及反向差异可由正式手册和本 checklist 重建。临时目录 `/private/tmp/daa011-r1-guide-baseline-1es8eomg` 是 Development 交接原件，建议保留供同一 Revision 返工复验；复验完成、Human Owner 最终验收后由协调方确认无剩余依赖再按授权处置。QA 未创建临时文件，未回收任何资源。

## Verdict 与交接

**`qa_failed`。** AC01、AC02 静态通过；AC03、AC04 分别有 F-QA1-001、F-QA1-002。无环境 blocker。把精确发现交回 Development；保留本轮结论和证据，返工 handoff 后由新 fresh-context Verification 复验。

## Human Owner 最终验收

待独立复验通过后交 Human Owner 决定。


# DAA-011 r1 独立文档复验 · QA2

## 候选与环境

2026-11-11（Asia/Shanghai）。命名 Verification `/root/daa011_dev_manual_verification_rework` 在 fresh context 接收 r1 返工交接。独立阅读根及作用域项目规则、README/PLAN、角色入口、canonical workflow、完整 3MD、正式候选及差异，按 `project-governance` 与 `aiis` 复验。工作树 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，Darwin arm64，Git 2.50.1，Python 3.9.6，zsh 5.9。候选以未提交工作树文件 SHA-256 固定。

| QA2 输入 | 独立重算的 SHA-256 |
| --- | --- |
| [Human Owner 批准的 r1 spec](spec.md) | `674c0880f1e700f2d4104458f7a096c56f36565b791bf59a5552e1604c0551d1` |
| [Development 返工 handoff](tasks.md#5-qa1-返工与重新交接) | `ff7b553a73416d30125ae7584ba578186c74689b0d018eb69faa53645c8a46fe` |
| QA1 checklist（本次更新前，含当时元数据） | `17435cda1293ac7d788e7eb321d64f3612e9f65f9532c1af978b0de00420fb7c` |
| [英文返工候选](../../STAGE_C_GUIDE.md) | `9df1cd0a8b08372caad39d4b9ae5e62f68490864850b17a7801a314e13a2fe84` |
| [中文返工候选](../../STAGE_C_GUIDE.zh-CN.md) | `892b83f79cd0f8e24f7751e802f1567d697cc4f244c23b4a977f5b720b9ad95c` |

## 验收复验

| 验收项 | 结果与证据 |
| --- | --- |
| AC01 当前入口、环境与归档 | **通过。** 两语 §1–4 与 QA1 候选逐字节一致。重新对照初始化文档、Compose、Vite 与两应用 profile 选择代码，确认默认端口、各自 profile 选择、初始化命令和 `.local` 保留规则。手册当前路径仍止于本地 SQLite。 |
| AC02 DS → DAA → SQLite | **通过，限静态走读。** 对照样例、共享标准布局和现有入口，复核 S7 `31281`、rack `0`/slot `1`、TSAP `256`/`257`，DB21 长 8 字节及 BOOL `0.0`、INT `2`、REAL `4`，DS 显式初值及版本加载，DAA 同组 `1000 ms`、激活配置、暂停采集与本地样本核对。两语的命令块和步骤与 QA1 候选一致。 |
| AC03 新版接续，F-QA1-001 | **通过，问题关闭。** 两语第 82 行都把 DAA-010 完成新版适配和实际联调获准列为登记测试来源、机器凭据和向项目 dev API `8000` 写入的共同前置条件。当前适配器仍是 `/batches`，DAA-010 r2 为 `draft`。按工作树 provider 合同和 ARCH-ACQ-003 r2 验收复核 `POST /api/v1/integration/plc-facts/samples` 的完整 DB 样本、实时与补传同路、匹配的 `committed` 与 `created`/`duplicate`，以及 Web `5190` 两个核对入口。 [英文操作段](../../STAGE_C_GUIDE.md#L82) · [中文操作段](../../STAGE_C_GUIDE.zh-CN.md#L82) · [Provider 验收](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) |
| AC04 历史与双语，F-QA1-002 | **通过，问题关闭。** 双语第 5、86 行把 `18281`、专用 API、数据库、relay、测试容器、路径及命令定位为 B-RUN-01 历史追溯，当前操作指回 §1–4。两语均移除了资源已退役的断言，并保留完整 Stage C 验收待后续联调的状态。所链 DAA-008 运行记录末尾为 `needs_owner_m02`。旧命令、留存约束、锚点和 `m01-launch` 起的全部历史字节均已核对。 [英文历史导语](../../STAGE_C_GUIDE.md#L86) · [中文历史导语](../../STAGE_C_GUIDE.zh-CN.md#L86) · [DAA-008 运行记录](../DAA-008-reliable-facts-upload/tasks.md#L658) |

## 命令与差异证据

| 命令 | 结果 |
| --- | --- |
| `shasum -a 256` 对 3MD 和两份正式候选；`git rev-parse --show-toplevel HEAD`、`git branch --show-current`、`uname -sm`、`git --version`、`python3 --version`、`zsh --version` | 退出 0，摘要和环境见上。 |
| 每语执行 `diff -u /private/tmp/daa011-r1-guide-baseline-1es8eomg/<手册> <正式手册>`；独立 `python3 -B -` 通过 stdin 比较字节与 SHA-256 | diff 均为 1，显示预期的单一区域替换。两份保留原第 1–4 行，从显式 `m01-launch` 锚点起与原件逐字节相等。英文后缀 22,515 字节，SHA-256 `7dbafc2ad934b2e50f52241d71cc22e837a407a33c94fca9914d195a17514536`；中文后缀 20,130 字节，SHA-256 `476b0732673347a25ec01b2cc44cf08b63e2b5d1ba3cc7d8b7bed21fa6d1f916`。Python 退出 0，用 QA1 留存提示行与正式候选重建两份实施前原件，字节及摘要与临时原件、QA1 记录均相符。 |
| 独立 `python3 -B -` 用返工前原文字节逆向重建两个 QA1 候选，再与本文件 QA1 独立记录的摘要匹配并逐行比较 | 退出 0，两份各仅第 5、82、86 行有变化，指南 §1–4、链接、命令及其他行完整保留。 |
| 独立 `python3 -B -` 检查相对链接与标题/显式锚点，将两份手册各 shell 块传入 `/bin/zsh -n` | 退出 0。更新本 checklist 前共核对 102 处本地链接（两语各 21、spec 14、tasks 13、QA1 checklist 33）和 8 个 shell 块；两语新段落的两个 dotenv 模板和两个 zsh 块一致。provider 合同和验收文件在正式工作树可达，检查时尚未进入 Git index。 |
| `git --no-optional-locks diff --check -- <两份手册>`、`git --no-optional-locks status --short -- <两份手册及任务 bundle>` | 退出 0。手册为 `M`，任务目录为 `??`。四处 DAA 索引读取时仍为 `draft`，机械同步由协调方处理。 |

Development 记录的 §1–4 继续列出首次交接候选、自检及边界，§5 独立记录返工，并注明首次交接的退役描述已撤销。QA1 正文、失败 verdict、原候选和原件摘要均保留。恢复 QA1 元数据时，第 3 行为 `Status: qa_failed`，第 6 行为 `Handoff: QA1 两项文档问题返回 Development；返工交接后由新 fresh-context Verification 复验，Human Owner 终验待复验通过`，截去本 QA2 追加段后可重算表中的 QA1 checklist 摘要。

QA1 两份指南也可从正式候选重建。按下表逐行恢复当时的片段。英文第 86 行恢复首句之后、批准链接之前的文字，中文第 86 行恢复首句之后、历史收据说明之前的文字。链接和其他字节沿用正式候选。

| 语言与行 | QA1 原片段（历史证据） |
| --- | --- |
| 英文 5 | the history of the retired DAA-008 B-RUN-01 joint-test environment |
| 英文 82 | and the joint-test scope is established |
| 英文 86 | The `18281` address, dedicated API, database, relay, paths and commands describe that environment. Its services and test container have been retired. Retained receipts and archives can be consulted for traceability; full Stage C acceptance awaits subsequent joint testing. |
| 中文 5 | 保留已退役的 DAA-008 B-RUN-01 联调环境历史记录 |
| 中文 82 | 完成新版适配并明确联调范围后 |
| 中文 86 | `18281`、专用 API、数据库、relay、路径和命令均属于当时环境，相关服务和测试容器已退役，供追溯使用。 |

本轮核验和证据限正式工作树及静态检查。未执行项目启动、构建、产品测试、阶段 B 重跑、HTTP、PLC、数据库或 Docker 操作，未访问真实 `.env`、profile、SQLite、历史或归档。本轮只写本 checklist，未创建或回收资源。实施前原件已能从正式指南及 QA1 留存的反向差异完整重建，验收证据对临时目录 `/private/tmp/daa011-r1-guide-baseline-1es8eomg` 无持续依赖。Human Owner 最终验收后，由协调方核对其他任务或复核依赖和现有授权再处置。

## QA2 Verdict 与 Human Owner 交接

**`qa_passed`，限 DAA-011 r1 双语手册的静态核验。** AC01–AC04 通过，无 blocker。交 Human Owner 对表中两份精确候选作最终验收。DAA-010 实际适配及联调、完整 Stage C 验收与历史资源状态沿各自任务记录。
