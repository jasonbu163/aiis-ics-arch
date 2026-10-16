Task ID: CU-007
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-007 r1 implementation and bounded DEV self-check complete in the protected working tree; ready for fresh-context QA / Verification, not a QA verdict or Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-007 r1 Development

## 依据与实施顺序

精确执行 [owner_approved spec](spec.md)；2026-10-16 Human Owner 批准只改 CU、源码开发模式及有限构建/启动/编辑应用验证。保留 dirty/untracked 基线，未从 HEAD 恢复任何源码。实现面仅 spec §3，四机械索引由主协调维护。

1. R3–R5：抽取固定 JSON/CSS helper，保留 CLI 合同，接入前置 Vite 开发通道和 loopback/Host/Origin/token/请求体保护。
2. R1–R2、R6–R7：显式应用按钮及对称 i18n，私有客户端跨 HMR 保留 pending/结果/参数页，不改草稿、公共 schema/API 或布局。
3. AC1–AC5：最终一次构建；本机一次原生窗口启动与同服务真实浏览器代表性编辑/应用/刷新；一条拒绝请求摘要不变，归属核对后恢复原公共默认；交精确增量给 fresh-context Verification。

## 基线与资源

- 工作树 HEAD：`1a5aa2d2fe7089b5671218865238cfaa240f9a30`（仅标识仓库起点，增量以本次文件备份为准）。
- 证据/恢复目录：`/private/tmp/cu-007-r1-hd36i7a9/`；`before/` 保存10个既有 allowlist 文件，4个新增文件原不存在；`baseline.json` 保存原文件摘要及受保护基线摘要。
- 写前 `lsof -nP -iTCP:15193 -sTCP:LISTEN` 发现既有 node PID 41748；未知归属，未停止/杀除。主协调确认 cwd 为本 CU；该既有服务随后自行消失。再次确认端口空闲后，本任务实际使用正常 `pnpm tauri dev`，未使用命令内覆盖、未修改 Tauri 配置或新端口。
- 本任务计时由主协调管理；Development 未重复启动 notifier。

## 实际实现文件与需求对应

最终12个实现路径（不含本 tasks；两个公共验证目标最后已原样恢复）：

| 路径 | 实际改变 / 对应需求 |
| --- | --- |
| `vite.config.ts` | 注册私有开发插件；既有 host/15193/14193/Vue/build 不变（R2、R5） |
| `scripts/design-profile.mjs` | 薄 CLI，复用固定 I/O helper；裸入口/help 先返回，原显式 import/generate/check 保留（R3–R4） |
| `scripts/shared-design-profile.js`（新增） | 自身路径锚定两个公共目标；共用纯生成/内容版本/唯一临时文件+rename+cleanup；导入无 I/O（R3–R4、R6–R7） |
| `scripts/shared-design-profile-dev.js`（新增） | 前置私有 dev-only 中间件；真实loopback/Host/Origin/session、方法/content-type/实际64KiB/schema保护、写前版本核对与进程内串行（R2、R5–R7） |
| `scripts/shared-design-profile-dev.d.ts`（新增） | 仅私有 Vite 插件工厂类型，不改 tsconfig 或依赖（R4） |
| `src/workbench/useSharedDesignProfile.ts`（新增） | 首次连接记录 revision，点击快照提交，无自动重试；内存 refs 与 HMR dispose 保留 pending/结果/profile/section；不新增存储键（R1–R2、R6） |
| `src/workbench/Workbench.vue` | 仅接线共用内存 profile/section；原主题、locale、预览与壳层布局不变（R6–R7） |
| `src/workbench/DesignProfileEditor.vue` | 应用按钮、显著源码模式说明和结果反馈；无效/不可用/pending禁用；原草稿/恢复/重置/导出保留且 pending 防修改快照（R1–R2、R7） |
| `src/locales/en-US/workbench.json`、`src/locales/zh-CN/workbench.json` | 对称新增开发限制/应用/成功/失败/冲突/恢复文案（R1–R2、R5–R7） |
| `README.md`、`README.zh-CN.md` | 同源消费、新私有 helper 职责、开发模式操作、恢复及宿主重构建责任（R2–R7） |

`src/ui/styles/design-profile.json` 和 `design-profile.generated.css` 实际用于有限应用验证，最后均恢复为本轮原始字节，未重新设计默认视觉。公共八组件/API、schema/纯映射、原入口及DIRECT宽度修复未改。无 package/锁文件/tsconfig/Rust/consumer/其他 Agent 修改，无新依赖、服务或端口。

## DEV self-check（非独立 QA）

环境：当前 macOS 主机，Node `v22.19.0`、pnpm `11.11.0`；沿用项目锁定依赖。以下证据均在 `/private/tmp/cu-007-r1-hd36i7a9/`。

| AC | 真实命令 / 方法 | 结果与证据 |
| --- | --- | --- |
| AC1 | `node --check scripts/shared-design-profile.js`、`node --check scripts/shared-design-profile-dev.js`、`node --check scripts/design-profile.mjs` | 三项语法检查无错误；随后独立端口检查返回1（空闲），不是语法失败。源码逐项审阅：无路径参数、导入时无I/O、dev-only前置端点、保护拒绝不透传、完整schema/生成在写入前、版本冲突409且不刷新基线/不自动重试、CLI裸/help无默认读写、build仍只读check。 |
| AC1 | Python静态键/本轮增量/相对链接/保护摘要检查 | 最终147个双语键结构对称，两个Vue文件的literal翻译键均可解析，README相对链接有效；12个实现路径全部在allowlist，新增diff行无尾随空白；13个保护摘要不变，包含 `workbench.css` 的150px修复。`static-check.log`、`baseline.json`、`manifest.json`。本轮新增反馈实际GUI观察为英文；中文通过键与文案审阅，未为切换语言改写原偏好。 |
| AC2 | CU目录 `pnpm build` | 首次exit0（`build.log`，Vite2.38s）。之后为恢复两条不必要的既有英文反馈文案发生locale源码变化，最后在实现冻结、公共默认恢复后再执行最终 `pnpm build`：exit0，现有只读CSS一致性check、vue-tsc、Vite通过，Vite2.37s（`build-final.log`）。仅既有第三方PURE注释及>500kB chunk提示，不改构建优化。未构建consumer。 |
| AC3 | 正常 `pnpm tauri dev`，需要已授权 `require_escalated` 允许本机监听 | 本任务session `72154`，Vite PID `49663`，15193 ready；Cargo既有target启动成功，`cu_window_created`、`cu_event_loop_ready`均ready。`tauri-dev.log`。只启动一次原生开发窗口，没有Cargo单独测试/打包。 |
| AC3 | 主协调在同次服务的真实IAB tab6提供 Development GUI self-check 支持（不是独立QA，也不是原生WebView交互） | 初始EN/Dark、动作间距12；稳定复查13→14后两公共文件为规范JSON/匹配CSS，HMR后参数页/成功反馈仍在，同屏真实样例可见；手工刷新后重新打开参数页值为14。`gui-observations.json`、`gui-applied-files.json`、`gui-refreshed.ax.txt`、`cu7-applied-stable.jpg`。未点击保存/恢复/重置、未改theme/locale偏好。 |
| AC4 | `python3 /private/tmp/cu-007-r1-hd36i7a9/check-rejection.py` | 首次沙箱在GET连接阶段EPERM，exit1，尚未发POST或改目标；相同范围经 `require_escalated` 成功，exit0：唯一实际非法schema POST返回400 `invalid_profile`，前后两目标SHA-256相同（`rejected-request.json`）。GET所得token仅内存使用，未写磁盘/日志。其他保护/冲突分支仅源码审阅，无攻击/并发矩阵。 |
| AC5 | Node ESM有限恢复脚本：先比对GUI与拒绝请求摘要、原方案只动作间距变14、规范JSON/匹配CSS，再用同helper版本保护恢复 | 当前仍属于本轮输出才执行；已保存 `applied/` 两文件，原默认动作间距12及两目标原始字节均恢复。`restoration.json`。未从HEAD恢复或覆盖未知更改。 |
| AC5 | `write_stdin(session_id=72154, chars=Ctrl-C)`，随后独立 `lsof -nP -iTCP:15193 -sTCP:LISTEN` | 本任务原生/服务session结束exit0；lsof exit1且空输出，15193已释放。未知旧服务未被停止。tab6由主协调关闭。 |

### 实际干扰与有限复查

首轮GUI12→13实际成功写入两个公共文件，立即反馈也可见。但Development在观察同时将两条不必要的旧locale反馈恢复原文，触发15:31:38 Vite locale full-reload，打断了页面观察。这不是已证明的公共JSON/CSS HMR缺陷：日志15:31:36先为两个Vue组件与CSS HMR，随后明确为locale page reload。保留 `gui-first-apply-files.json` 与 `cu7-interrupted-by-locale-reload.jpg`（及原PNG），不将失败截图冒充通过。停止全部源码编辑后只复查受干扰的同服务13→14流程；15:34:46仅组件/CSS HMR，参数页与成功反馈稳定。未为这次干扰额外引入架构、storage或原生重启。

## Developer handoff

- 精确目标：**CU-007 r1**，当前工作树，HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30`；无commit、分支/worktree/Git refs/推送/发布操作。
- 实现增量以本轮 `before/` 为基线（仓库已有大量历史dirty/untracked，不能用HEAD总diff冒充本轮）。精确12路径 `incremental.diff` SHA-256：`65e009e1afc9ac398576b9e017f6bf5bcacd1fde0c73d76efbbc9b9afed8c5c5`；按路径排序的实现文件摘要列表 `ordered-hashes.txt` SHA-256：`ae5338e822c3faf79a303ba81dd2c5373646b9fb7af3c51498fed0920ea34670`。`manifest.json`包含每文件before/after；`after/`保存最终14条allowlist快照（两验证目标净差异为零）。本tasks为唯一额外Development事实文件，不纳入实现diff摘要以免自引用。
- 两目标恢复摘要：JSON `b705bb4a7413ff185b09b1a7c92c50debd7c6af637bfa4c9436ada8b10bfd2bd`；CSS `3be630b1fca44bbb0e469d12ded98baa08050a53c96706a720cb821982a06739`。实测应用14时摘要及完整内容保存在 `gui-applied-files.json` / `applied/`，不是要求保留的视觉默认变化。
- 保留资源：本证据目录的before/after/applied/、diff/manifest/哈希、日志、GUI AX/JSON/JPG及原PNG、有限拒绝验证脚本，供freshQA与尚未提交源码恢复；验收前不清除。没有本任务运行服务或worktree。IAB初次端口未启动时产生的失败临时tab5转为data错误页，主协调无法因URL policy重新选择，未绕过；预计临时tab随turn结束关闭，未声称全部tabs手工收尾。
- 限制/风险：仅源码开发态可写；preview/打包无写端点由构建分支/插件边界审阅而未另行打包运行。进程内队列+乐观内容版本不等于跨进程锁；两个文件替换不等于事务，部分I/O失败按界面/README恢复。没有全量回归、主题/字段组合矩阵、consumer重构建、其他Agent集成、DB/PLC/现场/跨平台/分发证据。独立QA不能将本DEV self-check当成其自身操作；缺失或疑点才定向复查。
- 下一 gate：主协调显式启动 **fresh-context QA / Verification**，输入已批准spec、本tasks、当前实现和上述精确diff/输出/截图；Verification独占创建checklist及verdict，Human Owner仍保留最终验收。Development不修改spec/checklist或四机械索引，不授予QA/最终接受。
