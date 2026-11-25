Task ID: SMA-001
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Fresh-context Verification 按 rework-2 的精确工作树复验 SMA-001 r3
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Spec SHA-256: 7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34
Base HEAD: 7f654acd951171767bc253ea5bebdcda6435b608
Worktree: `/Users/jason/Desktop/DreamCode/aiis-ics-arch`

# SMA-001 r3 开发记录

## 范围与分工

按 2026-11-24 获批 [SMA-001 r3](spec.md) §5 实现。采集、映射、并发和配置交换共同交付。

- Development `/root/sma001_r3_dev` 负责 Rust 配置合同和 SQLite、HTTP 取值与组包、预览确认、Tauri 装配、实现说明、源码整合与自检。
- 同一 Development 阶段的 `/root` 实作调度组件及隔离 HTTP／SQLite、浏览器夹具。
- Development 支持 `/root/sma001_r3_ui` 负责 CU 页面、表格、交互、IPC 调用和中英文文案。
- Development 支持 `/root/sma001_r3_exchange` 负责配置管理、JSON／XLSX 读写、依赖和脱敏及浏览器侧回归。

## 实际变更

以下路径相对于 `automation-world/semantic-mapping-agent/`，根代码索引除外。

| 面 | 文件 | 行为 |
| --- | --- | --- |
| 运行入口 | `src-tauri/src/app.rs`、`commands/http_mapping.rs` 与同层模块注册 | 连接新 HTTP IPC。以原 `SMA_HTTP_ENABLED` 控制显式网络测试、确认和启动。打开应用、配置保存和纯预览不发网络请求。退出时停止两侧入队并收口已准入 HTTP。 |
| 配置与快照 | `src-tauri/src/contracts/{http_mapping,local_configuration}.rs`、`domain/local_configuration/{mod,merge,secret_fields,transform,validation}.rs`、`infrastructure/config_store/mod.rs`、`services/local_configuration/mod.rs` | 原配置 singleton 和 CAS 仍使用 schema v1。新增字段是可选项，首次成功采集时创建独立 `http_source_latest` 表。一次 SQLite 读事务固定配置和引用源的快照；提交失败保留原快照。按稳定 ID 合并并校验完整引用图。识别出的凭据不得由原生完整备份导出或随便携配置合并。 |
| 取值与组包 | `src-tauri/src/domain/http_mapping/{mod,evaluate}.rs`、`domain/mapping_runtime/mod.rs`、`infrastructure/http_mapping.rs`、`services/http_mapping.rs` | 通过 JSON Pointer 与数组稳定 ID 取值，保留来源版本、质量、上游时间和样本 ID。周期和手工测试共用组包。逐参数校验类型、快照年龄和可选合法值，删除无效可选正文／查询参数。预览的目标与正文冻结，来源版本和配置 revision 变化会拒绝旧令牌。POST 响应按 HTTP 和配置的业务条件判定，未知请求不重试。 |
| 调度 | `src-tauri/src/services/http_scheduler.rs` | GET 与 POST 独立启停、全局/单目标并发、队列、饱和和停止计数。实际 HTTP 并发在传输边界计数。 |
| 八页与配置文件 | `src/App.vue`、`src/main.ts`、`src/app/http-mapping/`、`src/app/configuration-management/`、`src/app/twin-facts/{api/localConfiguration.ts,types.ts,utils/mappingConfigurationFiles.ts}`、`src/locales/index.ts` | 接回当前 CU 壳层。连接、配置管理、映射执行、事实来源、事实点位、目标 API 配置、值规则和映射配置可独立进入。配置管理集中处理 JSON、结构化 XLSX、旧整包与旧单集合文件。端到端合并绑定本地预览 revision 和一次确认。 |
| 回归与说明 | `src-tauri/src/services/{http_mapping/{acceptance_tests,fixture}.rs,http_scheduler/tests.rs}`、`services/local_configuration/mod.rs` 中隔离交换测试、`tests/{configuration-exchange.test.mjs,http-mapping.test.mjs,http-forwarding.browser.cjs}`、两份 SMA README 和两份 `src/app/README`、仓库根 `CODE_INDEX.md` | 记录独立的来源/目标合同、隔离规模测量、配置兼容、浏览器交互及真实 dev Owner 操作。 |

保留已有 DIRECT 变更中的采集写回撤出状态，以及工作树中的其他项目改动。旧本地映射配置可读取，配置 `maxAgeMs` 并补齐 HTTP 来源后可加入新周期运行。旧启动偏好继续按原格式读取，每次启动都需要显式启用对应运行侧。

## DEV self-check

在 macOS 15.7.7 arm64、Node.js 22.19.0、pnpm 11.11.0、Rust／Cargo 1.89.0 上执行。

| 命令与环境 | 退出码及结果 |
| --- | --- |
| `pnpm --config.verify-deps-before-run=ignore check`、同参数 `test`、同参数 `build` | 均为 0。使用无 `.env` 的临时字节一致副本，复制新版源码、前端与 Rust 测试所需源码及 CU 公共 UI，复用仓库锁文件对应的已安装依赖。28 个前端测试全通过，生产构建完成。Rollup 提示依赖中两处 PURE 注解位置和约 984 kB 的 minified JS chunk。副本与交付源码的 `diff -qr` 返回 0。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo check --offline --locked --manifest-path src-tauri/Cargo.toml` | 均为 0。正式源码工作树，依赖保持锁定。 |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1 --nocapture` | 0。专属临时环境文件和 profile，原生 HTTP 夹具只绑定 `127.0.0.1:0`。19 个库测试与 34 个集成测试通过。原有真实环境只读 `dev_get_only` 用例按声明条件跳过。 |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib measured_full_profile_with_128_gets_and_384_mappings -- --nocapture --test-threads=1` | 0。单独捕获 stderr 的规模测量见下表。 |
| `node /private/tmp/sma001-browser-dev.s24mglqy/run.mjs` | 0。Chromium 新上下文、临时本机 Vite 端口、`envFile:false`、模拟 Tauri IPC 和 OpenAPI。浏览器回调为 `tests/http-forwarding.browser.cjs`，可与等价的 Playwright 驱动重跑。 |
| `git diff --check`、相对 Markdown 文件／锚点检查、规格 SHA-256 和源码内容指纹检查 | 0。16 个相关相对链接、批准规格的固定摘要、162 个候选文件的聚合摘要均已核对。 |

第一轮曾直接在源码目录运行 `pnpm build`，Vite 当时使用默认环境文件查找。正式构建证据来自之后的隔离副本。隔离脚本初次因 pnpm 依赖目录检查中止，第二次发现副本缺少 Rust 静态扫描输入及 CU 的 SSR 依赖解析入口。补齐临时输入并仅在隔离命令上关闭依赖目录重检后，三个命令全部通过。真实环境或用户 profile 文件均未修改。

| 规格检查 | Development 观测 |
| --- | --- |
| AC01、AC15 | Chromium 到达八个页面，通过手工与 OpenAPI 建立 GET／POST 定义，检查 GET 选点、列宽记忆、浅色/深色下 1440×900 与 1024×768 页面及编辑和预览弹窗、中英文、键盘、遮罩关闭、滚动与 JSON 导入预览。浏览器证据使用模拟 IPC。原生运行路径由 Rust 测试和 Tauri IPC 编译核对。本轮未执行实际 WKWebView 应用退出自动化或桌面打包。 |
| AC02、AC03、AC05、AC06 | HTTP／SQLite 夹具测三路来源与固定值、普通任务号字段、必传/省略、规则和空值语义。并行采集和上报看到至少八个版本的字段配对保持同一提交版本。Rust 验证新版本和新 revision 拒绝旧预览、并发确认只消费一个令牌。目标夹具收到与冻结正文一致的请求。 |
| AC04、AC07、AC08、AC10 | 历史原时间、无响应/坏响应、超时及 SQLite 人工失败后保留已提交快照。分别启动并停止采集和上报，已准入传输收口，继续运行一侧能前进。HTTP 失败、业务拒绝、超时、断连及无效回执分开记录。计数核对未知请求未自动重发，下一周期持有新执行 ID。 |
| AC09 | 本机 128 个 GET 配置与 384 条映射，两个 POST 目标。完成率、实际峰值和饱和计数见下表。 |
| AC11、AC12 | 测试实际 JSON／XLSX 字节，检查依赖闭包、0／false 与路径类型、文件格式和逐行定位。Rust 隔离配置库验证合并维护稳定 ID、逐项分类、旧 revision 拒绝、重复 ID 无写入和重开。原有 v1 配置、JSON 备份/恢复及单集合文件回归通过，脱敏文件排除运行态与凭据。 |
| AC13 | 炉温夹具 H1、H2 为两份有不同值和点位原时间的历史详情。任务号分别绑定 H1/H2 所在来源 A、独立来源 B 和固定测试号。实际 POST 与预览一致，混用来源时保留各自版本。空缺、bad 质量、错误类型都阻断本次必填任务号，未回退。 |
| AC14 | 保留 Human Owner 的真实 dev 手工证据。详见下文。 |

规模用例在 4.447 秒的观察窗运行。GET／POST 全局上限为 6／7，单 POST 目标上限为 3，GET／POST 等待上限为 12／18。正常目标模拟约 18 ms，慢目标约 115 ms。

| 观测项 | GET | POST |
| --- | ---: | ---: |
| 观察窗内调度完成率（次／秒） | 41.60 | 39.12 |
| 夹具累计完成（含量测前预热） | 190 | 177 |
| 夹具峰值在途 HTTP | 6 | 6 |
| 队列峰值 | 12 | 18 |
| 队列饱和计数 | 2,265 | 3,522 |
| 重叠周期跳过计数 | 212 | 165 |
| 失败／阻断／超时／未知计数 | 0 | 0 |

正常和慢 POST 目标峰值各为 3。正常目标完成 114 次，其中后半段继续完成 48 次，慢目标完成 63 次。停采后上报继续产生请求。两项完成率使用观测窗口内调度完成数之差计算，夹具累计计数采用 HTTP 服务器自己的传输观察口径。

## 已知限制与 Owner dev 事项

- `collectedAt` 对应 SMA 本次成功 HTTP 采集的时间。上游 `observedAt` 与 sample ID 原样携带。不同来源的当前值可以组成同一 POST，各自保留版本和时间。
- 人工预览令牌在 120 秒内有效，配置或引用快照更换会要求重新预览。频繁采集时可先停采，在仍满足快照有效期的窗口预览与确认。
- HTTP 2xx 无业务回执条件时只记录 HTTP 成功。配置了回执时按 JSON Pointer 的标量匹配判定业务结果。未知请求不会在后续周期或重启补发。
- 隔离负载仅用于本机本次测量。真实 dev 的 AC14 由 Human Owner 按 [§8](spec.md#8-整体验收标准) 核对专用测试任务、接口和字段后，在 SMA 界面确认一次 POST，复核回执、`planSync`、炉温和 `lastObservedAt`。Development 没有读取或写入真实业务目标。

## Developer handoff

精确候选为 SMA-001 r3，主源码工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `7f654acd951171767bc253ea5bebdcda6435b608`。任务未创建 commit。按源码和构建输入的 162 路相对路径生成 SHA-256 清单后，该清单的 SHA-256 为 `f59b0333447381e9cdcfaaf85e84afa8093684bcd95148de50aa1c91ff20610e`。源码此前已包含的 DIRECT 变更一并纳入候选字节。批准规格摘要为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。

在仓库根复算候选摘要。

```python
from hashlib import sha256
from pathlib import Path

root = Path.cwd()
base = root / "automation-world/semantic-mapping-agent"
folders = ("src", "src-tauri/src", "src-tauri/tests", "tests")
paths = [p for folder in folders for p in (base / folder).rglob("*") if p.is_file()]
paths += [base / p for p in (
    "README.md", "README.zh-CN.md", "index.html", "package.json", "pnpm-lock.yaml",
    "pnpm-workspace.yaml", "tsconfig.json", "vite.config.ts", "src-tauri/Cargo.toml",
    "src-tauri/Cargo.lock", "src-tauri/build.rs", "src-tauri/tauri.conf.json",
    "src-tauri/capabilities/default.json",
)]
paths.append(root / "CODE_INDEX.md")
manifest = "".join(
    f"{sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n"
    for p in sorted(paths)
)
print(len(paths), sha256(manifest.encode()).hexdigest())
```

交 fresh-context Verification 以同一候选核查已批准的 AC01–AC15、实现面、差异和运行证据，并保留 AC14 的实际 Owner 条件。

### 临时资源收尾

- 已清理临时前端源码副本、临时构建与输出日志、隔离 Rust env／profile／SQLite 测试文件，以及独立早期调度试验目录 `/private/tmp/sma001-scheduler-dev.vys2cgav`。HTTP 夹具随测试进程结束。项目已有的忽略构建目录用于工具链缓存。
- 保留 `/private/tmp/sma001-browser-dev.s24mglqy/` 的浏览器执行器及缓存供 fresh-context Verification 复测。结束后由协调器移除，源码中的浏览器回调和本交接记录提供持久复测依据。

## Rework-1 Developer handoff

2026-11-24 上海时间，Development `/root/sma001_r3_dev` 接回 SMA-001 r3 的 AC12 修正。初次候选摘要为 `f59b0333447381e9cdcfaaf85e84afa8093684bcd95148de50aa1c91ff20610e`。独立验证记录了正常目录预览和应用后，完整 JSON 备份仍带有敏感 header 参数的 OpenAPI 直接示例；初次 Development 自检漏掉该形态。[独立复现及结论](checklist.md#使候选失败的复验)

- `src-tauri/src/domain/local_configuration/secret_fields.rs` 将敏感参数或命名字段的上下文传入其内部 schema，并检查请求／响应示例正文的已知敏感字段。完整备份在发现示例或默认值的字面量时返回已有的 `SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog`，不生成备份文本。字段声明、无值的命名示例与引用按 OpenAPI 结构检查，不当作凭据字面量。
- `src-tauri/src/services/local_configuration/mod.rs` 增加两项原生回归。测试经目录预览和确认应用后调用完整备份，覆盖敏感 header／query 直接示例、标量或嵌套 schema 默认值、嵌套 schema examples、具名示例值、响应示例中的敏感字段，以及正常参数示例、仅声明的敏感参数及无内联值的引用。拒绝导出后原配置可按 v1 重开，正常备份可显式恢复并重开。便携交换沿用原接口和处理路径。

本轮候选仍在主源码工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `7f654acd951171767bc253ea5bebdcda6435b608`。用上文算法复算 162 项聚合 SHA-256 为 `841efda57355abc6efb23eefdb6d498ccf74ce395192e4ce2a47b5694c14fc9e`。批准规格 SHA-256 仍为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。此项修正未创建 commit。

| DEV self-check | 结果 |
| --- | --- |
| 修复前 `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib catalog_sensitive_parameter_literals_block_complete_archive` | 101。敏感 header 直接示例场景未返回拒绝，复现缺陷。 |
| 修复后 `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib http_exchange_tests` | 0。4 项配置交换回归全过。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo check --offline --locked --manifest-path src-tauri/Cargo.toml` | 均为 0。 |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1` | 0。21 个库测试、34 个集成测试通过。原真实环境只读用例按声明 ignored。使用临时环境文件、独立 SQLite profile 和本机回环夹具。 |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md`、精确候选摘要、文档相对链接 | 均为 0。 |

交 fresh-context Verification 按新摘要复验 AC12 的原合成反例和配置往返。识别仍以敏感名称、示例结构和已支持的凭据格式为依据。本轮前端、桌面驱动和负载性能无新增 Development 观测，AC14 继续等待 Human Owner 操作。

临时资源已清理本轮测试环境文件、SQLite profile 和日志。协调器保留上一轮的 `/private/tmp/sma001-browser-dev.s24mglqy/` 与 `/private/tmp/sma001-native-proof.bvkifyyz/` 驱动供独立复验，复验后由协调器清理。

## Rework-2 Developer handoff

2026-11-24 上海时间，Development `/root/sma001_r3_dev` 在原批准范围内接回 AC12。上一候选摘要为 `841efda57355abc6efb23eefdb6d498ccf74ce395192e4ce2a47b5694c14fc9e`。QA2 确认首轮修正覆盖直接示例，也发现四种敏感 `enum`／`const` 字面量与一个含凭据查询的服务器 URL 仍随完整备份导出。[QA2 复现](checklist.md#qa2--rework-1-独立复验)

- `src-tauri/src/domain/local_configuration/secret_fields.rs` 将 `enum` 和 `const` 纳入现有字面量检查，沿用敏感参数与 schema 属性上下文，并检查字面量内的敏感字段。OpenAPI 的服务器、引用、外部示例、操作链接、文档和安全方案 URL 等字段复用现有 userinfo 和查询凭据判定。相对引用使用本地占位基准解析，检查过程没有 URL 请求。完整备份发现凭据仍使用原 `SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog` 错误，目录与旧库读取保持原数据，便携交换保持原路径和文件合同。
- `src-tauri/src/services/local_configuration/mod.rs` 通过目录 preview/apply 和实际 export 验证 QA2 的五类反例。相关回归另外覆盖嵌套对象常量、协议相对 URL 的 userinfo、编码后的查询参数名、外部例值和操作引用、OAuth URL、文档 URL 的编码凭据及 discriminator 引用。校验保留非敏感枚举和常量、URL 模板和普通相对引用、凭据声明与正常 v1 导出／恢复。首轮示例与便携交换相关回归一并运行。

精确候选位于工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `7f654acd951171767bc253ea5bebdcda6435b608`。按本任务原算法复算，162 项候选聚合 SHA-256 为 `fb8865a0478fb358fd0405595eac84eb75952e29a0b5bf42e80029bdae8cb974`。批准规格的 SHA-256 仍为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。本轮未创建 commit。

| DEV self-check | 结果 |
| --- | --- |
| 修复前 `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib catalog_credential_schema_literals_and_urls_block_complete_archive` | 101，敏感 header 枚举未被拒绝，复现缺陷。 |
| 修复后 `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib http_exchange_tests` | 0。5 个配置交换用例通过。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo check --offline --locked --manifest-path src-tauri/Cargo.toml` | 均为 0。 |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1` | 0。22 个库测试、34 个集成测试通过。原真实环境只读用例按声明 ignored。使用专属临时环境文件、SQLite 和本机回环夹具。 |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md`、相对文档链接、候选和批准规格摘要 | 均为 0。 |

交 fresh-context Verification 对新摘要复验 AC12。检测依据为命名、OpenAPI 字面量位置、URL userinfo/查询和已有凭据格式。该范围不涉及重新定义文件协议或业务运行。真实 dev 的 AC14 仍由 Human Owner 操作。本轮未重新执行前端或桌面驱动。

本轮临时环境文件、SQLite 和日志已回收。由协调器保留的 `/private/tmp/sma001-browser-dev.s24mglqy/`、`/private/tmp/sma001-native-proof.bvkifyyz/` 继续供独立复验，复验后由协调器清理。
