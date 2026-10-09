# AIIS ICS Architecture 后端

English version: [README.md](README.md)

本目录是可复用的 FastAPI/SQLAlchemy Core。它负责认证、系统管理、模块发现、Schema maintenance、Projection 控制面和项目无关的 monitor 现场事实。使用方项目只需按约定增加业务模块，不修改 Core 组合根。

## Core 模块

~~~text
app/
├── user/             # 认证与账号 API
├── system/           # 字典与 Projection 控制面 API
├── control_agent/    # 后端侧 CA 授权合同
├── schema_maintenance/
├── monitor/          # 只保留 collector/raw/latest 事实
├── aiis_demo/        # manifest 参考模块
└── module_registry.py
~~~

普通模块通过 app/<module>/manifest.py opt-in。enabled=False 会隐藏模块 API；Registry 不会创建数据表。新增表必须走显式 Alembic revision 或获批的 schema-maintenance 动作。user 与 control_agent 是安全/运行时边界，继续在 app/router.py 显式挂载。

monitor Core 只返回 collector 健康状态和项目无关的 PLC DB-block raw/latest 事实。HMI、温度、能耗、过程曲线和生产实绩由项目仓库自己的模块负责。

## 运行边界

- FastAPI handler 调用 async Service/CRUD，不能轮询 PLC。
- 常驻 Rust/Tauri control-agent 负责 PLC 采集，并通过批准的合同写入现场事实。
- Celery、Redis、Beat、Flower 和 Python Worker runtime 不是 Core 依赖。
- Core baseline 现在是只包含十四张 Core 表的单一 `d4e6f8a0b2c4` Alembic root。其 upgrade 实际操作与当前
  SQLAlchemy metadata 由 `tests/test_core_migration_baseline.py` 机械核对；私有项目仓继续保留自己的历史
  migration 图。

## 本地检查

~~~bash
uv sync
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q
~~~

静态迁移检查可以在占位环境下运行 `uv run alembic heads`、`uv run alembic history` 和 offline SQL render。
源码检查不应连接真实数据库或执行在线迁移；Schema 工作必须使用单独获批的非生产数据库任务。

已批准的 `ARCH-DOCKER-001` smoke 从 backend 源码构建本镜像，并由一次性 `alembic upgrade head` 服务和
API 服务复用。它只连接同一 Compose 的 `mysql:3306`，使用可丢弃的 MySQL `8.4.6` volume；smoke env
被忽略，且每次运行后必须删除。

## 宿主机源码启动

宿主机源码开发请按[database-only 与账号初始化教程](../INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only)操作。完成迁移并在 `backend/.env` 配置所需 bootstrap 账号后，在本目录执行 `uv run python main.py --maintenance bootstrap-users`，再执行 `uv run python run.py`。Alembic 和 API 启动都不会创建登录账号；ENABLED 开关只在维护命令执行时生效。

## 打包

main.py 是禁用 reload 的应用入口；run.py 是本地开发入口；build.py 是可选 PyInstaller 源码打包路径，不会复制真实 .env、数据 dump 或客户输入。详见 BUILD.zh-CN.md。

## 单机 Docker 入口

根 `docker-compose.prod.yml` 复用本目录 Dockerfile，只读挂载 `.env.docker.prod` 到 `/app/.env`，日志写到 `runtime/backend/logs`；源码保留在镜像内。database-only 读取本目录 `.env`，其 MySQL 数据卷与 dev 独立。bootstrap 默认保持关闭，需要初始化账号时再显式启用。操作步骤见根[部署说明](../INITIALIZATION.zh-CN.md#单机部署)。

## 角色 API 权限

`SUPERVISOR_API_PERMISSIONS_JSON` 为 supervisor 账号授予 API permission；
`OPERATOR_API_PERMISSIONS_JSON` 为 operator 账号授予 API permission。两者均为非空白字符串的
JSON 数组，缺省 `[]`（不授予配置型权限）。key 精确、区分大小写匹配，是后端 permission，
不是前端 pageId、URL 或任意模块名。重复项按集合去重；`*` 是未知 key，不是通配符。
只有这两个角色使用数组；未知角色拒绝授权。

~~~dotenv
SUPERVISOR_API_PERMISSIONS_JSON='["monitor","control-agent-read"]'
OPERATOR_API_PERMISSIONS_JSON='["monitor"]'
~~~

operator 的**原始配置集合必须是 supervisor 原始配置集合的子集**。operator 获得的每个 key
必须在两数组中显式填写，不自动给 supervisor 补权限。先做此校验再过滤 unknown/disabled，
所以 operator 独有的未知或已关闭 key 也会阻止启动。
admin 无需数组，直接通过 `require_permissions()`；认证、参数校验、用户管理 actor/目标用户
约束、Projection 状态/合同校验及 CA gate-token 规则仍然执行。空数组不改变仅登录接口或
admin-only guard；授予一个 key 不会自动授予另一个 key。

| key | 当前接口表面与边界 |
| --- | --- |
| `system` | 显式用户管理查询与写入；actor/目标用户限制仍独立执行，不等于整个 system 模块权限。 |
| `system-dict` | 系统字典查询**和维护**共用该 key。 |
| `projection-mapping` | Projection handler/policy catalog 与 mapping 查询。 |
| `projection-mapping-manage` | mapping 草稿、校验、发布、复制与回滚 permission guard；Service 保留状态/合同校验，目前没有额外 role/admin 门槛。 |
| `monitor` | collector 与 raw/latest 现场事实；不包含客户业务曲线或前端 monitor 页面授权。 |
| `control-agent-read` | CA action-scope 目录查询。 |
| `control-agent` | gate-token 签发 permission guard；不会远程执行设备动作，仍有独立角色限制。 |
| `aiis_demo` | 默认关闭示例 manifest；配置后告警并忽略，数组不会启用该模块。 |

Projection 管理路由传入 `actor_user_id` 记录操作者；此字段不构成角色校验。

`schema_maintenance` 没有配置型 permission，使用 admin-only guard；CA authorization verify
使用其 gate-token 合同。两个数组不能代替这些独立边界。

普通模块在 `app/<module>/manifest.py` 声明 `enabled` 和 `permissions`。`enabled=False`
在重启/整个进程 reload 后移除该 manifest 的整组路由和 OpenAPI 项。所有角色（包括 admin）
请求其不存在的专属路径均得到正常 404。关闭不删表/数据、不阻止 model metadata 导入、不改变
Alembic。`user/auth` 和 `control_agent` 保持显式挂载，没有普通模块开关；前后端开关独立。
多个 owner 声明同一个 key 时，任一 owner 启用就可用；仅当所有普通 owner 都关闭时才视为
禁用。显式 user/CA 边界的 permission 视为可用 owner。

每次 API 组合只解析、校验和过滤一次，包括 `create_app(testing=True)`。请求消费本应用的
有效策略；修改配置需要重启/整个进程 reload。

| 情况 | 结果 |
| --- | --- |
| 变量缺失或 `[]` | 合法，该角色不获得配置型权限。 |
| 空字符串、坏 JSON、非数组、非字符串或空白成员 | 启动失败，指出变量/成员位置，不回显配置全文。 |
| operator key 不在 supervisor 中 | 启动失败，指出缺失 key 和两个变量。 |
| 未知 permission | `WARNING`，原因 `unknown_permission`；忽略该 key，允许启动。 |
| key 仅由关闭模块声明 | `WARNING`，原因 `disabled_module`，包含 owner 名称；忽略该 key，允许启动。 |
| 活动退役变量 `ROLE_API_PERMISSIONS_JSON`，即使 `{}` 或空值 | 启动失败，提示迁移；注释行不算活动配置。 |

告警包含变量名、permission 及适用模块名，只在组合期记录，不在每次请求重复。被忽略权限
不能授权。登录 401 表示认证失败；已认证但缺少权限返回 403；模块关闭后未注册路径返回 404。

### 配置来源与迁移

Settings 保持原来源优先级：显式 Settings 初始化、进程环境、唯一运行 `.env`、file secrets/默认值。
源码读取 `backend/.env`；打包读取可执行文件同目录 `.env`；Docker 使用所选入口挂载到
`/app/.env` 的配置。新数组的进程环境覆盖 dotenv。任一来源存在活动旧 key 都拒绝，即使新
key 同时存在；不兼容合并、不选择新旧优先级。三份公开示例使用安全空数组。真实 `.env`、
`.env.docker.dev`、`.env.docker.prod` 不会自动迁移。

重启前，人工迁移所选运行入口实际使用的配置：

1. 审核旧对象，保持各角色成员不变。例如：

   ~~~dotenv
   ROLE_API_PERMISSIONS_JSON='{"supervisor":["monitor","control-agent-read"],"operator":["monitor"]}'
   ~~~

2. 删除/注释 dotenv 的旧赋值，并从进程环境移除旧变量；写入上方两个数组。确认 operator 是
   子集，审核 permission 名称和模块 `enabled` 状态。
3. 重启/reload 后查看诊断。非法输入或等级错误由过去请求时空授权/403 变为服务就绪前失败；
   unknown/disabled 改为告警并过滤。合法等值迁移保持原角色授权不变。

`main.py` 在分发 `--maintenance schema` 或 `--maintenance bootstrap-users` 前先组合 app，
所以阻断错误也会发生在维护动作之前，unknown/disabled 告警则允许继续分发。这不表示所有
直接脚本或 Alembic CLI 都执行相同 API 校验；维护/数据库动作仍需要独立授权。

Bootstrap 继续是显式账号维护动作：数组不会创建/删除账号或修改密码。继续按
[宿主机源码初始化教程](../INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only)操作。

## 配置逐项说明

以下表格覆盖三份公开 env 示例的相同 68 个活动 key。源码缺省来自 Settings；“必填”表示缺失会在配置加载时失败。模板列列出 host/dev/prod 的公开值差异（相同值合并），口令/秘密只标为 placeholder；公开模板不是本机实际配置。bool 使用 True/False，字符串可单/双引号包裹；JSON 数组用外层单引号、内部双引号。

### 应用/API

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `APP_NAME` | 应用显示名称。 (str) | 必填，无源码缺省 | `AIIS ICS Architecture` |
| `APP_VERSION` | API 元信息报告的应用版本。 (str) | 必填，无源码缺省 | `1.0.0` |
| `APP_DESCRIPTION` | API 元信息中的应用描述。 (str) | `'AIIS ICS Architecture Core Backend'` | `AIIS ICS Architecture Core Backend` |
| `API_V1_PREFIX` | 版本化 API 路由前缀。 (str) | 必填，无源码缺省 | `/api/v1` |
| `BACKEND_HOST` | Uvicorn 监听地址；容器服务通常使用 0.0.0.0。 (str) | `'127.0.0.1'` | `127.0.0.1` / `0.0.0.0` |
| `BACKEND_PORT` | Uvicorn 监听端口，正整数。 (int) | `8000` | `8000` |
| `BACKEND_WORKERS` | 生产 Uvicorn worker 数；开发和打包入口固定为一个。 (int) | `1` | `1` / `4` |

### 运行/Projection

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `DEBUG` | 启用诊断错误详情；生产应关闭。 (bool) | 必填，无源码缺省 | `True` / `False` |
| `TESTING` | 使用独立 MySQL 测试数据库并关闭 Projection runtime。 (bool) | `False` | `False` |
| `BACKEND_MOCK_ENABLED` | 允许模块 Service mock provider 或显式示例 seed。 (bool) | `False` | `False` |
| `PROJECTION_RUNNER_ENABLED` | 仅在指定唯一 writer 宿主启用 lifespan Projection runner。 (bool) | `False` | `False` |
| `PROJECTION_RUNNER_INTERVAL_SECONDS` | Projection 轮询间隔，秒，正数。 (float) | `1.0` | `1.0` |
| `PROJECTION_RUNNER_BATCH_SIZE` | 每批 Projection 处理的 raw facts 上限，正整数。 (int) | `100` | `100` |
| `TZ` | 进程时区；重启生效，不修改数据库时区。 (str) | `'Asia/Shanghai'` | `Asia/Shanghai` |

### 认证/权限

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `JWT_SECRET_KEY` | JWT 签名秘密；替换公开占位符并保密。 (str) | 必填，无源码缺省 | placeholder |
| `JWT_ALGORITHM` | JWT 签发与验证算法，通常 HS256。 (str) | 必填，无源码缺省 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token 有效期，分钟。 (int) | 必填，无源码缺省 | `120` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token 有效期，天。 (int) | 必填，无源码缺省 | `7` |
| `SUPERVISOR_API_PERMISSIONS_JSON` | Supervisor API permission 字符串数组；缺省 [] 不授权。 (str) | `'[]'` | `[]` |
| `OPERATOR_API_PERMISSIONS_JSON` | Operator API permission 字符串数组；必须是 supervisor 子集。 (str) | `'[]'` | `[]` |

### 日志

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `LOG_DIR` | JSON Lines 日志文件目录。 (str) | `'logs'` | `logs` |
| `LOG_LEVEL` | 日志阈值，例如 DEBUG、INFO、WARNING、ERROR。 (str) | `'INFO'` | `INFO` |
| `LOG_MAX_BYTES` | 日志轮转前单文件大小上限，字节。 (int) | `10 * 1024 * 1024` | `10485760` |
| `LOG_BACKUP_COUNT` | 保留的轮转日志备份数量。 (int) | `5` | `5` |

### 数据库路由

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `PRIMARY_DATABASE` | 主数据库选择：mysql、postgresql、sqlite 或 mssql。 (str \| None) | `None` | `mysql` |
| `DATABASE_TYPE` | PRIMARY_DATABASE 为空时使用的兼容数据库选择。 (str) | `'mysql'` | `mysql` |
| `MYSQL_ENABLED` | 允许将 MySQL 选作主数据库。 (bool) | `True` | `True` |
| `POSTGRES_ENABLED` | 允许将 PostgreSQL 选作主数据库。 (bool) | `False` | `False` |
| `SQLITE_ENABLED` | 允许将 SQLite 选作主数据库。 (bool) | `False` | `False` |
| `MSSQL_ENABLED` | 允许将 SQL Server 选作主数据库。 (bool) | `False` | `False` |

### 数据库连接

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `MYSQL_HOST` | 应用和 root 维护连接共用的 MySQL 主机。 (str) | 必填，无源码缺省 | `127.0.0.1` / `mysql` / `replace-with-external-mysql-host` |
| `MYSQL_PORT` | 应用和 root 维护连接共用的 MySQL TCP 端口。 (int) | 必填，无源码缺省 | `3307` / `3306` |
| `MYSQL_USER` | MySQL 应用账号。 (str) | 必填，无源码缺省 | `devuser` / `appuser` |
| `MYSQL_PASSWORD` | MySQL 应用口令；保密。 (str) | 必填，无源码缺省 | placeholder |
| `MYSQL_DATABASE` | MySQL 主应用数据库名。 (str) | 必填，无源码缺省 | `aiis_ics_architecture` |
| `MYSQL_ROOT_USER` | MySQL root 维护连接账号，不用于应用请求。 (str) | 必填，无源码缺省 | `root` |
| `MYSQL_ROOT_PASSWORD` | MySQL root 维护口令；保密。 (str) | 必填，无源码缺省 | placeholder |
| `POSTGRES_HOST` | PostgreSQL 主机，选用时必填。 (str \| None) | `None` | `localhost` / `postgres` |
| `POSTGRES_PORT` | PostgreSQL TCP 端口，选用时必填。 (int \| None) | `None` | `5432` |
| `POSTGRES_USER` | PostgreSQL 应用账号，选用时必填。 (str \| None) | `None` | `devuser` / `appuser` |
| `POSTGRES_PASSWORD` | PostgreSQL 应用口令；保密。 (str \| None) | `None` | placeholder |
| `POSTGRES_DATABASE` | PostgreSQL 应用数据库名，选用时必填。 (str \| None) | `None` | `aiis_ics_architecture` |
| `SQLITE_DATABASE_PATH` | SQLite 数据库文件路径。 (str) | `'./data/aiis_ics_architecture.sqlite3'` | `./data/aiis_ics_architecture.sqlite3` |
| `MSSQL_HOST` | SQL Server 主机。 (str) | `'host.docker.internal'` | `host.docker.internal` |
| `MSSQL_PORT` | SQL Server TCP 端口。 (int) | `1433` | `1433` |
| `MSSQL_USER` | SQL Server 应用账号。 (str) | `'sa'` | `sa` |
| `MSSQL_PASSWORD` | SQL Server 应用口令；保密。 (str) | `''` | placeholder |
| `MSSQL_DATABASE` | SQL Server 应用数据库名。 (str) | `'aiis_ics_architecture'` | `aiis_ics_architecture` |
| `MSSQL_DRIVER` | 已安装的 SQL Server ODBC 驱动名称。 (str) | `'ODBC Driver 18 for SQL Server'` | `ODBC Driver 18 for SQL Server` |
| `MSSQL_TRUST_SERVER_CERTIFICATE` | 跳过 SQL Server 证书验证并信任该证书。 (bool) | `True` | `True` |

### 账号初始化

| key | 用途/类型 | 源码缺省 | 公开模板值 |
| --- | --- | --- | --- |
| `ADMIN_BOOTSTRAP_ENABLED` | 仅为显式 bootstrap 维护动作启用该账号。 (bool) | `False` | `False` |
| `ADMIN_BOOTSTRAP_USERNAME` | Bootstrap 查找或创建的用户名。 (str) | `'admin'` | `admin` |
| `ADMIN_BOOTSTRAP_PASSWORD` | 启用时所需非空 bootstrap 口令；保密。 (str) | `''` | `""` |
| `ADMIN_BOOTSTRAP_NAME` | 新建 bootstrap 账号的显示名。 (str) | `'Administrator'` | `Administrator` |
| `ADMIN_BOOTSTRAP_ROLE` | 新建 bootstrap 账号的角色。 (str) | `'admin'` | `admin` |
| `ADMIN_BOOTSTRAP_RESET_PASSWORD` | 允许显式 bootstrap 重置已有账号口令并重新激活。 (bool) | `False` | `False` |
| `SUPERVISOR_BOOTSTRAP_ENABLED` | 仅为显式 bootstrap 维护动作启用该账号。 (bool) | `False` | `False` |
| `SUPERVISOR_BOOTSTRAP_USERNAME` | Bootstrap 查找或创建的用户名。 (str) | `'supervisor'` | `supervisor` |
| `SUPERVISOR_BOOTSTRAP_PASSWORD` | 启用时所需非空 bootstrap 口令；保密。 (str) | `''` | `""` |
| `SUPERVISOR_BOOTSTRAP_NAME` | 新建 bootstrap 账号的显示名。 (str) | `'Supervisor'` | `Supervisor` |
| `SUPERVISOR_BOOTSTRAP_ROLE` | 新建 bootstrap 账号的角色。 (str) | `'supervisor'` | `supervisor` |
| `SUPERVISOR_BOOTSTRAP_RESET_PASSWORD` | 允许显式 bootstrap 重置已有账号口令并重新激活。 (bool) | `False` | `False` |
| `OPERATOR_BOOTSTRAP_ENABLED` | 仅为显式 bootstrap 维护动作启用该账号。 (bool) | `False` | `False` |
| `OPERATOR_BOOTSTRAP_USERNAME` | Bootstrap 查找或创建的用户名。 (str) | `'operator'` | `operator` |
| `OPERATOR_BOOTSTRAP_PASSWORD` | 启用时所需非空 bootstrap 口令；保密。 (str) | `''` | `""` |
| `OPERATOR_BOOTSTRAP_NAME` | 新建 bootstrap 账号的显示名。 (str) | `'Operator'` | `Operator` |
| `OPERATOR_BOOTSTRAP_ROLE` | 新建 bootstrap 账号的角色。 (str) | `'operator'` | `operator` |
| `OPERATOR_BOOTSTRAP_RESET_PASSWORD` | 允许显式 bootstrap 重置已有账号口令并重新激活。 (bool) | `False` | `False` |


### 入口与副作用说明

源码运行读取本目录 `.env`；dev/prod Docker 入口把所选 env 提供为 `/app/.env`；打包读取可执行
文件同目录配置。操作者需审查进程环境覆盖，并移除其中活动旧权限变量后自行重启。修改文件
本身不代表运行服务已加载。env 注释统一英文，本说明提供[英文对应版本](README.md#configuration-reference)。

`PRIMARY_DATABASE` 优先于兼容项 `DATABASE_TYPE`；支持 `postgres`/`pg`、
`sqlserver`/`sql_server` 等别名。所选数据库对应 `*_ENABLED` 必须打开；这些开关允许选择，
不会启动数据库，也不表示每个请求连接全部数据库。普通异步/同步应用 session 使用主数据库。
MySQL root 维护通过 `MYSQL_ROOT_USER`/`MYSQL_ROOT_PASSWORD` 和 `MYSQL_HOST`/`MYSQL_PORT`
连接，不使用普通应用账号；这些字段不是 Docker 镜像 root 账号初始化授权来源。驱动与外部数据库
可用性仍是部署前提。database-only 空卷初始化不会修改已有卷中的账号。

`TESTING=True` 将 MySQL 应用 URL 切到独立测试库（源码默认库名
`aiis_ics_architecture_test`），不是所有数据库引擎的通用沙盒。数据库测试可能建/清该库，必须
显式使用获批隔离目标；静态检查使用 `no_db` 测试。公开模板关闭 TESTING、业务 mock 和 Projection
runner。Projection 读取 CA raw facts，不轮询 PLC，必须只有一个活动 writer：仅在指定单 worker
宿主开启，不能在普通多 worker API 部署中开启。间隔和批量上限影响轮询/工作批次。
`TZ` 只设置进程时区，不迁移数据库时间戳或数据库服务端时区。

上方全部 18 个 bootstrap 字段仅用于显式 `main.py --maintenance bootstrap-users`，不用于普通
启动/登录或 Alembic。每个角色的 ENABLED 默认关闭；开启时 PASSWORD 必须非空。账号不存在时
按 USERNAME/PASSWORD/NAME/ROLE 创建；已存在时保持，除非 RESET_PASSWORD 为 true。Reset 修改
口令、重新激活账号，仅在原 name/role 为空时补齐，不覆盖已有非空角色/名称。完成预期维护后
应关闭 reset。授权数组不创建账号、不更新口令。维护是需要独立操作授权的数据库写入；其入口
会先执行上方说明的权限配置校验。

通用当前模块授权示例为 supervisor `["monitor","system","control-agent-read"]`、operator
`["monitor"]`。当前 monitor router 仅包含 GET `/monitor/collector/status` 和
GET `/monitor/realtime/latest`，operator 获得的是这两个事实查询。`system` 包含用户管理写入，
仍受独立 actor 限制；`control-agent-read` 是 action-scope 查询。这是显式授权选择，不是公开模板
安全 `[]` 缺省。本轮获批本机三环境迁移为 host/prod operator 新增 monitor，dev supervisor 新增
三项且 operator 新增 monitor；不是单纯等值变量改名。未来在同 key 下新增接口需要重新审查。
