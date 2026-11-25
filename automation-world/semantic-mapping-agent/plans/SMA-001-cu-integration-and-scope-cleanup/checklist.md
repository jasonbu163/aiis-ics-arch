Task ID: SMA-001
Revision: r3
Status: qa_blocked
QA Verdict: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3 隔离验证通过 14 项，AC14 等待 Human Owner 提供真实 dev 手工证据，最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session

# SMA-001 r3 独立验证

2026-11-24 上海时间。在 fresh context 独立复算 spec SHA-256 为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。正式工作树 HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`，按 tasks 的逐文件算法计算 162 项清单摘要为 `f59b0333447381e9cdcfaaf85e84afa8093684bcd95148de50aa1c91ff20610e`。此候选含既有 DIRECT 字节，其他模块同时有在途改动。Git 的当前总差异不能单独证明单次任务的变更归属。原批准范围和 Development 交付记录分别见 [spec.md](spec.md) 与 [tasks.md](tasks.md)。

## 使候选失败的复验

AC12 的完整 JSON 备份会保留 OpenAPI 敏感参数的直接示例。独立 Rust 探针链接当前已编译的项目库，使用新的 SQLite 文件，只使用合成标记。操作顺序如下。

1. 创建 `LocalConfigurationService`，向空库 preview `ChangeIntent {kind:"catalog",resource:"catalog",...}`。合成 `GET /fixture` 的 `operationSnapshot.parameters` 为 `[{"in":"header","name":"X-API-Key","schema":{"type":"string"},"example":"QA_ONLY_DUMMY_LITERAL"}]`。预览成功。
2. 使用预览令牌执行 apply。随后调用配置管理「完整备份」所用的 `export()`。探针检查返回的实际备份文本，输出 `full_backup_contains_synthetic_api_key_example=true`，退出码 0。全程无远端请求。
3. 前端 OpenAPI 归一化会保留参数的 example。Rust 的 `secret_fields.rs` 第 138–164 行检查敏感名称后，将直接 example 的字符串交给只识别对象的检查，随后普通字面量通过。现有通过的备份测试未覆盖该输入。期待显式阻止导出或依合同排除凭据，并覆盖合法的 OpenAPI 参数示例形态。需 Development 提交新候选供独立复验。

## 分项结果

| 项 | 本候选结果 | 本轮验证事实 |
| --- | --- | --- |
| AC01 | 通过 | Chromium 进入八页，分别手填和从 OpenAPI 创建 GET、POST，测试 GET 解析字段。原生 IPC 单 GET 返回 725.5，接收端 POST 计数为零。 |
| AC02 | 通过 | 炉温测试经真实本机 HTTP 采集 A/B/C、固定标量，检查绑定变更后的目标正文和标量类型。 |
| AC03 | 通过 | interleaved_http_generations 测试交错调度，两字段属于同一提交。SQLite 事务读取配置与所选快照，预览携带每路各自版本。 |
| AC04 | 通过 | whole_get_failures 注入无效响应、HTTP 错误、超时及存储失败，核对上次提交和过期阻断；标量、质量和可选省略由 evaluator 与炉温用例联合覆盖。 |
| AC05 | 通过 | Node 和 Rust 用例覆盖值规则、固定与点位绑定、合法值及拒绝；保存和运行时均检查，规则可独立或从点位派生。 |
| AC06 | 通过 | 单次令牌消费、过期版本与配置拒绝由 Rust 测试验证。Chromium 模拟 IPC 下遮罩只取消、键盘确认一次；真实 Tauri IPC 预览与一次确认产生一次 HTTP POST。 |
| AC07 | 通过 | 两侧分别启停，停止侧清队列，另一侧前进。原生夹具启动时两侧均 stopped，延迟请求在关闭后收口，进程正常退出。 |
| AC08 | 通过 | 隔离 Rust 调度／HTTP 用例测限流、饱和、慢目标、超时、错误和另一线路进展，真实峰值见下表。 |
| AC09 | 通过 | 128 路 GET、384 条映射和正常／慢目标独立跑测，后半段正常目标继续完成 53 次。 |
| AC10 | 通过 | receipts_distinguish_business_rejection_transport_unknown_and_next_cycle 测 HTTP 失败、业务拒绝、超时、断连和异常回执；复核目标计数和新周期执行身份。 |
| AC11 | 通过 | 两种真实格式分别对全选和单映射闭包往返；验证字段类型、重复身份、表行定位、错误文件、冲突、revision 变化以及显式合并后重开。 |
| AC12 | **失败** | v1 读取／恢复、单集合文件和选取交换回归通过；完整备份暴露敏感 OpenAPI 参数 example，见前述独立复验。 |
| AC13 | 隔离通过 | furnace_history_and_cross_source_bindings 以 A 的两次历史详情、B 任务号及固定号比较实际 HTTP 正文、温度、observedAt 和快照版本；任务号缺失、bad、错型均阻断。 |
| AC14 | 待 Human Owner 实施 | 专用测试任务、实际 OpenAPI 与启用字段、同号计划、人工确认唯一真实 POST、回执/planSync 及炉温与 lastObservedAt 回读均等待 Owner。 |
| AC15 | 隔离检查通过 | 1440×900 和 1024×768、浅／深四组合，覆盖编辑、预览、规则、导入、键盘、遮罩、正文滚动样式和实拖列宽。不同组合抽查不同弹窗。Chromium 提供交互及几何证据，原生夹具只证明 IPC 和退出。 |

## 环境、命令和量测

macOS 15.7.7 arm64、Node 22.19.0、pnpm 11.11.0、Cargo 1.89.0。QA 使用单独临时 env、profile 和 SQLite。自建 HTTP 夹具使用 127.0.0.1 随机端口，真实环境用例 dev_get_only 按声明 ignored，未查看真实配置或连接实际部署。Development 在 tasks 已披露的首轮默认 Vite 查找环境文件，不能据其后重跑追认那一次的隔离。

| 命令 | 退出码及证据 |
| --- | --- |
| `pnpm --config.verify-deps-before-run=ignore check`、`test`、`build` | 各 0。无 .env 的源码副本、相同锁文件和已安装依赖；28 项前端测试全过，Vite 完成，保留 chunk 体积提示。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` 和 `cargo check --offline --locked --manifest-path src-tauri/Cargo.toml` | 均 0，交付源码。 |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1 --nocapture` | 0，19 个库测试、34 个集成测试通过，1 个真实 dev 测试 ignored。 |
| 上述 Cargo test 使用 `--lib measured_full_profile_with_128_gets_and_384_mappings -- --nocapture --test-threads=1` | 0，单独读取 stderr 的量测见下表。 |
| `node /private/tmp/sma001-browser-dev.s24mglqy/run.mjs` | 0，envFile:false，临时 Chromium profile，执行候选 tests/http-forwarding.browser.cjs，Tauri IPC 为模拟。 |
| `node /private/tmp/sma001-native-proof.bvkifyyz/run.mjs` | 0，QA 独立执行，临时隐藏 incognito Tauri 窗口和夹具权限。实际编译并启动候选原生二进制，源版本 1、配置 revision 1、手工结果 http_succeeded，含后续周期发送，服务器收到 2 次且完成 2 次，在途慢请求收口 701 ms，正常退出。该运行使用测试专属 TAURI_CONFIG。 |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md`、Python 本地文档路径检查 | 0；SMA 双语 README 及 spec/tasks 的 28 处本地目标全部存在。 |

| 4.516 秒观测窗口 | GET | POST |
| --- | ---: | ---: |
| 调度完成率（次／秒） | 38.75 | 38.09 |
| 夹具累计完成／实际峰值在途 | 185 / 6 | 175 / 6 |
| 配置并发上限／等待队列上限 | 6 / 12 | 7 / 18 |
| 队列峰值／饱和计数／跳过计数 | 12 / 2245 / 229 | 18 / 3556 / 165 |
| 失败／阻断／超时／未知 | 均 0 | 均 0 |

分别测得正常目标 114 次、慢目标 61 次，两者的实际峰值均为 3，单目标上限为 3。累计完成含预热，窗口速率使用调度计数增量。

## 交接与资源

AC12 已退 Development。须记录修正后候选摘要、复验原合成反例与配置往返回归。Human Owner 保留 AC14 实操与最终决定。QA 的临时源码、测试日志、凭据探针、隔离 profile 和数据库位于 `/private/tmp/sma001-qa.gtL3Pdu4`，结论持久化后回收；原生夹具自动清除其运行目录。临时浏览器／原生驱动由原创建方保留至后续复验结束后清理。原生夹具使用仓库已有的 ignored Cargo target 缓存；已提醒协调器在最后一次使用后恢复普通 debug 构建。

## QA2 · Rework-1 独立复验

2026-11-24，fresh-context Verification。正式工作树 base HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`。按 tasks 中 Python 算法复算 162 项摘要为 `841efda57355abc6efb23eefdb6d498ccf74ce395192e4ce2a47b5694c14fc9e`，spec SHA-256 为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。**本候选 qa_failed，AC12 退回 Development。** QA1 的原始结果保留于上文。

### AC12 独立证据

用 rustc 链接本候选 Cargo 产出的项目库和 serde_json，逐场景新建 SQLite。每例以配置服务的 catalog preview/apply 持久化一条测试目录记录，再调用完整备份 export，检查返回错误或实际备份文本。以下 `M` 代表普通合成串 `QA2_SYNTHETIC_1124`，各例单独执行。全程没有网络请求。

| operationSnapshot 输入 | 实际结果 |
| --- | --- |
| header 参数 X-API-Key 直接 example=M | 拒绝，SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog，QA1 反例关闭 |
| requestBody 媒体具名示例 value.outer 数组含 access_token=M；响应媒体直接示例 outer 数组含 password=M | 两例分别拒绝，同一错误码 |
| header 参数 X-API-Key 的字符串 schema.enum=[M]；query 参数 access_token 的字符串 schema.const=M | 两例均成功导出，备份逐例包含 M |
| requestBody JSON schema.properties.apiKey.enum=[M]；响应 JSON schema.properties.password.const=M | 两例均成功导出，备份逐例包含 M |
| servers[0].url 为 https://fixture.invalid/base?api_key=M | 成功导出，备份包含 M |
| 普通 batch 整数参数 example=7 | 完整备份成功，另建空库执行 restore 预览、显式确认和重开，document 等于原始值 |

`src/app/connection/api/index.ts` 的目录归一化保留 parameters、requestBody 和 operation 级 servers。响应样例按配置服务可接收的目录快照验证。唯一枚举成员和常量指定实际允许的凭据值；服务器 URL 的 api_key 查询也带有具体值。`secret_fields.rs` 的 operation 检查处理 value/example/default/examples，对 enum/const 的普通字符串及服务器 URL 查询未实施相应检查。需要在可交付候选复验上述输入，同时保留无值声明及普通配置的备份能力。

### 其余验收与环境

macOS arm64，隔离环境文件、SQLite、回环随机端口。沿用上文 AC01–AC11、AC13、AC15 的验收映射，以下为本候选新跑结果。

- `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1 --nocapture` 退出 0。21 个库测试及 34 个集成测试通过，1 个真实环境测试 ignored；覆盖并发快照、绑定与炉温、失效阻断、预览令牌、回执和停止收口。AC09 的 128 GET／384 映射下，GET／POST 每秒完成 36.82／35.94，夹具在途峰值均为 6，队列峰值 12／18，饱和 2195／3553 次。正常／慢目标累计 106／57 次，正常目标后半窗仍完成 50 次，两者峰值均为 3。
- 隔离前端副本以 `pnpm --config.verify-deps-before-run=ignore check`、`test`、`build` 各退出 0，28 项测试通过。初建副本遗漏同级共享 UI 导致类型检查退出 2；补齐共享依赖后测试又指出缺少清理审计所读的 Rust 源码。补齐目录并复跑通过。构建仍提示第三方注释与 chunk 体积。
- 运行 tasks 交接的两个 Node 驱动，各退出 0。Chromium 访问八页并核对桌面／平板、主题、键盘和遮罩。临时测试专用 TAURI_CONFIG 原生实际 IPC：revision=1、latestVersion=1、确认 http_succeeded、接收及完成 POST 均为 2（含周期发送），停止在途收口 702 ms，退出码 0。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --check` 和 `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md` 均退出 0。AC14 由 Human Owner 使用专用 dev 测试任务执行唯一确认、planSync 及 by-task 回读，并另行决定最终验收。

临时资源：QA2 自有目录 `/private/tmp/sma001-qa2.6X4YLyJa` 包含探针、SQLite、隔离前端、副本构建及日志，证据持久化后清理。两份共享驱动由协调器保留至复验完成后回收，已通知协调器恢复普通 ignored 原生 debug 构建。

## QA3 · Rework-2 独立复验

2026-11-24，fresh-context Verification。正式工作树 base HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`，批准规格 SHA-256 为 `7a1f452812a22a4f59ff2c3db347e4156caa85961edd6ceec612d7af66141e34`。测试前后独立执行 tasks 的候选清单算法，两次均为 162 文件、SHA-256 `fb8865a0478fb358fd0405595eac84eb75952e29a0b5bf42e80029bdae8cb974`。核对了备份导出检查、目录转换、前端目录快照和原生配置服务测试。当前源码与交接清单一致。上一候选无独立逐文件清单，因此两轮间逐文件差异以 Development 声明的两个文件为据。

**AC01–AC13、AC15 隔离检查通过，AC14 待 Human Owner，整体验证状态 qa_blocked。** QA1 与 QA2 的 AC12 失败适用于各自历史候选。QA3 已复验两轮已知反例。

| 检查 | 本候选的观测 |
| --- | --- |
| AC12 原生目录与备份 | 在本次 Cargo 进程执行 5 个 `http_exchange_tests`。核对各分支实际创建独立 SQLite，经 catalog preview/apply 后调用 export。敏感 header 直接 example、header enum、query const、请求属性 enum、响应属性 const、服务器 URL 的 api_key 查询均返回 `SMA_CONFIGURATION_EXPORT_CREDENTIALS:catalog`。另覆盖嵌套字面量、外部引用、相对 URL、编码查询名和 OAuth URL。拒绝备份后原配置可重开。 |
| AC11/12 正向配置交换 | 普通枚举、常量、URL、无值凭据声明允许完整导出。测试解析 schemaVersion 1，显式恢复到空库，重开后 document 与原配置相等。便携合并保留稳定 ID、选中点及 revision，含凭据的便携配置被拒绝。前端 JSON/XLSX 测试与旧备份集成回归通过。 |
| Rust 与调度 | 在 macOS arm64，通过专用 SMA_ENV_FILE、SMA_PROFILE_DIR 和回环夹具执行 `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml -- --test-threads=1 --nocapture`，退出 0。22 个库测试、34 个集成测试通过，真实 dev 测试 1 个按声明 ignored。128 GET／384 映射，4.567 秒窗口，GET／POST 每秒完成 34.15／33.06，在途峰值 6／6，队列峰值 12／18，饱和 2233／3566 次，失败、阻断、超时、未知均为 0。正常／慢目标累计 98／54，单目标峰值各 3，正常目标后半窗完成 41 次。 |
| 前端与静态检查 | 独立无环境文件副本，复用已安装锁定依赖及 CU 共享源码。依次运行 `pnpm --config.verify-deps-before-run=ignore check`、同参数 test 和 build，均退出 0，28 项测试通过。构建有 chunk 体积提示。diff -qr 检查前端源码、测试及 Rust 源码与交付工作树均一致。Cargo fmt --check、cargo check --offline --locked、范围 git diff --check 均退出 0。双语 README 及任务三文件的 32 个本地链接目标均存在。 |
| 浏览器与 Tauri | 交接的两个 Node 驱动均实际运行。Chromium 八页、桌面／平板、主题、键盘与遮罩回归退出 0。首次并行启动原生夹具时 5173 端口正由浏览器夹具占用，退出 1。浏览器退出后串行复跑原生夹具成功，隔离 IPC 返回 revision=1、latestVersion=1、http_succeeded，POST 接收与完成各 2（含周期发送），停止收口 701 ms，应用退出 0。 |

**AC14 解除条件**　Human Owner 在真实 dev 核对实际 OpenAPI、启用字段、来源样本及同号计划，在 SMA 界面用专用任务预览并确认一次 POST，记录 HTTP 与业务结果、planSync、按任务号回读的炉温与 lastObservedAt。仅 Human Owner 决定最终验收。本轮未连接真实 dev。

**临时资源**　QA3 自有目录 `/private/tmp/sma001-qa3.6cEDlOhO` 中的日志、隔离前端副本、环境及 profile 在结论持久化后回收。已通知协调器原生夹具退出，可以清理两个共享驱动、恢复普通 ignored debug 构建。

协调器随后确认两个共享驱动目录已回收，清除 TAURI_CONFIG 后运行普通 debug 的 Cargo build 退出 0，并核对产物包含普通端口 15192、无夹具标识。QA3 自有目录已回收。
