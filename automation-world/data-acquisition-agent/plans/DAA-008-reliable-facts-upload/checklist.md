Task ID: DAA-008
Revision: r1
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 -> 唯一主协调/root；r1返工F-QA1-002至004独立关闭，F-QA1-001继续qa_failed并交PM/Development待另批恢复Revision；Human Owner最终验收pending，B及完整阶段C未完成
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-008 r1 独立核验（QA1）

## 1. 结论与被验证候选

2026-11-05，实际 fresh-context Verification `/root/daa008_verification_1` 对精确 **DAA-008 r1 partial developer_handoff** 给出 **qa_failed**。真实 hot-journal 恢复失败独立复现；另发现合法部分轮 ACK/历史响应被拒、单片完成不变量漏验、队列分类汇总缺失三项源码问题。通过的有限检查不能抵销这些失败，A0/A1 不能记为完成。

本次只验证第3节 A0 及 Owner明确批准的第11.1节有限 A1。实际 HTTP/loopback listener、DS/PLC/MySQL、Docker、GUI/原生视觉、目标/source采用与 AC18–AC20 不在本轮运行批准内，均未执行。既有 SQLite 配置、历史、默认 profile、原联调 profile、原8590样本及真实 `.env` 未发现、读取、复制、挂载、升级、清理或覆盖；不通过打开真实库来证明“未打开”。没有自动启动、旧历史上传、SMA 或现场验证结论。

| 固定输入 | SHA-256 / 身份 |
| --- | --- |
| [获批spec](spec.md) | `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`；`owner_approved`，§14登记精确A0/A1批准 |
| [Development事实](tasks.md) | `4a6a4d5ec7136bb5d7b1a51f8acf0a7d8f376c29cd88a629ee604dcea16523f1`；`dev_blocked` / partial developer_handoff |
| 正式源码树 / entry HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9` |
| 最终handoff-receipt.json | `f35c86185b72367e06181561287437a6c50aeb348a45d2729ee7754ecdbc562d` |
| candidate-r1-partial-manifest.json | `a99d85980d9ae8323d15a5824848a0ea1a0d4f46a4117f35cfb2e305a796076a`；52个有限允许表面、45个改动 |
| candidate-r1-partial.diff | `e34edcaa1271dc62219ec9fc5a744d9a8acf6cba196d3d7bd3da2d8105df90f4` |
| handoff-complete.diff | `05ae5ec014a644d7842df94fd1d1dfe08aa00a10200f5247f4349cc35b4c54aa`；含Development的tasks，不冒领PM/coordinator改动 |

后三种候选材料位于 `/private/tmp/daa-008-r1-a-xsm2qlrl/development/`。只消费上述最终候选；`candidate-manifest.json`、`implementation.diff`、`candidate/after` 是已被替代的中间材料，没有用作本次候选。正式树是实现/构建真相，`candidate-r1-partial/after` 仅为45个改动文件的证据快照。

独立重算：52个当前源码SHA与manifest全匹配；45个after快照全匹配；28个既有改动文件的before SHA及17个新文件重构出的unified diff逐字等于最终source diff。before来自coordinator的 `/private/tmp/daa-008-r1-a-coord-l73e8_ms/before/`；overview缺少before副本，依已明确确认其entry干净的handoff，使用entry HEAD原字节并核SHA。未将空的 `candidate-r1-partial/before` 当成全部文件不存在。CODE_INDEX差异仅为DAA所属段，其他entry脏改保留；本次未修实现、测试、spec、tasks或索引。

## 2. 独立性、规则与环境

入口没有继承Development对话推理。独立读取根 `AGENTS.md`、根 README/PLAN双语pair、AW和DAA最近README/PLAN、local_store及src/app双语规则、canonical lifecycle workflow、实际 `.codex/agents/verification.toml`、完整spec/tasks、最终diff、正式实现及可用Development输出。选择Verification角色并保持只写本checklist；角色TOML的model/effort只是配置证据，不声称独立观测了运行模型、平台ACL、强制路由或团队激活。

按表面消费 `aiis`、`project-governance`、`rust-runtime`、`desktop-tauri`、`backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；仅核验其对应边界。后端只读公开provider材料，无后端运行或写入；PLC协议/导入算法未改，不重跑阶段B。未启动子Agent、额外notifier或外发消息；notifier与机械索引归唯一主协调。

| 环境 | 实际值 |
| --- | --- |
| OS / architecture | macOS `15.7.7` / `arm64` |
| Rust / Cargo | `rustc 1.89.0 (29483883e 2025-08-04)`；`cargo 1.89.0 (c24e10642 2025-06-23)` |
| Node / pnpm | `v22.19.0`；`11.11.0`；使用现有依赖，没有安装 |
| 应用版本 | `aiis-data-acquisition-agent 0.1.0`；固定bundled rusqlite/libsqlite3-sys未升级 |
| QA自有A1根 / TMPDIR | `/private/tmp/daa-008-r1-a-kq7gjcj3`；mkdtemp新建、mode0700、canonicalize后使用；所有Rust测试显式传递同一TMPDIR |
| 执行方式 | 正式源码树运行；子命令环境移除继承的`DAA_*`键并显式设置TMPDIR，不调用Bootstrap::load、dotenv/default profile或完整产品入口 |

合成fixture由现有测试代码/公开固定vectors从零生成，路径拒绝既有文件并限制在自有临时根。actual-engine案例直接构造Bootstrap，`read_allowed=false`，仅注入有限Transport替身。没有socket监听或真实HTTP请求。不能把替身、源码字符串断言、构建或纯反例称为原生/跨系统证据。

## 3. 独立命令、真实结果与证据

除纯probe的显式临时manifest外，cwd均为正式仓根；所有Cargo运行使用现有锁及`--offline --locked`。下表中的 `M` 精确展开为 `automation-world/data-acquisition-agent/src-tauri/Cargo.toml`，`Q` 精确展开为上表QA自有根；这两个符号仅缩短记录，不是隐含环境选择。

| 编号 | 完整命令/检查 | Exit及实际结果 | Q内日志/记录 |
| --- | --- | --- | --- |
| Q01 | `TMPDIR=Q cargo test --manifest-path M --offline --locked --lib delivery -- --nocapture` | **101；21 passed / 1 failed / 0 ignored，76 filtered**。未skip hot case；21含3个由父例实际调用的child入口helper，不能当21项独立业务场景。 | `delivery-full.log`、`delivery-command.json` |
| Q02 | `TMPDIR=Q cargo test --manifest-path M --offline --locked --lib facts_canonical -- --nocapture` | 0；5 passed，provider固定vectors、独立十进制/REAL/控制字符/深度/分片边界及9位时间。 | `canonical.log` |
| Q03 | `TMPDIR=Q cargo test --manifest-path M --offline --locked --lib facts_http -- --nocapture` | 0；3 passed，origin、实际Read累计/截断上限、typed read模式；无socket。F002另有反例证明现有正例不完整。 | `http.log` |
| Q04 | `TMPDIR=Q cargo test --manifest-path M --offline --locked --lib time_contract -- --nocapture` | 0；5 passed，含合成v2配置/历史/ID/seq/pending/schema守恒与新2/3及拒绝门禁。 | `time-contract.log` |
| Q05 | `cargo fmt --manifest-path M --check` | 0。 | `fmt.log` |
| Q06 | `TMPDIR=Q cargo check --manifest-path M --offline --locked --features rust-snap7-driver` | 0；源码检查不连接S7。 | `driver-check.log` |
| Q07 | `TMPDIR=Q cargo check --manifest-path M --offline --locked --features local-validation` | 0；保留9个该非默认feature下既有ordinary-config未使用警告。 | `validation-check.log` |
| Q08 | `node --test automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs automation-world/data-acquisition-agent/tests/sample-details.test.mjs automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs` | 0；13 passed / 0 skipped；IPC facade和原文/时间/列宽增量。 | `node.log` |
| Q09 | `pnpm --dir automation-world/data-acquisition-agent build` | 0；vue-tsc/Vite通过。保留Rollup PURE注释和大chunk提示；无GUI/listener。 | `frontend-build.log` |
| Q10 | `TMPDIR=Q CARGO_TARGET_DIR=/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/src-tauri/target cargo test --manifest-path Q/pure-probe/Cargo.toml --offline --locked --lib qa_ -- --nocapture` | **101；1 control passed / 3 adversarial checks failed，8 filtered**。纯取证harness直接`#[path]`导入正式候选3个domain文件及facts_http，不复制/修改产品实现，不是产品整套测试。 | `pure-probe-second.log`、`pure-probe-second-command.json` |
| Q11 | `python3 -B -`（stdlib候选SHA/diff/锁/JSON/i18n/本地链接审计）及`git --no-optional-locks diff --check -- <manifest中45个changed路径>` | 0；重构diff相等；UTF-8/新文件末尾和行末空白通过；561双语key及placeholder对称、78个literal key可解析、141个本地文件目标存在。 | `static-verification.json` |

Q01覆盖冻结/派发/ACK的真实SQLite回滚、引用、容量/真实journal I/O失败、3:1、8冻结上限、202轮不均衡PLC、组轮询、拒绝派生、单调重试，以及实际LocalEngine单worker的重复start/resume、pause、在途ACK、shutdown、停态重开/锁释放。该worker案例已在Q01执行，没有为了计数重复运行。Q02–04只选择受影响模块，未扩大为阶段B、后端或DS全套。

32片/max-ID大ACK案例是纯validator的保守边界压力，不是实际32片POST或最大ACK的完整SQLite落盘/吞吐实证。该最坏实际持久化预算仍不能记作全部验收通过。正常worker的自有新fixture关闭后另做只读SQL核账：runtime3、2 samples/2 cycles/2 receipts、2 acknowledged、0 references，所有payload/manifest/context原串SHA匹配；记录 `worker-after-sql-evidence.json`。这不替代hot case的恢复账本。

已消费Development最终11份日志及tasks失败历史：其delivery 21通过确实skip了hot case，crash-first确实失败；不将其自检当QA。Q10第一次临时manifest保留了原default-run但没有对应bin，解析exit101（`pure-probe.log`），仅修正QA临时harness后得到上表真实反例。stdlib审计的早期辅助尝试因系统Python3.9无tomllib、错误假定before/after包含全部52文件而退出1；改用stdlib解析实际锁/明确before来源后通过，没有安装依赖或改产品规避检查。临时harness的23个未使用警告来自只导入部分源码；没有添加allow(dead_code)，也不是正式driver构建的新警告。

## 4. 必需返工项

### F-QA1-001（P1，开放）：真实hot ACK事务后无法重开恢复

- 对应：AC09/AC10/AC14，R08/R14及R02的RO准入边界。
- 位置：[RO preflight](../../src-tauri/src/infrastructure/local_store/mod.rs)第66/136行、[真实crash案例](../../src-tauri/src/infrastructure/local_store/delivery_tests.rs)第259–333行。子进程更新parts/sample_delivery/batch的未提交事务，`sqlite3_db_cacheflush`断言返回0后调用`libc::_exit(86)`；父例确认exit86和真实journal存在。
- QA仅一次自有复现，Q01实际失败：`known v3 hot-journal recovery must preserve complete prior ledger: "time_profile_unsupported:attempt to write a readonly database"`。RO的首个数据库读取需要SQLite回滚，因只读连接拒绝，尚未进入产品RW恢复。
- QA fixture：`Q/store-f7ee52ff-afc0-44ef-adb6-69751a489d62`。runtime 176128 bytes，SHA `74c63027ef6897cb74f859139689b0d914516097e1ccc36679764cf80ac7bbd7`；journal 42496 bytes，SHA `40cf44d4242ffdd35280153ea463ac6015ddf693d318a1f590f24bc2d5b03666`；header `d9d505f920a163d70000000a594a3e8c0000002b0000020000001000`。
- 本轮test在崩溃前持久化 `daa-008-hot-before.json`，SHA `12aec59c4af00be7517140d649838ba2fbec812f7dc276d8db7f45cefefa079f`；其中样本原串SHA逐项核准。失败后只作文件原始字节观测，未用SQLite恢复/immutable/nolock读取，**没有恢复后SQL/table不变量证明**。Development原fixture缺少持久before的限制继续保留，未替其补造。
- 影响：实际ACK中断可使新profile停在准入失败，无法达到同身份unknown恢复/完整旧或新ACK的要求；未据此宣称样本已丢失或已证明半ACK。
- Handoff：不能削AC09/10/14、把拒绝当通过、删journal或放宽旧库门禁。当前r1同时要求RO-before-write和hot恢复，需要PM明确新的r2信任/恢复边界及Owner精确批准后再实施。本QA只固定失败，不实现新协议。

### F-QA1-002（P1，开放）：把部分轮质量与完整性混为一轴，拒绝合法provider结果

- 对应：AC08/AC09/AC10，R09的分片确认/整轮完整性/质量分离及手工typed read合同。
- 位置：[ACK validator](../../src-tauri/src/domain/local_delivery.rs)第469行 `r.quality_good && !r.complete`；[history validator](../../src-tauri/src/infrastructure/facts_http.rs)第278行同一条件。
- 固定provider依据：`backend/app/plc_facts/services/async_ingest.py`第186行初始化 `complete=False, quality_good=True`，第217–218行分别累计received完整性与事实质量，第238行原样输出两轴；`async_query.py`继续输出持久cycle两轴。完整性不足不意味着已收事实质量坏。上述ingest SHA仍为spec固定的 `91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f`。
- Q10使用固定vectors `fixtures.partialFragment`，保留原batch/instance/requestDigest/每片sourceSHA/contentDigest/cycleDigest/成员集，构造完整success壳：`receivedParts=1, expectedParts=2, complete=false, qualityGood=true`，全good且该sample尚未收齐。结果ACK为 `Err("invalid_receipt")`；对应正确query-projection digest的合法history fact为 `Err("invalid_read_response")`。完整good轮control通过；只把qualityGood改false的比较样例也通过，隔离了该错误条件。
- 影响：真实跨HTTP部分轮可能已在后端可靠提交，却被本地标unknown，重复恢复相同合法回执继续失败，达到协议失败阈值后暂停；合法history核对页同样不可读。现有receipt helper把qualityGood写成received==expected，覆盖不到该provider语义。
- 返工：Development按r1修正这两个校验面及有意义的正反例；继续严格绑定原batch/成员/摘要和完整壳，不把修复解释为接受任意HTTP200。保留回执当时的partial状态；原批重放的历史标志不要求随着其他批到齐被改写。本QA没有运行后端或改变provider。

### F-QA1-003（P2，开放）：sourceSampleComplete虽解码但未校验其必要不变量

- 对应：AC08，R09的逐成员逻辑相容要求。
- 位置：[PartResult与verify_success](../../src-tauri/src/domain/local_delivery.rs)第144/365行；该字段只在DTO中声明，后续没有读取。
- Q10在已通过的单片完整good control中只改 `data.results[0].sourceSampleComplete=false`。其 `part=1, parts=1`、committed壳、全部身份/摘要/position及cycle完整性均保持。当前 `verify_success` 返回 **Ok(())**，预期拒绝，因此反例失败；这类输入仍可进入现有committed确认路径。
- 影响：严格ACK准入接受了单片已commit却声称源样本不完整的自相矛盾结果。已有成员/摘要绑定仍在，不能把这项发现扩大成已发生外部错提交或数据丢失。
- 返工：补足能由冻结请求及该回执证明的完成不变量，至少拒绝此单片矛盾。多片历史回执的 `sourceSampleComplete=false` 可能是合法当时事实，不能因其他批后来补齐就要求旧回执变true；不能无条件要求所有receipt标志为true。

### F-QA1-004（P2，开放）：未分列新待传、冻结/不确定及需处理数量

- 对应：AC15，R06/R15的可见队列分类汇总；这是A0源码功能缺口，与未获批原生视觉门禁分开。
- 位置：[运行/存储上传卡](../../src/components/console/FactsDeliveryPanel.vue)第7行仅显示pending/acknowledged，整个组件未消费 `delivery.counts`；[delivery_snapshot](../../src-tauri/src/infrastructure/local_store/delivery.rs)第98行的pending为所有sample_delivery pending，含已冻结、unknown及blocked。第119–123行running状态优先表还遗漏blocked/expired_unconfirmed。
- 可观察源码后果：新待传与已经冻结/未知的样本合并在同一个“待传”总数；需处理数量没有要求中的摘要入口，只有blocked的队列仍可把运行状态呈现为running。逐批列表/详情仍保留真实状态，不是数据被清掉。
- 返工：Development按r1提供去重且含义明确的分类统计和两页汇总，确保多个part/batch不会把同一样本重复计数；阻塞/过窗仍可见，继续保留原队列与证据。补相应行为断言，不能仅用模板字符串出现来冒充计数正确。

## 5. AC01–AC20核验表

“有限通过”只指本轮明确列出的源码/合成证据，未覆盖的要求继续开放，不能汇总为整项或整个A阶段通过。

| AC | 独立状态 | 证据与剩余门禁 |
| --- | --- | --- |
| AC01 | A0范围有限通过 | 精确批准、角色链、spec/tasks/最终diff、13项固定来源责任核对；不继承其他任务运行授权。 |
| AC02 | 本轮通过 | 只用自有新合成路径；Q04的v2配置/原串/ID/seq/pending/schema守恒。正常lifecycle元数据变化单列，不声称打开后整个SQLite字节恒等。 |
| AC03 | 有限通过 | Q04新config2/runtime3、合成v2/v2本地能力及未知/旧时区/半库/身份等拒绝；源码无旧库投递DDL。hot恢复仍见F001，未用拒绝替代恢复。 |
| AC04 | A0有限通过 | Q02固定provider向量及独立lexical oracle、0/false/REAL/中文/原SHA与9位时间；原local_sample.rs未改。 |
| AC05 | 有限通过 | Q02/01固定片、完整transportManifest和请求限额/超限blocked；无现场容量或真实大请求证据。 |
| AC06 | 有限通过、B未执行 | Q01冻结原bytes/唯一片归属/冷重开身份；后端duplicate不增事实尚需B。 |
| AC07 | runtime有限通过 | Q01 3:1、PLC/group轮询、202轮、8批、单worker/慢替身；实际HTTP负载未跑。R06可见分类缺口另见AC15/F004。 |
| AC08 | **fail** | 既有typed矩阵/8MiB边界通过；Q10独立反例证实F002/F003，不能全通过。 |
| AC09 | **fail** | SQL触发故障回滚/引用/原串和正常ACK有限通过；真实hot恢复F001失败，合法partial ACK另受F002阻断。 |
| AC10 | **fail** | unknown原批/字节、非hot崩溃位置有限通过；F001/F002未闭；真实POST commit后丢ACK恢复仍需B。 |
| AC11 | 有限通过、B未执行 | Q01错误/终结拒绝/合法子集/父深度/期限替身矩阵；真实provider证明寿命、换key和代表例未跑。 |
| AC12 | 部分证据 | Q01物理reserve、真实journal I/O故障/rollback、pending/reference保护与已确认清理通过；最坏合法大ACK仅纯边界压力，完整最坏SQLite落盘/恢复预算尚不能记全通过。 |
| AC13 | 有限通过、B未执行 | CAS、未决禁换目标、从未冻结source重评估与同URL静默换库限制均已核；实际source采用另批。 |
| AC14 | **fail** | Q01实际worker幂等控制、正常在途ACK/退出/停态重开/锁释放通过；hot事务重开F001失败，Owner M04未执行。 |
| AC15 | **fail；原生视觉blocked** | Q08/09与双语/列宽/原详情通过；F004缺分类汇总；明暗/窄窗/原生M05没有本轮授权或证据。 |
| AC16 | A0有限通过 | Rust三固定API、origin正反例、无代理/redirect/自动重试、validation/无桥门禁、具名IPC严格DTO及无人工ACK/SQL写面核准；未做实际TLS/HTTP联调。 |
| AC17 | 有限通过 | 正式树52SHA/45diff一致，最小CODE_INDEX与文件头、受影响编译、脱敏有界事件/时间语义及资源记录；Q10失败和所有限制如实保留。 |
| AC18 | **blocked** | B具体环境/操作未批准，无DS→真实HTTP→MySQL七表→local ACK/reads核账。 |
| AC19 | **blocked** | 无实际API中断/恢复/积压退出重开双方完整账；不复用阶段B历史作为本项证据。 |
| AC20 | **未满足** | 当前qa_failed，A0/A1不完整，B未批准/未执行，Human Owner最终验收pending；完整阶段C未完成。 |

## 6. Acceptance Audit与下一gate

| 分类 | 本次精确结论 |
| --- | --- |
| 已接受历史基线 | DAA-007受控阶段B及后端provider接受仅按各自任务记录消费；未重跑或扩大。 |
| 已观察的候选能力 | 无损wire/冻结/事务/公平调度/显式单worker/部分UI与构建有上述有限通过证据，尚非本r1已接受基线。 |
| 尚未接受 | F001–004、最坏ACK实际持久化证据及全部未闭验收面；本候选不得记A0/A1 passed。 |
| 后续明确门禁 | B实际HTTP/DS/MySQL/Docker/目标采用、原生视觉/Owner核账及最终Stage C接受；没有默认豁免。 |
| 保留路径/未来范围 | 既有v2/v2本地能力保留；旧profile迁移/历史上传、自动启动、SMA、真实现场/生产/长稳另项。 |

F002–004是已批r1内的实现返工，返回Development；不把修复现有合同缺陷变成新的Owner范围批准。F001涉及r1准入与恢复信任边界冲突，交PM新Revision并取得精确批准前不得实现绕过。任一返工须保留本失败历史、固定新候选与Development handoff，然后启动新的fresh-context Verification；本checklist不预判后续通过。所有结果仅交Human Owner评估，最终接受权没有转移。

## 7. 证据、资源归属与只写审计

QA自有根 `Q` 本次盘点91个文件、42个合成SQLite，含唯一仍必要的hot journal与崩溃前JSON。所有直接启动的subprocess及测试child已返回；实际engine父例join worker/store并重获profile锁。没有自有服务/listener、Docker资源、Git分支/worktree、真实env/profile或现场资源。共享 `src-tauri/target` 和忽略的DAA `dist` 由获批构建使用/扩展；纯probe编译也使用该target缓存，不把共享缓存当可随意删除的自有临时树。

Verification不执行任何回收。保留QA根、Development根 `/private/tmp/daa-008-r1-a-xsm2qlrl/`、coordinator基线 `/private/tmp/daa-008-r1-a-coord-l73e8_ms/`，用于r1返工、新r2和Owner证据依赖；coordinator在证据/后续依赖解除并确认归属后按workflow处理。本文件持久化关键命令、失败文本、必要标量与SHA；不能仅靠将来可能消失的tmp路径证明通过。

| QA证据（Q内） | SHA-256 |
| --- | --- |
| delivery-full.log | `ac3fe3523d4e74ab9924d06828bfa963df40def8e08895e5b8e06517b872545e` |
| pure-probe-second.log | `65e5d114ed639351170964ea80c1ed4800a9836b4c62d88dde5055371d1f5c1a` |
| pure-probe/probe.rs | `2c0b5eb252316443b4b978c7660fd8437b76cea1679f451ec7bd8d0ffe34aa77` |
| pure-probe/Cargo.toml | `131a1fc10c6a57335c90bee45f1a386d02c4e34b2f72208eaaf3e94ee530e610` |
| pure-probe/Cargo.lock | `3689918ee18e16f63357ceb92811bbcf6019486b38ea747853638073e26b18cc`；与正式锁相同 |
| provider-partial-good-ack.json | `f3e05d0f6158c2da628db5ada2eaea810f73fd5f3e3507422cb4f7ba4a026d52` |
| provider-partial-good-history.json | `e8e95c026326b2a01bd40def40bdcc164d64c84c2057535ce95ab5f92c37744a` |
| hot-journal-evidence.json | `78636922b06422098618577f84761eaa55a8a0ed0fee8a2b9474bf9c3d8de1e8` |
| worker-after-sql-evidence.json | `df74bbed75a58429dfb9d78fdc276e8d89c429de33d195165e746ec47af6d6dd` |
| static-verification.json | `6030afbda4cc5635f7c9c7f750e370b5285a14c36498eea7d921aeda9e3300be` |
| development-output-audit.json | `f01e702a1d4650386baf678330c019df049f3069a6e7339e7bb1cf6c757ce8f2` |
| verification-artifacts.json | `02a09fed387fb4f3587875d24de4babd94b8cda6a4bd6a4e2063152dbd583053`；完整日志/反例/资源清单 |

锁审计未移除或升级既有package，新增29个blocking/TLS所需锁节点，reqwest仍精确0.13.4；未改pnpm依赖、Tauri启动feature或构建入口。纯harness仅调整其临时lib path/名称、共享导入核心绝对路径与无对应bin的default-run，正式52表面仍为同一冻结候选。

本轮项目内唯一写入为本 `checklist.md`；合成夹具/日志/证据均在Q。未写spec/tasks、实现、测试或配置；不静默修复，未清理证据。最终文件SHA在外部handoff给主协调，避免自引用。

## 8. Human Owner final acceptance

Pending。本次独立结果为qa_failed，没有Human Owner最终接受、阶段C完成或发布/部署/数据库/设备授权记录。

---

## 9. QA2：精确返工候选与结论（2026-11-05）

新的实际 fresh-context Verification `/root/daa008_verification_2` 独立核验 **aiis-ics-arch::DAA-008 r1** 的部分返工交接。**最终 verdict 仍为 qa_failed**：F-QA1-002、003、004已关闭，AC12新增资源/普通事务证据通过；F-QA1-001仍开放，A0/A1、完整阶段C与Owner终验均不能记通过。本次没有新增实现finding，也未修源码。

QA1 §1–8全部正文原字节保留；顶部只更新当前Handoff，Status继续qa_failed。QA1原完整文件SHA为 `eab00b347a3b81350f64d5073f1f05bd333fdf8e6f7ba0eaa42076b545ab63f1`，原件存于Q2的 `qa1-checklist-before.md`。原Handoff完整保留如下，不把它当本轮当前gate：

> Handoff: QA1 -> 唯一主协调/root；F-QA1-002至004退回Development按r1返工，F-QA1-001保留并交PM处理r2恢复边界；Human Owner最终验收pending，完整阶段C未完成

| 本轮固定输入 | SHA-256 / 身份 |
| --- | --- |
| approved spec / 当前tasks | `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae` / `287b64181b1420e888e5c4aa9d296793963500263381ff774b35487e12f1070f` |
| 正式树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch` / `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`；不是临时源码副本 |
| DEV handoff-qa1-rework-receipt.json | `e0682b033925d48cf3aa131e42b5feb894813d6ae033adcb0029a3bc3a65ba05`；冻结时刻2026-11-05T11:33:12.048185+00:00 |
| candidate-r1-qa1-rework-manifest.json | `df68c4eba7ae5352b1decb799cca762b3450a49c1ac085a26665d91bca7e232e`；52有限表面、45累计改动、13返工文件 |
| QA1→返工 diff / entry累计 diff | `4111ca3a71082ec1fb7beb16e8ff5d23e66ca7e231125fe91a6dcc7eec995d72` / `bbb37e83e1e8ad014cbaeee3d76ca9944c1ba88e15cf8e6a8cc27a5cc654838c` |
| 完整handoff diff | `4d55c02c49b10a1cf39957cc8d69df9d821cf1cbb28d9015c4ffa423e5cf1e39`；包含Development的tasks |

以上DEV材料仍在 `/private/tmp/daa-008-r1-a-xsm2qlrl/development/`。Q2独立重算52当前SHA、45快照SHA、13返工before SHA，完整重构返工diff逐字相等；spec/tasks及全部返工收据SHA匹配。39个未返工表面继续消费QA1相同源码的有限证据，不重复阶段B整套、后端或DS测试。完整读取根/最近AGENTS与README/PLAN、实际verification角色/canonical workflow、相关八个skill、完整spec/tasks/QA1 checklist和701行返工diff；读取公开provider实现/模型/期限规则及DEV17份命令日志并核SHA。角色配置只作配置证据，不声称平台ACL、强制路由或可观测运行model/effort。

## 10. QA2环境、命令和结果

Q2=`/private/tmp/daa-008-r1-a-tww7ssar`，全新mkdtemp、canonicalize、mode0700；全部合成库从公开结构/向量生成。每个产品测试由Q2/run_check.py移除继承DAA_*/VITE_DAA_*并显式设置TMPDIR=Q2，argv/cwd/exit/log SHA见各 `*-command.json`。不读取dotenv/default/真实或原联调profile，不读取/复用DEV或QA1 SQLite；本轮只读SQL也仅针对自有新fixture。无GUI、listener、实际HTTP、DS/PLC/MySQL、Docker、子Agent、额外notifier或外发消息。主协调继续独占索引/通知。

环境为macOS15.7.7 arm64、Rust/Cargo1.89.0、Node22.19.0、pnpm11.11.0，应用0.1.0，既有依赖及锁，无安装。产品SQL使用未变bundled SQLite3.46.0；辅助PythonSQLite3.43.2仅用于本轮自有库只读核账/独立计数oracle，不冒充产品SQLite。

下表M=`automation-world/data-acquisition-agent/src-tauri/Cargo.toml`；除临时probe显式manifest外cwd为正式仓根。

| 命令 / 检查 | 真实exit / 结果 | Q2证据 |
| --- | --- | --- |
| `cargo test --manifest-path M --offline --locked --lib ack -- --nocapture` | 0；16 pass / 0 ignored；含一个未单独执行业务的child helper及名称含rollback的既有用例，并非16个新场景；未选hot父例，不把它称通过 | ack-regression.log |
| 同前缀，filter=`receipt_partial_quality`、`facts_http`、`delivery_sample_counts`，各带 `-- --nocapture` | 各0；1 / 4 / 1 pass，均0 ignored | partial-and-counts.log、http.log、counts.log |
| `cargo test --manifest-path Q2/pure-probe/Cargo.toml --offline --locked --target-dir /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/src-tauri/target --lib qa2_ -- --nocapture` | 0；一个独立test内40项语义正反例全部匹配；直接path导入正式domain/HTTP校验器，不调用DEV receipt helper，不改产品 | independent-semantic.log / independent-semantic-matrix.json |
| `cargo fmt --manifest-path M --check`；`cargo check --manifest-path M --offline --locked --features rust-snap7-driver` | 各0；driver无新增warning，无设备连接 | fmt.log、driver-check.log |
| `node --test automation-world/data-acquisition-agent/tests/{facts-delivery,sample-details,time-and-history-preferences}.test.mjs` | 0；13 pass / 0 skipped；花括号在实际argv展开为三个文件 | node.log |
| `node Q2/panel_ssr.cjs` | 0；实际SFC编译+Vue/i18n SSR，两卡×双语×blocked/expired共8次计数/单位/状态渲染；包装/动作/表格为惰性替身，无浏览器、IPC或原生视觉结论 | panel-ssr-report.json及8份HTML |
| `pnpm --dir automation-world/data-acquisition-agent build --outDir Q2/dist --emptyOutDir` | 0；vue-tsc/Vite；envDir=false，无应用启动 | frontend-build.log |
| stdlib独立SQL分类oracle；`python3 -B Q2/budget_audit.py`；`python3 -B Q2/typed_bound_audit.py` | 各0；分类、真实自有8MiB闭库核账、独立typed编码枚举 | independent-counts.json、independent-budget-sql-audit.json、independent-typed-bound.json |
| `python3 -B Q2/static_audit.py`；`git --no-optional-locks diff --check -- <45条路径>`；`git apply --check --reverse --whitespace=error-all <返工diff>` | 各0；52 SHA/45快照/13返工diff、13 pins按before/current责任匹配、565双语键/占位符对称、87完整literal键可解析、4个指南本地目标存在 | static-verification.json |

保留既有empty_for_test警告；独立probe的22个unused警告来自部分源码导入，未添加allow抑制；构建保留既有PURE/chunk提示。QA静态helper最初将4个拼接翻译前缀误当完整literal而exit1，限定完整引号键后exit0，未改产品。DEV早期缺leaf失败及已撤回的24h/u64Max预算夹具仍仅作历史；本轮只采用修正后的120天/signed BIGINT及新8MiB实证。

## 11. QA2 finding处理与AC更新

| Finding | 本轮独立结论 |
| --- | --- |
| F-QA1-002 | **closed**。公开provider `async_ingest.py` 的complete计数轴与quality累积轴分别复核；合法partial-good ACK/history通过，known-bad/null且quality=false通过，known-bad/quality=true拒绝。40项矩阵继续拒绝错identity、source/content/cycle/request摘要、错/缺/重复成员、received<sent、received>expected及complete矛盾；不是放宽任意HTTP200。 |
| F-QA1-003 | **closed**。单片false、created送齐片仍false、created且轮complete仍false、样本true但received不足均拒绝。multipart旧duplicate/historical_committed的cached false在后来轮完整时仍接受，不回写历史回执。 |
| F-QA1-004 | **closed（源码功能）**。实际新SQLite测试及独立8样本逐项oracle同时通过；多个片/批、重复诊断不重复计数，ack优先、需处理优先于frozen。独立结果unfrozen1/frozen3/needsProcessing3/ack1，pending7=1+3+3；blocked/expired状态可见。两卡中英文实际SFC显示四类与样本单位，原pending总数/批状态统计保留。原生明暗/窄窗仍未验证。 |
| F-QA1-001 | **open / fail**。RO preflight模块SHA仍为 `910bc481da945f17e5b92c73432c48564f87677c1b63561144d4b64537058027`；schema与hot child/parent测试体逐字未变。QA1无skip的21 pass/1 fail日志SHA `ac3fe3523d4e74ab9924d06828bfa963df40def8e08895e5b8e06517b872545e` 已复核；错误仍为 `time_profile_unsupported:attempt to write a readonly database`。未无效重跑、打开旧hot库或删journal。新普通rollback通过不能关闭此真实崩溃失败；需PM新Revision/精确Owner批准恢复信任边界后Development实施，再fresh QA。 |

AC12分层补证：本轮新fixture通过实际Configuration validate，256启用点、32DB/32reads、同一组，经activation/commit_cycle/builder/freeze/strict ACK/SQL；32样本/32片/1轮，请求383660B，compact ACK27230B。独立typed逐字段编码枚举为 `1112+32×753+31+437+256×259=91980B`，松界101120B<128KiB；它是独立字段上界，不是联合可达最大回执或已发送请求，协议32×512理论界与当前产品256点/单轮界分开。

同一typed合法ACK仅添加JSON空白至**8388608B**，作为客户端接收/原文保存资源上限压力，绝不称provider普通输出。新自有fixture `Q2/store-55941620-8044-4111-83af-4ca9c82bfd6a`：TEMP trigger在实际ACK事务观察journal后RAISE(ABORT)，Rust断言receipt0及原main SHA/原payload守恒；随后去掉故障真实提交。Q2闭库只读复核integrity=ok、32 acknowledged/1 receipt/0 references，原payload/manifest/context SHA与关联逐项匹配、raw UTF8恰8MiB，响应SHA `sha256:3b0e51b885c11b3af0c650929ca83723b0e44c2f1ca9d0c8a3c8dd507abf16cd`。proof恰committedAt+120天，raw期限为observedAt+3自然月，commitSerial=9223372036854775807；RO核账前后本轮两库文件SHA未变。

| AC12实测与预算，单位B | 本轮值与归属 |
| --- | --- |
| main前→峰值 / 新页增长 | 1110016→9515008 / 8404992；只计入额外ACK/恢复33554432 |
| rollback / commit活journal | 30240 / 79488；只计入旧页journal预算2226296 |
| 旧页公式 | 271×(4096+8+4096)+4096=2226296；另有原四轮B-tree33554432、维护33554432；不借用这两项作为新ACK余量 |
| reserved前→后 | 102889592→119715992；独立分项相加一致，无journal/new页双计 |
| request / receipt / delivery metadata前→后 | 383660→0 / 0→8388608 / 212004→212004；物理main仍实际计量，不把未来删除当空闲 |

| AC | QA2有效状态 / 未闭边界 |
| --- | --- |
| AC01–07、11、13、16、17 | 本轮身份/保护/相关回归及未返工QA1有限证据继续有效；范围仍是A0/A1有限观察，实际provider/采用/现场部分不补造通过。 |
| AC08 | 本轮A0严格ACK返工有限通过，F002/003关闭；不代表真实HTTP通过。 |
| AC09、AC10、AC14 | **fail**：普通事务/unknown及单worker有限证据保留，F001真实hot恢复未闭。 |
| AC12 | 本轮获批A1的合法产品域、编码上界、完整8MiB输入真实持久化/普通rollback及分项预算通过；hot恢复仍受F001限制，不称整项恢复全部通过。 |
| AC15 | F004源码缺口关闭，Node/SSR/i18n/构建通过；原生明暗/窄窗/Owner M05仍未执行。 |
| AC18、AC19 | **blocked**：B具体HTTP/DS/MySQL/目标source采用/Docker操作未批准、未执行，无双方真实核账。 |
| AC20 | **未满足**：当前qa_failed，A0/A1未全部通过，B开放，Human Owner最终验收pending，完整阶段C未完成。 |

## 12. QA2证据、资源与最终handoff

| Q2关键证据 | SHA-256 |
| --- | --- |
| independent-semantic-matrix.json | `055a7590fe090d0ce34d84643d557b10a5ffb778fa48e43e3c7d1dc999cef8a6` |
| independent-counts.json / panel-ssr-report.json | `080a2cbd63beab3f2303990d0adccb026a112595aee1822dca451049aa683683` / `991c9f91f638af2ca12db74fa3551aa2e947cfe6a336e7e2debe5e9fe4b7037b` |
| independent-budget-sql-audit.json / independent-typed-bound.json | `95c5f5fbc0945704d6d219d8ce8768221d0cca6aeb1f806a045fa3618fca6d09` / `b74ee6346f49fcb6429b81e9a47823fead912f0f7148ac8a23a05b3a124f6f15` |
| static-verification.json / qa2-artifacts.json | `cdb2dcf3d5e3c96f77f8229e4591770068cd63b922ceac86ec3c052212ae22fb` / `157faae03064c581c81578769aa24aa653aefa49ba81d1e5b694c3be26321f46` |
| resource-inventory.json | `abe50fba2a7001bd9e0763c08f4cebc16cfdd177a9094df79e35ade2dfff0eac`；27份自有合成SQLite文件，所有本轮启动subprocess均已退出 |

Verification未回收资源。继续保留F001的DEV/QA1 hot journal与before JSON、QA1反例/最终diff、返工最终收据/快照、DEV27KB及8MiB原文/预算/journal、Q2新8MiB双库/journal和独立报告/probe/日志，以及coordinator entry before；这些仍有r1/r2/Owner证据依赖。Q2关键标量、SHA、失败与限制已持久写入本checklist，不只依赖tmp路径。

可回收中间物须由唯一coordinator确认无后续/证据依赖后处理，**不是本QA执行删除**：DEV已标superseded的 `/private/tmp/daa-008-r1-a-xsm2qlrl/development/candidate/after`、`candidate-manifest.json`、`implementation.diff`不再作为QA2候选；Q2的 `dist/`及resource-inventory.json中逐项列出的12个可再生单测目录，在记录持久化且无后续依赖时可回收。DEV其余早期重复passed夹具由coordinator按DEV归属盘点；本QA没有为盘点而发现/打开其SQLite。不得清理真实/默认/原联调profile、原历史/真实dotenv、共享src-tauri/target/dist或任务外资源。

项目内唯一QA2写入为本checklist；原spec/tasks、52源码表面、测试、配置和索引不改，最终SHA通过外部handoff交主协调。失败F001继续经主协调返回PM/Development，任何新恢复方案须先获批；B具体操作提案另批。最终独立verdict只交Human Owner评估，最终接受权保留；本轮没有Owner接受、完整阶段C完成或发布/部署授权。

