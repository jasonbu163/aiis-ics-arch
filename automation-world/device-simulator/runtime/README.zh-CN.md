# Rust 模拟 Runtime

`ds-runtime` 0.1.0 是共用的产品业务库，拥有 UUID 实例管理、通用 DB image、大端 typed 编码、六写来源、CAS、五类确定规则、逐 item 公平、准入预算、停机换版及 DS 配置 SQLite。直接消费冻结 `aiis-tia-import-core` 0.1.0 API，不 fork parser、命名算法或 DAA transport。

默认 `native-s7` 自动构建有限 native 适配层；桌面也显式选择此 feature。构造时按合法 selected 版本初始化值并保持 stopped，保存不应用、不启动。SQL 和网络 IO 不持 image owner 锁；stop 封准入和 generation 变化不等待 apply 的 SQL 事务。selected 已提交但安装失败报告 `load_failed`，旧 image 只作诊断、禁止服务。

[产品构建](../BUILD.zh-CN.md) · [验证](../tests/README.zh-CN.md) · [批准范围](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)

`test-automation` 非默认。required-feature 测试宿主共用同一 App/服务/owner，只加入固定 owned manifest 命令、有界屏障/overlay 和逐 store 一次性事务故障点，不创建第二 image 或产品 IPC。历史 G0 文件在条件退役前保持未注册，不是正常构建入口。
