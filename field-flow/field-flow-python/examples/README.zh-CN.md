# Field Flow Python 基础案例

[English](README.md)

本目录由上层PLAN管理，三个case使用现有YAML v1、FF-001 r4 typed INT / Execution能力。源码可运行状态与DEV自检、独立QA和Owner终验分开；最新精确证据归FF-005任务bundle。每次只运行一个case。

| Case ID | 目的与入口 | Config / kind | Status / capability version |
| --- | --- | --- | --- |
| basic01 | 复用既有 [src/field_flow/app/demo01.py](../src/field_flow/app/demo01.py) | [loopback.yaml](../config/loopback.yaml) / demo01 | runnable / FF-001 r4 |
| basic02 | 先读target INT；负数才GET及执行: [src/field_flow/app/plc_guard_get_int.py](../src/field_flow/app/plc_guard_get_int.py) | [basic02.yaml](../config/basic02.yaml) / plc_guard_get_int | runnable / FF-005 r1 A, YAML v1 |
| basic03 | GET后先原typed解析；value≤0和value>100各自提前返回: [src/field_flow/app/get_value_guard_int.py](../src/field_flow/app/get_value_guard_int.py) | [basic03.yaml](../config/basic03.yaml) / get_value_guard_int | runnable / FF-005 r1 A, YAML v1 |


case ID是教学身份，flow.id是流身份，kind选择显式派发；source_id / command_id是命令身份。basic01没有复制另一份demo01。basic02使用同一target作条件和写点：默认DB1 offset0初值A5A5=-23131，首次允许42；execute写42后继续至少10轮独立读，不再GET/写。dry_run不改内存，仍逐轮读负数/GET，原命令只simulated一次。basic03只允许1..100；业务false仅结束本轮，runtime继续，无普通false逐tick持久日志。读失败传播原错误，不用0或上轮值替代。ready=false是严格idle，四个命令字段必须null；非法/过期输入在业务判断前报原错误。

同流一轮后等待500ms，不重叠；不同流并发，每PLC已有owner/driver持久连接只串行自身IO。HTTP和timer不占PLC执行位，重复读是独立采样，不是缓存或采样去重。条件读后写不是PLC原子比较写、工艺互锁或跨点一致快照。

所有写经Execution。confirmed只证明协议ACK和本地提交，非机器动作/业务完成。若PLC已写42但ACK丢失，basic02后续可能guard_false/health.running；必须看原`state inspect`的unknown和health.store/state，不能把skip当完成、回读升级confirmed、清库或盲重发。新增harness以无有效ACK（截断）证明unknown保留。旧hold_ack完整扣留ACK曾触发driver强制回收，该资源失败保留，不能据此宣称完全丢ACK下正常回收。原库重启保留配置/instance/source/command/issued/expires，不换case/kind/库规避TTL/幂等或unknown。不同case/语言不自动迁移状态。

新增app不产生新时间字段。来源Unix毫秒、monotonic耗时按自身语义；既有JSONL/SQLite日历UTC与根+08合同差异仍未整改，不迁历史或改宿主时钟。

| 方法 | 实际合同 / 错误 |
| --- | --- |
| `await owner.read(flow.id, db_number, byte_offset) -> Sample` | `.value:int`, quality/request identity; ready/queue/IO/deadline/protocol Failure propagates. Runtime passes its existing owner explicitly. |
| `await HttpClient.get(flow.get_url) -> dict` | Existing bounded GET; HTTP status/type/body/schema Failure. |
| `parse_input(incoming, flow, plc) -> Intent or None` | None=idle; strict source/INT/time Failure precedes guards. |
| `await execution.apply(intent) -> str` | Only write route; existing TTL, duplicate, identity_conflict, target_unknown, clock/audit/queue Failure. |
| `await once(http,flow,plc,execution[,owner]) -> str` | Existing health.result may be idle/guard_false/simulated/confirmed; health is not business completion. |


src/field_flow/config.py、src/field_flow/runtime.py显式import/dispatch；app initializer无副作用

## 准备（终端A）

以下交互命令面向本轮验证的 macOS arm64 / zsh；独立复制时将工程路径替换为副本的真实绝对路径。

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-python
FF_PROJECT=$(pwd -P)
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-005-r1-manual-python-XXXXXX)
printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
uv --version
uv python find 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache"
uv sync --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache"
FF_BIN="$FF_PROJECT/.venv/bin/field-flow"
# 每次只选basic01/basic02/basic03之一；无须修改YAML或命令时间。
FF_CASE=basic02
case "$FF_CASE" in
  basic01) FF_CONFIG="$FF_PROJECT/config/loopback.yaml"; FF_INSTANCE=ff-python-demo01 ;;
  basic02|basic03) FF_CONFIG="$FF_PROJECT/config/$FF_CASE.yaml"; FF_INSTANCE="ff-python-$FF_CASE" ;;
esac
mkdir "$FF_RUN_ROOT/dry_run" "$FF_RUN_ROOT/execute"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry_run/state" --instance-id "$FF_INSTANCE"
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute/state" --instance-id "$FF_INSTANCE"
printf 'PROJECT=%s\nRUN_ROOT=%s\nCASE=%s\n' "$FF_PROJECT" "$FF_RUN_ROOT" "$FF_CASE"
```


先确认已有工具；缺工具/解释器则停止，不下载SDK/解释器或安装Agent依赖。独立复制时把cd路径替换为该工程真实绝对路径。构建/sync和两模式init全部在fixture生成命令之前完成。init拒绝覆盖；run不建schema；inspect只读。dry/execute分库，每个新case重新执行准备段得到新根。旧场景恢复不能照此重建库。

终端A、B不共享变量。先在两终端分别执行下面赋值段，按提示粘贴准备段打印的真实绝对路径和case。FF_MODE先为dry_run；该场景全部停止后，两终端改为execute再运行各自后续段；不在一个10秒窗口内串做两模式。

```bash
read 'FF_PROJECT?Paste PROJECT absolute path: '
read 'FF_RUN_ROOT?Paste RUN_ROOT absolute path: '
read 'FF_CASE?Paste CASE (basic01/basic02/basic03): '
FF_MODE=dry_run
FF_SCENE="$FF_RUN_ROOT/$FF_MODE"
FF_CONFIG="$FF_PROJECT/config/$FF_CASE.yaml"
if [ "$FF_CASE" = basic01 ]; then FF_CONFIG="$FF_PROJECT/config/loopback.yaml"; fi
FF_BIN="$FF_PROJECT/.venv/bin/field-flow"
cd "$FF_PROJECT"
```


## 启动、观察、停止

终端B先准备好下一段；终端A启动fixture后立即在B运行（10秒input_max_age不刷新）。端口有占用则停止，不杀占用者/换端口。

Terminal A

```bash
"$FF_PROJECT/.venv/bin/python" -m tests.fixtures --config "$FF_CONFIG" --evidence-dir "$FF_SCENE/fixture" > "$FF_SCENE/fixture.stdout" 2> "$FF_SCENE/fixture.stderr" &
FF_FIXTURE_PID=$!
printf 'fixture PID=%s\n' "$FF_FIXTURE_PID"
read '?After B stops the runtime, press ENTER here: '
kill -INT "$FF_FIXTURE_PID"
wait "$FF_FIXTURE_PID"
FF_FIXTURE_EXIT=$?
printf 'fixture exit=%s\n' "$FF_FIXTURE_EXIT"
```


Python报告fixture_ready；B可读fixture.stdout。只有A持有此$!并负责精确SIGINT/wait，不能在B猜fixturePID。

Terminal B

```bash
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
FF_ARGS=()
if [ "$FF_MODE" = execute ]; then FF_ARGS=(--execute); fi
"$FF_BIN" run --config "$FF_CONFIG" --state-dir "$FF_SCENE/state" "${FF_ARGS[@]}" > "$FF_SCENE/product.jsonl" 2> "$FF_SCENE/product.stderr" &
FF_PID=$!
sleep 6
kill -INT "$FF_PID"
wait "$FF_PID"
FF_RUNTIME_EXIT=$?
printf 'runtime PID=%s exit=%s\n' "$FF_PID" "$FF_RUNTIME_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_SCENE/state"
cat "$FF_SCENE/product.stderr"
```


等待A的fixture exit=0后，仍在持有FF_PID的B执行：

```bash
cat "$FF_SCENE/fixture/report.json"
ps -p "$FF_PID" -o pid=,stat=,command=
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
"$FF_PROJECT/.venv/bin/python" - <<'PYBIND'
import socket
peers = []
try:
    for port in (32102, 32103, 32880):
        peer = socket.socket()
        peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer.bind(("127.0.0.1", port)); peer.listen(1); peers.append(peer)
    print("ports_rebound")
finally:
    for peer in peers: peer.close()
PYBIND
```


正常场景runtime/fixture均exit0；ps精确原PID无输出/exit1（非法PID或权限错误不算释放），lsof无listener，三口实际rebind。产品JSONL含正常join/reap与shutdown_complete；将driver/server的原正整数PID从产品JSONL和fixture报告单独`ps -p PID`确认消失。强杀、forced_driver_stop、超时、fault_cleanup不能当正常通过。上面Python仅做端口资源检查，不冒充产品验证。

计数按准备→产品→停止后核验三个窗口区分。人工fixture只固定value42（Python身份本次生成、Rust cmd-001），没有value/ready/fault参数/控制台。dry_run：simulated1、WriteVar0、16字节全A5；execute：confirmed1、WriteVar1、002a加14字节A5。basic01/basic03六秒内至少10次GET只执行一次；basic02 execute GET1、至少11次ReadVar（一轮触发+十轮skip），dry至少10次独立读/GET。额外独立读回会增加会话/ReadVar，不能混进产品窗口；新harness停止产品后才核验。手工Rust报告含协议而非完整内存，完整16字节读回由下面harness完成。

超龄/非法输入：原错误、零新增写；业务false：无command/写且下一轮继续，错误计数不因普通skip增长。失败时先保存原状态/日志和PID，不改时间/身份/TTL，不重init旧库；只停确切自有进程。

## 有界反向/边界矩阵

```bash
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/matrix" uv run --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache" pytest -q -s tests/test_basic_examples.py
# Single case:
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/basic02-only" uv run --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache" pytest -q -s tests/test_basic_examples.py -k basic02_cli
```


自身[tests/test_basic_examples.py](../tests/test_basic_examples.py)使用正式CLI/正式YAML，Fixture.command/body只在测试内生成一次身份/时间。新FF005_EVIDENCE_ROOT必须不存在或为空；每次运行用新路径。编译/init在生成命令前完成；每场景≤45秒（含回收），单语言矩阵≤600秒。报告为每scene/report.json及init/inspect原输出、product.jsonl/stderr；准备/产品/独立读回窗口分开，保存counts、内存、实际PID/退出、线程/child join与三口rebind。

basic01两模式42/idle；basic02两模式负值/写后42/-1/0、idle、非法、过期、读错误和execute无有效ACK（截断）保留unknown；basic03两模式-1/0/1/42/100/101、idle/非法/过期。读错误与unknown场景保留预期故障退出和原库，不计为正常stop；正常场景必须exit0，无强制回收。unknown只显示事实，不提供修复/重发工具。

## 可修改点和后续能力

可在消费方副本修改业务条件、合成输入值；basic03阈值是源码常量，不是配置参数，修改需重新构建/验证。目标只支持显式标准DB INT，物理target改变须重新评估冲突/授权；不要把case、kind、flow、source、instance、状态目录的改名当恢复。原命令不可变字段/时效和Execution路径不能改来取绿。未知kind/非法target/重叠target仍启动前拒绝。

进阶路线：advanced01同点多流、advanced02多DB/点、advanced03多PLC、advanced04混合协议、advanced05条件POST、advanced06恢复/退出均planned，需要各语言底层能力和独立批准后再交付。Modbus、POST、JSON点位API、C#均不是本案例库当前能力；C#全部planned。teaching01只是[自身USER_GUIDE](../USER_GUIDE.zh-CN.md)里的独立副本练习，不是第四个正式案例。
