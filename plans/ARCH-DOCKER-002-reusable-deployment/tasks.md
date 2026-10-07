Task ID: ARCH-DOCKER-002
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: fresh-context Verification of r2

# r1 Development 历史记录

依据已批准的 spec r1，新增入口并局部追加双语操作说明。既有 dev/root Compose、Dockerfile、Nginx 和前端模块工作保持不变；不执行 Docker 生命周期或数据库写入。

## 实施顺序

- DEV1 / AC1-AC3：新增隔离 database-only 与 prod 配置。
- DEV2 / AC4：补齐环境模板注释、双语准备/初始化/恢复/排障说明。
- DEV3 / AC1-AC5：临时占位目录解析四份 Compose，检查挂载、名称、数据卷、默认开关、保护文件及文档链接，记录结果后交接。

## 环境与证据

- 变更前保护文件 SHA256 和前端 README 内容保存在 /private/tmp/arch-docker-002-r1。
- 工作区已有 ARCH-FE-001 未提交修改；本任务仅追加 frontend README Docker 段落。
- Docker Compose v5.4.0；所有解析使用 /private/tmp/arch-docker-002-r1/fixture 下的模板副本和 --env-file /dev/null，没有读取真实 env。

## 文件交付

- 新增 docker-compose.database-only.yml：mysql:8.4.6、独立 Compose 默认命名卷、显式启动策略。
- 新增 docker-compose.prod.yml：复用 backend Dockerfile，固定 digest Nginx，env/logs/dist/nginx.conf 挂载及缺少 index.html 的失败检查。
- 根 README / INITIALIZATION 双语：四入口用途、Bash/PowerShell 准备、数据库/应用账号区分、显式 Alembic 和 bootstrap、重启更新语义、路径/403/502 排障及持久卷保护。
- backend README 双语与两个 env example：运行入口和配置位置注释，未更改默认配置值。
- frontend README 双语：仅追加预构建 dist 部署段落；完整保留实施开始时既有内容。
- 根 PLAN 与 plans catalog 双语：更新本任务状态。spec 仅记录 Human Owner 批准；没有改动范围。
- .gitignore 已覆盖 /runtime/、真实 env、logs 和 dist，因此未修改。未新增关键业务源码或变更源码结构，不调整 CODE_INDEX。

## Development 自检

1. `python3 /private/tmp/arch-docker-002-r1/check.py`：exit 0。
   - 对四份 Compose 分别执行 `docker compose --project-directory /private/tmp/arch-docker-002-r1/fixture --env-file /dev/null -f <fixture/compose> config --quiet`，全部 exit 0。
   - 同位置 `config --format json` 解析后检查：prod 服务集、名称/卷隔离、固定 MySQL/Nginx 镜像、健康依赖、重启策略、只读挂载及 create_host_path=false，全部通过。
   - 变更前 SHA256 核对五个受保护文件（dev/root Compose、backend/frontend Dockerfile、nginx.conf）无变化；前端 README 原内容前缀保留。
   - 三类 bootstrap ENABLED/RESET_PASSWORD=False、密码为空；真实 env/runtime/dist 的 git check-ignore 检查通过。
   - 本任务 10 个初始相关 Markdown 链接及锚点通过；新增 Compose 未包含来源项目号/名称/迁移标识。
2. `git diff --check`：exit 0。
3. 不执行 Docker build/up/down、在线迁移、bootstrap、登录或 PLC；不生成实际 dist，不安装项目依赖，不暂存/提交/push。临时配置解析不是实际运行验证。

## 交接

DEV1、DEV2、DEV3 已完成，AC1-AC4 及 AC5 的 Development 自检部分通过。当前仅为 developer_handoff；独立 Verification 尚未创建 checklist.md，未声称 qa_passed 或 Human Owner final acceptance。

下一步由 fresh-context Verification 按已批准 r1 独立核对配置/文档和上述自检证据。实际镜像构建及数据库运行链路仍需单独批准，不属于本次交接。

## r2 Development 与当前交接

2026-09-08 按 Human Owner 明确批准的三入口收敛执行：

- 删除根 docker-compose.yml；dev、database-only、prod 三份配置未修改。
- 清理根 README/INITIALIZATION、frontend README、prod env 模板注释、CODE_INDEX 与 docs/multi-project-pm.md 的旧入口引用；不改历史任务验收。
- 双语指南增加手动测试顺序；dev 示例停止操作改为保留卷和 env，避免手动测试误删数据。
- 保留现有 Dockerfile/nginx.conf；旧容器/镜像/卷未操作。
- `python3 /private/tmp/arch_docker_r2_check.py`：exit 0。三份 Compose 在模板副本及 --env-file /dev/null 下 config --quiet 全部通过；三入口文件清单、当前文档无旧引用、dev/Dockerfile/nginx.conf 保护哈希核对通过。
- `git diff --check`：exit 0。前述 r1 四入口验证仅为历史，不是当前文件清单。
- 本轮没有运行 build/up/down、迁移或登录测试；用户手动验证结果尚待提供。

当前 r2 状态为 developer_handoff，等待独立 Verification；未创建 checklist.md，未声称 QA 或最终验收通过。
