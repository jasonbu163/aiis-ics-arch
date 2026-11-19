Task ID: DAA-019
Revision: r2
Status: qa_blocked
Owner Role: Verification
Allowed Writers: Verification
Handoff: QA2 验证结果交 Human Owner；协调者转交 PM 处理证据缺口，解除后再进行独立验证。Human Owner 最终验收未发生。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-019 r2 独立验证

## 精确结论

`qa_failed`。存在一个已证实的交付文档缺漏：根 `AGENTS.md` 第 5 节要求真实结构变化时同步维护 `CODE_INDEX.md`；本任务新增五个导出源码/测试文件，但 QA1 核查时 DAA `CODE_INDEX.md` 声明仅索引 catalog-import，未收录新增的导出 service、command、原生存储测试、Vue 对话框和 Node 测试。`spec.md` 第 4 节将 `CODE_INDEX.md` 列入 Development 白名单；协调者确认本次无 Human Owner 明确豁免。此项返 Development 在批准范围内修复，Verification 不修改实现、索引、spec 或 tasks。

另有独立证据阻塞：D19-05 对用户 profile 的旧 context、样本及投递关联的全部前后保持不能以现有基线逐项证明；父 r7 §4.1 B 指定的 L2 自动选中与返回 ID 没有直接记录，L3 的补核和 L2 的再导出不能记成同一次操作。英文原生界面已由协调者补核，结果见下。上述证据不替代索引修复。未发现需在本轮记录为产品实现失败的其他具体反例；这不代表所有风险均已排除。

## 任务、工作树和角色

- 本轮由 Development handoff 后的新 Verification 上下文执行；只写本 checklist，未继承 Development 对话推理。已读取根 `AGENTS.md`、根及 Automation World / DAA 双语 README/PLAN、最近的 local_store 双语 README、canonical workflow、本任务完整 spec/tasks、父 ARCH r7 活动合同及对应实现/diff/可用测试输出。按范围使用 `project-governance`、`aiis`、`backend-arch`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 与 `code-document-indexer`；这些是合同控制，不声称平台 ACL 或强制路由。
- Human Owner 精确批准 `aiis-ics-arch::DAA-019 r2`、`aiis-ics-arch::ARCH-PLC-001 r7`、`device-simulator::DS-005 r2` 及衔接；本次不是最终验收。核得 DAA spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，Development tasks SHA-256 `7baafd2f8a5f6bd65cd59f7d7225e175172ef08938e630c273909d7d8922b952`，父 spec SHA-256 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。
- 正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，候选是未提交工作树而非 commit。Development 的 34 项最终清单 SHA-256 `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`；两次 `shasum -a 256 -c` 对正式 DAA 树均 34/34 相符。清单内容可由 tasks 的 34 项原表和其后两组明确替换重建。DAA 内其他 PLAN/catalog 改动、DS 工作树及其他已有差异不归本角色候选；未发现 34 项文件超出本任务 allowlist。
- 新文件均有现有风格的中文头部。索引缺项具体为 `src-tauri/src/services/catalog_export.rs`、`src-tauri/src/commands/catalog_export.rs`、`src-tauri/src/infrastructure/local_store/catalog_export_tests.rs`、`src/app/plc/components/CatalogExportDialog.vue`、`tests/plc-catalog-export.test.mjs`。本角色未更新该索引。
- QA1 报告缺项并写入 checklist 初稿后，协调者报告 Development 已返工；最终文档审计时观察到该索引已变更，当前 SHA 为 `9a1c7e94713f36d024849cee926da5b01194c7e2363933a3e32e3ea81f72a03a`，tasks 当前 SHA 为 `950032ea2f3b01212722702e1a4f11c708ad00fb1a6e8e39c05843f62172184d`。QA1 检查时索引与 HEAD 一致，其 SHA 为 `b3921c1b35b7fbaac9a04265ca4355cf2836d6da2837a5c98cf7fce95e034bf4`。协调者随后补做英文观察并由本角色追加记录；QA1 保留原候选 verdict，不把后续修改称为本轮通过，返工必须交新的 fresh-context Verification。

## 验收检查

| 项目 | 独立结果与边界 |
| --- | --- |
| D19-01 | 证据：页面源码的两个入口、一个导入对话框挂载、Node 状态测试和中英文原生界面观察已有证据；PLC locale 双语各 264 个叶键且差集 0，动作字面量正确。英文补核覆盖入口、导入对话框与导出预览，未实际导入或写文件。 |
| D19-02 | 已核实际 DAA catalog 来源 F1/F3 及既有普通 DB/UDT 来源 C 文件的 producer、保存状态、DB 层 `source_enabled` 缺省、点启用、BOOL/INT/REAL 等；C 是已有 `DEV-PLC-A`，不是合成 PLC。服务测试覆盖空侧双语、独立 description、停用点和版本选择；用户 profile 保护的全部历史比较仍受 D19-05 所列限制。 |
| D19-03 | 针对性 15 个 `catalog_import` 测试通过，含双 producer、身份/格式、冲突、篡改、存储回滚等；实际 seed 和 DS 重导文件另作只读复核。无 `DAA017_DS_EXPORT` 时外部文件测试会提前返回，不把该返回冒称原生文件测试。DB/UDT 定向回归重跑通过。 |
| D19-04 | 服务测试验证显式选择、重映射、本机 PLC/DB/点/逻辑来源分离、持久映射、重开和再导出；Node 替身覆盖按实际返回 ID 选择与清空 DB、未知结果不盲猜。L2 真正提交并再导出 F3；另一次 L3 提交后未手工选择即显示唯一同名 PLC，保存草稿只读确认其 ID 为 L3、四点停用未分组。但未直接截获任一原生 IPC 返回，L2 未观察自动选中，L3 未再导出。父 r7 明确要求核对 L2 返回/选中并对该实例再导出；现存证据不能倒记为同一实例全部观察。 |
| D19-05 | **阻塞**。r7 A 的自有合成 profile 服务操作独立重跑通过；实际用户 profile 的前测仅保留 context `8/19/0` 汇总，未保存逐行 context SHA，样本其他列与 `sample_delivery` 也无前测逐行摘要。后测当前 8 条 context 与对应旧 revision payload/SHA 字节一致、19 个来源引用有有效归档；这支持当前自洽，但不证明这些字段在本次操作前后逐行不变。可比较的样本 ID/SHA、uploads、attempts、binding 和原 PLC source 与前基线一致，详情见下。 |
| D19-06 | 现存 Development/协调者记录描述实际 DAA→DS→DAA 原生提交并在当前同源时拒绝；本角色独立复算 seed、F1/F2/F3 及真实 DB/UDT C 文件，排除导出头、连接端点和双方启用字段后，各链外部身份、技术字段、双语与描述一致。重开后 DS 导出与先前文件除时间外相同。L2/L3 的观察边界仍按 D19-04 报告。 |
| D19-07 | 增强测试二进制验证目标预览后出现同名文件时不覆盖、失败逐行报告、无新增半文件，并测 stale；Node 替身测试目录取消和未知状态。原服务测试的多选情形两项均失败，本 QA 在临时源码副本仅改对应测试断言后补测实际服务的一成功一失败，1/1 通过且输出目录仅含有效文件；未把前端替身冒充服务结果。未做操作系统级故障注入或同时启动两个原生 GUI。 |
| D19-08 | 正式候选对应的服务测试中两种语言 sentinel 经过实际 v2 正文构造与 fake transport，9 项 DAA 测试之一通过；没有真实 POST。双语用户手册和 local_store 说明的 32 个相对文件链接均存在；英文界面是协调者的后续实际观察，范围见下，不由静态键对称替代。 |
| D19-09 | 正式树 Node、Vue 类型、Vite 构建及 Rust 文件格式检查通过；Rust 测试采用经散列和源码对照的 Development 增强二进制并另编译 QA 隔离副本。正式入口/native app 与实际往返由协调者执行，本角色只复算文件与 native binary 散列，未自行启动 GUI、连接 PLC 或发送请求。索引缺漏令交付检查失败；英文界面已补核，D19-05 证据限制仍在。 |

## 实际文件和只读数据库复核

- `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 的旧合成 seed SHA-256 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`；F1 `117f0614a63de4fd11e7dce14a50ed445be87137ce9a47e2cd295bd701973261`；F2 `ed5a0ddecb223803c6201727718e723a8f9a96168122f098c3271d1f6bc33570`；F3 `840379d35815349025cbf6f450d47561fbc590969a7cefd2fdab2527b7d6e2cb`。普通 DB/UDT C 的 DAA 文件 `e609252a4212d2c0f4587d89abc34fc8acbbf763a83c777a90eb5242dbd8336e`，DS 文件 `bede8f759b4c06aab2f0cfd23bf70c03eada10c1efed2d3d3d3322e763973dd1`。首次复核脚本把两个 DS 文件名对调，归一化结果不符；按实际文件 SHA/点数纠正文件映射后 seed→F1→F2→F3 及 C DAA→DS 四个比较均为 true。
- F2′ 重开导出 SHA `5c9fa568c7d3d866cee55539d94a317cb53107b3ead548805794cfa073471a92`；普通来源重开导出 SHA `04c194da54cf35902f1fe52d20c1aa68bdab869fdd226db039a60da8c8d62168`；各自与首次 DS 文件除 `exported_at` 外全文一致。DAA/DS 原生 app binary SHA 分别为 `5aaf397a16a61ea7bec116a004c0478c595e6ee444309d75aeb3393609d1b67a` / `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`。这些文件/界面动作是协调者的原生证据，本角色只读复核，不冒称亲自操作 GUI。
- 使用 SQLite URI `mode=ro`、`PRAGMA query_only=ON`，检查时两库未见 WAL/SHM/journal。以 Development/协调者保存的 `baseline-hashes.json`（SHA `2550195d9bd33e04e8396478bd546f08da589920b4e49470e9508d1c427d778d`）为前测比较：草稿 SHA、active/previous、8 条 revision ID/SHA 均相同且当前 revision payload 8/8 自校验；118 条 samples 的 `id,sha256`、69 条 uploads 全行、73 条 attempts 全行、1 条 reporting binding 全行及原 PLC `plc_sources` 全行摘要相同；当前 118 条 sample payload 均与自身 SHA 一致。旧合成 PLC 现仍有 11 条样本；L1/L2/L3 当前均无 `plc_sources`、samples 或 reporting binding。
- 当前 context 8/8 对应旧 revision 原文/SHA，19/19 来源引用的内容 SHA 有效。前测 rollout 原始输出只有 `contexts 8 source_references 19 missing_archive_references 0`；它没有每行 context SHA。上述 8/19/0 前后汇总相符和当前自洽不能升级成逐行前后 hash 相同。样本其他列、`sample_delivery` 同样不能宣称逐行前后哈希相同。
- 协调者误点过未激活合成 L1 的“测试连接”，界面返回“PLC 操作队列繁忙或对象不存在”；不能称从未尝试。记录的读取开关 `DAA_PLC_READ_ALLOWED=false`，tasks 报告未建立连接、未发生真实 POST。本 QA 未自动启动用户 GUI、连接/上报或清理用户数据。
- QA 记录初稿后，协调者报告以相同 DAA binary 和 `.local/dev` 重启完成英文只读补核：PLC configuration 同时显示 `Import PLC JSON` / `Export PLC JSON`；导入对话框显示 `Create PLC: import point catalog`、`Choose JSON file`、`Cancel editing`，确认禁用并正常取消；导出选择 `DEV-PLC-A` 后执行 `Preview selected PLCs`，观察英文目标、来源和确认文案，未选目录或写文件。点位页同一技术点英文为 `switch`、切回中文为 `开关`；之后正常退出，报告 `clean_exit=1`。这是协调者的原生观察，本角色未亲自启动 GUI；未在英文模式下实际提交导入或导出文件，也不把预览称为提交。

## 命令、环境和结果

环境：macOS 15.7.7 / Darwin 24.6.0 arm64，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。项目验证以既有 Cargo/pnpm 工具链和锁文件执行；临时 profile、输出和日志属于 `/private/tmp/daa019-qa.yLy006l9`。

- `node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs tests/point-editing.test.mjs`：正式树 exit 0，27 passed；Node MockTimers 有 experimental 警告。
- `pnpm exec vue-tsc --noEmit` 和 `pnpm exec vite build --outDir /private/tmp/daa019-qa.yLy006l9/ui --emptyOutDir`：正式树均 exit 0；Vite 报第三方 PURE 注释及大 chunk 警告。
- `rustfmt --check --edition 2021 --config skip_children=true <本次 Rust 文件>`、`git diff --check -- automation-world/data-acquisition-agent` 均 exit 0。Cargo.lock 只增 14 个包，包括精确的 dialog 2.7.2，未删除已锁包；既有包元数据变化为 DAA 直接依赖、objc2-foundation libc 与 windows-targets 版本标注。
- 复用 Development r7 A 增强测试 binary `/private/tmp/daa019-r2-dev.c0EWK6bZ/target/debug/deps/aiis_data_acquisition_agent_lib-d57255d4d287a29b`，实际 SHA `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a` 与 tasks 一致；增强的两个测试文件 diff 仅为列明的额外身份、来源与历史断言；其余 Rust 工程、共享 TIA 与测试 fixture 用 `rsync -nrc` 与正式候选对照无差异。清除 DAA 相关环境变量、`DAA_PLC_READ_ALLOWED=false`，指定自有 `TMPDIR`，直接执行 binary `daa019_ --test-threads=1`：exit 0，9 passed；`catalog_import` 15 passed；`exclusive_link_distinguishes_conflict_from_other_write_errors` 1 passed。
- 同一 binary 的 `source_import_tests`、`point_naming_tests`、`point_display_names` 首次分别 exit 101（3/1、3/1、1/6），原因是 QA 首次将 `TMPDIR` 指到不含测试安全守卫要求的 `daa-008-r2-a-` 路径；不是将该轮写为通过。改为自有 `/private/tmp/daa019-qa.yLy006l9/daa-008-r2-a-fixtures` 后重跑分别 exit 0、4/4、4/4、7/7。`native_owned_legacy_seed` 无对应环境变量时提前返回，不作原生 seed 测试证据。
- 多选真实服务补测：在 QA 自有副本中将正式 `catalog_export_tests.rs` 中预置同名文件改为无预置文件，将第一项预期改为 `written` 并验证实际文件可解析；第二项仍预期 `failed`，检查目录恰有一份文件，其余生产源码与正式树 `rsync -nrc` 一致。`CARGO_TARGET_DIR=/private/tmp/daa019-qa.yLy006l9/target CARGO_BUILD_JOBS=4 CARGO_NET_OFFLINE=true TMPDIR=/private/tmp/daa019-qa.yLy006l9 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa019_catalog_export_saved_sources_partial_conflicts_and_cas -- --test-threads=1`：exit 0，1 passed。此测试在隔离副本编译，不是对正式树测试文件的修改；原同名竞争场景由上述增强 binary 覆盖。编译有既有 `empty_for_test` dead-code 警告。

## Blocker、资源与下一 gate

1. **返 Development**：更新批准白名单内的 DAA `CODE_INDEX.md`，准确索引本次实际新增导出文件及职责，保留无关并行改动；完成自检并形成新的精确 handoff。此缺漏是 `qa_failed` 的直接依据，不由 Verification 静默修复。
2. **历史证据 blocker**：若存在可信的操作前逐项基线或等价原始证据，应由协调者提供供 fresh QA 核验。若不存在，不能靠当前自洽或再测倒证这次之前的字节；需由 PM 按实际证据提出可行的验收处理，涉及实质变更须获得 Human Owner 精确批准。
3. **原生证据 blocker**：对父 r7 B 指定的同一往返实例，补充能核对实际返回 ID、自动选中和再次导出的证据，或由 PM 判定所述 L2/L3 分开观察是否需要修订批准。不得把 L3 的选中倒记成 L2。英文新增入口和对话框已由协调者补核，不再作为语言检查 blocker。
4. 暂保留协调者 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt`（真实文件、基线及 app bundles，含从已有配置导出的文件）、Development `/private/tmp/daa019-dev.MKLyerrV`（34 项候选清单和自检材料）、`/private/tmp/daa019-r2-dev.c0EWK6bZ`（r7 A 增强测试源码/二进制与合成 profile），以及 QA `/private/tmp/daa019-qa.yLy006l9`（测试副本、日志和合成 profile）供补证、返工和 fresh QA；关键摘要已固化于 tasks 和本 checklist。验证与 Human Owner 审阅均不再依赖且协调者确认归属及无占用后，按 workflow 由协调者回收各自任务临时资源；不直接清理用户 `.local/dev`、历史或其他任务资源。

Windows/VM、真实 PLC、真实 POST、旧二进制兼容、生产部署和发布不属本轮结论。QA verdict 不是 Human Owner 最终验收，不授权现场采集、上报、部署或发布。


## QA2：索引返工后的独立复核（2026-11-18）

**最新 verdict：`qa_blocked`。** QA1 的索引缺漏已由 Development 修复并经本轮检查关闭；本轮没有发现新的可复现产品实现 failure。现有材料仍不能满足 D19-04 / 父 `ARCH-PLC-001 r7` §4.1 B 对同一次 L2 回导的返回 ID、选中项及再导出的联合核对，也不能证明 D19-05 要求保持的全部旧 context、样本及投递关联在用户 profile 测试前后逐项保持。这些是证据缺口，并非已经发生数据损坏的结论。

### QA1 保全和本轮身份

- 本轮为新的 fresh-context Verification，按交接仅写本 checklist；没有操作 GUI、用户 profile、设备、上报或清理资源。角色为 `contract_only`，不声称平台 ACL 或自动路由。已读取仓库根和 Automation World / DAA 双语 README/PLAN、根 AGENTS、canonical workflow、local-store 双语 README、本任务完整三文件、父 r7 活动合同、相关实现/diff 及可用测试日志；按表面使用 `project-governance`、`aiis`、`backend-arch`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`code-document-indexer`。
- QA1 全部正文与其 `qa_failed` 原结论保留在本节之前；原文件 SHA-256 为 `1be2e395acc2597f5b67f8aceec6de8fff4d934703210ed12820a3ab5f49e026`。为使文件开头反映最新 QA2 状态，只更新最顶部状态和 handoff 两行；QA1 原元数据分别为 `Status: qa_failed` 和 `Handoff: 索引缺漏返 Development；其他证据阻塞保留并由协调者转交 Human Owner / 必要时 PM。修复并重新 developer_handoff 后须重新启动 fresh-context Verification；Human Owner 最终验收未发生。`。还原这两行并移除本 QA2 附录后可逐字节恢复上述 QA1 SHA。
- 验证目标 `aiis-ics-arch::DAA-019 r2`；正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。本次只读复核时 spec SHA `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，tasks SHA `f17f14c8d7a5e1a4e56cb866cf2b4641d921e7a9e768d4d2c6c897d19f7bf3d8`，父 r7 spec SHA `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。

### 验收标准复核

| 项目 | QA2 证据和结论 |
| --- | --- |
| D19-01 | 沿用 QA1 对单个导入弹窗挂载、Node 测试和中英文原生入口的观察；协调者补证实际打开英文导入对话框并取消、导出预览未写文件。QA2 未亲自操作 GUI，也未将英文预览记作提交。 |
| D19-02 | QA2 独立核对真实 catalog B 和普通 DB/UDT C 文件的哈希、producer 与字段；C 是既有配置。B 四份为 1 DB/4 点、C 两份为 1 DB/3 点，各链按外部 ID 排序、仅排除导出头、连接端点和两端启用字段后均一致；DAA 导出 DB 无 `source_enabled`、DS 有该字段，各点均有该字段。完整历史保护仍受 D19-05 阻塞。 |
| D19-03 | 保留 QA1 的 15 项 catalog import、DB/UDT 和其他定向回归结果；其日志可核。无外部文件环境变量而提前返回的旧测试不能当作真实文件验证。QA2 本轮未重跑产品测试。 |
| D19-04 | **阻塞**。源码 `confirm_catalog` 在保存后返回缓存的新本地 PLC ID；前端核验返回 ID 属于结果草稿后选中并清空 DB，QA1 服务/Node 测试覆盖这些分支。L2 已真实提交并导出 F3，但未直接捕获该次原生 IPC 返回或自动选中；L3 的自动选中是另外一次提交，未对 L3 再导出。父 r7 §4.1 B 要求同一 L2 核对返回、选中和再导出，现有分次证据不满足指定链路。 |
| D19-05 | **阻塞**。QA1 对自有合成 profile 的保存、激活、移除、再激活和旧样本/队列/回执隔离已独立复核。对于用户 profile，前测 baseline 对 samples 仅有 `id,sha256`，未包含其他列或 `sample_delivery` 行级摘要；前测 context 仅有 8 条、19 个引用、缺归档 0 的汇总。后测样本 payload SHA、context 与旧 revision 一致及归档有效支持当前自洽，但不证明未覆盖字段测试前后相等。schema 中这些表确有其他独立列。 |
| D19-06 | QA2 独立复算 seed、F1、F2、F3、C 两份和重开两份文件；B/C 比较与 QA1 一致，重开两份分别与原 DS 输出除 `exported_at` 外相同。真实界面提交和同源拒绝为协调者原生记录；本轮未重新执行。完整指定链仍受 D19-04 的同一次原生观察缺口约束。 |
| D19-07 | 保留 QA1 对同名拒绝、取消、stale 和真实服务一成功一失败的验证；没有补称 OS 故障注入或并行原生 GUI。配置/历史完全不变的范围仍受 D19-05 前测证据限制。 |
| D19-08 | 保留 QA1 对实际 v2 构造和 fake transport 的测试、双语指南链接检查；没有真实 POST。 |
| D19-09 | QA1 对 34 项未变产品候选已记录 Rust、Node、类型、构建和原生证据；QA2 只对文档返工做相称静态检查，未冒称重跑。QA1 已证实的索引缺漏本轮关闭，但必要原生观察和保护证据缺口仍在。 |

### 本轮命令、环境与结果

环境：macOS 15.7.7 (24G720)、Darwin 24.6.0 arm64，Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。以下仅为 QA2 执行；先前测试的命令、失败和重跑见 QA1，不把它们改写成本轮新跑。

- 正式 DAA 目录 `shasum -a 256 -c /private/tmp/daa019-index-rework.EEKrDEG1/candidate-sha256.txt`：exit 0，35/35 匹配；清单自身 SHA `40dadba1d4704605bf6cb89c581f3258a46605f7884bdab1ff5a71cece890875`。Python 字节前缀及逐行比较确认原 34 项清单被完整保留，第 35 项仅为 `CODE_INDEX.md`。第一次尝试 `cmp -n` 比较返回 EOF、exit 1；后续 Python 显示旧文件是新文件完整字节前缀，34 行全部相同，不将首次命令记为通过。
- `git diff -- automation-world/data-acquisition-agent/CODE_INDEX.md`：一处范围描述和五项新增，`git diff --check -- automation-world/data-acquisition-agent/CODE_INDEX.md` exit 0；Python 检查 19 个相对链接目标均存在、五个新增目标各一次、尾随空格 0。对照新文件头和职责，QA1 的五项缺漏已关闭。索引 SHA `9a1c7e94713f36d024849cee926da5b01194c7e2363933a3e32e3ea81f72a03a`。
- 使用 Python `hashlib`/`json` 只读复算 B/C 文件及排除项后的合同字段，结果见上表；重开文件比较均为 true。`shasum -a 256` 核对两端 app binary 分别为 `5aaf397a16a61ea7bec116a004c0478c595e6ee444309d75aeb3393609d1b67a` 和 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`。文件与 app 身份匹配不单独证明 GUI 操作；GUI 实测依协调者和 QA1 记录。
- 检查 baseline JSON 键与 `schema.rs`：有 8 个 revision、sample ID/SHA 和 uploads/attempts/binding/source 摘要，无 context / sample_delivery 完整前测摘要。只读核对原前测输出 `/Users/jason/.codex/sessions/2026/11/17/rollout-2026-11-17T23-32-54-01a1ea23-c141-7303-afa2-eb00f14811db.jsonl` 第 53 行，输出确为 `contexts 8 source_references 19 missing_archive_references 0`，不含 context 行级内容；该输出不是逐行一致性证明。
- 只读检查 QA1 / Development 留存日志：`catalog_import` 15 passed；QA1 对 `source_import_tests`、`point_naming_tests`、`point_display_names` 的首次失败及安全 TMPDIR 改正后分别 4、4、7 passed 均存在；Development `daa019_` 9 passed、Node 27 passed。QA1 增强测试 binary SHA `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a` 与交接一致。日志与已有 QA1 结论保留其原执行者和限制。

### Blocker、资源和 handoff

1. 索引缺漏不再返工；原 QA1 `qa_failed` 及发生时证据继续有效。两项未解除的 blocker 为：父 r7 B 同一 L2 的返回/自动选中与再导出联合核对；D19-05 旧 context、samples 其他列及 `sample_delivery` 缺可比前测逐项证据。应由协调者查找可信的操作前原始证据或等价证明；无法恢复时转 PM 评估验收处理，若实质改变已批准验收/风险，须先有新 Revision 和 Human Owner 精确批准。不得把 L3 的观察倒记为 L2，或用新测倒证既往数据。
2. `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt`（B/C 文件、基线、两端 app）、`/private/tmp/daa019-dev.MKLyerrV`（原 34 项清单及开发日志）、`/private/tmp/daa019-r2-dev.c0EWK6bZ`（增强测试二进制及合成证据）、`/private/tmp/daa019-qa.yLy006l9`（QA1 隔离测试、日志）、`/private/tmp/daa019-index-rework.EEKrDEG1`（35 项清单）目前仍供 blocker 核对及 Human Owner 审阅，暂留；其关键结论已记入 tasks / checklist。待证据与后续 QA/Owner 审阅均不再依赖，协调者确认归属、无占用后按 workflow 回收，不处理用户 `.local/dev` 或历史来源。QA2 未创建临时测试目录或执行清理。
3. 本 `qa_blocked` 结果交 Human Owner 知悉并由协调者转交 PM 处理 blocker；证据解除后须由独立 Verification 重新复核。Human Owner 最终验收尚未发生，QA 也不授权真实 PLC、上报、数据库迁移、部署或发布。Windows/VM 与旧二进制兼容性保持未验证。


## QA3：手册、文案及 Owner 新一轮往返的独立复核（2026-11-18）

**本轮最新 verdict：`qa_failed`。** 发现 `F-DAA019-QA3-001`：同一个 `catalog_origin_conflict` 错误码用于不同的冲突，本轮新中英文提示将它一律解释为重复导入时已有同源实例，并给出移除和激活建议；它不能准确描述导出中的目录来源不一致。此产品文案问题交 Development 在已批准范围内处理并重新 handoff。下述既有证据 blocker 仍未解除。本节为只追加记录；文件开头保留 QA2 当时的 `qa_blocked` 元数据，最新结论以本节为准，QA1/QA2 的正文及结论均保留。Human Owner 最终验收未发生。

### 身份、范围及 F-DAA019-QA3-001

- 本轮为新的 fresh-context Verification，角色为 `contract_only`，未继承 Development 对话推理。读取根 AGENTS、根及 Automation World / DAA 的双语 README/PLAN、canonical workflow、最近的 local_store 与 app 双语 README、DAA-019 r2 完整 bundle、ARCH-PLC-001 r7 当前合同、相关源码/diff 和可用测试记录；按实际表面使用 `project-governance`、`aiis`、`backend-arch`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 和 `code-document-indexer`。角色和 diff 控制不代表平台 ACL 或强制路由。本轮仅追加本 checklist，未改 spec、tasks、产品文件或用户数据。
- 精确目标为 `aiis-ics-arch::DAA-019 r2`，正式交付树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，未提交差异。核得本任务 spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`、本次读取 tasks SHA `39d5084f7eb2ce887d8920015587ff0a61b0de52cbf1a5e81a01b8f912ad5a1a`、父 r7 spec SHA `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`，追加前 checklist SHA `327cf8d23af9a6717bde1171f5d13d098c0346400263a4f56b1e60a5511ba1bd`。原 35 项候选清单以 tasks 最新四项替换后，只读复算正式树 35/35 相符，31 项未变、两手册与两 locale 为本轮替换。
- **F-DAA019-QA3-001，静态源码证据：** `src-tauri/src/infrastructure/local_store/configuration.rs:293`–`:310` 对当前草稿、active 和 loaded 配置比较外部 origin，当前同源时返回 `catalog_origin_conflict`；两份 locale 的该键针对这个导入场景区分仅草稿与仍活动/运行的处理，与此分支及手册一致。但 `src-tauri/src/services/catalog_export.rs:114`–`:120` 在同一待导出 PLC 的目录 DB 解析出不同 origin 时也将 **同一代码**作为逐 DB issue，`:369`–`:388` 将 issue 返回预览；`src/app/plc/components/CatalogExportDialog.vue:22` 交给 `local.label`，`src/console/composables/useLocalAcquisitionConsole.ts:293`–`:298` 统一查 `plc.catalog.errors.catalog_origin_conflict`。因此在该来源不一致的导出分支，同一新文案会错误断言是草稿/活动/运行中同源并建议移除、保存或激活，而非说明所选 PLC 的目录来源不一致；也不应把此建议当作该问题的处理依据。`configuration.rs:70`–`:92` 在核查单个 PLC 的多个来源 origin 不一致时亦返回同一代码。这里是源码可核对的条件分支和文案错配；本 QA 没有构造或操作异常用户 profile，也不声称已在原生界面复现该输入或用户数据发生损坏。请 Development 同时覆盖导入当前同源与导出/来源不一致两类语义；不得靠移除用户 PLC 或激活配置消除该验证问题。

### 验收项及证据分层

| 验收项 | 本轮独立结果 |
| --- | --- |
| D19-01、D19-08 手册 | 中英文 2.1–2.6 的入口、手动 PLC、DB/UDT 导入与地址核对、双语点名、分组/启用/停用、JSON 导入导出和激活路径已对照页面、对话框、locale 和状态方法；38 个相对文件/标题锚点链接检查无缺失。没有替代原生逐项操作。 |
| D19-02、D19-03、D19-07 | 手册关于普通 DB 初始 `65536` 不是实长、仅所有点符合并参与非人工确认才更新理论长度、人工确认保护，及含 catalog DB 的 PLC 禁用源文件选择，分别与 `tia_source/reconcile.rs:662`、`plc_layout.rs` 的 preview/confirm 和 `SourceImportPanel.vue:6,56-57` 一致。批量禁用会清组，单点关闭启用不自动清组，对应 `points/index.vue:71-72,108` 和 `useLocalAcquisitionConsole.ts:633-639`。既有产品测试覆盖和其限制仍以 QA1/QA2 为准。 |
| D19-04 | 当前同源导入提示区分仅草稿和仍活动/运行；手册列出移除前核对、编辑/移除/确认/保存及历史新本机身份。本轮 Owner 报告同一新 L2 未手选即显示 PLC、4 点并对它导出；协调者另报告草稿只读检查 L2 本地 ID `7d2ca225-da04-4548-b755-22a174c0fd22`、外部 PLC ID `e1dc3ad5-305f-4367-af1b-92333a582730`、点均停用未分组。本 Verification 未亲历 GUI，且本次没有直接截获该次 IPC 的 `importedLocalPlcId`；服务/Node 的返回与选择测试、Owner 报告和文件检查不能合称为原生返回值已直接观察。父 r7 §4.1 B 同一次返回值证据仍阻塞。 |
| D19-05 | QA1/QA2 的前一轮旧 context、样本其他列和 `sample_delivery` 缺前测逐行基线，仍不能用本轮或后测自洽倒证。下述新完整基线只能比较 Owner **新一轮**开始后的列出行；合成 profile 服务级证据仍按 QA1 原边界。 |
| D19-06 | 本轮三个实际文件只读复算及内容比较见下；界面的拒绝、提交、自动选中与清理分别为 Owner 或协调者回报，不冒充本 QA 操作，且不能替代同一 L2 的原生 IPC 直接捕获。 |
| D19-07、D19-09 | `F-DAA019-QA3-001` 使导出来源不一致时的逐实例错误提示语义失败。QA1 索引缺项已由 QA2 关闭；QA1 Rust/Node/构建证据与 Development 新的类型/构建自检保留原执行者，本轮只新跑下述 Node 测试，未重跑构建或原生 GUI。 |

### 新一轮实际文件和只读对账

- `/private/tmp/plc-json-owner-manual-82_5g47q/daa-export/` 三份文件实际 SHA-256：F1 `4670e3bd-8d51-4734-84d8-303b3d2afca2.json` 为 `63260610d54cb339d2807366abf078a0682ceab034f6adb06a8385237e2cdd68`；F2 `66155773-770a-42ea-9ad9-cf72be59766d.json` 为 `c62949dcfef4c054c7f0147a35e10af9095523e67e416f1ae2445b29f7dc8ec0`；F3 `7d2ca225-da04-4548-b755-22a174c0fd22.json` 为 `e14176aca6f28fb3e188d2904a29c22de89dad4e16fc7f0df132fb1a30f38ca2`。producer 依次 DAA/DS/DAA，版本状态依次 `saved_draft` / `saved_revision` / `saved_draft`；各 1 DB、4 点，点层启用值均 false，DAA DB 层省略 `source_enabled`、DS 为 false。去掉 export 头、连接目标和两端启用字段并按外部 DB/点 ID 排序后，F1=F2=F3，包括 origin、外部 ID、技术字段、双语及描述。文件存在与字段相符不单独证明 GUI/IPC 操作。
- 只读复算 `/private/tmp/plc-json-owner-manual-82_5g47q/full-baseline.json` SHA `dfc8bee1006da84f98a3efe6298a892df435ea146b6f56a34a08d228fe438269`。对 baseline 列出的 DAA config 6 表、DAA runtime 25 表、DS config 6 表逐行 `SELECT *`，SQLite 连接均使用 `mode=ro`、`PRAGMA query_only=ON` 和各自 `BEGIN` 只读事务。每行元组按 `json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)).encode()` 的 SHA-256 组成多重集，与前测 `row_sha256_sorted` 对比：37 表均无缺失前测行。新增行为 DAA `source_documents` +1、`runtime_events` +9；DS `configuration_revisions`、`source_blobs`、`source_versions` 各 +1；其余列出表增量 0。具体包括本轮前后的全部 8 条 context、118 条 samples、118 条 `sample_delivery` 和已有队列/回执行，限此次基线所列字段和表。
- 单独读草稿 payload：DAA 前后 SHA 均 `4b5f702b35a52ee90719a2d32795d96613600441bfbdf881bcef27fcdefee622`，当前仅 `DEV-PLC-A`；DS 前测 `ce8597902f74425249f0385514c68a0a71f732a14e6087d2bf770cabccea663a`，当前 `a4300e52d088946fe8061e8fe5a6234b1a8cbffecb7dd0d2f446e99f16354e6f` 且与当前保存 SHA 相同，当前 instances 为空、sourceVersions 有 5 条。未列入基线的表及草稿其他列不宣称逐行比较；profile 并非零写。
- 查询时 `lsof` 显示 DAA PID `5445` 打开两库、DS PID `5272` 打开其配置库；本 QA 未停止进程。各库事务彼此独立，草稿另行读取，不能称为跨三库同一瞬间的原子快照；结果只描述上述只读观察时点。初次 `ps` 查询因系统 `Operation not permitted` 而 exit 1，未据此推断无进程。

### 本轮命令、限制和 handoff

macOS 15.7.7 (24G720) arm64，Node `v22.19.0`、pnpm `11.11.0`。正式 DAA 根 `node --test tests/plc-catalog-import.test.mjs` exit 0、6 passed；此为内存替身，不是本轮原生 IPC 截获。Python 标准库只读比较 35 项候选 SHA、两个 PLC locale 的 JSON 叶键（各 264，差集 0）、38 个手册相对链接/标题锚点（缺失 0）、三文件 SHA/归一化内容及上述数据库多重集，均完成；`git diff --check` 限两手册、两 locale、`CODE_INDEX.md` exit 0。Node 启动时 shell 输出 `/bin/ps: Operation not permitted`，测试仍 exit 0。没有本轮新建测试副本、启动 GUI、连接设备、采集、上报、激活或清理。

`F-DAA019-QA3-001` 经协调者返 Development；修复后须以精确候选重新 handoff 和 fresh-context Verification。原 QA2 的旧轮前测与同次原生返回值 blocker 继续交 Human Owner 知悉；若无法取得可信旧证据，由 PM 评估，实质改变验收或风险需新 Revision 和 Human Owner 精确批准。`/private/tmp/plc-json-owner-manual-82_5g47q` 保存本轮三文件与完整基线，暂为证据依赖；QA1/QA2 列出的旧临时资源亦按各自证据依赖保留，待独立复核和 Human Owner 审阅不再依赖、协调者确认归属及无占用后按 workflow 回收，不触碰用户 profile 或历史。Windows/VM、旧二进制兼容、真实 PLC、真实 POST、部署和发布均不在本轮通过结论中。

追加审计：移除本 QA3 附录后的前缀 SHA-256 为 `327cf8d23af9a6717bde1171f5d13d098c0346400263a4f56b1e60a5511ba1bd`，与追加前完全一致；spec/tasks 的 SHA 仍为上述读取值。`git diff --no-index --check /dev/null <本 checklist>` exit 1 表示新文件与空文件不同，未输出空白错误；Python 检查尾随空格 0。

## QA4 · 2026-11-18 · F-DAA019-QA3-001 限定复验

独立 Verification 在正式工作树复核 DAA-019 r2。**本项通过，文案缺陷关闭。任务整体最新 verdict 为 `qa_blocked`。** 追加前 checklist SHA-256 为 `0f556176f7d525bed03c09a8c104848b7e42e3d792ec4ec65165a5afdaf3813e`。

- Darwin arm64，Node v22.19.0。用 `rg -n -C2 catalog_origin_conflict src-tauri/src` 核查生产分支：local_store/configuration.rs:310 检查当前已有同源，同行文件第 92 行检查 PLC 内目录 DB 来源不一致，services/catalog_export.rs:118 检查导出时各 DB 来源不一致。导入弹窗第 8 行和导出弹窗第 22 行均经 local.label 展示。两种语言仅说明来源身份冲突、请核对配置和目录来源并参阅手册，三种情形均适用。
- 在 DAA 根运行 Node ESM（fs 解析两 locale、assert.deepEqual 比较递归排序的叶键、vue-i18n createI18n 逐语言断言 t 的结果与对应 JSON 文本相等），exit 0，两边各 264 键。逐句审阅两手册 §2.4：仅确需移除时先评估影响；仅草稿则移除保存后重试；活动或运行中则先停采断连，再移除、保存并显式激活；仅历史时选择新本机实例。通用报错没有要求执行这些操作。限定两手册及 PLC locales 的 git diff --check exit 0。
- Python hashlib 按 tasks.md 中逐路径最后一次列出的摘要重算，35/35 一致。以模块相对路径升序、每行「小写文件 SHA-256、两个 ASCII 空格、路径、LF」编码 UTF-8，清单 SHA-256 为 `03acaaf5b4605c246d9148badaf8e514135b02a0645edbbc04d1093fbb46b858`。HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，含未提交差异。spec SHA-256 为 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，tasks SHA-256 为 `44ec6805ae48509a3a7d7cb5635538a5cf366af1fd7d5a1a9c31b57ea41e8696`。英文 locale 为 `0d02cbd85a0b4dc9096925728d2698f5d811e24030894fa29c65552c58097eee`，中文为 `715e385a8e82449c12b6b03f6a7ab213bf9f9a51723898587ae9b1a160d144df`。ARCH-PLC-002 可据该清单固定 DAA 来源候选接续。
- QA3 的 37 表及三文件复核沿用原记录。本轮未读取用户 profile，未操作 GUI、构造冲突或重跑未变源码测试。旧轮 D19-05 前测及同次 L2 IPC 返回 ID 的证据缺口仍保留，交 Human Owner 知悉，最终验收待 Human Owner。

## QA5 · 2026-11-18 · 双语使用手册独立复核

本轮手册候选结论为 **qa_failed**，返 Development 修正 F-DAA019-QA5-001。DAA-019 r2 整体沿用 QA4 的 **qa_blocked**。旧轮 D19-05 前测及同次原生 IPC 返回 ID 的证据缺口仍在，最终验收归 Human Owner。

- Darwin arm64，正式交付树未提交基线 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。模块根运行 `shasum -a 256` 核对英文手册 `b096f7cc578d48ec9736ef2a358908f5aa3e87127e0794848c68b241f5734624`、中文手册 `7e2b44d4af6d205bd3507c13a54b4dfbce20a24d07369702ad4b7029f5a4aafc`、tasks `4c45401f51f3376f69a7f9516a2742505b662475b8f51f26f3deeb31aa40077c`、r2 spec `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，均匹配。限定两份手册的 `git diff --check` 无输出，diff 位置为首页导航和第 2 节。Python 3 按标题生成锚点并逐项核查首页导航和第 2 节本地文件/锚点，中英各 18 项通过。
- 两种语言按资料分路，均有 6 个小节。逐项对照 PLC 配置和点位页、SourceImportPanel、采集控制台、ConfigRevisionBar、工作台及其采集状态页：PLC 可复用或新建，弹窗保存后选择目标；DB 按页勾选并指定编号，UDT 作依赖，预览后确认；地址推算或人工确认后核对实际长度；区分技术名、双语显示名、组和点启用；保存、显式激活、连接、启动采集后核对本地样本。示例夹具包含一个非优化 DB 和所引用的 BOOL、INT、REAL 结构。与采集无关的交换有独立停止点。
- 对照目录导入、导出对话框和对应实现，手册已写明目标与完整点表核对、当前同源与仅历史冲突的不同处理、导入默认停用和未分组、导出来源、预览确认、选择目录与逐项结果。发现一处两种语言共同的偏差。
- **F-DAA019-QA5-001**：§2.5 步骤 2 描述每个默认名一律为 PLC 名加 `.json`。现行 `src/app/plc/components/CatalogExportDialog.vue:71` 保留已有后缀且大小写不敏感，与 ARCH-PLC-002 的 E01 一致。用 Node ESM 从该组件提取实际默认名表达式并逐项断言，`LineA → LineA.json`、`LineA.json → LineA.json`、`LineA.JSON → LineA.JSON` 全部通过，exit 0。请 Development 在两种语言说明仅在缺少该后缀时补上，再交独立复验。
- Python 3 `os.path.lexists` 对本次 tasks 末尾列明的七个 /private/tmp 路径均返回 False。本轮仅能重读历史记录；未从已清理的原件复核历史结果。未启动 GUI、访问用户 profile、连接 PLC、运行整套测试或干预应用。QA 仅追加本段，追加前 checklist SHA-256 为 `5bf6ad7810841555d7db3d5369483ade6f82f99a4ca079fc8f1e60c691a40c1a`。

## QA6 · 2026-11-18 · F-DAA019-QA5-001 限定复验

双语手册返修 **qa_passed**，关闭 F-DAA019-QA5-001。DAA-019 r2 整体仍为 **qa_blocked**，旧轮 D19-05 前测及同次原生 IPC 返回 ID 的证据缺口继续提交 Human Owner 审阅。最终验收待 Human Owner。

- 正式交付工作树 Darwin arm64，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。模块根运行 `shasum -a 256`，英文手册 `e6e78aa6aa37607f3ad1f87460195fb94a88a4353ff2727c97bab60e807d7fe0`，中文手册 `70449aa68c3c4d821f8a86e47269f224e1925c70b9f87ef4484b8b69c6c5d72e`，tasks `28052c99001d5bb808012f2682ccadccd4185aadf48a91c663114f82b4f147cd`，spec 与 QA5 相同。追加前 checklist 摘要为 `a3ef477a76ec945b22bd610a112d664115504eb2c7790630ec890543c97bd93d`。
- 两份手册第 110 行均说明默认取 PLC 名，只在缺少大小写不敏感的 .json 后缀时补齐。Node 从 CatalogExportDialog.vue 第 71 行直接提取表达式，assert.strictEqual 核对 L、L.json、L.JSON、L.JsOn、L.json.old 五例，分别得到 L.json、L.json、L.JSON、L.JsOn、L.json.old.json，通过。
- Python 3 在内存中分别将第 110 行修改的短句换回旧文，两个整文件 SHA-256 均精确恢复为 QA5 记录值；去除 tasks 本轮交接段后，前文摘要也匹配 QA5。双语手册首页及第 2 节本地链接和锚点各 18 项通过。限定手册与任务目录的 git diff --check 通过。
- 本轮仅核验文档与现行源码。未运行 GUI、访问用户 profile 或复验已回收的历史工件。

## QA7 · DAA-019 r3 独立文档复核 · 2026-11-18

**文档 verdict 为 `qa_failed`。** R3-06 的 Development 交接摘要有误，编号 F-DAA019-R3-001。返回 Development 更正事实记录并重新交接。r2 整体仍为 `qa_blocked`，Human Owner 最终验收待定。

- R3-01 已核。正式工作树为本仓 main，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，Darwin arm64。对照 tasks 历史清单、ARCH-PLC-002 交付记录、QA1–QA6 与正式树差异，重新计算 36 项组合清单 SHA-256 得 `91cd78967c3fc67f6c8891641057924fecf1400267d9e2cc9027e8c03e5f45f4`。原 35 项含 25 项保留、8 项后继变更、2 份后修手册，另有样式文件。旧原生与程序检查只归当时候选。QA1、QA3、QA5 原失败及后续限定返修结论均保留。
- R3-02 已核。Owner 报告两端语言切换、DAA→DS→DAA、当前同源拒绝、移除保存草稿后选择历史新实例、自动显示 L2 和四点并对其再导出。QA3 曾比较三份实物文件，依次为 DAA、DS、DAA，各 1 DB / 4 点，外部身份、技术字段、双语及 description 按当时排除 export 头、连接目标与启用字段的口径一致。早轮 L2/L3 分次观察保留。本次 QA 阅读既有记录，同次原生 IPC 返回 ID 未直接截获。
- R3-03 已核。双语入口、单一挂载及手册有静态记录；空侧语言、独立 description、冲突及历史身份隔离有服务检查；返回 ID 选中、取消及未知结果有前端替身检查。逐项部分失败有既有隔离服务记录，两种 sentinel 有 fake transport 正文检查。英文原生仅入口、弹窗、取消与预览，双 GUI 并发和 OS 故障注入未覆盖。
- R3-04 已核。按 spec 私有定位核阅协调者既有报告。该人观察一次本机配置 seq 91–103 的 13 条实际上报，有匹配回执，status 为 committed，outcome 为 created 或 duplicate；本地正文与回执摘要对账。至少一个点双语显示名均非空，13 份正文均无显示名字段及对应文本；MySQL history 所核身份、正文摘要及三点名、类型、值、质量对应，点集未见显示名字段。latest 三点 good、seq 103，同期 DS 日志未见 WARN / ERROR。正文文本排除结论仅归请求正文。本轮独立核阅限于报告。
- R3-05 已核。旧 context 仅有汇总，samples 其他列及 sample_delivery 缺逐行前测；后一轮 37 表各自事务不能倒证早轮。DAA-018 原生隔离事件的写入及影响仍未知。旧二进制、Windows/VM、真实 PLC、异常回执、其他配置、持续运行与生产采用均未验证。原临时工件经 Owner 同意已清理，本轮未恢复，无新测试资源。
- R3-06 未通过。用 `shasum -a 256` 核对 r3 spec、父 r8 spec 与交接 tasks，分别为 `e0eb80fefbc14a664dfc380f1081691ad8e415d5ca4cff0f66fe9890612e29bd`、`38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`、`7b0f91fb35a145aeb1ce231fdf9a78f63f68112e0d65d49e6c0915272526af4a`。Python 3 hashlib 复算追加前 tasks 为 `28052c99001d5bb808012f2682ccadccd4185aadf48a91c663114f82b4f147cd`，与 QA6 一致。tasks 第 416 行记载的写前 checklist 摘要只有 62 位，中间遗漏 `8b`，与实际 64 位摘要不同。该处声称核验成功，读者无法按其记录复现。本次 QA 追加前完整 checklist SHA-256 为 `1442d5e2ff1d237d3b592e9bb5c8b32fbd7590c4e461e2b0174ab50e9fd4b391`，删除本节及新增分隔空行即可重建。

本次 fresh-context 复核只追加本节。文件读取、SHA 计算和工作树 diff 命令执行成功；一次父规格路径 glob 未匹配，定位至 automation-world/plans 后重核成功。按已批准范围，产品测试、构建、GUI、用户 profile、数据库、PLC、网络及上报均未执行。返修仅需更正原交接证据，随后独立复核该项。

## QA8 · DAA-019 r3 · F-DAA019-R3-001 返工复核（2026-11-18）

**文档收尾 verdict 为 `qa_passed`，关闭 F-DAA019-R3-001，交 Human Owner 最终验收。** 本结论限于已批准 r3 的 R3-01 至 R3-06。r2 整体仍为 `qa_blocked`；QA7 的文档失败及原交接按原字节保留。

- R3-06：在正式工作树 Darwin arm64、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，使用 `shasum -a 256` 得到批准 spec `e0eb80fefbc14a664dfc380f1081691ad8e415d5ca4cff0f66fe9890612e29bd`、返工 tasks `92462dd1f1c1a943745b28f56198eaf6dd56bb5b279322117e5bf7a0754c8f52`、追加前 checklist `3d45a4b855980d55f7d22816f765175374d23a3c65778e91b326091c81b8919d`。Python 3 hashlib 取 QA7 标题及其分隔空行之前的原始字节，得 `1442d5e2ff1d237d3b592e9bb5c8b32fbd7590c4e461e2b0174ab50e9fd4b391`，与更正段逐字匹配。相同方法截取 tasks 更正段前及初次 r3 交接前的字节，分别得 `7b0f91fb35a145aeb1ce231fdf9a78f63f68112e0d65d49e6c0915272526af4a` 和 `28052c99001d5bb808012f2682ccadccd4185aadf48a91c663114f82b4f147cd`。本任务三文件相对文档链接均可定位。上述命令退出 0。任务目录在 Git 中为未跟踪，历史差异依据上述前缀比对。
- R3-01：核对 QA7 与交接，36 项组合清单保留 25 项原候选、8 项后继变更、2 份后修手册及另计的样式。原自检和 QA 结果仍归各自候选。
- R3-02、R3-03：Owner 的双向往返、同源拒绝、新实例自动显示四点与再导出，QA3 当时对三份文件的对比，以及服务、替身、静态和手册检查均保留执行者与覆盖范围。同次原生 IPC 返回 ID 未直接观察。
- R3-04：核对 tasks 与 QA7 对协调者单机单配置 13 条既有上报观察的归属。seq 91–103 的回执、请求正文显示名排除、history 所核三点与 latest、同期 DS 日志仅覆盖所列记录。本轮依据既有文档。
- R3-05：旧轮逐行前测缺失、后轮 37 表分库事务的时点限制、隔离事件影响未知及旧工件已清理均已披露。旧二进制、Windows/VM、真实 PLC、异常路径、持续运行及生产采用仍未验证。本轮仅审阅文档和文件摘要，无测试、构建、GUI、用户 profile、数据库、PLC、网络或上报操作，无新增测试资源。
