Task ID: FF-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: FF-005 r1 A rework1 documentation and Python harness fixes self-checked in the formal tree; active coordinator -> new fresh-context Verification QA2; QA1 failure history retained and Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Independent Rust/Python basic examples, explicit wiring and bounded CLI validation
Owner: Field Flow
Acceptance Chain Reference: FF-005 r1 Owner approval -> Development -> fresh Verification -> Human Owner final acceptance

# FF-005 r1 Development

> **当前效力纠正 / r1 rework1：** QA1 已于独立 checklist 记录 `qa_failed`（SHA256 `ce2bb7418d447b2b13c334aed4795e40f27eddf550a3b24a1d31d777b77c4a0d`）。F-QA1-001 为六处旧注册文案；F-QA1-002 为 Python 用带空格字串检查紧凑 JSON，漏判真实 `forced_driver_stop`、driver SIGTERM/-15 与 `had_forced_driver_stop=true`。此前“74场景均无强收”及 Python unknown 的资源通过结论撤回；下方原 DEV1 表/报告/命令/误判文字作为历史保留，不再构成当前候选的无forced证据。DEV最终v3原driver63554/-15、QA原driver82757/-15均为真实失败，不是负载随机。unknown1/GET1/写1/42及后续读的业务事实保留，PID消失不能抹掉强收。当前仅在同一已批准r1 A内修复，独立QA/Owner终验未通过。

批准规格 SHA256：22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8。原审稿/批准链见 spec，范围仅 A；B/C 不实施。实际角色为命名 Development，配置 gpt-6.1-sol / high；配置值不冒充独立运行遥测。

正式交付树：/Users/jason/Desktop/DreamCode/aiis-ics-arch。已有并行 dirty 保留，无 Git refs/worktree 动作。主协调拥有 12 份 PLAN/catalog 的机械同步；Development 不写这些文件。

## 实施计划

1. 新增两个单轮 app 和 YAML，最小 kind/dispatch 接线 -> 既有严格配置与安全回归。
2. 各语言自有 Fixture + 正式 CLI 有界矩阵 -> 每场景真实计数、状态、读回、退出和 rebind。
3. 双语案例/配置 README 与教学接线兼容 -> 独立工程副本构建、运行和 teaching01 两模式复演。
4. hash/allowlist 审计及逐 AC 自检 -> developer_handoff；Verification 独立创建 checklist。

## 起步证据

已阅读根契约、README/PLAN、canonical workflow、development TOML、FF 及两工程最近说明/计划/catalog、完整当前 bundle（此时只有 spec），并核对相关 app/config/runtime/fixture/CLI/教程。加载 aiis、project-governance、rust-runtime、plc-point-mapping、code-document-indexer、i18n-workflow 及相关日志/语言中立/文档 placement reference。无新 UI 文案，稳定 result key 不翻译；不需 locale 修改。

基线由主协调提供：`/private/tmp/ff-005-r1-coordinator-n1exrlf8/baseline.json`，含 816 件既有 FF 文件哈希；原稿 35 件副本及 git-status-before 同目录。Development 自有资源根：/private/tmp/ff-005-r1-dev-ovnx25ib。状态/构建/环境/报告只在自有根；旧测试执行前目录清单已保存 resource-before.txt，执行后只登记确切新增目录。独立副本仅验证，交付源码在正式树。

## 执行记录

待实施；下列命令、失败及逐 AC 结论将在真实发生后追加。此文不是 QA verdict 或 Human Owner 终验。

### 首轮实施与真实失败记录

- 新增两语言两个app与两个YAML；config只放行两个新kind，runtime显式派发；Python basic02明确传原owner。业务函数无循环/SQL/连接/重试，所有写经原Execution。没有新增locale文案，只有既有health.result稳定key。
- 工具：rustc/cargo 1.89.0、uv 0.7.8、已有CPython3.11.12。最初`uv python find 3.11`因默认公共cache权限失败；后续全部使用自有cache与禁止解释器下载。
- 正式Rust cwd=field-flow/field-flow-rust：`cargo build --locked --release --no-default-features --bin field-flow --target-dir /private/tmp/ff-005-r1-dev-ovnx25ib/product` exit0，随后同target `cargo build --locked --release --features test-fixture --bin ff-fixture` exit0。日志commands/rust-product.log、rust-fixture.log。
- Python独立副本cwd=/private/tmp/ff-005-r1-dev-ovnx25ib/python：`uv sync --locked --python 3.11 --no-python-downloads --cache-dir /private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache` sandbox DNS失败exit1（python-sync.log）；相同命令获本机网络权限后exit0（python-sync-network.log），仅下载锁定公共依赖，不改锁/manifest/解释器。
- 一次Rust test编译误从仓库根执行，cargo找不到manifest，exit101（rust-test-compile.log）；改cwd后同`cargo test --locked --features test-fixture --target-dir .../product --test basic_examples --no-run` exit0（rust-test-compile-corrected.log）。
- Python新矩阵首轮sandbox禁止32102绑定，3 failed/exit1（python-basic-initial.log），未冒充运行通过；后续仅获批loopback权限运行。
- v2：Python basic01/basic03通过、basic02因harness把预期读协议故障exit1误断言0失败（2 passed/1 failed，python-basic-v2.log）；Rust v2因harness误把field-flow传给只存在于ff-fixture的__native_fixture失败，0/3（rust-basic-v2.log）。已修测试，正式产品仍由field-flow CLI启动，未改原fixture。
- Rust v3 basic02的idle场景暴露观测竞态：fixture ReadVar计数先于回包，GET可能尚未递增；新增独立等待预期GET计数，不改业务。原失败和场景报告保留。Python同样补该等待。读错误、ACK丢失导致原故障退出1保持为显式负向结果，绝不记成正常stop。

双语examples/config README已新增；四USER_GUIDE只修kind事实、新入口及teaching01精确锚点，正式不注册teaching01。独立源码副本在自有根rust/python；最终一致性在交接前再次核对。

### 第二轮证据与计数口径

- Python完整锁定副本命令：cwd=`/private/tmp/ff-005-r1-dev-ovnx25ib/python`，`uv run --locked --python 3.11 --no-python-downloads --cache-dir /private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache python -m compileall -q src tests` exit0；随后`FF005_EVIDENCE_ROOT=/private/tmp/ff-005-r1-dev-ovnx25ib/evidence-python-final uv run --locked --python 3.11 --no-python-downloads --cache-dir /private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache pytest -q -s` **exit0，25 passed in 256.71s**。这是当前pytest测试项数，其中三个新测试函数内共37个独立CLI场景；不与旧FF-001历史48行/向量数互换。
- Python新37场景全部通过自身期望，总场景耗时198.274750s、最大15.559421s，分别小于600/45秒；正常场景产品退出0，read_error两例及unknown一例预期退出1，记录原故障状态，未当正常stop。报告`evidence-python-final/*/report.json`含原输入（不刷新身份/时间）、计数窗口、状态/独立内存、PID/退出及fixture join/rebind。
- 新双语examples README里的赋值/启动/停止/回收bash块已由自有`manual_rehearsal.py python`真实运行，独立A/B `zsh -f`不共享FF变量；路径经各自read显式输入，B持有其FF_PID并真实wait，A持有fixture PID并SIGINT/wait。basic01/02/03各dry/execute六场景全部passed、正常退出0；完整原命令/A/B输出/报告归`manual-python-basic*/{dry_run,execute}`。
- Rust完整首轮的unknown `hold_ack`暴露真实既有driver_deadline强制收driver：unknown1仍保留、后十轮42/GET1/Write1，但`had_forced_driver_stop=true`、exit1，**失败保留且不算正常回收通过**，原报告`evidence-rust-final-v2/basic02-execute-unknown-42-None`。按获批既有fixture故障面改为HTTP延迟窗口后仅写阶段short_ack，仍真实写42但无有效ACK→unknown，不修改产品或降低状态/计数要求；主协调已确认该向量符合A范围。最终完整回归另行记录。
- Rust config新增matches行的首次rustfmt --check exit1；只格式化该获批文件的新增表达式，未整树格式化。随后对两新app、mod/config/runtime及新test的rustfmt --check exit0。teaching01配置锚点改为现有kind集合的唯一字面行，避免格式行折叠依赖。
- 教程：`prepare_teaching.py`从两工程USER_GUIDE逐字提取teaching01完整app/YAML与含精确assert的接线脚本，在自有两个teaching副本执行编辑脚本，均exit0；正式树无teaching01注册。Rust两个教学release bin已构建exit0，Python教学副本自有uv锁定环境sync exit0。最终两模式运行另行登记。
- 中英USER_GUIDE、examples/config README所有可执行代码块除注释语言外对称；当前367条局部文件链接目标全存在，`bilingual-blocks.json`/`doc-links.json`为只读结果。受保护源和最终copy候选hash将在交接记录封存。

## DEV1历史逐场景结果（QA1已否定Python unknown资源通过）

以下来自成功候选的真实报告，所有值按准备/产品/独立读回分窗；读/写数减去preparation，额外独立16字节核验不混入产品计数。`pass`表示场景的具体期望成立，不代表所有产品退出都正常。read_error/unknown为预期故障exit1，原库保留；其他场景均正常exit0。所有行fixture正常close/join，精确自有PID均已reap且检查不存在，各语言三口实际rebind；无强制清理。内存列用首INT的十六进制，后14字节逐一验证A5不变。idle为严格ready=false/null四字段，invalid为value字符串，expired保留一次生成后改为明确已过期的七键输入，测试过程中不刷新。

| 语言 / case / mode / variant / value / seed | GET / ReadVar / WriteVar（产品） | state counts | 首INT + 邻接 | 产品exit / fixture exit | 精确已回收PID（去重） | 秒 |
| --- | --- | --- | --- | --- | --- | --- |
| rust/basic01-dry_run-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64537,64538,64539 | 1.332 |
| rust/basic01-dry_run-value-42-None | 11 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 64458,64459,64460 | 6.006 |
| rust/basic01-execute-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64667,64668,64669 | 1.314 |
| rust/basic01-execute-value-42-None | 11 / 0 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 64571,64572,64573 | 5.352 |
| rust/basic02-dry_run-expired-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64859,64860,64861 | 1.325 |
| rust/basic02-dry_run-idle-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64791,64792,64793 | 1.347 |
| rust/basic02-dry_run-invalid-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64850,64852,64853 | 1.340 |
| rust/basic02-dry_run-read_error-42-None | 0 / 2 / 0 | `{}` | `a5a5` + 14×A5 | 1 / 0 | 64892,64893,64894,64895 | 0.871 |
| rust/basic02-dry_run-value-42-None | 11 / 11 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 64674,64675,64676 | 5.384 |
| rust/basic02-dry_run-value-42-Some(-1) | 11 / 11 / 0 | `{"simulated":1}` | `ffff` + 14×A5 | 0 / 0 | 64898,64899,64900 | 5.397 |
| rust/basic02-dry_run-value-42-Some(0) | 0 / 3 / 0 | `{}` | `0000` + 14×A5 | 0 / 0 | 64992,64993,64994 | 1.361 |
| rust/basic02-execute-expired-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65134,65135,65136 | 1.326 |
| rust/basic02-execute-idle-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65091,65092,65093 | 1.329 |
| rust/basic02-execute-invalid-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65127,65128,65129 | 1.309 |
| rust/basic02-execute-read_error-42-None | 0 / 2 / 0 | `{}` | `a5a5` + 14×A5 | 1 / 0 | 65205,65206,65208,65213 | 0.878 |
| rust/basic02-execute-unknown-42-None | 1 / 11 / 1 | `{"unknown":1}` | `002a` + 14×A5 | 1 / 0 | 65353,65354,65355,65358 | 5.744 |
| rust/basic02-execute-value-42-None | 1 / 11 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 65025,65026,65027 | 5.374 |
| rust/basic02-execute-value-42-Some(-1) | 1 / 11 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 65246,65247,65248 | 5.379 |
| rust/basic02-execute-value-42-Some(0) | 0 / 3 / 0 | `{}` | `0000` + 14×A5 | 0 / 0 | 65316,65317,65318 | 1.350 |
| rust/basic03-dry_run-expired-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65714,65715,65716 | 1.329 |
| rust/basic03-dry_run-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65647,65648,65649 | 1.235 |
| rust/basic03-dry_run-invalid-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65680,65681,65682 | 1.326 |
| rust/basic03-dry_run-value--1-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65469,65470,65471 | 1.338 |
| rust/basic03-dry_run-value-0-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65474,65475,65476 | 1.241 |
| rust/basic03-dry_run-value-1-None | 3 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 65507,65508,65509 | 1.327 |
| rust/basic03-dry_run-value-100-None | 3 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 65609,65610,65611 | 1.329 |
| rust/basic03-dry_run-value-101-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65642,65643,65644 | 1.232 |
| rust/basic03-dry_run-value-42-None | 11 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 65541,65542,65543 | 5.405 |
| rust/basic03-execute-expired-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 66008,66009,66010 | 1.333 |
| rust/basic03-execute-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65936,65937,65938 | 1.318 |
| rust/basic03-execute-invalid-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65973,65974,65975 | 1.324 |
| rust/basic03-execute-value--1-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65720,65721,65722 | 1.333 |
| rust/basic03-execute-value-0-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65753,65754,65755 | 1.336 |
| rust/basic03-execute-value-1-None | 3 / 0 / 1 | `{"confirmed":1}` | `0001` + 14×A5 | 0 / 0 | 65789,65790,65791 | 1.326 |
| rust/basic03-execute-value-100-None | 3 / 0 / 1 | `{"confirmed":1}` | `0064` + 14×A5 | 0 / 0 | 65898,65899,65900 | 1.345 |
| rust/basic03-execute-value-101-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 65931,65932,65933 | 1.326 |
| rust/basic03-execute-value-42-None | 11 / 0 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 65795,65796,65797 | 5.388 |
| python/basic01-dry_run-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62312,62313,62343 | 1.675 |
| python/basic01-dry_run-value-42-None | 11 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 62237,62238,62239 | 5.662 |
| python/basic01-execute-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62453,62454,62455 | 1.616 |
| python/basic01-execute-value-42-None | 11 / 0 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 62351,62352,62353 | 5.734 |
| python/basic02-dry_run-expired-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62645,62646,62647 | 1.694 |
| python/basic02-dry_run-idle-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62591,62592,62593 | 1.679 |
| python/basic02-dry_run-invalid-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62602,62631,62633 | 1.700 |
| python/basic02-dry_run-read_error-42-None | 0 / 2 / 0 | `{}` | `a5a5` + 14×A5 | 1 / 0 | 62685,62689,62690,62691 | 1.236 |
| python/basic02-dry_run-value-42--1 | 11 / 11 / 0 | `{"simulated":1}` | `ffff` + 14×A5 | 0 / 0 | 62722,62723,62724 | 5.849 |
| python/basic02-dry_run-value-42-0 | 0 / 3 / 0 | `{}` | `0000` + 14×A5 | 0 / 0 | 62840,62841,62843 | 1.791 |
| python/basic02-dry_run-value-42-None | 11 / 11 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 62491,62492,62493 | 5.724 |
| python/basic02-execute-expired-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63049,63050,63051 | 1.714 |
| python/basic02-execute-idle-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 62974,62975,62976 | 1.692 |
| python/basic02-execute-invalid-42-None | 3 / 3 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63013,63014,63015 | 1.754 |
| python/basic02-execute-read_error-42-None | 0 / 2 / 0 | `{}` | `a5a5` + 14×A5 | 1 / 0 | 63084,63085,63086,63090 | 1.159 |
| python/basic02-execute-unknown-42-None | 1 / 11 / 1 | `{"unknown":1}` | `002a` + 14×A5 | 1 / 0 | 63552,63553,63554,63644 | 10.668 |
| python/basic02-execute-value-42--1 | 1 / 11 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 63098,63099,63100 | 5.767 |
| python/basic02-execute-value-42-0 | 0 / 3 / 0 | `{}` | `0000` + 14×A5 | 0 / 0 | 63518,63519,63521 | 1.862 |
| python/basic02-execute-value-42-None | 1 / 11 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 62858,62887,62888 | 5.720 |
| python/basic03-dry_run-expired-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64065,64066,64067 | 1.618 |
| python/basic03-dry_run-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63985,63986,63987 | 1.638 |
| python/basic03-dry_run-invalid-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64023,64024,64025 | 1.664 |
| python/basic03-dry_run-value--1-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63707,63708,63709 | 1.722 |
| python/basic03-dry_run-value-0-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63743,63744,63745 | 1.624 |
| python/basic03-dry_run-value-1-None | 3 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 63778,63779,63780 | 1.690 |
| python/basic03-dry_run-value-100-None | 3 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 63939,63940,63944 | 1.676 |
| python/basic03-dry_run-value-101-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 63948,63949,63950 | 1.628 |
| python/basic03-dry_run-value-42-None | 11 / 0 / 0 | `{"simulated":1}` | `a5a5` + 14×A5 | 0 / 0 | 63831,63832,63833 | 5.631 |
| python/basic03-execute-expired-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64380,64381,64382 | 1.602 |
| python/basic03-execute-idle-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64313,64314,64315 | 1.605 |
| python/basic03-execute-invalid-42-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64347,64348,64349 | 1.594 |
| python/basic03-execute-value--1-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64098,64099,64100 | 1.608 |
| python/basic03-execute-value-0-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64108,64109,64110 | 1.619 |
| python/basic03-execute-value-1-None | 3 / 0 / 1 | `{"confirmed":1}` | `0001` + 14×A5 | 0 / 0 | 64144,64145,64146 | 1.674 |
| python/basic03-execute-value-100-None | 3 / 0 / 1 | `{"confirmed":1}` | `0064` + 14×A5 | 0 / 0 | 64271,64272,64273 | 1.697 |
| python/basic03-execute-value-101-None | 3 / 0 / 0 | `{}` | `a5a5` + 14×A5 | 0 / 0 | 64308,64309,64310 | 1.687 |
| python/basic03-execute-value-42-None | 11 / 0 / 1 | `{"confirmed":1}` | `002a` + 14×A5 | 0 / 0 | 64179,64180,64181 | 5.696 |

rust 新37场景总85.508760秒、最大6.005730秒。

python 新37场景总102.367274秒、最大10.668030秒。

两语言各自均满足每场景≤45秒及矩阵≤600秒，构建/init在每场景一次生成原命令之前完成。basic02正常execute及unknown均GET1/写1，之后至少十轮读而无GET/写增加。unknown两语言均仍为unknown1，退出1按原故障语义如实显示，不升级confirmed。最终expired向量TTL1000ms、issued=生成时刻-2000ms、expires=生成时刻-1000ms，首个input_stale时age仍小于10000ms，独立命中expires过期而不靠max_age过期。

rust unknown一次性原输入（后续未改）与inspect：

```json
{"input":{"command_id":"ff005-1793764744568-64427-14","expires_at_ms":1793764804568,"issued_at_ms":1793764744568,"ready":true,"schema_version":1,"source_id":"demo01-feed","value":42},"state":{"counts":{"unknown":1},"meta":{"implementation":"rust","instance_id":"ff-rust-basic02","mode":"execute","schema_version":1,"store_uuid":"1793764744556-65352-0"}}}
```

python unknown一次性原输入（后续未改）与inspect：

```json
{"input":{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"ff005-command","value":42,"issued_at_ms":1793764646989,"expires_at_ms":1793764676989},"state":{"meta":{"schema_version":1,"implementation":"python","mode":"execute","instance_id":"ff-python-basic02","store_uuid":"14822d0738f741df94673cce0a7c86da","created_at":"2026-11-04T03:57:26.853Z"},"counts":{"unknown":1}}}
```

正常execute/42的实际匹配写报文样本（原响应与实际发送响应；本地confirmed不是工艺完成）：

```jsonl
{"language":"rust","at_ms":1793764770117,"operation":5,"original_response_hex":"0300001602f0803203000000010002000100000501ff","positive":true,"request_hex":"0300002502f080320100000001000e00060501120a1002000200018400000000040010002a","request_ref":[0,1],"response_ref":[0,1],"sent_response_hex":"0300001602f0803203000000010002000100000501ff"}
{"language":"python","operation":5,"fault":"","request_hex":"0300002502f080320100000002000e00060501120a1002000200018400000000040010002a","original_response_hex":"0300001602f0803203000000020002000100000501ff","sent_response_hex":"0300001602f0803203000000020002000100000501ff","previous_same_ref":null,"previous_other_ref":null}
```

## DEV1历史自检与候选（当前效力由QA1及rework1取代）

平台macOS15.7.7 arm64，rustc/cargo1.89.0，uv0.7.8，锁定已有CPython3.11.12。正式交付树仍为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，交付为working tree，未创建commit/branch/tag/worktree或push。正式与独立原版副本的有效实现均已整合；教学副本只有本节注明的刻意接线差异。

最终expired向量经主协调复核改为issued=生成时刻-2000ms，expires=生成时刻-1000ms；正TTL1000ms且首个错误时age仍<10000ms，单独证明expires过期。此前非正TTL及正TTL但age同时过期的中间报告保留，不当最终候选。最终新矩阵的确切源码/输出如下，产品app/config/runtime没有因此改变：

| cwd / 命令（root=/private/tmp/ff-005-r1-dev-ovnx25ib） | 真实退出与数量 / 原输出 |
| --- | --- |
| 正式Rust工程：`FF005_EVIDENCE_ROOT=$root/evidence-rust-final-v5 cargo test --locked --features test-fixture --target-dir $root/product --test basic_examples -- --nocapture --test-threads=1` | exit0，3 passed（每函数内部合计37CLI场景），85.53s；commands/rust-basic-final-v5.log |
| 独立Python工程`$root/python`：`FF005_EVIDENCE_ROOT=$root/evidence-python-final-v3 uv run --locked --python 3.11 --no-python-downloads --cache-dir $root/uv-cache pytest -q -s tests/test_basic_examples.py` | exit0，3 passed（内部37CLI场景），102.45s；commands/python-basic-final-v3.log |
| 同产品源码的正式Rust全套：`FF005_EVIDENCE_ROOT=$root/evidence-rust-final-v3 cargo test --locked --features test-fixture --target-dir $root/product -- --nocapture --test-threads=1` | exit0，21个实际测试项=18既有+3新增；commands/rust-full-final-v3.log。之后只修新test的expired输入，并按上行重新跑完3新增；18旧test及产品hash不变。 |
| 同产品源码的独立Python全套：`FF005_EVIDENCE_ROOT=$root/evidence-python-final uv run --locked --python 3.11 --no-python-downloads --cache-dir $root/uv-cache pytest -q -s` | exit0，25项=22既有+3新增，256.71s；commands/python-full-final.log。之后只修新test的expired输入，并重跑3新增；22旧test及产品hash不变。 |
| 独立Rust`$root/rust`：锁定release无feature产品构建；`cargo test --locked --features test-fixture --target-dir $root/rust-test --test cli_contract --test s7_int_pdu -- --nocapture --test-threads=1`；最终新test `--no-run` | 全部exit0；独立实际6项（3 CLI/config + 3 codec），并从该副本release启动六个人工case；commands/rust-copy-product-final.log、rust-copy-unit.log、rust-copy-final-harness-compile.log |
| 正式Rust无feature产品与独立fixture构建：`cargo build --locked --release --no-default-features --bin field-flow --target-dir $root/product`；`cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir $root/fixture` | exit0；commands/rust-formal-product-final.log、rust-separated-fixture.log；普通产品和fixture分开，不将test-fixture宣称为普通产品依赖。 |
| 独立Python：`uv sync --locked --python 3.11 --no-python-downloads --cache-dir $root/uv-cache`；`uv run --locked --python 3.11 --no-python-downloads --cache-dir $root/uv-cache python -m compileall -q src tests` | exit0，最终tests修改后再次compileall0；环境在副本，清单/锁未变。 |
| Rust：`rustfmt --edition 2021 --check src/app/plc_guard_get_int.rs src/app/get_value_guard_int.rs src/app/mod.rs src/config.rs src/runtime.rs tests/basic_examples.rs` | exit0；仅获批文件；commands/rustfmt-final.log。 |
| 正式树：局部Markdown路径/双语代码块、`git diff --check -- field-flow`、baseline scope/hash审计 | exit0；无缺失链接、代码块对称、无范围外变化；非全仓治理QA，未修改旧checker/旧诊断。 |

全套旧安全回归包括严格输入/配置/目标冲突、TTL/队列期限、固定Clock、identity、ACK关联/逐字段拒绝、unknown/重启、已confirmed后审计故障不重发、串行IO/多flow/慢HTTP、父子进程与正常退出。旧故障测试中刻意触发的fault_cleanup保持其原期望，不与本任务正常案例回收混为一谈。Python原Server正常断开COTP0x80诊断行保留在日志，结合server_exit0、remaining_threads=[]和实际join/rebind判断退出；未改第三方源码或吞掉诊断。

### 逐 AC 的 Development 观察（不是 QA verdict）

| AC | DEV自检结果与证据 |
| --- | --- |
| AC01 | 精确r1 A批准链保持；正式无feature产品/fixture与独立工程锁定构建、非零测试、实际启动已验证；780受保护文件、两manifest/锁和旧bundle不变。 |
| AC02 | 三正式case由CLI/YAML实际load；旧CLI/config回归拒绝未知kind/非法target/重叠资源。demo01/loopback/domain/Intent/Execution/owner/driver/HTTP/state/audit原字节保持；新kind仅显式接线。 |
| AC03 | 两语言basic01两模式42/idle独立场景；42至少11次GET，仅simulated1或confirmed1；dry写0，execute写1/002a，14邻接A5。 |
| AC04 | basic02首产品协议操作读；默认负值读后GET，execute写42后≥10轮独立读、GET1/写1；dry≥11读/GET、simulated1/写0。-1/0各两模式实际CLI，读错误无GET/command/写。 |
| AC05 | basic03 -1/0/101正常skip且后续GET继续；1/42/100各两模式单独状态；42≥11GET仍一次执行；完整INT/邻接读回成立。 |
| AC06 | 两新case均有严格idle/非法类型/隔离expires过期；零新增写，input_stale原错误而非guard_false；普通skip无recovering/blocked与错误增长迹象，继续后续轮。 |
| AC07 | app所有写仅经Execution；原身份/issued/expires在场景中不刷新，旧TTL/ACK/unknown/时钟/排队回归保持；basic02写42但无有效ACK后十轮读/不再GET写，原inspect仍unknown1，故障退出1且原库保留。 |
| AC08 | 新app单轮、无连接/SQL/重试/调度；Python读函数由runtime传其原owner。既有独立flow/同流不重叠/每PLC串行/慢HTTP不占IO位回归通过；文档明示独立采样与非原子互锁边界。 |
| AC09 | 两工程examples/config双语pair包含完整真实命令/方法/条件/可改点/计数/停止/失败；各6人工场景真实双shell运行，反向/边界用正式CLI有限harness；无假参数或FF-004 API。 |
| AC10 | USER_GUIDE精确assert脚本在两个独立教学副本实际执行0；逐字teaching01 app/YAML提取后Rust两bin锁定构建0、Python锁定sync/import0；各dry/execute正常0。正式不注册teaching01，FF-002/004等旧bundle hash不变。 |
| AC11 | 最终74个新场景及16个人工/教学scene均有实际wait/join/reap和rebind。正常case产品/fixture0，明确协议故障产品1单列且没有强收；每scene<45秒、每语言矩阵<600秒。空cwd帮助、init拒覆盖、run不建schema、inspect只读由既有CLI回归保持。 |
| AC12 | 本tasks含真实命令、数量、失败、逐场景核心结果、候选文件hash、资源/限制及handoff。Development部分已就绪；fresh Verification checklist/verdict及Human Owner终验仍待各自真实执行，不由Development授予。 |

### 人工/教学的持久结果

正式三个case各自复演完整新指南的A/B代码块；teaching01逐字复演USER_GUIDE的app/YAML/精确接线脚本，使用同一真实CLI/fixture两模式路径。16场景均产品/fixture exit0；A/B shell也wait0，输入路径不依赖共享变量。人工case的命令内容除文档中英注释外相同；后续仅补状态/能力版本表，没有更改已复演命令。

| 语言 / case / mode | state counts | WriteVar | A/B及产品/fixture/driver/server精确已回收PID | 秒 |
| --- | --- | --- | --- | --- |
| rust / basic01 / dry_run | `{"simulated":1}` | 0 | 59421,59423,59433,59436,59439,59441 | 7.232 |
| rust / basic01 / execute | `{"confirmed":1}` | 1 | 59549,59551,59565,59582,59585,59587 | 6.599 |
| rust / basic02 / dry_run | `{"simulated":1}` | 0 | 59691,59693,59694,59696,59699,59701 | 6.576 |
| rust / basic02 / execute | `{"confirmed":1}` | 1 | 59803,59805,59806,59808,59811,59813 | 6.526 |
| rust / basic03 / dry_run | `{"simulated":1}` | 0 | 59911,59913,59914,59916,59919,59921 | 6.569 |
| rust / basic03 / execute | `{"confirmed":1}` | 1 | 60027,60029,60030,60032,60035,60037 | 6.627 |
| rust / teaching01 / dry_run | `{"simulated":1}` | 0 | 60482,60484,60490,60493,60496,60498 | 7.190 |
| rust / teaching01 / execute | `{"confirmed":1}` | 1 | 60619,60621,60622,60652,60655,60657 | 6.539 |
| python / basic01 / dry_run | `{"simulated":1}` | 0 | 53847,53849,53854,53862,53865,53867 | 7.265 |
| python / basic01 / execute | `{"confirmed":1}` | 1 | 54029,54031,54035,54039,54042,54044 | 6.974 |
| python / basic02 / dry_run | `{"simulated":1}` | 0 | 54229,54231,54239,54243,54246,54248 | 7.062 |
| python / basic02 / execute | `{"confirmed":1}` | 1 | 54378,54380,54412,54416,54419,54421 | 6.953 |
| python / basic03 / dry_run | `{"simulated":1}` | 0 | 54543,54545,54549,54553,54556,54559 | 6.994 |
| python / basic03 / execute | `{"confirmed":1}` | 1 | 54677,54679,54683,54692,54719,54726 | 7.168 |
| python / teaching01 / dry_run | `{"simulated":1}` | 0 | 55599,55601,55610,55613,55616,55618 | 7.666 |
| python / teaching01 / execute | `{"confirmed":1}` | 1 | 55735,55737,55741,55745,55748,55778 | 6.874 |

教学副本有意新增teaching01模块/YAML，Rust app/mod及config/runtime接线；Python仅config/runtime接线、initializer未动。其他正式源码保持相同，最终新tests和说明也同步以避免中间稿差异。教学副本不作为正式交付；正式候选不存在teaching01注册。一次辅助sync从Rust cwd误用仓库相对路径触发FileNotFound，未写入任何文件，随后改绝对路径成功；该helper错误不冒充产品失败或首次全绿。

### 正式候选文件清单与指纹

Development实际实现37文件；主协调另有12件PLAN/catalog机械导航，PM仅登记原spec批准。其余4件可选locale无改动。scope-current审计无unexpected，批准spec SHA256保持`22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8`；FF-004 r1保持`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。

以下为精确37件实现候选；`implementation-manifest.json` SHA256=`213cb81ca44cd3e0c1f04774e071f00fa30361ebe41aa8aa69e850b6bfc1e1ab`。本候选不包含会随handoff机械变化的导航及角色文档，后者单列来源和阶段；tasks自身最终hash由handoff消息提供，避免自引用。

| 相对正式树文件 | SHA256 |
| --- | --- |
| `field-flow/README.md` | `76aa8a982ddcc42ea38c127edbdb8e4dac3b58da0b20bce1099e1de19b92c070` |
| `field-flow/README.zh-CN.md` | `149be4875226c4d512b6352ab883698fe69a8491d09abbe546c06727d078a3cc` |
| `field-flow/USER_GUIDE.md` | `3da7b52a4133aef6a53c7c6f1b70262e50b8d64d78fec806b9f13ca3bde9ad69` |
| `field-flow/USER_GUIDE.zh-CN.md` | `674f30035ce4282b1d87009785ad45c7338ea925e2b1869d4cde8c38a53c44d1` |
| `field-flow/field-flow-python/CODE_INDEX.md` | `12d841d330b86cfd83c61535890a5b087b968947f49ad5a4b3549a6c8a15e7c1` |
| `field-flow/field-flow-python/README.md` | `8fb8bcd94d978c52cf80c9644afbf0381bef2203bc58e3e4ab651bfe4013fd48` |
| `field-flow/field-flow-python/README.zh-CN.md` | `a109b3ea877f1f4f99ed17f496c329191192322d268abf57e47558491d847fdf` |
| `field-flow/field-flow-python/USER_GUIDE.md` | `fb478c2a988bac0e5cebbfe735ce0401578f9ff82a61697eb8a944656ebb7a3f` |
| `field-flow/field-flow-python/USER_GUIDE.zh-CN.md` | `de1e7701390cc01120fa93b437f8b73788326fcc3d73be10f31c9e29c6ce901e` |
| `field-flow/field-flow-python/config/README.md` | `4cedcccb28e6a4e9970a3930581a1090c144222cf071899c6a8025e7256d990d` |
| `field-flow/field-flow-python/config/README.zh-CN.md` | `be8254c8073d83a4488e70e44e79aa34a12876f0d37afa8a8fc98b456d0185be` |
| `field-flow/field-flow-python/config/basic02.yaml` | `389210f219f5263632567e4767274c407bf755f32ff487f455cc380c83dcb029` |
| `field-flow/field-flow-python/config/basic03.yaml` | `bf1a3593c6c7efd432be57b7fa0f248998eb85033a4b85127722afea1bc484e2` |
| `field-flow/field-flow-python/examples/README.md` | `750ee25722e5a24e1c0819f994660a38f93db22f3c961f2115a795da5b78ee69` |
| `field-flow/field-flow-python/examples/README.zh-CN.md` | `115f8578b383c52a08c28f5d0b74d00c1a63771d28f3506d98d5c06e0f31f0bc` |
| `field-flow/field-flow-python/src/field_flow/app/get_value_guard_int.py` | `21c23d5eac1df02f70fcbd1c1ec5d7843b8e94f04f0246c947b3e162f2282932` |
| `field-flow/field-flow-python/src/field_flow/app/plc_guard_get_int.py` | `acc8fa65b1ec3d69e69cbb4d80469bdf68bf8fc24ce4e2d83a10833f9cf6b4ec` |
| `field-flow/field-flow-python/src/field_flow/config.py` | `8fa7e9d7e3b0ef26418407ceca084a96c5c1594aedda2ed3ed45e18581cbc949` |
| `field-flow/field-flow-python/src/field_flow/runtime.py` | `06ff0425b3a2179ccc3f6862bf27f803cbf9eca2e8ce2801c1e109b481dbed7d` |
| `field-flow/field-flow-python/tests/test_basic_examples.py` | `979bee2da2f179c6b1d1d51253a04ee728d52102bd48764038ccc943cde27d9c` |
| `field-flow/field-flow-rust/CODE_INDEX.md` | `924b6d59bbdeaf6671e9ea44c5804c61dc57a4dd3e92d7237a83b3a5c9b927e8` |
| `field-flow/field-flow-rust/README.md` | `3381b75ac66010801965ed00657efb1761bc2c27d20f1edf08347dff9669abe0` |
| `field-flow/field-flow-rust/README.zh-CN.md` | `ffb9430aafb8ce0040af414d069ea999a9505262f7cc8526389de7294cad745f` |
| `field-flow/field-flow-rust/USER_GUIDE.md` | `6c9bd7146834485dfe5333f5342663c89c576c43ee9998617429bf150a4bf674` |
| `field-flow/field-flow-rust/USER_GUIDE.zh-CN.md` | `fba1499ea9fe5d39f2d7a8a44b93e88f28a45cea8c6251ae6c467cf22b3576f4` |
| `field-flow/field-flow-rust/config/README.md` | `93f76a281e3e7eae0e52bbf87ebe021ed4c8d1ca2035460ba8d0c72632dfb12a` |
| `field-flow/field-flow-rust/config/README.zh-CN.md` | `05ded91a7aecc2e806276b52f747b9ee84ae36431716387130d598039744a392` |
| `field-flow/field-flow-rust/config/basic02.yaml` | `40354dce81d896595290f03ef8e665f5ae561b2e4b38e92bbd126c8f8e4df777` |
| `field-flow/field-flow-rust/config/basic03.yaml` | `7d461581751f452283b209c558b52d858d8e4bded75edefcba36af90ba35c31c` |
| `field-flow/field-flow-rust/examples/README.md` | `003e6c33ecb11a4911dc69e6dd728d12a75c267c3ee6c09cb0b5f665f38ec209` |
| `field-flow/field-flow-rust/examples/README.zh-CN.md` | `74352f57b483d289e11d84e326b443da4b5cb81f4f90bdc22ac1eea8854c2df1` |
| `field-flow/field-flow-rust/src/app/get_value_guard_int.rs` | `736a0d4d65a49cc991d9d9ce93a98c7eefeca85f139b4dece36ef4c24851baa1` |
| `field-flow/field-flow-rust/src/app/mod.rs` | `b29c08e169f0e450b342b3cba556fda17ba6696f1cb669041b192310da230472` |
| `field-flow/field-flow-rust/src/app/plc_guard_get_int.rs` | `72643af5ebe871b3cfcd8485759a949647da10540a67276e98a370d8d8510147` |
| `field-flow/field-flow-rust/src/config.rs` | `ddde5ed1853c9fdffad02f3cdf7a422888e3530d9dc051dbbc2dac3fb5aba39a` |
| `field-flow/field-flow-rust/src/runtime.rs` | `fe8ed233b8aea47716682212a37d6755b91780611344529923657c3c97a600d6` |
| `field-flow/field-flow-rust/tests/basic_examples.rs` | `da61a65fe0f4548ff22e27528cb992e1e85cbee055c33720c620eb8532417800` |

清单/锁原字节：Rust Cargo.toml=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`、Cargo.lock=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6`；Python pyproject.toml=`5d1716bdf7cbc0dbb8995bdd0eff9afcda7315b50654341d23400cafdd2783fc`、uv.lock=`0a1667a278e7688f7dd0d0347946bc2771bcbe5747fdb2d8f12af6b4f29ca2c5`、.python-version=`49a506dd32096b010d75205acf3430c9ae6c40351888129499e5a5e487126c93`。

### 资源清单、保留原因与清理触发

本任务自有根`/private/tmp/ff-005-r1-dev-ovnx25ib`：正式/独立/教学的product、fixture、rust-product、rust-test、teaching-product Cargo target；独立rust/python及rust-teaching/python-teaching源码副本（Python各自.venv）、uv-cache；全部evidence-*（含首败/中间稿/最终场景状态与报告）、manual-*及A/B脚本；commands原输出、baseline/scope/manifest/source-copy/protected/resource/expiry摘要与只作文本/执行编排的辅助脚本。manual根的product/fixture软链接只指向同一自有根内的已建target。无新增Git分支/worktree，没有安装Agent辅助包、解释器/SDK或全局工具。

保留供fresh QA、Owner终验和归属核对；关键结论/74+16场景counts、PID、内存、退出、ACK与候选hash已写本tasks，不仅依赖临时路径。最终验收后由active coordinator确认无运行/后续任务/证据依赖再回收自有资源；Development此阶段不删除旧资源/原库/日志。

末次资源检查：最终74场景及16人工场景共324个去重原PID全部精确检查不存在；lsof六口exit1、stdout/stderr空；Rust31102/31103/31880按不设REUSEADDR、Python32102/32103/32880按原REUSEADDR规则同时bind/listen/close成功。自有根可执行入口的ps残余为空。该检查不是对空PID或权限错误的推测，完整原结果final-resources.json。

旧回归采用硬编码旧前缀，本轮实际新建且保留的154件`/private/tmp`目录如下；它们是FF-005运行资源，不是新造旧任务证据。执行前已有目录均保留不动：

```text
/private/tmp/ff-001-r1-r3-rust-ack-rejections-1793763911325-43219-0
/private/tmp/ff-001-r1-r3-rust-ack-rejections-1793764105773-51817-0
/private/tmp/ff-001-r1-r3-rust-ack-rejections-1793764245733-55517-0
/private/tmp/ff-001-r1-r3-rust-audit-queued-1793764387574-58163-54
/private/tmp/ff-001-r1-r3-rust-bad-ref-read-1793764367376-57413-228
/private/tmp/ff-001-r1-r3-rust-bad-ref-write-1793764367518-57413-233
/private/tmp/ff-001-r1-r3-rust-block-boundary-1793764382173-58163-25
/private/tmp/ff-001-r1-r3-rust-capacity-1793764387121-58163-40
/private/tmp/ff-001-r1-r3-rust-child-death-1793764369417-57951-0
/private/tmp/ff-001-r1-r3-rust-concurrent-1793764342161-57413-15
/private/tmp/ff-001-r1-r3-rust-confirmed-then-sink-1793764340566-57409-0
/private/tmp/ff-001-r1-r3-rust-disconnect-1793764365707-57413-193
/private/tmp/ff-001-r1-r3-rust-dry-1793764350607-57413-161
/private/tmp/ff-001-r1-r3-rust-gate-normal-1793764367214-57413-222
/private/tmp/ff-001-r1-r3-rust-immutable-1793764382312-58163-30
/private/tmp/ff-001-r1-r3-rust-int-1793764341415-57413-0
/private/tmp/ff-001-r1-r3-rust-int-readback-1793764381371-58163-0
/private/tmp/ff-001-r1-r3-rust-int-readback-1793764381528-58163-5
/private/tmp/ff-001-r1-r3-rust-int-readback-1793764381690-58163-10
/private/tmp/ff-001-r1-r3-rust-int-readback-1793764381857-58163-15
/private/tmp/ff-001-r1-r3-rust-int-readback-1793764382017-58163-20
/private/tmp/ff-001-r1-r3-rust-lost-ack-1793764350758-57413-166
/private/tmp/ff-001-r1-r3-rust-matched-ack-preflight-1793764367207-57413-221
/private/tmp/ff-001-r1-r3-rust-parent-death-1793764375098-57951-2
/private/tmp/ff-001-r1-r3-rust-queued-expiry-1793764382454-58163-34
/private/tmp/ff-001-r1-r3-rust-queued-stop-1793764366845-57413-215
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-precall-1793764395205-58302-30
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-queued-1793764394354-58302-22
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-state-1793764394359-58302-23
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-state-1793764395213-58302-31
/private/tmp/ff-001-r1-r3-rust-r4-rework-fifo-1793764389831-58302-0
/private/tmp/ff-001-r1-r3-rust-r4-rework-fifo-state-1793764389838-58302-1
/private/tmp/ff-001-r1-r3-rust-r4-rework-minimum-io-1793764392392-58302-9
/private/tmp/ff-001-r1-r3-rust-r4-rework-started-1793764392638-58302-15
/private/tmp/ff-001-r1-r3-rust-r4-rework-started-state-1793764392644-58302-16
/private/tmp/ff-001-r1-r3-rust-ref-epoch-1793764387805-58163-61
/private/tmp/ff-001-r1-r3-rust-reject-1793764342012-57413-11
/private/tmp/ff-001-r1-r3-rust-reject-bits-1793763913250-43219-46
/private/tmp/ff-001-r1-r3-rust-reject-bits-1793764107962-51817-46
/private/tmp/ff-001-r1-r3-rust-reject-bits-1793764247599-55517-46
/private/tmp/ff-001-r1-r3-rust-reject-count-1793763912623-43219-26
/private/tmp/ff-001-r1-r3-rust-reject-count-1793763920544-43219-133
/private/tmp/ff-001-r1-r3-rust-reject-count-1793764107192-51817-26
/private/tmp/ff-001-r1-r3-rust-reject-count-1793764115309-51817-133
/private/tmp/ff-001-r1-r3-rust-reject-count-1793764247003-55517-26
/private/tmp/ff-001-r1-r3-rust-reject-count-1793764254554-55517-133
/private/tmp/ff-001-r1-r3-rust-reject-data_length-1793763912934-43219-36
/private/tmp/ff-001-r1-r3-rust-reject-data_length-1793764107638-51817-36
/private/tmp/ff-001-r1-r3-rust-reject-data_length-1793764247296-55517-36
/private/tmp/ff-001-r1-r3-rust-reject-empty-1793763913718-43219-61
/private/tmp/ff-001-r1-r3-rust-reject-empty-1793764108539-51817-61
/private/tmp/ff-001-r1-r3-rust-reject-empty-1793764248024-55517-61
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793763913872-43219-66
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793763920711-43219-138
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793764108741-51817-66
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793764115459-51817-138
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793764248163-55517-66
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793764254702-55517-138
/private/tmp/ff-001-r1-r3-rust-reject-follow_correct-1793763920873-43219-143
/private/tmp/ff-001-r1-r3-rust-reject-follow_correct-1793764115614-51817-143
/private/tmp/ff-001-r1-r3-rust-reject-follow_correct-1793764254850-55517-143
/private/tmp/ff-001-r1-r3-rust-reject-function-1793763912466-43219-21
/private/tmp/ff-001-r1-r3-rust-reject-function-1793763920379-43219-128
/private/tmp/ff-001-r1-r3-rust-reject-function-1793764107033-51817-21
/private/tmp/ff-001-r1-r3-rust-reject-function-1793764115147-51817-128
/private/tmp/ff-001-r1-r3-rust-reject-function-1793764246845-55517-21
/private/tmp/ff-001-r1-r3-rust-reject-function-1793764254406-55517-128
/private/tmp/ff-001-r1-r3-rust-reject-global0-1793763919870-43219-113
/private/tmp/ff-001-r1-r3-rust-reject-global0-1793764114684-51817-113
/private/tmp/ff-001-r1-r3-rust-reject-global0-1793764253979-55517-113
/private/tmp/ff-001-r1-r3-rust-reject-global1-1793763920046-43219-118
/private/tmp/ff-001-r1-r3-rust-reject-global1-1793764114838-51817-118
/private/tmp/ff-001-r1-r3-rust-reject-global1-1793764254121-55517-118
/private/tmp/ff-001-r1-r3-rust-reject-id-1793763911325-43219-1
/private/tmp/ff-001-r1-r3-rust-reject-id-1793764105773-51817-1
/private/tmp/ff-001-r1-r3-rust-reject-id-1793764245734-55517-1
/private/tmp/ff-001-r1-r3-rust-reject-item-1793763920211-43219-123
/private/tmp/ff-001-r1-r3-rust-reject-item-1793764114992-51817-123
/private/tmp/ff-001-r1-r3-rust-reject-item-1793764254263-55517-123
/private/tmp/ff-001-r1-r3-rust-reject-oldref-1793763919211-43219-91
/private/tmp/ff-001-r1-r3-rust-reject-oldref-1793764114082-51817-91
/private/tmp/ff-001-r1-r3-rust-reject-oldref-1793764253412-55517-91
/private/tmp/ff-001-r1-r3-rust-reject-otherref-1793763919374-43219-97
/private/tmp/ff-001-r1-r3-rust-reject-otherref-1793764114230-51817-97
/private/tmp/ff-001-r1-r3-rust-reject-otherref-1793764253549-55517-97
/private/tmp/ff-001-r1-r3-rust-reject-param_length-1793763912776-43219-31
/private/tmp/ff-001-r1-r3-rust-reject-param_length-1793764107352-51817-31
/private/tmp/ff-001-r1-r3-rust-reject-param_length-1793764247150-55517-31
/private/tmp/ff-001-r1-r3-rust-reject-payload4096-1793763914028-43219-71
/private/tmp/ff-001-r1-r3-rust-reject-payload4096-1793764108928-51817-71
/private/tmp/ff-001-r1-r3-rust-reject-payload4096-1793764248301-55517-71
/private/tmp/ff-001-r1-r3-rust-reject-payload4097-1793763918731-43219-76
/private/tmp/ff-001-r1-r3-rust-reject-payload4097-1793764113632-51817-76
/private/tmp/ff-001-r1-r3-rust-reject-payload4097-1793764252969-55517-76
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793763918894-43219-81
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793763919543-43219-103
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793764113782-51817-81
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793764114381-51817-103
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793764253123-55517-81
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793764253693-55517-103
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793763919051-43219-86
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793763919706-43219-108
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793764113931-51817-86
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793764114530-51817-108
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793764253274-55517-86
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793764253835-55517-108
/private/tmp/ff-001-r1-r3-rust-reject-reserved0-1793763912162-43219-11
/private/tmp/ff-001-r1-r3-rust-reject-reserved0-1793764106648-51817-11
/private/tmp/ff-001-r1-r3-rust-reject-reserved0-1793764246540-55517-11
/private/tmp/ff-001-r1-r3-rust-reject-reserved1-1793763912317-43219-16
/private/tmp/ff-001-r1-r3-rust-reject-reserved1-1793764106857-51817-16
/private/tmp/ff-001-r1-r3-rust-reject-reserved1-1793764246690-55517-16
/private/tmp/ff-001-r1-r3-rust-reject-rosctr-1793763912008-43219-6
/private/tmp/ff-001-r1-r3-rust-reject-rosctr-1793764106465-51817-6
/private/tmp/ff-001-r1-r3-rust-reject-rosctr-1793764246395-55517-6
/private/tmp/ff-001-r1-r3-rust-reject-short_data-1793763913561-43219-56
/private/tmp/ff-001-r1-r3-rust-reject-short_data-1793764108320-51817-56
/private/tmp/ff-001-r1-r3-rust-reject-short_data-1793764247885-55517-56
/private/tmp/ff-001-r1-r3-rust-reject-short_header-1793763913404-43219-51
/private/tmp/ff-001-r1-r3-rust-reject-short_header-1793764108139-51817-51
/private/tmp/ff-001-r1-r3-rust-reject-short_header-1793764247744-55517-51
/private/tmp/ff-001-r1-r3-rust-reject-transport-1793763913090-43219-41
/private/tmp/ff-001-r1-r3-rust-reject-transport-1793764107798-51817-41
/private/tmp/ff-001-r1-r3-rust-reject-transport-1793764247449-55517-41
/private/tmp/ff-001-r1-r3-rust-server-absent-1793764388182-58163-66
/private/tmp/ff-001-r1-r3-rust-short-read-1793764367875-57413-240
/private/tmp/ff-001-r1-r3-rust-short-write-1793764368021-57413-245
/private/tmp/ff-001-r1-r3-rust-silent-cotp-1793764365181-57413-189
/private/tmp/ff-001-r1-r3-rust-slow-1793764360373-57413-179
/private/tmp/ff-001-r1-r3-rust-slow-http-1793764342409-57413-79
/private/tmp/ff-001-r1-r3-rust-split-1793764355710-57413-174
/private/tmp/ff-001-r1-r3-rust-stale-1793764365041-57413-184
/private/tmp/ff-001-r1-r3-rust-stale-reference-probe-1793764368485-57413-252
/private/tmp/ff-001-r1-r3-rust-t1-1793764366215-57413-199
/private/tmp/ff-001-r1-r3-rust-t2-1793764366381-57413-204
/private/tmp/ff-001-r1-r3-rust-t3-fail-1793764366560-57413-208
/private/tmp/ff-001-r1-r4-python-absence-alias-zw5py2zn
/private/tmp/ff-001-r1-r4-python-ack-matrix-rie4v5yi
/private/tmp/ff-001-r1-r4-python-audit-order-7oi6vyhm
/private/tmp/ff-001-r1-r4-python-audit-stop-q3efdd0_
/private/tmp/ff-001-r1-r4-python-cli-o0dal9bb
/private/tmp/ff-001-r1-r4-python-clock-conflict-v0d_xxed
/private/tmp/ff-001-r1-r4-python-concurrency-1n7v2qkd
/private/tmp/ff-001-r1-r4-python-connect-queue-31na3ykb
/private/tmp/ff-001-r1-r4-python-deadline-max_short-ydz7m4or
/private/tmp/ff-001-r1-r4-python-deadline-slow-gwyf9ikf
/private/tmp/ff-001-r1-r4-python-deadline-split-bu4au7qp
/private/tmp/ff-001-r1-r4-python-deadline-stale-rtt7uu3z
/private/tmp/ff-001-r1-r4-python-gate-845h4_b3
/private/tmp/ff-001-r1-r4-python-process-death-2r10fy6m
/private/tmp/ff-001-r1-r4-python-recovery-tc36v5en
/private/tmp/ff-001-r1-r4-python-ref-maintenance-ze0n1k7n
/private/tmp/ff-001-r1-r4-python-state-fxe2z50v
/private/tmp/ff-001-r1-r4-python-values-pdz7ub9_
```

另两个Rust CLI回归按`std::env::temp_dir()`创建的本轮精确路径（不是/private/tmp；未回收历史同前缀目录）：

```text
/private/var/folders/k5/gb101k5j2nddcgfgrtsn0p300000gn/T/ff-001-r1-r3-cli-1793764231020-55065-0
/private/var/folders/k5/gb101k5j2nddcgfgrtsn0p300000gn/T/ff-001-r1-r3-cli-1793764340107-57400-0
```

### 限制、风险与 developer_handoff

没有未解决的A实现阻碍；独立Verification尚未执行，Development自检不替代QA。实际本机能力仅macOS arm64；Windows/Linux、真实PLC/第三方HTTP/DS/Backend/真实DB、现场工艺、托管/容量/长稳、安装/发布/部署、历史时区整改及跨状态迁移均未做/未授权。现有JSONL/SQLite日历UTC差异按spec保留，新app没有日历时间producer。unknown仍需原事实核对，不新增自动处置；条件读写仍非原子互锁。B/C和进阶/C#保持后续能力及独立批准gate。

Development -> active coordinator / fresh-context Verification：FF-005 r1仅A，正式working tree及本节37件实现hash、批准spec、完整tasks、baseline/original、780件保护哈希与原输出构成精确handoff输入。请实际调用`verification`、`fork_turns="none"`，独立核对当前正式候选与完整bundle，创建其checklist/verdict；主协调只按权威文档机械同步12导航。Human Owner最终验收仍pending。Development不写spec/checklist、不提供QA verdict或平台ACL/强制路由声明。

最后隔离expires验证：Rust四场景首个input_stale时age分别2042/2032/2015/2019ms，Python四场景2224/2224/2152/2148ms；均TTL1000ms、now≥expires且age<10000ms。`expiry-isolation.json`保存逐scene对应；最终37+37矩阵均exit0（Rust85.53s、Python102.45s）。额外自有路径`/private/tmp/ff005-dev-root`只存本任务资源根文本指针，与自有根一起在Owner gate后核对回收。

主协调交接前只读复核要求补齐shell标识：Rust/Python examples中英四文件已明确交互命令面向本轮macOS arm64 / zsh，独立复制替换真实工程绝对路径；不改任何可执行代码块或平台资格。对应37文件manifest及副本hash已刷新，无业务场景重跑需求。

最终封存：主协调12件PLAN/catalog已机械同步developer_handoff且声明冻结到QA结束；Development仅同步两个原版/教学副本内对应的8件导航文本，不写正式导航。Rust57件、Python62件独立工程文件与最终正式树逐字节一致，source-copy-hashes.json SHA256=`10b7929744f97965e80c9a787b0d9e3265ff055fe8f40e545508d4254ba9640a`，差异为空；教学副本相对正式树只有Rust3件既有接线+2新增、Python2件既有接线+2新增的刻意teaching01差异。37实现manifest稳定`213cb81ca44cd3e0c1f04774e071f00fa30361ebe41aa8aa69e850b6bfc1e1ab`；最终静态检查覆盖补shell说明后的四README，代码块未变。

## r1 rework1 起步与实际修复计划

已完整阅读QA1 checklist及当前实现/原输出，spec保持原批准SHA，checklist不写。保留DEV1与QA1全部资源。返工自有根：`/private/tmp/ff-005-r1-dev-ovnx25ib/rework1-39nzt0qd`；source-before为写入前快照，baseline.json记录QA1清单hash及当前文件hash，resource-before.json盘点旧前缀路径。

1. 六处注册事实及四份examples ACK表述最小修正；用户命令块不改。
2. Python新test文件加入JSON结构化强收/子进程退出检查和格式回归，将unknown写阶段改为原fixture短ACK（short_data），不改fixture/core/TTL。
3. 在全新独立Python副本/自身锁定环境重跑完整pytest及37CLI场景，结构化复核无forced/driver正常退出、unknown及计数；静态与源码一致性封存后developer_handoff。Rust业务源码/tests/YAML不改，QA1独立21/37与20个人工场景证据按等价范围引用。

### rework1 首阶段真实结果

- 六处注册事实已改为真实三个kind，basic01复用demo01、teaching01仅教程副本、未知kind拒绝/非自动发现保留。四份examples将harness向量准确改为无有效ACK（截断），并保留旧hold_ack完全扣留ACK会触发强收的失败边界；所有用户可执行命令块未改。
- 新test内JSON结构化检查不依赖空白格式，直接拒绝event=forced_driver_stop或布尔had_forced_driver_stop=true；另外拒绝driver_process_reaped非0退出，并要求真实driver回收记录。新增一个必要回归函数覆盖紧凑/带空格true、event、-15以及false/无关message不误判；原三个CLI case测试函数保留。
- 新副本cwd=`/private/tmp/ff-005-r1-dev-ovnx25ib/rework1-39nzt0qd/python`，从最终正式源独立复制，无env/target/cache/状态；自有.venv。`uv sync --locked --offline --python 3.11 --no-python-downloads --cache-dir /private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache` exit0，只复用原自有锁定公开包cache，不共享venv。
- `uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir /private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache pytest -q -s tests/test_basic_examples.py -k forced_driver_stop_json_formats` exit0，1 passed/3 deselected（0.28s）；完整套件新数量将在真实运行后记录。
- 同环境运行自有`focus_unknown.py`：新JSON检查明确拒绝DEV final-v3和QA1两个原误判日志；旧报告不改。新unknown用原fixture short_data，仅GET延迟窗口后截断写ACK，首读正常。正式CLI/正式basic02.yaml真实运行：unknown1、GET1/ReadVar11/WriteVar1，目标002a+14×A5；产品预期exit1，fixture0，两代driver均真实exit0；首driver result=fault_cleanup（原协议错误退休分类），替代driver result=normal，没有forced事件或true标志，精确PID均回收且三口rebind。focused报告不替代即将运行的完整pytest/37场景。
- 一次纯文档精确匹配脚本对父中文指南误猜旧分号文字触发assert并停止，已改为当前原句唯一匹配；之前成功改动仅属获批说明面，未覆盖其他修改。保留该执行事实，不把辅助编辑失败计成产品失败。

## r1 rework1 Developer handoff（当前有效 DEV 记录）

QA1保持`qa_failed`；本轮是同一获批r1 A内的有限返工，F-QA1-001/F-QA1-002已完成Development修复与自检，是否独立关闭由新fresh-context QA2决定。没有修改spec/checklist/core/旧fixture/锁。DEV1与QA1原报告、hold_ack强收与误判历史全部保留；顶部纠正声明继续有效。

### 实际命令、数量与结果

下表 `W=/private/tmp/ff-005-r1-dev-ovnx25ib/rework1-39nzt0qd`，`C=/private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache`。项目命令均在`W/python`，已有CPython3.11.12/uv0.7.8，macOS15.7.7 arm64；个人文本辅助Python不作为项目行为验证。无新依赖/解释器/SDK/系统工具安装。

| 实际命令 / cwd | 真实结果与证据 |
| --- | --- |
| `uv sync --locked --offline --python 3.11 --no-python-downloads --cache-dir C` / W/python | exit0；新副本自身.venv，复用本任务原声明公开包cache；commands/python-sync.log。 |
| `uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir C python -m compileall -q src tests` / W/python | exit0；commands/python-compile.log。 |
| `uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir C pytest -q -s tests/test_basic_examples.py -k forced_driver_stop_json_formats` | exit0，1 passed/3 deselected，0.28s；commands/json-regression.log。一个必要回归函数内覆盖两种JSON空白格式、真实event/布尔true/退出-15拒绝与false/无关message不误判，不把内部向量当pytest项数。 |
| `uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir C python W/focus_unknown.py` | exit0，原DEV/QA两个误判日志均被新结构化检查器拒绝；再实际运行一个截断ACK unknown CLI场景，6.386s，非pytest项；commands/focus-unknown.log、legacy-json-rejection.json、focus-evidence。 |
| `FF005_EVIDENCE_ROOT=W/evidence-python uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir C pytest -q -s` | **exit0，26 passed in 133.80s**，包括22既有+3CLI case函数+1新增JSON回归。三个CLI函数内部37独立场景全部实际运行，不是37 pytest项；commands/python-full.log。 |
| `python3 W/audit_matrix.py` / 正式树 | exit0，独立逐JSON解析37份产品日志/报告，核对forced事件/布尔标志/driver退出、计数、INT/邻接、过期与fixture join；matrix-audit.json。 |
| `python3 W/static_check.py`、`git diff --check -- field-flow` / 正式树 | exit0；11件实现差异、780保护hash/QA1 checklist保持，局部265链接无缺失，说明中全部可执行块与QA1候选逐字节相同。没有只靠链接检查猜文案正确；六处能力声明另逐字核对三kind/复用/教学边界。 |
| `python3 W/seal_resources.py` / 正式树 | exit0；247个本轮确切PID全部不存在，六口lsof1/空stdout/stderr且实际同时rebind，无W可执行入口残余；resources-final.json。 |

Rust源码/tests/配置与QA1候选逐字节不变（37实现manifest差异仅下列11件）；沿用QA1独立Rust21项/37CLI的限定行为证据，不机械重跑。六份注册事实与配置/显式dispatch一致；原kind未知/teaching01拒绝边界仍由QA1真实CLI22条支持。所有USER_GUIDE/examples可执行代码块与QA1候选完全相同，本轮只改说明段落，沿用QA1独立20个人工/教学场景（含正式树basic02）的命令证据。以上只引用精确未变表面的既有独立证据，不把QA1整体qa_failed改成通过，也不作为新QA2 verdict。

### 新37场景的持久关键结果

逐行JSON确认：所有场景的`stop_joined.had_forced_driver_stop`均为真实布尔false，无event=forced_driver_stop；所有driver_process_reaped.exit_code为0，且每个driver均有对应threads_joined/remaining_threads=[]。普通34场景产品exit0；read_error两例及unknown一例原故障exit1，不能称正常业务/正常stop；fixture均正常0/线程join与三口rebind。

矩阵场景总93.760154秒、最大5.965717秒，保持≤600秒/每scene≤45秒。一次生成原命令后不刷新身份/issued/expires；expired仍是TTL1000ms、issued=now-2000ms、expires=now-1000ms、首错age<10000ms的纯expires向量。

| Python scene | GET / ReadVar / WriteVar（减准备） | command counts | 首INT + 14邻接A5 | 产品/fixture exit | 精确已回收PID | 秒 |
| --- | --- | --- | --- | --- | --- | --- |
| basic01-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 16863,16864,16866 | 1.544 |
| basic01-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 16764,16765,16766 | 5.592 |
| basic01-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 16965,16981,16995 | 1.582 |
| basic01-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 16897,16898,16899 | 5.645 |
| basic02-dry_run-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17170,17171,17172 | 1.607 |
| basic02-dry_run-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17100,17101,17102 | 1.580 |
| basic02-dry_run-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17134,17135,17136 | 1.619 |
| basic02-dry_run-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 17175,17176,17177,17206 | 1.078 |
| basic02-dry_run-value-42--1 | 11/11/0 | `{"simulated":1}` | `ffff` +14×A5 | 0/0 | 17209,17210,17211 | 5.630 |
| basic02-dry_run-value-42-0 | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 17611,17612,17613 | 1.621 |
| basic02-dry_run-value-42-None | 11/11/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 17009,17010,17011 | 5.649 |
| basic02-execute-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17780,17781,17782 | 1.622 |
| basic02-execute-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17710,17711,17712 | 1.582 |
| basic02-execute-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 17743,17745,17746 | 1.588 |
| basic02-execute-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 17819,17822,17823,17824 | 1.106 |
| basic02-execute-unknown-42-None | 1/11/1 | `{"unknown":1}` | `002a` +14×A5 | 1/0 | 17957,17958,17959,17960 | 5.966 |
| basic02-execute-value-42--1 | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 17827,17828,17829 | 5.628 |
| basic02-execute-value-42-0 | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 17919,17921,17922 | 1.623 |
| basic02-execute-value-42-None | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 17619,17620,17649 | 5.625 |
| basic03-dry_run-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18336,18337,18338 | 1.531 |
| basic03-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18265,18266,18267 | 1.530 |
| basic03-dry_run-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18301,18302,18303 | 1.542 |
| basic03-dry_run-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18053,18054,18055 | 1.527 |
| basic03-dry_run-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18060,18061,18062 | 1.530 |
| basic03-dry_run-value-1-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 18094,18095,18096 | 1.530 |
| basic03-dry_run-value-100-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 18226,18227,18228 | 1.532 |
| basic03-dry_run-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18231,18232,18233 | 1.526 |
| basic03-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 18130,18131,18132 | 5.577 |
| basic03-execute-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18627,18628,18657 | 1.559 |
| basic03-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18584,18585,18586 | 1.538 |
| basic03-execute-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18619,18620,18621 | 1.577 |
| basic03-execute-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18341,18342,18343 | 1.525 |
| basic03-execute-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18377,18378,18379 | 1.523 |
| basic03-execute-value-1-None | 3/0/1 | `{"confirmed":1}` | `0001` +14×A5 | 0/0 | 18413,18414,18415 | 1.591 |
| basic03-execute-value-100-None | 3/0/1 | `{"confirmed":1}` | `0064` +14×A5 | 0/0 | 18515,18516,18517 | 1.594 |
| basic03-execute-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 18549,18550,18551 | 1.525 |
| basic03-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 18449,18451,18452 | 5.616 |

本轮unknown是**无有效ACK（截断）**，不是完整ACK整包丢失；原fixture short_data只在初次正常读后、GET的延迟窗口内设置。原写ACK帧的最后一字节被截断并按原fixture更新TPKT长度；native内存已写42，原parser拒绝无效ACK，unknown保留。后续≥10轮读42，不再GET/写；输入/原库保留，不升级confirmed/不自动处置。首driver按原协议错误退休记录result=fault_cleanup但exit0且threads_joined，替代driver退出result=normal/exit0；这与旧hold_ack的SIGTERM/-15/forced=true不同，预期产品故障exit1仍如实保留。

```json
{"input":{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"ff005-command","value":42,"issued_at_ms":1793767238880,"expires_at_ms":1793767268880},"counts":{"unknown":1},"GET":1,"ReadVar":11,"WriteVar":1,"memory_hex":"002aa5a5a5a5a5a5a5a5a5a5a5a5a5a5","product_exit":1,"driver_reaps":[{"pid":17959,"exit_code":0,"result":"fault_cleanup"},{"pid":17960,"exit_code":0,"result":"normal"}],"forced":[],"original_response_hex":"0300001602f0803203000000030002000100000501ff","sent_response_hex":"0300001502f0803203000000030002000100000501"}
```

### 相对QA1的有限文件差异与新候选

本轮只变更以下11件已获批实现路径和本tasks；主协调另机械更新12导航。四app、两工程config/runtime、Rust新test/所有YAML、domain/Execution/owner/driver/HTTP/state/audit、旧tests/fixture、manifest/锁均未改。QA1 checklist原SHA `ce2bb7418d447b2b13c334aed4795e40f27eddf550a3b24a1d31d777b77c4a0d`不变，另只读副本W/qa1-checklist.md供后续追溯；批准spec与FF-004 r1保持原SHA。最终独立副本哈希在导航同步后封存。

| QA1 -> rework1 变化实现文件 | 新SHA256 |
| --- | --- |
| `field-flow/USER_GUIDE.md` | `1d6c3a682f5201a68ba98d974a019e3e95025d6e1932b29ca3ff7a41c5cfa3b2` |
| `field-flow/USER_GUIDE.zh-CN.md` | `0163d42e9d6bffa292298f7a27b7e1b644f48707dc5c0b1425fe740dd770963a` |
| `field-flow/field-flow-python/README.md` | `9ef083388c9fba9b63aa76cce5cd86df127eb5e8c82534da1384d73cefbda345` |
| `field-flow/field-flow-python/README.zh-CN.md` | `cbe06eea822fbc2c66ea068f7b4f52a13e071c64e287e773029f9f3407641636` |
| `field-flow/field-flow-python/examples/README.md` | `aff027df2e5b9bb61d798c7c4aacef3b1aec45bcce6c0cc858b23b61ab147408` |
| `field-flow/field-flow-python/examples/README.zh-CN.md` | `036097681db7da84eeca90e92756bac4ad3a0c00b530001fbb6450fd5c210c33` |
| `field-flow/field-flow-python/tests/test_basic_examples.py` | `7406efbaa8b8b74a0b15820daed3d7d86001ab362770b0557f3f43e41c9af203` |
| `field-flow/field-flow-rust/README.md` | `9641edb212a055617d5630fe3544e69b1002e0b95b0f91b0f4b63c912881735a` |
| `field-flow/field-flow-rust/README.zh-CN.md` | `325544936cb4333251bcf97a23677f321ab7e3c442cbc9e3dc142f310a60698c` |
| `field-flow/field-flow-rust/examples/README.md` | `94e8d077e2e77b030389cd142c5f369112a86b5eb6880a855df9a3b2d643e4d7` |
| `field-flow/field-flow-rust/examples/README.zh-CN.md` | `ff09041cf82809014e8866ed3e03c91c15968c5f256c75a99b6d2970bf08d5d3` |

完整37件实现manifest在`W/implementation-manifest.json`，SHA256=`58516410099596398e8ae926b5582b91b82a0ae59ce811b32418c033b64ec268`；相对QA1未列路径保持原实现hash。此manifest不含12件机械导航或角色事实；完整候选与tasks最终hash在handoff消息单列，避免自引用。

### 本轮资源与当前限制

W拥有source-before（返工起点冻结输入）、新Rust/Python单工程副本（Python自有.venv）、commands、focus/evidence-python新synthetic库/原日志/报告、结构化原误判拒绝/矩阵/静态/资源审计与manifest脚本/输出。公开锁定包cache仍由原DEV根持有，未共享虚拟环境。未更动DEV1或QA1副本/target/原报告，没有分支/worktree/Git refs、通知或外部发送。所有关键新counts/内存/输入/ACK/driver实际退出已持久写本tasks，W保留供新QA、Owner核对，终验后由active coordinator按占用/归属/证据依赖回收；不删除此前已有目录或旧状态。

完整旧pytest回归使用原硬编码前缀，故意故障场景仍保持其原测试预期，不能把那些预期强收与新37场景的零forced混合宣称。下列18件确切路径是本轮full pytest创建的新资源，执行前已有同前缀目录均保留不动：

```text
/private/tmp/ff-001-r1-r4-python-absence-alias-oxwvfzzl
/private/tmp/ff-001-r1-r4-python-ack-matrix-ygetprpz
/private/tmp/ff-001-r1-r4-python-audit-order-26hdd3da
/private/tmp/ff-001-r1-r4-python-audit-stop-obo33ytm
/private/tmp/ff-001-r1-r4-python-cli-wycfqf__
/private/tmp/ff-001-r1-r4-python-clock-conflict-sdw4bzcc
/private/tmp/ff-001-r1-r4-python-concurrency-b0vv0k16
/private/tmp/ff-001-r1-r4-python-connect-queue-03xe5s0q
/private/tmp/ff-001-r1-r4-python-deadline-max_short-gc919nnw
/private/tmp/ff-001-r1-r4-python-deadline-slow-6dpdnl81
/private/tmp/ff-001-r1-r4-python-deadline-split-mwo6x9r5
/private/tmp/ff-001-r1-r4-python-deadline-stale-zf7s50w4
/private/tmp/ff-001-r1-r4-python-gate-dgv1jdlo
/private/tmp/ff-001-r1-r4-python-process-death-oqjks70k
/private/tmp/ff-001-r1-r4-python-recovery-2t587kt7
/private/tmp/ff-001-r1-r4-python-ref-maintenance-9f_yxosn
/private/tmp/ff-001-r1-r4-python-state-5p4vazgz
/private/tmp/ff-001-r1-r4-python-values-abpt7sss
```

返工DEV范围自检已具备交接条件，是否关闭两项QA1 failure由新的fresh Verification决定。当前未发现需要突破allowlist的实现阻碍；Windows/Linux、真实PLC/第三方HTTP/DS/Backend/真实DB、历史UTC整改、托管/长稳/部署发布、B/C与Owner终验均仍未做/未授予。完整扣留ACK引发的旧强收限制保留，不通过文字放宽unknown/零重发/无forced要求。

**Development -> active coordinator / fresh Verification：** 请按本轮11件差异、最终37件候选manifest、正式树/独立副本、QA1 checklist/原证据与本新增记录，另启`verification`且`fork_turns="none"`完成QA2；主协调只依tasks机械同步12导航。Development不改spec/checklist、不授予QA verdict或Owner验收。

rework1最后封存：主协调12导航已机械同步developer_handoff并冻结到QA2结束；Development仅同步W两个新原版副本的8件导航。Rust57件/Python62件与当前正式树逐字节一致，差异空；`W/source-copy-hashes.json` SHA256=`e6c8e9115b61afac6f75caaf19aba76ada25e3e1251645412acb7e467f789df0`。DEV1/QA1原版及教学副本作为旧证据保持不变，不把本轮说明改动写回其历史快照。37实现manifest SHA256保持`58516410099596398e8ae926b5582b91b82a0ae59ce811b32418c033b64ec268`。新候选、当前tasks、QA1固定checklist与资源路径在最终handoff.json/消息单列；此后Development冻结写入，待新QA真实反馈。
