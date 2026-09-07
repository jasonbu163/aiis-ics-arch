Task ID: ARCH-DOCKER-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending Human Owner r1 approval
Task Namespace: aiis-ics-arch
Classification: root
Capability: 可复用的 database-only 与单机 prod Docker 部署入口
Owner: AIIS ICS Architecture Human Owner
Acceptance Chain Reference: ARCH-DOCKER-002 r1 scope approval -> Development handoff -> fresh-context Verification -> Human Owner final acceptance
Related Task: aiis-ics-l2-1260327::D-001

# 目标与依据

将 1260327 已实践的 Docker 部署方式适配到公开架构仓，使用 aiis-ics-arch 前缀，只回收通用编排、静态文件交付和初始化说明。来源任务与当前源码已只读核对；其运行证据不作为 arch 的运行成功证据。

用户已确认调整 arch Docker 部署的方向；本 r1 是首次形成的精确范围，尚待 Revision 批准。

## 需求与设计决定

1. 保留 docker-compose.dev.yml 与根 docker-compose.yml 的现有行为、固定名称和数据卷；根入口继续是 release-check。不替换既有 frontend Dockerfile、Nginx 配置和镜像内构建能力。
2. 新增 docker-compose.database-only.yml，project name 为 aiis-ics-arch-database-only，仅运行 mysql:8.4.6，使用 backend/.env 和独立 named volume。默认发布 3307:3306，与 dev 互斥；不共享或复制 dev 数据卷。保持来源方案的显式启动方式，不配置自动重启。
3. 新增 docker-compose.prod.yml，project name 为 aiis-ics-arch-prod；服务名采用 arch 现有 backend、frontend。backend 使用现有 Dockerfile，从镜像运行源码，连接外部数据库；以只读文件 bind 挂载 backend/.env.docker.prod 到 /app/.env，并将 runtime/backend/logs 挂载到 /app/logs。不得带入客户 PLC 配置、项目迁移或不必要的 snapshot policy 挂载。
4. prod frontend 使用与 arch 现有 Nginx runtime 相同的固定版本及 digest，直接使用官方镜像并只读挂载现有 nginx.conf；frontend-js/dist 挂载到 /usr/share/nginx/html/current。启动前验证 index.html 存在，缺失时明确失败；bind 设置 create_host_path: false，健康检查使用 127.0.0.1。frontend 依赖 backend healthy，两者均使用 restart: unless-stopped。
5. backend 默认发布 8000，frontend 默认发布 80，沿用 BACKEND_HOST_PORT、FRONTEND_HOST_PORT；可按运行主机覆盖。名称隔离不解决端口冲突，dev/prod 同机切换须说明。Compose 默认生成隔离容器、网络、卷名称，不引入来源项目的固定名称。
6. 复用现有 backend/.env.example、backend/.env.docker.prod.example，必要时只补充运行位置注释。宿主机访问 database-only 使用 127.0.0.1:3307；Docker Desktop prod 访问它使用 host.docker.internal:3307；外部数据库使用部署方地址。实际 env、密码、数据库数据、dist、runtime 产物均不进入提交候选。
7. 初始化说明提供 macOS/Linux 与 Windows PowerShell 的准备命令：复制模板、设置部署值、创建日志目录、用 pnpm 和锁文件构建 dist、核对 index.html、显式 Alembic 迁移与 bootstrap-users、启动及检查。沿用 arch Core migration，不复制来源项目 70 表或 c17d9e8f4a21 历史。bootstrap 默认关闭、密码留空，不自动重置已有账号。
8. 文档区分文件 bind 与 env_file 的更新语义；说明 Docker Desktop 自身启动、已有容器重启策略、MySQL 显式恢复步骤，以及 missing dist / bind path / 数据库地址问题。持久数据库操作示例不使用 down --volumes；既有一次性 dev 证明清理步骤明确标记为仅可丢弃验证环境。

## 精确写入 allowlist

- 新增 docker-compose.prod.yml、docker-compose.database-only.yml。
- README.md、README.zh-CN.md、INITIALIZATION.md、INITIALIZATION.zh-CN.md：通用运行说明。
- backend/README.md、backend/README.zh-CN.md、backend/.env.example、backend/.env.docker.prod.example：部署入口及配置说明。
- frontend-js/README.md、frontend-js/README.zh-CN.md：仅追加静态 dist 交付说明，保留 ARCH-FE-001 工作。
- .gitignore：仅在现有规则未覆盖时补足 runtime 产物忽略。
- PLAN.md、PLAN.zh-CN.md、plans/README.md、plans/README.zh-CN.md：仅维护本任务行。
- plans/ARCH-DOCKER-002-reusable-deployment/spec.md：PM；批准后 tasks.md 由 Development 创建，交接后 checklist.md 由独立 Verification 创建。

不修改业务源码、权限、依赖清单或锁文件、现有 Dockerfile/nginx.conf/dev/root Compose、Core migration、CA、项目工具与其他任务记录。工作区已有 ARCH-FE-001 改动，不能覆盖或回滚。

## 验收标准

- AC1：四个 Compose 入口用途清楚；既有 dev/release-check 配置无差异；新增资源前缀统一且与 dev 卷隔离。
- AC2：新增 Compose 在临时占位夹具下 config --quiet 成功；prod 服务、挂载、健康依赖、重启策略及端口符合上述要求；不读取真实 env、不连接数据库。
- AC3：Nginx root、dist 挂载、缺少 index.html 的失败检查一致；没有宿主机源码或 node_modules 生产挂载。
- AC4：双语说明覆盖准备、显式迁移/账号初始化、启动恢复和故障处理；模板保持公开安全值；没有项目号、真实地址、密钥或客户 migration 混入新增交付内容。
- AC5：文档链接及 git diff --check 通过；记录真实验证命令、结果和未执行的运行检查。fresh-context Verification 独立核对 r1 实施差异。

## 验证与运行边界

本 Revision 授权范围为配置与文档实施、临时占位文件下的 Compose 静态解析及定向检查。验证夹具与输出写入 /private/tmp，不覆盖现有真实 env 或 dist。实施时可使用临时镜像目录复制配置及占位 env 完成解析，不使用 Docker up/down/build，不连接真实数据库，不执行在线迁移、bootstrap、PLC、发布、commit 或 push。

实际 Docker 镜像构建、首次空卷运行、数据库写入和登录链路需要后续单独批准运行验证范围；本次完成只能称配置/文档已验证，不能称 arch 部署成功。

## 风险与回退

- prod 依赖现场 dist 和日志目录，这是为复用已确认的单机交付方式而采用的宿主机挂载；文档明确准备步骤。回退可停用新增入口，继续使用原有入口；不删除任何数据卷。
- dev/database-only 默认同占 3307，dev/prod 默认同占 8000；必须切换或覆盖端口，不能通过改名前缀解决。
- frontend README 已有并行工作，只做局部追加；如并行修改影响本范围，重新核对差异。

## 批准与修订记录

- 2026-09-07：用户要求“好的，调整arch的docker部署。”；据此完成 r1 具体方案，状态 draft。未创建 Development/Verification 证据，未修改部署配置。
- Human Owner r1 approval：待确认。
