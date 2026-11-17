Task ID: DAA-016
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: 精确 r1 工作树与 DEV self-check 交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-016 r1 Development 记录

## 1. 批准、起点与步骤

Human Owner 明确批准 [DAA-016 r1](spec.md)：“批准 DAA-016 r1，删除旧文件，接受旧历史链接失效，按规格补充 Windows 验证文档和采集指南英文版。不要过度设计。”批准登记后的 spec SHA-256 为 `cdad98c59302a36de25ff2044a22253c77c73d90c0c21459a790706105fc39b6`。正式交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，起始 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；共享树已有 DAA-015 和其他并行修改，HEAD 不代表工作树全部字节。

1. 删除前核对四个短页及 DAA-014 QA2 交接摘要，在本记录先保全原字节和历史定位，再删除这四个路径。
2. 在批准的 Markdown allowlist 新建 Windows 待验证记录单及中文指南的英文配对，最小调整现行导航。
3. 定向核对差异、历史/现行链接、两语与机器合同及代码块语法，记录实际结果后交 fresh-context Verification。

## 2. 历史引用及版本追溯

旧任务仍保留其原记录和锚点；四个短路径删除后，38 条历史直链在当前树会失效，这是 Human Owner 明确接受的影响。下表链接至可用原记录、固定版本、仓内快照或复原说明；从当前统一手册操作时不要把不同候选或短页的行号当成历史正文。Git 固定版本链接依赖相应 Git 对象；亦可在本地仓库运行 `git show <完整 commit>:<仓库相对路径>`，只读取原字节。

| 原记录与原引用 | 候选及可点击定位 |
| --- | --- |
| [DAA-007 r1 冻结规格](../DAA-007-ds-joint-validation-and-time-contract/evidence/r1-before-r2/spec.md)第 25 行的中英试行稿链接 `../../JOINT_TEST_GUIDE.zh-CN.md`、`../../JOINT_TEST_GUIDE.md` | 原相对路径按冻结前的规格所在目录解释，不按归档后的 `evidence/r1-before-r2` 目录解释。可定位的后续阶段 B 双语版本：固定 Git commit `fd999224a8756feda314a33148304b4bf3461876` 的[英文](https://github.com/jasonbu163/aiis-ics-arch/blob/fd999224a8756feda314a33148304b4bf3461876/automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md) / [中文](https://github.com/jasonbu163/aiis-ics-arch/blob/fd999224a8756feda314a33148304b4bf3461876/automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md)，SHA-256 分别 `d6735c83806cf00d812e5f6feb76da881a1c51d8f7b93b43b7ab2302eed63fd6` / `cbff953d1b64717caf76bc6052eba062dbfe6db9117f2b07d039eb9673df149c`。该后续版本不冒称早期试行稿；试行稿全文与原摘要尚未核对，未声称可恢复。范围见 [DAA-007 接受记录](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)。 |
| [DAA-008 B-RUN-01](../DAA-008-reliable-facts-upload/tasks.md#L632) `#m01-launch`、中文 `#m01新配置及来源交接`；[DAA-011 核验](../DAA-011-dev-manual-refresh/checklist.md) `#L5`、`#L82`、`#L86` | DAA-008 r4 依 [DAA-014 双语恢复步骤](../DAA-014-unified-operator-guide/tasks.md#daa-008-原文重建)取得英文 SHA `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a`、中文 SHA `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769`。DAA-011 QA2 固定 Git 版本：[英文](https://github.com/jasonbu163/aiis-ics-arch/blob/fd999224a8756feda314a33148304b4bf3461876/automation-world/data-acquisition-agent/STAGE_C_GUIDE.md) SHA `9df1cd0a8b08372caad39d4b9ae5e62f68490864850b17a7801a314e13a2fe84`、[中文](https://github.com/jasonbu163/aiis-ics-arch/blob/fd999224a8756feda314a33148304b4bf3461876/automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md) SHA `892b83f79cd0f8e24f7751e802f1567d697cc4f244c23b4a977f5b720b9ad95c`；[DAA-011 QA2](../DAA-011-dev-manual-refresh/checklist.md#daa-011-r1-独立文档复验--qa2)曾记录依据第 5、82、86 行逆向重建并匹配 QA1 当时的摘要：[英文 QA1](../DAA-011-dev-manual-refresh/checklist.md#候选与环境) `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58` / 中文 QA1 `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065`。本次未在所引记录找到所有三行的完整原字节，未独立确认这两份 QA1 全文当前可恢复；保留当时核验观察，不用 QA2 冒充 QA1。以上为首次 Development 自检观察；此后 [DAA-016 QA1 原文复核](checklist.md#历史原文复核)列出双语第 5、82、86 行的完整逆向替换，本次返工按该表从固定 Git 的 QA2 字节恢复两份 QA1，并匹配上述各自摘要，具体见 §6。 [DAA-014 §3](../DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯) |
| [DAA-010 核验](../DAA-010-sample-facts-upload/checklist.md)三条旧引用：中文 `#L40`、`#L97` 与中文第 6 节 | r5 暂停候选的[原始双语摘要](../DAA-010-sample-facts-upload/tasks.md#L246)分别为英文 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a`、中文 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`。从 QA5 快照分别按 [中文差异](../DAA-014-unified-operator-guide/tasks.md#daa-010-r5-中文原文重建)和 [英文差异](../DAA-014-unified-operator-guide/tasks.md#6-qa1-返工与英文历史原文)重建，并匹配原摘要。中文原文第 40 行是分终端启动说明，第 97 行是“7. 暂停、目标变更与恢复”；英文 M01 显式锚点为原文第 105 行。这些行不是后续现行手册对应行。其余复验候选须沿原任务精确交接及摘要辨别，未确认的版本不冒称可恢复。 |
| [DAA-013 核验](../DAA-013-multi-plc-reporting-identity/checklist.md)英文 `#L102`、双语 `#6-register-sources-and-start-delivery` / `#6-登记来源并开始上报`；[ARCH-ACQ-004 核验](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md)对应双语第 6 节及全文 | QA4 英文为失败候选：从 [DAA-013 QA5 英文快照](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md)依 [QA4 逆向说明](../DAA-014-unified-operator-guide/tasks.md#daa-013-qa4-英文原文重建)恢复 SHA `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea`。QA5 的[英文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md) / [中文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md)分别为 `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235` / `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73`。它们与 QA4 英文不是同一版本。 |
| 尚未核对全文的过渡候选 | [ARCH-ACQ-004 r4 首轮 QA](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa1)记录双语当时观察及摘要；该任务 r2 QA6/QA7 的其他候选见同一 [checklist](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md)和[交接](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/tasks.md)。DAA-013 更早候选见其[交接](../DAA-013-multi-plc-reporting-identity/tasks.md)。只记录观察及原 SHA，尚未核对完整原文与摘要，不能声称可恢复；找到材料后应先对照其各自原 SHA。 |
| DAA-014 四份冻结证据 | [QA5 英文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md)、[QA5 中文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md)、[实施前英文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.md)、[实施前中文](../DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.zh-CN.md)保持原字节，其内部相对链接按原 `automation-world/data-acquisition-agent/` 目录解释。实施前双语快照 SHA 分别为 `5b40fad53bb68a4c4014c70ffa4eab1c7867425cb051536424ce62c3e5b80cb6` / `fec92516e5b83023568a60bcc40992ab25510446c207f55eaeac37d7e5a03c22`，不是其他历史候选的替身。 |

## 3. 删除前四份短页的原文

下列 fenced block 内内容从对应删除前文件按 UTF-8 原字节复制，包含每个文件末尾 LF；标题和 fence 不属于原文件。删除前逐项计算 SHA-256，与 [DAA-014 QA2 返工后的交接清单](../DAA-014-unified-operator-guide/tasks.md#返工后的精确交接清单)的四项 4/4 相同；[QA2 AC03](../DAA-014-unified-operator-guide/checklist.md#daa-014-r1-独立文档复验--qa2)记录独立核验。恢复时仅取相应 fence 内原文字节，核对 SHA，勿用这些短页代替历史长文。

### `STAGE_C_GUIDE.md`

SHA-256：`58fa3f4c7366a0316ef44ac8930d4099cd770fd2e89a1a201ff4d4099354331e`

```markdown
# Former Stage C entry

For everyday operation, use the [DAA user guide](USER_GUIDE.md).

This path was `STAGE_C_GUIDE.md`. Former run instructions are historical material, not the current procedure. See [DAA-014 historical trace](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯) for exact snapshots, Git versions, hashes and reconstruction of the DAA-008 originals.

## 6. Register sources and start delivery

This procedure is now in [Register the source and configure reporting](USER_GUIDE.md#3-register-the-source-and-configure-reporting). The [exact DAA-013 QA5 text](plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md) is historical verification material and does not imply current deployment adoption.

<a id="m01-launch"></a>
See the [DAA-014 historical trace](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯) and [DAA-008 run record](plans/DAA-008-reliable-facts-upload/tasks.md#L632) for B-RUN-01 M01 and the exact original version.

<a id="L5"></a><a id="L82"></a><a id="L86"></a><a id="L102"></a>
Line references in earlier records identify their respective versions; the [historical trace table](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯) distinguishes DAA-011, DAA-010 and DAA-013. This page's current line numbers are not the original text.
```

### `STAGE_C_GUIDE.zh-CN.md`

SHA-256：`9e9cf35fe511c5de86ba8a49e79be5d257f9aa887bec31b329ef1e77056169c9`

```markdown
# 阶段 C 旧入口

日常操作请使用 [DAA 使用手册](USER_GUIDE.zh-CN.md)。

本路径原名 `STAGE_C_GUIDE.zh-CN.md`。旧版本的运行说明仅供历史追溯，不是现行操作。原文快照、固定 Git 版本、摘要和 DAA-008 原文复现方法见 [DAA-014 历史追溯](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)。

## 6. 登记来源并开始上报

本节操作已整理到[登记来源并配置上报](USER_GUIDE.zh-CN.md#3-登记来源并配置上报)。[DAA-013 QA5 精确原文](plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md)用于追溯历史核验，不代表现行部署已采用。

<a id="m01-launch"></a>
<a id="m01新配置及来源交接"></a>
DAA-008 B-RUN-01 的 M01 历史与精确原文定位见 [DAA-014 历史追溯](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)和 [DAA-008 运行记录](plans/DAA-008-reliable-facts-upload/tasks.md#L632)。

<a id="L5"></a><a id="L40"></a><a id="L82"></a><a id="L86"></a><a id="L97"></a>
旧记录引用的行号属于各自当时的版本；[历史追溯表](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)区分 DAA-011、DAA-010 与 DAA-013。不得用本页或不同版本的当前行号代替原文。
```

### `JOINT_TEST_GUIDE.md`

SHA-256：`8e513160afbcb17ccce378359526b06cc36dff457951a0376cae35b8314dc416`

```markdown
# Former Stage B entry

For everyday operation, use the [DAA user guide](USER_GUIDE.md).

This path was `JOINT_TEST_GUIDE.md` for the DAA-007 controlled DS joint test. Its original bytes are fixed at Git commit `fd999224a8756feda314a33148304b4bf3461876` and are historical material, not the current procedure. See [DAA-014 historical trace](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯) for retrieval, SHA and acceptance links. The [DAA-007 acceptance record](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) retains the original scope and limits.
```

### `JOINT_TEST_GUIDE.zh-CN.md`

SHA-256：`eb287750a872157782cfd4db73fe1bdf05a0b597323448e6fbb808ca73ec40e8`

```markdown
# 阶段 B 旧入口

日常操作请使用 [DAA 使用手册](USER_GUIDE.zh-CN.md)。

本页原为 `JOINT_TEST_GUIDE.zh-CN.md`，对应 DAA-007 受控 DS 联调。原文固定于 Git commit `fd999224a8756feda314a33148304b4bf3461876`，不作为现行操作流程；查看方式、原文 SHA 与验收入口见 [DAA-014 历史追溯](plans/DAA-014-unified-operator-guide/tasks.md#3-旧指南历史追溯)。[DAA-007 验收记录](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)保留原范围与限制。
```

## 4. Development self-check

本节为 Development 自检，不是独立 QA 或 Human Owner 最终验收。核对依据包括 [DAA-014 QA2](../DAA-014-unified-operator-guide/checklist.md#daa-014-r1-独立文档复验--qa2)、[DAA-010 AC08 和 §7](../DAA-010-sample-facts-upload/spec.md#5-验收标准)、现行双语手册、[v2 合同](../../../../contracts/published/http-api/plc-facts-v2/README.md)、r4 数据和管理 OpenAPI、实际 Web 中英 locale 及来源管理依赖。

| 实际命令或方法 | 结果 |
| --- | --- |
| `shasum -a 256 automation-world/data-acquisition-agent/plans/DAA-016-docs-closeout/spec.md`；`git rev-parse HEAD`；`git status --short` | exit 0；批准后 spec 为 `cdad98c59302a36de25ff2044a22253c77c73d90c0c21459a790706105fc39b6`，正式共享树 HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`，并行任务 dirty 状态保留。 |
| `shasum -a 256 automation-world/data-acquisition-agent/{STAGE_C_GUIDE.md,STAGE_C_GUIDE.zh-CN.md,JOINT_TEST_GUIDE.md,JOINT_TEST_GUIDE.zh-CN.md}`；`python3 -` 从本文件 fenced block 提取字节 | 删除前 exit 0，四项摘要均与 DAA-014 QA2 交接清单相同，fenced 原文逐字节等于原短页。删除后再与 `git show 21cd789277695bbafaa55c24e39261fc7247f9b0:<原路径>` 逐字节对照，四条路径不存在且原字节、摘要 4/4 一致。 |
| `python3 -` 在内存读取 `git show fd999224a8756feda314a33148304b4bf3461876:<原路径>`、四份 DAA-014 快照和任务内差异；逐 hunk 核对原行和行数后重建 | exit 0。阶段 B 双语、DAA-011 QA2 双语及四份快照均匹配 §2 摘要；DAA-008 双语重建为 23039 / 20583 字节并匹配原摘要；DAA-013 QA4 英文匹配 `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea`。DAA-010 r5 中文 30728 字节、英文 34534 字节，均与 [原暂停清单](../DAA-010-sample-facts-upload/tasks.md#L246) SHA 匹配；中文原 L40/L97 和英文 M01 在原重建内容定位。无文件输出。DAA-011 QA1 及其他未确认全文的缺口见 §2。 |
| `python3 -` 统计历史任务 Markdown 指向 `STAGE_C_GUIDE` 的链接；`rg --files --hidden -g '*.md' -g '!.git' -g '!node_modules' -g '!target' -g '!dist'` 配合 Python 扫描 | exit 0。DAA-008/011 共 20、DAA-010 3、DAA-013 3、ARCH-ACQ-004 12，即批准例外的 38 条；另有 DAA-007 冻结 r1 的两条按原目录解释的相对引用、四份快照内部的语言互链，以及本表指向固定 Git 版本的链接。现行非历史文档及 DAA-015 记录未发现旧路径依赖。 |
| `python3 -` 扫描本任务新文档、任务追溯表和触达入口的本地相对路径、标题及显式锚点 | 最终 exit 0；初次修正后 9 份文档共 141 处本地链接/锚点、0 缺失；追加交接后再次检查为 145 处、0 缺失，6 个外部链接未由本角色访问。初次扫描发现本任务表内 1 个 QA1 标题锚点有误，修正后重跑通过。根 PLAN 的英文指南入口也逐项确认存在。 |
| `python3 -` 对照中英八节、请求/回执 JSON，逐块送 `/bin/zsh -n`，解析两份 r4 OpenAPI 并核对 Web locale；读取后端来源管理依赖 | exit 0。两语各 8 节、两份 JSON 请求和回执逐项一致且身份匹配；两语各两个相同 Bash 代码块通过语法解析，未执行。数据 OpenAPI 为 1 POST + 5 GET 且无 Bearer，管理 OpenAPI 的 GET/POST/PATCH 要求 HTTPBearer；源码 `get_current_active_admin` 与 Web 中英页面、复制按钮标签相符。数据 OpenAPI SHA `7c87f409caf704f02e2d018e2c1c9a37e9e8803febbcd98b6bd61db13495f13f`，管理 OpenAPI SHA `be7e8243f9217ce1a5edf9b8741d2a3dde826e8a404f6fbfa733a8494a1c0e51`。逐节人工核对流程、字段、时间、来源接管/删除、事实表、示例、可靠回执、错误和读取语义。 |
| `git diff --check -- PLAN.md docs/README.md docs/README.zh-CN.md docs/acquisition-data-guide.zh-CN.md automation-world/data-acquisition-agent/README.md automation-world/data-acquisition-agent/README.zh-CN.md automation-world/data-acquisition-agent/USER_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md`；`python3 -` 检查新文件行尾、末尾换行及 fence | exit 0。以 `git show HEAD:<路径>` 与精确文本替换对照 6 份已跟踪文档，均只有获批的链接、入口或中文语言/锚点改动；根 PLAN 的采集数据行只改获批英文指南链接，其他并行行保留。新文件为未跟踪文件，单独检查行尾和 fence。 |
| `command -v pwsh`、`python3 --version`、`/bin/zsh --version` | 本机 Python 3.9.6、zsh 5.9；未发现 `pwsh`。Windows 两个 PowerShell 代码块仅人工核对字面路径、引号和命令形式，未作 PowerShell 解析，更未执行。协调者另转交其只读核对 [Tauri Windows 前置条件](https://v2.tauri.app/start/prerequisites/#windows)的结果：C++ Build Tools 与 WebView2 需可用、Windows 10 1803 及以后通常已有 WebView2；本角色未发出 HTTP。 |
| `git status --short -- <DAA-007/008/010/011/013/014、ARCH-ACQ-004 历史 bundle>` | exit 0，目标历史 bundle 无工作树改动；四份 DAA-014 快照摘要亦与 §2 一致。 |

过程记录：最初读取本 bundle 的 `cat spec.md tasks.md` 因当时 `tasks.md` 尚不存在而 exit 1，spec 已完整读取；首次 Python 导航替换脚本在最后一个英文合同锚点遇到 2 处而断言 exit 1，前 7 个文件的预期替换已写入，之后显式修正两处并以定向差异及链接扫描复核。一次内存归档复核脚本因 Python bytes 字面量包含中文冒号而 `SyntaxError`、exit 1；改为 UTF-8 编码后重跑 exit 0。一次只读 `python3 -` 使用 `Path.rglob` 全仓盘点超出短等待返回运行状态时未保留会话 ID；随后 `ps -axo pid,command` 被环境以 `operation not permitted` 拒绝，无法复查该次进程。该脚本以仓根为工作目录、使用 `python3 -`，只读；后续使用上述有界 `rg --files` 方法成功完成盘点。协调者另转交只读命令 `lsof -a -u jason -c python3 -d cwd -Fpcn` exit 0 的观察：当时未见 cwd 为仓根的 python3，但这不是按 PID 确认该脚本退出。未为这些检查创建临时证据文件。

限制：没有启动、构建或测试 DAA，也没有运行 Windows、HTTP、服务、数据库/SQLite、模拟器或设备；未读取或修改真实 `.env`、profile、31 条样本及历史。记录单的故障条件需要后续受控工具和批准，不能把普通关闭当作发送未确认退出或热 journal。浏览器渲染、PowerShell 实机和远端固定 Git 链接可访问性没有在本角色验证；本地 Git 对象及仓内材料已核对。

## 5. 精确交付与 developer_handoff

交付对象为正式共享工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 加下列工作树文件；不是 commit。`PLAN.md` 是并行共享文件，其整文件摘要含其他任务现有改动，本任务只拥有采集指南链接替换。

```text
be7556f41182e5607d2ec95920267dd8bab87d31dd309024ad42285f59ac9810  PLAN.md
fae2a57f10772618413e4e761f75152c95453d90d572f4a39fb244d952b37dcb  docs/README.md
77c08d3849ea6ec397390d976433893b7e9930164eaddd4f58ca0d9b2889eb4a  docs/README.zh-CN.md
4bb1c803b16516cab3b12294b3303d5862f67b21a60a1720f8f914a16a6a6969  docs/acquisition-data-guide.md
6ba3b09ace3cfd0156c8027d8aa353eab11e516211daa4c269bb655ad4d74943  docs/acquisition-data-guide.zh-CN.md
7e5afaff2a7c52eaa5e3a5e326955d0622aa916cf5818dcab025a714b0d233e5  automation-world/data-acquisition-agent/README.md
0fe32f151769f66bccf47de0b7df15b992e858be18e917077520c520c4b8f443  automation-world/data-acquisition-agent/README.zh-CN.md
92861b37c492e7eb57eebb5b23aafa4ac6dbe654df1fca9c1175ca303ed5d5eb  automation-world/data-acquisition-agent/USER_GUIDE.md
9bf5573bb97af99c02139c11ea7e3aac91dc3b5466706e8d83d15fd0fc0fe1f5  automation-world/data-acquisition-agent/WINDOWS_NATIVE_VALIDATION.zh-CN.md
```

本任务 `tasks.md` 作为交接记录本身，最终 SHA-256 在交接时单独计算，避免自引用。四个删除路径与删除前 SHA-256 见 §3；它们的原字节已嵌入本记录。spec 未修改，checklist 尚待独立 Verification 创建；DAA 的四个 PLAN/目录状态行由协调者按真实状态同步。没有创建分支、worktree、运行环境或测试产物。

**developer_handoff**：请协调者把 DAA-016 r1 的精确 spec、上述正式共享树/摘要及删除清单、完整本任务 bundle、§2 历史追溯、§4 自检与限制交给新的 fresh-context Verification，独立检查 AC01–AC04、完整 diff、两语及合同对照、Windows 记录单的可操作性和历史可恢复范围。此交接不表示独立 QA 通过、Windows 实测、Human Owner 终验、阶段 C 完成或实际环境采用。

## 6. QA1 返工与 developer_handoff

fresh-context [DAA-016 QA1](checklist.md)记录 `qa_failed`，checklist 返工前 SHA-256 `75b2acff8f623c10f443d11e5ae3f48d2ef002be6baec1691efd6e96bd4ea3cd`。其中 F-DAA016-QA1-001 指出普通入口不会输出记录单所要求的 `data_acquisition_agent_started.profile_directory`。上述 §4–5 为首次自检及当时交接，保留原观察和原摘要；其“checklist 尚待创建”只描述当时，当前以本节及 QA1 原记录为准。

本次仍在获批 r1 和同一正式共享树、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 返工，仅修改 Windows 记录单的目录证据填写栏及启动后核对段，并在 §2 补注 QA1 的 DAA-011 双语恢复证据。对照 `local_supervisor.rs`、`local_store/mod.rs`、`local_logging.rs`：普通入口在所选 profile 的 `local-acquisition-v1` 中打开双库，向该目录的 `logs/runtime.jsonl` 写入 `runtime_started` / `instance` / `stopped`。记录单现在要求结合此前不存在的专用目录、进程设置和本次启动时间，只读核对两个 SQLite 文件存在和对应日志；日志不携带 profile 路径，文件存在不单独证明进程身份或独占，无法核清则停止。Windows 和故障情景仍待实测。

QA1 在 [历史原文复核](checklist.md#历史原文复核)列出从固定 Git `fd999224a8756feda314a33148304b4bf3461876` 的 DAA-011 QA2 中英原字节，分别替换第 5、82、86 行片段的方法。返工时 `python3 -` 在内存逐行应用该表并核对行内唯一匹配，英文恢复 31493 字节、SHA-256 `f6a6b6cc398e78f6fa153879ded9c5a3e1d68cdddad31335cbcfc880fc696b58`，中文恢复 28265 字节、SHA-256 `fcee309f51f80a0d1a6c02172c084ce62ae04cea60ae373bcb15bafbbe46c065`，均匹配 DAA-011 原 QA1 清单；exit 0，无临时文件。§2 和 §4 保留首次自检未确认的历史事实。

本轮定向自检：

- `shasum -a 256 <spec tasks checklist Windows 记录单>`，exit 0，输入的 spec、前次 tasks、QA1 checklist 和 Windows 记录单分别匹配前次精确摘要。
- `python3 -` 对 Windows 文本逆向还原改动，重算前次 SHA；对 tasks 移除 §2 的追加说明、重算前次 SHA：exit 0，证明在追加本节前只改了上述两个 Windows 段和 §2 补注。该检查首次误把补注删除时原有的空格也删除，断言 exit 1；改为恢复原空格后重跑通过。
- `python3 -` 静态核对记录单中的 `local-acquisition-v1`、双库文件、日志文件、事件字段和无法核实时停止的文字；扫描 Windows 文档及 tasks 的相对链接/锚点、行尾与 fence：exit 0，41 个本地链接目标均存在。未执行文档代码块。

本轮不构建或运行应用、Windows、PowerShell、服务、HTTP、数据库/SQLite 或设备；不访问真实配置、profile 或 31 条样本。日志和路径核对仅为静态文档修正，实际 Windows 结果留待后续验证。未修改 spec、checklist、源码或协调者负责的四个 DAA 索引，也不把并行工作纳入本次差异。

**返工精确交付：** `WINDOWS_NATIVE_VALIDATION.zh-CN.md` 新 SHA-256 为 `18c390be426e34373a879c96a21a80282c3889055d56d6c9c77c04c6177962b6`；其余八项交付文档沿用 §5 原摘要；四个删除路径及原字节继续见 §3。批准 spec SHA-256 为 `cdad98c59302a36de25ff2044a22253c77c73d90c0c21459a790706105fc39b6`；本 `tasks.md` 的最终 SHA 在交接时单独计算。

**developer_handoff**：请协调者将 DAA-016 r1、上述正式工作树及精确摘要、完整 bundle、QA1 原发现、此次最小差异、自检与限制交给新的 fresh-context Verification。请求独立复验，不表示 QA 已通过、Windows 已实测或 Human Owner 已最终验收。
