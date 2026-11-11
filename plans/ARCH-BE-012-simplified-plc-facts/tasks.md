Task ID: ARCH-BE-012
Revision: r4
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r4 A 源码候选 -> fresh-context Verification；B 隔离运行计划待具体目标授权
Approved Spec SHA-256: 19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0

# Development 实施记录

Human Owner 已批准 r4 实施范围。本轮交付后端源码候选及 A 离线自检。隔离 MySQL、实际 dev 数据库和 DAA 的后续步骤按规格分别进入对应门禁。

1. 完成两张值表、迁移和旧版本兼容。
2. 完成写入、授权读取和有界维护。
3. 固定合同工件，执行防数据库连接的源码检查，并记录真实结果。

## A 源码实现与自检

交付树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。源码仍为工作树改动。批准后的 spec SHA-256 为 `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0`。37 个源码、合同和受影响索引的逐文件摘要见 [development-r4-source-hashes.txt](evidence/development-r4-source-hashes.txt)，清单 SHA-256 `fbf11ead53653f128865123a9be34c3f7d9ce8df43d63dd1081bd965eeb1abe8`。

| 表面 | 实际实现 |
| --- | --- |
| v2 Domain / Schema / API | 单 PLC/DB 样本，512 点和 512 KiB 双上限，冻结正文 SHA、严格字段、每实例 Bearer、来源范围和上海时钟。新增四个登录只读查询，角色权限与数据范围分别校验。 |
| Model / 迁移 / 事务 | 两张值表及 `1b3d5f7a9c20 → 2c4e6a8b0d12`。历史唯一键裁定冲突，在一个事务中更新逐点 latest，提交成功后回执。过期水位保留实例、代次和序号。 |
| 旧接口兼容 | v1 新增已知 77 表后继 profile，保留七表 F7 和 schema-only 再核验。BE-010 采用证据只接受旧 revision 和该精确后继，目标匹配继续执行。 |
| 维护 / 合同 | `cleanup-v2 --plan/--apply` 验证目标及确认串，按行数、字节和时间预算清理。新增五个合同工件、双语模块及维护说明。模块 registry 内声明 `plc_facts.v2.*`，HTTP 返回 r4 固定的 `plc_facts_v2.*`。 |
| 验证入口 | `backend/tests/test_plc_facts_v2.py` 覆盖离线输入、合同、权限、事务故障及清理预算。`backend/tests_mysql/test_plc_facts_v2.py` 限定成对 loopback 端口、alias 和 schema 前缀，提供 HTTP、重试、旧 v1、读权限及负载入口。BE-010 runner 增加精确后继的独立确认及目标 UUID 检查。 |

在排除真实 `.env`、数据及日志的临时源码副本中，使用项目 `uv` 锁定环境执行下列定向自检。Python 入口在导入项目测试前设置公开合成环境，显式拦截 `socket.connect`、`socket.create_connection`、`sqlite3.connect`、`pymysql.connect`、`aiomysql.connect`、SQLAlchemy `Engine.connect/raw_connection`，并使用 `-m no_db`。结果为 **80 passed，exit 0**。

```bash
cd /private/tmp/arch-be012-r4-devA-sqmry467/backend
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be012-r4-uv-cache uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python - <<'PY'
import os, socket, sqlite3, sys
from pathlib import Path
from tests.module_admission_fixtures import public_environment
os.environ.update(public_environment())
def denied(*args, **kwargs):
    raise AssertionError('ARCH-BE-012 no-DB guard')
socket.socket.connect = denied
socket.create_connection = denied
sqlite3.connect = denied
import pymysql, aiomysql
pymysql.connect = denied
aiomysql.connect = denied
from sqlalchemy.engine import Engine
Engine.connect = denied
Engine.raw_connection = denied
sys.path.insert(0, str(Path.cwd() / 'tests'))
import pytest
sys.exit(pytest.main(['-q', '-p', 'no:cacheprovider', '-m', 'no_db',
    '--basetemp=/private/tmp/arch-be012-r4-pytest',
    'tests/test_plc_facts_v2.py', 'tests/test_plc_facts_migration.py',
    'tests/test_plc_facts_maintenance.py', 'tests/test_business_integration_storage.py',
    'tests/test_business_integration_migration.py']))
PY
```

同一 no-DB guard 的扩展运行包含 `tests/test_plc_facts_*.py` 与 `tests/test_business_integration_*.py`，结果 **536 passed、2 failed，exit 1**。扩展运行先于最后一轮 v2 吊销边界和 B fixture 调整，后者由上面的最新定向运行覆盖。两项失败保留如下。

| 精确 node ID | 原因与复现 |
| --- | --- |
| `tests/test_plc_facts_compatibility.py::test_isolated_owner_has_no_permissions_dependencies_or_projection` | 旧断言要求 `manifest.permissions == ()` 且只登记 v1 router。r4 明确增加 `plc-facts-read` 和 v2 router，旧断言因批准的行为变化失效。原版 manifest 独立单跑 1 passed，候选独立单跑 1 failed。新 r4 装配测试核对原 v1 三路存在及非 admin 默认无新权限。 |
| `tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes` | 扩展同进程运行时，先前 `create_app` 已缓存 `app.router`，后续内存 monkeypatch 不重建路由。原版和候选分别在新进程独立单跑均 1 passed。另以原版 manifest 先创建 app、再内存禁用并再次创建，观察旧 v1 路由仍被缓存。该测试的进程内重组现象来自既有 router 缓存。 |

另外在无 DB guard 下编译 20 个受影响 Python 文件，离线确认 Alembic 唯一 head `2c4e6a8b0d12` 与三个 JSON 工件，exit 0。13 份受影响 Markdown 的相对链接检查为 0 缺失，`git diff --check` 和逐文件空白检查 exit 0。35 个 backend/contract 文件的正式树摘要与隔离候选一致。首次 A 运行曾因新错误键不符合 registry namespace、临时副本缺 v1 vectors 而失败，已分别以内部枚举映射和补齐公开合同副本修正，结果以上述最终运行及扩展运行分别为准。

## A 交接与限制

Development 交接的是 r4 源码和 A 自检候选。B 的真实 MySQL、HTTP、故障、清理和 30 分钟负载尚无运行结果，AC01–AC09 中依赖真实数据库的部分待 B 证据。现有 dev 目标、DAA 和现场链路继续按各自门禁处理。请 fresh-context Verification 读取已批准 spec、本文、源文件摘要、实际 diff 及自检结果，独立判断源码和未运行门禁。

本次自有临时资源包括 `/private/tmp/arch-be012-r4-devA-sqmry467` 公开源码副本、`/private/tmp/arch-be012-r4-pytest` 和 `/private/tmp/arch-be012-r4-pytest-expanded` 测试目录，以及 `/private/tmp/arch-be012-r4-uv-cache`。它们保留供当前独立验证对照，关键结果和源码摘要已写入任务目录。没有创建分支、worktree 或 commit。

## B 隔离运行计划草案

本计划供源码自检后单独确认。每轮使用独占 MySQL 8.4.6、独立 volume、网络、临时用户、两个 schema 和 loopback HTTP 服务。先核查名称和端口未被占用。任何目标不符或命令失败时停止该轮，保留脱敏证据。

| 轮次 | MySQL 容器 / volume / network | 宿主机 MySQL / HTTP | alias | schema |
| --- | --- | --- | --- | --- |
| Development | `arch-be012-r4-dev-mysql` / `arch-be012-r4-dev-data` / `arch-be012-r4-dev-net` | `127.0.0.1:13392` / `127.0.0.1:18392` | `arch-be012-r4-dev` | `arch_be012_r4_dev_fresh`、`arch_be012_r4_dev_upgrade` |
| Verification | `arch-be012-r4-qa-mysql` / `arch-be012-r4-qa-data` / `arch-be012-r4-qa-net` | `127.0.0.1:13393` / `127.0.0.1:18393` | `arch-be012-r4-qa` | `arch_be012_r4_qa_fresh`、`arch_be012_r4_qa_upgrade` |

每轮按以下顺序执行，命名资源的创建、数据库写入、故障注入及回收均包含在待确认的具体操作中。

1. 在 `/private/tmp/arch-be012-r4-<round>-<run>/source/` 建立本轮源码副本，在同级 `private/` 建立私有运行目录。v2 profile 放在 `private/`，位于源码仓库根目录之外。排除 `.env`、真实数据和日志，核对候选文件摘要。随机生成仅本轮使用的 root、迁移、应用、机器与登录凭据，私有文件权限设为 `0600`，证据只记录摘要和目标标识。
2. 创建该轮 network、volume 和 `mysql:8.4.6` 容器，MySQL 端口仅绑定表中 loopback 地址，数据库时区为 `+08:00`、隔离级别为 `REPEATABLE-READ`。以一次性 root 凭据创建表中两个 schema 和独立迁移/应用账号。迁移账号只在本轮两个 schema 获得 `SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/INDEX/DROP/REFERENCES`，其中 `DROP` 用于获批空表降级。应用账号只在本轮两个 schema 获得 `SELECT/INSERT/UPDATE/DELETE`。
3. 从新容器读取 server UUID、版本、schema 和会话时钟，并将 UUID 写入本轮仓外 v2 私有配置及 `ARCH_BE012_B_SERVER_UUID`。将 alias、schema、MySQL/HTTP 端口和 UUID 拼成 `ARCH_BE012_B_CONFIRM=RUN:<alias>:<schema>:<uuid>:<mysql-port>:<http-port>`。测试入口仅接受表中成对端口、alias 和 schema 前缀。
4. fresh schema 从空库沿 Alembic 唯一链显式升级至 `2c4e6a8b0d12`，核对 77 张应用表。upgrade schema 先到 `0a2c4e6f8b10` 并建立合成 v1 来源和回执，再到 `1b3d5f7a9c20` 建立合成 BE-010 业务及永久回执。记录旧表定义、标识/值/精度摘要、v1 F7、adoption ID、storage epoch、来源和 proof 数，再升级至 `2c4e6a8b0d12`。先核对旧证据失配，再执行获批准的 v1 schema-only 再核验并提供 BE-010 新 revision 的合成采用证据。
5. 通过进程环境显式设置 `TESTING=True`、表中端口及测试 schema，主库名使用不同的合成名称。v2 私有配置授权 `daa-a/gen-a` 对 PLC-A 的 DB21/DB22 及 PLC-B 的 DB21。合成 supervisor 获 `plc-facts-read` 和 PLC-A/DB21 读范围，合成 admin 读范围为空，合成 operator 无权限。为三名测试用户生成普通 access token，启动正式 FastAPI 入口到表中 loopback HTTP 端口。禁用 mock、Projection runner 和 bootstrap。
6. 使用项目锁定环境执行 `tests_mysql/test_plc_facts_v2.py`，以 `--confcutdir=tests_mysql` 避开共享清库 fixture。提供 `ARCH_BE012_B_OPERATION_APPROVAL`、`ARCH_BE012_B_TOKEN`、`ARCH_BE012_B_READER_TOKEN`、`ARCH_BE012_B_ADMIN_TOKEN`、`ARCH_BE012_B_DENIED_TOKEN`、目标变量和本轮 `ARCH_BE012_B_CONFIRM`。fresh schema 运行该文件并以 `-k 'not v1_revalidated and not steady_load'` 执行功能冒烟。upgrade schema 提供旧 v1 adoption ID、epoch、F7、proof 数和下一序号，设置 `ARCH_BE012_B_RUN_LOAD=True`，运行整个文件，包括唯一一次 30 分钟双 PLC、每秒各一份 64 点样本和同期 10000 行过期清理。Development 与 Verification 各自的 upgrade schema 各执行一次负载。逐项保存 pytest 输出、HTTP 状态、P95、积压和耗时。
7. 在 upgrade schema 使用隔离 BE-010 runner 验证旧 revision 证据拒绝、新 revision 合成证据下八路写入与永久回执，并对照第 4 步摘要。执行空表降级及非空降级拒绝、提交前失败、提交后断连、并发顺序、清理竞争及越权查询。每项记录输入、输出、版本和资源标识，未执行项保留未验证状态。
8. 保存脱敏证据到本任务 `evidence/`。Verification 只记录和复核资源及证据，由获得具体回收授权的协调者在不再使用后停止本轮 HTTP 进程，回收表中属于该轮的容器、volume、network 和本轮私有目录，再核查资源已不存在。另一轮使用独立凭据、端口、schema 和证据复现。

现有 `aiis-ics-arch-database-only` 及其 `3307` 端口在本计划外。现有 dev 库增量升级需在隔离结果通过后另行核对目标、备份和实际采用状态。

## QA1 返工 Development 自检与 QA2 交接

同一 `ARCH-BE-012 r4`，交付树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`；批准 spec 仍为 SHA-256 `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0`。消费的独立 QA1 checklist SHA-256 为 `a88457754cf580454703a1b9b60e663e64df03002830c0723145d473f8e77a61`。本节只追加，不重写上次交接及其 37 文件摘要；追加前原 `tasks.md` SHA-256 为 `e8fcc930c8c58a3b54f96caf7bdc6b69d42459d4c5a28147f165f7e3a826b65d`。

| 返工项 | Development 修改和证据范围 |
| --- | --- |
| QA1-01 | 重复键回滚后，锁定身份记录，再读取持锁后的数据库 `CURRENT_TIMESTAMP(6)` 验证截止时间；新写入在竞争等待及更新后、提交前再验证。测试覆盖等待期间到期和新样本回滚，DB 时钟不取宿主日历时间。 |
| QA1-02 | GET 重复 query 校验移入登录及 `plc-facts-read` 依赖之后；POST 在机器 Bearer 鉴权之后校验。离线 HTTP 测试覆盖未登录/失效 401、无权限 403、有权重复参数 422。 |
| QA1-03 | REAL 的输入数值 token 经过严格 JSON 数字语法及 binary32 有限性检查，两张既有 JSON 值列内部以十进制文本保存 REAL；latest 和历史详情从受校验 token 输出原精度 JSON number。回归覆盖高精度、小指数、大整数、负零、数值伪装为字符串及 DB 文本注入，公开 schema、路由和 wire 类型未变；中英文说明已更新。 |
| QA1-04 | 每个维护事务连接均先设置行锁/元数据锁和 SQL 等待上限，前后核对精确目标与 DB 时钟；2 秒单调预算跨配置、目标核验及两表候选查询检查，预算不足不发新的带锁查询。最终报告释放锁并以 `oldestKnown` 表示积压是否已读取；维护专用连接使用 `NullPool` 与有界连接读写超时。替身回归覆盖两表 200/2000 上限、等待耗尽和每事务重新核验；真实 MySQL 等待耗时待 B。 |
| QA1-B1 | BE010 runner 增加严格成对端口、schema、UUID 和双确认的 r4 previous/successor 两阶段；后继先验证旧采用证据被三个 owner 拒绝，再复用原永久回执与八路新证据测试；无 r4 phase 时原 BE010 r2 路径保留。纯离线 guard 回归覆盖两阶段和错配端口。 |
| QA1-B2 | B 测试增加 75 表上一 head 和 77 表后继的 v1 F7/epoch/adoption/source/proof 与三路 HTTP 入口；下方流程明确 71→75 和 75→77 两次 schema-only 再核验，以及 v1、v2、角色运行配置。 |
| QA1-B3 | B 真实 HTTP 客户端均设置 `trust_env=False`；离线代理环境及 AST 回归验证该限制。 |
| QA1-B4 | B 负载入口准备真实 CLI 每分钟 30 tick、逐 tick 落盘脱敏行/字节/积压/耗时、15 分钟内排空但后续心跳继续，并保护未到期行和 tombstone 反重放水位；另准备故障、清理争锁和空/非空降级夹具。纯离线替身核对 30 行心跳持续生成，不能代替真实负载。 |
| 测试装配 | 新的 v2 正常装配测试暂存、重载并恢复 `app.router` 模块缓存；不更改 Core 和旧测试。同进程先执行旧 disabled 测试再执行新测试已通过。 |

本轮在 `/private/tmp/arch-be012-r4-devA2-v6u5jmmp/backend` 公开源码副本执行；副本排除真实 `.env`、数据、日志和虚拟环境。复用正式项目锁定环境，不安装依赖。下面是实际定向命令；防线在项目测试导入前拒绝 socket 连接、SQLite、PyMySQL、aiomysql 和 SQLAlchemy Engine 连接。结果 **88 passed in 11.45s，exit 0**：

```bash
cd /private/tmp/arch-be012-r4-devA2-v6u5jmmp/backend
env -i PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be012-r4-qa1-uv-cache \
  uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python - <<'PY'
import os,socket,sqlite3,sys
from pathlib import Path
from tests.module_admission_fixtures import public_environment
os.environ.update(public_environment())
def denied(*args,**kwargs): raise AssertionError('ARCH-BE-012 QA1 no-DB guard')
socket.socket.connect=denied
socket.socket.connect_ex=denied
socket.create_connection=denied
sqlite3.connect=denied
import pymysql,aiomysql
pymysql.connect=denied
aiomysql.connect=denied
from sqlalchemy.engine import Engine
Engine.connect=denied
Engine.raw_connection=denied
sys.path.insert(0,str(Path.cwd()/'tests'))
import pytest
sys.exit(pytest.main(['-q','-p','no:cacheprovider','-m','no_db',
    '--basetemp=/private/tmp/arch-be012-r4-qa1-pytest',
    'tests/test_plc_facts_v2.py','tests/test_plc_facts_migration.py',
    'tests/test_plc_facts_maintenance.py','tests/test_business_integration_storage.py',
    'tests/test_business_integration_migration.py']))
PY
```

同一环境和防线，`pytest.main` 的文件参数替换为以下两个 node ID，并使用独立 `--basetemp=/private/tmp/arch-be012-r4-qa1-order`，结果 **2 passed in 15.37s，exit 0**，次序即列表次序：

```text
tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes
tests/test_plc_facts_v2.py::test_normal_app_registers_routes_and_permission
```

对同一副本使用 `env -i PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be012-r4-qa1-uv-cache uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -` 执行不写字节码的 `compile`，实际编译 20 个本任务 Python 文件、确认 Alembic 唯一 head `2c4e6a8b0d12` 的前驱 `1b3d5f7a9c20`，并解析 v2 三个 JSON 工件，exit 0；不连接数据库。正式树 `git diff --check` exit 0。先前扩展批次中旧硬编码 `manifest.permissions == ()` / 仅 v1 路由的失败仍是 r4 明确增加只读权限与 v2 路由造成的预期合同变化；原测试未改。原版/候选独立单跑和首次扩展结果见本文件前文，不将其称为本轮通过。

完整 37 文件候选摘要见 [development-r4-qa1-fix-hashes.txt](evidence/development-r4-qa1-fix-hashes.txt)，清单 SHA-256 `f19a4d0829773cb20243263168a43bdabda4883dacacd8de3870f17e3615325f`。其中 35 个 backend/contracts 文件与本轮最终公开副本逐文件 SHA 一致；清单也记录当时的 spec 与共享 `CODE_INDEX.md`。变更文件精确列表以该清单和相对上一份清单的摘要变化为准；两份清单均保留。正式树中其他任务的 dirty 改动未回退。

### B 运行计划补充：覆盖前文第 4–7 步

以下是未来每轮的可复现次序，仍须具体目标和操作另批，本轮没有执行。容器、端口、schema、有限 grants 和资源回收分工沿用前表与第 1–3、8 步；每轮证据目录与另一轮隔离。每次迁移、命令、HTTP 服务启动前重新核对该轮 UUID/schema/端口和账号，所有失败即停，输出只保留脱敏数据。

1. fresh 库显式升级到 `2c4e6a8b0d12`。upgrade 库显式升级到 `0a2c4e6f8b10`（71 张应用表），从 `contracts/published/http-api/plc-facts-v1/vectors.json` 的 `request.cycles[0].contextUtf8` 原样生成合成 context 文件及 `sha256:` 摘要；用 `adopt --plan` 后 `--apply` 采用 `plc-demo / daa-demo / generation-demo / config-demo`、`--expected-binding-revision 0 --seq-from 1`，指定本轮随机 UUID storage epoch、目标 alias/schema、`--expected-schema-revision 0a2c4e6f8b10`、批准引用及确认人；apply 设置 `PLC_FACTS_MAINTENANCE_ENABLED=True`、`--confirm APPLY:adopt:<alias>:<schema>:<epoch>`。记录 adoption ID、epoch、F7、source、proof 数和下一序号。升级到 `1b3d5f7a9c20`（75 表），在核对原 F7、原 adoption/epoch 后执行 `adopt --revalidate-schema-only --plan` 和同参数 `--apply`，其中 `--expected-schema-revision 1b3d5f7a9c20 --expected-adoption-id <原ID> --expected-storage-epoch <原epoch>`；不得传来源参数，apply 使用上面的精确确认串。保留再核验前后状态及证据摘要。
2. 使用公开配置并在私有目录提供独立随机密钥，进程显式设置 `PRIMARY_DATABASE=mysql`、`TESTING=True`、`MYSQL_HOST=127.0.0.1`、本轮 `MYSQL_PORT` 和合成非 root 应用账号、不同于测试库的合成 `MYSQL_DATABASE`、`TEST_MYSQL_DATABASE=<本轮upgrade>`；mock、Projection runner、三个 bootstrap 均为 `False`。设置 `PLC_FACTS_ENABLED=True`、`PLC_FACTS_PLC_IDS_JSON='["plc-demo"]'`、`PLC_FACTS_STORAGE_PROFILE=mysql84_shanghai_v1`、随机 64 位十六进制 `PLC_FACTS_CURSOR_HMAC_KEY`；`PLC_FACTS_V2_ENABLED=True` 和 `PLC_FACTS_V2_PROFILE_FILE=<本轮private profile>` 指向以同 UUID/schema 和后继 revision 为目标的配置，75 表阶段 v2 写入须拒绝。配置 `SUPERVISOR_API_PERMISSIONS_JSON='["plc-facts-read"]'`、`OPERATOR_API_PERMISSIONS_JSON='[]'`，profile 对 supervisor 仅读 PLC-A/DB21、admin 无读取范围。分别建立三名仅存在本轮 schema 的合成 `User`（supervisor、admin、operator），用本轮 JWT 密钥和 `core.jwt.create_access_token` 签发足够覆盖 30 分钟测试的独立短期 access token；密钥和 token 仅存私有目录，证据不写其值。正式 FastAPI 入口只绑定本轮 loopback HTTP 端口。
3. 为 B runner 设置 `ARCH_BE012_B_OPERATION_APPROVAL`、`ARCH_BE012_B_TARGET_ALIAS`、`ARCH_BE012_B_SCHEMA`、`ARCH_BE012_B_SERVER_UUID`、`ARCH_BE012_B_MYSQL_PORT`、`ARCH_BE012_B_HTTP_PORT`、`ARCH_BE012_B_CONFIRM=RUN:<alias>:<schema>:<uuid>:<mysql-port>:<http-port>`、`ARCH_BE012_B_TOKEN` 和私有 profile 路径。设置 `ARCH_BE012_B_V1_PHASE=previous` 与记录的 `ARCH_BE012_B_V1_ADOPTION_ID`、`ARCH_BE012_B_V1_STORAGE_EPOCH`、`ARCH_BE012_B_V1_FINGERPRINT`（F7 的 64 位 hex）、`ARCH_BE012_B_V1_PROOF_ROWS`、`ARCH_BE012_B_V1_NEXT_SEQUENCE`，从 `source/backend` 运行 `uv run --offline --frozen --no-sync pytest -q --confcutdir=tests_mysql tests_mysql/test_plc_facts_v2.py -k v1_previous_revision_only`；记录三路状态后重新读取 proof/下一序号，供后继核对。
4. 在同一 upgrade 库运行 BE010 上一阶段：在 `source/backend/profile.json` 建立仅含公开合成 `{"profile":"BE010-r2-B","expected_table_count":75,"target_revision":"1b3d5f7a9c20"}` 的文件；设置 `BE010_R4_PHASE=previous`、`BE010_SUCCESSOR_REVISION=1b3d5f7a9c20`、`BE010_SUCCESSOR_ACK=ARCH-BE-012-r4-successor`，以及 `BE010_MYSQL_EXECUTION_ACK=ARCH-BE-010-r2-B`、`BE010_MYSQL_SCHEMA_ACK=<本轮upgrade>`、`BE010_MYSQL_ENDPOINT_ACK=127.0.0.1:<本轮MySQL端口>`、简单唯一 `BE010_MYSQL_RUN_ID=<base>` 和 `BE010_SOURCE_REVISION_ACK=<本轮冻结源码标识>`；再运行 `uv run --offline --frozen --no-sync python tests_mysql/test_business_integration.py --suite business`。保留生成的 `be010-business-proof.json` 和旧数据/回执摘要。
5. 将 upgrade 库升级到 `2c4e6a8b0d12`，确认 v1 旧采用凭据失配、原 F7 和事实不变；按步骤 1 的 schema-only plan/apply 再核验，但 revision 指定 `2c4e6a8b0d12` 且保留原 adoption ID/epoch。BE010 切换 `BE010_R4_PHASE=successor`、`BE010_SUCCESSOR_REVISION=2c4e6a8b0d12`；先用同一 `<base>` 执行 `--suite retained`（入口先验证三个 owner 拒绝旧证据，再验证旧永久回执），再用新唯一 run ID 执行 `--suite business`（三个 owner 使用新证据及八路新写入/故障场景）。比对两阶段数据、来源、证据和回执，不将脚本存在当作结果。
6. 配置合成写入源 `daa-a/gen-a` 对 PLC-A 的 DB21/DB22 和 PLC-B 的 DB21；合成 reader/admin/operator token 分别传 `ARCH_BE012_B_READER_TOKEN`、`ARCH_BE012_B_ADMIN_TOKEN`、`ARCH_BE012_B_DENIED_TOKEN`。提供与应用账号不同、以 `archbe012_` 开头的本轮迁移账号和密码 `ARCH_BE012_B_MIGRATION_USER/PASSWORD`，另设 `ARCH_BE012_B_DDL_CONFIRM=MIGRATE:<alias>:<schema>:<uuid>:<mysql-port>`。fresh 运行 `pytest -q --confcutdir=tests_mysql tests_mysql/test_plc_facts_v2.py -k 'not v1_previous_revision_only and not v1_revalidated and not steady_load'`。upgrade 更新步骤 3 的 v1 数量和下一序号，设置 `ARCH_BE012_B_RUN_LOAD=True`、`ARCH_BE012_B_TICK_EVIDENCE=<本轮目录>/evidence/cleanup-ticks.jsonl`，运行相同入口并指定 `-k 'not v1_previous_revision_only'`。每轮只有 upgrade 库执行一次 30 分钟负载；入口要求该轮 v2 两表起始为空，先测试空表降级再升级、非空降级拒绝，然后覆盖 HTTP、丢 ACK、提交前回滚、顺序竞争、过期/读权限、REAL 往返和清理争锁。每 tick 实际调用 CLI，持久记录脱敏行数、字节、积压及耗时；15 分钟排空后仍运行到第 30 次，并检查未到期值和 tombstone 旧样本重放水位。
7. 在该轮功能/负载完成后，以明确记录的合成数据进行 AC03 可复现补充：先并发提交同一 PLC/DB 的旧/新序号，核对两条历史与最新序号；停止并以完全相同来源配置重启本轮 HTTP 进程，确认相同凭据可重试且已提交数据保留。记下仍有效的旧历史 ID，停止进程，仅在本轮私有 profile 中将 PLC-A 改为另一独立机器凭据 `daa-b/gen-b`（PLC-A DB21/22），保留 PLC-B 原来源，然后重启该轮进程。旧 `daa-a/gen-a` 向 PLC-A 写入应 403；授权 reader 仍可读取未过期旧历史；`daa-b/gen-b` 从 seq 1 提交并接管 PLC-A latest；确认两凭据独立、PLC-B 不受影响。记录配置摘要、状态与脱敏回执，保留变更前后 profile 摘要供 QA 复核。

本轮没有连接任何数据库（包括 SQLite）、运行 Docker/迁移/DDL/DML、访问设备或 DAA，也没有运行 B 计划。临时公开副本 `/private/tmp/arch-be012-r4-devA2-v6u5jmmp`、pytest 目录 `/private/tmp/arch-be012-r4-qa1-pytest`、`/private/tmp/arch-be012-r4-qa1-order` 与 uv 缓存 `/private/tmp/arch-be012-r4-qa1-uv-cache` 为本任务所用，保留到 fresh QA 完成候选对照后由协调者按资源规则清理；关键结果与摘要已记录于本 bundle。

**Developer handoff**：请 fresh-context Verification 消费 r4 spec、完整 tasks、QA1 checklist、原始和返工两份 SHA 清单、工作树 diff 与上述 A 证据，独立复核 QA1 返工。真实隔离 B、QA verdict、Human Owner 最终验收、现有 dev 库升级和 DAA 工作均没有在本轮发生或被本交接授权。

## QA2 返工 Development 自检与 QA3 交接

同一获批 `ARCH-BE-012 r4`，交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 为未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`；spec SHA-256 `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0`，消费的 QA2 checklist SHA-256 `432b9366d8cac32b8ebe11269f7760b65181e013734dc771e5eb1c568b3f1415`。本节只追加；追加前保留的全部既有 `tasks.md` SHA-256 为 `cf2810ed9f7bf667c0582cbd303beb4d43596df72349ff8fab934fa6955b2749`。

- **QA2-01：** REAL 接受条件为绝对值小于 binary32 最近舍入的精确溢出中点 `M = (1 << 128) - (1 << 103)`。整数直接比较；小数和指数先比较 binary64，恰好等于 M 时以 `Decimal(token).copy_abs()` 比较原数值，不执行二次舍入或定点展开。输入校验与 DB 内部文本恢复采用同一规则。18 个离线边界案例覆盖正负、整数、小数、指数的 M 前一极小量、M 及 M 后一极小量，并验证接受值的内部存储与数字输出；原有高精度、大整数、负零和极小指数回归继续运行。
- **QA2-B1：** 两个 B runner 在导入 settings/database 前检查当前目录、runner 自身及 `settings`、`database`、`app` 的 `find_spec` 必须来自同一隔离源码副本，失败即停。v2 runner 启动 Alembic 和清理子进程时显式设置该副本的 `PYTHONPATH`。下方替换先前 B 计划中的启动方式；这不启动或批准 B。
- **QA2-B2：** 负载测试开始前以独占创建打开本轮 `evidence/load-summary.json`；正常完成和异常退出均在 `finally` 写入有限脱敏摘要，包括成功/失败/尝试数、每 PLC 的样本计数与点数分布、正文大小总量及最小/最大值、成功请求 P95、耗时及累计清理结果。并发任务使用 TaskGroup，异常时等待其余任务取消并计数；原有逐分钟 `cleanup-ticks.jsonl` 保留。离线替身覆盖错误路径拒绝、成功摘要、HTTP 失败摘要，以及原 30 个清理心跳；真实 30 分钟容量未运行。

本次只修改以下四个既获批准的源码文件：`backend/app/plc_facts/v2_domain.py`、`backend/tests/test_plc_facts_v2.py`、`backend/tests_mysql/test_plc_facts_v2.py`、`backend/tests_mysql/test_business_integration.py`；另追加本任务 `tasks.md` 和 [新的 37 路径摘要](evidence/development-r4-qa2-fix-hashes.txt)。清单 SHA-256 `cd77a9ee98b0a6b111ac2ae3132ccb01a7d9b84bad3b959408f17325a4fb23a2`；35 项 backend/contracts 与最终隔离副本逐文件一致。原始和 QA1 返工清单均未覆盖或重写。

本次公开副本 `/private/tmp/arch-be012-r4-devA3-096t2f79/backend` 不含真实 `.env`、数据、日志和 venv。以下实际命令在项目锁定环境运行，`PYTHONPATH` 明确指向副本；在导入项目模块前校验三处来源并封锁 socket、SQLite、DBAPI 和 SQLAlchemy Engine 连接。定向结果 **106 passed in 11.60s，exit 0；实际连接尝试 0**：

```bash
cd /private/tmp/arch-be012-r4-devA3-096t2f79/backend
env -i PATH="$PATH" PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-be012-r4-qa2-uv-cache uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python - <<'PY'
import os,socket,sqlite3,sys
from pathlib import Path
import importlib.util
for name,relative in (('settings','settings.py'),('database','database/__init__.py'),('app','app/__init__.py')):
    spec=importlib.util.find_spec(name)
    assert Path(spec.origin).resolve()==(Path.cwd()/relative).resolve(),(name,spec.origin)
from tests.module_admission_fixtures import public_environment
os.environ.update(public_environment())
attempts=[]
def denied(*args,**kwargs):
    attempts.append('denied')
    raise AssertionError('ARCH-BE-012 QA2 no-DB guard')
socket.socket.connect=denied
socket.socket.connect_ex=denied
socket.create_connection=denied
sqlite3.connect=denied
sqlite3.dbapi2.connect=denied
import pymysql,aiomysql
pymysql.connect=denied
aiomysql.connect=denied
from sqlalchemy.engine import Engine
Engine.connect=denied
Engine.raw_connection=denied
sys.path.insert(0,str(Path.cwd()/'tests'))
import pytest
status=pytest.main(['-q','-p','no:cacheprovider','-m','no_db','--basetemp=/private/tmp/arch-be012-r4-qa2-pytest',
    'tests/test_plc_facts_v2.py','tests/test_plc_facts_migration.py','tests/test_plc_facts_maintenance.py',
    'tests/test_business_integration_storage.py','tests/test_business_integration_migration.py'])
assert not attempts, attempts
print('connection attempts:',len(attempts))
sys.exit(status)
PY
```

同一环境、防线与模块来源检查，`pytest.main` 参数改为依次执行 `tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes`、`tests/test_plc_facts_v2.py::test_normal_app_registers_routes_and_permission`，且 `--basetemp=/private/tmp/arch-be012-r4-qa2-order`，结果 **2 passed in 15.26s，exit 0；实际连接尝试 0**。对同一副本编译 20 个相关 Python 文件、核对唯一 Alembic head/前驱及解析 3 个 JSON 工件，exit 0；`git diff --check` exit 0。旧静态零权限/单路由断言仍按前文的已批准合同变化记录，未修改也未计为通过。

针对 QA2-B1，在同一副本和锁定环境，仅调用 `find_spec` 的临时探针证实：不设置 `PYTHONPATH` 的 Python 文件入口与 pytest console 入口均解析到正式树的 `settings.py`，按预期 exit 1；设置 `PYTHONPATH="$PWD"` 的文件入口及 `python -m pytest` 均解析副本的 settings/database/app，分别 exit 0。对真实 BE010 runner，未设置 `PYTHONPATH` 的文件入口在读取 profile、导入 settings 或连接之前因新 guard exit 1；设置副本 `PYTHONPATH` 的 `python -m tests_mysql.test_business_integration` 通过来源 guard，随后因本次故意没有创建 B profile 而 `FileNotFoundError` exit 1。另用仅含合成 `APP_NAME` 的私有临时 shell 文件验证下述清洁环境启动模式及三处来源检查，exit 0。以上只做来源发现/离线测试，没有读取正式 `.env` 或连接数据库。

### B 启动方式修订：替换前文所有 B 直接启动命令

本段继续沿用之前列出的轮次、资源、schema、UUID、凭据、权限、执行顺序与独立授权门禁；此处不是操作批准。每轮先在 `/private/tmp/arch-be012-r4-<round>-<run>/source/backend` 放入同一候选公开副本，在同级 `private/` 创建仅含该轮合成环境变量的 `runtime.env.sh` 和 `migration.env.sh`（`0600`；后者使用本轮迁移账号），不放或读取任何真实 dotenv。它们包括前文明确的全部合成 app/DB/JWT、v1/v2、权限、目标确认、BE010 phase 和 B runner 变量；切换 schema/阶段时先更新其对应合成值，保持非 root 及 precise UUID/端口/确认。尤其设置：

- `ARCH_BE012_B_TICK_EVIDENCE=<本轮目录>/evidence/cleanup-ticks.jsonl`。
- `ARCH_BE012_B_LOAD_EVIDENCE=<本轮目录>/evidence/load-summary.json`。
- 单独随机生成的机器/用户令牌、合成测试库及项目设置均只在本轮私有文件；证据和终端不输出其值。

以下函数针对所有 B 进程先清除继承环境、显式装入当前轮次的合成变量，固定副本 `PYTHONPATH` 和工作目录，再通过项目锁定 venv 进行三处 `find_spec` 预检；仅在预检通过后执行参数所选入口。实际运行时用本轮任务目录替换 `<本轮目录>`；该函数未在 B 或数据库上执行。

```bash
be012_run() {
  local be012_round_dir="$1"
  local be012_env_file="$2"
  shift 2
  env -i PATH="$PATH" /bin/bash --noprofile --norc -c '
    set -eu
    [ "$2" = "$1/private/runtime.env.sh" ] || [ "$2" = "$1/private/migration.env.sh" ] || exit 2
    set -a
    . "$2"
    set +a
    export PYTHONPATH="$1/source/backend"
    export UV_CACHE_DIR="$1/uv-cache"
    export PYTHONDONTWRITEBYTECODE=1
    cd "$1/source/backend"
    uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python -c "
from importlib.util import find_spec
from pathlib import Path
base = Path.cwd().resolve()
assert not (base / \".env\").exists()
for name, relative in ((\"settings\", \"settings.py\"), (\"database\", \"database/__init__.py\"), (\"app\", \"app/__init__.py\")):
    assert Path(find_spec(name).origin).resolve() == (base / relative).resolve()
"
    shift 2
    exec uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend "$@"
  ' _ "$be012_round_dir" "$be012_env_file" "$@"
}

be012_round_dir="<本轮目录>"
be012_http_port="<本轮 HTTP 端口：18392 或 18393>"
be012_run "$be012_round_dir" "$be012_round_dir/private/runtime.env.sh" \
  python -m pytest -q --confcutdir=tests_mysql tests_mysql/test_plc_facts_v2.py -k 'not v1_previous_revision_only'
be012_run "$be012_round_dir" "$be012_round_dir/private/runtime.env.sh" \
  python -m tests_mysql.test_business_integration --suite business
be012_run "$be012_round_dir" "$be012_round_dir/private/migration.env.sh" \
  python -m alembic upgrade 2c4e6a8b0d12
be012_run "$be012_round_dir" "$be012_round_dir/private/runtime.env.sh" \
  python -m uvicorn main:app --host 127.0.0.1 --port "$be012_http_port"
```

示例展示入口，不改变前文阶段次序：75 表前测使用 `-k v1_previous_revision_only`，fresh 冒烟排除 `v1_revalidated` 和 `steady_load`；upgrade 运行一次完整负载并设置 `ARCH_BE012_B_RUN_LOAD=True`。BE010 保留 previous business、successor retained/business 的 phase/ID 及确认；迁移使用对应阶段 revision。手工 v1 再核验、token fixture、FastAPI、Alembic、pytest、BE010 与维护 CLI 均经同一 clean environment、副本 `PYTHONPATH`、source-origin 预检和批准目标运行；v2 runner 创建的子进程继承这一清洁环境并再次固定 `PYTHONPATH`。将 `load-summary.json` 与 `cleanup-ticks.jsonl` 同轮留存并验证完整 30 tick、P95、成功/失败数、每 PLC 分布和清理对账。失败摘要也须保留；不把已产生摘要或未执行测试当成 B 通过。

本轮没有连接数据库或 SQLite、运行 Docker/迁移/DDL/DML、执行 B、访问 DAA 或现场。临时公开副本、无敏感值的来源探针、`0600` 合成占位环境、`/private/tmp/arch-be012-r4-qa2-pytest`、`/private/tmp/arch-be012-r4-qa2-order` 和 `/private/tmp/arch-be012-r4-qa2-uv-cache` 为本任务资源，保留到 fresh QA 完成候选对照后由协调者按生命周期规则清理；关键结果和 SHA 已持久化。

**Developer handoff：**请 fresh-context Verification 消费同一 r4 spec、完整 tasks、QA1/QA2 checklist、三份 SHA 清单、受限 diff 与上述 A 结果，独立复核本次三项返工。真实隔离 B、独立 QA verdict、Human Owner 最终验收、实际 dev 库升级和 DAA 均未在本轮发生。

## 实际 dev 库 Alembic 迁移记录

Human Owner 在本轮明确批准：“批准你直接用 alembic即可，后续任务直接用dev的库。”以下为协调者提供的实际执行和核验证据，由 Development 记入本任务；本记录者未重新连接数据库或容器。2026-11-10（Asia/Shanghai），专用开发容器 `aiis-ics-arch-database-only` 健康，MySQL 8.4.6，已核对 Docker hostname 与 server UUID，数据库会话 UTC offset 为 +28800 秒；正式后端非 TESTING 配置连接 `127.0.0.1:3307` 的 `industrial_level_2_system`，v1/v2 和三个 BE010 接入均关闭，预检未见同库其他会话。迁移前实际 revision 为 `e4f6a8b0c2d4`、应用表 60 张，精确匹配；前置迁移涉及的 7 张旧业务表均为空，其结构变更包含增加列和索引、放宽列及提高精度，未改写历史值。已完成单事务 mysqldump，备份保存在私有权限路径 `/private/tmp/arch-be012-r4-dev-backup-tyfvtmkq/before-e4f6a8b0c2d4.sql`，大小 86254 字节，SHA-256 `55c374ebc0f100a6d21ac3ccc0e1c45819ed4d76a5138ef026506dc4e898e879`；已核对 60 张应用表、`alembic_version` 和完成标记，临时凭据文件已删除，未做恢复验证。随后在正式 `backend` 目录执行 `uv run --offline --frozen --no-sync alembic upgrade 1b3d5f7a9c20`，实际 21:33:58–21:34:01、exit 0，依次经过 `e4f6a8b0c2d4 → f6a8c0e2b4d6 → 0a2c4e6f8b10 → 1b3d5f7a9c20`；两阶段之间读核为 75 张应用表。再执行 `uv run --offline --frozen --no-sync alembic upgrade 2c4e6a8b0d12`，实际 21:35:20–21:35:22、exit 0；每步前后均执行 `alembic current`。最终为 `2c4e6a8b0d12 (head)`、77 张应用表，原 60 张表行数在两次对照中一致，v1 七表 F7 保持 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`；新表 `plc_facts_samples_v2` 和 `plc_facts_latest_points_v2` 均为 0 行，主键、历史/过期索引、样本唯一约束、JSON 与 `DATETIME(6)` 检查通过。此次仅由 Alembic 写入该 dev schema，没有清空数据或进行采用/配置、B 验证、负载或故障演练、DAA 工作、部署及验收判定。后续常规开发按 Human Owner 指定继续使用此 dev 库；独立 B 门禁和 Human Owner 最终验收状态保持原记录。

## 本机 dev 采集 v2 启用记录

2026-11-10（Asia/Shanghai），按 Human Owner 对本机 dev 模拟样本验证的授权，协调者仅更新 gitignored `backend/.env` 中 `PLC_FACTS_V2_ENABLED=True` 和 `PLC_FACTS_V2_PROFILE_FILE`，其余配置保持；仓外本机用户私有 profile 和机器测试材料权限均为 `0600`。写入范围仅 `PLC-BE012-DEV-441247C3`/DB21、实例 `be012-dev-smoke-441247c3` 及指定代次，读取范围仅已登录 admin 的同一 PLC/DB，其他角色默认授权保持；已有 8000 后端未重启，正常加载并连接同一 3307 dev schema，复用现有账号，admin 登录和 options 返回 200。新 fresh Verification 的上报、去重、冲突、旧样本补传、最新值、历史和权限及两表对账证据见 [checklist.md](checklist.md#独立-verification现有-dev-功能验收)，其 SHA-256 为 `155f47d796d81711e4b96dda1746d2e187a5346bfb7d6740f5c470cb5d4ba882`；配置及两份合成样本保留供 Human Owner 查看。独立 B 原矩阵和最终验收状态按既有记录，DAA 未改动。
