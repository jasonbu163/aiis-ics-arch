# DAA Windows 原生验证记录单

**状态：待验证。** 本单供 Human Owner 后续在 Windows 10/11 x64 实机填写；目前没有 Windows 实测结果。范围和验收依据为 [DAA-010 r5 AC08](plans/DAA-010-sample-facts-upload/spec.md#5-验收标准)及[第 7 节](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续)。先确认本次精确候选、合成环境、运行与故障注入范围获得相应授权；此记录单本身不授权运行、部署或真实环境采用。具体配置、操作与核对参照 [DAA 使用手册](USER_GUIDE.zh-CN.md)，步骤不适用或无法确认时停止并记录阻塞。

## 一、记录环境和候选

- 日期、操作人：________________
- Windows 版本、构建号、x64 架构：________________
- DAA 交付工作树或 commit、具体候选文件清单及摘要、与原 QA 候选的关系：________________
- Node.js、pnpm、Rust / Cargo、Windows SDK 与 MSVC 版本：________________
- 本次专用 DAA profile 绝对路径：________________；启动后的目录、日志时间及核对证据：________________
- 独立 DS/S7 模拟端及其 profile、地址和端口：________________
- 已采用对应合同的隔离后端 / Web、数据库目标和合成来源三标识：________________
- 故障注入工具、授权范围与停止方式：________________
- 脱敏证据位置、样本 ID、时间及操作者记录：________________

## 二、准备

1. 使用完整的精确候选源码及其锁文件，包含仓库内 DAA 所需的共享源码。核对本机 Git、与项目 `pnpm@11.11.0` 兼容的 Node.js / pnpm、Rust stable 的 `x86_64-pc-windows-msvc` 工具链及 Cargo；确认 Microsoft C++ Build Tools（含 MSVC C++ 工具链和 Windows SDK）及 Microsoft Edge WebView2 Runtime 已安装且可用，缺失时再安装；Windows 10 1803 及以后通常已带 WebView2。普通 Tauri 配置会传递 S7 驱动 feature，Rust 构建还需可用的 C++ 编译工具。实际版本和缺失项填入上表；安装或企业策略受阻则记阻塞。可查 [Tauri 官方 Windows 前置条件](https://v2.tauri.app/start/prerequisites/#windows)。
2. 仅使用经批准的合成 S7 模拟端、独立模拟器 profile、隔离后端及 Web，确认它们的候选、地址、端口、数据库目标和来源配置。后台提交与 Web 历史读回须指向同一受控目标；`127.0.0.1` 指运行相应程序的本机。不要连接真实 PLC 或复用现有 dev 后端。
3. 在受控位置用资源管理器新建本次专用父目录，例如 `C:\DAA-Validation\case-001`；若该目录已存在，不进入或覆盖，改用从未使用的名称。在新父目录中通过「新建 → 文本文档」创建空文件，显示文件扩展名并将其命名为 `empty.env`，在属性中确认文件大小为 0 字节；若同名文件已存在则停止并选择新的父目录，不覆盖。此时**不要创建**下一级 `profile` 目录。选择这个从未存在的 `profile` 绝对路径供 DAA 初始化。DAA profile、模拟器 profile、默认目录及现有 `.local/dev` 必须各不相同；不覆盖任何现有配置、库、journal 或样本。现有 Mac/dev 的 31 条样本由 Owner 选择保留，不用于本次验证。不要复制或搬动旧 profile 来制造空环境。
4. 以下仅为本次 PowerShell 窗口设置示例；先把路径替换成已核对的本次专用绝对字面路径，且环境文件已存在、为空。若 `Test-Path` 为 `True`，不要继续，选择另一新路径；不删除原目录。进程中的非空 profile 值优先于所选环境文件，路径不会展开 `~` 或变量。

   ```powershell
   $env:DAA_ENV_FILE = 'C:\DAA-Validation\case-001\empty.env'
   $env:DAA_PROFILE_DIR = 'C:\DAA-Validation\case-001\profile'
   Test-Path -LiteralPath $env:DAA_PROFILE_DIR
   ```

5. 在包含精确候选的仓库根目录打开同一个 PowerShell，进入 DAA 目录；在确认依赖获取可用且端口 `15191` 不冲突后执行：

   ```powershell
   cd automation-world/data-acquisition-agent
   pnpm install --frozen-lockfile
   pnpm tauri dev
   ```

   启动后、配置或采集前，在此前不存在的专用 `<DAA_PROFILE_DIR>\local-acquisition-v1` 下，只读核对新生成的 `config.sqlite`、`runtime.sqlite` 是否存在；不打开数据库。用文本查看器只读检查该目录下 `logs\runtime.jsonl` 中本次启动时间对应的记录：`event=runtime_started`、`process=daa-local`、`resource=instance`、`result=stopped`，并记录其 `at`。结合启动前不存在的路径、当前 PowerShell 的 `DAA_PROFILE_DIR` 设置及本次启动时间核对；日志本身不含 profile 路径，单凭文件存在不能证明进程身份或独占。无法核清则停止并记阻塞。新目录产生自己的配置和历史；该事件记录的是启动时状态，后续以实际界面为准。检查工作台的两个「启动设置」开关均关闭并保持关闭，以便后续重开由操作者显式继续；保存配置本身不会启动连接、采集或上报。记录命令退出/报错及证据，不更改已有 `.env`。

## 三、逐项操作与记录

每项结果填写 **通过 / 失败 / 阻塞 / 未测**，附实际观察、样本及脱敏证据；未做不能填通过。步骤中的 `sampleId` 必须来自本次新 profile 的合成样本。

| 项目 | 操作与核对 | 结果与证据 |
| --- | --- | --- |
| 新 profile 与配置激活 | 按[手册第 2 节](USER_GUIDE.zh-CN.md#2-配置一台-plc-并检查本地样本)在独立模拟器和 DAA 中创建合成 PLC/DB/点位，保存草稿、激活，检查实际已生效配置；连接模拟端、短暂采集、暂停，在本地历史核对值、质量和采集时间。登记绑定前的本地记录不会自动进入上报队列。 | __________ |
| 同一 profile 独占锁 | 第一实例保持运行并使用已核对的专用 profile。在相同进程环境中启动**本次精确候选构建出的第二个 DAA 可执行文件**（通常在 `src-tauri/target/debug/`；若构建目录被显式改变，以本次构建输出为准）。确认第二进程实际尝试同一目录，预期被独占锁拒绝，第一实例仍正常；记录提示/日志并只关闭本次第二实例。不要把第二次 `pnpm tauri dev` 的 15191 端口冲突当作锁验证；无法证明进入同一 profile 的锁检查则记未测或阻塞。 | __________ |
| 正常关闭与重开 | 确认两个启动开关关闭，暂停采集和上报并正常关闭本次第一实例；在同一专用路径和环境重新运行 `pnpm tauri dev`。核对原配置和合成样本可读，采集及上报停态，再由操作者显式连接/启动。记录真实现象；这不是异常中断或热 journal 测试。 | __________ |
| 来源登记、上报与回执 | 按[手册第 3–4 节](USER_GUIDE.zh-CN.md#3-登记来源并配置上报)在隔离 Web 以 active admin 登记合成来源，把该 PLC 的三标识配置到 DAA，绑定后产生新样本。开始前核对确认框中的目标 URL、合同和全部来源；不能核清即取消。对选定样本检查冻结请求的身份和 `sampleId`，以及匹配 `contractVersion`、`instanceId`、`sampleId`、`status=committed`、`outcome=created` 或 `duplicate` 的回执；在 Web「采集数据 → 采集历史」以请求中的上报 PLC、DB 和时间找到同一 `sampleId`，对照值与质量。GET 或 HTTP 状态不能代替回执。 | __________ |
| 断网积压与恢复补传 | 只中断本次**隔离上报目标或本次专用代理**，不影响真实网络或其他服务；确认 DAA 仍从模拟端采集、合成样本留在本机并未被虚假确认。暂停采集，记录样本 ID、原身份、采集时间及已冻结时的正文/目标；恢复同一目标后显式继续，逐份核对原样本的匹配回执与 Web 历史。未冻结的待传项可能尚无正文/目标，不能猜测。 | __________ |
| 发送后、确认前退出 | 仅在隔离目标及受控故障工具能证明请求已发送、回执尚未被 DAA 持久确认时，按本次获准方案中断**本次 DAA 测试进程**；记录何时发送、屏蔽回执和退出，不将其推定为服务端提交成功或失败。保留原 profile、目标、身份、已冻结正文和队列；同一环境重开后检查未确认状态，核清同一目标再显式继续原样本，以匹配 `committed` 回执和 Web 同一 `sampleId` 核对。无法可靠控制或证明时间窗口时记未测，不以普通关闭冒充。 | __________ |
| SQLite 写入期间的热 journal | 与上一项分开。只有本次独立**合成 profile**、已授权故障方法及工具可证实 SQLite 正在写入且产生实际热 journal 时才执行；记录操作、可见文件、提示和结果。保全整个测试目录及 SQLite、journal、锁、sentinel、staging 和日志；不要手动删除、编辑、复制覆盖或伪造 journal，也不要用真实数据注入。超出现有已证恢复路径时保留原件并记录拒绝/阻塞。若该问题阻塞本轮必须的重开或补传，须修复并重测对应场景后才能进入该 Windows 项验收；无法证明故障条件则记未测。 | __________ |
| 页面与结束 | 检查本次实际界面中的采集/上报状态、队列、投递详情、本地历史和错误提示。完成后暂停本次采集及上报并断开本次模拟连接，停止本次专属进程；按证据计划保留受控资料，清理须核对资源归属及另行适用的授权。 | __________ |

## 四、结论留空

- 各项汇总、未测与阻塞原因：________________
- 实际候选及脱敏证据索引：________________
- 缺陷、保留目录及后续处理：________________
- 操作人 / 日期：________________

[DAA-014 手测转交](plans/DAA-014-unified-operator-guide/tasks.md#2-human-owner-手测转交)记录的是两次 Mac/dev 人工观察和保留 31 条样本，不是 Windows 证据。[DAA-010 r5 QA2](plans/DAA-010-sample-facts-upload/checklist.md#独立验证-qa2)的 `qa_failed` 与首次建目录期间替换问题仍以原记录为准；本表不会改变该状态、完整阶段 C 或实际环境采用的 gate。后续 Windows 结果由执行者如实记录，再交独立 Verification 和 Human Owner 按所属任务处理。
