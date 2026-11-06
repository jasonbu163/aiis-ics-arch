Task ID: ARCH-DOC-001
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development完成同r1 rework1六处文档返工并自检；保留QA1 qa_failed与两个finding历史，交另一新fresh-context Verification复验，Owner文档终验pending
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 文档同步实施记录

> **历史效力说明（rework1进入）：** 以下§1–§7全文保留为QA1前Development候选及原自检历史，原tasks SHA256 `9460a50d416ce598373bfb786bddee7327af886147d24ed603e0e510c7554040`。QA1随后对该候选给出qa_failed（AC02/AC07），不能把原“已完成”表述当成QA通过。当前返工事实从§8起追加，原35候选hash与原QA失败不覆盖。

## 1. 精确批准、起点与交付

Human Owner于2026-11-05明确批准“批准 ARCH-DOC-001 r1，按 STD 实施”。[批准spec](spec.md) SHA256为`98abeb870ca9b864d68dcaca5518252dca982cd7fb70d7918e7af135b71e80a3`，实施后保持不变。正式工作树为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`。修改直接落在正式树，未创建或验证临时源码副本，未创建分支或提交。

Development先创建本tasks为implementation_in_progress并记录baseline，完成后才推进为developer_handoff。本轮独占写面为下表35件现有MD及本tasks。根`PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`四件由主协调独立写入；Development未写。spec归PM，本次不修改；checklist尚未创建，后续只由新的fresh-context Verification写入。39件现有文档均在精确42-path allowlist内。

已消费根/最近作用域AGENTS、README/PLAN、完整批准spec及既有最新任务证据，按实际Development TOML与canonical workflow执行；适用skill为aiis、project-governance、code-document-indexer，仅同步文档，不调用产品技能实施。最近任务checklist/Owner记录优先于旧索引；本轮没有重算旧raw或重做旧产品QA。

## 2. R01–R11实施与保留映射

| 要求 | 原位改写及落点 | 明确保留及理由 |
| --- | --- | --- |
| R01 证据层级 | 根README/ROADMAP、AW/Backend/frontend/FF PLAN、contracts/provider README及五份设计；源码、DEV、隔离独立QA、Owner、采用/现场分别陈述 | 所有旧任务bundle及失败/接受字节保持；没有总完成率或新增产品接受 |
| R02 总览与图 | 根README文本链、ROADMAP现状表/两图/能力阶段、CODE_INDEX；DAA受控B、新Backend隔离QA、SMA配置/关闭投递、FF/C#各自gate原位更新 | S0–S4及未实现方向继续保留；旧CA→monitor→Projection为冻结兼容链，新事实provider独立，目标链不画成已闭合 |
| R03 最小契约 | AGENTS只改第2节现有FE装配与验收层级、第3节DAA新采集/旧CA冻结/FF独立runtime两处句子 | 角色/STD/DIRECT/BACKFILL、权限、工具链、发布、时间、表格及其余所有条款保持原字节 |
| R04 AW现状 | AW README pair统一普通pnpm tauri dev、SQLite权威、应用隔离；清退Simulation/普通YAML/特殊别名；AW PLAN pair修CU008/DAA与SMA自身状态并补provider依赖 | 初始化/早期Owner接受行保留原日期与范围；父SMA001 draft不覆盖002/003接受或004 QA2 |
| R05 SMA采用界面 | 白皮书/运行原理/DAA/SMA详细设计、docs索引；当前为Rust/SQLite单文档revision/CAS，纯预览和正常执行拒绝；相关图/迁移/候选阶段同步，旧Backend-held不再作当前权威 | TSS来源与显式compat fixture保留；UI/localStorage及技术启动JSON独立。完整关系库、active/previous发布、运行库/checkpoint/outbox、GET→POST及新点身份适配仍未来 |
| R06 provider及合同 | 两provider README pair、contracts README/PLAN pair、backend README/PLAN pair、CODE_INDEX及DAA/SMA/总体设计；更新隔离A+B QA，引用已固定provider schema/摘要/游标/限额；plc_facts七表、业务四表/13表41列兼容及迁移顺序分开 | demand仍proposed；所有机器JSON/OpenAPI/schema/源码不变。Owner/provider-ready/真实采用/部署pending；旧monitor标量Projection兼容链不被新嵌套事实冒充替换 |
| R07 DS操作 | DS设计§3对象/§4.2/操作流程和docs索引，编辑→保存同一草稿→显式发布不可变版本→停机加载→另行启动；重复内容/引用保护沿现有实现手册 | 10月27日接受及原r4/r5历史保留；10月29日DIRECT增量仅DEV/人工确认边界，未追认为旧QA/接受。旧UTC存储与UI上海转换限制保留 |
| R08 FF及状态 | 根README/ROADMAP补FF005 accepted、FF004 r2 A QA3/有限多PLC S7 int16；FF PLAN pair澄清邻接旧r1；frontend PLAN修FE001 QA，backend PLAN修ARCH001接受，根README修BE008 QA2 | FF三kind/v1兼容/Rust主线/Python原型不改；Modbus只有结构校验、run拒绝，未授DS导出/Python/C#加载；完整hold_ack扣ACK强收未修、旧UTC限制均保留 |
| R09 替代/后移 | ROADMAP、白皮书/运行原理及DAA/SMA正文与图协调FOA/合并宿主被AW007 r2替代；共享Core/画布/中央管理非近期前置 | 未明确取消的未来方案继续留为可选，原日期来源与历史QA/接受保留，不以顶层提示代替正文修正 |
| R10 运维/历史 | contracts PLAN pair将K0–K3、旧root阻塞/head/路径历史化并提供当前入口；INITIALIZATION pair只补关闭态/采用gate及现有手册导航，backend补新旧链区别 | INITIALIZATION八个旧命令块逐文件原字节保持，没有新增生产/DB/Docker操作命令；新provider QA不接受旧CA现场或真实历史迁移 |
| R11 双语/职责 | 16组既有pair逐对核对能力、状态、日期、gate、路径和命令；中文五设计不造新语言副本，所有更名旧隐式锚点保留显式兼容ID | README稳定入口、PLAN短导航、实施证据只在本tasks；无docs PLAN、重复报告或额外bundle |

主协调四索引的实际工作为：本任务阶段/tasks实链、FE001 QA、SMA004及父/子状态、FF005、BE007目录对BE008证据说明，以及阶段B/Backend后续边界；根PLAN规范为spec入口，role文档实链留catalog。协调报告其4索引pair均有46条spec引用、状态/路径对称且链接/空白通过。Development把四件纳入只读链接/16pair与allowlist检查；它们不是35件Development哈希表或排除面漂移。主协调将在收到本handoff后只机械推进本任务状态并固定最终四索引给Verification。

## 3. 关键结果与源核对

- DAA-001至007已接受，但阶段B只指2026-10-30受控DS S7→SQLite；当前`local_acquisition.rs`仍返回`uploadAvailable:false`。后端优先/DAA暂缓是已选顺序。
- SMA002/003已接受，004 QA2通过待Owner、001父draft。`app.rs`选`configuration.sqlite3`；本地服务保存完整快照revision，`reject_execution`返回`SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE`。manual/start/resume/auto-start拒绝不被HTTP gate或旧偏好绕过。旧TSS只是来源/显式fixture，不作正常fallback。
- BE009/010最新checklist已给隔离MySQL A+B通过；默认关闭/空scope/unadopted和Owner/真实采用pending保持。已固定机器合同由provider源文件拥有；文档不再把全部字段/schema/游标说成待定。
- DS版本服务的`preview_publish`及手册明确草稿/显式发布/加载/启动分离；10月29日人工确认与10月27日接受范围分别保持。FF004 QA3和FF005 Owner附录保持原失败与完整hold_ack/UTC限制；本轮没有运行其测试。
- 原日期历史快照保持来源。CODE_INDEX A0旧标题、contracts旧验证标题、长期设计被改标题均补旧显式anchor，避免范围外反向引用失效。

## 4. Development纯文档自检

所有命令cwd均为正式仓根，使用现成系统文本/哈希解释器；辅助脚本只在本任务/private/tmp，不安装依赖、不导入业务代码。

| 实际命令/检查 | 真实结果 |
| --- | --- |
| `python3 /private/tmp/arch-doc001-r1-dev-8wce1wan/check_docs.py` | 最终exit 0；35 Development＋4协调＋spec/tasks，共41 MD，最终链接/锚点计数见下方收尾记录；本地文件/目录及相关锚点无缺失，reference-style定义/目标扫描完成（实际无标准reference-style使用）；白皮书相邻来源标签按其来源表处理 |
| `python3 /private/tmp/arch-doc001-r1-dev-8wce1wan/check_pairs_anchors.py` | exit 0，16 pair库存与命令块比较输出；INITIALIZATION两语旧块仅注释翻译不同，不当作新差异。另断言其各自8个原命令块与before逐字相同，exit 0；其余15 pair命令块一致。语义、日期、状态、gate、方法/路径及本轮inline启动命令人工逐对审查 |
| Mermaid静态人工及helper | 9块：ROADMAP EN/ZH各2、Runtime1、DAA2、SMA1、DS1。围栏/子图闭合、节点/引用/class/箭头静态核对；CU只对DAA/SMA用已接入实线，新CA虚线；Backend节点存在/隔离QA与DAA上传/SMA可靠运行未接线分开。没有现成parser/render/mmdc及项目Mermaid依赖，本轮没有parse、render或视觉验证，也未安装工具 |
| `git diff --check` | exit 0，无新增空白错误；收尾再次检查 |
| `git diff --stat`、`git diff -- AGENTS.md`、分组`git diff -- <allowlist paths>`、`git status --short` | 只读，均exit 0；逐段复核；AGENTS只两处授权句，39件existing MD及本bundle处于allowlist；无额外文件 |
| root-only `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch` | exit 1，368旧诊断：364重复metadata、4旧Allowed Writers；本新bundle/根索引无新增诊断 |
| 同baseline参数 `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch automation-world backend frontend-js contracts` | exit 1，385旧诊断：364 metadata、4 Allowed Writers、8 missing plans task link、6 missing模块catalog、3 find。相对协调407基线恰减少22（根索引12 missing task doc链接＋10非spec链接修正）；未修旧bundle、未创建缺失catalog或改checker。0新增可归因诊断 |
| before/after/protected SHA与allowlist核对 | exit 0，35件before→after如下；3467件排除面tracked文件逐文件哈希保持，批准spec SHA保持；4协调索引单独审计，不计排除面；未跟踪只spec/tasks，checklist待真实QA创建 |

辅助执行失败如实说明：起始编辑helper有一次中文编码声明缺失的SyntaxError、精确原文assert不匹配（在该文件写入前停止，前序已完成文件保留），均更正只读定位后再执行；不是产品失败。链接helper首轮exit 1，仅把白皮书`[U4][D3 §3]`等相邻历史来源标签误判成reference-style，6条均核对来源表后修helper，最终exit 0，未改旧来源。pair helper报告INITIALIZATION旧注释差异，未据此扩面改写旧命令。协调其计数helper曾出现一次list-set TypeError，修辅助表达式后同输入exit0，未产生产品/文档finding。

没有运行应用/监听、pnpm/uv/Cargo、产品测试或编译、SQLite/MySQL/DB/Docker、真实env/profile探测、PLC或HTTP、依赖安装、外发消息/邮件、Git写入/发布/部署。软件QA结果均为原记录引用，不能从这份Development自检获得新的产品或运行资格。

## 5. 35件Development候选指纹

下表路径均从仓根解析；before来自实施前原字节，after是本handoff候选。主协调4索引不混入本表。无35文件保留字节未改：每件均有对应R项的必要同步；所有排除面保持原字节。

| 文件 | before SHA256 | after SHA256 |
| --- | --- | --- |
| `AGENTS.md` | `eceaf1f2fbaa4e4ba6d60554cfb52579fa8ec8c8205a6e8f3f7a267ed2b579be` | `ca2c362868c8d9436feb0416615a67406b07d8ecd6148def35b84aa9ac94680a` |
| `README.md` | `dd607d3fd2105adabf805480a1fce92b534dcd53b987e41202dbea123029f516` | `e0bf3372b13f0c411d7d5334096b8c345663ec6c980a85bbe92fc9d89656db52` |
| `README.zh-CN.md` | `92f98817d9477e7307ef545ed13a82cfeae633c5ee7e462d2be0cd9971b1ae69` | `0090ee18a39bfcd0a08bdedf2f2bb4aba13c36391970c134d697226a61319658` |
| `ROADMAP.md` | `e5f1ed0dc3fcf6f94505da4363521a12d8294038c6e728b5a3ef8444c8db3ad9` | `3fbaae47a4c366ce91151cb9a22be9ca7dc6ba25da82521aa06c400f8f5de1a2` |
| `ROADMAP.zh-CN.md` | `811bbd9bf91ddf1e7243a847ed53f57eeb9316489d55c9951ddef1b26bf2fa34` | `3374129ea01e6c78f0bc846cc5f2c0ca61435f8ddf2a213882c4974d2e7207a2` |
| `INITIALIZATION.md` | `9b0ad192e9c741b39593d0b64db32fe0d9dd1263c735bf934dfd5eaba8078bb0` | `59817bd034a51eeb9c762a973ae17057f6556f163ae36293719703535bbf5bb5` |
| `INITIALIZATION.zh-CN.md` | `dd100899e3874fd5c5ea4d69177aecb15ca0ca26917804f4f30ce2083680cfd9` | `145639f14acb52f1c1cc6bd4eee5d0eb53823568651e58dc7cabcaf3d5d87909` |
| `CODE_INDEX.md` | `08cf4e2bdb02953a7806d17c32aa3a8b22d5812143feb2e860467f611488869a` | `c167b573b25a27ea275cac62a6a772a76a7ee5efbbb9bb0752de848340600d85` |
| `automation-world/README.md` | `f1d54077fd3006faf4ef3207b5957beeb7871ae938212b3c27c7de0eb177a074` | `932f39e919778225f5ef864a0ddcae35c557f254422502b2a61725a75fd5db0e` |
| `automation-world/README.zh-CN.md` | `3f50966d4b637855ae10431eae6d1f1bbdaa88e14b8d1a043d3e6dc2b6937469` | `2535dcd247e9b90c209cf744f171d8199f21ef3f52a1dbd7675af5c4c8dcf162` |
| `automation-world/PLAN.md` | `09b08ab31daeceb22d4517468f942758a93af54ee15d47c2c2f533d5b2e86ffa` | `be4a4aeda036b4efb59b0461ae8c20972349733005ab8fdf004edd8e48a6084c` |
| `automation-world/PLAN.zh-CN.md` | `4f39ab586fdf91773cf237f95479e854f4f73ca822c4cf9c03b7dfdb5d187227` | `99fccd0395658fbd392d733add5733f60c48fbb4e5f924cde1fcf43fcd8e028b` |
| `docs/README.md` | `5571ec1cab54ae66dd4e7d37f81827ebc32e6c01ff8a049b9e302d0f0f938231` | `4e33bd88570c4d00bc8fd9aaf6e5d3f8e2658c8c3ec499dfab1d83b6b0bbd517` |
| `docs/README.zh-CN.md` | `f817dafb5b59ea989e59a61c35f83cca31886d0d2caf4adb659c50113c3ef042` | `0ae309605b372a2b2c5cdeca74ec77ee799b7c9903d2f6b918224e17836048be` |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | `11896142e369f9025ece9e63f0a45b006fcb640f6740261aae1a5f77280733cd` | `6bcfa81cfa262bf457a28c146db8e54eefdfd16aa02fbd5890e29461ca3bbc35` |
| `docs/AIIS_AW_Runtime_Design.md` | `f87a3ef641a287731f73b3336c37b10977840b2609a99fc3ec27b534f1575d42` | `bc92f91d282448a23b73b5fdaf992177d9fac88c392d78229496b15093bc9b52` |
| `docs/AIIS_DAA_Detailed_Design.md` | `1ef581cbafca9d67fe117699079311c1691dafbcdfe0edfbc9f302a0d4f11049` | `55e39058602f582b7cb4b50b68de8beb838e754cee4777eb6fb3dbfd441c6864` |
| `docs/AIIS_SMA_Detailed_Design.md` | `50fd86acc3047c8dffc6767be03d27454b9364534a4dbd55d6704682f48a82c7` | `9cfba6151c8a2f63169d48465fab14f7a0510970f5583b285d7d16f9da8f7e55` |
| `docs/AIIS_DS_Detailed_Design.md` | `dfd775772ac086552f8d706fd5923f7c8beb5046a29030f83fb319481651ecd4` | `b196354d47eff9fdf2ac9403af39dbee072dc5ff6b165988c5baff4f206f2623` |
| `contracts/README.md` | `0d22882ba1aeb589bdd4e76dc162a5560ab402943a1ee7cd37cf17772ec4f700` | `622e0eeb6f8a5f26a8e9940f8444099410a3f3e608589205d6109039e82905f6` |
| `contracts/README.zh-CN.md` | `ac1677444bed7182703f58626eec88ff0809c767226f033a9dbe40d1d69aaab1` | `17b5d1a2683bab65c921de558f0dfe782903ca4adc932fe56cb18420bd263c9c` |
| `contracts/PLAN.md` | `8ab7229b92b093f219e70e0cb504bc8fc08f86d0542133c05ee09c99530408a4` | `fcca4e1278564f4cf6732ee5ab138b1f3d945a84c9512dcfcbc4f6caa09f1e3d` |
| `contracts/PLAN.zh-CN.md` | `c99e83afbbe79bd47bae1cd0e6b090bccec7dc6ad4e126c60f41d370b7ac9ff4` | `cad155df15814579183d242d7bd014764dcd84ef869af13a46b46c05845bec46` |
| `contracts/published/http-api/plc-facts-v1/README.md` | `1c039c4d19ef0637f94fbd0f8d7f8898e02f30d88ff7dcd9172ac09803ecd6c8` | `2b2e24a0d14acbc0ae54f264b706b040848be3a88bbcb8c2a9ab82bbe0726b42` |
| `contracts/published/http-api/plc-facts-v1/README.zh-CN.md` | `cd18b24a2302e232e3ee19f2fcf798263430afeb02dd3f5fb484d8a3ad46bfc3` | `477af9f359ff049f2088f9eddfa6f0e127aa6d95f2afbd6a16498c8778f66487` |
| `contracts/published/http-api/business-integration-v1/README.md` | `c190e77bfbf2a5bcf2bfab410b30bd88824a493bb3573f12d89efc497a9784cf` | `45a8fb46afff41b8d0f8c0e4792ce9a4901e993ad75a0c2e7af58db634374a66` |
| `contracts/published/http-api/business-integration-v1/README.zh-CN.md` | `1d6fc9be55c0e8e7c1880f21108dd556ec2191be0943bcc8dc79b801091b3e7a` | `ebe54ad6e5cf155acad59150a09cfff1a1d0d57a22ac173b18a35b887b608803` |
| `backend/README.md` | `2e259c4eb7e9bdcc4a788a0506b263a8b31bfb719342f51141e43144d0677b5d` | `44818a8189a86e893fbdc078b21869bcabbc36d5136d79e7485ffc9ff26b0956` |
| `backend/README.zh-CN.md` | `216ac6421e9a1634c27bf68152d52653be5ddddc381bc3d4707bfb74a70a5f92` | `bf810beb28285a231fce3a3d5e9a044b61b5032d99c2e39ae585efc093fa3ad7` |
| `backend/PLAN.md` | `3e117a3483c3021ac8adf78b994e556c00c34a6ade5f4fa0296a48f01cb7e80f` | `7b0b4018efbb827b7dfaccd3328bd21fb614c6af1c3fd67a5318b2da91cd4134` |
| `backend/PLAN.zh-CN.md` | `82494a9bd5ae5abdf35766ee5ae7c162d1d9c3d49f2c50e5efaf5f4980b9a24b` | `cfd6a00f8d7cc4dad11836a2903a50b6be11e91055ad6bdae84af4831a379eda` |
| `frontend-js/PLAN.md` | `d8426f7fb2327c6ab0bcfd853a5a62d0b1dc2a4da8133d2c9a0a3ddebc69a00f` | `4396491424fc8e55eec0c548f17379e8572782bd3b2fa0ad785d7472485a340a` |
| `frontend-js/PLAN.zh-CN.md` | `f10de307eec159306bdfe43de71c828ab85753610d5173e86345db15a976bbd1` | `4df0bddb2d3e7ca9c41b807e71614e20a0afb8a446bdf5d0ccc50a4b5419abf9` |
| `field-flow/PLAN.md` | `b3647936847aa7c4dba869aa07e9e315d13edf3f611f98aa9edd750b4a2f3ab4` | `5e417e9840db5a561e7402eb662a4bf413bbf740f2e1915abe51278d8f0d580f` |
| `field-flow/PLAN.zh-CN.md` | `32a6bee26900530053d537c457096a1b12acdadfac72bedf0ec6f9bd4751cf8c` | `3c52e5e9739289b8eb7722e68df2ffc208a48fc2013517cab2917604d2dbcaa9` |

35候选有序manifest SHA256：`d3b78a35c8808672e9af380972b6f0bf49a95b72697f3851bd059dbc2fedf66b`。3467件排除面hash映射及原字节、批准spec SHA/HEAD记录在私有baseline；baseline SHA256=`b1f320a7ceda7cec4cf352554620a8aa0f358f8b434765241d0f7468821ebe18`。关键数量/结果与全部35前后hash已持久化于本tasks，不以临时附件为唯一结论。

## 6. 资源与串行交接

唯一Development自有资源根为`/private/tmp/arch-doc001-r1-dev-8wce1wan`，入口指针`/private/tmp/arch-doc001-r1-development-active-path`。内有35原字节before、baseline/hash映射、一次性编辑helper、链接/pair检查helper、checks/pairs/candidate35 JSON及治理checker纯文本输出。没有运行环境、DB、监听、测试产物或软件安装；没有修改任务外临时资源。保留目的仅是fresh Verification/Owner审阅重核；关键证据已写本tasks。独立QA及Owner不再依赖后，由主协调先核对实际归属、占用和证据/后续依赖再精确回收这两个自有路径，不按前缀批量删除。

Development已交付精确ARCH-DOC-001 r1候选，待主协调机械同步4索引后固定给新的fresh-context Verification。Verification应读取完整spec/tasks、最终39文档diff、批准spec及保护面，独立核验AC01–AC14并只创建checklist。本记录不授予QA verdict或Human Owner最终接受；未渲染Mermaid、既有checker诊断及旧软件/现场/真实采用限制均明确保留。

## 7. 收尾复核

最终Development候选的离线扫描：41份MD、1084个本地路径目标、120个锚点、9块Mermaid静态库存，0实际链接/锚点/围栏/子图错误；标准reference-style实际使用数0。3467件protected哈希保持、批准spec不变；39件existing MD＋spec/tasks处于42allowlist，checklist尚未创建。16pair已按第4节完成核对。最终`git diff --check`及候选35哈希一致性exit 0；本tasks更新后再次执行本地扫描exit 0。

## 8. rework1开始：同r1有限文档返工

2026-11-05，实际Development完整消费最新QA1 checklist（SHA256 `20aeb54cf5c95830555ef6a2e02228b52491cfd2fb07bac1cfaa34472f38c2fd`，23231 bytes），当前进入implementation_in_progress。仅修四份Runtime/DAA/SMA/DS设计的5处provider权威残留与1处DS文字流程，以及本tasks；不修改spec/checklist、另外31件候选、协调四索引或产品。F-QA1-001/002来自原r1 R06/R07闭合，未改Revision或请求重复批准。

返工自有静态资源为`/private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc`，指针`/private/tmp/arch-doc001-r1-development-rework1-active-path`。进入时固定原35候选、4件待改正文、原tasks和QA1/spec指纹；旧DEV manifest/raw与QA1目录只读保留，未覆盖旧输出。完成后补真实diff、命令/退出、更新35候选及保护面结果，再给新developer_handoff。

## 9. rework1实际改动与证据边界

[QA1失败记录](checklist.md)全文保持SHA256 `20aeb54cf5c95830555ef6a2e02228b52491cfd2fb07bac1cfaa34472f38c2fd`；没有代写finding关闭或QA2结论。Development仅完成下列六处原位返工，是否满足AC02/AC07交新的fresh Verification。

| QA1位置 | 本次正文delta | 保持的后续/历史边界 |
| --- | --- | --- |
| F-QA1-001 Runtime §12 | 正式事实schema/编码/摘要/限额/latest/history/回执与混合批次矩阵改为引用plc-facts/v1；typed业务引用business-integration/v1。将已固定provider与待决客户端/扩展分段 | Owner/provider-ready/真实采用仍未获授；DAA上传、SMA目录/新点身份和可靠输入/投递仍未接通；既有受控范围外协议、客户端本地处置、人工缺口、扩展/托管另立 |
| F-QA1-001 DAA §6.1 | 删除“编码及摘要算法待Backend合同确认”，改为现有正式OpenAPI/schema/vectors及pf-json/v1已固定，未来编码器消费该版本 | 没有复制竞争schema/算法或运行编码器；DAA生成/校验/持久重试仍待单独批准和验证 |
| F-QA1-001 DAA §6.4 | 历史重复回执、有限proof、整批拒绝/退休/父批派生明确由正式provider定稿 | DAA本地终结/释放引用与人工缺口接受仍另立；unknown先核实、过期不复活、拒绝不假ACK及满额停采原约束保持 |
| F-QA1-001 SMA §7.2 | typed信封权威改为business-integration-v1的正式openapi.json/examples.json及provider说明；demand仅proposed需求/责任来源 | 原示意业务对象不冒充正式信封；既有POST鉴权、稳定身份/回执及不伪造actor约束保持；未改demand状态 |
| F-QA1-001 SMA §12.2 | 历史回执/有限proof/混合新过期批次拒绝、退休和派生改为现有plc-facts/v1正式矩阵 | DAA处置、SMA缺口接受/重同步与可靠运行客户端仍后续，不延长raw/latest窗口 |
| F-QA1-002 DS §3文字链 | 改为编辑→CAS保存同一草稿/ETag、不产版本→显式保存为版本、工作区/清理清单确认→不可变版本（重复内容不增）→停止/连接释放后apply→保留/初始化/移除清单确认且保持停止→安装loaded→另行start | §4.2/§15的selected/loaded保护、重复内容、未知结果核实不改；10月29日DEV/人工确认与10月27日旧接受边界保持；不是Mermaid结构返工 |

现行事实规范的只读核对包括canonical.py的pf-json/v1/域分离摘要与输入边界、async_ingest.py的历史确认/proof到期/可靠拒绝与父批派生分支，及两个provider README对应的机器工件入口；DS当前手册§2.5/五动作说明明确普通保存与发布/加载/启动分离。本轮只读源码文本，不导入业务模块、不打开DB、不执行原产品QA。

## 10. rework1 Development自检与保留证明

本轮辅助脚本/输出全部写到`/private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc`。先读取QA1复现helper，确认其会写QA1/findings.json；因此复制到rework1并仅改out路径，实际运行只写本轮findings.json，旧QA1资源无写入。旧DEV baseline/candidate35/raw同样只读，没有覆盖原指纹或输出。

| 实际命令（cwd正式仓根） | 结果与限制 |
| --- | --- |
| `python3 /private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc/edit_rework1.py` | exit0，精确四文档六处替换；没有扩大写面 |
| `python3 /private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc/reproduce_findings.py` | exit0，no_listed_residue，原六个残留字符串0命中；仅DEV复现自检，不给QA verdict，另有§9逐项语义/正式来源人工复核 |
| `python3 /private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc/check_docs.py` | exit0，检查39候选＋spec/tasks/checklist全42 MD，本地文件/目录、标准reference-style目标扫描及相关锚点无失效；最终计数在收尾追加。没有运行产品/HTTP |
| `python3 /private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc/verify_rework1.py` | exit0，35总体恰4变/31保持、3467保护文件保持、spec/QA1保持、旧manifest/helper保持、旧tasks§1–§7正文保留、顶层8字段各唯一；本轮四文档全部Mermaid块逐字未改 |
| `git diff --check` | exit0；新候选收尾再次复核 |
| 四件QA1→rework1纯文本diff人工审阅 | 限六个指定位置，没有新增节点/图或修改代码/机器合同/旧task证据；16组EN/ZH pair均不是本次四文档写面，维持QA1已有候选。未parse/render图，不安装工具 |

没有运行产品、软件测试/编译、pnpm/uv/Cargo、DB/SQLite/MySQL/Docker、真实env/profile/设备、网络/外发、依赖安装或Git写入。QA1已独立记录治理checker385既有诊断，本轮不因六处纯文字修正重做全仓治理/原产品QA；单份metadata/作用域/链接/保护面检查据实执行，不宣称全仓exit0。原QA1 AC02/AC07失败保留，由新QA独立决定是否关闭。

## 11. rework1候选指纹

35总体新manifest为`/private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc/candidate35-rework1.json`，SHA256 `c28ab1140c42a3308957714425dd937671d321031cca29a5d14535ef9be7ae17`。原35manifest `d3b78a35c8808672e9af380972b6f0bf49a95b72697f3851bd059dbc2fedf66b`保留为QA1前历史。四件delta如下，31件after继续等于§5原after。

| 文件 | QA1候选 SHA256 | rework1 SHA256 |
| --- | --- | --- |
| `docs/AIIS_AW_Runtime_Design.md` | `bc92f91d282448a23b73b5fdaf992177d9fac88c392d78229496b15093bc9b52` | `c9ebd307c45932a52ee179b914552a1858d0bd181e8e53efd6ec61529b0af94f` |
| `docs/AIIS_DAA_Detailed_Design.md` | `55e39058602f582b7cb4b50b68de8beb838e754cee4777eb6fb3dbfd441c6864` | `bc179da342d6eef0ac7d9abe1d4c229eb2e6fa5629304dcadb03dc17912334c3` |
| `docs/AIIS_SMA_Detailed_Design.md` | `9cfba6151c8a2f63169d48465fab14f7a0510970f5583b285d7d16f9da8f7e55` | `36bb4bf847009cedfccb19c61f2cc64dbaf4c4c4810ddf077cfbcfb39ac380c8` |
| `docs/AIIS_DS_Detailed_Design.md` | `b196354d47eff9fdf2ac9403af39dbee072dc5ff6b165988c5baff4f206f2623` | `ad13e9132c56a26324e9081f66873ab0659c7d4b899f622e4d067ff424bac2ba` |

完整当前35件after列表（供新fresh Verification固定候选）：

| 文件 | rework1当前 SHA256 |
| --- | --- |
| `AGENTS.md` | `ca2c362868c8d9436feb0416615a67406b07d8ecd6148def35b84aa9ac94680a` |
| `CODE_INDEX.md` | `c167b573b25a27ea275cac62a6a772a76a7ee5efbbb9bb0752de848340600d85` |
| `INITIALIZATION.md` | `59817bd034a51eeb9c762a973ae17057f6556f163ae36293719703535bbf5bb5` |
| `INITIALIZATION.zh-CN.md` | `145639f14acb52f1c1cc6bd4eee5d0eb53823568651e58dc7cabcaf3d5d87909` |
| `README.md` | `e0bf3372b13f0c411d7d5334096b8c345663ec6c980a85bbe92fc9d89656db52` |
| `README.zh-CN.md` | `0090ee18a39bfcd0a08bdedf2f2bb4aba13c36391970c134d697226a61319658` |
| `ROADMAP.md` | `3fbaae47a4c366ce91151cb9a22be9ca7dc6ba25da82521aa06c400f8f5de1a2` |
| `ROADMAP.zh-CN.md` | `3374129ea01e6c78f0bc846cc5f2c0ca61435f8ddf2a213882c4974d2e7207a2` |
| `automation-world/PLAN.md` | `be4a4aeda036b4efb59b0461ae8c20972349733005ab8fdf004edd8e48a6084c` |
| `automation-world/PLAN.zh-CN.md` | `99fccd0395658fbd392d733add5733f60c48fbb4e5f924cde1fcf43fcd8e028b` |
| `automation-world/README.md` | `932f39e919778225f5ef864a0ddcae35c557f254422502b2a61725a75fd5db0e` |
| `automation-world/README.zh-CN.md` | `2535dcd247e9b90c209cf744f171d8199f21ef3f52a1dbd7675af5c4c8dcf162` |
| `backend/PLAN.md` | `7b0b4018efbb827b7dfaccd3328bd21fb614c6af1c3fd67a5318b2da91cd4134` |
| `backend/PLAN.zh-CN.md` | `cfd6a00f8d7cc4dad11836a2903a50b6be11e91055ad6bdae84af4831a379eda` |
| `backend/README.md` | `44818a8189a86e893fbdc078b21869bcabbc36d5136d79e7485ffc9ff26b0956` |
| `backend/README.zh-CN.md` | `bf810beb28285a231fce3a3d5e9a044b61b5032d99c2e39ae585efc093fa3ad7` |
| `contracts/PLAN.md` | `fcca4e1278564f4cf6732ee5ab138b1f3d945a84c9512dcfcbc4f6caa09f1e3d` |
| `contracts/PLAN.zh-CN.md` | `cad155df15814579183d242d7bd014764dcd84ef869af13a46b46c05845bec46` |
| `contracts/README.md` | `622e0eeb6f8a5f26a8e9940f8444099410a3f3e608589205d6109039e82905f6` |
| `contracts/README.zh-CN.md` | `17b5d1a2683bab65c921de558f0dfe782903ca4adc932fe56cb18420bd263c9c` |
| `contracts/published/http-api/business-integration-v1/README.md` | `45a8fb46afff41b8d0f8c0e4792ce9a4901e993ad75a0c2e7af58db634374a66` |
| `contracts/published/http-api/business-integration-v1/README.zh-CN.md` | `ebe54ad6e5cf155acad59150a09cfff1a1d0d57a22ac173b18a35b887b608803` |
| `contracts/published/http-api/plc-facts-v1/README.md` | `2b2e24a0d14acbc0ae54f264b706b040848be3a88bbcb8c2a9ab82bbe0726b42` |
| `contracts/published/http-api/plc-facts-v1/README.zh-CN.md` | `477af9f359ff049f2088f9eddfa6f0e127aa6d95f2afbd6a16498c8778f66487` |
| `docs/AIIS_AW_Runtime_Design.md` | `c9ebd307c45932a52ee179b914552a1858d0bd181e8e53efd6ec61529b0af94f` |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | `6bcfa81cfa262bf457a28c146db8e54eefdfd16aa02fbd5890e29461ca3bbc35` |
| `docs/AIIS_DAA_Detailed_Design.md` | `bc179da342d6eef0ac7d9abe1d4c229eb2e6fa5629304dcadb03dc17912334c3` |
| `docs/AIIS_DS_Detailed_Design.md` | `ad13e9132c56a26324e9081f66873ab0659c7d4b899f622e4d067ff424bac2ba` |
| `docs/AIIS_SMA_Detailed_Design.md` | `36bb4bf847009cedfccb19c61f2cc64dbaf4c4c4810ddf077cfbcfb39ac380c8` |
| `docs/README.md` | `4e33bd88570c4d00bc8fd9aaf6e5d3f8e2658c8c3ec499dfab1d83b6b0bbd517` |
| `docs/README.zh-CN.md` | `0ae309605b372a2b2c5cdeca74ec77ee799b7c9903d2f6b918224e17836048be` |
| `field-flow/PLAN.md` | `5e417e9840db5a561e7402eb662a4bf413bbf740f2e1915abe51278d8f0d580f` |
| `field-flow/PLAN.zh-CN.md` | `3c52e5e9739289b8eb7722e68df2ffc208a48fc2013517cab2917604d2dbcaa9` |
| `frontend-js/PLAN.md` | `4396491424fc8e55eec0c548f17379e8572782bd3b2fa0ad785d7472485a340a` |
| `frontend-js/PLAN.zh-CN.md` | `4df0bddb2d3e7ca9c41b807e71614e20a0afb8a446bdf5d0ccc50a4b5419abf9` |

批准spec SHA仍`98abeb870ca9b864d68dcaca5518252dca982cd7fb70d7918e7af135b71e80a3`。rework1进入baseline SHA256 `50d8b67d8c3b092d666c68b1ea88642c006a0bd12dbf781e16895bc21577bb3a`，记录原tasks/QA1、四件原字节、35旧候选、3467保护面及协调root4进入指纹。根4阶段变化归主协调，不混为Development越界；本轮四件以外的35候选和受保护tracked源码/机器工件均不变。

## 12. rework1资源与新handoff

本轮新增自有资源只在`/private/tmp/arch-doc001-r1-dev-rework1-82t7pmcc`及指针`/private/tmp/arch-doc001-r1-development-rework1-active-path`：四件before/原tasks快照、baseline、四件最小diff、复制且改输出位置的纯文档helper、当前35manifest及检查JSON。没有环境、数据库、监听或产品产物。原DEV根及QA1根继续只读保留失败追溯。关键新hash、delta、命令/退出及限制已写入本tasks。

资源保留到返工复验及Owner审阅不再依赖；由唯一主协调核对精确归属、占用及证据/后续依赖后定点回收本轮目录和指针，不能连带覆盖/清理旧QA1或任务外资源。没有把应交付变更只留私有副本，四件正式正文已直接更新。

**Development rework1 -> 主协调 -> 另一新fresh-context Verification：**当前精确r1有限返工候选已形成developer_handoff。请消费本tasks当前§8–§13、原QA1完整失败记录、四件delta与35新manifest，独立复核AC02/AC07及关联保护面；旧AC pass不能代替新候选复验。主协调可据真实handoff机械推进根四索引并固定最终candidate。Development不宣称QA通过或Owner最终接受；Owner文档终验pending，产品/采用/现场/发布/部署边界不变。

## 13. rework1收尾固定

全部42 MD离线链接扫描为1123个本地文件/目录目标、122个相关锚点，0失效，标准reference-style使用0；9 Mermaid库存未变且本轮4件图库字节均未改，未parse/render。35总体恰4件返工/31件保留，3467保护文件、批准spec、QA1全文、旧35manifest及原tasks正文保持；metadata单份。最终复现helper、链接检查、scope/候选hash检查及git diff --check均exit0。没有新的DEV检查失败；QA1两finding的关闭决定仍交新Verification。
