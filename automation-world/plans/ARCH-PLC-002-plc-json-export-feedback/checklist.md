Task ID: ARCH-PLC-002
Revision: r1
Status: owner_accepted
Owner Role: Verification
Handoff: Human Owner 已最终验收本 Revision，交协调者按 workflow 收尾。

## 第一次独立复核 · 2026-11-18

正式工作树 main，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。以补齐原生证据的 tasks SHA-256 `aeab0f12908908e019a03b96942c2dd2ff66a8f2f4a2bcdaef40265b01fd9d3e` 和批准的 spec `a4d2744297d3882f90c4f865d2ef8ec0b8e2f5ada30ce4fc754be4913ae2b349` 复核。Python hashlib 逐项比较固定前序目录与正式工作树，再逐文件核 tasks 两表。DS 30 项中恰有表列 12 项不同，DAA 36 项中恰有表列 11 项不同，23 个候选摘要全部一致。`git diff --check` exit 0。前序 DS-005、DAA-019 的历史结论继续归原任务。

### 需返回 Development 的 E04 故障

DS 对话框 `CatalogExportDialog.vue` 第 207 行仅按 instanceId 取首条回执。独立复现使用正式 SFC、项目 Vue runtime、现有 Node 测试的 host，以内存 IPC 替身控制返回值。在 DS 的 tests 目录将 `sed '/^test(/,$d' plc-catalog-export.test.mjs` 输出和以下代码一同送入 `node --input-type=module`，未改测试文件。

```js
const first = {instanceId:'instance', name:'Saved', filename:'Saved.json',
  result:'written', fileSha256:'a'.repeat(64)};
for (const rows of [[{...first,filename:'other.json'}],
                   [first,{...first,result:'failed',fileSha256:null}]]) {
  const h = host({catalogCommit:async()=>({rows})});
  h.state.revisionId='revision'; await tick();
  h.state.selected=['instance'];
  await h.state.prepare(); await h.state.choose(); await h.state.commit();
  console.log(h.state.summary.key,h.state.results.rows[0].filename);
  h.unmount();
}
```

实际输出依次为 `success other.json`、`success Saved.json`，exit 0。第一组缺少所确认目标的回执；第二组同一目标的两条回执互相矛盾。两组均应将该行列为 unknown、保留确认的名称并提示检查目录。真实后端正常写出路径能生成一致的回执，本项复现的层级是正式 Vue 行为与受控 IPC。修复后需覆盖错名、重复、缺失及正常部分结果。

### 其余验收与证据层级

| 项 | 验证结果 |
| --- | --- |
| E01 | 两端现有 Vue 测试验证默认扩展、逐 ID 命名和多选。两次 Owner 单台导出及本次文件核验见下。 |
| E02 | 两端前后端逐名验证包含 UTF-8 长度、禁用字符、扩展、尾随字符、保留设备名和大小写重复。DAA 导入 candidate 的文件名条件接受普通 `DS-自定义测试.json`；该结论来自源码。本轮未在用户配置中执行原生导入。 |
| E03 | 两端 Rust 均以目录描述符和排他 linkat 发布目标。DAA 原生桥在 blocking_pick_folder 前 release_directory，取消时撤销 token。独立重跑交接构建的 DAA Rust 测试，真实引擎撤销旧目录后提交被拒，旧文件未创建。此项模拟选择器等待窗口，非 GUI 并发测试。两端组件覆盖修改与取消，DS 文件竞争复用 Development Rust 证据。 |
| E04 | **失败**。正常全成功、部分、全失败、缺行和整次未知已有组件证据，两端标题区展示摘要。异常对应关系的错误见上述复现。 |
| E05 | DS 和 DAA 实际文件的 origin、plc、dbs 分别与前序文件逐字段相等，含全部 4 / 3 点。DAA Rust 验证同一票据预览 SHA、落盘字节和回执 SHA 一致。DS 对应原字节断言与导入回归复用 Development 记录。 |
| E06 | 两端 Human Owner 各自报告原生改名后顶部成功。Verification 只读检查真实文件，未亲眼操作或观察界面。双语通过资源和组件检查，未取得两套语言分别运行原生窗口的证据。 |
| E07 | 已查两端中英文用户手册关于自定义名称、冲突、部分及未知结果的说明。仅使用隔离测试和只读原生输出，未接触真实 PLC 或写用户配置。 |

独立在两个应用目录运行 `node --test tests/plc-catalog-export.test.mjs tests/plc-catalog-import.test.mjs`，各 11/11 通过。于 DAA 目录清除 DAA_ENV_FILE、DAA_PROFILE_DIR、DAA006_NATIVE_SEED_ROOT，设置 DAA_PLC_READ_ALLOWED=false 和交接时的隔离 TMPDIR，重跑交接二进制 `aiis_data_acquisition_agent_lib-8ef9875a6f47283b catalog_export --test-threads=1`，5/5 通过，exit 0。环境为 macOS arm64，类型、Vite、DS Rust 与桌面编译复用 tasks 的开发证据；DS 大容量导入夹具两次首次失败、热缓存重跑通过的限制保留。

### 原生文件及资源

- `DS-自定义测试.json` SHA-256 `f24a68fd9c65433918748fef3fe6bddeff793cee404cab20375bc5b3a3572942`，producer 为 device_simulator，4 点；与前序 ds-export/38b0b960-99e0-4ebe-a5c0-dff340ad369f.json 的 origin、plc、dbs 一致。
- `DEV-自定义测试2.json` SHA-256 `1a60086e9585520054dd8c23687e9bc75cc262a6d691ca6b1f8ed2aa2d3fa00a`，producer 为 data_acquisition_agent，3 点；与前序 daa-dev-export/f6da5dac-7326-4a6c-bceb-55ad7e74b8cf.json 的同三部分一致。
- 两份输出的校验和内容对照已持久记录，本轮 Verification 对 `/private/tmp/plc002-owner-vl_d8us2` 无后续文件依赖。DS Vue 回执修复可用组件验证。前序快照、前序联测目录与本任务编译目录分别由协调者按所属任务和复验依赖收尾。

## 第二次独立复核 · 2026-11-18 · QA1 E04 返工

**最新总体 verdict 为 `qa_passed`。** 本轮将 `aiis-ics-arch::ARCH-PLC-002 r1` 交 Human Owner 最终验收。上方 `qa_failed` 保留第一次复核时点的结论。

- 正式树 main，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。在仓库根用 `shasum -a 256` 复核 spec 为 `a4d2744297d3882f90c4f865d2ef8ec0b8e2f5ada30ce4fc754be4913ae2b349`，最新 tasks 为 `93fe10c0255cf3d31be01e30678cb83efdff08996dab81acf0bf389d25665ee7`。Python pathlib/hashlib 比较固定前序目录、交付树和 tasks 两张指纹表并应用返工的两项替换。DS 30 项中 12 项有差异，DAA 36 项中 11 项有差异，均在 r1 白名单，23 项交付指纹一致。比 QA1 仅 DS 对话框和 DS 导出测试指纹有变。仓库根 `git diff --check` exit 0。
- E04 通过。在 Darwin arm64、Node v22.19.0 的正式 DS 目录运行 `node --test tests/plc-catalog-export.test.mjs tests/plc-catalog-import.test.mjs`，12/12 通过，exit 0。核读正式 Vue SFC 的 commit 分支与测试断言。组件按确认目录逐实例核对唯一回执、完整文件名和状态值。受控 IPC 分别返回错名、矛盾重复及非法状态时，该实例保留确认名和目标，显示 unknown、无 SHA，另一实例保留真实的失败原因；重复调用提交只发一次 IPC。缺行时保留已确认邻行的 written 和 SHA。逆序部分回执、全部成功、全部失败及整次传输未知的计数和摘要通过。此处的结果由组件接收测试回执产生。
- E01–E03、E05–E07 延用第一次独立复核及其明确的覆盖层级。两端原生单台改名与顶部提示由 Human Owner 实际观察；QA1 核过输出 SHA 与逐字段对照。原生输出经协调者复算后已回收。本轮未重做原生、Rust、DAA、双语窗口或类型与构建检查；已复算返工 Vite JS 的 SHA 与 tasks 一致。保留原记录中的 DS 大容量夹具首次失败、重跑通过及 Windows 原生未验证限制。
- 本次复验结束后，对三个任务自有目录 `/private/tmp/arch-plc-002-dev.hkE5uJ8v`、`/private/tmp/arch-plc-002-daa-7Lx7oV`、`/private/tmp/arch-plc-002-qa1-rework.NggGJYAw` 已无 QA 证据依赖，交协调者核对运行占用及其他任务依赖后回收。固定候选 `/private/tmp/arch-plc-002-predecessor-fpjq3d7g` 与前序联测文件仍供前序任务核对及 Owner 验收，由协调者按所属任务确认回收时点。本次仅追加本清单，未操作用户 profile、PLC、采集或上报。

## Human Owner 最终验收 · 2026-11-18

Human Owner 经协调者转达的原话为“验收 ARCH-PLC-002 r1”。Verification 据此记录 aiis-ics-arch::ARCH-PLC-002 r1 为 owner_accepted。验收范围为 DS 与 DAA 的逐 PLC JSON 导出文件命名及结果反馈。QA1 的 qa_failed 和 QA2 的 qa_passed 按原时点保留。DS-005 r2 与 DAA-019 r2 各自的 blocked 状态仍归原任务。现场设备和部署属于独立授权范围。
