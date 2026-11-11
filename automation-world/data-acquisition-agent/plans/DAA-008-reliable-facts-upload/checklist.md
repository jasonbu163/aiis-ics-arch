Task ID: DAA-008
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r2 QA3 approved A0/A1 only qa_passed -> sole coordinator /root -> Human Owner final acceptance; F-R2-QA2-001 closed for exact P2 fixture candidate with original guards and finite default/concurrent evidence; old parallel failure cause remains undetermined, B/AC18-20/full Stage C/native visual and Owner acceptance remain open
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

---

## 13. r2 QA1：精确候选与独立结论（2026-11-06）

新的实际 fresh-context Verification `/root/daa008_r2_verification_1` 对 **aiis-ics-arch::DAA-008 r2 developer_handoff** 给出 **qa_failed**。A0/A1 正常新 sealed 热恢复及有限矩阵已有实际通过证据，但新增 **F-R2-QA1-001（P1，开放）**：工厂在锁后/原生恢复后无条件重取基线，并根据此时凭据是否存在决定是否完整核账，允许本次已见凭据消失后降成 unsealed，乃至跳过必需后检而接纳错误原文 SHA。该实现失败返回 Development；不能以18项正向矩阵通过抵销。

本轮只改顶部 Revision/Handoff 并追加本节及后续内容。上述 r1 QA1/QA2 §1–12 的正文逐字保留，原完整 checklist SHA `eec8b82f5b444a7b125b9d4f76938ed1d4356c3ff1a790e32d4aa090f7422e84`，原件为 Q3/checklist-before.md。原顶部是 `Revision: r1 / Status: qa_failed`，原 Handoff 为：

> QA2 -> 唯一主协调/root；r1返工F-QA1-002至004独立关闭，F-QA1-001继续qa_failed并交PM/Development待另批恢复Revision；Human Owner最终验收pending，B及完整阶段C未完成

| 本轮固定输入 | 独立重算 SHA-256 / 身份 |
| --- | --- |
| approved spec / tasks | `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de` / `1c429e06a446710594831fb4235abbb0ea0146b7506051e32eea751d733f7349` |
| r2 批准前 draft / r1 只读 archive | `4029dfedfda0dd8523e4fe9bee0fa5df3536f274c88ecb4a3dd89bc8ebdfb524` / `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`；当前效力来自 spec §16 逐字 Owner 批准 |
| 正式树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch` / `bcafa89fa31bdf62329bced89baebc193323a739`；未提交源码交付 |
| r2-source-manifest.json | `00a4247e737ee31c831e60ef0dd868d62d994bb30e178cf19ed4665806b71236`；54项有限源码，18项本轮改变 |
| r2-source.diff / scope | `5e5d9312cf18f823ff486e234188ee67c7e8bbac7e8e9b7a60a6b020684fe74a` / `fb312d01075d430bd6af44b70eb042cf0b8317bf4d97fbb1f9ae3ea8bb437c8a` |
| r2-developer-handoff.json | `d59facfb841260ace5242f5774b4fe656fc7e8329fcc0c307d2739e00ed2264c` |
| r2-command-summary.json / r2-evidence-manifest.json | `07877832553ff9d5f167d55897c4dced087802294408c48d373a58bbe815a211` / `261f3b85db541b42c264c4595e9824af6ab9bee1a185cf1b17cd906de8b0da8a` |
| coordinator entry-manifest.json | `3646568338664f5c68d32513be6ae77b038f3d415e85087202ea4480a984c39b`；60个公开基线文件 |

DEV材料仍在 `/private/tmp/daa-008-r2-a-fhgcwsig/development/`，coordinator entry 在 `/private/tmp/daa-008-r2-a-coord-uwfgzvlz/entry/`。独立重算54项正式源码及54项 source-after 原件均匹配；从 entry 原件重构18项 before/after unified diff，逐字等于 r2-source.diff；scope 按排序 UTF-8 path+NUL+after SHA+LF 重算相等。460个 DEV evidence-manifest 项逐项 SHA 一致。source-after 是审计附件，正式树是交付/编译真相，未把附件当实施树。10个 provider pins、原 ProfileLock 与无改动 r1 wire/HTTP/调度/worker 源码继续固定；没有新增依赖、feature、env、IPC、启动入口或范围外写入。

## 14. r2 QA1 独立性、环境与命令

Q3=`/private/tmp/daa-008-r2-a-6pu9uiac`，本 Verification 从零 mkdtemp、canonicalize、0700；没有继承 Development 对话推理。独立读根 AGENTS、README/PLAN 双语、AW/DAA 最近规则、local_store 与 src/app 双语说明、实际 verification TOML/canonical workflow、完整本轮 spec/tasks 和旧 checklist、实现、完整精确 diff 及可用 DEV 输出。按表面加载 aiis/project-governance/rust-runtime/desktop-tauri/code-document-indexer/i18n-workflow，另以 frontend-ui/backend-arch 核 locale/既有 UI 与事务合同；仅验证，不修复。角色 TOML 的 model/effort 是配置证据，不声称独立观测到运行值、平台 ACL、强制路由或团队激活。

macOS15.7.7 arm64；rustc/cargo1.89.0、Node22.19.0、pnpm11.11.0，应用0.1.0；既有依赖/锁无安装。产品测试使用固定 bundled SQLite3.46.0；辅助 Python SQLite3.43.2 仅只读自有已闭库夹具，未充当产品 SQLite。所有命令清除继承 DAA_* / VITE_DAA_* 并显式 TMPDIR=Q3；没有 Bootstrap::load、真实 dotenv/default/旧 profile 访问，没有 HTTP/loopback、GUI、DS/PLC/MySQL/Docker、子 Agent、额外 notifier、外发消息或资源删除。

下表 M=`automation-world/data-acquisition-agent/src-tauri/Cargo.toml`；cwd 为正式仓根；P=`Q3/independent-probe/Cargo.toml`。Cargo 使用 `--offline --locked`，命令实际 argv/env/cwd/exit/log SHA 保存在 Q3/*-command.json，不以 wrapper 的状态替代子命令结果。

| 编号 | 实际命令 / 检查 | Exit / 真实结果 |
| --- | --- | --- |
| Q3-01 | `cargo test --manifest-path M --offline --locked --lib profile_contract_ -- --nocapture` | 0；18 passed / 0 failed / 0 ignored，102 filtered；含一个无参数 child helper，不把它计成额外独立业务场景。初始化故障/no-replace、真实 hot/commit、三处再次退出、外锁/漂移负例、坏账本拒绝、合法 partial/parent cold 与大本地 context 均执行。 |
| Q3-02 | `cargo test --manifest-path P --offline --locked --target-dir /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/src-tauri/target --lib qa_r2_ -- --nocapture` | **101；0 passed / 3 failed / 0 ignored**。三个独立有界漂移反例均错误准入，详见下一节；不是编译失败或预期拒绝。 |
| Q3-03 | 同正式 Cargo test 前缀，filter=`v2_keeps_schema_configuration_history_ids_sequence_and_pending`、`unsealed_hot_journal_is_refused_without_recovery_authority`，各带 `-- --nocapture` | 各0；各1 passed。只在新根造 v2/v3，v2配置/历史/ID/序号/pending守恒且不补封；新 unsealed hot 正确拒绝且 journal 保留，此拒绝不算热恢复成功。 |
| Q3-04 | `cargo fmt --manifest-path M --check`；`cargo check --manifest-path M --offline --locked --features rust-snap7-driver` | 各0；driver 编译不连接设备，无新增生产 warning。 |
| Q3-05 | `node --test automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs automation-world/data-acquisition-agent/tests/sample-details.test.mjs automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs` | 0；13 pass / 0 skipped。 |
| Q3-06 | `pnpm --dir automation-world/data-acquisition-agent build --outDir Q3/dist --emptyOutDir` | 0；vue-tsc/Vite，无启动/监听；原 PURE/chunk 提示保留。 |
| Q3-07 | `node Q3/locale_switch.cjs`，实际 vue-i18n `createI18n` 在 en-US/zh-CN 切换 | 0；15个新增 profile 诊断 × 2语言全部解析为翻译，580 paired keys/placeholder 对称。未取得原生视觉证据。 |
| Q3-08 | `python3 -B Q3/independent_evidence_audit.py` | 0；独立 DDL 字节指纹、五份正向闭库完整账本/原串/ACK、两条反例坏 SHA、10个 provider pins、aux/reserve 分账通过核准。 |
| Q3-09 | stdlib candidate/static/provenance 审计；`git --no-optional-locks diff --check -- <18 changed paths>` | 0；54候选/快照、18 diff 原字节相等；38本地文档目标存在；UTF-8/未跟踪文件空白、局部 CODE_INDEX/文件头、真实锁接线/feature及平台分支核准。 |

Q3-02 是补充取证 harness：`profile_contract.rs`、schema/capacity、ProfileLock、domain 和其余产品模块按正式路径直接导入；local_store/mod.rs、infrastructure 等临时接线副本只插入绝对 module path 属性，去掉这些属性与正式原文逐字相等。仅临时 private 测试 checkpoint 加 bounded mutation，附加三条断言；去掉该 hook/三例与正式测试原文逐字相等。没有测试免锁/免凭据 API、生产语义改写或正式实现/测试修改，也不是交付候选。所有原始 DB FD 操作发生于 locked（SQLite 开启前）或 after_native（native连接已close）阶段，沿用真实 OS 锁。完整 provenance、hook-only.diff、wiring-only.diff、临时 manifest/锁和测试输入持久在 Q3/independent-probe/。

初次 probe exit101 是 QA 绝对 path 接线导致 plc_layout/tia_source 子模块查找失败，未执行反例；仅调整临时 module path 后得到上述实际三项失败。正式矩阵保留既有 empty_for_test warning；补充 probe 的36个 unused warnings 来自没有产品 composition root 的部分调用图，未添加 allow 掩盖。DEV早期编译/两项 fixture 失败仍保留；当前正式18项独立通过核实其后定向修正有效，不把 DEV 摘要当独立 QA。

## 15. F-R2-QA1-001：锁后重建基线可丢失 sealed 状态并跳过完整后检（P1，开放）

对应 R02.3/R02.4/R14、AC03/09/10/14/22/24/25。位置为 [profile_contract.rs](../../src-tauri/src/infrastructure/local_store/profile_contract.rs) 的 locked checkpoint（624）、after_native（666）、新 baseline/重新读取 credential（685–691）及仅 `if let Some(c)` 才 full_check（694–699）。首次 RO 前后/锁后早期确有比较，但后续 checked 闭包对 cold 也无条件承认新的 baseline；它没有持续要求本次已见凭据仍存在/原字节一致，完整账本义务又取决于新 baseline 中是否还有凭据。

这与两条 PM 只读解释一致的边界冲突：启动前全部辅助文件就已不存在且 RO 合法，可以 unsealed cold；**本次已见后消失必须按漂移拒绝**。本反例不是历史彻底删除不可检测的场景，也没有要求认证、永久 poison 或防所有非合作 TOCTOU。after_native 可合法改变恢复库/journal，不能因此丢掉原凭据绑定和必需完整账本后检。

| 最小反例 / 注入点 | 输入与实际结果 |
| --- | --- |
| cold 已见 credential，locked 后仅删除 credential | 新建 sealed、正常关闭；本次前置 RO/原锁核验通过后注入一次删除。`Stores::open` 返回 Ok，`admitted=true,error=null`，错误降成 unsealed cold。profile=`Q3/profile-ee8199f6-a629-41f0-a486-e4ee0730b185`。 |
| cold locked 后在原 runtime inode 追加29字节 | credential/目录/双库 inode 均保持；runtime SHA 从 `945aac6e9724924515563bc0d8118ede9b5289c259075bdc9da547b8ba26fcc3` 变 `992b414d8dc0ee916aa3440987e04cd270b3610243dc54c4e2a0e214c2a63445`。无 native 却重新建基线、返回 Ok。profile=`Q3/profile-99fb9aa6-aa58-490f-a0df-edec4813c901`。 |
| 真 hot_bad_old → 精确776/native rollback → after_native 仅删除 credential | 合法配置/activation/轮/冻结后，私有反例预先把两条 payload 末尾各加一个空格而保留旧 SHA，再在真实 commit_delivery COMMIT 前 cacheflush rc0 / `_exit(86)`。精确 raw extended776 断言通过；native close 后删除凭据，产品返回 Ok，输出 `profile_recovery_completed/result=admitted`，完整原 SHA 后检被跳过。profile=`Q3/profile-33327e1f-a5c1-491c-9a03-3a68e5e781ae`。 |

最强反例在已闭库后由独立只读 SQL 再核：sample `49c9fd4d-bd51-4735-9f5f-d9a6f41693bf` 存储 SHA=`9903751678ccaf81f50e22256ae9cf00ba84d183a3754d4917ed033b21dfe86b`，实际原串 SHA=`2632dd025a67dc6dd55e40e0672ae65b441cbd9ba4174438c06f127b7ac4ac95`；sample `32c4dc3a-f785-41e4-9073-26ea73deb86c` 存储 SHA=`9075ca687630ff49fabb65b84552bea63daf93741a40cca72a470550908c3a30`，实际=`7cd5e9bc5b30bf902ee29a61255539f38835e4f83d7c292a01bc17a97f17ff98`。两串各7265字节。after_native 删除前后 runtime SHA 都为 `a657d7bdd542e70cbd8b1b3b081fbf129dee3457fc479cd573cc1bb18061583e`，注入在该点只删除凭据；准入后的坏 SHA 不是正常恢复可豁免的内容变化。

实际 probe 日志 `independent-drift-probe-second.log` SHA=`89f90b6ad227ac213bb1ccd2442a5ebe9818c7538eeb421973036b4e48cf3700`。最强 `qa-result.json` SHA=`912cc7f61f45668383059f63cc214d50e5adf06ad34b9516e520ad98630f7376`，`qa-injection.json` SHA=`1a0ce26adb510352a686510a1897b8c2ad49df19af00a17d1a04cdfebbdb5dc1`。前/后 stat、inode、长度、SHA、子命令/exit86、完整 before 原文、实际 admission 结果均留于上述自有 profile；原始 journal 保留来源信息，不将阶段退出叫 SQLite pager 内部掉电证明。

返工要求：Development 在原 r2 范围内保持本次已建立的 sealed/credential/目录及同伴绑定连续性；cold 不得借重取 baseline 接受非 native 漂移；native 合法变化建立明确新基线时仍强制完整 RO 账本核验，凭据消失/改变须拒绝且区分已发生恢复写。保留上述失败和原门禁，不能通过把反例改为 expected admission、删除完整核账、增加自动补封/清理/永久 flag 来解决。实现返工后固定新候选、更新 tasks，再新的 fresh Verification。本 QA 未修实现。

## 16. r2 正向恢复证据、AC 与历史 finding 处理

新 sealed 正常路径的实际 commit_delivery 在 COMMIT trace 前 cacheflush rc0，子进程 `_exit(86)`；父测试实际匹配原始 extended776 后调用正式 factory。代表 profile=`Q3/profile-23139687-f57d-4772-aaf2-f71ae13c79e0`，journal58880B、SHA=`535cf47c680b550369e1c6de27962f883694117d2404fcdd445c23605e2d2ed1`。runtime native前 SHA=`d274d122d29d6d09afccfa7077a8beac83d9769bf49ce0654b686c85b8dee494`，native后与 RO后均=`6f9bef866ca300cd44fc7f2d5ae7b9e7db115a4f60a523d4d01bcd442a9ea033`，journal由SQLite回滚移除；正常恢复事务另行改变文件，未称整个DB未写。

该例 durable before SHA=`db556ec1ad30a0ba5dc284c7f3bafa36795887cfc78529ba2b887448cc329b22`、after=`fcde15cc3425093bfc68cbf7829af70331ea357f571ed77fff37e7d30784c31f`；独立逐行核11张原资料/配置/activation/轮/sample/delivery-cycle表及3张ACK/引用表守恒，0 receipt、2 pending、1 unknown，frozen batch ID/body/digest/成员/原时间不变，running=false。已 commit 后退出的另 profile 保持 durable after-commit 完整新态（1 receipt、2 acknowledged、0 unknown），并非“旧或新任一”。三处第二次 exit86 各用独立 profile，下次有/无 journal 均通过同等级后检并保留旧账。五份闭库全表原行、原串 SHA/integrity/FK 与 durable after 逐项相等，辅助只读核账前后 DB SHA 未变。

独立指纹 oracle 从本轮实际 SQLite 显式 schema 的 `(type,name,sql)` 原串取值，按 UTF-8排序并逐字段 BE-u32长度编码，不调用 Rust fingerprint：config=`sha256:64cc8187689bf3e04eb4b914811fe75e77a8d5dd6c0c895cfe12ed4814e1a806`，runtime3=`sha256:6657f7735d9932d561f0a1bc8ff836bf6190f678c5a6955520a665cab920ad4e`；均等于凭据/静态 golden，缺 PRIMARY KEY 的反例会改变指纹。辅助 actual allocated4096 + remaining ACK33550336 =33554432B；256KiB子预算包含于该32MiB。旧页 journal340296B另计，`reserved100999496+aux4096=old340296+3×33554432`，无新增配额或双计。

| 项目 | 本轮独立结论 / 仍开放边界 |
| --- | --- |
| F-QA1-001 | **在 r2 新 sealed、材料未漂移的限定正常路径，原 RO 自举缺口修复已验证，可在该限定范围关闭。** r1 QA1/QA2 原失败不改写；旧 unsealed hot 仍按 r2 合同拒绝，不把它称恢复成功。新 F-R2-QA1-001 是额外必需门禁失败，不能据前者已补证而称整个恢复验收通过。 |
| F-QA1-002/003/004 | 沿用 QA2 已关闭结论及同SHA实现/有效40项协议、计数/UI证据；本轮未重跑该未变矩阵，没有把其内容悄然扩大为真实HTTP。 |
| AC01/02 | A0/本轮保护检查通过；精确批准、54/18候选、provider pins与角色权威一致；只用全新自有合成资料，没有打开真实旧库证明未打开。 |
| AC03/09/10/14 | 正常新 sealed/完整旧新账、unknown停态及兼容检查通过；**因 F-R2-QA1-001 整体 fail**。真实网络/Owner重开部分仍需 B。 |
| AC04–08/11/13/16 | 未变 r1/QA2 有效有限证据继续复用，原限制保持；新完整后检接受合法 partial/cached ACK/拒绝父子 cold。实际provider采用/HTTP/TLS/证明寿命仍未验证。 |
| AC12 | 既有 r1 QA2 合法大ACK/8MiB空白资源上限普通SQL rollback证据保留；新辅助分账、低空间拒绝及真实普通ACK hot恢复通过。8MiB空白不称provider普通输出，未重新跑旧整套。 |
| AC15/17 | Node13/build/580键/30次locale解析、文档38目标、源码/diff/资源归属通过；原生明暗/窄窗/OwnerM05未执行。新诊断名和锁接线已核，新 finding 及未执行项如实保留。 |
| AC21 | 有限初始化时序/故障/no-replace矩阵通过；末次unlink后fsync当次拒绝无业务日志，下次完整可见sealed cold独立核验，不追认前次成功、不称掉电证明。 |
| AC22/24/25 | marker/strict凭据/头/15类异常、双journal、early TOCTOU、真实外锁及正常三处再次退出通过；**已见凭据/快照在后续阶段丢失仍准入，fail，见 F-R2-QA1-001**。 |
| AC23 | 在无漂移新sealed路径，实际未提交ACK恢复完整旧账/已commit保留完整新账通过；受控恢复整体仍受新finding限制。 |
| AC26 | macOS辅助子预算/Unix身份/原兼容边界及双语说明有限通过；非Unix源码静态审阅不算Windows运行证明。Linux/Windows原生、filesystem掉电与恶意防篡改保证均未取得。 |
| AC18/19 | **blocked / 未执行**：具体 B HTTP/DS/MySQL/Docker/schema/source/Owner原生操作未批准，无真实双方端到端核账。 |
| AC20 | **未满足**：r2 qa_failed、A0/A1未全部通过、B未执行、Human Owner最终接受pending，完整阶段C未完成。 |

## 17. r2 证据、资源与串行 handoff

| Q3关键证据 | SHA-256 |
| --- | --- |
| profile-contract.log | `bdbd28cab07fb473c70b7bb69edeabdf7fd9e931f9c74ed0a45f1ccad8e9b9df` |
| candidate-audit.json | `921e9541b1ab0e3858cbd35ef42cce220b25d8aaa15e5d09b529185e589e5aaa` |
| independent-evidence-audit.json | `98aa90f09501e305671bb3eeadd6338d9859ca7af4c75a43186213b48e42aa1d` |
| independent-drift-findings.json | `d4216e876827e2f1fc27fc77a92fd81bef2ce731fa029ce4b99812d344f72950` |
| independent-probe/provenance.json | `02152e99845c86cb11751891168ce66a244bbe736b763bc97a28f2991543d448` |
| qa-command-summary.json | `8daec57562adcc7300856a553d69203fd4f5e33fd013b9ac4a43367d32fb4799` |
| resource-inventory.json | `52ae88386eb78da5afcb0d739f42016428c55206c5625eee37d535f99f37fd21` |

Q3现有61个合成fixture目录、112个SQLite文件，均为本轮从零生成；8个核心 witness 目录为五份正向 durable账与三份最小反例。所有本轮调用的子程序均已wait返回，真实profile锁在关闭后释放；无自有服务/listener/GUI/设备/数据库服务/Docker/分支/worktree。Verification不执行回收；Q3根报告、命令/日志、原文账/原journal、最小probe/provenance、checklist-before及8个核心witness继续依赖于返工/新QA/Owner审阅，须保留。`Q3/dist`和 inventory 标为可再生的其余有限夹具，在 Root 确认后续/证据依赖解除后可回收，不能因为失败而先删反例。DEV r2 frozen source-after/diff/manifest与r1历史hot/原文/QA证据仍按此前依赖保留；不读取/恢复/清理这些旧SQLite。既有真实配置、历史、原联调profile/真实.env及共享 target/node_modules/dist不是本QA清理对象。

本文件已经持久保存关键命令、反例触发/结果、原账标量、SHA、风险与未执行面；临时路径不是唯一结论来源。最终 evidence-manifest 和外部 `Q3/qa-final-handoff.json` 固定本文件SHA、candidate/spec/tasks未变及项目只写审计，避免本文件自引用。主协调接收后才机械同步四处索引，并将 F-R2-QA1-001 返回 Development；在新的 Development handoff 后必须另开 fresh Verification，当前QA不静默修或继续占写实现。Human Owner final acceptance 继续 pending，没有A-only完成、完整阶段C接受或任何部署/真实联调授权。

---

## 18. r2 QA2：返工精确候选与独立结论（2026-11-06）

新的实际 fresh-context Verification `/root/daa008_r2_verification_2` 对 **aiis-ics-arch::DAA-008 r2 F-R2-QA1-001 返工 developer_handoff** 给出 **qa_failed**。原 P1 漂移 finding **F-R2-QA1-001 已独立关闭**；正常 sealed 热恢复、完整旧/新账和阶段漂移也通过。但是，正式源码的默认并发矩阵再次在初始化故障后的立即重获锁断言失败，形成 **F-R2-QA2-001（P2，开放；验证门禁，产品/夹具原因未定）**。串行22通过不能覆盖这次真实失败，当前 A0/A1 不记全通过。

本轮只替换顶部 Handoff 并追加 §18–23；Status 继续 qa_failed。r1 QA1/QA2 和 r2 QA1 §1–17 正文原字节保留。进入本轮的完整 checklist SHA 为 `137fe21ac4eaf3c1e5ccc89694cb971485587be67bbfc3c552b3f630cf31d003`，原件存 Q4/checklist-before.md；原 Handoff 保留如下：

> r2 QA1 -> sole coordinator /root -> Development rework F-R2-QA1-001; new fresh Verification required after handoff; A0/A1 not fully passed, B/AC18-20 and full Stage C unexecuted; Human Owner final acceptance pending

| 精确输入 | 本轮独立重算 SHA-256 / 身份 |
| --- | --- |
| approved spec / tasks | `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de` / `a7ea253733e0c4dddd36f36e53bd50ca10a3e9f01868871a49d7fdddc0770992` |
| 正式交付树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch` / `bcafa89fa31bdf62329bced89baebc193323a739`；未提交交付 |
| r2-rework-source-manifest.json | `49bf21d9c80c93acd7872f863ef3730c03dd2b131b0c50343a273510648eb589`；54项、本次返工2项、相对r2 entry累计18项 |
| source scope | `6fd00d43b165268f1b175bf3e7cd106cbabb657601a1613678e9a3b5ff0e21fa`；sorted UTF-8 path+NUL+after SHA+LF |
| r2-initial-to-rework.diff / r2-entry-to-final.diff | `dde87fa8d003d844b5fad01b4c6c16d20df64952c34e1aae785b75a5062bc474` / `07e58beb84509b433a1efac3caaa589cbc153002fc5fb453e9c9e06bd708b814` |
| r2-rework-developer-handoff.json | `8f251d420e1ef51ec25353793a0766bf63a9b84443f9867cd7683d9b8fc8e038` |
| 实际 verification TOML | `ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`；与 AIIS 源逐字节一致 |

DEV材料在 `/private/tmp/daa-008-r2-a-dedws2xe/development/`。54项正式源码及54项 after 原件均匹配 manifest；用初r2 source-after 与 Root entry 公开原件重构两份 diff，均逐字相等。返工仅 profile_contract.rs=`c6b6873d98d6446382d2465b608e6d471592f5852e8d6cf53bc804e021f2711d`、profile_contract_tests.rs=`1b092904a3051b150be597615cb081da5afaf44f35203dfb78fa69f86f69882e`；其余52项与r2 QA1一致。1005项 DEV evidence-manifest 公共源码/JSON/log/journal证据逐项SHA匹配，未打开旧SQLite。10个 provider pins 和原 ProfileLock 保持；source-after 是审计附件，正式树是构建及交付真相。

## 19. r2 QA2 独立性、环境、命令与复用

Q4=`/private/tmp/daa-008-r2-a-3t3ig0tg/verification-2`；其父根由本 Verification 从零 mkdtemp/canonicalize、mode0700，Q4亦0700。全部实际 SQLite、marker、mutation、child、crash 与恢复仅在该新根从公开结构/合成值产生。没有继承 Development/QA1 对话推理；独立读根 AGENTS、根/AW/DAA README/PLAN 双语、local_store 和 src/app 最近规则、actual verification TOML/canonical workflow、完整 spec/tasks/checklist、实现、两份 diff 和可用输出。按表面使用 aiis/project-governance/rust-runtime/desktop-tauri/code-document-indexer、backend-arch、frontend-ui/i18n-workflow，只验证不修复；role TOML 的 model/effort 仅为配置证据，不声称平台 ACL、强制路由或可观测运行值。

macOS15.7.7 arm64；rustc/cargo1.89.0、Node22.19.0、pnpm11.11.0、应用0.1.0；无安装/依赖升级。产品 SQLite 仍为原 bundled3.46.0；辅助 Python SQLite3.43.2 仅只读本轮已闭库的新夹具。每个产品命令由 Q4/run_check.py 清除继承 DAA_*/VITE_DAA_*、显式 TMPDIR=Q4，在正式仓根执行，逐项保留 argv/cwd/env边界/pid/exit/log SHA。没有 Bootstrap::load、dotenv/default/真实/8590/旧profile访问，没有HTTP/loopback、GUI、DS/PLC/MySQL/Docker、子Agent、额外notifier、外发或删除动作。

下表 M=`automation-world/data-acquisition-agent/src-tauri/Cargo.toml`，P=`Q4/independent-probe/Cargo.toml`。所有 Cargo test/check 都使用现有锁、`--offline --locked`；所有 filter 后均带 `-- --nocapture`。这是实际子命令退出码，未用 wrapper 的0覆盖101。

| 编号 | 实际命令 / 检查 | Exit / 结果 |
| --- | --- | --- |
| Q4-01 | `cargo test --manifest-path M --offline --locked --lib profile_contract_ -- --nocapture` | **101；21 passed / 1 failed / 0 ignored、102 filtered**。初始化fault用例在sqlite_close阶段立即重获锁失败；其余21通过。 |
| Q4-02 | 同前命令，末尾追加 `--test-threads=1` | 0；22 passed / 0 failed / 0 ignored、102 filtered；43.05秒，明确为隔离诊断，不能覆盖Q4-01。包含一个无参数child helper，不称22项独立现场场景。 |
| Q4-03 | `cargo test --manifest-path P --offline --locked --target-dir /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/src-tauri/target --lib qa_r2_ -- --nocapture --test-threads=1` | 0；3独立反例全部正确拒绝。 |
| Q4-04 | 正式test前缀，分别filter=`v2_keeps_schema_configuration_history_ids_sequence_and_pending`、`unknown_reopen_same_identity_and_stopped`、`unsealed_hot_journal_is_refused_without_recovery_authority` | 各0、各1 pass；从零合成v2/unsealed v3，原配置/历史/ID/seq/pending及冻结身份保护，不补封；unsealed hot拒绝且journal原件保留。 |
| Q4-05 | 同前缀，分别filter=`time_contract_legacy_unknown_single_and_identity_reject_before_lock`、`time_contract_lock_second_check_detects_empty_and_valid_drift_before_rw` | 各0、各1 pass；未知/身份/旧时区/WAL和原锁后漂移门禁保持。 |
| Q4-06 | `cargo fmt --manifest-path M --check`；`cargo check --manifest-path M --offline --locked --features rust-snap7-driver`；同check改feature=`local-validation` | 各0；无设备动作；driver无新增warning，local-validation原9项unused提示保持。 |
| Q4-07 | `python3 -B Q4/evidence_audit.py` | 0；两次正式执行各5份正向闭库的全表/原串/ACK独立核账、三probe注入差异/两坏原SHA、28份formal拒绝记录（每次14）及DDL/aux预算核准。 |
| Q4-08 | `python3 -B Q4/candidate_audit.py`；`python3 -B Q4/static_audit.py`；脚本内明确18路径的 `git --no-optional-locks diff --check` 及两份diff的 `git apply --check --reverse --whitespace=error-all` | 各0；54源码/两diff、10pins、38本地文档目标、580双语key及placeholder、15诊断key核准。 |
| Q4-09 | 仅对失败fixture原锁 inode 的一次Python `fcntl.flock`（exclusive + nonblocking） | 0；所有已知factory子进程结束后可取锁，未重试；只证明这一后续时点无持续占锁，不确定失败时持锁者。 |

Q4-03临时probe复用先前QA的公开hook/三最小断言，全部夹具重新创建。当前正式profile_contract/schema/capacity/ProfileLock等均按正式路径直接导入；临时接线只加绝对module path，移除后与正式原文逐字相等；当前正式测试只加checkpoint注入和三个独立断言，移除后逐字相等。没有免锁/免凭据API或生产语义改写。原始FD操作只发生在SQLite关闭的locked/after_native阶段，真实OS锁始终由正式工厂持有。provenance及hook-only/wiring-only diff留于Q4/independent-probe，不属于交付候选。

未变52项的wire/UI/Node/build/i18n有效证据按r2 QA1及r1 QA2复用，没有重复40协议或StageB全套。已核r2 QA1 node13的日志SHA=`ecca10608b556fcc3694eacb34f5634c93a4490c661595ee4055b2134ead6d4b`、build=`a8a8684e3e4a0d119a23075490786678e09e2fd7655844c0f70f370d58a729e8`、实际locale切换command及同SHA locale；原生明暗/窄窗仍未验证。正式tests保留empty_for_test警告；补充probe的36项unused来自没有产品composition root的调用图，未添加allow。QA辅助初次误取entry manifest位置和旧QA构建log文件名各exit1，修正仅Q4临时helper后形成上述成功报告；不算产品失败，记录qa-helper-failures.json。

## 20. F-R2-QA1-001 独立关闭与恢复账本

独立probe三例全部从零构造，未调用DEV新rework_drift_case。结果与原QA1错误准入相反：

| 最小输入 / 注入 | 本轮实际结果 |
| --- | --- |
| cold、locked后只删本次已见credential | profile-060df085-20ef-4210-a90f-96c00178e5b2，`admitted=false`、profile_contract_business_admission_failed；runtime SHA保持`36dcf68ce9d4a60519de000030a19cd7e1ee7d00fc0f76d7641ea03a62dc4a21`，不降级。 |
| cold、locked后同runtime inode追加29字节 | profile-d155828d-764b-4bff-8da4-604ad5743df4，只有runtime材料变；SHA `ce17b1e1308b55181e8f6671434610da57168c1cecccd5e6a151b7c6c5331cf9`→`cf725648c3f167f38d49d107e8ebf6af46c6620ccf57a84ef178495cb61fa722`；admitted=false、profile_contract_business_admission_failed，不重取cold基线。 |
| hot_bad_old、真实cacheflush0/exit86/raw776/native close后只删credential | profile-8359e0bb-2bb7-408a-811a-505e48565f31，admitted=false、profile_recovery_business_admission_failed；日志recovery_write_completed=true，journal由SQLite去除，业务拒绝。注入前后runtime SHA均`e3adea04d3c980f7af476049f63a1531fff4e08ed3fb69960ef7e38ef4e89128`，该点只删credential。 |

最强例的两条payload仍各7265B；独立闭库RO核得 sample de49a2db-dc47-4535-8ccd-9aba644b5c68 存SHA=`4d96c2fe5a1e154ed13d8f4d7f33765d07556a8176d9ff88d08ea5711716373a`，实际=`e3d706792b7b19739324a3660fdb9e824f2eeb668089ac29cad441bfe262541a`；sample 3c2d8827-e353-40cb-afb8-111d4927d511 存=`619fb507b743734b0bab0817598ae827dde2264f065be5ba2504eb26f2262090`，实际=`b8033da5a5a8404a1fbdb64c9420a9a0806bcf15eb4ea62ecda50338ed70654c`。坏资料被保留而业务拒绝，不声称数据被修好。durable before SHA=`a6d1a1f38a083de67ada29f270439e2a1653b4ec888df5ad66da58d01f5a574e`；注入/结果SHA=`5aa3333d02389dbf78bec2eb5c0d1a47912fb5d21fbd5bdb4c217288d12b2cdd` / `f241c4890340369e5dbf6b8c872992009c93e6b8ce7f6b7304e923c9411f4ae0`。

源码已核：cold以原before为expected；完整sealed核账义务来自原credential或本次初始化返回的contract。native_closed之后只豁免失败库/对应journal的pager变化，目录canonical/identity/mode、credential原材料及同伴库必须连续，随后固定新基线；after_native/after_ro漂移均拒绝。初始化在原RO前后及安装前后守住DB材料，返回本次installed/contract，在sentinel_removed hook前锚定。正式两次矩阵中的每次14条组合（原3+新增11）均拒绝，覆盖native_closed凭据改字节/换inode/同伴变化、native新基线后变化、RO后变化、initial_ro_checked与sentinel_removed变化。P1按这些实际证据closed；原QA1三失败正文保持。

正向代表profile-31751c93-ab38-4a8d-80af-7358e17ed5ac：真实COMMIT trace前cacheflush0、child exit86、raw776；原journal58880B，SHA=`63ae52f50c0b1952ca4ba3f85fe1428d4706e9f9dc765eab59d8c9ed0587ef68`。runtime native前=`fac335a70ee7db1754e2b3f175fa3dfed269f287e7a763c1f8f090aa4ff83d9d`，native后/RO后=`eb04cb9d91d127a11d1aea8d91f4a99f3d3dd53d1dce3f7488ff02aaccb20bd7`；明确发生恢复写，不称整个DB SHA恒等。durable before/after SHA=`8c98ba4c6039b767936f82a314c072af18eb7de90915cb9d01c41bbf932c1526` / `51ab9956a1264370ec106e4c69520768d6c2eea9339457bc3028d706d00ea5c4`。两样本原SHA=`919f3f8a57c8483ae49f8de0ed48a722ca22d7bc4907ba79f3db57f896e9ef5c`、`c63e006de519c2b9d7119bfc23a9beb3ba137d41ab8f3f918c80c9a8fe6aedc5`，manifest=`f3ad95bc48a0061a8cf85f1a891a2d88052543ed15411f62c7c04240afd16519`，context=`4c67529e264bcc6f13ab05d1d872bd1b2e4248b36bd9e8543239c4fcdbbd54a1`；原材料及ACK/引用14表守恒、0 receipt/2 pending/1 unknown、原batch/body/digest/成员不变，停态。

两次正式执行各5份正向闭库（普通hot、已commit、三处二次exit），共10份完整表账/原串/integrity/FK均独立匹配durable after；已commit严格匹配after-commit的新ACK态，其余严格保持旧ACK及unknown，不用“旧或新任一”。辅助RO核账前后DB SHA未变。独立实际DDL编码仍得config=`sha256:64cc8187689bf3e04eb4b914811fe75e77a8d5dd6c0c895cfe12ed4814e1a806`、runtime=`sha256:6657f7735d9932d561f0a1bc8ff836bf6190f678c5a6955520a665cab920ad4e`。aux allocated4096+remaining33550336=33554432；reserved100999496+aux4096=old340296+3×33554432，256KiB包含于原extra32MiB，无双计或新额度。

## 21. F-R2-QA2-001：并发初始化故障后立即重获锁再次失败（P2，开放）

这是**重复真实验证失败且原因未定**，当前证据不把它直接归为生产持续FD/锁泄漏，也不将它解释成已证明的fork继承。对应R02.2/R14、AC21/24及交付检查完整性；位置为 [profile_contract_tests.rs](../../src-tauri/src/infrastructure/local_store/profile_contract_tests.rs) 的fault循环及第588行原重获锁断言的诊断分支。原ProfileLock实现和重获锁期待未改。

最小已证实触发范围为Q4-01的完整22项默认并发命令；没有声称单独用例也失败。输入全部本轮合成：fault循环在真实factory初始化的`sqlite_close` checkpoint返回synthetic_profile_sqlite_close，未建业务日志；随后再开因sentinel拒绝；紧接着对同一profile调用原ProfileLock::acquire，得到profile_locked，panic文本：`sqlite_close: lock not released: profile_locked`。父命令exit101，21pass/1fail。DEV此前同矩阵21/1的真实失败也已核日志，其当时没有现场PID/FD，不能事后补造。

本轮故障现场profile=`Q4/profile-e8aaca4e-2682-42ab-9e2f-a427287632c0`；initialization-lock-failure.json SHA=`f9be2ae2e007cd7620882e871270eb0e960ca9416749b73df6319f775d94b115`，记录pid83784、lock dev16777229/ino80841543、stage=sqlite_close、firstInitializationError=synthetic_profile_sqlite_close、ownFDsScanned=27（上限4096）、**ownMatchingLockFDs=[]**。这是当前进程自有FD的fstat结果；没有失败时外部持锁者/已知child关联快照，不能据空数组推出没有其他进程持锁。没有扫描真实资料或全机进程/FD。

Q4-02以同源码显式串行取得22pass，仅用于隔离差异。全部已知factory子进程结束后，于2026-11-06T03:09:24.579130Z对上述**同一dev/ino**作一次非阻塞Python flock成功，随后立即unlock/close；无循环、sleep或重试。这只排除该后续时点的持续占锁，不能追认失败时原因、替换失败结果或证明生产锁完全无缺陷。

**Handoff给Development：** 保留默认并发exit101、serial0与现场JSON；在本任务自有新profile/明确owned children内取得必要持锁者/FD及spawn/close/wait生命周期证据，区分产品资源归属和夹具并发边界。若需合法夹具协调，仅在既有test allowlist内实施并保留原锁断言；不得改生产重试/锁语义、加重试直到pass、skip、削期待或用串行摘要宣称原并发通过。当前不能判断生产修复是否必要；下一gate是精确新Development handoff与新的fresh Verification，不由本QA修源码或擅自接受未定因失败。

## 22. r2 QA2 AC更新与未执行门禁

| 项目 | 当前独立状态 / 边界 |
| --- | --- |
| F-R2-QA1-001 | **closed**，三独立最小注入及正式阶段连续性均拒绝；历史失败原文保留。 |
| r1 F-QA1-001 | 沿用且本轮补证：仅r2新sealed、材料未漂移路径的RO自举缺口已关闭；r1未sealed hot仍拒绝，历史失败不改写。 |
| F-QA1-002/003/004 | 沿用r1 QA2已closed的同SHA实现/有效协议、计数/UI证据；合法partial/cached ACK、父链cold仍在本轮正式矩阵通过。 |
| F-R2-QA2-001 | **open / failed verification gate**；重复默认并发锁断言失败，原因未定，不能将A0/A1汇总为passed。 |
| AC01/02/17 | 本轮身份/批准/源码交付/保护与记录通过；54源码/两diff/10pins/只写审计保持，失败/复用/资源如实记录。 |
| AC03/09/10/14/22/23/25 | 新sealed正常cold/hot、已知commit前旧账/commit后新账、三处二次退出、完整后检及P1漂移关闭的限定功能检查通过；整体交付仍受上述验证门禁限制。实际网络/Owner重开另需B。 |
| AC04–08/11/13/16 | 未变r1/QA2与r2 QA1有限证据按同SHA复用；不外推真实provider采用、HTTP/TLS或证明寿命。 |
| AC12/26 | aux子预算/低空间拒绝/普通真实ACK hot通过；r1 QA2 8MiB空白资源上限普通rollback继续有效，不称provider普通输出或本轮重跑。macOS实证不推出Linux/Windows/掉电/恶意防篡改保证。 |
| AC15 | 同SHA Node/build/locale证据复用、当前580键/placeholder再核；原生明暗/窄窗/OwnerM05未执行。 |
| AC21/24 | 串行初始化故障/no-replace/封存顺序、exact776正反门禁/外锁等有限检查通过；**默认并发锁释放断言失败，必要验证gate开放**。末次fsync错误当次拒绝、下次完整sealed独立cold全检，以及启动前aux全无的unsealed解释均按PM原澄清，不增poison/补封。 |
| A0/A1 aggregate | A0恢复增量的源码、编译及独立P1检查通过；A1当前qa_failed，整体本轮qa_failed，不能称全A通过。 |
| B、AC18/19 | **blocked / 未批准未执行**；无HTTP/loopback/DS/MySQL/Docker/source-schema采用/Owner原生双方端到端核账。 |
| AC20 / Human Owner | **未满足 / pending**；完整阶段C未完成。QA不授Owner最终接受、B运行或部署/发布权限。 |

## 23. r2 QA2 证据、资源与最终串行交接

| Q4证据 | SHA-256 |
| --- | --- |
| factory-parallel.log / factory-serial-diagnostic.log | `13f221595f604c9cb8dd5443c2c88768fda6dadb71f84c6575a77f9fc556fbb7` / `c41825fe30d611dd3c8f62b1475d7f5a2824036ebdb66dc3a239c10c1dac2f22` |
| independent-three.log | `f2001411d9cc56fdfc6622fead378d9a29278b5c0723c56a0df573b1bb07b0a4` |
| candidate-entry-audit.json | `c9fc2dfbd13657640b765443ad1d14a845a0114de777300be85a1f195ebdd788` |
| independent-evidence-audit.json | `3f565246e59cceb8761f24e477efe542b189f794ada4e9054dd3f3780e7d4527` |
| independent-probe/provenance.json | `b18e81810830abe17c149379272a8ef226fbd5186c16b538efe62cb392a054f6` |
| owned-lock-post-children.json | `30b1f55e3c51c264d5bf95550feade2a2b150bf7d17b87b118637c10cb1c294f` |
| qa-command-summary.json / static-verification.json | `db14b928c71ef823add9c6eafad73e2ad0e7d5c87c74c9f405c9cf295f756905` / `1ff3b82314963570e0f09c9c0a16bb187eb8318c3972beb7395b95e27a5c601c` |
| development-outputs-audit.json / resource-inventory.json | `e52dbcd200aea0c016d4e88d32653aef0ef05515855505f8a8c005ab2e17135b` / `9eef4ea18fb5fe7bfa813c3fa6d80e03eb78ca5e0201bed43c24af3f93f96452` |

Q4盘点时点1151个文件、140个合成fixture目录、258个普通SQLite文件；inventory逐项metadata及14个核心witness（10份正向、3独立反例、1锁失败现场）已列。所有本轮直接命令及技术child均wait返回；没有listener/GUI/设备/数据库服务/Docker/分支/worktree或需要接手的运行连接。失败原inode的后续单次取锁证据另列，不能替代失败时归因。共享Cargo target/node_modules/dist不属于本QA可删资源；没有安装。

Verification不执行回收。Q4的命令/成功失败log、before-after完整原账/原journal、probe/provenance、故障现场及closed-checklist before、正式source manifests/diffs与旧QA/DEV证据均仍有返工/新QA/Owner依赖；Root确认依赖解除后才按归属处理可再生资源。旧r1/r2 QA/DEV SQLite未被本轮打开、恢复、补封或清理；真实env/default/原8590/联调profile和历史永不列为本次清理对象。关键错误、标量、原SHA、命令和边界已持久在本checklist，不只依赖临时路径。

项目内唯一写入为本checklist；spec/tasks、54源码、实现/测试/配置/索引均未修改。最终Q4/qa-final-handoff.json固定checklist SHA、history-body保留、source/spec/tasks未变与只写审计，避免自引用。**最终qa_failed经唯一Root返回Development定位F-R2-QA2-001；任何返工后必须新的fresh Verification。** P1关闭不抵销当前失败，Human Owner仅在后续独立结果后决定最终验收；当前没有全A、完整阶段C或Owner最终接受。

---

## 24. r2 QA3：P2夹具协调精确候选与独立结论（2026-11-06）

新的实际 fresh-context Verification `/root/daa008_r2_verification_3` 对 **aiis-ics-arch::DAA-008 r2 P2测试夹具协调 developer_handoff** 给出 **qa_passed，仅限已批准A0/A1范围**。F-R2-QA2-001在本节固定的新候选下 **closed**：原立即重获真实ProfileLock的断言、13项故障/no-replace期待及真正跨进程hold_lock用例逐字保留；本轮一轮22项默认并发、两份同时启动的exact故障命令及退出前证据均通过。没有新增finding。

旧DEV/QA2的默认并发21pass/1fail、串行22pass、ownMatchingLockFDs=[]和后续单次取锁成功均继续作为真实历史保留。**旧失败原因仍未确定**；本结论关闭当前合法夹具所有权边界下的验证门禁，不追认“fork继承已证实”，不提供任意并发或生产锁全面无缺陷的保证。B及AC18–20、完整阶段C、原生视觉和Human Owner最终验收仍开放。

本次仅更新顶部Status/Handoff并追加§24–29；r1 QA1/QA2、r2 QA1/QA2 §1–23正文原字节保留。进入QA3的完整checklist SHA为 `b74c0e90ae7b0d0a4076434352b150c55baebde99d825ec831058d21b00ff6c6`，原件存Q5/checklist-before.md；其顶部Status为qa_failed，原Handoff为：

> r2 QA2 -> sole coordinator /root -> Development investigate F-R2-QA2-001 repeated parallel lock assertion; F-R2-QA1-001 independently closed, overall qa_failed; new fresh Verification required after next handoff; B/AC18-20/full Stage C and Human Owner acceptance remain open

| 固定输入 | QA3独立重算SHA-256 / 身份 |
| --- | --- |
| approved spec / tasks | `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de` / `47b1585d3d2eb7309acafd778ed3c1638ede23a85c3d06776d39a6d066810ff8`；spec §16精确批准r2/R02/§11.1有效，draft历史不改写 |
| 正式交付树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch` / `bcafa89fa31bdf62329bced89baebc193323a739`；未提交源码交付 |
| p2-source-manifest.json / source scope | `ebfa1abaca2d87f5f1d0ba13a018c9d07e89da93ef6b1c2dccadba84c8132e0c` / `26cebdb087c5aa4be93fd431bec1a54d253e104ca57fd5ee1d0b3a4e9aa57b7c`；54项，sorted UTF8 path+NUL+after SHA+LF |
| previous-6fd-to-p2.diff / entry-to-p2-final.diff | `9d3d0213f20631ea7425d48aaa3faecb46dd28f3c65dbb09f4f5c45669f56377` / `bc7138f68bf185083845344bbedda5e3b0c4c8e4ae4c2fd1071e025c015bd258` |
| p2-developer-handoff.json | `f78c6da266c6e34d5d3422e9aabf792672cf04becbdea9e224b82dfa100a7aad` |
| QA2最终receipt | `eeb9e8c172ea26c8a45542ca6fe07b4644e3bb91e29986f32e531c6c0d41ae21`；qa_failed及P1已closed事实保留 |

DEV材料在 `/private/tmp/daa-008-r2-a-w7gv433k/development/`。正式54文件及54份source-after均匹配；用QA2候选公开source-after及Root entry公开原件逐项重构两份diff，均与上述diff原字节相等。P2仅 `profile_contract_tests.rs` 从 `1b092904a3051b150be597615cb081da5afaf44f35203dfb78fa69f86f69882e` 改为 `625b2b6787b39b95de22193e220b64fc713eaa7cdfc41b2bc459a719baa83c62`；其余53文件与QA2相同，生产profile_contract仍为 `c6b6873d98d6446382d2465b608e6d471592f5852e8d6cf53bc804e021f2711d`。相对r2 entry累计18项变更、只新增已批两个源码文件。原ProfileLock、生产重试、依赖/feature/env/入口/locale均未改；source-after仅为公开证据副本，正式树为编译与交付真相。

## 25. QA3独立性、环境、命令及证据复用

Q5=`/private/tmp/daa-008-r2-a-bn98kwjd`，本Verification从零mkdtemp、canonicalize、0700；两份有限并发复验分别使用Q5/overlap-1和Q5/overlap-2。独立读取根AGENTS、根/AW/DAA README/PLAN双语、local_store最近双语规则、actual verification TOML/canonical workflow、完整当前spec/tasks/checklist、正式工厂/ProfileLock/测试和精确差异及可用DEV输出。没有继承Development/旧QA对话推理；只消费当前持久文件、公开源码和收据。按表面使用aiis/project-governance/rust-runtime/desktop-tauri/code-document-indexer，只验证不修复；未变UI/协议证据按同SHA复用。actual verification TOML SHA `ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`，与AIIS源普通文件逐字节相同；model/effort仅为配置证据，不宣称平台ACL、强制路由或运行模型观测值。

macOS15.7.7 arm64、rustc/cargo1.89.0、应用0.1.0、原锁/现有依赖，无安装。产品仍使用固定bundled SQLite3.46.0；辅助Python SQLite3.43.2仅只读本轮已闭库的新夹具。产品命令清除继承DAA_*/VITE_DAA_*及RUST_TEST_THREADS，显式TMPDIR；原环境这些键实际均不存在。未调用Bootstrap::load、dotenv/default profile或完整产品入口；无真实/旧/原8590/DEV/QA1/QA2 SQLite访问或复制、补封、恢复、迁移、清理。无HTTP/loopback、GUI、DS/PLC/MySQL/Docker、子Agent、额外notifier或外发消息。

下表M=`automation-world/data-acquisition-agent/src-tauri/Cargo.toml`，cwd为正式仓根。实际argv/env边界/pid/exit/log SHA保存在Q5/*-command.json；每项exit均为真实被调用命令结果。

| 编号 | 命令 / 检查 | Exit / 实际结果 |
| --- | --- | --- |
| Q5-01 | `TMPDIR=Q5 cargo test --manifest-path M --offline --locked --lib profile_contract_ -- --nocapture` | **0，22 passed / 0 failed / 0 ignored，102 filtered，测试15.91秒**；默认并发，无serial override；含一个无参数child入口helper |
| Q5-02 | 同时启动两份 `cargo test --manifest-path M --offline --locked --lib infrastructure::local_store::profile_contract_tests::profile_contract_initialization_faults_and_no_replace -- --exact --nocapture`，TMPDIR分别为Q5/overlap-1及overlap-2 | **各0，各1pass/0fail/0ignored**；先spawn两份再wait，case窗真实交叠；有限两次，无重试直到通过 |
| Q5-03 | `python3 -B Q5/audit_fixture.py` | 0；原断言/期待/child launcher/外锁函数逐字一致，3套39故障及3次no-replace，父子PID/inode/退出前证据核准 |
| Q5-04 | `python3 -B Q5/audit_ledgers.py` | 0；五份闭库全表与durable after相等，原文SHA/integrity/FK/独立DDL指纹及RO前后DB SHA核准 |
| Q5-05 | `cargo fmt --manifest-path M --check` | 0；Q5/fmt.log为空；正式默认矩阵已编译当前测试，未重复无变化构建 |
| Q5-06 | `python3 -B Q5/audit_candidate.py`；`python3 -B Q5/audit_static.py`；后者内执行显式18路径的 `git --no-optional-locks diff --check -- ...` | 各0；54/53/18候选、两diff、10pins、实际角色/原锁、38文档目标、580双语key/placeholder、9份DEV/QA收据与5份DEV命令日志核准 |
| Q5-07 | stdlib本轮phase/budget、owned child和资源审计 | 0；正式14阶段漂移全部拒绝、aux预留等式成立；31份child命令，38个明确owned PID在审计时均无运行实例 |

正式矩阵保留既有config/mod.rs的empty_for_test warning，无新增allow抑制。Q5-03首个QA helper因把最终LF计入公布的无LF断言SHA而exit1；旧/新断言本已相等，仅修正Q5 helper范围后得到原SHA并exit0，见qa-helper-failures.json。没有改产品或削断言。

复用依据为53文件逐字节未变，及已核SHA的QA2独立P1三反例日志、10份正向账本报告、原默认并发失败和串行诊断日志；旧SQLite均未打开。本轮默认矩阵另核14阶段拒绝及五份新正常账。未变wire40矩阵、UI/Node/build/实际locale切换及feature编译沿用此前QA有效证据；没有重跑阶段B、后端或DS整套，也没有把这些有限证据扩大为真实HTTP/原生视觉。

## 26. F-R2-QA2-001关闭依据：原义务保留及退出前锁释放

P2只调整测试进程所有权：父测试创建空控制目录后，由现有exact child helper的技术mode启动独立进程；13个case各自的新profile由该子进程从零创建/打开。case helper不spawn其他程序；父测试不预开case的SQLite或锁。子进程内仍逐项执行 **Stores失败→未完成sentinel重开拒绝→立即调用原ProfileLock::acquire→drop(lock)**，失败仍原panic/fstat诊断，无retry或skip。子进程实际取得并drop原锁后才写case记录/套件报告，父测试wait其exit0后再核报告PID和SHA，故退出释放不能代替原立即断言。

独立字节比较核得：原立即锁断言/诊断/drop段SHA仍为 `aad28a6c1a7498b7eee0fc5b62b2be29b8edb110d3c808ff35b75298d2e7dae8`；13阶段数组、各fault期待和no-replace竞争材料期待原字节一致。原真实外部hold_lock测试函数和原child launcher也逐字相同，且前者在Q5-01实际通过，仍证明已知外部holder活跃时拒绝、child结束后正常准入。

| 本轮suite | 实际Rust父PID / 子PID | 13项case时间窗（+08:00） | sqlite_close原锁身份 / 立即重获时刻 |
| --- | --- | --- | --- |
| 默认矩阵 | 26299 / 26342 | 11:36:00.117–11:36:01.335 | dev16777229/ino80854567；11:36:00.551 |
| exact并发1 | 27727 / 27728 | 11:37:01.682–11:37:02.401 | dev16777229/ino80856433；11:37:01.940 |
| exact并发2 | 27722 / 27723 | 11:37:01.523–11:37:02.296 | dev16777229/ino80856366；11:37:01.782 |

两份exact的Cargo runner PID为27668/27669；case窗交叠0.614秒。三组均在各自同一子PID中完成13项，逐case现场JSON与套件记录逐值相等；实际lock dev/ino与本轮文件metadata一致，各组13个inode互异。sqlite_close的firstError仍为synthetic_profile_sqlite_close、sentinel=true、productLogs=false，原拒绝义务没有因隔离而减少；3次no-replace仍保留竞争原字节和两个marker。

F-R2-QA2-001据当前精确候选的合法夹具协调与上述有限新证据closed。旧布局失败不被改记pass，旧持锁者及fork原因仍未定位；不把本轮一轮22项和两份exact外推为全部124测试、所有并发调度或现场/跨平台锁保证。生产工厂/ProfileLock无本轮修复变更。

## 27. 新正常恢复账本、P1连续性及边界

Q5-01的新sealed普通hot、已commit及before_native/after_native/after_ro三个二次退出路径均通过真实工厂。独立闭库RO核账只读本轮五份新profile：四份未提交/二次退出严格保持完整旧ACK账，已commit一份严格匹配durable after-commit新账；五份全部SQL表逐行等于各自durable after，integrity=ok、FK无违例、原payload/manifest/context/archive/revision及response原字节SHA相符，RO核账前后DB文件SHA不变。

普通hot代表 `Q5/profile-e34279ac-08de-40d8-9057-efee2f1a054b`，child PID26359，真实COMMIT trace前cacheflush rc0、exit86、raw extended776断言；journal58880B，SHA `048d2634a77c410243f608dfa2c99d14bc7299b15fe635fba92ba97dc1ad009c`。runtime native前SHA `834f95a21dad2d25506b2d9fb4616664f9721d4b217649f6328c5f2e1068c8ac`，native后/RO后同为 `2a2627185233ce3deb981ed203cf2afd24636b61c6d2764f0f227a7128a00c39`，明确发生原生恢复写。before/after完整账JSON SHA分别为 `d4b12106c2de26f2a42c73e1d3b17a5590eba07d61e3b71469439c2036a04276` / `1e4b19698e48b01afd2de21176b460e5ed72e3041bbf12bbfd9b15dc4a0e2e35`；14张原材料/ACK/引用表守恒、0receipt/2pending/1unknown、原冻结body/digest/ID/时间/成员不变，停态。已commit代表profile-c16a5ec0-ba79-4b9d-89c7-478541a02be9为1receipt/2acknowledged/0reference，未用“旧或新任一”掩盖已知checkpoint。

本轮14条正式phase反例均admitted=false；P1独立三最小反例及前轮10份闭库核账在生产SHA相同的条件下继续有效，F-R2-QA1-001保持closed。独立实际DDL长度前缀oracle仍得到config `sha256:64cc8187689bf3e04eb4b914811fe75e77a8d5dd6c0c895cfe12ed4814e1a806`、runtime `sha256:6657f7735d9932d561f0a1bc8ff836bf6190f678c5a6955520a665cab920ad4e`。新cold auxiliary logical1355B、allocated4096B；4096+remaining33550336=33554432，reserved100999496+aux4096=old340296+3×33554432，256KiB子预算仍包含在既有extra32MiB之中。

两条PM原只读解释继续保持：末次目录fsync失败当次拒绝，下次完整可见sealed须重新完整cold核验、不追认前次fsync成功；启动前aux全无且无hot的合法unsealed可保持r1 cold，但本次已见后消失拒绝。没有新poison、补封、永久历史删除识别或认证承诺。macOS进程阶段退出不等于SQLite pager内部掉电；恶意同inode/伪造journal/非合作TOCTOU及Linux/Windows原生保证仍未取得。

## 28. QA3 AC更新与Acceptance Audit

| 项目 | 当前独立状态 / 后续门禁 |
| --- | --- |
| F-R2-QA2-001 | **closed，当前P2精确候选有限验证通过**；旧失败/原因未定全部保留，原锁断言及跨进程用例未削弱 |
| F-R2-QA1-001；r1 F-QA1-001/002/003/004 | 沿用此前限定closed结论；本轮生产SHA相同、相关正常恢复/连续性补证通过，原失败正文保留 |
| AC01/02/17 | A0/A1当前范围通过：批准/角色/保护、54候选/两diff/10pins、文件头/局部索引、记录与交付一致 |
| AC03/09/10/14/22/23/25 | 新sealed正常cold/hot、明确旧/新ACK账、unknown停态、三处二次退出及P1连续性有限通过；真实HTTP及Owner重开仍属B |
| AC04–08/11/13/16 | 未变源码的wire/ACK/调度/unknown/来源/安全有限证据继续复用；provider实际采用、真实HTTP/TLS/证明寿命仍未验证 |
| AC12/26 | 新aux预算/低空间拒绝/普通ACK hot与既有r1 QA2合法8MiB空白资源上限普通rollback证据有效；8MiB空白不称provider普通输出；平台/掉电/防篡改限制保持 |
| AC15 | A0源码/Node/build/locale有效证据按同SHA复用；原生明暗/窄窗和Owner M05未执行 |
| AC21/24 | 当前初始化13故障/no-replace/封存退出、原立即锁释放、exact776正反/外锁及有限默认并发通过；本次P2验证门禁关闭 |
| A0/A1 aggregate | **qa_passed，仅限Owner已批准r2恢复增量及§11.1新合成验证**；没有Human Owner最终接受记录 |
| B、AC18/19 | **blocked / 未批准未执行**；无HTTP/loopback/DS/MySQL/Docker/schema/source采用及Owner原生双方端到端核账 |
| AC20 / 完整阶段C / Human Owner | **未满足 / 未完成 / pending**；A-only QA通过不授完整阶段C接受或后续运行/发布/部署权限 |

## 29. QA3证据、资源与最终串行handoff

| Q5关键证据 | SHA-256 |
| --- | --- |
| factory-default-parallel.log | `e67e925e094186897595d391cd8f63c68442b1888b8a6b69aacbfe51f08d5ae0` |
| fault-overlap-1.log / fault-overlap-2.log | `2506f764e0047a953b931e30433d4c521810060f5fbc69cd1790a7a6f45ea0ec` / `87f7daeb1121416e97a13bd519a02bf74f0886c49f770f7c5cea3c027293e3e5` |
| candidate-audit.json | `e299092e8aead6b47d91b441d496a9bb8507631444ff7394542abf11348fd261` |
| independent-fixture-audit.json | `330ebf131e1624221a655b5bf1a7be49ab1ad19717a3077360e1e93583b4f216` |
| independent-ledger-audit.json | `de8aec69435d6184b1c75431a186ddb6e91b6d00bd893bb6e66bc108d707da84` |
| current-phase-and-budget-audit.json / static-verification.json | `3711d0057b23098cbb4173190834d632a8b3da572602b626bda27a2e046a3154` / `78489da4e2e9f0f4b802650503285ea19188908223696120419e5b299e978f74` |
| known-child-lifecycle.json / resource-inventory.json | `ab56aa20a914598343b6f16112e5e2457b99ec60d55edf835319a25f1f88b225` / `6556502096131012b6179219f744ec514b9c72f34ec2f5e7947217110b9ced33` |

Q5盘点时点744文件、101合成fixture目录、170普通SQLite文件；inventory只对本轮生成物列metadata，不为盘点打开其他SQLite。31份child命令均已wait，含suite子进程exit0及阶段退出86；38个明确owned PID在后续signal0检查时均已无运行实例。无listener、GUI、设备/数据库服务、Docker、分支/worktree或待交接运行连接。本轮未产生dist；共享target/node_modules/正式dist均不归QA删除。

101个本轮fixture有具名证据关联，原journal、五份完整账、三suite/39case及3次no-replace、阶段拒绝及命令/日志/脚本/报告、checklist-before继续保留至Root和Owner解除审阅依赖。Q5/entry-diff-blocks只是可由固定source/diff再生的阅读分段，关键证据持久化后由Root核依赖处理。旧QA1 `/private/tmp/daa-008-r2-a-6pu9uiac/dist` **无本轮QA3依赖**；Root已报告其旧inventory标为reclaimableAfterDependencyReview，Root可在确认无其他依赖后回收，本QA不删除。旧QA/DEV/r1核心witness、原失败/probe/收据继续留至Owner gate；真实配置/历史/原联调profile/.env从不作为回收目标。

项目内唯一写入为本checklist；spec/tasks、54源码、实现/测试/配置/索引不改。关键结论、命令、退出码、原账标量/SHA、历史失败与限制已持久在本文件；最终Q5/qa-final-handoff.json另固定checklist最终SHA、§1–23正文保留、source/spec/tasks未变和只写审计，避免自引用。至此QA3停止写入，经唯一coordinator `/root` 交Human Owner做**已批准A0/A1范围的最终验收**；Root继续独占四索引、notifier和安全资源收尾。完整阶段C仍需具体B批准、实际证据、独立核验及Owner最终决定。

## 30. DQA1：B01文档及r3草案一致性独立核验（2026-11-06）

新的实际fresh-context Verification `/root/daa008_b_docs_verification_1` 对唯一协调方 `/root` 冻结的 **r2 B01文档提案、双语STAGE_C_GUIDE及最小r3 draft引用一致性** 给出 **qa_passed，仅限本次文档核验**。没有新增文档finding；不构成r3实施QA、R3-AC04运行通过、B运行QA或Human Owner最终接受。

本次在Development正式`developer_handoff`并停止三文档写入、PM停止r3草案写入、Root冻结9份公开文档之后开始。上下文未继承Development对话推理；独立消费持久文档/收据、公开源码入口及精确diff。只允许本checklist追加；没有修复或代写PM/Development/索引。当前顶部`Revision: r2 / Status: qa_passed / Handoff`仍是既有A-only QA3身份，不预改成r3实施；旧 **589行、95144字节** 全部逐字保留，进入本次SHA为`1bbbb201c6cdeafc9f917a7c583d5cdbbe8f727ea28e93e73ddb54986f8700be`。最新文档结论以本节至第34节为准，既有QA3/P1/P2关闭及失败史的限定效力不变，旧锁失败原因仍未确定，Owner A0/A1接受仍pending。

Owner本轮原话是“先只改文档，批准后再准备环境和联调”；本核验严格沿此范围。读取实际根AGENTS、根README/PLAN pair、AW及最近DAA README/PLAN/catalog、canonical workflow及实际verification TOML；使用project-governance、desktop-tauri、backend-arch的适用文档规则。完整当前spec/tasks/checklist及批准r2、r1档案作为UTF-8/字节审计输入；人工语义核验聚焦本次新差异和直接支撑入口，未重新审判或执行旧AA/阶段B实现。角色与fresh/串行handoff/diff审计是contract_only控制，不宣称平台ACL、强制路由或已观测运行模型。

### 固定候选与独立收据

正式树仍为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；handoff固定HEAD为`bcafa89fa31bdf62329bced89baebc193323a739`，不据此声称dirtytree等同HEAD。Root/PM/DEV的以下SHA均独立匹配；9文档逐项核准。

| 输入 | SHA-256 / 范围 |
| --- | --- |
| root-document-handoff.json | `5cadb21111e5e80fc227e267e663a032563ef07c213163d3db21e3e8a05427a9`；9公开文档冻结 |
| PM r3 handoff / r2→r3 diff | `220684c692eb6566f2e01310842dbe6f5c85b2865fded678d4e508ea8b986db5` / `5927af552fffbdab178a42bee794e0965c2278e65b8117dd68fe0014204bc019` |
| DEV document handoff / 三文件diff | `14b8486047574fba9d30f95ae6c599216a986eac73b4bc1dbaeb0cffdf4166e4` / `5f5a41f5eebd41303f66c798af05d8c06dc0e6191af41f56d500642efd4b3c00` |
| spec r3 draft | `0a6bbc4d5f0b6868e994b6dee2752d9876edca4577c01f02dc20752bb3352416`；99545字节，未批准 |
| 已批r2 archive / r1 archive | `2d9ffde6e3166216af9c157285e5819b9612db93c13637ee060db78f85ac69de`，86546字节 / `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`，62138字节 |
| tasks / EN guide / ZH guide | `ed3a3172c7d3b180d1f678755cfb5fbf9a16e4aa8d76673a75090d04de9cfb08` / `948f335a9e04cdc136d1a8559c0ffa96b3618bdfd2bd07ffc6b7f1d603c094ac` / `2c3395f25136329cc284c0e1955fda18d8e4bda97b1fd97844d5d5cbc69926ab` |
| 54当前manifest / scope | `b45767071c8f905e524ba784fa73ff8da991ba124203b9e4e10375dd2fcb8fd3` / `7e677674769862d7241148e0f57287f1e81e046eae3a4c32a19a704431fe1330` |
| 52未改非指南scope | `ca942975d851184d20987cee4c2af461eb3a72e231a79ae06553791e106e89f8`；含文档/索引/锁等，非52个纯代码文件；旧54 QA3 scope保持历史`26cebdb087c5aa4be93fd431bec1a54d253e104ca57fd5ee1d0b3a4e9aa57b7c` |
| 32关键pins manifest / scope | `94cfd2c74b2f56308a20a13d5856da464a0dcb9ae5f6104e289066712acc24f1` / `798dcf1bc414ccbf90d90d3ebb4cb8cba980f3dc756f25fa6dc11b29517d1c32` |
| 710公开provider/DS manifest / scope | `e407ec180afdbf2e0389ac6f6e7876d3894d61806e6392a89c798cb23e4ae5ae` / `76baa528e25088771db435cedb96d7e510f40f0e7556f8179665fb549e08a298` |

## 31. DQA1验收检查、源证与结果

| 检查 / 对应要求 | 独立结果及限制 |
| --- | --- |
| DQ01 历史/最小r3；R3-AC01 | **文档通过**。移除入口说明及新增§17/anchor、恢复Revision/Status/Handoff/Acceptance Chain Reference四原行后，完整结果86546字节/SHA与已批r2逐字相等；§1–16、AC02及§14/16两批准收据均在原文内。r1 archive也匹配。tasks前84507字节SHA仍`47b1585d3d2eb7309acafd778ed3c1638ede23a85c3d06776d39a6d066810ff8`。不把原批准扩为r3/B批准。 |
| DQ02 唯一DS读取例外；R3-AC02/05 | **文档通过**。公开DS bootstrap ordinary_profile确实先symlink_metadata/read_to_string自身根.env并parse_profile，再取非空process值；错误先发生，不能声称process阻止读取。profile resolver、Vite envDir=false、Tauri native-s7与文档对应。r3具名唯一例外、双批准、非空合法新process profile、无Agent人工内容读取、坏文件/冲突即停均完整；没有DS_ENV_FILE/新feature/绕读取错误路径。当前只核文本，不核任何真实.env。 |
| DQ03 候选复用；R3-AC03 | **通过**。54中仅两指南改变；52与entry及当前正式文件逐项相等。32/710仅作公开SHA漂移核验，没有审全部业务或C/C++实现。旧QA3不自动覆盖本次两指南；未变AA证据有限复用，未重跑AA/阶段B。 |
| DQ04 B具体字段；r2§11.2/11.3 | **文档通过**。D/S分别为各项目.local/daa-008-r2-b01，O为DAA下daa-008-r2-b01-ops，权限/新空/最终封存不移动、冲突停不换号明确；Vite15191/15194、S7 31281/31282、MySQL13381、API18283、relay18281对应。mysql8.4.6/container/volume/network/alias/schema/三账号及最小权限、0a2c4e6f8b10/71/F7/+08/RR、3自然月/120天/24h与预算、candidate/三机器pins/实例/故障/收尾均有唯一值。没有声称端口可用、目录不存在或资源已建。 |
| DQ05 后端导入隔离/采用 | **文档通过，运行待证**。Settings/FactsSettings均锚定backend/.env，maintenance/main另有显式dotenv_values合并，文档没有误称uv --env-file隔离；未生成runner须在项目导入前同时阻Pydantic与显式dotenv来源、清继承并仅用新私有配置，保留formal service/CLI enable/confirm/approval/target/CAS门禁。公开service对应首次bindingRev0/seqFrom1/oldSeqThrough=None/无expectedAdoptionId，第二PLC须同epoch/首次返回adoptionId及budgets，固定seqThrough9223372036854775806。本次未执行导入/迁移/采用。 |
| DQ06 原串交接/RO observer | **文档通过，运行待证**。公开facts_source_material无context原串/configRevision正文；原context在runtime.configuration_contexts，sample_chunk核原payload/manifest/context SHA。提案未要求Owner复制格式化JSON；observer只限新runtime、停采停传/在途排空/无journal-WAL-SHM、短mode=ro/query_only、固定身份/原UTF8/SHA/不覆盖导出。无immutable/nolock/ATTACH/DML/恢复，不获取/释放/绕ProfileLock或SQLite原生锁，busy/hot/前后漂移即停。未打开任何SQLite。 |
| DQ07 Owner M01–M05与fixture | **文档通过**。公开minimal.db/udt仅结构，三个BOOL/INT/REAL应明确DB21/8B/0.0,2,4，源BEGIN不执行；DS普通“草稿→确认初值/策略→保存版本→停机加载→Start”与公开手册一致。A false/0/12.5、B true/202/25显式填写；真实DS UUID后生成且不当DAA PLC ID。Owner主路径不写JSON/SQL，每段短采后暂停；M04仅一次正常退出、最长180秒case截止、全原串/ID/SHA/冻结request守恒与重开停态后显式续传，未要求重复StageB/AA或无限等待。原生行为尚未执行。 |
| DQ08 有限故障/读写含义 | **文档通过**。unknown/frozen同身份原体优先恢复，3:1仅新freeze机会；GET仅read_result不作ACK；PLC停采停连仍可上传已有积压。一次丢ACK以严格匹配上游已commit为前提，不造ACK、不改变重试body；一次≤2秒新schema busy及一次独立不采用source403，拒绝proof合法写变另列；有限history分页、3自然月/120天算式及cleanup-plan不冒称真实已等待过窗。复杂父链/大回执/本地故障仍按原SHA有限证据复用，缺覆盖如实保留。 |
| DQ09 生命周期/清理 | **文档通过**。未来B批准可条件授权只停登记PID/child及登记ID+label容器，且依赖解除后只移本次container/network/可再生缓存；D/S、MySQL卷、必要O证据/helpers/私有配置及复用卷所需凭据保留，删profile/volume须另点名，QA/验收自身不授删除。没有down -v/prune/旧schema清理；B007/8590/原.env/profile/历史/旧失败受保护。 |
| DQ10 双语/索引/收据 | **通过**。两指南2组实际启动shell除注释外逐字相等，均普通pnpm tauri dev，process DAA_ENV_FILE/DAA_PROFILE_DIR及DS_PROFILE_DIR为精确新值；不运行命令。M01–M05与关键技术值两语齐全。4索引明确r3 draft/B待批及r2 QA3历史，临时r3 spec与r2 tasks/checklist身份差异有具名说明，非机械地冒称同一r3实施bundle。133个本地链接/anchor、表格/空白通过。 |

## 32. DQA1环境、实际命令及退出码

环境为Owner提供的macOS/zsh工作区和正式源码路径；本次只用Agent辅助Python3标准库进行公开文本/JSON/SHA处理，以及Git只读diff与shell语法解析，不安装依赖、不进入项目运行时、不导入项目模块。没有探测本机工具链/端口/监听/进程/目标存在性、真实env/profile或数据库；没有任何产品/build/test/GUI/DS/Docker/HTTP/MySQL/SQLite操作。没有子Agent、额外notifier或外发邮件。

| 实际命令 / 检查 | Exit / 结果 |
| --- | --- |
| `shasum -a 256 /private/tmp/daa-008-r2-b-doc-rd8ex0t7/root-document-handoff.json` | 0；独立匹配Root冻结SHA |
| `python3 -B /private/tmp/daa-008-r2-b-doc-rd8ex0t7/verification-1/audit_documents.py` | **0；38项/0失败**。完整脚本SHA`7995718bb8af7af10518cb76b6d027d8cf3d6ac840214bb7a1b4095e57e904cc`；static-audit.json SHA`8ceda6ad43c710377585e23cc4ba5e94f5b540587b3ce289091bac2c0a63dd86`。九文档/9收据、54/52/32/710、档案/恢复/prefix/589行、UTF8、133links、表格/空白/双语参数/M01–M05均通过 |
| 脚本内两次 `bash --noprofile --norc -n`，stdin分别是EN指南两个bash块（去注释） | 各0；仅解析语法，不执行cd/export/pnpm、不读shell启动文件 |
| 脚本内 `git --no-optional-locks diff --check -- automation-world/data-acquisition-agent/PLAN.md automation-world/data-acquisition-agent/PLAN.zh-CN.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md automation-world/data-acquisition-agent/plans/DAA-008-reliable-facts-upload/evidence/r2-approved-spec.txt automation-world/data-acquisition-agent/plans/DAA-008-reliable-facts-upload/spec.md automation-world/data-acquisition-agent/plans/DAA-008-reliable-facts-upload/tasks.md automation-world/data-acquisition-agent/plans/README.md automation-world/data-acquisition-agent/plans/README.zh-CN.md` | 0；空stdout/stderr，限冻结9路径 |
| `cat`/`sed -n`/`rg -n -C`只读上述公开治理、bundle新范围、两diff/handoff/DEV结果及直接公开入口；stdlib处理JSON/SHA/diff hunk | 均0；部分最初聚合工具输出截断，后续仅补缺失的新范围；不将截断或关键词匹配当产品证明 |

DEV自检37links/32/710与本次独立133links的范围不同（本次另含PM新增§17及四索引）。DEV helper编码/EOF格式/PM并行spec保护断言失败已读且保留；它们只是文档辅助失败，不能改记产品failure或pass。记忆精确DAA-008查找未命中、没有采用历史记忆作当前证据；该rg退出1仅表示无命中。中断发生于已完成的短读取之后，没有遗留测试或产品进程。

## 33. DQA1 Acceptance Audit、blocker及限制

| 表面 | 最新结论 / 下一gate |
| --- | --- |
| 本次B01/双语手册/r3草案文档一致性 | **DQA1 qa_passed**；无文档blocker/finding，可由Root交Owner审阅具体提案 |
| r2 A0/A1 QA3 | 原有限qa_passed、P1/P2关闭与所有历史失败/旧原因未定保持；本次不重跑、不授Owner A0/A1验收 |
| r3范围批准及R3-AC04 | **未批准、运行未核验**；静态R3-AC01/02/03/05部分通过不代表R3-AC04通过。Owner须精确接受DS自身.env有限读取例外，且B-RUN-01获批后才可准备/运行 |
| B-RUN-01/环境准备/三helper | **未批准、未准备、未生成或执行**；本次拟定路径/端口/依赖/镜像/实际UUID/新profile、dotenv guard等未取得运行事实，未来准备失败需真实停止/交接 |
| 实际B/AC18/AC19/原生视觉 | **qa_blocked（未批准未执行）**；解除需上述双批准、实际Development B交接、Owner手动原生及双方有限完整账，再新fresh独立B Verification。文档QA不能替代这些证据 |
| AC20/完整阶段C/Human Owner最终接受 | **未满足/未完成/pending**；文档通过、既有A通过和拟议联合批准均不等于最终接受、生产/现场/SMA/自动启动/发布部署 |

r3唯一新增风险为普通DS可能先将自身.env完整UTF8正文读入进程再用非空process决定profile；本次没有读取其内容或声明没有秘密。坏文件不得移走、改名或绕过求过；若仍需额外env读取或产品改动则返PM范围，不能由本checklist放宽。联合批准语句在spec§17.6及tasks B01-6已具体可审阅；本QA没有替Owner发出该语句，也没有新增重复许可流程。

## 34. DQA1资源、只写审计与串行handoff

本QA只创建`/private/tmp/daa-008-r2-b-doc-rd8ex0t7/verification-1/`内公开静态脚本、结果、589行checklist原件和最终封存收据；仓内只在本checklist末尾追加。没有profile/SQLite/env/服务/容器/分支/worktree或待停运行资源。必要结论、命令、退出码、scope/SHA及边界已持久在本checklist，最终checklist SHA由外部receipt固定，避免自引用。

本次audit脚本只依赖正式公开源码、fixed manifests/原doc/diff/收据，不使用entry/52项非指南公开source副本；**这些52份冗余副本无本次Verification后续独立依赖**。Root仍须核其他使用方引用/归属，保留必要原spec/tasks/checklist/guide、两diff、manifest、失败/检查结果和收据后，才可按已记录文档资源规则回收冗余副本/空目录。QA不执行清理，也不把真实env/profile/任何SQLite或旧运行证据归入可回收项。上述结论不适用于其他历史QA资源。

本次文档Verification停止写入后，经唯一协调方`/root`交Human Owner审阅B01及精确r3/B-RUN-01提案；文档verdict为DQA1 qa_passed，实际B仍qa_blocked/未批未执行。Root可据权威事实机械同步索引；Human Owner保留精确范围批准及最终接受权。没有向Development发出返工finding；若未来B暴露产品问题，须记录新failure并返回实际Development，再以新的fresh Verification核验。

## 35. DAA-008 r4 · M01 启动说明独立核验（2026-11-09，Asia/Shanghai）

**`qa_passed`，仅限本次双语 M01 文档交接，无阻断。** 实际 fresh-context Verification `/root/daa008_r4_m01_guide_qa` 独立消费 [r4 批准记录](spec.md#r4-b01-f7-owner-approval)、[Development 交接](tasks.md#L632)、冻结原文、正式树差异及可用自检。批准 spec SHA-256 为 `bbf5cdb7d472f7439102431300f69736715928acf4c36159d270ab7fd90fda70`，交接 tasks 为 `ae5dc3d4b97a66d67c14011a562ee769eb8f6d3386ddda250fc39bac0c25f026`，HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`。[英文手册](../../STAGE_C_GUIDE.md#m01-launch) SHA-256 为 `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a`，[中文手册](../../STAGE_C_GUIDE.zh-CN.md#m01-launch) 为 `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769`。

| 检查 | 独立结果 |
| --- | --- |
| 启动方式与复用边界 | 两语均区分独立 DAA 日常使用与 M01 的 DS 模拟设备。仅复用同一 B01 隔离 DS 中已就绪且经核对的 C008-A/B，核对两个 S7 端点与 DB21、点位、读写配置。两应用都需启动时可用同一窗口的两个标签页或分屏。 |
| 环境变量与读门禁 | M01 不编辑任一项目根 `.env`。已登记的 `O/config/daa-launch.env` 为 0600，SHA-256 `e29fbdeeb89680b3e839623af076996b2895ea5c8401971f120fa0b3b4c76b35`，内容为唯一一行 `DAA_PROFILE_DIR=<获批 D 的绝对路径>`，与两语示例逐字节相同。两个命令分别给进程传 `DAA_ENV_FILE`、`DAA_PROFILE_DIR` 与 `DS_PROFILE_DIR`。DAA 在该 shell 已设置 `DAA_PLC_READ_ALLOWED` 时提示并跳过启动，空值同样拦截。公开入口支持 DAA 显式选文件、进程 profile 优先，DS 普通 bootstrap 先尝试只读自身根 `.env`，有效进程值决定本轮 profile。读错误停止，沿用 r3 有限例外。 |
| 范围与后续门禁 | 资源表仅 F7 值变为 r4 批准的 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。M01 采集约 5 秒后暂停、上报保持停止、交接来源材料并等待采用收据的正文及 M02–M05 均逐字保留。收尾只移除已无用的 shell export 清理说明。冻结原文及中文校订前副本与交接 SHA 匹配，继续保留在 O。 |

在正式树以 macOS 15.7.7 arm64、zsh 5.9 和 Python 3.9.6 做静态核对。`shasum -a 256`、`stat -f` 和 `git check-ignore` 对所列输入的核对通过。`git diff --no-index` 比较双语校订前后的实际差异均退出 1（存在预期差异）。最终 `/usr/bin/python3 -I -B -` 静态断言退出 0，核对表格、原文、启动路径和 18 个本地链接。首次两次辅助断言分别因 diff 匹配区间和中文收尾标点比较错误而退出 1，校正检查口径后通过。四段命令由 `/bin/zsh -f -n` 仅解析语法，均退出 0。`git --no-optional-locks diff --check` 对双语手册与任务 bundle 退出 0。

本次唯一写面为本清单追加，保留原 664 行、元数据及历史。只读公开源码、登记的启动文件和脱敏文档证据，未读取真实项目根 `.env` 或 profile 内容，未执行启动命令、产品构建或网络、数据库、服务操作。准备状态引用 Development 的记录，运行状态仍为 `needs_owner_m01`。由协调方交 Human Owner 审阅文档并亲自操作 M01。来源采用、R3-AC04、M02–M05、实际 B 独立核验及 Human Owner 最终验收待各自证据。
