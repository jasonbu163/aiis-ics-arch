Task ID: FF-001
Revision: r4
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 independently passed exact r4 rework1 dual-version candidate; F-001/F-002/F-003 closed; QA1 qa_failed original retained; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Run: QA2
Selected Role: verification
Fresh Context: fork_turns="none"

# FF-001 r4 返工1 独立 Verification QA2

## 1. 当前 verdict 与交接

**QA2 verdict：`qa_passed`。** 针对同一已批准 r4 的返工1统一 `developer_handoff`，Rust 和 Python 的 AC01–AC15 均在下述有限本机范围通过。F-001/F-002/F-003 已由本次实际运行、原始报文/状态/进程证据关闭；没有待解除的实现 failure 或环境 blocker。Development 的绿灯只作为输入，没有替代本 QA 的运行与判断。

**Human Owner final acceptance：pending。** 本结论只交接 Human Owner 决定精确 r4 的最终验收；不代表现场、生产、长稳、跨平台或部署/发布。主协调器可依本权威记录机械同步导航，不能把 QA 通过写成已获 Owner 最终验收。

执行者 `/root/ff001_verification_r4_after_rework1`，实际选定 `verification`，fresh context `fork_turns="none"`，未继承 Development 对话推理、未委派通用 Agent。只从批准 bundle、当前源码/diff、锁、原始输出和本次实际验证得出结论。角色 TOML 的 `gpt-6.1-sol / max` 是配置证据，未获得底层运行 model/effort 遥测；`contract_only`、串行 handoff 和写入审计不宣称平台 ACL 或强制路由。

## 2. QA1 失败完整保留，当前输入与范围

**QA1 的真实 verdict 仍为 `qa_failed`，不是被本次改成通过。** QA1 原 checklist 的完整 547 行/原字节、原失败说明、源码及输出索引，已由 Development 持久保存于 [QA1 原文快照](evidence/r4-rework-1/qa1-checklist-original.txt)，SHA256=`5e0048a80396b3b6a985a8f767782fe0d2e9a228add148f1db4810fa35705f3e`。QA2 已核对该快照、本次写入前的原 checklist、自有原字节副本三者相同；[保留映射](evidence/r4-rework-1/preserved-inputs.json)的全部 157 项 hash 均匹配。QA1 的原候选 `4221b6…`、原 tasks `b7507466…`、真实失败和错误 confirmed 历史均保持。QA1 内容及其指向的原始报告是历史独立证据，不是 DEV 自检。

| QA1 项目 | 原结论与证据类型 | QA2 处置 |
| --- | --- | --- |
| F-001 | 真实 S7 FIFO probe exit1；IO1200/queue2000/每 Read ACK 延迟600ms，第一读成功、第二 canceled，actual ReadVar1。 | 原探针以当前库重跑并保留完整 Sample，两读成功；另正式/隔离矩阵验证 queue1000 下的两读和 queued write。 |
| F-002 | QA1 为静态控制流 + 本地算术反例，没有伪称宿主跳时真实误写。返工 red-3 另实证 queued/precall 两例错误 confirmed1/WriteVar1。 | 本次真实 queued/precall 受控偏移均 canceled/clock_invalid、WriteVar0；不改宿主钟。 |
| F-003 | 真实调用前屏障 probe exit1；T2=1、WriteVar0、started日志0，但 health.in_flight=1。 | 本次观察 started 前0、ACK扣留时1、完成和实际故障reap后0，错身份 started 不回调。 |

Human Owner 的精确授权：“批准 FF-001 r4，按方案继续完成 Python 版本，完成后按 STD 进入双版本独立 QA。” 当前 spec §2.2 明确允许记录实际集成缺陷及受影响修复；返工为原合同内 bugfix，没有新 Revision 或扩大协议面。

正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD=`dbed9107dce5701fa138a66b3c13aba637a27b86`。dirty 是输入，未 reset、提交、推送或修改 refs。已读取根 AGENTS、根 README/PLAN 双语、canonical workflow、verification TOML、FF 和两工程 README/PLAN、完整 bundle/嵌套归档、源码及差异、锁与原始证据；FF 下没有更近 AGENTS。使用 `project-governance`、`aiis`、`rust-runtime`、`backend-arch`（仅本地状态/事务/稳定 key）、`plc-point-mapping`（仅标准 DB INT）、`i18n-workflow`、`code-document-indexer` 及适用 reference。未引入 FastAPI/ORM/Celery、UI/Tauri 或通用平台。

| 精确 QA2 输入 | SHA256 |
| --- | --- |
| owner_approved `spec.md` | `e30641845b63f295b408568009c25514f314101d0a2e2b72d331d4255a73045d` |
| 最新有效 `tasks.md` | `81fa30cdec9ce2f1640cdbd2ca7abd43bd127f8f910db5e1f87b3d3e068bc60c` |
| [返工1 candidate](evidence/r4-rework-1/candidate-manifest-final.json) | `701272f1ea19c4759d604810c1aaac4cdce3e4ee5930aaba62c147f4dd52c15b` |
| [返工1 evidence manifest](evidence/r4-rework-1/evidence-manifest.txt) | `4cd6cbfc1713ce72889b28747520b694a2c91b7e49f9b27fd34a043b7b73cac3` |
| QA1 原 checklist | `5e0048a80396b3b6a985a8f767782fe0d2e9a228add148f1db4810fa35705f3e` |

完整 spec 归档还原：r3 180301 bytes / `cf2ff0ff8e8d7bf1bc2302127f5f5bc7a32d767be470ddf9875cf3ced59efbb1`；r2 107258 / `1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`；r1 47049 / `13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70`。按完整归档还原及逐代活动合同差异核对，未把历史“未QA”当作当前事实。原证据 manifest 24项、r3 67项、r4 126项、返工1 275项（含清单自身共276文件）全部存在且 hash 匹配。

QA2 自有根下文记作 `Q=/private/tmp/ff-001-r4-qa2-RFwbir`。正式 Rust44/Python48 与当前 candidate 全部逐文件匹配，两个 Development 独立 copy 也匹配。QA2 自建 Rust `Q/isolated/rust/project` 的直接父目录只有 project，44文件相等；新 `Q/rust-copy-target` 不借父清单、兄弟源码、fixture、环境或可写状态。Python48及其 QA1 最终隔离副本 `/private/tmp/ff-001-r4-qa-wY5eCh/isolated/python/project` 全部保持，因此该副本原独立验收证据可按变更边界沿用。

相对 QA1 Rust43 仅12项新增/变更：runtime/domain/driver_process/execution 四处必要接线、fixture 的600ms故障、local_protocol 的 Clock 接线、新 runtime_regressions 三项回归，以及 README/PLAN 双语和 CODE_INDEX 五文档。Cargo清单/锁、INT codec、SQLite schema、Python48均不变。已独立审查这些差异，没有从整棵 dirty HEAD 推断本返工归属。

## 3. 实际环境、命令与结果

实际宿主 macOS15.7.7 (24G720)/arm64，rustc/cargo1.89.0、Apple clang17.0.0、uv0.7.8；QA2 自有 Python 环境 CPython3.11.12，sqlite3=3.47.1，python-snap7=3.0.0、httpx=0.28.1、PyYAML=6.0.3、pytest=8.4.2。hatchling1.32.4为冻结 build-system pin，离线 build 成功；不把辅助 provenance 的同名常量当运行遥测。Cargo保持 rust-snap7=1.142.2/rusqlite=0.32.1，实际 registry crate SHA256=`8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`，公开API/native四文件 hash 与 spec 一致；QA2 Python env 的 client/connection/s7protocol/server 四文件也与冻结原件匹配。

Rust 两个 cwd 分别为正式 `field-flow/field-flow-rust`、`Q/isolated/rust/project`，CARGO_TARGET_DIR分别 Q/rust-formal-target、Q/rust-copy-target。Python cwd为正式 `field-flow/field-flow-python`；清除 PYTHONPATH/VIRTUAL_ENV，UV_CACHE_DIR=Q/uv-cache（复制正常缓存）、UV_PROJECT_ENVIRONMENT=Q/python-venv、PYTHONPYCACHEPREFIX=Q/python-pycache；pytest禁 cacheprovider，build输出Q/python-dist。所有 uv 命令显式 `--python 3.11 --no-python-downloads --offline`。无解释器下载、全局安装、锁变更或仓库构建产物。

下表是 QA2 自己执行；完整逐命令 argv/cwd/PID/timeout/用时/输出 hash 在 Q 下对应 `*-commands.json`。每个 gate 外层120秒、full外层180秒，真实输出/协议报告另有原110秒gate约束；没有更改原单调用预算。

| Rust 命令（两 cwd 各执行） | 正式 exit / 秒 | 隔离 exit / 秒 |
| --- | --- | --- |
| `cargo fmt --check` | 0 / 0.212 | 0 / 0.382 |
| `cargo check --locked --offline --all-targets --features test-fixture` | 0 / 18.226 | 0 / 20.574 |
| `cargo build --locked --offline --bins --features test-fixture` | 0 / 22.851 | 0 / 16.115 |
| `cargo test --locked --offline --test s7_int_pdu -- --test-threads=1 --nocapture` | 0 / 2.7 | 0 / 2.084 |
| `cargo run --locked --offline --bin field-flow --` | 0 / 0.414 | 0 / 0.477 |
| `cargo test --locked --offline --features test-fixture --test local_protocol matched_ack_preflight -- --test-threads=1 --nocapture` | 0 / 2.146 | 0 / 3.15 |
| `cargo test --locked --offline --features test-fixture -- --test-threads=1 --nocapture` | 0 / 68.796 | 0 / 68.77 |

两份当前 full 各18个integration tests全部通过（含codec3、CLI3、原协议/进程及新增回归）；lib/bins/doc自身0-case不作为功能证据。正式 full=`22d245583dd05751edc9612f4757262000066f62640694849a64f9f56117fc7d`，隔离 full=`5d9fb44e5128feffa0680a637793870413ba5fd5d64361bf86cdda9eb37258a7`。正式/隔离当前测试均为最终 queue1000 参数，不沿用 DEV 的早期 queue2000 全测替代。

| Python QA2 命令 | exit / 秒 |
| --- | --- |
| `uv lock --check --offline --python 3.11 --no-python-downloads` | 0 / 0.09 |
| `uv sync --offline --locked --python 3.11 --no-python-downloads` | 0 / 0.047 |
| `uv build --offline --python 3.11 --no-python-downloads --out-dir /private/tmp/ff-001-r4-qa2-RFwbir/python-dist` | 0 / 0.592 |
| `uv run --offline --locked --python 3.11 --no-python-downloads pytest -p no:cacheprovider -q tests/unit -s` | 0 / 1.214 |
| `uv run --offline --locked --python 3.11 --no-python-downloads field-flow` | 0 / 0.386 |
| `uv run --offline --locked --python 3.11 --no-python-downloads python -c import field_flow,tests.fixtures,sys,json,sqlite3,importlib.metadata as m;print(json.dumps(dict(executable=sys.executable,source=field_flow.__file__,fixture=tests.fixtures.__file__,version=sys.version,sqlite=sqlite3.sqlite_version,snap7=m.version("python-snap7"),hatchling="1.32.4")))` | 0 / 0.048 |
| `uv run --offline --locked --python 3.11 --no-python-downloads pytest -p no:cacheprovider -q tests/test_matched_ack_gate.py -s` | 0 / 0.953 |
| `uv run --offline --locked --python 3.11 --no-python-downloads python -m tests.fixtures.cli_smoke` | 0 / 0.869 |

Python本次实际重跑 lock/sync/build、6 unit、R15 gate1、无参与真实产品CLI dry/execute/init/run/inspect/SIGTERM、provenance；没有无理由再跑未变源码的完整15项 protocol 或重建其 QA1 copy。QA2 对 [QA1完整保留输入](evidence/r4-rework-1/preserved-inputs.json)中的正式/最终隔离两套原命令20行、原样stdout、34份独立报告及实际三报文/状态/回收逐hash核对；两套 lock/sync/build/compile/unit6/gate1/local15/CLI/provenance 全exit0，local51.976/55.666秒。原raw ACK各30行、真实历史同操作/跨操作ref、4096/4097/65528、最大声明短body、unknown/重启/父子死亡/审计/退出均保留。沿用的是 QA1 独立证据，不是 Development self-check；当前 wheel SHA256同QA1=`5b64ee1e5b36cccc2417330a0d1c65e277ca90efa13b9b09bff5511fa2815b25`，中英locale实际在包内，无venv/SQLite。

| QA2 自有探针/辅助验证 | 真实结果 |
| --- | --- |
| `rustc --edition=2021 Q/qa2_fifo_probe.rs ... -o Q/qa2_fifo_probe`；执行 `Q/qa2_fifo_probe Q` | 编译exit0；实际协议exit0 / 1.823秒。原QA1 probe只在Q适配输出完整Sample及成功断言；当前正式feature库，原源码/失败未改。 |
| `rustc --edition=2021 Q/qa2_runtime_probe.rs ... -o Q/qa2_runtime_probe`；执行 `Q/qa2_runtime_probe Q` | 编译exit0；真实queued/precall/ACK hold/stop probe exit0 / 2.911秒，外层45秒。 |
| `rustc --edition=2021 Q/qa2_bad_started.rs ... -o Q/qa2_bad_started`；执行 `Q/qa2_bad_started Q` | 编译exit0；故意错request_id/generation的有限私有IPC peer，exit0；回调0、实际reap，不连接网络。 |
| `rustc --edition=2021 Q/qa2_extra.rs ... -o Q/qa2_extra`；执行 `Q/qa2_extra Q` | 原QA1 `rust_extra_v2.rs`原字节，以当前库编译exit0；原实际块写/坏后正确ACK两例exit0 / 1.408秒，外层30秒。 |

编译完整argv保留 Q/*-compile.json，`-L dependency`/`--extern`/native路径均来自 QA2正式target，按Cargo fingerprint选择 test-fixture feature rlib；未增加项目测试或依赖。辅助失败也保留：首次manifest辅助脚本把项目名前缀重复导致FileNotFoundError/exit1；首次runtime probe误选非feature rlib编译exit1，按已构建feature fingerprint重选后0；首次静态辅助误把Cargo自身bin的src path视为父依赖，AssertionError/exit1，纠正检查范围后0。均只改Q下helper，不是产品failure。首次正式gate沙箱bind EPERM/fixture_port_conflict，exit101、无协议；三口独立bind均EPERM且lsof空。原stdout/hash保留，合法权限后相同gate/full通过；没有 automatic approval rejection。

## 4. 三项关闭的独立实证

### F-001：关闭（R04 / AC08）

原QA1的同一个透明600ms Read ACK延迟探针，现在 actualReadVar2，两读均good=-23131、相同PID92147/generation1、不同request_id，只有一个COTP/Setup会话；第二请求1217ms，queue2000且IO1200保持。native PID92146自然exit0、proxy真实join、31102/31103实际rebind。请求/native/实发帧中的两次当前ref分别0001/0002；native与透传ACK逐字节相同，无stub ACK。

```text
Read1 request: 0300001f02f080320100000001000e00000401120a10020002000184000000
Read1 ACK:     0300001b02f0803203000000010002000600000401ff040010a5a5
Read2 request: 0300001f02f080320100000002000e00000401120a10020002000184000000
Read2 ACK:     0300001b02f0803203000000020002000600000401ff040010a5a5
```

正式/隔离当前回归再证明 queue1000、IO1200、每响应600ms：两读及queued write全部成功，第二读1201/1194ms、write1213/1210ms，总长均超过queue1000；各次等待及dispatch后的IO分别合法，同一PID90194/91457和一session。最小合法IO500的真实read/write也通过。源码以phase CAS区分queued/dispatched，在dispatch建立IO截止；ready/queue仍各自有限，原source UTC与min(expires,issued+max_age) monotonic上界不刷新，400ms只在父预算内扣一次，child接收工作期。原queued expiry零写、stop和实际reap上界全套重跑，没有延长参数/TTL绕过。

### F-002：关闭（R06 / AC04）

QA2自己写的真实queued及child-precall probe均用原年龄5000ms、受控偏移-2000ms；UTC-only向量仍合法，宿主系统钟没有修改。queued例先真实ReadVar阻塞FIFO，precall例使用可释放child闸门；T2落盘后才改变偏移。两例均返回clock_invalid，原Clock与owner写闸门稳定锁定，实际WriteVar0、started事件0。恢复偏移0后同Clock仍invalid，新ID也被拒；独立ReadVar仍good，未终止读能力。

对两份新私有库以只读连接导出三表：原age5000身份/source/target/issued/expires保持、state=canceled、dispatch_count=1；恢复后新ID state=canceled、dispatch_count=0。没有重置dispatch、刷新来源或改schema。ClockAnchor以同一wall/OS CLOCK_MONOTONIC起点传入owner和有限IPC，出队与真实开始闸门内复核，没有排队后重建锚点。旧可能已发写仍unknown，confirmed后sink组合及原库恢复都随全矩阵通过。

### F-003：关闭（R04/R11 / AC12/AC13）

自有precall probe在T2已in_flight1时仍health0/started日志0/WriteVar0；放行后实际WriteVar1并扣留ACK，此时health1、started日志1已可读，未等结果才补日志。IO deadline触发后原PID92170实际消失、health0、unknown1、runtime_fault/fault_cleanup，未写正常shutdown_complete。正式/隔离回归另实际确认正常完成后health0，以及第二次hold ACK forced reap后0。

自有stop-before-call例在相同屏障闭闸，canceled1/WriteVar0/started日志0、自然退出并join/rebind。反向IPC fixture只伪造错request_id或generation的started：两个case均`forced_driver_stop:ipc_mismatch`，started callback=0，PID91305/91307实际reap。它验证私有IPC身份闸门，不冒充真实S7协议证据；真实开始/未开始仍由前述native服务观察证明。

## 5. 双版本逐 AC verdict

下表“通过”均只限精确本机合成合同。Rust列为QA2正式/自建隔离矩阵及独立探针；Python列为QA2必要复验 + hash相同的QA1正式/最终隔离独立完整证据。测试打印的 dev_check_passed/dev_gate_passed 是原标签，本QA据真实命令和原始内容独立裁定。

| AC | Rust | Python | 验证内容及证据边界 |
| --- | --- | --- | --- |
| AC01 | 通过 | 通过 | 两工程各自锁/build/start/init/test/来源成立，正式候选一致；Rust自建父仅project/独立target全验，Python QA1相同48文件父/兄弟缺席copy完整通过，本次新env/build/CLI再验。 |
| AC02 | 通过 | 通过 | 分层入口/typed配置、中英CLI、空cwd无IO、缺/未知字段/重复ID与endpoint/overlap/预算/版本/模式拒绝，init不覆盖、run无DDL；locale键对称。 |
| AC03 | 通过 | 通过 | 五INT真实GET→WriteVar→每次停止后独立匹配raw读回；8000/ffff/0000/002a/7fff及邻接A5，非法类型/范围拒绝。Rust实际块越界写新probe unknown1/整块A5；Python自有IntMemory有限边界和原Server失败分别保留。 |
| AC04 | 通过，F-002关闭 | 通过 | idle/非200/body/JSON/schema/source/time/TTL零写、原TTL队列到期；本次Rustqueued/precall原锚点实际零写及稳定clock_invalid，Python原queued clock独立证据不变。 |
| AC05 | 通过 | 通过 | 至少10轮及父/child代次和原execute库重启只写1次；payload/time/target冲突保留原意图，不刷新身份。新增clock取消仍保dispatch1。 |
| AC06 | 通过 | 通过 | 三独立读流各20 sample/request，单PID/generation/一session/串行正确归流；新FIFO合法等待也复用同PID，Python原60个独立request证据保持。 |
| AC07 | 通过 | 通过 | 1200ms GET和100ms独立读8秒；Rust正式/隔离各77样本/maxgap106ms，Python QA1正式78/maxgap104.786ms、隔离77/113.950ms；同flow最大在途1、无补跑tick。 |
| AC08 | 通过，F-001关闭 | 通过 | 初始缺席/断连/静默COTP/分段/慢字节/stale、owner统一恢复、整体预算含实际reap；Rust新split4621/4618ms、slow4626/4627ms、stale100/102ms，未超过原上界。合法FIFO与最小IO另已实证。 |
| AC09 | 通过 | 通过 | T1/T2原库恢复；已应用扣ACK→unknown、10轮/重启不重发，物理alias/overlap、新ID不绕过；独立读继续、回读不升级unknown。 |
| AC10 | 通过 | 通过 | 实际父/子死亡、继承锁、T3失败与confirmed后sink、原库不重发；Rust父死亡旧child115/113ms实际结束（<=500ms），独立harness验证旧child存活时锁阻止writer；正常与forced分开。 |
| AC11 | 通过 | 通过 | dry实际GET/read、zero WriteVar/simulated/confirmed0，模式交叉拒绝；Python本次CLI两模式再验。 |
| AC12 | 通过，F-003关闭 | 通过 | 逐行JSONL、降低阈值真实轮转/容量背压、queued审计零写、读继续、confirmed保留；本次Rust真实started统计准确。 |
| AC13 | 通过，F-003关闭 | 通过 | 父队列+child屏障stop零写，正常join/wait/退出0与强制fault_cleanup/非零分列，单global deadline、实际reap/PID/端口释放；错身份started不伪计数。 |
| AC14 | 通过 | 通过 | 双语README/PLAN/catalog/locale/源码头及索引、任务完整交接/命令/资源/历史、实际fresh QA2 verdict均成立；Owner验收单独pending，终态导航由Main机械同步。 |
| AC15 | 通过 | 通过 | Rust29/Python30真实ACK字段/长度/ref拒绝矩阵，真实旧同op/跨op历史ref、迟到/坏后正确ACK、near65535、4096/4097及Python65528；坏会话退役，无good/T3/重发。原AC01–14独立给证据。 |

本次原QA1补充探针以当前Rust库重跑：实际块写offset15/声明32/实际16，s7_remote_error、actualWriteVar1/native正ACK0、unknown1/confirmed0、A5×16；坏ref后正确ACK例s7_reference_mismatch、actualWriteVar1/native正ACK1、unknown1/confirmed0、002a+A5×14。两例各原身份10轮 + 原库重启再10轮，actualWriteVar均仍1，旧driver已消失、native自然exit0、fixture真join及三口rebind。

## 6. 证据完整性、静态检查和限度

Python生产只用原公开connect与每job一次iso_exchange_buffer，没有私有transport、monkeypatch、vendor、换库或高层DB回落；原tests.python_api_preflight及其错误function返回success的历史失败源/hash保持，不改成通过。Python4096是库返回后的业务cap；原单帧payload最多65528，存在临时拷贝，未声称接收前4096硬cap或RSS上限。Rust仍初始化4096 FFI buffer，以合法24/30请求长度和actualSize/精确结构验证；未声称修复native或完整内存安全。

Python原plain bytearray Server的越界部分写真实失败保持。IntMemory仅通过公开register_area注册自有完整2byte合成内存边界，没有第三方修补；它不证明真实PLC块大小、写保护或物理完成。S7正ACK+T3只表示协议确认与本地持久事实，unknown保守阻断没有自动核实/清库/重发入口。

QA2实际 `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch field-flow field-flow/field-flow-rust field-flow/field-flow-python`：exit1、322行，stdout SHA256=`df8ce220425c9cbfd25f66a4fe756e916e75a72bf25aaa6fefac942a435ca15c`。318条任务外原诊断与原r4输出多重集完全相同；其余4条为两独立工程PLAN合法`../plans/FF-001…/spec.md`的字面识别限制，已手工确认目标存在并导航到唯一bundle。没有把checker exit1宣称全仓通过，没有改checker或造子任务。QA1旧332快照原文保持，原8+2暂时导航诊断已经在本次输出消失。

独立静态脚本在写本checklist前检查31份活动文档/570个本地路径，缺失0、空白通过；两版locale三键对称、所有src/tests源码头和CODE_INDEX条目齐全、无父/兄弟path依赖或patch，`git diff --check` exit0。最后checklist落盘后再核对链接/空白、源指纹与唯一写入范围，最终事实见末。

本轮没有真实PLC/第三方API/Backend/AW/CA/tools/Docker操作、真实数据库迁移、现场操作、Git refs/部署/发布或外部发送。真实来源时间可信度、现场型号/固件/权限/非优化DB/工艺互锁、跨主机单writer、长期浸泡/生产容量/归档、service hosting、全平台安装器/签名及许可分发仍为独立deferred gates；它们不掩盖本次验收项。本次当前验收没有未执行必需项或以deferred替代失败。

## 7. 原始输出指纹与资源

Q下原始输出/报告暂留供Owner复核；关键失败历史、命令/版本、实证数值、报文、状态与资源结论已在本checklist持久，不只依赖临时路径。以下为QA2自己产生的必要来源/hash；完整stdout含三报文、状态目录及真实计数，test-only trace不冒充产品审计行。

| Q下文件 | SHA256 |
| --- | --- |
| `rust-formal-protocol-gate.txt` | `ae05858bd189cddde951e96964b4ce5c22f563f382c862b69c6d0ac48924f362` |
| `rust-formal-protocol-full.txt` | `22d245583dd05751edc9612f4757262000066f62640694849a64f9f56117fc7d` |
| `rust-copy-protocol-gate.txt` | `490c1fd7632bf17b32dadc6e13f85d9d34bf3cabc199818c4e6b443e5e6a9df9` |
| `rust-copy-protocol-full.txt` | `5d9fb44e5128feffa0680a637793870413ba5fd5d64361bf86cdda9eb37258a7` |
| `python-protocol-gate.txt` | `69c83b937e50f4b1ff1354d8d690f546d143a387a606ec4079ef65db983b69f9` |
| `python-protocol-cli.txt` | `115cdae1f1a62177183eb87baadfcbaa48df2a8d2b41da9b8eb9ebbe7ef0e712` |
| `qa2_fifo_probe.rs` | `dc109c7081eed7b8db4bdf4e0ffb427c273479669087fbe0d261d44e2b10d72c` |
| `qa2_runtime_probe.rs` | `07fa0a0569ad9c4c4e620de686db221ebedda979b927e10bc9273d3235f77ede` |
| `qa2_bad_started.rs` | `6437c9cc33e6384a3ad680898b1a9fa44272d377e1b72ff9e2f586b33fedc6bc` |
| `fake_started_child.py` | `fa6e64cb5ae87751431b2ccd1018e4fd434bdb33925e259c7f5af4b46f0bd09a` |
| `rust-fifo-probe.json` | `dddc971477ed8d007778ccad8401c4fb221f3ed88fb29bcff477e58f1adb5950` |
| `qa2-runtime-probe.json` | `a2b586667d5522204f5022aff2711e135b3374bb5aadd4bdfd949738c80910f2` |
| `qa2-bad-started.json` | `466ac206c5b471fe41aa6313c5811b8d97332e007d6fa79aa81959f034beba99` |
| `rust-extra-2.json` | `b16439a76dae4ddfcf06e0bee249389500ca404904820839ff6e1d4d8c7a6bbb` |
| `selected-stores-qa2.json` | `5fa40cfe6bc3d954d81c93455151fcf005bee9a6de19e399692eb4979aa71ea1` |
| `python-qa1-reuse-audit.json` | `929c99e0668d8c28760486cacd3d2ead96e588c6e475291190d0ed38d13dec29` |
| `resources-qa2.json` | `55848216e07787de6da314fd80cff7c9edfafc4dbd5bca7925f2f2b5c10a066d` |

资源审计实际 `python3 Q/audit_resources_qa2.py` exit0：**251个本次输出/确切引用报告记录PID全部absent**，没有未回收或权限不明PID；六个固定端口逐个lsof exit1/空，并实际bind127.0.0.1成功后立即close。未按进程名扫描/杀进程、未杀占用者/换端口。正常案例原报告有native自然exit0、线程join、父wait/reap/rebind；forced/parent_lost案例如实为故障，不冒称优雅退出。

| 固定端口 | lsof exit / output | 实际 rebind |
| --- | --- | --- |
| `127.0.0.1:31102` | 1 / 空 | True |
| `127.0.0.1:31103` | 1 / 空 | True |
| `127.0.0.1:31880` | 1 / 空 | True |
| `127.0.0.1:32102` | 1 / 空 | True |
| `127.0.0.1:32103` | 1 / 空 | True |
| `127.0.0.1:32880` | 1 / 空 | True |

保留资源：Q内自有独立Rust源码copy、两个target、Python3.11 env/cache/build、QA helper/source与新合成状态/JSONL/原报告；以及本次输出明确识别的130个根（含Q，完整路径/hash在Q/resources-qa2.json）。单元内部未导出的临时目录不冒称全部枚举。没有新增Git worktree/分支；未执行目录回收、删除证据或改旧错误confirmed库。QA1/DEV的原资源和最终隔离副本只读保留，Python旧env未用于本次运行。

回收触发：Human Owner最终决定且无后续QA/返工/证据依赖后，由active coordinator核对归属、实际占用和必要证据归档，再安全回收确认无依赖的自有临时资源；本QA不代清理目录。当前无运行中的本QA runtime/driver/fixture/listener。

## 8. Human Owner 最终 gate

QA2通过精确FF-001 r4返工1双版本候选，F-001/F-002/F-003均关闭；QA1失败和r1–r4所有历史原样保留。下一gate是Human Owner最终验收本候选；尚无owner_accepted。若Owner提出实质范围/风险/验收改变，回PM新Revision；若出现实现failure，交实际Development新turn，修复后另启fresh QA。QA2没有修实现或授予范围外权限。


### QA2 最终落盘审计

- 检查时间：`2026-10-22T03:57:40.745682+00:00`。checklist落盘后再执行同一治理命令：**exit1 / 322行**；stdout SHA256=`df8ce220425c9cbfd25f66a4fe756e916e75a72bf25aaa6fefac942a435ca15c`，318原任务外诊断多重集不变，4条合法父bundle链接识别限制保持；无本任务新增实体链接缺失。
- 重新检查31份活动文档、575个本地路径，缺失0、空白/双语locale/源码头/索引均通过，`git diff --check` exit0。QA1原文快照hash仍5e0048…，spec/tasks/candidate/evidence清单与92候选源码hash保持。
- 2585文件基线在本QA写入前差异0；最终差异**仅本checklist.md**。HEAD仍dbed9107dce5701fa138a66b3c13aba637a27b86；没有实现/测试/config/spec/tasks/其他导航或旧evidence写入。临时helper、env、target、合成库及报告均在自有/private/tmp。
- 资源最终事实保持上述251 PID absent及六口lsof空/实际rebind成功；其后仅静态检查/本checklist写入，没有再启动协议、driver或fixture。当前verdict为qa_passed，F-001/F-002/F-003关闭，Human Owner final acceptance仍pending。
