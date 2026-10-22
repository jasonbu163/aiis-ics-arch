Task ID: FF-001
Revision: r4
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: same approved r4 rework1 complete for new fresh Verification; QA1 qa_failed history preserved; Rust F001/F002/F003 DEV red-green/formal/isolated checks exit0; Python48 frozen QA1 candidate; no QA2 verdict or Owner acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session

# FF-001 r4 Development

## r4 QA1返工 turn 1（当前）

QA1真实verdict为qa_failed，checklist SHA256=5e0048a80396b3b6a985a8f767782fe0d2e9a228add148f1db4810fa35705f3e；F-001入队前消耗IO预算、F-002实际排队/调用前缺anchored时钟漂移检查、F-003未真实started即置执行计数1。当前重新进入同已批r4 Development，不新Revision或扩scope。下面既有“最终交接”是QA1消费的历史快照，不能抵消本次失败。原tasks全文b750…/QA1全文/关键脚本原输出JSON及原Rust43文件均原字节持久于[evidence/r4-rework-1](evidence/r4-rework-1/preserved-inputs.json)，不覆盖r4-dev或checklist。

新自有根 `/private/tmp/ff-001-r1-r4-rework1-32onn0fh`；仅自建loopback Rust31102/31103/31880、新synthetic库，旧错误confirmed/QA1 target与state保持。先三项真实回归红→最小修复→绿，再同锁fmt/check/build/codec/R14/完整Rust协议/退出，全新父目录只含project的独立复制同建/启动/测试，最后统一candidate/逐AC/资源交接。Python48文件/锁保持原4221…候选，只继承QA1精确证据，不无理由重跑。已重读AGENTS/workflow/README/PLAN、完整批准spec/tasks历史与QA1和相关实现；使用既有aiis/rust-runtime/backend-arch(local state)/plc-point-mapping/i18n-workflow/code-document-indexer/project-governance规则。通知仍由协调器管理。


Human Owner真实批准“批准 FF-001 r4，按方案继续完成 Python 版本，完成后按 STD 进入双版本独立 QA。”；消费owner_approved spec SHA256=e30641845b63f295b408568009c25514f314101d0a2e2b72d331d4255a73045d，已审draft eb3dbc318c89b4772ff9f54f7a1e4ea5ede1520e309f51f310ceb2d5234ebdd1。HEAD仍dbed9107dce5701fa138a66b3c13aba637a27b86，正式交付当前仓库，无commit/push/refs。

1. 读取当前规则/完整合同与历史；Python自身独立INT codec单元向量，再复用正式driver/state/execution做120秒真实R15 gate。
2. gate后完成Python CLI/config/异步flow/FIFO owner/进程预算/状态审计/退出，完整AC01–15及单目录复制/build/start/tests。
3. 核对保留Rust43文件hash/既有全套与补测证据，不无理由重写/重复全测；统一精确candidate、逐AC证据、资源与developer_handoff，QA由协调器另启fresh角色。

使用aiis/project-governance/backend-arch（仅本地state）/plc-point-mapping/i18n-workflow/code-document-indexer，Rust仅保留既有rust-runtime规则。YAML为typed配置、JSON为locale/报告、SQLite为本实例执行事实、JSONL为审计。通知由协调器管理。Python锁/3.11.12/公开connect与iso_exchange_buffer保持；每job一次raw，无私有transport/monkeypatch/vendor/换库。Python写入仅自身工程/tasks/新增真实evidence，保留所有他人dirty；spec/checklist/根与FF导航由各owner控制。

新私有根：/private/tmp/ff-001-r1-r4dev-pc36ki7o；新schema仅此根下显式synthetic init，不触碰旧错误confirmed库。原r3任务全文原字节副本[r3-tasks-original.txt](evidence/r4-dev/r3-tasks-original.txt)，SHA48a52ef056ccced510bc4c24c685b4ef7d03fd03868487dff1616a1ba829dd76；以下前缀归档可同样还原，r2/r1嵌套完整。原112证据/43Rust候选/4长期文档由协调器baseline保护，不覆盖。

当前r4初始检查点codec/gate/Python完整矩阵not_run；之后按实际批次更新。

## QA1返工批次1：先红后绿与正式全矩阵

新tests/runtime_regressions.rs复用正式State/Runtime/Execution/Driver/native Fixture。只增加test-fixture时钟偏移文件/可释放child调用前屏障，以及自有proxy每响应600ms延迟；宿主时钟未改。red-1辅助脚本错cwd使新target缺失exit101、red-2 sandbox fixture_port_conflict未协议exit101，均保留；合法escalation后的red-3 exit101是真实3项红：FIFO第二read和queued write canceled；5000ms年龄命令queued/precall受控-2000ms仍错误confirmed/WriteVar1；屏障前health1而started0/WriteVar0、ACK等待期started日志仍0。四份实际完整报告在新增evidence，旧source43文件/QA1保持。

最小修复分离ready/queue/source deadline，owner实际dispatch才建立IO总期限；等待端以原子phase判断queue超时能否取消，已dispatch继续等待本次有界IO/真实回收，不能被旧queue截止误截。source monotonic同时取原expires和issued+max_age较小值。400ms只在父整体预算内部预留一次，child接收剩余工作期不再重复扣400ms，原合法IO500ms真实read/write通过。

同一任务ClockAnchor保存wall与OS CLOCK_MONOTONIC起点，原锚点随有限IPC到child而不在排队后重建；owner出队及child实际开始闸门前再核查。检测clock_invalid证明未开始时保守canceled/不重置dispatch，任务clock及owner写闸门稳定锁定；恢复测试偏移后新ID仍拒绝，独立read继续。匹配generation/request_id的child started事件立即更新执行计数和必要日志，回调仍在原work截止内；T2与IPC未开始统计0，真实ACK等待期1，结束及forced实际reap后0。

green-1/2/3三组均exit0，原queue2000先红后绿；随后queue1000/IO1200/每响应600ms回归exit0，排队约600ms+自身IO600ms总大于queue_wait仍成功且单PID/session。正式同锁fmt/check/build/codec3/R14 gate/全部原15+新增3integration与无参启动逐命令exit0。新独立父目录仅project的Rust副本完整同验正在执行。Python48文件与原候选锁不变。完整原样输出/三报文/状态和回收见[evidence/r4-rework-1/report-map.json](evidence/r4-rework-1/report-map.json)；辅助/真实失败分类见[interim-command-facts](evidence/r4-rework-1/interim-command-facts.json)。不构成QA verdict。

## r4返工1 最终统一 developer_handoff（最新有效交接）

本次同一Human Owner已批r4，spec SHA256仍`e30641845b63f295b408568009c25514f314101d0a2e2b72d331d4255a73045d`。正式工作树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD仍`dbed9107dce5701fa138a66b3c13aba637a27b86`，无commit/push/refs。QA1真实qa_failed不被改写：checklist与其持久原副本保持`5e0048a80396b3b6a985a8f767782fe0d2e9a228add148f1db4810fa35705f3e`，原tasks全文b750…和原candidate4221…/全部239既有evidence不覆盖。旧交接中“尚无checklist/QA”只属于QA1前历史；本节优先，当前须协调器实际另启新的fresh-context Verification。Development不写QA2、checklist或Owner验收。

### 精确候选、文件与边界

[返工后双版本candidate](evidence/r4-rework-1/candidate-manifest-final.json) SHA256=`701272f1ea19c4759d604810c1aaac4cdce3e4ee5930aaba62c147f4dd52c15b`。Rust44文件与本次隔离副本逐字节相等；Python48文件与QA1精确正式/隔离候选逐字节保持。Rust Cargo.toml/Cargo.lock、SQLite schema和INT adapter不变，无新依赖/库替换/私有transport/第三方patch。Python源码、说明、锁和环境入口本轮零写入，没有无理由重跑Python DEV全套；QA1 Python完整正式/隔离AC01–15通过是QA1事实，新的统一QA仍由新角色决定。

相对QA1 Rust43输入共12份新增/变更：`src/runtime.rs`、`src/domain.rs`、`src/driver_process.rs`、`src/services/execution.rs`为三个缺陷最少接线；`src/fixture.rs`仅自身600ms响应故障；`tests/local_protocol.rs`仅传入原任务Clock；新`tests/runtime_regressions.rs`三项真实回归；README/PLAN双语和CODE_INDEX共5文档同步，最新QA状态指向唯一bundle。无任务外重构。完整逐文件hash/变更集合见candidate。

F-001修复：ready/queue各自受配置与原source deadline约束，队列原子phase标记已dispatch后不再由旧queue期限取消；实际dispatch新建IO总deadline，取原命令monotonic有效期较小值，原source UTC/issued/max_age/expiry不刷新。400ms仍在本次IO预算内，child只收到工作期，不第二次再扣400ms；合法IO500ms的真实read/write均成功。没有增加timeout或清理宽限。

F-002修复：同一任务wall/CLOCK_MONOTONIC锚点从Execution进入owner队列、再随有限私有IPC到child；排队后和实际开始闸门内重查，不能重建锚点逃逸。超过1000ms漂移明确clock_invalid，证明未开始的原T2记canceled（dispatch仍1），原Clock与owner写闸门稳定暂停新写、独立read继续；可能已开始的错误仍unknown，confirmed不倒退。ClockAnchor不进入SQLite/配置摘要，不改schema/身份。时钟偏移文件与可释放precall屏障仅test-fixture，未改宿主系统时间。

F-003修复：Driver接收并校验request_id/generation的实际started事件后，原work期限内立即回调更新watch执行数和必要driver_call_started审计；T2/IPC未开始数0，真实已开始数1，完成或实际故障reap后0。副作用后审计失败仍保守unknown/暂停，不用计数替代T2或ACK。普通读不逐tick日志。

### 实际先红后绿与命令

红：red-3真实命令`CARGO_TARGET_DIR=/private/tmp/ff-001-r1-r4-rework1-32onn0fh/target cargo test --locked --offline --features test-fixture --test runtime_regressions -- --test-threads=1 --nocapture` exit101，3 failed/4.86秒，所有case在最终断言前实际close/join/reap/rebind。FIFO第二read与queued write canceled约593/602ms；queued/precall受控-2000ms两例实际WriteVar1/confirmed1，Clock未锁定；precall health1但started0/write0，ACK等待时started日志仍0。各红报告原字节保存，不能由后续通过掩去。red-1错cwd/无target、red-2 sandbox fixture_port_conflict未协议、临时Python辅助解析UTF-8问题均在[实际辅助/测试事实](evidence/r4-rework-1/interim-command-facts.json)，不当成三项真实缺陷的协议证据。

绿：green-1/2/3相同三目标均exit0；原queue2000先红后绿保留。最终正式`dispatch-outlives-queue.txt`同target exit0：queue1000/IO1200/每响应600ms，第二读1211ms、queued write1207ms（两段之和超过queue1000但各段合法），同PID/generation/session；500ms最小IO也成功。queued/precall两例均clock_invalid/canceled/WriteVar0，偏移恢复后新ID仍拒绝且read good；started前0/事件0/写0，ACK等待1/事件1，正常结束0，另真实hold ACK超时强制reap后0，运行fault_cleanup/unknown不冒充正常退出。

正式与隔离副本均从自身工程cwd依序执行，全部exit0；完整argv/cwd/target/timeout/用时见[正式ledger](evidence/r4-rework-1/formal-commands.json)、[副本ledger](evidence/r4-rework-1/copy-commands.json)，stdout原样.txt持久。

```bash
cargo fmt --check
cargo check --locked --offline --all-targets --features test-fixture
cargo build --locked --offline --bins --features test-fixture
cargo test --locked --offline --test s7_int_pdu -- --test-threads=1 --nocapture
cargo test --locked --offline --features test-fixture --test local_protocol matched_ack_preflight -- --test-threads=1 --nocapture
cargo test --locked --offline --features test-fixture -- --test-threads=1 --nocapture
cargo run --locked --offline --bin field-flow --
```

正式全套18个integration tests（原15+新增3）exit0/68.75秒；lib/bins/doc自身0-case不当功能证据。正式全套时新FIFO仍queue2000，之后只把本回归参数改1000并完整重跑对应3目标exit0；运行实现未再改变。最终隔离副本全套用当前queue1000版本，18个tests exit0/68.72秒，FIFO第二读1204ms/write1205ms，同一PID。R14两边gate外层仍120秒，实际2.99/3.05秒；full harness180秒，400ms内部reap预留与原3000/5000+500上界不变。原五INT、29 ACK矩阵、历史ref/另一操作ref、unknown/审计/队列stop/父子死亡/正常和fault退出都随核心修改重新通过。

新的Rust隔离工程`/private/tmp/ff-001-r1-r4-rework1-32onn0fh/isolated-rust/project`，直接父目录仅project，没有父运行清单/兄弟项目；新独立`copy-target`，没有修改QA1原target/失败副本。自身cargo metadata exit0确认workspace_root/manifest/targets均来自该复制品，见[实际来源](evidence/r4-rework-1/copy-provenance.json)。构建/启动/driver/fixture均由复制工程自身编译；正常公共Cargo缓存可用。最后仅阶段文档同步并重新hash，非源码或锁变化，不重复无关协议测试。

### 逐AC本轮交接映射

本表是DEV self-check；Python列均指**QA1正式和父/兄弟缺席副本相同48文件的精确证据**，不是本轮重新执行或QA2 verdict。其完整QA1原checklist、全部command ledgers/原样输出/报文索引及引用JSON在[原样QA1保留映射](evidence/r4-rework-1/preserved-inputs.json)及qa1子目录。Rust所有行引用上述新正式/隔离全套exit0，目标补充另见report-map和原stdout。

| AC | Rust本轮实际DEV | Python冻结输入与交接边界 |
| --- | --- | --- |
| AC01 | 正式/隔离各自fmt/locked check/build/codec/R14/full/bare，44文件一致、私有child自身入口，独立target与无父兄弟依赖。 | 原48文件一致；继承QA1两边lock/sync/build/compile/unit/gate/local/CLI/provenance全exit0。 |
| AC02 | cli_contract 3tests、typed无参/中英help/配置/显式schema/模式反例重跑通过。 | 同QA1精确源码、说明和锁，无新变更。 |
| AC03 | remaining/local真实五INT GET→写→各次停止后独立匹配读回及A5，非法类型/声明/实际范围拒绝。 | QA1五INT与自身IntMemory有限边界通过；第三方Server原partial-write失败及限制保持。 |
| AC04 | 原输入/TTL/queued-expiry重跑；新增queued/precall真实anchor偏移两case零写、canceled/clock_invalid、稳定拒新ID/read继续，修复F-002。 | QA1已通过queued clock用例；本轮hash不变。 |
| AC05 | 原十轮/原库重启/身份冲突/代次不重建通过；clock取消仍保dispatch和身份。 | 原QA1十轮/重启/冲突证据继承，无重发新逻辑。 |
| AC06 | 三独立读流各20样本/request、单PID/session/串行；新增合法FIFO两read和queued write复用同PID。 | QA1三流独立60 request/1session证据继承。 |
| AC07 | 1200ms GET与100ms读8秒并发、>=20/maxgap<=500ms、同flow不重叠重新通过。 | 原QA1正式/隔离窗口通过，源码无变更。 |
| AC08 | 原静默COTP/initial absence/disconnect/split/slow/stale总预算+实际reap；F-001两个queue参数先红后绿，实际dispatch IO独立起算且不被旧queue截止截断。 | 原QA1整体deadline/真实回收通过，未新增DEV执行。 |
| AC09 | T1/T2恢复/已应用丢ACK/10轮+原库重启/物理别名overlap阻断/read继续重跑通过。 | QA1对应unknown/物理范围通过；旧库与错误confirmed证据不触碰。 |
| AC10 | 子/父真实死亡、<=500ms/继承锁/原库unknown不重发、T3失败/confirmed-sink通过。新增hold ACK实际forced故障统计归0。 | QA1实际父/子死亡、锁与state组合通过，保留原报告。 |
| AC11 | dry真实GET/read、zero write/simulated及模式隔离重跑通过。 | QA1真实两模式CLI/协议通过，候选冻结。 |
| AC12 | 容量/轮转/审计前后故障/queued闭闸/read继续重跑；F-003未开始0、started1、结束/fault0且事件时点正确。 | QA1日志/容量/审计及实际统计通过，未改生产adapter。 |
| AC13 | 原child屏障+父队列stop零写/全join、正常exit0与forced非零/回收/单global end重跑；F-003区分T2与执行状态。 | QA1正常/forced/端口冲突与全局退出通过，新QA仍独立决定双版。 |
| AC14 | 本工程README/PLAN双语/索引少量同步；99工程链接/locale对称/空白/范围检查通过，逐AC/命令/资源完整。 | Python文档48内保持；最新QA结果以唯一bundle为准，DEV不代签。 |
| AC15 | 原R14/codec、29真实ACK及实际历史旧ref/另一操作ref、短长/迟到/近ref上界/unknown不重发完整重跑。 | QA1 R15/30真实ACK/4096/4097/65528及最大声明短body等通过，原48输入保持。 |

### 证据、资源与限制

[完整报文与状态报告映射](evidence/r4-rework-1/report-map.json)保留28份红/绿协议报告；[只读三表](evidence/r4-rework-1/selected-stores.json)从44个本轮明确记录的新合成库导出store_meta/commands/command_events，红的错误confirmed也原样保留，只读复核、不修旧库。普通native/protocol日志完整输出持久；hold_ack分支的trace预先记录native原ACK，实际未转发由该故障路径/强制结果证明，不能将预记录的ACK字段当“客户端已收到”。正常、corrupt及短包例保存实发三帧，原始输出不修饰。证据清单以本目录evidence-manifest.txt固定，不依赖被忽略的.log/.sha256。

[保护/范围](evidence/r4-rework-1/integrity-final.json)：239既有evidence、4长期保护文档、原tasks原字节/QA1全文/spec以及Python48均保持；Rust自身manifest/锁不变。原QA1根和target/失败副本未写入。root/FF13导航只由Main维护，本Development未写spec/checklist/Backend/AW/CA/tools/真实配置或Git refs。本轮Main机械索引后实际checkerexit1/322行（318原任务外多重集一致+4合法../plans识别限制），原332快照的8+2暂时导航诊断已消除；[准确原输出/分类](evidence/r4-rework-1/coordinator-governance-qa1-indexed.json)持久，未借机改checker/造子任务，不称QA。

[实际资源](evidence/r4-rework-1/resources-final.json)：本轮输出/报告明确记录230 PID全部不存在，六固定端口逐个lsof exit1/空，并实际bind127.0.0.1后立即close。所有harness命令已结束；协议内native自然exit0/真join/rebind与driver正常wait或forced/parent_lost分开，不把停止等待当结束。79个从本轮输出识别的自有根（沿用support helper的r3名称前缀但ID/时间属于本轮）及主根/target/copy/合成库/日志暂留供QA2/Owner复现；未导出路径的unit临时目录不冒称完整枚举。关键证据已持久，后续无验证/证据依赖时由协调器按归属安全回收，不删除历史或归属不明资源。

Main自有`/private/tmp/ff-001-r4-coordinator-1y0z0h4z`仅批准/归档/allowlist/导航基线及小报告、无运行服务，供QA2/Owner复核暂留，验收后无证据依赖再由Main清理；qa1-rework-baseline已原样持久。旧r1/r2/r3协调器根、QA1根/失败副本和原错误confirmed库沿历史保留，本Development不代删。

未验/外部gate不变：限macOS本机合成、固定INT形状和有界窗口；无真实endpoint、长期浸泡/生产容量、全OS/PLC型号、第三方完整内存安全、部署/发布。原source时效/unknown/confirmed、400ms内部回收、全局shutdown预算不变。Python4096后验cap/65528接收边界和Rust4096FFI限制仍按批准合同。**当前交接只将三项DEV修复和统一精确候选交Main实际启动新的fresh Verification；QA1失败历史仍在，QA2与Human Owner最终验收均未授予。**

## R15 gate 批次1

`uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit/test_s7_int_pdu.py -s` exit0，固定请求/INT/边界、逐长度截断与逐字段拒绝2 tests；同环境`pytest -q tests/test_matched_ack_gate.py -s`真实gate exit0，总harness120秒（含进程/线程/端口回收），实际时间见[逐命令](evidence/r4-dev/gate-commands.json)。正式共用State/Owner/Driver/Execution，不是probe-only状态机。正常真实Read/Write/T3 confirmed；badref Read无good，已应用Write错function/badref/短ACK均unknown1/confirmed0/actualWriteVar1，同身份10轮/原库重启10轮不重发，停止后独立raw匹配读回42；完整三hex/三表/计数/自然退出与端口rebind见[gate-1.json](evidence/r4-dev/gate-1.json)，[原样输出](evidence/r4-dev/gate-1.txt)。codec/driver未修改第三方或回落高层DB API。gate通过后继续完整Python CLI/runtime与AC矩阵；不是完整handoff/QA。

## 完整Python矩阵批次2（仍在完成剩余组合）

正式CLI/独立flow/复用HTTP/健康/global shutdown已实现。首轮matrix-1实际exit1，pytest收集失败：tests/unit缺package标记导致找不到自身tests，尚未协议执行；补本工程`tests/unit/__init__.py`后matrix-2实际exit0，16 tests/28.25秒，覆盖五值真实GET/写/各次停止后独立raw读回/A5、十轮与原库重启、60独立读sample/request/单PID/session、8秒慢GET并发、30行真实ACK拒绝/65528返回、split/slow/stale/最大声明短body总预算与实际reap、T1/T2/unknown/TTL、dry、容量轮转、确认失败和stop双屏障。命令/原样结果与协议报告在本r4-dev目录，不能用这批16个目标代替尚未完成的父子死亡/近ref上界等后续组合。

新增targets-1实际exit1：queued审计故障用例观察到两个请求expired而不是预期canceled。实际缺陷是IO期限错误地从入队时开始消耗；已把独立queue deadline与实际IPC dispatch开始的IO总deadline分开，源命令monotonic期限仍取min，排队未开始明确取消/过期。修正后重跑目标和后续整套；原失败与三表报告保留，不改成通过。另收敛T2/IPC同request_id及child started后的真实in_flight统计，读sample带独立request/flow/generation/质量/时间；这些接线改变纳入最终受影响回归。

工具/环境实际失败另见[implementation-first-errors.json](evidence/r4-dev/implementation-first-errors.json)：一次uv sync错cwd exit2；一次沙箱DNS访问mirror失败exit1，合法escalation后自身editable build/sync成功。不是S7版本不兼容。原构建backend family内实际解析hatchling1.32.4，已精确pin于build-system；无新增运行依赖/全局工具安装或解释器下载。生产S7仍原3.0.0/公开connect与单次iso_exchange_buffer。

## 剩余真实组合批次3

`targets-2`实际exit1：queued审计组合已通过；近ref65534/65535→正常关闭旧Client→新Client raw2也已通过，但新增实际块边界负向测试揭示原python-snap7 Server在16byte DB offset15/count2先写1byte、随后才返回错误，父正确unknown/confirmed0/dispatch1，末字节A5变00。此失败和原包源码hash/位置/原始三报文/内存保留于[server-memory-boundary-review.json](evidence/r4-dev/server-memory-boundary-review.json)及targets-2原输出/报告，不称原库有原子拒绝。

协调器明确这是已批R07/R13自有fixture接线：仅在tests/fixtures/runtime.py自有IntMemory bytearray的slice赋值检查完整2bytes，通过公开register_area传参；不碰Server私有属性/方法、不monkeypatch或加运行代理，原r3高层API失败preflight源码/证据完整保留。生产adapter不靠该边界证明真实PLC块大小，也未因此变更；配置声明范围检查与合成注册内存范围检查分开记录。后续正式全套验证五INT正常写、越界整块保持和unknown十轮/重启不重发。

`targets-3`实际exit0，5 tests/3.74秒：审计queued/prepermit/ACK提交后sink失败保持confirmed、ref近上界与合成内存越界拒绝、真实父/子死亡锁、初始Server缺席/重连恢复与3端口冲突。父SIGKILL后child实测64.11ms结束，旧child还活着的窗口实例锁仍阻止第二writer，之后独立锁取得；child单独SIGKILL使原运行exit1/fault_cleanup，正常CLI SIGTERM另例exit0/child已reap后才shutdown_complete。原输出、每例三表/完整报文、产品父stdout/进程命令均在本r4-dev目录。最终全套与独立copy仍继续，非QA。

## r4 QA1输入的原最终双版本 developer_handoff（历史）

本节为Development self-check及串行交接，精确批准对象仍为r4 spec `e30641845b63f295b408568009c25514f314101d0a2e2b72d331d4255a73045d`。正式交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `dbed9107dce5701fa138a66b3c13aba637a27b86`，本轮未commit/push/refs。两版正式源码均在field-flow自身工程；复制结果不替代正式树交付。当前由协调器另行实际启动fresh-context Verification，未创建checklist、未给QA verdict或Human Owner验收。

### 候选、实现与独立性

[固定candidate manifest](evidence/r4-dev/candidate-manifest-final.json) SHA256=`4221b6ded6ea871bb01cf7ac12059e0794d83550ea9d8fe755979a702ab5067f`，逐文件列Python48份、Rust43份及各自独立副本，全部相同。Python实现分domain/config、单轮app/demo01、execution服务、异步runtime/每PLC FIFO owner、专属常驻driver/匿名有界IPC、HTTP、唯一SQLite/audit线程、双语CLI和自身fixture/test；无兄弟环境、服务或可写状态依赖。无新运行依赖、原uv.lock和.python-version、r3 public_api/preflight源hash均保持；构建backend精确hatchling1.32.4，原失败已记录。

Rust相对r4 baseline只最小同步README/PLAN/catalog六份阶段文档；其余37份（含所有运行源码、测试、Cargo清单/锁及codec）逐字节保持已验证r3候选。原r3正式/独立复制整套及实际历史ref/confirmed-sink补测保留，不因仅文档更新无理由重复协议执行。r4新Rust说明副本 `/private/tmp/ff-001-r1-r4dev-pc36ki7o/rust-retained-copy` 与正式43份相同；原已实际构建/启动/全测副本 `/private/tmp/ff-001-r1-r3dev-k989azay/rust-copy` 保留，运行源码/锁相同。

Python新副本 `/private/tmp/ff-001-r1-r4dev-pc36ki7o/python-copy` 自身新.venv，CPython3.11.12/macOS15.7.7 arm64、uv0.7.8、python-snap7=3.0.0/httpx0.28.1/PyYAML6.0.3/pytest8.4.2、SQLite模块3.47.1。正常公共package缓存可复用；[正式来源](evidence/r4-dev/formal-provenance.json)/[复制来源](evidence/r4-dev/copy-provenance.json)实际断言sys.executable分别来自自身.venv，field_flow.__file__来自各自src，fixture.__file__来自各自tests。首次辅助诊断以仓外脚本路径启动导致tests不在sys.path，exit1；改成cwd内python -c执行后两边exit0，见[准确辅助错误](evidence/r4-dev/provenance-first-error.json)，不属于产品测试失败。

### 实际命令与退出码

Python从各自工程cwd执行以下完整顺序；环境仅显式UV_CACHE_DIR指向本任务缓存，没有PYTHONPATH借源。逐条完整argv/cwd/timeout/用时/输出在[正式逐命令](evidence/r4-dev/formal-1-commands.json)和[独立复制逐命令](evidence/r4-dev/copy-1-commands.json)，每条均exit0。

```bash
uv lock --check --python 3.11 --no-python-downloads
uv sync --locked --python 3.11 --no-python-downloads
uv build --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit -s
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_matched_ack_gate.py -s
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py -s
uv run --locked --python 3.11 --no-python-downloads field-flow
uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures.cli_smoke
```

正式unit6、gate1、local15通过（local测试本体32.83秒）；复制同数量通过（local命令33.17秒）。R15每次有外层120秒harness、内部110秒且含实际回收，正式gate命令1.16秒/复制0.94秒。local矩阵harness180秒，实际约33秒。CLI smoke用正式产品state init/fixture/run/inspect命令分别完成dry_run/execute，正常SIGTERM实际wait exit0；每条产品argv、父/driver/fixture PID、三表、native自然退出/线程join/端口rebind在[正式CLI证据](evidence/r4-dev/formal-1-cli-smoke-0_47ma_r.json)和copy对应报告。README给出可直接复现的显式分终端命令与fixture关闭方式。源文档状态同步后两份工程再次uv build均exit0，[最终构建](evidence/r4-dev/final-build-commands.json)；[artifact检查](evidence/r4-dev/build-artifacts.json)显示两边wheel和sdist分别hash相同、locale已打包、无venv/dist/state混入。产物留本机、不发布。

Rust继承的真实命令：正式 `cargo fmt --check`、`cargo check --locked --offline --all-targets --features test-fixture`、`cargo build --locked --offline --bins --features test-fixture`、`cargo test --locked --offline --lib`、`cargo test --locked --offline --features test-fixture -- --test-threads=1 --nocapture`均exit0；[正式命令](evidence/r3-dev/rust-delivery-commands.json)完整14integration/62.16秒，lib本身0-case，不能冒充功能证据。[独立复制](evidence/r3-dev/rust-copy-commands.json)locked build/无参启动/同一全套全部exit0（57.52秒）。新增confirmed后sink失败为第15个integration，实际旧ref/另一操作历史ref补测及受影响local_protocol回归共6项exit0；[补测与正式入口恢复](evidence/r3-dev/rust-gap-final-commands.json)、[正式目标原输出](evidence/r3-dev/rust-gap-closure-1.txt)、[补测摘要](evidence/r3-dev/rust-gap-summary.json)保留。CARGO_TARGET_DIR复用本任务r2缓存，不借兄弟工程。

### 逐AC Development self-check

下表仅表示已执行的DEV范围。Rust依据上述r3正式/复制/补测命令均exit0；Python依据上述formal-1与copy-1完整命令均exit0，每一测试报告由[正式报告来源/hash映射](evidence/r4-dev/formal-1-report-map.json)/[复制映射](evidence/r4-dev/copy-1-report-map.json)给出。原样stdout均.txt，完整三份S7 hex/ref/function、实际计数/内存、三表只读导出、真实回收保存在对应JSON，原log/旧失败未覆盖。

| AC | Rust已执行DEV | Python正式树与独立复制已执行DEV |
| --- | --- | --- |
| AC01 | 43文件；r3正式+独立复制locked build/start/full，补测后入口恢复；r4仅六文档同步/hash。 | 48文件新venv，锁检查/安装/build/compile/无参/help/init/run/inspect/完整测试，各自产生driver；来源三路径断言及copy一致。 |
| AC02 | cli_contract/typed配置/状态版本/无参零IO/模式拒绝通过。 | unit6覆盖无参/中英help空目录零IO、20组typed配置反例/init不覆盖/metadata版本只读拒绝；app仅单轮，状态编排归服务。 |
| AC03 | 五INT逐值真实GET/写/停止后独立raw读回及A5、类型/声明和注册范围拒绝。 | values报告五INT逐值完整链/各次停止后独立raw读回/A5，非法值/范围拒绝；ref-maintenance整块A5保持。原Server partial-write真实失败另保留，guard边界见下。 |
| AC04 | 输入/时效/clock/queued TTL零写原矩阵通过。 | values/clock-conflict/connect-queue：idle/status/body/JSON/source/schema/time/TTL拒绝；排队原时间到期零写；时钟变动后调用前取消，identity冲突永久blocked、不刷新来源。 |
| AC05 | 十轮/原库重启/driver generation与冲突保留原身份。 | values/recovery/ack矩阵：重复十轮/原库重启原身份actualwrite1；同ID payload/time/target冲突保原记录，新generation不重建身份。 |
| AC06 | 三读流各20独立sample/request，单PID/session/串行回传。 | concurrency三个流各20个独立sample/request，正常1PID/generation/1session、最大在途1且flow对应正确。 |
| AC07 | 慢GET1200ms/读100ms/8秒、>=20/maxgap<=500ms。 | 同一concurrency慢GET1200ms/读100ms/8秒，正式maxgap105.64ms；慢流maxinflight1、无tick积压。 |
| AC08 | 静默COTP/split/slow/stale/断连/初始缺席，整体预算含实际reap；强制路径与正常分开。 | connect-queue/四类deadline/absence：静默COTP实际父超时回收；split/slow/max声明短body走整体监督、stale拒绝；旧PID实际结束后恢复，不把库先报错当总预算证据。 |
| AC09 | T1/T2/丢ACK/物理别名与overlap unknown阻断，不相关读继续。 | recovery/absence-alias/ack矩阵：T1沿原库处理，T2恢复unknown；已应用扣ACK unknown、10轮及重启零重发，改ID/source/flow/PLC别名/重叠范围均blocked，读继续。 |
| AC10 | 真实父/子死亡、继承锁、T3失败/confirmed后sink组合补测通过。 | process-death/audit-stop/audit-order：已应用写分别杀自有driver/父，恢复unknown且不重发；父死亡child正式58.39ms/复制58.34ms实际结束，旧child存活时锁仍阻止writer；T3失败unknown，confirmed后sink故障不倒退/不重发。 |
| AC11 | dry真实GET/read、write0/simulated，交叉库拒绝。 | values和实际CLI smoke两模式独立库，dry实际GET/read且write0/confirmed0，仅simulated；dry/execute metadata互开失败。 |
| AC12 | 容量降低/真实轮转/审计queued闸门/read继续与confirmed保留。 | audit-stop/audit-order：10/100及2048byte测试阈值、实际轮转/JSON解析；T1/T2/ACK提交前后sink故障、排队两写零下发/read继续，confirmed10保留，健康recovering/blocked/running可区分。 |
| AC13 | 父队列/child调用前屏障stop零写、真实全join、单global end、fault_cleanup和占用者保留。 | audit-stop/process-death/CLI smoke/absence：stop先全闭闸，父队列及child屏障两个请求canceled/零写；flow/owner/HTTP/SQLite/audit共用一个monotonic截止，退出真实wait/join；forced exit1无shutdown_complete，正常exit0资源先释放，三端口冲突不杀占用者/不换端口。 |
| AC14 | 双语说明/PLAN/catalog/locale/index阶段相符；实际证据/历史仍在。 | README/PLAN/catalog/locale/index与48文件候选对应；98本地链接/locale parity/空白检查exit0；本表及命令/资源完成。fresh QA checklist及Owner验收为后续角色gate，DEV不代签。 |
| AC15 | R14 gate先过；29行真实ACK/边界矩阵，补实际历史旧ref/另一操作已有ref（非+1标签）、confirmed-sink。 | R15 gate先过；30行ACK真实向量/各字段/negative/短header+短data/附加/4096/4097/65528/transport/bitlength、实际历史read2→read3坏2和read2→write3坏2、坏后迟到正确ACK；首坏立即退役旧进程/会话，无good/confirmed，已发写unknown/dispatch1，十轮及原库重启不重发；65534/65535后新Client raw2，三份帧保留。 |

### 真实失败、边界及未验gate

r4失败历史完整保留：matrix-1收集失败→加本包marker；targets-1错误把IO deadline从enqueue计时→分离queue/实际dispatch总预算；targets-2原python-snap7 Server先截断写一byte后报错→仅自身IntMemory注册内存边界接线；错cwd uv sync/DNS和辅助provenance的失败均如实保留。后续正式和复制同矩阵全部exit0没有抹去旧失败。

[原Server边界源码/hash及失败](evidence/r4-dev/server-memory-boundary-review.json)证明plain bytearray在offset15/count2已发生partial write。仅自身tests/fixtures/runtime.py的IntMemory检查完整2byte slice，仍经公开Server.register_area，未覆盖Server私有方法/属性、monkeypatch第三方、改生产adapter或建立运行代理。正式与复制新完整报告记录整16byte A5不变、父unknown/confirmed0/dispatch1、十轮+原库重启无重发；这只证明本任务合成INT内存边界。运行配置声明范围检查是独立的调用前检查，不能由guard推导真实PLC块大小或写保护。原高层API错误function接受的r3 preflight原源/证据保持，并非产品raw路径。

两版都仅有限单item DB INT及本机合成，未验证真实设备/第三方endpoint、长期浸泡、生产容量、全型号、全平台或第三方完整内存安全；未部署/托管/发布。Python4096是库返回后cap，真实单帧接收payload上界65528且有临时拷贝；Rust4096缓冲依据冻结native，不声称修复native。unknown不是物理失败证明，不允许自动回读升级/重发。fresh-context QA和Human Owner最终验收均尚未完成。

### 文档、保护审计及资源

[完整保护检查](evidence/r4-dev/integrity-final.json)：4长期文档、112旧evidence、r3 tasks原字节hash不变；spec保持e306…；Rust仅六说明文档变动；两个工程98本地链接/locale键对称/源码与文档空白/git diff --check均exit0。根/FF导航由协调器维护，本Development未写spec/checklist/根导航。

协调器handoff前实际检查（不是QA）：13导航+21活动文档516路径/空白exit0，根非FF行不变，4保护/112旧证据保持；[治理命令/分类](evidence/r4-dev/coordinator-governance.json)和[原样输出](evidence/r4-dev/coordinator-governance.txt)真实exit1/322行，其中318任务外旧诊断与r3原输出多重集相同，4行是checker只识别`](plans/...md)`而不识别独立工程合法`../plans/`唯一父bundle链接的既有兼容限制。原8条draft/r3tasks元数据诊断已消失；未造子任务/改checker或隐去exit1。[导航检查](evidence/r4-dev/coordinator-navigation.json)为协调器实际交付输入。

[资源记录](evidence/r4-dev/resources-final.json)列出本轮419个记录PID全部已不存在、六固定端口lsof逐个exit1无占用、61个自有r4根路径及用途。每个协议报告另有真实native Server自然exit0/线程join/端口rebind，正常与forced/parentlost事实分开；不以停止等待当进程结束。保留r4主根/两版独立copy/自身venv/合成状态和trace供fresh QA复核与复现；关键报告均在bundle，待QA/Owner完成且无证据依赖后可清理这些自有资源，先保留持久证据。r1-r3旧资源/错误confirmed库与协调器根未触碰；无Git worktree/分支或任务外资源清理。

最终新增证据列表/hash在[evidence-manifest.txt](evidence/r4-dev/evidence-manifest.txt)，不依赖被根*.log/*.sha256忽略的报告作为唯一证据。交接给协调器实际启动的fresh-context Verification：消费本节精确r4、candidate、完整历史、原命令/退出码和已知边界后独立运行/记录checklist。该角色可验证本候选，不能把本DEV自检当自己的结果。

## r3 tasks完整历史

``````text
r3tasks|Task ID: FF-001
r3tasks|Revision: r3
r3tasks|Status: dev_blocked
r3tasks|Owner Role: Development
r3tasks|Allowed Writers: Development
r3tasks|Handoff: r3 blocked by real Python public DB write accepting wrong-operation ACK; Rust formal/copy DEV checks and approved historical-ref/confirmed-sink gap closures preserved; coordinator/PM prepares next Revision; no completed developer_handoff or QA
r3tasks|Workflow Mode: STD
r3tasks|Execution Mode: agent_team_same_session
r3tasks|
r3tasks|# FF-001 r3 Development
r3tasks|
r3tasks|批准：Human Owner于2026-10-22明确“批准 FF-001 r3，按这个方案继续推进。”；消费owner_approved spec SHA256=`cf2ff0ff8e8d7bf1bc2302127f5f5bc7a32d767be470ddf9875cf3ced59efbb1`。当前HEAD=`dbed9107dce5701fa138a66b3c13aba637a27b86`，不是本会话commit；正式树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，保留其他dirty，无commit/push/refs。
r3tasks|
r3tasks|## 实施计划与边界
r3tasks|
r3tasks|1. 原Rust driver内有限2-byte DB INT raw ISO adapter；先编码/截断/拒绝单元矩阵，再执行120秒有界真实matched_ack_preflight，真实自然/故障回收与unknown证据。
r3tasks|2. gate通过后完整Rust AC01–AC15，补原未验项、文档与独立复制；随后独立Python同例，自身3.11/uv锁/fixture。
r3tasks|3. 保持r1/r2失败及原库只读；完整矩阵成功后记录逐AC真实命令/退出码、candidate manifest、资源和developer_handoff，协调器另启fresh Verification。不得写spec/checklist或代验收。
r3tasks|
r3tasks|r3私有根`/private/tmp/ff-001-r1-r3dev-k989azay`保存新synthetic状态/日志/报告；可复用原r2 target缓存`/private/tmp/ff-001-r1-20261021-r2dev/rust-target`，只作编译缓存。重要证据持久化本bundle，新库不覆盖r2错误confirmed库。通知由协调器管理。
r3tasks|
r3tasks|初始检查点当时r3 gate与全AC均not_run；最新结果见后续批次，不用r2结果替代。本实现继续使用已加载aiis/rust-runtime/plc-point-mapping/backend-arch(local state only)/i18n-workflow/code-document-indexer；工程README/PLAN/catalog由project-governance约束，不运行初始化工具或修改skills。
r3tasks|
r3tasks|## R14 gate 批次1
r3tasks|
r3tasks|- `cargo test --locked --offline --manifest-path field-flow/field-flow-rust/Cargo.toml --test s7_int_pdu` exit0，固定请求/INT、全部逐长度截断和响应字段拒绝、typed结果3个测试通过。缓存沿用r2 target，无新依赖/锁变动。
r3tasks|- 从Rust工程执行 `cargo test --locked --offline --features test-fixture --test local_protocol matched_ack_preflight -- --test-threads=1 --nocapture`，外层本任务自有subprocess harness实际120秒timeout；实际总12.60秒（含编译）、exit0，测试本体1.97秒。内层110秒deadline也未触发。
r3tasks|- 真实正常GET/单item raw WriteVar/ReadVar及停止后匹配codec读回成立；bad-ref Read拒绝，已应用WriteVar的bad-ref/短响应均unknown=1、confirmed=0、actualWriteVar=1；各新私有库重复10轮/原库重启不重发。旧child真实退出后才返回失败，不在旧会话派发新job；fixture自然退出及31102/31103/31880实际rebind成功。
r3tasks|- [gate-1.txt](evidence/r3-dev/gate-1.txt)、[gate-1.json](evidence/r3-dev/gate-1.json)、[三表只读导出](evidence/r3-dev/gate-1-stores.json)已持久化。r2错误confirmed库未触达。此为Development gate，自主继续完整Rust矩阵，不是QA/Owner验收或完整handoff。
r3tasks|
r3tasks|## Rust完整矩阵批次2（Python之前）
r3tasks|
r3tasks|正式交付树依序`cargo fmt --check`、`cargo check --locked --offline --all-targets --features test-fixture`、`cargo build --locked --offline --bins --features test-fixture`、`cargo test --locked --offline --lib`、`cargo test --locked --offline --features test-fixture -- --test-threads=1 --nocapture`，逐条exit0，最后全套62.16秒。[命令/退出码](evidence/r3-dev/rust-delivery-commands.json)，原样输出rust-delivery-0.txt至4.txt。lib本身0-case，功能证据归14个integration tests。
r3tasks|
r3tasks|| AC | Rust实际DEV证据 |
r3tasks|| --- | --- |
r3tasks|| AC01 | locked构建/正式全套通过；42文件hash相同的单目录复制build/help/全矩阵正在执行。 |
r3tasks|| AC02 | CLI/config3 tests：无参/中英help空目录零IO、错误参数，非法schema/mode/缺库/不覆盖，字段/重复ID/endpoint/overlap/typed数值/budget拒绝。 |
r3tasks|| AC03 | 五个INT逐值GET/Write，停止后分别独立匹配raw ReadVar、A5保持，越界/float/bool/string/实际块越界拒绝。 |
r3tasks|| AC04 | idle/status/body/JSON/source/time拒绝、clock倒拨锁定invalid；queued TTL以父原子phase证明未派发，expired且零写。 |
r3tasks|| AC05 | 同ID十轮/原库重启不重发，payload/time/target冲突保原记录，ref维护后身份仍不重建。 |
r3tasks|| AC06 | 三读流各20独立sample/request，单PID/generation/session串行归回。 |
r3tasks|| AC07 | 1200ms GET与100ms读8秒并发，>=20样本、max_gap<=500ms，同流不重叠。 |
r3tasks|| AC08 | 静默COTP/分段/慢字节/stale/初始server缺席/断连恢复，总deadline含实际reap，无关HTTP flow恢复。 |
r3tasks|| AC09 | T1/T2恢复、丢ACK unknown十轮/重启不重发、物理别名/overlap阻断，不相关read继续。 |
r3tasks|| AC10 | 已应用写分别终止child/parent，unknown原库恢复/actualWriteVar1；父死亡child<=500ms结束、锁保留、PID消失；T3失败不重发。 |
r3tasks|| AC11 | 真实GET/read、write0/仅simulated、mode交叉拒绝。 |
r3tasks|| AC12 | 10/100容量/2048byte轮转，保confirmed10；audit失败闭child开始gate，排队两个write都canceled/零写、独立read继续。 |
r3tasks|| AC13 | child调用前屏障+父队列stop零写/全join；故障fault_cleanup/exit1、无正常shutdown_complete；冲突保占用者；runtime/SQLite/audit共享一个global end不追加15秒。 |
r3tasks|| AC14 | 自身双语README/PLAN/catalog、locale/索引/组件声明已补，tasks/证据分批记录；Verification/Owner gate未发生。 |
r3tasks|| AC15 | 29个真实ref/header/function/count/global/item/长度/短空附加/4096或4097/transport/bitlen/坏ref紧跟正确ACK拒绝例；无good/confirmed，写unknown/actualWriteVar1、旧会话退役；近65535维护不复用ref。 |
r3tasks|
r3tasks|本批真实失败：rust-remaining-1.txt exit101，测试INT数组缺i16类型；修正后remaining-2/3与正式全套exit0。证据整理脚本两次遇非dict JSON/非字符串evidence字段的AttributeError/TypeError，均exit1，补类型判断后完成；不是软件矩阵失败。
r3tasks|
r3tasks|runtime/driver文件500–800行，职责复核仍是owner监督/私有IPC封装，未扩大平台或任务外重构。根*.log规则不改；必要输出使用.txt原字节副本，旧r2输出以新增来源/hash映射复本保留，原44证据/manifest不覆盖；SQLite/target不纳入源码。Python尚未实现，Rust复制验证后再以独立Python环境/自身夹具核实公开API候选。
r3tasks|
r3tasks|## 当前r3停止事实与交PM的 blocker handoff
r3tasks|
r3tasks|Human Owner批准r3及其SHA256仍是本轮消费的精确输入；PM正在另行准备下一Revision，本Development不写spec/checklist。协调器确认Python真实候选失败后，要求停止后续Python实现/新协议执行、保留Rust成果，先做文档、hash与资源复核；随后协调器明确允许补完原r3的两项Rust测试缺口（实际历史ref/另一操作历史ref、confirmed后sink失败），仅最少测试/fixture接线，无runtime重构。两项均已执行并见下方批次3。本次为`dev_blocked`，不是完整`developer_handoff`，未启动QA或授予Owner验收。
r3tasks|
r3tasks|### Rust正式树与独立复制
r3tasks|
r3tasks|[Rust正式命令](evidence/r3-dev/rust-delivery-commands.json)的fmt/check/build/lib/all-tests逐条exit0；[独立副本命令](evidence/r3-dev/rust-copy-commands.json)的locked build、无参startup及同一全矩阵全部exit0（全tests57.52秒），正式树全tests62.16秒。42文件独立副本没有父/兄弟源码、清单、fixture、环境或可写状态依赖；只使用正常公共依赖缓存与本任务Cargo target缓存。复制品和正式树runtime源码/配置/锁hash相同；测试后仅PLAN双语状态同步为Python阻塞，并同步复制品，当前42文件仍逐字节相等。正式树实际build入口随后再次构建exit0，非仅临时副本交付。
r3tasks|
r3tasks|Rust公开原依赖/锁未换，finite raw codec及全部有效变更留在正式树。新增自身README/PLAN/catalog、locale索引、MIT本工程LICENSE和第三方原许可差异声明。框架/现场/长期运行与原生内存安全资格仍排除；有限本机证据不授权这些外部gate。
r3tasks|
r3tasks|### Python有限公开API真实失败
r3tasks|
r3tasks|本工程独立Python3.11.12、uv0.7.8；`uv lock --python 3.11 --no-python-downloads`、`uv sync --locked --python 3.11 --no-python-downloads`均exit0，自身uv.lock/.venv，未下载解释器/全局升级。锁定python-snap7=3.0.0、httpx=0.28.1、PyYAML=6.0.3、pytest=8.4.2；SQLite环境版本3.47.1来自运行中sqlite3模块，不代表已建本工程执行库。Rust bundled SQLite源宏3.46.0来自已锁libsqlite3-sys0.30.1源头，未额外执行runtime版本SQL。
r3tasks|
r3tasks|从Python工程执行：
r3tasks|
r3tasks|```bash
r3tasks|UV_CACHE_DIR=/private/tmp/ff-001-r1-r3dev-k989azay/uv-cache uv run --locked --python 3.11 --no-python-downloads python -m tests.python_api_preflight --evidence-dir /private/tmp/ff-001-r1-r3dev-k989azay/python-api-preflight-3
r3tasks|```
r3tasks|
r3tasks|实际exit1。真实WriteVar请求ref=`0002`/function05；自身Python S7 Server原正ACK ref=`0002`/function05；代理仅改TPKT绝对byte19为04，ref/error/count/status不变。Client.db_write返回0、get_last_error=0、调用0.147ms，actualWriteVar1，Server注册内存`002a`+14个`a5`，相邻字节保持。候选把ReadVar功能码的ACK当写成功，违反r3 AC15；与ref匹配无关，也不能靠IPC/deadline补校验。
r3tasks|
r3tasks|[完整三份hex/ref/function、版本、原API返回和释放事实](evidence/r3-dev/python-api-preflight.json)、[原样输出](evidence/r3-dev/python-api-preflight-3.txt)、[只读分析](evidence/r3-dev/python-public-api-review.md)、[原源码位置/签名/hash](evidence/r3-dev/python-source-review.json)均已持久化。该probe只验证公开候选，不是完成的Python runtime；没有Python SQLite执行schema、父T3或confirmed记录，不能伪称已提交confirmed。
r3tasks|
r3tasks|自身client PID32027、Server PID32026自然exit0、parent真实join；Server剩余线程[]、proxy真join，32102/32103实际rebind。最终合同断言在自然清理与JSON落盘后才exit1，整轮约121.278ms，不是超时。原两轮夹具误将正常COTP DR无数据ACK的EOF当异常，均exit1，输出原样保留；修正仅自身夹具EOF后得到上述合同失败，未修改第三方。中间辅助路径修正一次FileNotFoundError/exit1、源码hash辅助脚本对server.py误假设而失败，修正只读路径后完成，未造成协议实现变化。
r3tasks|
r3tasks|公开`Client.iso_exchange_buffer(self,data:bytearray)->bytearray`在client.py:1396存在，返回原S7 payload，长度用len；原连接处理TPKT/COTP。Client.connect(:152)内部已完成TCP/COTP和S7 Setup(:1868)，无须消费方调用私有握手。raw入口单send/单receive，无S7 ref/op/status过滤/自动重发；单TPKT16-bit长度/减4/strip3决定payload最多65528字节，没有4096 cap或native FFI指针。原DB写只返回0，无法拿到该次原response；check_write_response(:1484)不比较function。这里只读核查，不调用raw、不新增Python codec/私有transport/monkeypatch/换库；是否承担该责任交PM下一精确Revision。
r3tasks|
r3tasks|### 逐AC最终DEV范围及已知限制（含批次3补测）
r3tasks|
r3tasks|| AC | Rust | Python |
r3tasks|| --- | --- | --- |
r3tasks|| AC01 | 正式树及原42文件独立副本全套exit0；批次3最终43文件hash相同，受影响回归/正式入口检查exit0。 | 仅独立锁/sync/包环境/有限候选probe；完整runtime构建/启动/复制未做。 |
r3tasks|| AC02 | CLI/config3 tests通过，详见批次2。 | 产品CLI/config/schema未实现。 |
r3tasks|| AC03 | 五值逐次真实写/停止后匹配读回/A5保持、类型/块范围拒绝。 | 此probe只写42并查看自身Server内存；完整矩阵未做。 |
r3tasks|| AC04 | 输入拒绝/clock/queued expiry测试通过。 | 未实现/未做。 |
r3tasks|| AC05 | 十轮/原库重启/冲突/ref换代身份保留测试通过。 | 未实现/未做。 |
r3tasks|| AC06 | 三读流各20独立sample、单PID/session测试通过。 | 未实现/未做。 |
r3tasks|| AC07 | 慢GET与100ms读8秒调度测试通过。 | 未实现/未做。 |
r3tasks|| AC08 | 静默COTP/分段/慢字节/stale、缺席/断连恢复、实际回收测试通过。 | 仅正常公开connect/write自然关闭，非完整预算/恢复矩阵。 |
r3tasks|| AC09 | T1/T2/丢ACK/unknown身份和物理范围阻断测试通过。 | 未实现/未做。 |
r3tasks|| AC10 | 父/子死亡、T3 precommit失败、confirmed重启去重通过；批次3新增confirmed后sink真实失败，保持confirmed1、原库重启十轮actualWriteVar仍1，独立读回42。 | runtime/T3未实现，不能给confirmed结论。 |
r3tasks|| AC11 | dry GET/read/write0/simulated/mode隔离测试通过。 | 未实现/未做。 |
r3tasks|| AC12 | 轮转/容量/audit queued零写与独立read测试通过。 | 未实现/未做。 |
r3tasks|| AC13 | 正常/forced分列、队列/child屏障、parentdeath/实例锁/实际PID和端口释放测试通过。 | 仅自身finite probe自然join/PID/端口释放，非完整应用生命周期。 |
r3tasks|| AC14 | 自身双语文档/索引、tasks/命令/资源有真实记录。fresh QA/Owner gate未发生。 | partial工程文档准确标明缺少完整runtime；QA未发生。 |
r3tasks|| AC15 | R14 gate、字段/长度拒绝矩阵通过；批次3纠正早期oldref/otherref仅ref+1标签，实际先完成ReadVar0001，再分别对ReadVar0002/WriteVar0002注入该历史0001，均拒绝/旧child回收，后者unknown/confirmed0/actualWriteVar1。 | **失败**：匹配ref但function错误仍公开写成功；其余完整矩阵未做。 |
r3tasks|
r3tasks|Rust全套及受影响补测exit0是Development已运行范围的事实，不是独立QA/Owner验收。两个原r3覆盖缺口已在协调器明确许可后补完，早期标签错误和原报告仍保留；完整双语言任务因Python公开API失败而阻塞，不创建完整developer_handoff。
r3tasks|
r3tasks|### 最终候选、资源和保护
r3tasks|
r3tasks|- [candidate-manifest-final.json](evidence/r3-dev/candidate-manifest-final.json)：最终正式Rust43文件/Python16文件SHA256、HEAD、工作树与Rust copy逐字节一致性。原42文件快照[candidate-manifest.json](evidence/r3-dev/candidate-manifest.json)原样保留。状态仍`dev_blocked_cross_language_not_completed_handoff`，Python只是partial候选。无commit/push/refs/worktree；不回滚外部修改。
r3tasks|- [resources-final.json](evidence/r3-dev/resources-final.json)：对本轮输出累计397个确切记录PID逐个signal0，均pid_absent；6固定端口lsof exit1零输出，正常用例另有实际rebind。无按名称扫描/终止/杀占用者/换端口。原253PID检查点原样保留。
r3tasks|- 最终Development自有临时目录300个（299个synthetic测试根+本r3dev总根），完整路径/用途在资源JSON。早期前缀目录盘点误把独立coordinator根列入，最终已剔除；该根仅列示/只读，从未修改或回收。总根`/private/tmp/ff-001-r1-r3dev-k989azay`含独立Rust源码复制品、UV cache、3轮Pythonprobe目录与原输出。另复用r2 Cargo target cache；Python .venv在自身工程且已忽略。辅助入口读取/根指针文件也列明。都保留供PM新Revision与后续复现/Verification，由协调器在无依赖时核对回收，不作为唯一持久证据。
r3tasks|- 新必要输出都以.txt/JSON在bundle持久化，原被忽略.log原样保留并有.txt复本；原44历史证据/manifest与r2 tasks可还原归档不得改。运行库/JSONL/target不纳入源码。root导航与spec由协调器/PM改，本Development未修改。
r3tasks|
r3tasks|**交接协调器/PM：精确FF-001 r3、当前正式树/上述manifest/真实证据，Status=`dev_blocked`。** Python原公开DB路径接受错误操作ACK，需PM界定下一精确Revision的受限校验责任及风险并取得Owner批准；保留Rust成果、原标签错误及已补测的精确范围。此次为blocker handoff，非完成交付、QA verdict或Human Owner验收。
r3tasks|
r3tasks|## Rust原r3覆盖缺口补测批次3（最终补充，不扩Python）
r3tasks|
r3tasks|停Python之后的记录审计发现两项真实覆盖缺口，已原样报协调器/PM：早期`oldref`/`otherref`均只是当前ref第二byte+1；confirmed后sink失败虽有其他分别测试，组合未执行。协调器明确继续这两项原批准r3测试。原阶段tasks全文另存[tasks-pre-gap-finalization.txt](evidence/r3-dev/tasks-pre-gap-finalization.txt)，原报告不覆盖，不把标签当证据。
r3tasks|
r3tasks|仅改`src/fixture.rs`、`tests/ack_rejection_matrix.rs`，新增`tests/confirmed_audit.rs`并登记本工程CODE_INDEX。fixture按会话保存上一个Read/Write ref（两个Option，容量恒定），用例先实际完成ReadVar0001，再当前ReadVar0002收到旧同操作0001，或当前WriteVar0002收到另一操作已完成ReadVar0001。三份完整报文、prior请求/正响应、校验错误/unknown/confirmed0/旧PID实际回收见[rust-gap-summary.json](evidence/r3-dev/rust-gap-summary.json)及两份完整ACK报告；不是人工+1标签。已有runtime实现未重构。
r3tasks|
r3tasks|正式树命令`CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo test --locked --offline --features test-fixture --test ack_rejection_matrix --test confirmed_audit --manifest-path field-flow/field-flow-rust/Cargo.toml -- --test-threads=1 --nocapture` exit0；29行ACK矩阵与confirmed-sink两测试通过，[原样输出](evidence/r3-dev/rust-gap-closure-1.txt)。随后仅把fixture存储改为恒定容量last-ref Option、移除新产生的unused import，同步独立副本43文件。
r3tasks|
r3tasks|独立副本最终相同源码执行`cargo test --locked --offline --features test-fixture --test local_protocol --test ack_rejection_matrix --test confirmed_audit -- --test-threads=1 --nocapture` exit0，共6个integration tests/49.845秒，包含共享fixture受影响的四个local_protocol回归。[原样输出](evidence/r3-dev/rust-gap-copy.txt)、[逐命令/退出码/用时](evidence/r3-dev/rust-gap-final-commands.json)。随后正式树`cargo fmt --check`、`cargo check --locked --offline --all-targets --features test-fixture`、`cargo build --locked --offline --bins --features test-fixture`均exit0，恢复正式树实际入口。无理由重复的其他已通过全套未再重跑；原正式14integration及副本完整矩阵证据继续有效，新增组合为第15个integration test。
r3tasks|
r3tasks|confirmed-sink在真实GET→WriteVar→正ACK→T3 confirmed1之后，用已批准test-fixture审计故障入口让实际sink持久失败（返回audit_persist），健康闸门拒绝新iteration；停止后原进度仍confirmed1，原库重启十轮不重发，actualWriteVar1，停止后独立原协议读回42。两轮三表只读导出与结果见[confirmed-sink-stores.json](evidence/r3-dev/confirmed-sink-stores.json)。故障退出与重启正常退出分开，fixture真join和三端口rebind均实际完成。
r3tasks|
r3tasks|原24+18条旧证据manifest逐条hash复核、两个manifest本身及r2tasks还原ce9d哈希均保持；含manifest共44个旧文件完整保留，见[history-protection-final.json](evidence/r3-dev/history-protection-final.json)。最终候选、397PID/6端口与300自有目录清单见上述final JSON；被忽略.log保留且必要原样.txt复本可追踪，新增证据最终SHA256清单见[evidence-manifest.txt](evidence/r3-dev/evidence-manifest.txt)。本轮最终diff/链接/hash检查另记[final-static-checks.json](evidence/r3-dev/final-static-checks.json)。
r3tasks|
r3tasks|协调器在PM冻结r4 draft（SHA256=`eb3dbc318c89b4772ff9f54f7a1e4ea5ede1520e309f51f310ceb2d5234ebdd1`）后报告：13导航同步r4draft/r3dev_blocked，31活动文档481路径/空白检查exit0，根7导航去FF行与baseline一致，4保护文件与44旧证据保持，git diff --check exit0。这是协调器文档/保护自检，不是独立QA。本Development只原样持久其[checker输出](evidence/r3-dev/coordinator-governance-r4-draft.txt)与[实际命令/分类JSON](evidence/r3-dev/coordinator-final-governance-check.json)：治理checker实际exit1/330行，其中318条任务外旧诊断完全相同，8条为当前r4 draft spec/r3 dev_blocked tasks元数据兼容诊断（2项重复4次），4条为子工程PLAN指向`../plans/`唯一bundle的识别限制；脚本只认字面`](plans/...md)`。没有为消诊断伪造子任务、改checker或把r3tasks改为未批准r4。
r3tasks|
r3tasks|最终静态记录器首次提前检查时，尚待生成的manifest/自报告被判缺失，另将说明中的反引号字面checker模式误认成链接，实际exit1已保留[final-static-first.json](evidence/r3-dev/final-static-first.json)。先生成报告清单，再让链接检查跳过inline code后复核；没有代码/协议失败或任务外修改。
r3tasks|
r3tasks|静态记录器第二次在git-ignore检查发现根`*.sha256`也忽略新清单，实际AssertionError/exit1；诊断见[final-static-second.json](evidence/r3-dev/final-static-second.json)。未生成内容的本任务清单占位文件移除，最终用未忽略的evidence-manifest.txt，不改根.gitignore。协调器后续范围复核报告121个当前修改/未跟踪文件都在field-flow或13允许导航内，HEAD仍dbed9107，未建checklist；不是QA结论。
r3tasks|
r3tasks|最终状态仍FF-001 r3 `dev_blocked`：Rust已完成上述DEV范围及精确缺口补测；Python仅独立公开API有限预检真实失败，完整runtime/T3/矩阵未实现或执行，等待PM下一精确Revision。无完整developer_handoff、QA verdict或Owner验收；不以Rust成果代替双语言合同完成。
r3tasks|
r3tasks|## r2 tasks完整历史
r3tasks|
r3tasks|以下每个原物理行仅增加`r2tasks|`前缀；移除前缀可逐字节还原原r2 tasks（含其原r1归档），SHA256=`ce9dfe615dbfc69c2e0dccf00178d7bcb8856ea51458e4e2d405c3a55389d0e9`。
r3tasks|
r3tasks|`````text
r3tasks|r2tasks|Task ID: FF-001
r3tasks|r2tasks|Revision: r2
r3tasks|r2tasks|Status: dev_blocked
r3tasks|r2tasks|Owner Role: Development
r3tasks|r2tasks|Allowed Writers: Development
r3tasks|r2tasks|Handoff: r2 DEV blocked by real unmatched S7 WriteVar ACK being committed confirmed; exact evidence handed to coordinator/PM for next Revision; no completed developer_handoff or QA
r3tasks|r2tasks|Workflow Mode: STD
r3tasks|r2tasks|Execution Mode: agent_team_same_session
r3tasks|r2tasks|
r3tasks|r2tasks|# FF-001 r2 Development
r3tasks|r2tasks|
r3tasks|r2tasks|Human Owner 于2026-10-21明确“批准 ff001 r2”。消费owner_approved spec SHA256=`1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`。当前交付树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，不提交、不改任务外dirty。原r1 tasks完整原字节下方前缀归档，原24份evidence和manifest不改。
r3tasks|r2tasks|
r3tasks|r2tasks|## r2实施计划
r3tasks|r2tasks|
r3tasks|r2tasks|1. Rust独立工程：typed配置/输入、独立并发flow、父队列与每PLC持久driver子进程；匿名有界IPC、总deadline内回收、parentdeath与本实例锁、跨进程start/stop闸门。
r3tasks|r2tasks|2. 父SQLite单owner、T1/T2/T3与checked持久审计、unknown物理范围阻断、容量/日志和健康；demo01单轮编排，CLI无参无IO与双语。
r3tasks|r2tasks|3. 自身Rust协议fixture及AC01–AC14真实DEV矩阵，独立复制/源码一致性；Rust证据完成后Python3.11.12同例。
r3tasks|r2tasks|4. 文档/索引/逐AC命令退出码/限制/资源、固定candidate manifest，交精确r2 developer_handoff；fresh Verification由协调器另启动。
r3tasks|r2tasks|
r3tasks|r2tasks|辅助依赖理由（锁前记录）：`libc 0.2`仅POSIX实例锁/继承FD/非阻塞审计/磁盘容量及信号回收；`sha2 0.10`仅稳定typed意图SHA256；`chrono 0.4`仅UTC JSONL时间（亦为原driver传递依赖）。不引入新S7栈、service manager或通用平台。Tokio/reqwest/serde/serde_yaml/tracing/rusqlite保持批准family与精确S7版本。
r3tasks|r2tasks|
r3tasks|r2tasks|## r2事实进度
r3tasks|r2tasks|
r3tasks|r2tasks|- 已完整读取批准r2合同、r1归档/原tasks和驱动证据、根/FF规则、development角色与canonical workflow。r1结果不充当r2进程隔离验证。
r3tasks|r2tasks|- 初始r2检查点当时所有AC均not_run；恢复后的实际局部结果与当前阻塞见后续批次，不将旧检查点当作实时状态。
r3tasks|r2tasks|- r2私有临时根：`/private/tmp/ff-001-r1-20261021-r2dev/`；与r1资源分离，仍符合批准路径前缀。源码在正式交付树，测试库/日志/target与复制品仅本临时根。保留用途/释放情况随事实更新。
r3tasks|r2tasks|- 主协调器r2资源`/private/tmp/ff-001-r2-coordinator-nt6pixvu`供批准/保护hash复核，由协调器管理。
r3tasks|r2tasks|
r3tasks|r2tasks|## r2 平台中断检查点
r3tasks|r2tasks|
r3tasks|r2tasks|记录时间：2026-10-21T12:13:21Z（Asia/Shanghai 2026-10-21 20:13:21）。这是本次只读盘点时间；平台失败的独立精确时间戳未返回。主协调器报告实际`development`角色上一turn失败，转述的平台错误原文为：
r3tasks|r2tasks|
r3tasks|r2tasks|> This content was flagged for possible cybersecurity risk... This agent's turn failed.
r3tasks|r2tasks|
r3tasks|r2tasks|本次依主协调器指示仅恢复Development事实记录，不继续源码或运行测试。它是平台工具中断，不是本任务QA结论，也不撤销Human Owner对精确r2的批准；不因此改spec、改scope或请求重复范围批准。
r3tasks|r2tasks|
r3tasks|r2tasks|### 已落盘的实现面
r3tasks|r2tasks|
r3tasks|r2tasks|正式交付树`field-flow/field-flow-rust/`已新增以下未验证候选，全部保留，不撤销或清理：
r3tasks|r2tasks|
r3tasks|r2tasks|- `Cargo.toml`、`.gitignore`。
r3tasks|r2tasks|- `src/main.rs`、`src/lib.rs`、`src/commands.rs`、`src/config.rs`、`src/domain.rs`、`src/runtime.rs`、`src/driver_process.rs`。
r3tasks|r2tasks|- `src/infrastructure/mod.rs`、`audit.rs`、`state.rs`、`posix.rs`。
r3tasks|r2tasks|- `src/services/mod.rs`、`src/app/mod.rs`、`src/app/demo01.rs`。
r3tasks|r2tasks|- `src/bin/ff-fixture.rs`（当前仅占位帮助，不是已实现fixture）。
r3tasks|r2tasks|- `config/loopback.yaml`、`locales/en-US.json`、`locales/zh-CN.json`。
r3tasks|r2tasks|
r3tasks|r2tasks|正式`Cargo.lock`尚未生成；Rust README/PLAN/catalog/CODE_INDEX和测试尚未完成。`field-flow-python/`尚未创建。上述源码没有编译成功或运行证明，不能作为可交付候选或声称满足AC。
r3tasks|r2tasks|
r3tasks|r2tasks|### 最近实际命令与结果
r3tasks|r2tasks|
r3tasks|r2tasks|在上述文件写入后，实际尝试：
r3tasks|r2tasks|
r3tasks|r2tasks|```bash
r3tasks|r2tasks|CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo generate-lockfile --offline --manifest-path field-flow/field-flow-rust/Cargo.toml
r3tasks|r2tasks|CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo check --locked --offline --all-targets --features test-fixture --manifest-path field-flow/field-flow-rust/Cargo.toml
r3tasks|r2tasks|```
r3tasks|r2tasks|
r3tasks|r2tasks|两条都在依赖解析阶段非零失败；该次转录只保留了工具`output`，未单独保存数值`exit_code`，不补造。输出报告：`chacha20 = "^0.10.0"`的本地可见`0.10.1`被yank，依赖链为`rand 0.10.2 -> quinn-proto 0.11.17 -> quinn 0.11.11 -> reqwest 0.13.4`。尚未在线解析或安装新的依赖，没有运行到源码编译，更没有项目构建成功、启动、schema、协议fixture或AC测试结果。该普通离线解析问题尚未排除，不把它直接升级成合同不可实现。
r3tasks|r2tasks|
r3tasks|r2tasks|本次恢复只读命令`date -u`、tasks/文件列表读取、manifest hash及`du -sh`整体exit0；没有运行协议、构建或测试。原24份证据manifest SHA256仍为`d046e373c875c236ef1ad9678e1ba6dd9141d5667c92be2bd66ed70acbbd8770`。
r3tasks|r2tasks|
r3tasks|r2tasks|### 当前资源、未验项与下一步
r3tasks|r2tasks|
r3tasks|r2tasks|- r2自建临时根`/private/tmp/ff-001-r1-20261021-r2dev/`只读盘点为0B；没有本r2启动的runtime/driver/fixture、listener、状态库或日志，无本r2进程清理动作。r1私有资源按原历史保留；协调器临时资源归协调器管理。
r3tasks|r2tasks|- r1前缀归档、原24份证据及manifest原样保留；没有创建checklist或修改spec/其他模块/真实配置，也未连接真实设备或第三方业务接口。
r3tasks|r2tasks|- r2 AC01–AC14全部尚无完成证据，Python全未执行。平台失败不属于DEV自检完成、独立QA或Human Owner最终验收。
r3tasks|r2tasks|- 协调器已只读指出候选`force()`必须区分真正wait/reap和wait错误、spawn中途失败也须实际回收；子进程日志须用独立有界通道归父。这些建议尚未实施或验证，不能写成已修复。
r3tasks|r2tasks|- 下一步由主协调器处理平台工具中断，再恢复原Development或明确续接者；继续已批准r2时先解决依赖解析及上述未验证实现问题，再完成全部Rust矩阵、Python同例和正式developer_handoff。当前状态`dev_blocked`只表示本次执行中断，并非r2技术方案已被证伪或另一个Revision已获批准。
r3tasks|r2tasks|
r3tasks|r2tasks|## r2恢复批次1（2026-10-21）
r3tasks|r2tasks|
r3tasks|r2tasks|精确spec SHA256再次消费为 `1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`。当前是获批范围内的普通本机合成应用开发，原平台中断记录保留，不升级为软件故障或完成。
r3tasks|r2tasks|
r3tasks|r2tasks|- 正常在线 `cargo generate-lockfile --manifest-path field-flow/field-flow-rust/Cargo.toml` exit0，208个依赖；原离线解析问题来自缓存，正常下载已消除。固定 `rust-snap7=1.142.2`、`rusqlite=0.32.1`；未修改第三方源码。
r3tasks|r2tasks|- `CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo check --locked --offline --all-targets --features test-fixture --manifest-path field-flow/field-flow-rust/Cargo.toml` 最初exit101（候选类型推断/tracing错误）；实际修正后exit0。`cargo build --locked --offline --bins --features test-fixture` exit0。全部构建/依赖在本工程，无兄弟工程导入。
r3tasks|r2tasks|- `cargo fmt --manifest-path field-flow/field-flow-rust/Cargo.toml` exit0；修正原候选真实reap判定、spawn前完成可失败的IPC构造、独立有界child日志通道、service执行状态、unknown阻断、审计健康闸门、Stop通知竞态、JoinError/异常退出收尾。仍在真实矩阵迭代，不能以源码检查替代运行证明。
r3tasks|r2tasks|- 真实矩阵命令为 `CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo test --locked --offline --features test-fixture --test local_protocol --manifest-path field-flow/field-flow-rust/Cargo.toml -- --test-threads=1`。第1轮exit101：受限执行不能bind本机端口，后续 `lsof` exit1且零占用输出；未杀占用者或换端口。第2–4、6轮exit101：自有夹具在macOS接受socket继承nonblocking导致握手提前断开；已显式改blocking。第5轮exit101：新增健康gate字段编译错误。第7轮exit101：测试错误要求慢流瞬时in_flight==1（实际0合法），已改<=1。第8轮exit101：测试持有额外Owner/State句柄导致actor join等待，已在join前释放。第9轮exit101：故障收尾把完成后返回错误的JoinHandle再次poll，已改分辨timeout与已完成错误。所有真实失败日志保存于 [r2-dev](evidence/r2-dev/)，未覆盖历史。
r3tasks|r2tasks|- 已在这些真实运行获得局部事实：INT五个值实际各1次写，重复10轮与原库重启不重发；输入越界/float/bool/string/时间/body/schema拒绝；三个独立读流各20个request/sample，单PID/generation、一个S7 session；1200ms GET并发100ms读在8秒约77个sample，HTTP等待不占PLC队列。完整AC仍在继续，不宣称已通过整矩阵或完成handoff。
r3tasks|r2tasks|- 新增本机资源均为 `/private/tmp/ff-001-r1-r2-rust-<case>-<unique>/` 私有状态/日志，与既有r2 target根分开；fixture固定31102/31103/31880，只连接同项目合成服务。正常退出/故障回收与port释放由矩阵继续观测。现阶段Python尚未开始，fresh Verification/checklist尚无。
r3tasks|r2tasks|
r3tasks|r2tasks|## r2 当前停止事实与 blocker handoff（2026-10-21）
r3tasks|r2tasks|
r3tasks|r2tasks|主协调器已要求停止实现和新的协议执行，等待PM处理新Revision。当前不是平台中断，而是新得到的实际协议语义失败；原平台中断、r1驱动预算失败及r2所有测试失败均保留。未启动Python、未新增协议guard/运行代理、未换库/改第三方、未写spec或checklist。
r3tasks|r2tasks|
r3tasks|r2tasks|### 有限真实复核
r3tasks|r2tasks|
r3tasks|r2tasks|```bash
r3tasks|r2tasks|CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo test --locked --offline --features test-fixture --test local_protocol --manifest-path field-flow/field-flow-rust/Cargo.toml stale_reference_probe -- --test-threads=1 --nocapture
r3tasks|r2tasks|```
r3tasks|r2tasks|
r3tasks|r2tasks|实际exit101。真实ReadVar请求reference `0100`、服务端原响应 `0100`、代理实际发送 `0101`，driver仍返回good/-23131。真实WriteVar请求 `0200`、原正ACK `0200`、实发 `0201`，父业务iteration返回Ok，T3持久化 `confirmed=1`。只改TPKT绝对byte12（S7 PDU reference第二字节），没有改功能码、长度、error、item-status或INT；完整三份报文hex均在 [stale-reference-evidence.json](evidence/r2-dev/stale-reference-evidence.json)。实际WriteVar1/已应用正ACK1，停止runtime后独立协议读回 `002a`，邻接A5不变。这不是重复写或未写成功问题，而是未匹配ACK也被当成确认。
r3tasks|r2tasks|
r3tasks|r2tasks|[源码/API复核](evidence/r2-dev/stale-reference-review.md)只读确认锁定候选 `db_write` 返回路径检查ISO/global/item-success，没有提供原始ACK/ref；公开 `iso_exchange_buffer` 存在，但未使用，也没有为通过测试手写新的PDU适配器。IPC request_id/generation匹配不能替代r2 R08/T3要求的S7匹配正ACK。因此当前adapter未满足批准r2，需PM处理具体实现边界/风险，不由Development放宽合同。
r3tasks|r2tasks|
r3tasks|r2tasks|probe先完成自然收尾再执行合同断言：driver PID11963自然结束、父wait/reap且PID消失；fixture native server自然exit0、父wait、代理/HTTP真实join；31102/31103/31880实际rebind均成功。父JSONL保留正常资源收尾事实，它只表示该次程序自然退出，并不改变ACK业务断言失败。完整日志、state三表只读JSON导出及固定报文在本bundle，不依赖临时库作为唯一证据。
r3tasks|r2tasks|
r3tasks|r2tasks|### 批次2命令/结果
r3tasks|r2tasks|
r3tasks|r2tasks|- 第10轮同 `cargo test ... --test local_protocol -- --test-threads=1` 实际exit101：`approved_loopback_matrix`真实通过；`fault_and_stop_matrix`的split/slow用例通过后，stale返回成功导致合同断言失败。split和slow分别4617ms，父整体deadline触发实际TERM/wait/reap、原PID消失，属于fault_cleanup，不能写成正常shutdown。不能以这两项局部隔离实证抵消匹配ACK失败。日志为 [rust-matrix-10.log](evidence/r2-dev/rust-matrix-10.log)。
r3tasks|r2tasks|- `cargo fmt --manifest-path field-flow/field-flow-rust/Cargo.toml --check` exit0。
r3tasks|r2tasks|- `CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo check --locked --offline --all-targets --features test-fixture --manifest-path field-flow/field-flow-rust/Cargo.toml` exit0；[输出](evidence/r2-dev/final-partial-check.log)仅有共享测试support在另一测试binary中未用的dead_code warning，不是runtime错误。
r3tasks|r2tasks|- 源码结构还未完成文档/索引，也没有独立复制测试。`tests/process_lifecycle.rs`已写入并通过上述编译，但其真实进程矩阵未执行；不能把写入测试代码当作通过。
r3tasks|r2tasks|
r3tasks|r2tasks|### 逐AC当前DEV范围（均非独立QA）
r3tasks|r2tasks|
r3tasks|r2tasks|| AC | Rust实际范围与缺口 | Python |
r3tasks|r2tasks|| --- | --- | --- |
r3tasks|r2tasks|| AC01 | 自身Cargo.lock解析/编译/bins构建成功；库API显式synthetic初始化及运行已执行。独立复制、产品CLI无参/启动完整矩阵未执行。 | not_run，目录未创建 |
r3tasks|r2tasks|| AC02 | typed实现与分层编译成立；未完成非法配置/版本/CLI双语全矩阵，不能标完整通过。 | not_run |
r3tasks|r2tasks|| AC03 | 五个INT值实际各写1次；首段测试最后32767及有限probe42有停止后独立读回/A5邻接证据。未完成每个边界值分别独立读回/块越界矩阵。 | not_run |
r3tasks|r2tasks|| AC04 | 越界/float/bool/string、来源时间、非200、body超限/坏JSON/source/idle、domain时钟倒拨局部断言执行；入队时效/全部schema变体未完成。 | not_run |
r3tasks|r2tasks|| AC05 | 同命令10轮、原execute库重启不重发，payload冲突且原记录不变已执行；child恢复及time/target组合未完成。 | not_run |
r3tasks|r2tasks|| AC06 | 三个独立读流各20个request/sample，同child PID/generation及1个S7 session的真实断言通过。完整任务仍阻塞。 | not_run |
r3tasks|r2tasks|| AC07 | 1200ms GET和100ms读的8秒并发真实执行，约77样本、最大相邻成功间隔<=500ms断言通过；同流结构保持单轮，瞬时in_flight<=1。 | not_run |
r3tasks|r2tasks|| AC08 | 真实split/slow由父约4617ms内回收child/PID消失；stale读响应被错误接受，继而有限写ACK复核失败。静默COTP/断连恢复完整后续矩阵未执行完成。 | not_run |
r3tasks|r2tasks|| AC09 | 首段真实已写丢ACK、unknown10轮/重启/新ID阻断及不相关read断言在第10轮first test通过。T1/T2/别名/overlap后续用例写入但未执行到。 | not_run |
r3tasks|r2tasks|| AC10 | **未满足**：有限真实未匹配WriteVar ACK被父T3提交confirmed=1。父/子崩溃专项、ACK后T3失败未执行到。 | not_run |
r3tasks|r2tasks|| AC11 | 实际GET/read、simulated=1、write增量0及mode交叉拒绝在first test通过；不视作完整任务完成。 | not_run |
r3tasks|r2tasks|| AC12 | 有界日志/健康/容量与故障hook已编译；真实轮转/容量/排队审计故障矩阵未执行。 | not_run |
r3tasks|r2tasks|| AC13 | 有限probe普通driver/fixture自然关闭、真实wait/join/端口/PID释放；split/slow是fault_cleanup真实reap。排队/child调用前屏障正常stop及parentdeath专项未执行到。 | not_run |
r3tasks|r2tasks|| AC14 | 本tasks及证据已更新；Rust工程README/PLAN/catalog/CODE_INDEX尚未完成，Python未开始，无fresh Verification或Owner最终验收。 | not_run |
r3tasks|r2tasks|
r3tasks|r2tasks|### 当前候选、资源与保护复核
r3tasks|r2tasks|
r3tasks|r2tasks|- 正式源码在 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust/`；未commit、未push、无Git refs操作。当前局部candidate文件/hash/字节清单为 [partial-source-manifest.json](evidence/r2-dev/partial-source-manifest.json)，状态明确 `partial_implementation_blocked_before_handoff`；不得把它当可交付完成候选。
r3tasks|r2tasks|- 原20个候选文件均保留并做必要实现修正；新增Cargo.lock、独立fixture/HTTP infrastructure、execution service、真实协议/进程测试support，完整清单见manifest。不撤销任务外dirty。`field-flow-python`不存在。
r3tasks|r2tasks|- [resources-checkpoint.json](evidence/r2-dev/resources-checkpoint.json)列出30个本r2私有临时根：`/private/tmp/ff-001-r1-20261021-r2dev`保存target/原运行日志，其他均 `/private/tmp/ff-001-r1-r2-rust-<case>-<unique>`保存合成状态/日志。暂保留给PM复核及后续获批候选复现，由协调器在证据/验证依赖结束后核对回收；无临时源码复制品或新worktree。
r3tasks|r2tasks|- 对记录中50个本任务确切PID逐个 `kill(pid,0)` 只读探测：全部pid_absent；未按进程名扫描或终止任何进程。固定端口 `lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN` exit1且零输出；probe另有真实rebind证据。没有当前自有运行任务、driver/fixture或listener需继续清理；未清理其他任务资源。
r3tasks|r2tasks|- spec SHA256仍 `1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`；原24份r1 evidence/manifest保持。checkpoint日志和源码保留，未把失败改成pass或deferred complete。
r3tasks|r2tasks|
r3tasks|r2tasks|最终仅文档/hash复核exit0：27个Rust候选文件与partial manifest逐字节一致；spec、r1 tasks前缀归档及24份原evidence/manifest均保持批准/历史SHA256；本Development新增Markdown链接/空白检查通过，Python/checklist仍不存在。当前r2临时target/运行根约1.0GiB，新持久evidence约328KiB；保留供PM复核，资源不代表运行服务或交付产物。`git diff --check -- <本实现/tasks/evidence范围>` exit0，但该范围多为未跟踪新文件，不能替代前述逐文件/hash检查或声称全仓治理通过。
r3tasks|r2tasks|
r3tasks|r2tasks|**交给协调器/PM：FF-001 r2、当前正式工作树、上述partial manifest与全部证据，Status=`dev_blocked`。** blocker为候选高层S7 driver把未匹配WriteVar ACK接受为成功，现父T3无法满足r2匹配ACK合同。请PM决定下一精确Revision的受限适配方案、验证与风险，再取得Human Owner批准。此次为blocker handoff，明确不是`developer_handoff`完成，不启动完整实现QA，也不提供QA verdict或Owner验收。
r3tasks|r2tasks|
r3tasks|r2tasks|## r1 tasks完整历史
r3tasks|r2tasks|
r3tasks|r2tasks|下方每行唯一`r1tasks|`前缀；去前缀可逐字节还原r1最终tasks，SHA256=`d68e3e01be185ce124dff1387bed5784bf65ecbc9a0510022f066f9a203fbcc3`。历史状态/待批准描述仅指当时，不覆盖当前r2授权。
r3tasks|r2tasks|
r3tasks|r2tasks|````text
r3tasks|r2tasks|r1tasks|Task ID: FF-001
r3tasks|r2tasks|r1tasks|Revision: r1
r3tasks|r2tasks|r1tasks|Status: dev_blocked
r3tasks|r2tasks|r1tasks|Owner Role: Development
r3tasks|r2tasks|r1tasks|Allowed Writers: Development
r3tasks|r2tasks|r1tasks|Handoff: r1 dependency prechecks blocked; PM r2 draft awaits exact Owner approval; no developer_handoff completion/QA
r3tasks|r2tasks|r1tasks|Workflow Mode: STD
r3tasks|r2tasks|r1tasks|Execution Mode: agent_team_same_session
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|# Development 事实与计划
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|精确批准：Human Owner 于 2026-10-21 回复“批准 ff001 r1”。本次消费的 owner_approved spec SHA256：`13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70`。关联 ARCH-TOOL-001 r2 全文件 SHA256：`049574ad8fb9e43fcf7073aa217410b28cc21da7100500a28f9887510aac64ae`。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|Development 由主协调器实际选定 development 角色；contract_only。写入仅限本 tasks、真实 evidence 与两个获批独立工程。导航由协调器机械同步。本仓库存在大量任务外 dirty，保持不动；不提交/推送，不执行 Docker、真实数据库/PLC、第三方 HTTP。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|## 执行计划
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|1. 建立工具链/依赖与驱动预检证据，实际验证候选同步 timeout、ACK、server 正常退出；不满足时报告 blocker，不改第三方或降标。
r3tasks|r2tasks|r1tasks|2. Rust 独立工程：typed 配置/domain、专属 PLC owner、持久状态与审计、单轮 demo01、调度与正常停止；逐 AC01–AC14 自检，再做独立复制一致性核对。
r3tasks|r2tasks|r1tasks|3. Rust DEV 证据完成后，Python 以同矩阵实现并自检；显式 Python 3.11 / uv --no-python-downloads。
r3tasks|r2tasks|r1tasks|4. 固定源码 manifest、记录实际文件/命令/退出码/资源/限制，developer_handoff 至协调器后启动 fresh-context Verification。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|## 当前检查记录
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|- 已读取根 AGENTS、README/PLAN 双语、canonical workflow、development.toml、FF README/PLAN/catalog 双语与完整批准 spec。FF 内无更近 AGENTS。
r3tasks|r2tasks|r1tasks|- memory registry 对 FF-001/field-flow 检索无结果，未依赖历史结论。
r3tasks|r2tasks|r1tasks|- `rustc --version` / `cargo --version`：均 1.89.0；`uv --version`：0.7.8。
r3tasks|r2tasks|r1tasks|- 首次 `uv python find 3.11 --no-python-downloads`：因默认 uv cache `.git` sandbox 访问限制失败，尚未证明解释器缺失；后续使用任务私有 cache 重试。
r3tasks|r2tasks|r1tasks|- 两版实现、AC01–AC14、协议/退出测试：not_run，尚无 developer_handoff 或 QA verdict。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|## 临时资源
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|本任务临时根将使用唯一 `/private/tmp/ff-001-r1-20261021-dev/`，各资源用途和实际创建情况随执行更新。重要结果持久化本 bundle evidence；自然退出/端口释放实际检查后记录，不以停止标志代替 join。后续 QA 需要的资源保留至协调器按 workflow 审计回收。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|## Development 阶段停止事实（2026-10-21）
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|候选 `python-snap7==3.0.0` 的公开 Client 路径不能满足批准 R04 同步 connect/IO 硬预算。已向主协调器报告并完成其要求的公开配置入口、真实读写与重试核查。完整调用链、准确版本/源码hash、命令和原样结果见 [driver_api_review.md](evidence/driver_api_review.md)。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|- connect：5003 ms，超3000+500ms；实际断言exit1。
r3tasks|r2tasks|r1tasks|- 真实WriteVar已应用、正ACK分段送达：6019 ms，超5000+500ms；exit1。
r3tasks|r2tasks|r1tasks|- 真实ReadVar分段送达：6018 ms，超5000+500ms；exit1。
r3tasks|r2tasks|r1tasks|- 3次旧真响应后匹配ACK：有限receive重试，actual write=1，174ms；exit0，仅证明此路径不重发。
r3tasks|r2tasks|r1tasks|- 每次Python协议测试proxy已join、server子进程自然exit0且无剩余线程、32102/32103释放。Rust独立静默COTP预检实际500ms错误、thread join/31102释放，exit0。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|公开 Client 无timeout/transport注入参数；低层连接虽有timeout，但Client每次重建对象且无参连接。直接使用私有初始化/改第三方/替换候选不在本Development可自行决定范围。正式实现暂停，等待PM/协调器的新Revision决定；未安装其他候选、未创建两版正式源码目录。此处不是开发完成handoff，不能据此启动完整实现QA或宣称任务已完成。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### 逐AC当前状态
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|| AC | Rust | Python |
r3tasks|r2tasks|r1tasks|| --- | --- | --- |
r3tasks|r2tasks|r1tasks|| AC01 | not_run：只有独立probe锁/构建，不是runtime或复制验证 | not_run：只有独立probe环境，不是runtime锁/构建 |
r3tasks|r2tasks|r1tasks|| AC02 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC03 | not_run | 仅驱动预检INT42/相邻字节成立；完整demo01矩阵not_run |
r3tasks|r2tasks|r1tasks|| AC04 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC05 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC06 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC07 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC08 | 仅静默COTP500ms局部预检；完整AC not_run | 候选驱动预算实测失败；完整runtime矩阵not_run |
r3tasks|r2tasks|r1tasks|| AC09 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC10 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC11 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC12 | not_run | not_run |
r3tasks|r2tasks|r1tasks|| AC13 | 仅probe thread/31102释放；runtime/native server not_run | 仅probe proxy/server子进程/32102/32103释放；runtime not_run |
r3tasks|r2tasks|r1tasks|| AC14 | not_run：正式runtime文档/Verification尚无 | not_run：正式runtime文档/Verification尚无 |
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### 实际资源与限制
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|- `/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/`：唯一3.11 probe环境；无数据库。
r3tasks|r2tasks|r1tasks|- `/private/tmp/ff-001-r1-20261021-dev/uv-cache/`：本次依赖下载缓存。
r3tasks|r2tasks|r1tasks|- `/private/tmp/ff-001-r1-20261021-dev/rust-driver-preflight/`：独立候选crate probe源码/锁/target；不是交付runtime。清单/锁/源码已持久保存evidence。
r3tasks|r2tasks|r1tasks|- 当前无本任务常驻进程、listener、状态库。没有Docker/真实PLC/第三方业务HTTP、其他任务写入或Git refs操作。
r3tasks|r2tasks|r1tasks|- 临时资源暂保留给PM复核及协调器决定后续复现/回收；重要证据已在bundle，不依赖临时目录作为唯一记录。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### 交给协调器/PM的 blocker handoff
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|精确 FF-001 r1；工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，未commit。Development新增仅本tasks与evidence，不改spec/checklist/任务外文件。请由PM决定符合既定预算的获批候选/适配范围及新Revision；未获批准前不进行替代实现。成功预算不能用异步waiter超时代替同步driver终止。尚无developer_handoff完成、fresh Verification verdict或Human Owner最终验收。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### 追加有限 Rust native 预检（同日，协调器明确要求）
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|因为Python已实证分段接收突破总deadline，协调器要求在原r1批准的31102/31103核查Rust/native同类风险，未展开正式实现。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|- `ff001-driver-preflight native_standard`：实际原生server+透明proxy，connect3ms/write1ms/read1ms，actualWriteVar1、匹配正ACK、INT42及邻接字节成立；exit0。
r3tasks|r2tasks|r1tasks|- `ff001-driver-preflight native_split`：实际SendTimeout/RecvTimeout=5000ms，原始ACK7字节header延迟3s、body再延迟3s；write6020ms仍成功、实际写1；读回及原生server注册内存正确。超5500ms断言exit101，原失败保留。
r3tasks|r2tasks|r1tasks|- 两次proxy真join，原生server子进程自然exit0、父进程wait、31102/31103实际重bind；不是native stop返回即宣称线程已join。buffer直到server drop后仍活着。
r3tasks|r2tasks|r1tasks|- `cargo fmt`、`cargo build --locked --offline`、后续`cargo fmt --check`均exit0，仅临时候选probe。源码/锁与真实输出持久于evidence；完整调用链与限制见driver_api_review。
r3tasks|r2tasks|r1tasks|- 这项失败说明底层RecvTimeout不等于整次driver deadline；并未排除native所有可能保守预算适配。不能仅换Python候选就宣称问题解决。PM需在下一精确范围中决定可验证办法，不能降低原预算。
r3tasks|r2tasks|r1tasks|- Rust AC03仅新增单值驱动R/W局部证据，AC08新增现参数映射的总预算失败；其余完整runtime AC状态仍如上表not_run。
r3tasks|r2tasks|r1tasks|- 最终临时Rust probe占用97M，Python环境964K、UV缓存480K；保存用于失败复核及后续gate。无listener/常驻进程/状态库；正式Rust/Python源码目录依然未创建。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### Development 记录检查
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|`git diff --check -- field-flow/plans/FF-001-dual-runtime-demo01` exit0；因bundle未跟踪，该命令不构成新文件内容检查，另执行证据JSONL解析/源脚本编译/空白与链接断言。两份受保护spec的SHA256复核均保持原值。无替代依赖安装、spec/checklist写入、QA verdict或最终验收。当前gate为PM处理依赖/预算合同并取得Human Owner对新Revision的批准。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|### 公开native参数分配核查及最终阻塞结论
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|协调器再次要求仅用当前Rust候选公开参数判断保守阶段分配能力。已只读界定COTP2次接收、S7协商、INT单slice、每次PDU最多64片/128次RecvPacket；不能机械除2。发现native `Purge()`在raw recv恰为512字节时持续循环，无deadline/次数上限，且通过接收超时、协议错误、disconnect/析构可达；成功POSIX连接路径恢复blocking，socket未设置系统接收/发送超时。公开Ping/Send/Recv参数不能约束此路径，完整说明及源码hash见evidence/driver_api_review.md。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|最小 `native_split_budgeted` probe仅把公开Send/Recv参数改为10ms，同样真实分段ACK下write10ms错误、read10ms错误；server已写42，actualWriteVar1。proxy/server自然join/exit0、两端口释放。probe exit0只证明这一条路径能及时失败，不证明完整R04。原6020ms失败保留。未实际执行永不返回Purge/强杀用例，未修改第三方、未安装2.1.0，未扩成正式runtime。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|最终blocker handoff：当前r1两个候选的既有公开入口尚不能证明整次同步IO/退出预算，Rust有具体未受控Purge循环；需PM在新Revision中明确可验证适配方案并获Human Owner批准。继续保持`blocked_dependency`；无developer_handoff完成、QA verdict或Owner验收。
r3tasks|r2tasks|r1tasks|
r3tasks|r2tasks|r1tasks|元数据规范化：仅将当前状态名规范为`dev_blocked`并补充真实Handoff，Revision仍为r1；原`blocked_dependency`依赖合同阻塞事实和全部失败历史未消除，PM r2仍为待精确批准的draft，不表示r2已实施或已进入QA。
r3tasks|r2tasks|````
r3tasks|`````
``````
