# Field Flow Python

[English](README.md)

FF-001 r4独立手写Python运行时，自有typed配置、HTTP、每PLC FIFO owner与持久S7 driver子进程、SQLite执行状态、JSONL审计、CLI和本语言合成夹具。不依赖兄弟源码/可执行文件/服务/环境/可写状态。精确DEV证据与后续QA gate归[唯一任务](../plans/FF-001-dual-runtime-demo01/tasks.md)，独立Verification与Human Owner验收仍是后续阶段。

使用已有CPython3.11（首平台3.11.12/macOS arm64）、uv、自身uv.lock/.venv；不下载解释器或全局安装：

```bash
uv lock --check --python 3.11 --no-python-downloads
uv sync --locked --python 3.11 --no-python-downloads
uv build --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads field-flow
uv run --locked --python 3.11 --no-python-downloads field-flow --lang zh-CN --help
```

无参/help只读取自身locale，不建库/日志、不连接。run必须显式配置和状态路径，默认dry-run。`state init --synthetic`只对不存在的新目录显式建schema1，不覆盖；普通run不执行DDL，schema/implementation/mode/instance不匹配拒绝，inspect只读。

本机合成例子先只创建一次新父目录，其他终端使用同一个实际路径：

```bash
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-001-r1-python-XXXXXX)
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry" --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute" --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures --config config/loopback.yaml --evidence-dir "$FF_RUN_ROOT/fixture"
```

夹具固定绑定127.0.0.1:32102透明S7代理、32103自身Python Server、32880合成GET。占用就失败，不杀占用者/自动换端口。源生成一个新固定身份和值42，原时间不刷新，超过input_max_age便stale。在另一终端按对应已初始化目录选一个模式：

```bash
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir "$FF_RUN_ROOT/dry"
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir "$FF_RUN_ROOT/execute" --execute
```

依次运行，用SIGINT/SIGTERM正常停止每个进程。dry只记录simulated；execute每source/command身份最多一次写。`field-flow state inspect --state-dir PATH`只读查看。完整自动CLI init/fixture/start/stop命令为`uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures.cli_smoke`。

demo01每轮只GET一次，严格typed/时间校验后调用执行服务。独立flow不自身重叠、不积压历史tick；HTTP等待不占PLC队列。同一PLC用一个driver PID/session串行IO；测试读流各自有sample/request身份。每5秒JSONL健康区分flow/owner/队列/状态计数/日志/容量，无health监听器。

子进程保留python-snap7=3.0.0公开connect，每job仅一次公开iso_exchange_buffer。有限codec只生成单item/2byte DB INT，完整核对本请求ref/function/status/length后才typed成功。每新Client Setup用1，raw自有2..65535，不复用，耗尽正常退役且不重放。4096是库接收返回后的cap；原单帧payload上界65528，可能有临时拷贝。raw body不进父IPC/产品日志，首坏响应退役旧会话，不能为等正确ACK重发。

父是唯一SQLite/审计writer，持久T1/T2/T3、原来源身份及unknown物理重叠阻断。匹配S7正ACK且T3提交才confirmed，不代表工艺/物理完成。可能已发送后的错误为unknown，重启/新ID/别名/回读均不重发/升级；没有清空/重发/unknown处置CLI。

connect/IO整体预算含IPC和实际故障reap，400ms回收预留在原预算内。driver继承实例锁份额；父死亡后500ms内实际故障结束child。stop先关闭所有start gate，未开始请求取消；flow/owner/HTTP/SQLite/审计共用一个global shutdown截止。自然exit0与forced/unknown/audit故障exit1分开，参数/配置/状态错误exit2。强制结束不撤销已应用写。

容量：最多10000身份；event>=90000、主库>=48MiB、磁盘<256MiB时暂停新副作用，主库硬64MiB/含journal128MiB。不淘汰身份/事件。JSONL行<=4096byte，文件<=5MiB、4备份、总25MiB；必要审计flush/sync或stdout失败即闭新写闸门，独立读可继续。已confirmed不因后续sink失败倒退。

夹具经公开Server.register_area注册自有IntMemory bytearray，16byte DB1只接纳完整2byte slice。原未修改Server对越界写可能先部分赋值再返回错误，真实失败原证据保留。这个合成内存边界不修复第三方、不证明真实PLC写保护/块大小；runtime只另行校验配置声明范围。原高层API失败模块tests.python_api_preflight保留，显式执行仍失败，不能当生产IO或通过测试。

自身验证入口：

```bash
uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_matched_ack_gate.py
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py
```

gate复用正式state/owner/driver/execution，内110秒、DEV外层120秒含实际资源回收。完整测试在全新/private/tmp/ff-001-r1-r4-python-*保留三报文/次数/内存/三表/PID/join/rebind，关键报告由tasks持久化。复制整个本目录（排除.venv/dist/cache/state/log）后独立sync/build/start/tests；可复用正常package cache，不能借兄弟环境。

现场、真实endpoint/操作、长稳、托管、部署、三平台安装包、物理exactly-once均未覆盖。[PLAN](PLAN.zh-CN.md)、[代码索引](CODE_INDEX.md)、[组件声明](THIRD_PARTY_NOTICES.zh-CN.md)。
