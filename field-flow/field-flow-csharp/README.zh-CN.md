# Field Flow C#

[English](README.md)

本独立 .NET 控制台工程是 FF-003 r2 的开发候选。一台 S7 PLC 对应一个 JSON 文件，`demo01` 执行 HTTP GET → SQLite → S7 DB INT16 流。每台 PLC 由一个 owner 维护长期会话和有界队列，多条流独立推进。

默认运行模式只读取目标点位。显式 `--execute` 使用独立状态目录。重复命令复用已记录状态，不确定的写入保留为 `unknown`。

[BUILD.zh-CN.md](BUILD.zh-CN.md)说明锁定 SDK、隔离依赖、示例配置和运行命令。目标为 Windows 10 Enterprise LTSC 2021 x64，macOS 检查仅为开发证据。Windows 原生验证和独立 QA 状态见上级 FF-003 任务。
