# AIIS Semantic Mapping Agent

[English](README.md)

SMA 配置 HTTP GET 事实来源，并把各来源的最新值映射到 HTTP POST 目标。工作台分别控制采集和上报。交付范围与验收见 [SMA-001 r3 规格](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md)、[SMA 计划](PLAN.zh-CN.md)和 [Automation World 计划](../PLAN.zh-CN.md)。

## 配置与运行

1. 在「连接」保存可选的后台基础地址，查阅 OpenAPI 目录，或直接手填来源与目标地址。保存配置和打开应用均不发送请求。需要显式测试 HTTP 或启动运行时，在所选环境配置中启用 `SMA_HTTP_ENABLED=true`。
2. 在「事实来源」保存 GET 地址、采集间隔与超时，时间以毫秒配置。「测试 GET」展示原始响应与选点结果，不发布最新快照。响应和点位取值使用 JSON Pointer。点位在数组中时，先按稳定 ID 选中该项，再从该项读取值、质量、原点时间和样本 ID。以历史详情为例，合同包含相应字段时可配置响应根 `/data`、数组 `/points`、身份 `/pointId`、值 `/value`。用部署环境的 OpenAPI 和采集选项核实 PLC、DB 与样本详情。
3. 在「目标 API 配置」定义 POST 的路径、查询、请求头和 JSON 正文参数。完整 URL 优先于保存的连接地址与相对路径。仅在目标合同明确时配置业务回执条件，例如 JSON Pointer `/code` 等于数值 `200`。运行结果分别显示 HTTP 成功与配置条件判定的业务接受。
4. 需要合法值检查时创建「值规则」。在「映射配置」逐参数绑定来源点位或固定值，配置执行间隔和快照有效期。`taskNo` 等业务字段与其他参数使用同一套绑定。必填项失败阻断该次上报，可选项失败从请求中省略，包括正文模板和 URL 模板中的对应值。
5. 在「映射执行」启动采集，在「事实点位」查看已提交的最新值和最近读取错误。映射准备好后另行启动上报。执行页显示每侧在途 HTTP、队列、上限、峰值、错误及每目标 POST 并发。停止某侧会清理该侧队列，已进入 HTTP 的请求在超时边界内收口。手工测试时先核对已冻结的请求和来源版本，再确认一次。配置 revision 或引用快照变化时需重新预览。若需要预览期间保持同一输入，可先停止采集，在最新快照有效期内预览并确认。

每个来源的整组点值与采集时间在一次 SQLite 事务中发布。GET 失败或 SQLite 提交失败时保留上次已提交快照。`collectedAt` 是 SMA 成功采集该响应的时间，`observedAt`、质量和 sample ID 沿用上游点位语义。跨来源组包保留各自版本和时间。POST 断连后若远端可能已经提交，界面标记为未知，后续周期按独立执行记录。

真实「炉温 → 实绩」由 Human Owner 选择专用测试任务。确认前核对当前环境的 OpenAPI、允许写入的字段、历史详情样本、任务号与同号计划。Human Owner 在界面确认一次后，核对 HTTP 和业务回执、`planSync`，按任务号回读炉温和 `lastObservedAt`。详见[整体验收标准](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md#8-整体验收标准)。

## 本地配置与文件交换

Rust 写入 `<SMA profile>/configuration.sqlite3`。原 schema v1 配置文档保留 revision 与上海时间 `updatedAt`。新增来源与执行上限是 v1 的可选字段。`http_source_latest` 在首次成功采集时创建，运行快照独立写入。重开 profile 后保留上次数据及其原时间。`runtime-startup.json` 仍可读取，每次启动时采集与上报均处于停止状态。

「配置管理」按选择导出版本化 JSON 与 XLSX 配置包，并带出依赖。连接地址由用户选择包含。导入先展示逐项变化，再按预览 revision 显式确认。来源内的点位按 ID 合并。旧完整 v1 JSON 备份、旧单集合 JSON／XLSX 文件均从配置管理入口处理。完整备份发现已知凭据字段时拒绝导出，可改用便携配置包查看凭据排除项，导入后再补填。导出不带运行快照、回执、日志或偏好。本地完整配置和 JSON 备份最多 10 MiB，每类集合最多 10,000 项。

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

源码开发时先核对 SMA 工程内已有的 `.env`，文件不存在时可从 `.env.example` 复制。需要选择工程内开发目录时，可使用以下配置。

```dotenv
SMA_PROFILE_DIR=./.local/dev
```

`.local/dev` 和 `./.local/dev` 均指向所选 `.env` 所在目录下的 `.local/dev`，不随终端当前目录改变。选择已有的绝对 profile 目录时，将下面的示例替换为该目录路径。

```dotenv
SMA_PROFILE_DIR=/absolute/path/to/sma-profile
```

可选的进程 `SMA_ENV_FILE` 须指定绝对、可读的普通文件。进程和文件中的相对 profile 均以该文件的父目录为基准。profile 路径拒绝 `..`、`~`、变量、占位符、已存在的符号链接及非目录路径组件。启动拒绝时按错误中的键和原因核对。此前在终端 export 的非空 `SMA_PROFILE_DIR` 会覆盖文件值。

普通启动仍为 `pnpm tauri dev`，identity 为 `com.aiis.aw.semanticmappingagent`，dev/preview strictPort 为 15192/14192。可丢弃运行验证前固定任务自有 `SMA_ENV_FILE`/`SMA_PROFILE_DIR`、空 `SMA_BACKEND_BASE_URL` 与 `SMA_HTTP_ENABLED=false`。profile 隔离 Rust 文件。WKWebView 存储在应用重开后共享，原生测试使用受支持的临时 incognito overlay。该方式无法验证 native 跨 OS 进程 UI 偏好持久化。

SMA 使用自身依赖编译 CU 公开界面及样式。八个工作区共享 CU 壳层、语言、主题与表格列宽偏好。日历显示采用上海时间并精确到秒，底层时间保留原精度。

profile 路径无效、数据库损坏或 schema 未知时会显示错误。原配置和原启动偏好均保留，旧启动偏好不会自动启动采集或上报。历史逐条投递和按目标安全重试需要独立投递合同。[详细设计](../../docs/AIIS_SMA_Detailed_Design.md)记录早期设计。
