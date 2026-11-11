Task ID: FF-003
Revision: r2
Status: dev_blocked
Owner Role: Development
Allowed Writers: Development
Handoff: Development source and auxiliary macOS self-check recorded; required native Windows evidence unavailable, no developer_handoff yet
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 独立 C# FF、Windows 10 x64 自包含目录、每 PLC 一个 JSON 与 demo01 本机 S7 INT16 闭环
Owner: Field Flow
Acceptance Chain Reference: FF-003 r2 scope approval -> Development -> fresh-context Verification -> Human Owner final acceptance

# FF-003 r2 Development 记录

## 批准、候选和当前阻塞

Human Owner 于 2026-11-10 明确回复“批准 FF-003 r2”，随后对 Windows 实验宿主回复“暂时没有，先完成源码和 Mac 自检”。PM 登记的获批草案 SHA256 为 `0554de2376a5d644fe2ae13d6804f2dd498ffef37e9cc21ccf234f58fd59fb3a`；含批准登记和保留历史的当前 [spec.md](spec.md) SHA256 为 `e83cf7653b9a2d5407ebb0be3a83b0d474bade2d09d0c5c83ffbbe717a8d4893`。实际角色是 Development `/root/ff003_r2_development`；`contract_only` 依主会话、任务文件和 diff 审计执行。

在约定交付工作树创建了 [field-flow-csharp](../../field-flow-csharp/)，没有提交 Git；候选由 [53 个逐文件 SHA256](evidence/r2-development-macos/source-sha256.json) 精确固定，该清单文件 SHA256 为 `88da97ae9422be4cc5b7edf027a7a59a7bc24a974bea1c7483aacd3e1eb1acc4`。独立源码副本与这 53 个文件逐项相等。脱敏的 [Mac 自检、测试名称及进程数据](evidence/r2-development-macos/self-check.json) 随任务保存。工作树有任务外并行修改；本角色没有重置或声称它们属于本任务。

**阻塞：**获批 r2 的 AC01–AC08 要求拟定的 Windows 10 Enterprise LTSC 2021 x64 原生执行、独立复制验证和 self-contained publish；当前没有该 Windows 主机，用户已要求先做 Mac。现阶段只能记录 `dev_blocked`，不能从交叉编译或 Mac 自检推断 Windows 原生通过，也没有发出 `developer_handoff`。具备获准宿主后，Development 应从上述精确源码与锁复跑原生标准、补齐证据并进行真实交接，随后才进入 fresh-context Verification 和 Human Owner 最终验收。

## 实际实现面

- 三个独立 .NET 项目：产品、测试和自身 HTTP/S7 fixture；固定 SDK `10.0.403`、`net10.0`、runtime 目标 `10.0.14`、自身 NuGet.org 源及三份 `win-x64` 锁。产品直接包为 Hosting `10.0.14`、SQLite `10.0.14`、YamlDotNet `16.3.0`；测试包及传递依赖见各自清单与锁。
- `config/demo01.yaml` 使用 v2，一台 PLC 一份 JSON；样例 A / B 原字节 SHA256 分别为 `fcda187b9a72bd75720409a4a9b84c1feb0b4bb8c01f98af027e945fcad9535d` / `614e35946c63a622642d881b911b5c2f869e2840dd3ee8139e5d71e8a07a4b53`。预检冻结配置及文件 hash，拒绝不受支持的协议与来源、错误字段、重叠和不安全路径。
- 多流独立调度；每台 PLC 有自己的连接持有者和有界 FIFO，已入队等待也受队列期限约束。S7 只支持规格所列标准 DB INT16 子集，核对对应请求的完整 ACK；连接失效先关闭旧 I/O 再恢复，ref 耗尽前更换会话。
- `demo01` 使用 typed 命令和意图，状态执行器通过 SQLite 记录 `pending`、`in_flight`、`confirmed`、`unknown`、`simulated` 等状态。重复身份不会刷新原期限；不能确认的写保留 unknown、阻止重叠写入并等待核实，不自动重发。默认 dry 只读；写须显式 `--execute` 和匹配的独立 execute 库。
- 提供帮助、只读 validate/inspect、synthetic init 和 run；结构化日志包括必要身份、时长与稳定错误键，关停时关闭接纳与发送闸门并按全局预算等待自有任务。独立双语 README、BUILD、PLAN、代码索引、locale 和 notices 均在工程内。BUILD 的复制 exe 和空 cwd 命令尚未在 Windows 执行。

## 辅助 Mac 自检

2026-11-10，Darwin `24.6.0` arm64，已存在 .NET SDK `10.0.403` 和 runtime `10.0.14`。运行与构建使用任务根 `/private/tmp/ff-003-r2-dev-A6vZEa` 下隔离的 CLI home、NuGet packages/HTTP cache、构建、临时文件和 synthetic 状态，使用 `DOTNET_GENERATE_ASPNET_CERTIFICATE=false`、`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH=false`、`DOTNET_CLI_TELEMETRY_OPTOUT=1`、`MSBUILDDISABLENODEREUSE=1`。两条只读环境盘点 `dotnet --list-sdks` / `--list-runtimes` 后续调用时没有携带这些变量，输出仅见已安装列表，没有额外首次运行提示；不能据此证明宿主其他状态未改变。

本地受限环境的 NuGet DNS 首次 restore 报 `NU1301`、exit 1；按批准的公共源和私有缓存进行自动升级后成功，后续产品、fixture、tests 的 `win-x64` `--locked-mode` restore 均 exit 0。普通沙箱的 socket bind 报 `SocketException(13)`，受限的本机夹具不能启动；后续按授权自动升级，只使用 `127.0.0.1:34102`、`34880` 的独立测试。首次任务 CLI home 的 restore 还输出了原文：

```text
CSSM_ModuleLoad(): One or more parameters passed to a function were not valid.
已安装 ASP.NET Core HTTPS 开发证书。
若要信任该证书，请运行 "dotnet dev-certs https --trust"
```

该提示本身不能确定钥匙串实际写入情况；没有运行 trust 命令，也没有修改或清除用户证书。后续构建、restore 和测试设置了上述证书生成 opt-out。

以下为最终候选实际检查；运行路径均为此工程或其独立副本，命令中的 `$FF_TMP` 指上述任务私有根，`$FF_DOTNET` 指 `/usr/local/share/dotnet/dotnet`。所有退出码均来自实际命令：

```bash
# 在工程根，Mac 图写入私有锁，正式 win-x64 锁不被覆盖。
$FF_DOTNET restore tests/FieldFlow.Tests/FieldFlow.Tests.csproj --configfile NuGet.Config \
  -p:RuntimeIdentifier=osx-arm64 -p:RuntimeIdentifiers=osx-arm64 -p:SelfContained=false \
  -p:FFBuildRoot=$FF_TMP/mac-build2 -p:FFLockRoot=$FF_TMP/mac-lock2
$FF_DOTNET build tests/FieldFlow.Tests/FieldFlow.Tests.csproj --no-restore --disable-build-servers \
  -p:RuntimeIdentifier=osx-arm64 -p:RuntimeIdentifiers=osx-arm64 -p:SelfContained=false \
  -p:FFBuildRoot=$FF_TMP/mac-build2 -p:FFLockRoot=$FF_TMP/mac-lock2
$FF_DOTNET test tests/FieldFlow.Tests/FieldFlow.Tests.csproj --no-build --no-restore \
  -p:RuntimeIdentifier=osx-arm64 -p:RuntimeIdentifiers=osx-arm64 -p:SelfContained=false \
  -p:FFBuildRoot=$FF_TMP/mac-build2 -p:FFLockRoot=$FF_TMP/mac-lock2 \
  --logger 'trx;LogFileName=final7.trx' --results-directory $FF_TMP/test-results-final7
```

Mac restore exit 0；最终 build exit 0、0 警告/0 错误；最终 test exit 0，21 passed、0 failed、0 skipped。隔离复制工程使用自身复制后的源码、私有 `copy-build`/`copy-lock`/`copy-tmp` 和同一任务自有包缓存，restore、build、test 均 exit 0，最终同为 21 passed、0 skipped；源码和锁与交付候选的 SHA256 逐项一致。测试包括固定 S7 帧与 INT16、截断/错 ref ACK、unknown 恢复、相邻字节、慢 HTTP 并发、就绪前停止、队列已接纳但未领取时超时和配置路径边界。

`win-x64` 依各项目 `dotnet restore --locked-mode --configfile NuGet.Config -p:RuntimeIdentifier=win-x64 -p:SelfContained=true -p:RuntimeFrameworkVersion=10.0.14 -p:FFBuildRoot=$FF_TMP/win-locked-build` exit 0；最后在 Mac 上对 tests 项目及其 product/fixture 引用执行同样目标参数的 `dotnet build -c Release --no-restore --disable-build-servers`，exit 0、0 警告/错误。此项只是 Mac 主机交叉编译，没有运行 Windows 可执行文件，也没有执行 publish。

实际独立进程 fixture 加产品的五组合成检查 exit 0，使用任务自有 `process_cases.py final3`：dry 读取 1 次、写 0 次；正常模式连续 10 次 GET、单会话写 1 次、confirmed 1，重启仍保持写 1 次；已应用写后丢 ACK 与坏 ref 各保持 unknown 1，重启不重发；未就绪时停止保持 canceled 1、写 0。五组共等待 13 个自有进程退出，并逐场重绑 34102/34880；未对其他进程发送信号。CLI 从空 cwd 的无参及英文帮助 exit 0，非法语言 exit 2；非法目标预检 exit 2，原 synthetic 库 hash 不变且无新文件。结果见附带 JSON；这些仅证明 Mac 合成场景。

历史失败均保留在私有原始日志中：早期测试有 11 passed / 1 failed（Windows 路径测试样例的 YAML 引号构造不当），修正测试输入后全过；另有一次遗漏构造参数的测试编译失败，补全后全过。之前项目局部 `obj` 干扰导致重复属性，已以工程 `DefaultItemExcludes` 修正并重新编译。最终候选两次在普通沙箱内并行 build 无输出，人工中断为 exit 130；顺序在获准环境中重跑得到上述真实 exit 0。没有将这些历史失败当作通过。

静态检查：53 个候选文件与独立副本逐个 SHA256 一致；JSON 解析、本工程 Markdown 本地链接、C# 职责头、英文/中文 locale 键对称和尾随空白检查均通过；`git diff --check` 对当前任务范围 exit 0。所有正式变更在交付工作树，不仅存在于临时副本。

## AC 覆盖和未完成事项

| AC | 当前事实 |
| --- | --- |
| AC01 | Mac 原生 21 项及复制工程通过，Mac 上锁定 win-x64 还原/交叉构建通过；Windows 原生 build/test/apphost 未运行。 |
| AC02 | Mac 测到 A 目录和部分非法 JSON、Windows 路径、symlink、预检无状态变化与空 cwd 帮助；完整 Windows 路径语义及全部负例仍须原生复核。 |
| AC03 | Mac 固定帧、匹配 ACK、截断/错 ref、实际合成读回及相邻字节检查通过；Windows 的迟 ACK、关闭旧 I/O、完整超时/断连矩阵尚无原生证据。 |
| AC04 | Mac dry、显式 execute、连续 10 GET 和原库重启最多写一次通过；全部冲突、失效矩阵仍须按规格在 Windows 复核。 |
| AC05 | Mac 合成已写无匹配 ACK、恢复 unknown、同命令重启不重发及重叠资源阻断测试通过；Windows 原生过程和读回后行为仍待验证。 |
| AC06 | Mac 慢 HTTP 不挡另一流、一个 owner 有界排队、就绪前停止及进程/端口释放有辅助证据；两流同一 session 的精确计数、在途 Ctrl+C、全部锁和 Windows 资源释放仍须原生核验。 |
| AC07 | 尚未在 Windows 发布、复制自包含目录并运行 exe；实际 runtime/SQLite native 资产清单、hash 和独立于 SDK 的启动均未验证。 |
| AC08 | 此文件是 Development 自检及阻塞记录；未进行 Development 正式 handoff、独立 QA 或 Human Owner 最终验收。 |

## 资源、回退与限制

`/private/tmp/ff-003-r2-dev-A6vZEa` 是本任务所有的私有 SDK 使用环境、包缓存、构建、复制工程、合成状态和原始日志；为后续复核保留，解除证据依赖并核对无进程使用后由协调者按资源规则清理。最终五组进程已等待结束、端口已重绑验证。此前生成在本工程的六个 task-owned `bin/obj` 目录，在 `lsof` 未发现打开文件后已删除；保留的正式证据无需依赖这些目录。没有连接真实 PLC、第三方 HTTP 或真实数据库，没有部署、发布、安装服务、改其他 FF 版本或发送邮件。

真实设备、PLC 型号/固件、长期运行、Windows 控制台/文件锁与现场托管均无验证结论。未知写必须保留状态和日志、人工核实效果；回退从停止新写并保全记录开始，不能通过删库解除阻断。原生验证、发布与最终验收应继续按 r2 范围和角色顺序执行。
