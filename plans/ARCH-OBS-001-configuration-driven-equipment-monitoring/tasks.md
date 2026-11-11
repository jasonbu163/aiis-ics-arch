Task ID: ARCH-OBS-001
Revision: r7
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r7 isolated source candidate to fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

以下 r6 D-06 及更早 Development 记录作为完整历史原字节保存。r7 交接正文保持原文，其中“前 23232 字节”的恢复说明对应本次修正前的文件布局；现在应提取以下两个 history 标记之间的全部字节，再按原 SHA-256 核对。此更正仅调整任务文档的顶层元数据和历史封装。

<details>
<summary>r6 D-06 及更早完整 Development 历史（23232 字节）</summary>

<!-- ARCH-OBS-001-r6-history-begin -->
Task ID: ARCH-OBS-001
Revision: r6
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: D-06 working-tree candidate to fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# D-06 第三方与 SMA 接入说明

2026-11-11（Asia/Shanghai）。按 [r6 §7.4 D-06 文档范围](spec.md#r6-d-06-第三方与-sma-接入说明)对读并更新中英文讨论稿。软件方案仍处于 `draft`。

## D-06 实施与 DEV 自检

两稿补充第三方每次必传的来源事件、采样时任务号、原采集时间及指标值，区分后端从接入配置补齐的字段、固定设备组的省略条件、实时和历史质量规则、显式 `null` 与缺测指标，以及来源事件和目标投递事件在重试时的不同作用。两稿说明 SMA 固定配置需由程序每次发送完整信封，GET 需要的集成身份和精确设备／组／目标准入、历史白名单及其与业务读权限的区别，并各自链接规格的字段规则、发现示例和两份第三方最简 JSON。

| 检查或命令 | 实际结果 |
| --- | --- |
| 内联 `python3` 对照 r6 规格与中英文稿，检查本地链接、标题与显式锚点、字段标识、原链接与 Mermaid | 退出 0。两稿各 39 个链接，合计 78 个本地链接解析成功；两个原 Mermaid 源码、原阅读锚点和所有原链接保留。两稿各自链接第三方字段规则、实时与历史最简示例、GET 示例。 |
| 内联 `python3` 解析规格 JSON 并检查两份第三方示例 | 退出 0。11 段 JSON 均可解析，原 9 段逐字节保留；两份新例的来源事件、任务号、原采集时间和指标一致，历史显式带 `quality: good`，实时省略质量。 |
| `git diff --no-index --check -- <编辑前讨论稿> <当前讨论稿>`（两稿各执行一次） | 两次均退出 1，表示存在内容差异；输出为空，未发现空白错误。 |
| `shasum -a 256`、内联 `python3` 字节比对 | 退出 0。规格摘要与 PM 交接一致，原 `checklist.md` 与编辑前字节一致。 |
| 内联 `python3` 移除本节并还原旧交接元数据 | 退出 0。恢复的 `tasks.md` 与 D-05 编辑前副本逐字节相同，旧交接及更早记录保留。 |
| `git diff --no-index --check -- <编辑前 tasks> <当前 tasks>` | 退出 1，表示存在内容差异；输出为空，未发现空白错误。 |

## D-06 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。本轮 Development 修改双语讨论稿和本记录，候选为当前工作树，规格为 PM 所有。下表摘要通过 `shasum -a 256` 核对。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `ea288e72715f4e29f6ec0f30431954935f23e3b1990538fc5624aa6eae32f25a` |
| `docs/equipment-status-process-monitoring.md` | `ac7970c856038a9cc289a167da714ca287d92c93ebeb5c5a0d951553185ac799` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `0b005b6b1077187438518830c4d4fea44eb5a8df3d8ace0c4dda6fcd807ec194` |

由主协调会话启动 fresh-context Verification。DEV 检查仅覆盖静态文档、JSON 和链接，未运行渲染、API、数据库或现场验证。本任务未修改代码或执行外部操作。既有通用任务讨论稿是本地链接依赖；协调者管理 `/private/tmp/aiis-arch-obs-001-r6-d06-yemwinwu` 编辑前对照，留给独立核验，核验后按其资源生命周期处理，Development 未另建临时资源。

## 历史 Development 记录（r6 D-05 及更早修订）

# D-05 完整方案审阅稿

2026-11-09（Asia/Shanghai）。交接范围为 [r6 §7.4 D-05 文档授权](spec.md#r6-d-05-完整方案审阅稿)。软件设计仍处于 `draft`。

## 实施与 DEV 自检（D-05）

按 D05-AC01 至 D05-AC04 对读双语稿与规格。两稿说明共用指标登记、两张值表的固定列、每目标每组的槽位和类型保留、卷号字符串、按任务查询历史及发现、写入、读取和管理接口。炉区 1 同源样本串起 `01/02/03` 与 `07/08` 的落库差异，表定义和完整请求与响应由规格维护。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 核对相对路径、标题、显式锚点、两稿的规格引用、页面预设及 `json.loads` 落库片段 | 退出 0。每稿 33 个链接，6 个旧阅读锚点和 2 个新锚点，4 页卡片、3 页历史预设和 6 条 Mermaid 连线。两路槽位及原类型值对应。 |
| 内联 `python3` 核对规格授权段及 `json.loads` | 退出 0。D-01 至 D-04 历史授权和验收正文匹配 r5 基线。9 段 JSON 可解析，发现结果、任务和卷号 `000042`、两路事件、同源任务与采集时间及字符串回执记录号通过比对。 |
| `git diff --binary HEAD -- . <文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` 比对协调者基线摘要 | 退出 0。六份索引、checklist、范围外跟踪差异和 6 个既有未跟踪文件匹配基线。 |
| `git diff --no-index --check -- "$before" "$after"`（双语指南和本记录）、`git diff --cached --quiet` | 空白检查均退出 1，表示有内容差异，输出为空。暂存区检查退出 0。 |
| 内联 `python3` 恢复下方 r5 元数据并比较原 `tasks.md` | 退出 0。旧正文及历史交接标题逐字节保留。去除 r5 元数据的引用前缀后，恢复摘要为 `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7`。 |

## D-05 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。交接对象为工作树的双语稿和本记录，按 `shasum -a 256` 核对以下规格及指南。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `b7ffda29b0ecb1631998ecff7611e54a76e5f88dcfcd0b2e368d23e7a7206512` |
| `docs/equipment-status-process-monitoring.md` | `c1af519d2eb5846fa9d70fea89002f116d77478a8e8393124729a40a228af2c7` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `4154d8df6cc66b6fc87a1017bd114c504199253b3bb83e1f49b9b5dd9c3686a7` |

由主协调会话启动 fresh-context Verification。DEV 检查为静态文档、样例及工作树对照，未运行渲染、API、数据库或现场验证。两份通用任务讨论稿是既有本地链接依赖。编辑前对照由协调者留至独立核验结束，Development 未另建临时资源。

## 历史 Development 记录（r5 D-04 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r5
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-04 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-04 从零开始的总体方案讨论稿

2026-11-09（Asia/Shanghai）。本交接限于 [r5 §7.4 D-04 文档范围](spec.md#r5-d-04-从零开始的总体方案讨论稿)，软件方案仍处于 `draft`。

## 实施与 DEV 自检（D-04）

双语指南按 D04-AC01 至 D04-AC04 对读。首版从项目配置和空库开始，以合成炉区 1 样本串起四页卡片、三页历史曲线、任务归属、SMA 两路和管理列表。首次现场启用按真实产线范围另行批准。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 核对两稿的相对链接、标题与显式锚点、预设表行和 Mermaid 源码 | 退出 0。两稿各 25 个链接、6 个既有阅读锚点、4 个设备状态预设、3 个历史页预设及 6 条 Mermaid 连线。两稿规格链接对应，接口路径和 JSON 由规格维护。 |
| 内联 `python3` 对照 r4 授权段与 `json.loads` | 退出 0。D-01 至 D-03 授权段正文匹配 r4 对照。6 段 JSON 均可解析，两路共用写入格式、来源任务、采集时间和映射，投递身份各自独立，加热就绪只进入实时。 |
| `git diff --binary HEAD -- . <文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` SHA-256 比对 | 退出 0。六份索引、checklist、范围外跟踪差异及 6 个既有未跟踪文件匹配协调者基线。 |
| `git diff --no-index --check -- "$before" "$after"`（双语指南及本记录），`git diff --cached --quiet` | 空白检查各退出 1，表示有内容差异，输出为空。暂存区检查退出 0。 |
| 内联 `python3` 恢复下方 r4 元数据引用并比较旧 `tasks.md` | 退出 0。原正文逐字节保留。去除 r4 元数据的引用前缀后，摘要匹配 r4 原记录 `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d`。 |

## D-04 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。候选为工作树中的双语指南及本 `tasks.md`。下列摘要通过 `shasum -a 256` 核对。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `cc1a481afc4b250e04e4daa33fcb6a29ae56531093fb9bb2d79e5a2fad295bf6` |
| `docs/equipment-status-process-monitoring.md` | `6b5ad2a36f60cc2ed7b7816c74aa0378d2be4daf4374a127a039014aa2ffe88d` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `2e6723a2e1ccf9e461654dfdbce053f038aa1e7310c6e590cd3e642d0d5a8e8e` |

由主协调会话启动 fresh-context Verification。DEV 自检限于静态文档、JSON 示例及工作树差异，未实测 Mermaid 渲染、软件运行或现场。两份既有通用任务讨论稿是本地链接依赖。编辑前对照由协调者留至独立核验结束，Development 未另建临时资源。

## 历史 Development 记录（r4 D-03 及 r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r4
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-03 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-03 任务归属和管理列表讨论稿

2026-11-09（Asia/Shanghai）。本交接限于 [r4 §7.4 D-03 文档范围](spec.md#r4-d-03-任务归属和管理列表讨论稿)，软件方案仍处于 `draft`。

## 实施与 DEV 自检（D-03）

两份指南更新至 r4。对照 D03-AC01 至 D03-AC04，核对了按原任务归属的采样与换单空态、SMA 一次映射和两路投递、管理员列表及备注和标记权限。两稿保留指标类型、单位、时区和历史留存规则。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 检查相对路径、显式及标题锚点、双语规格链接、关键字段、历史授权及 `json.loads` | 退出 0。两稿各 23 个链接，共 46 个目标解析成功，既有阅读锚点保留。规格六段 JSON 可解析，两路写入示例任务号、原采集时间和映射一致，投递身份各自独立，两路均有采样任务号点位证据。D-01 和 D-02 授权段正文匹配 r3 对照。 |
| `git diff --no-index --stat` 与 `git diff --no-index --check`（当前文件与编辑前快照比较） | 每稿各 34 行新增、18 行删除。两稿及本记录的空白检查均退出 1，表示存在内容差异，输出为空。 |
| `cmp` 对照根 PLAN、双语 docs 索引、双语 plans 目录和 checklist 编辑前字节，`git diff --cached --quiet` | 均退出 0。 |
| 内联 `python3` 解开下方历史元数据引用，比较旧 `tasks.md` 字节 | 退出 0。恢复后 SHA-256 为 `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e`，原 r3 Development 正文逐字节保留。 |

## D-03 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。候选是工作树中的两稿及本 `tasks.md`，依据下列 PM 规格。用 `shasum -a 256` 核对摘要。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `5e8e9d7ffe670187afb142f5665525810313b69484384324a82df23832c0a8e3` |
| `docs/equipment-status-process-monitoring.md` | `5f9d498808d9589ef1a6d4785f78da8636cf28baae9276ee02a0a14490733e2a` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `fcd73dd295dc555170d0d855895478b8db40ec1a837c78f629c9b616ce4d0a47` |

由主协调会话启动 fresh-context Verification。自检限于静态文档和工作树，软件运行和 Mermaid 渲染未实测。编辑前对照由主协调会话保管至独立核验结束，Development 未另建临时资源。两份通用任务讨论稿是既有的本地链接依赖。

## 历史 Development 记录（r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r3
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-01 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-01 设备状态与过程监控讨论稿

2026-11-07（Asia/Shanghai）。范围与批准见 [r3 §7.4](spec.md#74-长期阅读指南)，自检对应 D01-AC01 至 D01-AC04。r3 软件设计仍处于 `draft`，软件实施及现场采用分别审批。

## 实施记录

| 验收项 | D-01 交付 |
| --- | --- |
| D01-AC01 | 新建[中文讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md)与[英文讨论稿](../../docs/equipment-status-process-monitoring.md)。两稿互链，分别链接本规格，在[中文索引](../../docs/README.zh-CN.md)与[英文索引](../../docs/README.md)各增加一行。 |
| D01-AC02 | 用同一炉区的实测温度和设定温度说明指标登记、四页共用卡片、每卡 10 个启用指标上限、逐项新鲜度和独立曲线配置。 |
| D01-AC03 | 两稿用简图和正文走读 DAA 事实、SMA 标量映射、实时覆盖、历史追加和两路回执。历史白名单、选样间隔和持久留存各归采样与存储，曲线组负责展示。 |
| D01-AC04 | 具体接口、字段及 JSON 示例链接 r3。本文件记录 D-01 交接。 |

## DEV self-check

在交付工作树根目录执行。环境为 macOS 15.7.7、Python 3.9.6 和 Apple Git 2.50.1。

| 命令或核对方式 | 实际结果 |
| --- | --- |
| 逐节对读中英两稿及 r3 §2–§5、§7 | 五个主题、步骤与图示对应。炉区两标量、管理员配置、10 项上限、逐项采集时间、缺测、`0` 与 `false`、曲线缺口、独立投递和留存均已对照。 |
| 下方 `python3` 静态检查 | 退出 0。每稿 19 个本地链接，含 5 个阅读锚点。每个索引新增行有 2 个链接，总计 42 个目标解析成功。移除新增行后，两份索引各自匹配编辑前 SHA-256。初次运行把总数预设为 40，核对实际 42 个链接后更正检查计数。 |
| `git diff --check -- docs/README.md docs/README.zh-CN.md` | 退出 0。 |
| `git diff --no-index --check -- /dev/null "$guide"`（两篇新稿各运行一次） | 均退出 1，表示相对空文件存在差异。两次均无空白错误输出。 |
| 编辑前后分别执行 `git diff --binary`、`git status --porcelain=v1 --untracked-files=all`，用 `diff -u` 比较快照 | 差异退出 1。跟踪文件差异仅两条索引行及其 diff 元数据。新增路径为两份讨论稿和本记录。对照用通用任务讨论稿两份 SHA-256 相同。 |
| `shasum -a 256` 核对下表规格和候选文件 | 退出 0，规格摘要与 PM 交接值一致。 |

本地链接按相对路径、显式 HTML 锚点或 Markdown 标题 slug 检查。Mermaid 对照了源码节点与连线。当前环境 `command -v mmdc` 退出 1，图形渲染未实测。D-01 是 Markdown 交付，检查限于文档与工作树，软件编译、单测和运行验证属于软件实施范围。

<details>
<summary>可重跑的链接、结构与索引检查</summary>

```bash
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
import re

stem = 'equipment-status-process-monitoring'
docs = Path('docs')
expected_ids = ['metric-registry', 'latest-cards', 'history-curves', 'data-flow', 'adoption']
expected_indexes = {
    '': '01b40650b7f3fd06fc0fec7f7a2b657c2274a3200f8488228c59b7433801e156',
    '.zh-CN': '4bf114862b40e9474bfaef6b24cd179c6c3f7031b6c3148442ac6ccef366a35d',
}
link_pattern = r'\]\(([^()\s]+)\)'
all_links = 0
for lang, index_hash in expected_indexes.items():
    guide = docs / f'{stem}{lang}.md'
    other = '' if lang else '.zh-CN'
    source = guide.read_text()
    links = re.findall(link_pattern, source)
    assert re.findall(r'<a id="([^"]+)"', source) == expected_ids
    assert [link[1:] for link in links if link.startswith('#')] == expected_ids
    assert [source.count(token) for token in ('`furnaceZone1Actual`', '`furnaceZone1Set`', '`0`', '`false`', '10', '```mermaid')] == [1] * 6
    assert not re.search(r'/api/|^```json', source, re.M)
    assert source.count('```') == 2 and source.endswith('\n')
    assert f'{stem}{other}.md' in links and f'README{lang}.md' in links

    index = docs / f'README{lang}.md'
    index_lines = index.read_bytes().splitlines(keepends=True)
    rows = [row for row in index_lines if stem.encode() in row]
    assert len(rows) == 1 and rows[0].startswith(b'| ')
    assert sha256(b''.join(row for row in index_lines if row != rows[0])).hexdigest() == index_hash
    index_links = re.findall(link_pattern, rows[0].decode())
    assert index_links == [f'{stem}{lang}.md', f'{stem}{other}.md']
    for origin, targets in ((guide, links), (index, index_links)):
        for link in targets:
            path, _, anchor = link.partition('#')
            target = origin.parent / path if path else origin
            assert target.is_file(), (origin, link)
            if anchor:
                body = target.read_text()
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-')
                         for h in re.findall(r'^#{1,6} (.+)$', body, re.M)]
                assert f'<a id="{anchor}">' in body or anchor in slugs, (origin, link)
            all_links += 1
    print(f'{guide}: {len(links)} guide links, {len(index_links)} index links, 5 reading anchors, 1 index row')
assert all_links == 42, all_links
print(f'{all_links} local links resolved across both guides and index rows')
PY
```

</details>

## Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，基线 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。以工作树文件而非仅 HEAD 为验证对象。规格、讨论稿及任务记录为未跟踪文件，索引包含另一项工作原有的未提交行。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `c5b49be944d3ae40abd72ac77967b529afa6a449e0cf608a415872e486310391` |
| `docs/equipment-status-process-monitoring.md` | `738441be2a54cef103e714e03c6ae9ebb89e7b4debf31f393332aedba8c361b6` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `345fa0b94197ef14cb0bbc916ca3d0916f775ecb98ea008c9601162dc3d05041` |
| `docs/README.md` | `a74d088ca1802bc1906a929004cb73bc8c3a6adb19a66d4579f5b957ee17a673` |
| `docs/README.zh-CN.md` | `9bc039d9b9dc5c2261f6682485ff2facb623afee43c3d8b931ef09abf6d5c87a` |
| `docs/generic-task-workflow-discussion.md`（既有链接目标） | `b0913d0fe16627b9d7bbe1043b8b602ccee312b08915a70a68ed628fc7032fff` |
| `docs/generic-task-workflow-discussion.zh-CN.md`（既有链接目标） | `2e55a70064945d4836f4204bb7f9a7dba2151d3c76b78156aa88ca7416f39439` |

下一阶段由主协调会话启动 fresh-context Verification，对 r3 §7.4 D-01 按 D01-AC01 至 D01-AC04 独立验证。需从工作树读取新稿和既有未跟踪链接目标。后续整理交付内容时，这两个链接目标须随相应索引内容可用。

临时资源仅为本任务的 `/private/tmp/arch-obs-001-d01.WbzS9p` 前后对照快照，完成比较后回收。验证输入为仓库文件及本文记录。

# D-02 单位规则补充

2026-11-07（Asia/Shanghai）。D-02 状态为 `developer_handoff`，授权及验收项见 [r3 §7.4 D-02](spec.md#r3-d-02-单位规则补充)。r3 软件设计仍处于 `draft`。

## 实施与 DEV 自检

两份讨论稿仅在第 1 至 4 节补充单位说明。指标名称与两种语言共用的可选 `unit` 分开保存，前端组合指标项标题，值区仅显示格式化后的值。曲线组沿用同一物理量和单位，共用纵轴只标注一次单位，空单位省略标注。SMA 按 `metricKey` 上报原类型的 JSON 标量，两路按同一登记业务单位上报。

| 检查 | 实际结果 |
| --- | --- |
| 对照两稿与 r3 §3、§4.1、§4.2、§5 及 D02-AC01 至 D02-AC04 | 两稿均说明空单位、标题拼接与 `810.2` 值区示例、曲线轴和 SMA 上报规则。原有接口与 JSON 示例链接继续指向规格。 |
| 从上方 D-01 记录提取 `python3` 链接脚本执行 | 初次退出 1，原子串计数将 `810.2` 也计入 `10`。执行时经 `sed 's/source.count(token)/source.replace("810.2", "").count(token)/'` 排除该示例后退出 0。两稿各 19 个链接、5 个阅读锚点，含两条既有索引行共 42 个链接解析成功。 |
| 内联 `python3` 比较编辑前副本，按差异分段、链接、锚点及 Mermaid 围栏检查，并用 `json.loads` 解析规格示例 | 退出 0。两稿的差异各限于第 1 至 4 节，链接、锚点及 Mermaid 源码逐字节一致。规格和 QA 记录与 DEV 开始时的副本一致，规格中 6 段 JSON 可解析，看板示例将 `label` 与 `unit` 分开，两路温度值均为 JSON 数字。 |
| `git diff --binary`、`git status --porcelain=v1 --untracked-files=all` 与编辑前快照用 `cmp` 比较 | 均退出 0。三份本次交付文件在编辑前已经是未跟踪文件，内容差异另与编辑前副本比较。 |
| `git diff --no-index --check -- "$before" "$after"`（两稿及本记录分别与编辑前副本比较） | 三次均退出 1，表示内容存在差异，均无空白错误输出。 |
| `head -c 7255 plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md \| shasum -a 256` | 退出 0。摘要 `b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f` 匹配 D-01 原记录。 |

## D-02 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。以当前工作树文件为候选，`shasum -a 256` 核对结果如下。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `55c168a7120af682e98af4246fb0d8c192492d8d7830d7dddc14be379fe3d3a3` |
| `docs/equipment-status-process-monitoring.md` | `939db98596e85464552c8250d0322e659af923216becba83063d3a1e9c4400e3` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `9c032abe5be2f04acf6b05d2c9404eae425841938a01ac07379f3da7b639d22e` |

交主协调会话启动 fresh-context Verification，对 D02-AC01 至 D02-AC04 独立验证。本轮证据限于静态文档和工作树，未运行软件或渲染。既有通用任务讨论稿仍为工作树内的链接依赖。编辑前快照仅用于 DEV 比对，交接前回收。
<!-- ARCH-OBS-001-r6-history-end -->

</details>

# r7 Development 交接

2026-11-11（Asia/Shanghai）。状态：`developer_handoff`。Human Owner 的精确授权为“批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证”；完整规格 SHA-256 为 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。这份记录是 Development 自检与未完成验证的事实，不是独立 QA 结论或 Human Owner 最终验收。

## 来源、范围和实现

交付源码是独立目录 `runtime/arch-obs-001-r7/source`，起点为冻结基线 `runtime/arch-obs-001-r7/baseline`，基线 Git HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。基线清单含 888 个公共文件；协调者比对了 ARCH-ACQ-003 r2 已验收清单中的 53 个依赖文件，清单 SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。源码复制排除了真实环境文件、私有 profile、数据库、构建产物、依赖缓存与密钥。本次 57 个新增／修改文件逐项符合 §9.4；下表逐项列出候选 SHA-256。未将变更合入现有运行树。

实现了 `equipment_observation` 模块及显式后继 revision `5f7a9c1e3b26`，包括指标登记、两目标槽位、卡片和曲线配置、实时快照、过程历史及带任务证据的事务回执。SMA 和第三方使用同一发现接口及两个独立写入目标；身份、范围和任务归属由私有 profile 与 v2 事实校验。任务点年龄与每设备／组的采集值陈旧阈值分别配置。Web 四页卡片、三页曲线、两个管理员管理入口、双语及受范围保护的记录列表接入候选 API；原能耗和采集数据入口保留。机器合同、示例 profile、合成向量及回环可复跑走读位于 `contracts/published/http-api/equipment-observation-v1/`，两份讨论稿追加 r7 实际流程。

| 证据 | SHA-256 |
| --- | --- |
| 冻结基线树（对有序 `sha256  相对路径\n` 文本取 SHA-256） | `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f` |
| 候选树（相同算法，924 个公共文件） | `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402` |
| [r7-source.patch](evidence/r7-source.patch) | `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` |
| [r7-source-baseline.json](evidence/r7-source-baseline.json) | `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10` |
| 本记录追加前的 tasks.md 前缀（23232 字节） | `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3` |

补丁先以 `git apply --check --whitespace=error` 对冻结基线验证；再在 `/private/tmp/arch-obs-001-r7-dev-tq7d4aq3/patch-reproduction/check` 的基线副本实际应用，逐项比对 924 个候选文件 SHA-256，均匹配。证据 JSON 包含完整基线、候选及每个变更文件摘要；生成产物和依赖目录排除在树摘要外。上述 r6 及更早 `tasks.md` 字节逐字保留，可取前 23232 字节恢复。

<details><summary>57 个候选变更文件和 SHA-256</summary>

| 候选相对路径 | 类型 | SHA-256 |
| --- | --- | --- |
| `CODE_INDEX.md` | 修改 | `ea9afc17e95c692f0f9f06b3f5d292c5b3f84bc4c69a3f65abc9ba21dcfea11c` |
| `backend/alembic/versions/20261111_1800_5f7a9c1e3b26_add_equipment_observation.py` | 新增 | `77e28319827ec54257ef889ec7b4eda4ce7e29dc203035ea76b8e6529d96038a` |
| `backend/app/equipment_observation/README.md` | 新增 | `5af542dd1fd47f75937f41816fe2cbec95a2b9c0cdc296482e89ec44b0fa17d7` |
| `backend/app/equipment_observation/README.zh-CN.md` | 新增 | `61ca08d3c20ad18a3698a9e5c19fc170d29e748f7fa90d418c7405e4d9c4fde4` |
| `backend/app/equipment_observation/__init__.py` | 新增 | `56fc319faab27f00444050a7f4cede5bfd82c40a776223482a9d0b6cb9b92130` |
| `backend/app/equipment_observation/api/__init__.py` | 新增 | `77a668728ad2886630462f40fe5920f121ce342aaba26c2cc2934040570df252` |
| `backend/app/equipment_observation/api/routes.py` | 新增 | `5db2559282c98aed75c35f7736f79e69a06eb6a208fba30390d59e5fc74c374a` |
| `backend/app/equipment_observation/domain.py` | 新增 | `17a61fb2175db447a0fd31f6050a4a86a0585982d128fbc80017db54e4faa0bc` |
| `backend/app/equipment_observation/error_codes.py` | 新增 | `662d6e34cdfd9c5df8fe39fa27408e591033b3e600dceee2058195806c130fd3` |
| `backend/app/equipment_observation/manifest.py` | 新增 | `592adc32634ec1edce508deca9ccba6004cdef6bb64a5848ea9a548c09abe4c3` |
| `backend/app/equipment_observation/models/__init__.py` | 新增 | `8a49f24867d27ae803823dc6d6f2253404437439bcbbfaff253b6797186b3c73` |
| `backend/app/equipment_observation/models/records.py` | 新增 | `346a80dad24623f6f6bf70f72690870c42b94705fd86c963bcce42c4dc30a59e` |
| `backend/app/equipment_observation/profile.py` | 新增 | `65ca4b294d84e01e45f8b6b9ad20ca90e3078fcd95877e4a890ba1a8e2c88ba1` |
| `backend/app/equipment_observation/schemas.py` | 新增 | `1072841d8c535cd1dd54d6d446ddf70b859d73078ef71fabbc682c051dd96850` |
| `backend/app/equipment_observation/services/__init__.py` | 新增 | `877cf89acf402aedd0374737b6e5c80c355d914974d8e84c15b5409eb9da12de` |
| `backend/app/equipment_observation/services/configuration.py` | 新增 | `9278f71accaea1ae8df6affdb3835e5dd0dae0d78c2fda9aa499c1490ec10451` |
| `backend/app/equipment_observation/services/ingest.py` | 新增 | `2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34` |
| `backend/app/equipment_observation/services/reads.py` | 新增 | `c5e2939fb76187ce47db11bda849ba75292f85b14eb7d0d6098c3bfbf9c7980e` |
| `backend/app/plc_facts/README.md` | 修改 | `6ba8d94ba587f3fc106a37b2be12741b385602ec90f0cbcfbfd0bd5bb8e9b305` |
| `backend/app/plc_facts/README.zh-CN.md` | 修改 | `07b905c7970dbaa145c10d0f5f0c3354690ffdda725149532382f78453858713` |
| `backend/app/plc_facts/crud/async_v2.py` | 修改 | `4f39e0f4fa4ae612523377bafc0917ea249160d90350c30d062a4e47be0f6e76` |
| `backend/app/plc_facts/crud/sync_v2_maintenance.py` | 修改 | `ba26d3b21f3cce238d88c9aea961e410e4064928f4084888594170fa51aa12f9` |
| `backend/app/plc_facts/manifest.py` | 修改 | `79afed8eae956c82e14d7c28b489e76b51bfe58c105c8fd2e30cba54d7e689e3` |
| `backend/app/plc_facts/services/observation_evidence.py` | 新增 | `8defa9ed4fd38133debef1fd41f442664ba493e25e1f4aadcf8331ee7e8e2141` |
| `backend/app/plc_facts/v2_config.py` | 修改 | `233dcd6b033e664daec245f8b0a575c2c36c277fb5d8fa9569a989913162ec75` |
| `backend/common/integration/storage.py` | 修改 | `b230f7e1fb9288511abf0c1dffc07e954fcbe2b7ca0982b5ddeb2703f8b176d2` |
| `backend/tests/test_equipment_observation_domain.py` | 新增 | `98bdb98f65605aac04f461651143018fc6dfdce76524008bce2e523465e50c8d` |
| `backend/tests/test_equipment_temperature_migration.py` | 修改 | `3c611ab32eca25e6c749350f6305e423e29b579be35677c5fa2ce4ed16b8009f` |
| `backend/tests/test_legacy_acquisition_retirement.py` | 修改 | `57d8b37c815f269e7b7b90b57be3f9e0dee570ced556bf25fe49623018076c55` |
| `backend/tests/test_mapping_migration.py` | 修改 | `9b99ff37c4241c6b7dc67e943655229a3d80ac6eee8e0192a024f1ec0f60697f` |
| `backend/tests_mysql/test_equipment_observation_mysql.py` | 新增 | `4c3376b87c5393a5f301d7193f637655a3315b617700c1e6de512875c3423885` |
| `contracts/README.md` | 修改 | `ea4bb17979772a2f240ee23ac127ec6b68a36c8413a69882354ee2a072e5f924` |
| `contracts/README.zh-CN.md` | 修改 | `bcbb72e6c50fd65f3e5245641783f3d1a01a4b3a1f118309100b0066316e6386` |
| `contracts/published/http-api/equipment-observation-v1/README.md` | 新增 | `49ff29317e038a0b39b2bc86184f7a90383e956f840803071b7264391afcfa7a` |
| `contracts/published/http-api/equipment-observation-v1/README.zh-CN.md` | 新增 | `e0263e0ff2fb43ae19b0b6bafec13bbe64ca03a107bf2fcf79d9dca11f8770ec` |
| `contracts/published/http-api/equipment-observation-v1/example-profile.json` | 新增 | `061519aedb07594486383285d37e83010c9dc66631b2b5569674dc7f2da3265e` |
| `contracts/published/http-api/equipment-observation-v1/openapi.json` | 新增 | `7a5bd636a75208dbaf65531bff9d72e9dae8d81765d73f2ae10631e745849c07` |
| `contracts/published/http-api/equipment-observation-v1/vectors.json` | 新增 | `dd904d37d2a787c04afe14f13331c08b44ab54cb72708a37206be8be05456ed8` |
| `contracts/published/http-api/equipment-observation-v1/walkthrough.py` | 新增 | `79c2072ed1f31bce414715af06753505d23257c4ce5eafe15b0e4ea02876e7ee` |
| `docs/equipment-status-process-monitoring.md` | 修改 | `5ed0909de0273d0f5cfb3489cf4e7269f3671465080acf52dfdd8c343131494e` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | 修改 | `d4f15c10470e8f0b7c421ff170db5819ac3eb91c5c0f674a4d2751cf8bf606c8` |
| `frontend-js/src/app/equipment/api/observations.js` | 新增 | `ffb34494dd99d57ab4375ca55fcd87aa34ac14f12b5e886acbba53e41c7bc16d` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | 新增 | `66f4a3ae514917b5d055d1baebba3c89c692d39c7a2cf459f540f959c0e3f2cf` |
| `frontend-js/src/app/equipment/locales/en-US.json` | 修改 | `1e808aed676cfbced4b821ea229bfd84f7e606815b6e77d4884bdbde2a2ee4b0` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | 修改 | `238aa4b86e59d54556abfdf3ce2fed7e0cf6bd391873a56ed202d7ca9fbed6f3` |
| `frontend-js/src/app/equipment/manifest.js` | 修改 | `8ccc0f244d154ec0f9216142736b940daa630ff4cc722db426639d876faab96e` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | 新增 | `42d34402b53fc7012a86146f2442ba05c9d0e10d30d98e59990effe2e30cdc38` |
| `frontend-js/src/app/equipment/views/observations/cards.vue` | 新增 | `0f0f9330cae3d1c97fb941a36fc4886108a0d5ed2b9fef8a91e220f45506bcd9` |
| `frontend-js/src/app/monitor/api/observations.js` | 新增 | `6d3ee0a8ad807f5c292e1857253b0d8d7ff6e19d173c540de2427792bfa4887d` |
| `frontend-js/src/app/monitor/components/observations/CurveChart.vue` | 新增 | `167c0e55ca1d0135a90c2214d6498a52353cfa5d8643ddc68289d89e9bf215cb` |
| `frontend-js/src/app/monitor/components/observations/curveSeries.js` | 新增 | `b092e99b878609f8cb107dd50922972cadd239ee3c4a13195948c5e8b2162d7d` |
| `frontend-js/src/app/monitor/locales/en-US.json` | 修改 | `e8aec65ac4314240d233e5a0e263c73bad8d6f47dc33b8f1845f20f712e26534` |
| `frontend-js/src/app/monitor/locales/zh-CN.json` | 修改 | `7fdabe4b01e7fc6d0e124307174e7283bb0dbf00335668da3180ac06c5f8a80b` |
| `frontend-js/src/app/monitor/manifest.js` | 修改 | `fe604032a2ab8a81c6dfd20d8bc5d620fc631d502254a2a4e285526e81db9d85` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | 新增 | `08f5c558e55bac2877bdc18e408ffb40171318524b60f172e712b8c41e89b210` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | 新增 | `b852627a9ca29de568a363ce7527a654c4bb0d9ce951f32f425e5592ad34ee34` |
| `frontend-js/tests/module-registry/equipment-observation.test.mjs` | 新增 | `eb957cb55b10596b0e0c896b26705a7db4ef0282d166394fb391062ea00b0bc5` |

</details>

## DEV 自检和已观察结果

使用候选工作目录及仓库锁文件，Python 为 `uv run --offline --frozen --no-sync`，`PYTHONPATH` 显式指向候选 `backend`，复用只读依赖虚拟环境；前端使用候选独立的 `node_modules` 副本和 `pnpm_config_verify_deps_before_run=false`。未使用 3307、8000、5190 或真实 PLC/DAA/SMA。DEV 专属 MySQL 8.4.6：回环映射 13395、schema `arch_obs_r7_dev`、server UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`、业务会话 +08:00；API 18395、Web 15395 均回环。真实凭据和 profile 仅在仓库外测试私有目录。首次空库升级到新 head，随后在已有合成 v2 事实的同一隔离库对 r7 七表执行降级至 `4e6a8b0d2f14` 再升级；核对目标 UUID/schema/revision 和非空 `task_evidence` 列。未操作旧业务实例。

| DEV 检查和命令 | 实际结果 |
| --- | --- |
| `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql` | 退出 0；新增段的离线 SQL 包含七张表及回执任务证据。隔离 MySQL 空库升级和仅 r7 的降级／再升级均退出 0。 |
| `pytest -q -m no_db tests/test_equipment_observation_domain.py`（以上 uv 方式） | 退出 0：4 passed；覆盖任务号、原始类型、缺省和 null、两目标稳定事件、无效 UUID 及每组不同陈旧阈值。 |
| `pytest -q tests_mysql/test_equipment_observation_mysql.py`（由确认的 `OBS_FIXTURE_*`、专属 MySQL 和私有合成机器凭据驱动） | 退出 0：2 passed；实际 socket 与真 MySQL 验证未认证、越权、413/415、质量/空值、SMA 必填，A→B、B 缺测、迟到 A、旧包 stale、回执重试/冲突、历史同源去重、伪造引用／采样时间、0/false 及任务证据。测试自身先校验精确轮次、UUID、端口、schema、用户、MySQL 版本、时区及 revision。 |
| `python contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18395`（以 `OBS_DEMO_*` 私有合成凭据运行） | 实际执行退出 0；两份不同合成 v2 样本、第三方和 SMA 全信封各自独立 latest/history、发现、重试与任务证据详情、`000042` 的 `812.2/815.0` 卡片及曲线通过。完成边界测试后再次运行恢复 `000042`。 |
| 候选 ASGI + 真 MySQL 对两条管理员 PATCH | 退出 0；实时备注与历史备注／`reviewed` 均 HTTP 200、响应返回新值。另由协调者执行真实浏览器保存。 |
| `pnpm check:modules`、`pnpm build --outDir /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/frontend-dist` | 均退出 0；构建提示既有大 chunk 和外部 outDir 警告。 |
| `pnpm test:modules` | 退出 1：53 passed、4 failed。失败是两个既有测试文件中对退役 `monitor.realtime` 的四个固定路由／授权断言，均在原 §9.4 修改范围外；已保留原文件并提交协调者。 |
| 受影响后端 `pytest -q -m no_db tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_acquisition_facts_migration.py tests/test_business_integration_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_equipment_observation_domain.py`，所有 bootstrap 和 mock/projection 开关设置 False | 退出 1：133 passed、3 skipped、2 failed。一个既有测试固定迁移数 11，新增 head 后为 12；另一个既有测试将旧元数据表集合全等，未包含七张新表。前者文件不在 §9.4，后者虽可同步 head 但原授权仅允许 head 断言，故两处原断言均未改。初次运行另因合成 supervisor bootstrap 为 True 多失败一项，关闭后该项通过。 |
| 协调者的候选真实浏览器 DEV 检查 | `runtime/arch-obs-001-r7/output/playwright/dev-browser-result.json` 及 3 张 PNG：登录、双语指标编辑、四卡片页、三曲线页、任务筛选、同单位、两类记录详情及实际保存、普通读用户与管理 403、无 pageerror；这仍是 DEV 自检而非独立 QA。 |
| 文档及合同 | 新 OpenAPI 三条路径及所有 `$ref` 可解析；向量、示例 profile JSON 可解析且 profile 经实现校验通过；两稿、合同及新模块说明的相对路径链接均存在。 |

## Developer handoff：待独立复核和限制

请 fresh-context Verification 直接核对上述 `source`、规格 SHA、补丁／文件清单及 §9.5 验收项。独立轮次应使用另一个专属 MySQL（13396）和独立 API/Web 端口与私有 profile，不复用 DEV 数据或密钥。尤其复核旧 profile/旧 revision 与新 profile/新 revision 的实际读写、错配拒绝、旧 typed 接口在新 revision 的实库行为，以及空闲／未知／过期任务、两条受控产线、历史筛选、首用锁与 100 槽上限、并发／未知提交与独立补投；这些项目本 DEV 记录没有完整实库证据，不能视为已通过。所列 2 个旧后端断言和 4 个旧前端断言仍失败，是否扩展修订范围由 Human Owner 决定，勿将其当通过。

SMA 全信封由合成 HTTP 客户端发送，未运行 SMA 产品或连接 DAA/真实 PLC；没有进行性能、长时稳定性、真实数据库采用、发布或生产部署验证。截图和合成实例为 DEV 资产，协调者负责按本任务范围停止及回收；候选源码、冻结基线、任务记录和脱敏补丁需保留给 QA 与后续单独批准的整合。测试机私有 profile、测试账号、令牌和日志不进入交付。DEV 实际启动入口（环境文件和 profile 内容不展示）：在候选 `backend/` 导出仓库外 DEV `backend.env`、独立 facts／observation profile 路径、`UV_PROJECT_ENVIRONMENT` 和私有 `UV_CACHE_DIR`，设置候选 `PYTHONPATH`，执行 `uv run --offline --frozen --no-sync python main.py`，绑定 `127.0.0.1:18395`；在候选 `frontend-js/` 设置 `VITE_PROXY_TARGET=http://127.0.0.1:18395` 和隔离角色页面清单，执行 `pnpm exec vite --host 127.0.0.1 --port 15395 --strictPort`。协调者已停止这两个 DEV 进程并核实端口无监听；浏览器证据使用本机 Chrome headless/Playwright。


# r7 QA1 返工 Development 交接

2026-11-11（Asia/Shanghai）。同一获批 `ARCH-OBS-001 r7` §9 内按 QA1 的 1–4 项缺陷返工，状态 `developer_handoff`，交 fresh-context Verification 重新验证。规格 SHA-256 保持 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`；返工开始读取的 canonical QA1 checklist SHA-256 为 `3d9c5c749e35de3b596bacef9dbd5cc74e0c798c9232fb847f707dd4c1e35aca`，其 `qa_failed` 记录由 Verification 管理，本角色未修改。这个记录不授予 QA 结论或 Human Owner 验收。

## 改动与并发语义

1. 曲线保存时按稳定顺序对所引用指标行做 `FOR UPDATE` 并保留至提交；指标类型变更锁定同一指标行，并用锁定读取检查**所有**曲线组和系列引用，包括停用项。未首次使用的已引用数值指标不能改成布尔或字符串，解除全部引用后才可在原有规则下修改；已使用指标的类型和单位仍按原首用锁拒绝。单位兼容检查保留。
2. 两类管理员详情共用视图显示采集质量及其中文／英文值，与人工复核标记分开；对应列表质量显示也采用同一语言文本。
3. 管理员详情 GET 和 PATCH 的查询以记录 ID 与当前角色获准设备集共同限定；越权记录与不存在记录均为 404，显式带越权设备筛选的列表仍返回 403，写操作沿用同一受限详情查询。
4. 双语走读及机器合同补充后续 SMA 独立登录身份的 `plc-facts-read`、v2 `readScopes` 精确 PLC/DB 与观察写 Bearer 的区分、双路回执、SMA-004 后续 GET→POST、ARCH-ACQ-001 统筹、DAA-010、ARCH-BE-012 精确 provider/隔离独立验证及 Human Owner 最终验收、DAA-010 精确批准和新隔离 profile、逐 DB 的 SQLite/后端事实与回执确认及相关 API 与 SMA 产品执行的独立门槛。本版没有运行产品或真实现场链。

相对 QA1 候选仅以下 11 个允许文件发生变化；SHA-256 分别为 QA1 与本返工候选。完整基线到新候选的 57 文件差异及 924 文件摘要仍在下述新的 canonical 清单。其余源码字节不变。

| 相对交付源码路径 | QA1 SHA-256 | 返工 SHA-256 |
| --- | --- | --- |
| `backend/app/equipment_observation/api/routes.py` | `5db2559282c98aed75c35f7736f79e69a06eb6a208fba30390d59e5fc74c374a` | `547d571f9cf845c1a65d414eb193736aacf0751cacff4ef81d6de48fc2a7999e` |
| `backend/app/equipment_observation/services/configuration.py` | `9278f71accaea1ae8df6affdb3835e5dd0dae0d78c2fda9aa499c1490ec10451` | `c85202890990bcbb333e58bfa37cf89bb5aec7e10b1f80065e0a1c2ca6a82696` |
| `backend/app/equipment_observation/services/reads.py` | `c5e2939fb76187ce47db11bda849ba75292f85b14eb7d0d6098c3bfbf9c7980e` | `85fa8b78e1ee4b82001badf0c1e1af8e2e050eeaf577e90be7c15cb744e6f932` |
| `backend/tests_mysql/test_equipment_observation_mysql.py` | `4c3376b87c5393a5f301d7193f637655a3315b617700c1e6de512875c3423885` | `4e6928fd79f6b574b7c5b1af2c70852c8f613237edbf86da33d010aeecfcffdf` |
| `contracts/published/http-api/equipment-observation-v1/README.md` | `49ff29317e038a0b39b2bc86184f7a90383e956f840803071b7264391afcfa7a` | `e4b57b94e795258462a477a189f41c281d164e303b0f648e924b89dcc8e1ba05` |
| `contracts/published/http-api/equipment-observation-v1/README.zh-CN.md` | `e0263e0ff2fb43ae19b0b6bafec13bbe64ca03a107bf2fcf79d9dca11f8770ec` | `7d4484c21425cb185e2cb759d6316b77f2bd9e8231884f621e8e0cfb62a12eed` |
| `docs/equipment-status-process-monitoring.md` | `5ed0909de0273d0f5cfb3489cf4e7269f3671465080acf52dfdd8c343131494e` | `8b5e0a2f62fc55259486791a9eb42f722d3f1c86d016b6e64ee917fc8344647f` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `d4f15c10470e8f0b7c421ff170db5819ac3eb91c5c0f674a4d2751cf8bf606c8` | `fbf9061bb5b07724a1c17f99acbb18b4e1a7f745d8ce1a7e8ff03ab9677d3ef4` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `66f4a3ae514917b5d055d1baebba3c89c692d39c7a2cf459f540f959c0e3f2cf` | `9d27c7507bdcf73be5514fec533b13b4b34035a8867706a559119df2a78bf4f3` |
| `frontend-js/src/app/equipment/locales/en-US.json` | `1e808aed676cfbced4b821ea229bfd84f7e606815b6e77d4884bdbde2a2ee4b0` | `861a7937509a221964a8b0ff0944260b86baf1c2d9fbfb9d2938c9b12b216c20` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | `238aa4b86e59d54556abfdf3ce2fed7e0cf6bd391873a56ed202d7ca9fbed6f3` | `c7a2be418b4bca75ea0a08180edf56d502a317468904de97691b66f6fa9072a9` |

## DEV 返工自检

DEV 专用 MySQL 8.4.6 的 UUID、库名 `arch_obs_r7_dev`、13395、+08:00 和 revision `5f7a9c1e3b26` 由协调者重新核对；候选 API `127.0.0.1:18395`、Web `127.0.0.1:15395`。未连接 QA 13396 或旧的 3307／8000／5190。

| 检查 | 真实结果 |
| --- | --- |
| `pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py`（明确 DEV round/UUID/port/schema/ACK，私有 profile 与合成凭据） | 退出 0，**5 passed**。新增三项真实 HTTP + MySQL 覆盖启用及停用曲线／系列的类型保护、解除引用和可编辑名称、首用后类型／单位保护；用两方向竞争同一指标行锁的事务验证曲线保存／类型更改串行化，检查等待及提交后结果；两类详情和 PATCH 的越权／不存在同 404、显式越权列表 403、被拒记录未变化。原两项写入/任务回归仍通过。 |
| 协调者真实 Chrome DEV 浏览器 | [返工结果](../../runtime/arch-obs-001-r7/output/playwright/dev-rework-browser-result.json)及[历史详情图](../../runtime/arch-obs-001-r7/output/playwright/dev-rework-task-000042-history-detail.png)：`000042` 的实时与历史详情均返回 `quality=good`；两处中文显示“采集质量／正常”、英文显示“Source quality／Good”，无 pageerror。未修改这些记录。 |
| 候选 `walkthrough.py --base-url http://127.0.0.1:18395` | 退出 0，第三方／合成 SMA 两目标与独立回执、task evidence、重试及 `000042` 卡片／曲线通过；边界测试结束后恢复 `000042`。 |
| `pnpm build --outDir <DEV私有目录>/frontend-rework-dist` | 退出 0；前置 `check:modules` 通过，28 路由，原有大 chunk 提示保留。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**；仍为 QA1 已列出的旧 `monitor.realtime` 固定路由／权限断言，文件未改。 |
| 原交接的受影响后端 `pytest -q -m no_db` 套件，所有 bootstrap、mock 和 projection 开关显式关闭 | 退出 1，**133 passed、3 skipped、2 failed**；仍是 QA1 记录的旧迁移数量与旧 metadata 全等断言，超出 §9.4 中允许的旧断言修改范围，保持原样。 |
| 双语讨论稿与合同本地链接、锚点及质量 i18n | 退出 0：115 条本地链接／锚点解析，两个语言的质量文本键存在。 |
| 原基线重建 | `git apply --check --whitespace=error` 退出 0；从原冻结 888 文件基线实际应用新补丁后，逐项重建的 924 个候选文件 SHA-256 全部一致。 |

## 新候选固定与复验 handoff

| 项 | SHA-256 |
| --- | --- |
| 新候选树（排序的 `sha256  相对路径\n` 文本摘要） | `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada` |
| [新 canonical 补丁](evidence/r7-source.patch) | `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4` |
| [新 canonical 基线与候选清单](evidence/r7-source-baseline.json) | `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f` |
| 返工前完整 tasks.md 前缀（40915 字节） | `21bfb30971cdaa3268cbf200b6a6e28691b9ec92f98e7efa5bb933990bb488f8` |

QA1 的原候选树为 `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402`；其原补丁 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` 与原清单 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10` 原字节保存在 [qa1-source](../../runtime/arch-obs-001-r7/output/qa1-source/)。上方 QA1 以前的记录均保持原字节，可截取本记录前 40915 字节还原；其中旧 23232 字节 r6 历史仍可按先前标记单独还原。

请由 fresh-context Verification 针对新固定候选重新检查 QA1 四项及受影响验收，QA 资源独立于 DEV。QA1 记录中的两条后端、四条前端旧断言仍失败，不能当通过或擅改范围。浏览器／MySQL 测试是 DEV 自检；未运行 SMA 产品、DAA、PLC 或真实 profile，也未实施生产发布或环境采用。DEV 服务和隔离资源由协调者按已批准归属停止与回收。


# r7 QA2 返工 Development 交接

2026-11-11（Asia/Shanghai）。按已批准的 `ARCH-OBS-001 r7` §9 对 QA2 唯一的 R7-AC06 管理界面本地化问题进行最小返工，状态 `developer_handoff`。规格 SHA-256 仍为 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`；本轮读取的 canonical QA2 checklist SHA-256 为 `e1b7255f8360fd4273e8def8309b1601bdb65670b048eade849ea6fae85a4967`，其 `qa_failed` 与 QA1 历史由 Verification 管理，Development 未修改。QA2 已关闭 QA1 四项，但最终 QA 与 Human Owner 验收需各自完成。

## 精确返工内容

历史列表的复核枚举用现有中英词条显示：`abnormal` 为“异常”／“Abnormal”，`reviewed` 为“已复核”／“Reviewed”，空值继续显示空白。详情表和指标配置表的名称表头随显示值使用 `nameZh`／`nameEn` 对应文案；卡片和曲线配置表的标题表头同样匹配 `titleZh`／`titleEn`。只改变显示，提交数据仍沿用原枚举。各表 `prop`、`nameZh`／`titleZh` 列宽偏好键及表宽工具均保留。

相对 QA2 仅有以下 3 个允许的前端组件发生变化，没有修改后端、合同、字典或旧测试。下列 SHA-256 可分别定位 QA2 候选和返工候选。

| 相对交付源码路径 | QA2 SHA-256 | 返工 SHA-256 |
| --- | --- | --- |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `9d27c7507bdcf73be5514fec533b13b4b34035a8867706a559119df2a78bf4f3` | `e1650bdb69611ce995b660c41967151da56d58957ba46ece45235bc2d5641c81` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `42d34402b53fc7012a86146f2442ba05c9d0e10d30d98e59990effe2e30cdc38` | `aa1d0f887281b60ff5d0517f216a9264a1ebc0d321466b1965f81c724392e591` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | `08f5c558e55bac2877bdc18e408ffb40171318524b60f172e712b8c41e89b210` | `60494af0dc8ad6f7622d3db441e4db48045b2f399443759bbd7042769917e4b0` |

## DEV 自检

| 命令或方法 | 实际结果 |
| --- | --- |
| 候选前端 `node /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/qa2-ui-targeted.cjs` | 退出 0。离线加载项目锁定的 `vue/compiler-sfc`、Vue 模板编译器及 SSR 渲染器，实际编译三个组件中相应列模板和读取现有词典。两种语言均核对 `abnormal`、`reviewed`、null、undefined、空字符串；对详情、指标、卡片、曲线四列分别核对中英表头与对应内容，并验证原 prop/列宽键。脚本无凭据，完整正文附下，SHA-256 `bfb25239f2f4d4ce72e5b058e77f43f973487c675f6eb4d8c2bf1e4bbbfdb883`。SSR 不是浏览器验证。 |
| `node --test tests/module-registry/equipment-observation.test.mjs` | 退出 0，**2 passed**。 |
| `pnpm check:modules` | 退出 0，28 个路由、10 个分组。 |
| `pnpm build --outDir /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/qa2-rework-dist`（显式隔离页面授权及锁定依赖） | 退出 0；保留既有大 chunk 和 outDir 提示。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**。仍为 QA1/QA2 已识别的四个旧 `monitor.realtime` 路由与权限断言；本轮未修改这些旧测试。 |
| 补丁重建 | `git apply --check --whitespace=error` 退出 0；从 888 文件原冻结基线实际应用新补丁后，924 文件逐项 SHA-256 均匹配。 |

本轮仅做离线渲染、模块检查与构建；未启动或连接 DEV/QA MySQL、API、Web、浏览器、SMA、DAA 或真实 PLC，**没有对返工版做 DEV 浏览器复跑**。QA2 记录中的两项旧后端断言仍失败，本轮未改后端也未重跑该套件。临时测试脚本与构建产物由协调者在 QA3 不再需要后按资源生命周期回收。

## 新候选固定与 handoff

| 项 | SHA-256 |
| --- | --- |
| 新候选树（有序 `sha256  相对路径\n` 文本摘要） | `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf` |
| [新 canonical 补丁](evidence/r7-source.patch) | `d753328ceeb32cdd2cbd5387e221e14376403ef6024ea9cc0cf7adf7f5b00e46` |
| [新 canonical 清单](evidence/r7-source-baseline.json) | `df0145272f56505929e63e1c2a4c77d13b84acc88cead36359de5224f4f6d5e1` |
| 本轮追加前完整 tasks.md 前缀（49388 字节） | `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4` |

QA2 候选树为 `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada`；其原[补丁和清单](../../runtime/arch-obs-001-r7/output/qa2-source/) SHA-256 分别为 `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4` 和 `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f`。此前 QA1、QA2 交接内容及更早历史仍逐字节保存在本记录前 49388 字节。请 fresh-context Verification 在独立 QA3 环境验证中英文实际界面、空标记、列宽及受影响验收，不将本 DEV SSR 当作浏览器或 QA 通过。

<details><summary>本次离线 Vue SSR 定向检查原脚本</summary>

在候选 `frontend-js/` 下将以下内容另存为 `.cjs` 后运行；通过 `createRequire` 使用该项目锁定的依赖，无网络和数据库访问。

```javascript
/* Isolated, offline SSR probe of actual candidate column templates and dictionaries. */
const fs = require('node:fs')
const assert = require('node:assert/strict')
const path = require('node:path')
const { createRequire } = require('node:module')
const project = createRequire(path.join(process.cwd(), 'package.json'))
const { parse } = project('vue/compiler-sfc')
const { createSSRApp, defineComponent, h, compile } = project('vue')
const { renderToString } = project('vue/server-renderer')
const source = {
  records: 'src/app/equipment/components/observations/RecordList.vue',
  equipment: 'src/app/equipment/views/observations/admin.vue',
  monitor: 'src/app/monitor/views/observations/admin.vue'
}
const templates = Object.fromEntries(Object.entries(source).map(([key, file]) => {
  const result = parse(fs.readFileSync(file, 'utf8'), { filename: file })
  assert.deepEqual(result.errors, [])
  return [key, result.descriptor]
}))
const dicts = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale,
  JSON.parse(fs.readFileSync(`src/app/equipment/locales/${locale}.json`, 'utf8')).observation]))
function translator(locale) {
  return key => {
    const value = dicts[locale][key.replace('equipment.observation.', '')]
    assert.notEqual(value, undefined, `missing i18n key: ${key}`)
    return value
  }
}
function column(descriptor, prop) {
  const expression = new RegExp(`<el-table-column\\b[^>]*prop="${prop}"[^>]*>[\\s\\S]*?<\\/el-table-column>`)
  const matches = descriptor.template.content.match(expression)
  assert.ok(matches, `column ${prop} missing`)
  return matches[0]
}
const marker = templates.records.scriptSetup.content.match(/function reviewLabel\(value\)\s*\{[^}]*\}/)
assert.ok(marker, 'actual reviewLabel function missing')
async function render(template, locale, row, extra = {}) {
  const Column = defineComponent({
    props: ['prop', 'label', 'width'],
    setup(props, { slots }) {
      return () => h('section', { 'data-prop': props.prop, 'data-label': props.label, 'data-width': props.width },
        slots.default ? slots.default({ row }) : [])
    }
  })
  const t = translator(locale)
  const reviewLabel = new Function('t', `return (${marker[0]})`)(t)
  const app = createSSRApp({
    setup: () => ({ t, locale, reviewLabel, isHistory: true, ...extra }),
    render: compile(template)
  })
  app.component('el-table-column', Column)
  return renderToString(app)
}
;(async () => {
  const states = { 'zh-CN': { abnormal: '异常', reviewed: '已复核' }, 'en-US': { abnormal: 'Abnormal', reviewed: 'Reviewed' } }
  for (const locale of Object.keys(states)) {
    for (const [value, expected] of Object.entries(states[locale])) {
      const result = await render(column(templates.records, 'reviewMark'), locale, { reviewMark: value }, { columns: { widths: { reviewMark: 131 } } })
      assert.ok(result.includes(`>${expected}</section>`), result)
      assert.ok(result.includes('data-prop="reviewMark"') && result.includes('data-width="131"'), result)
    }
    for (const value of [null, undefined, '']) {
      const result = await render(column(templates.records, 'reviewMark'), locale, { reviewMark: value }, { columns: { widths: { reviewMark: 131 } } })
      assert.ok(result.endsWith('></section>'), result)
    }
  }
  const rows = { nameZh: '温度', nameEn: 'Temperature', titleZh: '炉区', titleEn: 'Zone' }
  const checks = [
    ['records', 'nameZh', 'detailColumns', 'name'],
    ['equipment', 'nameZh', 'metricColumns', 'name'],
    ['equipment', 'titleZh', 'cardColumns', 'title'],
    ['monitor', 'titleZh', 'columns', 'title']
  ]
  for (const [sourceKey, prop, widthKey, kind] of checks) {
    const template = column(templates[sourceKey], prop)
    assert.ok(template.includes(`:width="${widthKey}.widths.${prop}"`), 'stable width key changed')
    for (const locale of ['zh-CN', 'en-US']) {
      const data = await render(template, locale, rows, { [widthKey]: { widths: { [prop]: 183 } } })
      const lang = locale === 'en-US' ? 'En' : 'Zh'
      assert.ok(data.includes(`data-label="${dicts[locale][kind + lang]}"`), data)
      assert.ok(data.includes(`data-prop="${prop}"`) && data.includes('data-width="183"'), data)
      assert.ok(data.includes(`>${rows[kind + lang]}`), data)
    }
  }
  console.log('PASS actual Vue column SSR: both locales, reviewed/abnormal/empty, four bilingual headers/cells and stable width keys')
})().catch(error => { console.error(error); process.exitCode = 1 })
```

</details>
