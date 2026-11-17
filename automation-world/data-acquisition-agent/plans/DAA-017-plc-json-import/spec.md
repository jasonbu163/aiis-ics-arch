Task ID: DAA-017
Revision: r5
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DAA-017 r5 -> Development 接续 r4 已有工作 -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 将逐 PLC 完整 S7 点位 JSON 作为可追溯目录来源导入 DAA 草稿
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r5; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: ARCH-PLC-001 r5 和 r4 下游时序衔接已批准；本任务 r5 已获 Human Owner 精确实施批准；跨应用验收依赖 DS-003 r5 实际导出候选

# DAA-017 r5：按 PLC 导入完整点位 JSON

## 1. 状态、目标与范围

2026-11-17（Asia/Shanghai），Human Owner 反馈已在 DS、DAA 各自的 .local/dev 手工测试中英切换及 display_name，结果没问题；该反馈是用户手工观察，不等于独立 QA 通过或最终验收，两基础任务当前仍为 qa_blocked。用户明确授权后续 JSON 互通直接使用各应用各自的 .local/dev，无需另建 profile；环境授权与实施批准为不同事实；此前 r4 已获精确实施范围批准，本 r5 也已另获精确批准。

**本 r5 实施范围已获 Human Owner 精确批准。** r4 开发中发现现有命名预览服务文件不在本任务白名单，无法按目录真实地址保留既有双语编辑。本 r5 仅补足该文件及直接对应验收，r4 全文与批准记录封存在附录；Development 可按本 r5 接续。DS-004 r2、DAA-018 r3 原独立 QA 历史及当前 qa_blocked 不变。

目标：用户选择一份 DS 导出的 PLC 点位 JSON，预览确认后仅新建一台 DAA PLC，将完整目录及来源写入草稿；无需再次提供 .db / .udt，经分组、启用、保存和显式激活后可受控采集。已有来源、PLC/DB/点身份冲突及同文件重导均拒绝，不修改既有 PLC；合并、差异更新及点位覆盖移后。

本切片只实现 DAA 输入、来源完整性和现有编辑/激活兼容。DS 导入、DAA 导出、本地新增点生成 `daa.catalog_snapshot`、FF 适配、正式发布公共跨运行时合同、其他协议、DDL、真实 profile/数据库迁移和现场采用另立范围；不得将父设计批准视为这些实施批准。

## 2. 同一输入合同与严格验证

输入只接受 [ARCH-PLC-001 r5](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 共同的 aiis.plc_points、整数 schema_version 1 且 export.producer 为 device_simulator 的文件：每文件一台 PLC、至少一个 DB 及完整点集。其他 producer 的导入以后另定，不另造 DS 专属子格式。以下示例逐字复制父规格。

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

1. 从用户选择的文件读取并计算**原始字节** SHA-256；严格 UTF-8 无 BOM，大小上限 1 MiB、层级 16、至多 32 DB / 4096 点；拒绝重复 key、未知字段、错误版本、非整数字面量、null/隐式转换、非法 UUID v4、重复/跨类别 ID、名字重复及其他父合同负例。对所有点和禁用点同等检查物理范围、类型宽度、BOOL bit 与重叠，包括 `STRING[n]` n=1..254、ASCII 及 n+2 字节。未知类型或任何坏点使整台导入失败，不跳过、不更名、不推算偏移。`export.payload_sha256` 是导出方声明的配置原字节摘要，不能拿输入 JSON 的摘要冒充或宣称已验证到源配置；本地保存输入原字节及自己的摘要。
2. 本期只接收 DS producer，DB 和点的 source_enabled 均必填布尔值。源值在归档原文中保留并展示；新 PLC 和点默认不启用、不分组，不能将源值当作 DAA 采集许可。
3. display_names 缺省时新点两值为空；存在时必须含 zh-CN、en-US 两字符串，各至多 256 UTF-8 字节，允许空串但非法类型、null、缺键或多余键拒绝。确认后按本地点 ID 保存，不从其他字段推测。可选 display_name 独立保存为语言未标记值，原文件及字段存在性一并归档。
4. description 缺省或空时新点 comment 为空；非空值经确认原样写入 comment，最多 500 UTF-8 字节。原始文件保留字段是否存在，description、comment 和显示名互不冒充，不新增上报字段。
5. `connection` 是客户端目标，预览并要求用户明确核对/确认，可在确认前编辑目标；仅允许规范 IPv4 单播、合法 port/rack/slot，保留项目的端点唯一和 PLC 数量等校验。`0.0.0.0`、非法地址和非默认 TSAP（DAA 当前没有自定义 TSAP 模型）明确阻断；loopback 提示仅同机有效。不得试连以测试地址或自动连接真实 PLC。来源输出摘要不证明设备布局、设备许可、文件真实性或物理可达性。

## 3. 新建 PLC 与原子提交

选择一个 DS JSON，仅预览新建 PLC，不提供选择已有 PLC、合并或覆盖入口。预览来源、SHA、目标连接、所有 DB/点、双语、旧单条名称和描述。确认前不写；PLC、DB、点沿用文件 UUID。任一 UUID 在本地已使用、相同 origin 已存在或同文件重导时，明确拒绝整份，不改 ID，不猜测身份。

确认绑定文件 SHA、目标连接及当前草稿 ETag，变化或并发使预览失效。成功时一次提交新 PLC、目录原文、绑定和草稿；取消、冲突或已知提交前失败不写，结果未知先读取草稿和来源，不盲重试。其他 PLC、活动配置、历史及上报身份不受影响。

新 PLC 和点默认不采集，用户在新 PLC 下设置组、周期和点启用，保存后显式激活并连接。目录点集、技术名、地址及类型本期不做本地覆盖；双语和 comment 按现有流程维护。已有 PLC 匹配、三方比较、差异重导及覆盖均为后续。

### r5：沿用命名预览的目录点编辑

现有点位编辑将完整名称、地址、双语、comment、启用及分组送入既有命名预览；服务当前只认可 manual / inferred 地址，因此会拒绝已确认的 catalog 地址。r5 在已有预览服务中，仅对经过真实目录绑定、原文 SHA、PLC/DB/点成员、类型和地址验证的目录点接受其原样 catalog 地址，不伪称人工或推算来源，也不能对无有效绑定的 catalog 放行。

显示名、comment、启用和分组可走现有预览确认；界面即使原样提交技术名及完整地址对象也须接受。技术名、点集、类型及地址（含 offset、bit、confirmed、origin、reason）的实际变更或清空仍明确拒绝，目录点不能通过批量名称生成被改名。原始目录及历史不写，原 DB/UDT 流程不变。沿用原 inputDigest、previewToken、有效期、ETag 重验和一次 CAS；伪造、篡改、过期、并发、取消或失败不得产生部分点编辑，不绕开既有校验或创建第二次保存。

## 4. 目录来源与可验证配置

首次导入将所选原始 JSON 与 SHA 保存为新 PLC 的真实 catalog SourceDocument；多个 DB 共用 source_id，逐 DB 绑定原 DB 和点 ID。优先在 schema version 1 可选 catalogBindings 保存 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和完整点身份对应；本期同身份沿用，不设 localOverride 或三方差异元数据。

目录分支重验原文和 SHA、origin、成员、类型、地址、宽度、BOOL bit、越界及重叠；两端点集一一对应，伪造、缺失、重复或跨 PLC 绑定拒绝。Db.complete 仅表示目录完整，tree 可为空但不伪造 TIA 树或 DB/UDT；原 DB/UDT 分支的 source_id、tree、leaf_matches 和地址校验不变。

确认后目录地址可标记 confirmed、origin=catalog 并记明依据；普通保存不可伪造绑定或覆盖目录点集、技术名、地址和类型。采集分组、周期及启用仍按既有规则。若无法无原 DB/UDT 地保存、激活及采集，停止回 PM；不改双库 DDL、不迁移用户 profile。旧版原生兼容未验证，不声称通过。

## 5. 历史样本和事实契约保护

双语与未标记显示名不进入 Point、PointFact.definition 或 name/comment/value；既有上报合同和程序名不变。目录身份不替代 DAA 本地 PLC、采样或上报身份；不改用户旧配置、样本、队列和回执。新目录样本经原事实校验器并用模拟 v2 transport 捕获正文，确认中文及英文显示名不在正文且原字段语义不变，不发真实网络请求。父设计和 DAA-018 r3 对既有 v2 各路径及旧 v1 test-only 的原有要求与结果独立保留；本切片不重新启用旧 v1、不裁剪上下文或改写历史，也不能声称未验证的旧路径通过。

## 6. 已批准的 Development 允许文件

本 r5 已获精确批准；相对已批准 r4 唯一新增的现有文件为 src-tauri/src/services/local_point_naming.rs。路径均以 automation-world/data-acquisition-agent/ 为根；花括号仅展开所列文件；下列文件仅限首次新建 PLC、目录绑定、必要采集兼容和相关验证；不得用本白名单实现已有 PLC 匹配、重导差异合并或点位覆盖。需要其他文件先回 PM。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 模型、来源校验 | `src-tauri/src/domain/{mod.rs,local_configuration.rs}`；`src-tauri/src/services/{mod.rs,local_configuration.rs,local_supervisor.rs,local_activation.rs,local_point_naming.rs}` | `src-tauri/src/domain/plc_catalog.rs`；`src-tauri/src/services/catalog_import.rs` |
| 本地存储与桌面桥 | `src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；`src-tauri/src/commands/local_acquisition.rs`；`src-tauri/src/lib.rs` | `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` |
| UI 与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/components/SourceImportPanel.vue`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/plc/components/CatalogImportDialog.vue` |
| 回归和说明 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`（仅相关回归需要时）；`src-tauri/src/services/local_delivery_tests.rs`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `tests/plc-catalog-import.test.mjs`；`tests/fixtures/plc-catalog-v1.json`；`CODE_INDEX.md`（实际结构发生变化时按仓库契约新建） |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后 Development 创建本 bundle `tasks.md`；交接后独立 Verification 创建 `checklist.md` |

禁止修改 schema.rs、迁移/DDL、依赖锁、.env、原始 DB/UDT、DS/FF/backend 源码、根 contracts 或其他任务。已授权通过 DAA 应用在核对后的 .local/dev 仅新增本任务测试 PLC、来源和必要草稿/版本；不直接编辑数据库，不覆盖既有 PLC、配置内容、样本、队列或历史。真实网络 POST、现场设备及其他数据库不在范围；新文案中英文成对。

## 7. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DA01 | 接受共同格式且 producer 为 device_simulator 的单 PLC 文件；非法版本、字段、编码、类型、ID、容量或点集拒绝且不写，其他 producer 不在本期。 |
| DA02 | BOOL、INT、REAL、STRING 与停用点完整导入，核对 ID、名称、类型、地址和双语；DS 的 DB 与点 source_enabled 必填但不自动采集。 |
| DA03 | BOOL bit、非 BOOL bit、非法 STRING 长度、越界、物理重叠、无效名称/类型和禁用点错误均阻断整台；客户端地址/端口与 TSAP、同机 loopback 提示及不连接行为明确可验。 |
| DA04 | 一个 PLC 多 DB 引用同一真实目录 source，source_id、原文 SHA、origin、DB/点映射全链一致；伪造 source、错 SHA/DB/点/类型/地址、重复或跨 PLC 引用均无法保存或激活。旧 DB/UDT 完整树、leaf_matches、UDT 及源校验正反例行为不变，目录 UI 不显示伪造 TIA 树。 |
| DA05 | 首次新建沿用 PLC、DB、点 UUID；任一身份已占用、origin 已存在或同文件重导时明确拒绝，原草稿、ETag 和来源不变。 |
| DA06 | 目录点集、技术名、地址及类型覆盖明确拒绝；新 PLC 的组、周期和启用可设置并激活。 |
| DA07 | 预览取消、更换文件或端点、过期预览、草稿并发变化及提交失败均无部分来源、映射或写入；重复来源明确拒绝，未知结果先重读、不盲目重试。 |
| DA08 | 新 PLC 和点默认不采集；用户显式设置组、周期、启用并保存时，既有 PLC 内容不变、active 不自动改变；显式激活产生正常新 active revision，但不得改变既有 PLC 及上报设定或触发其设备动作。 |
| DA09 | 在核对后的 DAA .local/dev 仅新增测试 PLC 和目录，双库物理 schema 不改，既有 PLC、配置历史、样本和回执不覆盖；正常运行审计和新 revision 如实记录，不声称整库零写。迁移或 DDL 另批；未验证旧版兼容不得声称通过。 |
| DA10 | 新导入目录的实际本地样本通过既有事实校验；以中文、英文不同 sentinel 捕获该样本模拟 v2 正文，验证程序 name/value 等原字段语义不变且不含显示名，未发真实 POST。旧 v1 和旧 v2 各路径按 DAA-018 自身证据如实记录。 |
| DA11 | 使用实际 DS-003 候选对受控 DS 保存版本导出的原文件（记录候选、revision、SHA），在已核对的 DAA .local/dev 新建测试 PLC 导入，无需 .db/.udt；显式分组、启用、保存和激活后，仅连接自有 loopback DS S7，读取 BOOL、INT、REAL 并核对身份、地址、值与质量，停用点仍保留。不得触发既有 PLC 或真实上报；fixture 不能替代闭环。 |
| DA12 | 针对实际交付候选运行相关 Rust/Node 检查及项目构建，记录真实结果；按用户已授权的合成目标验证实际导入操作。Windows、虚拟机及其他未测平台不作为通过前置。 |
| DA13 | 新点中文、英文、单侧空及无语言单条按合同保留，顶栏切换不改配置，description 和程序 name 不被显示名代替。 |
| DA14 | 新点 description 非空经确认写入 comment；缺失或空串显示为空、原文件字段存在性保留；重导冲突和覆盖不在本期。 |
| DA15 | 核对 DAA .local/dev、进程与新测试 PLC 身份；目标不明或可能触及既有数据/设备时停止。只连接自有 DS loopback，fixture 不代替真实读取。 |
| DA16 | 两份中英文 USER_GUIDE 记录核对 DAA .local/dev、导入 DS 实际文件、分组/保存/激活/显式采集、核对值及仅清理自有对象的步骤；未实现或未验证入口不能冒称可用。 |

| DA17 | 有效 catalog 点通过原命名预览和一次确认修改双语、comment、启用或分组；原样提交技术名和完整地址可用，原来源/SHA、技术名及地址保持。无有效目录绑定、伪造 token/摘要、过期或并发 ETag、修改/清空技术名或地址及对目录点批量生成名称均明确拒绝且不产生部分写入；原 DB/UDT 的预览确认行为不变。 |

## 8. 实施依赖、验证和停止条件

真实互通使用 DS-003 实际导出的文件及 DAA-017 实际导入结果，记录两端候选、revision 和原文件 SHA；手写样例只作格式自检。用户已授权使用各自 .local/dev 新增测试对象；如需 DDL、迁移、覆盖既有数据、公共合同或白名单外修改则停止。定向验证不能推断全部旧版本或历史兼容。

### 本机合成互通与人工复验（r5 已批准）

1. **角色与状态。** 仅当父 ARCH-PLC-001 r5、本任务 DAA-017 r5 和涉及两基础的下游时序衔接均经 Human Owner 精确批准后，Development 才可修改本任务白名单，记录候选、自检并 handoff；fresh-context Verification 复核实际交付候选。两基础仍按各自已批准验收办理，其现有 qa_blocked 不能由本任务改成通过。若两项候选涉及相同文件，先记录现有改动并协调整合，不能覆盖其他工作；完整最终候选及锁文件须在正式交付树复核。
2. **本机测试目标。** 用户明确授权直接使用 DS、DAA 各自的 .local/dev。先核对实际应用、进程、profile 及路径，区分已有对象和本任务带唯一标识的合成测试 PLC/文件；不得覆盖已有配置、实例或历史。可使用现有已运行应用或项目普通入口；不输出、复制或修改真实 .env 内容。普通启动程序可能按既有规则读取自身 .env，必须确认实际 profile 不回落到其他位置；目标不明即停止。
3. **原生事故与残余风险。** 此前 DAA 窗口退出后 CUA 可能重绑或启动用户默认 profile，影响未知，该历史及原 QA 结果保留。此次仅操作经核对的自有进程及已授权 .local/dev，不按应用名重绑或触及不明 profile；若无法确认目标、避免影响既有数据、设备或真实上报则停止。无需 VM、Windows 或完整系统层排查，不能声称系统缓存完全隔离。
4. **主线与清理。** 通过 DS 正常流程新增可识别测试实例和所需保存版本，导出文件供 DAA 在自己的 .local/dev 新建测试 PLC；不提供 DB/UDT，显式分组、保存和激活后只连接该 DS 的 127.0.0.1 端口。先核实既有实例不会被自动采集、连接或上报，无法保证则停止；不得为测试静默改变既有实例或上报设定。v2 使用假 transport，不发真实 POST。新增配置可能产生新 revision、active 指针变化以及正常 runtime 审计事件，不得说整个数据库零写。完成后只通过安全的正常方式清理可确认属于本任务且不影响既有历史的测试 PLC/文件；不可安全删除或已被历史引用的如实保留并说明，绝不删除整个 .local/dev 或已有数据。中英文 USER_GUIDE 写实际复验步骤。

## 9. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品、数据库或测试。批准后 Development 根据触达面使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及治理规则独立复核。Development 自检或 QA 通过均不自动授权真实设备、上线、数据库迁移或 Human Owner 最终验收。

## r4 Human Owner 精确实施批准记录（历史）

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

本决定精确批准 aiis-ics-arch::DAA-017 r4 实施范围、ARCH-PLC-001 r5 设计范围及两基础原下游门槛的顺序调整，并授权按本规格使用两应用各自 .local/dev 完成受控互通、清理本任务资源及更新手册。本任务批准前完整草案 SHA-256 为 efece638b647a04c82a9116df463d6cfe9a8d7d278cb0835b3c580e196ead966。该批准不代表本任务或双语基础 QA 通过、Human Owner 最终验收，也不授权真实设备、外部上报、物理 DDL、用户 profile 迁移、FF/CA 或发布。

## r5 修订与批准记录

r4 开发时发现命名预览的硬编码来源只支持 manual / inferred；目录点必须保留 origin=catalog，因此现有白名单无法以原预览完成允许的编辑。r5 仅新增上述一个现有文件和 DA17 的直接验证；首次新建、重复拒绝、JSON、采集、双语、上报、历史、.local/dev 授权与其余 AC 不变。此前 r4 和历史批准不被撤销；Human Owner 已另行精确批准 r5，Development 可按本 r5 修改新增路径。

### Human Owner 精确实施批准

2026-11-17（Asia/Shanghai），Human Owner 对列明 DS-003 r5 和 DAA-017 r5 的批准请求明确回复：

> 批准两个 r5

本决定精确批准 aiis-ics-arch::DAA-017 r5 的实施范围；用户审阅、登记前完整草案 SHA-256 为 956b786d8b82a03404f80c5344a2894cfa7a622ab9347636c186a9bb0e69f0ba。原 r4 实施批准及全部历史继续保留；Development 可按本 r5 接续。该决定不代表 QA 通过或 Human Owner 最终验收，两项双语基础原 qa_blocked 状态不变；原 .local/dev 互通测试授权及数据保护边界继续有效。

## 附录 A：已批准 r4 完整原文（含全部历史）

r4 写前 SHA-256：005312642152ee1c0a9bcc9a351171069ddd32121dc074bc7ca55091ebceecaf；围栏内保留原 UTF-8 字节及末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-017
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准父 r5、本 r4 及基础任务下游时序衔接 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 将逐 PLC 完整 S7 点位 JSON 作为可追溯目录来源导入 DAA 草稿
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r4; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: ARCH-PLC-001 r5、本任务 r4 和两基础任务下游时序衔接已获 Human Owner 精确批准；跨应用验收依赖 DS-003 r4 实际导出候选

# DAA-017 r4：按 PLC 导入完整点位 JSON

## 1. 状态、目标与范围

2026-11-17（Asia/Shanghai），Human Owner 反馈已在 DS、DAA 各自的 .local/dev 手工测试中英切换及 display_name，结果没问题；该反馈是用户手工观察，不等于独立 QA 通过或最终验收，两基础任务当前仍为 qa_blocked。用户明确授权后续 JSON 互通直接使用各应用各自的 .local/dev，无需另建 profile；环境授权与实施批准为不同事实；本 r4 已另获精确实施范围批准。

**本 r4 实施范围已获 Human Owner 精确批准。** Human Owner 已批准 ARCH-PLC-001 r5、DS-003 r4、DAA-017 r4 及下游顺序调整，两个 JSON 任务可各自开展 Development 和自检，不再等待两基础任务最终验收。DS-004 r2、DAA-018 r3 的原独立验收及 QA 历史不变，目前仍为 qa_blocked；本决定不是 QA 通过或最终验收。另一个 JSON 任务有独立验收链。

目标：用户选择一份 DS 导出的 PLC 点位 JSON，预览确认后仅新建一台 DAA PLC，将完整目录及来源写入草稿；无需再次提供 .db / .udt，经分组、启用、保存和显式激活后可受控采集。已有来源、PLC/DB/点身份冲突及同文件重导均拒绝，不修改既有 PLC；合并、差异更新及点位覆盖移后。

本切片只实现 DAA 输入、来源完整性和现有编辑/激活兼容。DS 导入、DAA 导出、本地新增点生成 `daa.catalog_snapshot`、FF 适配、正式发布公共跨运行时合同、其他协议、DDL、真实 profile/数据库迁移和现场采用另立范围；不得将父设计批准视为这些实施批准。

## 2. 同一输入合同与严格验证

输入只接受 [ARCH-PLC-001 r5](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 共同的 aiis.plc_points、整数 schema_version 1 且 export.producer 为 device_simulator 的文件：每文件一台 PLC、至少一个 DB 及完整点集。其他 producer 的导入以后另定，不另造 DS 专属子格式。以下示例逐字复制父规格。

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

1. 从用户选择的文件读取并计算**原始字节** SHA-256；严格 UTF-8 无 BOM，大小上限 1 MiB、层级 16、至多 32 DB / 4096 点；拒绝重复 key、未知字段、错误版本、非整数字面量、null/隐式转换、非法 UUID v4、重复/跨类别 ID、名字重复及其他父合同负例。对所有点和禁用点同等检查物理范围、类型宽度、BOOL bit 与重叠，包括 `STRING[n]` n=1..254、ASCII 及 n+2 字节。未知类型或任何坏点使整台导入失败，不跳过、不更名、不推算偏移。`export.payload_sha256` 是导出方声明的配置原字节摘要，不能拿输入 JSON 的摘要冒充或宣称已验证到源配置；本地保存输入原字节及自己的摘要。
2. 本期只接收 DS producer，DB 和点的 source_enabled 均必填布尔值。源值在归档原文中保留并展示；新 PLC 和点默认不启用、不分组，不能将源值当作 DAA 采集许可。
3. display_names 缺省时新点两值为空；存在时必须含 zh-CN、en-US 两字符串，各至多 256 UTF-8 字节，允许空串但非法类型、null、缺键或多余键拒绝。确认后按本地点 ID 保存，不从其他字段推测。可选 display_name 独立保存为语言未标记值，原文件及字段存在性一并归档。
4. description 缺省或空时新点 comment 为空；非空值经确认原样写入 comment，最多 500 UTF-8 字节。原始文件保留字段是否存在，description、comment 和显示名互不冒充，不新增上报字段。
5. `connection` 是客户端目标，预览并要求用户明确核对/确认，可在确认前编辑目标；仅允许规范 IPv4 单播、合法 port/rack/slot，保留项目的端点唯一和 PLC 数量等校验。`0.0.0.0`、非法地址和非默认 TSAP（DAA 当前没有自定义 TSAP 模型）明确阻断；loopback 提示仅同机有效。不得试连以测试地址或自动连接真实 PLC。来源输出摘要不证明设备布局、设备许可、文件真实性或物理可达性。

## 3. 新建 PLC 与原子提交

选择一个 DS JSON，仅预览新建 PLC，不提供选择已有 PLC、合并或覆盖入口。预览来源、SHA、目标连接、所有 DB/点、双语、旧单条名称和描述。确认前不写；PLC、DB、点沿用文件 UUID。任一 UUID 在本地已使用、相同 origin 已存在或同文件重导时，明确拒绝整份，不改 ID，不猜测身份。

确认绑定文件 SHA、目标连接及当前草稿 ETag，变化或并发使预览失效。成功时一次提交新 PLC、目录原文、绑定和草稿；取消、冲突或已知提交前失败不写，结果未知先读取草稿和来源，不盲重试。其他 PLC、活动配置、历史及上报身份不受影响。

新 PLC 和点默认不采集，用户在新 PLC 下设置组、周期和点启用，保存后显式激活并连接。目录点集、技术名、地址及类型本期不做本地覆盖；双语和 comment 按现有流程维护。已有 PLC 匹配、三方比较、差异重导及覆盖均为后续。

## 4. 目录来源与可验证配置

首次导入将所选原始 JSON 与 SHA 保存为新 PLC 的真实 catalog SourceDocument；多个 DB 共用 source_id，逐 DB 绑定原 DB 和点 ID。优先在 schema version 1 可选 catalogBindings 保存 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和完整点身份对应；本期同身份沿用，不设 localOverride 或三方差异元数据。

目录分支重验原文和 SHA、origin、成员、类型、地址、宽度、BOOL bit、越界及重叠；两端点集一一对应，伪造、缺失、重复或跨 PLC 绑定拒绝。Db.complete 仅表示目录完整，tree 可为空但不伪造 TIA 树或 DB/UDT；原 DB/UDT 分支的 source_id、tree、leaf_matches 和地址校验不变。

确认后目录地址可标记 confirmed、origin=catalog 并记明依据；普通保存不可伪造绑定或覆盖目录点集、技术名、地址和类型。采集分组、周期及启用仍按既有规则。若无法无原 DB/UDT 地保存、激活及采集，停止回 PM；不改双库 DDL、不迁移用户 profile。旧版原生兼容未验证，不声称通过。

## 5. 历史样本和事实契约保护

双语与未标记显示名不进入 Point、PointFact.definition 或 name/comment/value；既有上报合同和程序名不变。目录身份不替代 DAA 本地 PLC、采样或上报身份；不改用户旧配置、样本、队列和回执。新目录样本经原事实校验器并用模拟 v2 transport 捕获正文，确认中文及英文显示名不在正文且原字段语义不变，不发真实网络请求。父设计和 DAA-018 r3 对既有 v2 各路径及旧 v1 test-only 的原有要求与结果独立保留；本切片不重新启用旧 v1、不裁剪上下文或改写历史，也不能声称未验证的旧路径通过。

## 6. 已批准的 Development 允许文件

路径均以 automation-world/data-acquisition-agent/ 为根；花括号仅展开所列文件；下列文件仅限首次新建 PLC、目录绑定、必要采集兼容和相关验证；不得用本白名单实现已有 PLC 匹配、重导差异合并或点位覆盖。需要其他文件先回 PM。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 模型、来源校验 | `src-tauri/src/domain/{mod.rs,local_configuration.rs}`；`src-tauri/src/services/{mod.rs,local_configuration.rs,local_supervisor.rs,local_activation.rs}` | `src-tauri/src/domain/plc_catalog.rs`；`src-tauri/src/services/catalog_import.rs` |
| 本地存储与桌面桥 | `src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；`src-tauri/src/commands/local_acquisition.rs`；`src-tauri/src/lib.rs` | `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` |
| UI 与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/components/SourceImportPanel.vue`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/plc/components/CatalogImportDialog.vue` |
| 回归和说明 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`（仅相关回归需要时）；`src-tauri/src/services/local_delivery_tests.rs`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `tests/plc-catalog-import.test.mjs`；`tests/fixtures/plc-catalog-v1.json`；`CODE_INDEX.md`（实际结构发生变化时按仓库契约新建） |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后 Development 创建本 bundle `tasks.md`；交接后独立 Verification 创建 `checklist.md` |

禁止修改 schema.rs、迁移/DDL、依赖锁、.env、原始 DB/UDT、DS/FF/backend 源码、根 contracts 或其他任务。已授权通过 DAA 应用在核对后的 .local/dev 仅新增本任务测试 PLC、来源和必要草稿/版本；不直接编辑数据库，不覆盖既有 PLC、配置内容、样本、队列或历史。真实网络 POST、现场设备及其他数据库不在范围；新文案中英文成对。

## 7. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DA01 | 接受共同格式且 producer 为 device_simulator 的单 PLC 文件；非法版本、字段、编码、类型、ID、容量或点集拒绝且不写，其他 producer 不在本期。 |
| DA02 | BOOL、INT、REAL、STRING 与停用点完整导入，核对 ID、名称、类型、地址和双语；DS 的 DB 与点 source_enabled 必填但不自动采集。 |
| DA03 | BOOL bit、非 BOOL bit、非法 STRING 长度、越界、物理重叠、无效名称/类型和禁用点错误均阻断整台；客户端地址/端口与 TSAP、同机 loopback 提示及不连接行为明确可验。 |
| DA04 | 一个 PLC 多 DB 引用同一真实目录 source，source_id、原文 SHA、origin、DB/点映射全链一致；伪造 source、错 SHA/DB/点/类型/地址、重复或跨 PLC 引用均无法保存或激活。旧 DB/UDT 完整树、leaf_matches、UDT 及源校验正反例行为不变，目录 UI 不显示伪造 TIA 树。 |
| DA05 | 首次新建沿用 PLC、DB、点 UUID；任一身份已占用、origin 已存在或同文件重导时明确拒绝，原草稿、ETag 和来源不变。 |
| DA06 | 目录点集、技术名、地址及类型覆盖明确拒绝；新 PLC 的组、周期和启用可设置并激活。 |
| DA07 | 预览取消、更换文件或端点、过期预览、草稿并发变化及提交失败均无部分来源、映射或写入；重复来源明确拒绝，未知结果先重读、不盲目重试。 |
| DA08 | 新 PLC 和点默认不采集；用户显式设置组、周期、启用并保存时，既有 PLC 内容不变、active 不自动改变；显式激活产生正常新 active revision，但不得改变既有 PLC 及上报设定或触发其设备动作。 |
| DA09 | 在核对后的 DAA .local/dev 仅新增测试 PLC 和目录，双库物理 schema 不改，既有 PLC、配置历史、样本和回执不覆盖；正常运行审计和新 revision 如实记录，不声称整库零写。迁移或 DDL 另批；未验证旧版兼容不得声称通过。 |
| DA10 | 新导入目录的实际本地样本通过既有事实校验；以中文、英文不同 sentinel 捕获该样本模拟 v2 正文，验证程序 name/value 等原字段语义不变且不含显示名，未发真实 POST。旧 v1 和旧 v2 各路径按 DAA-018 自身证据如实记录。 |
| DA11 | 使用实际 DS-003 候选对受控 DS 保存版本导出的原文件（记录候选、revision、SHA），在已核对的 DAA .local/dev 新建测试 PLC 导入，无需 .db/.udt；显式分组、启用、保存和激活后，仅连接自有 loopback DS S7，读取 BOOL、INT、REAL 并核对身份、地址、值与质量，停用点仍保留。不得触发既有 PLC 或真实上报；fixture 不能替代闭环。 |
| DA12 | 针对实际交付候选运行相关 Rust/Node 检查及项目构建，记录真实结果；按用户已授权的合成目标验证实际导入操作。Windows、虚拟机及其他未测平台不作为通过前置。 |
| DA13 | 新点中文、英文、单侧空及无语言单条按合同保留，顶栏切换不改配置，description 和程序 name 不被显示名代替。 |
| DA14 | 新点 description 非空经确认写入 comment；缺失或空串显示为空、原文件字段存在性保留；重导冲突和覆盖不在本期。 |
| DA15 | 核对 DAA .local/dev、进程与新测试 PLC 身份；目标不明或可能触及既有数据/设备时停止。只连接自有 DS loopback，fixture 不代替真实读取。 |
| DA16 | 两份中英文 USER_GUIDE 记录核对 DAA .local/dev、导入 DS 实际文件、分组/保存/激活/显式采集、核对值及仅清理自有对象的步骤；未实现或未验证入口不能冒称可用。 |

## 8. 实施依赖、验证和停止条件

真实互通使用 DS-003 实际导出的文件及 DAA-017 实际导入结果，记录两端候选、revision 和原文件 SHA；手写样例只作格式自检。用户已授权使用各自 .local/dev 新增测试对象；如需 DDL、迁移、覆盖既有数据、公共合同或白名单外修改则停止。定向验证不能推断全部旧版本或历史兼容。

### 本机合成互通与人工复验（已批准范围）

1. **角色与状态。** 仅当父 r5、本任务 r4 和涉及两基础的下游时序衔接均经 Human Owner 精确批准后，Development 才可修改本任务白名单，记录候选、自检并 handoff；fresh-context Verification 复核实际交付候选。两基础仍按各自已批准验收办理，其现有 qa_blocked 不能由本任务改成通过。若两项候选涉及相同文件，先记录现有改动并协调整合，不能覆盖其他工作；完整最终候选及锁文件须在正式交付树复核。
2. **本机测试目标。** 用户明确授权直接使用 DS、DAA 各自的 .local/dev。先核对实际应用、进程、profile 及路径，区分已有对象和本任务带唯一标识的合成测试 PLC/文件；不得覆盖已有配置、实例或历史。可使用现有已运行应用或项目普通入口；不输出、复制或修改真实 .env 内容。普通启动程序可能按既有规则读取自身 .env，必须确认实际 profile 不回落到其他位置；目标不明即停止。
3. **原生事故与残余风险。** 此前 DAA 窗口退出后 CUA 可能重绑或启动用户默认 profile，影响未知，该历史及原 QA 结果保留。此次仅操作经核对的自有进程及已授权 .local/dev，不按应用名重绑或触及不明 profile；若无法确认目标、避免影响既有数据、设备或真实上报则停止。无需 VM、Windows 或完整系统层排查，不能声称系统缓存完全隔离。
4. **主线与清理。** 通过 DS 正常流程新增可识别测试实例和所需保存版本，导出文件供 DAA 在自己的 .local/dev 新建测试 PLC；不提供 DB/UDT，显式分组、保存和激活后只连接该 DS 的 127.0.0.1 端口。先核实既有实例不会被自动采集、连接或上报，无法保证则停止；不得为测试静默改变既有实例或上报设定。v2 使用假 transport，不发真实 POST。新增配置可能产生新 revision、active 指针变化以及正常 runtime 审计事件，不得说整个数据库零写。完成后只通过安全的正常方式清理可确认属于本任务且不影响既有历史的测试 PLC/文件；不可安全删除或已被历史引用的如实保留并说明，绝不删除整个 .local/dev 或已有数据。中英文 USER_GUIDE 写实际复验步骤。

## 9. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品、数据库或测试。批准后 Development 根据触达面使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及治理规则独立复核。Development 自检或 QA 通过均不自动授权真实设备、上线、数据库迁移或 Human Owner 最终验收。

## Human Owner 精确实施批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

本决定精确批准 aiis-ics-arch::DAA-017 r4 实施范围、ARCH-PLC-001 r5 设计范围及两基础原下游门槛的顺序调整，并授权按本规格使用两应用各自 .local/dev 完成受控互通、清理本任务资源及更新手册。本任务批准前完整草案 SHA-256 为 efece638b647a04c82a9116df463d6cfe9a8d7d278cb0835b3c580e196ead966。该批准不代表本任务或双语基础 QA 通过、Human Owner 最终验收，也不授权真实设备、外部上报、物理 DDL、用户 profile 迁移、FF/CA 或发布。

## 附录 A：完整 r3 原文（含全部历史，非本草案）

写前 SHA-256：9cf86a570fef7e72fbd12efab246a8db7ead5669640f9a590b2e253ec3c22c00；围栏内保留原始 UTF-8 字节和末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-017
Revision: r3
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 双语基础原生 blocker 解除并各自 STD 最终验收 -> Human Owner 精确批准 DAA-017 r3 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 将逐 PLC 完整 S7 点位 JSON 作为可追溯目录来源导入 DAA 草稿
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r3; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r4 设计批准；DS-004 和 DAA-018 各自完成 STD 至 Human Owner 最终验收；跨应用端到端验收依赖 device-simulator::DS-003 r3 的实际导出候选

# DAA-017 r3：按 PLC 导入完整点位 JSON

## 1. 状态、目标与范围

**本任务为 draft / r3，尚未获得实施批准。** Human Owner 已选择先做 DS→DAA，并授权两应用各自在 `.local` 下新建非 `dev` 合成环境、测试后清理及在手册保留人工复验步骤；这不是对本实施任务或最终验收的批准。[ARCH-PLC-001 r4](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获批准。DS-004 r2 与 DAA-018 r3 各自实施范围已批准，但独立 QA 目前均 `qa_blocked`，原生必测及 Human Owner 最终验收未完成；必须先处理隔离事件并完成两项原有 STD 最终验收，再对本 r3 和 DS-003 r3 分别取得精确实施批准。DS-003 是另一独立 owner 和验收链；旧 r1/r2 均为未批准实施草案，原文和历史保留。

目标：用户选择一份 PLC 点位 JSON，预览并确认新建或匹配本地 PLC，将完整目录及来源写入草稿；无需再次提供该 PLC 的原始 `.db` / `.udt`，经本地选择组、启用、保存和显式激活后，受控 S7 采集可以读取。保留 BOOL、INT、REAL、STRING 等所有声明点和停用点，不把来源启用事实当成 DAA 采集权限。导入确认不自动激活、连接、采集、上报或改写其他实例。

本切片只实现 DAA 输入、来源完整性和现有编辑/激活兼容。DS 导入、DAA 导出、本地新增点生成 `daa.catalog_snapshot`、FF 适配、正式发布公共跨运行时合同、其他协议、DDL、真实 profile/数据库迁移和现场采用另立范围；不得将父设计批准视为这些实施批准。

## 2. 同一输入合同与严格验证

输入**只接受** [ARCH-PLC-001 r4 §3–5、§7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 `aiis.plc_points` / 整数 `schema_version: 1` 候选：一次文件是一台 PLC、至少一个 DB，每 DB 至少一个点。它既可声明 `export.producer=device_simulator`，也可声明 `data_acquisition_agent`；本任务支持两者的合同验证及导入，不要求本次实现 DAA 导出。不得创造第二种受限 DS 格式。以下示例逐字复制父规格，示例摘要只是词法，不代表真实保存内容。

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

1. 从用户选择的文件读取并计算**原始字节** SHA-256；严格 UTF-8 无 BOM，大小上限 1 MiB、层级 16、至多 32 DB / 4096 点；拒绝重复 key、未知字段、错误版本、非整数字面量、null/隐式转换、非法 UUID v4、重复/跨类别 ID、名字重复及其他父合同负例。对所有点和禁用点同等检查物理范围、类型宽度、BOOL bit 与重叠，包括 `STRING[n]` n=1..254、ASCII 及 n+2 字节。未知类型或任何坏点使整台导入失败，不跳过、不更名、不推算偏移。`export.payload_sha256` 是导出方声明的配置原字节摘要，不能拿输入 JSON 的摘要冒充或宣称已验证到源配置；本地保存输入原字节及自己的摘要。
2. 来源启用只按 `export.producer` 解读：DS 导出时 DB `source_enabled` 必填且取 DS DB 事实；DAA 导出时该字段必须缺省；点层两种 producer 均必填实际布尔值。DB 字段缺省不是 true/false，null、错误分型或缺失点层字段拒绝；`origin.kind` 仅是身份命名空间，不能据此推断最后导出者。所有源启用值保存在可校验的归档原文并展示；新建的 DAA PLC/点默认不启用、不分组，不从源值推导采集许可。已存在点的本地 enabled/组及周期默认保留，差异展示后须由用户使用现有本地设置明确改变。
3. `display_names` 可缺省，缺省对新点为两值 `""`、对已有点默认保持本地；存在时恰有 `zh-CN`/`en-US` 两字符串（各 ≤256 UTF-8 字节），允许显式空串，缺键、null、其他键、非字符串或超限拒绝。输入两个值逐点预览并以本地点 UUID 写入 DAA-018 的 `pointDisplayNames`；空语言不从 name、另一语言、路径、comment 或旧值推测。原有可选 `display_name` ≤256 字节，独立保存到可省略 `pointLegacyDisplayNames`（UUID→原字符串）并标注语言未标记，不写进双语字段、name 或 comment；原始 JSON 内容、字段有无及 bytes/SHA 全部归档。空旧值在本地可省略，但归档保留原文；无任何本地记录等于未提供，重导时由原文 presence 区分。
4. `description` 可缺省；缺省不清空已有 DAA comment，新点无描述则 comment 空。非空值来自输入、最多 500 UTF-8 字节，新点经用户确认后原样写入现有 comment；已有非空或已编辑 comment 与输入不同需预览并显式选择保留或采用。文件显式 `description: ""` 表达来源为空，对已有非空 comment 须明确确认才能清空；源原文、历史版本和用户未选中的点始终保留。description、comment 和显示名语义独立，不以任何显示名冒充描述，也不增加上报字段。
5. `connection` 是客户端目标，预览并要求用户明确核对/确认，可在确认前编辑目标；仅允许规范 IPv4 单播、合法 port/rack/slot，保留项目的端点唯一和 PLC 数量等校验。`0.0.0.0`、非法地址和非默认 TSAP（DAA 当前没有自定义 TSAP 模型）明确阻断；loopback 提示仅同机有效。不得试连以测试地址或自动连接真实 PLC。来源输出摘要不证明设备布局、设备许可、文件真实性或物理可达性。

## 3. 交互、身份、差异与原子提交

1. 选择一个 JSON 文件；在导入流程内可新建 PLC，或显式选择已有 PLC。预览目标、外部 origin、生产者、导出版本、输入 SHA、连接、全部 DB/点和不可支持项；界面将目录点列表与 TIA 结构树区分。新目标可生成预览用本地 UUID，但只有确认成功才持久化。取消或只预览不写草稿、来源档案、活动版本、设备、上报或用户文件。
2. 外部身份是 `(origin.kind, origin.profile_id, origin.plc_id, db.id, point.id)`，不以名称、IP、DB 号或相似地址自动认同。首次新建时 ID 在本地全局可用可保留，否则分配新本地 UUID 并持久映射，预览给出对应关系；映射到未绑定的既有 PLC/DB/点须逐项一一匹配并显式确认。同一个目标已绑定不同 origin 时阻断，不合并、不覆盖、不冒充单一来源。origin 是身份命名空间，不声称所有点都由 DS 创建。
3. 已有映射按外部身份稳定匹配并保留本地 PLC/DB/点 UUID、组/周期与历史引用。相同文件、相同目标、有效映射且无本地显示名/comment 冲突时再次导入无变化：不产生新的草稿 ETag、版本或重复源。名称、类型、地址、源启用事实等变化列出前后和影响，物理地址/类型变化及覆盖冲突须用户明确决定；DB 编号变化、同一外部 ID 归属冲突、不同 origin、文件缺少目标匹配 DB 里的任何点或目标含文件未声明额外点，一律阻断整 PLC，保持原草稿和源归档，不因点未启用或无历史而放宽。不得依次部分覆盖或静默删除。
4. 对两个显示语言、未标记 `display_name` 和 description/comment 分别进行三方比较：上次已确认源原文与 SHA 为来源基准，同时展示本地当前值和本次文件值（区分缺字段与显式空串）。已有点输入与本地不同，或本地在基准后编辑时，须让用户逐项选择保留本地/采用输入；缺字段默认保留，若选显式空串清空已有值必须确认。新目标直接按确认预览保存输入各值。逐项选择、绑定和基准与原文归档在同一 CAS 事务提交；同文件且来源基准未变、用户保留当前值时不改变 ETag；若新文件 bytes/SHA 已变，即使选择保留本地名称，来源归档或绑定基准发生变化仍可使草稿 ETag 正常改变。用户明确恢复/清空也按正常编辑改变草稿。不得依文件名、技术名或地址自动改身份。
5. 有界预览 token 绑定输入原字节 SHA、目标、候选映射、端点选择、当前草稿 ETag 和有效期。文件、目标、选择、映射或草稿改变即失效；确认时在引擎侧重算并进行 CAS。并发、重复确认、超时、取消、断电/提交失败和结果未知时不得留半条来源/绑定/草稿；结果未知先按现有机制重读判断，不盲目重复写。确认事务提交前核算输入、完整配置 payload、归档及容量预算，超限整台拒绝，不因单文件小于 1 MiB 而忽略目标整体容量。
6. 新点保留但默认不采集：用户随后显式选择现有组，或新建组、确认周期并批量选择点/启用；未选点保留为未分组/停用。现有 PLC/组启用开关、组周期、active/loaded、上报绑定和已有启动选项原样保持；导入不更改 DAA-015 的既有自动启动设置，也不对与本次导入无关的活动配置承诺停止。显示可激活性和既有 runtime 资源预算，超限则阻断激活并指出原因，不裁剪文件。运行时版本 4 的每 DB 512 启用点与相关采集/编码预算、旧 runtime 的组限额仍按现有规则执行。

## 4. 目录来源与可验证配置

当前 DAA `Db.source_id` 必须指向本 PLC 的真实 SourceDocument，原 DB/UDT 启用点受 `Db.tree` 和 `leaf_matches`、源/UDT 闭包与布局校验保护。**不得伪造 `.db`/`.udt`、TIA 源行或来源树，也不得整体关闭旧校验。** 本切片优先实现父设计的 schema version 1 可选目录分型：

- 按一次输入在目标 PLC 建立一个逻辑 catalog SourceDocument，保存所选完整原始 UTF-8 内容及 SHA；同一输入包含多个 DB 时，各 DB 的 `source_id` 指向同一个逻辑源，每 DB 的绑定指向自己的外部 DB。其他 PLC 的逻辑源独立；相同 SHA/字节物理归档可复用现有全局策略，不重写历史来源。来源变更时先保留原归档，不能原位篡改旧版本依赖材料。
- 配置增加可省略 `catalogBindings`：每项含 `localDbId`、`sourceId`、`sourceSha256`、`sourceKind=exchange_json`、`originDbId` 和 `pointMappings`，后者每项含 `localPointId`、`catalogPointId` 以及可选 `localOverride`；另含可选的按字段显示名/描述冲突确认元数据，记录最后确认 source SHA、字段 presence、源值及所选本地值，缺项不得伪称来自源。其 PLC 从本地 DB 关联确定，不信任外部传入的本地 PLC；重算源 SHA、解析封闭合同并检查单一 origin、source_id 与所属 PLC、外部 DB/点、本地 DB/点、成员身份及每边完整一一对应。重复、缺失、伪造、错 hash、跨 PLC、越界、重叠、类型/地址不符均拒绝。一个本地 PLC 同一外部文件的 DB 共用一个逻辑源，同一 originDbId 不得被绑定两次。
- 仅对有效 catalog binding 走目录校验分支，以完整的 DB/点关联替代 DB/UDT 专属的 `db_number` / `importBinding` 和 `leaf_matches` 条件；`Db.complete` 表示目录点集完整，不表示原 TIA 工程完整，`tree` 可为空。原 DB/UDT 分支仍执行原来的树、leaf、source_id、UDT 及地址验证。外部 `source_path` 缺省时不能伪造：当前 Point 字段若必须为字符串，目录分支用空字符串表达没有路径、以明确 catalogPointId 追溯且 UI 显示未提供；若存在逻辑路径按原值保留，不把它当磁盘路径。双语显示名使用基础任务的配置级 `pointDisplayNames`；无语言单条使用 `pointLegacyDisplayNames`（本地 UUID→字符串，非空存、空可省略），两者均不得添加到 Point/PointFact。description 可按明确选择进入既有 Point.comment。原文独立归档，不能伪造或静默丢弃。
- 经用户在预览中确认后，目录地址以 `Address.confirmed=true`、`origin=catalog` 和真实确认原因进入本地配置；该 origin 仅在有效目录绑定下合法。已导入点使用现有编辑流程修改类型或地址时，必须显式确认，记录 `localOverride` 的原 source SHA、新 dataType/offset/可选 bit 和确认原因；重验重叠及所有布局。新源中该点的基准变更时，列明与 override 的冲突并由用户选择保留或采用，不能将旧覆盖静默套用。禁止用普通保存接口伪造或删除绑定/覆盖来绕过引擎校验。若尝试在目录 DB 中新增旧原文未包含的点，本切片明确拒绝并提示后续单独设计的内部快照操作，不生成假来源或不完整映射。
- 保留 `schema_version=1` 和两库现有物理 DDL：可选字段在没有目录来源时省略，以保证旧 payload 新程序零写读。必须验证新旧二进制兼容，而非将加可选字段视作自动兼容：含新绑定的 payload 应让旧二进制安全拒绝，不能静默按旧树运行或新建空库；已有原生配置、样本、不可变 payload/sha 不被重写。若受现有校验、预算或兼容性限制不能满足此方案，停止并回 PM；任何双 SQLite CHECK/物理 schema 调整、已使用 profile 迁移、备份恢复须另立 schema-maintenance 范围和批准，本任务不暗中升级。

## 5. 历史样本和事实契约保护

双语与未标记显示名始终不进入 Point、PointFact.definition，也不混入 name/comment/value 或产品实际可达的任何外发字段；沿用 DAA-018 的配置级存储。输入目录身份不等于 DAA 的 instanceId、plcId、sourceGeneration、采样 ID/sequence 或上报绑定；不自动创建、替换或合并它们。既有 active/used 版本、样本原始 bytes/SHA、历史、排队/冻结上报和 ACK 维持原状；不追溯更改旧样本的定义。`PointFact.definition` 包含本地 Address，因此只在新采样中可能出现 `origin=catalog`：必须用真实 DAA 本地事实校验器/manifest 和序列化链路验证新旧样本可读，再验证输出的既有 `plc-facts/v2` 上报 body 与当前合同一致；当前 plc-facts/v2 单样本 Point 不包含 Address/origin，不能往其中新增字段；历史 batch 可能按原合同含 Point 定义/Address，须对该路径按原样验证，不能宣称所有路径原本都没有这些字段。按父 r4 和 DAA-018 r3 区分产品实际可达的 v2 外发与旧 v1 test-only 本地构造：v2 新采样、既有冻结/重试及符合 legacy_status 的旧样本转 v2 均须以双语 sentinel 验证不进入外发正文；旧 v1 测试构造的完整 contextUtf8 可按原合同含显示名，须如实保留并明确未外发，不得启用旧发送链、裁剪上下文或重算历史摘要；用户保存激活新配置可正常产生新 configRevision，不要求新旧样本字节相同；旧样本、历史、冻结正文及回执不得重写。受控测试不发网络请求。若接收方既有合同或旧历史无法兼容，标记阻塞并回 PM，不能修改公共合同、后端或悄悄丢弃定义。

## 6. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/data-acquisition-agent/` 为根；花括号仅展开列名，不是通配符。仅改列出的本切片相关内容；需要额外文件先回 PM 修订。当前 PM 只写本 `spec.md`，角色文档各按 STD 创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 模型、来源校验 | `src-tauri/src/domain/{mod.rs,local_configuration.rs}`；`src-tauri/src/services/{mod.rs,local_configuration.rs,local_supervisor.rs,local_activation.rs}` | `src-tauri/src/domain/plc_catalog.rs`；`src-tauri/src/services/catalog_import.rs` |
| 本地存储与桌面桥 | `src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；`src-tauri/src/commands/local_acquisition.rs`；`src-tauri/src/lib.rs` | `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` |
| UI 与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/components/SourceImportPanel.vue`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/plc/components/CatalogImportDialog.vue` |
| 回归和说明 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`（仅相关回归需要时）；`src-tauri/src/services/local_delivery_tests.rs`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `tests/plc-catalog-import.test.mjs`；`tests/fixtures/plc-catalog-v1.json`；`CODE_INDEX.md`（实际结构发生变化时按仓库契约新建） |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后 Development 创建本 bundle `tasks.md`；交接后独立 Verification 创建 `checklist.md` |

禁止修改 `schema.rs`、迁移/DDL、Cargo 或 pnpm 依赖及锁、`.env`、用户数据库/profile、样本/队列/回执、原始 DB/UDT 文件、DS/FF/backend 源码、根 contracts、其他任务。允许测试只在全新隔离 profile 与自有临时输出；网络 POST、现场设备和真实数据库均不在范围。新可见文案中英文键成对；新增或触达的业务表复用公共列宽组件：普通列可拖拽、有最小宽和横向滚动，刷新/切页/重启按稳定字段恢复，可恢复默认；功能列可固定，偏好不写业务配置。

## 7. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DA01 | 父规格示例及受控多 DB 合成文件对两种合法 producer 通过；严格拒绝重复 key、BOM、非法 UTF-8、未知字段/版本、非法整数/UUID/null、超限、重复身份与空点集，逐个报告具体原因且没有写入。 |
| DA02 | 包含 BOOL、INT、REAL、STRING、不同 BOOL bit 与禁用点的完整文件无丢点导入；比较原始 bytes/SHA、点 ID 对应、名称、类型、地址、范围及原启用事实。DB/点字段按 producer 分型检查：DS DB 缺失、DAA DB 存在、点缺失/null 均拒绝；源点 true 不导致 DAA 自动采集。 |
| DA03 | BOOL bit、非 BOOL bit、非法 STRING 长度、越界、物理重叠、无效名称/类型和禁用点错误均阻断整台；客户端地址/端口与 TSAP、同机 loopback 提示及不连接行为明确可验。 |
| DA04 | 一个 PLC 多 DB 引用同一真实目录 source，source_id、原文 SHA、origin、DB/点映射全链一致；伪造 source、错 SHA/DB/点/类型/地址、重复或跨 PLC 引用均无法保存或激活。旧 DB/UDT 完整树、leaf_matches、UDT 及源校验正反例行为不变，目录 UI 不显示伪造 TIA 树。 |
| DA05 | 新建和既有 PLC 映射经显式确认，ID 冲突安全分配且映射稳定；同文件且无本地冲突重导 ETag 不变；改名/地址/类型和 source_enabled 差异可见并按规则确认；缺点、额外点、DB 改号、跨 origin 阻断，原草稿字节/ETag 和历史不变。 |
| DA06 | 地址/类型人工覆盖有 SHA 基准、理由和后续源变更冲突；普通保存接口不能伪造绑定或覆盖；目录 DB 本地新增点被明确阻断，既有原始来源和历史版本完整。 |
| DA07 | 预览取消、切换目标/文件、过期 token、草稿并发变化、容量/事务失败与重复提交均无部分来源、映射或写入；未知结果先重读，不能盲重试。 |
| DA08 | 新 PLC/点默认不采集；用户显式分组、周期、启用、保存和激活，资源限额有定位并可阻断；原有组/周期、active/used、启动设置及未选 PLC 不因导入被改变。双语、表格列宽与恢复默认按 §6 验证。 |
| DA09 | 用自有旧合成 profile 副本核验新程序读取旧 schema 1 原 bytes/SHA 不变；旧二进制遇新目录 payload 安全拒绝且不产生空库；双库物理 schema、旧版本、样本及来源原文无变更。不能以空配置通过此项。 |
| DA10 | 自有合成旧样本和新 catalog 样本经原本地定义/manifest 解码，导入前后旧样本、pending 和 ACK bytes/SHA 一致；产品可达 v2 各路径不外发双语 sentinel，不改变既有字段语义。旧 v1 test-only 本地完整 context 可含双语值，保留原正文和摘要且明确未外发；不得启用旧发送链。允许新 configRevision，未发真实网络 POST。 |
| DA11 | 独立端到端：使用实际 **DS-003 候选导出器**对受控 DS saved revision 导出的原文件（记录候选、revision、文件 SHA），在全新隔离 DAA profile 导入；不额外提供或重复导入原 `.db` / `.udt`，用户完成必要分组、启用、保存、激活后，通过自有 loopback DS S7 真正读取 BOOL、INT、REAL，并核对本地/外部 ID、地址、类型、预设值与质量；同时证明停用点仍在草稿/保存配置。DS/DAA 候选均须可追溯，建议 DS-003 已通过 fresh QA；合成 JSON 单测或仅解析不能替代此项。 |
| DA12 | 实际交付树和锁文件执行相关 Rust/Node 测试、类型检查、前端构建、`rust-snap7-driver` 检查和 macOS 原生交互；记录真实命令、退出码、隔离路径、证据、未执行项与清理。其他平台及现场未测不得声称已通过。 |
| DA13 | 输入双语两值、单侧空、字段缺省、原无语言单条和超限/错误类型均按 r4 验证；用户预览后准确保存到按本地点 ID 的独立映射，顶栏语言不改变配置；原文件字节、旧 comment 与 name 不被显示名替代。 |
| DA14 | description 非空经确认进入新点 comment，已有 comment 冲突选择保留/采用可验；缺字段不清空、显式空串清空需确认；本地编辑后重导显示基准/本地/输入三方差异，同文件取消和保留不误写；明确恢复/清空或新源归档/绑定基准变化可正常改变草稿，旧源和历史 revision 不动。 |
| DA15 | 建立自有 DAA `.local` 合成 profile，显式任务 env 与唯一进程/应用身份；证明每次启动/重启同一 profile、不触及真实配置或真实 WebKit store，环境变量缺失、路径错误、CUA 重绑或 OS/XPC 落点未证均阻断。真实 S7 只连接自有 DS loopback，DAA local-validation fixture 不可代替。 |
| DA16 | `USER_GUIDE.md` 与 `USER_GUIDE.zh-CN.md` 给出可重新建立环境、接收实际 DS exporter 文件、无 DB/UDT 导入、分组/保存/激活及显式采集、对照值与质量、关闭和仅清理自有资源的步骤；验证者在完成必要 QA 和证据固化后实际按步骤核对，不能把合成 fixture 或未实现界面冒称闭环。 |

## 8. 实施依赖、验证和停止条件

r4 设计精确批准、DS-004 与 DAA-018 各自完成 STD 最终验收，且 Human Owner 精确批准本 r3 后，Development 才创建 `tasks.md`、实施并自检，交 developer_handoff；fresh-context Verification 独立创建 checklist、复核精确交付候选；Human Owner 最终验收另行决定。DAA 格式、来源、原子性等单端工作可先用受控合成文件自检；DA11 必须等待可追溯的 DS-003 实际导出结果和 DAA-017 实际导入结果，不能将 fixture 冒称跨应用或真实设备联调。

在独立批准的实施与 QA 阶段，仅使用自有新合成数据、两个应用各自全新隔离 profile、隔离临时目录及非特权 IPv4 loopback；不得使用用户原有 dev 联调 profile、数据库或真实设备。受控测试负责进程、文件和端口生命周期；记录候选、来源、证据及清理，无法安全执行则报告 blocked/not_run。

项目工具链为 `pnpm@11.11.0` 与 Cargo/Rust，普通入口 `pnpm tauri dev`。拟议检查示例：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver`、`node --test tests/plc-catalog-import.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR` 和 `RUN_DIR` 指向任务自有隔离临时目录。命令需由 Development 按实际测试入口核实，未安装/离线不可用或无法运行原生 UI 须如实报告，不修改依赖锁以假称通过。

新配置元数据令旧二进制可能拒绝是预期的安全回退门槛，不能将可能拒绝写成旧版可运行。回退前停止隔离采集，使用证明兼容的停机合成副本或原备份；不得以旧程序覆盖新配置或历史。任何需要 DDL/真实 profile 迁移、公共合同改动、扩大白名单或真实设备行为时，停止并提交对应独立 Revision/批准。

### 隔离、跨应用验证与人工复验（r3 待批准）

1. **先决条件。** DS-004 r2 和 DAA-018 r3 的实施范围已分别批准，但当前均为 `qa_blocked`：前者 QA4 的真实原生及普通入口、后者 QA2 的真实原生及旧普通 native 安全拒绝尚未完成。此前 DAA 受控窗口退出后 CUA 可能重新绑定或启动默认真实 profile，实际影响未知。协调者/Human Owner 须先明确处理并解除 GUI/CUA 暂停，独立 Verification 完成两基础的必需检查，再由 Human Owner 分别最终验收；本方向及合成环境授权不代替这些 gate。本任务实施还须本 r3 自身精确批准。不得重新打开、扫描、复制、清理或回滚疑似真实数据来追证事故。
2. **任务自有目录。** 两应用分别在自身工程目录内新建唯一、原先不存在的 `.local/plc-json-<run-id>/`，各自放独立合成 profile、仅含测试值的 env、隔离构建/日志和临时输出；`<run-id>` 是每次显式替换的唯一值，不是可直接运行的字面路径。绝不使用任一 `.local/dev`、默认目录或真实配置/样本/凭据，绝不复制用户 profile。创建前验证父目录归属、非符号链接、目标不存在且不与现有资源交叉；Mac DAA 新 profile 根按现有指南先在可控父目录预建，不能把预建说成修复底层目录替换竞态。新 SQLite 可运行既有初始建库 DDL，不对已有库执行 DDL/迁移。
3. **env 与重启不可回落。** DAA 每次受控启动显式使用绝对 `DAA_ENV_FILE` 指向 DAA 任务自有可读普通文件，并用绝对 `DAA_PROFILE_DIR` 指向 DAA 任务 profile；路径无 `..` 和已有符号链接。每次重启都经同一受控入口传入完整参数，验证实际进程、应用身份与打开的同一合成 profile/实例 ID；不得经 Dock、名称重绑或无参数自动重启。先检验缺失、错误、失效路径和进程变量时受控入口明确停止、不启动默认 profile；这是对**受控入口**的要求，不能虚称普通产品无参数会拒绝默认路径。单靠启动后查看 UI 不能证明启动前没有写到错误目录。
4. **DS 特有阻塞。** DS 普通 bootstrap 即使进程指定 `DS_PROFILE_DIR`，仍先读取编译期源码根的 `.env`；本任务不得读取真实 `.env`。可评估在 DS 任务根建立不含用户 `.env`、`.local`、私有输入和真实数据的源码快照，在其编译根使用自己的空/合成 env 与绝对任务 profile，以全新任务专属 Cargo target 构建；按实际依赖包含必要的 `shared/tia-import-core` 和 `console-ui`，逐文件比较正式交付候选与快照，并记录锁文件、编译路径、二进制及 profile 身份。快照普通入口证据不能冒称正式工作树普通入口已验证，也不能取代 DS-004 原有 DS4-07 证据。若无法在不读取真实配置的前提下证明正式入口和候选一致，或无法确定重启不回落，保持 blocker 并回 PM，不能启动。
5. **WebKit / CUA 独立门槛。** 独立 SQLite profile 不是 WebKit、应用身份、系统缓存或自动化绑定隔离：DS 用 profile UUID 配置 WebView store，但系统进程/缓存落点仍需验证；DAA 正式默认窗口未按 profile 单独指定 WebKit store。此前唯一 bundle + incognito 也未阻止异常，incognito 不能证明正式列宽跨重启持久化。须在独立 macOS 用户或隔离 macOS 环境、或经证实等价的环境中，证明任务账户对自有 `.local` 有权限且无法触达真实用户配置；明确 App/bundle/进程身份、持久 WebKit store、实际 OS/XPC 数据落点及退出、重开后身份。不得因目录不同、名称相同或 CUA 旧绑定就推定安全；不能证明不会按应用名重新绑定/拉起默认应用时，改用受控人工操作并保持 CUA 禁用。所需平台身份/目录不可安全建立时标记 blocked，不能用临时 incognito 或合成 DOM 冒称原生通过。
6. **受控 S7。** 仅使用自建合成实例及本机 `127.0.0.1` 非特权端口；先核对端口和进程归属，不杀未知进程、不静默换端口。DAA 预先禁止自动采集和上报，只在确认该合成目标与本机 DS listener 身份后显式连接、分组和采集；不访问现场网络、外部服务或真实设备。DAA 的 `DAA_PLC_READ_ALLOWED` 按当前代码是进程变量（缺失默认允许，env 文件中的同名键被忽略）；准备阶段可显式设 false，确需环回采集时须在受控进程中显式许可并重新核验唯一目标。`local-validation` feature 使用 fixture/禁止真实 S7，不能当作真实 loopback 读取证据；DS 原生 `test-automation` 受固定 manifest/scenario 约束，也不能自动代表普通产品入口。
7. **可复验与清理。** 两份用户手册中英文版本各记录本应用侧可复验步骤及相互链接：隔离前提、创建全新任务根和合成数据、每次启动/重启参数及身份核验、DS 多实例逐个导出和 DAA 选同一文件导入/分组/保存/激活/显式采集、每一步可观察结果、已知 blocker 和停止条件。具体产品入口和截图只能在实现且验证后记录，不能把拟议入口写成现成能力。测试结束、必要 DEV/独立 QA 证据已写入各自 bundle 且无进程或后续验证依赖后，先核对任务 marker、实际路径、PID/句柄及所有权，再清理本次两处自有 `.local` 根和可证明属于本次的系统资源；不清理用户、其他任务或归属不明的 profile/WebKit/日志。无法证明归属或退出则停止清理并如实报告；保留任务文档中的非敏感候选标识、源 revision、文件 SHA、验证结果及可重新创建的操作步骤，不保留实际测试数据或伪称清理成功。

## 9. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品、数据库或测试。批准后 Development 根据触达面使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及治理规则独立复核。Development 自检或 QA 通过均不自动授权真实设备、上线、数据库迁移或 Human Owner 最终验收。

## 附录 A：r2 完整原文（含 r1 历史，非活动规格）

r2 SHA-256: c2798d12541a74a4a400f4358059bb136d47538a9083b9cc48040dacbf619267

~~~~~~~~~~~~~~~~markdown
Task ID: DAA-017
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 设计 r3 获批、DS-004 与 DAA-018 均 STD 最终验收，且 Human Owner 精确批准 DAA-017 r2 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 将逐 PLC 完整 S7 点位 JSON 作为可追溯目录来源导入 DAA 草稿
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r2; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r3 设计批准；DS-004 和 DAA-018 各自完成 STD 至 Human Owner 最终验收；跨应用端到端验收依赖 device-simulator::DS-003 r2 的实际导出候选

# DAA-017：按 PLC 导入完整点位 JSON

## 1. 状态、目标与范围

**本任务为 draft / r2，尚未获得实施批准。** 2026-11-16 Human Owner 批准 ARCH-PLC-001 r2 设计范围，2026-11-17 要求先完成两端双语基础再做导出/导入、保留描述且不增加显示名上报。[ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获 Human Owner 批准；本任务基于该设计形成，实施范围仍待精确批准。旧 r1 未获实施批准。r3 设计获批、DS-004 和 DAA-018 各自完成 STD 至 Human Owner 最终验收，且本 r2 精确批准后，才可启动本任务 Development。DS-003 是另一独立 owner 和验收链。

目标：用户选择一份 PLC 点位 JSON，预览并确认新建或匹配本地 PLC，将完整目录及来源写入草稿；无需再次提供该 PLC 的原始 `.db` / `.udt`，经本地选择组、启用、保存和显式激活后，受控 S7 采集可以读取。保留 BOOL、INT、REAL、STRING 等所有声明点和停用点，不把来源启用事实当成 DAA 采集权限。导入确认不自动激活、连接、采集、上报或改写其他实例。

本切片只实现 DAA 输入、来源完整性和现有编辑/激活兼容。DS 导入、DAA 导出、本地新增点生成 `daa.catalog_snapshot`、FF 适配、正式发布公共跨运行时合同、其他协议、DDL、真实 profile/数据库迁移和现场采用另立范围；不得将父设计批准视为这些实施批准。

## 2. 同一输入合同与严格验证

输入**只接受** [ARCH-PLC-001 r3 §3–5、§7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 `aiis.plc_points` / 整数 `schema_version: 1` 候选：一次文件是一台 PLC、至少一个 DB，每 DB 至少一个点。它既可声明 `export.producer=device_simulator`，也可声明 `data_acquisition_agent`；本任务支持两者的合同验证及导入，不要求本次实现 DAA 导出。不得创造第二种受限 DS 格式。以下示例逐字复制父规格，示例摘要只是词法，不代表真实保存内容。

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

1. 从用户选择的文件读取并计算**原始字节** SHA-256；严格 UTF-8 无 BOM，大小上限 1 MiB、层级 16、至多 32 DB / 4096 点；拒绝重复 key、未知字段、错误版本、非整数字面量、null/隐式转换、非法 UUID v4、重复/跨类别 ID、名字重复及其他父合同负例。对所有点和禁用点同等检查物理范围、类型宽度、BOOL bit 与重叠，包括 `STRING[n]` n=1..254、ASCII 及 n+2 字节。未知类型或任何坏点使整台导入失败，不跳过、不更名、不推算偏移。`export.payload_sha256` 是导出方声明的配置原字节摘要，不能拿输入 JSON 的摘要冒充或宣称已验证到源配置；本地保存输入原字节及自己的摘要。
2. 来源启用只按 `export.producer` 解读：DS 导出时 DB `source_enabled` 必填且取 DS DB 事实；DAA 导出时该字段必须缺省；点层两种 producer 均必填实际布尔值。DB 字段缺省不是 true/false，null、错误分型或缺失点层字段拒绝；`origin.kind` 仅是身份命名空间，不能据此推断最后导出者。所有源启用值保存在可校验的归档原文并展示；新建的 DAA PLC/点默认不启用、不分组，不从源值推导采集许可。已存在点的本地 enabled/组及周期默认保留，差异展示后须由用户使用现有本地设置明确改变。
3. `display_names` 可缺省，缺省对新点为两值 `""`、对已有点默认保持本地；存在时恰有 `zh-CN`/`en-US` 两字符串（各 ≤256 UTF-8 字节），允许显式空串，缺键、null、其他键、非字符串或超限拒绝。输入两个值逐点预览并以本地点 UUID 写入 DAA-018 的 `pointDisplayNames`；空语言不从 name、另一语言、路径、comment 或旧值推测。原有可选 `display_name` ≤256 字节，独立保存到可省略 `pointLegacyDisplayNames`（UUID→原字符串）并标注语言未标记，不写进双语字段、name 或 comment；原始 JSON 内容、字段有无及 bytes/SHA 全部归档。空旧值在本地可省略，但归档保留原文；无任何本地记录等于未提供，重导时由原文 presence 区分。
4. `description` 可缺省；缺省不清空已有 DAA comment，新点无描述则 comment 空。非空值来自输入、最多 500 UTF-8 字节，新点经用户确认后原样写入现有 comment；已有非空或已编辑 comment 与输入不同需预览并显式选择保留或采用。文件显式 `description: ""` 表达来源为空，对已有非空 comment 须明确确认才能清空；源原文、历史版本和用户未选中的点始终保留。description、comment 和显示名语义独立，不以任何显示名冒充描述，也不增加上报字段。
5. `connection` 是客户端目标，预览并要求用户明确核对/确认，可在确认前编辑目标；仅允许规范 IPv4 单播、合法 port/rack/slot，保留项目的端点唯一和 PLC 数量等校验。`0.0.0.0`、非法地址和非默认 TSAP（DAA 当前没有自定义 TSAP 模型）明确阻断；loopback 提示仅同机有效。不得试连以测试地址或自动连接真实 PLC。来源输出摘要不证明设备布局、设备许可、文件真实性或物理可达性。

## 3. 交互、身份、差异与原子提交

1. 选择一个 JSON 文件；在导入流程内可新建 PLC，或显式选择已有 PLC。预览目标、外部 origin、生产者、导出版本、输入 SHA、连接、全部 DB/点和不可支持项；界面将目录点列表与 TIA 结构树区分。新目标可生成预览用本地 UUID，但只有确认成功才持久化。取消或只预览不写草稿、来源档案、活动版本、设备、上报或用户文件。
2. 外部身份是 `(origin.kind, origin.profile_id, origin.plc_id, db.id, point.id)`，不以名称、IP、DB 号或相似地址自动认同。首次新建时 ID 在本地全局可用可保留，否则分配新本地 UUID 并持久映射，预览给出对应关系；映射到未绑定的既有 PLC/DB/点须逐项一一匹配并显式确认。同一个目标已绑定不同 origin 时阻断，不合并、不覆盖、不冒充单一来源。origin 是身份命名空间，不声称所有点都由 DS 创建。
3. 已有映射按外部身份稳定匹配并保留本地 PLC/DB/点 UUID、组/周期与历史引用。相同文件、相同目标、有效映射且无本地显示名/comment 冲突时再次导入无变化：不产生新的草稿 ETag、版本或重复源。名称、类型、地址、源启用事实等变化列出前后和影响，物理地址/类型变化及覆盖冲突须用户明确决定；DB 编号变化、同一外部 ID 归属冲突、不同 origin、文件缺少目标匹配 DB 里的任何点或目标含文件未声明额外点，一律阻断整 PLC，保持原草稿和源归档，不因点未启用或无历史而放宽。不得依次部分覆盖或静默删除。
4. 对两个显示语言、未标记 `display_name` 和 description/comment 分别进行三方比较：上次已确认源原文与 SHA 为来源基准，同时展示本地当前值和本次文件值（区分缺字段与显式空串）。已有点输入与本地不同，或本地在基准后编辑时，须让用户逐项选择保留本地/采用输入；缺字段默认保留，若选显式空串清空已有值必须确认。新目标直接按确认预览保存输入各值。逐项选择、绑定和基准与原文归档在同一 CAS 事务提交；同文件且来源基准未变、用户保留当前值时不改变 ETag；若新文件 bytes/SHA 已变，即使选择保留本地名称，来源归档或绑定基准发生变化仍可使草稿 ETag 正常改变。用户明确恢复/清空也按正常编辑改变草稿。不得依文件名、技术名或地址自动改身份。
5. 有界预览 token 绑定输入原字节 SHA、目标、候选映射、端点选择、当前草稿 ETag 和有效期。文件、目标、选择、映射或草稿改变即失效；确认时在引擎侧重算并进行 CAS。并发、重复确认、超时、取消、断电/提交失败和结果未知时不得留半条来源/绑定/草稿；结果未知先按现有机制重读判断，不盲目重复写。确认事务提交前核算输入、完整配置 payload、归档及容量预算，超限整台拒绝，不因单文件小于 1 MiB 而忽略目标整体容量。
6. 新点保留但默认不采集：用户随后显式选择现有组，或新建组、确认周期并批量选择点/启用；未选点保留为未分组/停用。现有 PLC/组启用开关、组周期、active/loaded、上报绑定和已有启动选项原样保持；导入不更改 DAA-015 的既有自动启动设置，也不对与本次导入无关的活动配置承诺停止。显示可激活性和既有 runtime 资源预算，超限则阻断激活并指出原因，不裁剪文件。运行时版本 4 的每 DB 512 启用点与相关采集/编码预算、旧 runtime 的组限额仍按现有规则执行。

## 4. 目录来源与可验证配置

当前 DAA `Db.source_id` 必须指向本 PLC 的真实 SourceDocument，原 DB/UDT 启用点受 `Db.tree` 和 `leaf_matches`、源/UDT 闭包与布局校验保护。**不得伪造 `.db`/`.udt`、TIA 源行或来源树，也不得整体关闭旧校验。** 本切片优先实现父设计的 schema version 1 可选目录分型：

- 按一次输入在目标 PLC 建立一个逻辑 catalog SourceDocument，保存所选完整原始 UTF-8 内容及 SHA；同一输入包含多个 DB 时，各 DB 的 `source_id` 指向同一个逻辑源，每 DB 的绑定指向自己的外部 DB。其他 PLC 的逻辑源独立；相同 SHA/字节物理归档可复用现有全局策略，不重写历史来源。来源变更时先保留原归档，不能原位篡改旧版本依赖材料。
- 配置增加可省略 `catalogBindings`：每项含 `localDbId`、`sourceId`、`sourceSha256`、`sourceKind=exchange_json`、`originDbId` 和 `pointMappings`，后者每项含 `localPointId`、`catalogPointId` 以及可选 `localOverride`；另含可选的按字段显示名/描述冲突确认元数据，记录最后确认 source SHA、字段 presence、源值及所选本地值，缺项不得伪称来自源。其 PLC 从本地 DB 关联确定，不信任外部传入的本地 PLC；重算源 SHA、解析封闭合同并检查单一 origin、source_id 与所属 PLC、外部 DB/点、本地 DB/点、成员身份及每边完整一一对应。重复、缺失、伪造、错 hash、跨 PLC、越界、重叠、类型/地址不符均拒绝。一个本地 PLC 同一外部文件的 DB 共用一个逻辑源，同一 originDbId 不得被绑定两次。
- 仅对有效 catalog binding 走目录校验分支，以完整的 DB/点关联替代 DB/UDT 专属的 `db_number` / `importBinding` 和 `leaf_matches` 条件；`Db.complete` 表示目录点集完整，不表示原 TIA 工程完整，`tree` 可为空。原 DB/UDT 分支仍执行原来的树、leaf、source_id、UDT 及地址验证。外部 `source_path` 缺省时不能伪造：当前 Point 字段若必须为字符串，目录分支用空字符串表达没有路径、以明确 catalogPointId 追溯且 UI 显示未提供；若存在逻辑路径按原值保留，不把它当磁盘路径。双语显示名使用基础任务的配置级 `pointDisplayNames`；无语言单条使用 `pointLegacyDisplayNames`（本地 UUID→字符串，非空存、空可省略），两者均不得添加到 Point/PointFact。description 可按明确选择进入既有 Point.comment。原文独立归档，不能伪造或静默丢弃。
- 经用户在预览中确认后，目录地址以 `Address.confirmed=true`、`origin=catalog` 和真实确认原因进入本地配置；该 origin 仅在有效目录绑定下合法。已导入点使用现有编辑流程修改类型或地址时，必须显式确认，记录 `localOverride` 的原 source SHA、新 dataType/offset/可选 bit 和确认原因；重验重叠及所有布局。新源中该点的基准变更时，列明与 override 的冲突并由用户选择保留或采用，不能将旧覆盖静默套用。禁止用普通保存接口伪造或删除绑定/覆盖来绕过引擎校验。若尝试在目录 DB 中新增旧原文未包含的点，本切片明确拒绝并提示后续单独设计的内部快照操作，不生成假来源或不完整映射。
- 保留 `schema_version=1` 和两库现有物理 DDL：可选字段在没有目录来源时省略，以保证旧 payload 新程序零写读。必须验证新旧二进制兼容，而非将加可选字段视作自动兼容：含新绑定的 payload 应让旧二进制安全拒绝，不能静默按旧树运行或新建空库；已有原生配置、样本、不可变 payload/sha 不被重写。若受现有校验、预算或兼容性限制不能满足此方案，停止并回 PM；任何双 SQLite CHECK/物理 schema 调整、已使用 profile 迁移、备份恢复须另立 schema-maintenance 范围和批准，本任务不暗中升级。

## 5. 历史样本和事实契约保护

双语与未标记显示名始终不进入 Point、PointFact.definition，也不混入 name/comment/value 或任何外发字段；沿用 DAA-018 的配置级存储。输入目录身份不等于 DAA 的 instanceId、plcId、sourceGeneration、采样 ID/sequence 或上报绑定；不自动创建、替换或合并它们。既有 active/used 版本、样本原始 bytes/SHA、历史、排队/冻结上报和 ACK 维持原状；不追溯更改旧样本的定义。`PointFact.definition` 包含本地 Address，因此只在新采样中可能出现 `origin=catalog`：必须用真实 DAA 本地事实校验器/manifest 和序列化链路验证新旧样本可读，再验证输出的既有 `plc-facts/v2` 上报 body 与当前合同一致；当前 plc-facts/v2 单样本 Point 不包含 Address/origin，不能往其中新增字段；历史 batch 可能按原合同含 Point 定义/Address，须对该路径按原样验证，不能宣称所有路径原本都没有这些字段。同样核查 v2 单样本、历史 facts_wire batch/冻结和可触达旧采集/快照路径；用户保存激活新配置可正常产生新 configRevision，不要求新旧样本字节相同；旧样本、历史、冻结正文及回执不得重写。受控测试不发网络请求。若接收方既有合同或旧历史无法兼容，标记阻塞并回 PM，不能修改公共合同、后端或悄悄丢弃定义。

## 6. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/data-acquisition-agent/` 为根；花括号仅展开列名，不是通配符。仅改列出的本切片相关内容；需要额外文件先回 PM 修订。当前 PM 只写本 `spec.md`，角色文档各按 STD 创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 模型、来源校验 | `src-tauri/src/domain/{mod.rs,local_configuration.rs}`；`src-tauri/src/services/{mod.rs,local_configuration.rs,local_supervisor.rs,local_activation.rs}` | `src-tauri/src/domain/plc_catalog.rs`；`src-tauri/src/services/catalog_import.rs` |
| 本地存储与桌面桥 | `src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；`src-tauri/src/commands/local_acquisition.rs`；`src-tauri/src/lib.rs` | `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` |
| UI 与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/components/SourceImportPanel.vue`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/plc/components/CatalogImportDialog.vue` |
| 回归和说明 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs,delivery_tests.rs,sample_upload_tests.rs}`（仅相关回归需要时）；`src-tauri/src/services/local_delivery_tests.rs`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `tests/plc-catalog-import.test.mjs`；`tests/fixtures/plc-catalog-v1.json`；`CODE_INDEX.md`（实际结构发生变化时按仓库契约新建） |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后 Development 创建本 bundle `tasks.md`；交接后独立 Verification 创建 `checklist.md` |

禁止修改 `schema.rs`、迁移/DDL、Cargo 或 pnpm 依赖及锁、`.env`、用户数据库/profile、样本/队列/回执、原始 DB/UDT 文件、DS/FF/backend 源码、根 contracts、其他任务。允许测试只在全新隔离 profile 与自有临时输出；网络 POST、现场设备和真实数据库均不在范围。新可见文案中英文键成对；新增或触达的业务表复用公共列宽组件：普通列可拖拽、有最小宽和横向滚动，刷新/切页/重启按稳定字段恢复，可恢复默认；功能列可固定，偏好不写业务配置。

## 7. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DA01 | 父规格示例及受控多 DB 合成文件对两种合法 producer 通过；严格拒绝重复 key、BOM、非法 UTF-8、未知字段/版本、非法整数/UUID/null、超限、重复身份与空点集，逐个报告具体原因且没有写入。 |
| DA02 | 包含 BOOL、INT、REAL、STRING、不同 BOOL bit 与禁用点的完整文件无丢点导入；比较原始 bytes/SHA、点 ID 对应、名称、类型、地址、范围及原启用事实。DB/点字段按 producer 分型检查：DS DB 缺失、DAA DB 存在、点缺失/null 均拒绝；源点 true 不导致 DAA 自动采集。 |
| DA03 | BOOL bit、非 BOOL bit、非法 STRING 长度、越界、物理重叠、无效名称/类型和禁用点错误均阻断整台；客户端地址/端口与 TSAP、同机 loopback 提示及不连接行为明确可验。 |
| DA04 | 一个 PLC 多 DB 引用同一真实目录 source，source_id、原文 SHA、origin、DB/点映射全链一致；伪造 source、错 SHA/DB/点/类型/地址、重复或跨 PLC 引用均无法保存或激活。旧 DB/UDT 完整树、leaf_matches、UDT 及源校验正反例行为不变，目录 UI 不显示伪造 TIA 树。 |
| DA05 | 新建和既有 PLC 映射经显式确认，ID 冲突安全分配且映射稳定；同文件且无本地冲突重导 ETag 不变；改名/地址/类型和 source_enabled 差异可见并按规则确认；缺点、额外点、DB 改号、跨 origin 阻断，原草稿字节/ETag 和历史不变。 |
| DA06 | 地址/类型人工覆盖有 SHA 基准、理由和后续源变更冲突；普通保存接口不能伪造绑定或覆盖；目录 DB 本地新增点被明确阻断，既有原始来源和历史版本完整。 |
| DA07 | 预览取消、切换目标/文件、过期 token、草稿并发变化、容量/事务失败与重复提交均无部分来源、映射或写入；未知结果先重读，不能盲重试。 |
| DA08 | 新 PLC/点默认不采集；用户显式分组、周期、启用、保存和激活，资源限额有定位并可阻断；原有组/周期、active/used、启动设置及未选 PLC 不因导入被改变。双语、表格列宽与恢复默认按 §6 验证。 |
| DA09 | 用自有旧合成 profile 副本核验新程序读取旧 schema 1 原 bytes/SHA 不变；旧二进制遇新目录 payload 安全拒绝且不产生空库；双库物理 schema、旧版本、样本及来源原文无变更。不能以空配置通过此项。 |
| DA10 | 自有合成旧样本和新 catalog 样本经原本地定义/manifest 解码，导入前后旧样本、pending 和 ACK bytes/SHA 一致；v2 单样本及历史 batch 等各自按既有合同验证，不新增显示名或字段、不混入 name/comment/value；允许新 configRevision，未发网络 POST。 |
| DA11 | 独立端到端：使用实际 **DS-003 候选导出器**对受控 DS saved revision 导出的原文件（记录候选、revision、文件 SHA），在全新隔离 DAA profile 导入；不额外提供或重复导入原 `.db` / `.udt`，用户完成必要分组、启用、保存、激活后，通过自有 loopback DS S7 真正读取 BOOL、INT、REAL，并核对本地/外部 ID、地址、类型、预设值与质量；同时证明停用点仍在草稿/保存配置。DS/DAA 候选均须可追溯，建议 DS-003 已通过 fresh QA；合成 JSON 单测或仅解析不能替代此项。 |
| DA12 | 实际交付树和锁文件执行相关 Rust/Node 测试、类型检查、前端构建、`rust-snap7-driver` 检查和 macOS 原生交互；记录真实命令、退出码、隔离路径、证据、未执行项与清理。其他平台及现场未测不得声称已通过。 |
| DA13 | 输入双语两值、单侧空、字段缺省、原无语言单条和超限/错误类型均按 r3 验证；用户预览后准确保存到按本地点 ID 的独立映射，顶栏语言不改变配置；原文件字节、旧 comment 与 name 不被显示名替代。 |
| DA14 | description 非空经确认进入新点 comment，已有 comment 冲突选择保留/采用可验；缺字段不清空、显式空串清空需确认；本地编辑后重导显示基准/本地/输入三方差异，同文件取消和保留不误写；明确恢复/清空或新源归档/绑定基准变化可正常改变草稿，旧源和历史 revision 不动。 |

## 8. 实施依赖、验证和停止条件

r3 设计精确批准、DS-004 与 DAA-018 各自完成 STD 最终验收，且 Human Owner 精确批准本 r2 后，Development 才创建 `tasks.md`、实施并自检，交 developer_handoff；fresh-context Verification 独立创建 checklist、复核精确交付候选；Human Owner 最终验收另行决定。DAA 格式、来源、原子性等单端工作可先用受控合成文件自检；DA11 必须等待可追溯的 DS-003 实际导出结果和 DAA-017 实际导入结果，不能将 fixture 冒称跨应用或真实设备联调。

在独立批准的实施与 QA 阶段，仅使用自有新合成数据、两个应用各自全新隔离 profile、隔离临时目录及非特权 IPv4 loopback；不得使用用户原有 dev 联调 profile、数据库或真实设备。受控测试负责进程、文件和端口生命周期；记录候选、来源、证据及清理，无法安全执行则报告 blocked/not_run。

项目工具链为 `pnpm@11.11.0` 与 Cargo/Rust，普通入口 `pnpm tauri dev`。拟议检查示例：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver`、`node --test tests/plc-catalog-import.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR` 和 `RUN_DIR` 指向任务自有隔离临时目录。命令需由 Development 按实际测试入口核实，未安装/离线不可用或无法运行原生 UI 须如实报告，不修改依赖锁以假称通过。

新配置元数据令旧二进制可能拒绝是预期的安全回退门槛，不能将可能拒绝写成旧版可运行。回退前停止隔离采集，使用证明兼容的停机合成副本或原备份；不得以旧程序覆盖新配置或历史。任何需要 DDL/真实 profile 迁移、公共合同改动、扩大白名单或真实设备行为时，停止并提交对应独立 Revision/批准。

## 9. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品、数据库或测试。批准后 Development 根据触达面使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及治理规则独立复核。Development 自检或 QA 通过均不自动授权真实设备、上线、数据库迁移或 Human Owner 最终验收。

## 附录 A：r1 原始未批准草案（历史）

原始 SHA256: `a304916dea51a2222bc73791846eeb67bb6e97241fc7ba5b8f350c500ec7cd14`；围栏内原字节含末尾换行，供追溯，不是当前实施范围。

~~~~~~~~markdown
Task ID: DAA-017
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 批准精确 DAA-017 r1 -> Development tasks.md / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 将逐 PLC 完整 S7 点位 JSON 作为可追溯目录来源导入 DAA 草稿
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立完成 STD 全部 gate；不继承其他任务的实施批准或验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r2; device-simulator::DS-003 r1; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: aiis-ics-arch::ARCH-PLC-001 r2 设计范围；跨应用端到端验收依赖 device-simulator::DS-003 r1 的实际导出候选

# DAA-017：按 PLC 导入完整点位 JSON

## 1. 状态、目标与范围

**本任务为 draft / r1，尚未获得实施批准。** Human Owner 于 2026-11-16（Asia/Shanghai）批准 [ARCH-PLC-001 r2](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的设计范围，要求按 STD 优先拆分 DS 导出和 DAA 导入、暂不改代码；此批准不代替本任务精确 r1 的实施批准、独立 QA 或最终验收。DS-003 是另一 owner、另一独立验收链的任务。

目标：用户选择一份 PLC 点位 JSON，预览并确认新建或匹配本地 PLC，将完整目录及来源写入草稿；无需再次提供该 PLC 的原始 `.db` / `.udt`，经本地选择组、启用、保存和显式激活后，受控 S7 采集可以读取。保留 BOOL、INT、REAL、STRING 等所有声明点和停用点，不把来源启用事实当成 DAA 采集权限。导入确认不自动激活、连接、采集、上报或改写其他实例。

本切片只实现 DAA 输入、来源完整性和现有编辑/激活兼容。DS 导入、DAA 导出、本地新增点生成 `daa.catalog_snapshot`、FF 适配、正式发布公共跨运行时合同、其他协议、DDL、真实 profile/数据库迁移和现场采用另立范围；不得将父设计批准视为这些实施批准。

## 2. 同一输入合同与严格验证

输入**只接受** [ARCH-PLC-001 r2 §3–5、§7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 `aiis.plc_points` / 整数 `schema_version: 1` 候选：一次文件是一台 PLC、至少一个 DB，每 DB 至少一个点。它既可声明 `export.producer=device_simulator`，也可声明 `data_acquisition_agent`；本任务支持两者的合同验证及导入，不要求本次实现 DAA 导出。不得创造第二种受限 DS 格式。以下示例逐字复制父规格，示例摘要只是词法，不代表真实保存内容。

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

1. 从用户选择的文件读取并计算**原始字节** SHA-256；严格 UTF-8 无 BOM，大小上限 1 MiB、层级 16、至多 32 DB / 4096 点；拒绝重复 key、未知字段、错误版本、非整数字面量、null/隐式转换、非法 UUID v4、重复/跨类别 ID、名字重复及其他父合同负例。对所有点和禁用点同等检查物理范围、类型宽度、BOOL bit 与重叠，包括 `STRING[n]` n=1..254、ASCII 及 n+2 字节。未知类型或任何坏点使整台导入失败，不跳过、不更名、不推算偏移。`export.payload_sha256` 是导出方声明的配置原字节摘要，不能拿输入 JSON 的摘要冒充或宣称已验证到源配置；本地保存输入原字节及自己的摘要。
2. 来源启用只按 `export.producer` 解读：DS 导出时 DB `source_enabled` 必填且取 DS DB 事实；DAA 导出时该字段必须缺省；点层两种 producer 均必填实际布尔值。DB 字段缺省不是 true/false，null、错误分型或缺失点层字段拒绝；`origin.kind` 仅是身份命名空间，不能据此推断最后导出者。所有源启用值保存在可校验的归档原文并展示；新建的 DAA PLC/点默认不启用、不分组，不从源值推导采集许可。已存在点的本地 enabled/组及周期默认保留，差异展示后须由用户使用现有本地设置明确改变。
3. `connection` 是客户端目标，预览并要求用户明确核对/确认，可在确认前编辑目标；仅允许规范 IPv4 单播、合法 port/rack/slot，保留项目的端点唯一和 PLC 数量等校验。`0.0.0.0`、非法地址和非默认 TSAP（DAA 当前没有自定义 TSAP 模型）明确阻断；loopback 提示仅同机有效。不得试连以测试地址或自动连接真实 PLC。来源输出摘要不证明设备布局、设备许可、文件真实性或物理可达性。

## 3. 交互、身份、差异与原子提交

1. 选择一个 JSON 文件；在导入流程内可新建 PLC，或显式选择已有 PLC。预览目标、外部 origin、生产者、导出版本、输入 SHA、连接、全部 DB/点和不可支持项；界面将目录点列表与 TIA 结构树区分。新目标可生成预览用本地 UUID，但只有确认成功才持久化。取消或只预览不写草稿、来源档案、活动版本、设备、上报或用户文件。
2. 外部身份是 `(origin.kind, origin.profile_id, origin.plc_id, db.id, point.id)`，不以名称、IP、DB 号或相似地址自动认同。首次新建时 ID 在本地全局可用可保留，否则分配新本地 UUID 并持久映射，预览给出对应关系；映射到未绑定的既有 PLC/DB/点须逐项一一匹配并显式确认。同一个目标已绑定不同 origin 时阻断，不合并、不覆盖、不冒充单一来源。origin 是身份命名空间，不声称所有点都由 DS 创建。
3. 已有映射按外部身份稳定匹配并保留本地 PLC/DB/点 UUID、组/周期与历史引用。相同文件、相同目标及有效映射再次导入是无变化：不产生新的草稿 ETag、版本或重复源。名称、类型、地址、源启用事实等变化列出前后和影响，物理地址/类型变化及覆盖冲突须用户明确决定；DB 编号变化、同一外部 ID 归属冲突、不同 origin、文件缺少目标匹配 DB 里的任何点或目标含文件未声明额外点，一律阻断整 PLC，保持原草稿和源归档，不因点未启用或无历史而放宽。不得依次部分覆盖或静默删除。
4. 有界预览 token 绑定输入原字节 SHA、目标、候选映射、端点选择、当前草稿 ETag 和有效期。文件、目标、选择、映射或草稿改变即失效；确认时在引擎侧重算并进行 CAS。并发、重复确认、超时、取消、断电/提交失败和结果未知时不得留半条来源/绑定/草稿；结果未知先按现有机制重读判断，不盲目重复写。确认事务提交前核算输入、完整配置 payload、归档及容量预算，超限整台拒绝，不因单文件小于 1 MiB 而忽略目标整体容量。
5. 新点保留但默认不采集：用户随后显式选择现有组，或新建组、确认周期并批量选择点/启用；未选点保留为未分组/停用。现有 PLC/组启用开关、组周期、active/loaded、上报绑定和已有启动选项原样保持；导入不更改 DAA-015 的既有自动启动设置，也不对与本次导入无关的活动配置承诺停止。显示可激活性和既有 runtime 资源预算，超限则阻断激活并指出原因，不裁剪文件。运行时版本 4 的每 DB 512 启用点与相关采集/编码预算、旧 runtime 的组限额仍按现有规则执行。

## 4. 目录来源与可验证配置

当前 DAA `Db.source_id` 必须指向本 PLC 的真实 SourceDocument，原 DB/UDT 启用点受 `Db.tree` 和 `leaf_matches`、源/UDT 闭包与布局校验保护。**不得伪造 `.db`/`.udt`、TIA 源行或来源树，也不得整体关闭旧校验。** 本切片优先实现父设计的 schema version 1 可选目录分型：

- 按一次输入在目标 PLC 建立一个逻辑 catalog SourceDocument，保存所选完整原始 UTF-8 内容及 SHA；同一输入包含多个 DB 时，各 DB 的 `source_id` 指向同一个逻辑源，每 DB 的绑定指向自己的外部 DB。其他 PLC 的逻辑源独立；相同 SHA/字节物理归档可复用现有全局策略，不重写历史来源。来源变更时先保留原归档，不能原位篡改旧版本依赖材料。
- 配置增加可省略 `catalogBindings`：每项含 `localDbId`、`sourceId`、`sourceSha256`、`sourceKind=exchange_json`、`originDbId` 和 `pointMappings`，后者每项含 `localPointId`、`catalogPointId` 以及可选 `localOverride`。其 PLC 从本地 DB 关联确定，不信任外部传入的本地 PLC；重算源 SHA、解析封闭合同并检查单一 origin、source_id 与所属 PLC、外部 DB/点、本地 DB/点、成员身份及每边完整一一对应。重复、缺失、伪造、错 hash、跨 PLC、越界、重叠、类型/地址不符均拒绝。一个本地 PLC 同一外部文件的 DB 共用一个逻辑源，同一 originDbId 不得被绑定两次。
- 仅对有效 catalog binding 走目录校验分支，以完整的 DB/点关联替代 DB/UDT 专属的 `db_number` / `importBinding` 和 `leaf_matches` 条件；`Db.complete` 表示目录点集完整，不表示原 TIA 工程完整，`tree` 可为空。原 DB/UDT 分支仍执行原来的树、leaf、source_id、UDT 及地址验证。外部 `source_path` 缺省时不能伪造：当前 Point 字段若必须为字符串，目录分支用空字符串表达没有路径、以明确 catalogPointId 追溯且 UI 显示未提供；若存在逻辑路径按原值保留，不把它当磁盘路径。其他可选展示字段保留在可追溯原文，不能伪造或静默丢弃。
- 经用户在预览中确认后，目录地址以 `Address.confirmed=true`、`origin=catalog` 和真实确认原因进入本地配置；该 origin 仅在有效目录绑定下合法。已导入点使用现有编辑流程修改类型或地址时，必须显式确认，记录 `localOverride` 的原 source SHA、新 dataType/offset/可选 bit 和确认原因；重验重叠及所有布局。新源中该点的基准变更时，列明与 override 的冲突并由用户选择保留或采用，不能将旧覆盖静默套用。禁止用普通保存接口伪造或删除绑定/覆盖来绕过引擎校验。若尝试在目录 DB 中新增旧原文未包含的点，本切片明确拒绝并提示后续单独设计的内部快照操作，不生成假来源或不完整映射。
- 保留 `schema_version=1` 和两库现有物理 DDL：可选字段在没有目录来源时省略，以保证旧 payload 新程序零写读。必须验证新旧二进制兼容，而非将加可选字段视作自动兼容：含新绑定的 payload 应让旧二进制安全拒绝，不能静默按旧树运行或新建空库；已有原生配置、样本、不可变 payload/sha 不被重写。若受现有校验、预算或兼容性限制不能满足此方案，停止并回 PM；任何双 SQLite CHECK/物理 schema 调整、已使用 profile 迁移、备份恢复须另立 schema-maintenance 范围和批准，本任务不暗中升级。

## 5. 历史样本和事实契约保护

输入目录身份不等于 DAA 的 instanceId、plcId、sourceGeneration、采样 ID/sequence 或上报绑定；不自动创建、替换或合并它们。既有 active/used 版本、样本原始 bytes/SHA、历史、排队/冻结上报和 ACK 维持原状；不追溯更改旧样本的定义。`PointFact.definition` 包含本地 Address，因此只在新采样中可能出现 `origin=catalog`：必须用真实 DAA 本地事实校验器/manifest 和序列化链路验证新旧样本可读，再验证输出的既有 `plc-facts/v2` 上报 body 与当前合同一致；当前上报 Point 不包含 Address/origin，不能往其中新增字段。受控测试不发网络请求。若接收方既有合同或旧历史无法兼容，标记阻塞并回 PM，不能修改公共合同、后端或悄悄丢弃定义。

## 6. 拟议 Development 允许文件（当前不授权写入）

路径均以 `automation-world/data-acquisition-agent/` 为根；花括号仅展开列名，不是通配符。仅改列出的本切片相关内容；需要额外文件先回 PM 修订。当前 PM 只写本 `spec.md`，角色文档各按 STD 创建。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 模型、来源校验 | `src-tauri/src/domain/{mod.rs,local_configuration.rs}`；`src-tauri/src/services/{mod.rs,local_configuration.rs,local_supervisor.rs,local_activation.rs}` | `src-tauri/src/domain/plc_catalog.rs`；`src-tauri/src/services/catalog_import.rs` |
| 本地存储与桌面桥 | `src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；`src-tauri/src/commands/local_acquisition.rs`；`src-tauri/src/lib.rs` | `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` |
| UI 与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/components/SourceImportPanel.vue`；`src/app/plc/views/points/index.vue`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | `src/app/plc/components/CatalogImportDialog.vue` |
| 回归和说明 | `src-tauri/src/infrastructure/local_store/{source_import_tests.rs,point_naming_tests.rs}`（仅旧路径相关回归需要时）；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN}.md` | `tests/plc-catalog-import.test.mjs`；`tests/fixtures/plc-catalog-v1.json`；`CODE_INDEX.md`（实际结构发生变化时按仓库契约新建） |
| STD 角色记录 | 本任务 `spec.md` 仅 PM/Owner | 批准后 Development 创建本 bundle `tasks.md`；交接后独立 Verification 创建 `checklist.md` |

禁止修改 `schema.rs`、迁移/DDL、Cargo 或 pnpm 依赖及锁、`.env`、用户数据库/profile、样本/队列/回执、原始 DB/UDT 文件、DS/FF/backend 源码、根 contracts、其他任务。允许测试只在全新隔离 profile 与自有临时输出；网络 POST、现场设备和真实数据库均不在范围。新可见文案中英文键成对；新增或触达的业务表复用公共列宽组件：普通列可拖拽、有最小宽和横向滚动，刷新/切页/重启按稳定字段恢复，可恢复默认；功能列可固定，偏好不写业务配置。

## 7. 验收矩阵（未来执行，均未完成）

| 编号 | 可复现的通过标准 |
| --- | --- |
| DA01 | 父规格示例及受控多 DB 合成文件对两种合法 producer 通过；严格拒绝重复 key、BOM、非法 UTF-8、未知字段/版本、非法整数/UUID/null、超限、重复身份与空点集，逐个报告具体原因且没有写入。 |
| DA02 | 包含 BOOL、INT、REAL、STRING、不同 BOOL bit 与禁用点的完整文件无丢点导入；比较原始 bytes/SHA、点 ID 对应、名称、类型、地址、范围及原启用事实。DB/点字段按 producer 分型检查：DS DB 缺失、DAA DB 存在、点缺失/null 均拒绝；源点 true 不导致 DAA 自动采集。 |
| DA03 | BOOL bit、非 BOOL bit、非法 STRING 长度、越界、物理重叠、无效名称/类型和禁用点错误均阻断整台；客户端地址/端口与 TSAP、同机 loopback 提示及不连接行为明确可验。 |
| DA04 | 一个 PLC 多 DB 引用同一真实目录 source，source_id、原文 SHA、origin、DB/点映射全链一致；伪造 source、错 SHA/DB/点/类型/地址、重复或跨 PLC 引用均无法保存或激活。旧 DB/UDT 完整树、leaf_matches、UDT 及源校验正反例行为不变，目录 UI 不显示伪造 TIA 树。 |
| DA05 | 新建和既有 PLC 映射经显式确认，ID 冲突安全分配且映射稳定；同文件重导 ETag 不变；改名/地址/类型和 source_enabled 差异可见并按规则确认；缺点、额外点、DB 改号、跨 origin 阻断，原草稿字节/ETag 和历史不变。 |
| DA06 | 地址/类型人工覆盖有 SHA 基准、理由和后续源变更冲突；普通保存接口不能伪造绑定或覆盖；目录 DB 本地新增点被明确阻断，既有原始来源和历史版本完整。 |
| DA07 | 预览取消、切换目标/文件、过期 token、草稿并发变化、容量/事务失败与重复提交均无部分来源、映射或写入；未知结果先重读，不能盲重试。 |
| DA08 | 新 PLC/点默认不采集；用户显式分组、周期、启用、保存和激活，资源限额有定位并可阻断；原有组/周期、active/used、启动设置及未选 PLC 不因导入被改变。双语、表格列宽与恢复默认按 §6 验证。 |
| DA09 | 用自有旧合成 profile 副本核验新程序读取旧 schema 1 原 bytes/SHA 不变；旧二进制遇新目录 payload 安全拒绝且不产生空库；双库物理 schema、旧版本、样本及来源原文无变更。不能以空配置通过此项。 |
| DA10 | 自有合成旧样本和新 catalog 样本经原本地定义/manifest 解码，导入前后旧样本、pending 和 ACK bytes/SHA 一致；新样本通过现有 plc-facts/v2 序列化及合同校验，未额外加入 Address/origin，未发网络 POST。 |
| DA11 | 独立端到端：使用实际 **DS-003 候选导出器**对受控 DS saved revision 导出的原文件（记录候选、revision、文件 SHA），在全新隔离 DAA profile 导入；不额外提供或重复导入原 `.db` / `.udt`，用户完成必要分组、启用、保存、激活后，通过自有 loopback DS S7 真正读取 BOOL、INT、REAL，并核对本地/外部 ID、地址、类型、预设值与质量；同时证明停用点仍在草稿/保存配置。DS/DAA 候选均须可追溯，建议 DS-003 已通过 fresh QA；合成 JSON 单测或仅解析不能替代此项。 |
| DA12 | 实际交付树和锁文件执行相关 Rust/Node 测试、类型检查、前端构建、`rust-snap7-driver` 检查和 macOS 原生交互；记录真实命令、退出码、隔离路径、证据、未执行项与清理。其他平台及现场未测不得声称已通过。 |

## 8. 实施依赖、验证和停止条件

Human Owner 精确批准本 r1 后，Development 才创建 `tasks.md`、实施并自检，交 developer_handoff；fresh-context Verification 独立创建 checklist、复核精确交付候选；Human Owner 最终验收另行决定。DAA 格式、来源、原子性等单端工作可先用受控合成文件自检；DA11 必须等待可追溯的 DS-003 实际导出结果和 DAA-017 实际导入结果，不能将 fixture 冒称跨应用或真实设备联调。

在独立批准的实施与 QA 阶段，仅使用自有新合成数据、两个应用各自全新隔离 profile、隔离临时目录及非特权 IPv4 loopback；不得使用用户原有 dev 联调 profile、数据库或真实设备。受控测试负责进程、文件和端口生命周期；记录候选、来源、证据及清理，无法安全执行则报告 blocked/not_run。

项目工具链为 `pnpm@11.11.0` 与 Cargo/Rust，普通入口 `pnpm tauri dev`。拟议检查示例：`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1`、`cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver`、`node --test tests/plc-catalog-import.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`；`CARGO_TARGET_DIR` 和 `RUN_DIR` 指向任务自有隔离临时目录。命令需由 Development 按实际测试入口核实，未安装/离线不可用或无法运行原生 UI 须如实报告，不修改依赖锁以假称通过。

新配置元数据令旧二进制可能拒绝是预期的安全回退门槛，不能将可能拒绝写成旧版可运行。回退前停止隔离采集，使用证明兼容的停机合成副本或原备份；不得以旧程序覆盖新配置或历史。任何需要 DDL/真实 profile 迁移、公共合同改动、扩大白名单或真实设备行为时，停止并提交对应独立 Revision/批准。

## 9. 角色和 skill handoff

PM 本轮使用 `aiis`、`project-governance`、`plc-point-mapping` 定义范围，未执行产品、数据库或测试。批准后 Development 根据触达面使用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；Verification 在 fresh context 按对应技术及治理规则独立复核。Development 自检或 QA 通过均不自动授权真实设备、上线、数据库迁移或 Human Owner 最终验收。
~~~~~~~~
~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
