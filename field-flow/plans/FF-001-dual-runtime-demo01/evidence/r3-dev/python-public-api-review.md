# FF-001 r3 Python公开路径有限预检（Development）

批准spec SHA256 `cf2ff0ff8e8d7bf1bc2302127f5f5bc7a32d767be470ddf9875cf3ced59efbb1`。Rust正式树全套和独立副本全部通过后，才创建本Python工程与自身环境/夹具。此文是Development实际失败证据，不是独立QA。

## 实际命令与结果

依赖/环境：本工程 `uv lock --python 3.11 --no-python-downloads`、`uv sync --locked --python 3.11 --no-python-downloads` 均exit0；使用已有CPython3.11.12，Python项目自身`.venv`，锁定python-snap7=3.0.0/httpx0.28.1/PyYAML6.0.3/pytest8.4.2，不安装全局解释器、不借Rust服务/源码或旧probe虚拟环境。uv安装hatchling只属于已批准本工程build backend。

从 `field-flow/field-flow-python/`：

```bash
UV_CACHE_DIR=/private/tmp/ff-001-r1-r3dev-k989azay/uv-cache uv run --locked --python 3.11 --no-python-downloads python -m tests.python_api_preflight --evidence-dir /private/tmp/ff-001-r1-r3dev-k989azay/python-api-preflight-3
```

实际exit1；客户端API调用0.147ms，fixture整轮约121.278ms。`Client.db_write(1,0,bytearray(002A))`返回0，`get_last_error()`=0。代理只把匹配ACK的TPKT绝对byte19（function）从05改04：

- 请求：`0300002502f080320100000002000e00060501120a1002000200018400000000040010002a`
- 原Server正响应：`0300001602f0803203000000020002000100000501ff`
- 实际发送响应：`0300001602f0803203000000020002000100000401ff`

三者PDU reference均`0002`；global error=0000、item count=1、item status=FF均未改。只有WriteVar正响应变为ReadVar功能码。actualWriteVar1、Server注册内存 `002a`+14个`a5`。完整三份hex、ref、function、版本/路径/hash和实际返回都在 [python-api-preflight.json](python-api-preflight.json) 与 [原样输出](python-api-preflight-3.txt)。

本项没有Python业务runtime/SQLite/T3；不能伪称Python已提交confirmed。失败结论是原公开DB write API无法拒绝错误操作ACK，与r3 AC15公共语义冲突。主程序若只沿其成功返回，无法证明“本次WriteVar的正ACK”；不能通过总deadline/IPC request_id补充该校验。

## 自然回收

断言在报告落盘及收尾完成后才执行。自身client PID32027与Server PID32026均自然exit0，parent真实join，Server剩余线程[]、proxy thread真实join，32102/32103实际rebind成功。全6个批准端口后续lsof exit1且零listener输出。没有终止端口占用者、换端口或连接真实目标。

原两轮输出 [python-api-preflight.txt](python-api-preflight.txt)、[python-api-preflight-2.txt](python-api-preflight-2.txt)保留：夹具错误地将正常COTP disconnect DR无数据ACK的EOF当异常，未到最终合同断言；修正夹具只对DR的EOF作正常结束后得到上述完整结果。中间一次辅助修正使用了错误cwd相对路径，FileNotFoundError/exit1，未修改实现；随后正确路径修正。它们不是已通过的协议证据，也不是第三方设备失败。Server在disconnect时仍输出“Expected COTP DT, got 0x80”，但实际自然exit0/无剩余线程，不能将该终端信息隐藏或说成已修改第三方。

## 只读API核查与边界

已锁3.0.0本工程site-packages原文件未修改：

- `Client.db_write`（client.py约250）调用write_area并返回0；write_area单个2byte请求经`_send_receive`后只交`protocol.check_write_response`。
- `_send_receive`（约117）只发送一次，有限receive检查PDU ref；当前错function的ref正确，因此返回。
- `S7Protocol.check_write_response`（s7protocol.py约1484）检查error_code和data return_code，不比较parameters.function_code；调用者只得到0，不得到原始response。
- 公开`Client.iso_exchange_buffer(data: bytearray)->bytearray`（client.py约1396）存在，可读原S7 payload。这里只读核查，没有调用，没有新增Python codec、私有协商、monkeypatch、运行代理或候选替换。r3 R14明确Python保持原公开DB路径；任何raw适配责任须PM下一Revision决定。

候选client.py SHA256=`0d4ca7c3f178fe3484b8282b61635c14d2edf1ef925b1761e2f5b2865251c2ff`；精确其他源码hash/方法签名补入source-review.json。组件3.0.0为纯Python重写（其METADATA说明），不是使用Rust/native桥接；本例Server也是同包Python Server，不宣称native C++资格。包METADATA声明MIT，原声明未改。

当前停止继续实现，交协调器/PM具体范围处理。Rust已通过的DEV成果、Pythonpartial工程及全部失败证据保留。没有developer_handoff完成、fresh Verification或Owner最终验收。
