Task ID: DAA-017
Revision: r5
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 通过 -> Human Owner 决定最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-017 r5 独立验证 QA1

## 验证对象与范围

- 本次按 fresh-context Verification 角色复核 `aiis-ics-arch::DAA-017 r5`；不继承 Development 对话推理。`spec.md` 状态 `owner_approved`，SHA-256 `daa1735f7d8f70c27bae67fd979e5012906592391aaa476db152a1e6763f44e1`；`tasks.md` 状态 `developer_handoff`，SHA-256 `93fbc34ff32c2f3715dbaac508b85eb1c3247a0025f8b1713f5c509c5789abcd`。
- 交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。按 `tasks.md` 首轮 28 项文件清单应用最终七项替换，独立计算 28/28 全部匹配。`src-tauri/Cargo.lock` SHA-256 `3689918ee18e16f63357ceb92811bbcf6019486b38ea747853638073e26b18cc`；`pnpm-lock.yaml` SHA-256 `0417e47e58e19974d9bde4f3866164e88ffe1c1c22eb2ade356e48f12464d44c`，均匹配交接；schema、manifest 与锁文件的所列 Git status 无变更。现有 dirty 工作树包含其他任务改动，整文件哈希不意味着全部 Git 差异归属 DAA-017。
- 本次读取根契约、生命周期 workflow、verification 角色和任务 bundle，按治理、AIIS 工业边界、PLC 映射、Rust runtime、Tauri、Vue、i18n 与源码索引规范审阅；只修改本 checklist。角色配置与本任务的 fresh-context 调用是可观察事实，不宣称平台 ACL、强制路由或 Human Owner 验收。
- 环境：macOS 15.7.7（24G720），Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。工作目录均为 `automation-world/data-acquisition-agent`。Rust 使用仓库锁、`--offline`，独立临时 target 从交接所列 Development target 作 APFS 写时复制，测试在该副本及本次独有 TMPDIR 中运行；`DAA_ENV_FILE`、`DAA_PROFILE_DIR`、`DAA006_NATIVE_SEED_ROOT` 从环境移除，`DAA_PLC_READ_ALLOWED=false`。未启动真实设备或真实网络上报，未写用户 `.local/dev`。

## QA1 失败 F-DAA017-QA1-001：非法 UUID variant 被接受

**违反 DA01**：r5 §2 要求拒绝非法 UUID v4，DA01 要求非法 ID 拒绝且不写。`src-tauri/src/domain/plc_catalog.rs:139` 的 `canonical_id` 只检查 `get_version_num() == 4` 和规范小写文本；所用 uuid 1.23.3 的 `get_version_num()` 只取版本半字节，不验证 RFC 变体位。该函数用于 origin、export、DB 和点 ID。

**独立复现**：从交接的实际 DS 文件生成仅供本次测试的合成副本，将 DB21 停用点 ID 从 `ca21fc06-a489-4948-83fc-08b8e798168e` 改为 `ca21fc06-a489-4948-03fc-08b8e798168e`。后者的版本位仍为 4，但 Python 标识 variant 为 `reserved for NCS compatibility`、version 为 `None`，不是 RFC UUID v4。合成文件 SHA-256 `a3fc54a6767ce1db98e436f0f932bf5212852aa63c7e3c5a92a278ffb8be302f`；原 DS 文件未修改。生成方式（路径只在本次测试中有效）：

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json, uuid
src = Path('/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json')
dst = Path('/private/tmp/daa017-qa.vcrODk/invalid-uuid-variant.json')
x = json.loads(src.read_bytes())
x['dbs'][0]['points'][3]['id'] = 'ca21fc06-a489-4948-03fc-08b8e798168e'
b = json.dumps(x, ensure_ascii=False, separators=(',', ':')).encode()
dst.write_bytes(b)
u = uuid.UUID(x['dbs'][0]['points'][3]['id'])
print(u.variant, u.version, hashlib.sha256(b).hexdigest())
PY
```

在上述隔离环境以该副本调用候选现有测试（此测试对 `parse()` 成功执行 `unwrap` 并核对 SHA 和 BOOL/INT/REAL）：

```sh
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT \
  DAA_PLC_READ_ALLOWED=false \
  CARGO_TARGET_DIR=/private/tmp/daa017-qa.vcrODk/target \
  TMPDIR=/private/tmp/daa017-qa.vcrODk/daa-008-r2-a-fixtures \
  DAA017_DS_EXPORT=/private/tmp/daa017-qa.vcrODk/invalid-uuid-variant.json \
  DAA017_DS_EXPORT_SHA256=a3fc54a6767ce1db98e436f0f932bf5212852aa63c7e3c5a92a278ffb8be302f \
  cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib \
  catalog_import_explicit_ds_export -- --exact \
  domain::plc_catalog::tests::catalog_import_explicit_ds_export --test-threads=1
```

实际 exit 0、`1 passed`，说明解析器接受了该非法点 ID；这个测试进程的“passed”恰恰是本负例预期拒绝的失败证据。该复现未对副本执行导入确认，因此不声称已实际写入用户数据。请 Development 修复 UUID v4 验证，并覆盖非 RFC variant 的正负例及受影响身份字段，记录新的精确交付候选和自检后重新 handoff。不得仅增加测试而保留当前接受行为。

为避免复现依赖临时 DS 文件，本角色还以仓库固定的 `tests/fixtures/plc-catalog-v1.json` 作源，把第一个点 ID 从 `55555555-5555-4555-8555-555555555555` 改为 `55555555-5555-4555-0555-555555555555`，同样通过上述精确测试（exit 0、1 passed；NCS variant，`version=None`）。复现时可将上面的 `src` 改为 `Path('tests/fixtures/plc-catalog-v1.json')`、赋值改为 `x['dbs'][0]['points'][0]['id'] = '55555555-5555-4555-0555-555555555555'`，输出文件及 `DAA017_DS_EXPORT` 使用 `/private/tmp/daa017-qa.vcrODk/invalid-uuid-from-fixture.json`，并将 `DAA017_DS_EXPORT_SHA256` 改为 `685b15a9fd766ee3628f8eb080f3a7a48df5bdf9a538348f9c15a777426d4ecd`；其余生成和测试步骤相同。此结果仍是非法输入被接受的失败证据。

## 已执行的独立检查

| 检查 | 结果及限度 |
| --- | --- |
| 独立读取实际 DS 导出并 SHA-256 校验 | exit 0；SHA `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`，revision `3d50439c-fb2b-41bd-9d95-56c67cd98672`，PLC `31d327ba-2b97-4f5e-8949-6956ac3a5648`，DB21 有 BOOL、INT、REAL 和额外停用 BOOL 四点。仅证明读到该文件，非独立原生采集观察。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1`，环境如上，`DAA017_DS_EXPORT` / SHA 指向实际 DS 文件 | exit 0，8 passed；覆盖真实文件解析、合成多 DB、部分格式及布局负例、目录绑定、事务失败、身份冲突、激活和目录点编辑。F-DAA017-QA1-001 不在原有负例之中。 |
| 同一环境 `cargo test ... --lib daa017_catalog_sample -- --test-threads=1` | exit 0，1 passed；合成 profile 中使用内存 S7 数据生成本地样本，假 v2 transport 捕获正文，断言中英文 sentinel 不出现及三点 name/value；未发送真实 POST，不是现场读取或对原生联测样本的独立重放。 |
| 同一环境依次 `cargo test ... --lib source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_`，均追加 `-- --test-threads=1` | 测试摘要分别为 4、4、7、3 passed、0 failed；`native_owned_legacy_seed` 未设置种子时提前返回，不作原生覆盖声明；DAA-018 原有独立状态不因本次测试改变。 |
| 同一隔离 Cargo target `cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0。检查正式 feature/binary 编译，不启动应用或设备。 |
| `node --test tests/plc-catalog-import.test.mjs tests/point-editing.test.mjs` | exit 0，23 passed；有 Node MockTimers experimental 提示，UI 为测试替身，并非本次独立原生 GUI 操作。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa017-qa.vcrODk/ui --emptyOutDir` | 均 exit 0；Vite 有第三方 PURE 注释和大于 500 kB chunk 警告。 |
| 28 文件 Rust 候选中的 Rust 文件 `rustfmt --check --edition 2021 --config skip_children=true`；对应已跟踪文件 `git diff --check` | 均 exit 0；新增未跟踪文件已按交接清单整文件哈希核对。 |
| 两份 PLC locale 递归键对照；两份 USER_GUIDE、两份 local_store README、CODE_INDEX 的本地 Markdown 文件链接 | locale 221/221 键相同；5 文件缺失目标 0。未以机械检查替代实际双语视觉验证。 |

## 验收项目状态

| 项目 | QA1 记录 |
| --- | --- |
| DA01 | **失败**，见 F-DAA017-QA1-001；即使其余现有正负例通过也不能判此项通过。 |
| DA02–DA03 | 合成解析测试覆盖多 DB、BOOL/INT/REAL/STRING、停用点、类型/地址及部分非法目标；最终实际文件含三类运行点及停用点，独立读取文件通过。非 RFC variant 的停用点未被拒绝，整体仍需修复后复验。 |
| DA04–DA07 | 源码和合成测试核对同源多 DB、归档原文、绑定、冲突、取消、篡改、过期、失败事务及目录保护；Node 测试覆盖选中文件变更、目标变更和未知结果。具体原生替换场景属协调者观察，并非本角色亲见。 |
| DA08–DA09 | 合成测试验证默认停用、保存及显式激活、原 PLC 比较；锁文件/DDL 面检查如上。协调者在 `tasks.md` 记录实际 `.local/dev` 操作前后对照、正常 revision 与历史保留；本角色未操作或独立重演该 profile。 |
| DA10 | 合成真实本地存储样本经内存 S7、假 v2 transport 的上述测试通过；其为隔离合成证据，非实际联测样本外发证明。未发真实网络请求。 |
| DA11、DA15 | `tasks.md` 记录协调者使用正式候选在各自 `.local/dev` 的 DS 原生导出、DAA 导入、仅 loopback 读取 15 次（15/15 good）、保留停用点及 local-only/无 upload 行的观察和清理；这不是本 Verification 亲自观察，不将其冒称独立原生复验。最终文件哈希、revision 和点身份由本角色只读核对。 |
| DA12 | 交付树候选哈希、Node、Rust、正式 feature 编译和前端构建见上；实际原生导入为协调者观察。Windows、虚拟机和其他未测平台不作为本任务前置。 |
| DA13–DA14 | 合成导入和点编辑检查涵盖双语/单侧空、独立旧名称及描述；`tasks.md` 另记协调者的语言切换与编辑观察，不冒称独立操作。 |
| DA16 | 已审阅双语 USER_GUIDE 和本地链接；清理与未验证平台限制按指南及本次交接核对。 |
| DA17 | 合成测试覆盖原样地址、双语/comment/分组/启用编辑，以及更名、清空/修改地址、批量生成、伪造 token/摘要和过期拒绝；旧命名回归测试如上。重新交接后须针对修复候选做独立复验。 |

## 交接、资源与边界

QA1 verdict：**`qa_failed`**。先将 F-DAA017-QA1-001 返回 Development；修复后的精确候选须再次进行 fresh-context Verification，之后才可交 Human Owner 决定最终验收。此记录没有授予最终验收，也不改变 DS-004、DAA-018 各自的 QA 状态；真实设备、真实 POST、Windows、旧版普通原生二进制、部署和生产采用均不在本次证据范围。

本次独有临时根 `/private/tmp/daa017-qa.vcrODk` 包含隔离 Cargo target、副本 profile、合成无效 UUID 文件与前端构建，故障的复现方法和哈希已写在本文件；本角色完成检查后可由协调者确认无后续依赖并回收，仅限该目录。Development 自有 `/private/tmp/daa017-r4-dev.O7G5Nm` 和协调者保留的 `/private/tmp/ds003-final-json-RfE0TL/` 不由本角色删除：二者归属及未来修复/复验依赖由对应所有者确认。协调者记录的 15+18 条测试样本及相关 revision 已被历史引用，按其记录保留，不能删除整个 profile 或既有数据。

Human Owner 最终验收：待定。

# DAA-017 r5 独立验证 QA2（2026-11-17）

## 对象、身份和限制

- QA1 失败全文及原 verdict 保留在上文。QA1 的 NCS UUID 错误接受已由 Development 返修并重新交接；本轮为 fresh-context Verification，不继承 Development 对话推理。批准的 `spec.md` SHA-256 `daa1735f7d8f70c27bae67fd979e5012906592391aaa476db152a1e6763f44e1`，当前 `tasks.md` SHA-256 `8a61da64d3fbc67f97337ca73ab797dbb6d75c8e09de2e7af4f33c50af95a81c`；写本节前的 QA1 `checklist.md` SHA-256 `bac8d30eb829b9a5f6273e29dded4200bb41ada95cd7d2a17c77551aeeaa01e9`。
- 交付工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。独立读取 `tasks.md` 首轮 28 文件清单，依次应用七项最终替换和 QA1 后两项替换，实际整文件 SHA 28/28 匹配。返修两文件分别为 `src-tauri/src/domain/plc_catalog.rs` = `8d8032a216ef75984a8016aa3d66346752753d69897f4eeb99eaeabc42923ae8`，`src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` = `9f00e9adf708d219832e85280eaf8313c11b10097b48022b86a6ca0e14360f7f`；其余 26 项与 QA1 对象相同。`src-tauri/Cargo.lock` = `3689918ee18e16f63357ceb92811bbcf6019486b38ea747853638073e26b18cc`，`pnpm-lock.yaml` = `0417e47e58e19974d9bde4f3866164e88ffe1c1c22eb2ade356e48f12464d44c`，均与交接匹配；Cargo/package manifest、两锁文件和 `schema.rs` 的 Git status 为空。工作树同时有大量既有和并行任务变动，整文件哈希不意味着所有差异都属于 DAA-017。
- 读取根及触达范围契约、canonical workflow、verification TOML、完整任务 bundle，按 `aiis`、`project-governance`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 对相应表面做独立复核。此次只更新本 checklist；角色合同为 `contract_only`，不宣称平台 ACL 或强制路由。
- 环境：macOS 15.7.7 (24G720)、Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0；除特别注明，工作目录为交付树 `automation-world/data-acquisition-agent`。测试不使用既有 `.local/dev`、真实设备或真实 POST；Cargo 固定 `--locked --offline`，target 是从 Development target 复制到本轮自有目录的 APFS 写时复制副本，测试 SQLite 与构建产物均在本轮自有目录。终端有 `/bin/ps: Operation not permitted` 的 shellenv 提示；下列退出码与测试结果按实际返回记录。
- 原 DS 文件 `/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json` 只读核对 SHA-256 `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`，producer `device_simulator`，saved revision `3d50439c-fb2b-41bd-9d95-56c67cd98672`，DB21 含 BOOL、INT、REAL 与额外停用 BOOL。此读取不代表本角色原生连接或采样。

## F-DAA017-QA1-001 的独立前后复现

按上文 QA1 方法从同一 DS 文件生成停用点 ID 为 `ca21fc06-a489-4948-03fc-08b8e798168e` 的合成副本；SHA-256 再次为 `a3fc54a6767ce1db98e436f0f932bf5212852aa63c7e3c5a92a278ffb8be302f`，Python `uuid` 判断为 NCS variant、version `None`。在本轮临时源码副本中恢复 QA1 的两个文件，SHA 分别精确为 `7c0229859322f140489243d6c602334889a359524687f52dfe10e753323c0a44` 与 `2564d30757d88975fa4f4a9337bf3824ec3647d0ab915950bee058ba24cb34f0`；其余内容取当时当前工作树。对同一非法 JSON 调用下面的既有精确解析测试：

```sh
# E 指下面测试环境；旧候选运行目录为本轮 qa1-snapshot 的 DAA 根
E DAA017_DS_EXPORT=/private/tmp/daa017-qa2.ruhfzx/invalid-uuid-variant.json \
  DAA017_DS_EXPORT_SHA256=a3fc54a6767ce1db98e436f0f932bf5212852aa63c7e3c5a92a278ffb8be302f \
  cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib \
  catalog_import_explicit_ds_export -- --exact \
  domain::plc_catalog::tests::catalog_import_explicit_ds_export --test-threads=1
```

旧文件隔离副本 exit 0 / 1 passed：测试的 `parse().unwrap()` 接受了非法 ID，独立复现 QA1 的缺陷。返修后的正式工作树上同一命令 exit 101 / 0 passed，`unwrap()` 报 `catalog_point_invalid`：这是负例预期拒绝，不是有效输入测试失败。旧文件对照的快照不声称等于此前原生二进制。`diff -u` 显示两次交接的 `plc_catalog.rs` 实现变化为增加 `uuid::Variant::RFC4122` 校验，并新增变体测试；另一个文件新增隔离预览无写测试。当前 `canonical_id` 也保留 version 4 与规范小写要求。

本角色另以该实际 DS JSON 的副本做 60 个解析组合：依次替换 origin profile/PLC、export profile/revision、DB ID、停用点 ID 的 UUID 变体首半字节。对每份 bytes 计算 SHA，运行上述当前候选的精确解析测试：`0,7,c,d,e,f` 的 36 项分别返回对应 `catalog_metadata_invalid`、`catalog_db_invalid` 或 `catalog_point_invalid`；`8,9,a,b` 的 24 项均 exit 0，合计 60/60 与预期一致。此项只读原文件并在本轮临时目录生成副本。目录预览的实际无部分写由下列隔离持久化测试验证。

## 本轮独立检查

下表中的 `E` 为：

```sh
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT \
  DAA_PLC_READ_ALLOWED=false \
  CARGO_TARGET_DIR=/private/tmp/daa017-qa2.ruhfzx/target \
  TMPDIR=/private/tmp/daa017-qa2.ruhfzx/daa-008-r2-a-fixtures
```

| 检查 | 实际结果和证据边界 |
| --- | --- |
| `E DAA017_DS_EXPORT=<上列真实 DS 文件> DAA017_DS_EXPORT_SHA256=0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1` | exit 0，10 passed；包括真实 DS 文件原字节解析、合成多 DB 和布局、非法 UUID 各字段、目录绑定、事务与编辑。`catalog_import_non_rfc_uuid_rejected_without_writes` 在隔离 profile 比较草稿、来源归档、其他受保护数据和 ETag。 |
| 在本轮隔离源码副本中恢复为当前交付源码，将原始 DS JSON 复制为该副本的 `tests/fixtures/plc-catalog-v1.json`，`E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import_existing_name_preview_accepts_user_fields_and_rejects_overrides -- --test-threads=1` | exit 0，1 passed，日志 `catalog_imported` 的 PLC 为 `31d327ba-2b97-4f5e-8949-6956ac3a5648`；真实导出 bytes 进入隔离本地存储，既有测试检查目录点编辑、限制及归档不变。`diff -qr --exclude target` 对快照 `src-tauri` 与交付树、快照 `shared/tia-import-core` 与交付树均 exit 0；测试 fixture 有意换成实际 DS 文件。这是隔离源码副本和内存/本地存储测试，不是正式候选原生 GUI 或 loopback。 |
| `E cargo test ... --lib <filter> -- --test-threads=1`，filter 依次 `daa017_catalog_sample`、`source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_`；另从环境移除 `DAA017_DS_EXPORT`、`DAA017_DS_EXPORT_SHA256` | exit 均为 0，分别 1、4、4、7、3 passed；`native_owned_legacy_seed` 在未提供种子时提前返回，不作为原生覆盖。采集样本和 v2 正文使用合成数据及假 transport，未发实际网络请求。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；只编译检查，不运行设备。 |
| `node --test tests/plc-catalog-import.test.mjs tests/point-editing.test.mjs` | exit 0，23 passed；UI/IPC 使用测试替身，非原生操作。Node 有 MockTimers experimental 提示。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa017-qa2.ruhfzx/ui --emptyOutDir` | 均 exit 0；Vite 有第三方 PURE 注释和大于 500 kB chunk 警告。 |
| `rustfmt --check --edition 2021 --config skip_children=true src-tauri/src/domain/plc_catalog.rs src-tauri/src/infrastructure/local_store/catalog_import_tests.rs`；`git diff --check -- automation-world/data-acquisition-agent` | 均 exit 0。两返修文件未跟踪，另逐行检查无尾随空白且有末尾换行。Rust 有既有 `empty_for_test` dead-code warning。 |
| 递归比较两份 PLC locale；检查两份 USER_GUIDE、两份 local_store README 和 CODE_INDEX 的本地 Markdown 目标 | 两侧各 221 键，差集 0；五文件不存在的本地链接 0。此机械检查不替代本次原生双语观察。 |

## r5 验收对照与 blocker

| 验收项 | QA2 当前证据 |
| --- | --- |
| DA01 | UUID QA1 问题经同一负例前后复现及 60 组合检查，当前行为符合要求；格式/编码及其他负例由目录解析测试覆盖。 |
| DA02–DA03 | 受控多 DB、BOOL/INT/REAL/STRING、停用点、布局和地址负例有 Rust 证据；真实 DS 文件只读解析与隔离本地存储导入通过。 |
| DA04–DA07 | 目录绑定、原文归档、身份冲突、事务、取消、篡改及目录保护有隔离测试；文件变化和未知提交状态有 Node 替身测试。 |
| DA08–DA09 | 合成 profile 验证默认停用、原 PLC 保留及显式激活；schema/锁文件状态如上。QA1 前的 `.local/dev` 互通及清理是协调者旧候选观察，不能扩大为返修后二进制的原生证据。 |
| DA10 | `daa017_catalog_sample` 以隔离本地样本、内存 S7 和假 v2 transport 检查两个显示名 sentinel 不进入正文；未外发，旧 v1/v2 各路径维持其各自任务证据边界。 |
| DA11、DA15 | **返修后候选原生闭环未完成**。协调者报告已用正式入口构建并启动修复后 DS 与 DAA，binary SHA 分别为 `44aa51f3049e31c5907662eb6abb97a277419a09f4cff235ec11036f98b8ea9f` 和 `3b4c538cb9663ca4c43b691a193ca0c89285d51b9cb986755885ce6073b68a85`，对应原生测试窗口和各自 dev 锁曾核对；这些为协调者报告，非本角色亲见。系统锁屏导致本次实际新 DS 文件导出、DAA 原生导入、显式分组/激活、loopback BOOL/INT/REAL 和停用点核对未执行。协调者随后报告为释放环境已停止本次窗口 PID 9000/9018 和 Vite，`lsof` 确认两套 `.local/dev` 锁与 15191/15194/31974/31975 端口均无持有；本次启动未新增 PLC、连接或上报。上文 15 次原生样本属于修复前候选，不能替代。 |
| DA12 | 当前正式工作树的 Rust/Node、类型检查、前端构建及 driver feature 检查已通过；返修后二进制实际原生导入仍受 DA11 blocker 影响。Windows、虚拟机等不是本任务的通过前置。 |
| DA13–DA14 | 合成目录及编辑测试覆盖双语/单侧空/旧名称和 description/comment；本角色未执行新候选原生语言切换。 |
| DA16 | 两份指南包含核对 profile、DS 原文件、导入、分组/激活、采样检查和仅清理自有对象步骤，本地链接检查通过。 |
| DA17 | 合成目录及真实 DS 文件隔离导入后，现有命名预览测试覆盖可编辑字段、目录受保护字段、伪造 token/摘要及过期；旧命名回归通过。 |

**QA2 verdict：`qa_blocked`。** 当前没有发现新的实现 failure；F-DAA017-QA1-001 的返修行为已在本轮独立验证，但 DA11 / DA12 的返修后候选原生互通尚缺必要证据。解除条件：用户解锁后，协调者按已批准 r5 核对目标与既有对象，完成修复后候选从实际 DS 导出到 DAA `.local/dev` 新建、显式分组/保存/激活、仅自有 loopback 采样及停用点/数据保护与安全清理；记录双方候选、revision、文件 SHA、采样结果、历史保留和清理，然后交本 Verification 接续复核。若无法安全执行，保留 blocker；不得以旧二进制、fixture 或本角色未亲见的观察冒称新候选已通过。

Human Owner 最终验收仍待决定；本次不改变 DS-004 / DAA-018 各自的 QA 状态，也不证明 Windows、旧版普通二进制、真实设备、真实外发、部署或生产采用。

本轮自有 `/private/tmp/daa017-qa2.ruhfzx` 包含隔离 target、源码副本、合成 UUID 文件、测试 profile、回归输出及前端构建；关键摘要和结论已写入本文件。Verification 不执行资源回收；待 Human Owner 验收后，由协调者核对本轮归属、无进程和无后续验证依赖后仅回收此目录。Development 的 `/private/tmp/daa017-r4-dev.O7G5Nm` 与协调者保留的实际 DS 文件目录均不由本角色删除；`.local/dev` 和历史数据不属于本角色临时资源。

# DAA-017 r5 QA2 接续核验（2026-11-17）

## 原生闭环及独立只读核对

用户解锁后，协调者按 r5 已授权范围执行原生互通；本 Verification 未亲自操作原生界面或写 `.local/dev`。接续前 `checklist.md` SHA-256 为 `06adc8e3bb26cfcd0b2929e92b70c2cb5aecce3d0199007609657dd117ec30f4`。上文 QA1 `qa_failed`、锁屏时 QA2 `qa_blocked` 及其原因继续作为历史保留；本节是同一返修候选的接续结果。

- 再核对 DAA r5 交接清单 28/28、DS-003 r5 最后交接清单 29/29 整文件哈希均匹配；DAA `spec.md`、`tasks.md` 的 SHA 与上文一致。独立读取双方正式工作树 debug 二进制及协调者自有测试 `.app` 内二进制，DS 两份均为 SHA-256 `44aa51f3049e31c5907662eb6abb97a277419a09f4cff235ec11036f98b8ea9f`，DAA 两份均为 `3b4c538cb9663ca4c43b691a193ca0c89285d51b9cb986755885ce6073b68a85`。实际构建、启动和进程/profile 核对由协调者执行与报告。
- 协调者报告在各自已核对的 `.local/dev`，使用 DS 保存 revision `b4fd38fa-0d2a-48e6-b83b-fb16d2da35c8`，从实例 `e1dc3ad5-305f-4367-af1b-92333a582730` 的原生界面实际导出，再在 DAA 原生界面选择并确认新建。预览显示四点、双语和描述；新点均默认停用未分组。同文件再次导入时界面提示“PLC 端点重复”、确认禁用。协调者切换英文核对 `Running`、`Count`、`Actual temperature`、`Disabled label` 后切回中文；这些界面现象为协调者观察，并非本角色亲见。
- 实际导出文件 SHA-256 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`。本角色重新计算文件 SHA，使用上节同一隔离 `E` 环境，将该路径和 SHA 传给正式工作树的 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import_explicit_ds_export -- --exact domain::plc_catalog::tests::catalog_import_explicit_ds_export --test-threads=1`，exit 0、1 passed；这项独立检查为真实文件解析，不冒称本人操作 GUI。
- 通过 SQLite URI `mode=ro&immutable=1` 只读 DS `.local/dev` 保存版本，验证原始 payload 的 SHA-256 等于其保存值及导出声明值 `20c8882a2f5e1e902ae32896043e773370f3e24972a863cc731a279c6ed3345d`。导出实例、端点 `127.0.0.1:31976`、DB 及四点 ID、类型、地址、启用、双语和描述与该版本逐字段比较无差异。
- 协调者报告只给三个源启用点分组并启用测试 PLC，保存并显式激活后只连接上述自有 loopback DS，采集 11 轮并暂停、断开、停止测试实例；未启动实际或自动上报，原待发送 5 和已确认 69 未变。本角色只读 DAA 配置与运行库：采样 revision `9acbff9e-0539-4b91-b397-a6d7cf1a1368` 的 payload SHA 有效，目录来源正文与上述实际导出文件逐字节一致；四点 ID/类型/地址/comment/中英文名称匹配，三个点启用并分组，`STRING[10]` 点停用且未分组。
- 本角色只读汇总到该 PLC 11 条 sample 和 11 条 collection cycle 均 `good`；11 条均有 reporting cycle 行且均为三项身份 NULL 的 local-only，关联 `sample_uploads=0`、`sample_upload_attempts=0`，11 条 sample payload 的 SHA 均有效。末条样本为 BOOL DB21 `0.0=false`、INT `2=0`、REAL `4=0.0`，各点质量 `good`，地址 `origin=catalog`，REAL comment 为 `本机合成温度`；停用字符串点未进入样本。样本事实和原生 GUI 的执行者分别如上，不将两者混同。
- 清理由协调者报告通过应用移除测试 PLC、保存并激活，DS 测试实例也经界面移除；本角色随后只读比对 DAA 草稿及 active JSON，二者均逐对象等于联测前 active revision `423e612e-291c-45d0-b171-557126ee4ad5`，测试 PLC 不在草稿或 active 中。DS 草稿等于其 v1 保存内容、原 `DEV-PLC-A` 仍选择 v1。DAA 测试来源原文、11 条样本和相关 revision 作为历史保留；未直接删除历史或整个 profile。
- 对 DA09 的物理 schema，本次互通前协调者未单独采集 sqlite_master 指纹；本角色发现既有 `profile-contract.json` 创建于 2026-11-13、文件 mtime 为当日，且其 payload SHA 有效。按实现的 `daa-ddl-sha256/v1` 算法只读重算当前 sqlite_schema：config 的 `sha256:64cc8187689bf3e04eb4b914811fe75e77a8d5dd6c0c895cfe12ed4814e1a806` 与 runtime 的 `sha256:93000b2fe7aa28beae236d4aca9651a260033a5b61db3b33bfa604524cc53b91` 均与该预存 contract 指纹一致；两数据库文件 dev/ino 也与 contract 匹配，schema_migrations 分别仍为 2026-11-13 的 v2/v4。证据证明当前结构等于此前封存基准，不声称排除了过程中短暂变化后再恢复，也没有对全部既有历史做联测前后逐条字节快照。
- 协调者如实说明此前为避免自动化重绑而对已核对的测试进程发送 SIGTERM，故不能将当时退出称为正常关闭。其后协调者用同一正式构建和已核对的 `.local/dev` 受控重启，确认 0 连接、采集/上报停止及 5/69 队列计数后，以原生 Cmd-Q 正常退出。本角色只读核对当前 `runtime_metadata.clean_exit=1`；`runtime_events` id 148 保留 `2026-11-17T20:54:43.890+08:00 uncertain_gap / restart`，id 150 为 `2026-11-17T20:58:14.967+08:00 runtime_stopped / clean`，11 条测试样本仍在。`lsof` 检查两应用锁及 TCP 15191、15194、31976 无输出，exit 1；不把历史间隙当作已消除或推断其造成数据损失。

## 验收与交接

DA01 的 QA1 非法 UUID variant 已按上节前后复现并关闭；DA02–DA08、DA10、DA13–DA14、DA16–DA17 的解析、原子性、编辑、双语、样本与文档检查见上节及本节。DA09 的实际配置恢复及封存 schema 指纹核对见上；DA11、DA12、DA15 的锁屏 blocker 已由本节返修后候选原生操作报告及独立文件/版本/样本核对解除。先前 macOS 文件底层替换的原生观察仍对应 QA1 前候选；本返修后前端整文件哈希未变，当前候选对应的文件变化检查另有上节 Node 替身证据，不将旧原生二进制冒充本次复测。

**QA2 最终 verdict：`qa_passed`。** 移交 Human Owner 决定最终验收；本结论只覆盖本任务获批的本机受控 DS/DAA 范围，不代表 DS-003、DS-004 或 DAA-018 的独立 QA/Owner 状态改变，也不代表真实设备、真实外发、Windows、旧普通二进制、部署或生产采用已验证。

## 临时资源与历史保留

关键文件 SHA、版本、样本摘要及核对结果已持久化在本 checklist；本 Verification 对 `/private/tmp/daa017-qa2.ruhfzx`、Development 的 `/private/tmp/daa017-r4-dev.O7G5Nm`、协调者前轮 `/private/tmp/ds003-json-x7cWRU` 和 `/private/tmp/ds003-final-json-RfE0TL`、本轮 `/private/tmp/ds003-qa2-json-dCWNwR`，以及本轮 `.app` 目录 `/private/tmp/ds003-native-we7ab4or`、`/private/tmp/daa017-native-5d7gjmxv` 均无进一步 DAA QA 核验依赖。本角色不执行回收；协调者应按用户清理授权，先确认 DS-003 QA 也不再读取、核对各目录归属和无进程/其他后续依赖，再仅回收符合条件的自有临时资源。DS Development `/private/tmp/ds003-dev.Zc2maS`、DS QA `/private/tmp/ds003-qa2-Ggidgy` 的依赖与回收由对应所有者确认。不得删除或回滚 `.local/dev`、DS 已保存历史及 DAA 测试样本、来源归档、revision 或已有数据。
