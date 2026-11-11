# 通用计划与实绩 HTTP v1

[English](README.md) · [实际装配 OpenAPI 子集](openapi.json) · [获批规格](../../../../plans/ARCH-TASK-001-generic-plan-performance/spec.md)

本目录记录 ARCH-TASK-001 r1 的候选源码合同和合成样例。`openapi.json` 从正常 `create_app(testing=True)` 的实际路由提取本任务 16 条路径及所引用 schema；它不是部署或现场接入证明。成功信封为 `code/message/data/timestamp`，错误使用相应 HTTP 状态和 `errorCode: task.*`。任务、目标和字段值的大小写、类型及时间规则以规格为准。ID 和配置修订号是十进制字符串；采样序号为 JSON 安全整数；API 业务时间带 `+08:00`。字段值中的名称和 `labels` 语言键保持原样。

## 调用边界与版本

登录入口使用既有认证及 `plan`、`performance` 角色授予；配置保存仅 admin。补建要求两项 API 权限。集成入口默认关闭，免前端 token 的请求仅适用于项目显式开放的受信边界；`producerId` 是追踪和资格匹配键，本身不是凭据。入口关闭或目标、写入来源未登记返回 `403 task.forbidden`。字段配置集成 GET 只需 `module` 和可选 `fieldConfigVersion`；按任务 GET 只需路径任务号，并核对记录的目标已登记。项目网络访问控制仍由项目负责。

项目映射通过 `TASK_INTEGRATION_PROFILE_FILE` 指向仓库外的私有 JSON 文件；`TASK_INTEGRATION_ENABLED` 只控制集成入口。登录用户创建计划仍需要已登记的目标版本和必填下发字段，即使集成入口关闭。格式见[纯合成 profile](examples/private-project-profile.json)：`mes`、`executors` 分别列出允许来源；每个 `versions` 版本分别声明 `dispatch` 字段名、PLC 序号上限 `plcSeqMax`（不大于 9007199254740991）和唯一自动流 `producerId/recordSource`。项目保存文件后需按其批准的进程配置流程加载。已被任务使用的版本和目标的映射、序号上限及自动来源必须保留，切换流使用新版本并并行保留旧版，直到旧任务不再需要；配置文件不是业务版本的自动存档。

全新迁移只初始化空的字段版本 1/修订 1。按下面两次保存样例会依次产生版本 2、3 和修订 2、3；若期间有其他管理员修改，必须先重读并按实际结果调整。先准备并审核目标的 v1–v4 映射后再进行该例；v3 用于完整 A/B，AC09 停用反馈字段后为 v4。不要将示例覆盖到现有私有配置或在未获操作批准的 dev 上写入。

## 合成 A/B 走法

1. 使用已批准的管理员账号读取 `GET /task-field-configs?module=plan`；确认空配置为 v1/修订 1 后提交 [计划字段](examples/config-plan.json)。随后读取 `module=performance`，确认 v2/修订 2 后提交[实绩字段及共享显示](examples/config-performance.json)，再读取确认实际生效版本 V。示例中的 3 假设上述顺序无并发变更。展示设置仅改修订；业务设置发布新版本，历史任务继续使用绑定版本。
2. 为每个独立场景选一个 1–12 位大写字母或数字 `RUN`，把所有样例中的 `GT1-RUN-A/B` 一致替换为 `GT1-<RUN>-A/B`。在受控环境先提交 [B 计划](examples/plan-b.json)，再提交 [A 计划](examples/plan-a.json)。MES 每个任务串行重试原内容。
3. CA/FF 提交 [A 领取](examples/claim-a.json)，确认先得到 A，保存返回的 `dispatchId` 和冻结 `parameters`；把实际批次 ID 填入 [A 回执](examples/ack-a.json) 并发送。之后领取 [B](examples/claim-b.json)，用它返回的批次 ID 发送 [B 回执](examples/ack-b.json)。现场执行方在本地持久保存领单请求号、原批次、参数、序号和现场回执；结果不明先核对，不盲目重下发。`plc_accepted` 不代表已开工。
4. SMA 发 [A 序号 12](examples/snapshot-a12.json)，操作员使用登录入口提交 [A 人工检验 true](examples/manual-a.json)。按规格分别试低序 11、同内容重发 12 和同序不同内容；再发 [B 序号 1](examples/snapshot-b1.json)、[B 人工检验 false](examples/manual-b.json) 和 [A 完工序号 13](examples/snapshot-a13.json)。核对 A 目标仍为 1200、反馈为 1200、速度 0 可见、人工 true 保留；B 反馈仍为 50、人工 false 保留。A 更高序号 14 返回 `already_completed`。所有序号重试保留原时间和内容。
5. 两个独立 RUN 中先提交 B1、再从实绩详情补建；分别使用[补建请求](examples/supplement-b.json)的默认 `false` 和 `true`。前者计划反馈为空，后者为 50；两者均为 `not_required`、保留生产状态，重复返回同一计划。再报 B 序号 2、长度 60 和速度 41，检查仅反馈槽回写，原实绩订单快照仍为空。

示例调用（从本目录运行；令牌通过用户自己的安全方式取得，以下只是占位变量）：

```sh
curl -fsS "$TASK_API/task-field-configs?module=plan" -H "Authorization: Bearer $TASK_ADMIN_TOKEN"
curl -fsS -X PUT "$TASK_API/task-field-configs" -H "Authorization: Bearer $TASK_ADMIN_TOKEN" -H 'Content-Type: application/json' --data-binary @examples/config-plan.json
curl -fsS -X PUT "$TASK_API/task-field-configs" -H "Authorization: Bearer $TASK_ADMIN_TOKEN" -H 'Content-Type: application/json' --data-binary @examples/config-performance.json
curl -fsS -X POST "$TASK_API/integration/plans/upsert" -H 'Content-Type: application/json' --data-binary @examples/plan-b.json
curl -fsS -X POST "$TASK_API/integration/plans/upsert" -H 'Content-Type: application/json' --data-binary @examples/plan-a.json
curl -fsS -X POST "$TASK_API/integration/plans/dispatch/claim" -H 'Content-Type: application/json' --data-binary @examples/claim-a.json
```

请先将样例复制到临时目录并替换 RUN、V、批次 ID 和时间，不要编辑合同工件；`$TASK_API` 包含 `/api/v1`。这些命令是对接示例，不自动授权任何数据库或设备操作。

## 前后端与现场分工

Vue 列表和详情读取各自 API 与任务绑定的字段定义；设置入口维护共享组和本地组，列宽及未提交草稿留在本机。FastAPI 在数据库事务中保存计划、实绩、下发批次及人工动作；已接受实绩和允许反馈一起提交。MES 负责订单，CA/FF 负责 PLC 接收条件、序号握手和原批次回报；DAA 保存采集事实，SMA 根据事实生成按任务号和版本固定的完整自动快照。后端不直接轮询 PLC，也不代替 SMA、CA/FF 的本地持久化和重启核对。

现场设备地址、PLC 握手位宽、旧执行方隔离、SMA 续号、事实末次采样保留和释放属于现场接入；本合同样例与源码检查不证明真实联调。历史 [business-integration-v1](../business-integration-v1/README.zh-CN.md) 的四条实绩匿名操作由本任务退出；其历史 schema 和证据保留。设备和监控四条集成、独立质量与采集事实 v2 按各自合同保留。
