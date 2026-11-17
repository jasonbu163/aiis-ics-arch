Task ID: DS-003
Revision: r5
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DS-003 r5 -> Development 接续 r4 已有工作 -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 按保存版本及 PLC 实例导出完整 S7 点位 JSON
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; aiis-ics-arch::DAA-017 r5; device-simulator::DS-002 r2
Depends On: ARCH-PLC-001 r5 和 r4 下游时序衔接已批准；本任务 r5 已获 Human Owner 精确实施批准；跨应用验证依赖 DAA-017 实际导入候选

# DS-003 r5：按 PLC 实例导出点位 JSON

## 1. 状态、目标与边界

2026-11-17（Asia/Shanghai），Human Owner 反馈已在 DS、DAA 各自的 .local/dev 手工测试中英切换及 display_name，结果没问题；该反馈是用户手工观察，不等于独立 QA 通过或最终验收，两基础任务当前仍为 qa_blocked。用户明确授权后续 JSON 互通直接使用各应用各自的 .local/dev，无需另建 profile；环境授权与实施批准为不同事实；此前 r4 已获精确实施范围批准，本 r5 也已另获精确批准。

**本 r5 实施范围已获 Human Owner 精确批准。** r4 开发中确认安全处理已有同名目标需要收窄交互；本 r5 明确同名目标一律拒绝并提示选择其他目录，不执行覆盖。r4 原文和批准记录封存在附录；Development 可按本 r5 接续。双语任务原 QA 历史及 qa_blocked 状态不变。

目标：用户从明确保存版本选择 PLC 实例，确认可达地址，导出每实例一份完整 S7 JSON。DAA 首期仅用该文件新建 PLC；来源、身份冲突及同文件重导均拒绝，不做已有 PLC 合并、更新或覆盖。DS 导入、DAA 导出、FF/CA 和现场采用均非本任务。

## 2. 来源、选择与用户流程

1. 用户先选择一个确实存在且完整可读的不可变 `saved_revision`；列表中的实例及其 DB/点均来自**该版本**，不能把实例页当下草稿冒充所选版本。显示所选 revision 标识、保存信息和该实例当前 selected / actual_loaded 的真实标识或缺失状态。所选版本与实际 loaded 不同或无法核验时，清晰提示并由用户明确确认；不得称为已模拟成功或用 selected 代替 actual_loaded。未保存编辑、模拟状态/实时值不进入文件。
2. 可多选所选版本里的实例，分别展示 DB、全部点、类型、位置、启停事实和逐项错误。为每个实例显示并由用户填写或明确确认 `connection` 客户端目标：合法 IPv4 单播 host、port 1..65535、rack 0..7、slot 0..31；禁止将通配监听地址当客户端目标。loopback 仅为同机目标，提示跨机器不可直接使用。展示客户端/服务端 TSAP 方向及推导；若导出为非默认 TSAP，明确 DAA 当前不能导入执行，不得省略来伪装兼容。只读取 DS 模拟配置和操作者输入，不发网络包、连接真实 PLC 或启动模拟器。
3. 批量预览逐实例显示数目、来源版本、字段、错误和每份是否可导出；含禁用 DB 和点。名称、地址、源映射/确认、类型、范围或重叠有问题时，阻断该实例并定位 DB/点，不以禁用绕过或改写默认值。其他独立实例可继续，最终逐个报告成功、失败、取消；不能把部分成功表述为全部成功。
4. 通过原生目录选择器显式选择目标目录；每实例文件名为稳定 PLC UUID 加 .json。若目标已存在（含文件、目录或符号链接），该实例明确拒绝并提示选择其他目录；不提供覆盖或改名绕过，原目标保持原样。每个文件在所选目录使用自有临时文件写入并验证完整 bytes，再以原子不覆盖方式发布；目标在预览后被其他操作创建时同样拒绝，不能先检查后以覆盖式 rename 写入。取消或失败不能留下目标半文件、删除原有文件或越目录写入；只清理本次临时文件。若平台或文件系统不能证明上述不覆盖及原子发布，明确失败，不回退为覆盖。多实例逐项报告成功、冲突或失败，重复点击与并发结果不冒称全部成功。
5. 导出是配置只读操作：不得保存/发布草稿、修改来源归档或历史、改变 selected/actual_loaded、启动/停止实例、改变规则/权限/初值。可对已保存原始 payload 建立有界只读快照或短期保护，以避免预览到执行期间被版本清理或源发生竞争；如版本不存在或完整性不能核实则该实例失败，不能用其他版本替代。

## 3. 同一候选格式与字段语义

本任务实现 [ARCH-PLC-001 r5 §3–5、§6.1](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 **`aiis.plc_points` / `schema_version: 1`**，不是第二种 DS 专属格式。以下示例逐字复制父规格：其中摘要仅示词法，非真实 payload 哈希。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

- UTF-8 无 BOM，一个 PLC；最多 1 MiB、层级 16、32 DB、4096 点。字段、UUID v4、名称、整数词法、未知字段、连接端点等按父规格严格验证；不能截断或猜测。保存的实际配置 payload 原始字节 SHA-256 填 `export.payload_sha256`，`revision_id` 与该字节必须指向同一个真实 saved revision；生成时间使用项目上海时间工具，RFC 3339 `+08:00`，时间不可用则报错，不能伪造。`origin` 是身份命名空间而非每点作者：对尚无外部绑定的本机 DS 配置，取真实 workspace profile 与 PLC UUID；导出不偷偷重编号。若当前实现存在不可表达或不一致的外部来源，明确阻断而不伪造来源；外部来源导入及其持久化不在本任务。
- 每点均输出 `display_names` 严格对象（`zh-CN` / `en-US` 两个字符串），从所选保存版本取值，旧版本缺字段则两者 `""`；不得从 `name`、另一语言、路径、注释或旧显示名推测。旧 DS `displayName` 如非空按原文放入可选 `display_name`，明确语言未标记，绝不归入双语值。两种语言、旧单条值均按父合同 UTF-8 字节上限检查，任何无效值不截断或换点。
- 每点输出 `description` 字符串：取所选保存版本中 DS-004 提供、用户明确维护的独立可选描述，非空原样输出；旧版本缺失或值为空输出 `""`。手工点与 TIA 点都可填写；不能从旧 displayName、TIA comment、双语名推测。DAA 收到描述和其原有 comment 的处理遵循 DAA-017 r5 的预览与显式确认，不增加 DAA 上报字段。
- 每个 DB、点的 ID、名称、DB 编号/大小、类型、byte/bit、可证实 `source_path` 都来自被选版本的已确认事实；无实际路径时省略，不能从显示名杜撰。预览同时展示两个语言的原值、无语言旧值（如有）和描述；切顶栏语言只改变界面显示，不改变输出。输出所有声明点，包括 disabled 点：DS 的 DB 与 point `source_enabled` 均为实际各自 `enabled`，不是采集组、采集许可或写权限。DS 当前禁用分支若未做布局校验，导出时仍需按合同校验所有点。
- 类型含 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL、STRING[n]（1..254）；BOOL bit 0..7，其他类型禁止 bit；按 S7 存储宽度、ASCII STRING 的 n+2 字节、DB 长度、物理重叠规则逐点验证，不能仅按现有 enabled 集合推算。未知类型、未确认名称/布局、无效 DB、非法 bit、越界、重复标识/技术名、重复 DB 号或不满足合同的 disabled 点均使该实例失败。不得输出模拟初值、规则、现场凭据、文件系统路径或实时值。
- DAA 必须原样能接收这一份候选格式；本任务不生成第二份筛选文件。实际 DS→DAA 受控闭环属于 DAA-017 的跨应用验收，同时由 DS Development/Verification 提供精确 exporter 候选及其产生文件和来源摘要；本任务单独的格式验证不能冒充闭环。

## 4. 技术实施边界（仅供批准后 Development）

DS 当前实例页以草稿为数据源，保存版本读取与原始 payload 的哈希校验在 runtime 配置存储；本任务需通过正式 runtime 服务读取相同 revision 的原始 bytes、解析结果与受保护引用，不能由 UI 拼接点表或将草稿序号当 revision。桥接返回结构化预览/定位错误、版本和每文件结果，不泄露 profile 绝对路径。多次预览/取消需清理本任务资源，不引入长期后台任务。

Tauri 当前没有文件夹选择能力依赖。拟在 `src-tauri/Cargo.toml` 增加精确 `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，在 Rust 端注册原生对话框并选目录；仅更新 DS 桌面 Cargo.lock 的该依赖必要传递闭包，不升级其他依赖或添加 npm 包。不提供任意前端文件系统路径/宽泛 FS capability：由后端保存本次原生选择的短期、不可猜测授权引用，确认绑定路径和实例，结束即失效。所选 crate 版本与本机缓存的 manifest 兼容性只是 PM 源码检查，编译、权限、平台对话框及传递依赖仍需 Development 真实验证；如需其他依赖、系统权限、清单文件或扩大文件范围，停止并回 PM 修订，而非悄悄放宽。项目普通入口仍为 `pnpm tauri dev`。

中文/英文文案新增成对 locale；实例/预览表格沿用共享表格列宽与本机偏好工具：普通列可拖拽、设置最小宽度、横向滚动、按稳定字段键隔离并恢复默认，功能列允许固定。已存在表格不能因为导出入口破坏列宽偏好；不把偏好写进业务版本。

## 5. 已批准的 Development 允许文件

本 r5 已获精确批准，文件白名单与已批准 r4 相同。路径均以 `automation-world/device-simulator/` 为根；花括号仅展开列名，不是通配符。仅为本功能改动列出的文件；发现需新增其他文件须回 PM。本次 PM 工作只写本 `spec.md`，角色文档按 STD 的各自权限创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| runtime 模型及版本查询 | `runtime/src/domain/{mod.rs,configuration.rs}`；`runtime/src/services/{mod.rs,queries.rs,versions.rs,layout.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs}`；`runtime/src/app.rs` | `runtime/src/domain/plc_catalog.rs`；`runtime/src/services/catalog_export.rs` |
| Tauri 桥接及原生选择 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/mod.rs`；`src-tauri/{Cargo.toml,Cargo.lock}` | `src-tauri/src/commands/catalog_export.rs` |
| UI 与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/simulator/components/CatalogExportDialog.vue` |
| 测试、用户说明与索引 | `{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/plc_catalog_export.rs`；`tests/plc-catalog-export.test.mjs`；`tests/fixtures/plc-catalog-v1.json` |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后由 Development 创建本 bundle `tasks.md`；交接后由独立 Verification 创建 `checklist.md` |

不改数据库物理 schema、迁移、.env、设备/网络协议能力、pnpm 依赖/锁或其他任务。用户已授权通过 DS 自身应用在核对后的 .local/dev 仅新增本任务可识别测试实例及必要草稿/版本；不覆盖或清理原有实例、配置及历史。导出功能本身只读所选版本，用户侧文件输出只写本次明确确认的目录。

## 6. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DS01 | 从已核对的 DS .local/dev 的保存版本中选择本次可识别测试 PLC，导出一份完整 JSON；版本、摘要和点只来自该实例，selected 或实际 loaded 有差异时明确提示。 |
| DS02 | 完整文件按父共同格式严格解析，含 BOOL、INT、REAL、STRING 和停用点；按所选版本核对 ID、程序名、类型、地址、双语、描述及旧无语言值，不丢点或串实例。 |
| DS03 | 重复 ID/名称/DB、错误类型/bit、STRING 宽度、地址重叠/越界、未确认名称或地址、非法来源、非整数和超预算的启用及禁用点均定位并阻止对应文件，不通过默认值补救；合法另一实例的结果单独报告。 |
| DS04 | 通配地址、无效 IPv4/端口、无法确认的客户端目标及错误 TSAP 被阻断；loopback 告知同机限制；非默认 TSAP 按合同精确保留并提示 DAA 当前不兼容，不能悄悄变默认。 |
| DS05 | 目录选择取消不写；同名文件、目录或符号链接均拒绝并提示选择其他目录，原目标字节不变。预览后目标被并发创建、重复提交、只读/写错和符号链接或目录竞争时，不覆盖、不越目录、不留下目标半文件；成功仅原子发布至原本不存在的目标，逐实例报告结果。 |
| DS06 | 读/预览/导出前后比较自有 profile 的配置 payload/source bytes 与 SHA、草稿/版本/selected/loaded、规则及实例状态；除用户指定输出外没有业务写入，也不触发网络连接或实例启停。版本被删/竞争时失败而非换源。 |
| DS07 | 中文和英文导出入口、实例选择和预览可操作；本次不将列宽跨重启作为 JSON 主线验收前置。 |
| DS08 | 原有 S7 创建、保存、版本选择与运行行为回归；真实 macOS arm64 原生 Tauri 文件夹对话框和落盘可验证。纯 Vue/模拟器测试不代替原生交互；其他平台未测如实标记。 |
| DS09 | 保存实际导出的 JSON 文件及 SHA、源 revision 和实例对应关系，交 DAA 用该文件新建 PLC；同来源再次导入由 DAA 明确拒绝。合成 fixture 不冒称跨应用闭环。 |
| DS10 | 使用正式交付源码与锁文件，在隔离路径执行相关 Rust/Node 测试、类型检查、前端构建和 native-s7 桥接检查；记录命令、环境、退出码、未跑项及清理。可执行受限语义交给独立 QA 再验。 |
| DS11 | 选旧 revision 的未标记旧值被原样导出，缺双语/描述输出两空语言及空描述；含单侧空、两侧非空、手工点描述和禁用点的版本按实际值导出，语言切换不改变数据或 SHA；错误类型、超字节字段阻断该实例，不能把旧值或注释冒充语言/描述。 |
| DS12 | 实际测试核对 DS 的 .local/dev、进程、来源版本与目标目录；仅新增可识别测试对象，不覆盖既有实例及历史，不连接真实设备。目标或进程无法确认时停止。 |
| DS13 | 两份中英文 USER_GUIDE 记录核对 DS .local/dev、准备测试实例、选择版本、导出文件及 SHA、交 DAA 使用和清理自有对象的可复验步骤；未实现或未验证入口不能写成可用。 |

## 7. 验证与 gate、风险和回退

主线以所选实例真实导出文件为依据，记录实际候选、revision、实例、文件 SHA 和结果；单元测试不能冒充 DAA 导入。Development 与 Verification 分别记录测试，Human Owner 分别决定验收。已授权按应用流程使用 .local/dev 新增测试对象；若需物理 schema、迁移、覆盖已有数据或白名单外文件则停止。旧版原生兼容、列宽跨重启和完整系统层证明不是本 JSON 任务新增前置，未证事实不能标为通过。

### 本机合成互通与人工复验（r5 已批准）

1. **角色与状态。** 仅当父 ARCH-PLC-001 r5、本任务 DS-003 r5 和涉及两基础的下游时序衔接均经 Human Owner 精确批准后，Development 才可修改本任务白名单，记录候选、自检并 handoff；fresh-context Verification 复核实际交付候选。两基础仍按各自已批准验收办理，其现有 qa_blocked 不能由本任务改成通过。若两项候选涉及相同文件，先记录现有改动并协调整合，不能覆盖其他工作；完整最终候选及锁文件须在正式交付树复核。
2. **本机测试目标。** 用户明确授权直接使用 DS、DAA 各自的 .local/dev。先核对实际应用、进程、profile 及路径，区分已有对象和本任务带唯一标识的合成测试 PLC/文件；不得覆盖已有配置、实例或历史。可使用现有已运行应用或项目普通入口；不输出、复制或修改真实 .env 内容。普通启动程序可能按既有规则读取自身 .env，必须确认实际 profile 不回落到其他位置；目标不明即停止。
3. **原生事故与残余风险。** 此前 DAA 窗口退出后 CUA 可能重绑或启动用户默认 profile，影响未知，该历史及原 QA 结果保留。此次仅操作经核对的自有进程及已授权 .local/dev，不按应用名重绑或触及不明 profile；若无法确认目标、避免影响既有数据、设备或真实上报则停止。无需 VM、Windows 或完整系统层排查，不能声称系统缓存完全隔离。
4. **主线与清理。** 通过 DS 正常流程新增可识别测试实例和所需保存版本，导出文件供 DAA 在自己的 .local/dev 新建测试 PLC；不提供 DB/UDT，显式分组、保存和激活后只连接该 DS 的 127.0.0.1 端口。先核实既有实例不会被自动采集、连接或上报，无法保证则停止；不得为测试静默改变既有实例或上报设定。v2 使用假 transport，不发真实 POST。新增配置可能产生新 revision、active 指针变化以及正常 runtime 审计事件，不得说整个数据库零写。完成后只通过安全的正常方式清理可确认属于本任务且不影响既有历史的测试 PLC/文件；不可安全删除或已被历史引用的如实保留并说明，绝不删除整个 .local/dev 或已有数据。中英文 USER_GUIDE 写实际复验步骤。

## 8. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品或测试。批准后 Development 按实际触达使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及项目治理规则独立检查。任何自检或 QA 通过均不自动授权上线、真实数据库/设备或 Human Owner 最终验收。

## r4 Human Owner 精确实施批准记录（历史）

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

本决定精确批准 device-simulator::DS-003 r4 实施范围、ARCH-PLC-001 r5 设计范围及两基础原下游门槛的顺序调整，并授权按本规格使用两应用各自 .local/dev 完成受控互通、清理本任务资源及更新手册。本任务批准前完整草案 SHA-256 为 47278826db4c3e5e9ee65ed428236ca9bc957ffb0fb9193950af486215d12ec8。该批准不代表本任务或双语基础 QA 通过、Human Owner 最终验收，也不授权真实设备、外部上报、物理 DDL、用户 profile 迁移、FF/CA 或发布。

## r5 修订与批准记录

r4 开发时发现：对已存在目标，在本机无法仅凭先检查目标身份、再执行覆盖式 rename 保证确认与提交之间无替换竞争。r5 仅将同名目标从可确认覆盖改为明确拒绝并提示换目录，同时要求原子不覆盖发布；其他功能、JSON 合同、点位、采集联测、.local/dev 授权及文件白名单不变。r4 完整原文和已批准事实保留；Human Owner 已另行精确批准 r5。

### Human Owner 精确实施批准

2026-11-17（Asia/Shanghai），Human Owner 对列明 DS-003 r5 和 DAA-017 r5 的批准请求明确回复：

> 批准两个 r5

本决定精确批准 device-simulator::DS-003 r5 的实施范围；用户审阅、登记前完整草案 SHA-256 为 2e2bfa448fcb59fcc3dbb6648df406f49f1dc735552a73beae1195b059b49734。原 r4 实施批准及全部历史继续保留；Development 可按本 r5 接续。该决定不代表 QA 通过或 Human Owner 最终验收，两项双语基础原 qa_blocked 状态不变；原 .local/dev 互通测试授权及数据保护边界继续有效。

## 附录 A：已批准 r4 完整原文（含全部历史）

r4 写前 SHA-256：89ce0e468312e013003f796909765bf94d08d3b6cf07d4d36fd0439aa96699a3；围栏内保留原 UTF-8 字节及末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DS-003
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准父 r5、本 r4 及基础任务下游时序衔接 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 按保存版本及 PLC 实例导出完整 S7 点位 JSON
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; aiis-ics-arch::DAA-017 r4; device-simulator::DS-002 r2
Depends On: ARCH-PLC-001 r5、本任务 r4 和两基础任务下游时序衔接已获 Human Owner 精确批准；跨应用验证还依赖 DAA-017 r4 实际导入候选

# DS-003 r4：按 PLC 实例导出点位 JSON

## 1. 状态、目标与边界

2026-11-17（Asia/Shanghai），Human Owner 反馈已在 DS、DAA 各自的 .local/dev 手工测试中英切换及 display_name，结果没问题；该反馈是用户手工观察，不等于独立 QA 通过或最终验收，两基础任务当前仍为 qa_blocked。用户明确授权后续 JSON 互通直接使用各应用各自的 .local/dev，无需另建 profile；环境授权与实施批准为不同事实；本 r4 已另获精确实施范围批准。

**本 r4 实施范围已获 Human Owner 精确批准。** Human Owner 已批准 ARCH-PLC-001 r5、DS-003 r4、DAA-017 r4 及下游顺序调整，两个 JSON 任务可各自开展 Development 和自检，不再等待两基础任务最终验收。DS-004 r2、DAA-018 r3 的原独立验收及 QA 历史不变，目前仍为 qa_blocked；本决定不是 QA 通过或最终验收。另一个 JSON 任务有独立验收链。

目标：用户从明确保存版本选择 PLC 实例，确认可达地址，导出每实例一份完整 S7 JSON。DAA 首期仅用该文件新建 PLC；来源、身份冲突及同文件重导均拒绝，不做已有 PLC 合并、更新或覆盖。DS 导入、DAA 导出、FF/CA 和现场采用均非本任务。

## 2. 来源、选择与用户流程

1. 用户先选择一个确实存在且完整可读的不可变 `saved_revision`；列表中的实例及其 DB/点均来自**该版本**，不能把实例页当下草稿冒充所选版本。显示所选 revision 标识、保存信息和该实例当前 selected / actual_loaded 的真实标识或缺失状态。所选版本与实际 loaded 不同或无法核验时，清晰提示并由用户明确确认；不得称为已模拟成功或用 selected 代替 actual_loaded。未保存编辑、模拟状态/实时值不进入文件。
2. 可多选所选版本里的实例，分别展示 DB、全部点、类型、位置、启停事实和逐项错误。为每个实例显示并由用户填写或明确确认 `connection` 客户端目标：合法 IPv4 单播 host、port 1..65535、rack 0..7、slot 0..31；禁止将通配监听地址当客户端目标。loopback 仅为同机目标，提示跨机器不可直接使用。展示客户端/服务端 TSAP 方向及推导；若导出为非默认 TSAP，明确 DAA 当前不能导入执行，不得省略来伪装兼容。只读取 DS 模拟配置和操作者输入，不发网络包、连接真实 PLC 或启动模拟器。
3. 批量预览逐实例显示数目、来源版本、字段、错误和每份是否可导出；含禁用 DB 和点。名称、地址、源映射/确认、类型、范围或重叠有问题时，阻断该实例并定位 DB/点，不以禁用绕过或改写默认值。其他独立实例可继续，最终逐个报告成功、失败、取消；不能把部分成功表述为全部成功。
4. 通过原生目录选择器显式选目标目录；每实例文件名使用稳定 PLC UUID 加 `.json`，不使用名称、任意输入路径或服务器默认目录。预览所有冲突，覆盖只能由用户对具体目标明确确认；取消不写。目标路径须防止目录穿越、符号链接替换和并发改名绕过确认。每个文件在同目录创建任务自有临时文件，写入完整 bytes 并验证后原子落盘；失败/取消不得留下目标半文件，不删除用户既有文件。提交期间若目标或所选目录状态改变，重新提示或失败，不能覆盖未经确认的对象。重复点击、并发操作和结果未知时返回明确状态，先检查结果再重试；每次预览均绑定 revision、实例、目标和冲突状态，变更使旧确认失效。
5. 导出是配置只读操作：不得保存/发布草稿、修改来源归档或历史、改变 selected/actual_loaded、启动/停止实例、改变规则/权限/初值。可对已保存原始 payload 建立有界只读快照或短期保护，以避免预览到执行期间被版本清理或源发生竞争；如版本不存在或完整性不能核实则该实例失败，不能用其他版本替代。

## 3. 同一候选格式与字段语义

本任务实现 [ARCH-PLC-001 r5 §3–5、§6.1](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 **`aiis.plc_points` / `schema_version: 1`**，不是第二种 DS 专属格式。以下示例逐字复制父规格：其中摘要仅示词法，非真实 payload 哈希。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

- UTF-8 无 BOM，一个 PLC；最多 1 MiB、层级 16、32 DB、4096 点。字段、UUID v4、名称、整数词法、未知字段、连接端点等按父规格严格验证；不能截断或猜测。保存的实际配置 payload 原始字节 SHA-256 填 `export.payload_sha256`，`revision_id` 与该字节必须指向同一个真实 saved revision；生成时间使用项目上海时间工具，RFC 3339 `+08:00`，时间不可用则报错，不能伪造。`origin` 是身份命名空间而非每点作者：对尚无外部绑定的本机 DS 配置，取真实 workspace profile 与 PLC UUID；导出不偷偷重编号。若当前实现存在不可表达或不一致的外部来源，明确阻断而不伪造来源；外部来源导入及其持久化不在本任务。
- 每点均输出 `display_names` 严格对象（`zh-CN` / `en-US` 两个字符串），从所选保存版本取值，旧版本缺字段则两者 `""`；不得从 `name`、另一语言、路径、注释或旧显示名推测。旧 DS `displayName` 如非空按原文放入可选 `display_name`，明确语言未标记，绝不归入双语值。两种语言、旧单条值均按父合同 UTF-8 字节上限检查，任何无效值不截断或换点。
- 每点输出 `description` 字符串：取所选保存版本中 DS-004 提供、用户明确维护的独立可选描述，非空原样输出；旧版本缺失或值为空输出 `""`。手工点与 TIA 点都可填写；不能从旧 displayName、TIA comment、双语名推测。DAA 收到描述和其原有 comment 的处理遵循 DAA-017 r4 的预览与显式确认，不增加 DAA 上报字段。
- 每个 DB、点的 ID、名称、DB 编号/大小、类型、byte/bit、可证实 `source_path` 都来自被选版本的已确认事实；无实际路径时省略，不能从显示名杜撰。预览同时展示两个语言的原值、无语言旧值（如有）和描述；切顶栏语言只改变界面显示，不改变输出。输出所有声明点，包括 disabled 点：DS 的 DB 与 point `source_enabled` 均为实际各自 `enabled`，不是采集组、采集许可或写权限。DS 当前禁用分支若未做布局校验，导出时仍需按合同校验所有点。
- 类型含 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL、STRING[n]（1..254）；BOOL bit 0..7，其他类型禁止 bit；按 S7 存储宽度、ASCII STRING 的 n+2 字节、DB 长度、物理重叠规则逐点验证，不能仅按现有 enabled 集合推算。未知类型、未确认名称/布局、无效 DB、非法 bit、越界、重复标识/技术名、重复 DB 号或不满足合同的 disabled 点均使该实例失败。不得输出模拟初值、规则、现场凭据、文件系统路径或实时值。
- DAA 必须原样能接收这一份候选格式；本任务不生成第二份筛选文件。实际 DS→DAA 受控闭环属于 DAA-017 的跨应用验收，同时由 DS Development/Verification 提供精确 exporter 候选及其产生文件和来源摘要；本任务单独的格式验证不能冒充闭环。

## 4. 技术实施边界（仅供批准后 Development）

DS 当前实例页以草稿为数据源，保存版本读取与原始 payload 的哈希校验在 runtime 配置存储；本任务需通过正式 runtime 服务读取相同 revision 的原始 bytes、解析结果与受保护引用，不能由 UI 拼接点表或将草稿序号当 revision。桥接返回结构化预览/定位错误、版本和每文件结果，不泄露 profile 绝对路径。多次预览/取消需清理本任务资源，不引入长期后台任务。

Tauri 当前没有文件夹选择能力依赖。拟在 `src-tauri/Cargo.toml` 增加精确 `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，在 Rust 端注册原生对话框并选目录；仅更新 DS 桌面 Cargo.lock 的该依赖必要传递闭包，不升级其他依赖或添加 npm 包。不提供任意前端文件系统路径/宽泛 FS capability：由后端保存本次原生选择的短期、不可猜测授权引用，确认绑定路径和实例，结束即失效。所选 crate 版本与本机缓存的 manifest 兼容性只是 PM 源码检查，编译、权限、平台对话框及传递依赖仍需 Development 真实验证；如需其他依赖、系统权限、清单文件或扩大文件范围，停止并回 PM 修订，而非悄悄放宽。项目普通入口仍为 `pnpm tauri dev`。

中文/英文文案新增成对 locale；实例/预览表格沿用共享表格列宽与本机偏好工具：普通列可拖拽、设置最小宽度、横向滚动、按稳定字段键隔离并恢复默认，功能列允许固定。已存在表格不能因为导出入口破坏列宽偏好；不把偏好写进业务版本。

## 5. 已批准的 Development 允许文件

路径均以 `automation-world/device-simulator/` 为根；花括号仅展开列名，不是通配符。仅为本功能改动列出的文件；发现需新增其他文件须回 PM。本次 PM 工作只写本 `spec.md`，角色文档按 STD 的各自权限创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| runtime 模型及版本查询 | `runtime/src/domain/{mod.rs,configuration.rs}`；`runtime/src/services/{mod.rs,queries.rs,versions.rs,layout.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs}`；`runtime/src/app.rs` | `runtime/src/domain/plc_catalog.rs`；`runtime/src/services/catalog_export.rs` |
| Tauri 桥接及原生选择 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/mod.rs`；`src-tauri/{Cargo.toml,Cargo.lock}` | `src-tauri/src/commands/catalog_export.rs` |
| UI 与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/simulator/components/CatalogExportDialog.vue` |
| 测试、用户说明与索引 | `{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/plc_catalog_export.rs`；`tests/plc-catalog-export.test.mjs`；`tests/fixtures/plc-catalog-v1.json` |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后由 Development 创建本 bundle `tasks.md`；交接后由独立 Verification 创建 `checklist.md` |

不改数据库物理 schema、迁移、.env、设备/网络协议能力、pnpm 依赖/锁或其他任务。用户已授权通过 DS 自身应用在核对后的 .local/dev 仅新增本任务可识别测试实例及必要草稿/版本；不覆盖或清理原有实例、配置及历史。导出功能本身只读所选版本，用户侧文件输出只写本次明确确认的目录。

## 6. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DS01 | 从已核对的 DS .local/dev 的保存版本中选择本次可识别测试 PLC，导出一份完整 JSON；版本、摘要和点只来自该实例，selected 或实际 loaded 有差异时明确提示。 |
| DS02 | 完整文件按父共同格式严格解析，含 BOOL、INT、REAL、STRING 和停用点；按所选版本核对 ID、程序名、类型、地址、双语、描述及旧无语言值，不丢点或串实例。 |
| DS03 | 重复 ID/名称/DB、错误类型/bit、STRING 宽度、地址重叠/越界、未确认名称或地址、非法来源、非整数和超预算的启用及禁用点均定位并阻止对应文件，不通过默认值补救；合法另一实例的结果单独报告。 |
| DS04 | 通配地址、无效 IPv4/端口、无法确认的客户端目标及错误 TSAP 被阻断；loopback 告知同机限制；非默认 TSAP 按合同精确保留并提示 DAA 当前不兼容，不能悄悄变默认。 |
| DS05 | 原生目录选择、关闭/取消、同名覆盖拒绝和明确确认、符号链接/目标竞争、只读目录/磁盘写错、并发/重复确认逐一验证；无目标半文件、越目录写入和未经确认覆盖，失败信息正确且用户原文件保留。 |
| DS06 | 读/预览/导出前后比较自有 profile 的配置 payload/source bytes 与 SHA、草稿/版本/selected/loaded、规则及实例状态；除用户指定输出外没有业务写入，也不触发网络连接或实例启停。版本被删/竞争时失败而非换源。 |
| DS07 | 中文和英文导出入口、实例选择和预览可操作；本次不将列宽跨重启作为 JSON 主线验收前置。 |
| DS08 | 原有 S7 创建、保存、版本选择与运行行为回归；真实 macOS arm64 原生 Tauri 文件夹对话框和落盘可验证。纯 Vue/模拟器测试不代替原生交互；其他平台未测如实标记。 |
| DS09 | 保存实际导出的 JSON 文件及 SHA、源 revision 和实例对应关系，交 DAA 用该文件新建 PLC；同来源再次导入由 DAA 明确拒绝。合成 fixture 不冒称跨应用闭环。 |
| DS10 | 使用正式交付源码与锁文件，在隔离路径执行相关 Rust/Node 测试、类型检查、前端构建和 native-s7 桥接检查；记录命令、环境、退出码、未跑项及清理。可执行受限语义交给独立 QA 再验。 |
| DS11 | 选旧 revision 的未标记旧值被原样导出，缺双语/描述输出两空语言及空描述；含单侧空、两侧非空、手工点描述和禁用点的版本按实际值导出，语言切换不改变数据或 SHA；错误类型、超字节字段阻断该实例，不能把旧值或注释冒充语言/描述。 |
| DS12 | 实际测试核对 DS 的 .local/dev、进程、来源版本与目标目录；仅新增可识别测试对象，不覆盖既有实例及历史，不连接真实设备。目标或进程无法确认时停止。 |
| DS13 | 两份中英文 USER_GUIDE 记录核对 DS .local/dev、准备测试实例、选择版本、导出文件及 SHA、交 DAA 使用和清理自有对象的可复验步骤；未实现或未验证入口不能写成可用。 |

## 7. 验证与 gate、风险和回退

主线以所选实例真实导出文件为依据，记录实际候选、revision、实例、文件 SHA 和结果；单元测试不能冒充 DAA 导入。Development 与 Verification 分别记录测试，Human Owner 分别决定验收。已授权按应用流程使用 .local/dev 新增测试对象；若需物理 schema、迁移、覆盖已有数据或白名单外文件则停止。旧版原生兼容、列宽跨重启和完整系统层证明不是本 JSON 任务新增前置，未证事实不能标为通过。

### 本机合成互通与人工复验（已批准范围）

1. **角色与状态。** 仅当父 r5、本任务 r4 和涉及两基础的下游时序衔接均经 Human Owner 精确批准后，Development 才可修改本任务白名单，记录候选、自检并 handoff；fresh-context Verification 复核实际交付候选。两基础仍按各自已批准验收办理，其现有 qa_blocked 不能由本任务改成通过。若两项候选涉及相同文件，先记录现有改动并协调整合，不能覆盖其他工作；完整最终候选及锁文件须在正式交付树复核。
2. **本机测试目标。** 用户明确授权直接使用 DS、DAA 各自的 .local/dev。先核对实际应用、进程、profile 及路径，区分已有对象和本任务带唯一标识的合成测试 PLC/文件；不得覆盖已有配置、实例或历史。可使用现有已运行应用或项目普通入口；不输出、复制或修改真实 .env 内容。普通启动程序可能按既有规则读取自身 .env，必须确认实际 profile 不回落到其他位置；目标不明即停止。
3. **原生事故与残余风险。** 此前 DAA 窗口退出后 CUA 可能重绑或启动用户默认 profile，影响未知，该历史及原 QA 结果保留。此次仅操作经核对的自有进程及已授权 .local/dev，不按应用名重绑或触及不明 profile；若无法确认目标、避免影响既有数据、设备或真实上报则停止。无需 VM、Windows 或完整系统层排查，不能声称系统缓存完全隔离。
4. **主线与清理。** 通过 DS 正常流程新增可识别测试实例和所需保存版本，导出文件供 DAA 在自己的 .local/dev 新建测试 PLC；不提供 DB/UDT，显式分组、保存和激活后只连接该 DS 的 127.0.0.1 端口。先核实既有实例不会被自动采集、连接或上报，无法保证则停止；不得为测试静默改变既有实例或上报设定。v2 使用假 transport，不发真实 POST。新增配置可能产生新 revision、active 指针变化以及正常 runtime 审计事件，不得说整个数据库零写。完成后只通过安全的正常方式清理可确认属于本任务且不影响既有历史的测试 PLC/文件；不可安全删除或已被历史引用的如实保留并说明，绝不删除整个 .local/dev 或已有数据。中英文 USER_GUIDE 写实际复验步骤。

## 8. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品或测试。批准后 Development 按实际触达使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及项目治理规则独立检查。任何自检或 QA 通过均不自动授权上线、真实数据库/设备或 Human Owner 最终验收。

## Human Owner 精确实施批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

本决定精确批准 device-simulator::DS-003 r4 实施范围、ARCH-PLC-001 r5 设计范围及两基础原下游门槛的顺序调整，并授权按本规格使用两应用各自 .local/dev 完成受控互通、清理本任务资源及更新手册。本任务批准前完整草案 SHA-256 为 47278826db4c3e5e9ee65ed428236ca9bc957ffb0fb9193950af486215d12ec8。该批准不代表本任务或双语基础 QA 通过、Human Owner 最终验收，也不授权真实设备、外部上报、物理 DDL、用户 profile 迁移、FF/CA 或发布。

## 附录 A：完整 r3 原文（含全部历史，非本草案）

写前 SHA-256：c7f98356b517889c8ebf13c3c7ccfcbee02549104e99a1f28b6ca7ac70713ef5；围栏内保留原始 UTF-8 字节和末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DS-003
Revision: r3
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 双语基础原生 blocker 解除并各自 STD 最终验收 -> Human Owner 精确批准 DS-003 r3 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 按保存版本及 PLC 实例导出完整 S7 点位 JSON
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; aiis-ics-arch::DAA-017 r3; device-simulator::DS-002 r2
Depends On: aiis-ics-arch::ARCH-PLC-001 r4 设计批准；DS-004 和 DAA-018 各自完成 STD 至 Human Owner 最终验收；DS 与 DAA 的受控端到端验证还依赖 DAA-017 r3 实际导入候选

# DS-003 r3：按 PLC 实例导出点位 JSON

## 1. 状态、目标与边界

**本任务为 draft / r3，尚未获得实施批准。** Human Owner 已选择先做 DS→DAA，并授权两应用各自在 `.local` 下新建非 `dev` 合成环境、测试后清理及在手册保留人工复验步骤；这不是对本实施任务或最终验收的批准。[ARCH-PLC-001 r4](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获批准。DS-004 r2 与 DAA-018 r3 各自实施范围已批准，但独立 QA 目前均 `qa_blocked`，原生必测及 Human Owner 最终验收未完成；必须先处理隔离事件并完成两项原有 STD 最终验收，再对本 r3 和 DAA-017 r3 分别取得精确实施批准，才可按各自范围推进。旧 r1/r2 均为未批准实施草案，原文和历史保留。

目标：用户从一个明确的 DS 保存版本选择一个或多个 PLC 实例，确认客户端可达地址，在所选目录为每个实例各导出一份完整 S7 点位 JSON。优先服务 DS→DAA 无需再次导入 DB/UDT 的路径；无论点位启用状态均不静默丢失。DS 导入 JSON、DAA 导出 JSON、FF 适配、正式发布跨运行时公共合同、其他协议和真实 PLC/数据库/现场采用均非本任务范围。不得因本规格启动实现、修改代码或写入现有 profile。

## 2. 来源、选择与用户流程

1. 用户先选择一个确实存在且完整可读的不可变 `saved_revision`；列表中的实例及其 DB/点均来自**该版本**，不能把实例页当下草稿冒充所选版本。显示所选 revision 标识、保存信息和该实例当前 selected / actual_loaded 的真实标识或缺失状态。所选版本与实际 loaded 不同或无法核验时，清晰提示并由用户明确确认；不得称为已模拟成功或用 selected 代替 actual_loaded。未保存编辑、模拟状态/实时值不进入文件。
2. 可多选所选版本里的实例，分别展示 DB、全部点、类型、位置、启停事实和逐项错误。为每个实例显示并由用户填写或明确确认 `connection` 客户端目标：合法 IPv4 单播 host、port 1..65535、rack 0..7、slot 0..31；禁止将通配监听地址当客户端目标。loopback 仅为同机目标，提示跨机器不可直接使用。展示客户端/服务端 TSAP 方向及推导；若导出为非默认 TSAP，明确 DAA 当前不能导入执行，不得省略来伪装兼容。只读取 DS 模拟配置和操作者输入，不发网络包、连接真实 PLC 或启动模拟器。
3. 批量预览逐实例显示数目、来源版本、字段、错误和每份是否可导出；含禁用 DB 和点。名称、地址、源映射/确认、类型、范围或重叠有问题时，阻断该实例并定位 DB/点，不以禁用绕过或改写默认值。其他独立实例可继续，最终逐个报告成功、失败、取消；不能把部分成功表述为全部成功。
4. 通过原生目录选择器显式选目标目录；每实例文件名使用稳定 PLC UUID 加 `.json`，不使用名称、任意输入路径或服务器默认目录。预览所有冲突，覆盖只能由用户对具体目标明确确认；取消不写。目标路径须防止目录穿越、符号链接替换和并发改名绕过确认。每个文件在同目录创建任务自有临时文件，写入完整 bytes 并验证后原子落盘；失败/取消不得留下目标半文件，不删除用户既有文件。提交期间若目标或所选目录状态改变，重新提示或失败，不能覆盖未经确认的对象。重复点击、并发操作和结果未知时返回明确状态，先检查结果再重试；每次预览均绑定 revision、实例、目标和冲突状态，变更使旧确认失效。
5. 导出是配置只读操作：不得保存/发布草稿、修改来源归档或历史、改变 selected/actual_loaded、启动/停止实例、改变规则/权限/初值。可对已保存原始 payload 建立有界只读快照或短期保护，以避免预览到执行期间被版本清理或源发生竞争；如版本不存在或完整性不能核实则该实例失败，不能用其他版本替代。

## 3. 同一候选格式与字段语义

本任务实现 [ARCH-PLC-001 r4 §3–5、§6.1](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 **`aiis.plc_points` / `schema_version: 1`**，不是第二种 DS 专属格式。以下示例逐字复制父规格：其中摘要仅示词法，非真实 payload 哈希。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

- UTF-8 无 BOM，一个 PLC；最多 1 MiB、层级 16、32 DB、4096 点。字段、UUID v4、名称、整数词法、未知字段、连接端点等按父规格严格验证；不能截断或猜测。保存的实际配置 payload 原始字节 SHA-256 填 `export.payload_sha256`，`revision_id` 与该字节必须指向同一个真实 saved revision；生成时间使用项目上海时间工具，RFC 3339 `+08:00`，时间不可用则报错，不能伪造。`origin` 是身份命名空间而非每点作者：对尚无外部绑定的本机 DS 配置，取真实 workspace profile 与 PLC UUID；导出不偷偷重编号。若当前实现存在不可表达或不一致的外部来源，明确阻断而不伪造来源；外部来源导入及其持久化不在本任务。
- 每点均输出 `display_names` 严格对象（`zh-CN` / `en-US` 两个字符串），从所选保存版本取值，旧版本缺字段则两者 `""`；不得从 `name`、另一语言、路径、注释或旧显示名推测。旧 DS `displayName` 如非空按原文放入可选 `display_name`，明确语言未标记，绝不归入双语值。两种语言、旧单条值均按父合同 UTF-8 字节上限检查，任何无效值不截断或换点。
- 每点输出 `description` 字符串：取所选保存版本中 DS-004 提供、用户明确维护的独立可选描述，非空原样输出；旧版本缺失或值为空输出 `""`。手工点与 TIA 点都可填写；不能从旧 displayName、TIA comment、双语名推测。DAA 收到描述和其原有 comment 的处理遵循 DAA-017 r3 的预览与显式确认，不增加 DAA 上报字段。
- 每个 DB、点的 ID、名称、DB 编号/大小、类型、byte/bit、可证实 `source_path` 都来自被选版本的已确认事实；无实际路径时省略，不能从显示名杜撰。预览同时展示两个语言的原值、无语言旧值（如有）和描述；切顶栏语言只改变界面显示，不改变输出。输出所有声明点，包括 disabled 点：DS 的 DB 与 point `source_enabled` 均为实际各自 `enabled`，不是采集组、采集许可或写权限。DS 当前禁用分支若未做布局校验，导出时仍需按合同校验所有点。
- 类型含 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL、STRING[n]（1..254）；BOOL bit 0..7，其他类型禁止 bit；按 S7 存储宽度、ASCII STRING 的 n+2 字节、DB 长度、物理重叠规则逐点验证，不能仅按现有 enabled 集合推算。未知类型、未确认名称/布局、无效 DB、非法 bit、越界、重复标识/技术名、重复 DB 号或不满足合同的 disabled 点均使该实例失败。不得输出模拟初值、规则、现场凭据、文件系统路径或实时值。
- DAA 必须原样能接收这一份候选格式；本任务不生成第二份筛选文件。实际 DS→DAA 受控闭环属于 DAA-017 的跨应用验收，同时由 DS Development/Verification 提供精确 exporter 候选及其产生文件和来源摘要；本任务单独的格式验证不能冒充闭环。

## 4. 技术实施边界（仅供批准后 Development）

DS 当前实例页以草稿为数据源，保存版本读取与原始 payload 的哈希校验在 runtime 配置存储；本任务需通过正式 runtime 服务读取相同 revision 的原始 bytes、解析结果与受保护引用，不能由 UI 拼接点表或将草稿序号当 revision。桥接返回结构化预览/定位错误、版本和每文件结果，不泄露 profile 绝对路径。多次预览/取消需清理本任务资源，不引入长期后台任务。

Tauri 当前没有文件夹选择能力依赖。拟在 `src-tauri/Cargo.toml` 增加精确 `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，在 Rust 端注册原生对话框并选目录；仅更新 DS 桌面 Cargo.lock 的该依赖必要传递闭包，不升级其他依赖或添加 npm 包。不提供任意前端文件系统路径/宽泛 FS capability：由后端保存本次原生选择的短期、不可猜测授权引用，确认绑定路径和实例，结束即失效。所选 crate 版本与本机缓存的 manifest 兼容性只是 PM 源码检查，编译、权限、平台对话框及传递依赖仍需 Development 真实验证；如需其他依赖、系统权限、清单文件或扩大文件范围，停止并回 PM 修订，而非悄悄放宽。项目普通入口仍为 `pnpm tauri dev`。

中文/英文文案新增成对 locale；实例/预览表格沿用共享表格列宽与本机偏好工具：普通列可拖拽、设置最小宽度、横向滚动、按稳定字段键隔离并恢复默认，功能列允许固定。已存在表格不能因为导出入口破坏列宽偏好；不把偏好写进业务版本。

## 5. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/device-simulator/` 为根；花括号仅展开列名，不是通配符。仅为本功能改动列出的文件；发现需新增其他文件须回 PM。本次 PM 工作只写本 `spec.md`，角色文档按 STD 的各自权限创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| runtime 模型及版本查询 | `runtime/src/domain/{mod.rs,configuration.rs}`；`runtime/src/services/{mod.rs,queries.rs,versions.rs,layout.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs}`；`runtime/src/app.rs` | `runtime/src/domain/plc_catalog.rs`；`runtime/src/services/catalog_export.rs` |
| Tauri 桥接及原生选择 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/mod.rs`；`src-tauri/{Cargo.toml,Cargo.lock}` | `src-tauri/src/commands/catalog_export.rs` |
| UI 与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/simulator/components/CatalogExportDialog.vue` |
| 测试、用户说明与索引 | `{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/plc_catalog_export.rs`；`tests/plc-catalog-export.test.mjs`；`tests/fixtures/plc-catalog-v1.json` |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后由 Development 创建本 bundle `tasks.md`；交接后由独立 Verification 创建 `checklist.md` |

不改数据库物理 schema、迁移、现有 DS profile、`.env`、设备/网络协议实现及运行权限、不改 DS 其他配置格式、不改 pnpm 依赖/锁、DAA/FF/根 contracts、其他任务或其证据。用户侧文件输出只写用户本次原生明确选择并确认的目录；测试和构建输出只使用自有隔离目录。

## 6. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DS01 | 从含至少两个不同实例、多个 DB、多个 saved revision 和未保存草稿的合成 profile 选择一个 revision，多选生成各自一份 JSON；其版本、配置原字节 SHA、身份及点只来自所选版本；selected/loaded 不同或缺失有提示和显式确认。 |
| DS02 | 两文件分别被 r4 共同格式严格解析，至少含 BOOL、INT、REAL、STRING[n] 和 disabled DB/点；对照该 revision 每点 ID、技术名、类型、偏移、bit、启用、双语和描述完整相等，旧无语言值原样保留，无遗漏、串实例、运行值或模拟规则。 |
| DS03 | 重复 ID/名称/DB、错误类型/bit、STRING 宽度、地址重叠/越界、未确认名称或地址、非法来源、非整数和超预算的启用及禁用点均定位并阻止对应文件，不通过默认值补救；合法另一实例的结果单独报告。 |
| DS04 | 通配地址、无效 IPv4/端口、无法确认的客户端目标及错误 TSAP 被阻断；loopback 告知同机限制；非默认 TSAP 按合同精确保留并提示 DAA 当前不兼容，不能悄悄变默认。 |
| DS05 | 原生目录选择、关闭/取消、同名覆盖拒绝和明确确认、符号链接/目标竞争、只读目录/磁盘写错、并发/重复确认逐一验证；无目标半文件、越目录写入和未经确认覆盖，失败信息正确且用户原文件保留。 |
| DS06 | 读/预览/导出前后比较自有 profile 的配置 payload/source bytes 与 SHA、草稿/版本/selected/loaded、规则及实例状态；除用户指定输出外没有业务写入，也不触发网络连接或实例启停。版本被删/竞争时失败而非换源。 |
| DS07 | 中文和英文可操作，实例和预览表列宽拖拽、横向滚动、切换页面/重启恢复、恢复默认和功能列例外符合项目公共组件；常规操作符合现有 DS 可用性。 |
| DS08 | 原有 S7 创建、保存、版本选择与运行行为回归；真实 macOS arm64 原生 Tauri 文件夹对话框和落盘可验证。纯 Vue/模拟器测试不代替原生交互；其他平台未测如实标记。 |
| DS09 | 保存候选原始 JSON 字节、SHA、输入 revision 和实例对应关系；交 DAA-017 用**该实际 exporter**完成独立闭环。合成格式 fixture 单测不称跨应用联调；DS-003 本身完成单端验证不等于 DAA 已完成。 |
| DS10 | 使用正式交付源码与锁文件，在隔离路径执行相关 Rust/Node 测试、类型检查、前端构建和 native-s7 桥接检查；记录命令、环境、退出码、未跑项及清理。可执行受限语义交给独立 QA 再验。 |
| DS11 | 选旧 revision 的未标记旧值被原样导出，缺双语/描述输出两空语言及空描述；含单侧空、两侧非空、手工点描述和禁用点的版本按实际值导出，语言切换不改变数据或 SHA；错误类型、超字节字段阻断该实例，不能把旧值或注释冒充语言/描述。 |
| DS12 | 仅在两基础已最终验收、本 r3 已精确批准及原生隔离暂停经明确处理后，按 §7 的隔离方案建立唯一自有 DS/DAA `.local` 目录，验证进程/源代码/启动参数/profile 身份与 WebKit 落点；缺失变量、错误目标、重启回落或无安全证明须阻断，不能使用 `.local/dev`。快照与正式候选差异、普通入口未验证项均如实记录。 |
| DS13 | `USER_GUIDE.md` 与 `USER_GUIDE.zh-CN.md` 记录可重新建立合成环境、选择 revision、多选逐实例导出、文件 SHA 与 DAA 手册交接、清理和失败停止的步骤；验证者实际按手册操作后检查仅任务自有资源被回收，未实现或未验证入口不得写成可用。 |

## 7. 验证与 gate、风险和回退

两项双语基础分别完成 STD 最终验收、r4 设计和本 r3 经 Human Owner 精确批准后，Development 才创建 `tasks.md`，先完成实现和自检并给出 developer_handoff；新鲜上下文 Verification 独立创建 checklist，复验精确交付树及结果；之后由 Human Owner 选择是否最终验收。DS-003 与 DAA-017 可分别进行实现自检；跨应用证据必须使用实际 DS-003 候选和 DAA-017 候选，不能共享用户现有 dev 联调 profile。任何运行须仅用自有新合成 profile、隔离输出目录与非特权 loopback；已有用户 DB、真实设备和现场网络不在授权内。测试前记录合成 fixture，结束关闭自有进程并清理无证据依赖的临时资源。

适用验证以实际项目工具链和文件为准：DS `pnpm@11.11.0`、Cargo/Rust，示例命令（路径变量是自有临时目录）为 `cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7`、`node --test tests/plc-catalog-export.test.mjs`、`pnpm exec vue-tsc --noEmit` 及 `pnpm exec vite build --outDir "$RUN_DIR/ui"`；编译输出以 `CARGO_TARGET_DIR` 指向隔离目录。实际依赖离线不可用、命令不适配或原生交互无法执行时如实记录 blocked/not_run，不改锁或安装未批准依赖来假称通过。

若实现发现须修改物理 SQLite/迁移已使用 profile、扩大协议能力或引入超出白名单的文件/依赖，立即停止对应部分，交 PM 修订并另经明确批准。误选地址可能指向真实设备：导出本身不连接，并由使用者确认客户端目标；离线 JSON 也不是物理布局或真实设备验收证明。回退采用旧 DS 程序及停机前独立保全的自有合成 profile；本切片设计不转换 profile 或删除历史，任何用户 profile 的备份、迁移、恢复和现场使用另行批准。

### 隔离、跨应用验证与人工复验（r3 待批准）

1. **先决条件。** DS-004 r2 和 DAA-018 r3 的实施范围已分别批准，但当前均为 `qa_blocked`：前者 QA4 的真实原生及普通入口、后者 QA2 的真实原生及旧普通 native 安全拒绝尚未完成。此前 DAA 受控窗口退出后 CUA 可能重新绑定或启动默认真实 profile，实际影响未知。协调者/Human Owner 须先明确处理并解除 GUI/CUA 暂停，独立 Verification 完成两基础的必需检查，再由 Human Owner 分别最终验收；本方向及合成环境授权不代替这些 gate。本任务实施还须本 r3 自身精确批准。不得重新打开、扫描、复制、清理或回滚疑似真实数据来追证事故。
2. **任务自有目录。** 两应用分别在自身工程目录内新建唯一、原先不存在的 `.local/plc-json-<run-id>/`，各自放独立合成 profile、仅含测试值的 env、隔离构建/日志和临时输出；`<run-id>` 是每次显式替换的唯一值，不是可直接运行的字面路径。绝不使用任一 `.local/dev`、默认目录或真实配置/样本/凭据，绝不复制用户 profile。创建前验证父目录归属、非符号链接、目标不存在且不与现有资源交叉；Mac DAA 新 profile 根按现有指南先在可控父目录预建，不能把预建说成修复底层目录替换竞态。新 SQLite 可运行既有初始建库 DDL，不对已有库执行 DDL/迁移。
3. **env 与重启不可回落。** DAA 每次受控启动显式使用绝对 `DAA_ENV_FILE` 指向 DAA 任务自有可读普通文件，并用绝对 `DAA_PROFILE_DIR` 指向 DAA 任务 profile；路径无 `..` 和已有符号链接。每次重启都经同一受控入口传入完整参数，验证实际进程、应用身份与打开的同一合成 profile/实例 ID；不得经 Dock、名称重绑或无参数自动重启。先检验缺失、错误、失效路径和进程变量时受控入口明确停止、不启动默认 profile；这是对**受控入口**的要求，不能虚称普通产品无参数会拒绝默认路径。单靠启动后查看 UI 不能证明启动前没有写到错误目录。
4. **DS 特有阻塞。** DS 普通 bootstrap 即使进程指定 `DS_PROFILE_DIR`，仍先读取编译期源码根的 `.env`；本任务不得读取真实 `.env`。可评估在 DS 任务根建立不含用户 `.env`、`.local`、私有输入和真实数据的源码快照，在其编译根使用自己的空/合成 env 与绝对任务 profile，以全新任务专属 Cargo target 构建；按实际依赖包含必要的 `shared/tia-import-core` 和 `console-ui`，逐文件比较正式交付候选与快照，并记录锁文件、编译路径、二进制及 profile 身份。快照普通入口证据不能冒称正式工作树普通入口已验证，也不能取代 DS-004 原有 DS4-07 证据。若无法在不读取真实配置的前提下证明正式入口和候选一致，或无法确定重启不回落，保持 blocker 并回 PM，不能启动。
5. **WebKit / CUA 独立门槛。** 独立 SQLite profile 不是 WebKit、应用身份、系统缓存或自动化绑定隔离：DS 用 profile UUID 配置 WebView store，但系统进程/缓存落点仍需验证；DAA 正式默认窗口未按 profile 单独指定 WebKit store。此前唯一 bundle + incognito 也未阻止异常，incognito 不能证明正式列宽跨重启持久化。须在独立 macOS 用户或隔离 macOS 环境、或经证实等价的环境中，证明任务账户对自有 `.local` 有权限且无法触达真实用户配置；明确 App/bundle/进程身份、持久 WebKit store、实际 OS/XPC 数据落点及退出、重开后身份。不得因目录不同、名称相同或 CUA 旧绑定就推定安全；不能证明不会按应用名重新绑定/拉起默认应用时，改用受控人工操作并保持 CUA 禁用。所需平台身份/目录不可安全建立时标记 blocked，不能用临时 incognito 或合成 DOM 冒称原生通过。
6. **受控 S7。** 仅使用自建合成实例及本机 `127.0.0.1` 非特权端口；先核对端口和进程归属，不杀未知进程、不静默换端口。DAA 预先禁止自动采集和上报，只在确认该合成目标与本机 DS listener 身份后显式连接、分组和采集；不访问现场网络、外部服务或真实设备。DAA 的 `DAA_PLC_READ_ALLOWED` 按当前代码是进程变量（缺失默认允许，env 文件中的同名键被忽略）；准备阶段可显式设 false，确需环回采集时须在受控进程中显式许可并重新核验唯一目标。`local-validation` feature 使用 fixture/禁止真实 S7，不能当作真实 loopback 读取证据；DS 原生 `test-automation` 受固定 manifest/scenario 约束，也不能自动代表普通产品入口。
7. **可复验与清理。** 两份用户手册中英文版本各记录本应用侧可复验步骤及相互链接：隔离前提、创建全新任务根和合成数据、每次启动/重启参数及身份核验、DS 多实例逐个导出和 DAA 选同一文件导入/分组/保存/激活/显式采集、每一步可观察结果、已知 blocker 和停止条件。具体产品入口和截图只能在实现且验证后记录，不能把拟议入口写成现成能力。测试结束、必要 DEV/独立 QA 证据已写入各自 bundle 且无进程或后续验证依赖后，先核对任务 marker、实际路径、PID/句柄及所有权，再清理本次两处自有 `.local` 根和可证明属于本次的系统资源；不清理用户、其他任务或归属不明的 profile/WebKit/日志。无法证明归属或退出则停止清理并如实报告；保留任务文档中的非敏感候选标识、源 revision、文件 SHA、验证结果及可重新创建的操作步骤，不保留实际测试数据或伪称清理成功。

## 8. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品或测试。批准后 Development 按实际触达使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及项目治理规则独立检查。任何自检或 QA 通过均不自动授权上线、真实数据库/设备或 Human Owner 最终验收。

## 附录 A：r2 完整原文（含 r1 历史，非活动规格）

r2 SHA-256: ed3c54cc4d67262a4dd1269fa68090863686767c85a10baabaef59c4cdd6a32c

~~~~~~~~~~~~~~~~markdown
Task ID: DS-003
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 设计 r3 获批、DS-004 与 DAA-018 均 STD 最终验收，且 Human Owner 精确批准 DS-003 r2 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 按保存版本及 PLC 实例导出完整 S7 点位 JSON
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; aiis-ics-arch::DAA-017 r2; device-simulator::DS-002 r2
Depends On: aiis-ics-arch::ARCH-PLC-001 r3 设计批准；DS-004 和 DAA-018 各自完成 STD 至 Human Owner 最终验收；DS 与 DAA 的受控端到端验证还依赖 DAA-017 r2 实际导入候选

# DS-003：按 PLC 实例导出点位 JSON

## 1. 状态、目标与边界

**本任务为 draft / r2，尚未获得实施批准。** 2026-11-16 Human Owner 批准 ARCH-PLC-001 r2 设计范围，2026-11-17 要求先完成 DS/DAA 双语点位，再实施导出/导入并保留描述。本修订依 [ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 拟议新合同形成；r3 设计范围已获 Human Owner 批准，DS-004 和 DAA-018 尚未获实施批准，旧 r1 也未获实施批准。必须等 r3 设计获批，DS-004、DAA-018 各自完成 STD 至 Human Owner 最终验收，且本 r2 精确批准，才可启动本任务 Development；下游批准和跨应用验收互不继承。

目标：用户从一个明确的 DS 保存版本选择一个或多个 PLC 实例，确认客户端可达地址，在所选目录为每个实例各导出一份完整 S7 点位 JSON。优先服务 DS→DAA 无需再次导入 DB/UDT 的路径；无论点位启用状态均不静默丢失。DS 导入 JSON、DAA 导出 JSON、FF 适配、正式发布跨运行时公共合同、其他协议和真实 PLC/数据库/现场采用均非本任务范围。不得因本规格启动实现、修改代码或写入现有 profile。

## 2. 来源、选择与用户流程

1. 用户先选择一个确实存在且完整可读的不可变 `saved_revision`；列表中的实例及其 DB/点均来自**该版本**，不能把实例页当下草稿冒充所选版本。显示所选 revision 标识、保存信息和该实例当前 selected / actual_loaded 的真实标识或缺失状态。所选版本与实际 loaded 不同或无法核验时，清晰提示并由用户明确确认；不得称为已模拟成功或用 selected 代替 actual_loaded。未保存编辑、模拟状态/实时值不进入文件。
2. 可多选所选版本里的实例，分别展示 DB、全部点、类型、位置、启停事实和逐项错误。为每个实例显示并由用户填写或明确确认 `connection` 客户端目标：合法 IPv4 单播 host、port 1..65535、rack 0..7、slot 0..31；禁止将通配监听地址当客户端目标。loopback 仅为同机目标，提示跨机器不可直接使用。展示客户端/服务端 TSAP 方向及推导；若导出为非默认 TSAP，明确 DAA 当前不能导入执行，不得省略来伪装兼容。只读取 DS 模拟配置和操作者输入，不发网络包、连接真实 PLC 或启动模拟器。
3. 批量预览逐实例显示数目、来源版本、字段、错误和每份是否可导出；含禁用 DB 和点。名称、地址、源映射/确认、类型、范围或重叠有问题时，阻断该实例并定位 DB/点，不以禁用绕过或改写默认值。其他独立实例可继续，最终逐个报告成功、失败、取消；不能把部分成功表述为全部成功。
4. 通过原生目录选择器显式选目标目录；每实例文件名使用稳定 PLC UUID 加 `.json`，不使用名称、任意输入路径或服务器默认目录。预览所有冲突，覆盖只能由用户对具体目标明确确认；取消不写。目标路径须防止目录穿越、符号链接替换和并发改名绕过确认。每个文件在同目录创建任务自有临时文件，写入完整 bytes 并验证后原子落盘；失败/取消不得留下目标半文件，不删除用户既有文件。提交期间若目标或所选目录状态改变，重新提示或失败，不能覆盖未经确认的对象。重复点击、并发操作和结果未知时返回明确状态，先检查结果再重试；每次预览均绑定 revision、实例、目标和冲突状态，变更使旧确认失效。
5. 导出是配置只读操作：不得保存/发布草稿、修改来源归档或历史、改变 selected/actual_loaded、启动/停止实例、改变规则/权限/初值。可对已保存原始 payload 建立有界只读快照或短期保护，以避免预览到执行期间被版本清理或源发生竞争；如版本不存在或完整性不能核实则该实例失败，不能用其他版本替代。

## 3. 同一候选格式与字段语义

本任务实现 [ARCH-PLC-001 r3 §3–5、§6.1](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 **`aiis.plc_points` / `schema_version: 1`**，不是第二种 DS 专属格式。以下示例逐字复制父规格：其中摘要仅示词法，非真实 payload 哈希。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

- UTF-8 无 BOM，一个 PLC；最多 1 MiB、层级 16、32 DB、4096 点。字段、UUID v4、名称、整数词法、未知字段、连接端点等按父规格严格验证；不能截断或猜测。保存的实际配置 payload 原始字节 SHA-256 填 `export.payload_sha256`，`revision_id` 与该字节必须指向同一个真实 saved revision；生成时间使用项目上海时间工具，RFC 3339 `+08:00`，时间不可用则报错，不能伪造。`origin` 是身份命名空间而非每点作者：对尚无外部绑定的本机 DS 配置，取真实 workspace profile 与 PLC UUID；导出不偷偷重编号。若当前实现存在不可表达或不一致的外部来源，明确阻断而不伪造来源；外部来源导入及其持久化不在本任务。
- 每点均输出 `display_names` 严格对象（`zh-CN` / `en-US` 两个字符串），从所选保存版本取值，旧版本缺字段则两者 `""`；不得从 `name`、另一语言、路径、注释或旧显示名推测。旧 DS `displayName` 如非空按原文放入可选 `display_name`，明确语言未标记，绝不归入双语值。两种语言、旧单条值均按父合同 UTF-8 字节上限检查，任何无效值不截断或换点。
- 每点输出 `description` 字符串：取所选保存版本中 DS-004 提供、用户明确维护的独立可选描述，非空原样输出；旧版本缺失或值为空输出 `""`。手工点与 TIA 点都可填写；不能从旧 displayName、TIA comment、双语名推测。DAA 收到描述和其原有 comment 的处理遵循 DAA-017 r2 的预览与显式确认，不增加 DAA 上报字段。
- 每个 DB、点的 ID、名称、DB 编号/大小、类型、byte/bit、可证实 `source_path` 都来自被选版本的已确认事实；无实际路径时省略，不能从显示名杜撰。预览同时展示两个语言的原值、无语言旧值（如有）和描述；切顶栏语言只改变界面显示，不改变输出。输出所有声明点，包括 disabled 点：DS 的 DB 与 point `source_enabled` 均为实际各自 `enabled`，不是采集组、采集许可或写权限。DS 当前禁用分支若未做布局校验，导出时仍需按合同校验所有点。
- 类型含 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL、STRING[n]（1..254）；BOOL bit 0..7，其他类型禁止 bit；按 S7 存储宽度、ASCII STRING 的 n+2 字节、DB 长度、物理重叠规则逐点验证，不能仅按现有 enabled 集合推算。未知类型、未确认名称/布局、无效 DB、非法 bit、越界、重复标识/技术名、重复 DB 号或不满足合同的 disabled 点均使该实例失败。不得输出模拟初值、规则、现场凭据、文件系统路径或实时值。
- DAA 必须原样能接收这一份候选格式；本任务不生成第二份筛选文件。实际 DS→DAA 受控闭环属于 DAA-017 的跨应用验收，同时由 DS Development/Verification 提供精确 exporter 候选及其产生文件和来源摘要；本任务单独的格式验证不能冒充闭环。

## 4. 技术实施边界（仅供批准后 Development）

DS 当前实例页以草稿为数据源，保存版本读取与原始 payload 的哈希校验在 runtime 配置存储；本任务需通过正式 runtime 服务读取相同 revision 的原始 bytes、解析结果与受保护引用，不能由 UI 拼接点表或将草稿序号当 revision。桥接返回结构化预览/定位错误、版本和每文件结果，不泄露 profile 绝对路径。多次预览/取消需清理本任务资源，不引入长期后台任务。

Tauri 当前没有文件夹选择能力依赖。拟在 `src-tauri/Cargo.toml` 增加精确 `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，在 Rust 端注册原生对话框并选目录；仅更新 DS 桌面 Cargo.lock 的该依赖必要传递闭包，不升级其他依赖或添加 npm 包。不提供任意前端文件系统路径/宽泛 FS capability：由后端保存本次原生选择的短期、不可猜测授权引用，确认绑定路径和实例，结束即失效。所选 crate 版本与本机缓存的 manifest 兼容性只是 PM 源码检查，编译、权限、平台对话框及传递依赖仍需 Development 真实验证；如需其他依赖、系统权限、清单文件或扩大文件范围，停止并回 PM 修订，而非悄悄放宽。项目普通入口仍为 `pnpm tauri dev`。

中文/英文文案新增成对 locale；实例/预览表格沿用共享表格列宽与本机偏好工具：普通列可拖拽、设置最小宽度、横向滚动、按稳定字段键隔离并恢复默认，功能列允许固定。已存在表格不能因为导出入口破坏列宽偏好；不把偏好写进业务版本。

## 5. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/device-simulator/` 为根；花括号仅展开列名，不是通配符。仅为本功能改动列出的文件；发现需新增其他文件须回 PM。本次 PM 工作只写本 `spec.md`，角色文档按 STD 的各自权限创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| runtime 模型及版本查询 | `runtime/src/domain/{mod.rs,configuration.rs}`；`runtime/src/services/{mod.rs,queries.rs,versions.rs,layout.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs}`；`runtime/src/app.rs` | `runtime/src/domain/plc_catalog.rs`；`runtime/src/services/catalog_export.rs` |
| Tauri 桥接及原生选择 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/mod.rs`；`src-tauri/{Cargo.toml,Cargo.lock}` | `src-tauri/src/commands/catalog_export.rs` |
| UI 与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/simulator/components/CatalogExportDialog.vue` |
| 测试、用户说明与索引 | `{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/plc_catalog_export.rs`；`tests/plc-catalog-export.test.mjs`；`tests/fixtures/plc-catalog-v1.json` |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后由 Development 创建本 bundle `tasks.md`；交接后由独立 Verification 创建 `checklist.md` |

不改数据库物理 schema、迁移、现有 DS profile、`.env`、设备/网络协议实现及运行权限、不改 DS 其他配置格式、不改 pnpm 依赖/锁、DAA/FF/根 contracts、其他任务或其证据。用户侧文件输出只写用户本次原生明确选择并确认的目录；测试和构建输出只使用自有隔离目录。

## 6. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DS01 | 从含至少两个不同实例、多个 DB、多个 saved revision 和未保存草稿的合成 profile 选择一个 revision，多选生成各自一份 JSON；其版本、配置原字节 SHA、身份及点只来自所选版本；selected/loaded 不同或缺失有提示和显式确认。 |
| DS02 | 两文件分别被 r3 格式严格解析，至少含 BOOL、INT、REAL、STRING[n] 和 disabled DB/点；对照该 revision 每点 ID、技术名、类型、偏移、bit、启用、双语和描述完整相等，旧无语言值原样保留，无遗漏、串实例、运行值或模拟规则。 |
| DS03 | 重复 ID/名称/DB、错误类型/bit、STRING 宽度、地址重叠/越界、未确认名称或地址、非法来源、非整数和超预算的启用及禁用点均定位并阻止对应文件，不通过默认值补救；合法另一实例的结果单独报告。 |
| DS04 | 通配地址、无效 IPv4/端口、无法确认的客户端目标及错误 TSAP 被阻断；loopback 告知同机限制；非默认 TSAP 按合同精确保留并提示 DAA 当前不兼容，不能悄悄变默认。 |
| DS05 | 原生目录选择、关闭/取消、同名覆盖拒绝和明确确认、符号链接/目标竞争、只读目录/磁盘写错、并发/重复确认逐一验证；无目标半文件、越目录写入和未经确认覆盖，失败信息正确且用户原文件保留。 |
| DS06 | 读/预览/导出前后比较自有 profile 的配置 payload/source bytes 与 SHA、草稿/版本/selected/loaded、规则及实例状态；除用户指定输出外没有业务写入，也不触发网络连接或实例启停。版本被删/竞争时失败而非换源。 |
| DS07 | 中文和英文可操作，实例和预览表列宽拖拽、横向滚动、切换页面/重启恢复、恢复默认和功能列例外符合项目公共组件；常规操作符合现有 DS 可用性。 |
| DS08 | 原有 S7 创建、保存、版本选择与运行行为回归；真实 macOS arm64 原生 Tauri 文件夹对话框和落盘可验证。纯 Vue/模拟器测试不代替原生交互；其他平台未测如实标记。 |
| DS09 | 保存候选原始 JSON 字节、SHA、输入 revision 和实例对应关系；交 DAA-017 用**该实际 exporter**完成独立闭环。合成格式 fixture 单测不称跨应用联调；DS-003 本身完成单端验证不等于 DAA 已完成。 |
| DS10 | 使用正式交付源码与锁文件，在隔离路径执行相关 Rust/Node 测试、类型检查、前端构建和 native-s7 桥接检查；记录命令、环境、退出码、未跑项及清理。可执行受限语义交给独立 QA 再验。 |
| DS11 | 选旧 revision 的未标记旧值被原样导出，缺双语/描述输出两空语言及空描述；含单侧空、两侧非空、手工点描述和禁用点的版本按实际值导出，语言切换不改变数据或 SHA；错误类型、超字节字段阻断该实例，不能把旧值或注释冒充语言/描述。 |

## 7. 验证与 gate、风险和回退

两项双语基础分别完成 STD 最终验收、r3 设计和本 r2 经 Human Owner 精确批准后，Development 才创建 `tasks.md`，先完成实现和自检并给出 developer_handoff；新鲜上下文 Verification 独立创建 checklist，复验精确交付树及结果；之后由 Human Owner 选择是否最终验收。DS-003 与 DAA-017 可分别进行实现自检；跨应用证据必须使用实际 DS-003 候选和 DAA-017 候选，不能共享用户现有 dev 联调 profile。任何运行须仅用自有新合成 profile、隔离输出目录与非特权 loopback；已有用户 DB、真实设备和现场网络不在授权内。测试前记录合成 fixture，结束关闭自有进程并清理无证据依赖的临时资源。

适用验证以实际项目工具链和文件为准：DS `pnpm@11.11.0`、Cargo/Rust，示例命令（路径变量是自有临时目录）为 `cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7`、`node --test tests/plc-catalog-export.test.mjs`、`pnpm exec vue-tsc --noEmit` 及 `pnpm exec vite build --outDir "$RUN_DIR/ui"`；编译输出以 `CARGO_TARGET_DIR` 指向隔离目录。实际依赖离线不可用、命令不适配或原生交互无法执行时如实记录 blocked/not_run，不改锁或安装未批准依赖来假称通过。

若实现发现须修改物理 SQLite/迁移已使用 profile、扩大协议能力或引入超出白名单的文件/依赖，立即停止对应部分，交 PM 修订并另经明确批准。误选地址可能指向真实设备：导出本身不连接，并由使用者确认客户端目标；离线 JSON 也不是物理布局或真实设备验收证明。回退采用旧 DS 程序及停机前独立保全的自有合成 profile；本切片设计不转换 profile 或删除历史，任何用户 profile 的备份、迁移、恢复和现场使用另行批准。

## 8. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品或测试。批准后 Development 按实际触达使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及项目治理规则独立检查。任何自检或 QA 通过均不自动授权上线、真实数据库/设备或 Human Owner 最终验收。

## 附录 A：r1 原始未批准草案（历史）

原始 SHA256: `b90e1701f746fc941e79d97eeb17fe837829d9377321a67fd3237aff3c5bac87`；围栏内原字节含末尾换行，供追溯，不是当前实施范围。

~~~~~~~~markdown
Task ID: DS-003
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 批准精确 DS-003 r1 -> Development tasks.md / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 按保存版本及 PLC 实例导出完整 S7 点位 JSON
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r2; aiis-ics-arch::DAA-017 r1; device-simulator::DS-002 r2
Depends On: aiis-ics-arch::ARCH-PLC-001 r2 设计范围；DS 与 DAA 的受控端到端验证还依赖 DAA-017 的实际导入候选

# DS-003：按 PLC 实例导出点位 JSON

## 1. 状态、目标与边界

**本任务为 draft / r1，尚未获得实施批准。** Human Owner 于 2026-11-16（Asia/Shanghai）批准 [ARCH-PLC-001 r2](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的设计范围，并要求优先拆分 DS 导出和 DAA 导入、暂不改代码。该批准不代替对本任务精确 r1、Development、独立 QA、最终验收或现场操作的批准。本文只提出 DS 一侧可审阅的实施切片；DAA-017 是另一独立 owner、独立验收链的任务。

目标：用户从一个明确的 DS 保存版本选择一个或多个 PLC 实例，确认客户端可达地址，在所选目录为每个实例各导出一份完整 S7 点位 JSON。优先服务 DS→DAA 无需再次导入 DB/UDT 的路径；无论点位启用状态均不静默丢失。DS 导入 JSON、DAA 导出 JSON、FF 适配、正式发布跨运行时公共合同、其他协议和真实 PLC/数据库/现场采用均非本任务范围。不得因本规格启动实现、修改代码或写入现有 profile。

## 2. 来源、选择与用户流程

1. 用户先选择一个确实存在且完整可读的不可变 `saved_revision`；列表中的实例及其 DB/点均来自**该版本**，不能把实例页当下草稿冒充所选版本。显示所选 revision 标识、保存信息和该实例当前 selected / actual_loaded 的真实标识或缺失状态。所选版本与实际 loaded 不同或无法核验时，清晰提示并由用户明确确认；不得称为已模拟成功或用 selected 代替 actual_loaded。未保存编辑、模拟状态/实时值不进入文件。
2. 可多选所选版本里的实例，分别展示 DB、全部点、类型、位置、启停事实和逐项错误。为每个实例显示并由用户填写或明确确认 `connection` 客户端目标：合法 IPv4 单播 host、port 1..65535、rack 0..7、slot 0..31；禁止将通配监听地址当客户端目标。loopback 仅为同机目标，提示跨机器不可直接使用。展示客户端/服务端 TSAP 方向及推导；若导出为非默认 TSAP，明确 DAA 当前不能导入执行，不得省略来伪装兼容。只读取 DS 模拟配置和操作者输入，不发网络包、连接真实 PLC 或启动模拟器。
3. 批量预览逐实例显示数目、来源版本、字段、错误和每份是否可导出；含禁用 DB 和点。名称、地址、源映射/确认、类型、范围或重叠有问题时，阻断该实例并定位 DB/点，不以禁用绕过或改写默认值。其他独立实例可继续，最终逐个报告成功、失败、取消；不能把部分成功表述为全部成功。
4. 通过原生目录选择器显式选目标目录；每实例文件名使用稳定 PLC UUID 加 `.json`，不使用名称、任意输入路径或服务器默认目录。预览所有冲突，覆盖只能由用户对具体目标明确确认；取消不写。目标路径须防止目录穿越、符号链接替换和并发改名绕过确认。每个文件在同目录创建任务自有临时文件，写入完整 bytes 并验证后原子落盘；失败/取消不得留下目标半文件，不删除用户既有文件。提交期间若目标或所选目录状态改变，重新提示或失败，不能覆盖未经确认的对象。重复点击、并发操作和结果未知时返回明确状态，先检查结果再重试；每次预览均绑定 revision、实例、目标和冲突状态，变更使旧确认失效。
5. 导出是配置只读操作：不得保存/发布草稿、修改来源归档或历史、改变 selected/actual_loaded、启动/停止实例、改变规则/权限/初值。可对已保存原始 payload 建立有界只读快照或短期保护，以避免预览到执行期间被版本清理或源发生竞争；如版本不存在或完整性不能核实则该实例失败，不能用其他版本替代。

## 3. 同一候选格式与字段语义

本任务实现 [ARCH-PLC-001 r2 §3–5、§6.1](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 **`aiis.plc_points` / `schema_version: 1`**，不是第二种 DS 专属格式。以下示例逐字复制父规格：其中摘要仅示词法，非真实 payload 哈希。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

- UTF-8 无 BOM，一个 PLC；最多 1 MiB、层级 16、32 DB、4096 点。字段、UUID v4、名称、整数词法、未知字段、连接端点等按父规格严格验证；不能截断或猜测。保存的实际配置 payload 原始字节 SHA-256 填 `export.payload_sha256`，`revision_id` 与该字节必须指向同一个真实 saved revision；生成时间使用项目上海时间工具，RFC 3339 `+08:00`，时间不可用则报错，不能伪造。`origin` 是身份命名空间而非每点作者：对尚无外部绑定的本机 DS 配置，取真实 workspace profile 与 PLC UUID；导出不偷偷重编号。若当前实现存在不可表达或不一致的外部来源，明确阻断而不伪造来源；外部来源导入及其持久化不在本任务。
- 每个 DB、点的 ID、名称、DB 编号/大小、类型、byte/bit、可证实 `source_path` 都来自被选版本的已确认事实；无实际路径时省略，不能从显示名杜撰。输出所有声明点，包括 disabled 点：DS 的 DB 与 point `source_enabled` 均为实际各自 `enabled`，不是采集组、采集许可或写权限。DS 当前禁用分支若未做布局校验，导出时仍需按合同校验所有点。
- 类型含 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL、STRING[n]（1..254）；BOOL bit 0..7，其他类型禁止 bit；按 S7 存储宽度、ASCII STRING 的 n+2 字节、DB 长度、物理重叠规则逐点验证，不能仅按现有 enabled 集合推算。未知类型、未确认名称/布局、无效 DB、非法 bit、越界、重复标识/技术名、重复 DB 号或不满足合同的 disabled 点均使该实例失败。不得输出模拟初值、规则、现场凭据、文件系统路径或实时值。
- DAA 必须原样能接收这一份候选格式；本任务不生成第二份筛选文件。实际 DS→DAA 受控闭环属于 DAA-017 的跨应用验收，同时由 DS Development/Verification 提供精确 exporter 候选及其产生文件和来源摘要；本任务单独的格式验证不能冒充闭环。

## 4. 技术实施边界（仅供批准后 Development）

DS 当前实例页以草稿为数据源，保存版本读取与原始 payload 的哈希校验在 runtime 配置存储；本任务需通过正式 runtime 服务读取相同 revision 的原始 bytes、解析结果与受保护引用，不能由 UI 拼接点表或将草稿序号当 revision。桥接返回结构化预览/定位错误、版本和每文件结果，不泄露 profile 绝对路径。多次预览/取消需清理本任务资源，不引入长期后台任务。

Tauri 当前没有文件夹选择能力依赖。拟在 `src-tauri/Cargo.toml` 增加精确 `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，在 Rust 端注册原生对话框并选目录；仅更新 DS 桌面 Cargo.lock 的该依赖必要传递闭包，不升级其他依赖或添加 npm 包。不提供任意前端文件系统路径/宽泛 FS capability：由后端保存本次原生选择的短期、不可猜测授权引用，确认绑定路径和实例，结束即失效。所选 crate 版本与本机缓存的 manifest 兼容性只是 PM 源码检查，编译、权限、平台对话框及传递依赖仍需 Development 真实验证；如需其他依赖、系统权限、清单文件或扩大文件范围，停止并回 PM 修订，而非悄悄放宽。项目普通入口仍为 `pnpm tauri dev`。

中文/英文文案新增成对 locale；实例/预览表格沿用共享表格列宽与本机偏好工具：普通列可拖拽、设置最小宽度、横向滚动、按稳定字段键隔离并恢复默认，功能列允许固定。已存在表格不能因为导出入口破坏列宽偏好；不把偏好写进业务版本。

## 5. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/device-simulator/` 为根；花括号仅展开列名，不是通配符。仅为本功能改动列出的文件；发现需新增其他文件须回 PM。本次 PM 工作只写本 `spec.md`，角色文档按 STD 的各自权限创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| runtime 模型及版本查询 | `runtime/src/domain/{mod.rs,configuration.rs}`；`runtime/src/services/{mod.rs,queries.rs,versions.rs,layout.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs}`；`runtime/src/app.rs` | `runtime/src/domain/plc_catalog.rs`；`runtime/src/services/catalog_export.rs` |
| Tauri 桥接及原生选择 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/mod.rs`；`src-tauri/{Cargo.toml,Cargo.lock}` | `src-tauri/src/commands/catalog_export.rs` |
| UI 与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/simulator/components/CatalogExportDialog.vue` |
| 测试、用户说明与索引 | `{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/plc_catalog_export.rs`；`tests/plc-catalog-export.test.mjs`；`tests/fixtures/plc-catalog-v1.json` |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后由 Development 创建本 bundle `tasks.md`；交接后由独立 Verification 创建 `checklist.md` |

不改数据库物理 schema、迁移、现有 DS profile、`.env`、设备/网络协议实现及运行权限、不改 DS 其他配置格式、不改 pnpm 依赖/锁、DAA/FF/根 contracts、其他任务或其证据。用户侧文件输出只写用户本次原生明确选择并确认的目录；测试和构建输出只使用自有隔离目录。

## 6. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DS01 | 从含至少两个不同实例、多个 DB、多个 saved revision 和未保存草稿的合成 profile 选择一个 revision，多选生成各自一份 JSON；其版本、配置原字节 SHA、身份及点只来自所选版本；selected/loaded 不同或缺失有提示和显式确认。 |
| DS02 | 两文件分别被父格式严格解析，至少含 BOOL、INT、REAL、STRING[n] 和 disabled DB/点；对照该 revision 每点 ID、名称、类型、偏移、bit 及启用值完整相等，无遗漏、串实例、运行值或模拟规则。 |
| DS03 | 重复 ID/名称/DB、错误类型/bit、STRING 宽度、地址重叠/越界、未确认名称或地址、非法来源、非整数和超预算的启用及禁用点均定位并阻止对应文件，不通过默认值补救；合法另一实例的结果单独报告。 |
| DS04 | 通配地址、无效 IPv4/端口、无法确认的客户端目标及错误 TSAP 被阻断；loopback 告知同机限制；非默认 TSAP 按合同精确保留并提示 DAA 当前不兼容，不能悄悄变默认。 |
| DS05 | 原生目录选择、关闭/取消、同名覆盖拒绝和明确确认、符号链接/目标竞争、只读目录/磁盘写错、并发/重复确认逐一验证；无目标半文件、越目录写入和未经确认覆盖，失败信息正确且用户原文件保留。 |
| DS06 | 读/预览/导出前后比较自有 profile 的配置 payload/source bytes 与 SHA、草稿/版本/selected/loaded、规则及实例状态；除用户指定输出外没有业务写入，也不触发网络连接或实例启停。版本被删/竞争时失败而非换源。 |
| DS07 | 中文和英文可操作，实例和预览表列宽拖拽、横向滚动、切换页面/重启恢复、恢复默认和功能列例外符合项目公共组件；常规操作符合现有 DS 可用性。 |
| DS08 | 原有 S7 创建、保存、版本选择与运行行为回归；真实 macOS arm64 原生 Tauri 文件夹对话框和落盘可验证。纯 Vue/模拟器测试不代替原生交互；其他平台未测如实标记。 |
| DS09 | 保存候选原始 JSON 字节、SHA、输入 revision 和实例对应关系；交 DAA-017 用**该实际 exporter**完成独立闭环。合成格式 fixture 单测不称跨应用联调；DS-003 本身完成单端验证不等于 DAA 已完成。 |
| DS10 | 使用正式交付源码与锁文件，在隔离路径执行相关 Rust/Node 测试、类型检查、前端构建和 native-s7 桥接检查；记录命令、环境、退出码、未跑项及清理。可执行受限语义交给独立 QA 再验。 |

## 7. 验证与 gate、风险和回退

Development 在 Human Owner 精确批准本 r1 后创建 `tasks.md`，先完成实现和自检并给出 developer_handoff；新鲜上下文 Verification 独立创建 checklist，复验精确交付树及结果；之后由 Human Owner 选择是否最终验收。DS-003 与 DAA-017 可分别进行实现自检；跨应用证据必须使用实际 DS-003 候选和 DAA-017 候选，不能共享用户现有 dev 联调 profile。任何运行须仅用自有新合成 profile、隔离输出目录与非特权 loopback；已有用户 DB、真实设备和现场网络不在授权内。测试前记录合成 fixture，结束关闭自有进程并清理无证据依赖的临时资源。

适用验证以实际项目工具链和文件为准：DS `pnpm@11.11.0`、Cargo/Rust，示例命令（路径变量是自有临时目录）为 `cargo test --manifest-path runtime/Cargo.toml --locked --offline --test plc_catalog_export`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7`、`node --test tests/plc-catalog-export.test.mjs`、`pnpm exec vue-tsc --noEmit` 及 `pnpm exec vite build --outDir "$RUN_DIR/ui"`；编译输出以 `CARGO_TARGET_DIR` 指向隔离目录。实际依赖离线不可用、命令不适配或原生交互无法执行时如实记录 blocked/not_run，不改锁或安装未批准依赖来假称通过。

若实现发现须修改物理 SQLite/迁移已使用 profile、扩大协议能力或引入超出白名单的文件/依赖，立即停止对应部分，交 PM 修订并另经明确批准。误选地址可能指向真实设备：导出本身不连接，并由使用者确认客户端目标；离线 JSON 也不是物理布局或真实设备验收证明。回退采用旧 DS 程序及停机前独立保全的自有合成 profile；本切片设计不转换 profile 或删除历史，任何用户 profile 的备份、迁移、恢复和现场使用另行批准。

## 8. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品或测试。批准后 Development 按实际触达使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及项目治理规则独立检查。任何自检或 QA 通过均不自动授权上线、真实数据库/设备或 Human Owner 最终验收。
~~~~~~~~
~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
