Task ID: ARCH-BE-008
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 已独立验证 rework1 精确候选，关闭 F-QA1-001；交 Human Owner 最终验收，pending；主协调按脱敏白名单归档并核对回收本轮专属资源，机械同步索引
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 独立 Verification QA2（当前有效）

## QA2-1. 依据、调用边界与 verdict

**Verdict：`qa_passed`，仅限 ARCH-BE-008 r1 A+B 当前学习切片；Human Owner final acceptance pending。** 当前候选完成独立 locked restore/build、完整 A11/11、全新空 MySQL B1/1、正式 DLL 完整291 HTTP及真实跨进程时区/SELECT/日志验证。F-QA1-001 在本轮关闭；下面完整保留 QA1 的原 `qa_failed`、复现、返工要求和所有限制，不把旧结果改成通过。未发现当前候选的实现失败或未解除环境 blocker。

本轮为实际命名 `verification` / `csharp_backend_qa2`，原调用 `fork_turns="none"`；从当前批准 bundle、交付树、diff/manifest、源码/锁、测试与归档输出独立判断，没有继承 Development 对话推理。独立完整读取根 AGENTS、README/PLAN pair、canonical workflow、verification.toml、最近作用域 README/PLAN/catalog、r1 spec、当前 rework1 tasks、QA1 checklist、全部32份C#源码、B脚本/Compose/fixture及相关 Python 来源。使用 `aiis`、`project-governance`、`backend-arch`、`code-document-indexer`、`i18n-workflow`、`docker-project-ops`、`docker-expert`。本角色只写本 checklist 与必要私有验证产物，未修复源码/测试/配置、未改 spec/tasks/索引、未 stage/commit/push。

主协调告知前一次角色启动返回 `Selected model is at capacity`，发生在实际验证前；该失败不是QA证据，不给 verdict。本次保持原命名角色/配置进行一次受控续接并实际运行工具；首次持久候选审计时间为 **2026-10-28T07:02:33.002061Z（上海15:02:33）**，之前已发生合同读取，但没有采集首个读取工具的精确时刻，不倒填。角色配置为普通文件，与 canonical 逐字节一致，SHA256 `ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`；model/effort 仅是配置证据，不宣称运行遥测、ACL或强制路由。

## QA2-2. 精确候选与环境

| 项目 | 本轮独立证据 |
| --- | --- |
| 工作树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b` 上未提交实现 |
| 批准 | spec §16.1 Human Owner 明确批准 `ARCH-BE-008 r1 A+B`；仅专属可丢弃MySQL/本机API，首期无登录 |
| spec / 当前tasks SHA256 | spec `998a56f2c97639d958cb61ab1b90ed1b7e4fa5c7329c38a4a18c6b7a199162f8`；tasks `22f9482faa53b0dbeeb5c924bf3d4c9fb7e2298a7a75ea77305035ef509f06da`；QA2前后均不变 |
| 44文件候选 | 实际路径集合及逐文件SHA全等于 rework1 manifest；排序“相对路径+LF+文件SHA256+LF”聚合为 `a9afc3bb5a75a610f25e6a42cbc694e019e0e66247c8c60926ca03cff78819f6` |
| 相对QA1变化 | 仅 `Common/Errors/ErrorBoundary.cs`、`tests/AIIS.Backend.Tests/Contracts/HttpTests.cs`；其余42文件/固定版本/双锁不变 |
| 实际运行DLL | 正式交付树 `backend-dotnet/bin/Debug/net10.0/AIIS.Backend.Api.dll`；SHA256 `8abae9632c4f6bff12e675e000adaa2af8c35bb25941180e3fdb08b6bc49f152`；四构建artifact重建前后均符合handoff |
| 双锁 / 参考 | API `2020c500652154081b9944687397b8012286ccab3a3aefc57a62b051cb2ba0ce`，测试 `1d6cab6be94310b1767f4894553f320484b700506b2f55c4061ed57ed3701bc9`；11/4直接包及36/81锁图核准；spec八份Python参考哈希全匹配，未运行或修改Python |
| SDK / 私有缓存 | `/private/tmp/arch-be008-sdk-rfSK3RBg/sdk/dotnet`；10.0.403 / runtime及ASP.NET10.0.14 / Darwin arm64；原官方归档SHA512重新计算，与官方metadata精确条目相等 |
| SDK SHA512 | `5893c66b48ea3674c7da18501059d606e96f3672fabe4d5e41762e692c7c83df3ee0b2b9dc5a0786191da2dc413d7335158101c14c935ab217f31ac2529770f3` |
| 环境 | BE008_TOOL_ROOT同一私有根；DOTNET_CLI_HOME/NUGET_PACKAGES/NUGET_HTTP_CACHE_PATH分别为其cli-home/nuget-packages/nuget-http-cache；证书生成false、遥测关闭；无roll-forward/preview、NuGet只官方源 |
| QA根 / B根 | `/private/tmp/arch-be008-qa2-gkv496cr` / 新空 `/private/tmp/arch-be008-run-s272kqdk`；均0700，秘密/连接文件0600；runId `ab0f0fb5409b36026f53281f` |
| 精确Docker目标 | project `aiis-arch-be008`；container `aiis-arch-be008-mysql`；network `aiis-arch-be008-net`；volume `aiis-arch-be008-mysql-data`；仅 `127.0.0.1:13388/arch_be008_plan` |
| 版本 / 镜像 | Docker29.7.2/aarch64；官方mysql8.4.6/arm64，digest `mysql@sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9` |

B前实际核对固定三资源不存在、两个端口可重bind；prepare再次检查并创建新实例，从0行开始，未复用DEV/QA1的库/凭据。Docker/VSTest/loopback操作仅按已获A+B批准用require_escalated克服沙箱socket限制；未安装/启动/重配Docker、不读真实env或其他任务配置。

## QA2-3. 实际命令和独立结果

所有 dotnet、B、正式DLL命令 cwd 均为 `.../aiis-ics-arch/backend-dotnet`；dotnet使用上表绝对SDK入口与私有环境。文档/git/governance命令cwd为仓库根。完整 argv/cwd/退出/耗时在脱敏白名单的原始命令JSON与stdout/stderr；以下不是DEV结论复述。

| 命令 / 动作 | 本轮真实结果 |
| --- | --- |
| 两项目 `dotnet restore ... --configfile NuGet.Config --locked-mode` | 各exit0；锁不变 |
| `dotnet build AIIS.Backend.Api.csproj --no-restore` | exit0，0warning/0error |
| `dotnet msbuild AIIS.Backend.Api.csproj -getItem:Compile,Content,None -nologo` + 独立断言 | exit0；三类item无tests/** |
| `dotnet test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter 'TestCategory!=MySQL' --logger 'trx;LogFileName=qa2-a.trx' --results-directory /private/tmp/arch-be008-qa2-gkv496cr/results-a` | exit0；11/11，0跳过；实际disabled新进程、配置失败、415完整信封及日志轮转 |
| `tests/scripts/run-mysql-tests.sh prepare --run-root /private/tmp/arch-be008-run-s272kqdk` | exit0；全新空实例/随机凭据/固定资源/单表fixture |
| 独立 `db_audit.py before`，只读MySQL CLI与AST/fixture核对 | exit0；零行，25列/类型/null/default精确匹配源d2；四命名索引+PK；仅plans；INSERT/SELECT，server/session+08和实际28800秒 |
| `TZ=UTC BE008_TOOL_ROOT=... BE008_DOTNET=... tests/scripts/run-mysql-tests.sh test --run-root /private/tmp/arch-be008-run-s272kqdk` | exit0；真实MySQL1/1、0跳过；含same-raw并发、实际Service命名1062与rollback、断线503/恢复和独立SELECT |
| 私有正式DLL公开合同helper最终轮 | exit0；291 HTTP，239个拒绝请求前后全表内容指纹不变；七类非JSON完整415，保留422/业务404/基础404/405 |
| 正式DLL NY→UTC两个串行进程 | PID84291/84332各exit0、均消失；18108 SO_REUSEADDR实际重bind；计划19的25字段和双时间完全相同，启动/重启无增行或DDL |
| 独立最终 `db_audit.py final` / `final_runtime_audit.py` | 各exit0；仅plans、23条合成行；结构与空实例相同；15个Decimal直接SELECT逐值精确匹配，原卷号HEX/双时间匹配；2199行runtime JSON全可解析 |
| 真实日志、错误关联、秘密私下比对 | exit0；7个415均有相同requestId的plan_request_failed/plan_invalid_request及415完成日志；实际1062 requestId `0HNPKO8KDVJG8`有成功rollback；创建事件有planId/requestId；五项秘密/完整连接匹配0 |
| 文档与diff | exit0；18份Markdown、577本地目标存在，32份C#头/本地CODE_INDEX齐全；根README pair/CODE_INDEX仅增加入口，无旧行删除；QA2写checklist前全部作用域文档哈希不变 |
| `bash -n` / 裸B脚本 / 限定 `git diff --check` | 各exit0；裸入口只帮助 |
| 根级governance checker | exit1、320行；对相同范围原320行基线多重集新增0/删除0；全库治理仍未通过，不扩大整改 |

已审阅QA1公开合同helper后在私有根适配当前runId及更严格媒体/header断言，本轮真正执行291次请求；复用的是可审阅测试材料，不是旧pass结论。DEV的旧实现失败→中间失败→最终回归TRX也独立解析，保留真实失败，不作为本轮通过替代。

## QA2-4. AC01–AC19

| AC | 结果 | 当前候选独立证据 |
| --- | --- | --- |
| AC01 | 通过 | r1 A+B原话、批准spec和当前handoff/allowlist核准；实际只专属学习环境 |
| AC02 | 通过 | 官方SDK归档/版本、精确直接包/双锁、locked restore/build、私有缓存、禁roll-forward与API排除tests |
| AC03 | 通过 | A实际启用三路由、独立disabled进程三404/OpenAPI无Plan；正式文档仅三业务操作+health，无JWT/维护/额外模块 |
| AC04 | 通过 | 本轮正式6缺失、20非remark null、42对象/数组错误、未知/重复/snake/非法Unicode等422；七非JSON均统一415；239拒绝前后行内容指纹不变 |
| AC05 | 通过 | 本轮最小默认、remark:null、25字段/GET相同；全非零最大值完整往返，独立SELECT |
| AC06 | 通过 | 15 Decimal逐个7类拒绝共105项，原始超长非零尾数/边界；指数/尾零接受；15列直接SELECT等于固定scale字符串，无double路径 |
| AC07 | 通过 | Python-strip/control顺序、Unicode标量长度边界、原卷号HEX原样；顺序ASCII大小写/空格409；完整Unicode/collation限制保留 |
| AC08 | 通过 | B并发同字面1成功+1冲突/一行；真实16并发Service named1062/确认rollback同requestId，未扩大canonical原子保证 |
| AC09 | 通过 | 存在200/合法不存在404，0负数非整数溢出422；更新/删除405、XLSX等404，无假成功 |
| AC10 | 通过 | 新库空列表，分页边界/checked offset/超末页、真实总数、四过滤；同秒五行三页与独立SELECT ID降序一致；priority/sort未知忽略 |
| AC11 | 通过 | 四过滤SQL片段参数化、包含引号卷号原样保存、%/_为声明LIKE通配，无结构/越表作用 |
| AC12 | 通过 | AST仅读源d2→fixture→实际25列逐项一致、无业务server default；四索引+PK、仅plans，engine/collation固定 |
| AC13 | 通过 | 源码同连接单次CURRENT_TIMESTAMP赋双时间；计划19 DB bracket同秒15:09:47，输出+08；NY→UTC实际重启同值，GET不更新时间 |
| AC14 | 通过 | 实际named1062与同requestId成功回滚、原记录不变；239拒绝无数据变化、上下文后续可用；无failpoint/锁/新增表 |
| AC15 | 通过 | 本轮stop→请求503/无行→start→真实创建/查询；正式DLL重启读回且不增行/DDL |
| AC16 | 通过 | INSERT/SELECT应用账号真实运行、DELETE1142；缺连接配置A失败且无泄露；普通注册/启动/请求无DDL/seed |
| AC17 | 通过 | stdout/文件2199行解析、七媒体稳定错误/requestId、创建planId、实际1062/rollback；A实际10MiB轮转/保留5文件/flush，秘密匹配0 |
| AC18 | 通过 | 源码/双语文档/索引/头与CODE_INDEX核对，差异限制/退出码和helper失败保留，当前候选等于正式DLL；生命周期索引由协调按本真实verdict机械同步 |
| AC19 | 通过 | 本轮新fresh证据、资源/归属和白名单明确；API已停；本角色不回收、不授Owner最终验收，交协调归档/cleanup |

## QA2-5. F-QA1-001 关闭的正式HTTP证据

同一正式DLL、新B账号，`POST /api/v1/plans`携带合成合法正文。以下每次均HTTP415、132字节、`Content-Type: application/json; charset=utf-8`，包含 `code:415,message:plan_invalid_request,data:null,errorCode:plan_invalid_request,timestamp`（另errors:null），timestamp落在请求开始/结束之间。每个requestId逐条关联稳定错误及415完成日志。

| 请求Content-Type | 正式响应requestId |
| --- | --- |
| text/plain | `0HNPKO9PH33DB:00000001` |
| application/octet-stream | `0HNPKO9PH33DC:00000001` |
| application/x-www-form-urlencoded | `0HNPKO9PH33DD:00000001` |
| application/merge-patch+json | `0HNPKO9PH33DE:00000001` |
| application/problem+json | `0HNPKO9PH33DF:00000001` |
| multipart/form-data; boundary=qa2 | `0HNPKO9PH33DG:00000001` |
| 缺Content-Type（实际不发送该header） | `0HNPKO9PH33DH:00000001` |

该七类包含原失败的三媒体、+json与缺header分支。正常JSON创建200，非法JSON/字段422、卷号规则422、业务plan_not_found404、未知路径404和不支持方法405均经当前正式HTTP验证；239拒绝（含七媒体）前后全表内容指纹相同。关闭理由为当前实测符合原r1 §7.2；QA1失败历史继续是原候选的真实结果。

## QA2-6. 本轮辅助/环境失败历史

| 真实失败 | 分类与保留处理 |
| --- | --- |
| 首次B preflight exit1 | 私有helper只识别“no such”，实际Docker网络缺失文案为“network … not found”；尚未创建资源。保留原日志/helper后只修文案判断，重跑prepare0 |
| 读库初查索引断言exit1 | 私有helper假设PRIMARY按ASCII先排，数据库index_name按collation排序；改为精确内容多重集比较，源码/数据库未改 |
| 首次正式helper exit1，249HTTP | 私有helper换了大写QA2标识却留小写qa1-abc，正确创建新卷返回200；不是实现失败。合法合成行id18保留；换新QA2B标识/不同Unicode边界卷后291完整exit0，无清库 |
| 最终schema helper首轮exit1 | 空表SHOW CREATE省略AUTO_INCREMENT计数，原helper将有行计数换成marker，导致与初始文本不同；只去除该非schema计数后其余结构精确相等 |
| runtime audit helper语法/执行exit1 | 私有SQL字符串引号SyntaxError，未进入审计或执行SQL；原文件保留，改等价只读CAST并先compile成功，最终审计exit0 |
| 最终端口审计默认沙箱PermissionError | socket权限限制；同一已批准A+B范围require_escalated后实际bind成功；无产品失败、无安装/宿主重配 |
| 最后文档helper首轮exit1 | helper误要求没有status列的模块catalog含字面qa_passed；实际QA2通过链接和Owner pending语义正确。按该catalog真实形状复核exit0，未修改目录来迎合helper |

## QA2-7. 限制、资源与持久交接

通过范围仍是无认证、loopback、固定MySQL8.4.6/collation的首期学习切片。非ASCII完整casefold/任意collation等价、跨字面canonical并发原子唯一、跨请求分页快照不保证；真实COMMIT ACK丢失未模拟或实证，源码保留结果未知且不盲重试。无生产部署/共享真实库/现有前端或Python鉴权切换/MES/PLC/现场/长稳证明；SDK初期证书生成副作用未完全定位的原历史保留，本轮持续关闭生成。

| 自有资源 | 当前事实与交接 |
| --- | --- |
| QA根 `/private/tmp/arch-be008-qa2-gkv496cr` | 原始命令/失败helper/HTTP/日志/哈希；按白名单机械持久归档后由协调核对回收 |
| B根 `/private/tmp/arch-be008-run-s272kqdk` | runId `ab0f0fb5409b36026f53281f`；0700，秘密0600；仅本轮合成数据。不得供后续fresh QA复用；证据固定后协调回收秘密/目录 |
| 三Docker资源 | 精确containerId `2add411f89f9a093abfa77b393e957e9353710131a77aff7d10bc5fa52658719`；task/runId核准；验证结束时只有plans/23行；随后主协调按归属和containerId执行cleanup退出0，三资源不存在、13388/18108实际重bind；本角色未执行down |
| 正式API18108 | 本轮PID83216、84291、84332均exit0/PID已消失，18108实际可重bind；无运行依赖 |
| A生成4根 | disabled `arch-be008-disabled-af0b498180554c869c1ccd2a667fd955`、test-logs `arch-be008-test-logs-beaa92bd0bb8434088a3a0e01f64a7eb`及`arch-be008-test-logs-0bb1bf219a4046e182080e73765a0cf2`、rotation `arch-be008-log-check-2f1700a0aeb44db68afd9e83e8a6f849`，均在/private/tmp；清单有文件/大小/hash，轮转原件约46MB不整体归档，必要摘要/TRX持久后协调回收 |
| SDK/缓存、正式bin/obj | SDK仍同任务原私有根，交协调按后续依赖回收；bin/obj为正式源码实际可重建忽略产物，不提交 |

白名单 `/private/tmp/arch-be008-qa2-gkv496cr/archive-manifest.json` SHA256 **`840f4fff6ea5fadd77f4ab6253b283ffd4b572e5a1969089e61828f7783a30d3`**，115个确切文件、1,980,437字节；逐项列出source、relativeDestination、SHA256、bytes，五项随机秘密/完整连接私下比对均0。不含凭据/连接、全工作树快照或大体积轮转原件。主协调已将115件及manifest机械归档到本bundle `evidence/qa2/`；本轮随后对全部已归档文件重新核对SHA/bytes全匹配。主协调归档与精确资源回收事实见QA2-8，不冒认由Verification执行。必要事实和输出已持久，不以/tmp作为唯一证据。

主要目标为 `evidence/qa2/results-a/qa2-a.trx`、`mysql/results/mysql-1793171260283673000.trx`、`db-before.json`/`db-final.json`、`formal-probes-attempt2/formal-http-cases.jsonl`及summary/processes、`runtime-independent-summary.json`、`independent-decimal-full-select.tsv`、`document-audit-before-verdict.json`、`resource-handoff.json`、`governance-independent-increment.json`及原始失败/helper/日志。精确文件以白名单为准。

主协调在证据/依赖/归属核对后使用已有批准的精确入口（Verification未执行）：

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch
BE008_COORDINATOR_CLEANUP_CONFIRMED=ab0f0fb5409b36026f53281f \
  backend-dotnet/tests/scripts/run-mysql-tests.sh cleanup \
  --run-root /private/tmp/arch-be008-run-s272kqdk
```

完成后核实三资源不存在、13388/18108可实际重bind，不操作其他任务/未知资源。当前进入Human Owner最终验收gate，**pending**；本qa_passed不等于Owner接受或其他外部操作授权。

## QA2-8. 最后机械同步审计

主协调根据已持久的真实QA2 verdict同步四根/四模块索引后，独立窄审计exit0：相对QA2开始，作用域文档仅这8份索引和本checklist发生变化；四根索引剔除007/008任务行后与HEAD逐字一致。所有索引均明确QA2通过、F001关闭/QA1保留与Owner验收pending，模块catalog链接真实checklist；44文件/四构建artifact、spec/tasks、八Python来源仍逐项不变。18份Markdown的577本地目标和限定diff检查通过。最终根governance仍exit1/320行，对相同范围320基线多重集新增0/删除0；基线SHA256 `c00b4c44f0e7467b8d098fec21fea3e7678e6c87eec6240e6335515f2d8b1256`。旧QA1正文SHA与本轮开始完全相同。

[QA2归档清单](evidence/qa2/archive-manifest.json)的115文件/1,980,437字节已逐件独立复算相符；[协调归档回执](evidence/qa2/coordinator-archive-receipt.json)明确归档完成。[协调资源回收证明](evidence/qa2/coordinator-resource-cleanup.json)记录精确runId/containerId、cleanup退出0、三资源消失和13388/18108 SO_REUSEADDR实际重bind；本角色读取该持久事实并核对，未自行down或再次连接库/API。最后文档/历史保全审计输出作为补充白名单交协调归档；不改变初115清单。

补充白名单 `archive-supplement-manifest.json` SHA256 `d97798e478ce51be011ccbf2f9f0d39520c6681a2a03ce75128b91415fac4f09`，6件/57,250字节，逐项source/relativeDestination/SHA/bytes及五秘密比对均无匹配；目标仍为`evidence/qa2/`，只补历史保全/最终文档与治理/归档回收审计，不修改原115清单。

QA根/B根及4个A日志根暂由主协调保留到补充输出归档与归属/依赖核对结束后回收；SDK/缓存按任务后续依赖处理。当前最终verdict仍`qa_passed`，Human Owner最终验收**pending**。

---

# QA1 历史原始记录（不作为当前verdict）

以下保留旧QA1正文逐字不变；其当时元数据摘录为：

> Task ID: ARCH-BE-008
> Revision: r1
> Status: qa_failed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: F-QA1-001 返回 Development 修复；本轮精确候选独立验证未通过。由主协调持久归档脱敏原始输出并核对回收专属资源；修复后须新的 fresh-context Verification；Human Owner 最终验收 pending
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# 独立 Verification QA1

## 1. 验证依据与结论

2026-10-28，实际命名 `verification` 角色、任务名 `csharp_backend_qa1`，在 Development handoff 之后以不继承 Development 对话推理的 fresh context 开始。独立阅读根 AGENTS、README/PLAN pair、canonical lifecycle workflow、项目 `.codex/agents/verification.toml`、backend-dotnet 最近作用域 README/PLAN/catalog、完整 [spec](spec.md) / [tasks](tasks.md)、实际源码、diff、锁及 Development 已有 TRX/失败输出。角色配置是普通文件，与 AIIS canonical 源逐字节一致，SHA256 `ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`；配置中的 model/effort 仅为配置证据，不声称独立运行遥测或平台 ACL。

Human Owner 在 spec §16.1 明确批准 `ARCH-BE-008 r1 A+B`，包括专属可丢弃 MySQL 操作。没有扩大为共享/真实库、部署或现场批准。本角色仅写本 checklist 与任务私有临时验证产物，未修复实现、测试、配置、spec、tasks 或索引。按适用面使用 `aiis`、`project-governance`、`backend-arch`、`code-document-indexer`、`i18n-workflow`、`docker-project-ops`、`docker-expert`；无前端、Worker、PLC、包装或其他 runtime 工作。

**Verdict：`qa_failed`。** 独立 locked restore/build、A10/10、新空 MySQL B1/1 与正式 DLL 的其他边界/跨时区/回读检查通过，但 F-QA1-001 证明非 JSON 请求未满足获批的统一错误信封。DEV 与现有测试通过不能覆盖该失败。未出现阻止必要验证的环境 blocker；Human Owner 最终验收仍 pending。

## 2. 精确候选与环境

| 项目 | 独立核对结果 |
| --- | --- |
| 工作树 / HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b` 上未提交候选；无 stage/commit/push |
| 批准 spec SHA256 | `998a56f2c97639d958cb61ab1b90ed1b7e4fa5c7329c38a4a18c6b7a199162f8`；原获批草案及只记录批准的历史见 spec，未改实质合同 |
| tasks 交接 SHA256 | `6e4bbd9cca95f6107f5183e63df860ba23168eca8c13f049b085d0fde9925966`；Status 为 developer_handoff |
| 实现候选 | 44 文件实际集合、逐文件 SHA 与 manifest 均相符；按“排序相对路径 + LF + 文件SHA256 + LF”的 UTF-8 字节求 SHA256，结果 `20a7474a4f9766bec0f70f081c56a7f5a77922caf1efe64ccad839efe022aad5` |
| Python 冻结参考 | spec §3 八份来源 SHA256 全匹配；独立阅读涉及创建/详情/列表和源 plans migration 的相应代码；未运行/修改 Python 功能 |
| 锁 | API `2020c500652154081b9944687397b8012286ccab3a3aefc57a62b051cb2ba0ce`；测试 `1d6cab6be94310b1767f4894553f320484b700506b2f55c4061ed57ed3701bc9`；API 11 个直接包、测试 4 个直接包与 spec 精确版本相符，锁图分别 36/81 项 |
| 正式 API DLL | `backend-dotnet/bin/Debug/net10.0/AIIS.Backend.Api.dll`；SHA256 `1ce88a2684f58996200f0d0a2e39493c5bffbd61ecee550e594e4647cc76b1c1`，本轮实际进程直接使用该 DLL；重建前后与交接相符 |
| SDK | 本任务原私有根 `/private/tmp/arch-be008-sdk-rfSK3RBg`；SDK10.0.403 / runtime及ASP.NET10.0.14 / Darwin arm64；global.json 禁 roll-forward/preview；无版本更换 |
| SDK 来源 | 对原官方归档重新流式计算 SHA512 `5893c66b48ea3674c7da18501059d606e96f3672fabe4d5e41762e692c7c83df3ee0b2b9dc5a0786191da2dc413d7335158101c14c935ab217f31ac2529770f3`，与本任务已下载官方 metadata 的10.0.403/osx-arm64条目完全一致 |
| 私有 CLI/缓存 | DOTNET_CLI_HOME、NUGET_PACKAGES、NUGET_HTTP_CACHE_PATH 分别为上述根 `cli-home/`、`nuget-packages/`、`nuget-http-cache/`；所有命令设置 `DOTNET_GENERATE_ASPNET_CERTIFICATE=false`、`DOTNET_CLI_TELEMETRY_OPTOUT=1`；未改全局 PATH/用户 SDK/项目依赖 |
| 本轮 QA 根 | `/private/tmp/arch-be008-qa1-3c2_4j81`，0700；存命令、独立辅助检查、原始脱敏结果及归档白名单 |
| 本轮 B 根 / runId | 新空 `/private/tmp/arch-be008-run-eihb7rry`，0700；`500b7e71711c83fdb763a0a3`；凭据/连接/manifest 文件均0600，不打印秘密 |
| Docker / MySQL | Docker29.7.2/aarch64；官方 mysql8.4.6/arm64，digest `mysql@sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9` |
| 精确目标 | project `aiis-arch-be008`；container `aiis-arch-be008-mysql`；network `aiis-arch-be008-net`；volume `aiis-arch-be008-mysql-data`；仅 `127.0.0.1:13388/arch_be008_plan`；API最多同时一个 `127.0.0.1:18108` |

本轮准备前独立检查三资源均不存在、13388/18108以 SO_REUSEADDR 实际可 bind；prepare 自身再次检查资源/端口/空schema。没有复用 Development 库、随机秘密或数据。受限沙箱中的 Docker/VSTest socket 限制按已批准 A+B 用 `require_escalated` 执行，不将权限限制误判为 Docker 未运行，不安装/启动/重配宿主 Docker。

## 3. 实际命令与结果

以下所有 dotnet / B / 正式 DLL 命令的 cwd 均为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet`，SDK 绝对入口为 `/private/tmp/arch-be008-sdk-rfSK3RBg/sdk/dotnet`，环境为上表私有配置。无库 A 与综合 B 取本轮新输出，不复用 DEV pass。

| 命令 / 独立动作 | 真实结果与退出码 |
| --- | --- |
| 对 44 文件/八 Python 参考/批准 spec/四个交接构建 artifact 重新 SHA256 与路径集合比较 | 0；完全相符；无缺失或额外实现文件 |
| 对 SDK 归档流式 SHA512 与官方 metadata 精确条目比较；`dotnet --info` | 0；归档与版本/架构匹配 |
| `dotnet restore AIIS.Backend.Api.csproj --configfile NuGet.Config --locked-mode` | 0 |
| `dotnet restore tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --configfile NuGet.Config --locked-mode` | 0 |
| `dotnet build AIIS.Backend.Api.csproj --no-restore` | 0；0 warning / 0 error |
| `dotnet msbuild AIIS.Backend.Api.csproj -getItem:Compile,Content,None -nologo` + JSON断言 | 0；三类 item 均没有 tests/** |
| `dotnet test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter 'TestCategory!=MySQL' --logger 'trx;LogFileName=qa1-a.trx' --results-directory /private/tmp/arch-be008-qa1-3c2_4j81/results-a` | 0；10/10 passed，0 skipped；含真实新进程 disabled 路由、配置失败及实际日志轮转 |
| `tests/scripts/run-mysql-tests.sh prepare --run-root /private/tmp/arch-be008-run-eihb7rry` | 0；pull/up/config、全新资源、空库与单表 fixture；server/session +08:00、实际offset28800 |
| 独立 MySQL CLI SELECT 版本/空行数/information_schema/SHOW GRANTS | 0；业务行数0；只有plans；25列、无业务server default、四源命名索引；app仅INSERT/SELECT |
| `TZ=UTC BE008_TOOL_ROOT=... BE008_DOTNET=... tests/scripts/run-mysql-tests.sh test --run-root /private/tmp/arch-be008-run-eihb7rry` | 0；综合真实MySQL1/1 passed；本轮 stop/start 后503/恢复创建、实际1062/rollback等均执行 |
| 私有 `formal_http_probes.py` 第1轮 | 1；90请求时 QA helper 把合法首次remark:null误判为重复，详情见§5；API已正常停止 |
| 同一私有 helper 第2轮 | 1；100请求时真正观察到415空body，原断言对空JSON产生TypeError；原始失败完整保留 |
| 同一私有 helper 第3轮（只改私有验证辅助，不改实现） | 1；完整286 HTTP用例走完；唯一合同失败 F-QA1-001 被保留为非零；其余断言通过。234个拒绝输入前后全表指纹不变 |
| 正式 DLL 两个串行进程 `TZ=America/New_York` → `TZ=UTC` | 各0；PID16379/16419消失，18108可rebind；同计划25字段和双时间重启读回一致；启动前后schema/行数不变 |
| 私有 `media_header_repro.py` | 0（取证命令正常完成，不是缺陷通过）；完整headers精确复现三个空415；+json对照有正确统一415；无数据/schema变化；PID17688已正常退出 |
| 独立 MySQL SELECT 所有15个Decimal列、原卷号HEX及双时间 | 0；全部与API精确字符串/原UTF8字节一致；最终只有plans/18条合成行 |
| 解析本轮 stdout/文件 JSON Lines、私下比对自有随机秘密 | 0；1961行均可解析（含stdout/文件副本），秘密匹配0；成功planId/requestId与停止flush可追溯 |

完整 argv、cwd、实际耗时/退出及原始 stdout/stderr 由本轮归档清单逐项固定。根治理/文档/最终diff审计在本 checklist 的最终审计记录中给出，不将旧治理诊断扩大成整改授权。

## 4. AC01–AC19 独立结果

| AC | 结果 | 独立证据与实际边界 |
| --- | --- | --- |
| AC01 | 通过 | 精确r1、A+B原话、spec/tasks状态与allowlist核对；未触真实库/生产，角色归属保留 |
| AC02 | 通过 | 官方SDK复核、固定直接依赖/双锁、locked restore/build0、MSBuild三item排除测试；私有CLI/NuGet与禁roll-forward/preview核准 |
| AC03 | 通过 | A中启用三业务操作；新独立disabled进程三404且OpenAPI无Plan；正式OpenAPI仅三Plan操作及health，无JWT方案/维护/额外业务入口；无库health200 |
| AC04 | **失败（F-QA1-001）** | JSON内6必填逐个省略、20非remark null、42对象/数组错误类型、未知/重复/snake/非法Unicode等真实HTTP均422且无写库；但R07/§7.2非JSON媒体类型415未统一错误信封 |
| AC05 | 通过 | 最小默认/remark null及全部非零最大值25字段，随后GET相同；独立SELECT原值；默认special/planned/priority5与精确零字符串明确 |
| AC06 | 通过 | 15个Decimal字段逐一bool/空/NaN/Infinity/负值/超上界/非零超scale拒绝；超长原始非零尾数拒绝；指数/合法尾零及各型最大值接受；15列直接SELECT与固定scale输出全相符，无double路径 |
| AC07 | 通过 | Python strip/control顺序、空白/内部控制拒绝；空格/Tab/CR原卷号按HEX原样保存；ASCII大小写/首尾空格顺序409；Unicode标量长度20/50/500边界往返；不宣称完整Unicode casefold等价 |
| AC08 | 通过 | 本轮B两同字面并发200+409/仅1条；另实际16并发触发Service命名1062，requestId `0HNPKND4QQ14F` 与成功rollback同链；仅ix_plans_coil_no匹配为重复，canonical跨字面并发保证未扩张 |
| AC09 | 通过 | 存在200/合法不存在404，0/负数/非整数/Int32溢出422；PUT/DELETE/PATCH405、XLSX/登录/UI等未实现入口404，无假成功 |
| AC10 | 通过 | B空列表正确；默认/页长/页码/重复值/checked offset/超末页；五个同秒PAGE行按独立SELECT的id倒序分三页完全相同；四筛选实际值/总数匹配数据库；空过滤和未知priority/sort忽略 |
| AC11 | 通过 | coilNo/grade/materialStatus/status引号/SQL片段均参数化返回空；包含SQL字面的卷号可原样创建；%/_保持LIKE通配；表与结构未改变 |
| AC12 | 通过 | AST仅读源d2，逐列比对fixture与实际information_schema：25列类型/nullability、无业务server defaults、四索引+PK；InnoDB/utf8mb4_0900_ai_ci；仅plans，无其他业务/Alembic/EF历史表 |
| AC13 | 通过 | Service同连接单次CURRENT_TIMESTAMP赋双时间，独立DB bracket为14:24:04–05；存DATETIME秒值，输出+08:00；读不更新；NY→UTC实际进程读回同值，无依赖宿主时区 |
| AC14 | 通过 | 拒绝输入前后所有行内容指纹相同；实际命名1062及确认rollback同requestId、原记录不变，后续上下文可继续创建/读；无第二业务动作/生产failpoint/锁/新表 |
| AC15 | 通过 | B明确专属stop→POST503且无假成功/秘密→start→新建/列表/独立SELECT成功；正式API串行重启保留计划，启动不增行或DDL |
| AC16 | 通过 | 使用本轮app INSERT/SELECT，DELETE实际1142（B）；缺连接配置A启动失败且不含连接串；注册/启动/正常请求无DDL/seed；配置不扫真实env |
| AC17 | 部分通过，F-QA1-001关联缺口 | 1961行stdout/文件JSON解析、requestId/planId、真实10MiB/5文件轮转及dispose/flush通过；named1062/rollback可区分预查。空415仅有result415访问事件，缺少统一errorCode路径，未掩盖该缺陷 |
| AC18 | 通过范围/来源审计，保留F-QA1-001 | 双语README/PLAN/catalog、源码中文头与CODE_INDEX逐项核查；根既有内容保全；候选与实际正式DLL一致；README宣告的统一415与实际差异已作为F001返回，不据文档推断通过 |
| AC19 | 通过角色/证据/交接控制 | 本轮fresh证据与DEV完全分开；API已停且PID/端口证明；本角色不down/清理，Docker与临时根交主协调；本verdict不授予Owner验收 |

## 5. 失败、辅助历史与 Development 返工

### F-QA1-001：非 JSON 媒体类型返回空415，未进入统一错误信封

- 类型：实现合同失败；涉及R07、AC04和spec §7.2，阻止本r1通过。
- 精确环境：上述冻结候选与正式DLL；专属本轮DB/app账号；首确认NY PID15151，复现UTC PID17688。均已退出0，不留运行API。
- 请求：`POST http://127.0.0.1:18108/api/v1/plans`，`Content-Type: text/plain`，正文如下（全为合成数据）：

```json
{"coilNo":"QA1-MEDIA-ONLY","grade":"G","spec":"S","weight":"1.2300","thickness":"0.123","width":"10.00"}
```

在按本spec显式启动本任务API后，可用以下无秘密请求复现：

```bash
curl -i -sS -X POST http://127.0.0.1:18108/api/v1/plans \
  -H 'Content-Type: text/plain' \
  --data-binary '{"coilNo":"QA1-MEDIA-ONLY","grade":"G","spec":"S","weight":"1.2300","thickness":"0.123","width":"10.00"}'
```

独立复现实际响应：

```text
HTTP 415
Content-Length: 0
Connection: close
Date: Wed, 28 Oct 2026 06:25:31 GMT
Server: Kestrel
X-Request-Id: 0HNPKNH22HQES:00000001

[0 bytes; no response JSON]
```

`application/octet-stream`、`application/x-www-form-urlencoded`同为415/0字节，requestId分别 `0HNPKNH22HQET:00000001`、`0HNPKNH22HQEU:00000001`。对照 `application/merge-patch+json`返回415/132字节、`application/json; charset=utf-8`及正确 `plan_invalid_request` 信封，requestId `0HNPKNH22HQEV:00000001`。四次前后schema/行数无变化。

预期：非application/json全部返回415和统一 `code=415/message=plan_invalid_request/data=null/errorCode=plan_invalid_request/timestamp` JSON。仅状态码正确不满足合同。

源码定位输入：`app/Plan/Endpoints/CreatePlanEndpoint.cs:14` 声明 Accepts；`Common/Serialization/CreatePlanJson.cs:20` 自定义binder已有415抛出；`Common/Errors/ErrorBoundary.cs` 只在异常时形成错误体。观测表明这些媒体类型在自定义binder异常映射之前走了空415路径；具体框架短路原因属推断，由Development定位，QA没有修改。现有 `HttpTests.EnabledRoutesAndStrictFailuresDoNotNeedDatabase` 只断言非JSON的415状态，未断言响应信封，所以A10通过未能发现。

Development返工应让所有非JSON媒体类型遵循原已批准错误合同，并补有意义的HTTP错误体回归断言；保持版本、三接口、schema、无认证/无生产钩子等原范围。完成后提交新的精确candidate与DEV handoff，由主协调另启fresh QA2、新空B实例，不能把本轮qa_failed覆盖为通过。

原始完整headers/请求/空body证据：QA根 `F-QA1-001-headers-repro.json`、`F-QA1-001-repro.json`、`formal-attempt2/formal-http-cases.jsonl`、`formal-attempt3/formal-http-cases.jsonl` 及对应stdout/持久日志；脱敏归档白名单/哈希交协调机械持久化，关键事实已完整留在本checklist。

### 真实辅助失败历史

| 次序 | 结果与归因 | 处理 |
| --- | --- | --- |
| B预查第一次 | helper对Docker缺失诊断使用大小写敏感匹配，遇`no such volume`退出1；当时未创建run-root或资源 | 仅修私有helper的匹配规则后退出0；原结果在b-preflight-attempt1.json，不是Docker或业务失败 |
| 正式探针第1轮 | 把base中未出现过的remark追加一次null误标为duplicate；接口正确200，创建QA1-INPUT合成行id13；90请求后helper退出1 | 保留请求/响应与分类；只修私有helper为真正双remark，合法合成行保留，不把它当脏写 |
| 正式探针第2轮 | 100请求时空415的JSON解析值为None，helper直接取code产生TypeError，根因证据为真实F001 | 保留全部原始输出；第3轮将已知缺陷作为失败记录继续其余断言，最终仍exit1 |

本轮没有修改实现来“修复测试”。Development 原有SQL/disabled缓存/断线辅助/证书等完整失败历史仍归tasks与原evidence；本checklist不抹去或重新归因。

## 6. 明确限制与验收审计

- 当前只验证首期无认证、本机学习切片。没有使Python鉴权失效，没有接既有前端/MES/PLC/FF或共享/真实数据库。
- 原始字符串不同但canonical相同、且既有唯一键未覆盖的并发，不保证原子canonical唯一；非ASCII完整casefold/任意collation等价、跨请求分页快照均不在首期保证。
- 真实COMMIT ACK丢失未模拟、未实证。源码将提交尝试后无法确认归为`plan_write_outcome_unknown`，未盲重试、未假承诺回滚；可靠幂等/回执另任务。
- 没有EF migration、startup DDL/seed、EnsureCreated/Migrate、额外表、锁/failpoint或通用故障注入。fixture只是本轮专属新空库测试材料，Alembic现库权威不变。
- QA通过条件未满足；本轮不能进入Human Owner final acceptance。修复、DEV自检、新fresh QA与Owner决定均仍是各自独立gate。
- Development首次SDK曾显示开发HTTPS证书生成且宿主副作用未完全定位的历史仍保留；本轮持续显式关闭生成，未操作用户证书或全局环境。

## 7. 资源与协调 handoff

Verification只核对/记录，不执行Docker down、目录回收或任何未知资源操作。以下为本轮结束时仍需主协调核对的归属：

| 资源 | 当前状态 / 保留原因 / 下一步 |
| --- | --- |
| `/private/tmp/arch-be008-run-eihb7rry` | 本轮新空B根；runId `500b7e71711c83fdb763a0a3`；含0600随机凭据、manifest、prepare/结果/日志；关键脱敏输出归档后协调删除私有根/秘密，不供新QA复用 |
| `aiis-arch-be008-mysql` / `aiis-arch-be008-net` / `aiis-arch-be008-mysql-data` | 本轮task/runId已核对，mysql8.4.6/arm64，仅18条合成计划，测试后正常运行供最后只读核验；由主协调确认输出持久化、无API/后续依赖后精确cleanup |
| `/private/tmp/arch-be008-qa1-3c2_4j81` | 本轮独立命令/辅助/失败/完整HTTP及日志/哈希清单；协调机械归档白名单后回收；不把/tmp作为唯一证据 |
| 本轮A生成的GUID日志/disabled/轮转根 | 在本轮A前后目录集合差异与资源清单中逐项列明；均无运行依赖；真实轮转5文件的大日志不需整份归档，TRX及哈希/摘要保留后协调回收 |
| `/private/tmp/arch-be008-sdk-rfSK3RBg` | 复用本任务已校验私有SDK/缓存，未复用其他任务环境；仍可能供Development返工，清理时点由主协调决定；原归属历史保留 |
| 正式API18108 | 本轮显式PID14010、15151、16379、16419、17688均正常退出0；每次核对PID消失及18108 SO_REUSEADDR可bind；A disabled进程也已由测试停止；最终状态另见资源摘要 |
| 正式工作树bin/obj | 本轮实际源码build/test的可重建忽略输出；不提交、不以临时副本替代交付源码 |

主协调的精确资源清理入口（本角色未执行）：

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch
BE008_COORDINATOR_CLEANUP_CONFIRMED=500b7e71711c83fdb763a0a3 \
  backend-dotnet/tests/scripts/run-mysql-tests.sh cleanup \
  --run-root /private/tmp/arch-be008-run-eihb7rry
```

必须先核对manifest中的task/runId/containerId、三资源labels、无API/PID/端口依赖及非秘密证据已归档，再执行；确认三资源消失、13388/18108可重bind。不能全局prune，不动Development/FF/DAA或归属未知资源。

## 8. 最终审计与归档

- 独立根治理最终命令 `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch` 退出1、320行。与主协调真实320行原始基线 `/private/tmp/arch-be008-coordinator-wkj0jq0q/governance-before.txt` 逐行多重集比较，新增0/删除0；全库治理仍未通过，非本任务扩大整改范围。
- checklist首次形成后根catalog尚未同步，首次本轮检查出现四条新的008 checklist缺链接诊断（共324）；主协调机械同步四根索引的qa_failed/实际checklist链接后，最终恢复上述320/新增0。最初辅助差异比较误用了Development带module参数的旧324行输出，该比较不作为最终证据；真实原始输出保留，最终比较使用明确同范围320基线。
- 限定 `git diff --check`、新文件空白检查、`bash -n`、裸脚本仅帮助均0。17份当前作用域Markdown共548个本地目标存在；32份C#源码中文/现有头风格与本地CODE_INDEX条目齐全。
- 按主协调初始七文件快照独立复核：根README pair各仅插入3行C#入口、CODE_INDEX仅1行，无旧行删除；四索引除007/008对应行以外内容逐字不变。Verification开始时完整文件hash基线到创建checklist前无文件改写；最终仅主协调四索引合法机械更新，本角色新增本checklist。
- 44个实现文件、spec、tasks、八Python参考及四交接构建artifact最终仍相符；没有用隔离副本取代正式交付树。
- 本轮A另生3个任务自有日志根（由测试生成）：`/private/tmp/arch-be008-disabled-93b58f401cc74024a6d20fb8027dfc2e`；`/private/tmp/arch-be008-log-check-c475e9567e7049f68ffd2cc88aabcc2f`；`/private/tmp/arch-be008-test-logs-bd4e1b609aba4a609ed53539f80bd9b0`。用途、文件数、字节数与清理条件在 `a-owned-temporary-resources.json` / `resource-handoff.json`；均无运行依赖，协调归档必要TRX/轮转摘要后回收。专属QA根与B根的0700已实际核对。
- 精确脱敏白名单：`/private/tmp/arch-be008-qa1-3c2_4j81/archive-manifest.json`，SHA256 `3ad526b1da8edf54d04fe147166114c3a8450bd1aa389a6169570a80e5aa2dc8`。95个明确文件、总1,617,137字节；逐文件SHA256/字节数/真实源路径及目标相对路径均已列明，私下随机秘密/完整连接字符串比对匹配0。不包含凭据/连接文件、全工作树hash快照或大体积轮转原始文件。
- 主协调将按白名单机械复制到本bundle的 `evidence/qa1/`，并将上述manifest本身复制为 `evidence/qa1/archive-manifest.json`，核对全部hash后才清理。Verification本轮交接时尚未替协调宣称复制或回收已完成；关键结论和完整失败复现已在本持久checklist，不依赖/tmp唯一存在。
- 主要归档目标约定：`evidence/qa1/F-QA1-001-headers-repro.json`、`formal-attempt3/formal-http-summary.json` / `formal-http-cases.jsonl`（均位于qa1下）、`results-a/qa1-a.trx`、`mysql/results/mysql-1793168308627517000.trx`、`mysql/prepare-evidence.json`、`mysql/select-readback.tsv`、`independent-db-final-summary.json`、`b-log-summary.json`、`all-runtime-log-summary.json`、`resource-handoff.json`、`governance-independent-increment-final.json`及对应原始stdout/文件日志；精确路径以白名单为准。

交Development：F-QA1-001仍开放，必须完成实现修复、回归断言和新候选handoff；交主协调：归档与本轮固定runId精确cleanup；交Human Owner：本轮真实qa_failed和上述限制，不进入最终验收。

## 9. Human Owner 最终验收

Pending。当前结果为qa_failed，交Development返工，不代替Human Owner范围批准、风险接受或最终验收，不授权发布/部署/真实数据库/现场操作。
