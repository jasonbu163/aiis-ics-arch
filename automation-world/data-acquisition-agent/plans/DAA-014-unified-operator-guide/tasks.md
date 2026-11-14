Task ID: DAA-014
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: 精确 r1 文档与 DEV self-check 交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-014 r1 Development 记录

## 1. 批准与实施起点

Human Owner 已明确批准 [DAA-014 r1](spec.md)：“批准 DAA-014 r1，按规格整理 DAA 手册与采集数据指南，并清理旧的阶段指南。不要过度设计。”登记后的 spec SHA-256：`f34640c33b162851c8534e29b6793a81e9af638ef3eaf506575ddb878e0d736d`（spec 内另列批准前草案摘要）。在 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 正式共享脏工作树实施，起始 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`；HEAD 本身不标识未提交文件的内容。工作树已有其他任务改动，保留其起点，不运行服务或读写实际配置、SQLite、样本、数据库和设备。

1. 核对 DAA-007、DAA-008、DAA-011 及当前旧指南的历史版本、摘要和引用，按 R04 处理旧入口。
2. 对照界面、后端 provider 和合同，编写双语 DAA 操作手册并整理 README、采集数据通用指南与允许的活跃链接。
3. 仅做文档差异、链接/锚点、双语与启动命令语法自检，记录结果、限制与精确交接。

## 2. Human Owner 手测转交

协调者转交：两项手测和相关调试均已在本次指定 Mac/dev 环境由 Human Owner 亲自完成。第一项停采上报，原有 6 条待发送与 1 条结果未知，最终统计 `0/0/0/7`；抽查原未知样本回执为 `committed/created`，Web 同一 `sampleId` 的点值、质量一致。第二项在上报运行时连接 DS 并启动采集，采集运行期间确认累计超过原 7；暂停采集并排空后为 `0/0/0/31`，抽查新样本 `committed/created`，Web 同一 `sampleId` 的点值、质量一致。采集和上报均由 Owner 暂停；Owner 选择保留全部 31 条样本。本角色没有操作或复验这些数据。本手测不改变 DAA-010 r5 的独立 `qa_failed` 与 Windows 原生待验证状态，不代表阶段 C 或生产验收。

## 3. 旧指南历史追溯

旧 B/C 四个路径在上述手测收尾后收为首屏指向新手册的短入口。以下定位用于历史核对，不是重新运行旧测试的指令；旧任务状态和原记录均未改写。`evidence/` 中至多四份快照保留原字节，不重写其中按原目录编排的相对链接；如需跟随旧链接，以原文件所在目录为相对基准。不要把迁移前的当前快照称为旧任务的冻结版本。

| 历史入口及锚点 | 精确版本与追溯方式 |
| --- | --- |
| DAA-007 双语 `JOINT_TEST_GUIDE` | 原文件名 `automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md` / `JOINT_TEST_GUIDE.zh-CN.md`。实施前两份与固定 Git commit `fd999224a8756feda314a33148304b4bf3461876` 完全相同，SHA-256 分别为 `d6735c83806cf00d812e5f6feb76da881a1c51d8f7b93b43b7ab2302eed63fd6` / `cbff953d1b64717caf76bc6052eba062dbfe6db9117f2b07d039eb9673df149c`。从仓库根目录用 `git show fd999224a8756feda314a33148304b4bf3461876:automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md` 查看英文；中文将文件名改为 `JOINT_TEST_GUIDE.zh-CN.md`。原结论见 [DAA-007 checklist](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)。 |
| DAA-008 B-RUN-01 双语 `#m01-launch`、中文 `#m01新配置及来源交接` | [原运行记录](../DAA-008-reliable-facts-upload/tasks.md#L632)和 [DAA-011 checklist 的原文恢复说明](../DAA-011-dev-manual-refresh/checklist.md#实际命令边界与资源)记录原文件名及步骤。精确 DAA-008 r4 M01 校订后英文 SHA `960f8d0be4d10efa00372845a1e9725476d83fa49cd937e4f512dda5d9968b8a`、中文 SHA `aa4ad53702962a05c956b7c82253a2502919b20c9b861330c5642d9ec18cc769`。按下方步骤可从固定 Git 原件和 checklist 重建；`#m01-launch` 后缀在 DAA-011 QA2 版本中可直接定位。 |
| DAA-011 QA1/QA2 双语 `#L5`、`#L82`、`#L86` | 固定 Git commit `fd999224a8756feda314a33148304b4bf3461876` 中的 `automation-world/data-acquisition-agent/STAGE_C_GUIDE.md` / `STAGE_C_GUIDE.zh-CN.md` 即 QA2 原文：英文 SHA `9df1cd0a8b08372caad39d4b9ae5e62f68490864850b17a7801a314e13a2fe84`，中文 SHA `892b83f79cd0f8e24f7751e802f1567d697cc4f244c23b4a977f5b720b9ad95c`。以 `git show <完整commit>:<原文件名>` 读取；[DAA-011 QA2](../DAA-011-dev-manual-refresh/checklist.md#daa-011-r1-独立文档复验--qa2)记录 QA1 的三行原文及逐行逆向重建，勿用后续现行页行号冒充。 |
| DAA-013 英文 `#L102` 与双语 `#6-…` | [英文 QA5 原文](evidence/STAGE_C_GUIDE-DAA-013-QA5.md) SHA `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235`；[中文 QA5 原文](evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md) SHA `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73`，二者原文件名分别为 `STAGE_C_GUIDE.md` / `STAGE_C_GUIDE.zh-CN.md`。QA4 英文 `#L102` 是此前失败候选，不能用 QA5 文字冒充；[QA4 checklist](../DAA-013-multi-plc-reporting-identity/checklist.md#f-daa013-qa4-001--英文单表接入步骤的-web-控件名称与实际界面不符)保存发现与当时措辞，可按下方两处逆向替换还原全文。 |
| DAA-010 中文 `#L40`、`#L97` | 原 [QA 记录](../DAA-010-sample-facts-upload/checklist.md)分别说明预建空目录步骤及外部 GET 限制；原 Development 暂停清单中双语指南 SHA 为英文 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a` / 中文 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`。后续 QA5 和迁移前快照是不同版本，不能冒称该清单原文。 |
| 迁移前工作树双语 | [英文原字节](evidence/STAGE_C_GUIDE-before-DAA-014.md) SHA `5b40fad53bb68a4c4014c70ffa4eab1c7867425cb051536424ce62c3e5b80cb6`；[中文原字节](evidence/STAGE_C_GUIDE-before-DAA-014.zh-CN.md) SHA `fec92516e5b83023568a60bcc40992ab25510446c207f55eaeac37d7e5a03c22`。这是 DAA-014 实施前的并行脏工作树，不是 DAA-008、DAA-011 或 DAA-013 的冻结 SHA；用以保全后续修改。 |

### DAA-008 原文重建

1. 对应语言用 `git show fd999224a8756feda314a33148304b4bf3461876:automation-world/data-acquisition-agent/STAGE_C_GUIDE.md` 取得 DAA-011 QA2 字节；中文改成 `STAGE_C_GUIDE.zh-CN.md`。
2. 取该文件前四行（包含行尾），接上 [DAA-011 QA1 checklist](../DAA-011-dev-manual-refresh/checklist.md#实际命令边界与资源)中相应语言代码块的 DAA-008 原提示行 UTF-8 字节及两个 LF，再接固定 Git 版本从 `<a id="m01-launch"></a>` 起至文件末尾的全部原字节。
3. 算 SHA-256，必须等于上表对应的 `960f8d…8b8a` 或 `aa4ad5…c769`。本次在内存按此方法重建，英文 23039 字节、中文 20583 字节，均匹配，不依赖原临时目录。

### DAA-013 QA4 英文原文重建

从上述仓内英文 QA5 精确快照开始，保持其余 UTF-8 字节及换行，分别仅替换一次：

1. `After saving, open **Connection parameters** on the row and select **Copy parameters** for its three-field JSON.` → `After saving, copy the row's three-field **Access parameters**.`
2. `Save, open **Connection parameters** on the row and select **Copy parameters**.` → `Save and copy **Access parameters**.`

恢复后的全文 SHA-256 应为 `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea`。这解释 QA4 引用的 `#L102` 与 QA5 不同，不把后续修正文案倒记到失败候选。

### DAA-010 r5 中文原文重建

以仓内 `STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md` 原字节为基底，应用下列零上下文统一差异，可重建原名 `STAGE_C_GUIDE.zh-CN.md` 的 DAA-010 r5 Development 暂停候选；本次已在内存逐行应用并验证与恢复原文逐字节一致，SHA-256 为 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`。该候选第 40 行是从仓库根目录分终端启动说明，第 97 行是“7. 暂停、目标变更与恢复”。它是当时历史，不作为现行操作。英文清单 SHA 尚无可达精确原文，不用其他版本替代；原 [DAA-010 记录](../DAA-010-sample-facts-upload/tasks.md)保留其事实与限制。

```diff
--- DAA-013-QA5-STAGE_C_GUIDE.zh-CN.md
+++ DAA-010-r5-STAGE_C_GUIDE.zh-CN.md
@@ -5,7 +5 @@
-**本页说明 DS → DAA → 本地 SQLite 采集及 DAA-010 样本上报。** ARCH-ACQ-004 r2 精确候选已通过隔离独立验证；下方 r3/r4 单表步骤仅适用于已采用该合同的目标。ARCH-ACQ-004 r4 整体状态及实际环境采用以各自任务记录和授权为准；DAA 原生界面与 Windows 按各自记录处理。本手册不代表实际环境已切换。后半部分保留 DAA-008 B-RUN-01 联调历史。[阶段 B 验收](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 规格](plans/DAA-010-sample-facts-upload/spec.md)
-
-## 已有项目 dev 配置时
-
-如 DS 和 DAA 已分别使用各自的 `.local/dev`，且模拟 PLC、DB、点位和采集组已配置，先核对两应用实际选中的 profile、端点与现有配置，继续使用原目录；不必按下方隔离示例重新建目录或重新导入点表。实际后端采用和初始化按获批目标执行，先查看[项目 dev 启动说明](../../INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only)及[r3/r4 单表迁移与恢复](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md#r3-单表迁移与恢复)及 [r2 前驱迁移、导入与恢复](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md#r2-候选迁移导入与恢复冻结前驱工具)。
-
-已有待传或结果未知样本时，先核对并保全采样时的原实例 ID、PLC ID、DB 和代次；已冻结或尝试过的样本，还应核对并保留详情中已有的目标、正文和回执。待传样本可能尚未冻结，其目标、正文或回执为空并不表示丢失；不要用当前设置猜测或改写原身份。复用后端已有活跃来源时，核对它与原队列身份一致；已知旧代次不能重新登记时，先处理旧队列，新代次仅用于新采样，不给旧样本换身份。确认目标已采用后，从[来源登记与单样本核对](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本)和下方第 5–7 节继续。开始上报会逐份处理可发送队列，可能不止一份。
+**本页说明 DS → DAA → 本地 SQLite 采集及 DAA-010 样本上报。** 当前候选仍须完成对应验证，本手册不代表验收或实际运行授权。后半部分保留 DAA-008 B-RUN-01 联调历史。[阶段 B 验收](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 规格](plans/DAA-010-sample-facts-upload/spec.md)
@@ -17 +11 @@
-使用新建并显式选择的 DS profile、DAA profile 和获准的隔离后端目标。启动前核对实际地址及端口是否空闲；下表只是示例，不表示服务正在运行。使用现有项目 dev 后端、MySQL 或 `.local/dev` profile 前，须取得 [DAA-010 第 7 节](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续)的具体运行批准，才能登记、迁入或上报。
+使用新建并显式选择的 DS profile、DAA profile 和获准的隔离后端目标。启动前核对实际地址及端口是否空闲；下表只是示例，不表示服务正在运行。使用现有项目 dev 后端、MySQL 或 `.local/dev` profile 前，须取得 [DAA-010 第 6 节](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续)的具体运行批准，才能登记、迁入或上报。
@@ -92,5 +86 @@
-新空 DAA profile 建立 config2/runtime4，启动时采集和上报均停止，上报来源为空。未绑定时仍可采集；这些样本标为「仅本地记录」，之后填写绑定也不会自动排入上报队列。符合原打开条件的冷态 runtime2/3 继续使用同一目录进行本地采集及历史查看，不自动升级上报。
-
-ARCH-ACQ-004 r2 候选对通过原结构、身份和完整检查的 runtime4 提供同目录兼容：保持数据库 inode、原采集配置、样本及冻结正文，将上报身份独立保存。既有可上报记录保留原身份及目标规则。该精确候选已通过隔离独立验证，实际目标采用仍需单独完成；不能推定真实 profile 已完成升级。[QA5 记录](../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa5)
-
-若显示初始化/身份升级未完成或凭据不匹配，停止并保留整个原目录、数据库、journal、sentinel 和 staging，留待核对；不要手动删除、重建或复制文件冒充原 profile。
+新空 DAA profile 建立 config2/runtime4，启动时采集和上报均停止。符合原打开条件的冷态 runtime2/3 继续使用同一目录进行本地采集及历史查看，旧 v1 派发已退役；本候选尚无经过验证的原位上报升级，页面会说明该目录只能本地使用。原配置、样本、序号及历史回执不自动迁入、补传或删除。需要新上报时，可用正常入口选择空目录并重新配置；该目录会产生自己的实例和来源身份，须单独登记。
@@ -102,11 +92,4 @@
-1. 在获准后端，以管理员进入 Web「采集数据 → 来源配置」，按目标实际采用的版本操作：
-
-   - **已采用 r3/r4 单表的目标：**每台 PLC 登记一行，填写 `plcId`、`instanceId`、`sourceGeneration` 和 `sourceType`（DAA 选 `daa`）。`sourceType` 仅用于标注和展示，不参与 POST 准入，也不放入样本正文。POST 准入核对前三项标识。`dbNumber` 仍是样本字段和查询筛选项，不登记 DB 读写清单。保存后复制该行仅含三项标识的「接入参数」。
-   - **尚未切换的旧 r2 目标：**登记类型 `daa`、PLC ID、实例 ID、来源代次和明确授权上报的 DB，并另行授权需要读取的 DB。该目标继续按既有 DB 写入和读取范围运行。保存后复制「接入参数」。
-
-   两种目标均为新来源选择从未使用过的新代次；如有原队列并复用已有活跃来源，先核对原身份。
-2. 在 DAA「上报与存储 → 上报设置 → 上报来源」，每台本机 PLC 一行，分别手填或粘贴实例 ID、上报 PLC ID 和来源代次。不同 PLC 可以使用相同或不同实例 ID；同一上报 PLC 更换实例时须使用新代次。支持仅包含三项的 JSON，也兼容旧的带 `dbNumbers` JSON；界面的 DB 始终来自本机已生效采集配置，粘贴材料不修改 DB。暂不绑定的三项均留空。保存不会验证后端或启动上报。填写服务地址（含端口）和路径，默认路径 `/api/v1/integration/plc-facts/samples`，核对完整 URL；异机时填后端机器地址，`127.0.0.1` 是 DAA 本机。上报间隔 1–3600 秒，默认 5 秒。
-3. 保存绑定后重新采集一轮，再逐项核对目标、合同以及每个实例 / PLC / DB / 代次（含符合条件的历史待传来源），显式开始或继续上报。每个 POST 提交一份完整 PLC/DB 样本；实时和补传共用身份、原字节及回执规则。页面区分待上报、结果未知、需处理和已确认；历史 v1 确认不计入 v2。只有匹配原请求的有效 `committed` / `created|duplicate` 回执才确认，HTTP 状态或 GET 读回不能代替回执。[当前开发合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
-   在“上报记录”按状态筛选，每条记录可分别打开“查看样本”和“投递详情”；前者显示采集时保存的点值、质量和配置上下文，后者显示目标、正文摘要与只读回执。列表的 PLC 名称来自当前已保存配置，历史身份以 PLC ID 为准；找不到名称时显示 ID。状态统计变化时列表会重新读取，也可手动刷新。列宽可拖动并恢复默认。
-   “本地存储”显示运行库与回滚日志占用、待上报字节、最早待上报时间和当前生效的保留期。展开的策略表单显示草稿值；修改后，使用页面顶部配置栏保存草稿并显式激活。没有活动配置时不推断生效策略。本地历史与运行事件位于页面下方的折叠区。
-4. 另用后端 GET 或项目 Web 核对。已采用单表的目标须核对 PLC 登记及查询条件；有符合条件事实的 DB 无须登记读取清单即可读回。未切换的 r2 目标仍须确保既有读取范围覆盖该 PLC/DB。当前开发合同免机器 Bearer。自定义 POST 路径不能推导 GET 地址，需向部署方确认读取地址；无法读取时仍可查看本地样本、请求及回执。
+1. 在获准后端登记 DAA 的 `instanceId`、`plcId`、`sourceGeneration` 和 `dbNumber`。在“上报与存储 → 上报设置 → 查看接入材料”核对本地身份；页面不能证明后端登记或数据库身份。
+2. 在“上报设置”填写后端服务地址（含端口，例如 `http://127.0.0.1:38117`）和接口路径。默认路径为 `/api/v1/integration/plc-facts/samples`；部署方可提供兼容路径。后端在异机时填写后端机器的地址；`127.0.0.1` 指运行 DAA 的本机。核对预览完整 URL，按需设置 1–3600 秒上报间隔（默认 5 秒）。保存不会连接、采集或派发。
+3. 核对来源后显式开始或继续上报。每个 POST 提交一份完整 PLC/DB 样本；实时和补传共用身份、原字节及回执规则。页面区分待上报、结果未知、需处理和已确认；历史 v1 确认不计入 v2。只有匹配原请求的有效 `committed` / `created|duplicate` 回执才确认，HTTP 状态或 GET 读回不能代替回执。[当前开发合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
+4. 另用后端已配置的 GET 路由或项目 Web 核对，`readScopes` 须覆盖该 PLC/DB；当前开发合同免机器 Bearer。自定义 POST 路径不能推导 GET 地址，需向部署方确认读取地址；无法读取时仍可查看本地样本、请求及回执。
```

## 4. 实施与 DEV self-check

- 新建中英文 `USER_GUIDE`，按真实 DAA、Web 界面及合成 DB21 描述启动、配置、本地样本、三项来源参数、队列、可靠回执、两种手测和恢复。明确本机样本身份与逐 PLC 上报身份可能不同；采集与上报可分别启停。
- 精简 DAA README；采集数据通用指南保留 Web 登记、三标识、样本字段、后端两表、第三方示例、可靠回执、逐点最新值与完整历史读取，把 DAA 专属操作集中至手册。精确接口字段和限制继续指向 `contracts/`。
- 双语旧 B/C 路径改短指引；保留历史引用锚点并按第 3 节定位原文；AW、DS、DAA `src/app`、DAA-011 旧链接只调整引用目标。DAA 双语 PLAN 与任务目录仅新增本任务行。四份历史快照原字节保持。
- 实际静态走读了 DAA `FactsDeliveryDialog.vue`、`FactsDeliveryPanel.vue`、`LocalHistoryPanel.vue`、中英导航及 common locale，Web 来源配置、历史页及中英 locale，以及后端 `plc_facts` source registry、v2 service/CRUD；对照 [v2 合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) 和历史任务记录。静态走读不证明运行时行为。

实际检查（工作目录均为仓库根目录；`python3 -` 为 stdin 脚本，不运行项目服务）：

| 实际命令或方法 | 结果 |
| --- | --- |
| `shasum -a 256 automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/spec.md` | exit 0，`f34640c33b162851c8534e29b6793a81e9af638ef3eaf506575ddb878e0d736d`，与批准登记后版本一致。 |
| `shasum -a 256 automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/*` | exit 0，4 项分别匹配第 3 节的 QA5 及实施前字节摘要。 |
| `python3 -` 以 `git show fd999224a8756feda314a33148304b4bf3461876:<原路径>` 从固定对象和 DAA-011 checklist 所列提示行在内存还原 DAA-008 双语；对仓内 QA5 英文实施两处逆向替换 | exit 0，DAA-008 双语分别为 23039 / 20583 字节且匹配第 3 节 SHA；DAA-013 QA4 英文匹配 `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea`。 |
| `python3 -` 对仓内 DAA-013 QA5 中文应用第 3 节统一差异，逐字节比较已恢复的 DAA-010 中文原件 | exit 0，30728 字节，匹配 `0fe51b3153c115b146c50d86a7333475ff1fc139ae8ab8903a105b518bbff4e1`。英文该版本未定位，见限制。 |
| `python3 -` 解析 22 个受影响现行 Markdown 的相对链接、标题和显式锚点 | exit 0，检查 325 处相对链接，0 缺失；原字节历史快照内部旧相对链接按原目录解释，不作为迁移后的现行操作入口。 |
| `python3 -` 提取双语新手册、README 与通用指南的 shell 代码块，逐块交 `/bin/zsh -n`；解析通用指南 JSON 示例 | exit 0；4 个启动块及 2 个读取示例块通过，手册及 README 分别双语命令一致，2 个 JSON 示例可解析。命令只做语法解析，没有执行。 |
| `python3 -` 检查四份新增文本的行尾空白和末尾换行；`git diff --check -- <本次触达的已跟踪文档>` | exit 0；新增文本 0 空白问题，已跟踪文档 diff 无空白错误。检查范围以第 5 节文件清单为准，非本任务并行源码不计入。 |
| 中英文手册逐节人工对照 | 六个编号章节、合成地址/点值、两种手测、回执条件、暂停及恢复口径相互对应；界面标签来自实际中英文 locale。 |

本次 Development 未执行构建、产品运行、HTTP 写入、数据库/SQLite、PLC/DS、Docker 或应用启停；没有读取或更改真实 `.env`、profile、样本与历史。两个手测系协调者转交的 Human Owner Mac/dev 观察，不是本角色重新测试，也不代替 DAA-010 r5 独立 QA、Windows 验证、阶段 C 或 Human Owner 终验。DAA-010 暂停清单中的英文旧指南 SHA 目前没有可达精确原文；中文可按上文重建，不能以其他版本冒充英文原件。截图或浏览器渲染未检查。

上表的已跟踪文档 whitespace 检查实际参数如下（未跟踪的新文本由上表 Python 检查）：

```sh
git diff --check -- automation-world/README.md automation-world/README.zh-CN.md \
  automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/USER_GUIDE.zh-CN.md \
  automation-world/data-acquisition-agent/README.md automation-world/data-acquisition-agent/README.zh-CN.md \
  automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md \
  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md \
  automation-world/data-acquisition-agent/PLAN.md automation-world/data-acquisition-agent/PLAN.zh-CN.md \
  automation-world/data-acquisition-agent/plans/README.md automation-world/data-acquisition-agent/plans/README.zh-CN.md \
  automation-world/data-acquisition-agent/src/app/README.md automation-world/data-acquisition-agent/src/app/README.zh-CN.md \
  docs/README.md docs/README.zh-CN.md
```

资源：本角色没有创建分支、worktree、运行环境或临时测试文件。协调者为本次证据恢复创建的 `/private/tmp/daa014-qa5-recovered-gb7uiz85` 和 `/private/tmp/daa014-daa010-recovered-hgcrsiv8` 在本角色确认仓内复现后，由该协调者核对归属并回收。Verification 以仓内快照、任务差异和固定 Git 对象为准，不依赖这两个临时目录；其他任务资源未触碰。

## 5. 变更文件与 developer_handoff

正式交付为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 共享工作树，HEAD `fd999224a8756feda314a33148304b4bf3461876`；包含任务开始前已存在的并行 dirty 变更。下面摘要固定本任务交付文件的当前全文件内容，并不表示 Git HEAD 即这些未提交内容，也不把其他任务的差异记成本任务。`tasks.md` 不在自身哈希清单中，交接时另行计算。

```text
d7c8a3052e47a6700b8e8de9bb31465945c3e6b43bd88354578b92946f6f1559  automation-world/README.md
88e2c48fd39151908473fb106c924f53d372e7f305640d76039928223371cec3  automation-world/README.zh-CN.md
d13cf518834f7178cd62725a3b15f3ad68e42922004bd68137a4e878eb05d164  automation-world/device-simulator/USER_GUIDE.md
eb1d746db4eb2bc8d08d4092a87fd94d4f3e8b6cf33a5519bbb097e360c8aba1  automation-world/device-simulator/USER_GUIDE.zh-CN.md
d7d28953c3015a3668e14ad3f8612f7da0d922bcb9e9000e226af14fbbc883bf  automation-world/data-acquisition-agent/README.md
1c34165c2867c489c99b8551b404006f5fd3b01cb28520cb9797209d766b3842  automation-world/data-acquisition-agent/README.zh-CN.md
cbc0e0df732679e2bca1005da459591401ed8f5be0c37ccec3b82a4d85f1a4f5  automation-world/data-acquisition-agent/USER_GUIDE.md
28d16366ba4479acc506a1f049cf0e265b804c2d5f4307c51fb02ebc04a83433  automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md
8e513160afbcb17ccce378359526b06cc36dff457951a0376cae35b8314dc416  automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md
eb287750a872157782cfd4db73fe1bdf05a0b597323448e6fbb808ca73ec40e8  automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md
58fa3f4c7366a0316ef44ac8930d4099cd770fd2e89a1a201ff4d4099354331e  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
9e9cf35fe511c5de86ba8a49e79be5d257f9aa887bec31b329ef1e77056169c9  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
ec8438c49f7d935869e81a15ed6c2a8cda0a809609319ba074c257cab527ae6a  automation-world/data-acquisition-agent/PLAN.md
f4577eb4d5ae0b9019c19e23081156469011b2a247989d82581a1387f54aac79  automation-world/data-acquisition-agent/PLAN.zh-CN.md
048623bcdd94147635fbaa744be8bc587a94bc9b1b2051ccf8a00d518310ba85  automation-world/data-acquisition-agent/plans/README.md
6f07d38991cd2e313d7561bb7575d1a1cfa11b765e10b7d9e10b4824bc1e6a2f  automation-world/data-acquisition-agent/plans/README.zh-CN.md
da24e7c3040bc1af3df092c895c92045ff8f631094fd5e6374314f52b8e5a60c  automation-world/data-acquisition-agent/src/app/README.md
e6a65fcc570d8ac1fb8980457046e8a17232239f720054e280d2af5a39eca80d  automation-world/data-acquisition-agent/src/app/README.zh-CN.md
69bb3f8d3f664ed8a81ee937099e3b821da7432dbbce5b7e77ff4e33006c3a89  docs/README.md
fe9acbaf70eed46fc3e2827df3c64771dcc6634b4055b0fe8e4c5fded074980f  docs/README.zh-CN.md
7aca7eb62e49865184d80764eae9ad01d49740d7dddc5912811ce665be79c1f5  docs/acquisition-data-guide.zh-CN.md
15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md
a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md
5b40fad53bb68a4c4014c70ffa4eab1c7867425cb051536424ce62c3e5b80cb6  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.md
fec92516e5b83023568a60bcc40992ab25510446c207f55eaeac37d7e5a03c22  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.zh-CN.md
```

**developer_handoff**：请协调者将 DAA-014 r1、上述正式工作树/文件摘要、完整任务 bundle、实施差异、DEV self-check、手测转交、历史材料及已列限制交给新的 fresh-context Verification。Verification 应自行核对现行源码和文档，不要求重跑采集或发出 HTTP 写入。此交接不是 QA verdict、Human Owner 最终验收或阶段 C 完成。

## 6. QA1 返工与英文历史原文

本次在同一获批 DAA-014 r1 正式工作树返工。原 §1–5 的 `developer_handoff`、当时摘要、检查和英文未定位限制逐字保留；[QA1 checklist](checklist.md) SHA-256 为 `972ddaff594b417ef2f006ba90d13d18a6c51289889885f9f5b70af52ba1e247`，其中 `qa_failed` 与 F-001–F-003 保持原记录。下述是返工事实与 Development 自检，不替代独立复验。

- **F-001：** 双语第 4、5 节区分未冻结样本的本机可见信息与发送前确认框提供的全部来源集合；确认框不把来源行映射到单个 `sampleId`。核不清来源及当前 URL 时停止；冻结或尝试后，按实际请求正文和可靠回执逐条核对。Web 以请求中的上报 PLC ID 查询，不以本机名称或本机 ID 替代。
- **F-002：** 双语第 4、6 节说明已冻结 `prepared` 且 `attempt=0` 的样本经核对和显式继续可使用新目标而身份/正文不变；已尝试未确认样本保留原目标，结果未知的换址按原同一 provider 和数据库确认规则处理。
- **F-003：** 协调者找回的英文 DAA-010 r5 Development 暂停候选由原 QA 复核，并由本角色重算 SHA。以下以仓内 [DAA-013 QA5 英文快照](evidence/STAGE_C_GUIDE-DAA-013-QA5.md)为基底，应用零上下文统一差异，在内存重建原名 `STAGE_C_GUIDE.md` 的英文原文。实际重建 34534 字节，与找回文件逐字节相同，SHA-256 为 `2302cb15f374b9f29d4bda8715f69f8ce6d0323f6c37a8729208e4292d1ba35a`。这补足原 §3、§4 在首次交接时如实记录的英文缺口；仍仅有四份完整快照，不将临时路径作为持久依据。历史原文仅供追溯。

```diff
--- DAA-013-QA5-STAGE_C_GUIDE.md
+++ DAA-010-r5-STAGE_C_GUIDE.md
@@ -5,7 +5 @@
-**This walkthrough covers DS → DAA → local SQLite and the DAA-010 sample uploader.** The exact ARCH-ACQ-004 r2 candidate passed independent isolated verification; the r3/r4 single-table steps apply only to targets that have adopted that contract. ARCH-ACQ-004 r4 status and actual environment adoption follow their own task records and authorizations. DAA native UI and Windows remain subject to their own records. This guide does not imply that an existing environment has been switched. The second half retains the DAA-008 B-RUN-01 joint-test history. [Stage B acceptance](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 specification](plans/DAA-010-sample-facts-upload/spec.md)
-
-## Reusing an existing project dev setup
-
-If DS and DAA already use their respective `.local/dev` profiles and the simulated PLC, DB, points and collection group are configured, check the selected profile, endpoint and configuration in each app and continue in those directories. There is no need to create new profiles or reimport points from the isolated example below. Adopt and initialize the actual backend under the approved target procedure; see [host-source project dev](../../INITIALIZATION.md#host-source-development-with-database-only) and [r3/r4 single-table migration and recovery](../../backend/scripts/plc_facts_maintenance/README.md#r3-single-table-migration-and-recovery) and [r2 predecessor migration, import and recovery](../../backend/scripts/plc_facts_maintenance/README.md#r2-candidate-migration-import-and-recovery-frozen-predecessor-tooling).
-
-When pending or unknown samples exist, check and preserve the instance ID, PLC ID, DB and generation captured at sampling. For samples already frozen or attempted, also check and retain the target, body and receipt where present in their details. A pending sample may not yet be frozen, so its target, body or receipt can be empty; do not infer or rewrite its original identity from the current settings. If reusing an existing active backend source, check that it matches the queued identity. If a known old generation cannot be registered, resolve the old queue first and use a new generation only for new samples; do not reassign old samples. After target adoption, continue with [source registration and single-sample reconciliation](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本) and sections 5–7 below. Starting reporting processes the eligible queue one sample at a time and may send more than one sample.
+**This walkthrough covers DS → DAA → local SQLite and the DAA-010 sample uploader.** The current candidate still requires its specified verification; do not treat this guide as an acceptance or operating authorization. The second half retains the DAA-008 B-RUN-01 joint-test history. [Stage B acceptance](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 specification](plans/DAA-010-sample-facts-upload/spec.md)
@@ -17 +11 @@
-Use a new, explicitly selected DS profile, DAA profile and an approved isolated backend target. Check the actual addresses and that the intended ports are free before starting; the values below are examples, not a claim that any service is running. The existing project dev backend, MySQL and `.local/dev` profiles require the separate operating authorization described in [DAA-010 §7](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续) before registration, migration or delivery.
+Use a new, explicitly selected DS profile, DAA profile and an approved isolated backend target. Check the actual addresses and that the intended ports are free before starting; the values below are examples, not a claim that any service is running. The existing project dev backend, MySQL and `.local/dev` profiles require the separate operating authorization described in [DAA-010 §6](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续) before registration, migration or delivery.
@@ -92,3 +86 @@
-A new empty DAA profile initializes config2/runtime4 with collection and upload stopped and reporting identity empty. An unbound PLC can collect; its samples are marked local only and do not enter the upload queue when a binding is later saved. A cold runtime2/3 profile that passes its original admission checks continues local collection and history at the same path, without automatic upload upgrade.
-
-The ARCH-ACQ-004 r2 candidate adds a same-directory runtime4 compatibility path after the original structure, identity and integrity checks. It preserves database inode, acquisition configuration, original samples and frozen request bytes, and stores reporting identities separately. Existing eligible records keep their original identity and target rules. The exact r2 candidate passed independent isolated verification; actual target adoption remains separate and must not be assumed for a real profile. [QA5 record](../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa5) On an incomplete initialization/identity upgrade or credential mismatch, stop and preserve the entire original directory, databases, journals, sentinel and staging; do not manually remove or recreate them.
+A new empty DAA profile initializes config2/runtime4, with collection and upload stopped. A cold runtime2/3 profile that passes its original admission checks continues local collection and history at the same path; v1 dispatch is retired. This candidate has no verified in-place reporting upgrade, and the page identifies such a directory as local-only. Existing configuration, samples, sequences and historical receipts are not automatically migrated, replayed or deleted. To use new reporting, select an empty directory through the normal entry and configure it again; its new instance and source identities require registration.
@@ -100,11 +92,4 @@
-1. On an approved backend, an administrator opens **Acquisition data → Source configuration** and follows the rules of the target's adopted version:
-
-   - **Adopted r3/r4 single-table target:** register one row per PLC with `plcId`, `instanceId`, `sourceGeneration` and `sourceType` (`daa` for DAA). `sourceType` only labels and displays the source; it is not part of POST admission or the sample body. POST admission matches the first three identifiers. `dbNumber` remains a sample field and a query filter; no DB read or write list is registered. After saving, open **Connection parameters** on the row and select **Copy parameters** for its three-field JSON.
-   - **Older r2 target not yet switched:** register the `daa` source with PLC ID, instance ID, generation and the explicitly authorized reporting DBs; separately authorize the DBs to read. This target continues to use its existing DB write and read scopes. Save, open **Connection parameters** on the row and select **Copy parameters**.
-
-   For either target, use a never-used generation for a new source. If an old queue exists and an active source is reused, check its original identity first.
-2. Under DAA **Reporting and storage → Delivery settings → Reporting sources**, enter or paste instance ID, reporting PLC ID and generation separately on each local PLC row. Different PLCs may use the same or different instance IDs; changing the instance for a reporting PLC requires a new generation. Paste accepts the three-field JSON or the older JSON with `dbNumbers`; displayed DBs always come from the active local acquisition configuration and paste does not alter them. Leave all three fields blank for an unbound PLC. Saving does not verify backend registration or start delivery. Enter the backend address including port and API path, default `/api/v1/integration/plc-facts/samples`, and check the combined URL. For a remote backend use that machine's address; `127.0.0.1` is the DAA machine. The interval is 1–3600 seconds, default 5.
-3. Collect a new cycle after saving the bindings, then check the target, contract and each instance / PLC / DB / generation, including eligible historical pending sources, before explicitly starting or resuming reporting. Each POST contains one complete PLC/DB sample; live and backlog use the same identity, original bytes and receipt rules. The page separates pending, unknown, needs-processing and confirmed; historical v1 confirmations are separate. Only a matching valid `committed` / `created|duplicate` receipt confirms a sample, not an HTTP status or GET result. [Current development contract](../../contracts/published/http-api/plc-facts-v2/README.md)
-   In **Reporting records**, filter by state and open **View sample** or **Delivery details** for a row. The former shows the saved point values, quality and configuration context; the latter shows the target, body digest and read-only receipt. List PLC names come from the currently saved configuration; the PLC ID identifies the historical source and is shown if no current name exists. The list reloads when status counts change and can also be refreshed manually. Column widths can be dragged and reset.
-   **Local storage** shows runtime and rollback-journal usage, pending bytes, oldest pending time and the active retention period. The expanded policy form shows draft values; after editing, save the draft and explicitly activate it using the configuration bar at the top. No active policy is inferred when no configuration is active. Local history and runtime events are in the collapsible sections below.
-4. Check readback using the backend's configured GET routes or project Web. For an adopted single-table target, check the PLC registration and query conditions; DBs with qualifying facts can be read without a registered DB read list. On an unswitched r2 target, the existing read scope must cover the PLC/DB. The current development contract needs no machine Bearer. A custom POST path does not reveal the GET address: ask the deployer for it. Local samples, requests and receipts remain available if readback is unavailable.
+1. Have the approved backend register the DAA `instanceId`, `plcId`, `sourceGeneration` and permitted `dbNumber`. Check local identities under **Reporting and storage → Upload settings → View source material**; this does not prove backend registration or database identity.
+2. In **Upload settings**, enter the backend service address including its port, for example `http://127.0.0.1:38117`, and the API path. The default is `/api/v1/integration/plc-facts/samples`; a deployment may supply a compatible path. For a remote backend enter that machine's address; `127.0.0.1` means the machine running DAA. Check the combined URL and optionally set the 1–3600 second interval (default 5). Saving starts no connection, collection or dispatch.
+3. After checking registration, explicitly start or resume reporting. Each POST contains one complete PLC/DB sample; live and backlog use the same identity, original bytes and receipt rules. The page separates pending, unknown, needs-processing and confirmed; historical v1 confirmations are separate. Only a matching valid `committed` / `created|duplicate` receipt confirms a sample, not an HTTP status or GET result. [Current development contract](../../contracts/published/http-api/plc-facts-v2/README.md)
+4. Check readback using the backend's configured GET routes or project Web; `readScopes` must cover the PLC/DB. The current development contract needs no machine Bearer. A custom POST path does not reveal the GET address: ask the deployer for it. Local samples, requests and receipts remain available if readback is unavailable.
```

### 返工 DEV self-check

| 实际命令或方法 | 结果 |
| --- | --- |
| `shasum -a 256` 复核 spec、QA1 checklist、两份新手册、已找回的英文原件 | exit 0；spec 和 QA1 checklist 分别匹配 `f34640…d736d`、`972dda…e247`；英文原件匹配 `2302cb…e770`。 |
| `python3 -` 使用仓内两份 QA5 快照与本任务两段统一差异，在内存恢复 DAA-010 r5 双语 | exit 0；中文 30728 字节、英文 34534 字节，分别匹配 `0fe51b…ff4e1` 和 `2302cb…e770`；`evidence/` 仍为四份完整快照。英文重建还与协调者找回的原件逐字节一致，后续复验不依赖临时路径。 |
| `python3 -` 将本节之前的原 handoff 原字节按追加边界分离、重算摘要，对原 25 项清单逐项比较 | exit 0；原 handoff 保持 SHA `b926f0…dee`，原清单中只有两份手册因本轮返工不同，其余 23 项不变。首次自检误在原 handoff 已有换行之外又补一个 LF，断言 exit 1；移除多余 LF 后重算 exit 0。 |
| `python3 -` 解析两份新手册及本任务记录中的相对链接/锚点、检查行尾空白 | exit 0；3 文件 34 个相对链接/锚点可达，3 文件 0 空白问题。历史快照保留原字节，其内部相对链接按原目录解释。 |
| `python3 -` 对照双语六节、核对本轮上报身份/回执关键术语，将两个手册启动块传给 `/bin/zsh -n` | exit 0；两份六节一致，两个启动块均通过且命令相同。仅语法解析，没有执行项目命令。 |

英文差异首次尝试用含非 ASCII 正文的 stdin Python 脚本写入任务时发生源码编码 `SyntaxError`，exit 1、没有写入；随后使用补丁追加中文事实，再以纯 ASCII stdin 脚本生成和核验差异，exit 0。未运行服务、构建、HTTP、数据库或设备，未访问或更改真实 profile 和 31 条样本；本轮依然不做 QA verdict 或 Owner 验收。协调者自有 `/private/tmp/daa014-daa010-en-_u1kus0d` 不再是复现依赖，保留/回收由协调者依照 QA1 的资源记录处置。

### 返工后的精确交接清单

工作树与 HEAD 保持 §1：`/Users/jason/Desktop/DreamCode/aiis-ics-arch` / `fd999224a8756feda314a33148304b4bf3461876`。下面列出本轮交接的 25 项当前完整文件 SHA-256；`tasks.md` 的最终摘要在交接时单独计算。QA1 已有失败记录和原 §5 清单继续保留。

```text
d7c8a3052e47a6700b8e8de9bb31465945c3e6b43bd88354578b92946f6f1559  automation-world/README.md
88e2c48fd39151908473fb106c924f53d372e7f305640d76039928223371cec3  automation-world/README.zh-CN.md
d13cf518834f7178cd62725a3b15f3ad68e42922004bd68137a4e878eb05d164  automation-world/device-simulator/USER_GUIDE.md
eb1d746db4eb2bc8d08d4092a87fd94d4f3e8b6cf33a5519bbb097e360c8aba1  automation-world/device-simulator/USER_GUIDE.zh-CN.md
d7d28953c3015a3668e14ad3f8612f7da0d922bcb9e9000e226af14fbbc883bf  automation-world/data-acquisition-agent/README.md
1c34165c2867c489c99b8551b404006f5fd3b01cb28520cb9797209d766b3842  automation-world/data-acquisition-agent/README.zh-CN.md
7ffc201d39ab919a180ff03bcef0b8c4a944a4cd4599319836af57c6e7ee8e50  automation-world/data-acquisition-agent/USER_GUIDE.md
3c337d6984d31068bab4b658bddcf24049ad125ac20156a5dc8bd72c39492557  automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md
8e513160afbcb17ccce378359526b06cc36dff457951a0376cae35b8314dc416  automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md
eb287750a872157782cfd4db73fe1bdf05a0b597323448e6fbb808ca73ec40e8  automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md
58fa3f4c7366a0316ef44ac8930d4099cd770fd2e89a1a201ff4d4099354331e  automation-world/data-acquisition-agent/STAGE_C_GUIDE.md
9e9cf35fe511c5de86ba8a49e79be5d257f9aa887bec31b329ef1e77056169c9  automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md
ec8438c49f7d935869e81a15ed6c2a8cda0a809609319ba074c257cab527ae6a  automation-world/data-acquisition-agent/PLAN.md
f4577eb4d5ae0b9019c19e23081156469011b2a247989d82581a1387f54aac79  automation-world/data-acquisition-agent/PLAN.zh-CN.md
048623bcdd94147635fbaa744be8bc587a94bc9b1b2051ccf8a00d518310ba85  automation-world/data-acquisition-agent/plans/README.md
6f07d38991cd2e313d7561bb7575d1a1cfa11b765e10b7d9e10b4824bc1e6a2f  automation-world/data-acquisition-agent/plans/README.zh-CN.md
da24e7c3040bc1af3df092c895c92045ff8f631094fd5e6374314f52b8e5a60c  automation-world/data-acquisition-agent/src/app/README.md
e6a65fcc570d8ac1fb8980457046e8a17232239f720054e280d2af5a39eca80d  automation-world/data-acquisition-agent/src/app/README.zh-CN.md
69bb3f8d3f664ed8a81ee937099e3b821da7432dbbce5b7e77ff4e33006c3a89  docs/README.md
fe9acbaf70eed46fc3e2827df3c64771dcc6634b4055b0fe8e4c5fded074980f  docs/README.zh-CN.md
7aca7eb62e49865184d80764eae9ad01d49740d7dddc5912811ce665be79c1f5  docs/acquisition-data-guide.zh-CN.md
15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.md
a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-DAA-013-QA5.zh-CN.md
5b40fad53bb68a4c4014c70ffa4eab1c7867425cb051536424ce62c3e5b80cb6  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.md
fec92516e5b83023568a60bcc40992ab25510446c207f55eaeac37d7e5a03c22  automation-world/data-acquisition-agent/plans/DAA-014-unified-operator-guide/evidence/STAGE_C_GUIDE-before-DAA-014.zh-CN.md
```

**返工 developer_handoff**：将精确 DAA-014 r1、上述正式工作树及 25 项摘要、本任务完整记录、QA1 checklist、双语手册与本轮自检交新的 fresh-context Verification；F-001–F-003 是否关闭由该角色独立判断。原 DAA-010 r5 qa_failed、Windows 原生、阶段 C、实际环境采用及 Human Owner 终验仍按各自 gate。
