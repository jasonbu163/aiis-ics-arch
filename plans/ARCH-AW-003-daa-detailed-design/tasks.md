Task ID: ARCH-AW-003
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Exact ARCH-AW-003 r3 DAA documentation and DEV self-check in current working tree to NEW fresh-context Verification; r1/r2 retained as history and Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA 详细设计 r3 Development 记录

## r3-1. 批准、消费依据和基线

Human Owner于2026-10-17（Asia/Shanghai）精确批准ARCH-AW-003 r3，原话和历史见[spec](spec.md)§1；批准后spec为owner_approved，SHA-256 `91b294a22644a69ad3de8297e35e744114f4c480d425790a8e6e8568ff814fd2`。本实际Development角色仅写下表6文件；PM/QA/协调归属不写，r1/r2 DEV完整原文与元数据快照保留在本文件后部，r2独立QA不自动升级r3。Human Owner终验仍pending。

已读根AGENTS、README/PLAN双语、canonical workflow、development TOML、完整spec/tasks/checklist、docs/AW/DAA/CU最近README/PLAN（存在者）、r2 DAA全文与SMA/AW Runtime共享边界；只读核对CU公共代码/样式/类型/侧栏/壳/顶栏/公共方案、DAA App/旧布局/PLC domain/采集Service/S7 adapter。作用域检索无额外AGENTS；docs为README-only，DAA无本地PLAN，不新增治理入口。应用`aiis`及BLUEPRINT/CONTRACTS、`project-governance`处理设计/历史与角色边界，不加载未来实现skill扩大范围。

当前HEAD `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，现有dirty working tree交付，无新commit/分支/worktree。主协调证据 `/private/tmp/arch-aw-003-r3-exec-wgubo80i/` 的baseline.json固定1601路径、12 allowlist/1589 protected，approved-spec.md/json固定批准，pre-development-snapshot.json为本角色阶段起点；dev/before保存6文件原字节。当前SMA/AW Runtime仍为r2原指纹。并发dirty不归本任务，不reset/覆盖/整理。

## r3-2. 实际文件、顺序和影响

| 顺序 | 唯一写入面与内容 | 需求/验收映射 |
| --- | --- | --- |
| DEV-1 | docs/AIIS_DAA_Detailed_Design.md：保持16节；§1修订/现状/历史，§2控制配置事实反馈图与Rust所有权，§8有界等待，§10响应确认表/三包示例与身份，§11事实/业务分层，§12 CU/导航/四页及简单流程，§16三候选阶段 | R18–R27；AC21–AC34 |
| DEV-2 | docs/README.md、README.zh-CN.md：仅现有DAA设计行的双语用途补充 | R18/R27；AC34 |
| DEV-3 | automation-world/data-acquisition-agent/README.md、README.zh-CN.md：仅原目标设计段的双语CU/页面/数据流/例子/阶段补充 | R18/R27；AC34 |
| DEV-4 | 本tasks增补r3真实实施、自检、精确handoff；r2元数据围栏及原正文/嵌套r1逐字保留 | R28；AC35 |

原§3–7、§9、§14–15全文不变，F01–F30及三方责任表保持；§10.2/10.4/10.6保持，§10.5仅改历史引导措辞。SMA/AW Runtime正文、SMA/CU/AW入口及全部源码/配置/依赖/测试受字节保护。当前代码仍旧YAML/直库/自有壳，目标能力没有因文档出现而实现。

## r3-3. DEV self-check

以下仅Development自检，不是独立QA。系统Python标准库只作/private/tmp文档/JSON/指纹辅助，不导入工程代码或改环境；本轮无应用/工程测试运行。辅助环境Python 3.9.6、Git 2.50.1（Apple Git-155）。

| 实际命令/检查 | 退出码/结果 |
| --- | --- |
| `rg --files -g AGENTS.md -g 'AGENTS.*'`及必读cat/sed，`git rev-parse HEAD` | 0；无额外作用域AGENTS，HEAD/现状/批准与完整bundle消费；未生成新PLAN或角色文档 |
| `python3 /private/tmp/arch-aw-003-r3-exec-wgubo80i/dev/revise-docs.py` | 0；原位修订DAA，616→774行，差异+216/-58；四入口各恰好一行替换，其他条目/命令块不变 |
| `python3 /private/tmp/arch-aw-003-r3-exec-wgubo80i/dev/write-tasks.py` | 0；r3事实面与r2完整原文/嵌套r1历史形成；r2历史可按围栏拆回原字节 |
| `python3 /private/tmp/arch-aw-003-r3-exec-wgubo80i/dev/audit.py audit-first.json` | 0，errors=[]；6文档74本地链接/锚点、39表格、11对围栏、1JSON，16节及F01–F30/保护章节检查通过；三包cycle/manifest/原身份/点自描述一致；1601库存无增删，1589 protected及1595非DEV路径不变 |
| audit通过argv展开6文件运行 `git diff --check -- <6 paths>` | 0，无输出；未跟踪DAA全文另以标准库原文diff与行尾检查纳入，未使用空Git diff作证明 |
| `sed -n`逐段审阅完整dev/scoped.diff及r2共享边界；`rg -n`核对write_snapshot/record_success/标量读取/递归to_camel | 0；源码现状符合目标未实现说明；双语入口意义对称、SMA/其他文档入口与模块命令不变；R26语义对读见下一表 |

全部实施/首轮自检命令无失败；关键词计数仅作存在性辅助，不代替语义审阅。最终handoff落盘后已执行 `python3 /private/tmp/arch-aw-003-r3-exec-wgubo80i/dev/audit.py final-audit.json`，exit 0、errors=[]；74本地链接/锚点、41表格、11对围栏、1JSON、1601库存/1589 protected及1595非DEV路径保持。已保存final-manifest.json固定批准/6文件最终指纹；写入本实际结果后再以同命令复核并刷新manifest。本自检不构成独立QA。

## r3-4. 语义回归对读

| 核对面 | 对读位置及结果范围 |
| --- | --- |
| R18–R21 / AC21–AC26 | §1/12：CU两公共入口/八组件/展示类型、宿主与私有层边界、平铺现状与独立CU二级依赖；工作台+配置中心3子页。草稿/持久active/实际已用分别反馈；连接/采集/上传分开，部分成功；首次无样本只校验预览，测试可选不阻断保存/采集，采后原身份测试或直接上报，无强制往返。 |
| R22 / AC27–AC28 | §2图/职责及§5：控制经IPC/Rust校验；草稿/摘要/active/加载屏障分步可恢复；事实先runtime提交再上传；可靠回执先本地ack后反馈。快照收敛显示、有界日志/订阅、UI无事实写权限/时钟/队列，切页不推定退出托管。 |
| R23–R24 / AC29–AC31 | §8/10.1.1/10.3：A10/A20同组同轮同源seq、不同sample与原时间；B10独立不冲突；两manifest及固定片、sample/point/cycle/batch分清。限额前拆批、冻结后拒绝不改旧批；不丢中间样本或造同步帧。单在途只是建议，客户端超时不证明服务端取消；整批原子确认仍推荐，200/202不自动ack，部分/过期矩阵正式合同再定。 |
| R25 / AC32 | §16：A先CU能力与旧UI迁移，保旧gate/接口、缺功能不假成功；B本地配置/采集/容量/恢复不等Backend/SMA；C正式Backend合同先稳定再各自实现联调。每阶段有范围/依赖/证据/回退，现场/长稳/原生/生产切换另批。 |
| R26 / AC33：连接/结构/组 | 对比起点§3–4原字节：唯一受管理会话与诊断有界公平、人工断开/异常重连、独立意图；完整DB/UDT/手动受限推算与修正、单PLC跨DB/点最多一组、唯一enabled、非重入/不补造遗漏tick保持。 |
| R26 / AC33：双库/容量/身份 | 起点§5–7原字节：短事务/单写/可恢复屏障，不假跨WAL原子；配置回退不倒退seq/ack；本地提交起持久保证。保护未确认/需处理/冻结/未完整材料，计WAL/日志/维护/实际空间，满额停新轮次但上传继续，低水位仅恢复原意图；冻结交叠批次/单调ack/引用钉住保持。 |
| R26 / AC33：来源/完整性 | 起点§9原字节：受控代次、持久PLC内seq/跨PLC不比、manifest与质量/缺片/过滤跳号分清，B不等M；§10.2安全feed防晚提交保持。新例子A先到一包不完成轮次；优先和公平历史均保中间样本。 |
| R26 / AC33：定义/窗口/兼容 | §10.4/10.6及§13保持，§10.5原UTC三自然月规则保持：单份points/派生合并目录、显式成员/版本、逐绑定签名排除采样/无关revision、物理程序变而定义未报不可自动证明。逐点到期/不接收续期，拒绝不假ack/删保护，业务/outbox独立持久与TTL；旧标量适配、单writer切换另批。SMA仅对读共享边界，字节不动。 |
| R27–R28 / AC34–AC35 | 6文档最小入口与历史重建、批准/保护指纹、本地链接/锚点/围栏/表格/JSON及全文diff另检；F01–F30原字节/责任不变。后续须新fresh-context Verification记录verdict，不使用旧QA代替。 |

## r3-5. 限制、资源和下一gate

Mermaid只做文本/职责审阅，未渲染；示意JSON解析仅证明语法和本例身份一致，不是正式Backend schema验证。没有新增官方技术结论或外部联网事实；CU现状以本地公共源核对，既有外部引用保留，不把它们重标本轮在线核验。未安装依赖、构建/启动应用、跑项目测试、创建/读取数据库或SQLite、连PLC/HTTP、跑Docker/迁移、推送/发布、给Backend/SMA会话发消息。

CU二级导航与DAA消费未实现；正式字段/manifest/回执/混合结果/批次退休、驱动/地址支持/规模/周期、SQLite版本/参数/额度、平台退出/后台托管与现场证据仍需各端精确任务。首版整批原子ACK/单在途是推荐，不能据此声称正式协议定稿或可靠性已运行通过。

本角色只创建父证据目录dev/中的before/原文、initial-status.txt、revise-docs.py、write-tasks.py、finalize-tasks.py、audit.py、scoped.diff及审计/最终manifest；主协调baseline/approved/pre-development为输入依赖。r1/r2历史证据继续按原记录保留供QA/终验复核；无进程/数据库/容器/分支/worktree或外部持久资源，不清理。长期命令/结果/指纹/限制记录在bundle，临时目录不是唯一事实源。

## r3-6. 精确 developer_handoff

交接目标`aiis-ics-arch::ARCH-AW-003 r3`，状态developer_handoff，在上述HEAD的当前dirty working tree，无新commit。批准spec SHA-256仍为 `91b294a22644a69ad3de8297e35e744114f4c480d425790a8e6e8568ff814fd2`；请主协调随后显式启动**新的**`verification`、`fork_turns="none"`，读取完整批准bundle/当前正文、dev/before、全文scoped.diff、self-check及final-manifest。QA独立核验AC21–AC35、R26受影响回归与全范围保护，不使用本自检或旧QA代替verdict，且只写checklist；之后Human Owner最终验收。

5个设计/入口最终指纹如下；tasks不能自存自身稳定指纹，其最终SHA与全部6文件指纹在外置final-manifest.json和Development消息交接给协调，便于新QA固定。

| 文件 | SHA-256 |
| --- | --- |
| `docs/AIIS_DAA_Detailed_Design.md` | `20071f25c374f40ee4600bffda4aef13f37bb86a82c2a6cd1f19e2580370a576` |
| `docs/README.md` | `5e05bd81a1042e1bc2e92b8099d8a59219a59a7fd3d4be3595848b64878bd903` |
| `docs/README.zh-CN.md` | `ef51b6548e779f65c21e0201016c8c5ff4c5f9fc5f90b5f61e33e6f16afd2073` |
| `automation-world/data-acquisition-agent/README.md` | `7a12bb592bdf151576ae148d3016c650269ce37954cf1b53ba452bfb8803fc50` |
| `automation-world/data-acquisition-agent/README.zh-CN.md` | `4c79d729a45da47074454d8e6cacaec798ce2fb3c73130f4da08dc4390393498` |

保护SMA指纹 `e849bec4a4e29e587f16915b99b7e29d3774355b5d649be3b2f89ac724ea94b7`，AW Runtime指纹 `1d4b34e10c72555fcdbc2850d5ee54ecb43b2507b5c102e1414e35f0ec8d59fa`，旧r2 checklist指纹 `a6f2abb69280d5732f62deda901b3d27918a5eaa0f95cecbca53f52406683cf8`；本角色均未改动。根四索引本轮仍为owner_approved，由主协调在真实handoff后机械同步。

当前profile为contract_only，不宣称平台ACL/强制路由，不给QA verdict或最终验收。

---

# r2 Development 历史记录（原文保留）

以下元数据与正文为2026-10-17的完整r2交接，原文件SHA-256 `2e2a0f4e04a22d0bb633698e680d78fbd6c94006613e78b3d03a546031d3f611`；含原r1历史。旧pending表述仅指当时gate，不替代后续独立checklist；本版不继承旧通过。

```text
Task ID: ARCH-AW-003
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Exact ARCH-AW-003 r2 documentation and DEV self-check to new fresh-context Verification; r1 retained as history and Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

```

# DAA/SMA 详细设计 r2 Development 记录

## r2-1. 精确批准、基线与当前效力

Human Owner 于 2026-10-17（Asia/Shanghai）精确批准 ARCH-AW-003 r2，原文见 [spec](spec.md) §1。读取时为 owner_approved，SHA-256：`a6464506e3e8d86e55cc98415e4a4af9f91ab815598411bc3ec2d26676696537`。本角色没有写 spec/checklist 或根4索引；r1 tasks 正文/元数据快照/原指纹保留在本文件后部，r1 QA 仍为历史，Human Owner 未终验，不能覆盖 r2。

已读根 AGENTS、双语 README/PLAN、Development TOML/canonical workflow、完整 r2 spec 和 r1 tasks/checklist、docs/AW/DAA/SMA 最近 README/PLAN（存在者）、当前 DAA/AW 设计，projection-mapping README/PLAN；只读复核 DAA domain/Service/adapter、SMA API materials store/managed runtime、Backend Projection input resolver/common serializer。当前代码仍是旧路径，文档没有改写成已实现。

适用 aiis/project-governance 与既有 CONTRACTS 边界，本会话前次已读取 skills；本次只修中文长期设计和入口，不冻结驱动、API/DDL、Rust/UI，未加载全部未来实现 skills。本轮只浏览必要官方资料，不取实际项目 OpenAPI 或调用业务 API。

工作树 HEAD：`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，无新 commit/分支/worktree。主协调基线 `/private/tmp/arch-aw-003-r2-gc842o4s/` 含16 allowlist/1585 protected 指纹；`approved-spec.json`、`pre-development.json` 固定批准 spec/旧 checklist/4个索引，不能误用主 manifest 的旧 draft spec 哈希。自有 `dev/baseline.json` 与 `dev/baseline/` 保存10文档原文；当前 DAA 起点为 `c1ab983acdf47a7754d682046b47645fcd062cb77731ed253255fe1fd01654ce`，保护现有格式，没有恢复旧 QA 的 `4a657...` 文件。并发 dirty 不归本任务，不 reset/覆盖/格式化整仓。

## r2-2. 实际文档变更及对应要求

| 顺序 | 唯一写入文件/内容 | 对应需求 |
| --- | --- | --- |
| 1 | docs/AIIS_DAA_Detailed_Design.md：保留有效r1机制；原位更新共享唯一连接、独立控制、DB自描述样本/完整轮次、派生目录/定义、三自然月/过期、业务保存及30故障场景 | R1–R11/R16–R17 |
| 2 | docs/AIIS_SMA_Detailed_Design.md：新中文16节；本地配置/表单绑定/API材料与手工目标/转换预览，四类时序、双进度与事务/outbox、业务确认/期限/缺口/GUI/迁移 | R8–R17 |
| 3 | docs/AIIS_AW_Runtime_Design.md：仅相关局部效力/指向、SMA首版非画布前置及DAA/SMA待定措辞 | R1 |
| 4 | docs/README.md、docs/README.zh-CN.md：两文用途/入口对称 | R1/AC20 |
| 5 | automation-world/data-acquisition-agent/README.md、README.zh-CN.md：替换原设计段，现状/目标与配套SMA入口 | R1/AC20 |
| 6 | automation-world/semantic-mapping-agent/README.md、README.zh-CN.md：仅加目标/旧基线/两文入口 | R1/AC20 |
| 7 | 本 tasks：r2真实DEV记录/交接，保留r1原记录 | AC20 |

Development 恰好写10个Markdown；未写16路径之外文件，也未写其中PM/QA/协调归属6文件。未改代码/测试/依赖/锁文件/env/YAML/SQLite/正式schema/DDL/contracts/CODE_INDEX/白皮书/ROADMAP/其他任务/skills。未构建、启动、执行工程测试、创建/读取数据库、连接PLC、调用实际HTTP测试、Docker、推送/发布或外部会话消息。

## r2-3. DEV self-check

以下为 Development 自检，不是 QA verdict。系统 Python 3.9.6 标准库仅在 /private/tmp 做 Markdown/JSON/哈希辅助，不代表项目运行验证，未新增项目依赖。未跟踪 SMA 新文全文和 DAA 当前原文差异都纳入，不能用空 Git diff 代替验证。

| 实际命令/检查 | 退出码与结果 |
| --- | --- |
| `rg --files -g 'AGENTS*' -g 'README*' -g 'PLAN*' docs automation-world/ tools/plc/projection-mapping/` 及必读文件的 cat/sed/rg | 0；确认最近入口、无额外AGENTS、DAA/SMA无本地PLAN，按r2不增建 |
| 标准库基线 helper，`git rev-parse HEAD`/`git status --short` | 0；固定10文档、HEAD/dirty及批准spec；9已有+1新SMA |
| `python3 .../dev/revise-daa.py`、`python3 .../dev/common-design.py` | 0；外置一次性编辑helper，原位修订DAA并生成共同30场景/责任材料 |
| `python3 .../dev/update-entries.py` 前两次 | 各exit 1；编译阶段报 Non-UTF-8 SyntaxError，未执行脚本/未半写入口；严格UTF8解码成功，添加显式coding:utf-8后下一次exit 0 |
| `python3 .../dev/create-tasks-r2.py` | 0；增补r2记录，保留r1元数据快照/正文原文 |
| `python3 /private/tmp/arch-aw-003-r2-gc842o4s/dev/audit-docs-r2.py` 首次 | 0；10文档、112本地链接、55表格、18对围栏、32显式锚点、2个JSON示例；DAA F01–F30/两文16节/共用责任表/双语入口/历史/指纹均通过 |
| 同一audit在latest原子条件补清定义/到期后 | 0；结果保留audit-first.json，errors=[]，1585 protected与6阶段保护无变化，无越界新增文件 |
| 通过argv展开10路径的 `git diff --check -- <10文档>` | 0；whitespace-first.json保留完整argv/输出；未跟踪全文另检查 |
| 标准库difflib生成并审阅 `dev/scoped.diff`，特别旧AW/4模块README | 0；AW仅+4/-2行，其他Agent/代码块不变；4模块运行命令围栏逐字保持，入口双语目标一致 |
| 跨文人工语义对读、源锚点复核 | 完成；区分包/点/cycle/批次、前缀与可读窗口、定义与质量、新鲜度与TTL、处理与业务确认；纠正工具只读schema导出现状和“不按同名自动重绑”措辞 |

必要官方事实通过 web open 核对 SQLite WAL/pragma/backup、Siemens块访问、Snap7 Client、AWS幂等API、OpenAPI官方v3.1.1规范；全部返回正文，链接在对应段落。规范版本只是材料语义依据，不声明首版解析支持全部版本/结构。未请求项目OpenAPI、执行API测试或安装依赖。文档audit没有失败退出；上表临时编辑helper的两次编码失败及修正如实保留。

| AC覆盖人工复核 | 位置与结论范围 |
| --- | --- |
| AC1–AC3 | 两文§1–2互链/现状；DAA§3–4唯一连接/诊断/完整结构/分组/周期；只确认设计表述完整 |
| AC4–AC6 | DAA§5–9双库激活/ack与冻结批次/实包容量/完整单位/过滤跳号/1005示例；保持r1可靠性机制并受窗口约束 |
| AC7–AC8 | DAA§4/8/12独立控制、配置中心/工作台/批量部分成功、固定API/自动预览、单在途建议/退避、真实原样本测试 |
| AC9–AC11 | DAA§10.3–10.4、SMA§4–5：单份自描述points、原样pointId键、多组合并/显式成员/历史不倒灌、目录到期消失 |
| AC12–AC14 | DAA§6.4/10.5–10.6、SMA§12：UTC三自然月/月末/闰年、过期拒绝不ack、本地保护、独立outbox与可靠业务长期保存 |
| AC15–AC16 | 两文定义章节：逐绑定签名排除采样内容/无关revision；局部暂停/人工确认，PLC实际变而定义未变的自动检测限制 |
| AC17–AC19 | SMA§3/6–12/14：表单/材料/手工参数/转换/预览、SQLite权威/双进度/事务/outbox/四时序、期限/unknown/目标部分失败、旧标量适配与单writer |
| AC20 | DAA§14–16/SMA§15–16共同矩阵/责任/待决/gate；10文件边界、双语/本地链接/JSON及r1历史检查；r2独立QA/终验未发生 |

最终handoff落盘后再运行同一audit与scoped whitespace，最终输出/退出码在dev目录；所有检查只覆盖文档。JSON检查仅语法解析，不证明Backend正式schema或业务类型兼容；Mermaid仅文本结构/职责对读，未渲染。关键词覆盖只是辅助存在性检查，未当独立语义QA。

## r2-4. 限制与风险

本次没有运行机制或故障注入；Mermaid只审文本，不安装渲染器。字段/单位/鉴权/DDL/签名算法、成员声明/样本正式粒度、时钟容差/物理清理SLA、去重/feed/历史回执/混合批次、SQLite选型/限额、目标幂等/最终业务回执、后台托管仍需各端精确任务。

三自然月是最大可用事实窗口，不是实时新鲜度；到期拒绝不假ack，DAA未确认保护可能最终停采；SMA未接收输入超窗无法保证全业务回填，已有自足outbox也须目标/本地期限允许。定义签名只检测已上报定义，不能自动发现PLC实际程序改而DAA定义没变。原标量消费者和递归camel字典键需Backend显式适配，不能声称新JSON天然兼容。外部无幂等/结果核实时无法保证一次业务效果。

## r2-5. 精确 developer_handoff

交接目标 `aiis-ics-arch::ARCH-AW-003 r2`，状态 **developer_handoff**，在上述HEAD的当前dirty working tree，无新commit。批准spec SHA-256为 `a6464506e3e8d86e55cc98415e4a4af9f91ab815598411bc3ec2d26676696537`；后续Verification读取完整spec/tasks/当前两文和入口、自有基线/diff/最终报告，使用新的fresh context，只验证记录不修文。r1 checklist仍由QA持有且保持原文；不得继承r1 verdict。下一gate为主协调显式启动 `verification`/`fork_turns="none"`，之后Human Owner终验。

以下为9个设计/入口最终指纹；tasks自指纹不写自身，在 `dev/final-manifest.json` 与精确交接中给出全部10文件。

| 文件 | SHA-256 |
| --- | --- |
| `docs/AIIS_DAA_Detailed_Design.md` | `55a7f8d28548e2e3c95618098086d7e63270b57f49c11ed1dfeb8d5d8b46c22d` |
| `docs/AIIS_SMA_Detailed_Design.md` | `e849bec4a4e29e587f16915b99b7e29d3774355b5d649be3b2f89ac724ea94b7` |
| `docs/AIIS_AW_Runtime_Design.md` | `1d4b34e10c72555fcdbc2850d5ee54ecb43b2507b5c102e1414e35f0ec8d59fa` |
| `docs/README.md` | `48a45e7a5fa89fb037342011eb4c6f6d740074e8aad2355ea0a58d683d1824e2` |
| `docs/README.zh-CN.md` | `2209a3ac86c621bd0bf258833345bdd4fa85c125e2f6b54246345aa73e3f6b20` |
| `automation-world/data-acquisition-agent/README.md` | `38c96772045c99fd2467772aabe5e7932d33512d9405b04355ff9aabe3ea2ea3` |
| `automation-world/data-acquisition-agent/README.zh-CN.md` | `f1d985c03443cb302486bbc16018288cdedaa9a1b8e77e04548feff9bd8a7a5e` |
| `automation-world/semantic-mapping-agent/README.md` | `94a97dd1649379e94af23ea0473c4ed3126e9f0c569ce5f1e2e1bdd6a2bf7672` |
| `automation-world/semantic-mapping-agent/README.zh-CN.md` | `1be1ed41953f9d78417dbdc12ef8ef3e195503c2b7b259a72ed2c4614419f0e6` |

创建资源仅在 `/private/tmp/arch-aw-003-r2-gc842o4s/dev/`：baseline.json/baseline/、HEAD.txt/initial-status.txt，revise-daa.py/common-design.py/update-entries.py/create-tasks-r2.py/finalize-tasks.py 一次性编辑helper、fault-matrix.md/responsibility.md 临时材料，audit-docs-r2.py/scoped.diff/audit-first.json/audit-report.json/whitespace-first.json、最终报告和final-manifest.json。父目录manifest/approved-spec/pre-development是主协调输入依赖，r1临时证据仍由其历史记录索引；均保留供QA，不在本角色清理。没有创建进程/数据库/容器/分支/worktree/外部持久资源。长期事实/命令结果/限制已记录在任务与两文，临时路径不是唯一事实面。

本profile仅contract_only；没有平台ACL/强制路由声明，没有授予QA verdict、最终验收或后续实现/现场权限。

---

# r1 Development 历史记录（原文保留）

以下元数据与正文为2026-10-16的r1实际交接记录，不是r2结果；当时任务顶层文件SHA-256为 `a5af35632b6bd02ffad3be645e01b883235707510cec302e3945a294f55c7db2`。其未发生QA/终验的表述仅指当时阶段；后续r1文档QA事实见独立checklist，终验仍未发生。

```text
Task ID: ARCH-AW-003
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Exact ARCH-AW-003 r1 documentation and DEV self-check in the current working tree to fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
```

# DAA 详细设计文档 Development 记录

## 1. 批准与只读依据

Human Owner 于 2026-10-16 精确批准 ARCH-AW-003 r1，原文见 [spec](spec.md) §1。消费时 spec 为 `owner_approved`，SHA-256 为 `f41918ab3fc9da837e2337a75760a464b9fa79efe2236831348931d0c150b19e`；未修改 spec 或创建/修改 checklist。开始时 bundle 只有 spec，Development 只在批准后创建本文件。

已读根 AGENTS、双语 README/PLAN、canonical lifecycle workflow、Development 角色 TOML、docs 双语 README、AW 双语 README/PLAN、DAA 双语 README、完整 approved spec、AW 运行设计与白皮书相关章节，以及 DAA 的 PLC domain/采集 Service/S7 adapter 和 SMA managed runtime。作用域文件检索未发现 docs、AW、DAA、plans 下额外 AGENTS；DAA 没有本地 PLAN，按 r1 不增建。`ARCH-AW-002/tasks.md` 只作为旧设计交付背景，不继承其批准/验收。

使用 `aiis`、`project-governance`（含 aiis CONTRACTS 边界引用）；本次是中文设计正文及双语入口，不冻结算法、DDL、依赖、endpoint，也未实施 Rust/UI/Backend，故没有加载未来实现表面的全部 skills。官方事实仅查 SQLite WAL/pragma/backup、Siemens 标准块访问、Snap7 Client、AWS 幂等 API，并在正文对应段落就近引用。

基准 HEAD 为 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，在现有多会话 dirty working tree 工作，无本任务 commit/worktree/分支。主协调基线 `/private/tmp/arch-aw-003-r1-koql8w94/` 的 `manifest.json` 保存 13 文件 allowlist、631 个 protected 文件哈希；本角色在其 `dev/` 下建立 7 文档独立 `baseline.json`、`baseline/`、`HEAD.txt`、`initial-status.txt`。新正文/tasks 起点不存在，其他 5 文件保留原文，不能以 Git 空 diff 代替审阅。

## 2. 实际实施与范围

| 顺序 | 文件与实际内容 | 对应需求/AC |
| --- | --- | --- |
| DEV-1 | 新建 [DAA 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)：16 节、组件图、配置/采样关系、事务/状态表与 18 行故障矩阵 | R1–R12；AC1–AC12 |
| DEV-2 | AW 运行设计只加一个 DAA 局部细化段；明确旧 latest/samples 待决和通用丢弃/合并选项不再作本目标默认 | R1；AC1/AC13 |
| DEV-3 | docs README pair 各加同一设计入口/用途 | R1；AC13 |
| DEV-4 | DAA README pair 各加目标入口与非实现说明，不改命令/身份/配置 | R1；AC13 |
| DEV-5 | 本 tasks 记录基线、开发自检、限制和精确 handoff；根 PLAN/catalog 由主协调机械同步 | AC14 |

Development 唯一写入上述 7 个 Markdown 文件。未写根 PLAN/catalog、Backend/SMA/CU/CA、代码/测试、配置/YAML/env、SQLite、依赖/锁文件、CODE_INDEX、contracts、白皮书/ROADMAP、AGENTS/workflow 或其他任务 bundle。未启动/构建应用、执行工程测试、连接数据库/PLC、运行 Docker、推送/发布或消息外部会话。

核心机制已形成可推演方案：完整组轮次分配 PLC 持久 sourceSeq，manifest/失败成员/上报分片区分采集质量和接收完整；组筛选自然跳号不作缺口；配置激活逐步提交并以准入屏障恢复；样本 ack 独立于多对多冻结批次，仍需重试引用的已确认样本不能早删；容量预算计入附属文件/钉住内容/维护空间；最新优先与历史有界公平；Backend 原子去重/latest 与安全 feed；SMA 双进度和原子处理/outbox，外部效果取决于对方幂等。正式 schema/编码/数值和各端实施仍留给 owning task。

## 3. DEV self-check

以下命令在仓库根执行，使用系统 Python 标准库仅作隔离的文档辅助检查，未修改项目环境/依赖，也不是项目运行验证。Development 自检不是 QA verdict；独立文档 Verification 由主协调在本角色 developer_handoff 后 fresh context 启动。

| 真实命令/检查 | 退出码与结果 |
| --- | --- |
| `rg --files -g AGENTS.md -g 'AGENTS.*' -g README.md -g README.zh-CN.md -g PLAN.md -g PLAN.zh-CN.md docs automation-world plans` | 0；确认触达层级 README/PLAN 和无额外 AGENTS |
| `git rev-parse HEAD`、`git status --short`（由基线 Python helper 读取并保存） | 0；HEAD/dirty 基线保存在 dev 目录，未更改 Git 状态 |
| 基线 Python 标准库 helper，读取批准 spec 并保存 7 文档原文/哈希 | 0；5 个已有、2 个不存在，spec 精确匹配批准指纹 |
| `python3 /private/tmp/arch-aw-003-r1-koql8w94/dev/audit-docs.py` 初轮 | 0；7 文件、56 本地链接、33 表格、22 围栏边界、16 显式锚点；18 故障行，AC1–AC12 关键词覆盖；无新增或既有断链 |
| 同一 audit，在确认清理增加完整事实完成门槛后再次运行 | 0；结构、双语入口和 631 protected 指纹仍通过，spec 未变 |
| `git diff --check -- docs/AIIS_DAA_Detailed_Design.md docs/AIIS_AW_Runtime_Design.md docs/README.md docs/README.zh-CN.md automation-world/data-acquisition-agent/README.md automation-world/data-acquisition-agent/README.zh-CN.md plans/ARCH-AW-003-daa-detailed-design/tasks.md` | 0；Git 已跟踪差异无 whitespace 错误，未跟踪内容另由 audit 全文检查 |
| Python `difflib.ndiff`/`unified_diff` 比对自有开始前原文 | 0；正文新增 528 行；旧运行设计仅 +2 行（一个段落/空行）；docs README 各 +1；DAA README 各 +2；tasks 新建，完整 scoped.diff 保存在 dev 目录 |
| 正文覆盖/术语人工复读，含 1000/1005 示例、完整性、冻结批次与 SMA 游标 | 完成；纠正一处混合词“状态ful”为“有状态”；未把关键词检查当成语义正确证明 |

官方核验中首次对 WAL 页面以 URL 调用 `web click` 的两次节链接解析失败（invalid arguments），随后改用已打开页面的 ref 与 link ID，返回成功；页面正文及 backup/pragma/Siemens/Snap7/AWS 打开成功。未因节链接失败推断技术事实。文档审计无失败退出，纠错与上述核验限制如实保留。

最终 tasks 落盘后再次运行同一 audit 和 scoped `git diff --check`；结果见 dev 目录最终报告，退出 0。该 audit 是标准库一次性文档检查 helper，不加入项目，也不是自动化工程测试。它检查本地路径/锚点、围栏/表格、双语新增目标、文档结构与术语存在、7 文件内容差异、批准 spec/631 protected 哈希；不编译 Mermaid 或证明设计可运行。

| 内容自检映射 | 正文位置/核对重点 |
| --- | --- |
| AC1–AC4 | §1–4：效力/源码现状、多 PLC 三维状态、单点单组/完整结构、独立周期/非重入/质量与采样限制 |
| AC5–AC7 | §5–7：激活令牌与双库崩溃表、ack/批次多对多与清理钉住、容量/WAL/实际空间/低水位 |
| AC8–AC9 | §8–9：有限最新优先/公平补传、组轮次序号/分片/自然跳号、严格完整前缀与策略缺口分开 |
| AC10–AC11 | §10–11：raw/latest/可靠回执、安全 feed/保留、SMA 四类时序/双进度/outbox/外部幂等 |
| AC12–AC13 | §12–16、全部入口：18 故障行、开放参数/责任/证据/gate、双语链接/局部旧文效力补充 |
| AC14 | 本 tasks 仅 DEV 事实；独立 Verification 和 Human Owner 最终验收仍待真实后续 gate |

## 4. 限制、未决与已知风险

本轮只检文档，不证明驱动、类型/偏移、吞吐、SQLite 耐久性、数据库/API 并发、原生生命周期、真实 PLC 或 SMA 运行正确。18 行故障场景是未来验证输入，未执行运行注入。

支持矩阵、限额/水位、SQLite 实际版本/schema、凭据/备份、API/确认/manifest、来源交接/质量、feed/保留、SMA 流程/缺口/重算/目标幂等及后台托管仍需后续精确任务。尤其 FULL 同步不代替硬件保证，双库不提供同磁盘容灾，有限容量不支持无限断网持续无损，第三方无幂等时不能保证外部副作用一次。

现有旧 YAML/直库与 SMA 内存进度未迁移；正文诚实分开现状与目标。并发 dirty 不归本任务；只根据受影响原文和 protected 指纹审计，不 reset/覆盖/整理他人改动。

## 5. developer_handoff

交接目标：`aiis-ics-arch::ARCH-AW-003 r1`，状态 **developer_handoff**；批准 spec 指纹见 §1，当前交付为上述 HEAD 上的 dirty working tree，无本任务 commit。Verification 应读取完整 approved spec、本 tasks、7 文档、自有基线/scoped.diff/最终报告与主协调索引；只验证记录，不静默修文。下一 gate 是主协调显式启动 `verification`、`fork_turns="none"`，之后才进入 Human Owner 最终验收。

6 个设计/入口文件最终 SHA-256 如下；tasks 的最终自指纹不写进自身，在 `dev/final-manifest.json` 与主协调 handoff 中提供。manifest 包含全部 7 文件，供 fresh-context Verification 与当前内容核对。

| 文件 | SHA-256 |
| --- | --- |
| `docs/AIIS_DAA_Detailed_Design.md` | `4a657992be20cdeb9c26bbbf34117ee4b52eecd6eed23cab1978f8e6d01cb10b` |
| `docs/AIIS_AW_Runtime_Design.md` | `485bc73f65a99783901e4b70a773386225699a9e7e38a38310d4e824eee3cda6` |
| `docs/README.md` | `4e8c961f440b063a9a47e1ce2d82a96e39261e83542c2ab9b0b280cce6c97dee` |
| `docs/README.zh-CN.md` | `97362c3f4436a6f2d14a64c816efad24c262a5718eb400426f3eb10a9ae562c1` |
| `automation-world/data-acquisition-agent/README.md` | `13c6afdfc445ec0036d554f845734ea335db508526f83002bfa930043db398f4` |
| `automation-world/data-acquisition-agent/README.zh-CN.md` | `df6da5681c920c6f1f7548ec0d0d74c41ada40f3546c5aa2bcc8865c21a5243c` |

本角色创建的临时资源均在 `/private/tmp/arch-aw-003-r1-koql8w94/dev/`：`baseline.json`、`baseline/`、`HEAD.txt`、`initial-status.txt`、`audit-docs.py`、`audit-report.json`、`scoped.diff`、`final-manifest.json`、最终命令报告。父目录及其主 manifest/原基线是主协调创建的输入依赖；没有创建后台进程、数据库、容器、worktree、分支或持久外部资源。临时文件保留供独立 QA 审阅，最终验收后由主协调按资源边界清理；长期设计/实际检查结果/限制已在仓库记录，临时路径不是唯一事实面。

`contract_only` 是角色合同边界，不是平台 ACL 或强制路由。Development 没有给出 QA verdict、授予 Human Owner 验收或批准后续代码/部署/现场动作。
