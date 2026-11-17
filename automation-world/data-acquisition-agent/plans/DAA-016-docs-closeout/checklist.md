Task ID: DAA-016
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 已最终验收 DAA-016 r1 文档；Windows 原生验证和完整阶段 C 另行跟踪
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-016 r1 独立文档核验 · QA1

2026-11-14（Asia/Shanghai）。命名 Verification `/root/daa016_verification` 在 fresh context 收到精确交接。查阅根项目契约及适用作用域 README、PLAN、任务目录、角色 TOML 和 canonical workflow。现场配置和 API 分别按 `desktop-tauri`、`rust-runtime`、`backend-arch`、`i18n-workflow` 核对，文档治理和工业边界使用 `project-governance`、`aiis`。角色 TOML 配置为 `gpt-6.1-sol / high`，此处记录配置值。 [项目契约](../../../../AGENTS.md) · [工作流](../../../../.codex/workflows/development-lifecycle-workflow.md) · [Verification 角色配置](../../../../.codex/agents/verification.toml)

## 精确候选与环境

正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 加正式树未提交文档。环境 Darwin 24.6.0 arm64、Git 2.50.1、Python 3.9.6、zsh 5.9；`command -v pwsh` 退出 1。获批 spec SHA-256 `cdad98c59302a36de25ff2044a22253c77c73d90c0c21459a790706105fc39b6`，本轮 Development handoff SHA-256 `c1c773c7ec90657c106be01e28cc47ea71b2933dd66eb31a7a9223c3f397b265`。独立重算本轮交付清单九项全部匹配。 [获批范围及原批准](spec.md#4-验收与交接) · [精确交付](tasks.md#5-精确交付与-developer_handoff)

## 验收结果

| 项目 | 独立核验 |
| --- | --- |
| AC01 旧入口及历史追溯 | 四条旧路径均删除。短页四项从交接 fenced 原文恢复，字节分别为英文 C 1352、中文 C 1300、英文 B 610、中文 B 544，与对应 HEAD Git blob 逐字节相同，SHA-256 与 DAA-014 QA2 交接清单 4/4 相同。旧路径引用 38 条（DAA-008 7、DAA-011 13、DAA-010 3、DAA-013 3、ARCH-ACQ-004 12）；另有 DAA-007 冻结 r1 两条及 DAA-014 四份快照内部互链按原目录解释，均属已批准影响。七个有关历史任务无工作树差异，四份冻结快照等于 HEAD。现行导航及新增本地链接可达。版本与原行号见下，DAA-011 QA1 恢复成功是本轮新增证据。 [追溯表](tasks.md#2-历史引用及版本追溯) · [DAA-014 交接](../DAA-014-unified-operator-guide/tasks.md#返工后的精确交接清单) |
| AC02 Windows 记录单 | **失败，F-DAA016-QA1-001。** 单份中文记录单为「待验证」，两个 PowerShell 块采用普通启动和独立绝对 profile/空 env；锁试验排除第二个 Vite 争抢端口。表覆盖激活、正常重开、隔离采集、离线恢复、逐样本回执及 Web 历史。发送后确认前退出与 SQLite 写入期间的热 journal 明确分列，要求受控注入、停止并保全、不能证明条件时记未测。现有 Mac/dev 两次观察、31 条样本保留决定、DAA-010 r5 `qa_failed`/首次目录替换缺陷及 Windows AC08 都按原任务引用。启动后的实际选中目录验证步骤无法按记录单执行。 [Windows 记录单](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md) · [Mac/dev 手测转交](../DAA-014-unified-operator-guide/tasks.md#2-human-owner-手测转交) · [DAA-010 r5 QA2](../DAA-010-sample-facts-upload/checklist.md#独立验证-qa2) |
| AC03 中英配对及合同 | 通过。两语八节、Mermaid 节点连线、流程、表、JSON 请求/回执和 GET 示例逐项对照。三个标识用于登记准入，仍需满足请求字段、类型及限额，`sourceType` 展示、DB 属于样本和查询。上报保留原 ID、采集时间、顺序、原字节，可靠回执与逐点最新值、独立未过期历史各有用途。r4 数据 OpenAPI 一 POST、五 GET 未设 Bearer；管理 OpenAPI 三方法均为 `HTTPBearer`，源码 active admin 依赖、PATCH 删除及 Web 中英标签相符。指南首部互链，英文入口直达英文版，中文原第 7 节别名可达。真实目标采用依据当前环境。 [英文](../../../../docs/acquisition-data-guide.md) · [中文](../../../../docs/acquisition-data-guide.zh-CN.md) · [数据 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev-r4.json) · [管理 OpenAPI](../../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json) |
| AC04 独立证据与边界 | 通过本轮验证程序。读过 Development 自检及限制，独立重算摘要、检查任务差异、历史原文、双语文档、合同、导航和代码块。根 PLAN 只归属采集指南所在行的英文链接替换，DAA 双语 PLAN/目录只归属 DAA-016 行；复核期间观察到并行 DAA-015 索引更新为 `owner_accepted`，归其任务。共享树另有 DAA-015 三处源码/测试差异，不计入本次文档交付。 [Development 自检](tasks.md#4-development-self-check) |

### F-DAA016-QA1-001 · Windows 的 profile 验证引用未注册的启动日志

[记录单第 38 行](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md#L38) 要求操作者先从 `data_acquisition_agent_started.profile_directory` 核对实际目录，否则停止。普通入口经 `main.rs → lib.rs → local_recovery.rs → local_supervisor.rs` 打开 `bootstrap.profile/local-acquisition-v1` 并发出 `runtime_started / instance / stopped`。指定事件定义在未注册的旧 `infrastructure/logging.rs`，唯一非测试调用在退役且未注册的 `commands/headless_runtime.rs`。使用本次普通入口时，所要求的事件不会出现，因此照文档执行无法完成配置前的实际路径核对。此为静态源码复现。 [入口](../../src-tauri/src/main.rs#L10) · [普通运行](../../src-tauri/src/lib.rs#L86) · [实际启动事件](../../src-tauri/src/services/local_supervisor.rs#L173) · [模块注册](../../src-tauri/src/infrastructure/mod.rs) · [旧事件](../../src-tauri/src/infrastructure/logging.rs#L189)

返工限定在记录单。保留启动前核对从未存在的隔离路径，改用普通入口实际可产出的证据确认选中目录。例如只读检查专用 `<profile>\local-acquisition-v1\logs\runtime.jsonl` 内本次 `runtime_started / instance / stopped`，并核对同一 `local-acquisition-v1` 存储目录中新生成的 `config.sqlite` 和 `runtime.sqlite` 文件存在；无须打开数据库。保留无法确认则停止的条件。 [双库和日志目录](../../src-tauri/src/infrastructure/local_store/mod.rs#L379) · [日志文件](../../src-tauri/src/infrastructure/local_logging.rs#L110)

## 历史原文复核

- 固定 Git `fd999224a8756feda314a33148304b4bf3461876` 下阶段 B 双语及 DAA-011 QA2 双语的四项 SHA-256 均匹配追溯表。DAA-007 更早的冻结 r1 试行稿仍无匹配的完整原文证据。重建 DAA-008 r4 双语（23039 / 20583 字节）与 DAA-013 QA4 英文，重算摘要与原记录或所引精确恢复说明相同。 [DAA-014 恢复说明](../DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)
- DAA-010 r5 暂停候选用各语言 QA5 快照与对应零上下文差异逐 hunk 比对旧行、计数和新行位置后重建。英文 34534 字节，SHA-256 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a`，M01 锚点在原 L105。中文 30728 字节，SHA-256 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`，原 L40 是两终端启动提示，原 L97 是「7. 暂停、目标变更与恢复」。二者均匹配原暂停清单。历史 QA 链接指向当时各自候选，解释时沿其候选摘要，不借现行行号替代。 [原暂停清单](../DAA-010-sample-facts-upload/tasks.md#L246) · [中文差异](../DAA-014-unified-operator-guide/tasks.md#daa-010-r5-中文原文重建) · [英文差异](../DAA-014-unified-operator-guide/tasks.md#6-qa1-返工与英文历史原文)
- DAA-011 QA1 现已独立确认双语全文可恢复。取上述固定 Git 的 DAA-011 QA2 原文件，在第 5、82、86 行各替换指定片段，保留其余 UTF-8 字节及 LF。下表为本轮实际逆向替换，分别得到原 QA1 英文 `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58` 和中文 `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065`。Development §2/§4 的未确认是首次自检的观察；请在返工交接时补注本轮已确认的恢复结果，保留首次观察。其余 ARCH-ACQ-004 r4 首轮、r2 QA6/QA7 的其他候选及 DAA-013 较早候选仍沿原任务记录，未在本轮声称全文可恢复。 [DAA-011 QA1 摘要](../DAA-011-dev-manual-refresh/checklist.md#候选与环境) · [QA2 逆向说明](../DAA-011-dev-manual-refresh/checklist.md#命令与差异证据) · [其他过渡候选](tasks.md#2-历史引用及版本追溯)

| 行 | QA2 原片段 | 替换为 QA1 片段 |
| --- | --- | --- |
| 英文 5 | retains the DAA-008 B-RUN-01 joint-test history | retains the history of the retired DAA-008 B-RUN-01 joint-test environment |
| 英文 82 | and joint testing has been authorized | and the joint-test scope is established |
| 英文 86 | The `18281` address, dedicated API, database, relay, test container, paths and commands describe that earlier environment for traceability. Follow sections 1–4 above for the current operation. Retained receipts and archives can be consulted for traceability. Full Stage C acceptance awaits subsequent joint testing. | The `18281` address, dedicated API, database, relay, paths and commands describe that environment. Its services and test container have been retired. Retained receipts and archives can be consulted for traceability; full Stage C acceptance awaits subsequent joint testing. |
| 中文 5 | 保留 DAA-008 B-RUN-01 联调历史记录 | 保留已退役的 DAA-008 B-RUN-01 联调环境历史记录 |
| 中文 82 | 完成新版适配且实际联调获准后 | 完成新版适配并明确联调范围后 |
| 中文 86 | `18281`、专用 API、数据库、relay、测试容器、路径和命令均为当次环境的历史记录，供追溯使用。当前操作按本页第 1–4 节执行。 | `18281`、专用 API、数据库、relay、路径和命令均属于当时环境，相关服务和测试容器已退役，供追溯使用。 |

## 实际命令与限制

| 命令/方法 | 结果 |
| --- | --- |
| `git --no-optional-locks status --short --untracked-files=all`、`git rev-parse HEAD`、`git --no-optional-locks diff HEAD -- <获批文档及相关行>`、同范围 `git --no-optional-locks diff --check HEAD -- <路径>`、`shasum -a 256 <spec、tasks 和交付文档>` | 退出 0。跟踪文档差异在授权内容内，四个删除符合清单，新增未跟踪文档另外检查行尾、末尾换行和 fence。 |
| `python3 -B -` 内存解析交接清单与 fenced 原文，通过 `git show <精确 commit>:<path>` 独立取字节，按历史说明作逆向替换/补丁并重算 SHA-256 | 退出 0。九项交接摘要、四个删除短页、固定 Git 的四份原文、四份冻结快照及上文重建结果均核对；七个历史任务定向 `git status --short` 为空。 |
| `rg --files --hidden -g '*.md' -g '!.git' -g '!node_modules' -g '!target' -g '!dist' -g '!.local'` 与 `python3 -B -`（跳过围栏），定向扫描 Markdown 链接以及路径、标题、行号、显式锚点 | 退出 0。旧路径 38 条，符合已批准例外。现行和任务追溯链接核对 184 处本地目标（62 处含锚点），0 缺失；6 处外部链接未访问，固定 Git 链接所指本地对象已复核。 |
| `python3 -B -` 对照两语图、节、请求字段、JSON 回执标识；逐个将 Bash 块的字节送 `/bin/zsh -n`；读取两份 r4 OpenAPI、源码和 Web locale | 退出 0。两语各八节，同拓扑、相同请求与回执、四次 shell 语法检查通过。数据与管理 OpenAPI SHA-256 分别为 `7c87f409caf704f02e2d018e2c1c9a37e9e8803febbcd98b6bd61db13495f13f`、`be7e8243f9217ce1a5edf9b8741d2a3dde826e8a404f6fbfa733a8494a1c0e51`。 |
| `rg -n 'emit_startup_event|data_acquisition_agent_started|runtime_started|runtime.jsonl'` 定向读取 Tauri 入口、配置、模块注册与日志实现；`python3 -B -` 核两个 PowerShell 块的绝对字面路径、`Test-Path -LiteralPath` 与预期命令 | 退出 0。记录单的两段语法形态经静态核查，未用 PowerShell 解析；发现 F-DAA016-QA1-001。初次 `rg` 路径误含不存在的 `src/app.rs`，退出 2；改由 `main.rs`、`lib.rs` 和已注册模块入口追踪。 |

本轮只写此 checklist，无临时文件或环境依赖。未执行示例中的命令，未构建或启动应用，未作 PowerShell、Windows、HTTP、数据库、SQLite、PLC、DS、Docker、真实 profile、真实 `.env` 或现有 31 条样本的访问或运行验证。文档链接为静态检查，未验证浏览器渲染。Tauri 平台前置条件沿用交接记录所引核对，本轮未访问外部站点。

## Verdict 与交接

`qa_failed` 由 AC02 的普通启动文档缺陷决定。按获批 r1 交 Development 修正 Windows 记录单并精确再交接；历史追溯补记本轮确认的 DAA-011 QA1 可恢复证据。之后由新 fresh-context Verification 复验。Human Owner 最终文档验收待 QA 通过，Windows 原生 AC08、DAA-010 r5 状态、完整阶段 C、实际环境采用按各自任务处理。

## DAA-016 r1 独立文档复验 · QA2

2026-11-14（Asia/Shanghai），命名 Verification `/root/daa016_qa2` 在 fresh context 读取项目契约、作用域文档、角色与工作流、完整 bundle 及源码。正式树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，以工作树文件摘要标识交付。环境 Darwin 24.6.0 arm64、Git 2.50.1、Python 3.9.6、zsh 5.9，`command -v pwsh` 退出 1。 [获批规格](spec.md#4-验收与交接) · [返工交接](tasks.md#6-qa1-返工与-developer_handoff)

| 输入 | SHA-256 |
| --- | --- |
| 获批 `spec.md` | `cdad98c59302a36de25ff2044a22253c77c73d90c0c21459a790706105fc39b6` |
| 本轮 `tasks.md` | `4ef8faa25f9e18ca2e8db1f349c0b3dc6475bca969d1a920d46978743b12fd20` |
| 写入前 QA1 `checklist.md` | `75b2acff8f623c10f443d11e5ae3f48d2ef002be6baec1691efd6e96bd4ea3cd` |
| 返工 Windows 记录单 | `18c390be426e34373a879c96a21a80282c3889055d56d6c9c77c04c6177962b6` |

| 验收项 | 复验结果 |
| --- | --- |
| AC01 | 通过。四个旧短路径仍不存在，交接内四份原文逐字节等于 HEAD，摘要 4/4 匹配。七个相关历史 bundle 无工作树差异，沿用 QA1 已核实的 38 条历史直链例外及冻结快照的原位置语义。独立重建 DAA-011 QA1 双语，保留首次自检观察，详见下文。未核对全文的 ARCH-ACQ-004 r4 首轮、r2 QA6/QA7 其他候选、DAA-013 较早候选及 DAA-007 更早试行稿仍列于追溯表。 [历史追溯](tasks.md#2-历史引用及版本追溯) |
| AC02 | 通过，关闭 F-DAA016-QA1-001。普通 `pnpm tauri dev` 由 Tauri 配置传递驱动 feature，`main.rs` 通过 `prepare_runtime` 读取选定的 `DAA_ENV_FILE`，非空进程 `DAA_PROFILE_DIR` 优先，再由 `lib.rs` 调用 `local_recovery::open`。`LocalEngine::open` 在该 profile 的 `local-acquisition-v1` 打开双库，随后调用 `runtime_started`。`LocalLog` 持久写入同目录的 `logs\runtime.jsonl`，事件字段对应 `process=daa-local`、`resource=instance`、`result=stopped` 与 `at`。记录单正确要求在配置或采集前，用此前不存在的专用路径、同一 PowerShell 进程设置及本次启动时间交叉核对双库与事件，无法确认即停止。日志无 profile 字段，文件存在单独无法证明进程身份或独占，独占另有第二进程测试。已去除退役事件要求。记录单保留正常重开、待传样本恢复、发送后确认前退出和热 journal 的不同核对步骤，仍为「待验证」。 [记录单](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md#L38) · [Tauri 配置](../../src-tauri/tauri.conf.json#L6) · [入口](../../src-tauri/src/main.rs#L10) · [配置优先级](../../src-tauri/src/config/mod.rs#L43) · [普通装配](../../src-tauri/src/lib.rs#L86) · [启动事件](../../src-tauri/src/services/local_supervisor.rs#L173) · [双库路径](../../src-tauri/src/infrastructure/local_store/mod.rs#L379) · [日志字段](../../src-tauri/src/infrastructure/local_logging.rs#L110) |
| AC03 | 通过。双语指南、两份 r4 OpenAPI 与 QA1 核验候选同摘要，延续 QA1 两语八节、示例及合同对照结果。本轮重新检查当前入口、两语切换、中文旧锚点及触及的记录和索引链接。 [英文指南](../../../../docs/acquisition-data-guide.md) · [中文指南旧锚点](../../../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) |
| AC04 | 通过。九项精确交付摘要匹配，其中八项等于首次交付记录。独立复核受影响差异、返工自检与两个 PowerShell 块的静态文字形态。根 PLAN 本任务只涉及采集指南英文入口，DAA 四个索引内本任务只涉及 DAA-016 行。并行任务内容由各自记录管理。 |

独立从固定 Git `fd999224a8756feda314a33148304b4bf3461876` 读取 DAA-011 QA2 双语字节，核对其 SHA-256，再按上方 QA1 表在第 5、82、86 行逐一替换唯一匹配的片段。英文重建 31493 字节、`f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58`，中文 28265 字节、`fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065`。二者均匹配 DAA-011 QA1 原清单和返工交接。仅在内存去掉 `tasks.md` §2 补注及 §6 后，整份恢复为首次交接 SHA-256 `c1c773c7ec90657c106be01e28cc47ea71b2933dd66eb31a7a9223c3f397b265`。 [DAA-011 原摘要](../DAA-011-dev-manual-refresh/checklist.md#候选与环境) · [QA1 恢复表](#历史原文复核)

`shasum -a 256`、`git --no-optional-locks diff --check HEAD -- <授权文档路径>`、`git show <精确 commit>:<路径>`、`python3 -B -` 内存比对最终均退出 0。两次内存比对先因 §2 补注分隔符定位错误退出 1，修正取界后重跑通过。限定 Windows 记录单、spec、tasks、双语指南和现行导航相关行测试 128 个本地链接，0 缺失，6 个外部链接未访问。源码通过 `rg -n` 及逐行阅读验证，未运行文档中的 PowerShell 或任何构建、应用、Windows、HTTP、数据库或设备，未触达真实环境和 31 条样本。仅写本 checklist，无临时证据依赖。

**QA2 verdict 为 `qa_passed`。** QA1 的失败与证据继续保留。交 Human Owner 最终文档验收，当前为待验收。Windows 原生 AC08 仍待实测，DAA-010 r5 的 `qa_failed`、完整阶段 C 和实际环境采用继续按各自任务记录。

## Human Owner 最终验收（DAA-016 r1）

Human Owner 在主会话明确验收 DAA-016 r1。登记时间为 `2026-11-14T17:06:56+08:00`（Asia/Shanghai）。验收原文：

> 验收 DAA-016 r1。现在 DAA 阶段 C 是不是完成了？后续还有什么工作？

最终状态为 `owner_accepted`，范围为 [r1 文档交付](spec.md#4-验收与交接)：退役四个旧文档入口并保留历史追溯、补充 Windows 原生验证记录单，以及补齐通用采集数据指南的英文版与相关导航。QA1 失败、返工和 QA2 的 `qa_passed` 结论均保留。[Windows 原生验证记录单](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md)仍为「待验证」；DAA-010 r5 的 `qa_failed`、Windows 原生 AC08、完整阶段 C 验收及实际环境采用仍按各自任务记录。

DAA-016 QA2 之后，主会话按 Human Owner 要求将 DAA 中英文使用手册的按钮文案分别同步为「启动上报」和 **Start reporting**。这两处更正由 [DAA-015 r1 的后续独立静态核验](../DAA-015-startup-automation-and-workbench/checklist.md#验收后手册按钮文案的独立核验)覆盖；DAA-016 QA2 记录对应同步前的精确候选。本次仅登记最终文档验收，未运行应用或实机验证。
