# Field Flow Rust — 使用与案例开发手册

[English](USER_GUIDE.md)

Rust 是后续长期部署 runtime 的主要建设方向。FF-001 r4 已实现本地 demo01 闭环并通过独立 QA2，Human Owner 最终验收仍待定。本手册不授予现场、托管、容量、长稳或生产资格；未来生产 flow 不要求双语言同步实现，保留既有 Python 功能、测试与历史证据。

## 1. 独立工程与准备

复制整个本工程，排除 target、.venv、dist、缓存、状态目录、gate/lock 运行文件和日志；保留 Cargo.lock 依赖锁。仅使用自身源码、配置、locale、夹具，不依赖父级或兄弟进程、可执行文件或环境。README 的父任务链接仅是可选治理导航。

```text
src/main.rs → commands.rs → runtime.rs
src/app/demo01.rs → services/execution.rs
src/domain.rs, config.rs; infrastructure/{http,state,audit,s7_int_pdu,posix}.rs
src/driver_process.rs; src/bin/ff-fixture.rs, src/fixture.rs
Cargo.toml, Cargo.lock, config/loopback.yaml, locales/, tests/
```
以下命令使用当前仓库路径；独立副本先改为副本的真实绝对工程路径。准备阶段终端 A 始终位于工程根。缺工具属于前置条件失败，不自动安装解释器、target 或系统工具链。

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust
FF_PROJECT=$(pwd -P)
FF_LESSON=$(mktemp -d /private/tmp/ff-002-r1-rust-XXXXXX)
printf "%s\n" "$FF_PROJECT" "$FF_LESSON"
rustc -Vv
cargo -V
clang++ --version
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_LESSON/target-product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_LESSON/target-fixture"
FF_BIN="$FF_LESSON/target-product/release/field-flow"
mkdir "$FF_LESSON/empty" "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
(cd "$FF_LESSON/empty" && "$FF_BIN" && "$FF_BIN" --lang en-US --help && "$FF_BIN" --lang zh-CN --help)
ls -A "$FF_LESSON/empty"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-rust-demo01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-rust-demo01
```
空 cwd 应保持空，帮助退出 0，不读配置、不连网络、不建状态。依赖、构建及两个显式初始化均先于夹具。init 创建全新子目录并拒绝已有目录；父目录必须存在。普通 run 不建 schema。

本工程 [BUILD](BUILD.zh-CN.md)说明 native 依赖与平台 gate。

## 2. 夹具实际启动什么

| 组件 | 地址 / 职责 |
| --- | --- |
| HTTP | `127.0.0.1:31880/demo01/command` — 一条合成 GET 命令 |
| S7 proxy | `127.0.0.1:31102` — 透明帧转发、计数/trace、测试内部故障注入 |
| S7 server | `127.0.0.1:31103` — 注册 16 字节 DB1 内存的真实 S7 服务 |

夹具父进程拥有 HTTP/proxy 线程并用自身 executable 启动 native server 子进程。runtime 是独立进程，每 PLC owner 启动一个常驻 driver 子进程/session。proxy 前后两段 TCP 不代表两个业务 PLC client。此有限协议夹具不是 Device Simulator（DS）产品，无需 DS、Backend、Docker 或另一语言。

Rust CLI 没有 fixture_ready 行：核对进程持续存活且三个 listener 属于本演练。固定 source=demo01-feed、cmd-001、value=42。命令时间仅生成一次（expires=issued+60000 ms），重复 GET 不刷新。默认 input_max_age_ms=10000，故夹具启动后只有 10 秒启动 runtime，尽管 expiry 为 60 秒。先准备好终端 B 命令，再启动终端 A 夹具。超过 10 秒后出现 stale 符合语义。

自动测试可在内部改 feed/故障；人工 CLI 没有控制面板、管理 API、持续命令生成、任意点表或交互故障编辑。本手册仅用DB1/16/offset0；native夹具不会按任意配置生成feed/DB。配置可表达的 DB/地址范围不扩大夹具能力。native server夹具不证明真实PLC写保护或现场块大小。

## 3. 两个独立、有界教学场景

每次夹具启动前只读检查三个端口。出现占用就停止演练并报告，不杀占用者、不改端口。lsof 无输出且退出 1 代表无匹配 listener。

```bash
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
```
终端 B：明确读取 A 输出的真实绝对工程与 lesson 路径（逐行粘贴路径，不加引号）。shell 变量不共享。保留本 shell 运行/inspect。

```bash
read -r FF_PROJECT
read -r FF_LESSON
cd "$FF_PROJECT"
FF_BIN="$FF_LESSON/target-product/release/field-flow"
```
### dry-run 教学

A，工程 cwd；报告目录必须尚不存在，启动夹具：

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
```
B，同工程 cwd：立即启动，运行两秒，只向记录的本进程 PID 发送信号并实际 wait。

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/loopback.yaml" --state-dir "$FF_LESSON/dry-lesson/state" > "$FF_LESSON/dry-lesson/stdout.jsonl" 2> "$FF_LESSON/dry-lesson/stderr.txt" &
FF_PID=$!
printf "runtime PID=%s\n" "$FF_PID"
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
FF_EXIT=$?
printf "runtime exit=%s\n" "$FF_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/dry-lesson/state"
```
A：按 ENTER，等前台夹具命令返回，生成 protocol.json。命令返回后立即在A记录自身夹具退出码：

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

切回第3节一直保留的终端B（工程cwd），再执行下面的报告、端口和runtime/driver/server PID检查。FF_PID只在B由本轮$!赋值，A不使用它。先核对下方打印的PID为本轮原PID且是正整数；空值或错误PID须停止，不能当“进程不存在”。有效PID的ps退出1只有在stdout/stderr均为空时才代表未找到；非法参数或权限诊断是检查失败。


```bash
cat "$FF_LESSON/dry-lesson/fixture/protocol.json"
cat "$FF_LESSON/dry-lesson/stderr.txt"
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
预期 inspect 为 simulated=1，fixture writes/applied=0。正常 runtime/fixture 均退出0；端口无 listener、记录的 runtime PID 不存在。还须从 stdout.jsonl 的 driver_ready 取 driver PID（Rust context 是 JSON 字符串），Rust 从 protocol.json 取 native_pid；逐个精确 PID 执行 ps -p 并确认不存在。仅发送 SIGINT 不算释放证据。

### execute 教学

A，工程 cwd；报告目录必须尚不存在，启动夹具：

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
```
B，同工程 cwd：立即启动，运行两秒，只向记录的本进程 PID 发送信号并实际 wait。

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/loopback.yaml" --state-dir "$FF_LESSON/execute-lesson/state" --execute > "$FF_LESSON/execute-lesson/stdout.jsonl" 2> "$FF_LESSON/execute-lesson/stderr.txt" &
FF_PID=$!
printf "runtime PID=%s\n" "$FF_PID"
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
FF_EXIT=$?
printf "runtime exit=%s\n" "$FF_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/execute-lesson/state"
```
A：按 ENTER，等前台夹具命令返回，生成 protocol.json。命令返回后立即在A记录自身夹具退出码：

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

切回第3节一直保留的终端B（工程cwd），再执行下面的报告、端口和runtime/driver/server PID检查。FF_PID只在B由本轮$!赋值，A不使用它。先核对下方打印的PID为本轮原PID且是正整数；空值或错误PID须停止，不能当“进程不存在”。有效PID的ps退出1只有在stdout/stderr均为空时才代表未找到；非法参数或权限诊断是检查失败。


```bash
cat "$FF_LESSON/execute-lesson/fixture/protocol.json"
cat "$FF_LESSON/execute-lesson/stderr.txt"
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
预期 inspect 为 confirmed=1，fixture writes/applied=1，DB1 offset0 为 00 2a。正常 runtime/fixture 均退出0；端口无 listener、记录的 runtime PID 不存在。还须从 stdout.jsonl 的 driver_ready 取 driver PID（Rust context 是 JSON 字符串），Rust 从 protocol.json 取 native_pid；逐个精确 PID 执行 ps -p 并确认不存在。仅发送 SIGINT 不算释放证据。

仅全新的 synthetic 教学创建新目录，这不是故障恢复。原 execute 场景重启必须保留原 state/config/instance/source/command 身份；不重做 init、不删库、不重启夹具刷新 cmd-001、不改时间或换 ID 绕过去重/unknown。stale 不产生新写；相同身份/内容抑制重复，immutable 内容改变则 identity_conflict。新教学不得用来掩盖旧场景结果。

## 4. 配置与输入合同

config/loopback.yaml 是完整可跑样例。对象为 Config → Plc[]、Flow[] → Target、Http；拒绝未知/缺失字段及字符串/布尔到整数的隐式转换。ID 为 ASCII 字母数字/_/-，1–64 字符。flow.id 标识流程，kind 选择明确 app 派发，business_name 表达规则，source_id 必须匹配 feed；含义不同。

| 字段 | 允许值 / 关系 |
| --- | --- |
| `schema_version / instance_id` | 1 / valid_id；须匹配状态 |
| `plcs / flows` | 1–4 / 1–8；ID 唯一、PLC host:port 唯一 |
| `plc.host / port / rack / slot` | IPv4 字面量 / 1–65535 / 0–7 / 0–31 |
| `connect_timeout_ms / io_timeout_ms` | PLC：500–3000 / 500–5000 |
| `queue_capacity / queue_wait_ms / ready_wait_ms` | 1–16 / 100–5000 / 100–5000 |
| `flow.kind / interval_ms / input_max_age_ms` | 教程接线前仅 demo01 / 100–10000 / 1–60000 |
| `get_url` | http(s)、host，无凭据/fragment；不走环境代理/重定向/业务重试 |
| `target.plc_id / db_number` | 已存在 PLC / 1–65535 |
| `db_size_bytes / byte_offset / type` | 2–65536 / 0–65534 / INT；offset+2 ≤ size |
| `target overlap` | 相同物理 host/port/rack/slot/DB 的两字节重叠拒绝 |
| `http.connect_timeout_ms / pool_wait_ms` | 各 100–1500，均 ≤ total_timeout_ms |
| `http.total_timeout_ms / max_connections / max_body_bytes` | 100–5000 / 1–8 / 1–4096 |
| `shutdown_timeout_ms` | 5000–20000 且 ≥ max(HTTP total, 每 PLC connect/IO)+5500 |
| `config bytes` | ≤65536；相对路径按命令 cwd 解析 |

标准非优化 DB INT 为两字节大端有符号整数，范围 -32768…32767。DB 号、声明大小、offset 是显式配置，DB1 不是现场合同，也不证明真实 PLC 块大小。尚未实现 BOOL/DINT/REAL、优化 DB 符号访问、POST、鉴权或 demo02。

```json
{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"example-001","value":42,"issued_at_ms":1792742400000,"expires_at_ms":1792742460000}
```
JSON 是故意使用历史时间的形状示例，不能当实时命令投递。必须恰好七键、JSON Content-Type、HTTP200。ready=false 时 command_id/value/issued_at_ms/expires_at_ms 全为 null；ready=true 要求合法 command_id、严格 INT 整数及 signed64 Unix 毫秒。要求 0<expires−issued≤60000、issued≤now+1000、now<expires、now−issued≤input_max_age_ms。原 wall/monotonic 锚点拒绝超过1000ms漂移，排队/出队/driver开始均不重置；不为测试改宿主时钟。

## 5. 一轮执行、状态与生命周期

一轮 await GET → 校验 → idle返回 → 接纳intent并 await Execution.apply。外层循环归 runtime：完成后等待 interval_ms，同流不重叠、不追赶历史 tick。不同流为并发异步任务；runtime 复用一个 HTTP client，HTTP/interval 等待不占 PLC FIFO。每 PLC owner 复用一个 child/session，仅串行自身 IO。每次读产生独立 request/sample身份，不提供共享快照或业务互斥。见本工程tests/local_protocol.rs（三独立读/慢GET）和tests/runtime_regressions.rs。这些测试直接使用服务，人工CLI仍只接受已注册kind。

Ready等待、FIFO容量/排队等待与真正dispatch后的connect/IO是不同预算；connect/IO总期限包括IPC及实际故障reap，400ms回收预留在原预算内，不额外延长来源期限。过期/时钟/闭闸在排队、出队和实际开始处再次检查。T2=in_flight只表示已持久派发许可，不等于native调用已开始；owner health的in_flight基于真实started事件。连接失败按250/500/1000/2000ms及每轮10秒冷却有界退避，不重放unknown写；独立flow/HTTP仍可推进。

T1 持久 source/command、不可变 payload/config/物理 target，进入 pending（dry_run 为 simulated）。T2 在获准外部调用前持久 dispatch_count=1 与 in_flight。T3 仅在匹配 typed S7 ACK 后持久 confirmed；这不代表机器/工艺完成。可能发送后无法证明 ACK 则 unknown；重启把遗留 in_flight 恢复 unknown。expired/canceled 是保护阶段的失败分类，不撤销已应用的写。unknown 按物理重叠阻写，不因别名/新身份/回读解除。没有 unknown处置、重发、清库CLI，须保留原状态/日志并停 writer 审查。

每状态目录含 state.sqlite（schema1 的 store_meta/commands/command_events）、instance.lock、临时 gate-*、runtime.jsonl 与 .1… .4。SQLite 是本地执行事实，非 Backend 业务库。state inspect 只读输出 meta/counts；health 是 JSONL，非监听 API。CLI 相对路径按cwd解析，教程使用输出的绝对路径。Rust/Python 可写库及 dry_run/execute 库不可共享互换。writer交接先停旧端、核对pending/unknown与confirmed进度；本地继承锁/开始闸门不提供跨主机fencing。

容量：10000命令身份；event达90000、主库≥48MiB或磁盘<256MiB暂停接纳新副作用；主库硬64MiB、含journal128MiB；不自动淘汰身份/事件。JSONL单行≤4096字节、文件≤5MiB、4备份，总25MiB。必要审计持久化/flush/sync/stdout失败即闭新写闸门；confirmed不因后续sink失败倒退。通过stderr/health/state识别identity_conflict、target_unknown、clock_invalid、audit_unhealthy/audit_*、capacity_paused；停止并保留证据，不通过加限额或清历史恢复。

常用事件key：`process_start, driver_spawn, driver_ready, driver_call_started, intent, in_flight, ack, health, flow_health, stop_gate_closed, driver_process_reaped, runtime_tasks_joined, resources_released, shutdown_complete`. 部分状态事件使用更具体名称，以实际JSONL为准。

正常SIGINT/SIGTERM先关闭全部start gate，取消排队/未开始工作，保守分类在途结果，在一个shutdown预算内join flow/owner、关HTTP、wait/reap child与state/audit线程。强杀、forced_driver_stop、fault_cleanup、shutdown_incomplete不算正常成功。不按进程名/端口杀进程。退出0为正常；Rust CLI/config/state前缀错误退出2，其余runtime错误1。Python参数/配置/状态启动失败通常退出2，close故障/unknown退出1（shutdown_incomplete为1）；不是所有Python运行失败都映射1，须读实际key与日志。

当前时间限制：来源issued/expires及sampled/health *_ms为Unix毫秒，耗时/期限用monotonic，不给epoch机械加八小时。现SQLite日历元数据使用UTC Z的strftime，Python JSONL显式UTC+00:00，Rust tracing时间为UTC；与根Asia/Shanghai日历存储合同不同。FF-002只如实记录，不迁schema/历史/日志；实现与数据兼容整改另需批准。

## 6. app 可用方法与内部边界

以下是源码级合同，不是已版本化公共SDK。Result<T>为Result<T,String>，异步方法须await并以?传播错误key。

| 路径 / owner | 实际签名 | 用法 / 返回 / 错误 |
| --- | --- | --- |
| `src/app/demo01.rs` | `iteration(f:&Flow,p:&Plc,http:&Http,owner:&Owner,state:&State,stop:&Stop,clock:&mut Clock) -> Result<()>` | async；一轮GET/校验/apply，runtime拥有参数与clock |
| `src/infrastructure/http.rs (re-export services::Http)` | `Http::new(&config::Http)->Result<Http>; get(&self,url:&str)->Result<Input>` | new同步装配、clone复用client；get异步；http_config/http_pool_timeout/http_communication/http_status/input_content_type/input_body_size/input_schema/http_timeout |
| `src/domain.rs` | `Input::intent(self,&Flow,&Plc)->Result<Option<Intent>>` | 同步；None为idle、Some为intent；input_schema/input_stale |
| `src/domain.rs` | `Intent::validate_time(&self,now:i64)->Result<()>; deadline(&self)->std::time::Instant` | 同步；校验原issued/expiry；input_stale |
| `src/domain.rs` | `Clock::default(); check(&mut self,wall:i64)->Result<()>` | 同步；每流原锚点；clock_invalid |
| `src/services/execution.rs` | `Execution { owner:&Owner,state:&State,stop:&Stop }.apply(Intent,&mut Clock)->Result<()>` | 异步；app唯一写路径；duplicate/simulated可无IO返回Ok；target_unknown/identity_conflict/clock_invalid/capacity_paused及IO/审计失败 |
| `src/runtime.rs` | `Owner::read(&self,flow:&str,db:u16,offset:u32)->Result<Sample>; health(&self)->OwnerHealth` | read异步独立请求，health同步快照；plc_unavailable/queue_timeout/expired/canceled/driver或s7_*错误 |
| `src/config.rs` | `Config::load(p:&Path)->Result<Config>; validate(&self)->Result<()>` | 同步装配；Flow/Plc/Target/Http字段见第4节；config_read/config_size/config_schema/config_* |
| `src/domain.rs` | `Clock::anchor(&self)->ClockAnchor; ClockAnchor::check(&self,wall:i64)->Result<()>` | 同步；原wall/monotonic锚点clone供内部IPC，clock_invalid；app用Clock::check，不重置锚点掩盖漂移 |
| `src/runtime.rs` | `Stop::close(&self)->Result<()>; wait(&self); stopped:Arc<AtomicBool>` | close同步、wait异步；runtime拥有闭闸生命周期，app可检查stopped.load(Ordering::Acquire)；gate_*错误；不每轮创建/关闭gate |
| `src/infrastructure/state.rs` | `inspect(dir:&Path)->Result<Value>; State::snapshot(&self)->Result<Value>` | inspect同步CLI只读meta/counts；snapshot异步内部health {commands,log_writable,capacity}；state_io/state_schema/state_deadline；state线程拥有 |
| `src/infrastructure/state.rs` | `State::log(&self,event:&str,c:serde_json::Value)->Result<()>` | 异步内部观察经state/audit actor，例如state.log("observation",json!({"result":"ok"})).await?；传播audit_*/state_*；不代替状态迁移 |

Rust Sample含request_id/flow_id/generation/pid/value:i16/quality/sampled_at_ms及可选write_ack。读Sample的write_ack为None；写ACK证明归Execution。


有界app一轮内的读示例（使用独立flow请求标签）：

```rust
let sample = owner.read("teaching-read", f.target.db_number, f.target.byte_offset).await?;
let value: i16 = sample.value;
```
这不新增已注册读flow。quality=good是sampled_at_ms时刻的有效协议样本，不是物理完成。

仅装配/生命周期使用：Config::load/validate、Runtime::start/launch_flows/health/shutdown、State::open/finalize与StateTask::join。State.admit/dispatch/finish与Owner.write归Execution内部，不绕过持久执行。Driver.spawn/call/close、raw iso_exchange、S7 codec、gate/lock、SQL和夹具变更hook属于内部/测试面。不存在POST/auth、BOOL/REAL或自动发现案例公共方法。第7节完整demo同能力代码展示最短合法写路径。

## 7. 新增同能力 teaching01 案例

仅在新的独立教程源码副本操作，不作为事故恢复或未批准的正式runtime修改。teaching01刻意复用GET→INT，不是demo02/上升沿/POST。放文件或改YAML不会注册kind。先完成并停止第3节，保留旧状态。新副本使用自身环境/target，不导入兄弟工程。

终端A仍有第1节FF_PROJECT。复制公开教学源码到新目录（不复制状态/环境/target），随后只编辑副本：

```bash
FF_TUTORIAL=$(mktemp -d /private/tmp/ff-002-r1-teaching-rust-XXXXXX)
python3 - "$FF_PROJECT" "$FF_TUTORIAL/project" <<'PY'
from pathlib import Path
import shutil, sys
shutil.copytree(Path(sys.argv[1]), Path(sys.argv[2]),
    ignore=shutil.ignore_patterns("target*", ".venv", "dist", "__pycache__", ".pytest_cache", "*.pyc", "runtime.jsonl*", "state.sqlite*", "instance.lock", "gate-*"))
PY
FF_PROJECT="$FF_TUTORIAL/project"
FF_LESSON="$FF_TUTORIAL/run"
mkdir "$FF_LESSON"
cd "$FF_PROJECT"
printf "%s\n" "$FF_PROJECT" "$FF_LESSON"
```

创建完整文件 `src/app/teaching01.rs`:

```rust
//! 文件：src/app/teaching01.rs；教学案例：手写单轮GET→typed条件→执行服务，无循环、SQL或协议IO。
use crate::{
    config::{Flow, Plc},
    domain::{now_ms, Clock},
    infrastructure::state::State,
    runtime::{Owner, Stop},
    services::{execution::Execution, Http},
    Result,
};
pub async fn iteration(
    f: &Flow,
    p: &Plc,
    http: &Http,
    owner: &Owner,
    state: &State,
    stop: &Stop,
    clock: &mut Clock,
) -> Result<()> {
    clock.check(now_ms())?;
    let input = http.get(&f.get_url).await?;
    if let Some(intent) = input.intent(f, p)? {
        Execution { owner, state, stop }
            .apply(intent, clock)
            .await?;
    }
    Ok(())
}
```
逐文件接线。src/app/mod.rs声明模块，config.rs放行新kind，runtime.rs明确派发。下列文本编辑脚本含精确匹配断言；基线改变则停止，不猜测替换。工程根使用已有辅助Python执行（仅改文本）：

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("src/app/mod.rs")
s = p.read_text()
assert "pub mod teaching01;" not in s
p.write_text(s + "\npub mod teaching01;\n")
p = Path("src/config.rs")
s = p.read_text()
old = 'f.kind != "demo01"'
assert s.count(old) == 1
p.write_text(s.replace(old, '!matches!(f.kind.as_str(), "demo01" | "teaching01")'))
p = Path("src/runtime.rs")
s = p.read_text()
old = 'crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await'
new = 'match f.kind.as_str() { "demo01" => crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await, "teaching01" => crate::app::teaching01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await, _ => Err("config_flow".into()) }'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
PY
```
在副本创建 config/teaching01.yaml，完整内容：

```yaml
# FF-001 synthetic loopback；不是现场目标授权。
schema_version: 1
instance_id: ff-rust-teaching01
plcs:
  - id: plc_demo
    host: 127.0.0.1
    port: 31102
    rack: 0
    slot: 1
    connect_timeout_ms: 3000
    io_timeout_ms: 5000
    queue_capacity: 16
    queue_wait_ms: 2000
    ready_wait_ms: 3000
flows:
  - id: teaching01
    kind: teaching01
    business_name: teaching_command_to_int
    interval_ms: 500
    source_id: demo01-feed
    get_url: http://127.0.0.1:31880/demo01/command
    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
    input_max_age_ms: 10000
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```
flow ID/business/instance已改变；source demo01-feed与DB1/16/offset0因人工夹具固定而保留。只运行这一条flow，不与demo01同时写重叠target；配置重叠校验会拒绝误合并配置。没有新增locale key或CLI文案，因此locales/en-US.json与zh-CN.json均无需修改。消费方教程副本应将teaching01加入CODE_INDEX.md并从README链接本地说明，不宣称正式源码已有案例。

```bash
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_LESSON/target-product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_LESSON/target-fixture"
```
下面在新副本完成完整两模式教学。FF_PROJECT/FF_LESSON已经指向上面打印的新路径，不再回原仓库cd。先初始化，再逐模式启动夹具，不同时跑两个夹具。

```bash
FF_BIN="$FF_LESSON/target-product/release/field-flow"
mkdir "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-rust-teaching01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-rust-teaching01
```

终端B重新执行第3节read -r两行，粘贴新工程与新lesson真实路径，cd并重设FF_BIN。先按第3节lsof检查端口无占用。

**dry — A**

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
```
B立即执行（仍须在原10秒input age内）：

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/teaching01.yaml" --state-dir "$FF_LESSON/dry-lesson/state" > "$FF_LESSON/dry-lesson/stdout.jsonl" 2> "$FF_LESSON/dry-lesson/stderr.txt" &
FF_PID=$!
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
printf "runtime exit=%s\n" "$?"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/dry-lesson/state"
```
A按ENTER关闭夹具，返回后立即按第3节在A记录FF_FIXTURE_EXIT；再切回保留本轮FF_PID的B核对报告、有效精确PID和端口释放，完成后才进下一模式。A不使用B的FF_PID。

**execute — A**

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
```
B立即执行（仍须在原10秒input age内）：

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/teaching01.yaml" --state-dir "$FF_LESSON/execute-lesson/state" --execute > "$FF_LESSON/execute-lesson/stdout.jsonl" 2> "$FF_LESSON/execute-lesson/stderr.txt" &
FF_PID=$!
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
printf "runtime exit=%s\n" "$?"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/execute-lesson/state"
```
A按ENTER关闭夹具，返回后立即按第3节在A记录FF_FIXTURE_EXIT；再切回保留本轮FF_PID的B核对报告、有效精确PID和端口释放，完成后才进下一模式。A不使用B的FF_PID。

预期dry为simulated1/write0、execute为confirmed1/write1，inspect meta.instance_id=ff-rust-teaching01。夹具load与产品启动均校验kind，Rust仅编译不能验证YAML。保留旧状态，不需要schema/driver/API变化。

## 8. 核对与限制

FF-002有限演练使用独立macOS arm64副本、真实产品CLI、各自新synthetic dry/execute场景和已接线教程案例；真实证据与失败归FF-002 tasks。fresh Verification给出自身verdict前仅为DEV自检。不宣称重跑FF-001全部故障矩阵、真实endpoint/PLC、DS联调、生产托管、跨平台移植、长稳或分发合规。后续资源回收前先保留报告/PID/退出码/端口证据。

本地导航：[README](README.zh-CN.md)、[CODE_INDEX](CODE_INDEX.md)、[组件声明](THIRD_PARTY_NOTICES.zh-CN.md)。
