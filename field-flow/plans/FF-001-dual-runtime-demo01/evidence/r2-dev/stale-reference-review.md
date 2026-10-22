# FF-001 r2 有限 S7 reference 复核（Development）

2026-10-21，正式交付树 `field-flow/field-flow-rust`。这是 Development 真实失败证据，不是 Verification verdict。批准 spec SHA256 保持 `1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`。

## 命令和结果

```bash
CARGO_TARGET_DIR=/private/tmp/ff-001-r1-20261021-r2dev/rust-target cargo test --locked --offline --features test-fixture --test local_protocol --manifest-path field-flow/field-flow-rust/Cargo.toml stale_reference_probe -- --test-threads=1 --nocapture
```

实际 exit101，完整 stdout/stderr 在 `rust-stale-reference-probe.log`；协议与状态摘要在 `stale-reference-evidence.json`，SQLite 只读导出在 `stale-reference-state-export.json`，父持久日志在 `stale-reference-runtime.jsonl`。未提交 SQLite 或其他可写状态文件。

仅同项目 `127.0.0.1:31102/31103/31880` 合成夹具；保持一个 runtime driver/session，先真实 ReadVar，后 HTTP GET→真实 WriteVar，然后自然停止 runtime，再单独建立真实读回连接。代理只改正响应中 TPKT 绝对索引12，即 S7 header 的 PDU reference 第二字节；未改功能码、长度、global error、item status或数据。原始请求/原始服务端响应/实际发给client的响应全部保留hex，可复查没有改错字段。

| 项 | 请求reference | 原服务端响应reference | 实发响应reference | 实际父结果 |
| --- | --- | --- | --- | --- |
| ReadVar | `0100` | `0100` | `0101` | good sample `-23131`，driver返回成功 |
| WriteVar | `0200` | `0200` | `0201` | driver返回成功，业务iteration `Ok`，T3提交 `confirmed=1` |

WriteVar实际计数1、native正ACK计数1；独立读回 `002aa5a5a5a5a5a5a5a5a5a5a5a5a5a5`，相邻A5不变。该写确已应用42，失败不是“未写入”或“重复下发”，而是**未匹配请求reference的ACK被确认成功**。IPC request_id/generation正确不能补充缺失的S7 PDU关联证明。

本probe故意最后断言r2 T3合同，因此自然清理完成后才exit101：driver PID11963自然关闭且PID消失；fixture native server自然exit0、parent真实wait；代理/HTTP线程join；31102/31103/31880均实际rebind成功。额外 `lsof -nP ... -sTCP:LISTEN` exit1、零输出，未杀任何端口占用者或换端口。

## 已读候选源码 / 公开API

已锁 `rust-snap7=1.142.2`，本机registry缓存只读：

- `native/s7_micro_client.cpp`，`opWriteArea` 为每请求设置 `PDUH_out->Sequence=GetNextWord()`；返回路径在 `isoExchangeBuffer` 成功后检查全局 `Answer->Error` 与 item `0xFF`，这一入口未比较请求/响应Sequence。
- `native/s7_isotcp.cpp`，`isoExchangeBuffer` 是底层ISO发送/接收，不为此DB write路径增加S7关联校验。
- `src/client.rs` 的公开 `db_write/db_read` 返回 `Result`，不返回原始response PDU/ref；`set_as_callback`提供operation/result，不提供原始ACK。另有公开 `iso_exchange_buffer`（约line1654）接收自建S7 PDU；这里只读确认其存在，未使用、未构造协议guard或新低层适配器。

当前 r2 adapter 不能据 `db_write` 的 `Ok` 证明 r2 R08/T3 的“匹配请求正S7 write ACK”。使用低层PDU API自建请求/校验会改变当前高层driver实现边界，应由PM明确处理；Development没有为了通过测试换库、改第三方、添加协议代理/guard或放宽合同。

## 局部成功和未执行项

`rust-matrix-10.log` 中原有普通矩阵1项通过，advanced矩阵在stale用例失败停止。其 split / slow 真实响应场景分别约4617ms，由父整体deadline触发TERM并实际reap旧driver，PID消失；这些局部实证说明r2新增进程边界工作，但不抵消本ACK关联失败。

父/子崩溃专项 `tests/process_lifecycle.rs` 只写入并编译，尚未运行；队列stop/T1/T2/T3/审计/容量完整矩阵尚未执行完成。Python未创建。没有完整AC01–AC14 self-check、developer_handoff完成、独立QA或Owner最终验收。
