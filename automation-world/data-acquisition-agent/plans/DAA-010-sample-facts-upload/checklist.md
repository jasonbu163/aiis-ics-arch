Task ID: DAA-010
Revision: r5
Workflow Mode: STD
Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Status: qa_failed
Handoff: QA2 复验关闭 F-R5-QA1-001/002 的原复现路径。新发现 F-R5-QA2-001 交回 Development，独立结论供 Human Owner 审阅。修订候选重新交接后由 fresh-context Verification 复核。

# 独立验证 QA1

2026-11-12（Asia/Shanghai）。本次为 Development 完成 [r5 handoff](tasks.md#developer_handoff--daa-010-r5) 后独立发起的 QA，角色配置为 `contract_only`。验收面以[批准稿](spec.md#5-验收标准)为准。

- 正式交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876`，包括未提交候选。`spec.md` SHA-256 `e63c4909027a097e258ab0e812515ad4f4dcf0ddc2266e765e1802075ad5e27c`，Development 交付清单 SHA-256 `3f87893b79c2b5f97074bf6631f3bca52d4cf5a56d5148c965978e6d40767430`。`shasum -a 256 -c` 核对交付清单 47/47。共享 `CODE_INDEX.md` SHA-256 `83d55836c15a9793f6967240d36fe30f88a313c25c7b6ef5d6d59ccf0b8a71eb`，其中 DAA 条目对应实际结构。工作树还含已存在的 PM、provider 和并行工作。
- 按根 `AGENTS.md`、canonical workflow、DAA、DS、后端的项目文档和对应技能核对交接、差异与运行证据。独立验证写入本文件。源候选和批准稿在本轮收尾复核时一致。

## 阻断发现

### F-R5-QA1-001 合法但尚未存在的 profile 路径首次启动被拒绝

**影响 R04 / AC06，阻断正常首次启动。** 在 Mac arm64 上以 QA 自有源码副本执行普通 `pnpm tauri dev`，保留原 Snap7 feature，Vite 使用 §6 预留 QA 端口 15194。启动前 `daa-profile` 不存在，所选 env 文件为空。进程 PID 39902 的可执行文件、工作目录、`DAA_ENV_FILE`、`DAA_PROFILE_DIR` 和 `TMPDIR` 均经 `lsof` 与过滤后的进程环境确认属于 QA 根。精确启动形态如下。

```sh
qa=/private/tmp/daa010-r5-qa-private
cd "$qa/source-copy/automation-world/data-acquisition-agent"
test ! -e "$qa/daa-profile" && test ! -L "$qa/daa-profile"
env -i PATH="$PATH" TMPDIR="$qa" DAA_ENV_FILE="$qa/daa.env" \
  DAA_PROFILE_DIR="$qa/daa-profile" DAA_PLC_READ_ALLOWED=true \
  pnpm_config_verify_deps_before_run=warn pnpm tauri dev
```

Rust 编译结束后原生进程实际记录 `{"error_code":"time_profile_unsupported:profile_changed","event":"runtime_rejected","process":"daa","resource":"profile","result":"rejected"}`。Owner 提供的 QA 窗口截图显示“无法确认运行模式，控制台已停止加载”以及“此 profile 的时间合同不受支持，旧配置和历史已保留”。失败路径实际仅产生零字节 `.daa-runtime.lock`，没有 `local-acquisition-v1`、SQLite 文件或旧历史。运行失败的进程未持有 SQLite 文件句柄。日志 SHA-256 `77c69a7954a92b7103aad855c4c6eaec8b232e67621a8d4547c11cbfcdd59b50`，错误截图 SHA-256 `74e2fd9d15851370ac28957d449fbe0c2f48572d1efe3726432cadc5152495cb`。

首次 `capture` 记录 `profile_identity=None`。`ProfileLock::acquire` 为创建锁而建立父目录，下一次 `capture` 得到目录身份并在初始化分支前拒绝。相同快照比较静态存在于 HEAD 的 `profile_contract.rs:636,665–666`，本轮确证的是当前候选的实际用户路径。默认选择与显式选择进入同一 `LocalEngine::open`，因此默认目录缺失时有同一风险。默认用户目录与 Windows 原生行为未实测。期望合法新路径在持有原安全约束的前提下建立 config2/runtime4 并从停态打开，实际不兼容的历史库继续按原准入规则处理。 [profile 快照和准入](../../src-tauri/src/infrastructure/local_store/profile_contract.rs#L314) · [加锁创建目录](../../src-tauri/src/infrastructure/local_profile_lock.rs#L20) · [普通运行入口](../../src-tauri/src/services/local_supervisor.rs#L78)

用 `mkdir -m 700 "$qa/daa-profile-precreated"` 预建另一个空目录后，同一候选普通启动成功。PID 43050 持有独立双库，日志于 `16:13:10.123309000+08:00` 记录 `runtime_started / stopped`，只读 SQL 显示 config2/runtime4、同一实例 `f8adcf15-6eb8-4c2c-99af-9145db34a0e2`、时间合同 `asia-shanghai-rfc3339-ms-v1`、0 样本、0 v2 尝试。Stage C 指南已经给出预建目录步骤，实际首次路径失败仍成立。 [启动指南](../../STAGE_C_GUIDE.zh-CN.md#L40)

### F-R5-QA1-002 新增测试夹具拒绝约定的独立 QA 根

**影响 §5 锁定测试及 AC02–AC06、AC09 的可复现性。** `sample_upload_tests.rs:25–28,108–111` 的新夹具把 `daa010-r5-dev-private` 写为 TMPDIR 必含子串。整个文件是 `#[cfg(test)]`，受影响两个入口为 `#[cfg(unix)]`。本轮它导致 18 个额外断言失败，覆盖测试经共享 `sealed_fixture` 扩散到旧 profile 准入、两 DB、目标重绑、暂停、持续采集公平和 ACK 写入故障等。`delivery_tests.rs:20–24` 的历史夹具另含 `/private/tmp`、`daa-008-r1-a-` / `daa-008-r2-a-` 的原有路径门槛，当前 diff 只为该夹具增加 Development 路径作为备选。直接导致本轮额外 18 项失败的是新 `sample_upload_tests.rs` 的 Development 路径断言。 [新夹具](../../src-tauri/src/infrastructure/local_store/sample_upload_tests.rs#L23) · [测试模块装配](../../src-tauri/src/infrastructure/local_store/mod.rs#L8) · [旧夹具](../../src-tauri/src/infrastructure/local_store/delivery_tests.rs#L14)

预期是 §6 的 QA 自有根可以独立执行适用套件并保持夹具路径安全。Mac 已复现。Windows 仍需原生及适用工具链复验，Unix 限定的新断言本身没有进入 Windows 产品路径。`rustup target list --installed` 只返回 `aarch64-apple-darwin`。

## 验收逐项

| 条目 | 结果及证据 |
| --- | --- |
| AC01 | **通过独立 provider 部分。** §2 的 3 个合同及 5 个源码增量 SHA 全匹配。独立 QA FastAPI/MySQL 接收无 Bearer POST，四种错误登记值均 403。五个 GET 成功，已获写入登记而缺 `readScopes` 的另一 PLC 在 latest/history 均 403。 |
| AC02 | **部分证实。** `versioned_configuration_import_activation_and_two_db_collection` 在诊断目录通过，走实际保存/导入 readiness/激活/提交/重开和合成 S7 transport，DB501 为 400 good，DB502 为 512 bad，两份在 SQLite 以合成回执独立确认。独立真实 HTTP 向 QA MySQL 分别提交 400/512 点和 `bad/null/bad_timeout`，524288 B 成功，524289 B 返回 413，513 点返回 422。两个阶段使用不同夹具。真实 DAA 已保存超 1 B 样本零 POST 的证据来自 DEV，QA 未独立做合并链路。 |
| AC03 | **部分证实。** QA 诊断目录中的实际 worker/合成 transport 单测通过，涵盖本地 ACK 写入失败后同正文重试、v4 reopen 保持 unknown、确认/保留。独立 HTTP 原字节重发获得 `duplicate`，MySQL 历史唯一。本轮未复跑真实 worker 的响应丢失、离线 S7 或标记尝试后退出。DEV 的响应丢失实验与进程退出实验使用不同 transport。 |
| AC04 | **部分证实。** 独立 provider 实测 403、409、410、413、415、422 的完整错误信封及无额外历史行，诊断目录中严格回执、局部来源阻断、暂停期间旧在途回执结算等定向用例通过。本轮未在同一实际 DAA/provider 组合注入 503、错误回执、配置切换及延迟响应。 |
| AC05 | **部分证实。** QA provider 的 DB91 先 seq3 后 seq2，history 两条按原时间读回，latest 400 个点保持 seq3。独立 `v2_worker_drains_bounded_bursts_and_interleaves_old_with_new` 与 `retry_clock_ignores_running_wall_jumps_and_clamps_restart` 通过。后者为时钟组件注入，未调整 Mac 系统时钟。 |
| AC06 | **失败。** F-R5-QA1-001 发生在正常首次路径。已预建空路径成功并停态。合成旧库、v2 保护、容量、原生 hot-journal 恢复及四项 v4 回归由诊断目录下单测部分证实。正常 QA 根因 F-R5-QA1-002 额外 18 项失败。四个历史失败详见下方。未独立用旧产品二进制打开 v4，也未触达用户数据。 |
| AC07 | **未完成。** QA DS 原生空界面已打开，`ds_get_runtime_snapshot` 为 `ok`，S7 35118 始终未开 listener。DAA 的首次失败与预建路径正常停态已实际确认。发现返修项后停止本候选的 UI 配置，未完成独立环回 S7、原生上报和页面操作矩阵。DEV 原生链路与界面观察见下方。 |
| AC08 | **Owner 后续验证。** Mac arm64 测试记录已固定。Windows x64 构建、独占锁、普通重开、发送中退出、热 journal、历史与页面均未实测。 |
| AC09 | **部分证实。** 定向 Node 和 SQLite 测试覆盖设置/拼接、显式重绑、未核对的旧地址保持、记录原/新尝试。DEV 独立代理证据存在，本轮未复跑别名代理和原生设置/重启。GET 诊断的实际行为见下方。 |

## 运行记录与证据

环境为 Darwin 24.6.0 arm64、Asia/Shanghai、Cargo/rustc 1.89.0、Node v22.19.0、pnpm 11.11.0、uv 0.7.8（锁定后端环境 Python 3.13.3）。各项运行使用 QA 私有根 `/private/tmp/daa010-r5-qa-private`，权限 0700，凭据及私有 env 0600。原生端口替代限临时副本各自的 `package.json`、`vite.config.ts`、`src-tauri/tauri.conf.json`。DAA/共享源文件复核 291 条。DS 从 HEAD 重建，补齐 `.gitignore:15` 遮蔽的 `src/app/simulator/views/logs/index.vue`，摘要 `68c6c96ccbc6b77144531e39d5b4588f497fb97d1590394a8c18b06dfa04270b`，controlled Snap7 34/34，临时 CMake 缓存清除旧构建路径后编译成功。已有 DS test-only 宿主锁定另一任务的根、manifest 和 S7 端口，因此未用于本次配置。

| 命令 | 结果 |
| --- | --- |
| `git diff --check`，`cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check` | 各 exit 0。 |
| `env pnpm_config_verify_deps_before_run=error pnpm build --outDir /private/tmp/daa010-r5-qa-private/daa-formal-dist` | exit 0，现有 Rollup PURE 注释及大 chunk 警告。 |
| `node --test tests/facts-delivery.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs` | exit 0，15/15。含真实 Vue SFC、状态筛选、存储策略以及中英文案和列宽辅助逻辑。 |
| 六个 README/指南及 `spec.md`、`tasks.md` 的 Markdown 相对目标扫描 | 119 个本地目标存在，锚点未自动校验。 |
| `env -i PATH="$PATH" CARGO_HOME=/Users/jason/.cargo RUSTUP_HOME=/Users/jason/.rustup TMPDIR=/private/tmp/daa010-r5-qa-private/daa-008-r2-a-tests TZ=Asia/Shanghai cargo test --manifest-path src-tauri/Cargo.toml --locked --lib -- --test-threads=1` | **exit 101，125 passed / 22 failed / 2 ignored**。日志 SHA-256 `900ffdad2d62ae7ba26d97c14694795ad795cc151df0290941512c116a72ec7d`。18 个新增拒绝均停在 F-R5-QA1-002 的路径断言。 |
| 同一命令，`TMPDIR=/private/tmp/daa010-r5-qa-private/daa-008-r2-a-tests/daa010-r5-dev-private` | **exit 101，143 passed / 4 failed / 2 ignored**。QA 根内的诊断子目录只满足夹具字符串断言。日志 SHA-256 `b77f7757c5bb8504d6a388103b21028e8c1d92710f9cfe383c075e2857cb4f58`。首轮结果有效。 |

两次全量均有下列四项失败。前三项使用历史合成账本，进入 `profile_contract_business_admission_failed`，第四项发生在 YAML 历史测试尝试取得锁时。DEV 提供的 HEAD 比较已记录相同四项，QA 本轮复现当前候选四项，未重新运行 HEAD 全量。

- `maintenance_faults_recover_original_protected_ledger`
- `periodic_maintenance_ioerr_reaches_product_log_and_stdout`
- `periodic_maintenance_log_failure_keeps_history_stop_and_shutdown_available`
- `yaml_migration::tests::migration_empty_retry_cas_capacity_lock_and_private_protection`，`yaml_migration_tests.rs:358` 返回 `profile_locked`。

QA 诊断目录实测下列四项通过，覆盖 v4 合法材料、定向故障和激活策略。

- `v4_maintenance_fault_recovery_keeps_receipts_and_protected_samples` 覆盖写失败与中断事务恢复，v2 回执及受保护样本保留。
- `v4_periodic_maintenance_ioerr_preserves_ledger_and_reports_failure` 覆盖写失败日志与账本完整性。
- `v4_periodic_maintenance_log_failure_retains_history_and_stops_safely` 覆盖日志失败后拒绝继续采集，历史、停机及重开能力。
- `snapshot_storage_policy_follows_active_revision_not_saved_draft` 覆盖无活动策略、已保存草稿和活动版本的不同状态。

### 独立 provider / MySQL

- Docker 预检发现 `mysql:8.4.6` 已存在，`linux/arm64`，镜像 ID/摘要 `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`。只读预检的首次默认沙箱命令因 Docker socket 权限拒绝，已获准的精确资源命令成功。新网络、卷和容器均用 `aiis.task=DAA-010-r5-qa` 标记，挂载与端口记录见收尾段。
- 从 HEAD `git archive` 加 §2 五文件组装脱敏副本 615 项，清单 SHA-256 `92a9145df8fcdd8063de949157c5775e5a72640ccbba94e7107c0682c1a2b379`。私有 `settings.py`/v2 API import 路径和唯一 `.env` 已核对。先读 MySQL 8.4.6、UUID `e3b59e3d-de6f-11f1-802e-82aa7f938855`、`daa010_r5_qa`、`daa010_qa_app@%`、仅 schema 权限、0 表及 `+08:00` 28800 秒。首次只读检查因 QA 脚本未考虑 MySQL 对 schema 下划线的 grant 转义退出 1。复核返回的真实 grant 格式后，修正合成检查并通过，期间没有数据库写入。
- 从私有副本以 `env -i`、私有 `TMPDIR` / `UV_CACHE_DIR` 执行 `uv run --offline --frozen --no-sync --project <正式 backend> alembic heads`、带 `ACQ_RETIREMENT_*` / `ACQ_FACTS_*` / `TASK_CUTOVER_*` schema、UUID 和操作 ID 防护的 `alembic upgrade 5f7a9c1e3b25`，各 exit 0。迁移后同 UUID/schema、revision `5f7a9c1e3b25`、56 表，两个事实表各 0 行。迁移日志 SHA-256 `0a5d021ded7210106bc3a112269157686767011215de68864bb361e81c6a86bd`。
- 同一锁定环境从 QA 私有副本执行 `python -m uvicorn main:app --host 127.0.0.1 --port 38118 --workers 1`。独立 `check-http.py` 使用同一清理环境和显式 `PYTHONPATH`，仅访问 QA 38118 和 33318，exit 0。核对 HTTP status、`Content-Type`、完整 success/error JSON、MySQL 内容 SHA 和 `source_type`。无 Authorization 头，400/512 点收到 `committed/created`，真实失败类型见上表。合成验证产物 `http-result.json` SHA-256 `ba359471564fa049031dacd4306a9b3b0b8a0c8464d8da33e9ae590ef6a6b9b2`。
- 真实 POST 的三份可读 DB 样本为 DB91 seq3 `95e5f086-83d0-4309-ae0f-266fb3df4edc`（400 点，SHA `49553a9396a532a71f594947d2be032ec309dd2168837125bbf5af5138a8f61b`）、DB92 seq3 `19b8594d-2452-487f-978d-b36300a71f9b`（512 点，524288 B，SHA `50bb9d4e0a937510875a361f4a7e16ab5be6e181a702893dc463a1287882936a`）、DB91 后到 seq2 `fa97c85a-e8b8-4487-8be1-94899c0dc122`（400 点，SHA `74f2e5256d8848e4d5d159109338fc37a792a653c36e281551bd77a8b5010b1c`）。三份的 `instanceId` 为 `a9882dac-574e-4905-a0b5-0f5ddfc8e3cf`。DB92 用相同正文再提交返回 HTTP 200、`code=200`、`message=success`、`contractVersion=plc-facts/v2`、对应实例/样本、`status=committed`、`outcome=duplicate`。SQL 历史 4 行包含一个无读取权限的合成来源，两个可读 DB 的 latest 为 seq3 的 400/512 点，DB91 的历史两行、detail 400 点、browse total 400。GET 结果用于对账。

### 开发证据复核和界面边界

- 在开发材料回收前，独立重算三份留存 manifest 的 24 + 7 + 3 项 SHA/长度，全部匹配。复核了 provider 结果、两个真实 worker DB 回读、旧/新 URL 及 duplicate、超限与退出证据、Dev 最终库测试、原生两张截图、首次/恢复 readback、离线冻结快照及闭库日志。DEV 原生证据显示 9 条正常、8 条断网补传，17 条确认、73 次尝试，SQL history 17、latest 2。截图分别为调整前布局与实际断网状态，调整后的四卡片一行、筛选、详情、最窄窗、切换语言和帮助交互属于 `tasks.md` 所记的 Owner 手工观察。本轮 QA 的独立结果见前表。
- DEV 的 `draft_saved` 与 `configuration_activated` 事件相差约两秒，独立读回发生在激活后，草稿 7 天与活动 8 天同时出现属于 Owner 的中间观察。独立单测覆盖了草稿与活动策略分离。DEV 原生重开日志确证停态，后有显式启动记录。后来界面显示停态且无红色告警的原因、时间及操作者无法从现有日志归因。
- `tableWidths.ts` 使用应用/表/字段键和 WebView `localStorage`，配置未显式按 DAA profile 绑定 WebView 数据目录。DEV 在原生拖拽、过滤、复位已观察，重启持久化和共享来源隔离未证。QA 采用独立 15194 Vite 源以减少旧原生 origin 偏好共用的可能，未操作原生偏好或读取用户 WebView 存储。
- R06/AC09 的“保留的 GET 诊断”按条件适用。HEAD 的读按钮在本候选撤出，旧 `daa_test_facts_endpoint` IPC 固定返回 `legacy_delivery_read_only`，因此当前 DAA 内没有通过实际 GET 路由读取的诊断。双语指南说明使用外部后端 GET/`readScopes`，自定义 POST 无法推导读地址，仍可核本地详情与可靠 POST 回执。独立验证确认了外部 GET 与权限边界。本轮交接可核对批准稿的草图方向和 `tasks.md` 的实际观察，缺少可逐项比对的原始草图工件。如果 Owner 的验收要求保留原读按钮，现候选缺少该 UI 能力，需 PM 明确后交 Development。本轮未登记为 DAA 内 GET 诊断通过。 [IPC 行为](../../src-tauri/src/commands/local_delivery.rs#L139) · [双语手册的中文操作](../../STAGE_C_GUIDE.zh-CN.md#L97)

## 交接与资源收尾

- QA1 `qa_failed` 由两个精确发现决定。已向 Development 发送可复现路径、预期与现有证据。重新交接需保有旧库保护和并行工作，并提供新精确候选以独立重测两项发现、余下 Mac 链路与 Windows 待验范围。Human Owner 保留对应范围最终验收。
- 首次 DAA/Vite PID 39902/39865，预建目录 DAA/Vite 43050/43014，DS/Vite 40193/40153，provider 43789。分别结束各自的任务会话，`ps` 复核无上述 PID。provider 日志记录正常关闭。DAA/DS 的会话停止和句柄释放已证，预建 DAA 日志无 `runtime_stopped / clean`，故该停止只记为进程退出。端口 15194/15196/35118/38118/38218 无监听，`lsof +D` QA 私有根无打开文件。
- Docker 容器 `590e7bff5d531b90d8a5f094d2b6bb608849fe7ffaf4324d0d425db2e0cfcc2f`，专属卷 `daa010-r5-qa-mysql-data`，网络 ID `16e7f16d75a9ab86d42c5538732b096dc0272ff666ec50ae602592978050dfa9`（`daa010-r5-qa-net`）。三者标签 `aiis.task=DAA-010-r5-qa`。启动后 inspect 证实只挂此卷到 `/var/lib/mysql`，唯一端口映射 `127.0.0.1:33318`，网络唯一成员是该容器。协调者对精确容器执行 stop、rm，确认卷没有使用者、网络成员为 `{}`，再删除精确卷和网络，均 exit 0。QA 独立按精确 ID/名称过滤列表均无匹配，六个专属端口均无监听。
- 原失败目录、两份测试日志和截图已完成证据核对。此处的实际命令、结果、身份和摘要为持续记录。协调者核对 QA 私有根的真实路径、所有者、0700 权限、无挂载点及无打开文件后，仅回收该精确根，exit 0。QA 独立复核原路径不存在。

## 独立验证 QA2

2026-11-12（Asia/Shanghai），返工后的 fresh-context Verification，角色配置 `contract_only`。QA1 的两项发现和当轮 `qa_failed` 保留于上文。QA2 对 [返工交接](tasks.md#developer_handoff---daa-010-r5-qa1-rework)的结论为 **`qa_failed`**，由 F-R5-QA2-001 决定。

- 正式交付树 HEAD `fd999224a8756feda314a33148304b4bf3461876` 加未提交候选，批准稿 SHA-256 `e63c4909027a097e258ab0e812515ad4f4dcf0ddc2266e765e1802075ad5e27c`。返工交付清单 SHA-256 `23ea1cf05f18efdbd0625885f81d4e39275da8892d7cb8d195c22111d37167ca`，QA 开始和收尾的 `shasum -a 256 -c` 均 47/47。以 [§4](spec.md#4-精确实施范围)核对候选的 DAA 源码、定向测试、双语文档和 `CODE_INDEX.md` 的 DAA 条目。共享索引的完整摘要含并行变化。Provider、合同、PLAN 及其他并行工作由各自任务负责。旧命名和源导入测试只将旧账本夹具改为显式 runtime2，保留旧 JSON、CAS、历史和回执断言。
- QA2 独立重算返工开发证据清单内 14 个工件的 SHA-256 和长度。清单摘要 `e6f2ee7786a11f8ecc4566309a7089c0ad7097988c9278b30831707751942cb8`。阅读了旧候选首次失败、预建目录通过、新候选七个路径回归、151/4/2 全量及正式原生停态日志。协调者获知 QA2 已完成读取并回收 Dev 证据根，实际记录见 [tasks.md](tasks.md#qa1-rework-private-resource-cleanup)。下文的独立复验使用 QA2 自有材料。

### F-R5-QA2-001 首次创建期间替换的空目录被封存为新 profile

**影响 R04 / AC06，阻断本候选。** R04 要求普通入口沿用既有 profile 选择校验，并在所选目录使用双库；AC06 核对首次建库及原锁保护。候选在 `create_dir` 成功与第一次 `symlink_metadata` 之间尚无原目录身份，随后把按路径观察到的替代目录身份当成自己的创建结果。空目录替换因此通过后续两次快照和路径加锁。现有空目录替换回归在 `stat` 得到身份之后才注入，QA2 运行该测试通过。此处是更早的窗口。 [首次创建和加锁](../../src-tauri/src/infrastructure/local_store/profile_contract.rs#L673) · [现有空目录替换测试](../../src-tauri/src/infrastructure/local_store/profile_contract_tests.rs#L1736)

在 QA 私有根使用 `cc -dynamiclib -O2 -Wall -Wextra` 编译临时 Mach-O `__DATA,__interpose`，源 SHA-256 `7ec4a3e99ee60d66bc1423d929e98066cfeee16680b855f67b27b7a13652f353`。使用 `env -i`、`TMPDIR=/private/tmp/daa010-r5-qa-private`、`DAA_008_R2_CHILD=init`、`DAA_008_R2_PROFILE=<QA 合成路径>` 和 `DYLD_INSERT_LIBRARIES=<QA dylib>`，直接调用正式候选 Cargo 库测试二进制 `--exact infrastructure::local_store::profile_contract_tests::profile_contract_child --nocapture`。没有改测试或产品文件。注入仅匹配本轮完整合成路径。该子用例若 `Stores::open` 失败会在 `unwrap` 报准入错误，若打开成功则随后刻意触发 `expected checkpoint exit`。下表三种注入的外层 exit 均为 101，实际差异来自准入分支及文件证据。

| 注入时序 | 实际结果 |
| --- | --- |
| 最终路径原本不存在。包装 `mkdir` 先执行真实调用，成功后在返回产品代码前把目录移到 `.original`，以 0700 在同路径建立另一空目录。 | 候选 inode `83151190 → 83151191`，进入打开成功后的 `expected checkpoint exit`。原目录空，替代目录实际有 0 B `.daa-runtime.lock`、`config.sqlite`（只读 PRAGMA 2）、`runtime.sqlite`（4）及 `profile-contract.json`。日志 SHA-256 `b313dddb203125d41334ba39b0473adaa85f2ed87a94e8170e997855b24be3d4`。HEAD 对相同注入返回 `time_profile_unsupported:profile_changed`，替代目录仅留 0 B lock。HEAD 对照日志 `d8f8b33f4cff8710a482e459e86091b5f3d6cea6c38b2678744c96e9162952f7`。 |
| 同一 `mkdir` 时序，替换为已有两个 SQLite 文件且有合成哨兵数据的目录。 | 候选拒绝 `profile_changed`，无锁或封存文件。两库 SHA-256 `0459ed4d43088a3d9259572ef6199f09e4b29545143e72a4c7427209359702c0` / `629090b90075c632706c1ac0785ba9866fca2b843b9af9d34b99cf3843fd6177` 前后一致，只读查询得到原哨兵。日志 `b03c5e38dca10147922651538990209b93c908d26b6ee937a5724ecdba0e9885`。 |
| 既有空目录已通过 pre-lock 快照，包装 `open` 在对精确 `.daa-runtime.lock` 调用真实 `open` 前，以另一目录替换，内含两个合成历史文件。 | 候选与 HEAD 均在锁后身份校验拒绝 `profile_changed`，只在替代目录留下 0 B lock。原两文件内容 SHA-256 `398e9e45b0878316da54894727b56a8b12f773e2128e4538a7541079b83c9ff8` / `38fd0ec2892a064102ee83dbf637589da160c19498712d60bb41ecb096326289` 前后一致。候选日志 `4a3ecbc3d89568f1fcf72e8b538c281a17255563295f7b7bf25eda63d48d7875`，HEAD 日志 `cdc319cc25d8505ef1a3c2ec418e03423fd0850764e1adcf4bffca2cd9d111cb`。本边界属于既有行为。 |

已证影响是不同 inode 的替代空目录获准并被初始化为受信 profile。带既有 SQLite 的对照保留了原数据，本轮无历史数据损坏证据。返工需对确实新建且身份连贯的目录成功开库，并在该替换发生时拒绝初始化。继续保留 pre-create 竞争、已有材料及符号链接拒绝、中断保全、同进程锁和封存重开验证。实验涉及有权限重命名目录的合成进程，适用结论限于所列时序。

### 首次原生启动和独立 Cargo 回归

- **F-R5-QA1-001 的原复现路径已关闭。** Darwin 24.6.0 arm64，Cargo/rustc 1.89.0、Node 22.19.0、pnpm 11.11.0。普通 `pnpm tauri dev` 从 QA 副本启动，Tauri 原 `rust-snap7-driver` feature 保留。临时 DAA Vite origin 15194 用于隔离应用 WebView 的本机偏好，DS origin 15196。两应用各只替代副本内的 `package.json`、`vite.config.ts`、`src-tauri/tauri.conf.json` 的开发端口。DAA、DS、CU 和 shared 的 740 个文件与正式树匹配，清单 SHA-256 `dab6651577bd4ac4dacb768bf71b43622f00ffaaa0f0e3de09c985b745dad097`。其中排除六份端口替代配置；副本有五份 HEAD 版本的治理文档（PLAN、spec 和目录索引）与当前树不同，运行证据以正式批准稿为准。DS 的 Git 忽略日志页及 34 个受控 Snap7 文件从正式源码补入副本，日志页 SHA-256 `68c6c96ccbc6b77144531e39d5b4588f497fb97d1590394a8c18b06dfa04270b`，Snap7 两树 `diff -qr` 一致。默认沙箱拒绝 Vite bind，后以已批准的隔离端口重跑。补齐 shared 和忽略的原生源后实际编译启动。
- 16:43:44 启动前 `test ! -e "$qa/daa-profile" && test ! -L "$qa/daa-profile"` 均成功。DAA PID 49494、Vite PID 49446 经 `lsof` 验证，进程 cwd 和可执行文件在本轮副本。过滤 `ps eww` 证实使用空 0600 `DAA_ENV_FILE=$qa/daa.env`、`DAA_PROFILE_DIR=$qa/daa-profile`、`TMPDIR=$qa`、`DAA_PLC_READ_ALLOWED=true`、`TZ=Asia/Shanghai`。启动通过 `env -i`，仅传上述隔离变量及命令所需工具链环境。16:44:09 实际 `runtime_started / stopped`，无 `runtime_rejected`。新建独立双库的只读 PRAGMA 结果 2/4，实例同为 `e65b3042-cdd0-45b8-9f48-84822efbe3ae`，时间合同 `asia-shanghai-rfc3339-ms-v1`，活动版本、样本、尝试及来源为空。收尾日志 SHA-256 `0263d72d204529a2965e3d889f24e934f0aa9d16553a56fcdb707da3f87dd6d1`。这次实测使用显式新路径。默认用户目录及 Owner 首屏观察待验。
- **F-R5-QA1-002 已复验。** 两次完整命令使用 `env -i PATH="$PATH" CARGO_HOME=/Users/jason/.cargo RUSTUP_HOME=/Users/jason/.rustup TMPDIR=/private/tmp/daa010-r5-qa-private/daa-008-r2-a-tests TZ=Asia/Shanghai cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib -- --test-threads=1`。规范化 TMPDIR 无 Development 子串。默认沙箱首次 150/5/2（exit 101），额外失败为 loopback HTTP mock bind `Operation not permitted`，日志 `ab1369095e5e56ef821e4383c244af5f21dd92f799cae94f4d37dcd45fb7ea01`。允许环回 bind 的同命令完整重跑为 **151 passed / 4 failed / 2 ignored**（exit 101），日志 `e4bbbacb94c6e6d1d47ae2dcc58a445e0cebf99b8b2a99459e53aae9cbfaa26f`。相对 QA1 的 125/22/2，18 个路径拒绝均消失，另有 8 个新增用例通过。临时夹具先做 canonical 路径检查，再在系统临时根独占建立唯一合成目录。全量通过项包含首次与嵌套目录、并发抢先创建、不同/空目录与 symlink 替换、初始化故障和真实子进程退出，以及独立临时根规则。
- 独立 HEAD 副本同环境完整 Cargo 运行 **109/13/2**（exit 101），日志 `4c0cad6f3df2eda5c42ce07081343e23f65f17c37a83463ea218f98f3b9cb0f0`，与批准稿引用的基线相同。该副本只补正式树三个因 Git ignore 缺失的 ASCII 合成 `flat.db`、`nested.db`、`invalid.db` 文本夹具。返工 4 个失败均包含于此基线，名称同 QA1。三个旧维护失败为 `profile_contract_business_admission_failed`，YAML 旧迁入用例为 `profile_locked`。未降级历史断言。v4 维护事务中断、写失败、日志失败和活动/草稿策略四个定向替代覆盖仍通过。
- `git diff --check`、`cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check`、`env pnpm_config_verify_deps_before_run=error pnpm build --outDir "$qa/daa-formal-dist"`、`node --test tests/facts-delivery.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs` 均 exit 0，Node 15/15。构建保有 Rollup 注释/大 chunk 警告，日志 `81dcbb47b61b89f3f8bf61d24e1743149a2f2f8de5e7418cc5df05fdfb7b27ce`。六份 README/指南和两份 bundle 文档的 120 个相对文件目标均存在，锚点未自动校验。rustup 只装有 `aarch64-apple-darwin`。

### 独立 provider、故障代理与验收边界

从 HEAD 归档加 §2 的五个增量组装 615 项，另核对 §2 三个公开合同，8/8 摘要匹配。副本清单 SHA-256 `a660d8be7ac4045ca8c2f3cfd27eb84fd396a74fde046c5afb9f5778d2a85cff`。从该副本以 `env -i`、本轮 TMPDIR 和 uv cache、`uv run --offline --frozen --no-sync --project <正式 backend>` 使用锁定 Python 3.13.3 / uv 0.7.8。预检初次缺私有 `API_V1_PREFIX`，在连接数据库前退出。补齐私有配置后验证唯一 env 和实际 import 位于副本，MySQL 8.4.6 / UUID `bde93faf-de74-11f1-b801-8e5990eb95e7`、`daa010_r5_qa`、仅 schema 权限的 `daa010_qa_app@%`、0 表和 `+08:00` / 28800 秒。 `alembic heads` 与带 `ACQ_RETIREMENT_*`、`ACQ_FACTS_*`、`TASK_CUTOVER_*` 目标防护的 `alembic upgrade 5f7a9c1e3b25` 均 exit 0。迁移日志 `dea1eddfdfbbad2634cd6010577da70440cf75a23c1a203bad99942a9c337bcb`。迁后同 UUID/schema、revision `5f7a9c1e3b25`、56 表，两个事实表均空。

以 `python -m uvicorn main:app --host 127.0.0.1 --port 38118 --workers 1` 运行私有 FastAPI PID 51013。独立临时 Python HTTP 客户端和私有 38218 代理的 24 个 HTTP 检查 exit 0，全部核对实际状态、`Content-Type`、完整错误/回执信封及相应 SQL。合成结果 SHA-256 `35941117b94f091c69b1a41348ca52ed6efae02322dc82eb2d6bd5b4dc95126f`。以下分项保留是否经过原生 DAA 的实际边界。

| 验收 | QA2 结果 |
| --- | --- |
| AC01 | 通过 provider 复验。合成 `daa` 免 Bearer，错实例、PLC、DB、代次各返回 403。五个 GET 可读，另外一个可写但无 `readScopes` 的 PLC 的 latest/history 均 403。 |
| AC02 | 部分证实。真实 HTTP 通过 400 / 512 点及 `bad/null/bad_timeout`，524288 B 通过，524289 B 返回 413，513 点返回 422。QA 全量中的 `versioned_configuration_import_activation_and_two_db_collection` 通过真实保存、导入 readiness、激活、采样事务、重开与两个独立回执的合成 transport 场景。独立 HTTP 与 DAA SQLite 用例使用不同夹具。实际原生 S7 与 DAA 已落盘超 1 B 样本零 POST 本轮未跑。 |
| AC03 | 部分证实。38218 代理转发合成样本 `qa2-alias` 并丢弃 provider 的 `committed/created`，已读 SQL 为 1 行。客户端以同正文 SHA `5bc034821f840b85b758053bbef052cbffb17a2d91973f933e2779ffd89d3beb` 直接重发至 38118，`committed/duplicate`，仍 1 行。定向实际 worker/SQLite 测试证实本地确认失败后重试以及重开停态。代理实验客户端为 QA 脚本。真实 DAA 的断网采集、发送后退出和原生补传本轮未跑。 |
| AC04 | 部分证实。provider 的 403/409/410/413/415/422 有完整错误信封，无额外历史。代理主动返回 503 时 SQL 为 0 行。Rust 全量的定向错误回执、阻断来源、暂停和旧尝试结算通过。未将这些故障同时注入实际原生 DAA/provider 组合。 |
| AC05 | provider DB91 seq3 先到、seq2 后到，history 可读两条原时点，400 个 latest 值仍为 seq3。DB92 的 512 个最新点、DB93 的 3 点、DB94 的 1 点与 SQL 对齐。合成 worker 有界公平和重开时钟用例通过，墙钟跳变由组件注入。 |
| AC06 | **失败，见 F-R5-QA2-001。** 原首次路径、停态、配置与历史保护、容量停采恢复和 v4 故障测试覆盖如上。合成 runtime2/3 可按已证条件保留原路径本地功能，runtime4 原生旧产品二进制打开未实测。当前候选没有交付或验证 runtime2/3 原位开启 v2 上报。 |
| AC07 | 本轮原生 DAA 停态有证；DS PID 50691 持有独立 profile、Vite 50640 在 15196，`ds_get_runtime_snapshot` 返回 ok。出现 QA2 阻断后未配置设备或邀请 Owner 继续操作。35118 未启动监听。环回 S7 至 DAA、原生补传、存储/筛选/帮助/中英/窄窗/列宽完整交互矩阵待下一候选。 |
| AC08 | Windows 10/11 x64 构建、独占锁、普通重开、发送期间退出、热 journal 和页面仍按 §7 由 Owner 后续实测。 |
| AC09 | 部分证实。Node 与 SQLite 检查覆盖 URL/CAS、未发送及已尝试的不同绑定、未核对目标拦截和迟到回执。QA 代理证明合成兼容别名和直接端口连至相同 provider/MySQL，且同正文在丢响应后获得 duplicate。真实 DAA 的原生设置/重开及端口/路径分别切换待下一候选。 |

R06 / AC09 保留 QA1 的 GET 限制。当前旧 `daa_test_facts_endpoint` IPC 固定拒绝 `legacy_delivery_read_only`，DAA 无实际 GET 诊断入口。候选指南给出后端 GET 和独立 `readScopes` 的操作，自定义 POST 路径无法推导读路由，本地详情与可靠回执仍可核。若 Human Owner 要求保留原读按钮，交 PM 澄清 R06/AC09 的条件范围。Vue 使用稳定应用、表及字段键存列宽，实际 WebView 使用 `localStorage`，DAA 未显式按 profile 绑定 WebView 数据目录。QA2 以 15194 隔离 origin，未改变本机列宽，原生跨重启持久化和不同 profile 在同 origin 时的偏好行为仍待验。 [诊断 IPC](../../src-tauri/src/commands/local_delivery.rs#L139) · [指南](../../STAGE_C_GUIDE.zh-CN.md#6-登记来源并开始上报) · [上报表本机存储](../../src/components/console/FactsDeliveryPanel.vue#L120)

### 交接和回收

- 已把 F-R5-QA2-001 的最小复现、影响和历史路径对照交 Development。QA2 供 Human Owner 审阅。Mac 受控链路未完成，Windows 为后续门槛，实际采用、部署及最终验收仍分别由 Human Owner 决定。本轮只触达合成数据及私有资源。
- DAA、DS、provider 分别结束自己会话，`ps` 复核上述五个 PID 均无匹配。15194 / 15196 / 35118 / 38118 / 38218 无监听，`lsof +D` 私有根无打开文件。Provider 日志确认正常关闭；DAA 日志无 `runtime_stopped / clean`，只记录进程退出。代理随 HTTP 验证结束自行关闭。DS 停止证据日志 SHA-256 `cb1adfab159f23628b85dedf9ced669611dc80181bb559fdc350be2e37f5d014`。
- 交协调者回收，复核时尚运行的专属容器为 `44ee8fc27f2acd3286c7aa23bdb7d5750dc6ef2bff51e15bc0b7ee9ec1aaf910`，唯一 127.0.0.1:33318 映射，唯一卷 `daa010-r5-qa-mysql-data` → `/var/lib/mysql`，唯一网络 `cc698ca01220299083616292d8223a81c40877acfe34a78f4d195159cdabbdf5`（`daa010-r5-qa-net`）。三者标签为 `aiis.task=DAA-010-r5-qa`，网络唯一成员为该容器。镜像为本地 `mysql:8.4.6` arm64，ID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`。默认沙箱的 Docker 只读预检被 socket 权限拒绝，已获批准的精确预检和执行成功。QA 私有根 `/private/tmp/daa010-r5-qa-private` 是 UID 501、0700，必要证据见本记录，复核资源归属后可由协调者回收。
- 协调者复核归属后对上述精确容器执行 `docker stop`、`docker rm`，均 exit 0。确认卷无容器使用且网络成员为 `{}` 后，对上述卷执行 `docker volume rm`、对上述网络执行 `docker network rm`，均 exit 0。协调者核对私有根真实路径、UID 501、0700、无挂载及打开文件后，以固定路径且拒绝符号链接的 `rmtree` 回收该根，exit 0。QA 于 `2026-11-12T17:01:40+08:00` 独立使用精确 ID / 名称过滤 `docker ps -a`、`docker volume ls`、`docker network ls`，均无匹配。根路径及符号链接均不存在，33318 / 38118 / 38218 / 35118 / 15194 / 15196 均无监听。复核 exit 0。

## DAA-010 r5 R06 多 PLC 文案独立复核

2026-11-13（Asia/Shanghai），fresh-context Verification（`contract_only`）。**局部通过**，覆盖 R06 双语设置与开始/继续确认，以及 AC07、AC09 的相关前端交互。依据获批 r5 §3–5 和 ARCH-ACQ-004 r2 R2-04 核对逐 PLC 绑定。工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`，r5 原文前 101915 字节摘要 `e63c4909027a097e258ab0e812515ad4f4dcf0ddc2266e765e1802075ad5e27c`，含 r6 待批附录的完整摘要 `39a04890c3cfe9d3737ef959484fcfca92a289d0921d2b379e8b0f396f17d92f`。以下 `shasum -a 256` 结果与[本轮 Development 交接](tasks.md)逐项一致。

| DAA 相对路径 | SHA-256 |
| --- | --- |
| `src/locales/en-US/common.json` | `cb19cf17fbdd55aab33df6d32ab6305f48f37f39c5970f63d0f490efb9fd7a88` |
| `src/locales/zh-CN/common.json` | `dd0092edafe049ee271b4d7a52c921390694e3a139e8ca6a49074df086f1ab46` |
| `tests/facts-delivery.test.mjs` | `86516e7fb13226c0f67ae65f555c5fd3c028848ee6c18001cf12d8deda2cd4ed` |

- `git diff --check` 退出 0。设置模板、composable、IPC facade 和样本账本的摘要与 ARCH-ACQ-004 r2 交接记录一致。逐台编辑并一次保存完整绑定，开始与继续将完整已确认来源和设置版本传给 `daa_set_delivery`。当前 Rust 服务源码校验完整来源集合。该文件摘要与旧 r2 清单有差异，本轮只读核对相关分支，前端局部结论不沿用旧清单的 Rust 运行证据。 [设置模板](../../src/components/console/FactsDeliveryDialog.vue) · [开始及继续](../../src/console/composables/useLocalAcquisitionConsole.ts) · [r2 交接](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/tasks.md)
- Darwin arm64，Node `v22.19.0`，pnpm `11.11.0`。`node --test tests/facts-delivery.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs` 退出 0，17/17。真实弹窗 setup 切换两台 PLC 并共同保存各自绑定，覆盖 DB、重复、无效标识和实例变更。真实 composable 和 facade 经模拟 IPC 复验开始及继续都提交两台 PLC 的来源，确认文字包含完整地址、合同、实例、来源、合格历史待传样本及人工核对提醒。
- `node --input-type=commonjs` 内联核验退出 0。以项目实际 i18n 装配及编译的 Vue 设置模板在内存切换中英文，656 个 `common` 叶键对称。两种语言均渲染“选择要配置的 PLC”及逐台填写说明，确认消息四个参数均完成插值。该轮复跑为源码与合成组件层，正式构建见 Development 原记录。
- 供 Human Owner 审阅。任务总体仍为 `qa_failed`，F-R5-QA2-001 待处理。Mac 原生完整验证、Windows AC08 及实际 dev 采用各按原门槛处理。本轮未启动原生应用或访问后端、MySQL、Docker、设备和现有 `.local/dev`，无临时产物。

## DAA-010 r8 独立验证（QA1，2026-11-16）

**Verdict：`qa_failed`。** F-R8-QA1-001 是本轮交付的配置示例与已保存自动启动行为不一致。路径解析、单次合成 profile 冷重开和文档链接的独立检查结果如下；它们不覆盖或取消该失败。r5 QA2 的 `qa_failed`、F-R5-QA2-001 及其原证据继续保留。当前发现交回 Development；修正并重新交接后须进行新的 fresh-context Verification，再交 Human Owner 决定最终验收。

### 验证输入与范围

- 命名 Verification 在 fresh context、`contract_only` 下，独立阅读根契约、canonical workflow、相关双语 README/PLAN、完整任务 bundle、正式工作树及差异。按本轮表面使用 `project-governance`、`aiis`、`desktop-tauri`、`rust-runtime`、`code-document-indexer`。本角色只追加本 checklist，不修改其他角色文档或实现。
- 目标为正式树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 加未提交内容；HEAD 不能单独标识候选。开始前重算 `spec.md` SHA-256 `dd319580fd81bb119312f495d17bd81d85a78955ece68e26477bbfd792b5d6fb`、`tasks.md` `2c69388944f8cb22d090aa0c2e9f75b1610b2fa786b2588a3e59be176915a0a3`、原 `checklist.md` `1fc97cc24b64ecdbfb015f150e16e75a74b64018968027eb4a486eadebc58d31`，均与精确 handoff 一致。独立重算 handoff 表中 10 个实现/文档文件摘要均匹配；三个 Rust 文件联合 `git diff` SHA-256 `d8901b940f18cbab29437018366c48b029509c8bbb4a9253365c65d9fba58c8e` 一致。按交接划定 r8 归属，不把共享脏树全部差异归给本任务。
- r8 §6 记录 Human Owner 的精确范围批准及对 §2 限定风险的接受，不是最终验收。r8 §3 将 `.env.example` 列为本轮触达的说明面，§2 要求保留 DAA-015 已保存采集/上报启动开关行为，§5 要求核对数据与使用说明。

### F-R8-QA1-001 配置示例错误描述重开后的自动启动

[`.env.example` 第 17–18 行](../../.env.example#L17)无条件写明启动或重开保持断开、停止，并要求在工作台显式连接和采集。但 [DAA README](../../README.md#start) 正确说明采集和上报默认停止、工作台可为下次启动分别开启；[普通恢复入口](../../src-tauri/src/services/local_recovery.rs)在非验证模式调用 `startup_automation()`，[实现](../../src-tauri/src/services/local_startup.rs)根据已保存的 `auto_collect` 和 `auto_report` 分别请求自动采集与自动上报，仍受各自现有准入条件约束。[DAA-015 QA4](../DAA-015-startup-automation-and-workbench/checklist.md#独立验证-qa42026-11-14asiashanghai)记录了四种开关组合的独立合成验证。

该错误语句已存在于当前 HEAD 的示例文件，并非本轮新增代码回归；但它仍在本轮修改并交付的路径示例中，与 r8 明确保留既有启动开关的使用语义冲突。使用者按示例复用已有 profile 时，不能据此假定重开后一定保持停态。本轮未启动现有 profile 或验证任何实际设备动作。需要 Development 在获批 `.env.example` 范围内使说明与实际默认值及已保存开关一致，并保持中英文说明一致，再提交新精确候选复验。

### r8 验收逐项与独立命令

环境为 macOS 15.7.7 / Darwin 24.6.0 arm64，rustc/cargo 1.89.0，已安装 target 仅 `aarch64-apple-darwin`。QA 使用 `mktemp -d /private/tmp/daa010-r8-qa.XXXXXXXX` 新建的 `/private/tmp/daa010-r8-qa.VJzhCOl6`，UID 501、mode 0700；从正式树已有的忽略构建缓存以 `cp -cR` 克隆到该根的 `target`，不复用 Development 临时根。Cargo 使用 `env -i`、锁定离线依赖、独立 `CARGO_TARGET_DIR` 和 `TMPDIR=<QA根>/daa-008-r2-a-tests`；没有读取实际 `.env` 或 profile。

| 核对 | 独立结果 |
| --- | --- |
| 配置来源、基准与优先级 | DAA 目录执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib --no-default-features --features rust-snap7-driver startup_env_ -- --test-threads=1`，退出 0，5/5；其中两个不同 cwd 的子进程各 1/1。覆盖默认文件缺失、默认/显式选中文件中的相对值、进程相对覆盖、空白回退和默认值、绝对值、重复键、无效文件、上级路径、占位符及所测 symlink。检查 `local_bootstrap::load` 将解析结果传给普通启动；不存在的新目录在解析阶段未被拒绝。测试构建有既有 `empty_for_test` 未使用告警。 |
| 既有合成 profile 身份 | 同一环境下使用完整过滤器 `infrastructure::local_store::profile_contract_tests::profile_contract_relative_and_absolute_configuration_reopen_same_profile -- --exact --test-threads=1`，退出 0，1/1。这是本轮唯一的合成 profile/SQLite 检查：对同一预建目录，相对值创建并保存合成配置/样本，再用绝对值冷重开，核对配置正文、非空样本正文及摘要、实例和封存凭据；测试自行删除其合成 profile 与环境文件。不证明真实 profile、排队/回执全矩阵或设备链路。 |
| 构建、格式、链接 | `cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` 退出 0；为调用实际 `prepare_runtime` 的隔离探针另运行相同锁定/feature 条件的 `cargo build ... --lib`，退出 0，均未启动应用。`rustfmt --edition 2021 --check --config skip_children=true` 对三份交付 Rust 文件退出 0；交付路径限定的 `git diff --check` 退出 0。独立 Python 扫描 AW/DAA 的六份双语 Markdown：70 个本地链接、14 个 Markdown 标题或显式锚点，0 问题，退出 0；未请求外部网页。 |
| 文档及上层范围 | 双语 README/手册和示例说明相对路径基准、优先级、Mac 新目录预建、既有目录保全及 Windows 待验；AW 双语 diff 仅更正 DAA 路径表述，SMA 表述未改。但示例另有 F-R8-QA1-001 的错误启动陈述，因此本项失败。 |
| 符号链接边界 | 实际源码路径与独立探针结果见下；所测相对链接最终在原存储准入中拒绝且未创建文件。Windows 专用不完整路径断言由 `cfg(windows)` 包围，本机未编译或执行该分支。 |

上述 Cargo 命令的共同环境为 `env -i PATH="$PATH" CARGO_HOME=/Users/jason/.cargo RUSTUP_HOME=/Users/jason/.rustup TMPDIR=/private/tmp/daa010-r8-qa.VJzhCOl6/daa-008-r2-a-tests CARGO_TARGET_DIR=/private/tmp/daa010-r8-qa.VJzhCOl6/target TZ=Asia/Shanghai`。配置测试日志 SHA-256 `df7a9a74a43d47fac81cb78006575ae96274ce137d58e933e41ce14b491edfe2`，profile 测试日志 `07e592a0bb4582494bdf37737e2ebd45dd7d57d0d22e55aaad1006ed06688c8f`，Cargo check 日志 `484a670d162eca7bafb7770726a1372c85bc78dc55343342175b718cf5ccdf5b`。shell 初始化曾输出 `/bin/ps: Operation not permitted`；上述命令及实际测试均正常结束，不能据此声称进程枚举能力完整。

**末尾 symlink 的分层验证。** QA 自有空目录中建立指向同一自有空目标的 `alias`。用从正式候选重新构建的库链接一个只调用公开 `prepare_runtime(Vec::new())` 的临时探针：文件值 `alias` 与 `alias/./child` 分别返回 `profile_symlink:DAA_PROFILE_DIR`，文件值 `alias/`、`alias/.` 及进程值 `alias/.` 却返回 `Ok(())`。这是配置层 `Path::ancestors()` 对末尾斜杠/点的观察，不应写成配置层已拒绝。对同一合成路径，独立调用实际 Cargo 测试二进制的 `profile_contract_child`（`DAA_008_R2_CHILD=init`，`DAA_008_R2_PROFILE=<QA合成alias>/.`，`--exact ...::profile_contract_child --nocapture`），实际 `Stores::open` 返回 `time_profile_unsupported:profile_symlink`；子测试因 `unwrap` 该预期拒绝而退出 101，外层断言错误及目标目录仍为空后退出 0。子日志 SHA-256 `bc6424725e927ffe0f6ffb6f93ddb337340cd338aba5c068a4c391ffc549cd57`。源码路径为 `LocalEngine::open → Stores::open → admit → canonical`，拒绝先于 profile 锁、SQLite 和日志创建；本次探针分两个进程调用配置入口和存储工厂，没有启动 GUI。旧 HEAD 的绝对 `alias/.` 在配置层同样返回 `Ok`；无本轮业务写入绕过的证据，也不将此配置层缺口称作已修复。

### 既有证据的候选关联与限制

- 独立阅读 DAA-014 人工手测记录：6 条待发送及 1 条未知恢复后共 7 条确认，随后累计 31 条包含这 7 条；仅原未知和一条新样本按 `sampleId` 抽查回执及 Web 值/质量。它是 Owner 手测转交，不是本轮 QA 或 31 条逐条对账。将两份现行手册仅在内存逆向本轮配置段后，重算英文 `7cc06f6f74d57b6afd07aac034b0b3cded75e7daecbf3ef307f4780501528ba9`、中文 `bbf783fd15f213af53d49ce4f71546ca99fcac905e41d03240f3ccccdd2f183e`，与 DAA-014 记录一致；这只建立文档关联。
- DAA-010 r5 的 17 条合成样本是较早候选的 Owner 操作及 Development 对账；QA2 是独立但不同候选的记录。r5 QA1 rework 的 `profile_contract.rs` SHA 为 `5a1d344176e235d9bafb83294473e423dd971fcafa0c607fd12b72fccaacf8a0`，当前为 `4d3f56e16ba0deb522b7842d817d0afdc7a600b20d8a59d939479fd163c520d5`，不能宣称旧路径/故障矩阵对当前候选逐字节复验。DAA-012 的预建 profile 初始化与冷重开按其原候选和实际范围引用；本轮的合成重开结果单独见上。
- 独立重算 DAA-015 QA4 归档清单 SHA-256 `52001c772e90de2c010807b3cd81e564a6ef221e69b5def9200fc9f194650648`，34 项中当前 28 项相同、6 项不同、0 缺失；不同项为四份 DAA README/手册、`StartupSettings.vue`、`app.css`。清单不含本轮配置解析文件，故不能将 QA4 整体称为 r8 独立验证。DAA-015 的 Owner 自动采集/上报反馈仍是原记录中的自述，不补写目标、样本或回执。
- F-R5-QA2-001 的首次自动创建目录竞态**未修复**。本轮 Mac 受控前提是使用者先在自己控制且可写的父目录预建空 profile，确认实际所选目录，并在首次启动期间不移动或替换父目录及 profile；这只绕开原发现的特定创建窗口，不证明其他替换安全，也不是程序强制检查。已有兼容 profile 保留原路径和数据；本次没有检查真实目录。
- 未重跑既有 dev 或 17 条隔离联调，也未运行全套测试、DAA/DS GUI、后端、MySQL、Docker 或设备；未操作现有 `.local/dev`、真实配置、历史及数据库。Windows 10/11 原生路径/锁/重开/补传/热 journal 和界面仍按 [记录单](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md)后续实测；安装版 `.env`、实际采用、现场/生产和完整阶段 C 不在本轮结论内。

### 交接与资源

将 F-R8-QA1-001 的原文位置、已保存开关证据和所需说明修正交 Development；重新 handoff 后由新的 fresh-context Verification 审核精确候选。本 `qa_failed` 供 Human Owner 知悉，不能进入最终验收或推定 r5 已通过。

QA 专属根 `/private/tmp/daa010-r8-qa.VJzhCOl6` 由本次 Verification 创建，含克隆 Cargo 构建缓存、定向测试日志、仅用合成路径的配置/链接探针及空目标；无本轮常驻服务，`lsof -nP +D` 对该根退出 1 且无匹配输出。上述命令、断言和必要摘要已持久记录，本结论不以临时文件为唯一证据。按协调者指示本角色不回收该根；由协调者在后续返工/验收及证据依赖结束后核对归属和占用并决定回收。未创建分支或 worktree。

追加后核对：本角色首次用标题分割历史前缀时多计了新增的分隔换行，比较脚本退出 1；改为按 `git show HEAD:<checklist>` 的原始长度比较，退出 0，原 39467 字节完整保留，SHA-256 仍为 `1fc97cc24b64ecdbfb015f150e16e75a74b64018968027eb4a486eadebc58d31`。交付 10 文件及 `spec.md` / `tasks.md` 摘要与 handoff 仍一致；本 checklist 的 `git diff --check` 退出 0。

## DAA-010 r8 独立验证（QA2，2026-11-16）

**Verdict：`qa_passed`，限 r8 获批的路径兼容与 Mac 受控范围。** F-R8-QA1-001 的示例启动说明已关闭；上方 r8 QA1 的 `qa_failed` 与 r5 QA2 的 `qa_failed` 和 F-R5-QA2-001 均原样保留。此结论交 Human Owner 决定 r8 最终验收，不代表 r5 各项全部通过或底层竞态已修复。

### 验证输入与候选关联

- 新一轮 fresh-context Verification 按 `contract_only` 独立读取项目契约、canonical workflow、相关 README/PLAN、任务 bundle、r8 批准与原始及返工交接、QA1 和 r5 QA2 记录，复核正式树及差异。按本轮表面使用 `project-governance`、`aiis`、`rust-runtime`、`desktop-tauri`、`code-document-indexer`，只追加本 checklist。环境为 macOS 15.7.7（24G720）/ Darwin 24.6.0 arm64，Rust/Cargo 1.89.0；本机唯一已安装 Rust target 为 `aarch64-apple-darwin`。
- `git rev-parse HEAD` 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`，候选仍为正式树加未提交改动，HEAD 单独不能固定候选。追加前 `shasum -a 256` 重算：获批 `spec.md` `dd319580fd81bb119312f495d17bd81d85a78955ece68e26477bbfd792b5d6fb`；返工后 `tasks.md` `292a34a9d54f902e57339365fca66d9036c05d49acd3e88e3714ce041c558f5c`；含 QA1 的原 `checklist.md` `5e3e3fc397e1b6285a29c6fbbe4b24a72b0f8aea803a1c1bbba237fc36ea9ae3`；返工后 `.env.example` `fb7f4403ae37726ee2638e6ae4dae2f9dfc971fefd3ff711a4277f1940202b1c`，均与交接相符。
- 使用 `python3 -B -` 在内存中将示例新六行替换回 QA1 原两行，恢复后的完整文件 SHA-256 `2bd8ea520360242969b267938ac8a6229fd976df12a5bcaa6c01d9491ca0a223`，与 QA1 交付清单一致；仅一个实际 `DAA_PROFILE_DIR=` 赋值。相同方式按新返工标题切分 `tasks.md`，追加前 154832 字节 SHA-256 `2c69388944f8cb22d090aa0c2e9f75b1610b2fa786b2588a3e59be176915a0a3`，与 QA1 所用的 tasks 一致。两项断言均退出 0。
- 重算原交付清单其余九个文件，均与 [r8 原交接](tasks.md#daa-010-r8-development-self-check-与-developer_handoff2026-11-16)及 QA1 相同：AW 双语 README、DAA 双语 README/手册和三个 Rust 文件。三个 Rust 文件相对 HEAD 的联合 `git diff | shasum -a 256` 为 `d8901b940f18cbab29437018366c48b029509c8bbb4a9253365c65d9fba58c8e`。AW 双语差异仅更新 DAA 路径说明，SMA 规则未改。当前 `profile_contract.rs` 为 `4d3f56e16ba0deb522b7842d817d0afdc7a600b20d8a59d939479fd163c520d5`。
- 重算 [DAA-015 QA4 归档清单](../DAA-015-startup-automation-and-workbench/evidence/daa015-qa4-manifest.json) SHA-256 `52001c772e90de2c010807b3cd81e564a6ef221e69b5def9200fc9f194650648`，逐项比较当前树为 28 相同、6 不同、0 缺失，与 QA1 观察一致；相同项包含 `local_recovery.rs`、`local_startup.rs`、`local_runtime.rs`、存储 `configuration.rs`、`local_supervisor.rs`、`sample_upload.rs` 和受影响 Rust 测试。六项为四份 DAA 文档、`StartupSettings.vue` 和 `app.css`，它们与 DAA-015 QA4 的差异不能据此被称为 QA1 后均未变化。QA1 没有保存整个共享工作树逐文件摘要，因此本轮只证明上述可比候选及证据的关联，不宣称树上所有其他文件在 QA1 后逐字节未变。共享工作树的其他并行改动未归属本任务。

### 验收对照

| 项目 | 独立核对结果 |
| --- | --- |
| F-R8-QA1-001、默认及保存行为 | 通过。新中英文示例均写明采集和上报启动开关默认关闭、自动采集关闭时手动连接采集、启动分别遵循已保存开关和各自既有准入条件；不再无条件宣称重开必停。`StartupSettings::default()` 两项为 `false`，无记录时存储返回该默认；普通 `local_recovery::open` 在非 validation 模式调用 `startup_automation`，后者分别按 `auto_collect` 与 `auto_report` 请求原动作并记录失败。示例与 [英文手册](../../USER_GUIDE.md)及[中文手册](../../USER_GUIDE.zh-CN.md)的分别启用、下次启动及保存不影响当前运行的说明一致，不保证实际动作一定成功。DAA-015 QA4 的四组合是原候选合成验证；其 Owner 自动启动反馈仍按原记录的自述范围使用。 |
| 路径配置及同一 profile | 采用上方逐文件摘要和日志关联，复用 r8 QA1 在独立根以 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib --no-default-features --features rust-snap7-driver startup_env_ -- --test-threads=1` 的 5/5，以及完整过滤器 `infrastructure::local_store::profile_contract_tests::profile_contract_relative_and_absolute_configuration_reopen_same_profile -- --exact --test-threads=1` 的 1/1；两者原记录 exit 0。本轮只读重算原日志 SHA 分别为 `df7a9a74a43d47fac81cb78006575ae96274ce137d58e933e41ce14b491edfe2`、`07e592a0bb4582494bdf37737e2ebd45dd7d57d0d22e55aaad1006ed06688c8f`，并读取测试结果。该一次合成重开核对原配置、非空样本及摘要、实例和 sealed 凭据，不扩大到真实 profile、完整回执矩阵或设备链路。 |
| 格式、编译和文档 | r8 QA1 的定向 `rustfmt`、交付路径 `git diff --check`、六份双语 Markdown 的 70 个本地链接和 14 个锚点检查均 exit 0；`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` 及探针所需 `cargo build ... --lib` 均 exit 0。只读重算 check 日志 SHA `484a670d162eca7bafb7770726a1372c85bc78dc55343342175b718cf5ccdf5b` 并确认其完成输出。本轮对 r8 交付路径、tasks 和 checklist 运行 `git diff --check`，退出 0；未因只改示例注释而重复 QA1 的测试、编译或链接扫描。 |
| 符号链接 | 保留 QA1 的实际分层观察：`alias/`、`alias/.` 在所测配置入口可返回成功，不能声称配置层已拒绝；对同一合成链接，实际存储工厂的探针在锁、SQLite、日志创建前拒绝。只读核对原 store 子测试日志 SHA `bc6424725e927ffe0f6ffb6f93ddb337340cd338aba5c068a4c391ffc549cd57` 和 `time_profile_unsupported:profile_symlink`；子测试因 `unwrap` 预期拒绝退出 101，外层断言按 QA1 记录 exit 0。源码正常入口为 `LocalEngine::open → Stores::open → admit → canonical`，`Stores::open` 先 `admit`，再连接双库及初始化日志；QA1 配置入口和存储工厂是两个进程的探针，没有启动完整 GUI 链路。此为所测路径的写前拒绝，不是配置层缺口或所有竞态已修复。 |
| Mac 前提与历史证据 | Human Owner 在 r8 §6 已明确接受 §2 的限定风险和受控使用条件，尚未作 r8 最终验收。F-R5-QA2-001 的首次自动创建目录替换窗口仍未修复；新 Mac profile 须先在自己控制、可写的父目录预建并确认空根，首次启动期间不移动或替换父目录及 profile。这只绕开该特定窗口，不是程序强制检查，也不证明其他替换安全；已有兼容 profile 原路径与数据保持原状。DAA-014 的 7 和累计 31 条及其中两条抽查、r5 的 17 条和 DAA-012 的旧候选证据继续按 QA1 所列来源与限制引用，不冒充本轮独立联调。 |

### 交接、限制与资源

将本 r8 QA2 结论交 Human Owner 做最终验收；没有新的 Development failure。本轮未重跑 dev/17 条联调或全套测试，未启动 DAA/DS GUI、后端、MySQL、Docker 或设备，未操作现有 `.local/dev`、真实配置、历史和数据库。Windows 10/11 原生路径、锁、重开、补传、热 journal 和界面仍待按[记录单](../../WINDOWS_NATIVE_VALIDATION.zh-CN.md)实测；安装版 `.env`、实际环境采用、现场/生产及完整阶段 C 均不由本次 QA 证明。

本 QA2 为只读复核和本 checklist 追加，未新建临时根、进程、分支或 worktree。QA1 专属 `/private/tmp/daa010-r8-qa.VJzhCOl6` 和 Development 专属 `/private/tmp/daa010-r8-dev.hYP5gNUZ` 在本次只读检查时仍存在；前者包含原测试日志与探针，必要结果和摘要已记入 checklist，均不以临时文件为唯一证据。Verification 不回收，交协调者在确认任务归属、占用及证据依赖后处理。

追加审计：以 QA2 标题前的原始字节复算，QA1 前缀 51422 字节的 SHA-256 仍为 `5e3e3fc397e1b6285a29c6fbbe4b24a72b0f8aea803a1c1bbba237fc36ea9ae3`；QA2 新增的 5 个本地链接文件目标均存在。`git diff --check` 对本 checklist 和交付路径退出 0。复核 `spec.md`、`tasks.md`、`.env.example` 及 HEAD 仍与本节候选摘要一致。

## DAA-010 r8 Human Owner 最终验收（Mac 受控范围）

2026-11-16（Asia/Shanghai），Human Owner 在当前会话对 DAA-010 r8 作出以下最终验收决定：

> 好的，验收 DAA-010 r8 的 Mac 受控范围，Windows 原生验证后续安排。

**状态：`owner_accepted`，仅限 DAA-010 r8 的 Mac 受控范围。** 上方 r8 QA2 的 `qa_passed`、r8 QA1 和 r5 QA2 的 `qa_failed` 及其原始证据均保持不变。F-R5-QA2-001 的首次自动创建目录替换竞态仍未修复；首次使用新的 Mac profile 须在使用者控制且可写的父目录预建并确认空 profile 根，首次启动期间不移动或替换父目录及 profile。该前提只绕开所记录的特定自动创建窗口，并非程序强制检查，也不证明其他替换安全；已有兼容 profile 原样沿用。

Windows 原生验证后续安排；实际环境采用、安装版 `.env`、现场/生产和完整阶段 C 不由本次验收涵盖。本记录仅转录 Human Owner 的真实决定，未运行测试或操作现有 dev 环境。
