# 产品验证

[获批 r5 spec](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) 定义全部阈值和精确来源/依赖闭集。[tasks](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) 区分实际 DEV、独立 Verification 与最终接受。测试使用自有合成 profile，不操作 DAA 应用数据库或真实 PLC。

在 DS 目录使用正式 Python 3.9 stdlib 入口，显式提供根路径与角色：

```sh
/usr/bin/python3 -B scripts/run_validation.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev --suite all
/usr/bin/python3 -B scripts/build_native.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev
/usr/bin/python3 -B scripts/run_protocol.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev --case W01
```

fresh 独立角色使用 `qa` 及自己的 stage/cache/build/tmp/profile/runs；只复制冻结原包内容到独立 cache，不复用 DEV target，也不要求 QA 的 Mach-O SHA 与 DEV 相同。不隐式安装、更新包或采用其它依赖。参数缺失时只显示帮助、不启动。协议 listener 前以本角色 closed B0 核来源、固定输入与实际产物；B0 过期或固定端口占用均拒绝运行。

`all` 依次运行普通 `pnpm tauri dev`、Rust/core/SQLite 合同与真实双进程 profile 锁、产品/test release 构建、新 B0、固定原生 N1–N3，之后通用 K07 拓扑及原协议矩阵。W01–W09 各三份独立 profile/reset，每次 W03 均包含 100 轮 BOOL 竞争；C01 保持原 16 会话完成 C02，C03–C06 保留原时长、频率和资源阈值。D01 消费冻结真实 ManagedS7 模块；X01 三次、单进程适配条件下 X02 不适用。失败立即停止聚合序列，后项不推定成功。

非默认原生 driver 仅使用固定 DOM 事件、File/DataTransfer 和正常 16 命令 IPC；有界 report 命令只记录断言，不是任意 eval/SQL/raw 控制入口。N1 通过真实表单保存配置；N2 重开 selected/stopped 并验证真实 S7、typed 写入、stale 快照恢复及选择隔离；N3 验证运行值不持久化、单连接关闭、dirty Cancel/Discard。全部使用 `Window.close` 和正常保存/丢弃/取消流程。TERM/KILL 只收尾失败实验，绝不当正常生命周期证据，不要求用户反复手动关窗。

[夹具](fixtures/README.zh-CN.md) 区分原 DB41/57 回归 bytes、通用产品拓扑及共享 v1 命名/布局 oracle。Rust 测试执行真实消费者服务、独立 typed bytes、单 owner 拒写、保值、真实 SQLite 事务和非默认逐 store 一次性故障点。故障注入明确标识，不冒充断电安全或物理磁盘耗尽。原生资源区分主进程、已观察子进程、client 与 observer；未知 OS 服务归属不按零费用处理。

原命令、stdout/stderr、file events、wire、images、进程/资源、SQLite 副本及 status 先保存角色 T5 run，再逐成员复制持久 A5 并二次核 SHA/bytes。公开 P5 只放五个紧凑 manifest/index，不放 raw DB、日志或二进制。`collect_evidence.py` 封存新 run；`verify_evidence.py` 只读核显式 archive 或同角色 B0，不写 P5。`retire_g0.py` 先生成逐文件计划、核持久原件，仅当前完整产品验证通过后逐文件退役，不删归属未知的 build/profile/系统数据。

原生资源归属结合实际POSIX children、精确owned WebKit store与当前WKWebView固定只读PID getter，仅非默认测试构建包含该probe。macOS Private SPI经运行时守卫，不是稳定产品API；不支持或无法归属的费用保持unknown。逐PID样本、终止时不可用样本及共享XPC生命周期分列，不杀系统服务。
