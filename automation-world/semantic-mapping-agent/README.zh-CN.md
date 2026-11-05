# AIIS Semantic Mapping Agent

[English](README.md)

来源：DTB TSS a87c107c10e8d9d9d3e389e357b50d203d2aebf7。交付gate归[SMA PLAN](PLAN.zh-CN.md)与[SMA-004 bundle](plans/SMA-004-local-configuration/spec.md)，[AW PLAN](../PLAN.zh-CN.md)管理跨工程依赖。软件检查、独立QA与Human Owner验收是不同事实。

SMA管理本地连接、OpenAPI目录/入选材料、目标API、值规则、映射与最小只读源元数据。事实定义/值生产、Simulation、内置帮助、客户页与legacy SQL IPC继续退役。本阶段只提供配置维护和纯预览。**正常manual、start、resume与auto-start在构造HTTP client、读取远端配置或spawn之前，返回 `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE`**；HTTP开启、旧启动偏好为true也不能放行。pause、stop与status保留。

## 配置与文件

Rust是业务配置唯一写权威。`<SMA profile>/configuration.sqlite3`使用SMA自有bundled rusqlite `=0.32.1`、schema v1和一个完整singleton文档，保存单调revision与真实上海时间updatedAt。每次短事务比较用户观察到的revision、校验合并后全图再提交。过期表单或预览须重新加载/预览。被引用的材料、目标或规则不能删除；使已有映射失效的修改整体拒绝。禁用不会丢弃引用。

profile来自显式绝对`SMA_PROFILE_DIR`，正常采用时可归应用自己的app-data。非法显式override、损坏库或未知schema明确失败，不回落默认目录或删库重建。本任务只授权可丢弃profile验证，真实/默认profile采用或迁移须另行决定。不自动导入旧TSS配置或localStorage连接，也不fallback；环境Backend URL不是已保存配置。

在**连接**显式保存唯一Backend地址；保存本身不发请求。**API材料**先显示本地目录与选择。导入本地OpenAPI JSON后复核候选操作、显式应用目录，再保存勾选。网络目录刷新须显式操作并通过原HTTP gate；目录改变不自动替换派生目标。目标也可手工维护。`targetApis`、`mappingValueRules`与`mappings`原JSON wrapper、单sheet XLSX模板继续支持，旧目标九列默认POST。preview不写库，apply绑定同内容与revision。重复key、非法引用、公式、宏或超限均整批拒绝。

现有配置工作区提供完整JSON备份与恢复。备份使用`format: aiis.sma.configuration`、`schemaVersion: 1`及完整`document`。恢复先展示整包替换/删除范围并要求显式确认，不倒退本地revision；不包含`.env`、HTTP gate、UI/启动偏好、事实值或运行记录。使用JSON导出，不复制打开的SQLite主文件。输入载荷和实际UTF-8美化JSON备份信封最多10MiB；每类最终集合最多10,000项，连续小保存也不能绕过。

**源事实**仍是显式门禁下的只读HTTP检查器。离线绑定保存`sourceKey + factName`；未知引用可保存为未验证，不编造事实或值。最小源元数据保留证据来源与原定义版本，读取到的值只留当前会话。编辑草稿预览与已保存行预览分开：后者由Rust从当前本地revision读取并复用原纯映射算法，不申请claim或投递。缺少必需事实时返回诊断，不输出完整请求；保存配置不记作目标业务成功。

`runtime-startup.json`仍是独立schema v1，不进入业务revision。加载不改字节，显式保存保留惰性旧段；新profile默认false。该偏好在本阶段不能授权投递。发现非终态runtime时所有业务配置写入均拒绝，须显式stop并确认终止。旧HTTP/lease/审计算法仅作为显式兼容fixture入口保留回归；应用没有旧执行模式开关。

## 开发与UI

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

普通启动仍为`pnpm tauri dev`，identity为`com.aiis.aw.semanticmappingagent`，dev/preview strictPort为15192/14192。可丢弃运行验证前固定任务自有绝对`SMA_ENV_FILE`/`SMA_PROFILE_DIR`、空`SMA_BACKEND_BASE_URL`与`SMA_HTTP_ENABLED=false`。profile只隔离Rust文件，**不隔离WKWebView存储**；原生测试须用受支持临时incognito overlay，不能据此证明native跨OS进程UI偏好持久化。

SMA以自身依赖编译CU公共`src/ui/index.ts`与`src/ui/styles/index.css`，构建应用不需要CU进程或CU node_modules。五组七叶ID保持。主题/语言与Element Plus主题弹层不重挂业务工作区。UI偏好继续归`sma.*` localStorage，排除业务备份。普通表复用稳定字段ID列宽拖拽、记忆与每表重置；操作/选择等特殊列可固定。日历显示按上海时间到秒，底层精度保留，缺失/无时区时间显示缺失状态。

可配置GET源、本地投递运行器、历史/outbox、可靠恢复、DAA/Backend全链及真实操作仍归后续精确批准阶段。[详细设计](../../docs/AIIS_SMA_Detailed_Design.md)不是这些阶段已交付的证据。
