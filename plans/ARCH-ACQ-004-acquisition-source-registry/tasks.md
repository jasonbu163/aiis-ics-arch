Task ID: ARCH-ACQ-004
Revision: r4
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: QA2 所缺迁移前冻结队列的连续合成链路已补证；合同笔误已修正，交 fresh-context Verification；最终 DAA 指南与原生复验仍待处理。
Workflow Mode: STD

# r4 Development 当前事实

Human Owner 已批准 r4，正式 `spec.md` SHA-256 为 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`。后端、Web、迁移和根指南沿用原已批准 r3 的实现范围；最初实施时的 r3 规格 SHA-256 为 `a5e6c374b466ff62b188d848a3db7f6e0dbf1a90518e9560d82afeb01f81c2db`。临时候选为 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/source`，基于复制时交付树的源码及未跟踪文件；不含真实 `.env`、`.local`、数据库、Git 或原有构建产物。初始状态和 4471 文件摘要分别在同目录上一级 `delivery-tree-status.txt`、`candidate-baseline.json`。本角色未编辑 spec/checklist 或其他任务文件。

协调者报告获 Human Owner 授权后已正常停止正式 8000/5190，未碰数据库，并按原始/候选摘要将 34 个非 DAA 文件整合至正式树，6 个 DAA 共享文件未覆盖。Development 随后只读比对全部 34 个正式文件与候选 SHA，34/34 一致，6/6 DAA 文件仍等于并行任务版本；正式 r4 规格 SHA 与批准记录一致。根据 r4 AC02，本角色只补充 MySQL 测试中接管后不同实例的第二个 DB 及两 PLC 当前身份断言，并逐字同步候选与正式树；测试文件新 SHA 为 `3f5ad6a70dc95c4a89b9a41317eb61a595326b7c3aa30eeb524fbecd8519d3bf`。协调者随后完成正式树无库回归及构建，证据见下；源码整合不等于数据库迁移或实际环境采用。

候选完成后端 PLC 单行登记、三个标识准入、按登记 PLC 的事实读取、管理 API/Web、r3 OpenAPI 和非 DAA 说明的第一轮实现。历史六表模型与当前活跃 metadata 分离，原历史迁移原字节保留；后继迁移受目标、时间、前驱和空登记确认约束，并在清理旧表前核对登记和事实表结构、全部行摘要及水位。MySQL DDL 非事务，故障只能保全现场后按说明恢复或前向修复。旧 JSON 用冻结 r2 工具在迁移前导入，当前 r3 CLI 拒绝旧导入导出命令。上述为上轮候选记录，当时尚未经 MySQL 验证；本轮合成验证见下。

## r4 迁移前冻结队列的连续链路补证与 Development handoff

2026-11-13（Asia/Shanghai）。依获批准的 ARCH-ACQ-004 r4 及独立 QA2 对 R4-AC04 的缺口，在任务自有环境补做迁移前已冻结的 v2 样本经新候选上报。输入 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`、本次更新前 tasks SHA-256 `5e9d8351a407a9ae2d7140e706a7922afadd14e16a40d8d47b5d0ba213fc5250`、QA2 checklist SHA-256 `3f1f9f84bb041395098333e9db704b3ceef345dc24848434b27e5fc955a817dd`。这是 Development 实际补证，独立结论由 Verification 更新 checklist。

- **目标和授权。** Human Owner 明确授权专用 MySQL 隔离验证及 DEV app 用户临时访问此专用 guard schema 所需的 SELECT/INSERT/UPDATE/DELETE。专用 MySQL 8.4.6 的 `127.0.0.1:33404`、UUID `43b1c562-df4b-11f1-83c9-72f35d3e7827`、`+08:00`、`arch_acq004_r3_dev_guard` 均经连接核验；执行前该 schema 无表、视图、routine、trigger 和 revision。初始空库及前次 guard 测试证据此前已固定。专用进程的 socket guard 仅允许 33404 和 `127.0.0.1:38410`；静态断言拒绝 3307 等其他目标，并未向其连接。未连接 QA schema、真实库、历史、真实 profile 或 PLC。应用使用非 root DEV app，迁移/导入使用 DEV DDL 用户；密码及 JWT 仅在任务私有 0600 配置，未写本记录。
- **前驱和候选。** 旧 DAA 复制自先前保留的任务源码快照，`domain/sample_upload.rs` SHA-256 `72274a2ffa5bbdf49dfdc62a32680b4cdc432b5b7f4a6ced13e329b5fe2d498e`、`services/local_delivery.rs` `dc14cc9df50b27c0c30728b3e098271f262088d170a05b3f4e7a4f552fe589f2`、`infrastructure/local_store/sample_upload.rs` `038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c`，两份对应旧测试 SHA 分别为 `e41ef8893d353619963ac62adaf7fae71c90f32e0a3d663d1f4234768bffc4af` 和 `b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7`；五项均与 DAA-013 的实际实施前基线一致。新 DAA 对应三项为 `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b`、`212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2`、`82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951`。两代的 schema、runtime、profile contract、Cargo.toml 和 Cargo.lock 另逐项一致。私有副本中的两段 `cfg(test)` helper 只增加测试编排，产品逻辑未改；所用 97 个 DAA 源码/锁文件与各自复制源一致，正式新候选复核时仍 97/97 一致。
- **真实顺序。** 先以冻结 r2 后端执行完整 Alembic 到 `6a8c0e2b4d16`，用实际 r2 CLI 预览并确认导入合成 PLC `acq-frozen-plc`、实例 `acq-frozen-instance`、代次 `acq-frozen-generation` 和当时的 DB1/DB2 授权；只读 SQL 核对旧登记、空 history 后，在 `127.0.0.1:38410` 启动旧后端并核验实际 v2 路由。旧 DAA 使用自己的真实 `Stores`、模拟采样及 `next_sample_upload` 在任务私有新建的 sealed runtime4 SQLite 冻结 sampleId `908c2bbb-3a55-4c07-8ceb-07b72b26c72b`、DB1、原目标 `http://127.0.0.1:38410/api/v1/integration/plc-facts/samples`；持久行是 `prepared`、attempt 0、无回执，未在旧后端发送。样本原始正文 SHA-256 为 `e00e5abce79d73d4942b0a1f91f01f74782c89d567f9523e40f2101109b6ee63`，SQLite 按 DAA 原格式存为 `sha256:` 加此摘要。
- 旧后端停止后，再次核验该 **同一** SQLite 原字节、三标识、目标及 r2 库仍无 history；在同一 schema 上执行实际 `6a8c0e2b4d16 -> 7b9d1f3a5c7e`，核对单表登记仍是原三标识且迁移前后事实表为空。然后用新后端在同一 `38410` 重启，新 DAA 的真实 LocalEngine 打开原 profile 和同一 runtime.sqlite inode `84370819`，在显式确认当前来源后由真实 HTTP worker 上报。该原样本取得 `committed/created`，SQLite 为 `acknowledged`、attempt 1，唯一尝试目标与原目标相同，可靠回执的实例/sampleId 匹配；该行的全部正文、摘要和三标识与迁移前逐字节一致。专用 MySQL 对应 history 唯一行的三标识、sampleId、DB、`source_type=daa`、`content_hash` 均匹配原始正文摘要，查询时 `expires_at > NOW()`。旧合成周期还有 DB2 的未冻结待传样本，启动 worker 后亦上报；最终 SQLite 2 条 acknowledged、history 中该 PLC 的 DB1/DB2 各 1 行。跨迁移原字节的本条结论特指上述 DB1。
- **实际命令与失败。** 两代私有 DAA 分别运行 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --features rust-snap7-driver <helper> --no-run`，成功退出 0；随后固定生成的旧/新测试二进制分别运行 `acq004_freeze_before_registry_upgrade --nocapture --test-threads=1` 和 `acq004_deliver_preupgrade_frozen_bytes --nocapture --test-threads=1`，各退出 0、1 passed。`backend/.venv/bin/python -u .../run_frozen_upgrade.py` 中 r2 初始化、预览、导入及旧 helper 均退出 0；其后测试脚本误将带 `sha256:` 前缀的 SQLite 摘要与裸十六进制比较，退出 1 并停止旧后端，未迁移。仅修正私有对账脚本后，`backend/.venv/bin/python -u .../resume_frozen_upgrade.py` 保留并复用原冻结行，r4 迁移、新 helper 及 SQLite/MySQL 对账全部退出 0。旧/新服务 PID 14301/14792 均已停止，38410 无监听。最初离线编译因旧快照缺少 6 份 `.db` 后缀的 TIA 文本测试夹具而退出 101；从正式源码的测试夹具目录补入私有副本后通过，未改原快照。首次只读 MySQL 预检在默认沙箱被拒绝而退出 1，对已获授权的专用端口提权后退出 0。
- **精确候选与资源。** r2 迁移 SHA-256 `e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924`；r4 迁移 SHA-256 `3c31bf18eae8a7140252ce0453bd5cd101ea7df5fecfda71b429f4299d2e3d56`。两代 DAA 与后端逐文件源码摘要清单为 `/private/tmp/arch-acq004-r4-isolated-ebbghp32/frozen-upgrade/source-manifests.json`，SHA-256 `62eaa88a3eba0319c7f346ba097dcb657537dd4e016688e2e1a19acd8c2c730e`；旧原文快照 `old-frozen.json` SHA `ed5dc8814a68edd77530ef19276213755f44056d351ebd6ba9da0266d886c122`，成功对账摘要 `verified-evidence.json` SHA `87964777aeacae525c5d7841b335d7006199a918b17e3640fc3d44c48cdc1613`。旧/新 helper 二进制 SHA 分别为 `3181bd08968492ef8c93666e445458aa32369861d3a6de7d3ed4ca6abfefc9c4`、`9e0b894d2f97b8db67150d79fb77d4a25b5185613c87a37fd5eaf036a203abdf`。私有源码、SQLite、日志及探针保留于上述 `frozen-upgrade` 目录，MySQL 容器、网络、卷及 DEV guard 暂保留至协调者确认新一轮独立复核和证据均完成后回收；QA 可由协调者提供现有合成 DEV app 凭据，对此 guard 仅做只读查询，不得将其当 QA 自有可写 schema。
- **QA2 非阻塞笔误。** 按协调者转交的核查，仅删除中文合同 Swagger 第一步 `合成来源，。` 中多余的一个中文逗号；这是 1 个 Unicode 字符、UTF-8 为 3 字节，其余字节不变。中文合同 SHA 从 `f2609bae20b2b130a9a45e6fbc184389fd7b08127364d935d8fb4b1000e7f0b5` 变为 `56489bc4093918e5422672fd385af90442debe51e44103563f28f019ee734aea`；英文仍为 `ef4e88754c6adf778e59f15cb23a4f673e069ebf94814bb411032acd42d728a5`。34 路径中仅此文件不同于 QA2 输入，更新清单 `/private/tmp/arch-acq004-r4-isolated-ebbghp32/frozen-upgrade/manifest-qa2-rework.txt` SHA-256 `b882f7a6da1fc9a6a784b9585c20222db130d23e5e450498a1e995958ca0b9b4`；此前清单及返工记录不覆盖。
- **交接边界。** 正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交差异；本轮正式写入仅此中文合同及本 `tasks.md`，未改 spec、checklist 或产品代码。QA2 当时的 `qa_blocked`、R4-AC05 依最终 DAA 候选按新版指南的独立原生复验以及 Human Owner 最终验收仍需各自处理。DAA-013 的 QA3 通过只适用于其当时候选；其后 QA4 因英文 Stage C Web 控件名称不匹配记录 `qa_failed`，不可从本次 Rust 合成上报推定 DAA 文档或最终候选已验收。交 fresh-context Verification 独立复核本次精确候选及证据。

## r4 补充原生联合验证与 Development handoff

2026-11-13（Asia/Shanghai），协调者在本任务专用环境补做原生联合验证。输入 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，补证前 tasks SHA-256 `026cb51d0f2a66f7fc6b94b3b318b2d508bd7e49e6fa9b41381456f603b6b0ab`，已有独立 QA1 checklist SHA-256 `644d7162ec6de1871cacb9daccad4ba42482379f6cb5f646d7433b65d62db6b3`。下述是协调者实际执行的 Development 补充证据，不是独立 QA verdict。先前合同文档返工及旧候选分段测试作为历史保留。

- 专用 Web 在 `arch_acq004_r3_dev_main` 中为合成 PLC E/F 分别保存登记：两台共用 `instanceId`、各自 `sourceGeneration`，各采集 DB21/22。Web 展示并点击复制每条已保存记录的三个参数，任务专用原生 DAA `.app` 的对应行分别粘贴或填入、保存，关闭设置后重开，三项均一致。IAB 与原生应用的剪贴板不共享：第二组通过只读取得 Web 展示文字，再以 CUA paste 注入原生应用；本证据不声称全部跨应用系统剪贴板均端到端成功。独立 QA1 已另行验证 Web 一键复制与提交行一致。
- 原生 DAA 使用任务私有新 runtime4 SQLite profile、`DAA_PLC_READ_ALLOWED=false` 和 `127.0.0.1:38404`，没有连接 PLC。原生进程关闭后，在同一 profile 上以临时测试 helper `acq004_inject_native_fixture_cycles` 先核对已保存身份，再注入两台 PLC × DB21/22 的 4 份合成样本；`cargo test` 定向运行退出 0、1 passed。重新启动原生应用，读取同一 profile 的 `pending=4`；在 UI 显式确认开始后显示 `acknowledged=4`、四行各尝试一次，再暂停上报。这是测试 helper 注入的样本，不代表真实设备采集。
- 项目 Web 实时页可见两台 PLC 的 DB21/22 点位。协调者以任务私有 `native-joint-check.py` 只读比较同一 profile 的 SQLite 原始正文与 `committed/created` 回执，并核验专用 MySQL UUID 及登记、历史、最新值：退出 0，2 条登记、4 条历史、48 个最新点位，四组 PLC/DB 的三标识与 sampleId 一致。探针 SHA-256 `03317dbcdbd0d8defda2c3340ae61b51ff3b1c373e46896ec3ca12e00dcf336e`；输出不等于现场数据或真实设备证明。
- 随后协调者复用同一隔离 profile 和已在 Web 登记的 C/D 两台不同 `instanceId` 的 PLC。Web 分别点击复制后，因 IAB/原生剪贴板隔离，均只读取得页面显示文字再以 CUA paste 注入原生对应行；保存、关闭再打开后三项一致。关闭原生进程后，任务私有 helper `acq004_inject_distinct_native_fixture_cycles` 向同一 profile 注入两台 PLC 各 DB21/22 的 4 份合成样本，定向 `cargo test` 退出 0、1 passed。重开原生应用先见 `pending=4` 和此前 `acknowledged=4`，UI 显式开始后为 `pending=0`、`acknowledged=8`，随后暂停；没有连接 PLC。
- `uv run --offline --no-sync python native-joint-both-check.py` 在任务私有环境只读检查 SQLite 与专用 `33404` / `arch_acq004_r3_dev_main`，校验 UUID、四行登记、8 份 SQLite 正文和可靠回执及其对应 8 条 MySQL 历史的 PLC/DB、实例、代次与 sampleId；按正文 pointId 核对本次 96 个最新点，退出 0。四台 PLC 八组最新点的实际合计为 144，另 48 个来自之前的 C/D 合成样本点 ID。首次误以 96 作为这八组总数的断言失败；逐点分辨之前与本次样本后，保留 144 合计并复验通过。探针 SHA-256 `fd5b55eb7202f102a2c22626f440e3c5c34601340249751d4751edcedf87e3b8`。
- 此原生候选固定为 `FactsDeliveryDialog.vue` SHA-256 `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd`、`services/local_delivery.rs` `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2`、`domain/sample_upload.rs` `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b`。本角色只读复核这些私有候选摘要与当时正式 DAA 文件相同；后续 DAA-013 返工仍须重新固定，不把当前联合结果扩大为最终候选结论。A/B 同实例和 C/D 异实例的旧候选分段证据另见下文，本次 E/F 原生证据仅覆盖同实例。
- 新发现：DAA 开始或继续上报的中英文 `confirmRegistration` 提示仍把 DB 包含在“已登记”中；只读源码核对中英文 `confirmSameTarget` 也使用同类登记表述。它们与 r4 三标识准入不一致，已由协调者转交 DAA-013 归属方；中英文 Stage C 的 R4-QA-03 仍待归属方处理。本任务未修改 DAA 源码或指南。
- R4-QA-01/02 两份合同文档的返工仍为本节下方候选：英文 SHA-256 `ef4e88754c6adf778e59f15cb23a4f673e069ebf94814bb411032acd42d728a5`，中文 `f2609bae20b2b130a9a45e6fbc184389fd7b08127364d935d8fb4b1000e7f0b5`；34 条 ACQ 源码/文档清单 SHA-256 `cfcbe57e6e52fe0da2fa65432459b2ac4af899bb9337288465c70eeca59dedfb`，补证前逐项复核 34/34 匹配。本轮只更新 `tasks.md`，不写 spec/checklist 或产品代码。
- DAA-013 的独立 QA3 已对其当时精确候选记录 `qa_passed` 并关闭 QA1/QA2 并发反例；后续本任务发现的 DAA 文案/指南仍在归属方返工，不能把既有 QA3 自动扩展到新的候选。后续需在 DAA 文案/指南返工及最终精确候选确定后，由 fresh-context Verification 独立复核其影响、QA1 的 R4-QA-01/02/03 及同实例/异实例的联合范围；本任务现有 QA1 仍为 `qa_failed`，Human Owner 最终验收未发生。实际数据库、历史、PLC、生产采用、部署和发布不属此隔离证据。

## R4-QA-01/02 文档返工与 Development handoff

本轮依据 Human Owner 已批准的 ARCH-ACQ-004 r4，以及协调者转交的独立 QA `qa_failed` 记录，限两份公开事实接口 README 修正 R4-QA-01/02；不修改产品源码、数据库、DAA 文件、规格或 checklist。输入 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，返工前 tasks SHA-256 `c28128b701577407eb2b6536700f2c5f9d11de5cae7fd252338273f952b89ed0`，输入 checklist SHA-256 `644d7162ec6de1871cacb9daccad4ba42482379f6cb5f646d7433b65d62db6b3`。 [QA1 发现](checklist.md#失败与返回项)

- R4-QA-01：两种语言的补传说明均要求样本仍有效、三个标识仍匹配当前 PLC 登记，再解释同实例及样本 ID 的原字节重试返回 `duplicate`；说明接管后旧身份即使原字节不变也可能得到 `403 plc_facts_v2.scope_rejected`。相邻 `409` 错误及 Swagger 重试步骤同步加上当前准入和有效期条件。
- R4-QA-02：`instanceId` 说明改为该实例是三个准入标识之一并限定样本 ID 去重范围；`sourceType` 明确来自该 PLC 当前登记行，供展示且不参与样本准入/校验，后端按写入时的登记值标注历史。
- 正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交差异。相对 QA1 的 34 条非 DAA 清单仅两份 README 字节变化：英文从 `679c980db881655e7bd948f6ace31ed8a8ef65763dc07231ac2d7c08c1dfcf58` 到 `ef4e88754c6adf778e59f15cb23a4f673e069ebf94814bb411032acd42d728a5`；中文从 `ee54358075a734d29f2a3589f0dce0d5b845df542853d340514825bc9944f72e` 到 `f2609bae20b2b130a9a45e6fbc184389fd7b08127364d935d8fb4b1000e7f0b5`。新 34 条 SHA 清单 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/manifest-qa1-rework.txt` SHA-256 `cfcbe57e6e52fe0da2fa65432459b2ac4af899bb9337288465c70eeca59dedfb`；此前 34 条正文及原始清单保留在下文，两处新摘要以本节为准。
- DEV self-check：静态对照当前 `async_source_registry.admit` 和 `async_v2.write_sample`，确认登记行标签来源、重复分支重新准入和有效期先于 duplicate/409；独立 QA1 已有接管前 `created/duplicate`、接管后原字节 403 的实际隔离证据。本轮 Python 标准库检查两份文档 36 个本地目标与片段、4 个 JSON 块，退出 0、无缺失；与返工前副本比较，链接和 JSON 示例完全不变。`git diff --check -- contracts/published/http-api/plc-facts-v2/README.md contracts/published/http-api/plc-facts-v2/README.zh-CN.md` 退出 0。两次 `git diff --no-index --check` 因文件存在预期差异各退出 1、无空白诊断。纯文档返工未运行数据库或重新执行产品测试。
- 本次只交 R4-QA-01/02 的新候选供 fresh-context Verification；是否关闭发现由 Verification 判断。R4-QA-03 中两份 Stage C 及其链接由 DAA-013 归属方处理，DAA-013 的独立复验和同一真实 Tauri UI / SQLite profile / worker 全链路仍需核验。未授权真实数据库迁移、部署或最终验收。

## r4 本轮专用 MySQL 与 HTTP Development 自检

Human Owner 在 2026-11-13（Asia/Shanghai）明确要求：“那现在进行隔离验证吧，使用专用 MySQL 环境，不要动现有数据库和历史数据。”协调者依此创建本任务独占的 MySQL 8.4.6 容器、网络和空卷；宿主回环 `127.0.0.1:33404`，服务端 UUID `43b1c562-df4b-11f1-83c9-72f35d3e7827`，数据库时钟偏移 `+08:00`。DEV 与 QA 各 7 个不同 schema，用户及权限分离；本 Development 只连接 `arch_acq004_r3_dev_*`，没有对 QA schema 或既有 3307 发起连接。临时候选及其前驱工具不含真实 `.env`、profile 或历史数据。

- 使用项目已安装、受锁文件约束的 `.venv/bin/python` 及 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/dev_preflight.py`：逐个核验 7 个 DEV schema 的实际 UUID、名称、MySQL 版本、上海偏移、非 root DDL 用户与空表，退出 0；进程的 socket guard 限定 `127.0.0.1:33404`，未尝试连接 3307。默认沙箱首次回环连接返回 EPERM、退出 1；仅对已批准的专用目标提权重跑成功。
- 从先前保留的临时候选和 pre-integration 前驱文件重建无真实配置的 `frozen-r2/backend`，按此前记录的初始清单逐项核对 **707 个 backend 文件 SHA，0 差异**；旧工具的 7 个关键 SHA 由 MySQL 测试再次核对。候选与正式树逐项比较全部 **708 个 backend 文件，0 差异**；Python 路径集合一致，额外的 `sitecustomize.py` 仅存在测试副本并负责网络 guard。本轮未改产品源码。
- `dev_initialize.py` 在逐目标重新验证全空后调用实际 Alembic 链：`dev_main` 到 `7b9d1f3a5c7e`；`dev_restore/dev_initialized/dev_json/dev_empty/dev_failure` 到 `5f7a9c1e3b25`；`dev_guard` 保持空白。6 次均退出 0。迁移前驱使用显式目标 UUID、schema、operation 守卫及合成 DDL 用户；没有对现有数据库或历史执行迁移。
- 仅在专用 main 建立合成 active admin/operator，实际通过 `/api/v1/auth/login` 获 token，使用仅本机、无 reload 的两个后端 `127.0.0.1:38404/38405`（启动时 PID 46068/46069）。另建立协调者指定的合成浏览器管理员及普通用户，并在两端各验证两种角色登录，4 次成功。随机 DB 密码、JWT 和登录材料只放 0600 的本轮私有配置，不写仓库、任务记录或终端。
- `dev_test.py http`：实际执行 `pytest -p no:cacheprovider -q tests_mysql/test_acquisition_source_registry.py -k 'two_running_apis or first_registration or retired_generation' -x --tb=short --disable-warnings`，退出 0，**3 passed、4 deselected**。覆盖两进程即时登记/提交、同实例和不同实例的两台 PLC 各 DB21/22、匹配 committed 回执与 duplicate、错误 ID 的 403、非法 DB 的 422、标签编辑、旧版本冲突、上报与接管真实行锁先后及退役代次拒绝。日志 SHA-256 `dd33d3f64db46c3fa9e2641d756b7f03df9b293ea2fe3491190cc7101841276d`。
- `dev_test.py migration`：实际执行同测试文件中 `-k 'three_predecessor_migration_paths or partial_ddl_refuses'`，退出 0，**4 passed、3 deselected**，29.79 秒。覆盖已初始化、旧 JSON 先预览/确认/导入和空登记直接迁移三条路径；逐项比较旧登记、事实表列及排序行、当前和已清空点位水位。模拟部分 DDL 后守卫拒绝盲重跑，独立恢复 schema 逐行对账并再迁移；切换后合成新数据无法无损表达成 r2 时保全新事实并不尝试破坏性回退。日志 SHA-256 `d8994c5cb96622c072fedbe283c6972d3b3dfdc51450a7f0ffa8f0de9ef5d15e`。这一检查证明合成场景行为，不自动提供真实现场迁移或回退授权。
- `dev_read_probe.py` 使用独立合成 PLC 前缀、实际两 DB 与匹配回执，退出 0。实际 HTTP 覆盖五条 GET，核对 `/latest/browse` 过滤/分页、标签编辑后实时显示与历史标注、未知 PLC 403、已登记无该 DB 的空结果；只对本探针 DB22 事实及最新值设为过期后，options/history/latest/browse 排除、详情 404。该操作只写独占 DEV main 的合成行。
- `dev_metadata.py` 只读校验专用 main 的当前 UUID、schema、版本与上海时钟：退出 0；revision 为 `7b9d1f3a5c7e`，来源登记仅 `plc_source_registry` 一张 InnoDB 表，列为四项业务输入和四项系统维护字段，六张 `acq_source_*` 旧登记表均不存在；没有读取记录内容。
- 协调者在 IAB 实际 Web `127.0.0.1:38408` 经 `38404` 使用合成管理员登记 A/B 同实例、C/D 异实例四台 PLC，每台保存四项后点击该已保存行的一键复制；切换至正式 DAA 构建出的 `127.0.0.1:38409` 页面逐行粘贴、保存并重开，三项内容均正确。DAA 页面此次使用内存合成 IPC，不代表同一个真实 SQLite 或原生进程。合成普通用户授予 realtime/history 页面后实际登录，不显示“来源配置”，直接访问其路径重定向到 realtime。协调者首启 Web 时 Vite 因配置变化重优化了候选依赖链接指向的共享可再生 Vite 缓存；已立即停止并用任务专属 `vite-cache` 重启，未因此访问其他数据库或用户配置。
- 协调者使用任务私有 DAA 源码副本、原 Rust LocalEngine/队列和新建合成 runtime4 SQLite，设备数据来自临时 fixture、未连接 PLC。以相同四份 Web 登记身份运行两次 `cargo test --locked --offline ... acq004_real_backend_two_plcs_two_dbs`，各退出 0、1/1；每轮两台 PLC 各 DB21/22，合计 8 份真实 HTTP `committed` 回执，按三标识、DB、sampleId、contract/status/outcome 核对。测试断言设置保存并重开、上报后再重开仍保留四份 confirmed。为匹配 DB21/22，只在私有副本调整测试 helper 和 transport fixture，产品逻辑未改；首次编译因缺冻结公开 `vectors.json` 退出 101，补入原合同文件后编译并运行通过。IAB 以 PLC C 筛选看见 DB21/22 共 24 个 DAA 点。`dev_joint_check.py` 随后只读核对专用 DEV main 的指定 A–D：4 行登记、8 份历史、8 组共 96 个最新点，实例及代次均匹配对应登记，退出 0。
- 上述联合证据固定于 DAA 副本 `FactsDeliveryDialog.vue` SHA-256 `66e9149f8734d6e7c47c03a0ba34a22c996546e8daaea72c7abc290fbe1d260b`、`local_delivery.rs` SHA-256 `f8f71af5ff072b4872347f1052f00e3914f8e14035c103ee047078c50895bbe6`、`sample_upload.rs` SHA-256 `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951`。由于 DAA-013 并行返工，正式 DAA 的前两项已变动；该证据不自动覆盖新的 DAA 候选，也不能将浏览器内存 IPC 和单独 Rust/SQLite 测试合称同一原生 UI 全链路。最终候选及联调需在 DAA 返工稳定后重新核验。
- 本轮辅助入口均在 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/`，其 `sitecustomize.py` 限制所有测试子进程连接至 `127.0.0.1` 的 33404/38404/38405；冻结 r2 工具使用同一 guard。实际测试使用新的专用容器 UUID，并无 3307 连接、真实 profile 或真实历史读取。当前后端和任务私有材料暂供协调者的合成浏览器/DAA 联调及独立 QA 使用，待它们结束、必要证据持久化后由协调者仅回收本任务自有进程、容器、网络、卷和临时资源。

当时的限制：上述浏览器与真实 worker 联调覆盖固定 DAA 候选的分段链路；当时 DAA-013 QA2 新增 F-DAA013-QA2-001，记录为 `qa_failed`。后续该任务 QA3 与原生联合补证的现状见本文件顶部；本角色不代判 DAA-013。中英 `STAGE_C_GUIDE` 第 6 节当时只描述 r2 的 DB 登记，且第 4 步无条件要求读取范围覆盖，与 r4 不一致；两文件由 DAA-013 拥有，本轮未覆盖，待协调修订。独立 Verification 和 Human Owner 最终验收当时均未进行。

### r4 Development 精确交接

以下为此前交接时的记录；后续合同返工和原生联合补证以本文件顶部的新交接为准。

- Human Owner 已批准的 r4 规格 SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`；源码交付为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交差异。任务 34 条非 DAA 路径的清单 SHA-256 `922a75e9a57dac4ff9862ecace4fa6f8c5ce149a875560e79fe4e12cabf640c8`；DEV 后端 708 条源码与正式树一致，唯一额外 `sitecustomize.py` 是临时测试网络 guard。任务修改路径及此前正式树无库测试、构建和链接检查仍见下方原有清单与记录；本轮只更新 `tasks.md`，未修改产品代码。
- 隔离自检实际结果为本节上述 MySQL/双进程测试 7/7、五 GET 过期/分页补充、四行 Web→DAA 粘贴的内存 IPC、普通用户页面边界、两次独立 Rust/合成 SQLite→HTTP 的 8 份 committed 与 4 行登记/8 行历史/96 个最新点位对账。浏览器与 Rust/SQLite 是分别验证的两段；没有在同一真实 Tauri UI 及持久化 profile 上贯通这两段。DAA 证据固定到上述私有副本 SHA，正式 DAA 并行返工后已变化；QA2 finding、两份 Stage C 的 r4 操作说明及最终 DAA 候选不在本角色已通过结论内。
- 本任务专用 `127.0.0.1:33404` MySQL 仍运行以供 QA，容器、网络与卷分别为 `arch-acq004-r4-verify-mysql`、`arch-acq004-r4-verify-net`、`arch-acq004-r4-verify-data`；DEV 后端 `127.0.0.1:38404/38405` 的任务进程 PID 分别为 46068/46069。协调者确认 Web `38408` 和 DAA 合成 UI `38409` 已停止，交接时 `lsof` 无对应监听。正式 8000/5190、现有 3307、真实 profile、历史和设备不属本轮验证目标；本角色未连接现有库。独立 QA 使用自己的 `qa_*` schema、账号和精确候选，保留失败证据后再按资源生命周期回收仅本任务资源。
- 本交接不表示 QA 已通过、Human Owner 最终验收、真实环境数据库迁移、产品部署或现场设备验收。按 STD 交 fresh-context Verification 核查，特别审阅 DAA 并行变动与缺失的整条原生 UI 链路。

下方为隔离环境获准之前的 DEV 自检与资源事实，保留当时的命令和状态，不作为本轮仍未运行 MySQL 的结论。

## DEV self-check（实际结果）

后端测试从候选 `backend/` 启动，所有命令使用如下合成进程环境（本机地址端口 1，非运行中的 MySQL）：`PYTHONDONTWRITEBYTECODE=1 APP_NAME=fixture APP_VERSION=1 API_V1_PREFIX=/api/v1 DEBUG=false TESTING=true MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=fixture MYSQL_PASSWORD=fixture MYSQL_DATABASE=fixture TEST_MYSQL_DATABASE=fixture_test MYSQL_ROOT_USER=fixture MYSQL_ROOT_PASSWORD=fixture JWT_SECRET_KEY=synthetic JWT_ALGORITHM=HS256 ACCESS_TOKEN_EXPIRE_MINUTES=15 REFRESH_TOKEN_EXPIRE_DAYS=1 LOG_DIR=/private/tmp/arch-acq004-r3-dev.0fxOzki5/logs`。候选复用交付树的只读 `.venv`；`database.__file__`、`app.plc_facts.models.source_registry.__file__` 和 `app.plc_facts.services.async_v2.__file__` 均显示候选绝对路径，未从运行树导入项目代码。

- `.venv/bin/python -m pytest -q -m no_db tests/test_acquisition_source_registry.py tests/test_acquisition_data_browse.py tests/test_plc_facts_v2.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py -k 'not test_business_runner_accepts_only_guarded_previous_and_successor' --tb=short --disable-warnings`：退出 0，140 passed、3 skipped、1 deselected。首次适配前同三组后端回归为 28 failed、78 passed、2 skipped；适配后第一轮为 104 passed、2 skipped、1 failed。唯一保留失败 `test_business_runner_accepts_only_guarded_previous_and_successor` 是 BE012 专用 runner 的源码目录守卫要求特定临时前缀，与本任务候选目录不符；最终命令明确排除，不能称全量通过。
- 协调者在同一候选，以相同合成环境额外设置 `TMPDIR=/private/tmp/arch-acq004-r3-dev.0fxOzki5/pytest-tmp`，执行 `.venv/bin/python -m pytest -q -m no_db tests/test_acquisition_source_registry.py tests/test_acquisition_data_browse.py tests/test_plc_facts_v2.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py --tb=short --disable-warnings`：退出 0、141 passed、3 skipped（13.13 秒），包括此前因默认临时目录不符而失败的 BE012 路径守卫；此前失败事实仍保留。单独 `pytest -q -rs` 对 3 项 skip 退出 0：ACQ003 实库用例缺少其专属隔离 fixture；BE012 B runner 只在保留的前退役候选执行；BE003/60 旧结构测试固定在不可变 `f85bea8` 源码。
- `.venv/bin/python -m pytest -q -m no_db tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py --tb=line --disable-warnings`：退出 0，32 passed、1 skipped。`.venv/bin/python -m alembic heads`：退出 0，唯一 head `7b9d1f3a5c7e`。
- `.venv/bin/python -m pytest -q tests_mysql/test_acquisition_source_registry.py --disable-warnings`：退出 5，1 module skipped、无测试收集，因为没有授权的专属目标；没有连接数据库。现已编写合成用例源码，包括 r2 已初始化、待导入旧 JSON、确认空登记、事实与水位对账、部分 DDL 拒绝重试及独立前驱恢复、r3 新数据无法被前驱表达时保全现场，以及双后端/两 PLC/两 DB 检查。r4 不同实例/两 PLC 各两 DB 测试补充后，7 项仅在阻断 socket 的合成环境做 `pytest --collect-only -q`：退出 0、7 collected；缺少单独迁移确认时执行 `pytest -q -rs ... -k "three_predecessor_migration_paths or partial_ddl_refuses"`：退出 0、4 skipped、3 deselected；该文件 Python AST 解析退出 0。没有实际连接、运行或调试任何 MySQL 用例，不能视为通过。
- Python 标准库 `ast.parse` 对候选 `backend/app/plc_facts/**/*.py`、`backend/scripts/plc_facts_maintenance/*.py`、新迁移及 MySQL 测试共 28 文件：退出 0。`git diff --no-index --check` 对 37 个更改的已有文件和 3 个新增文件逐一检查：退出 0，无空白错误。旧 `6a8c0e2b4d16` 迁移 SHA 为 `e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924`，旧采集 OpenAPI SHA 为 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`，旧管理 r2 OpenAPI SHA 为 `2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad`，均与候选基线相同。
- Web 从候选 `frontend-js/`：`node scripts/check-module-manifests.mjs --check` 退出 0；`node --test tests/module-registry/acquisition-data.test.mjs` 退出 0、12/12。初次运行旧 r2 测试为 9 passed、3 failed，更新为 r3 行为断言后通过。`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' node node_modules/vite/bin/vite.js build --outDir /private/tmp/arch-acq004-r3-dev.0fxOzki5/web-dist` 退出 0，有 chunk 大小警告；未提供上述合成配置的第一次 Vite 构建退出 1，原因是页面权限配置缺失。`pnpm build` 在 Web 和 DAA 均退出 1：隔离副本的链接依赖触发自动安装检测，网络元数据不可用并因无 TTY 中止移除提示；没有确认安装或清理。直接执行了锁定依赖提供的相同工具入口。Node 验证 Web 的 `process.cwd()` 和 `src/app/acquisition-data/views/sources/index.vue` 真正解析到候选，Vite 依赖解析到原树只读依赖。
- DAA 在收到共享路径冲突消息**之前**，候选 `node --test tests/facts-delivery.test.mjs` 退出 0、6/6；`node node_modules/vue-tsc/bin/vue-tsc.js --noEmit` 退出 0，`node node_modules/vite/bin/vite.js build` 退出 0，有依赖注释与 chunk 警告。这些仅证明被冻结的 r3 候选，不证明之后 DAA-013 的实现、实际浏览器、原生 IPC、队列或其验收。
- 对非 DAA 的 7 份文档以 Python 正则及路径存在性核对 64 个相对目标：退出 0，0 个缺失；未宣称所有锚点或按指南实操已核验。两份 r3 OpenAPI 由候选 FastAPI 路由生成，并由离线合同测试与运行模型比较。

## 正式交付树复核（协调者执行）

- 后端在正式 `backend/` 使用合成进程环境与 `TMPDIR=/private/tmp/arch-acq004-r3-dev.0fxOzki5/pytest-tmp`，执行 `.venv/bin/python /private/tmp/arch-acq004-r3-dev.0fxOzki5/offline_verify.py -q -m no_db tests/test_acquisition_source_registry.py tests/test_acquisition_data_browse.py tests/test_plc_facts_v2.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py --tb=short --disable-warnings`：退出 0，141 passed、3 skipped。辅助入口对 `BaseSettings` 注入 `_env_file=None`，禁止 `socket.connect`、`connect_ex` 和 `create_connection`，并确认 `database`、登记模型及采集 Service 都从正式 `backend/` 导入；未读取真实 `.env` 或连接数据库。三项 skip 原因见上。
- 正式 `frontend-js/` 执行 `node --test tests/module-registry/acquisition-data.test.mjs` 退出 0、12/12；`node scripts/check-module-manifests.mjs --check` 退出 0。任务已跟踪范围 `git diff --check` 退出 0；本角色之后对新增的 MySQL 测试补充，以 pre-integration 备份作 `git diff --no-index --check`，退出 0。
- 正式 Web 构建在 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/formal-web-env` 执行：

```bash
env -i PATH=/usr/bin:/bin NODE_ENV=production VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' /Users/jason/.nvm/versions/node/v22.19.0/bin/node /private/tmp/arch-acq004-r3-dev.0fxOzki5/formal_web_build.mjs
```

退出 0，有既有 chunk size 警告。首次同命令使用 `node` 而非绝对路径，因 `PATH` 不含 Node 而退出 127；改绝对路径后成功。为便于清理临时文件后复现，脚本核心配置如下：

```js
import { build } from '/Users/jason/Desktop/DreamCode/aiis-ics-arch/frontend-js/node_modules/vite/dist/node/index.js'
const root = '/Users/jason/Desktop/DreamCode/aiis-ics-arch/frontend-js'
let sawSource = false
await build({ root, configFile: `${root}/vite.config.js`, envDir: process.cwd(),
  plugins: [{ name: 'confirm-formal-source', enforce: 'pre', transform(_code, id) {
    if (id.split('?')[0] === `${root}/src/app/acquisition-data/views/sources/index.vue`) sawSource = true
  }}],
  build: { outDir: '/private/tmp/arch-acq004-r3-dev.0fxOzki5/formal-web-dist', emptyOutDir: true } })
if (!sawSource) throw new Error('Formal acquisition source page was not built')
```

正式 Vite 配置及项目根作为输入，`envDir` 是不含真实 `.env` 的临时目录；插件核实正式来源页参与构建。构建和无库测试不能替代隔离 MySQL、双进程或 DAA 联合验证。

- 正式与候选 `backend/app/plc_facts/v2_config.py` 的模块说明和旧 `readScopes` 解析注释已同步纠正：旧 JSON 仅用于历史材料校验，当前 HTTP 读取按已登记 PLC。Python AST 比较证明除模块 docstring 外无语法树变化；验证退出 0，无行为调整。

- 正式交付树对 `docs/acquisition-data-guide.zh-CN.md`、`backend/app/plc_facts/README{,.zh-CN}.md`、`backend/scripts/plc_facts_maintenance/README{,.zh-CN}.md` 和 `contracts/published/http-api/plc-facts-v2/README{,.zh-CN}.md` 使用 Python 标准库解析 Markdown 相对文件目标并检查路径存在：退出 0，7 份指南、64 个目标、0 个缺失；未访问网络，未声称逐锚点或按指南实操。

## 冻结重叠与未完成事项

Human Owner 已授权 DAA-013 负责 DAA 对话框、逐 PLC 三参数与队列、DAA 双语文案/测试和 Stage C 手册。下列 6 个候选文件在协调消息前已变更，**冻结、不得由本任务直接整合**；DAA-013 新行为、双 PLC 原生 UI/SQLite、绑定和未绑定队列、指南实操须待其交付后联调核对。根指南把三标识粘贴标注为 DAA-013 对应版本完成及采用后的条件，不宣称该版本已交付。

尚需：获明确授权的独占合成 MySQL 目标，实际调试并运行三条迁移路径及故障恢复用例、双后端并发/实时读取/历史和回执的验证、Web 管理员/普通用户浏览器、DAA 版本联调和按指南实操；随后还须 fresh-context Verification，且不等于 Human Owner 最终验收。Development 角色没有启动/停止运行中的服务、连接 3307 或其他真实数据库、使用真实 profile、启动容器、部署或发布。候选与原树复用依赖仅供读取。

整合前正式 8000 使用 reload。协调者报告 Human Owner 已批准停止正式 8000/5190 服务并正常停止，端口及原父子进程已退出、未碰数据库；随后按清单机械整合非 DAA 文件并保持 DAA 版本。Development 已核对正式文件与候选摘要；后续重新启动、数据库迁移及实际采用仍按各自授权处理。DAA-013 仍可能并行修改 `CODE_INDEX.md` 等共享文件；后续变更先比对，不得整体覆盖并行工作。协调者的本轮 pre-integration 备份为 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/pre-integration`，其中保留正式树原有但尚未提交的 r2 源码；连同候选、初始摘要及未变前驱源码保留，用于将来重建冻结 r2 工具、旧 JSON 导入和恢复隔离测试。只有冻结前驱逐项核验、全部必要证据持久化且后续依赖解除后，协调者才按任务回收这些自有资源。协调者在本角色确认相关构建/测试会话已结束且 `lsof +D` 未发现打开文件后，仅回收本轮可再生的 `formal-web-dist`、`web-dist`、`formal-web-env`、`pytest-tmp`、`logs`、候选 `frontend-js/dist` 与 DAA `dist`；回收 `formal-web-env` 前仅解除其指向正式源码的 `src` 符号链接。候选源码、双摘要清单、`pre-integration` 和验证脚本保留；未删除真实数据或并行资源。

## 候选路径与双摘要

每行依次为「基线 SHA-256、候选 SHA-256、正式树复核状态、路径」。`ABSENT` 表示初始不存在；`INTEGRATED` 表示正式树与候选摘要相同，`PARALLEL:<sha>` 表示保留的 DAA 并行版本，候选 DAA 文件不得覆盖。候选清单非 DAA 34 项均已整合，冻结 DAA 6 项保留并行版本；后续变更仍须重新比对。正式 `tasks.md` 逐字保留 r2 原文，不纳入自身摘要清单。整合前清单 SHA-256 `acb1a322c69b7b2d50c9f39c0a2b03c45deb8303e3f9fa8ddf5c2fd1c2d5b840` 保存在本轮目录 `manifest-pre-integration.txt`。完整清单旁本 SHA-256 为 `922a75e9a57dac4ff9862ecace4fa6f8c5ce149a875560e79fe4e12cabf640c8`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  c24e4131d2161b9b358dde059d5427099ac3ca7be2c62025381a3fd1f9634655  INTEGRATED  CODE_INDEX.md
ABSENT  3c31bf18eae8a7140252ce0453bd5cd101ea7df5fecfda71b429f4299d2e3d56  INTEGRATED  backend/alembic/versions/20261113_1600_7b9d1f3a5c7e_plc_source_registry_single.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  343e731d9962694e72eb0010716613d1a946ea14d6facaf50fd7f407181daa9e  INTEGRATED  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  49e1d9006897358ff5e1dab3e4302c01e54fc4c48c30357a41212f35a22af40f  INTEGRATED  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  7926a935f80e6a45de5f271cae98373b517553440958cc2d2854e77d40043984  INTEGRATED  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  ae697bd61cb06f414adf29cc8760c0450bc0d9a9694e8690546ba9e654195ac9  INTEGRATED  backend/app/plc_facts/api/v2.py
9edd7f8b6baa0263752634baf761c3bcd963d1ca01d58b2c10c27332b7c1407b  f56e6a9771d9aeaa79ef35149f76ce3b923bc39b85080962afc32cc3fd951abf  INTEGRATED  backend/app/plc_facts/crud/async_source_registry.py
89483004833e50bd72893645e81fa7e2161975a8c3af5c4ee0306039e082442b  3f2edd4b10b51feb22858cbff945fcf050150028b99b536eb49c636336fe55de  INTEGRATED  backend/app/plc_facts/crud/async_v2.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  4434cb03cd2b35075a94f69f3046deb2f99084af9f6204c6805b2356f937fd7f  INTEGRATED  backend/app/plc_facts/models/__init__.py
ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8  b54cae59e8efa2f27f3bdc47c0826295d2aa50cdf6806e06b7a6206ddae29502  INTEGRATED  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  fb5ab4e174632bd0a08ba323de85db19cce4e412d8f2ef05a9592c460a1c1f68  INTEGRATED  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  69b689322fe75b481eb5b9b7e5a03f499bcd1b60cbd4036a6e3b57f25c66ac00  INTEGRATED  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  0149e1bd613a77cb40b3b0eadabd561108098f4e2e6b6d1cbbc40c5cfb6b9c0e  INTEGRATED  backend/app/plc_facts/services/async_v2.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  a8973a02603619d99d48b3074a4f7b1b64bea7bb702512fa1beef7e0472e83d1  INTEGRATED  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  ab9265420e014caf738addd013a4d62235965517aed6d93b24936871999b97ba  INTEGRATED  backend/common/integration/storage.py
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  6ebe7a6c2337aac344cbb3bdc289bdfbeeb704d1dedc823b52e10dd04d393fac  INTEGRATED  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  242b129b39803fa38886fd47f05661e021c9fec577f508131034fca6af4744ff  INTEGRATED  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  fcbf509b033de57147e5bc3e9a9c49e62ed4b4e491a0a731f4fc88448be119ef  INTEGRATED  backend/scripts/plc_facts_maintenance/main.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  4b063e742d1fcb1a298a51268ce06ec1ff927763805c89101edac3fb031e49ed  INTEGRATED  backend/tests/test_acquisition_data_browse.py
610873ba55cad98961b9786904cc9dfa2e700fc66d9efa449d047bccc888b007  f789b61bd544ff5b155aec31f3fcfd0c4f93ce00af1e11b9fe8169b2ccb61933  INTEGRATED  backend/tests/test_acquisition_source_registry.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  8aee2a5517bee35c8990609da7610498749e5ab67d3bfeaee925a0927f6bf9b0  INTEGRATED  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  7c18d5378844fe918b78746c5cd605fb790d41e2d66e8229ece273d8234bd854  INTEGRATED  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  c3bc4f061b1e598c084990e18d0ee31846a790a1884f8dd76957c8f8546b58e8  INTEGRATED  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  3f0def5e31c20bc2b87340c6d44cf088022e4a0d48f710e38ec9a89200ef00fb  INTEGRATED  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  3f5ad6a70dc95c4a89b9a41317eb61a595326b7c3aa30eeb524fbecd8519d3bf  INTEGRATED  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  679c980db881655e7bd948f6ace31ed8a8ef65763dc07231ac2d7c08c1dfcf58  INTEGRATED  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  ee54358075a734d29f2a3589f0dce0d5b845df542853d340514825bc9944f72e  INTEGRATED  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
ABSENT  0dc2e762a7337bbdd969086ef161d949887f9364b10892c8ce48ae77184ffda7  INTEGRATED  contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev-r3.json
ABSENT  46f8ff1ff7b4a75ac79ead3a7e5d824fbe2363df92c3a1767b51bb3c0e7b76d3  INTEGRATED  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r3.json
0dec414bae02916e62a792ee9c9aab4e1f268492922e3b86c08aea300970c664  753e95d6062615fe4546d19d88ff5032075772935d7bab16ba3a2a0694c899d1  INTEGRATED  docs/acquisition-data-guide.zh-CN.md
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  be96ed15affcdfdfb937db877dd5f1886b1f92aaa535d53dce9e479c27fda9f0  INTEGRATED  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  5e78ca4e1c7f0a2f563a461764445fd19cefb56c8ef009bec1ec4b603bfe1129  INTEGRATED  frontend-js/src/app/acquisition-data/locales/zh-CN.json
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  6f3c8f34b2b7b7398c935a488492958a0077e4eabc4dd4008a73be25810421c0  INTEGRATED  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  2061a9c3bd0df43ef7694169b74b721ae223c515e743693d843774e49f391c84  INTEGRATED  frontend-js/tests/module-registry/acquisition-data.test.mjs
```

冻结重叠文件（禁止直接合入）：

```text
b5dca306f7865003ee2f7cd203a3afb892d9c31433e5b6a0bb7e88185fd63d4e  e59cdbfd4593aef6cc1ab0d270063909db522917ce7c1c0a7f70c516027b308a  PARALLEL:4b6854fed2a742ef3efa4f7e2e1a45b57cb9eda144f7b8d21651d4ee99e3c982  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
621778efe38ec663aac2618fd3714b47ee365d8f8c3652bb2c3b0104f2eb2d49  2418161eef022c477273ee4327ad5a5c33bdc57c9777b9faa6d96bdb5eec1211  PARALLEL:dda01608f7ee820cefe28e330cf07673cdcf593e626ccd6e6048bf0105ccbcc5  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  1a538e24db46e2596e72195ca28c036abdfd37f644b65e7787c91bf29278322e  PARALLEL:66e9149f8734d6e7c47c03a0ba34a22c996546e8daaea72c7abc290fbe1d260b  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
cb19cf17fbdd55aab33df6d32ab6305f48f37f39c5970f63d0f490efb9fd7a88  ccc73ee938ee11cc7e1410918c6562af720e85ed9685a1f56d8eeb9f41db2aa5  PARALLEL:c9535dc0818aacf1e529b8c2c1bfecefc1ba946744e83ddaaba4a3d2b9337c39  automation-world/data-acquisition-agent/src/locales/en-US/common.json
dd0092edafe049ee271b4d7a52c921390694e3a139e8ca6a49074df086f1ab46  6d40b64a50620c636b2d9ba181dd57d8c3b7196cbf22153917eb08632979f22c  PARALLEL:9eb9025354fdc58c14a59a77aeb90e822173051a47f10567546b0b2be026833a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
86516e7fb13226c0f67ae65f555c5fd3c028848ee6c18001cf12d8deda2cd4ed  9be68594f8dc493f4c19848cabf41c5689a11d990b2a39a185efe437caeac089  PARALLEL:d51e9e9ae8d447f9714a14dfc15c8b3fd8ef71887fd7c5acd43b8297ee66458f  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```


## 合成 MySQL 夹具使用边界（未执行）

除已规划的专属 main 与 guard 外，恢复和中断试验使用 5 个预先建立、互不污染的独占 schema：`arch_acq004_r3_{dev|qa}_{initialized,json,empty,failure,restore}`。它们必须在本轮专用服务上处于 `5f7a9c1e3b25`、两事实表为空；夹具先对全部 schema 只读核验 UUID、MySQL 8.4.6、上海时钟、实际 DDL 账号、revision、表及空状态。运行前需要专用 DDL 账号和逐目标 `ACQ004_TEST_MIGRATION_CONFIRM`，并在本轮目录放入 `frozen-r2/backend` 的无真实配置源码副本，由测试校验 7 个关键文件的前驱 SHA。fixture 只属于隔离验证，不增加产品表或配置。测试不会创建或删除 schema；为失败试验保留部分 DDL 原现场，在独立空 restore 复制并核对备份，严禁覆盖其他数据。测试用的不可表达判断只验证该手工恢复场景，不表示生产环境具有自动回退拦截。所有实际 MySQL 迁移、并发和恢复测试须另获具体目标授权后运行，首次运行仍需调试。

## r2 历史 Development 记录

以下是 r3 开始前 `tasks.md` 的原文，SHA-256 `0f259d237deb08072c4ffc8526b3eb5f27349ac90b39832f28859738ab54d900`。其 `Revision`、状态和完成描述只属于历史 r2，不描述当前 r3。

<details><summary>展开 r2 原记录</summary>

Task ID: ARCH-ACQ-004
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 固定交付工作树候选供 fresh-context Verification；专属 MySQL 与实际 Web 联调需明确目标批准后补齐。
Workflow Mode: STD

# Development 实施与交接

## 精确依据和交付树

- 当前已批准 r2 规格 SHA-256 为 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，批准前草案 SHA-256 为 `f17437cf58ec92b51a2e977f803b9d81e25f7169214652c9f9735410ce515b05`。批准原文和 r1 历史保存在 spec。
- 候选在 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树，未创建 commit。该树开始即含 DAA-010、CU、provider 及其他工作；下列 SHA 固定整个当前文件，**不声明文件全部差异均由本任务产生**。`sample_upload.rs` 和现行采集 OpenAPI 等是既有未跟踪候选，不得当作可丢弃产物。冻结采集 OpenAPI `contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json` 当前 SHA-256 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`，本任务未修改。

## 实施事实

- 后端增加受管理员保护的来源列表、创建、追加和预期版本接管；登记、独立读写范围、已知代次存 MySQL InnoDB，写入路径在样本事务持来源锁，提交后读写范围从数据库取得。保留单样本 POST、回执及既有六条采集合同。维护 CLI 具有目标校验的导入预览/应用、提交结果不明提示、只读恢复导出和携带代次材料的再采用；Alembic 唯一后继为 `6a8c0e2b4d16`。
- Web 在采集数据模块增加来源配置列表、新增、编辑、读范围选择、显式接管及参数复制。DAA 在上报设置支持全局实例和逐本机 PLC 身份、JSON 填表、DB 范围校验；记录采样开始时的来源，空绑定的轮次仅存本地。历史轮、冻结正文、重试身份及回执按原字节保留。绑定和地址设置通过原 SQLite 设置事务和 CAS 保存；成功保存暂停派发，失败不改变运行状态。旧 runtime4 先全检/持原锁，再同目录添加受识别 DDL 和更新 seal；staging 或凭据不一致中断时拒绝打开并保全文件。原 runtime2/3 不转换。来源代次与本机计数器的持久对应阻止无法证明序号连续的复用；完整无引用的过期仅本地轮按保留期回收，不伪造回执。
- 双语指南说明 Web 登记 → DAA/第三方填参 → 单样本 → 回执 → 可选读回，区分尚未采用的候选、前驱格式及历史材料。

## DEV self-check

- 后端：在 `backend/`，`TMPDIR=/private/tmp/daa-008-r2-a-acq004-dev UV_CACHE_DIR=/private/tmp/acq004-r2-uv-cache uv run --offline --no-sync pytest -q tests/test_acquisition_source_registry.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py` 退出 0，88 passed、2 skipped；带 `test_business_integration_storage.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_business_integration_migration.py` 的上一轮退出 0，140 passed、12 skipped。后续新增管理事件前后类型记录，已由上述最新定向组复验。模型/路由单元测试不证明 MySQL 并发或实际授权系统。
- 不提供目标批准变量时，`pytest -q tests/test_acquisition_source_registry.py tests_mysql/test_acquisition_source_registry.py` 退出 0，6 passed、1 skipped；这只证明新 MySQL 用例默认不运行。`uv run --offline --no-sync alembic heads` 退出 0，唯一 head `6a8c0e2b4d16`；维护入口 `--help` 和 Python 编译退出 0，无数据库连接。
- Web：`pnpm check:modules` 退出 0；`node --test tests/module-registry/acquisition-data.test.mjs` 9/9；`pnpm exec vite build --outDir /private/tmp/acq004-r2-web-dist --emptyOutDir` 退出 0。静态构建有现有大 chunk 警告，不等于浏览器真实 API 验收。
- DAA：`node --test tests/facts-delivery.test.mjs` 5/5，含粘贴 DB 覆盖、重复 PLC、空绑定及修改实例提示；`pnpm exec vue-tsc --noEmit` 和 `pnpm exec vite build --outDir /private/tmp/acq004-r2-daa-dist --emptyOutDir` 退出 0（Vite 依赖注释与 chunk 警告）。Rust 指定修改文件 `rustfmt --check --edition 2021 --config skip_children=true` 退出 0。
- DAA Rust，均使用上述独立 TMPDIR、`cargo test --offline --lib ... --no-default-features -- --test-threads=1`：`infrastructure::local_store::sample_upload_tests` 13/13，覆盖新空 profile、跨保存采样绑定、local-only、不安全代次复用拒绝、旧 v4 冻结和 inode、升级中断保护与旧格式拒绝；`infrastructure::local_store::tests` 34 通过、1 个私有子测试按设计忽略；`services::local_delivery::tests` 13/13；`infrastructure::local_store::profile_contract_tests` 30/30。真实 SQLite 故障测试中，sealed v4 有真实 v2 回执的故障/kill/reopen 用例通过；无 seal v3 热 journal 用例明确检查不修改文件并拒绝自动恢复，两者不能混称。
- 初始全量 Rust 运行退出 101（146 passed、11 failed、2 ignored）：其中 9 项仅本地状态/维护夹具问题已在上面的定向重跑中处理；一项沙箱禁止本机监听（`EPERM`），以 scoped escalation 单独重跑 `infrastructure::facts_http::tests::v2_loopback_posts_original_utf8_to_sample_path_without_bearer` 1/1 通过，只使用自有回环端口；剩余 `infrastructure::yaml_migration::tests::migration_empty_retry_cas_capacity_lock_and_private_protection` 在仍持 Stores 锁时期望另一次锁成功，报 `profile_locked`，位于本任务允许面外，未修改。此项及旧维护夹具的基线证据见 [DAA-010 Development 记录](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/tasks.md) 原记录第 45、191、460 行；该 YAML 测试文件当前 SHA-256 `0e77314d10c05057f5bc8bb2275b46c5dbfa83673c837cf9cd7e1d6f8e430205`，经协调者与原 r1 快照逐字节比对一致。最后未再运行整套 Rust；上述定向结果不是全套通过声明。
- `git diff --check` 对所触及的已跟踪范围退出 0；文档脚本检查 13 份受触及指南中的 103 个本地相对目标，0 个缺失。未核查每一个锚点。`openapi-acquisition-sources-r2.json` 与当前管理路由生成结果和 Bearer 声明由单元测试比对。

## 未完成证据和资源边界

- 未获具体隔离 MySQL/Docker 目标批准前，不运行迁移、导入、复制、双进程 HTTP 或恢复。`backend/tests_mysql/test_acquisition_source_registry.py` 仅准备好受显式批准、专属目标名和确认串约束的 DEV/QA 合成用例；目标不就绪、锁等待/提交未知、同进程并发与跨进程即时生效、前驱恢复、读写权限守恒及实际 MySQL 模型一致性仍待执行并记录，不能据静态/模拟测试宣称通过。确认串、3 schema 角色和启动条件已向协调者交接。实际 Web 管理员/普通用户浏览器联调也仍待该环境；DAA UI 当前仅 SFC 合成验证。
- 没有操作现有 `.local/dev`、用户实际 SQLite、现有 dev 后端/数据库、真实 PLC；没有执行真实迁移、部署或推送。Windows 原生锁、重开、UI 和设备路径仍需另行实测。此交接不是 QA verdict、Owner 最终验收或任何真实环境采用授权。
- 已回收本任务自建的 `/private/tmp/daa-008-r2-a-acq004-dev` 合成 profile、`/private/tmp/acq004-r2-{daa,web}-dist` 及 `/private/tmp/acq004-r2-uv-cache`。`/private/tmp/acq004-*.log` 和 `/private/tmp/acq004-r2-development-manifest.txt` 为开发临时日志及清单，保留供协调者核对后回收，关键结论和完整清单已写入本文件。未创建或启停 Docker、监听中的业务服务或 MySQL。

## 固定候选文件 SHA-256

下列 64 行按路径和内容固定候选；清单原字节 SHA-256 `ff3f12cd8f45d1865c9f867139a01397a5e8f7a686255bae6c3c47da1f9ace15`。共享文件的 SHA 包括任务前已存在的并行工作。后续修改须重新固定并复验。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
1b91afd0296fa501b06cf7c0e4d9eef117b31d1a8d5f79e6a0aadc5df9374e53  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
42254a169e31c8916f64bcc2a48f96f3ed01f9f2e531f8f5ce77b3de3e8cb42f  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
58a52760af64a7b6a298141b23e71aca6fdf94da9e9bc6bd5b5484f385a2fe19  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
c5a2641a0e5df93fd6369b5157b3801dd87f8b5d4097a12ced9e56821b406ba4  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
7cb1f78bbe94177d8c4581f212d4ce7794298c6ed565ed31ad2750100c41e487  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
4c38f3c5da8a849f5cb9d79d4f7cd3f60119023229548c7ce0d22b0f2d775a64  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
51d4876c45a876c603a31e13566ded9224a4fa73d1d9961ba3647e1820395538  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
c4b4576609d17d30443ebfb8f3bdac01bd6d29237ff2e40a1e02a73d103e55e2  frontend-js/src/app/acquisition-data/locales/en-US.json
ba8a5a15fd326028a471a5f9b6f30c16540e4e23d624e7d84c1b95f334c58e9b  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
3eca0c153bef420425f0ca62aa1694c7292dd1f2015d13ce87110cb8df6a67f0  frontend-js/src/app/acquisition-data/views/sources/index.vue
d3839355c1ca73144f2047576d6bc014dad8cc234251cc00d438c29debbaa406  frontend-js/tests/module-registry/acquisition-data.test.mjs
033124b98b5185f525e5490d084e96807ac224b13d6719046db13e344f0924cb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
11aef1d39602696ada37483eca570353d2423c6183b04d517daeb114d1177d3a  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
6502bab43ce5222b06dd0c67b6abe62451252b445e33f5c8117f6452eb0e5264  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
0e2d0df131aa93eb9317e691e2a3f58e34d4ce5e91c9d3a2859dd787ab00273f  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
4f0a249aa4dec4a0e07d0b78e396c578ae7d69b07c04356041add3f8693543a5  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
d1acbaf6109d9f08869a3a40ac4c016597507b76808ad8f49cefbe39d6425d0b  automation-world/data-acquisition-agent/src/locales/en-US/common.json
0b3eb31b60861cc03113027cf18a722b660e2471ab7b2593aa73f546c95cc3de  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
91cabe56534b2855b44eb3a39d1f86c0ea305216daa5174914d158e844bbdffe  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```


## QA1 修复与第二次 Development handoff

- 2026-11-13 Asia/Shanghai，依据独立 QA1 `qa_failed` 原文逐项修复。原 [checklist](checklist.md) 未修改，当前 SHA-256 为 `bdfbbae404951806d17e952e0de891454315674c4c91cc85de00af249bd69041`。获批 spec SHA 仍为 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`；工作树 HEAD 仍为 `fd999224a8756feda314a33148304b4bf3461876`，无新 commit。上方首轮清单和证据原样保留，**本节清单是本次 rework 候选**。
- QA1-01：三个管理方法通过已有管理员依赖后才检查重复 query。实际 FastAPI 路由测试覆盖有效 JSON 的匿名和无效 Bearer 的 401/挑战头、普通用户 403、管理员重复参数 422；FastAPI 对语法损坏 JSON 的原生解析顺序未被改写。
- QA1-02：编辑已有零上报 DB 的活跃来源可保留空上报集并显式接管；已有独立读取权限及新增加的读写 DB 正确保留。新建时空 DB、移除原写 DB 仍不通过。测试执行实际 Vue setup。
- QA1-03：在同一登记事务中，只有无活跃绑定的初次 POST 需要检查已知代次；事实历史、最新水位及代次账本使用 MySQL 当前共享锁读取，命中返回 `generation_reused`。已有同身份的重复 POST 保持幂等。SQL 编译与合成服务回归通过；新增专属 MySQL 用例准备了仅有旧历史与仅有旧水位的两种复现，尚未运行。
- QA1-04：POST 提交尝试后的 `OperationalError` 即使回滚也失败，仍返回 `commit_outcome_unknown`。Web 按稳定错误码区分该状态、明确 `not_ready`、历史代次复用、实例类型冲突、活跃身份冲突和版本冲突，不自动重提；未知结果提示先刷新核对。中文和英文对称。实际浏览器和后端进程仍需后续独立验证。
- 按本轮协调补充 DAA 证据：`services/local_delivery_tests.rs::v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback` 使用新建合成 SQLite profile，通过实际 `LocalEngine` 设置入口保存地址和上报身份、关闭重开读取，在显式开始前验证无 HTTP，生成合成采集轮（配置含 DB1、DB2，故产生两份单样本），调用实际 `set_delivery` 和真实本机 HTTP client，将每份请求交给自有 loopback 回执替身，逐一核对 sampleId、来源身份、原始正文及 committed 回执，并确认 SQLite 状态和关闭重开。该回执来自合成测试替身，不证明后端或 MySQL 持久化。

### 本轮自检

- 测试在仅有合成变量的专属临时源码副本进行，未复制 `.env`，MySQL 参数为 `127.0.0.1:1` 占位。九个变更的后端/Web 代码和测试文件，均逐字节与交付树相同。
- `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_business_integration_storage.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_business_integration_migration.py`：退出 0，149 passed、11 skipped。随后只追加无效 Bearer 参数化覆盖；`uv run --offline --no-sync pytest -p no:cacheprovider -q tests/test_acquisition_source_registry.py tests_mysql/test_acquisition_source_registry.py`：退出 0，14 passed、1 skipped；MySQL 文件由于缺少专属目标确认按设计跳过，并未建立数据库连接。管理 OpenAPI 与已发布工件的 JSON 语义对照由离线测试覆盖，冻结采集 OpenAPI SHA 保持 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。
- Web `node --test tests/module-registry/acquisition-data.test.mjs`：退出 0，11/11；`pnpm check:modules`：退出 0；`pnpm build --outDir <自有临时目录>/web-dist --emptyOutDir`：退出 0，沿用大 chunk 警告。构建设置两项角色页面变量为 `[]`，禁用依赖重装。
- DAA `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --no-run`：退出 0；用产出的测试二进制、专属 `TMPDIR` 运行上述 `--exact` 回环测试：权限复验退出 0，1 passed；其余 `services::local_delivery::tests::` 排除该回环用例运行：退出 0，13 passed。Rust 目标目录是从 QA 的构建缓存克隆到本次专属目录，编译目标源码来自交付树。首轮沙箱仅禁止本机端口而报 EPERM；限该测试的授权复验中曾发现测试错误地假设 PLC 排序，修正测试后重跑通过。
- 环境修正记录：后端宽回归首次因 pytest 临时目录不符合旧 BE-010 守卫而失败，改用 `/private/tmp` 内专属目录后得到上述 149/11；DAA 旧 suite 首次因临时目录名不符合 `daa-008-r2-a-` 测试守卫而 6 项失败，改用守卫要求的自有目录后 13/13 通过。
- 改动 Python 文件 `py_compile`、该 Rust 文件 `rustfmt --check --edition 2021 --config skip_children=true`、`git diff --check` 均退出 0。

### 剩余边界和资源

- QA1 记录依然是失败事实；这份 handoff 只交付修复候选，须由 fresh-context Verification 重新判定。真实 MySQL 8.4.6、合成双进程/API 与浏览器、迁移和回退、完整原生 DAA 联调尚未验证；专属目标批准前不连接任何数据库。Windows 和现有 dev 的采用另按原批准边界。
- 本轮仅创建 `/private/tmp/arch-acq004-r2-rework.BWL4HtbX` 作为自有合成源码、SQLite、构建和缓存目录，证据已记录于本文件，自检后已回收。未操作已有 `.local/dev`、dev 服务、真实数据或设备，未启动 Docker。
- 相对首轮 64 文件清单变更 10 项：后端 `api/source_registry.py`、`crud/async_source_registry.py`、`services/async_source_registry.py`、`tests/test_acquisition_source_registry.py`、`tests_mysql/test_acquisition_source_registry.py`；Web 两份来源 locale、`views/sources/index.vue`、`tests/module-registry/acquisition-data.test.mjs`；DAA `services/local_delivery_tests.rs`。共享脏树其他差异仍独立保留。
- 以下 64 行包含每项末尾换行，原字节 SHA-256：`6c0e978c3b64188af93e3282399f088deb206dc8ea226eadd23daa1566fba766`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
412027f5e40838ec1c9b6b79c925fc96f1d36dbaae118d6b328540515faf0947  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
eea5461a6811848d37c04e397d53720baecb1a85f4a3eb844e02784cb61c066a  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
58a52760af64a7b6a298141b23e71aca6fdf94da9e9bc6bd5b5484f385a2fe19  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
f57e59e7cda027b86a4cbf13b34105848d485d0058b9199c1c862ffa0ddf5db5  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
51d4876c45a876c603a31e13566ded9224a4fa73d1d9961ba3647e1820395538  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
778e11dd24d737ae3755ba2a31b7d0e21b0e64d9287fc030147696e9e0d02c53  frontend-js/src/app/acquisition-data/views/sources/index.vue
c347c33b899a029684732ad2a2e5e0753f86846a6efc24196b0c09d961fbbb80  frontend-js/tests/module-registry/acquisition-data.test.mjs
033124b98b5185f525e5490d084e96807ac224b13d6719046db13e344f0924cb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
11aef1d39602696ada37483eca570353d2423c6183b04d517daeb114d1177d3a  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
0e2d0df131aa93eb9317e691e2a3f58e34d4ce5e91c9d3a2859dd787ab00273f  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
4f0a249aa4dec4a0e07d0b78e396c578ae7d69b07c04356041add3f8693543a5  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
d1acbaf6109d9f08869a3a40ac4c016597507b76808ad8f49cefbe39d6425d0b  automation-world/data-acquisition-agent/src/locales/en-US/common.json
0b3eb31b60861cc03113027cf18a722b660e2471ab7b2593aa73f546c95cc3de  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
91cabe56534b2855b44eb3a39d1f86c0ea305216daa5174914d158e844bbdffe  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```


## QA2 修复与第三次 Development handoff

- 2026-11-13 Asia/Shanghai，按独立 QA2 的三项复现修复同一批准的 ARCH-ACQ-004 r2；[QA2 checklist](checklist.md) 原样保留，SHA-256 `be8b6558f7a309a9f8c6f9abb96cbf94cb8dce7cc4cc97572f830ee674cc349b`。批准 spec SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树，未创建 commit。上面两轮清单和实际证据保留；以下 64 项为本次 rework 候选。
- QA2-01：仅来源管理路由的 Request 子类将不合法 JSON 或 UTF-8 延迟到原有身份依赖之后作为必填正文验证失败；未变更共享鉴权或 Pydantic 声明。实际 POST/PATCH 路由定向测试对 `{`、非法字节 `0xff` 和 JSON `null`，分别核对匿名/无效 Bearer 的 401 与挑战头、普通用户 403、管理员 422 `invalid_request`，业务 session 未调用；现有实际生成管理 OpenAPI 与已发布 JSON 的语义对照通过。
- QA2-02：Web 和 DAA 设置按后端 Unicode 空白及有效 UTF-8 语义校验 1–128 字节，保留 U+FEFF 原值、接受合法 emoji，拒绝两端 U+0085 与单独代理码位；两端真实 Vue setup 对新增/编辑、手填/粘贴的实例、PLC、代次分别覆盖，以及空白、控制字符和字节上限。既有标识编辑和粘贴均保持原字符串，不做规范化或替换。
- QA2-03：DAA 设置保存单独保留本地错误；CAS 冲突在弹窗内显示中英文提示，要求先记下未提交内容，关闭并重开后核对当前设置。冲突时未提交表单不变，保存按钮禁用，程序不自动重试；其他保存错误同样在弹窗内反馈。成功保存后才关闭弹窗。

### 本轮定向自检

- 后端在不含 `.env` 的临时副本，以显式合成配置和 `127.0.0.1:1` 作为不会连接的占位，`uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py`：退出 0，17 passed。覆盖 QA1 已修复路径和上述新增权限/Unicode 情形。没有访问数据库。
- Web `node --test tests/module-registry/acquisition-data.test.mjs`：退出 0，12/12；`pnpm build --outDir <自有临时目录>/web-dist --emptyOutDir`：退出 0，包含模块装配检查与既有大 chunk 警告。角色页面访问测试变量为 `[]`。
- DAA `node --test tests/facts-delivery.test.mjs`：退出 0，5/5；`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir <自有临时目录>/daa-dist --emptyOutDir` 均退出 0，有既有依赖注释和大 chunk 警告。新增标识回归针对实际设置 SFC 的手填和 JSON 粘贴。
- 以复制并加强的协调者 `daa_settings_smoke.cjs` 和上述构建，在无头 Chrome 使用合成 Tauri IPC 跑 `--require-localized-conflict`：退出 0。检查中文冲突提示实际位于弹窗上层、待保存字段保留、保存按钮禁用，短暂等待后提交次数仍为 2；关闭重开读回旧设置且保存重新可用。首次在沙箱启动 Chrome 被拒，随后仅对该合成页面的权限复验通过；不连接后端。英文文案已做 locale 键对称和构建检查，未单独执行英文浏览器动作。
- 九个相对 QA2 候选变化的源码和测试文件，已逐字节对照临时构建/测试副本；`git diff --check` 退出 0。冻结开发采集 OpenAPI 未改，SHA-256 仍为 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。
- 资源：自有临时副本和构建目录 `/private/tmp/arch-acq004-r2-qa2fix.k5brqjf8` 供本轮构建及浏览器合成复验使用，自检后已回收；协调者和 Verification 原有资源不动。未启动 Docker，未访问现有 dev、真实配置、数据库或设备。

### 后续验证边界

QA2 的 `qa_failed` 是保留的独立事实，Development 修复不等于复验通过。请由 fresh-context Verification 核对新候选。真实 MySQL、双进程和管理 Web/API、迁移回退与原生 DAA 到后端的完整链路仍需 Human Owner 明确批准的专属目标；Windows 和实际 profile 采用保持原边界。

相对上一份 64 项清单，本轮变更 9 项：`backend/app/plc_facts/api/source_registry.py`、`backend/tests/test_acquisition_source_registry.py`；Web 来源页面及其 module-registry 测试；DAA 上报设置弹窗、console composable、中英文 locale 和 facts-delivery 测试。以下 64 行包含每项末尾换行，原字节 SHA-256：`ca73b6c12dfc451fe813216cad42fd503a80f0490cd7d53bc67aae433202bc97`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
eea5461a6811848d37c04e397d53720baecb1a85f4a3eb844e02784cb61c066a  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
58a52760af64a7b6a298141b23e71aca6fdf94da9e9bc6bd5b5484f385a2fe19  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
f2be2dc9c70b0597c91f8d42bb3898b6d21c460d504f5b94e824f606f9664828  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
51d4876c45a876c603a31e13566ded9224a4fa73d1d9961ba3647e1820395538  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  frontend-js/tests/module-registry/acquisition-data.test.mjs
033124b98b5185f525e5490d084e96807ac224b13d6719046db13e344f0924cb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
11aef1d39602696ada37483eca570353d2423c6183b04d517daeb114d1177d3a  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
6887cd492991280823cd4430b28d35905b04e82543dafc87616950224592e6e8  automation-world/data-acquisition-agent/src/locales/en-US/common.json
2d4bb629034276b2021f680ecd6c5a1f693d1f5eadb570e888368b98a121e39a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
29f0adf8a0e7d198b813e9cdf60fe52c52e0ccc46e3522c7b4cb9fee0de1f6bf  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```

## 专属 MySQL DEV 自检与第四次 Development handoff

- Human Owner 本轮明确批准：`批准 ARCH-ACQ-004 r2 使用专属 MySQL 8.4.6（127.0.0.1:33404）做合成隔离验证，允许创建和回收本轮专用 Docker 容器、网络及卷。隔离验证通过并清理完临时环境后，再安排 dev 切换。` 此处 DEV 指本次合成测试角色，非项目既有 dev。当前 spec SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`；交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树；QA3 checklist SHA-256 `234915025ea96f171ae36872910e26cba4cc174a88c57179b520749883daee13`，本角色未修改 checklist。前几轮候选、命令和结论保持原样，以下清单是本轮产品修复后的新候选。
- 验证目标为 `127.0.0.1:33404` 的 MySQL 8.4.6，server UUID `5e4fc94b-df14-11f1-bd61-76346c8acc30`，数据库时钟为上海时间；仅使用 `arch_acq004_r2_dev_main`、`arch_acq004_r2_dev_restore`、`arch_acq004_r2_dev_guard` 及该角色受限合成账号。两个候选 API 运行于 `127.0.0.1:38404/38405`，浏览器前端运行于 `127.0.0.1:39404`。
- `backend/.venv/bin/python <本轮目录>/copy_backend.py dev`：退出 0，复制 674 项，排除真实 `.env`。分别对 DEV 的 main、restore、guard 执行 `run_backend.py dev <purpose> <本轮目录>/dev/backend predecessor`：均退出 0，得到精确前驱 `5f7a9c1e3b25`。
- main 首次 `run_backend.py dev main <本轮目录>/dev/backend upgrade` 在真实 MySQL 退出 1：`acq_source_initialization.id` 的隐式 `AUTO_INCREMENT` 与 `CHECK (id = 1)` 同时存在，MySQL 返回 3818。DDL 非事务，实际保留前驱 revision、56 张前驱表和 5 张空的部分新表；重试同一 upgrade 退出 1，正确提示 `source registry objects already exist; inspect and restore predecessor backup`，未绕过守卫。
- Development 在批准的 `backend/app/plc_facts/models/source_registry.py` 明确将该单例主键设为 `autoincrement=False`；迁移从此 ORM 定义创建表，无需修改迁移脚本。`backend/tests/test_acquisition_source_registry.py` 新增 MySQL DDL 编译检查。离线 `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py`：退出 0，18 passed。仅这两个清单文件相对上一轮发生变化。
- 协调者使用前驱 restore 合成库制备只归本轮的逻辑备份，SHA-256 `03ec5dd3f3d496d81d9759473e2053a8d653a88c52ca288dbf5cfa46d389c2f4`，仅重建并恢复本轮 DEV main；以实际 UUID/schema/revision、56 张表的规范化 DDL、673 列及已有两行基线数据核对。修正后 DEV 副本的 674 个文件逐一与交付树一致，副本文件清单 SHA-256 `835469034567fa70b32623677bd93d14b0e06e78fa6a8de9f5c0b671af6116d6`。
- 顺序执行 `run_backend.py dev main <本轮目录>/dev/backend upgrade`、`init`、`users`：均退出 0。精确前驱升级到 `6a8c0e2b4d16`，空旧配置预览和导入完成，合成管理员与普通账号建立。启动 `primary`、`secondary` 后两个进程在下列集成测试期间保持同一候选和目标。
- `backend/.venv/bin/python <本轮目录>/run_backend.py dev main <本轮目录>/dev/backend integration`：退出 0，3 passed。实际 MySQL 和双后端覆盖登记前拒绝、登记后同一原字节 `committed/created` 和 `duplicate`、读授权追加、旧预期冲突、采样事务与接管重叠、旧身份拒绝、新代次成功、无活跃来源的旧历史/水位代次防重、登记与代次导出、含事实和最新水位的前驱恢复、升级和两次导入对账。测试日志 SHA-256 `363efe95801dcb9e99680539ab8ea314ec1d86f9733aaac1a21320aa9faeedf3`。
- `TMPDIR=<本轮目录>/dev node <本轮目录>/dev/browser-dev-smoke.cjs dev`：退出 0，真实无头浏览器通过合成管理员与普通账号登录、DAA 和第三方登记、默认关闭读取、参数复制、追加读写 DB、接管取消与确认、过期编辑 409、列宽拖动 180→228 且刷新保留/恢复默认、双语、窄弹窗和普通用户路由拒绝。私有脚本 SHA-256 `bd2fa2f47eb0c139bd47802912ad5e454c837b8cd209fbb22c7e7daae449c6b0`。初次自动化对 Element Plus 隐藏 input 的 `.check()` 超时，改为点击可见标签并核对选中；列宽初次因确认弹窗淡出且首列滚出视野而失败，等遮罩退出并回滚首列后通过。均为测试操作调整，未更改 UI 产品代码。
- 本次为 Development 自检，不改变 QA3 的 `qa_blocked`。真实过期/撤销/禁用账号、并发 POST、Web 增量后的重复导入、旧 profile 拒绝和真实提交未知等补充覆盖由协调者与独立 Verification 继续；DAA 到该 API 的合成链路尚在准备。Windows、本机真实数据和现有 dev 采用仍需原批准边界。
- 资源状态：本次自己的 API `38404/38405` 和 Web `39404` 暂时保留，供协调者完成当前合成 DAA 及补充验证；自有进程退出和专属容器/网络/卷回收结果稍后追加。没有连接既有 dev 的 3307、真实 profile 或设备。
- 以下 64 行逐项为交付树现有文件，含每行末尾换行，原字节 SHA-256：`1f51828441473e0c3dfb7249bdc5817daf7b107616e3b99036e0a66c7a864773`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
eea5461a6811848d37c04e397d53720baecb1a85f4a3eb844e02784cb61c066a  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
d38205efa2455e9401c2781feab3d4b84a4282fbf7ed4faa76473f52a2159b72  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
51d4876c45a876c603a31e13566ded9224a4fa73d1d9961ba3647e1820395538  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  frontend-js/tests/module-registry/acquisition-data.test.mjs
033124b98b5185f525e5490d084e96807ac224b13d6719046db13e344f0924cb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
11aef1d39602696ada37483eca570353d2423c6183b04d517daeb114d1177d3a  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
6887cd492991280823cd4430b28d35905b04e82543dafc87616950224592e6e8  automation-world/data-acquisition-agent/src/locales/en-US/common.json
2d4bb629034276b2021f680ecd6c5a1f693d1f5eadb570e888368b98a121e39a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
29f0adf8a0e7d198b813e9cdf60fe52c52e0ccc46e3522c7b4cb9fee0de1f6bf  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```

### 协调者合成 DAA 到实际 API 的补充证据

- 协调者在独立临时源码副本追加测试并编译，未改变产品源码。测试补丁 `daa_mysql_probe.rs` SHA-256 `b2104bedc94378481c778db2a5ca4e8ccc33ca4734e416d9439dd1c9b5ca9280`；`cargo test --manifest-path <临时副本>/src-tauri/Cargo.toml --locked --offline --lib --no-default-features --no-run` 后，以专属 TMPDIR 对 DEV 端口运行精确测试 `services::local_delivery::tests::acq004_disposable_mysql_settings_sample_and_takeover`，退出 0，1/1，3.43 秒。
- 合成链路中，两代次共四个单 DB 样本分别获得可靠确认；原字节重放得到 duplicate；未绑定轮只存本地；已退役来源的排队项收到 403，原正文和 SHA 保留且没有伪造回执；历史保留两代次，最新值指向新代次，重开后回执保留。此结果由协调者执行，独立 Verification 仍需复跑并记录自己的判断。

### Development 自有进程回收

- 2026-11-13 12:01 Asia/Shanghai，协调者释放 DEV 接口后，先以 `lsof -nP -iTCP:38404 -iTCP:38405 -iTCP:39404 -sTCP:LISTEN -Fpcn` 核对三项分别是本轮 Python PID 77059、77073 和 Node PID 76690，再向这三个 PID 发送 `SIGTERM`。两个 Python 会话退出码为 143，Node 会话退出码为 0；随后同一 `lsof` 无监听项、`ps -p 76690,77059,77073` 无进程项（两条只读确认均因无匹配退出 1）。
- 两个 Python 进程退出时各打印 `resource_tracker` 提示有 24 个 semaphore 对象将在退出时清理；此处仅记录进程退出和端口释放，不声明已独立盘点全部系统对象。私有浏览器脚本及其余合成资源暂留给独立 Verification；专属容器、网络和卷由协调者在复验后统一回收。




## QA4 分页修复与第五次 Development handoff

- 根据 [QA4 独立记录](checklist.md#qa4-01-管理列表的合法超页返回-503) 修复唯一交回项，QA4 checklist 未修改，SHA-256 `fc6c9df5df2148525c7dd43f99a994307f8e7a4dd453b6b326ae715bd1a4bc91`。批准 spec SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`；交付树仍为 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交改动，无 commit。保留前四轮清单及运行事实，以下为本轮新候选。
- 只修改 `backend/app/plc_facts/crud/async_source_registry.py` 和 `backend/tests/test_acquisition_source_registry.py`：先取得总数，只有目标页偏移小于总数时才向 MySQL 发起分页查询；无数据或超页返回空项，保留原页码、每页数量、总数和总页数。没有改变 API、OpenAPI 或数据写入。
- 在私有副本用合成环境执行 `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py`：退出 0，24 passed。覆盖空登记、首页、末页、首个超页及 `9223372036854775807`、`1000000000000000000000000`，确认不对 MySQL 发出超范围 OFFSET。
- 对已有合成数据的专属 MySQL 8.4.6 `127.0.0.1:33404`，重新启动本轮 `38404` API，以合成管理员实际登录；`backend/.venv/bin/python <本轮目录>/dev/qa4_page_check.py` 退出 0。首页、末页、首个超页和上述两个极大页均返回 HTTP 200；超页 `items=[]`，原页码及 `total=19`、`pageSize=50`、`totalPages=1` 正确。复测脚本 SHA-256 `27a71ba20954f5641136dd382a5c7fbd89f580394880ef62c41d0d02908fc783`。
- 后端私有副本 674/674 项与交付树逐字节一致，副本文件清单 SHA-256 `a03470656e200f20f66754106b3312683feb3be181369075c70d720c59c09335`。`git diff --check` 退出 0。
- 复测后核对 `38404` 的进程是本轮 PID 82668，向该进程发送 `SIGTERM`，会话退出码 143；随后 `lsof -nP -iTCP:38404 -sTCP:LISTEN` 无监听项、退出 1。专属数据库与协调者/Verification 的其余资源仍由协调者统一回收。未访问既有 dev `3307/8000`、真实 profile 或设备。
- 当前是 Development handoff，QA4 的 `qa_failed` 仍由独立 Verification 复验并更新；不表示 Human Owner 验收。以下 64 行是交付树当前文件，含每行末尾换行，原字节 SHA-256：`a005c3a8abe188f55e6c4e25526c91a64adc238a171c301af479a8185de36269`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
9edd7f8b6baa0263752634baf761c3bcd963d1ca01d58b2c10c27332b7c1407b  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
610873ba55cad98961b9786904cc9dfa2e700fc66d9efa449d047bccc888b007  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
51d4876c45a876c603a31e13566ded9224a4fa73d1d9961ba3647e1820395538  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  frontend-js/tests/module-registry/acquisition-data.test.mjs
033124b98b5185f525e5490d084e96807ac224b13d6719046db13e344f0924cb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
11aef1d39602696ada37483eca570353d2423c6183b04d517daeb114d1177d3a  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
6887cd492991280823cd4430b28d35905b04e82543dafc87616950224592e6e8  automation-world/data-acquisition-agent/src/locales/en-US/common.json
2d4bb629034276b2021f680ecd6c5a1f693d1f5eadb570e888368b98a121e39a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
29f0adf8a0e7d198b813e9cdf60fe52c52e0ccc46e3522c7b4cb9fee0de1f6bf  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```



## 采集数据指南补充与文档 Development handoff

- Human Owner 本轮要求把 `docs/acquisition-data-guide.zh-CN.md` 和相关指南更新为采集来源登记及六张表的实际架构；这些文档属于已批准 ARCH-ACQ-004 r2 的指南范围。当前 spec SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`；交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交改动。未修改产品源码、实际数据库或运行配置。
- 采集数据指南补充管理员 Web 登记和采集 POST/GET 的权限边界、六张 `acq_source_*` 登记表及独立读范围、两张事实表和 DAA 本机 SQLite 的分工；说明事务提交后立即生效、旧 JSON 一次性导入和目标配置、复用已有 `.local/dev`、原样本和原身份补传、未绑定样本仅本地、`403` 与 `503` 区分，以及按 `sampleId` 的回执和只读对账。双语 `docs/README` 只调整既有指南索引行，原有示例及读取接口保留。
- 中英文 `STAGE_C_GUIDE` 在历史区之前补充已有 DS/DAA `.local/dev` 和 PLC 配置的复用入口、原队列身份处理及当前来源登记/目标采用链接；修正 ARCH-ACQ-004 r2 已通过隔离独立验证的状态，保留实际 profile 和目标采用的边界。两份 DAA-008 历史区从各自 `## Historical record` / `## 历史记录` 开始均逐字节保留。
- 对照实际 ORM、路由、DAA 本地运行和目标迁移手册；纯文档检查：三份指南当前段落共 44 个相对文件及锚点均存在，采集数据指南的 3 个 JSON 示例可解析，登记表名恰好与模型的 6 张一致，代码围栏配对，`git diff --check` 退出 0。英文历史后缀 23110 字节 SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`，中文历史后缀 20602 字节 SHA-256 `d3fb8a87caf7107eecff4ff6fb74048a87db44b5f6639e2eac179936a7f0b7cc`，修改前后相同。未运行应用、构建或数据库操作；Mermaid 图未执行渲染器。
- QA5 的 `qa_passed` 记录固定的是文档修改**前**的精确第五次候选，原 checklist SHA-256 `6cb87d1e2279a3d42583aed0c595723d0648fdd203a8ba74a898db792cb1d94f` 不变；本次仅文档变更另交 fresh-context Verification。除采集数据指南及两份 Stage C 指南外，前一份 64 项清单其余 61 项字节未变；两个 README 索引原本不在该清单，现额外固定如下：
  - `docs/README.md` SHA-256 `83f7dcebd06f045addff423b2516cddce6f67e96da96e3ccb45a313c2e16e1f8`
  - `docs/README.zh-CN.md` SHA-256 `860104ff9f92068e0e5b9631eed7dd7ca6f2550f1839bf0aebe7e792569325b5`
- 以下 64 行固定本次工作树文件，含每行末尾换行，原字节 SHA-256：`7a327ceda201bd9659ca875dd4ae6a376b518fda857d50c30f47b89a1d8f05e2`。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
9edd7f8b6baa0263752634baf761c3bcd963d1ca01d58b2c10c27332b7c1407b  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
610873ba55cad98961b9786904cc9dfa2e700fc66d9efa449d047bccc888b007  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
df76386a1e8cadd33502c5f636e141acddf5e7d13d84c50dcfa310996e2f70cf  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  frontend-js/tests/module-registry/acquisition-data.test.mjs
cc1c56caf1aac167af1a252bc5728124476c4532e784fce9a83c2d64a1694b99  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
b89908d198abcc935379df8c1afa6f85af1ca73f85f72506af6fa2c90a4e3beb  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
6887cd492991280823cd4430b28d35905b04e82543dafc87616950224592e6e8  automation-world/data-acquisition-agent/src/locales/en-US/common.json
2d4bb629034276b2021f680ecd6c5a1f693d1f5eadb570e888368b98a121e39a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
29f0adf8a0e7d198b813e9cdf60fe52c52e0ccc46e3522c7b4cb9fee0de1f6bf  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```

## QA6 文档返工与 Development handoff

2026-11-13（Asia/Shanghai）。本次按同一已批准 ARCH-ACQ-004 r2 返工 QA6，仅修改中央采集指南与中英文 Stage C 三份文档；不修改源码、规格或 checklist。输入 checklist SHA-256 `13afe28b7b3c0778e9a448683a05b7b99ea9fcc7d7ce018dee28a45e8fda71b3`，先前 QA5 产品候选与 QA6 记录均保留，不能把产品候选的 QA5 结果扩展为本次文档复验或 Human Owner 验收。

- QA6-01：区分按 PLC / DB 范围读取的 `403` 与历史详情不存在、过期或超读范围的 `404 plc_facts_v2.not_found`。
- QA6-02：DBX 查询使用合成的两个 MySQL 字符串字面值，并提示替换为实际实例与样本 ID；查询列对照事实表模型。
- QA6-03：两份 Stage C 的已有 dev 授权链接文字改为 DAA-010 §7；待传可能尚未冻结，已冻结或尝试过的记录只核对详情中已有的目标、正文和回执。原身份继续保全。中文 QA5 链接后另起段落。
- QA6-04：在仍被当前来源准入且未过期的条件下解释 `duplicate` / `409`；补充接管后的 `403`、过期的 `410 plc_facts_v2.expired_unconfirmed` 和保留记录的处理方式。

**DEV self-check。** 在交付树运行 Python 3 标准库静态检查：五份文档现行部分 90 个相对链接及锚点无错误；3 个 JSON 块可解析；DBX 查询含两处合成 MySQL 字面值；四项返工相关文字存在；中英文 Stage C 历史部分分别保持 23110 / 20602 字节及此前交接摘要。首次链接脚本错误地把存在的目录链接当作文件，报告 4 项，修正检查器接受目录后复跑退出 0。`git diff --check` 退出 0。此为文档静态核对，未打开 DBX、执行 SQL、连接数据库、启动服务或设备；保留原有实际目标、Windows 和原生界面验证边界。

精确交付为工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交修改；规格 SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`。64 文件清单相对上次交接仅上述三份文档改变；清单原字节 SHA-256 `3a62a9a3053f3dd817fdeb6761bed2780354638b103945efd5545cfa3b0c9490`。既有两份目录索引保持不变，`docs/README.md` SHA-256 `83f7dcebd06f045addff423b2516cddce6f67e96da96e3ccb45a313c2e16e1f8`，`docs/README.zh-CN.md` SHA-256 `860104ff9f92068e0e5b9631eed7dd7ca6f2550f1839bf0aebe7e792569325b5`。交 fresh-context Verification 独立复验。

```text
abed57c75b79b3c07035b975bd58f593c089f1a8c426c67c41c17288b7ba7dbf  CODE_INDEX.md
e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924  backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py
f4bc7cc1e255636852c2388c58cecb28f18a9797f506641d05010a07b6e6e931  backend/app/plc_facts/README.md
53075996f9e806e128c64d8a4ccd1e39c7b306c60a06911c746d9eb346c491cd  backend/app/plc_facts/README.zh-CN.md
2d0053df3441e8bfb137b09d41524e20be96ba27f4bd74d2a4f81305723dedea  backend/app/plc_facts/api/source_registry.py
29d72367445de5e6a272b5a7bc4a4d7f48d84755ba25547b7514ce98a420b7f7  backend/app/plc_facts/api/v2.py
9edd7f8b6baa0263752634baf761c3bcd963d1ca01d58b2c10c27332b7c1407b  backend/app/plc_facts/crud/async_source_registry.py
978ed3bdf1b71be2b51ec2008a6bfd4e736f29df0afa4751a566bc6c7b1dab44  backend/app/plc_facts/manifest.py
5724fd1bbf453c5545f4333c4baa19b24019833b481b8983c23352fb522c9633  backend/app/plc_facts/models/__init__.py
ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8  backend/app/plc_facts/models/source_registry.py
70746ba284f60e5aab367b0fc3a9e542a10466f94595d8f3b0a6a22a49d2e579  backend/app/plc_facts/schemas/source_registry.py
e1cff840381162bcb86c28ba667dd38bf6414f78186e0100fe3805fe35a7583a  backend/app/plc_facts/services/async_source_registry.py
6823b34a4a74d6610e255ba8129050c706b184ab9477bea2fb93396f10d33dd2  backend/app/plc_facts/services/async_v2.py
2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968  backend/app/plc_facts/services/sync_source_registry_import.py
9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905  backend/app/plc_facts/v2_config.py
58530b524018d027719e8cbdb4b8c45f5a51e7c99049f967b483f3216bdd0cd0  backend/common/integration/storage.py
2c0e44535142924be7c740f9b87446b8c9e79adb1872635d2be80b08fe32595c  backend/scripts/business_time_adoption/README.md
60ea70fc4f723938689c087e1574f71b935d06bc54de00852e58085637b7cc8a  backend/scripts/business_time_adoption/README.zh-CN.md
3e43ab1a2e345c8aa3985ca6fe0f68b7002589b1fe91f757390498e4f82d34fe  backend/scripts/plc_facts_maintenance/README.md
6a2fb1585681b96704ef591be9a1061c4148c9898cc105fff8a36f6925fe77f5  backend/scripts/plc_facts_maintenance/README.zh-CN.md
ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14  backend/scripts/plc_facts_maintenance/main.py
cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a  backend/scripts/plc_facts_maintenance/source_registry.py
610873ba55cad98961b9786904cc9dfa2e700fc66d9efa449d047bccc888b007  backend/tests/test_acquisition_source_registry.py
6f1d79c686d24ffe2bb52af9c4e9e6a9d40f2ade0b2f446e16431d8c0a6c82b6  backend/tests/test_acquisition_data_browse.py
69b64aa288d9d41b6e91f036d68be6e0fae6d9919429ca7a069cf9a535f9ec41  backend/tests/test_equipment_temperature_migration.py
72a256840f935d76e6206a81a27cd9a4ba4bb64b250f611cc5dbb1464da2ed3c  backend/tests/test_legacy_acquisition_retirement.py
704460647d2ae30a8b03aba306f763e79dc2f97cd503d004b4719f7744ef2b71  backend/tests/test_mapping_migration.py
0bede3b9d48a31365e152512d7ea1649f96a21276da17a9387f0455e3f5d1335  backend/tests/test_plc_facts_v2.py
de6fdec4ac4ba2b945d7efce2444d28e29f89c2eefa2f715c559870ab2fbbba2  backend/tests_mysql/test_acquisition_source_registry.py
4314f4286c522d3059853c42271dbe064939534ff1307e1823977c1b5c001326  contracts/published/http-api/plc-facts-v2/README.md
5c1846f70a08fcf3c0ccd996414c823ac98c602870514f226d744ca83dd5e8ca  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json
0dec414bae02916e62a792ee9c9aab4e1f268492922e3b86c08aea300970c664  docs/acquisition-data-guide.zh-CN.md
406160861026efe379d54834c370562d3679b95699c0f416a90a5c1ca81e99a5  frontend-js/src/app/acquisition-data/api/index.js
d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381  frontend-js/src/app/acquisition-data/locales/en-US.json
14e1e99fad45fd437d2be38dfb27ffd50a3f8b74be67082321826417c918e585  frontend-js/src/app/acquisition-data/locales/zh-CN.json
3e567fd1ece4e0e3e1fc407476aed5a6dba97daec42008ee7a40831b4a1d5f41  frontend-js/src/app/acquisition-data/manifest.js
4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c  frontend-js/src/app/acquisition-data/views/sources/index.vue
0e5a76ab8a2ba5526fd7dd24d8ebec480463328d01cdc1d5b4761d560c6e53d7  frontend-js/tests/module-registry/acquisition-data.test.mjs
b5dca306f7865003ee2f7cd203a3afb892d9c31433e5b6a0bb7e88185fd63d4e  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
621778efe38ec663aac2618fd3714b47ee365d8f8c3652bb2c3b0104f2eb2d49  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925  automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs
ac777ca60b6f4f90350925a39bd25e4abe5a978a19540762b68862df255ffaa2  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md
5d47e3586b575beeb3a561be30a49b7b4139270b95324cddffafea0d035ae956  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md
3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/delivery.rs
f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs
26b80d0aec2ac4b9d9b738a455336929bcd1d44d1e640d464b46f96856ffb364  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs
511ada1edafb8877f020a80040c2c294893507f2d70a9ab0e82d92d6e5f65820  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract_tests.rs
fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs
038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs
b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
9c9c29e13712ea30ca81cf3480993191ef20e37b2a072b075dcdf057e1f78f1f  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs
3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669  automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs
8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs
21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2  automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs
5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25  automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs
ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c  automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue
dad3e648c18b19935c6dc6ea07cd1900a453a397083308d6bc6e5ebd6e07cfaf  automation-world/data-acquisition-agent/src/components/console/LocalSampleDetail.vue
6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500  automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts
6887cd492991280823cd4430b28d35905b04e82543dafc87616950224592e6e8  automation-world/data-acquisition-agent/src/locales/en-US/common.json
2d4bb629034276b2021f680ecd6c5a1f693d1f5eadb570e888368b98a121e39a  automation-world/data-acquisition-agent/src/locales/zh-CN/common.json
6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb  automation-world/data-acquisition-agent/src/services/factsDelivery.ts
4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6  automation-world/data-acquisition-agent/src/services/localAcquisition.ts
29f0adf8a0e7d198b813e9cdf60fe52c52e0ccc46e3522c7b4cb9fee0de1f6bf  automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs
```

</details>

## r4 已授权 dev 目标采用记录与 Development handoff

2026-11-13（Asia/Shanghai）。在 r4 源码及隔离验证的 Human Owner 最终验收之后，Human Owner 针对本机既有 dev 目标的单次采用明确表示：

> 不用备份了，直接开搞，旧的记得清理。
>
> 测试遗留记得清理。我授权批准你用alembic

本次是该具体目标的环境操作，不修改 r4 产品源码、规格或原 QA/验收结论。Human Owner 明确选择不建立本次新备份；因此不能声称有本次新备份可恢复。旧私有 JSON 保持原文件和原字节。只清理本操作拥有的临时目标文件，不对历史事实执行到期清理，不删除已有配置或其他任务资源。目标私有 UUID、路径、账号及 PLC 标识不写入本仓。

- 调用项目环境 `uv run --no-cache --offline --frozen --no-sync python` 执行只读预检，核对已批准本机 dev 目标及旧 JSON 的 schema/UUID、MySQL 8.4.6、上海时钟、六张空旧表、原 revision `6a8c0e2b4d16` 与 2 条来源；旧只读而未登记 PLC 为 0，当前有效事实中新开放读取的 PLC/DB 组合为 0。协调者核对并停止旧测试后端，后端/Web 手测端口在迁移前未监听。默认沙箱对 uv 原缓存的首次访问被拒，改用 `--no-cache`；该次未连接数据库。
- 对照已验证夹具检查冻结 r2 的 7 个关键源码 SHA 与 r4 Alembic 文件 SHA，全部一致。旧测试副本自带仅限合成端口的 `sitecustomize.py`，保持副本原字节并以项目 Python `-I` 运行其 CLI；CLI 自身目标、UUID、schema、revision、来源 SHA 和确认串守卫均未绕过。
- 冻结 r2 的 `import-sources --plan` 退出 0，预览 2 个实例、2 条 PLC 登记，旧读、写范围各 2 项；`--apply` 按预览源 SHA 和精确确认串退出 0、`created`。再次 `--plan` 退出 0，初始化标记及当前登记的逻辑 SHA 与导入前预览一致。仅此次导入写入旧登记表，未写入样本。
- 在已授权本机 dev 目标运行项目环境 `python -m alembic upgrade 7b9d1f3a5c7e`，退出 0。目标版本、时间和前驱守卫通过；两张事实表迁前、迁后的结构及全部有序行 SHA 一致，历史 4 行、最新值 3 行，含原始样本与最新水位。迁后只读核对 revision 为 `7b9d1f3a5c7e`，新表 2 条来源的 PLC、实例、代次和来源标签逐字节对应旧配置，旧六张登记表均不存在；两事实表行数与迁前一致。

  以下为该次 Alembic 输出的 `facts-before` 与 `facts-after` 中相同的脱敏摘要，直接记录原输出，未重跑迁移：

  | 事实表 | rowCount | schemaSha256 | rowsSha256 |
  | --- | ---: | --- | --- |
  | `plc_facts_history` | 4 | `74146bed9508cd388647259581ab218b8c791dd8e765828363bd25373dbb8170` | `a4b7b1831f56d94ea702499611e54c38c6fd65c2a9df478f1e21259481e77564` |
  | `plc_facts_latest` | 3 | `71c48493d0492a01e733847ba3ba3a5d6805785bdb96707396e920781cf4107e` | `ca975202ec48561a465d1f3ae342f489a4b9e5b8cbeb532dd153bd73fc0a0e96` |

- 在旧 profile 同一仓外私有目录独占新建仅含 `target` 的 revision `7b9d1f3a5c7e` 文件，权限 `0600`，项目 `V2Settings` 实际加载通过。`backend/.env` 仅调整 `PLC_FACTS_V2_PROFILE_FILE` 的值，解析后的其余设置完全一致；旧配置未覆盖或删除。未启动 DAA、未调用样本 POST、未写手测样本、未访问真实设备或启动 Docker。
- 本操作自有的临时 `target-r2.json` 和 `/private/tmp/arch-acq004-dev-adopt-ko6p4zeq` 已回收。此前保留的前驱源码材料归协调者核对用途与生命周期，不在本角色擅自删除；原有测试证据与其他并行工作保持不动。

**Development handoff。** 输入 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，本次记录前 tasks SHA-256 `99f33d2bf282193d8200d0c0d66bb1bdfcf897da56849e2a567c0a1beeeafc8c`；工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加既有未提交改动。请独立只读核对 dev 目标 revision、来源一致性、事实和运行配置后，再由 Human Owner 自己进行 Web/DAA 手测。该 handoff 不代表实际设备联调、手动验收、生产部署或发布完成。
