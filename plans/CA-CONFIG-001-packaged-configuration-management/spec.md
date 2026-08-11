# CA-CONFIG-001 Packaged Configuration Management — PM Spec

Task ID: CA-CONFIG-001  
Revision: r1  
Status: draft  
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Direction captured; Development blocked until ARCH-001 is owner_accepted, the de-branded Control Agent baseline is fixed, and this Revision is refreshed and approved

Task Namespace: aiis-ics-arch  
Classification: root  
Capability: Packaged Control Agent database profile and paired PLC YAML lifecycle  
Owner: control-agent configuration/runtime/UI boundary  
Target Version: next Control Agent minor after the ARCH-001 baseline; current source suggests `0.2.0` candidate from `0.1.0`  
Acceptance Chain Reference: CA-CONFIG-001 PM spec -> ARCH-001 owner acceptance -> Control Agent baseline/version refresh -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context QA checklist.md -> Human Owner final acceptance -> separate CA release action  
Execution Mode: agent_team_same_session  
Created: 2026-08-08  
Updated: 2026-08-10

Revision History:

- `r1 metadata correction`：在根 `plans/README.*` 目录启用当前 governance checker 后，将旧的自由文本 Classification 规范化为允许值 `root`；本次只修正 PM metadata，不改变 r1 范围、验收、风险、版本门或 Development 阻塞条件。

## 1. PM 结论

`CA-CONFIG-001` 为打包后的 AIIS ICS Control Agent 建立本机可写、可审计、默认关闭的配置管理能力。
现场操作员无需重新编译源码，即可在 Tauri 运维控制台中维护当前已安装数据库 provider 的连接 profile，
并成组导入、校验、激活和回滚：

- `plc_points.yaml`
- `plc_snapshot_policy.yaml`

本任务是独立的 CA 跨 runtime/UI 能力，不属于 `ARCH-001` 的去旧品牌、源码提取或 public-safety 清理。
当前只落 PM 方向；必须等 `ARCH-001` 完成并固定新的 CA 身份、路径和版本后刷新本 spec，才能批准
Development。

## 2. 启动前置 gate

Development 必须同时满足：

1. `aiis-ics-arch::ARCH-001` 已通过 fresh-context QA 并获 Human Owner final acceptance；
2. Control Agent 已收敛为 `AIIS ICS Control Agent`，crate、binary、bundle identifier 和配置样例均为
   public-safe baseline；
3. 当前 CA baseline 的独立版本或不可变 commit 已记录；
4. PM 基于 baseline 重新核对本 spec 的路径、现有 gates、YAML schema、Tauri capabilities 和依赖；
5. 如 baseline 与 r1 有 material drift，先形成新 Revision；
6. Human Owner 对最终 Revision 使用精确批准语句。

现在创建 r1 不授权 `tasks.md`、源码修改、依赖安装、数据库或 PLC 操作。

## 3. 当前事实

只读代码审计确认：

- 当前 CA package、crate 与 Tauri 配置版本均为 `0.1.0`；产品身份将在 `ARCH-001` 中先行收敛；
- `AgentConfig` 当前从 process env 和工作目录/manifest 相对 `.env` 加载值；
- relative runtime path 当前依赖 working directory 或 Cargo manifest，不能作为打包应用的长期可写配置根；
- 数据库配置使用 `CONTROL_AGENT_DATABASE_URL`，当前 SeaORM 只启用 `sqlx-mysql`，repository 包含
  MySQL-specific backend/time-zone 语义；
- `CONTROL_AGENT_DATABASE_ENABLED` 与 `CONTROL_AGENT_DATABASE_READ_ONLY` 是独立安全门禁；
- `plc_points.yaml` 和同构 v2 `plc_snapshot_policy.yaml` 已有解析与交叉引用校验基础；
- CA UI 已采用 module-local section/locales，但当前没有 settings section；
- PLC read、persistence 和 autostart 均已有 fail-closed gate，配置更新不能绕过这些 gate。

本 PM 审计没有读取真实 `.env` 内容、真实数据库 URL、客户 YAML 内容或运行日志。

## 4. 成功目标

完成后应满足：

1. packaged Tauri 和 headless runtime 使用同一个明确的 writable config root，不依赖源码目录或当前
   working directory；
2. 非敏感数据库 profile 与数据库 secret 分离存储，UI、日志、status 和错误中不泄露 password 或
   完整 URL；
3. UI 只能选择当前二进制实际安装的 provider；本任务仅启用现有 MySQL provider；
4. 两份 PLC YAML 必须成组导入、成组校验和原子激活，不存在只更新一份的半配置状态；
5. 每次导入形成不可变 bundle id、schema/version、SHA-256、时间和来源摘要，并能回滚到上一已验证
   bundle；
6. profile 或 bundle 更新时 collection workers 必须停止，激活后保持 stopped，不自动读 PLC 或写库；
7. process/env override、开发 `.env` compatibility、app profile 和 built-in default 的有效来源可见且
   不冲突；
8. 浏览器/Vite-only 模式不伪造配置写入成功；配置写入只通过 Tauri command；
9. Development/QA 在 fake adapter、临时目录和脱敏 fixture 下验证，不连接真实 DB/PLC；
10. PostgreSQL/MSSQL 可在后续 adapter 任务接入 provider registry，而不重做 UI/profile/bundle lifecycle。

## 5. Writable config root

默认目录由 Tauri/OS app config directory 解析，逻辑身份固定为：

```text
<os-app-config>/aiis-ics-control-agent/
├── settings.yaml
├── bundles/
│   └── <bundle-id>/
│       ├── manifest.json
│       ├── plc_points.yaml
│       └── plc_snapshot_policy.yaml
├── active-bundle.json
└── state/
```

规则：

- packaged app 不写安装目录、resource 目录、源码 `config/` 或当前 working directory；
- headless/runtime 测试可通过显式 CLI 参数或 `CONTROL_AGENT_CONFIG_ROOT` 指定根目录；
- root precedence 固定为 explicit CLI -> `CONTROL_AGENT_CONFIG_ROOT` -> OS app config directory；
- root 必须 canonicalize 并限制所有写入在其内部，拒绝 `..`、symlink escape 和任意绝对输出路径；
- 测试只使用临时目录；Development 不写用户真实 app config directory；
- repository `config/` 只保存 default-off、public-safe 示例，不是 packaged runtime 的可写事实源。

## 6. Database profile contract

`settings.yaml` 只保存非敏感 profile 与 gate：

```yaml
schema_version: 1
database:
  provider: mysql
  host: 127.0.0.1
  port: 3306
  database: aiis_ics
  username: aiis_ics
  secret_ref: database/default
  connect_timeout_ms: 1500
  enabled: false
  read_only: true
```

固定边界：

- 默认 `enabled=false`、`read_only=true`；样例不得包含真实地址、用户名或密码；
- UI 不接受/保存原始 database URL，只接受结构化字段；连接 URL 由 Rust provider adapter 安全构造；
- password 不写入 YAML、localStorage、日志、event payload、clipboard 默认值或 runtime snapshot；
- password 通过 OS credential-store abstraction 保存，profile 只保留 opaque `secret_ref`；
- credential store 不可用时不得回退为明文持久化；只允许保持未配置，或使用显式 process env compatibility；
- save profile、save secret、test connection、enable database 与解除 read-only 是分离动作；
- 将 `read_only` 改为 `false` 必须有本地确认，但仍不自动启用 PLC write、persistence 或 autostart；
- settings status 只返回 provider、masked host/user、configured boolean、gate、effective source 和错误摘要。

OS credential-store crate/plugin、许可证和 Windows/macOS 支持必须在 baseline refresh 时形成显式
dependency decision；无法证明安全持久化时本任务 `qa_blocked`，不得采用明文 fallback。

## 7. Provider registry 与后续 adapters

`CA-CONFIG-001` 只建立 provider-neutral profile、capability registry 和当前 MySQL adapter 接口：

- UI provider selector 只显示 binary 返回的 `available=true` providers；
- 当前实现只允许 `mysql`；
- `postgresql` 与 `mssql` 可以显示为 roadmap 信息，但不得可选、可保存或宣称已支持；
- test connection 只执行只读 connection/ping/time-source 检查，不建表、不迁移、不 seed、不写业务数据；
- collection repository 继续只写 backend-owned raw/latest/status 表，不扩大业务表边界。

后续独立任务：

- `CA-PG-001`：SeaORM/SQLx PostgreSQL feature、time/query differences、schema identifier 与集成测试；
- `CA-MSSQL-001`：Rust driver/SeaORM compatibility、TLS/licensing/platform packaging 可行性 gate，gate 通过后
  才能形成 adapter Development spec。

不得为了让下拉框看起来完整，在本任务编译未验证 driver 或接受无实现 provider。

## 8. Configuration precedence

有效值来源从高到低：

1. explicit process environment（deployment compatibility 与紧急 override）；
2. development `.env` compatibility（仅开发环境存在时）；
3. packaged app profile/credential store；
4. built-in default-off values。

UI 必须显示每个关键值的 effective source。被 process env 或开发 `.env` 覆盖的字段可以编辑下一份
profile，但必须清楚标记“当前未生效”；不得让操作员误以为 save 已改变 active runtime。

现有 `CONTROL_AGENT_DATABASE_URL` 只作为 compatibility override，永远不回显。新 profile 生效后，
runtime service 接收 resolved typed configuration，不在 service/command 层重复解析 URL 或 source precedence。

## 9. Paired YAML bundle lifecycle

导入操作必须一次选择两个角色明确的文件：

- point contract -> canonical `plc_points.yaml`
- snapshot policy -> canonical `plc_snapshot_policy.yaml`

流程：

```text
select pair
  -> copy to staging under config root
  -> YAML parse + schema validation
  -> cross-contract PLC/group/point validation
  -> normalized summary + SHA-256
  -> Human confirmation
  -> immutable bundle directory
  -> atomic active-pointer switch
  -> remain stopped
```

要求：

- 限制文件数量、类型和大小；拒绝 symlink、目录、空文件、重复角色与路径逃逸；
- 复用现有 point/policy parser 和 same-shape v2 交叉校验，不在 UI/command 层复制 YAML 规则；
- validation 失败不产生 active bundle，不改变当前配置；
- bundle manifest 不保存 secret，记录 schema version、hash、导入时间和脱敏摘要；
- active bundle 通过小型 pointer 文件原子切换，旧 bundle 保持不可变；
- rollback 只能指向曾验证成功的 bundle，同样要求 workers stopped，并保持 stopped；
- 激活/回滚失败必须保留此前 active pointer；
- 不提供任意 YAML 文本编辑器；内容修改继续由项目工具生成并重新导入。

## 10. Runtime apply boundary

- 配置读取形成 immutable runtime snapshot；正在运行的 worker 不接受中途 profile/bundle 替换；
- database profile save、secret save、bundle activate/rollback 在任何 read/persistence worker 运行时均 fail closed；
- 激活后刷新 status，但不自动 start read、enable persistence 或改变 autostart；
- 下一次显式 start/restart 才消费新的完整 snapshot；
- headless runtime 与 Tauri UI 必须复用同一 config service 和 gate；
- 配置管理不能绕过 `PLC_READ_ALLOWED`、`PLC_WRITE_ALLOWED`、database enabled/read-only 或现有授权门禁。

## 11. Tauri command 与分层

建议 command contract：

- `get_configuration_status`
- `save_database_profile`
- `set_database_secret`
- `clear_database_secret`
- `test_database_connection`
- `validate_plc_configuration_bundle`
- `activate_plc_configuration_bundle`
- `list_plc_configuration_bundles`
- `rollback_plc_configuration_bundle`

command 只做输入适配与输出脱敏；schema、filesystem、credential、provider connection 和 bundle lifecycle
分别归 domain/service/infrastructure。command/service 不直接拼 SQL，UI 不直接读写 filesystem。

Tauri capability 只开放完成本合同所需的最小本机权限。浏览器/Vite-only 模式必须返回
`unavailable_in_browser_mode`，不能写 localStorage 或模拟成功。

## 12. Settings UI

新增 module-local `settings` section，至少包含：

### Database

- available provider 与 capability；
- host、port、database、username、masked password state、timeout；
- enabled/read-only gate 与 effective source；
- Save profile、Save/Clear secret、Test connection；
- 写入 gate 变更的明确确认和“不会自动开始采集”提示。

### PLC configuration bundle

- 当前 active bundle id、hash、激活时间和 point/policy 摘要；
- 选择两份 YAML、validate preview、activate；
- 最近已验证 bundle 列表与 rollback；
- workers running、validation error、restart/apply 状态。

UI 不显示完整 database URL、password、真实 YAML 全文或无脱敏错误堆栈。所有可见文案进入 settings
module 的中英文 locale pair，不污染 shell/global locale。

## 13. Audit 与错误处理

- structured events 记录 profile saved、secret configured/cleared、connection test outcome、bundle validated/
  activated/rolled back；
- event 只含 provider、bundle id、hash、result、reason code 和脱敏 endpoint 摘要；
- 禁止记录 password、完整 URL、secret_ref backend value 或 YAML 全文；
- validation/activation error 使用稳定 reason code 和可操作中文/英文说明；
- config 文件写入使用同目录 temporary file、flush 和 atomic replace；失败不得留下可被 runtime 读取的
  partial file。

## 14. 明确不做

- 不实现 PostgreSQL 或 MSSQL driver；
- 不执行 Alembic、建表、schema bootstrap、seed 或业务数据迁移；
- 不连接生产/真实数据库或 PLC，不运行长时间 collection/soak；
- 不自动启用 database、解除 read-only、开启 PLC write 或 autostart；
- 不实现远程 Web 设置、多人账号/RBAC、云同步或中央配置服务；
- 不实现 YAML 在线编辑、点位生成、mapping 编辑或业务 Projection；
- 不把 secret 保存为明文 YAML/.env/localStorage；
- 不修改 backend、frontend-js、tools、contracts、Compose 或 Docker；
- 不执行 Git/GitHub、CA tag、release branch、打包发布或生产部署；
- 不顺手完成 `ARCH-001` 的去旧品牌/清理工作。

## 15. Development 精确 write allowlist

前置 gate 与最终 Revision approval 完成后，只可写：

### Rust/runtime

- `control-agent/src-tauri/Cargo.toml`
- `control-agent/src-tauri/Cargo.lock`
- `control-agent/src-tauri/capabilities/default.json`
- `control-agent/src-tauri/src/config/**`
- `control-agent/src-tauri/src/domain/configuration.rs`（新建）
- `control-agent/src-tauri/src/domain/runtime.rs`
- `control-agent/src-tauri/src/commands/configuration.rs`（新建）
- `control-agent/src-tauri/src/commands/mod.rs`
- `control-agent/src-tauri/src/services/configuration.rs`（新建）
- `control-agent/src-tauri/src/services/mod.rs`
- `control-agent/src-tauri/src/services/runtime_snapshot.rs`
- `control-agent/src-tauri/src/infrastructure/configuration/**`（新建）
- `control-agent/src-tauri/src/infrastructure/database/repositories/mod.rs`（仅 resolved profile 与只读 test）
- `control-agent/src-tauri/src/infrastructure/mod.rs`
- `control-agent/src-tauri/src/infrastructure/plc_points.rs`（仅 active bundle path consumption）
- `control-agent/src-tauri/src/infrastructure/plc_snapshot_policy.rs`（仅 active bundle path consumption）
- `control-agent/src-tauri/src/lib.rs`

### Tauri/Vue UI

- `control-agent/src/app/settings/**`（新建）
- `control-agent/src/App.vue`
- `control-agent/src/console/sections.ts`
- `control-agent/src/console/types.ts`
- `control-agent/src/console/composables/useControlAgentConsole.ts`
- `control-agent/src/services/configuration.ts`（新建）
- `control-agent/src/services/runtimeSnapshot.ts`
- `control-agent/src/components/console/**`（仅复用/小型配置表单组件）
- `control-agent/src/styles/app.css`
- `control-agent/src/styles/theme.css`
- `control-agent/package.json`
- `control-agent/pnpm-lock.yaml`（仅经批准的 Tauri dialog/credential integration 确实需要时）

### Public samples, docs and 3MD

- `control-agent/config/examples/**`
- `control-agent/README.md`
- `control-agent/README.zh-CN.md`
- `control-agent/PLAN.md`
- `control-agent/PLAN.zh-CN.md`
- `plans/CA-CONFIG-001-packaged-configuration-management/tasks.md`
- `plans/CA-CONFIG-001-packaged-configuration-management/checklist.md`

dependency 只能用于 OS credential store、safe URL construction 或最小 Tauri file dialog/capability；每个新增
dependency 必须记录用途、许可证、平台支持和无更小现有方案的证据。baseline refresh 后路径有变化时
必须先更新 Revision，不能临时扩大 allowlist。

## 16. 验证矩阵

至少验证并记录：

1. config-root CLI/env/OS precedence 与 path traversal/symlink escape 负向测试；
2. settings schema、default-off、invalid provider/port/timeout 和 source precedence 测试；
3. credential store fake adapter 的 save/read/clear/error 测试，以及所有输出/日志 redaction；
4. MySQL provider typed URL construction 和 fake read-only connection test；不得连接真实 DB；
5. paired YAML parse、cross-validation、hash、atomic activation、failure preservation 和 rollback 测试；
6. workers-running 时 profile/bundle mutation 被拒绝，激活后仍 stopped；
7. Tauri command 输入校验、thin-adapter boundary 和 browser-mode unavailable 测试；
8. settings 中英文 locale key parity 与 UI source contract；
9. `cargo fmt --manifest-path control-agent/src-tauri/Cargo.toml --check`；
10. `cargo test --manifest-path control-agent/src-tauri/Cargo.toml --features rust-snap7-driver`；
11. `pnpm --dir control-agent install --frozen-lockfile` 和 `pnpm --dir control-agent build`；
12. public-safety scan：secret/URL/YAML content、旧 identity、绝对私有路径、真实 endpoint 和 generated output；
13. 不执行真实 DB/PLC、Docker、Git/GitHub 或 release 操作。

如 credential store/platform API 无法在当前 QA OS 上完整证明，必须记录平台限制；Windows packaged smoke
可以作为后续交付 gate，但不得把 mock test 误写为跨平台生产证明。

## 17. Acceptance Criteria

| ID | 验收条件 |
| --- | --- |
| AC-001 | 前置 gate、Revision、Execution Mode、allowlist 和 3MD handoff 一致。 |
| AC-002 | packaged/headless 共用 writable config root；安装/源码/cwd 不作为 packaged writable truth。 |
| AC-003 | profile 非敏感字段与 OS credential secret 分离；不可用时无明文 fallback。 |
| AC-004 | effective source/precedence 可见，env override 不回显且不会被 UI 静默覆盖。 |
| AC-005 | 当前只有 MySQL provider 可用；PG/MSSQL 不可选择且没有伪支持。 |
| AC-006 | test connection 只读、无 schema/data write，并通过 fake adapter 验证。 |
| AC-007 | 两份 YAML 成组校验、不可变保存、原子激活；任一步失败保留旧 active bundle。 |
| AC-008 | rollback 只指向已验证 bundle，workers running 时拒绝，完成后保持 stopped。 |
| AC-009 | 配置变更不绕过 PLC/database/read-only/autostart/authorization gates。 |
| AC-010 | settings UI 完成 Database 与 PLC bundle 流程，browser mode 不伪造成功，中英文 locale 对称。 |
| AC-011 | Tauri commands 薄，filesystem/credential/provider/YAML 规则各归明确 service/infrastructure owner。 |
| AC-012 | audit/log/status/error 不含 password、完整 URL、secret 或 YAML 全文。 |
| AC-013 | 不修改 backend/Compose，不运行真实 DB/PLC/Docker/Git/release。 |
| AC-014 | Rust tests、frontend build、source/public scans 通过；平台限制真实记录。 |
| AC-015 | `tasks.md` 记录实际事实，fresh-context `checklist.md` 独立复核并给出正式 verdict。 |
| AC-016 | Human Owner final acceptance 前不宣称新 CA minor 已发布；artifact/tag 属于独立 release action。 |

## 18. Stop conditions

出现以下情况立即停止：

- `ARCH-001` 或去旧品牌 CA baseline 尚未稳定；
- 需要明文保存 password/URL，或 credential store 方案许可证/平台支持不明确；
- 需要把 PostgreSQL/MSSQL driver 塞入本任务；
- 需要修改 backend schema/Alembic 或写入业务表；
- 需要在 workers 运行中热切换配置；
- 需要自动打开 read/write/autostart gate；
- 需要连接真实 DB/PLC、执行 Docker、Git/GitHub 或发布；
- 需要修改 allowlist 外文件或引入与配置生命周期无关的 UI/Runtime 重构。

## 19. 当前状态与后续批准

本 r1 只固定方向，当前不进入批准或 Development。`ARCH-001` 和 CA baseline gate 完成后，PM 必须刷新
版本、路径、credential dependency 与 Tauri capability；若无需修订，再由 Human Owner 使用届时 spec
中的精确批准语句启动 Development。

在此之前任务保持 `draft`，不得创建 `tasks.md` 或 `checklist.md`。
