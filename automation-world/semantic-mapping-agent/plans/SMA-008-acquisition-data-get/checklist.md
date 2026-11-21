# SMA-008 r3 独立验证

Task ID: SMA-008  
Revision: r3  
Role: Verification（fresh context）  
Verdict: qa_failed  
Handoff: Development

## 候选与结论

2026-11-20，macOS 15.7.7、rustc 1.89.0、pnpm 11.11.0。在交付工作树核对基准 HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。从 tasks.md 提取 31 行交付清单，SHA-256 为 `6900d4ef456c96e4b5014193e1d8c0bda89bdfb910a04b52b936df5d5747f22b`，31 项候选和 3 项只读依赖摘要匹配。共享工作树另有并行修改。核对九个 acquisition 命令的前端名称、参数、Tauri handler 注册、托管服务、返回结构及服务到 HTTP 的调用。浏览器使用模拟 IPC，原生测试直接执行同一 Rust 服务。现有 dev 仅执行 GET。

## 返回 Development 的可复现缺陷

1. **合法 REAL 被整批拒绝。** REAL 值 `340282356779733661637539395458142568447` 等于 binary32 溢出中点减一。以普通 plc-facts/v2 测试正文调用当前 backend 的 `parse_sample` 与 `stored_value`，得到同一原值。用 `rustc --edition=2021 -L dependency=src-tauri/target/debug/deps --extern sma=src-tauri/target/debug/deps/libaiis_semantic_mapping_agent_lib.rlib` 编译临时只读探针，将下列单点解析为 JSON 值并传入实际候选 `sma::domain::acquisition::point_data`。结果为 `Err("SMA_ACQUISITION_RESPONSE_INVALID")`，相同输入换为 0 得到 `Ok(1)`。原因见 `src-tauri/src/domain/acquisition.rs:131`，先转 f64 再转 f32 会将这个合法数舍入到溢出边界。latest 和 detail 在选择、展示前校验整批，含该点的 GET 无法展示或预览。
2. **REAL 负零丢失。** 同一探针把 value 改为 JSON number `-0`。backend 的 `parse_sample` 和 `stored_value` 保留 `-0`，Rust 实际 `point_data(...)[0].value.to_string()` 得到 `0`，对照 `-0.0` 仍输出 `-0.0`。adapter 先解析为 serde_json::Value，latest/detail 以该值生成 valueText，目标正文继续复用已变为 0 的值。现有 plc-facts/v2 中文合同的历史查询说明明确要求保留负零。受影响的是显示、预览与采集值回环。

探针输入示例（合成数据）：

~~~json
{"pointId":"test","name":"T","dataType":"REAL","value":340282356779733661637539395458142568447,"quality":"good","observedAt":"2026-11-20T08:02:03+08:00"}
~~~

## 验收证据

| 项 | 结果与范围 |
| --- | --- |
| AC01 | 部分通过。只读 dev 原生 GET 验证 options、外部 PLC 的 DB 21 单点、多点、全量 latest 及 false。夹具验证 0、false、坏质量；页面与 adapter 有空状态、超时和 HTTP 错误反馈，浏览器计数确认 GET 无 POST。上述两项 REAL 缺陷导致原值展示失败。 |
| AC02 | 部分通过。dev GET 读取历史列表和 ID 1 的同次两点详情。浏览器提示混合样本，原生预览回查详情。含上述边界 REAL 的合法详情会被拒绝。 |
| AC03 | 部分通过。夹具验证同 PLC 不同 DB、同源目标拒绝、配置修订失效、URL、身份及序号。REAL 负零预览正文与源值不同。 |
| AC04 | 夹具通过普通样本的免 Bearer POST、匹配回执和同次目标 GET。REAL 负零的原值回环失败。实际 dev 页面 POST、回执与回读仍待用户执行。 |
| AC05 | 夹具验证首发已存后断开，显式重试的两次请求字节相同，duplicate、单条目标及 409 后禁止重发。重启提示由界面与双语说明复核。 |
| AC06 | 夹具与源码复核序号边界、冲突、空/缺点、坏类型、修订和 HTTP gate。配置与预览校验可阻止无效发送；缺陷 1 对合法值产生误拒绝。 |
| AC07 | 原生配置和回环测试通过。旧文档与备份处理、重开、SQLite 操作前后字节比较、导出和日志的样本标识/时间/正文标记检查通过，测试自有 profile。 |
| AC08 | 独立 Chrome 浏览器夹具通过 1280×800 中文浅色与 1024×720 英文暗色，验证选样、弹窗、键盘、宽度保存与恢复、未知反馈、重试及回读。双语 README 提供 dev 步骤。操作者 Verification；真实 GET 为 PLC-BE012-DEV-441247C3 / DB 21，浏览器与 Rust POST 使用合成目标，正式页面写入尚无实际操作记录。 |

## 命令、限制与交接

- SMA 目录执行 `pnpm check`、`pnpm test`、`pnpm build`，退出 0，20 项测试通过。打包有既有 PURE 注解和体积提示。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline` 均退出 0。
- 临时 SMA_ENV_FILE 配置 HTTP 默认关闭，执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline -- --test-threads=1`，最终 42 项通过、1 项默认忽略。并行初跑既有 SMA-007 fixture_root 同名碰撞，沙箱内随机端口监听被拒；本机串行首轮另有既有 manual_run 夹具 WouldBlock，复跑通过。回环 POST 仅在自建随机端口上执行。
- `SMA_HTTP_ENABLED=true cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --test acquisition_loopback_tests dev_get_only -- --exact --ignored` 使用测试环境文件、本机 127.0.0.1:8000，1 项通过，退出 0。
- 以本机 Playwright/Chrome 对临时 Vite 15208 执行交付的 `tests/acquisition-loopback.browser.cjs`，退出 0。会话和 Vite 已关闭，自建探针、环境文件已删除。前端 dist 与 Cargo target 使用原有共享构建目录。`git diff --check` 退出 0。
- Development 修正上述两种 REAL，并用源 GET、历史详情与预览正文验证后重新交接精确候选。复验通过后由 Human Owner 确认测试 DB（既有示例 61421）、注册实例/代次及可用序号，以页面显式 POST、核对回执和目标历史进行最终验收。

## QA2 · SMA-008 r3 rework-1 · 2026-11-20

**当前 verdict 为 qa_blocked。** QA1 的两项 REAL 缺陷已关闭。软件与隔离回环检查通过。AC04 尚缺 Human Owner 在现有 dev 页面显式执行 POST 后的真实回执及目标历史。交接 Human Owner 完成该操作并决定最终验收，当前无代码返工项。

独立 Verification 在交付工作树以 tasks.md 最后一段的 31 行重新计算 SHA-256，得到 `b00447cd99f229bb6826f8393e158e7ecc6200a8f7c7564704588fa56744be17`。逐文件校验 31/31、只读依赖 3/3 匹配，HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。环境为 macOS 15.7.7、rustc 1.89.0、pnpm 11.11.0。

| 验收项 | QA2 证据 |
| --- | --- |
| AC01 | dev GET 从 PLC-BE012-DEV-441247C3 / DB 21 读取 options、单点、多点及全部点。隔离 latest 返回 0、false、正负 REAL 边界值和原始 -0，Rust 断言精确 valueText，Vue 点表直接渲染该字符串。沿用 QA1 空状态及错误反馈复核。 |
| AC02 | dev 历史列表与详情 ID 1 读取成功。浏览器验证混合样本提示，原生详情独立断言正负边界与 -0。 |
| AC03 | 原生夹具在同 PLC 不同 DB 预览，无 POST；实际发送字节与预览正文相等，包含原始 REAL。目标相同和配置修订失效检查通过。 |
| AC04 | 隔离 HTTP 的样本 POST、回执与目标详情已通过，目标中的原始数值、点位与采集时间有断言。现有 dev 的人工 POST、实际业务回执和对应目标历史待补。 |
| AC05 | 隔离服务模拟提交后断开，重发收到 duplicate，两次请求字节相同且目标为单条。新会话使用旧 handle 失败；浏览器显示未知与手动重试。 |
| AC06 | 正负 binary32 溢出中点减一（绝对值）接纳，精确中点及其外侧拒绝。合成 -0 保留。序号、类型、目标与 HTTP gate 回归通过。 |
| AC07 | 临时 SQLite 前后字节、备份导出及日志断言通过，旧配置读写、导入与重开回归通过。 |
| AC08 | Chrome 模拟 IPC 复跑 1280×800 中文浅色和 1024×720 英文暗色，两种尺寸、键盘、弹窗、列宽保存与恢复、未知/重试/回读检查通过。现有双语 README 提供操作步骤。操作者为 QA2，真实 GET 使用上述 DB 21，隔离 POST 目标为夹具 DB 61421。 |

- 在 SMA 目录执行 `pnpm check`、`pnpm test`（20 项）、`pnpm build --outDir <QA临时目录>/dist`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`git diff --check`，均退出 0。Vite 报告构建体积提示。
- 使用测试自有 SMA_ENV_FILE 执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline -- --test-threads=1`。首轮沙箱禁止夹具监听（EPERM，退出 101），获准本机回环后 43 项通过，1 项 dev GET 默认忽略，退出 0。单独设置 SMA_HTTP_ENABLED=true 执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --test acquisition_loopback_tests dev_get_only -- --exact --ignored`，1 项通过，退出 0。
- 使用 Vite 15208 和独立 Playwright CLI Chrome 会话运行交付的 tests/acquisition-loopback.browser.cjs，得到两种尺寸场景通过的结果。浏览器控制台仅记录 favicon.ico 404。会话与 Vite 已关闭，测试自有临时产物清理，保留共享 Cargo target。
- 人工步骤请使用已登记的测试实例、代次、目标 DB 和可用序号。记录操作者、源与目标、sampleId、sourceSeq、HTTP 状态与业务回执，按 sampleId 回读目标历史并比对点值、类型、质量与采集时间。
