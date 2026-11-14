Task ID: ARCH-ACQ-004
Revision: r4
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: Human Owner 已验收 ARCH-ACQ-004 r4 的源码及隔离验证。dev 手动测试由 Human Owner 另行执行。
Workflow Mode: STD
Fresh Context: true

# ARCH-ACQ-004 r4 独立验证

2026-11-13（Asia/Shanghai），命名 Verification 在 fresh context 独立复核正式树及任务交接。已核对批准规格、Development 清单、历史 checklist、根与最近作用域契约、实际实现、差异和可用日志。验证覆盖项目治理、工业边界、后端/API/MySQL、维护脚本、Web/Vue 和中英文文案，分别按 `project-governance`、`aiis`、`backend-arch`、`backend-script-tooling`、`frontend-ui`、`i18n-workflow` 及浏览器用 `playwright`。 [规格](spec.md) · [交接](tasks.md#r4-development-精确交接) · [工作流](../../.codex/workflows/development-lifecycle-workflow.md)

## 候选与环境

- 正式树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树，spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，tasks SHA-256 `c28128b701577407eb2b6536700f2c5f9d11de5cae7fd252338273f952b89ed0`。交接文件 `manifest.txt` SHA-256 `922a75e9a57dac4ff9862ecace4fa6f8c5ce149a875560e79fe4e12cabf640c8`，其中 34 条集成路径与基线、正式候选的摘要均匹配；另六条为 DAA 并行项。独立副本固定 backend/contracts/frontend-js/docs 915 个文件，清单 SHA-256 `634c71268434bd78ada29aff52e530ab075d7b04889e277cae26776d23f210e7`，保留正式源码路径集的隔离快照和跟踪差异；四条在 Git 中已有差异的 manifest/domain/API facade 路径与 r4 实际前驱一致。历史迁移和旧两份 OpenAPI 保留前驱字节，SHA 分别为 `e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924`、`971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`、`2892f8b795207559a75037bca590f19ec8f637ec6c033f1e245aa4da5c50d1ad`。
- macOS 15.7.7 arm64，项目 Python 3.13.3，Node 22.19.0，pnpm 11.11.0，Vite 5.4.21，Chrome 157.0.8103.78。使用已安装的锁定依赖，测试、编译输出、Chrome profile、合成运行配置和日志写入私有目录。隔离副本未复制真实 dotenv、真实历史或 profile。MySQL 仅为 Human Owner 批准的任务专用 `127.0.0.1:33404`，8.4.6、UUID `43b1c562-df4b-11f1-83c9-72f35d3e7827`、会话 UTC+08:00。七个 `arch_acq004_r3_qa_{main,restore,guard,initialized,json,empty,failure}` 逐个核对目标、非 root DDL 角色及空表，main 另核对 app 角色。进程 socket guard 限定 QA 本机地址与端口。API 仅用 38406/38407，构建后的 Web 仅用 38416。使用实际合成 admin/operator 登录。
- DAA 的本轮源码只读观察固定到 `FactsDeliveryDialog.vue` `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd`、`services/local_delivery.rs` `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2`、`domain/sample_upload.rs` `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b`。这三项与本任务 Development 分段联调记录的三个 SHA 均不同。DAA-013 r1 返工交接 SHA `0cc6e79e1a737b8c6d6af75cccb823d2e0fe7ad15f2922909bdebe11011d7580`。其独立 checklist 的当时 SHA `9c37de9e48afa239e66eb576e7172e3ae5e37f30967da6feac3009859fee3f8b`，最新 verdict 为 QA2 `qa_failed`，F-DAA013-QA2-001 记录旧候选超时保存延迟提交后 worker 仍向旧地址发出新 POST。返工 handoff 已出现，故该反例只归 QA2 候选。当前返工候选的独立复验及联合链路仍需实际证据。 [DAA-013 交接](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/tasks.md) · [DAA-013 QA2](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/checklist.md#f-daa013-qa2-001--超时保存延迟提交后仍可向旧目标派发)

## 逐项验收

| 编号 | 结果 |
| --- | --- |
| R4-AC01 Web 与管理 API | **通过。** Chrome 实际登录，四项表单、无 DB 字段，分别对两条已提交的记录显示并一键复制三标识，剪贴板与显示逐字节一致，并与各自 POST 响应逐项一致。覆盖中英页面、普通用户菜单与直达拒绝、匿名和非管理员管理接口拒绝、标签独立编辑、显式接管弹窗显示新旧三标识及取消、外部编辑后旧版本 409。并发相同 POST 得 `created/unchanged`，管理审计日志包括操作者、PLC、前后标签及结果。 |
| R4-AC02 通用上报与回执 | **通过。** 双真实 API、独立 HTTP 客户端及 Chrome 复制出的身份分别覆盖两台同实例和异实例 PLC、每台 DB21/22；核对回执完整信封、实例和 sampleId、`committed/created` 及原字节 `duplicate`。MySQL 历史归属和当前最新点位一致。DAA 标签可省略两个可选字段，第三方可省略或填 null；错误实例、其他 PLC 的代次及未知 PLC 均 403，DB 0/65536/布尔及额外 `sourceType` 均 422。 |
| R4-AC03 读取与可见性 | **通过。** Web 实时、历史筛选使用实际 DB21/22 选项并打开样本详情。五条 GET 验证按 PLC/DB/点筛选、先过滤再计数分页、已登记无数据、未知 PLC、过期与不可见详情；迁移夹具证实旧未开放的 DB22 可读，原只有读取授权且未登记的 PLC-孤历史保留、详情 404。接管后旧历史仍可查、实时仅显示当前代次，标签编辑后实时显示新标签、旧历史保留写入标签。 |
| R4-AC04 联合接入与接管 | **后端通过，联合链路阻塞。** 实际 MySQL 两事务持锁验证上报提交与接管顺序，旧身份和已用代次拒绝；两 API 并发接管 200/409，原字节在接管后 403。两条 Web 三标识的实际剪贴板及独立发送方已验证。DAA-013 QA2 的反例仍待对返工候选独立复验，本轮未在同一个真实 Tauri UI 与持久化 SQLite profile 上完成逐 PLC 粘贴、保存、重开、显式开始、同/异实例多 DB 及迁移前队列原身份原正文回执。Development 的旧候选内存 IPC 与合成 Rust/SQLite 到 API 分段结果不覆盖这条整链。 |
| R4-AC05 迁移与指南 | **迁移和第三方示例通过，指南合同失败。** 完成 r2 已初始化、待导入 JSON、确认空登记直迁三路径，覆盖历史 r2 原迁移、原事实内容与列结构、逐点水位、身份/退役代次、只剩单登记表及部分 DDL 独立前驱恢复。空表通过真实 Web 创建首行并成功复制。使用根指南 JSON 替换合成标识和当前采样时间，实际 POST 两 DB 并校验回执、读回。两 OpenAPI 工件与运行路由的操作/Schema 完全匹配。公开双语合同两处叙述、Stage C 的单表步骤和中文链接仍不一致，独立按指南走完 DAA 原生流程依赖 AC04。 |

## 失败与返回项

1. **R4-QA-01 · 双语事实合同遗漏重复回执的当前准入条件（R4-03、R4-06）。** 两版公开合同第 46 行把有效期内同实例、同 ID、同正文的重试写成返回 `duplicate`，缺少当前 PLC 登记仍匹配的条件。独立双进程实测同一原始字节首次 `200 created`、重试 `200 duplicate`，接管提交后同一原始字节返回 `403 plc_facts_v2.scope_rejected`。根指南第 208 行已正确说明两个条件。要求公开合同把条件写在补传规则处，并核对相邻 409/403 说明。 [英文合同](../../contracts/published/http-api/plc-facts-v2/README.md#commit-and-retry) · [中文合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#提交与补传) · [实际重试实现](../../backend/app/plc_facts/services/async_v2.py#L39)
2. **R4-QA-02 · 双语事实合同错误归属来源标签（R4-01、R4-03、R4-06）。** 两版公开合同第 20 行的 `instanceId` 字段说明称该字段“匹配来源类型”或 “resolves its source type”。实测同一实例可给两台 PLC 分别登记 `external` 和 `daa`，各两份样本按自己的 PLC 登记行持久化标签。实例 ID 是准入三标识之一，也是样本 ID 去重范围；来源标签来自各 PLC 当前登记行并在写入时保存。 [英文合同](../../contracts/published/http-api/plc-facts-v2/README.md#sample-fields) · [中文合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#样本字段) · [准入](../../backend/app/plc_facts/crud/async_source_registry.py#L14)
3. **R4-QA-03 · Stage C 接入步骤只覆盖旧目标且中文迁移链接失效（R4-05、R4-06）。** 英文第 100/105 行、中文第 102/107 行要求 r2 DB 授权，步骤 4 无条件要求读取范围覆盖。现行根指南链接到这两份说明中的 DAA 操作章节，已采用单表目标的使用者仍缺对应分支。中文第 9 行还链接到不存在的 `#r2-候选迁移导入与恢复`，维护手册现标题为「r2 候选：迁移、导入与恢复（冻结前驱工具）」。指南固定 SHA 英文 `4b6854fed2a742ef3efa4f7e2e1a45b57cb9eda144f7b8d21651d4ee99e3c982`、中文 `dda01608f7ee820cefe28e330cf07673cdcf593e626ccd6e6048bf0105ccbcc5`。由 DAA-013 归属方区分旧 r2 目标和已采用单表目标，修复迁移链接后与中央指南一起复验。 [英文 Stage C](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.md#6-register-sources-and-start-delivery) · [中文 Stage C](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md#6-登记来源并开始上报) · [维护手册](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md)

## 独立命令与结果

在正式仓库执行下列命令时，`Q` 指任务私有目录 `/private/tmp/arch-acq004-r3-qa.PVvRygAh`。网络命令仅为上述已批准的合成目标经工具权限运行。

| 命令 | 退出码与证据 |
| --- | --- |
| `shasum -a 256 plans/ARCH-ACQ-004-acquisition-source-registry/{spec,tasks,checklist}.md`、标准库 SHA 对照及 `git diff --check` | 0，34/34 基线与候选匹配。冻结前驱副本中 700 个对应文件匹配；测试副本排除了两个无关嵌套 `sitecustomize.py` 和 dotenv，MySQL 迁移夹具校验了运行旧工具的七条关键 SHA。 |
| `backend/.venv/bin/python "$Q/qa.py" setup` | 默认沙箱 1，回环连接 EPERM，未初始化；同一受限命令的许可复跑 0。六个 schema 分别运行 `python -m alembic upgrade 7b9d1f3a5c7e`（main）或 `5f7a9c1e3b25`（五个前驱）均 0，guard 留空。 |
| `backend/.venv/bin/python "$Q/qa.py" offline` | 0，`pytest -p no:cacheprovider -q -m no_db` 对登记、采集浏览、v2 及三组历史迁移测试执行 141 passed、3 skipped。三项为需 ACQ003 实库、冻结 BE012 候选及旧 BE003/60 基线的独立覆盖。日志 SHA `7f1377dc75375cae0a525e218aaf4fdd47ddc6989618cbd2a85f377dfe2a91c5`。 |
| `backend/.venv/bin/python "$Q/qa.py" start` | 0，uvicorn 两实例在 38406/38407，各两种角色真实登录成功。 |
| `backend/.venv/bin/python "$Q/qa.py" http` | 0，`pytest -p no:cacheprovider -q tests_mysql/test_acquisition_source_registry.py -k 'two_running_apis or first_registration or retired_generation'`，3 passed、4 deselected。日志 SHA `b776e0a4e395c9351b33795da77196eb0c0a33674101b40d6ab8ec394d037a7f`。 |
| `backend/.venv/bin/python "$Q/qa.py" migration` | 0，同文件 `-k 'three_predecessor_migration_paths or partial_ddl_refuses'`，4 passed、3 deselected，29.25 秒。JSON 和 empty 在未明确状态时拒绝，failure 在保有部分 CREATE 时拒绝，三次预期失败的子命令各退出 1。initialized/json/empty/restore 的前后两表均各 3 行，结构及排序行 SHA 相同；failure 留在 `6a8c0e2b4d16`，同时保留六张旧表与空新表。日志 SHA `c861acc726302085a04c6d4d151517e71e9b4226995848ad1022c44a8d8b7f2f`。 |
| `backend/.venv/bin/python "$Q/read_probe.py"`、`backend/.venv/bin/python "$Q/replay_and_concurrency.py"` | 各 0。实际第三方示例、五 GET、过期、两 OpenAPI，另验证原字节接管前后及双 API 并发结果。 |
| 在隔离 Web 源码 `node node_modules/vite/bin/vite.js build --outDir "$Q/dist"`、`node --test tests/module-registry/acquisition-data.test.mjs`、`node scripts/check-module-manifests.mjs --check` | 首次构建 1，合成 operator 权限页未加入 supervisor 集合；二者均配置 realtime/history、mock=false 后三命令均 0，Web 12/12，Vite 有 chunk 大小提示。 |
| `backend/.venv/bin/python "$Q/serve_web.py"`、`node "$Q/web.cjs" QA-web3` | Web 启动成功，最终 Chrome 流程退出 0。前三次浏览器入口分别因合成密码超过 UI 20 字限制、选择框隐藏 input 被遮挡、两个可见 dialog 未区分而退出 1。仅修正专用合成账号和验收脚本。最终脚本 SHA `eda707503deb48bcc7eb95badeedc66e16bfa0cb97d2387f64902d778cb75959`。 |
| `backend/.venv/bin/python "$Q/metadata.py"`、`backend/.venv/bin/python "$Q/start_empty.py"`、`backend/.venv/bin/python "$Q/serve_empty_web.py"`、`node "$Q/empty_web.cjs" QA-first` | 只读核对各 schema，维护 `cleanup-v2 --plan` 和裸帮助均 0。空登记 schema 保持 0 行直到实际 Web 创建首行，空库后端启动与浏览器命令均 0，首行复制校验通过。脚本 SHA `ee417a5b2a7cff7c57bb1cbe4bab5f1129ac79559c13508a1110c9792c5f912b`。 |
| `python3 "$Q/docs_verify.py"` | 修正探针纳入显式 HTML 锚点后仍退出 1，110 个相对链接/片段、7 个合法 JSON 块，唯一缺失为 R4-QA-03 的中文锚点。该检查未运行外部链接或 Mermaid 渲染。 |

## Verdict、资源与下一次交接

**`qa_failed`。** R4-QA-01/02 是本任务精确候选的可复现文档不符，交本任务 Development。R4-QA-03 由 DAA-013 归属方处理。R4-AC04 的双候选原生链路及 R4-AC05 的 DAA 按指南实操仍阻塞。待修订文档、DAA-013 返工候选独立复验完成且 Mac 原生 UI 可操作后，固定两候选、专用 MySQL 与同一批样本，重新完成 Web 复制 → DAA 实际粘贴、持久化重开和显式开始 → 同一合成 profile 的新样本与原队列 → API 回执和 Web 读回，交 fresh-context Verification。最终验收由 Human Owner 决定。

本轮专用浏览器上下文已退出，QA API/Web 三个自有进程经 PID 与回环端口核对后 SIGTERM，端口 38406/38407/38416 均已释放，命令退出 0。保留任务私有目录、合成 schema 和 failure 部分 DDL 现场供当前返工与后续联调核对；本轮 QA 已无在线依赖，不使用 DEV 端口。协调者确认后续联调依赖已解除、所需证据已持久化及相关进程全部停止后，按任务授权回收 `arch-acq004-r4-verify-mysql`、专用网络/卷和私有资源。当前证据正文可脱离临时目录阅读。未连接现有 3307、DEV schemas、真实 DAA profile 或现场 PLC，未实施实际环境切换。仅写入本 `checklist.md`。

# ARCH-ACQ-004 r4 独立复验 QA3

2026-11-13（Asia/Shanghai）。命名 Verification 在 fresh context 核验精确交接。**结论为 `qa_passed`。** R4-AC01–05 均有对应独立验证证据，QA2 两项阻塞已解除，历史失败与验证边界保留。交 Human Owner 最终验收。 [获批规格](spec.md) · [本轮交接](tasks.md#r4-迁移前冻结队列的连续链路补证与-development-handoff) · [工作流](../../.codex/workflows/development-lifecycle-workflow.md)

## 精确候选与文档核对

- 正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交差异。spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，Development handoff SHA-256 `99f33d2bf282193d8200d0c0d66bb1bdfcf897da56849e2a567c0a1beeeafc8c`，进入本轮时 checklist SHA-256 `3f1f9f84bb041395098333e9db704b3ceef345dc24848434b27e5fc955a817dd`。已读项目根与最近作用域契约、完整任务 bundle、实现、差异和可用输出。使用 `project-governance`、`backend-arch`、`desktop-tauri`、`rust-runtime`、`frontend-ui`、`i18n-workflow` 和 `playwright`；维护步骤按对应 `backend-script-tooling` 边界复核。
- ACQ 34 路径清单 SHA-256 `b882f7a6da1fc9a6a784b9585c20222db130d23e5e450498a1e995958ca0b9b4`，正式树 34/34 匹配。与 QA2 相比，33 项逐字节一致。唯一差异为中文合同 Swagger 第一步删除「合成来源，。」中的一个全角逗号，UTF-8 共 3 字节。还原该字后与 QA2 的 `f2609bae20b2b130a9a45e6fbc184389fd7b08127364d935d8fb4b1000e7f0b5` 匹配。两份合同均保留有效期和登记三标识匹配的重复回执条件，以及每台 PLC 的标签归属。 [中文合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#swagger-手工测试) · [英文合同](../../contracts/published/http-api/plc-facts-v2/README.md)
- DAA-013 r1 最终 14/14 交付摘要同时匹配正式树与私有快照，采用 QA5 `qa_passed` 的候选。其 handoff SHA-256 `4af58dd5542fbbdd0b7b393a742a808803a54a8694c5931b19f579e72d1ab797`，QA5 checklist SHA-256 `971e5381d45997a19187184539fc4a3e187c2b25a16fed4cceb171fbd97e42e8`。英文 Stage C 指南 SHA-256 `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235`，英文 locale `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc`。QA3 实际按新版英文指南的单表步骤操作。两种语言共 664 个对应 locale 叶键，原生补证副本到本轮每种语言仅两个确认提示值变化，占位符和两份 DAA-008 历史后缀均一致。112 个本地链接、40 个 Markdown 片段和 7 个 JSON 示例通过，外部链接和 Mermaid 渲染未执行。 [DAA 最终交接](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/tasks.md#qa4-返工后的完整源码及指南-sha-256) · [DAA QA5](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/checklist.md#daa-013-r1-独立验证-qa5) · [实操指南](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.md#6-register-sources-and-start-delivery)
- 后端、Web、DAA、共享 UI、TIA 导入库与合同私有快照共 1483 个普通文件，清单 SHA-256 `74c76790a199a633002bbb2b65db281130260b091dab64ddac99495dbbdf8d0f`。运行前后核验正式树 1483/1483。隔离副本变更限 Tauri 应用名、窗口名、bundle ID、回环 dev URL，以及在原生编译完成后向测试文件追加独立合成夹具。原生二进制编译 SHA-256 `0ee7cccbe2959d9fd5597c466959bb77a161a8f286a1f0386613b7b6592392db`，本地临时签名后二进制 SHA-256 `9127b68d89b83215202153676c0abfd6f4fee67caf7cf23cadfafebe678c8712`。复核 QA1 后端/Web 对应路径字节、141 passed/3 skipped 离线日志、3 项 HTTP 与 4 项迁移测试日志均匹配原 QA1 记录。

## R4-AC04 迁移前冻结队列

独立读取留存的前驱和后继源码、编排、日志与原文，再用 SQLite URI `mode=ro`、`query_only` 和专用 app 用户 SELECT 对账。两代 DAA 各 97 项、两代后端各 572 项与对应源摘要核对一致，隔离副本中的两份 Rust 差异只追加 test-only helper，后端副本的环境保护差异为 `sitecustomize.py`。验证该 helper 前驱只准备原文，后继以实际 `LocalEngine` 打开原 profile 后使用 worker 发 HTTP。相同专用目标 `127.0.0.1:33404`，MySQL 8.4.6，UUID `43b1c562-df4b-11f1-83c9-72f35d3e7827`、`arch_acq004_r3_dev_guard`、UTC+08:00。两代私有目标配置均指向此 UUID 和 schema，对应 revision 为 `6a8c0e2b4d16` 与 `7b9d1f3a5c7e`。本轮以已保留的真实迁移运行证据结合实际数据库独立对账，未重新执行迁移。 [冻结补证交接](tasks.md#r4-迁移前冻结队列的连续链路补证与-development-handoff)

| 证据 | 实测结果 |
| --- | --- |
| 迁移前原文 | DB1，sampleId `908c2bbb-3a55-4c07-8ceb-07b72b26c72b`，三标识 `acq-frozen-instance` / `acq-frozen-plc` / `acq-frozen-generation`，原目标 `http://127.0.0.1:38410/api/v1/integration/plc-facts/samples`，`prepared`、attempt 0。重算原正文字节 SHA-256 `e00e5abce79d73d4942b0a1f91f01f74782c89d567f9523e40f2101109b6ee63`。旧 API 日志无该 POST。 |
| 同一账本与实际回执 | 同一 profile 的 SQLite inode `84370819`，三标识、DB、sampleId、完整正文字节、摘要及目标均等于旧快照。账本现为 `acknowledged`，唯一一次尝试的目标相同，完整 JSON 回执合同为 `plc-facts/v2`，实例和 sampleId 匹配，`committed/created`，回执 SHA-256 `9e07717c446de3d27851bbaac0568ee86120ede55195ad8f4425a00ec59266ae`。样本时间 20:13:46.070，迁移运行日志开始于 20:14:59.631，新 API 同 sampleId 提交事件为 20:15:07.024775，SQLite 确认为 20:15:07.025（均 +08:00）。 |
| 实际 MySQL | 查询时 revision 为 `7b9d1f3a5c7e`，单行登记三标识不变。唯一 DB1 history 行与原始 SHA-256、三标识、sampleId、序号、group、配置 revision 和 `daa` 一致。12 个 history 与 12 个 latest 点值、类型和质量匹配，REAL 按实现的数值文本用十进制精确比较。有效截止 2027-02-12 20:13:46.070 +08:00。跨迁移的原字节断言限 DB1，另一个 DB2 是先前未冻结队列。 |

对 QA2 的两轮原生操作再次以只读探针复核。E/F 共用实例、C/D 各用不同实例，每台 DB21/22，仍为 4 条登记、8 份 exact-body 可靠回执和对应 history、96 个匹配 sampleId 的最新点。QA2 的早期原生 UI 与最终候选的运行差异经源码比对限两种语言各两条确认提示，另有私有 `cfg(test)` 夹具差异。QA2 的一部分 IAB 到原生粘贴曾用 CUA 转交 Web 显示文本。下节用最终候选实测了系统剪贴板。接管事务与旧身份、已用代次拒绝沿用 QA1 在相同后端字节上的运行证据。 [QA2 同／异实例证据](#联合证据和逐项结论) · [QA1 接管证据](#逐项验收)

## R4-AC05 最终候选按指南实操

1. 解锁的 macOS 上以 headed Chrome 登录合成管理员。在 38416 的 Web 用四项登记 `acq-r4-qa3-native-A`，真实 POST 返回 `created`。从已保存行点 **Connection parameters** → **Copy parameters**。显示 JSON 和浏览器剪贴板逐字节相同，含且仅含 instance `acq-r4-qa3-instance-A`、PLC `acq-r4-qa3-native-A`、代次 `acq-r4-qa3-generation-A`，复制文本 SHA-256 `d84ebd57551a4ef376b13bca6e66ada531c6dee0e7c9debcd0b09b903f082f97`。
2. 在真实 Tauri 原生 DAA 的 **Reporting and storage → Delivery settings → Reporting sources** 选择 Fixture 31001，点对应行 **Paste**，用 macOS `Cmd+V` 读取 Chrome 写入的系统剪贴板。观察到三项准确进入原生文本框，未以 CUA 文本转交。点 **Fill form**、**Save settings** 后仍为 Stopped，重开设置核对三项及完整回环地址。Fixture 31001 的本地 DB 列始终为 DB1、DB2。采集读取门禁为 `DAA_PLC_READ_ALLOWED=false`，通过测试夹具代替指南的采集轮。
3. 退出原生程序后用独立 Rust 测试夹具复用同一新 SQLite profile（runtime inode `84462071`），以 UI 已保存身份注入一轮 DB1/DB2 合成样本。重启原生程序观察 2 Pending、0 Acknowledged、Stopped。确认前发现夹具第二台 PLC 带测试初始化身份，先取消确认，在 UI 清空未用行再保存。再次确认面板仅显示本轮 PLC 的 DB1、DB2、原三标识和实际目标，显式确认启动 worker。原生显示 2 Acknowledged，运行日志 `sample_delivery_started` 为 20:32:14.319600 +08:00，随后暂停并干净退出。
4. 用 app SELECT、SQLite `mode=ro`、实际 API 事件和五条 GET 独立核对两次尝试均为 1 且各有匹配的完整 `committed/created` 回执。两份 history 请求摘要与 SQLite 字节一致，24 个最新点的身份、类型、质量与原值匹配。五条 GET 返回两个 DB 的选项、两份 latest/browse、两条过滤历史及详情，与原点值逐项相同。回到同一 Chrome profile，Web 按 PLC/DB 筛选实时各 12 点，历史 DB2 打开详情，显示同一 sampleId 和完整 12 个点。
5. 独立 HTTP 另取根指南第三方 JSON，以专用合成标识和当前上海采样时间上报 DB21/22。两份 `created`、各一次原字节 `duplicate`，实际 latest 原值与 `external` 标签匹配。两份 OpenAPI 共 9 项操作与 29 个 schema 和本轮运行 API 完全一致。迁移三路径、前驱故障恢复和空表 Web 首行沿用 QA1 已比对的独立证据。 [根指南](../../docs/acquisition-data-guide.zh-CN.md#6-第三方如何上报) · [QA1 迁移结果](#独立命令与结果)

| 样本 | sampleId | 正文字节 SHA-256 |
| --- | --- | --- |
| DB1 | `1f70f6c0-61e8-4d43-9a1d-fff858e588c1` | `bead490a5f159383d1db9dd0f8dfce5889be811cf04571ba377aed5352ebd6a9` |
| DB2 | `7d8590c5-db3b-415b-b000-0c7085c748d7` | `f8103bfaf90c94b8d8d4d4dee594344f64d5e17f8667f60ba20944af710333f3` |

## 执行与交接

macOS 15.7.7 arm64，Rust/Cargo 1.89.0，后端项目 Python 3.13.3，Node 22.19.0，Vite 5.4.21。下表 `Q` 是 QA3 私有根 `/private/tmp/arch-acq004-r4-qa3.7A0ZjAU6`。自有 API 38406、Web 38416、DAA Vite 38411 都只绑定 127.0.0.1。测试 API 使用专用 QA app 和 `arch_acq004_r3_qa_main`，DEV guard 仅用专用 DEV app SELECT，QA2 历史证据以专用只读账号在 `arch_acq004_r3_dev_main` 重查。无其他 MySQL 端口、DDL/root 或真实 PLC、数据库、profile、历史操作。

| 命令或检查 | 退出码及结果 |
| --- | --- |
| `backend/.venv/bin/python "$Q/setup.py"`、`"$Q/check-frozen-manifest.py"` 与独立全路径 SHA、`git diff --check` | 0。34/34、DAA 14/14、1483/1483，留存两代候选和 QA1 相关路径核对通过。 |
| `python3 "$Q/docs-audit.py"` | 0，112 链接、40 片段、7 JSON。先前 QA3 前驱证据目录由 DAA 协调者回收后，静态脚本改用仍保留且相应摘要匹配的早期原生候选。当前正式指南与 locale 核验通过。 |
| `backend/.venv/bin/python "$Q/frozen_read.py"` | 最终 0。先后修正日志 JSON 转义、REAL 按文本保存的探针断言。默认沙箱禁止回环 MySQL，按已批准目标限制复跑。只读输出 SHA-256 `4677950a29c19aa757d2fb1cf3cff69e18d44c9cab833e54a32b0ee168405905`。 |
| `backend/.venv/bin/python -B /private/tmp/arch-acq004-r4-qa2.peZVG5tN/joint-read.py` | 0。八份旧原生样本和同/异实例实证重查通过。 |
| `cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --features rust-snap7-driver --bin aiis-data-acquisition-agent`；`cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --features rust-snap7-driver acq004_qa3 --no-run` | 最终均 0。首次测试 helper 编译因闭包借用退出 101，修正私有 helper 的所有权后通过。两条定向测试 `acq004_qa3_prepare_native_profile` 与 `acq004_qa3_inject_native_cycles` 各 1 passed。 |
| `node node_modules/vite/bin/vite.js build --outDir "$Q/dist" --emptyOutDir`、`"$Q/api.py"`、`"$Q/serve_web.py"`、独立 Vite、`"$Q/start-daa.sh"` 与原生 CUA | Web 构建 0，有已知 chunk 提示。三个回环监听及两次原生启动成功，真实投递 worker 经 UI 显式启动、暂停，DAA 两次干净退出。 |
| `node "$Q/web-flow.cjs"` 与 `node "$Q/web-flow.cjs" --readback-only` | 首轮真实登记、复制与实时读回断言通过，历史 GET 200 且响应匹配，随后因探针只匹配无标签 sampleId 退出 1。修正至页面实际 `Sample ID: ...`，复跑退出 0，Web 实时和历史详情全部通过。 |
| `backend/.venv/bin/python "$Q/native_read.py"`、`"$Q/contracts-read.py"`、`"$Q/third-party.py"` | 最终均 0。第三方探针首次因登录字段名读取错误退出 1，改用实际 `accessToken` 后通过。新样本联合对账输出 SHA-256 `f3c227bd80bc4441262fa5bfd71664670e22719b9e0f95a6dccd503892430f8b`。 |

R4-AC01–03 沿用 QA1 对同一后端/Web 字节的独立结果，并增加本轮英文 Web 实操、五条 GET 和 MySQL 对账。R4-AC04 的同/异实例、接管与迁移前冻结样本均已闭合。R4-AC05 的迁移、恢复、第三方示例、合同及最终 DAA 新版指南链路通过。合成样本验证限 macOS arm64 和获批专用环境；现场设备、Windows、真实环境采用、部署及发布待各自授权。Human Owner 最终验收待定。

QA3 原生 PID 17693/18094 已干净退出，Chrome 私有上下文已关闭。核对端口和工作目录后停止本轮 API/Web/Vite PID 17034/17072/17068，端口 38406/38416/38411 均无监听，QA3 无在线依赖。QA3 私有根含快照、构建、合成 SQLite、截图和日志，必要事实已写入本清单，随任务专用 MySQL、卷、网络及 Development/QA1/QA2 临时证据在协调者确认归属及无依赖后回收。仓库仅更新本 checklist。

### 资源收尾复核

2026-11-13（Asia/Shanghai），协调者按授权回收后，Verification 通过 Docker 只读 `inspect` 核实容器 `b44b373c0f8b2fa0f31cde4e6f8c398fda0508d9c73416f8ee8fa4bb146a28d3`、卷 `arch-acq004-r4-verify-data` 和网络 `arch-acq004-r4-verify-net` 均已不存在。四个临时根 `/private/tmp/arch-acq004-r4-isolated-ebbghp32`、`/private/tmp/arch-acq004-r4-qa2.peZVG5tN`、`/private/tmp/arch-acq004-r4-qa3.7A0ZjAU6` 和 `/private/tmp/arch-acq004-r3-qa.PVvRygAh` 均已删除。监听检查确认任务端口 33404、38404、38406–38411 和 38416 已释放。旧 3307 仍有监听，本次只检查端口，未连接数据库。

`/private/tmp/arch-acq004-r3-dev.0fxOzki5` 仍保留，其中 `frozen-r2` 与 `pre-integration` 是 Git 尚未固化的 r2 前驱和整合前源码备份，供后续真实环境迁移规划核对。真实切换前须另行核对该备份。QA3 的 `qa_passed` 结论继续有效，Human Owner 最终验收待定。

## ARCH-ACQ-004 r4 Human Owner 最终验收

2026-11-13（Asia/Shanghai），Human Owner 针对会话中提出的「验收通过 ARCH-ACQ-004 r4 的源码及隔离验证。现有 dev 数据库、真实历史和现场部署另行决定。」作出如下答复。Verification 记录该决定。

> 先验收，dev那边你给出步骤带我走一遍，我自己手动测，遇到问题再问你

本任务状态为 `owner_accepted`，范围限于 QA3 已核验的 ARCH-ACQ-004 r4 源码及隔离验证，R4-AC01–05 的独立结论为 `qa_passed`。上文「Human Owner 最终验收待定」为 QA3 和资源收尾复核时的记录。 [QA3 验证](#arch-acq-004-r4-独立复验-qa3)

| 依据 | SHA-256 |
| --- | --- |
| 获批 r4 规格 | `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234` |
| r4 Development 交接 | `99f33d2bf282193d8200d0c0d66bb1bdfcf897da56849e2a567c0a1beeeafc8c` |
| 验收前 QA 清单 | `dcc9f42af9f031a2f4a40f010d0ca3a1265062a0dfb0de357b3ac9dfa6de59f7` |
| QA3 的 34 路径候选清单 | `b882f7a6da1fc9a6a784b9585c20222db130d23e5e450498a1e995958ca0b9b4` |

Verification 在验收代录前以 `shasum -a 256` 核对三份任务文件，并用 Python 标准库 `hashlib` 核对正式树 34/34 路径与 QA3 候选匹配。验收沿用已记录的隔离运行证据。

dev 手动测试由 Human Owner 另行执行。现有 dev 数据库和真实历史未在本任务中迁移，实际目标采用与迁移仍须另行决定。真实 PLC 操作、现场部署及发布各有独立授权，DAA-013 的最终验收归其自身任务记录。

# ARCH-ACQ-004 r4 独立复验 QA2

**结论为 `qa_blocked`。** R4-QA-01/02 已关闭。R4-QA-03 的双语指南、迁移链接及确认提示通过本任务的静态与定向复验。联合证据已核实两种实例组合的新样本回执与事实归属。R4-AC04 仍缺迁移前待传样本经迁移后实际候选 API 的同批回执，R4-AC05 仍缺以最终 DAA 候选独立按新版指南走完原生链路。DAA-013 后续交接自身的独立 verdict 待该任务记录。保留上文 QA1 的候选、失败和命令结果。

## 候选和验证范围

- 2026-11-13（Asia/Shanghai），fresh-context Verification。正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交差异。获批 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，Development 最新 handoff SHA-256 `5e9d8351a407a9ae2d7140e706a7922afadd14e16a40d8d47b5d0ba213fc5250`，进入复验时本清单 SHA-256 `644d7162ec6de1871cacb9daccad4ba42482379f6cb5f646d7433b65d62db6b3`。34 条 ACQ 文件清单 SHA-256 `cfcbe57e6e52fe0da2fa65432459b2ac4af899bb9337288465c70eeca59dedfb`，正式树 34/34 匹配。相较 QA1 清单，仅合同两份 README 字节发生变化。 [获批规格](spec.md) · [返工交接](tasks.md#r4-qa-0102-文档返工与-development-handoff)
- DAA-013 r1 获批 spec SHA-256 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，精简后的 handoff SHA-256 `9c5bc1a568adbf31c6a65931b2023a1a732eb998539bceb17ae61581ce2c1573`，最终交付清单在正式树匹配 14/14。第一次指南返工交接后的 3 个差异已由精简后的交接逐项固定。相比 DAA-013 QA3 候选，最终候选只改双语指南、双语 locale 和一个定向测试，共 5 项；原生补证副本中 9 个运行代码和界面输入核对匹配 QA3 摘要，含两份旧 locale。DAA-013 checklist 当时 SHA-256 `54df3807ca30c7de375490563c6eb63deaaa3d59f992f75195f153aa03cb0cdf`，该 QA3 verdict 只覆盖其原始 14 项。 [DAA-013 最终交接](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/tasks.md#精简后的完整源码及指南-sha-256) · [DAA-013 QA3](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/checklist.md#daa-013-r1-独立验证-qa3)

## 返工复验

| 项目 | 结果 |
| --- | --- |
| R4-QA-01 | **关闭。** 两份合同的补传段落、409 说明与 Swagger 重试步骤均写明当前登记三标识仍匹配、样本仍有效的前提；原字节重试为 `duplicate`，接管后的旧身份可得到 `403 plc_facts_v2.scope_rejected`。当前服务在唯一键冲突后回滚，再核对登记与时间，才判断原字节或冲突。QA1 对同一正文的 200/200/403 实测继续适用于未变的服务。 [中文合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#提交与补传) · [英文合同](../../contracts/published/http-api/plc-facts-v2/README.md#commit-and-retry) · [重试分支](../../backend/app/plc_facts/services/async_v2.py#L39) |
| R4-QA-02 | **关闭。** `instanceId` 文案准确说明它是三标识之一及样本 ID 去重范围。历史标签来自当前 PLC 登记行的 `sourceType`，正文额外提交该字段返回 422，标签只用于标注和展示。对照数据库准入和历史写入路径，以及 QA1 同实例不同 PLC 分别存储各自标签的实测。 [中文字段](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#样本字段) · [英文字段](../../contracts/published/http-api/plc-facts-v2/README.md#sample-fields) · [准入实现](../../backend/app/plc_facts/crud/async_source_registry.py#L14) |
| R4-QA-03 | **内容和定向复验通过。** 双语 Stage C 第 6 节按实际部署区分已采用单表与旧 r2，明确单表按三标识准入，DB 随样本和查询，旧 r2 仍核对 DB 读写授权。中文迁移链接解析到冻结前驱的现有标题，根采集指南到 Stage C 链接有效。中英文开始/继续和同目标核对提示均将 DB 写作本地样本信息，按目标规则核对上报许可；实际调用保留目标、合同、完整逐样本来源及设置版本，同目标确认保留相同逻辑目标及数据库、原身份原字节和可靠回执。DAA-013 最终候选独立 verdict 与原生指南实操仍按各自验收记录。 [中文 Stage C](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md#6-登记来源并开始上报) · [英文 Stage C](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.md#6-register-sources-and-start-delivery) · [实际确认调用](../../automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts#L38) |

中文合同 Swagger 步骤 1 的「合成来源，。」在 QA1 源码副本已存在，当前仍可见。交 Development 下次文档返工时修正，操作含义清楚，本轮记为非阻塞编辑项。 [中文 Swagger 步骤](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#swagger-手工测试)

## 联合证据和逐项结论

- 对协调者补证的同一专用 runtime4 SQLite 使用 URI `mode=ro`、`PRAGMA query_only=ON` 读取，只核对 E/F 共用实例、C/D 各用不同实例，每台 DB21/22。按八个样本逐条重算原始请求和原始回执的 SHA-256，检查保存的 `sha256:` 前缀、确切三标识、DB、sampleId、`plc-facts/v2`、`committed/created`、尝试次数均为 1、尝试地址和确认时间偏移 `+08:00`。两轮中旧一轮的样本仍保留原身份，最后保存的两条活动绑定是 C/D。协调者的原生关闭、重开、操作、样本注入及 Web 读回见 Development，Verification 此轮独立复核持久化证据。 [原生联合执行记录](tasks.md#r4-补充原生联合验证与-development-handoff)
- 以专用合成只读账号仅连接 `127.0.0.1:33404`，先用 SELECT 核对 UUID `43b1c562-df4b-11f1-83c9-72f35d3e7827`、MySQL 8.4.6、schema `arch_acq004_r3_dev_main`。随后用四台 PLC 和八个 SQLite sampleId 限定 SELECT，确认 4 个 `daa` 登记、8 条历史的实例、PLC、DB、代次、序号、点 ID 和历史标签一致，每个 `content_hash` 与原始请求字节相同。最新表八组总计 144 点，本次 96 点按 sampleId、序号、点 ID、数据类型、质量与请求逐条匹配。按 SQLite 排序（C、D、E、F，各 DB21、DB22）的 sampleId 为 `02116735-150a-45b0-aa13-f7fc781be5e9`、`9d32ab20-c713-4c31-8f7c-8602fde2ae0e`、`42f2011b-ac02-464d-a67a-6e261a322946`、`1c942886-b8fc-45f5-aef7-67b1091c9847`、`25425c17-f4c3-4a94-9b49-abdd777ea82e`、`9cb0028e-7d62-48a0-b70b-9014743d921d`、`c6ef4138-8dc1-4d82-879c-4fcd02ee29f0`、`1b7881cd-a6bc-41fb-85d1-2639cd6f008c`。

| 验收 | 当前状态 |
| --- | --- |
| R4-AC01–03 | 沿用 QA1 在同一后端/Web 候选上的已通过证据。本轮未重跑浏览器或双 API 场景；补充对账确认本批原生样本归属。 |
| R4-AC04 | **部分通过，仍阻塞。** 沿用 QA1 的真实接管事务、403、已用代次拒绝和 Web 剪贴板证据。新补证覆盖同实例及异实例、两 PLC 各两个 DB 的原生设置和新样本可靠回执。其中部分跨应用粘贴由协调者以 Web 显示文本注入原生框，因 IAB 与原生系统剪贴板不共享。8 份样本由新 runtime4 profile 的测试 helper 在后端已迁移后生成。未发现固定双方候选、同一隔离目标及同一批迁移前待传样本的原身份、原正文和实际后端回执证据。DAA-013 QA3 的旧库保全、合成回环回执及 QA1 的后端迁移数据对账各有覆盖，仍需从迁移前的已绑定、有效待传样本到迁移后实际候选 API 的对应回执。 |
| R4-AC05 | **迁移与第三方示例通过，原生指南实操阻塞。** 沿用 QA1 的三条迁移、前驱恢复、空表首行、第三方示例及两份 OpenAPI 与运行路由对比；本轮复验新版指南、公开合同及链接。仍需由独立 Verification 按新版指南在最终候选上执行 Web 登记和复制、DAA 对应行粘贴并保存重开、显式启动、两台 PLC 两 DB 的回执和 Web/GET 读回。协调者运行中的早期 locale 及本轮只读查询未覆盖这项实操。 |

## 命令、环境与交接

macOS 15.7.7 arm64、Node 22.19.0、项目后端 Python 3.13.3 与现有 PyMySQL。下表 `Q` 是本轮专用 `/private/tmp/arch-acq004-r4-qa2.peZVG5tN`。

| 命令 | 结果 |
| --- | --- |
| `shasum -a 256 -c /private/tmp/arch-acq004-r3-dev.0fxOzki5/manifest-qa1-rework.txt`；`git diff --check` | 退出 0，34/34 匹配、无空白问题。 |
| `python3 "$Q/docs-audit.py"` | 最终交接运行退出 0，112 个相对链接、40 个 Markdown 片段、7 个合法 JSON 示例。DAA 最终 14/14 匹配，664 个英中叶键对称，仅两个提示键变化且占位符一致，两份 DAA-008 历史后缀逐字相同。中间一次摘要检查因正式树三项已进入下一交接而退出 1，改用该后续交接后通过。未访问外部链接或渲染 Mermaid。脚本 SHA-256 `6fb25e88f8391db61d3367b7d44cb76d097133920bd4ff6f4dc514c427fffba6`。 |
| 在 DAA 模块 `node --test tests/facts-delivery.test.mjs` | 退出 0，7/7。执行实际 composable 的中英开始/继续与同目标重绑，使用合成对话框和 IPC。 |
| `backend/.venv/bin/python -B "$Q/joint-read.py"` | 首次退出 1，探针漏计 SQLite 摘要的 `sha256:` 前缀。修正后 SQLite 检查通过，沙箱拒绝回环 MySQL 连接（EPERM，退出 1）。同一固定目标的最小权限重跑退出 0，SQLite 和 MySQL 全部核对通过。脚本 SHA-256 `3ac6bd808dcfa2d0628869f75270419d2df61bde85fc417c2b9a3703eefedd0d`。 |

解除阻塞需要同一专用环境下的迁移前队列证据及新的 Development handoff，随后固定 ACQ 和 DAA 最终候选、DAA-013 对应独立 verdict，重跑新版指南原生操作。原生复验可使用获准专用 MySQL、同候选回环 API 和 Web、合成管理员、新专用 profile（关闭 PLC 读取）及任务私有双 PLC DB21/22 采样夹具。使用同一系统剪贴板的浏览器与原生 DAA，记录 Web 已提交行、复制和粘贴、持久化重开、明确开始、匹配回执及读回。旧队列对账还需保留迁移前原三标识、sampleId、原正文摘要与迁移后实际回执。届时仅验证已批准合成目标。

本轮无自有运行进程。两个只读探针保留在 QA2 自有临时根，待下一次独立验收无依赖后由协调者回收。专用 MySQL、隔离 profile、原生候选、冻结前驱及其只读材料仍供旧队列补证与后续独立 QA 使用，协调者按任务归属和实际占用收尾。本轮未运行活 API、原生 UI、设备或 Windows，未触及现有数据库、真实 profile、历史、部署或发布。仓库内只写本清单。整体 `qa_blocked` 交协调者组织补证，Human Owner 最终验收待定。


# r2 历史 Verification 记录

Task ID: ARCH-ACQ-004
Revision: r2
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: QA7 通过精确文档返工候选，沿用 QA5 隔离产品验证证据，交 Human Owner 最终验收。
Workflow Mode: STD
Fresh Context: true

# 独立验证 QA1

2026-11-13（Asia/Shanghai）。在 Development 交接后启动命名 `verification` 角色，以 fresh context 读取根契约、项目及所属模块 README/PLAN、任务完整 `spec.md` 和 `tasks.md`，复核交付文件、差异和测试。采用与表面相应的 `project-governance`、`aiis`、`backend-arch`、`backend-script-tooling`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 的适用约束。

## 候选与范围

- 交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树。`spec.md` SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，`tasks.md` SHA-256 `e2206aa9b7cf5ffa7627e361bfc663f5cacaef07e5bfc3b8ffafd3c7d88614af`。嵌入清单原字节 SHA-256 `ff3f12cd8f45d1865c9f867139a01397a5e8f7a686255bae6c3c47da1f9ace15`，64/64 文件逐一通过。r1 引用还原为 21,335 字节，SHA-256 `619148a651c465f1f091b7439f285b57fc44ad9cadeb0f73fa0e41f14fe8e0b0`。冻结开发采集 OpenAPI SHA-256 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。
- 对照 r2 §4 和 r1 §5 核对清单路径及 Git 差异。64 路径均可追溯到该允许范围。交付树包含并行 DAA-010、provider、CU 与索引差异，清单固定共享文件整体字节。HEAD 对比只能定位差异，无法逐行证明任务间的归属。既有 Alembic 版本文件无 Git 差异，单一新增后继为 `6a8c0e2b4d16`。 [批准规格](spec.md) · [交付清单](tasks.md)

## 可复现失败

| 编号 | 对应规格 | 复现及结果 |
| --- | --- | --- |
| QA1-01 | R04、AC01、R2-02、R2-AC01 | `uv run --offline --no-sync python` 用 FastAPI `TestClient` 挂载实际 `source_registry.router`，保留实际鉴权依赖。无 token 的 `GET /api/v1/admin/acquisition-sources` 返回 `401` 和 `WWW-Authenticate: Bearer`。追加 `?page=1&page=2` 后变成 `422 acquisition_sources.invalid_request`，无认证头。无 token 的 POST、PATCH 加 `?x=a&x=b` 同样为 422。`RegistryRoute` 在实际管理员依赖运行前返回业务校验错误。 [路由](../../backend/app/plc_facts/api/source_registry.py#L21) |
| QA1-02 | R07、R2-01、R2-02、R2-AC01 | `node --input-type=module` 用 `node:vm` 执行候选 Vue 的 `parseDbs`、`openEdit`、`save` 原函数，注入合成列表行 `{plcId:'plc/only-read',sourceType:'external',instanceId:'old',sourceGeneration:'old-gen',dbNumbers:[],readDbNumbers:[21]}`。编辑只把代次改为 `new-gen`。实际结果 `dbText=""`、提示 `acquisition-data.sourceConfig.invalid`、PATCH 调用 0 次。该行来自允许导入的零写授权活跃绑定，PATCH 允许空增量接管并保留既有读授权。 [表单](../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L181) |
| QA1-03 | R2-03、R2-AC02 | `uv run --offline --no-sync python` 执行实际 `async_source_registry.register`，用 `AsyncMock` 注入无活跃绑定、旧事实中存在 `plc/only-read` 的 `history-gen`，`generation_exists` 配置为 `True`。提交 `{sourceType:'external',instanceId:'new-instance',plcId:'plc/only-read',sourceGeneration:'history-gen',dbNumbers:[21]}` 得 `created`，代次检查调用 0 次，提交 1 次。POST 首次登记漏查事实/水位里的已知代次，只有 PATCH 接管调用检查。存在旧历史而无活跃来源是 R07 的有效输入。 [POST 服务](../../backend/app/plc_facts/services/async_source_registry.py#L37) · [已知代次查询](../../backend/app/plc_facts/crud/async_source_registry.py#L82) |
| QA1-04 | R04、AC02、R2-AC01 | `uv run --offline --no-sync python` 用实际管理 POST ASGI 路由与服务，注入管理员和 SQLAlchemy `OperationalError(2013)` 的提交边界。模拟回滚成功得到 `503 acquisition_sources.commit_outcome_unknown`。模拟回滚也抛错得到 `503 acquisition_sources.not_ready`，丢失先 GET 核对的错误标识。同样的组合在 PATCH 服务保留 `commit_outcome_unknown`。此外 Web 仅按 409 区分错误，代次重用和实例类型冲突都显示「来源已被修改」，明确的 `not_ready` 也显示「保存结果未确认」。浏览器仍需用真实 API 核对错误、刷新和重试流程。 [POST 异常处理](../../backend/app/plc_facts/services/async_source_registry.py#L65) · [Web 错误分支](../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L221) |

## 验收结果

| 标准 | 结果与边界 |
| --- | --- |
| AC01 / R2-AC01 | 管理三操作 OpenAPI Bearer、无参数匿名 401、离线管理员操作和响应信封通过。QA1-01、QA1-02、QA1-04 失败。真实账号登录、过期/撤销/禁用、两个编辑者、管理员与普通账号的浏览器动作、双语、窄屏及列宽持久化待独立目标。 |
| AC02 / AC03 / R2-AC02 | 源码的样本准入以同一事务共享锁读活跃绑定，重复回执分支先回滚，再核验目标和登记并检查原字节。同一 PLC 的管理更新先取得排他锁再比对版本。QA1-03 和 QA1-04 失败。真实 MySQL 上同进程/双进程的 403 → 原字节 200 `committed/created` → `duplicate`、两事务重叠、并发编辑/冲突及真实提交未知对账待测。 |
| AC04 | 离线覆盖五个 GET、读并集、活跃类型、第三方与 DAA 字段、原字节幂等和清理等。独立 MySQL 上的实时与历史对账、零写活跃绑定及无绑定的只读对继续可读待测。 |
| AC05 | Web 模块、构建通过。QA1-02、QA1-04 失败。实际 API 浏览器验证仍待。 |
| R2-AC03 | DAA 前端合成用例覆盖粘贴覆盖、空绑定及重复 PLC，Rust/SQLite 覆盖 CAS 原子保存、同目录重开、采样跨保存的新旧绑定、配置前记录留本地、在途回执和暂停派发。回环 HTTP 单测独立证明原字节与免 Bearer。实际隔离 DAA 界面手填/粘贴/取消/冲突和同一合成样本从设置、采集、显式启动、真实 POST 到本机确认、可选 GET 的贯通仍待。 |
| R2-AC04 | 通过 sealed 旧 runtime4 同 inode 升级、原 payload/SHA、manifest、在途转未知及原冻结正文重试；v4 另测有效回执与保留期，实际子进程故障/重开及原生锁。中断 staging 被保留并拒绝重开；无 seal 的旧热 journal 保留原文件并拒绝自动恢复。旧格式本机采集/历史行为有测试，旧二进制打开升级格式未独立实跑。当前证据没有覆盖同一个前驱库内全部队列状态、后端接管后 UI 展示和对账。 |
| AC06 / AC07 / R2-AC05 | Alembic 唯一 head、冻结工件、管理合同、Python 编译、后端回归、两端构建、Rust 格式和本地文档目标通过。复核 cleanup 目标守卫及 BE-010 增加已知后继。实际 MySQL 前驱升级和故障中断、模型/迁移一致性、错目标/未初始化/旧 JSON/连接不可用 fail closed、预览无写、重复导入保留 Web 增量、导出接管代次并恢复前驱及样本/水位/读写对对账仍待。 |

## 执行证据

使用 macOS 15.7.7 arm64、`uv 0.7.8`、`node v22.19.0`、`pnpm 11.11.0` 和 `cargo 1.89.0`。从交付树复制固定源码到任务专用 `/private/tmp/daa-008-r2-a-acq004-qa.KNXKyP/source`，复用已安装的锁定依赖，排除仓内 `.env`。后端只传显式合成变量，数据库 URL 指向 `127.0.0.1:1` 占位，离线组用 `no_db`，没有数据库服务。Web 构建传两个角色页面访问变量为 `[]`。DAA profile、Rust target、Vite dist 及日志归 QA 私有目录。三个已存在的 ignored DAA-002 合成文本夹具 `flat.db`、`nested.db`、`invalid.db` 是原测试的 `include_str!` 编译输入，初次隔离编译发现缺失后，仅从现有合成夹具目录补拷这三份。未复制真实现场配置。

| 命令 | 退出及结果 |
| --- | --- |
| `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_business_integration_storage.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_business_integration_migration.py` | 0，141 passed、11 skipped。 |
| `uv run --offline --no-sync pytest -p no:cacheprovider -q tests/test_acquisition_source_registry.py tests_mysql/test_acquisition_source_registry.py` | 0，6 passed、1 skipped，MySQL 用例按专属目标守卫跳过。 |
| `uv run --offline --no-sync alembic heads` 和 `uv run --offline --no-sync python -m scripts.plc_facts_maintenance.main --help` | 均 0，唯一 `6a8c0e2b4d16`，CLI 打印帮助。22 个清单 Python 文件用 `py_compile` 编译到临时目录，退出 0。 |
| Web `pnpm check:modules`、`node --test tests/module-registry/acquisition-data.test.mjs`、`pnpm build --outDir <QA>/artifacts/web-dist --emptyOutDir` | 均 0，模块测试 9/9，有 Vite 大 chunk 警告。 |
| DAA `node --test tests/facts-delivery.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir <QA>/artifacts/daa-dist --emptyOutDir` | 均 0，测试 5/5，有 Vite 依赖注释和大 chunk 警告。两端 pnpm 临时源码使用 `pnpm_config_verify_deps_before_run=false`，避免重装现有依赖。 |
| `rustfmt --check --edition 2021 --config skip_children=true <清单中13个Rust文件>` | 0。 |
| `TMPDIR=<QA>/rust-profiles CARGO_TARGET_DIR=<QA>/artifacts/target cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features -- --test-threads=1` | 101，156 passed、2 failed、2 ignored。`sample_upload_tests` 13/13，`profile_contract_tests` 30/30，`services::local_delivery::tests` 13/13。日志 SHA-256 `7197658d7ebc89365a315fb2dc629c13167918e927998751bb8ada0d53164e67`。 |
| 同一 Cargo 命令追加 `infrastructure::facts_http::tests::v2_loopback_posts_original_utf8_to_sample_path_without_bearer -- --exact --test-threads=1`（替换原测试参数） | 单测原为沙箱 `EPERM`。限于自有 `127.0.0.1` 监听的权限复验退出 0，1/1。全量另一失败 `infrastructure::yaml_migration::tests::migration_empty_retry_cas_capacity_lock_and_private_protection` 在 `yaml_migration_tests.rs:358` 重现 `profile_locked`。测试文件 SHA-256 `0e77314d10c05057f5bc8bb2275b46c5dbfa83673c837cf9cd7e1d6f8e430205` 且与 HEAD 无差异。该结果已见 DAA-010 历史自检。 [DAA-010 历史证据](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/tasks.md#L191) |
| `git diff --check` 和 16 份受检 Markdown 本地目标扫描 | 0，237 个本地相对链接目标无缺失，未逐个校验锚点。 |

## 交接与解除条件

- `qa_failed` 交回 Development 修复 QA1-01 至 QA1-04，再重新固定候选并交 fresh-context Verification。QA1 原证据保留。
- 独立目标需 Human Owner 明确批准的专用 MySQL 8.4.6 实例和 main/restore/guard 合成 schema，目标 UUID、精确前驱/后继、上海时钟、仅限该 schema 的账号、两个独立后端进程和合成管理员/普通账号。使用该候选执行数据库、浏览器和 DAA 剩余验收。没有启动 Docker、连接现有服务、操作真实 profile、真实数据或设备。Windows 原生行为另归批准边界。
- QA 临时目录内有复跑日志、合成 profile 和构建产物，仅供协调者复核后按流程回收。可复核结果和关键摘要已保存在本文件。仓库写入限本 checklist。

## Human Owner 最终验收

待定。

# 独立验证 QA2

2026-11-13（Asia/Shanghai）。协调者在第二次 Development handoff 后调用命名 `verification` 角色并使用 fresh context。读取根契约、模块规则、任务三文件、候选源码、差异及测试输出。适用规则来自 `project-governance`、`aiis`、`backend-arch`、`backend-script-tooling`、`frontend-ui`、`i18n-workflow`、`rust-runtime`、`desktop-tauri` 和 `code-document-indexer`。QA2 仅更新本 checklist。

## 验证对象

- 交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树。规格 SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，第二次 Development handoff `tasks.md` SHA-256 `f6c23a7d3b39fbad9d88137c2c7247ad39431d9645e7a0e974a01e29c14eeea4`，QA1 checklist 输入 SHA-256 `bdfbbae404951806d17e952e0de891454315674c4c91cc85de00af249bd69041`。
- 末尾清单 SHA-256 `6c0e978c3b64188af93e3282399f088deb206dc8ea226eadd23daa1566fba766`。交付树与私有测试副本均通过 64/64 校验。相对 QA1 清单变化为交接所列 10 个允许路径。共享文件的摘要包含并行任务已有改动。已跟踪的既有 Alembic 文件无差异。冻结采集 OpenAPI SHA-256 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。按行移除引用前缀还原 r1 原文 21,335 字节，SHA-256 `619148a651c465f1f091b7439f285b57fc44ad9cadeb0f73fa0e41f14fe8e0b0`。 [批准规格](spec.md) · [第二次交接与清单](tasks.md#qa1-修复与第二次-development-handoff)

## QA1 复验

| 编号 | QA2 实际结果 |
| --- | --- |
| QA1-01 | 原复现通过。实际 FastAPI GET、POST、PATCH 路由在重复 query 且 JSON 可解析时，匿名和无效 Bearer 返回 401 与 Bearer 挑战头，合成普通用户返回 403，合成管理员返回 422。不可解析的正文仍暴露下方 QA2-01。 |
| QA1-02 | 原复现通过。编译并执行来源页 Vue setup，零上报 DB、独立读 DB21 的记录发出空增量 PATCH 接管，既有独立读 DB 保留。显式添加 DB23 发出对应的读写增量。空 DB 新建及移除既有写 DB 仍拒绝。 |
| QA1-03 | 离线层通过。实际首次 POST 服务检查历史代次并在命中时返回 `generation_reused`，不创建实例或提交。同身份重复仍 `unchanged`。用 MySQL 方言编译三个查询均含 `LOCK IN SHARE MODE`，分别模拟代次账本、仅历史、仅水位命中。真实 MySQL 的锁和存量事实复验待批准目标。 |
| QA1-04 | 原复现通过。实际 POST 路由和服务在模拟提交抛 `OperationalError(2013)` 时，回滚成功及同时抛错均返回 503 `commit_outcome_unknown`。编译后的 Web setup 对未知提交、不可用和四种冲突显示各自文案，保留表单且只发一次请求。实际断连和 GET 对账待隔离目标。 |

## 可复现失败

| 编号 | 对应规格 | 复现及结果 |
| --- | --- | --- |
| QA2-01 | R04、AC01、R2-02、R2-AC01 | 在合成设置下用 `uv run --offline --no-sync python`，以 FastAPI `TestClient` 挂载实际 `source_registry.router` 到 `/api/v1`。对 `/api/v1/admin/acquisition-sources` 的 POST 和 PATCH 发送 `Content-Type: application/json`、正文单字节 `{`。无 token、无效 `Bearer invalid.token.value`、通过用户依赖注入的普通用户三组均返回 422 `acquisition_sources.invalid_request`，无挑战头。正文换成可解析的 `{}` 后匿名及无效 token 为 401，带 `WWW-Authenticate: Bearer`。无效 token 加正文单字节 `0xff` 返回框架 400，同样没有挑战头。实际业务 session 入口调用 0 次。R04 要求前两组返回带挑战头的 401，普通用户返回 403。FastAPI 在管理员依赖前解析正文，当前路由直接把解析失败映射为 422 或沿用 400。 [管理路由](../../backend/app/plc_facts/api/source_registry.py#L20) |
| QA2-02 | R01、R2-01、R2-04、R2-AC01、R2-AC03 | 实际 `RegistrationIn.model_validate` 接受首字符为 U+FEFF 的标识并原样保留，拒绝首字符为 U+0085 的标识。以 `node --input-type=module` 编译实际 Web 来源页 Vue setup，`plcId="\uFEFFPLC"` 新增和编辑（既有 DB21，增加 DB22）均显示 `sourceConfig.invalid`，POST/PATCH 调用各 0 次。同一编辑改用 `plc/中文` 后发出保留原字节的 PATCH。用同一方式编译执行 DAA 实际设置组件，粘贴覆盖 DB21 的合法 JSON，`plcId="\uFEFFPLC"` 返回 `sourceInvalid`，合法标识未进入表单。相同输入改为 U+0085 或单个 U+D800 前缀时，DAA 表单允许填入并调用保存。Python 标识验证拒绝前者，非法 Unicode 代理码位不能编码为合同要求的 UTF-8。两处 JavaScript `trim()` 与后端的首尾空白集合不同，`TextEncoder` 也会替换孤立代理码位。合法的已登记标识应能继续编辑并原样粘贴、保存。 [后端标识](../../backend/app/plc_facts/v2_domain.py#L62) · [Web 校验](../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L132) · [DAA 校验](../../automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue#L92) |
| QA2-03 | R2-04、R2-AC03、根契约 §5 | 用独立 Vite 构建及无头 Chrome 打开中文 DAA「上报设置」，从合成 IPC 先保存 `gen-1`，再粘贴覆盖 DB21 的 `gen-2`，让第二次保存返回 Rust CAS 错误形状 `{errorCode:"delivery_settings_conflict"}`。弹窗保留未提交输入，关闭后重开读回 `gen-1`。页面唯一含错误的 alert 文本为「运行结果：delivery_settings_conflict」，位于弹窗之外。在该 alert 中心调用 `document.elementFromPoint` 命中弹窗表单项，弹窗内无可读的冲突提示。实际 Rust 返回同一错误码，用户需要在保存失败时能看见本地化的冲突反馈。 [Rust CAS](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs#L250) · [保存 IPC](../../automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts#L48) · [弹窗反馈](../../automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue#L24) |

## 独立执行与验收范围

macOS 15.7.7 arm64，`uv 0.7.8`、`node v22.19.0`、`pnpm 11.11.0`、`cargo 1.89.0`。从交付树复制到 `/private/tmp/daa-008-r2-a-acq004-qa2.WEA046/source`，复用已安装依赖并从 QA1 独立克隆 Cargo 目标缓存，重新编译本候选。补拷既有三个合成 DAA 编译夹具。没有读取现有运行 `.env`，后端仅传合成配置及 `127.0.0.1:1` 占位。Web 角色页面变量为 `[]`，两端使用 `pnpm_config_verify_deps_before_run=false`。SQLite、日志及构建输出均使用自有临时目录。

| 命令 | 退出及结果 |
| --- | --- |
| `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_business_integration_storage.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_business_integration_migration.py` | 0，149 passed、11 skipped。覆盖管理路由和工件 Bearer 合同、事实读写、迁移图、回退材料及守卫离线回归。首次退出 4，补齐缺少的合成 `API_V1_PREFIX=/api/v1` 后重跑。 |
| `uv run --offline --no-sync pytest -p no:cacheprovider -rs -q tests_mysql/test_acquisition_source_registry.py` | 5。整文件因缺独立目标确认跳过，零收集，未连接数据库。 |
| `uv run --offline --no-sync alembic heads`；`uv run --offline --no-sync python -m scripts.plc_facts_maintenance.main --help` | 均 0。唯一 head 为 `6a8c0e2b4d16`，维护入口只显示帮助。22 个 Python 文件语法编译、13 个 Rust 文件 `rustfmt --check --edition 2021 --config skip_children=true` 和 `git diff --check` 均通过。记录写入前对 17 份 Markdown 的 247 个相对目标检查无缺失，未逐一复核锚点。 |
| Web `pnpm check:modules`、`node --test tests/module-registry/acquisition-data.test.mjs`、`pnpm build --outDir <QA>/artifacts/web-dist --emptyOutDir` | 均 0，11/11。有 Vite 大 chunk 警告。 |
| DAA `node --test tests/facts-delivery.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir <QA>/artifacts/daa-dist --emptyOutDir` | 均 0，5/5。有 Vite 依赖注释与大 chunk 警告。 |
| `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --no-run`，随后运行该测试二进制 `<filter> --skip v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback --test-threads=1` | 均 0。 `infrastructure::local_store::sample_upload_tests` 13/13，`infrastructure::local_store::profile_contract_tests` 30/30，`infrastructure::local_store::tests` 34 passed、1 个由父测试运行的私有故障子测试忽略，`services::local_delivery::tests` 13/13。覆盖 SQLite 设置 CAS、跨保存的采样绑定、冻结正文、重开、在途恢复、保留期与 runtime2/3/4 受测结构。未重跑整套 Rust，QA1 的 YAML 测试限制保留。 |
| 同一测试二进制 `--exact services::local_delivery::tests::v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback --test-threads=1` | 首次退出 101，沙箱在 `127.0.0.1:0` bind 返回 EPERM。仅对该测试使用权限复验，清空继承环境并传自有 `TMPDIR`，退出 0，1/1。实际 Rust 保存、重开及显式开始后产生两次单 DB POST。断言目标路径、无 Bearer、原始正文、样本 ID、实例、PLC、代次和匹配的 `committed` 回执，两条 SQLite 记录确认且再次重开仍为确认状态。回执来自自有回环替身。 |
| `node /private/tmp/arch-acq004-r2-run.NR4HRT/daa_settings_smoke.cjs <QA>/artifacts/daa-dist` 与其 QA2 CAS 探针 | 各退出 0。Chrome 从文件路由加载实际构建，使用合成 Tauri bridge。验证手填、取消、重开、DB 范围不符、正确粘贴只填表单、CAS 后保留先前设置、无额外 IPC。CAS 探针退出 0 表示成功复现 QA2-03。 |

## 交接与剩余验收

- **`qa_failed`。** 将 QA2-01、QA2-02 和 QA2-03 交回 Development，完成后重新固定候选并交 fresh-context Verification。Human Owner 最终验收待定。
- **AC01–AC07、R2-AC01/02/05 环境缺口。** 需要 Human Owner 单独批准的可丢弃 MySQL 8.4.6、main/restore/guard 合成 schema、UUID 与精确前驱/后继、上海时钟、专用账号、两个预先启动的后端实例和合成管理员及普通账号。须复跑真实登录与 Web 操作、即时 403 → 原字节 200/committed/created → duplicate、事务串行和旧身份拒绝、读写权限及历史与水位守恒、迁移/初始化/回退、真实未知提交及 GET 对账。现有 dev、真实数据、数据库或设备均未接触。
- **R2-AC03/04 证据边界。** 有独立构建页面、真实 SQLite 和实际回环传输。完整原生 DAA 界面到候选 API/MySQL 的设置、采样、送达、确认与读回，以及旧身份拒绝后的原生展示仍待隔离链路。旧格式兼容结论限实测合成 profile，旧程序打开升级格式未独立实跑。Windows 与实际 profile 采用仍按单独批准处理。
- QA2 自有目录含固定源码、构建、合成 SQLite 和日志。诊断日志为 `logs/qa2-auth-adversarial.log`、`logs/qa2-web-id.log`、`logs/qa2-daa-id.log`，CAS 探针为 `daa_settings_cas_observation.cjs`。关键证据与复现已经写入本 checklist。保留供协调者和返工复核，确认无后续依赖后由协调者回收。QA2 对 QA1 缓存和夹具没有运行依赖。

# 独立验证 QA3

2026-11-13（Asia/Shanghai）。第三次 Development handoff 后，协调者以 fresh context 调用命名 `verification` 角色。读取根契约、生命周期工作流、适用模块规则、任务三文件、实现差异及既有测试证据。复验限本次九个变化文件和 QA2-01 至 QA2-03。 [批准规格](spec.md) · [第三次交接](tasks.md#qa2-修复与第三次-development-handoff)

## 验证对象

- 交付树为 `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树。`spec.md` SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，`tasks.md` SHA-256 `d033010d6848706ac67542423dd8f0162ea36193cd7c87a17515e7936272511a`，QA2 checklist 输入 SHA-256 `be8b6558f7a309a9f8c6f9abb96cbf94cb8dce7cc4cc97572f830ee674cc349b`。
- 末尾 64 行清单原字节 SHA-256 `ca73b6c12dfc451fe813216cad42fd503a80f0490cd7d53bc67aae433202bc97`，交付树逐项通过 64/64。清单中复制进私有候选的 62 项通过 62/62，含全部九个变化文件。对比第二次交接清单仅变化后端管理路由及测试、Web 来源页及模块测试、DAA 设置弹窗、console composable、两份 locale 和 facts-delivery 测试。Rust 文件摘要一致。共享文件摘要涵盖并行差异。
- 冻结开发采集 OpenAPI SHA-256 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。还原 r1 引用原文为 21,335 字节，SHA-256 `619148a651c465f1f091b7439f285b57fc44ad9cadeb0f73fa0e41f14fe8e0b0`。`git diff --check` 退出 0，既有 Alembic 文件无跟踪差异。检查三文件及清单指南共 16 份文档、145 个相对文件目标，无缺失。未逐个核查锚点。

## QA2 修复复验

| 编号 | 独立结果 |
| --- | --- |
| QA2-01，AC01 / R2-AC01 | 通过。实际 FastAPI 管理 POST、PATCH 分别接收正文 `{`、单字节 `0xff` 和 `null`。匿名及无效 Bearer 均为 401 且有 `WWW-Authenticate: Bearer`，合成普通用户为 403，合成管理员为 422 `acquisition_sources.invalid_request`，业务 session 入口调用 0 次。重复 query 权限顺序回归通过。实际路由生成 OpenAPI 与管理 r2 工件 JSON 对象完全一致，GET、POST、PATCH 均声明 Bearer。 [管理路由](../../backend/app/plc_facts/api/source_registry.py) · [实际路由测试](../../backend/tests/test_acquisition_source_registry.py) |
| QA2-02，R2-AC01 / R2-AC03 | 通过。后端标识校验及两端实际 Vue setup 保留首尾 U+FEFF、内部 U+0085 和恰好 128 字节的 32 个 emoji。拒绝首尾 U+0085、NBSP、EM SPACE、孤立代理码位、ASCII 控制字符及 132 字节输入。Web 新增和编辑、DAA 手填和 JSON 粘贴均复验实例、PLC、代次字段。 [Web 定向测试](../../frontend-js/tests/module-registry/acquisition-data.test.mjs) · [DAA 定向测试](../../automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs) |
| QA2-03，R2-AC03 | 通过。用实际 DAA Vite 构建、无头 Chrome 和合成 IPC 验证手填保存、取消、重开、DB 不匹配、正确粘贴及 CAS。先保存 `fixture-manual` / `gen-1`，再粘贴 `fixture-pasted` / `gen-2`，第二次保存返回 `{errorCode:"delivery_settings_conflict"}`。弹窗内显示「上报设置已被其他操作修改」及关闭重开提示，alert 中心命中弹窗内自身，未提交实例、PLC、代次留在表单。保存按钮禁用，等待 350 ms 后仍只有两次保存 IPC。关闭重开读回 `fixture-manual` / `gen-1`，清除冲突提示并重新启用保存。无额外 IPC 命令。中文浏览器流程实测，英文冲突文案和键在源码及构建检查中验证。 [DAA 设置弹窗](../../automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue) |

## 执行环境与命令

macOS 15.7.7 arm64，`uv 0.7.8`、`node v22.19.0`、`pnpm 11.11.0`。`<QA3>` 为 `/private/tmp/arch-acq004-r2-qa3.avimuynq`。从交付树复制源码并复用已安装依赖。排除 `.env`，后端清空继承环境后显式传合成设置，MySQL 地址为 `127.0.0.1:1` 占位。Web 两个角色页面变量均为 `[]`，两端使用 `pnpm_config_verify_deps_before_run=false`。

| 命令 | 退出及结果 |
| --- | --- |
| `UV_CACHE_DIR=<QA3>/uv-cache uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py` | 0，17 passed。首次默认 uv 缓存被沙箱拒绝，退出 2。改用专属缓存后成功。未建立数据库连接。 |
| Web `node --test tests/module-registry/acquisition-data.test.mjs`、`pnpm build --outDir <QA3>/web-dist --emptyOutDir` | 均 0，12/12，含 prebuild 模块装配检查。Vite 报既有大 chunk 警告。 |
| DAA `node --test tests/facts-delivery.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir <QA3>/daa-dist --emptyOutDir` | 均 0，5/5。Vite 报依赖注释及大 chunk 警告。 |
| `node /private/tmp/arch-acq004-r2-run.NR4HRT/daa_settings_smoke.cjs <QA3>/daa-dist --require-localized-conflict`，随后 `node <QA3>/daa_cas_assertions.cjs <QA3>/daa-dist --require-localized-conflict` | 原脚本沙箱内启动 Chrome 退出 1，Chrome `SIGABRT`。临时复制原脚本并加草稿、禁用、无重发和重开断言后，限该合成浏览器验证的权限复验退出 0。原脚本 SHA-256 `c19234e39fc2f75b796124c8ab940a594db956ea601df77b4c3c631212a69a88`，QA3 脚本 SHA-256 `bcb0f7978ac4de7e15bdc97962e0e36f77c61a3846e3619e7a70ee3bde9c736a`。页面资源以文件拦截加载，Tauri bridge 使用合成数据。 |
| QA2 Rust、SQLite 和回环 HTTP | 当前 Rust 与 QA2 清单逐项一致，沿用本文件 QA2 的命令和退出记录。设置事务、重开、跨保存采样绑定、旧队列和两条经实际 Rust HTTP client 的单 DB POST／匹配 `committed` 回执已有独立证据。回执来自回环替身。QA3 未重跑 Cargo，QA1 的全量 Rust 限制仍见原记录。 |

## 当前结论与恢复条件

**`qa_blocked`。** QA2-01、QA2-02、QA2-03 已通过独立复验。以下验收仍待补充可复跑证据。

| 规格 | 待验证结果 |
| --- | --- |
| AC01、AC05、R2-AC01 | 在专属环境以实际登录账号检查 active admin、过期／撤销 token、禁用账号及普通角色。Web 浏览器连接实际管理 API，完成 DAA 与第三方新增、参数复制、权限增量、双语、列宽、接管确认、两个编辑者冲突及未知提交后 GET 对账。 |
| AC02–AC04、R2-AC02 | 同进程和两个预先启动的候选后端验证登记前 403、登记后同一原字节 200 `committed/created`、重发 `duplicate`，核对事实行和水位。运行真实 MySQL 并发登记、样本与接管事务重叠、旧身份拒绝、新代次准入、实时与历史和独立读权限对账，记录进程未重启。 |
| AC06、AC07、R2-AC05 | 用合成数据验证 `5f7a9c1e3b25` → `6a8c0e2b4d16`、前驱 JSON 预览及幂等导入、精确目标守卫、DDL 中断处理、维护守卫、退回前驱的登记／代次导出及事实、水位、有效读写范围守恒。 |
| R2-AC03、R2-AC04 | 合成 DAA 设置页面、真实 Rust/SQLite、受测旧格式及合成回环传输已有上述证据。候选 API/MySQL 接收同一隔离合成来源的提交、确认、可选读回及切换后旧队列展示待贯通。旧程序实际打开升级格式尚无独立执行证据，兼容结论限已测结构与行为。 |

解除环境阻塞需 Human Owner 明确批准专属可丢弃 MySQL `8.4.6` 目标 `127.0.0.1:33404` 的合成验证操作，含该目标的启用／停止或对现有专属实例的明确复用、独立 main／restore／guard schema 及限定账号。开始写入前核验实际 server UUID、schema、上海时钟和精确前驱／后继 revision。以两个预先启动的候选后端及合成管理员、普通账号跑完上述矩阵。QA3 未连接任何数据库或现有 dev 服务，未读取现有 `.env`，未启停 Docker，未使用现有 profile 或真实设备。Human Owner 最终验收待定。

QA3 私有目录包含源码副本、两个 Vite 构建、uv 缓存及加强的 CAS 脚本。浏览器验证已退出，关键命令、断言和结果已写入本文件。QA3 无 QA1／QA2 临时目录运行依赖。由协调者核对后续复跑是否使用 QA3 或共用脚本，再按生命周期工作流处置相应临时资源。

# 独立验证 QA4

2026-11-13（Asia/Shanghai）。第四次 Development handoff 后，协调者以 fresh context 调用命名 `verification` 角色。读取根契约、生命周期工作流、适用目录文档、完整任务三文件、实现、差异及已有测试结果。应用 `project-governance`、`backend-arch`、`backend-script-tooling`、`frontend-ui`、`i18n-workflow`、`rust-runtime`、`desktop-tauri` 和 `code-document-indexer` 的相关条款。 [批准规格](spec.md) · [第四次交接](tasks.md#专属-mysql-dev-自检与第四次-development-handoff)

## 候选和环境

- HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交交付树。规格 SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，第四次交接和追加资源记录 SHA-256 `fe76d2d1e40130ccf98031c18cb9e6cd0ae189d2d97df3357e1060838ba63d0b`，此前 checklist SHA-256 `234915025ea96f171ae36872910e26cba4cc174a88c57179b520749883daee13`。末尾交接清单 SHA-256 `1f51828441473e0c3dfb7249bdc5817daf7b107616e3b99036e0a66c7a864773`，交付树 64/64 逐项一致。相对 QA3 仅变化来源登记模型的单例主键及其 MySQL DDL 编译回归，已有迁移文件无跟踪差异，`git diff --check` 退出 0。冻结采集 OpenAPI SHA-256 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。
- Human Owner 明确批准的 MySQL 8.4.6 `127.0.0.1:33404`，server UUID `5e4fc94b-df14-11f1-bd61-76346c8acc30`、实际上海偏移 28800 秒。QA 账号限 `arch_acq004_r2_qa_main`、`arch_acq004_r2_qa_restore`、`arch_acq004_r2_qa_guard`。Python 3.13.3、macOS 15.7.7 arm64、Node v22.19.0，使用项目已装锁定依赖。以下 `<RUN>` 为 `/private/tmp/arch-acq004-r2-run.NR4HRT`。各 API 启动后使用固定的源副本，`38406/38407` 的 PID 为 80898/80899，Vite `39405` 的 PID 为 80900。实际验证期间双 API 无重启或重载。沙箱默认连接回环端口返回 EPERM，限定本轮专属目标复验成功。
- `backend/.venv/bin/python <RUN>/copy_backend.py qa` 退出 0，复制 674 项，文件摘要清单 SHA-256 `835469034567fa70b32623677bd93d14b0e06e78fa6a8de9f5c0b671af6116d6`。Web 用独立临时副本，仅调整 Vite 缓存目录并注入隔离回环配置。全部测试使用合成账号、目标和 DAA profile。QA 仓库写入限本 checklist。

## QA4-01　管理列表的合法超页返回 503

R04 声明 `page` 为从 1 起的整数，`pageSize` 为 1–100，运行 OpenAPI 和 r2 管理工件均无 `page` 最大值。用真实合成管理员登录后，在已核对的 QA main 访问 `GET /api/v1/admin/acquisition-sources?page=<页码>&pageSize=50`。同一进程、库和账号下结果如下。

| 页码 | HTTP | 响应 |
| --- | --- | --- |
| 1 | 200 | `total=15`，15 项。 |
| 1000000 | 200 | `total=15`，空列表。 |
| 9223372036854775807 | 503 | `acquisition_sources.not_ready`，`data=null`。 |
| 1000000000000000000000000 | 503 | `acquisition_sources.not_ready`，`data=null`。 |

管理 CRUD 先得到总数，仍把 `(page - 1) * page_size` 交给 MySQL OFFSET，过大的有效页码被包装成目标不可用。预期为 200、空项、原页码、原页长、实际总数和总页数。请 Development 修复并回归有数据、空登记、边界页与极大页，交付新候选后由 fresh-context Verification 复验。 [实际路由](../../backend/app/plc_facts/api/source_registry.py#L81) · [登记分页](../../backend/app/plc_facts/crud/async_source_registry.py#L124) · [现有事实分页参考](../../backend/app/plc_facts/crud/async_v2.py#L116)

## 验收与运行证据

下列命令中的 Python 由仓库 `backend/.venv/bin/python` 执行。早期离线、构建、DAA 界面及 SQLite 证据按 QA1–QA3 记录沿用。

| 标准 | 独立运行结果 |
| --- | --- |
| AC01、AC02、R2-AC01 | `<RUN>/api_edges.py qa` 退出 0。三个管理方法上，匿名、无效、过期、已注销撤销和停用账号均返回 401 与 Bearer 挑战头，普通 operator 为 403，登记总数未变化。两个 API 并发 POST 覆盖同值 200 `created/unchanged`、互补 DB 均成功且授权完整、冲突绑定及不同类型共用实例均明确 409。管理分页见 QA4-01。 |
| AC03、AC04、R2-AC02 | `<RUN>/run_backend.py qa main <RUN>/qa/backend integration -p no:cacheprovider` 退出 0，3 passed，3.17 秒。双 API 同库验证登记后跨进程即时可用，受控并发中采样事务完成后接管才取得绑定锁。旧身份 403，新代次写入且成为最新值，三条旧新历史仍可读。仅历史、仅水位的旧代次首次登记被拒绝。另运行 `<RUN>/qa/live_contract.py` 退出 0。DAA 与第三方原字节在同进程 403 → 200 `committed/created`，在另一进程重放为 `duplicate`。匹配完整回执、MySQL 事实 SHA 与水位。尾部空格改写返回 409；迟到 seq 99 落历史、最新仍是 seq 100。核对五个 GET、默认关闭读权限和显式开启后的即时读回、第三方省略/空元数据、DAA 必填元数据、错身份/代次/DB、DB 1 和 65535、类型与范围拒绝、大小写、Unicode 组合/分解字节、U+FEFF、128 字节和字节序。自建脚本初次误套用管理成功文案到登录接口，改为匹配登录自己的合同后通过。 |
| AC05、R2-AC01 | `TMPDIR=<RUN>/qa node <RUN>/qa/browser-qa-smoke.cjs qa` 退出 0，无头 Chrome 连接真实 API。管理员新增 DAA 与第三方、读默认关闭、复制实际参数、追加读写 DB、固定 PLC、取消/确认接管、两个编辑者的过期版本 409 和明确文案、中文/英文、600px 窄弹窗。列宽 180→228，刷新恢复本地偏好，再恢复默认；普通账号无菜单且路由拒绝。浏览器脚本沿用交接夹具，改用 QA 身份、端口和截图路径。未知提交对账通过实际 ASGI/数据库探针，未在浏览器内注入断连；Web 对应错误分支沿用 QA2。 |
| R2-AC03、R2-AC04 | 用私有 Rust 测试二进制 `aiis_data_acquisition_agent_lib-1452dab104e07439`，清空继承环境，设置 `ACQ004_DAA_TEST_ROLE=qa` 和独立 TMPDIR，运行 `--exact services::local_delivery::tests::acq004_disposable_mysql_settings_sample_and_takeover --test-threads=1 --nocapture`，复跑退出 0，1 passed，3.52 秒。实际 Rust 设置事务、SQLite 重开、未绑定轮仅本地、显式开始、两代次 4 个单 DB POST 与匹配回执、同字节重放、退役队列 403 后原身份/正文 SHA/无回执、逐 DB 旧新历史和新代次最新值，再次重开保有回执。首次探针以 `sampleCounts.unknown` 判断已经结算，实际计数包含在途，读取 `lastError` 得 null。API 日志随后记录真实 403，未改产品或探针的独立新 profile 复跑验证了落盘后的 `scope_rejected`。合成 UI 的手填、粘贴、取消与冲突沿用 QA3；跨保存采样轮和 runtime2/3/4、原格式队列、异常与原路径重开沿用 QA2。旧二进制实际打开新格式及完整原生界面贯通仍缺直接运行证据。 |
| AC06、AC07、R2-AC05 | `run_backend.py qa <main/restore/guard> <RUN>/qa/backend predecessor` 三次退出 0；main 的 `upgrade`、`init`、`users` 均退出 0。独立 guard probe `run_backend.py qa guard <RUN>/qa/backend exec <RUN>/guard_probe.py qa` 退出 0。错误 schema 在 DDL 前拒绝，正确迁移保持 55 张前驱业务表快照和三条历史、三个最新水位。旧 profile 和未初始化均关闭准入；CLI 预览无写，显式导入后保留活跃 PLC 的独立只读 DB、无活跃绑定的历史只读 DB、零写绑定和独立实例。两类只读对拒绝上报。隔离实际 ASGI 通过会话夹具在真实 commit 成功后注入提交响应异常，返回 503 `commit_outcome_unknown`，GET 对账只存在一项，原样重试 `unchanged`。相同旧 JSON 再导入保留后续新增登记及原四项读取授权。DEV 首次实际 3818 导致前驱 revision 与五张部分新表并存，守卫拒绝盲重试，随后从前驱备份恢复并通过固定候选升级；QA 核对未变的守卫及实际错误目标拒绝。 |
| AC07、R2-AC05 恢复与维护 | 3 项 MySQL 集成包含接管后完整登记及两代次导出，用前驱格式兼容解析、实际前驱 `5f7a9c1e3b25` 的恢复 schema 核对两事实表列结构及完整排序行，再升级、再导入及幂等复跑并核对代次和原行。缺失或冲突恢复材料的拒绝由离线回归和文档步骤覆盖。未启动精确的前驱无 Bearer 应用，当前 Git HEAD 上较早的前驱实现仍使用 Bearer，所观测兼容边界为实际前驱 schema、恢复材料解析和再采用。只读 `cleanup-v2 --plan` 在实际 QA main 上核对新 revision 退出 0，错误旧 revision 退出 1、`plc_facts.maintenance_failed`；未执行清理 apply。BE-010 复核仅增加已知后继，仍比对实际 UUID/schema/revision，采用凭据不会自动刷新。 |

关键输出 SHA-256 分别为 MySQL 集成 `ecbdfc5ec37d47da04587798c4934464edbee50ff33e0667388cecdc48ad2b97`，真实浏览器 `3ae63efbbf953402c9a88b1053aa2a6d0441ceed24236b6036f9696f2a7919b4`，鉴权与并发 `83a7043e0589ff2c7d0195e58da72def15f700ba89eb47a94be026a6c9ee5968`，原字节和 GET `54f0020c697484e1b99b5d2f446f0a9619039a45a4f4c4dd835b11954dae4c3a`，迁移/导入及提交探针 `ea249e9f0f56c7cbd8204633bb2982bb30015c45a22f0c80af9452ea447df931`，DAA 复跑 `2af3b4b311a23dbb5fab39344d8569fa6c6df3f7809abb0e79fd4361974620e8`。DAA 私有测试二进制 SHA-256 `7b3777dd5c04a1a6851bbc7b9d2a47e9f99de2cce9913c3312ceeca8fde3467d`，测试钩子 SHA-256 `b2104bedc94378481c778db2a5ca4e8ccc33ca4734e416d9439dd1c9b5ca9280`。本轮只复跑变化和真实环境验收。全量 Rust 的历史 YAML profile 锁测试限制仍见 QA1。

## Verdict 与交接

**`qa_failed`。** QA4-01 交回 Development。当前候选的专属环境运行证据保留，返工后重新核对交付清单并独立复验分页。QA 自有两个 API 和 Vite 已于 12:05 停止，`lsof` 核对对应端口无监听；专属 Docker 资源和私有文件由协调者在后续复验完成后核对清理。此轮未操作现有 3307 dev、真实配置、真实 SQLite profile、设备或生产环境。Human Owner 最终验收待定。

# 独立验证 QA5

2026-11-13（Asia/Shanghai）。协调者在第五次 Development handoff 后以 fresh context 调用命名 `verification` 角色。独立核对项目契约、生命周期工作流、完整三文件、候选差异和已执行证据。应用 `project-governance`、`backend-arch` 和旧版 SQLite 准入补验所需的 `rust-runtime`。 [批准规格](spec.md) · [第五次交接](tasks.md#qa4-分页修复与第五次-development-handoff)

## 精确候选

- 交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交工作树。批准规格、第五次交接与 QA4 checklist 输入的 SHA-256 依次为 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`、`1921ad7539ee8eafad23f58f9e1b704c5ff11964a7f197100b1320a264b4df23`、`fc6c9df5df2148525c7dd43f99a994307f8e7a4dd453b6b326ae715bd1a4bc91`。QA4 正文原字节保留。
- 最后 64 项交接清单原字节 SHA-256 `a005c3a8abe188f55e6c4e25526c91a64adc238a171c301af479a8185de36269`，交付树逐项 64/64。对照 QA4 清单及私有副本，只有来源列表 CRUD 与定向测试两处变化。CRUD 在取总数后仅对页起点小于总数的请求发分页 SQL，其他请求保留原分页元数据。增量只复制这两个已核实文件到 QA 副本，再对比全部 674 项，逐项与交付树一致。排序键为路径、无空白的 JSON 副本清单 SHA-256 `5babeb14fd0ecae7f049b5b6dd2512588dd5f7cae161d82965ec5a47475f06b7`。`git diff --check` 退出 0，既有迁移文件无跟踪差异，冻结采集 OpenAPI SHA-256 仍为 `971b2791f42d5b6257c0d7768a8ba5b468908f5184bb7bde57563a5573f090a2`。 [分页实现](../../backend/app/plc_facts/crud/async_source_registry.py#L124) · [定向回归](../../backend/tests/test_acquisition_source_registry.py#L53)

## QA4-01 分页复验

macOS 15.7.7 arm64，Python 3.13.3、uv 0.7.8，使用项目已装锁定依赖。以下 `<RUN>` 为 `/private/tmp/arch-acq004-r2-run.NR4HRT`。以 `backend/.venv/bin/python <RUN>/run_backend.py qa main <RUN>/qa/backend primary` 启动单一 QA API `127.0.0.1:38406`，实际 MySQL 为 `127.0.0.1:33404` 的 8.4.6。独立探针核对同一连接的 server UUID `5e4fc94b-df14-11f1-bd61-76346c8acc30`、schema `arch_acq004_r2_qa_main`、唯一 revision `6a8c0e2b4d16` 与上海时钟偏移 28800 秒。

| 验证 | 独立结果 |
| --- | --- |
| `backend/.venv/bin/python <RUN>/qa/qa5_pagination.py` | 退出 0。实际合成管理员登录后，18 个有效请求均返回 HTTP 200、JSON 成功信封和整数分页字段，逐项比对 MySQL 的 15 条活跃 PLC 及原字节顺序。页长 2 时首页和第二页各 2 项，末页 8 有 1 项，首个超页 9 无记录，`totalPages=8`。默认页长 50 及页长 100 时首页有 15 项，首个超页 2 无记录，`totalPages=1`。页码 `1000000`、`9223372036854775807`、`1000000000000000000000000` 在三种页长下均保留原页码、页长和总数，`items=[]`。页码 0、-1 及页长 0、101 均为 422 `acquisition_sources.invalid_request`。实际 OpenAPI 页码最小值为 1，无最大值。探针前后登记清单一致。探针 SHA-256 `523fcc38426ad0ab73c0ed55ee9e1ddfcdb98ca2dec2ed69592e78fe344c9b16`。 |
| `uv run --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_acquisition_source_registry.py` | 在 QA 私有副本清空继承环境，以项目 venv、专用 uv 缓存、合成环境和 `127.0.0.1:1` 占位执行。退出 0，24 passed，0.33 秒。包括空登记仅取总数、普通分页、边界和超大页不会发出越界 OFFSET。空登记覆盖为离线 CRUD 测试。 |

## 旧版 DAA 准入补验

对应 R2-AC04。核对归档 DAA-010 `profile_contract.rs` SHA-256 `5a1d344176e235d9bafb83294473e423dd971fcafa0c607fd12b72fccaacf8a0`，其 `decode`、`local_json` 与探针逐字节相同，原版 `runtime_v4_sql` 也逐字节相同。旧版 `admit` 在调用 SQL 检查、文件锁和恢复之前传递 seal 解码失败。用协调者在私有源码副本构建的 Rust 测试二进制独立复跑，清空继承环境并设置新的专属 `TMPDIR`，运行 `--exact infrastructure::local_store::acq004_predecessor_profile_probe::old_admission_decoder_rejects_new_sealed_runtime_without_changes --test-threads=1`。退出 0，1 passed，0.25 秒。原解码器接受同一合成目录身份及原 v4 指纹组成的旧格式 seal，拒绝实际升级后的 seal 并返回 `profile_contract_invalid`。检查前后两库及 seal 快照相等，新版可沿原路径重开。探针 SHA-256 `39342b0600a321f11baac949d6368809df6375fe06a36ea140bdb3b2b41c9151`，二进制 SHA-256 `42797681e57a697083937c55d15a433859b32060494b23d0cc45ef74abdafce7`。运行证据限旧版准入解码路径和合成 SQLite，完整旧版应用未启动。 [旧版文件归档摘要](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/tasks.md)

## Verdict 与交接

**`qa_passed`。** QA4-01 在精确第五次候选上关闭。AC01–AC07 与 R2-AC01–R2-AC05 的其余隔离验证采用上文 QA1–QA4 对未变化路径的证据，包括双 API、实际管理员和浏览器、MySQL 导入和恢复、DAA 合成设置界面与实际 Rust/SQLite 上报及回执。此轮不重跑那些路径。恢复验证覆盖实际前驱 schema、前驱 profile 解析、事实及水位和再采用，前驱后端二进制未启动。DAA 界面验证使用实际构建和合成 IPC，Rust 实际发送至候选 API/MySQL 的链路见 QA4，完整原生 DAA 界面贯通和 Windows 未运行。全量 Rust 的历史 YAML 锁测试限制见 QA1。现有 dev `3307/8000`、真实配置、profile、历史和设备采用属独立操作。交 Human Owner 最终验收。

QA5 于 12:15:02 对仅服务本轮的 API PID 83507 发送 `SIGTERM`，会话退出 143，`lsof -nP -iTCP:38406 -sTCP:LISTEN -Fpcn` 无匹配、退出 1。退出时 Python 报告 24 个 semaphore 待清理。合成 SQLite 探针自行清除其 profile。此处已持久记录复验结果，QA5 不依赖私有源码或临时证据继续运行。其余专属资源交协调者核对清理。

协调者执行 `backend/.venv/bin/python <RUN>/fixture.py cleanup`，退出 0，移除本轮专属容器 `arch-acq004-r2-mysql`、网络 `arch-acq004-r2-net` 和卷 `arch-acq004-r2-data`。协调者复查 Docker 资源与端口，三个专属资源均无匹配，`33404`、`38404–38407` 与 `39404–39405` 均无监听。

# 独立验证 QA6 · 采集指南补充

2026-11-13（Asia/Shanghai）。命名 Verification 在 fresh context 复核本次纯文档交接，按 `project-governance`、`backend-arch`、`rust-runtime` 核对三文件、项目与相应目录契约、工作树、实际管理及采集路由、ORM、DAA 采样与上报路径和可用 QA5/开发输出。覆盖 R2-AC01/02 的登记、准入和回执口径，R2-AC03/04 的原样本及本地兼容说明，R2-AC05 的指南、链接和候选一致性。 [批准规格](spec.md) · [文档交接](tasks.md#采集数据指南补充与文档-development-handoff)

- `python3` 标准库 `hashlib` 配合 `git show HEAD:<path>` 退出 0。HEAD `fd999224a8756feda314a33148304b4bf3461876`，spec SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，文档 tasks SHA-256 `e3e140896aaf4270f968c33c58833d4067dd5dee378ce98675c8ada9a29d9e72`，原 checklist SHA-256 `6cb87d1e2279a3d42583aed0c595723d0648fdd203a8ba74a898db792cb1d94f`。清单 SHA-256 `7a327ceda201bd9659ca875dd4ae6a376b518fda857d50c30f47b89a1d8f05e2`，交付树 64/64 匹配。与 QA5 的 64 项同路径比较，只有中央指南和两份 Stage C 的摘要变化，原交接正文摘要可复原。两份 `docs/README` 摘要匹配额外固定值，各较 HEAD 只增加一条指南索引。英文及中文 Stage C 自历史标题起分别为 23,110 和 20,602 字节，SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`、`d3fb8a87caf7107eecff4ff6fb74048a87db44b5f6639e2eac179936a7f0b7cc`，与文档交接一致，自 M01 操作子段起亦与 HEAD 逐字节一致。`git diff --check` 退出 0。
- macOS 15.7.7 arm64。`python3` 静态脚本检查五份文档现行部分 90 个相对链接及其锚点、代码围栏、六张登记表名、两个 OpenAPI 工件和 Mermaid 15 条有向关系，退出 0。无 Mermaid 渲染器，本轮以源码检查图的结构与语义。以 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python` 对两个请求示例调用实际 `parse_sample`、`validate_times`，使用示例时钟，对回执调用 `receipt`，退出 0。两个请求符合形状和采集时间规则，回执正文与示例一致。
- 六张登记表、独立只读范围、两张事实表与 DAA 双 SQLite 的分工符合实现。管理端为 active admin，数据端一条 POST 与五条 GET 沿用免 Bearer 开发合同。已采用目标按事务提交应用登记，初始化由一次性旧 JSON 导入处理，缺失初始化与来源不匹配分别为 503、403。Stage C 已有 `.local/dev` 的条件式复用、原身份和原正文、未绑定样本仅本地、发送队列逐份处理、回执与只读对账的总体链路符合源码。

| 发现 | 证据与复验条件 |
| --- | --- |
| QA6-01　读详情的范围拒绝缺项 | 中央指南错误表只解释了读取 `403`。`history/{id}` 在不存在、过期或超读取范围时统一为 `404 plc_facts_v2.not_found`。需在操作表区分按 PLC/DB 查询的 `403` 和详情的 `404`。 [指南第 7 节](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) · [详情实现](../../backend/app/plc_facts/services/async_v2.py#L171) · [公开合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#提交与补传) |
| QA6-02　DBX 示例依赖未证实的客户端绑定 | 查询以 `:instance_id` 和 `:sample_id` 作为 MySQL 表达式。未在项目中找到 DBX 对该语法的绑定说明，已安装的 DBX 0.6.5 仅核对应用元数据。需用实际示例字面值给出可直接执行的只读 MySQL `SELECT`，并说明替换实例和样本 ID。 [指南第 7 节](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) |
| QA6-03　Stage C 两份手册写错授权章节且混淆冻结时点 | 隔离环境 §1 的链接文字均指 DAA-010 §6，实际锚点为 §7。现有 dev 采用见 §7，§6 是隔离 Mac 运行。现有 dev 段还把所有待传记录都描述成已有冻结正文和目标，实际上待传可能尚未冻结，详情中的 `origin`、`body`、`receipt` 可空。需对齐章节号，并明确仅在已有冻结或尝试记录时核对其目标和正文。 [英文手册](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.md) · [中文手册](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md) · [DAA-010 §7](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续) · [详情数据](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs#L100) |
| QA6-04　重复回执和冲突缺少准入及有效期限定 | 中央指南称原样重试即为 `duplicate`，正文或序号冲突即为 `409`。重试路径先复查登记和时间，接管后旧身份拒绝为 `403`，超期返回 `410 plc_facts_v2.expired_unconfirmed`。需在第三方示例和异常处补充这两个条件和到期处置。 [指南第 6 节](../../docs/acquisition-data-guide.zh-CN.md#6-第三方如何上报) · [重试校验](../../backend/app/plc_facts/services/async_v2.py#L49) · [时间规则](../../backend/app/plc_facts/v2_domain.py#L210) |

**`qa_failed`。** 该结论限上述精确文档补充候选，返 Development 修订后重新交 fresh-context Verification。上文 QA5 的隔离产品结果与待验边界按原候选保留。本轮未启应用、构建、DBX 会话或 Mermaid 渲染，未访问实际数据库、现有 profile 或设备，也未重跑原隔离用例。独立复验通过后交 Human Owner 最终验收。

# 独立验证 QA7 · 采集指南返工

2026-11-13（Asia/Shanghai），macOS 15.7.7 arm64。命名 Verification 在 fresh context 消费已批准 r2 规格、Development 交接、QA5/QA6 记录、当前工作树与对应实现。以 `project-governance`、`backend-arch` 和 `rust-runtime` 复验 QA6 的四项文档发现，覆盖 R2-AC01/02 的准入、读取与回执说明，R2-AC03/04 的原样本证据说明，以及 R2-AC05 的指南交付一致性。 [批准规格](spec.md) · [Development 返工交接](tasks.md#qa6-文档返工与-development-handoff)

| 复验项 | 结果与证据 |
| --- | --- |
| QA6-01　历史详情 | 通过。指南第 7 节区分 PLC/DB 范围读取的 `403` 与历史详情的 `404 plc_facts_v2.not_found`。详情查询以 `expires_at > now` 排除过期项，空结果与超出读范围均返回该 `404`。 [指南第 7 节](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) · [详情服务](../../backend/app/plc_facts/services/async_v2.py#L171) · [详情查询](../../backend/app/plc_facts/crud/async_v2.py#L143) |
| QA6-02　DBX 查询 | 通过。单条只读 MySQL `SELECT` 使用第 6 节请求与回执中的合成字面值 `'external-a'` 和 `'external-sample-001'`，并说明替换两处实际 ID。静态核对十个投影列与两个过滤字段均属于 `plc_facts_history`，两个过滤字段组成唯一键。 [指南第 7 节](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) · [事实模型](../../backend/app/plc_facts/models/v2.py#L9) |
| QA6-03　现有 dev 与冻结证据 | 通过。两份 Stage C 手册的隔离环境步骤 1 均指向 DAA-010 §7。已有 dev 的说明保全原采样身份，已冻结或尝试过的记录才核对详情中已有的目标、正文与回执。待传未冻结时这些值可空，与详情的左连接和可空字段一致。 [英文手册](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.md) · [中文手册](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md) · [DAA-010 §7](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续) · [详情数据](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs#L100) |
| QA6-04　重复、冲突和过期 | 通过。第 6 节将 `duplicate` 和样本冲突 `409` 限于当前准入且未过期的样本，说明接管后旧身份可被拒绝为 `403`，到期可返回 `410`。第 7 节给出完整 `plc_facts_v2.expired_unconfirmed` 和保留原记录、对账的操作。服务重试分支在计算重复或冲突前复查准入及时间，DAA 将该 `410` 映射为需处理。 [指南第 6 节](../../docs/acquisition-data-guide.zh-CN.md#6-第三方如何上报) · [重试服务](../../backend/app/plc_facts/services/async_v2.py#L49) · [有效截止](../../backend/app/plc_facts/v2_domain.py#L210) · [DAA 回执分类](../../automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs#L494) |

- `python3` 标准库静态核对退出 0。HEAD `fd999224a8756feda314a33148304b4bf3461876`。输入 `spec.md` SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`，`tasks.md` SHA-256 `0f259d237deb08072c4ffc8526b3eb5f27349ac90b39832f28859738ab54d900`，写入前 `checklist.md` SHA-256 `13afe28b7b3c0778e9a448683a05b7b99ea9fcc7d7ce018dee28a45e8fda71b3`。本轮交接清单原字节 SHA-256 `3a62a9a3053f3dd817fdeb6761bed2780354638b103945efd5545cfa3b0c9490`，64/64 匹配。分别比较 QA5、QA6 清单，同路径均仅中央指南及 Stage C 双语手册三处摘要变化。两份 `docs/README` 匹配交接固定摘要。
- 同一检查验证五份文档现行部分 90 个相对链接及锚点、代码围栏、三个 JSON 代码块和 DBX 查询列。Stage C 英文和中文自历史标题起各 23,110 和 20,602 字节，摘要与 QA6 一致，自 M01 子段起与 `git show HEAD:<path>` 逐字节一致。规格内 r1 原文可恢复为 21,335 字节，匹配原归档摘要。`git diff --check` 退出 0。

**`qa_passed`。** QA6-01–QA6-04 全部关闭。产品验证沿用 QA5 的精确隔离证据，文档中其余验收沿用 QA6 已通过的检查。本轮执行静态文档、源码与交付摘要核对，未重跑产品用例，未启动应用、执行 SQL、打开 DBX、渲染 Mermaid 或接触实际数据库、profile 和设备。完整原生 DAA 界面贯通、Windows 与实际目标采用仍依各自记录和授权。证据保存在本记录，未产生依赖的临时资源。交 Human Owner 最终验收。

## ARCH-ACQ-004 r4 dev 环境采用独立只读复核

2026-11-13（Asia/Shanghai），fresh-context Verification 对 Human Owner 另行授权的 `127.0.0.1:3307/industrial_level_2_system` 执行只读复核。范围涵盖 R4-AC05 迁后对账、R4-AC03 选项读取和 R4-AC01 匿名访问拒绝。输入 spec SHA-256 `e74f8254726b262feac0b3709e21263bde87331957b07c02da1711170d6f7234`，dev 采用 handoff 的 tasks SHA-256 `1452dd29b4870e930641269deb03e77e3b4f884f54242722676833da56a67233`，写入前 checklist SHA-256 `c7f987e5072f535f8a5a88940b08837a401b1d066125a3b64a55ff84e449cf82`。HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`，核对工作树 diff 及当前迁移、配置、路由和代理实现，迁移文件 SHA-256 `3c31bf18eae8a7140252ce0453bd5cd101ea7df5fecfda71b429f4299d2e3d56` 与已核验候选一致。 [规格](spec.md) · [采用交接及原迁移摘要](tasks.md#r4-已授权-dev-目标采用记录与-development-handoff)

- **目标与来源对账通过。** macOS 15.7.7 arm64，使用后端项目 Python 3.13.3。两段内联检查均执行 `uv run --no-cache --offline --frozen --no-sync python -B -`。数据库段使用与迁移相同的 aiomysql，连接前验证主机、端口和 schema，执行 `SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ`、`START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY`，查询目标身份、时区、`alembic_version`、表清单和登记列，最后回滚。实测 MySQL 8.4.6、会话 UTC+08:00、目标身份与私有配置一致、唯一 revision 为 `7b9d1f3a5c7e`。单表两行的 `plc_id`、`instance_id`、`source_generation` 和 `source_type` 均与旧私有配置逐字段、逐字节匹配，六张旧登记表均已退场。
- **事实表对账通过。** 同一只读快照使用迁移的 `fact_snapshot`，按相同顺序重算 `SHOW CREATE TABLE` 的 SHA-256 及全部有序行的 SHA-256。历史 4 行、最新值 3 行，两表结构及全行摘要均匹配 Development 留存的原迁前、迁后摘要。迁前取样证据来自 Development，本轮独立重算的是当前数据。
- **配置与 HTTP 通过。** `backend/.env` 的 profile 指向与项目有效 `V2Settings` 一致，启用开关已生效。新私有文件仅含 `target`，归当前用户，权限 `0600`，其目标及 revision 匹配数据库。新旧私有文件在本轮检查前后字节一致。内联 HTTP 段关闭代理环境变量，仅向现有服务发匿名 GET。8000 的 `/health` 返回 200、JSON `healthy`，5190 的 `/` 返回 200、Vite HTML，5190 代理 `/api/v1/acquisition-data/options` 返回 200、成功信封和 1 项有效选项，5190 代理 `/api/v1/admin/acquisition-sources` 返回 401、JSON 错误及 `WWW-Authenticate: Bearer`。两段默认沙箱探测分别因本机连接受限退出 1，获本机连接权限后各退出 0。
- **资源检查通过。** `lsof -nP -iTCP:8000 -iTCP:5190 -iTCP:3307 -sTCP:LISTEN -Fpcn` 确认约定端口监听，`lsof` 的 cwd 记录指向正式树后端和前端。采用自有临时目录 `/private/tmp/arch-acq004-dev-adopt-ko6p4zeq` 已不存在，`git diff --check` 退出 0。本轮检查以内联命令执行，无新增临时产物，前驱源码材料交协调者核对归属和清理时点。

**本次 dev 采用只读复核 `qa_passed`，交 Human Owner 手动验收。** 本次迁移未新建备份，依据 Human Owner 对此目标的一次性授权。复核限数据库与配置对账、GET 响应，未执行迁移、配置或数据写入、服务启停、DAA 启动或样本上报。dev 的登录操作、Web/DAA 人工验收、真实设备联调和生产部署仍未验收。原源码及隔离验证的 `owner_accepted` 和 QA3 记录保留。

### dev 采用后的测试资源回收复核

2026-11-13（Asia/Shanghai），协调者按 Human Owner 的测试遗留清理指令回收本任务自有产物。协调者报告，清理前已核对交付树的快照基线文件、r1 的 12 项已被 r4 取代的候选、r3 的合成 `sitecustomize.py` 及两目录无进程占用。Verification 执行 `python3 -B -`，用 `Path.exists/is_symlink/is_dir` 只读复核，退出 0。确认 `/private/tmp/arch-acq004-r1.d1hrlb6y` 及 `/private/tmp/arch-acq004-r3-dev.0fxOzki5` 下的 `source`、`dev-runtime-logs`、`migration-evidence-nx5phqf9` 和 `migration-setup-logs` 均已不存在。

同一 r3 根目录下的 `frozen-r2` 与 `pre-integration` 仍在，供核对尚未由 Git 固化的前驱及整合前源码，待协调者确认相关内容已固化且无后续依赖后清理。真实旧配置与历史数据不在本次回收范围。此记录仅补记资源状态，dev 人工验收仍由 Human Owner 执行。
