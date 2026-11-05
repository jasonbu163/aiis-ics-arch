# Rust 模拟 Runtime

`ds-runtime` 0.1.0 是共用的产品业务库，拥有 UUID 实例管理、通用 DB image、大端 typed 编码、六写来源、CAS、五类确定规则、逐 item 公平、准入预算、停机换版及 DS 配置 SQLite。直接消费冻结 `aiis-tia-import-core` 0.1.0 API，不 fork parser、命名算法或 DAA transport。

默认 `native-s7` 自动构建有限 native 适配层；桌面也显式选择此 feature。构造时按合法 selected 版本初始化值并保持 stopped，保存不应用、不启动。SQL 和网络 IO 不持 image owner 锁；stop 封准入和 generation 变化不等待 apply 的 SQL 事务。selected 已提交但安装失败报告 `load_failed`，旧 image 只作诊断、禁止服务。

[产品构建](../BUILD.zh-CN.md) · [验证](../tests/README.zh-CN.md) · [批准范围](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)

`test-automation` 非默认。required-feature 测试宿主共用同一 App/服务/owner，只加入固定 owned manifest 命令、有界屏障/overlay 和逐 store 一次性事务故障点，不创建第二 image 或产品 IPC。历史 G0 文件在条件退役前保持未注册，不是正常构建入口。

草稿/版本增量：configuration_draft保持单行CAS；仅显式publish插入configuration_revisions，由永受保护的latest保持版本号高水位。versions服务串行化引用变更及加载预览/提交，检查全部selected、实际loaded、pending apply和previous；目录区分使用保护与仅作回退保留。单个/批量删除预览最多100版本，绑定全部引用及selection CAS；仅作回退保留时须额外明确确认全部实例释放。Store在同一事务重新核对持久引用、以selection CAS清除准确的previous标记并删除全部清单，失败整体回滚；不改当前selected/已加载image。重复加载相同selected版本保留原previous，真正换版才更新。最近5份以外的无引用版本仅经具体清单确认后清理，自动清理不会解除回退保留；启动、保存草稿和升级不清理。v1 schema和legacy UTC字段未改，stop和S7 IO不等待版本锁，未知回执不盲重试。
