Task ID: ARCH-OBS-008
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 过程监控与设备状态日常读写解除无关数据库放行条件
Owner: Core 设备状态与过程监控
Acceptance Chain Reference: 本规格批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-005、ARCH-OBS-006、ARCH-ACQ-007

# 过程／实时观测运行兼容修复

## 1. 目标与现状

ARCH-ACQ-007 将 dev 的全库 revision 推进到 `a1c307f8d2e4`，设备状态与过程监控仍使用旧观测 profile 的 `schemaRevision`。当前观测 guard 对全库 revision 做精确比较，请求会在业务读写前返回 503。profile 解析和来源登记可用性还各有 revision 白名单。过程／实时与能耗共用部分 guard 和 profile，处理时须按调用边界核对。

本任务以现有 dev 和交付工作树为对象，调整过程／实时的后端日常读写；已有接口、观测 JSON 和业务表继续使用。Human Owner 已指定在 dev 修复和验证，本规格为待批准草案。

## 2. 范围与要求

1. 过程／实时的普通 API、配置管理和来源管理请求，不因全库 Alembic revision、配置中旧 revision、数据库 UUID、库名、MySQL 版本或数据库时钟偏移而拒绝；日常请求不预检观测数据表结构。数据库通过现有连接配置访问。真实数据库错误按现有错误协议返回，不能伪装成无数据。
2. 覆盖公开登记来源读写、私有实时卡片／数据管理、过程曲线／历史数据管理和相关配置入口，并核对旧机器入口。配置解析及登记可用性不得把目标 revision 白名单作为过程／实时运行条件；已有 profile 原样可用。当前已有的观测总开关及原有业务配置继续使用。
3. `POST /api/v1/integration/observations` 和 `GET /api/v1/integration/observations/latest` 沿用无需 Bearer 的已发布合同。POST 仍检查来源已登记、启用且未删除，以及目标、采样组、启用槽位、指标类型和重复事件；GET 仍按来源、目标及可选任务号取得最新一条。登记是来源标识，部署访问范围仍由现有部署决定。
4. 前端私有接口继续沿用登录 Bearer 以及设备／过程读权限和管理员权限。旧机器 Bearer 接口继续沿用原鉴权、生产者与设备授权、范围及语义。保留登记来源内部身份冲突检查、事务及幂等、实时整包替换、过程追加、历史记录与备注／复核行为。不得扩大旧 profile 设备的读取范围。
5. 按项目时间合同处理采集时间与服务生成的上海时间，不以进程所在电脑时区冒充业务时区，也不把数据库会话时区的不同误判为可直接使用的上海时间。保留时间精度、API 偏移和现有事件先后及未来时间校验语义。
6. 能耗继续沿用当前权限、配置、写入及 guard 行为。采集数据的结构校验、来源登记、事实读写及维护规则不因本任务改变。共享代码修改须证明这两个调用边界；若发现现状无法同时满足，应先报告具体冲突。
7. 允许修改 `backend/app/equipment_observation/` 内的必要后端源码、对应后端聚焦测试及该模块双语 README 中与本变更直接冲突的说明。真实文件结构改变时按项目规则维护索引。测试应覆盖本次可能回归的行为，不引入新依赖。

## 3. 验收

| 编号 | 验收标准 |
| --- | --- |
| AC01 | 旧 profile 不修改，dev 的现有后继 revision 下，过程／实时公开 GET、卡片、曲线、配置与数据管理不再因上述数据库放行条件返回 503；运行路径不以全库版本和白名单判断登记可用性。 |
| AC02 | 用无 Bearer 的有效登记来源分别提交 `latest` 和 `history`，返回现有合同；对应公开 GET 返回最新记录及正确指标。未知、停用或删除来源和错误槽位／类型被拒绝；相同事件重试与冲突按原合同处理。 |
| AC03 | 私有页面接口无登录或权限不足时拒绝，有相应读取权限时可读，配置管理仍限管理员；旧机器接口的 Bearer 和原 scope 仍有效。 |
| AC04 | 源码和聚焦验证覆盖可用数据、空结果、数据库失败、旧 profile、版本后继、时间语义、来源身份冲突以及事务／重试，不把查询错误当空数据。 |
| AC05 | 能耗调用维持现有 guard 及权限语义。采集数据样本写入、latest/history 查询和现有维护校验保持原合同，执行与环境相符的回归并记录实际结果。 |
| AC06 | 使用现有 dev、现有服务入口进行验证，不创建隔离库、不执行 DDL、迁移、stamp 或 revision 更新。在线 GET 优先使用已有数据。若为验证公开 POST 需写测试记录，只使用已启用来源、独立测试任务号与事件号，不覆盖或删除现有业务数据，记录保留的测试记录标识和实际影响。 |

Development 和 fresh-context Verification 分别记录源码版本、命令、结果、使用的环境与实际覆盖，不能将自检当作独立验证。验证无关后继时以现有 dev 实际 revision 为证，不在 dev 增加测试迁移。无法安全完成某项在线读写时，记录具体原因和未覆盖项。

## 4. 不包含与风险

不修改前端、公开接口请求或响应、数据表结构、Alembic 脚本、现有业务数据或用户私有配置；不重置服务、不清空数据库、不操作真实 PLC。dev 上为验证新增的非覆盖性测试观测按 AC06 单独记录。后续迁移改动实际依赖表或业务语义时，需要对应迁移任务验证兼容性。

若回退源码，dev 已有的较新 revision 仍可能使旧观测 guard 返回 503；回退不通过改写 Alembic 版本或删除记录处理。鉴于后端和测试文件可能被其他任务同时修改，Development 以任务相关 diff 精确修改并保留并行工作。

## 5. Handoff

待 Human Owner 对 ARCH-OBS-008 r1 范围批准后交 Development。Development 使用 `backend-arch` 和 `code-document-indexer` 处理相关源码和必要测试，核对既有业务时间工具、运行入口及 dev 安全验证边界。完成自检后交 fresh-context Verification 独立核对相同候选，并由 Human Owner 最终验收。

## 6. Revision 记录

| 版本 | 状态 | 依据 |
| --- | --- | --- |
| r1 | owner_approved | Human Owner 明确回复「批准 ARCH-OBS-008 r1」，批准按本规格实施和 dev 验证。批准记录写入前草案 SHA-256 为 `79714fe0f2edc1463f4aadca9c099ee1dd61e6703ad7934e8fb28a0038dbd68a`。 |
