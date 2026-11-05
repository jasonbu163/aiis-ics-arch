Task ID: ARCH-BE-008
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-BE-008 r1 rework1 已形成精确候选 a9afc3bb5a75a610f25e6a42cbc694e019e0e66247c8c60926ca03cff78819f6 与实际DEV自检；交主协调启动新 fresh QA2；QA1失败保留，QA2/Owner验收 pending
Workflow Mode: STD
Execution Mode: agent_team_same_session

# Development 实施与自检

## 依据与所有权

- Human Owner 已于 2026-10-28 明确批准 r1 A+B；唯一范围来源 [spec.md](spec.md)，当前批准记录 SHA256 `998a56f2c97639d958cb61ab1b90ed1b7e4fa5c7329c38a4a18c6b7a199162f8`。
- 角色为实际 `agent_type=development`、任务名 `csharp_backend_dev`；配置入口 `.codex/agents/development.toml`，配置 model/effort 不是独立运行遥测。
- 交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`。初始已有根 PLAN/catalog、007 spec 和 008 spec 的并行 dirty；未修改或回退。
- 已核对 spec §3 八份来源 SHA256 全部匹配；Python 功能继续保留。
- 写入限于 spec §5；主协调负责四个根 PLAN/catalog，Development 不写 spec/checklist。

## 实施顺序

1. 固定私有 SDK、NuGet 源、直接版本及锁 → 官方 SHA512、locked restore、build。
2. 三接口/严格输入/规则/模块/响应/时间/日志 → 无库 MSTest。
3. 专属 MySQL fixture/最小权限/合成业务 → B category、独立 SELECT、断线恢复和重启。
4. 双语说明与索引、脱敏证据、候选清单 → diff/链接/资源核对后 developer_handoff。

## 命令与失败历史

| 阶段 | 实际命令/结果 |
| --- | --- |
| 来源核对 | `shasum -a 256` spec §3 八文件及 spec，退出 0，全匹配 |
| 官方 metadata 首次下载 | 默认沙箱 `curl -fsSL https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json`，退出 6：DNS 被限制；未判定为版本不存在 |
| metadata 网络重试 | 已批准 A 范围的 require_escalated 同 URL，退出 0；10.0.403 对应 runtime 10.0.14，osx-arm64 官方 SHA512 已取回 |

## 当前限制

本段为实施启动阶段记录，保留真实时序；当前有效状态与精确交接见末节。Development self-check 不构成独立 QA 或 Human Owner 最终验收。

## 实施进展与保留失败

- 私有工具根 `/private/tmp/arch-be008-sdk-rfSK3RBg`；官方 URL `https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.403/dotnet-sdk-10.0.403-osx-arm64.tar.gz`，SHA512 `5893c66b48ea3674c7da18501059d606e96f3672fabe4d5e41762e692c7c83df3ee0b2b9dc5a0786191da2dc413d7335158101c14c935ab217f31ac2529770f3` 匹配；实际 SDK10.0.403 / runtime与ASP.NET10.0.14 / arm64。
- 第一次辅助校验使用系统 Python3.9 不具备的 `hashlib.file_digest`，退出127（前置脚本失败后未找到 dotnet）；改为标准库流式 SHA512，退出0。未为辅助工作安装依赖。
- 两项目首次 restore 均退出0，固定直接版本全部可恢复，两个锁文件已形成。首次 build 错用根 cwd 导致 MSB1009，退出1，无项目构建；回到 `backend-dotnet` 后 build退出0，0警告/0错误。后续 dotnet 项目命令均显式该cwd。
- SDK首次执行显示生成开发HTTPS证书；私有CLI存在 aspNetCertificateSentinel。窄范围只读检查用户 `.aspnet/https`、`.dotnet/corefx/cryptography/x509stores/my` 与 `security find-certificate -a -c localhost -Z` 未定位现存证书；这不能证明宿主完全无变化，未执行信任、dev-certs clean或清理用户环境。后续显式 `DOTNET_GENERATE_ASPNET_CERTIFICATE=false`，遥测关闭。
- A首次测试因VSTest loopback socket被沙箱拒绝退出1；相同命令在已批准范围经require_escalated后实际运行。最初完整8pass/1fail：disabled模块路由503；修正配置读取时机后仍失败，进一步断言 typed Enabled=false、单独进程测试通过，定位FastEndpoints同进程多宿主注册缓存。最终以真实新进程验证符合“重启采用”的disabled合同，完整9/9退出0；其stdout/TRX保留在私有工具根，后续持久化关键结果。
- B1 `prepare`退出0；固定三资源全部新建，run-root `/private/tmp/arch-be008-run-68i4YG5R`，runId `e0f8250b0e34faf81d88dac5`；mysql8.4.6/arm64，digest `mysql@sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`。结构25列/仅plans/四命名索引/无业务server defaults；app INSERT/SELECT，DELETE实际1142拒绝。
- B1首次POST500；独立EF诊断定位SQL别名 LocalTime 为MySQL保留字，固定版本内加反引号后主业务全部走通。此为同版本SQL适配，不改变版本/表合同。
- B1业务、Decimal/Unicode、重复/实际1062、同卷并发、分页/过滤/SQL输入、独立SELECT与新宿主读回均通过到AC15断线阶段；Stop后测试辅助 `docker port`不提供运行态端口输出，使Start前保护校验误失败。容器已按task/runId/containerId精确核对后恢复，退出0；改保护校验为静态HostConfig.PortBindings。失败TRX与8条合成行回读已持久化 [evidence/](evidence/)，主协调核实回收后Dev另起空实例重跑，不以B1部分成功当完整通过。
- 创建、异常及请求日志改为宿主注入的ILogger，避免同进程测试宿主关闭另一宿主静态logger；实际生产依然Serilog JSON Lines stdout/文件，关闭由host dispose flush。

## 最终 DEV self-check

以下是 Development 自检，不能解释为独立 QA verdict。所有项目 dotnet 命令 cwd 均为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend-dotnet`；SDK绝对入口 `/private/tmp/arch-be008-sdk-rfSK3RBg/sdk/dotnet`，CLI/NuGet三缓存明确指向同一私有根。VSTest与Docker/loopback命令因沙箱socket限制使用已批准范围的require_escalated。

| 命令/动作 | 最终实际结果/退出码 | 持久证据 |
| --- | --- | --- |
| `dotnet --version` | 0；10.0.403，官方SHA512匹配，runtime/ASP.NET10.0.14/osx-arm64 | 本文件工具链段；[精确依赖](evidence/dev-fixed-dependencies.json) |
| 两个项目 `restore --configfile NuGet.Config --use-lock-file` | 各0；首次锁定固定候选，无版本更换 | 两个packages.lock.json；精确依赖JSON |
| 两个项目 `restore --configfile NuGet.Config --locked-mode` | 各0；直接/传递依赖锁一致 | [候选清单](evidence/dev-candidate-manifest.json) |
| `dotnet build AIIS.Backend.Api.csproj --no-restore` | 0；0warning/0error | 候选清单的实际DLL/deps/runtimeconfig哈希 |
| `dotnet msbuild AIIS.Backend.Api.csproj -getItem:Compile,Content,None -nologo` + JSON断言 | 0；三类item无任何tests/** | 私有工具根api-items.json；本文件断言与最终候选csproj |
| `dotnet test tests/AIIS.Backend.Tests/AIIS.Backend.Tests.csproj --no-restore --filter 'TestCategory!=MySQL'` | 0；最终候选10/10，无库规则/输入/HTTP/模块/配置/真实日志轮转 | [最终A TRX](evidence/dev-a-final-candidate.trx)；前轮10项TRX保留 |
| `tests/scripts/run-mysql-tests.sh prepare --run-root /private/tmp/arch-be008-run-uzFgtzgt` | 0；新runId/三资源/空库/fixture，固定8.4.6/arm64 | [B3准备](evidence/dev-b3-prepare-evidence.json)、[manifest](evidence/dev-b3-manifest.json) |
| `BE008_TOOL_ROOT=... BE008_DOTNET=... TZ=UTC tests/scripts/run-mysql-tests.sh test --run-root /private/tmp/arch-be008-run-uzFgtzgt` | 0；最终候选综合真实MySQL用例1/1；覆盖结构/权限/业务/并发/失败/断线恢复 | [B3 TRX](evidence/dev-b3-mysql-1793167261719039000.trx)、[独立SELECT](evidence/dev-b3-select-readback.tsv) |
| 正式DLL两次独立进程（America/New_York→UTC）smoke | 各进程退出0；PID84752/94303已消失，创建/GET/重启读回25字段相同、时间相同；11行/仅plans不被启动修改；最终OpenAPI Decimal anyOf与6query检查通过 | [最终进程摘要](evidence/dev-b3-smoke-process-summary.json)、[请求](evidence/dev-b3-smoke-create-request.json)、[响应](evidence/dev-b3-smoke-create-response.json)、[SELECT](evidence/dev-b3-smoke-select-readback.tsv)、[OpenAPI](evidence/dev-b3-smoke-openapi.json) |
| 真实日志解析、随机秘密私下比对、1062/rollback requestId关联 | 0；146行JSON均可解析，真实Service named1062=1，其requestId `0HNPKN3CLC5KN` 有成功rollback；创建事件有requestId/planId，秘密无匹配；stdout/文件flush成功 | [日志摘要](evidence/dev-b3-final-log-summary.json)、evidence/dev-b3-http-logs-*.jsonl、dev-b3-outage-logs-*.jsonl、dev-b3-smoke-*.jsonl |
| 真实日志轮转 | A测试实写64条约1MiB日志；stdout64行JSON可解析，10MiB轮转、保留5文件、dispose后文件可读 | 最终A TRX的JsonLinesRotateRetainAndFlush |
| `bash -n tests/scripts/run-mysql-tests.sh` 与裸脚本 | 各0；裸入口只帮助，无资源动作 | 脚本源码、本文件 |
| 任务限定 `git diff --check`、新文件中文头/空白/本地链接检查 | 0；54文件、190个本地Markdown目标存在；批准spec SHA不变 | [文档检查](evidence/dev-source-document-check.json) |
| 主协调根级全库治理checker | exit1、320行，与开始前320行诊断多重集完全一致，新增0/删除0；全库未通过 | [根级诊断增量](evidence/coordinator-governance-increment.json)；不是本任务整改全库的授权 |

Development曾额外显式指定 `backend-dotnet` 参数运行治理checker：exit1/324行，其中根PLAN两条tasks链接已由主协调移除；另两条来自旧工具仅识别本地`plans/*/spec.md`，而本spec明确允许模块索引根`../plans/`唯一bundle。此检查范围不同于上表根级全库复查；不伪造本地bundle/链接迎合旧checker，不能把这两条当作根级全库新增。

### 最后修复与失败历史补充

- B2新空实例完整1/1退出0、正式进程与日志通过；主协调已核实回收三资源，证据 [B2协调回收](evidence/coordinator-dev-b2-cleanup.json)。B1回收证据 [B1协调回收](evidence/coordinator-dev-b1-cleanup.json)。两轮原始run-root仍暂存私有日志/秘密，供协调按资源表收尾，不复用其内容作为fresh QA。
- 为将顺序预查409与真实唯一键失败区分，新增稳定`plan_unique_conflict`（仅命名1062）及成功`plan_transaction_rolled_back`事件；真实16并发同字面测试按requestId关联二者且SELECT只有1条，未增加failpoint、拦截器、锁或新表。B3最终候选全矩阵及正式DLLsmoke重跑，而非沿用修改前证据。
- OpenAPI最初将CLR Decimal描述为number/double且遗漏手动绑定query；同固定包版本内增加schema/operation transformer，明确number|string、六查询参数，六必填由JsonRequired标记。最终A与正式OpenAPI检查通过；没有新增实际API。
- 最终smoke辅助在首API已正常退出0后，立即裸socket bind短暂返回EADDRINUSE，辅助退出1，未启动第二进程。后续只读lsof/netstat未发现18108监听者，首PID已不存在；继续原第二进程完成，不重复创建。最终两个进程退出0、PID消失；以SO_REUSEADDR实际重绑定证明无监听占用，未杀未知进程。不能把这次辅助失败抹去，也不据此宣称是已证实的具体内核状态。
- 中间一次诊断编辑命令因cwd相对路径重复而FileNotFound，未写文件；随后以正确cwd重跑。所有失败/局限均保留，不将工具辅助错误归因于固定版本不存在或替换版本。

## AC 对照（Development）

| AC | 本轮DEV证据与边界 |
| --- | --- |
| AC01 | 精确r1 A+B批准、spec当前SHA与八来源不变，diff写入限allowlist；未创建checklist/给QA或Owner结论 |
| AC02 | SDK官方校验/固定全直接包/双锁/locked restore/build均0；私有CLI/NuGet；MSBuild三item排除tests |
| AC03 | A真实启用三业务路由；新进程disabled三404且OpenAPI无Plan；只有health/OpenAPI基础入口、无鉴权 |
| AC04 | A逐个必填缺失、所有非remark null、错误类型/未知重复snake/非法Unicode；HTTP绑定统一422，B无脏行 |
| AC05 | B最小默认/全部非零可选/25输出字段/GET相同；独立SELECT，真实MySQL无Mock |
| AC06 | A原始数文本精度/语法；B最大值/多余尾零/超scale范围拒绝，string固定scale、DB回读无double |
| AC07 | Python strip/control顺序、Unicode标量、原卷号保留；顺序ASCII变体409；非ASCII限制留README |
| AC08 | 两并发1成功1冲突/SELECT1；另16并发实际触发Service命名1062并成功回滚，日志requestId关联；不同原始字面canonical并发不作原子承诺 |
| AC09 | ID正整数/存在/不存在及0负数非整溢出；未实现操作404/405，不假成功 |
| AC10 | 空列表/真实总数/超末页、四过滤、同秒ID倒序、页长页码offset边界；未知priority/sort无效 |
| AC11 | 引号/SQL片段参数化输入仍为空结果，%/_按LIKE通配；表未改变 |
| AC12 | fixture对照冻结d2片段：25列精确类型、仅remark nullable、无业务server defaults、原四命名索引、仅plans |
| AC13 | 创建一次DB CURRENT_TIMESTAMP同值赋双时间、秒精度+08；GET时间不变；最终NY/UTC正式进程验证上海输出 |
| AC14 | 非法请求无写入；真实named1062后同requestId rollback确认、竞争只1条、原记录完整相同；上下文后续可用 |
| AC15 | B3明确stop→请求503且无行→start→真实创建/查询；正式DLL重启读回，schema/行数无启动变化 |
| AC16 | INSERT/SELECT应用账号真实运行，DELETE1142；启动无DDL/seed，空配置启动失败不回显连接串 |
| AC17 | A真实轮转/保留/flush；B3 stdout/文件146行JSON解析、requestId/planId与秘密私下比对，无泄漏 |
| AC18 | 双语README/PLAN/catalog与CODE_INDEX完整，Python差异、失败退出码/限制留存；最终DLL对应候选hash |
| AC19 | Development只交实际精确candidate/资源/命令；fresh Verification由主协调下一gate启动，独立证据与最终验收尚未发生，不由DEV宣称通过 |

## 资源与明确限制

完整临时路径/类型/大小见 [自有临时资源清单](evidence/dev-temporary-resources.json)。归属均为本任务Development；不包含主协调 `/private/tmp/arch-be008-coordinator-wkj0jq0q`，更不包含FF/DAA或其他任务资源。

| 资源 | 用途/当前依赖/清理入口 |
| --- | --- |
| `/private/tmp/arch-be008-sdk-rfSK3RBg` | 官方SDK归档/解压、私有CLI/NuGet缓存、A TRX、MSBuild清单；必要证据已持久化，暂供本任务后续核验；协调确认QA不再依赖后删除 |
| `/private/tmp/arch-be008-run-68i4YG5R` | B1失败证据/随机秘密；三Docker资源已协调回收；持久证据完成后协调删除私有目录/凭据 |
| `/private/tmp/arch-be008-run-GyiTC6VL` | B2完整证据/秘密；三Docker资源已协调回收；持久证据完成后协调删除 |
| `/private/tmp/arch-be008-run-uzFgtzgt` | 最终B3完整证据/秘密、正式API日志/PID退出；全部必要脱敏证据已持久化；API已停；三资源已由主协调核实回收，供QA另起新空实例 |
| B3 `aiis-arch-be008-mysql` / `aiis-arch-be008-net` / `aiis-arch-be008-mysql-data` | runId `2c9e03db9080c5c960a29359`；本轮仅11条合成计划，mysql8.4.6/arm64；主协调已按下方精确cleanup移除，三资源均不存在，无真实数据 |
| `/private/tmp/arch-be008-*-<GUID>` 与初期系统TMPDIR同前缀日志 | A in-process/disabled/64MiB轮转验证日志；清单逐项列出；无运行依赖，证据已归TRX，协调确认归属后回收 |
| `/private/tmp/arch-be008-release-metadata.json`、`arch-be008-tool-root.path`、`arch-be008-run-root.path` | 本任务公开metadata及helper路径指针；非秘密必要结论已持久化，协调最终收尾 |
| `backend-dotnet/**/bin`、`obj` | 交付工作树实际构建输出，被.gitignore排除；QA可重建，不提交。源码与实际DLL哈希已记录 |
| 正式API18108 | 最终PID84752/94303均正常退出0且已消失；无监听/重绑定通过；B2早期PID68763/69096亦已停 |

B3三资源的批准内精确协调清理命令已由主协调在归属/证据核对后执行，退出0；[B3协调回收证明](evidence/coordinator-dev-b3-cleanup.json)确认三资源不存在、13388/18108以SO_REUSEADDR实际重绑定通过。Development只机械复制该真实事实，不冒认自己执行。可复现命令如下（不是要求再次运行）：

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch
BE008_COORDINATOR_CLEANUP_CONFIRMED=2c9e03db9080c5c960a29359 \
  backend-dotnet/tests/scripts/run-mysql-tests.sh cleanup \
  --run-root /private/tmp/arch-be008-run-uzFgtzgt
```

SDK首次HTTPS证书生成消息的宿主副作用不能完全定位；后续关闭生成，未做用户证书清理。真实COMMIT ACK丢失未实证：代码将尝试提交后未确认归`plan_write_outcome_unknown`，不盲重试/不假称回滚；没有新幂等表或故障框架。非ASCII完整casefold/既有collation等价、跨字面canonical并发原子唯一、跨请求分页快照均不在首期保证。学习切片无认证，仅loopback/专属测试；真实数据库采用、生产部署、既有前端/业务切换、MES/PLC及Owner最终验收仍需独立任务/gate。

## 首次 developer_handoff（历史，QA1已返回返工）

- Revision：`ARCH-BE-008 r1`，唯一批准spec SHA256 `998a56f2c97639d958cb61ab1b90ed1b7e4fa5c7329c38a4a18c6b7a199162f8`，实质范围未变。
- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b` 上的未提交变更；未commit/stage/push、未改spec/checklist/既有Python或其他runtime。
- 实现冻结：44个源码/配置/锁/测试文件的确定性组合SHA256 `20a7474a4f9766bec0f70f081c56a7f5a77922caf1efe64ccad839efe022aad5`；算法、逐文件和实际API/测试DLL哈希见 [候选清单](evidence/dev-candidate-manifest.json)。Markdown交接/索引状态不纳入此实现hash；最终文档完整性另行检查。
- 锁：API `2020c500652154081b9944687397b8012286ccab3a3aefc57a62b051cb2ba0ce`；测试 `1d6cab6be94310b1767f4894553f320484b700506b2f55c4061ed57ed3701bc9`。
- 修改面：新增完整`backend-dotnet`（单根API、Common/Configuration/Infrastructure、唯一Plan模块、一个MSTest工程、fixtures/infra/scripts、双语说明/索引与CODE_INDEX）；根README pair/CODE_INDEX仅新backend-dotnet入口；本tasks及实际evidence。根PLAN/catalog由主协调独立机械同步，不归Development写入。
- DEV结果：最终locked restore/build0、A10/10、B3真实MySQL1/1、正式DLL两进程smoke/日志/重启回读通过；完整失败历史、限制、资源均见上文。
- 下一gate：B3自有三资源已由主协调核实释放；主协调启动新的 `agent_type=verification, fork_turns="none"`，提供批准spec、当前tasks/候选manifest、diff/锁/正式源码、A+B批准和运行证据；QA在新空实例独立取证并创建checklist，不复用DEV结论。独立QA verdict与Human Owner final acceptance均pending。


## QA1 返工：F-QA1-001（rework1）

独立QA1已在 [checklist.md](checklist.md) 正式记录qa_failed。原候选 `20a7474a...` 的A10/新空MySQL/其余正式HTTP/重启/日志证据保留，但text/plain、application/octet-stream、application/x-www-form-urlencoded的POST415没有错误体，违反spec§7.2；既有A只检查415状态，漏检错误体。QA1归档在 [evidence/qa1/](evidence/qa1/)，Development不写checklist、不覆盖旧manifest/失败记录。

本轮仍为获批r1 A+B，不换包/SDK/表/路由。先新增完整415信封HTTP回归证明旧实现失败；最小修复面为公共ErrorBoundary对框架未抛异常的415路径统一映射，保留404/405。随后必要locked restore/build、完整A、新空B、正式DLL媒体类型/422/404/405/日志和跨时区重启验证。QA1三资源已由主协调核实回收，证明 [QA1协调回收](evidence/qa1/coordinator-resource-cleanup.json)；本轮另起空实例，不复用QA数据/秘密。

### 返工根因与最小修复

- 根因：Plan的Accepts媒体元数据可使框架以非异常方式返回415，原ErrorBoundary只处理抛出的异常，故三个非JSON媒体返回`Content-Length:0`且无错误体；缺Content-Type另有更早开始响应的路径。原测试只看状态，未验证协议体。
- 实现仅改 `backend-dotnet/Common/Errors/ErrorBoundary.cs`：对已匹配POST入口的JSON媒体元数据，在框架开始响应前拒绝缺失/不符Content-Type；next返回未开始的415也走既有PlanException映射；写统一JSON前清除框架的Content-Length:0。沿用已有requestId及`plan_request_failed`/`plan_invalid_request`日志，不增加路由/钩子/依赖，404/405不转业务错误。
- 回归仅改 `backend-dotnet/tests/AIIS.Backend.Tests/Contracts/HttpTests.cs`：新增完整信封、Content-Type、requestId及timestamp断言，覆盖原三媒体、+json和缺Content-Type，并检查422与基础404/405；删除原先仅断言415状态的弱检查。
- 与QA1冻结44文件逐项比较，只有上述2文件变更；固定SDK/包/双锁、其他42文件不变。旧candidate与所有DEV/QA1证据均保留。

### 返工真实命令、结果与失败历史

SDK仍为 `/private/tmp/arch-be008-sdk-rfSK3RBg/sdk/dotnet`；三个CLI/NuGet路径仍显式在同私有根，证书生成/遥测关闭。dotnet命令cwd仍为正式交付树 `backend-dotnet`；VSTest/网络/专属Docker使用已批准A+B范围的require_escalated，未安装新辅助依赖。

| 实际动作 | 退出与结果 | 持久证据 |
| --- | --- | --- |
| 新增目标测试，旧实现 `dotnet test ... --no-restore --filter 'FullyQualifiedName~UnsupportedMediaHasUnifiedEnvelope'` | 1；准确复现text/plain415空body，失败在“必须有统一信封”断言 | [before-fix.trx](evidence/dev-rework1/results-a/before-fix.trx) |
| 首轮after-next映射修复后，同一目标测试/第一次完整A | 1；原三个媒体和+json已正确，但缺Content-Type仍空415；未将部分通过当最终结果 | [after-fix.trx](evidence/dev-rework1/results-a/after-fix.trx)、[第一次A输出](evidence/dev-rework1/a-attempt1.log)、results-a/rework1-a.trx |
| 增加已匹配POST的JSON元数据提前校验后，目标测试 | 0；1/1，完整415及422/404/405对照通过 | [after-guard.trx](evidence/dev-rework1/results-a/after-guard.trx) |
| 两项目 `restore --configfile NuGet.Config --locked-mode` | 各0；固定双锁不变 | [API restore](evidence/dev-rework1/restore-api-final.log)、[测试 restore](evidence/dev-rework1/restore-tests-final.log) |
| `dotnet build AIIS.Backend.Api.csproj --no-restore` | 0；0warning/0error | [build](evidence/dev-rework1/build-final.log) |
| 完整 `dotnet test ... --no-restore --filter 'TestCategory!=MySQL'` | 0；11/11，包括新的完整415错误体回归及原全部A | [最终A TRX](evidence/dev-rework1/results-a/rework1-a-final.trx)、[A输出](evidence/dev-rework1/a-final.log) |
| `tests/scripts/run-mysql-tests.sh prepare --run-root /private/tmp/arch-be008-run-GnRSwKDz` | 0；新空实例、新随机凭据；runId013d21e7c16865760980de3a，固定8.4.6/arm64/digest不变 | [prepare](evidence/dev-rework1/mysql/prepare-evidence.json)、[manifest](evidence/dev-rework1/mysql/manifest.json) |
| `BE008_TOOL_ROOT=... BE008_DOTNET=... TZ=UTC tests/scripts/run-mysql-tests.sh test --run-root /private/tmp/arch-be008-run-GnRSwKDz` | 0；完整真实MySQL1/1，含真实named1062/确认rollback、断线503与恢复、独立SELECT、结构/最小权限及全部原业务矩阵 | [B TRX](evidence/dev-rework1/mysql/results/mysql-1793169974042550000.trx)、[SELECT](evidence/dev-rework1/mysql/select-readback.tsv) |
| 私有正式DLL helper首轮 | 1；Python3.9 HTTPConnection不支持context manager，尚未发业务请求；finally停止自建启动期进程，退出-15且PID已消失，不算正式smoke通过 | [辅助失败记录](evidence/dev-rework1/formal-attempt1/failure.json)、同目录原stdout/PID/exit |
| 仅修私有helper连接释放写法后，`python3 formal-probes.py <本轮run-root> <本轮work-root>` | 0；18正式HTTP用例，7种非JSON均完整415及关联稳定错误日志；422、业务404、基础404/405保留；拒绝输入前后全表内容指纹相同 | [实际helper](evidence/dev-rework1/formal-probes.py)、[全部请求响应](evidence/dev-rework1/formal-http-cases.jsonl)、[摘要](evidence/dev-rework1/formal-summary.json) |
| 最终正式DLL NY→UTC两个串行进程 | 各0；PID59837/59873已消失，18108 SO_REUSEADDR实际重bind；25字段/双时间相同，11行/仅plans；启动无增行/DDL | [formal-summary](evidence/dev-rework1/formal-summary.json)、[创建响应](evidence/dev-rework1/create-response.json)、[独立SELECT](evidence/dev-rework1/formal-select-readback.tsv)、formal-first/second原始stdout与exit |
| 日志解析与私下秘密比对 | 0；正式stdout/文件74行JSON可解析；7条非JSON响应requestId逐一关联`plan_invalid_request`事件，随机秘密/完整连接串匹配0 | formal-summary.json、formal-logs/、原stdout；不复制凭据 |
| 续接后的必要完整性复核 | 0；44源文件与4构建artifact逐项匹配新candidate；37件已归档文件250980字节逐项SHA/大小匹配；批准spec未变 | [新候选](evidence/dev-rework1-candidate-manifest.json)、[归档manifest](evidence/dev-rework1/archive-manifest.json) |

原批准媒体边界的正式回归为：text/plain、application/octet-stream、application/x-www-form-urlencoded、application/merge-patch+json、application/problem+json、multipart/form-data和缺Content-Type。均HTTP415，包含code415/message与errorCode为plan_invalid_request/data=null/timestamp、JSON Content-Type和requestId。application/json;charset=utf-8实际创建成功；不存在路径与不支持方法不伪造业务错误或成功。

### 模型容量工具失败与续接

主协调在上述37件证据与新candidate已持久化、最后进度消息之后观测到 `Agent errored: Selected model is at capacity. Please try a different model.`。该返回是角色工具/模型容量失败，不是软件测试失败，也不能证明已保存文件丢失。本命名Development按主协调指令原角色续接，先核对tasks尚未完成返工handoff；不换模型/角色，不重做已通过软件/测试，不改冻结44文件。续接只收束本tasks及必要文档/链接/哈希，已验证持久candidate/4artifact/37归档内容仍匹配。

### rework1 精确 developer_handoff（当前有效）

- Task/Revision：`ARCH-BE-008 r1` 原Human Owner批准A+B；spec SHA256仍为 `998a56f2c97639d958cb61ab1b90ed1b7e4fa5c7329c38a4a18c6b7a199162f8`。F-QA1-001的DEV修复与自检完成，待新fresh QA2独立核实；不由Development关闭QA finding或授予验收。
- 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，仍为HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b` 上未提交交付；没有stage/commit/push，保留并行修改。
- 新44文件candidate SHA256：`a9afc3bb5a75a610f25e6a42cbc694e019e0e66247c8c60926ca03cff78819f6`，算法同首次“排序相对路径+LF+文件SHA+LF”，逐文件与4构建artifact见 [新manifest](evidence/dev-rework1-candidate-manifest.json)。实际API DLL SHA256 `8abae9632c4f6bff12e675e000adaa2af8c35bb25941180e3fdb08b6bc49f152`；正式进程使用该交付树DLL。
- 双锁仍为API `2020c500652154081b9944687397b8012286ccab3a3aefc57a62b051cb2ba0ce`、测试 `1d6cab6be94310b1767f4894553f320484b700506b2f55c4061ed57ed3701bc9`。SDK/所有包/表/路由/无认证等原r1范围不变。
- 本轮改动只为ErrorBoundary.cs、HttpTests.cs、本tasks和新`evidence/dev-rework1*`。旧manifest/DEV证据、QA1/checklist/spec、四根索引和其他源码均不写。源码拓扑未改变，不扩写索引或抽象。
- DEV证据：固定锁restore/build0；A11/11；新空B真实MySQL1/1；正式18HTTP、7类完整415及稳定错误日志、拒绝无写入、NY→UTC25字段/时间持久读回/无启动DDL与seed通过。旧QA1 qa_failed与原/本轮辅助失败全部保留。
- 本轮临时根 `/private/tmp/arch-be008-dev-rework1-57i2YIoP`：命令/失败TRX/正式helper/日志；本轮DB根 `/private/tmp/arch-be008-run-GnRSwKDz`：新runId `013d21e7c16865760980de3a`、0600秘密、DB日志。API已停且PID/端口无运行依赖；固定三Docker资源已由主协调核对runId/归属后cleanup退出0，三资源均不存在、13388/18108实际可重bind；见 [协调回收证明](evidence/dev-rework1/coordinator-resource-cleanup.json)。[资源handoff](evidence/dev-rework1/resource-handoff.json) 保留回收前的真实交接时事实，不覆盖原37件归档。必要37件脱敏证据已持久，旧QA1和旧DEV临时根不供新实例复用。SDK/私有缓存仍保留供本任务QA2；其余A生成GUID日志及本轮根由协调依用途/归属与后续依赖核对收尾，不删除任务外资源。
- 限制未变：首期无认证且只loopback/专属测试；非ASCII完整casefold/任意collation等价、跨字面canonical并发原子唯一、跨请求分页快照不保证；真实COMMIT ACK丢失未实证，保留结果未知处理；无真实采用/部署/MES/PLC/Owner验收。
- 下一gate：主协调提供上述精确候选、批准spec、当前tasks、旧qa_failed与返工证据，启动新的 `agent_type=verification, fork_turns="none"`；QA2另起新空实例独立验证并更新checklist。不能用DEV11/1/18通过覆盖QA1失败，也不能跳过fresh QA2或Human Owner最终验收。
