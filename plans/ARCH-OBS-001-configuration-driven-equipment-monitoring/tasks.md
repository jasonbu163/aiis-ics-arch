Task ID: ARCH-OBS-001
Revision: r11
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r11 R11-QA-001 授权返工开发自检完成；交新的 fresh-context Verification 独立复验
Workflow Mode: STD
Execution Mode: agent_team_same_session

# r11 QA1 返工

2026-11-17：接收独立 Verification 的 R11-QA-001 与 `qa_failed`，checklist SHA-256 `0b45a548c236245b20816d061827465186d49113077821a2be0d7a45d167c959`；原 65 项正式源码及 27 项临时材料逐项匹配。只在指定隔离容器修正本任务账号授权及临时材料，保留原 QA 和开发记录。

### r11 QA1 返工 developer_handoff

**精确对象。** 本轮只修复获批 r11 的 R11-QA-001 隔离测试账号授权和任务临时材料，保留 Verification 的 `qa_failed` 和 r10 QA4 `qa_blocked` 原记录；不修改 spec、checklist、正式业务实现或真实配置。spec SHA-256 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`；返工依据的 checklist SHA-256 `0b45a548c236245b20816d061827465186d49113077821a2be0d7a45d167c959`。正式工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，前次 65 文件逐项复核均未变化，清单整体 SHA-256 `b3d52719cb1c99c329ac015e1bb5886efb3b86837481989b4d886b80d9dd194f`，完整 65 项仍见下方先前 r11 handoff。前次 27 项临时材料写入前也全部匹配。

**授权修正。** 仅对指定容器 `58c935ee29f4e782204fb20a1866a4f0733a882cb68da4df84b0a26ef9f01c40` 中本任务的 `obs_r11@%` 操作，先审计 UUID、镜像、绑定、账号、无活动测试客户端/事务、原授权和 main 全部 11 表行/DDL，再逐 schema 撤销旧的未转义通配授权并授予下划线按字面转义的授权。三个授权对象分别为 `` `obs\_r11\_main`.* ``、`` `obs\_r11\_guard`.* ``、`` `obs\_r11\_recovery`.* ``，每个仅含 `SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, LOCK TABLES`，全局只有 `USAGE`，账号无活动角色；未改变全局 `partial_revokes=0`、其他账号或任何 schema 数据。该 10 项列表是依据现有迁移/测试静态审计收窄的候选，**完整迁移链尚未用该授权执行**，由 fresh Verification 独立确认其是否足够；不得因权限不足自动扩大范围。

MySQL DCL 非事务：第一条 main 撤销和新授权实际已提交，但初次逐步核对脚本因 `mysql --batch` 把输出中的反斜杠再次转义而误判并立即停止；当时 guard/recovery 尚未处理。经独立只读比较，驱动与 `mysql --raw` 的实际 SHOW GRANTS 一致，确认 main 新授权正确且 baseline 不变；未重复其 DCL。随后以精确预期的部分状态和原 journal 为前置条件，只对 guard/recovery 逐条完成撤销与精确授权，每步读取实际 SHOW GRANTS；没有自动重试失败 DCL。非秘密步骤日志 SHA-256 `0c080d3342c78ea453ce0e4394ab6b5d60e4a2fc764a749ece554ec569a20e0e`。初次误判和中间部分提交事实不以最终成功覆盖。

**DEV self-check 与边界。** 最终以该账号实际连接三个精确 schema，检查 `SHOW GRANTS FOR CURRENT_USER()`、`CURRENT_ROLE()` 和 `@@partial_revokes`：恰好 3 个字面授权、每个 10 项、无旧通配授权，三个库均可连接。main 保持 r8 `8c0e2a4d6f18`，11/11 旧基线表的全部行与 `SHOW CREATE TABLE` 逐项不变；guard/recovery 仍为空。对三个合法名称及其人为构造的相似**字符串**执行 MySQL LIKE 正/反例，均符合转义规则；没有创建、连接或测试实际其他 schema 的拒绝，不能把字符串结果冒充该证据。实际授权/基线只读报告 SHA-256 `71f2eca70362a582c83c00890d549e376af06bd730425307e2363a1cf56a3e29`。

临时 `create_target.py` 和 `initialize_target.py` 已改用同一严格 allowlist/转义/10 权限策略，并在创建授权后检查实际 SHOW GRANTS；`safe_target.connect` 每次连接均对身份、无活动角色、`partial_revokes=0` 和精确权限 fail closed。新增 `grant_policy.py`、实际只读 `audit_grants.py` 和纯策略测试；测试覆盖合法授权、未转义授权、权限增删、额外范围/角色/语义及 CLI 双转义输出，**5 passed**；25 个临时 Python 文件语法检查通过，`git diff --check` 退出 0。修订后的 bootstrap 脚本未重新创建容器实跑。65 项正式源码逐项不变；原 27 项临时材料中仅 `RUNBOOK.md`、`safe_target.py`、`create_target.py`、`initialize_target.py` 按本缺陷更新，另加 7 项策略/检查/一次性修复证据，当前 **34 项**清单整体 SHA-256 `b05b4590ef9e70cbda98e7c7f3029933fa9dfd433c69d5983174b5cfed7fef03`，逐项见下。

**独立复验与资源。** 当前 [RUNBOOK](/private/tmp/arch-obs-r11-8O97SDOg/RUNBOOK.md) SHA-256 `51019ccf41cf54cfbdc6706abd906067740b801e6cba49622dc09d7c04f59241`；Verification 可先独立运行 `test_grant_policy.py` 和 `audit_grants.py`，重新核对容器 ID、镜像、UUID、角色、三条实际授权及数据，随后按已批准顺序自行执行 r8→r10、真实 MySQL 原请求回放、ID 重叠、受控恢复、guard 和中断。上述迁移/回放/恢复仍**未由本轮 Development 执行**，既有 R11-AC02–04 和 R10-AC03/09 不因此通过。容器及 0700 专属目录继续保留供 QA；三份 0600 临时凭据仅供该实例/QA 使用，不输出或提交。QA 结束并持久化证据后，由协调者核验完整 ID、镜像、标签、挂载、UUID、端口和无后续依赖再按授权回收。未访问 3307/dev、其他容器或 SMA/DAA/PLC，未改其他账号或用户服务。

**返工后临时验证材料 34 项摘要**（SHA-256 和相对 `/private/tmp/arch-obs-r11-8O97SDOg` 的路径，不含凭据文件）：

```text
51019ccf41cf54cfbdc6706abd906067740b801e6cba49622dc09d7c04f59241  RUNBOOK.md
34832b746aa711948038eaa46436d4dabae89f03e14c405e2dfc77915b67850c  audit_facts_predecessor.py
adfbc96103b7b8165eb654210e5781da11afe531e8d3cf125292e70f54541106  audit_final.py
5d0d798de574e3adff33f160d62af99b5f7cad231d940da190ce5e352d284ce6  audit_grants.py
0cbf731aeeeffa5aba8fda9385e5f61951a686541546857b0e68f2dc4cf4e5ca  audit_predecessor.py
2d50c0fa23f98c40ca4b6115ad057bbd35138b93bf841458d792bb8e92f6bfb5  control.py
dc892ffa91cdd3d9c3717b78b7406411fb4741e55ab85e9e4969ba5f7c6126e0  copy_source.py
da4fa57002591dc343634d060216a15056fda7e0fd86161b8214ec9d8f26148c  create_target.py
71f2eca70362a582c83c00890d549e376af06bd730425307e2363a1cf56a3e29  grant-final-audit.json
0c080d3342c78ea453ce0e4394ab6b5d60e4a2fc764a749ece554ec569a20e0e  grant-repair-steps.jsonl
d524237d9e3ed0995b18fad1777cc2ac707a9aa3f9cc9a9754de3d4fe366657e  grant_policy.py
fe147b784732585d6e1334755a124cec043acdc92d4ca3b3c5bba9a3f1476ee7  init-r8-obs_r11_main.log
9b4cc9f7637984f3170df791eab45203ae15cccdae97257629eaa19dd6973309  initialize_target.py
0cfb4549525f745d4c4bca532cc922f19cd4c5fbf8d99dec52a6926c34c4e619  ownership.json
fe1405a3d61bbeb4ab3a21a0e12f11af4e19999d5c24af0df003ee42e2302109  qa_guards.py
8ea68b115b90fc1775da4f200157bb2ea062810a30b6cc046971fabfd0350d96  qa_interrupt.py
8ac61b38971841819ac748d427d02d8486ac3e2acd3350f70b191fa2f9131e0c  qa_interrupt_child.py
a6c4226fc67898adb608c6088470675ccec6020334bc7472bf82f1916787a24b  qa_interrupt_refusal.py
d1f9ca554b786987955eea5fcd626080064ee2447306e874237a4551fdb68a30  qa_recover.py
7563b35c084b5401261b9ae88a3948a076a2251233c43c081b357a1906cc01c6  qa_recovery_collision.py
a56780c5930b8925da9cab3dacfde85c76202cf5a9ab36430e5ec8004df9aa4d  qa_replay.py
630dd116bc3ada541452d0b11fa08ca0c4a350e508789e045fdec438614a4272  qa_replay_http.py
62e93d2895089c650511b3e3937245cab2b5769bd4dafddd54d576b4172b73c7  qa_upgrade.py
1cfdaad0f872e8d26a16b645fdc50cfaec13029684797cee3b2b7adde07bfa22  r8-baseline-obs_r11_main.json
2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34  r8_ingest_reference.py
4d6807f0eac80b8bc62189ce10dd8e772b33189cc254d998f915c5b1c2bb5cef  repair_grants.py
c5c9359fb2e5186409b33e01e5feed97dc23f03f9473c2f768c0abbf284e5e09  resume-r8-facts-obs_r11_main.log
e5d6f6c2a4f2ecda1a939d9814773c78a45f65c7c420366cd04b9360d27c882b  resume-r8-obs_r11_main.log
7528c17846442145139be07900d742a8050c39c92376644e32215f78ef016d76  resume_grants.py
30af3b9ccfd75d75e8204989f37842d0ac410ee245500bb31a577f55c0a7769f  safe_target.py
1fb4054b563379cd9d6f77638a38d25f8ce6a69cec0fa94026bd80ed94dc2662  seed-r8-obs_r11_main.log
9436125d5ea2e92add134cc3a9546c47d3a4e2b56bc86f2e35e3813baedb75e8  seed_r8.py
4cb75f820fa09beaec2a65a984182d00478a3783ca08917d17b9480491ee3662  source-manifest.json
a78aca73c4f201425edd35aa99df3d1d113c22772b6f0f3925da7cbb9a0e6543  test_grant_policy.py
```

# r11 隔离迁移复验准备

2026-11-17：Human Owner 批准 r11 §13，批准后 spec SHA-256 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`；QA4 `qa_blocked` checklist SHA-256 `7599d30b39d3b1b98e915bc06348b0e83e23f17b4bad8ee16fbb5e4e1e704830`。原 63 项候选逐项核对一致；此前 r10 事实及 QA 记录完整保留。此阶段仅更新两份前端 README、本文件和专属临时测试材料。

### r11 developer_handoff

**批准与精确交付。** Human Owner 已批准 `ARCH-OBS-001 r11 §13`（[§13.6](spec.md#r11-approval)）；spec SHA-256 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`，本轮依赖的 QA4 checklist SHA-256 `7599d30b39d3b1b98e915bc06348b0e83e23f17b4bad8ee16fbb5e4e1e704830`，其 `qa_blocked` 事实不变。交付为正式 `main` 工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 上未提交候选；写入前原 63 项全部匹配，此轮只改 [英文前端 README](../../frontend-js/README.md#business-observation-source-selection)、[中文前端 README](../../frontend-js/README.zh-CN.md#业务观测来源选择) 的指定段落及本 `tasks.md`，未修改实现、其他源码、spec 或 checklist。原 63 项加两份 README 共 65 项，逐项清单见下，整体 SHA-256 `b3d52719cb1c99c329ac015e1bb5886efb3b86837481989b4d886b80d9dd194f`；tasks/spec/checklist 单独定身，不计入该清单。

**说明与静态检查。** 两份说明对应当前四设备页的配置化卡片、温度/传动/清洗过程曲线、独立能耗及来源无关的 v2 机器上报，明确现行页面没有 URL legacy/HTTP 选择，旧历史合同和原能耗统计边界仍保留，并分别链接同语种 r10 使用说明及 v2 合同；与之无关的计划/实绩、部署、权限与历史段落原样保留。仅有两个指定段落产生 diff；4 个新增本地链接及显式片段锚点均存在，`git diff --check` 退出 0。按 §13.3 本轮没有因文档改动修改或构建页面、接口和迁移。

**合成目标及 DEV 准备。** 仅在指定 `127.0.0.1:13316` 创建本任务 MySQL 8.4.6：完整容器 ID `58c935ee29f4e782204fb20a1866a4f0733a882cb68da4df84b0a26ef9f01c40`，容器名 `arch-obs-r10-qa-20261117-a1`，精确镜像 ID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9` / arm64，目标 UUID SHA-256 前缀 `c6c91aa0c925`，时差 +08:00；经核对不同于现有 dev UUID。数据库 datadir 为容器独占 tmpfs，无已有卷；仅两个本任务凭据文件只读 bind mount，桥接网络并非完全隔离。专用 schema `obs_r11_main` 已用正式 Alembic 链到 `8c0e2a4d6f18`，`obs_r11_guard`、`obs_r11_recovery` 最后核查均为空。专用测试账号仅对三个 schema 授权；容器 ID/镜像/随机归属标签/端口/挂载与 UUID 记录在 0600 的临时所有权文件中。既有 3307 dev 未连接、复制或修改；未操作其他容器、SMA、DAA、PLC 或正式前后端进程。

`obs_r11_main` 最后一次只读对账：旧实时 2、过程 3、旧回执 5、指标 2、槽位 4、卡片 1、曲线 1；旧能耗量、旧曲线、价格和小时价格各 1。两组实时具有不同原采集时间；两条同区域历史有相同原时刻、不同合成来源键及独立行；备注、异常/复核、ID、配置和原上海采样时间保留。5 个旧原请求及其实际数据库回执指纹逐条对账：使用与 r8 交接一致的旧 `ingest.py` SHA-256 `2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34` 提取 `_fields`/`normalize`/`fingerprint`，与当前回放函数及 `permitted` AST 相同，domain 源字节一致；旧 task evidence 是明确标注的合成元数据，不能证明真实来源。包括请求、结果 ID、逐行数据和旧表 DDL 的基线文件 SHA-256 `1cfdaad0f872e8d26a16b645fdc50cfaec13029684797cee3b2b7adde07bfa22`。

**环境隔离与已知启动过程。** 临时源码副本从正式树只复制 507 个 Python 源码与 Alembic 配置，逐文件与正式源码比较 507/507 一致，清单 SHA-256 `4cb75f820fa09beaec2a65a984182d00478a3783ca08917d17b9480491ee3662`；不含真实 `.env`、私有运行 profile、Git 或符号链接。子进程以清空后的显式 env 覆盖数据库类型、host、port、用户名、schema、其他数据库禁用和测试目标；同环境核实 settings 解析的异步/同步 URL 均为获批 13316/对应 schema，root engine 配置为无效身份且未连接。数据库与 Alembic 每步前由脚本重验容器 ID、UUID、schema 与版本，不提供自动换目标。

创建时 `mysqladmin ping` 先于认证 SQL 就绪，首次身份查询非零、当时未保存错误文本，未创建 schema；只读复查同一容器运行且初始化完成、目标名为空后，才创建三个 schema。创建脚本随后改为等待认证 `SELECT 1`，**该改版尚未重新执行**。main 从空库执行 Alembic 时先在 `2c4e6a8b0d12` 因缺少旧 ACQ 目标变量停止；只读核查 77 张表集合、待退役 9 张均空且可见外键为 0 后，显式提供本容器 UUID/schema 继续。一次隔离审计子进程因精简 PATH 未包含 Docker 目录而停止、未写库；补正 PATH 后继续，正式迁移在空合成库删除这 9 张空旧表。接着在 `3d5f7a9c1e23` 因缺少 facts 迁移目标/操作号停止；只读核查两旧 facts 表为空且新名不存在后，配置本容器的 facts、task 和 registry 后续守卫，正式链完成至 r8。以上均有专属日志，未 stamp、降级、重置或自动忽略失败。

**供 fresh Verification 独立执行。** [本任务临时 RUNBOOK](/private/tmp/arch-obs-r11-8O97SDOg/RUNBOOK.md) SHA-256 `557cdf38d877cb0e0629fffebb598704e2e286db2212cecba069e6f580fd8545` 提供精确命令、目标检查和保全步骤：main 使用 `qa_upgrade.py` 在线升级并对照旧表/约束、`qa_replay.py` 以真实 r10 FastAPI ASGI 路由和真实隔离 MySQL 重放每个原请求并制造新旧 ID 1 重叠，随后明确测试恢复目标碰撞和 `qa_recover.py` 的受控恢复；guard 与 recovery 两个空 schema 分别从正式链建到 r8 并执行未静默、未确认旧时间、归档冲突及真实 RENAME 后注入异常的中断/监督拒绝测试。ASGI 不等于回环 HTTP；受控异常不等于断电或覆盖所有 DDL 故障。碰撞标记及中断现场默认保留，不自动 stamp、盲目重试或删除。

这些 QA 脚本已完成 **19 个临时 Python 文件的语法检查和安全边界静态审阅**；main 的 r10 升级、旧请求回放、新行/配置保全恢复、guard 拒绝及受控中断 **均尚未由 Development 执行**，不能把工具或 r8 准备当作 AC02–04 通过。若实际执行出现错误或缺陷，停止并保存现场，由独立 Verification 记录事实，不在 r11 内修改实现或更换目标。原 R10 其余未覆盖条件仍按 QA4 保留；Development 不作 QA verdict 或 Human Owner 最终验收。

**资源归属与结束条件。** 本轮容器仍运行，供下一名独立 Verification 使用；本任务私有目录 `/private/tmp/arch-obs-r11-8O97SDOg` 为 0700，临时 root/client/测试账号凭据文件为 0600，仅供该容器和 QA 使用，不输出、提交或记入日志。QA 完成、关键脱敏证据写入 checklist，协调者确认无后续依赖后，按完整 container ID、镜像、标签、挂载、UUID、端口及写入方重新核对，再仅停止/删除该容器并移除任务独有目录和凭据；不使用通配 Docker 删除或触及其他卷。意外中断先审计所有权、revision 和对象，不因名称相同就清理。留存的脚本、基线、DDL 日志、源码及敏感临时文件都有该 QA/回收依赖；容器删除前不得删其挂载。

**正式源码 65 项摘要**（SHA-256 和路径，按路径排序）：

```text
db53dca713fd3f1e2c6844284f6ef56fc93aa11f9ff2ad88e46d6feb4766f501  CODE_INDEX.md
8d0780c83d990c88ac6fa8ba7c40052740ea4dbe1f4fb4d67b4bdf7ee9d8dcb3  backend/alembic/versions/20261117_1200_9d1f3a5c7e20_observation_bundles.py
d12b94302436835dcd322646c788fd30755dcad48d2318405d22ec606bfc4847  backend/app/equipment_observation/README.md
93bc8166ad154d8a0039a0e7e9eff592cc67b530733fbb93b622fd6ea21b21c2  backend/app/equipment_observation/README.zh-CN.md
89d04f96973411baa31b2ec40c7e8335fab80c86dc5ff892b83c153e9d8f6af0  backend/app/equipment_observation/api/routes.py
39798a2a3119d40b1b846bf26d8fd3ab9a624bfb1cb9b8854f1c0b16dd1dffc2  backend/app/equipment_observation/error_codes.py
93cb6b4d5c6a464b06364441c8887aa466885bed75902fc97d1fe5fb77ca51ef  backend/app/equipment_observation/machine_openapi.py
35b037ee43126b2e6bf991c44f327f5b123a6446c4b239986ea62430258079d7  backend/app/equipment_observation/manifest.py
5a69c30586f65364fb57485dd3adabfd00fc178b2168228f8c08f09cc12f6a7d  backend/app/equipment_observation/models/__init__.py
8ae102b30edf13beb3387f779e35c4ed5119b97b9d55d6d5c07c48322b736914  backend/app/equipment_observation/models/records.py
80e5f3cffd54f67736da287e973110d1e3ce8c94cf20fbd8561921f5f8efc89e  backend/app/equipment_observation/profile.py
262612e3364e725a9f821cec719bc8048e987951a1a4c1bd37b7ce60b2e5956e  backend/app/equipment_observation/schemas.py
aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49  backend/app/equipment_observation/services/configuration.py
135dc8f46b5758cd9600ad5e93553c8993c3ab762c5a48a3422e8f8ab4c95ee8  backend/app/equipment_observation/services/energy_reads.py
af5601fdcc89298f71b8adfae07af0465786c7f746fd8ae905653011df09778c  backend/app/equipment_observation/services/energy_statistics.py
60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3  backend/app/equipment_observation/services/guard.py
0ee4c6c94420f29db504f384491b5e54f2d7d7aa6c72cac02e4c288cf411138e  backend/app/equipment_observation/services/ingest.py
cd94cc1ff19975054ed4903666bf2a794b137af312ca199685f1a1b14b773894  backend/app/equipment_observation/services/ingest_v2.py
f3e8ab8c2d5d711f301593cabb68a756d76699f5b22a6e97a65d479673daf6c2  backend/app/equipment_observation/services/reads.py
bd7f081c6791dbf2ee9969c3f0e77ce13aad686d4a4f20a9c71b4e437fbb4b89  backend/app/equipment_observation/services/v2_domain.py
6f92dfb56df56d3ca1d9866a609d0c4bf55cbc74380394a91ba48a89de5d2fe0  backend/app/plc_facts/v2_config.py
39e4cdd218d83475112cddc5780a1fd4a8eba24cfc3ce79b29d5ef3b8a6bce76  backend/common/integration/storage.py
582e34fc026e80291c44e90dae45f9814a5ceb4a9db76369f8a3b5f48af37748  backend/tests/test_energy_price_api.py
a6f24f3b01610bdd3736564148c179ae3a28fd95d165d16d82f5562222ef59e6  backend/tests/test_equipment_observation_domain.py
32ead808cdf317b9b38c32fa45eb35bef66074d0a8d87dbec06e384a2469d855  backend/tests/test_equipment_observation_r10.py
b19452c3fdae3722579cd17628de196732f2e6ed291032a6f99deb0a82751641  backend/tests/test_equipment_observation_r10_flow.py
71d91aa54ae883be9c2e3961fdb89fa5eb6ad4b52d57d7de808fc5422a609444  backend/tests/test_equipment_observation_r8.py
4fdc00cdf51d41f1b87badcf7b9c3af0d5c8e805fb5441022a57c08ed8905123  backend/tests/test_equipment_temperature_migration.py
0393e9346c4d04884d99d77c6c006754894864c7a3d57b2517a4feb5d3e208ae  backend/tests/test_legacy_acquisition_retirement.py
706acd4edfe88e09a0f38dcacda98f0792407e41fed2b7ee30083f225f98f6c2  backend/tests/test_mapping_migration.py
0532f522a69fe2db7e463536617cd0de3af08fc86bbb2775dabd4084b2d2e68f  contracts/README.md
980e5616459dcda55633fd289368e88829a176486e7c88504d481867766b3c23  contracts/README.zh-CN.md
b3379d7181b285680f739bd3b9ebc6ca8ea010a542b546993bd706244a4609bc  contracts/published/http-api/equipment-observation-v2/README.md
e84d4c2afe7e55bf3ddc7005244bfd755f715d7469072508d91da3b5222958d6  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
d11a7c030f7a4401219b2d5160f4d77345df28d42a39e364861144a019252989  contracts/published/http-api/equipment-observation-v2/example-profile.json
cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646  contracts/published/http-api/equipment-observation-v2/openapi.json
870378e53e1becd7c70a5d0b38f062b2e4bf809ff68a8269c34bd5441962d0a7  contracts/published/http-api/equipment-observation-v2/vectors.json
0b777e70584e0086b00616270716fe93df24419ed737c1df9720473e368b7528  docs/equipment-status-process-monitoring.md
7c7137720e399e7e60cf89614ad1f9b486c52928c1a9f23ca68b4fa44ff3d798  docs/equipment-status-process-monitoring.zh-CN.md
28b21dda4d0e9b5eef7af1b8fd60d341741e197883adced60202839b39304183  frontend-js/README.md
ad82b29d155e715eb2e3c9d36b5eb80c8dc8f9ba9c3248dac843e760d7409d99  frontend-js/README.zh-CN.md
ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef  frontend-js/src/app/equipment/api/observations.js
b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688  frontend-js/src/app/equipment/components/observations/RecordList.vue
f89964f9802f9a99339981947864fcb405d2b5a61a68c746a0d979ea63a53341  frontend-js/src/app/equipment/locales/en-US.json
2a374840c98e82d808615502e80fa229d87a88230c30875f3dbd9ea1c4834970  frontend-js/src/app/equipment/locales/zh-CN.json
cd24870f3c2301acae453cf99ba40669414c018974b895b0420333ccdce96dbe  frontend-js/src/app/equipment/manifest.js
dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68  frontend-js/src/app/equipment/views/observations/admin.vue
9d3dcb8d7f74e69dfb2c270978e9c688187f8c9d68091b0b383864e64182579d  frontend-js/src/app/equipment/views/observations/cards.vue
086e8027db5990bda7d006b8a92bdd865fc1c1f8aea135dfb46631d034de41d0  frontend-js/src/app/equipment/views/observations/data.vue
144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5  frontend-js/src/app/monitor/api/observations.js
ef53632ce9a9fc9dc522a86336c35f85e42b59b9738cd1f940913f2121a190dd  frontend-js/src/app/monitor/components/observations/CurveChart.vue
19865b25d524b65edcdf155fe2436a7efd921b3c7ef311749e215739d55c64a5  frontend-js/src/app/monitor/components/observations/EmptyAxes.vue
7e11059e9a03496b5f39b247e3e98608aaacae68c0e5fb7853fd0fe28da784e1  frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue
a6f659342eea1b29862c75a440a4a21ec8cdeeeb473e4bbfdcaf723fa977f1ee  frontend-js/src/app/monitor/components/observations/curveSeries.js
309cc3912ae14d1d8dbeffb0cb81dd26949a9e995aedd1ceccb240c48f18ffe6  frontend-js/src/app/monitor/locales/en-US.json
dfddf97b60aeb1eb1242b6fa22cf530a93426910f9c43410166b29c504385f10  frontend-js/src/app/monitor/locales/zh-CN.json
e8dfbec2c1537e33d9624cce8fff4c5c0c325b340eb08ec229a1a1f115212dc7  frontend-js/src/app/monitor/manifest.js
3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787  frontend-js/src/app/monitor/views/observations/admin.vue
a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10  frontend-js/src/app/monitor/views/observations/curves.vue
11e3a81d8b0e425e83058fdf65da2eadb809d4239de49c0673846d20a38256ac  frontend-js/src/app/monitor/views/observations/data.vue
7a9318614f675691c12386dd342cf492e1b578ad3e59a74ac658148c49b7eb65  frontend-js/src/app/monitor/views/observations/energy.vue
d28979a3b7817f1c54e1191255d9cc9f7028db6753f55fc0af9311e8fd939a59  frontend-js/tests/module-registry/equipment-observation-columns.test.mjs
f21807090478aff142e6c0679ffc6a32e450ff70077880924d1b64ecc4f0d247  frontend-js/tests/module-registry/equipment-observation.test.mjs
e2918a4a63ebf7f923a7ee8f50399f5c4d110628e1eff0c223b6d424752aee8a  frontend-js/tests/module-registry/page-access.test.mjs
0a3c1ef166eae9dcd0303bc8450b3186962bb7e335ad835fbe6ccb45cc71c5de  frontend-js/tests/module-registry/registry.test.mjs
```

**临时验证材料 27 项摘要**（SHA-256 和相对 `/private/tmp/arch-obs-r11-8O97SDOg` 的路径，不含凭据文件）：

```text
557cdf38d877cb0e0629fffebb598704e2e286db2212cecba069e6f580fd8545  RUNBOOK.md
f178e8f5bac84a1b3cf54e215be70ae675d39c2752992f9bc2c5a33b9a332e67  safe_target.py
2d50c0fa23f98c40ca4b6115ad057bbd35138b93bf841458d792bb8e92f6bfb5  control.py
9436125d5ea2e92add134cc3a9546c47d3a4e2b56bc86f2e35e3813baedb75e8  seed_r8.py
2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34  r8_ingest_reference.py
62e93d2895089c650511b3e3937245cab2b5769bd4dafddd54d576b4172b73c7  qa_upgrade.py
a56780c5930b8925da9cab3dacfde85c76202cf5a9ab36430e5ec8004df9aa4d  qa_replay.py
630dd116bc3ada541452d0b11fa08ca0c4a350e508789e045fdec438614a4272  qa_replay_http.py
7563b35c084b5401261b9ae88a3948a076a2251233c43c081b357a1906cc01c6  qa_recovery_collision.py
d1f9ca554b786987955eea5fcd626080064ee2447306e874237a4551fdb68a30  qa_recover.py
fe1405a3d61bbeb4ab3a21a0e12f11af4e19999d5c24af0df003ee42e2302109  qa_guards.py
8ea68b115b90fc1775da4f200157bb2ea062810a30b6cc046971fabfd0350d96  qa_interrupt.py
8ac61b38971841819ac748d427d02d8486ac3e2acd3350f70b191fa2f9131e0c  qa_interrupt_child.py
a6c4226fc67898adb608c6088470675ccec6020334bc7472bf82f1916787a24b  qa_interrupt_refusal.py
adfbc96103b7b8165eb654210e5781da11afe531e8d3cf125292e70f54541106  audit_final.py
4cb75f820fa09beaec2a65a984182d00478a3783ca08917d17b9480491ee3662  source-manifest.json
1cfdaad0f872e8d26a16b645fdc50cfaec13029684797cee3b2b7adde07bfa22  r8-baseline-obs_r11_main.json
f1e0f225e43e74363f7927b0c1de5cb47840fc74426df7df8b8f8e04f1d4e96e  create_target.py
e98b485d1adebc0087e43f78e89bdbe5a1e610f4a737b0b3a63ad5d0e59beb4c  initialize_target.py
dc892ffa91cdd3d9c3717b78b7406411fb4741e55ab85e9e4969ba5f7c6126e0  copy_source.py
0cbf731aeeeffa5aba8fda9385e5f61951a686541546857b0e68f2dc4cf4e5ca  audit_predecessor.py
34832b746aa711948038eaa46436d4dabae89f03e14c405e2dfc77915b67850c  audit_facts_predecessor.py
0cfb4549525f745d4c4bca532cc922f19cd4c5fbf8d99dec52a6926c34c4e619  ownership.json
fe147b784732585d6e1334755a124cec043acdc92d4ca3b3c5bba9a3f1476ee7  init-r8-obs_r11_main.log
e5d6f6c2a4f2ecda1a939d9814773c78a45f65c7c420366cd04b9360d27c882b  resume-r8-obs_r11_main.log
c5c9359fb2e5186409b33e01e5feed97dc23f03f9473c2f768c0abbf284e5e09  resume-r8-facts-obs_r11_main.log
1fb4054b563379cd9d6f77638a38d25f8ce6a69cec0fa94026bd80ed94dc2662  seed-r8-obs_r11_main.log
```

# r10 QA3 返工

2026-11-17：接收独立 Verification 的 `qa_failed`，checklist SHA-256 `c71a6ff741600b5db30e96cd9bc58ceaa1c8eda411bde26715096181775d7b11`；前次交接 61 文件摘要、spec SHA-256 与两份模块 README 的修改前摘要均已核对。仅按获批 r10 §12 修复 R10-QA-008–009，历史交接与 QA 结论保留。

### r10 QA3 返工 developer_handoff

**对象与变更。** 获批对象为 `ARCH-OBS-001 r10 §12`，正式交付为 `main` 工作树、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0` 上的未提交候选。spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`；返工依据 checklist SHA-256 `c71a6ff741600b5db30e96cd9bc58ceaa1c8eda411bde26715096181775d7b11`。上一 61 项逐项核对一致后，本轮只修改 `frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue`、`frontend-js/tests/module-registry/equipment-observation-columns.test.mjs`，补正 `backend/app/equipment_observation/README.md`、`README.zh-CN.md`，以及本 `tasks.md`。前两份为原清单修改，两份 README 为此轮补入候选；其余 59 项保持原字节，未改 spec、checklist 或其他并行工作。本节末完整 63 项清单整体 SHA-256 为 `8512aaecbd8610cae2d44cf02014b7bb643dddea48bf0876d4866d5eb41fb6ea`，该摘要不含 tasks/spec/checklist 本身。QA3 对旧缺陷的结论及本轮 `qa_failed` 原样保留，开发自检不是 QA 或 Human Owner 最终验收。

**R10-QA-008。** 两份模块 README 以 r10/v2 为当前入口，解释来源无关、真实 `observedAt`、设备最新整包／过程追加／独立能耗三表、配置与人类/机器权限；v1、PLC 任务证据仅作为旧合同和原回执重放的历史说明。保留 SMA 产品和实际 PLC 接入未由本任务证明的边界。

**R10-QA-009。** 表计、组和页改变时同步失效旧请求、关闭旧编辑、清除旧行；仅提交仍匹配当前选择及请求代次的配置、样本与错误，并保留同范围分页总数以避免翻页重置。样本配置与数据作为同一查询结果提交；旧配置请求不能再发新表计的样本请求。编辑只允许当前已展示且属于所选表计的对象，保存固定打开时的身份；保存期间禁用切换控件，旧保存回调不能覆盖新选择。新增 4 个实际 Vue SFC 与可控 promise 回归；修复前复现 A 旧配置覆盖 B、A 旧样本覆盖 B 和 A 旧请求重复请求 B 三条失败，修复后覆盖两模式逆序、筛选／分页、迟到错误与旧保存失败、无表计选项重试、打开后切换、修改表单身份但固定目标，以及既有动态列顺序、零/false/空值、语言、微秒与同名图例。

**正式源码 DEV self-check。** `frontend-js/` 执行 `pnpm_config_verify_deps_before_run=false pnpm test:modules` 退出 0，**85 passed**；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa3-rework-dist` 退出 0、2262 模块；外部 outDir 与大 chunk 提示保留。`backend/` 用不可连接的合成 MySQL 端口 1 和项目 uv 锁定环境执行 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r8-private.ZQFVM8IQ/uv-cache LOG_DIR=/private/tmp/arch-obs-r10-qa-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=fixture MYSQL_PASSWORD=fixture MYSQL_DATABASE=fixture MYSQL_ROOT_USER=fixture MYSQL_ROOT_PASSWORD=fixture TEST_MYSQL_DATABASE=fixture_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py`：退出 0，**50 passed、1 warning**，warning 为 SQLite datetime adapter 弃用。包含独立 SQLite/ASGI 普通能耗读角色允许表计 1、拒绝表计 2 和管理接口的测试。六份公开说明 150 个本地目标、两份模块 README 10 个本地链接及显式锚点均可达；`git diff --check` 通过，新改文件无行尾空格。先前扩展测试集中旧 `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` 的固定数量断言失败仍按旧 handoff 保留；本轮未改、未重跑该范围外测试或示例模板。

**真实 dev／正式浏览器。** 测试前复核授权 `127.0.0.1:3307 / industrial_level_2_system`、server UUID SHA-256 前缀 `ac2319a3fdc8`、revision `9d1f3a5c7e20`、连接与近 5 分钟采集事实；当时无活动 SQL、未见近期事实写入，Human Owner 此前确认已停止 SMA 投递，不代表可预测后续所有写入。使用后缀 `aaa8d2962e25` 的独有合成设备、4 区、指标、绑定、卡片、3 曲线、两表计、两种模拟机器身份与临时 admin/operator；没有操作 SMA 产品或 PLC。先仅切换指向该临时 profile 的一项 OBS 引用并按授权短暂重载现有 8000，真实机器发现成功；正式普通账号访问设备/过程/能耗读及能耗管理各 403，未改已有全局角色权限。

以任务独有 Chrome 会话和临时账号登录状态访问**正式 5190 + 正式 8000 + 真实 dev MySQL**：温度曲线在配置存在但无样本时实际显示所选范围的空 X/Y 轴、`°C` 与“暂无数据”；正式 8000 的第三方和模拟 SMA HTTP 写入后，页面查询恢复真实多区域曲线，移除一区只留二区、再全选。过程管理表显示 6 条样本与实际值／设定值指标列；能耗数据管理从表一的 `1000/1006` 切至表二的 `2/3`，编辑表二记录 `32` 的备注；表计配置管理从累计表一切到时段增量表二，修改表二中文名。随后以真实 MySQL 只读核对，表二配置和记录 32 已按测试修改，表一的对应配置与两条样本均未改。完整业务路由得到实时 1、历史 6、能耗 4，累计用量 6、区间用量 5，真实缺测事件与微秒入库校验通过；本轮没有执行撤权重放，旧证据仍在。页面快照显示管理页面无浏览器 error、出现 1 条未深入定位的 warning；本轮未在正式页重复传动／清洗／能耗统计直达、错误重试、普通角色获授权正向浏览器及所有权限组合。普通角色正向目前只有上面的 SQLite/ASGI 测试，不能冒充真实 MySQL／浏览器正向验证。

空图与有值图截图仅含合成数据，分别暂留 `/private/tmp/arch-obs-r10-private.j0jFyKfK/qa3-formal-empty.png`、`qa3-formal-with-data.png`，SHA-256 `591738510fce6c7bdfd6e930d06f02ba2de5c0a7a15ca69bc0af5b6019506f29`、`469660ee11c3ba32fa61dd9f21387db122cbf1f14c8037829817b950d719c039`；截图辅助记录，不代替上述实际 HTTP 和 MySQL 对账。

**恢复与资源。** 已主动释放窗口，原 `.env` 字节恢复并重载；采集 GET 200，临时机器身份返回 401。按本轮主键与回执核对归属后清理，区域、指标、槽位、卡片、曲线、实时／历史／能耗、回执、两个测试账号及临时 profile 均零残留；17 张保护表的行数与 checksum 前后一致，包含原采集、计划/实绩、旧表、价格、用户及 token blacklist。自有 API 和隔离 Chrome 已停止，临时浏览器 auth 文件与 `.env` 备份已删；原 5190 和其他进程未停止，未再次迁移、未改持久 profile。精确对象及行 ID 的私有归属证据 `dev-r10-row-evidence-aaa8d2962e25.json` SHA-256 `ae31e0f30b7eaa48866be45a6c2250044b763c1b3a9f7010514700ac96aa4c92`，仅含合成标识，不含令牌。前述截图、脚本、私有证据、前端临时构建暂由当前任务持有，供 fresh QA 复查；完成 QA 且无依赖后由协调者按各自归属回收。

**独立复验的可执行路径。** `/private/tmp/arch-obs-r10-private.j0jFyKfK/dev_r10_qa3_formal.py` SHA-256 `309e65bc018034cf9ca4cfbfa2d2d652e94eff729516dfaaee7bbc55899707ff` 是本次已运行的任务专用脚本，不含明文凭据；执行前须重新审计脚本及准确 dev UUID/schema/revision、写入方、端口、profile、目标键、当前数据和授权。当前库/用户状态可能变化，不可把上次预检当作永久结论。`backend/` 用项目环境及仅供自有子进程的占位 bootstrap 值执行：

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r8-private.ZQFVM8IQ/uv-cache ADMIN_BOOTSTRAP_USERNAME=fixture ADMIN_BOOTSTRAP_PASSWORD=fixture-only JWT_SECRET_KEY=fixture-only uv run --offline --frozen --no-sync python /private/tmp/arch-obs-r10-private.j0jFyKfK/dev_r10_qa3_formal.py --execute-dev-http-fixture ARCH-OBS-001-r10
```

脚本先打印 `blank_ready`、随机任务号、一次性浏览器 state 路径和第一个信号路径；在独立浏览器访问 `http://127.0.0.1:5190/monitor/temperature`，加载该 **0600 临时测试账号** state 或使用已授权 admin 会话，选择该任务与时间范围，检查已配置无样本空轴；按输出的精确第一个 signal 路径创建空文件后才写数据，检查 `data_ready` 对应有值页面、管理列表及两表计，再按第二个精确信号路径释放。脚本每阶段最多等 600 秒并在正常异常路径恢复 OBS 引用、重载、验证并按明确归属清理；不输出或保存明文密码。不得使用旧固定身份脚本清理 dev，不得用通配符删除。若进程被强杀或断电使 `finally` 未运行，不要重跑或猜删：先核对当前 `.env` 仍只指向该轮 `dev-r10-profile-<suffix>.json`，并核对其他配置未被并发修改；受保护的 `qa3-env-backup-<suffix>` 是原 `.env` 字节，仅在满足这些条件后原子恢复，再仅重载授权的 8000、核对采集 GET、原 profile 和机器拒绝。依据该轮 `dev-r10-owned-<suffix>.json`、回执与业务行外键逐项确认归属、无外部引用后按反依赖清理；遇到不明关联或配置变化即停止并报告，不覆盖其他工作。备份可能含真实密钥，永不打印或提交，确认恢复后删除。

普通角色获授权的正向独立实测可另用任务独有随机设备／表计及局部 profile，启动任务独有的正式源码 API 和 Vite 端口，在**该进程**给予 operator 所需的 `equipment-observation-read`、`monitor-observation-read`、`energy-consumption-read` 和对应非 admin pageId（supervisor 授权需为其超集），只授一个设备／表计；以真实或清楚标注的合成登录身份验证获准查询 200、其他设备/表计及管理 403，完成后精确清理。不得为此更改正式 8000/5190 的全局角色授权，且应标注独立端口与认证夹具的边界。此路径是后续复验建议，并非本次已完成的证据。

**最终源码逐项摘要**（SHA-256 与路径，按路径排序）：

```text
db53dca713fd3f1e2c6844284f6ef56fc93aa11f9ff2ad88e46d6feb4766f501  CODE_INDEX.md
8d0780c83d990c88ac6fa8ba7c40052740ea4dbe1f4fb4d67b4bdf7ee9d8dcb3  backend/alembic/versions/20261117_1200_9d1f3a5c7e20_observation_bundles.py
d12b94302436835dcd322646c788fd30755dcad48d2318405d22ec606bfc4847  backend/app/equipment_observation/README.md
93bc8166ad154d8a0039a0e7e9eff592cc67b530733fbb93b622fd6ea21b21c2  backend/app/equipment_observation/README.zh-CN.md
89d04f96973411baa31b2ec40c7e8335fab80c86dc5ff892b83c153e9d8f6af0  backend/app/equipment_observation/api/routes.py
39798a2a3119d40b1b846bf26d8fd3ab9a624bfb1cb9b8854f1c0b16dd1dffc2  backend/app/equipment_observation/error_codes.py
93cb6b4d5c6a464b06364441c8887aa466885bed75902fc97d1fe5fb77ca51ef  backend/app/equipment_observation/machine_openapi.py
35b037ee43126b2e6bf991c44f327f5b123a6446c4b239986ea62430258079d7  backend/app/equipment_observation/manifest.py
5a69c30586f65364fb57485dd3adabfd00fc178b2168228f8c08f09cc12f6a7d  backend/app/equipment_observation/models/__init__.py
8ae102b30edf13beb3387f779e35c4ed5119b97b9d55d6d5c07c48322b736914  backend/app/equipment_observation/models/records.py
80e5f3cffd54f67736da287e973110d1e3ce8c94cf20fbd8561921f5f8efc89e  backend/app/equipment_observation/profile.py
262612e3364e725a9f821cec719bc8048e987951a1a4c1bd37b7ce60b2e5956e  backend/app/equipment_observation/schemas.py
aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49  backend/app/equipment_observation/services/configuration.py
135dc8f46b5758cd9600ad5e93553c8993c3ab762c5a48a3422e8f8ab4c95ee8  backend/app/equipment_observation/services/energy_reads.py
af5601fdcc89298f71b8adfae07af0465786c7f746fd8ae905653011df09778c  backend/app/equipment_observation/services/energy_statistics.py
60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3  backend/app/equipment_observation/services/guard.py
0ee4c6c94420f29db504f384491b5e54f2d7d7aa6c72cac02e4c288cf411138e  backend/app/equipment_observation/services/ingest.py
cd94cc1ff19975054ed4903666bf2a794b137af312ca199685f1a1b14b773894  backend/app/equipment_observation/services/ingest_v2.py
f3e8ab8c2d5d711f301593cabb68a756d76699f5b22a6e97a65d479673daf6c2  backend/app/equipment_observation/services/reads.py
bd7f081c6791dbf2ee9969c3f0e77ce13aad686d4a4f20a9c71b4e437fbb4b89  backend/app/equipment_observation/services/v2_domain.py
6f92dfb56df56d3ca1d9866a609d0c4bf55cbc74380394a91ba48a89de5d2fe0  backend/app/plc_facts/v2_config.py
39e4cdd218d83475112cddc5780a1fd4a8eba24cfc3ce79b29d5ef3b8a6bce76  backend/common/integration/storage.py
582e34fc026e80291c44e90dae45f9814a5ceb4a9db76369f8a3b5f48af37748  backend/tests/test_energy_price_api.py
a6f24f3b01610bdd3736564148c179ae3a28fd95d165d16d82f5562222ef59e6  backend/tests/test_equipment_observation_domain.py
32ead808cdf317b9b38c32fa45eb35bef66074d0a8d87dbec06e384a2469d855  backend/tests/test_equipment_observation_r10.py
b19452c3fdae3722579cd17628de196732f2e6ed291032a6f99deb0a82751641  backend/tests/test_equipment_observation_r10_flow.py
71d91aa54ae883be9c2e3961fdb89fa5eb6ad4b52d57d7de808fc5422a609444  backend/tests/test_equipment_observation_r8.py
4fdc00cdf51d41f1b87badcf7b9c3af0d5c8e805fb5441022a57c08ed8905123  backend/tests/test_equipment_temperature_migration.py
0393e9346c4d04884d99d77c6c006754894864c7a3d57b2517a4feb5d3e208ae  backend/tests/test_legacy_acquisition_retirement.py
706acd4edfe88e09a0f38dcacda98f0792407e41fed2b7ee30083f225f98f6c2  backend/tests/test_mapping_migration.py
0532f522a69fe2db7e463536617cd0de3af08fc86bbb2775dabd4084b2d2e68f  contracts/README.md
980e5616459dcda55633fd289368e88829a176486e7c88504d481867766b3c23  contracts/README.zh-CN.md
b3379d7181b285680f739bd3b9ebc6ca8ea010a542b546993bd706244a4609bc  contracts/published/http-api/equipment-observation-v2/README.md
e84d4c2afe7e55bf3ddc7005244bfd755f715d7469072508d91da3b5222958d6  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
d11a7c030f7a4401219b2d5160f4d77345df28d42a39e364861144a019252989  contracts/published/http-api/equipment-observation-v2/example-profile.json
cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646  contracts/published/http-api/equipment-observation-v2/openapi.json
870378e53e1becd7c70a5d0b38f062b2e4bf809ff68a8269c34bd5441962d0a7  contracts/published/http-api/equipment-observation-v2/vectors.json
0b777e70584e0086b00616270716fe93df24419ed737c1df9720473e368b7528  docs/equipment-status-process-monitoring.md
7c7137720e399e7e60cf89614ad1f9b486c52928c1a9f23ca68b4fa44ff3d798  docs/equipment-status-process-monitoring.zh-CN.md
ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef  frontend-js/src/app/equipment/api/observations.js
b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688  frontend-js/src/app/equipment/components/observations/RecordList.vue
f89964f9802f9a99339981947864fcb405d2b5a61a68c746a0d979ea63a53341  frontend-js/src/app/equipment/locales/en-US.json
2a374840c98e82d808615502e80fa229d87a88230c30875f3dbd9ea1c4834970  frontend-js/src/app/equipment/locales/zh-CN.json
cd24870f3c2301acae453cf99ba40669414c018974b895b0420333ccdce96dbe  frontend-js/src/app/equipment/manifest.js
dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68  frontend-js/src/app/equipment/views/observations/admin.vue
9d3dcb8d7f74e69dfb2c270978e9c688187f8c9d68091b0b383864e64182579d  frontend-js/src/app/equipment/views/observations/cards.vue
086e8027db5990bda7d006b8a92bdd865fc1c1f8aea135dfb46631d034de41d0  frontend-js/src/app/equipment/views/observations/data.vue
144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5  frontend-js/src/app/monitor/api/observations.js
ef53632ce9a9fc9dc522a86336c35f85e42b59b9738cd1f940913f2121a190dd  frontend-js/src/app/monitor/components/observations/CurveChart.vue
19865b25d524b65edcdf155fe2436a7efd921b3c7ef311749e215739d55c64a5  frontend-js/src/app/monitor/components/observations/EmptyAxes.vue
7e11059e9a03496b5f39b247e3e98608aaacae68c0e5fb7853fd0fe28da784e1  frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue
a6f659342eea1b29862c75a440a4a21ec8cdeeeb473e4bbfdcaf723fa977f1ee  frontend-js/src/app/monitor/components/observations/curveSeries.js
309cc3912ae14d1d8dbeffb0cb81dd26949a9e995aedd1ceccb240c48f18ffe6  frontend-js/src/app/monitor/locales/en-US.json
dfddf97b60aeb1eb1242b6fa22cf530a93426910f9c43410166b29c504385f10  frontend-js/src/app/monitor/locales/zh-CN.json
e8dfbec2c1537e33d9624cce8fff4c5c0c325b340eb08ec229a1a1f115212dc7  frontend-js/src/app/monitor/manifest.js
3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787  frontend-js/src/app/monitor/views/observations/admin.vue
a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10  frontend-js/src/app/monitor/views/observations/curves.vue
11e3a81d8b0e425e83058fdf65da2eadb809d4239de49c0673846d20a38256ac  frontend-js/src/app/monitor/views/observations/data.vue
7a9318614f675691c12386dd342cf492e1b578ad3e59a74ac658148c49b7eb65  frontend-js/src/app/monitor/views/observations/energy.vue
d28979a3b7817f1c54e1191255d9cc9f7028db6753f55fc0af9311e8fd939a59  frontend-js/tests/module-registry/equipment-observation-columns.test.mjs
f21807090478aff142e6c0679ffc6a32e450ff70077880924d1b64ecc4f0d247  frontend-js/tests/module-registry/equipment-observation.test.mjs
e2918a4a63ebf7f923a7ee8f50399f5c4d110628e1eff0c223b6d424752aee8a  frontend-js/tests/module-registry/page-access.test.mjs
0a3c1ef166eae9dcd0303bc8450b3186962bb7e335ad835fbe6ccb45cc71c5de  frontend-js/tests/module-registry/registry.test.mjs
```

# r10 QA2 返工

2026-11-17：接收 fresh-context Verification 正常完成并持久化的 `qa_failed` checklist，SHA-256 `673dc33d2d4c7ae146da213d1defb0c29a4f39cab9bb69ef052127910f2e1bd8`。写入前核对 spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623` 及先前交接 61 文件摘要均匹配。QA1 原缺陷 R10-QA-001–004 的原始复现由 QA2 关闭；本轮仅在已批准 r10 §12 范围返工 R10-QA-005–007，不修改 spec／checklist，保留全部历史。新的 developer_handoff 已记录如下。

### r10 QA2 返工 developer_handoff

**精确候选。** 获批范围为 ARCH-OBS-001 r10 §12；正式 `main` 工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，交付为当前未提交源码及任务文档。spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`；返工依据的 QA2 checklist SHA-256 `673dc33d2d4c7ae146da213d1defb0c29a4f39cab9bb69ef052127910f2e1bd8`，原 `qa_failed` 和 QA1 四项关闭事实由 Verification 记录，本角色不改判。写入前 QA1 返工候选 61 文件逐项匹配；本轮只改变其中下列 6 项：设备卡片页、能耗页、曲线组件、对应前端测试和两份双语使用说明。新的 61 文件 `SHA-256  相对路径` 清单整体 SHA-256 为 `dab8569947134f5c331a1d71d111f5f86ac819b2518169cee97e41bea12104ad`，逐项清单见下。未改变其他并行工作、spec 或 checklist。

**R10-QA-005。** 表计定义读取按当前表计及请求代次核对，多个同表计重试共用正在进行的定义请求；切换表计、组、指标或范围立即使旧采样／汇总／分页请求失效并清除旧值。只提交属于当前 `(meterId, groupKey, metricKey, range)` 的结果，迟到的旧结果及错误不能覆盖新选择或将新界面误设为失败。定向测试实际编译 Vue SFC，通过可控 promise 验证 A→B 定义倒序、旧失败、同名指标跨组、旧分页和汇总迟到、当前组 0 值、中英名称以及初始化重试；真实 dev 合成浏览器中 B 显示最新 3，切回 A 时旧统计消失，重新查询显示 1006。该浏览器观察不是对全部网络时序的证明，乱序由受控 SFC 测试验证。

**R10-QA-006。** 四个设备页共用的卡片对过期值显示其自身的真实 `observedAt`，按项目上海时区格式显示到秒；采集时间缺失或无效时显示 `—`，不使用刷新、接收或当前时间。实际 Vue 模板双语 SSR 覆盖带 UTC 偏移转换、0、false、缺测及空采集时间；独立合成浏览器从真实 MySQL/API 看到的值 810.2／815 标记陈旧，接口原时刻 `2026-11-17T14:21:29.200538+08:00` 在中英卡片均为 `2026-11-17 14:21:29`。

**R10-QA-007。** 每个图例的内部身份使用稳定 `groupKey + metricKey`，同一指标的连线与同刻散点归同一图例；图例和 tooltip 显示当前语言的区域及指标名，若两个显示名仍相同则附带无歧义的稳定键，tooltip 对名称继续 HTML 转义。不同区域指标各自隐藏／恢复；切换语言或刷新渲染时保留同一稳定系列的图例选择。项目 ECharts 实例和实际 SFC 测试覆盖两个区域同名、区域名称也相同、含分隔符的键、独立控制、同刻散点、语言变化与特殊字符转义；先前微秒／缺测／宽范围提示回归仍通过。正式源码的任务专属浏览器副本在真实 MySQL 上看到两个区域的同名实际值，隐藏一区后二区仍在，切换中文到英文后该隐藏状态仍保持。浏览器截图在工具中观察但未保存；tooltip 的独立名称和转义由实际 ECharts SSR 测试验证，本轮未在浏览器中复现 hover 提示。

**正式树 DEV self-check。** 在 `frontend-js/` 执行 `node --test tests/module-registry/equipment-observation-columns.test.mjs tests/module-registry/equipment-observation.test.mjs` 得 **18 passed**；`pnpm_config_verify_deps_before_run=false pnpm test:modules` 得 **81 passed**；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa2-final-dist` 退出 0、2262 模块，仍有外部 outDir 与大 chunk 提示。

正式 `backend/` 使用不可连接的合成 MySQL 端口 1、虚构账号及项目锁定运行时执行 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r8-private.ZQFVM8IQ/uv-cache LOG_DIR=/private/tmp/arch-obs-r10-qa-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=fixture MYSQL_PASSWORD=fixture MYSQL_DATABASE=fixture MYSQL_ROOT_USER=fixture MYSQL_ROOT_PASSWORD=fixture TEST_MYSQL_DATABASE=fixture_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py`，**50 passed、1 warning**，退出 0；warning 为 SQLite datetime adapter 弃用。包含先前回执当前授权、旧 v1 重放和能耗相关保护。此前额外扩展集合的 `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` 仍有已记录的固定数量断言失败（当时 338 passed、2 skipped、1 failed）：断言公开示例为 69／91，三份实际 66／84。本次未重跑该扩展集合；该测试及三份示例当前无工作树改动，未篡改其断言。双语使用说明及机器合同的 98 个本地文件链接可达，`git diff --check` 通过；新改的 4 个源码／测试文件另查尾随空格为 0。

**dev、浏览器及清理。** 两轮唯一合成对象后缀 `3fc39f339e51`、`86b2e92d607f` 均在明确授权的 `127.0.0.1:3307 / industrial_level_2_system` 上，先核对 server UUID 摘要前缀 `ac2319a3fdc8`、schema、唯一 revision `9d1f3a5c7e20`、时区及唯一键无冲突。每轮使用随机第三方与模拟 SMA 机器身份、独立回环 API、真实正式 OBS 路由与 MySQL；独立 UI API 使用合成只读 admin 身份，四个直接前端源码文件与正式树分别匹配。每轮验证 1 条实时、6 条历史（含微秒与缺测）、4 条能耗、卡片曲线、两路撤权和恢复重放以及累计／区间统计。只按本轮精确记录、回执、指标、区域、卡片、曲线与表计键核查归属和外部引用后清理；两轮残留均 0，15 张保护表行数及 checksum 前后不变，独立 API／只读 API／Vite 停止、合成 profile 删除。第一轮窗口到 300 秒上限自动结束，第二轮主动释放。按顺序的私有归属证据 SHA-256 为 `09e3b212bc4cfb1156308a93a8e1b338a6b2f109323339cb990e8cbe9f75e46e`、`75b4d7e8dbcc73b0f0c866d9a39147b5b292060123fa23914fb8338cbffd6141`，仅用于复核，不提交密钥。

最终只读对账：新三主表、回执及配置均为 0；原采集历史／latest 为 73／6、来源登记 3，旧能耗两表 0，原价格表 1／3；没有再次迁移或改写持久 profile。用用户已自行登录的正式 5190 同浏览器配置**新建的独占标签**，只读看到温控页面、温度曲线的无设备提示及能耗的无表计提示，随后只关闭本轮新标签；未接管或覆盖原用户标签、输入、密码或 token。合成 admin 不代表正式账号权限矩阵，正式用户下有数据的三项页面及普通用户范围仍由 QA 复核；未操作 SMA／DAA 产品、PLC、其他进程或生产。

**资源及下一 gate。** 两轮本任务独占的临时浏览器源码副本及迟到释放标志已清理；`/private/tmp/arch-obs-r10-qa2-rework-dist`、`/private/tmp/arch-obs-r10-qa2-final-dist` 是本轮构建产物，原候选与 `/private/tmp/arch-obs-r10-private.j0jFyKfK` 私有证据／恢复资料继续由协调者保留，独立 QA 完成且无恢复依赖后核对归属回收。以下精确候选交新的 fresh-context Verification 复验 QA2 三项和未覆盖项；本记录是 Development 自检，不是 QA 或 Human Owner 验收。

<details><summary>r10 QA2 返工交付清单（61 项）</summary>

```text
db53dca713fd3f1e2c6844284f6ef56fc93aa11f9ff2ad88e46d6feb4766f501  CODE_INDEX.md
8d0780c83d990c88ac6fa8ba7c40052740ea4dbe1f4fb4d67b4bdf7ee9d8dcb3  backend/alembic/versions/20261117_1200_9d1f3a5c7e20_observation_bundles.py
89d04f96973411baa31b2ec40c7e8335fab80c86dc5ff892b83c153e9d8f6af0  backend/app/equipment_observation/api/routes.py
39798a2a3119d40b1b846bf26d8fd3ab9a624bfb1cb9b8854f1c0b16dd1dffc2  backend/app/equipment_observation/error_codes.py
93cb6b4d5c6a464b06364441c8887aa466885bed75902fc97d1fe5fb77ca51ef  backend/app/equipment_observation/machine_openapi.py
35b037ee43126b2e6bf991c44f327f5b123a6446c4b239986ea62430258079d7  backend/app/equipment_observation/manifest.py
5a69c30586f65364fb57485dd3adabfd00fc178b2168228f8c08f09cc12f6a7d  backend/app/equipment_observation/models/__init__.py
8ae102b30edf13beb3387f779e35c4ed5119b97b9d55d6d5c07c48322b736914  backend/app/equipment_observation/models/records.py
80e5f3cffd54f67736da287e973110d1e3ce8c94cf20fbd8561921f5f8efc89e  backend/app/equipment_observation/profile.py
262612e3364e725a9f821cec719bc8048e987951a1a4c1bd37b7ce60b2e5956e  backend/app/equipment_observation/schemas.py
aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49  backend/app/equipment_observation/services/configuration.py
135dc8f46b5758cd9600ad5e93553c8993c3ab762c5a48a3422e8f8ab4c95ee8  backend/app/equipment_observation/services/energy_reads.py
af5601fdcc89298f71b8adfae07af0465786c7f746fd8ae905653011df09778c  backend/app/equipment_observation/services/energy_statistics.py
60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3  backend/app/equipment_observation/services/guard.py
0ee4c6c94420f29db504f384491b5e54f2d7d7aa6c72cac02e4c288cf411138e  backend/app/equipment_observation/services/ingest.py
cd94cc1ff19975054ed4903666bf2a794b137af312ca199685f1a1b14b773894  backend/app/equipment_observation/services/ingest_v2.py
f3e8ab8c2d5d711f301593cabb68a756d76699f5b22a6e97a65d479673daf6c2  backend/app/equipment_observation/services/reads.py
bd7f081c6791dbf2ee9969c3f0e77ce13aad686d4a4f20a9c71b4e437fbb4b89  backend/app/equipment_observation/services/v2_domain.py
6f92dfb56df56d3ca1d9866a609d0c4bf55cbc74380394a91ba48a89de5d2fe0  backend/app/plc_facts/v2_config.py
39e4cdd218d83475112cddc5780a1fd4a8eba24cfc3ce79b29d5ef3b8a6bce76  backend/common/integration/storage.py
582e34fc026e80291c44e90dae45f9814a5ceb4a9db76369f8a3b5f48af37748  backend/tests/test_energy_price_api.py
a6f24f3b01610bdd3736564148c179ae3a28fd95d165d16d82f5562222ef59e6  backend/tests/test_equipment_observation_domain.py
32ead808cdf317b9b38c32fa45eb35bef66074d0a8d87dbec06e384a2469d855  backend/tests/test_equipment_observation_r10.py
b19452c3fdae3722579cd17628de196732f2e6ed291032a6f99deb0a82751641  backend/tests/test_equipment_observation_r10_flow.py
71d91aa54ae883be9c2e3961fdb89fa5eb6ad4b52d57d7de808fc5422a609444  backend/tests/test_equipment_observation_r8.py
4fdc00cdf51d41f1b87badcf7b9c3af0d5c8e805fb5441022a57c08ed8905123  backend/tests/test_equipment_temperature_migration.py
0393e9346c4d04884d99d77c6c006754894864c7a3d57b2517a4feb5d3e208ae  backend/tests/test_legacy_acquisition_retirement.py
706acd4edfe88e09a0f38dcacda98f0792407e41fed2b7ee30083f225f98f6c2  backend/tests/test_mapping_migration.py
0532f522a69fe2db7e463536617cd0de3af08fc86bbb2775dabd4084b2d2e68f  contracts/README.md
980e5616459dcda55633fd289368e88829a176486e7c88504d481867766b3c23  contracts/README.zh-CN.md
b3379d7181b285680f739bd3b9ebc6ca8ea010a542b546993bd706244a4609bc  contracts/published/http-api/equipment-observation-v2/README.md
e84d4c2afe7e55bf3ddc7005244bfd755f715d7469072508d91da3b5222958d6  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
d11a7c030f7a4401219b2d5160f4d77345df28d42a39e364861144a019252989  contracts/published/http-api/equipment-observation-v2/example-profile.json
cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646  contracts/published/http-api/equipment-observation-v2/openapi.json
870378e53e1becd7c70a5d0b38f062b2e4bf809ff68a8269c34bd5441962d0a7  contracts/published/http-api/equipment-observation-v2/vectors.json
0b777e70584e0086b00616270716fe93df24419ed737c1df9720473e368b7528  docs/equipment-status-process-monitoring.md
7c7137720e399e7e60cf89614ad1f9b486c52928c1a9f23ca68b4fa44ff3d798  docs/equipment-status-process-monitoring.zh-CN.md
ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef  frontend-js/src/app/equipment/api/observations.js
b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688  frontend-js/src/app/equipment/components/observations/RecordList.vue
f89964f9802f9a99339981947864fcb405d2b5a61a68c746a0d979ea63a53341  frontend-js/src/app/equipment/locales/en-US.json
2a374840c98e82d808615502e80fa229d87a88230c30875f3dbd9ea1c4834970  frontend-js/src/app/equipment/locales/zh-CN.json
cd24870f3c2301acae453cf99ba40669414c018974b895b0420333ccdce96dbe  frontend-js/src/app/equipment/manifest.js
dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68  frontend-js/src/app/equipment/views/observations/admin.vue
9d3dcb8d7f74e69dfb2c270978e9c688187f8c9d68091b0b383864e64182579d  frontend-js/src/app/equipment/views/observations/cards.vue
086e8027db5990bda7d006b8a92bdd865fc1c1f8aea135dfb46631d034de41d0  frontend-js/src/app/equipment/views/observations/data.vue
144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5  frontend-js/src/app/monitor/api/observations.js
ef53632ce9a9fc9dc522a86336c35f85e42b59b9738cd1f940913f2121a190dd  frontend-js/src/app/monitor/components/observations/CurveChart.vue
19865b25d524b65edcdf155fe2436a7efd921b3c7ef311749e215739d55c64a5  frontend-js/src/app/monitor/components/observations/EmptyAxes.vue
8bbb08b46eb61fed0a282944851ee8c3805aad03bd4fadcff78d4e5e9bf25b37  frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue
a6f659342eea1b29862c75a440a4a21ec8cdeeeb473e4bbfdcaf723fa977f1ee  frontend-js/src/app/monitor/components/observations/curveSeries.js
309cc3912ae14d1d8dbeffb0cb81dd26949a9e995aedd1ceccb240c48f18ffe6  frontend-js/src/app/monitor/locales/en-US.json
dfddf97b60aeb1eb1242b6fa22cf530a93426910f9c43410166b29c504385f10  frontend-js/src/app/monitor/locales/zh-CN.json
e8dfbec2c1537e33d9624cce8fff4c5c0c325b340eb08ec229a1a1f115212dc7  frontend-js/src/app/monitor/manifest.js
3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787  frontend-js/src/app/monitor/views/observations/admin.vue
a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10  frontend-js/src/app/monitor/views/observations/curves.vue
11e3a81d8b0e425e83058fdf65da2eadb809d4239de49c0673846d20a38256ac  frontend-js/src/app/monitor/views/observations/data.vue
7a9318614f675691c12386dd342cf492e1b578ad3e59a74ac658148c49b7eb65  frontend-js/src/app/monitor/views/observations/energy.vue
8acecef11f47402a01c0801c4c5ae0a82e79f381772042e76a833c662b0570a9  frontend-js/tests/module-registry/equipment-observation-columns.test.mjs
f21807090478aff142e6c0679ffc6a32e450ff70077880924d1b64ecc4f0d247  frontend-js/tests/module-registry/equipment-observation.test.mjs
e2918a4a63ebf7f923a7ee8f50399f5c4d110628e1eff0c223b6d424752aee8a  frontend-js/tests/module-registry/page-access.test.mjs
0a3c1ef166eae9dcd0303bc8450b3186962bb7e335ad835fbe6ccb45cc71c5de  frontend-js/tests/module-registry/registry.test.mjs
```
</details>

# r10 QA1 返工

2026-11-17：接收独立 Verification 已持久化的 `qa_failed` checklist，SHA-256 `d30c929766f3f6f4fdd4b066694565c0c319e02190f2401528b35b6416d9fb78`。写入前核对原 r10 交接 60 文件摘要均匹配、spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623` 未变，按该清单对 R10-QA-001–004 返工；既有独立 verdict、旧 handoff 和全部历史保留。Verification 在写完 checklist 后的最终交接回复因自动内容审核提示可能的网络安全风险而中断，随后只请求其确认元数据的回复也被同样中断；此处仅记录该通信限制，不伪造其最终回复或改变已持久化的 QA 结论。本轮在批准的 r10 §12 范围内继续，尚未形成新的 developer_handoff。

### r10 QA1 返工 developer_handoff

**交付身份。** 精确获批版本为 ARCH-OBS-001 r10 §12，批准后 spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`；返工依据的独立 QA1 checklist SHA-256 `d30c929766f3f6f4fdd4b066694565c0c319e02190f2401528b35b6416d9fb78`，其 `qa_failed` 不改判。交付为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main` 未提交工作树，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。新候选包括原 r10 60 文件及本次新增到候选清单的既有 `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs`，下方 61 文件的 `SHA-256  相对路径` 清单整体 SHA-256 为 `90195c854713c4d93503d996c49e298a2c7d61c2bda9ce4d59c87bf2fbfb9ea0`。返工前原 60 文件逐项匹配；未覆盖其他并行工作。开发不修改 spec 或 checklist，也不宣称独立 QA 通过或 Human Owner 最终验收。

**R10-QA-001（F1）。** 曲线以带偏移原始 `observedAt` 转换为精确微秒身份，只有真实同刻才并列；绘图以所选起始日期附近为相对原点，以避免常见日期的绝对毫秒浮点误差。缺测和配置间隔的断点仍基于精确时刻；每个图表点保留原始时间并在提示中显示。实际 ECharts SVG SSR 测试检验公元 2500 年相差 1 微秒的两点在真实数据和像素坐标中不同、真正同刻两点坐标相同、缺测不连线；间隔恰好阈值和多 1 微秒分别不断／断线。极长时间跨度受浮点坐标精度限制，已实测选择 2300 年至 2601 年时，2600 年 `.123001`／`.123002` 可能落在相同坐标；两个真实点及原始时间仍保留、不判作同刻，并显示中英文提示要求缩小范围。屏幕像素也可能重合，不能据此推断事实同刻。默认轴标签仍按项目合同显示到秒，诊断提示保留原始精度。

**R10-QA-002（F2）。** 设备实时和历史回执重放先核对当前 producer、设备、目标、区域和指标授权；实时还核对全部可替换范围，之后才返回匹配回执。原文、原权限下重试仍返回原回执，冲突正文仍 409；权限收窄后两路均 403、无新增回执或业务行，恢复后仍能重放。SQLite 实际路由用真实机器 Bearer 校验，覆盖模拟 `sma`／`external`／`other`、区域或指标撤权、禁用机器、恢复、历史窄范围新事件和实时替换范围；v1 已存回执与能耗原回归仍保留。真实 MySQL／回环 HTTP 使用独有 external 和模拟 SMA 身份，对区域、指标各收窄分别验证两目标拒绝、无行数变化及恢复后原回执；未运行 SMA 产品。

**R10-QA-003（F3）。** 表计指标编辑可设置已有的列表顺序；能耗样本列表以启用的列表列按顺序升序显示，未设置顺序排后，写入启用和列表显示仍独立。实际组件测试验证 20／10／空顺序与保存；真实 MySQL 的两列分别配置 10 和 20，独立浏览器按 `Synthetic power (kW)`、`Synthetic reading (kWh)` 显示 43／1006，配置弹窗显示列顺序 20。保存测试来自 SFC 合成 API，浏览器只读夹具不提交编辑。

**R10-QA-004（F4）。** 人类曲线 GET 按当前语言返回每个系列的配置区域 `groupLabel`，多选显示该名称但保留稳定 `groupKey`，后续改名不改变键。SQLite 实际路由覆盖两种语言和重命名；真实 MySQL 浏览器中选中 `一区/二区`，切换语言后为 `Area One/Area Two`，单选生效。机器 v2 双语说明已补充回执的当前授权规则，双语使用说明补充区域、排序与精度提示。

**DEV self-check 命令与结果。** 以下数据库变量均为不可连接的合成占位符，端口 1；执行前未访问用户登录凭据。共同前缀为 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r8-private.ZQFVM8IQ/uv-cache LOG_DIR=/private/tmp/arch-obs-r10-qa-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=fixture MYSQL_PASSWORD=fixture MYSQL_DATABASE=fixture MYSQL_ROOT_USER=fixture MYSQL_ROOT_PASSWORD=fixture TEST_MYSQL_DATABASE=fixture_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line`，在正式 `backend/` 执行：

1. 附加 `tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_energy_price_api.py`：**147 passed、1 skipped、1 warning**，退出 0。skip 是冻结 BE003 候选；warning 是 SQLite datetime adapter 弃用。
2. 附加 `--basetemp=/private/tmp/arch-obs-r10-rework-complement.168c6820d081 tests/test_acquisition_data_browse.py tests/test_acquisition_facts_migration.py tests/test_acquisition_source_registry.py tests/test_business_integration_migration.py tests/test_energy_price_migration.py tests/test_energy_price_service.py tests/test_monitor_business.py tests/test_monitor_frontend_permissions.py tests/test_monitor_mapping.py tests/test_plc_facts_v2.py`：**179 passed、2 skipped**，退出 0。skip 分别为采集浏览需独立 fixture、BE012 B runner 仅在保留前驱候选运行。两批覆盖先前记录的 18 文件；本次新增测试和此前时点不同，不能将 326 和原 317 当同一个数量。
3. 额外扩大第二批，还纳入 `tests/test_equipment_temperature_api.py tests/test_equipment_temperature_config.py tests/test_equipment_temperature_service.py`，使用独有 `/private/tmp/arch-obs-r10-rework-pytest.168c6820d081` basetemp：**338 passed、2 skipped、1 failed**，退出 1。失败是未修改的 `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment`：断言三份未修改的公开 `.env` 示例历史字段数／总数为 69／91，而三份现均为 66／84。该失败不在原 18 文件集合，未修改示例、旧断言或以其他通过数掩盖。
4. 正式 `frontend-js/` 执行 `pnpm_config_verify_deps_before_run=false pnpm test:modules`：**75 passed**；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-rework-dist` 退出 0，2262 模块，保留外部 outDir／大 chunk 提示。独立定向运行两个 observation 模块测试 **12 passed**。四份双语指南／机器说明的 98 个本地文件链接可达；中英文 monitor observation 键集合相等；`git diff --check` 退出 0；项目 Alembic 唯一 head `9d1f3a5c7e20`。

**授权 dev 与真实浏览器边界。** 对 `127.0.0.1:3307 / industrial_level_2_system` 重查 server UUID 摘要前缀 `ac2319a3fdc8`、东八区、9d revision、旧私有 profile 引用及本轮随机键无冲突；用独立随机机器、独立合成 admin 认证依赖和正式 OBS 路由／真实 dev MySQL 执行上述两路 HTTP。唯一身份后缀 `168c6820d081`，实时 1 行、历史 6 行（含两条相差 1 微秒的原始时间及缺测）、能耗 4 行，并检查卡片、列表、累计 6、区间 5。只读临时 UI API 使用相同正式读取路由和服务及真实 MySQL，独立浏览器查看 F3、F4；前端副本的五个直接触达文件与正式树摘要一致。浏览器中截图可见，但本轮未持久化截图，不能以此称有截图证据；该合成 admin 不证明正式 8000 用户授权，且本次未重新验证正式 5190 的已登录账号完整权限。QA1 已在用户自行登录后独立观察正式 5190 四页空态，具体边界以 QA checklist 为准。未读取或使用用户密码／token，未操作 SMA、PLC 或用户其他进程。

测试结束前对本轮已创建区域、指标、槽位、曲线、卡片、表计指标、producer／事件／回执和业务行逐键核验归属及外部引用，只删除本轮唯一对象；残留 0，15 张保护表前后行数及 checksum 一致。私有精确行归属证据 SHA-256 `041f4d6432ff59eceeaed72f45f454b6a1d0e9a973c6d6caed5a4dcb70c17ef1`；自有 API、只读 API 和 Vite 已停止，测试 profile 已删。授权目标复核：三张新主表、回执和配置表均为 0；既有采集历史／latest 73／6、来源 3，旧能耗两表 0、原价格 1／3。8000 OpenAPI 与 5190 两入口只读 HTTP 200，不以 HTTP 成功代替浏览器闭环。正式持久 profile／.env 未修改，本轮未再次迁移。

**资源与下一 gate。** 本轮独立浏览器源码副本及两个独有 pytest 临时目录已按归属清理；`/private/tmp/arch-obs-r10-rework-dist` 构建产物、原隔离候选 `/private/tmp/arch-obs-r10-dev.jt9Ah6Pc` 及私有 `/private/tmp/arch-obs-r10-private.j0jFyKfK` 证据／恢复资料暂由协调者保留供独立 QA 与恢复审计，QA 完成且无恢复依赖后核对归属回收；私有目录不可提交或输出凭据。下列正式工作树候选交新的 fresh-context Verification 复验全部返工及 QA1 未覆盖事项。真实 SMA/DAA 产品、PLC、生产部署及 Human Owner 终验均未执行。

<details><summary>r10 QA1 返工交付清单（61 项）</summary>

```text
db53dca713fd3f1e2c6844284f6ef56fc93aa11f9ff2ad88e46d6feb4766f501  CODE_INDEX.md
8d0780c83d990c88ac6fa8ba7c40052740ea4dbe1f4fb4d67b4bdf7ee9d8dcb3  backend/alembic/versions/20261117_1200_9d1f3a5c7e20_observation_bundles.py
89d04f96973411baa31b2ec40c7e8335fab80c86dc5ff892b83c153e9d8f6af0  backend/app/equipment_observation/api/routes.py
39798a2a3119d40b1b846bf26d8fd3ab9a624bfb1cb9b8854f1c0b16dd1dffc2  backend/app/equipment_observation/error_codes.py
93cb6b4d5c6a464b06364441c8887aa466885bed75902fc97d1fe5fb77ca51ef  backend/app/equipment_observation/machine_openapi.py
35b037ee43126b2e6bf991c44f327f5b123a6446c4b239986ea62430258079d7  backend/app/equipment_observation/manifest.py
5a69c30586f65364fb57485dd3adabfd00fc178b2168228f8c08f09cc12f6a7d  backend/app/equipment_observation/models/__init__.py
8ae102b30edf13beb3387f779e35c4ed5119b97b9d55d6d5c07c48322b736914  backend/app/equipment_observation/models/records.py
80e5f3cffd54f67736da287e973110d1e3ce8c94cf20fbd8561921f5f8efc89e  backend/app/equipment_observation/profile.py
262612e3364e725a9f821cec719bc8048e987951a1a4c1bd37b7ce60b2e5956e  backend/app/equipment_observation/schemas.py
aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49  backend/app/equipment_observation/services/configuration.py
135dc8f46b5758cd9600ad5e93553c8993c3ab762c5a48a3422e8f8ab4c95ee8  backend/app/equipment_observation/services/energy_reads.py
af5601fdcc89298f71b8adfae07af0465786c7f746fd8ae905653011df09778c  backend/app/equipment_observation/services/energy_statistics.py
60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3  backend/app/equipment_observation/services/guard.py
0ee4c6c94420f29db504f384491b5e54f2d7d7aa6c72cac02e4c288cf411138e  backend/app/equipment_observation/services/ingest.py
cd94cc1ff19975054ed4903666bf2a794b137af312ca199685f1a1b14b773894  backend/app/equipment_observation/services/ingest_v2.py
f3e8ab8c2d5d711f301593cabb68a756d76699f5b22a6e97a65d479673daf6c2  backend/app/equipment_observation/services/reads.py
bd7f081c6791dbf2ee9969c3f0e77ce13aad686d4a4f20a9c71b4e437fbb4b89  backend/app/equipment_observation/services/v2_domain.py
6f92dfb56df56d3ca1d9866a609d0c4bf55cbc74380394a91ba48a89de5d2fe0  backend/app/plc_facts/v2_config.py
39e4cdd218d83475112cddc5780a1fd4a8eba24cfc3ce79b29d5ef3b8a6bce76  backend/common/integration/storage.py
582e34fc026e80291c44e90dae45f9814a5ceb4a9db76369f8a3b5f48af37748  backend/tests/test_energy_price_api.py
a6f24f3b01610bdd3736564148c179ae3a28fd95d165d16d82f5562222ef59e6  backend/tests/test_equipment_observation_domain.py
32ead808cdf317b9b38c32fa45eb35bef66074d0a8d87dbec06e384a2469d855  backend/tests/test_equipment_observation_r10.py
b19452c3fdae3722579cd17628de196732f2e6ed291032a6f99deb0a82751641  backend/tests/test_equipment_observation_r10_flow.py
71d91aa54ae883be9c2e3961fdb89fa5eb6ad4b52d57d7de808fc5422a609444  backend/tests/test_equipment_observation_r8.py
4fdc00cdf51d41f1b87badcf7b9c3af0d5c8e805fb5441022a57c08ed8905123  backend/tests/test_equipment_temperature_migration.py
0393e9346c4d04884d99d77c6c006754894864c7a3d57b2517a4feb5d3e208ae  backend/tests/test_legacy_acquisition_retirement.py
706acd4edfe88e09a0f38dcacda98f0792407e41fed2b7ee30083f225f98f6c2  backend/tests/test_mapping_migration.py
0532f522a69fe2db7e463536617cd0de3af08fc86bbb2775dabd4084b2d2e68f  contracts/README.md
980e5616459dcda55633fd289368e88829a176486e7c88504d481867766b3c23  contracts/README.zh-CN.md
b3379d7181b285680f739bd3b9ebc6ca8ea010a542b546993bd706244a4609bc  contracts/published/http-api/equipment-observation-v2/README.md
e84d4c2afe7e55bf3ddc7005244bfd755f715d7469072508d91da3b5222958d6  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
d11a7c030f7a4401219b2d5160f4d77345df28d42a39e364861144a019252989  contracts/published/http-api/equipment-observation-v2/example-profile.json
cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646  contracts/published/http-api/equipment-observation-v2/openapi.json
870378e53e1becd7c70a5d0b38f062b2e4bf809ff68a8269c34bd5441962d0a7  contracts/published/http-api/equipment-observation-v2/vectors.json
99cf87e523d23b84273a4ff36ed8008054f6a45c0e048161d78a0ce544a1f84b  docs/equipment-status-process-monitoring.md
a90f4ed555f132d0ac40a63debfc59b5927c27f0afc849d247c0da8dfcd70530  docs/equipment-status-process-monitoring.zh-CN.md
ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef  frontend-js/src/app/equipment/api/observations.js
b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688  frontend-js/src/app/equipment/components/observations/RecordList.vue
f89964f9802f9a99339981947864fcb405d2b5a61a68c746a0d979ea63a53341  frontend-js/src/app/equipment/locales/en-US.json
2a374840c98e82d808615502e80fa229d87a88230c30875f3dbd9ea1c4834970  frontend-js/src/app/equipment/locales/zh-CN.json
cd24870f3c2301acae453cf99ba40669414c018974b895b0420333ccdce96dbe  frontend-js/src/app/equipment/manifest.js
dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68  frontend-js/src/app/equipment/views/observations/admin.vue
d819f2b0452b6ec58cbc5b54d51b0e8577e3b5cf80d3f989c4d933a295e889ef  frontend-js/src/app/equipment/views/observations/cards.vue
086e8027db5990bda7d006b8a92bdd865fc1c1f8aea135dfb46631d034de41d0  frontend-js/src/app/equipment/views/observations/data.vue
144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5  frontend-js/src/app/monitor/api/observations.js
c4024622f0b1415cec362d0401abf3b7925e23ea0f5212d1520ce3271726bce5  frontend-js/src/app/monitor/components/observations/CurveChart.vue
19865b25d524b65edcdf155fe2436a7efd921b3c7ef311749e215739d55c64a5  frontend-js/src/app/monitor/components/observations/EmptyAxes.vue
8bbb08b46eb61fed0a282944851ee8c3805aad03bd4fadcff78d4e5e9bf25b37  frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue
a6f659342eea1b29862c75a440a4a21ec8cdeeeb473e4bbfdcaf723fa977f1ee  frontend-js/src/app/monitor/components/observations/curveSeries.js
309cc3912ae14d1d8dbeffb0cb81dd26949a9e995aedd1ceccb240c48f18ffe6  frontend-js/src/app/monitor/locales/en-US.json
dfddf97b60aeb1eb1242b6fa22cf530a93426910f9c43410166b29c504385f10  frontend-js/src/app/monitor/locales/zh-CN.json
e8dfbec2c1537e33d9624cce8fff4c5c0c325b340eb08ec229a1a1f115212dc7  frontend-js/src/app/monitor/manifest.js
3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787  frontend-js/src/app/monitor/views/observations/admin.vue
a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10  frontend-js/src/app/monitor/views/observations/curves.vue
11e3a81d8b0e425e83058fdf65da2eadb809d4239de49c0673846d20a38256ac  frontend-js/src/app/monitor/views/observations/data.vue
8786b58198a8f03de4aeb78b47b7c4def27bd355512cb246d23b960e14e7aa77  frontend-js/src/app/monitor/views/observations/energy.vue
5aa7d0139025d5ce20fb21fd4c58114fdba452183c50f5d722bdbbf6cfdd32f3  frontend-js/tests/module-registry/equipment-observation-columns.test.mjs
f21807090478aff142e6c0679ffc6a32e450ff70077880924d1b64ecc4f0d247  frontend-js/tests/module-registry/equipment-observation.test.mjs
e2918a4a63ebf7f923a7ee8f50399f5c4d110628e1eff0c223b6d424752aee8a  frontend-js/tests/module-registry/page-access.test.mjs
0a3c1ef166eae9dcd0303bc8450b3186962bb7e335ad835fbe6ccb45cc71c5de  frontend-js/tests/module-registry/registry.test.mjs
```
</details>

# r10 Development 实施进展

Human Owner 按 [spec §12.10](spec.md#r10-approval) 精确批准 r10，批准登记后 spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`，并授权指定 dev 的必要保全迁移、配置、合成数据联调及必要的短暂后端重载；须预先核对写入方，只清理本次测试对象。原 r8 `qa_failed` 不改判，未批准的 r9 `mappedPointIds` 不实施。

2026-11-17：建立不含真实 `.env`、profile、密钥和 Git 数据的隔离候选 `/private/tmp/arch-obs-r10-dev.jt9Ah6Pc`；1,050 个源码／文档文件初始摘要清单 SHA-256 `c49c352c0647a9f77c6945d97e0565833ed80b8ea5abdc2dcefc77b81906467d`。先按合同实现并进行无库、编译和离线 SQL 核对；正式整合前须复核并保留并行修改，dev 执行前须复核目标、旧数据、写入方及恢复方案。当前没有经授权的独立 MySQL，不新建 dev schema 或启停 Docker。建立候选时未修改 dev、正式源码或运行服务，尚未形成 developer handoff。

**本轮 MySQL 合成表恢复预演（不是正式迁移）。** 2026-11-17 在用户授权的 `127.0.0.1:3307 / industrial_level_2_system`，执行前重查目标 UUID 的 SHA-256 前缀 `ac2319a3fdc8`、MySQL 8.4、东八区和唯一 8c revision；先核对随机前缀 `o342e344b_` 的所有候选表及约束无冲突。以 `/private/tmp/arch-obs-r10-private.j0jFyKfK/mysql_rehearsal.py --execute-dev-ack ARCH-OBS-001-r10-owned-table-rehearsal` 使用项目 Python，仅将 r8 基线、r10 升级及恢复离线 SQL 的表、索引、约束替换为该前缀，跳过原版的只读 SQL 哨兵和版本表更新；每个语句校验目标与 FK／来源归属，绝不对正式表执行 DDL 或业务写入。离线 r8、r10 升级、r10 恢复 SQL SHA-256 分别为 `16cbe885fc855c2245c2fb78e56b7d9754c30b87e04ef1a4f374c9fedd10ed51`、`13711951634ef5c66b41fb0259b9afbc421c6d2be82539abb6eb03e8411cd7ec`、`9aadddf95821190fc508f1b6f9b90a53e07d7445b903eb5113594b21eaa5a175`。其中两个 r10 离线文件开头均有强制失败的 review-only 哨兵，不能直接用于正式库。

预演成功核对：两条不同时刻、不同备注的旧实时组行完整进入 r8 归档，新实时表为空；一条旧过程行按原 ID、时刻、值、备注和复核标记转为单组新历史；旧回执标识为 v1/r8。加入本次新实时、新历史、能耗和变更后的卡片配置后，原子恢复保留 r8 原行和旧配置，同时将新实时／历史与新配置保存在 r10 保全表、保留能耗行；新旧相同数字 ID 能按版本／表区分。实际仅有该轮 16 张唯一表，执行后检查完整 owned 集合、无外部 FK，再按依赖叶删除，残留 0；14 张原表的行数和 `CHECKSUM TABLE` 均与操作前一致，包括计划、实绩、采集三表、r8 两主表及指标／槽／回执、旧能耗两表和 `energy_prices`、`energy_price_hours`。脚本 SHA-256 `541be6b6d80be1ce5d7d127ec356993471704613aaa1173af78b7edcd36b0e44`，脱敏日志 SHA-256 `ff7eb3aa524e7ead0c851ebac88a91180e79c9d79c74421c1d4e0717428d7680`；临时目录保留供后续核对。该预演没有修改正式表、Alembic revision、真实 profile、原价格或运行服务，也不证明生产迁移、并发或完整页面闭环。源代码仍在实施，尚无新的 developer_handoff。

**原结构恢复的第二次预演。** 迁移调整为把六张 r8 原表原子改名归档，再复制配置到新的 r10 可写表；恢复时保留 r10 表，原子恢复原 r8 表。2026-11-17 13:00 在同一授权目标重查 UUID 摘要、库、8c revision、时区、表名与约束冲突后，以唯一前缀 `o0eb93525_` 重跑完整合成预演：旧数据、新数据及两版配置均保留；六张恢复后的旧表逐项比较列、索引、约束和外键均与原表一致。只删除本轮成功创建且可证明归属的 16 张表，剩余 0；原有 14 张表的行数及校验和保持不变。升级 SQL SHA-256 `8907d0537382e9161968f86f6c958baaa25692afca0dfa86f5c33c3861a3a05a`，恢复 SQL `9aadddf95821190fc508f1b6f9b90a53e07d7445b903eb5113594b21eaa5a175`，脚本 `cb24ae977e339d56d92aae75dc11b44f0863b051c8b63432bde7a37ed1aa174d`，脱敏日志 `4b4e37193f7881b248dff95afab1fcdd84b51b9f1826ca84a1207e0a926f6cb6`；仍为改名合成预演，不等同正式迁移、并发或生产验证。

**候选和切换准备。** 13:00 后隔离候选的 observation 四组无库测试共 41 passed（含 SQLite 合成 HTTP；1 条 SQLite datetime 弃用警告），前端模块测试 69 passed、生产构建成功（Vite 大 chunk 提示）。生产构建与 SQLite 测试不等于正式 MySQL 联调或独立 QA。真实浏览器使用独立合成 SQLite fixture 检查四过程页面、数据列表、真实数据曲线和区域多选，不使用 dev 业务数据；原 5190 仍需在服务恢复后另行复验。机器 v2 合同、双语说明和恢复流程已在候选整理；v1 历史合同保留。

切换前只读复查目标 UUID 摘要 `ac2319a3fdc8`、库、唯一 8c revision、MySQL 8.4.6／+08 与新表无冲突；r8 七表和旧能耗两表均 0，原价格表分别 1 和 3 行，采集事实表分别 73 和 6 行。可见该库 27 个连接、当时无活动 SQL，近五分钟未见采集事实新增，最近事实距检查约 250790 秒；时点观察不证明间歇写入不存在。新 profile 两份及 .env 备份已在仓库外私有目录以 0600 保全，对象比较仅 revision 不同，原 profile 和当前引用未改。精确后端短暂重载由 Human Owner 在 r10 批准原文授权；不停止 5190、DBX 或其他进程。正式树 55 个候选路径与隔离副本基线比较无冲突，实际写入前仍复核。所有数字均为时点记录，正式 DDL 前再次核验。

**授权 dev 实际迁移。** Human Owner 随后确认已停止 SMA 投递，授权仅以第三方或模拟 SMA 的 HTTP 包联调，不使用 SMA 产品。执行前检查 SMA 进程存在，但当前配置中的目标 API 和映射为 0、观察时无 TCP 连接，持久日志长期无投递；本机锁屏，未直接读取其内存运行状态，上述时点观察不声称能预测后续活动。未停止或修改 SMA、DBX 或 5190。受控脚本验证授权目标及精确 Alembic URL、唯一 9d 源码 head、60 文件摘要、旧新 profile、admin 登录、8c 配置 GET、无活动 SQL 与未提交事务，短暂结束 8000 的工作子进程而保留其重载父进程；静默后再次核对事务 0 和业务快照不变，执行 `alembic -x obs_r10_writers_quiesced=yes upgrade 9d1f3a5c7e20`。数据库现为 `9d1f3a5c7e20`：9 张既有保护表行数和 checksum 不变，6 张 r8 原表归档与原表行数及 checksum 一致，3 张新主表开始为空；旧采集事实 73／最新 6，价格数据 1／3 保留。切换 .env 中两个私有 profile 引用到新 revision，其余值逐项不变并保留原文件及 0600 备份，重载 8000 后事实 options 和 admin 区域配置 GET 均为 200。两份切换前后脱敏对账摘要 SHA-256 `a16de1d842bed92cc6e020a58e487974263266f5b269f69fbda6700ec7890026`／`1bb92940d21c956b494e3beb626463b1f350ac0de84096145e52104644fdc069`，Alembic 日志 `948ee7029f6ccf8e922c3120ffc9e737fd8d6500b292f09ed8b72c407d9e930c`；该迁移不证明 SMA／真实 PLC 或生产部署。现正进行仅本轮身份的 HTTP 联调，尚无 developer_handoff。

**dev 合成 HTTP 和浏览器自检。** 使用任务自有回环 API、私有临时 profile 与实际 dev MySQL，认证使用本轮随机机器身份，分别模拟 external 与 SMA 的同合同 HTTP，未运行或改动 SMA 产品。三轮唯一前缀 `500598ebd8fd`、`c69473ade097`、`59383de333fd` 各验证四个设备整包、实时覆盖一行、历史追加四行、禁用历史项跳过、未知组拒绝、相同事件重放、列表动态指标列和卡片／曲线读取；两表计累计 `1006−1000=6`、区间 `2+3=5`。每轮先检查随机键不存在；清理前核对成功创建的配置键、producer／事件／回执行和具体业务行及无外部引用，逐精确 ID 和键逆依赖删除本轮对象。三轮均检查无残留、15 张原有保护表行数与 checksum 不变，任务独有 API／Vite 停止、临时 profile 删除。精确行与配置身份证据文件 SHA-256 分别为 `4e50f452f795d37c5f8ecf7649a7d11b6a0d23eb21698c367b4842e36ffdacfa`、`22814ed69b2018c0111fdc05cdf5f51a11d232c1dd352ca14b2e9cee316141f7`、`de505c8f4bd3fa6a73c8af22b690ff5c0800b31ba7ce5b095fab2c3f37110ef9`，保存在本任务私有临时证据目录；未保留测试令牌。

第二轮独立 Chrome 使用仅允许 GET 的任务专用 UI API，挂载正式 OBS 路由和读取服务、读取真实 dev MySQL，并用合成只读身份；它不代表正式 8000 的用户鉴权或正式 5190 的页面验证。真实温控卡及实时列表显示 810.2／815 和同一任务，过程列表显示四行及缺测 `—`；从菜单进入温度、传动、清洗、能耗，温度图两区域单选／全选及空样本区间→真实数据恢复可操作，能耗最新读数 1006、缺边界显示不完整。暂时暂停并恢复的仅为本任务专属只读 UI API：页面显示“读取失败，请重试”，重试后恢复真实数据。第一次浏览器窗口使用旧标签连续直达时日期／菜单点击未可靠触发；关闭另一任务自有 Vite，重新建立同源登录后的独立直达标签后操作正常，不能确定原故障唯一原因。正式 5190 已由协调者按 Human Owner 另行授权重启，不由本角色操作。

第三轮把同一合成任务采样时间拉开为 `2026-11-17 09:59:43.488128+08:00`（810.2）、`10:59:43.488128+08:00`（缺测）、`11:59:43.488128+08:00`（810.2）、`12:59:43.488128+08:00`（810.2）；所有时刻早于请求时刻。浏览器选 11 月 17 日至 18 日的时间框，实际 Vue/ECharts 图上第一点孤立，跨缺测处没有连线，第三和第四点相连。对应唯一任务的脱敏真实数据库点序列证据 SHA-256 `c3a6cae57af0462eed5fe741b50cb1b5ed48e82453ef37e3196b158544531aea`。截图在实时工具结果中观察到，但本轮未持久化为截图文件；独立 Verification 应在自己的唯一样本下重新观察，不得将无文件截图当持久证据。

### r10 developer_handoff

**交付面。** 交付源码为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 当前 `main` 工作树的未提交变更，非临时源码副本。r10 改动包括来源无关的设备多区域整包、最新快照和过程历史、独立能耗写入与统计、区域／指标／槽位／卡片／曲线配置、三个管理列表及权限、新的显式后继迁移和版本守卫、机器 v2 合同及双语使用说明。已发布 v1 合同、r8 `qa_failed` 和 r9 未批准记录未倒写。下方清单只列本次 60 个实现文件；并行任务的工作树差异不属于本交接，不得覆盖。

**DEV self-check。** 正式树以项目 uv 和锁文件、假 MySQL 端口／虚构设置及唯一 `/private/tmp` basetemp 对 observation、受影响历史迁移和采集 guard、旧能价及 monitor 测试运行 `pytest -q -p no:cacheprovider -m no_db -rs --tb=line`：**317 passed、3 skipped、1 warning**；三项分别是冻结 BE003 测试、采集浏览需隔离 fixture、保留 BE012 B runner。为适配当前 head 与新增能耗路由，保留旧保护并修订 4 个相关断言；首次扩大运行因旧 head／路径断言及默认临时目录不满足旧 runner guard 出现 5 项失败，修订并使用专用 `/private/tmp` basetemp 后重跑上述集合通过。随后补齐实时 OpenAPI 描述，正式树重跑 observation 与 4 项受影响回归 **46 passed、1 warning**，包含三条运行时 POST 正文 schema 与发布 v2 的完整比对及原始 JSON／类型校验。唯一警告为 Python 3.12+ SQLite datetime adapter 弃用提示。正式前端 `pnpm_config_verify_deps_before_run=false pnpm test:modules` **69 passed**；生产构建成功，Vite 提示既有大 chunk；6 份相关 Markdown 150 个本地文件目标均可解析，`git diff --check` 通过，Alembic 唯一 head `9d1f3a5c7e20`。运行中的 8000 OpenAPI 三条机器 POST schema 与公开 v2 一致，采集 options、admin 全局区域配置及两个空管理列表均 HTTP 200。

**实际 dev 与资源。** 目标仅为授权的 `127.0.0.1:3307 / industrial_level_2_system`，当前 revision 为 `9d1f3a5c7e20`。清理核对后三张主表、回执及本次新配置均 0 行；既有采集历史／latest 为 73／6 行，来源登记 3 行，旧能耗两表 0 行，原价格表 1／3 行。启用的持久 OBS 私有 profile 故意保留 0 设备、0 表计、0 producer；管理员能打开全局配置，设备选择和机器写入在用户按项目配置前为空／关闭。facts 与 OBS 目标 profile 在仓库外用户私有 Application Support 的 dev 目录，由 `backend/.env` 两个 profile 引用定位；旧 profile 和 0600 的 .env 备份保留供受控恢复，不将路径内容或凭据提交仓库。独立测试 API、只读 UI API、各自 Vite 和浏览器标签均退出；协调者按用户明确授权重启的正式 5190 继续运行。

**限制及 QA 复核重点。** 重启后 5190 的温度模块、图表组件和 ECharts 变换资源只读 HTTP 均 200，旧缺失优化依赖的 hash 已变化；正式浏览器无可复用已登录 5190 标签，不能证明正式账号登录后的四页动态导入、菜单或权限已恢复。真实 MySQL 浏览器结果来自隔离 Vite／只读合成认证夹具，且断点截图未持久化；独立 Verification 须用实际登录的正式 5190 会话和独立合成样本复核相关页面、权限、曲线及清理，不能把本自检代作 QA verdict。原 MySQL DDL 预演覆盖无损恢复，但隐式提交中断后的处理仍须人工对账，禁止自动 stamp／删除／降级。首次各设备、表计、机器权限、时钟、单位、累计与增量规则由项目管理员配置；真实 SMA/DAA 产品、PLC、现场联调、生产部署与 Human Owner 最终验收均未包含在本交接。

隔离候选 `/private/tmp/arch-obs-r10-dev.jt9Ah6Pc` 与私有证据／恢复记录 `/private/tmp/arch-obs-r10-private.j0jFyKfK` 暂留供 fresh-context Verification 复查；后者含私有备份，文件权限 0600，不得提交或输出内容。待独立核验完成、Human Owner 最终验收且无恢复依赖时由协调者核实归属回收。下列逐文件摘要按 `SHA-256  相对路径\n` 排序后整体 SHA-256 为 `a7a9ba7ca57b121736559c6e9c902a55c3c7f662f1f50d407c08c12e594de279`；60/60 与已验证候选一致。此记录是 Development 自检和交接，不是独立 QA 或最终验收。

<details>
<summary>r10 交付文件与 SHA-256（60 项）</summary>

```text
db53dca713fd3f1e2c6844284f6ef56fc93aa11f9ff2ad88e46d6feb4766f501  CODE_INDEX.md
8d0780c83d990c88ac6fa8ba7c40052740ea4dbe1f4fb4d67b4bdf7ee9d8dcb3  backend/alembic/versions/20261117_1200_9d1f3a5c7e20_observation_bundles.py
89d04f96973411baa31b2ec40c7e8335fab80c86dc5ff892b83c153e9d8f6af0  backend/app/equipment_observation/api/routes.py
39798a2a3119d40b1b846bf26d8fd3ab9a624bfb1cb9b8854f1c0b16dd1dffc2  backend/app/equipment_observation/error_codes.py
93cb6b4d5c6a464b06364441c8887aa466885bed75902fc97d1fe5fb77ca51ef  backend/app/equipment_observation/machine_openapi.py
35b037ee43126b2e6bf991c44f327f5b123a6446c4b239986ea62430258079d7  backend/app/equipment_observation/manifest.py
5a69c30586f65364fb57485dd3adabfd00fc178b2168228f8c08f09cc12f6a7d  backend/app/equipment_observation/models/__init__.py
8ae102b30edf13beb3387f779e35c4ed5119b97b9d55d6d5c07c48322b736914  backend/app/equipment_observation/models/records.py
80e5f3cffd54f67736da287e973110d1e3ce8c94cf20fbd8561921f5f8efc89e  backend/app/equipment_observation/profile.py
262612e3364e725a9f821cec719bc8048e987951a1a4c1bd37b7ce60b2e5956e  backend/app/equipment_observation/schemas.py
aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49  backend/app/equipment_observation/services/configuration.py
135dc8f46b5758cd9600ad5e93553c8993c3ab762c5a48a3422e8f8ab4c95ee8  backend/app/equipment_observation/services/energy_reads.py
af5601fdcc89298f71b8adfae07af0465786c7f746fd8ae905653011df09778c  backend/app/equipment_observation/services/energy_statistics.py
60b870f2eb2fc7dbea43a83a498245e1312d6f3d6402d0aca80ef535c1de4be3  backend/app/equipment_observation/services/guard.py
0ee4c6c94420f29db504f384491b5e54f2d7d7aa6c72cac02e4c288cf411138e  backend/app/equipment_observation/services/ingest.py
b10b6a6529004f319b95c39a00083fd35aedcd6a577a4b4f043e01c76bebae33  backend/app/equipment_observation/services/ingest_v2.py
a76e8e190900e42ec3b5f2d3408b2b47f1577f711b1aba60f10ff6c01182c622  backend/app/equipment_observation/services/reads.py
bd7f081c6791dbf2ee9969c3f0e77ce13aad686d4a4f20a9c71b4e437fbb4b89  backend/app/equipment_observation/services/v2_domain.py
6f92dfb56df56d3ca1d9866a609d0c4bf55cbc74380394a91ba48a89de5d2fe0  backend/app/plc_facts/v2_config.py
39e4cdd218d83475112cddc5780a1fd4a8eba24cfc3ce79b29d5ef3b8a6bce76  backend/common/integration/storage.py
582e34fc026e80291c44e90dae45f9814a5ceb4a9db76369f8a3b5f48af37748  backend/tests/test_energy_price_api.py
a6f24f3b01610bdd3736564148c179ae3a28fd95d165d16d82f5562222ef59e6  backend/tests/test_equipment_observation_domain.py
32ead808cdf317b9b38c32fa45eb35bef66074d0a8d87dbec06e384a2469d855  backend/tests/test_equipment_observation_r10.py
cfcebfbe646c333405a81776787a9504c10f735084f7835080ee2d4907a57f18  backend/tests/test_equipment_observation_r10_flow.py
71d91aa54ae883be9c2e3961fdb89fa5eb6ad4b52d57d7de808fc5422a609444  backend/tests/test_equipment_observation_r8.py
4fdc00cdf51d41f1b87badcf7b9c3af0d5c8e805fb5441022a57c08ed8905123  backend/tests/test_equipment_temperature_migration.py
0393e9346c4d04884d99d77c6c006754894864c7a3d57b2517a4feb5d3e208ae  backend/tests/test_legacy_acquisition_retirement.py
706acd4edfe88e09a0f38dcacda98f0792407e41fed2b7ee30083f225f98f6c2  backend/tests/test_mapping_migration.py
0532f522a69fe2db7e463536617cd0de3af08fc86bbb2775dabd4084b2d2e68f  contracts/README.md
980e5616459dcda55633fd289368e88829a176486e7c88504d481867766b3c23  contracts/README.zh-CN.md
67fd745096bb59946e6dc04eabf62d7110403f71deefced35db883ff8739ce30  contracts/published/http-api/equipment-observation-v2/README.md
a47daac5b9ec3b08d3e694e14838737005ed1a1e35513a571385ddcfd32c5144  contracts/published/http-api/equipment-observation-v2/README.zh-CN.md
d11a7c030f7a4401219b2d5160f4d77345df28d42a39e364861144a019252989  contracts/published/http-api/equipment-observation-v2/example-profile.json
cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646  contracts/published/http-api/equipment-observation-v2/openapi.json
870378e53e1becd7c70a5d0b38f062b2e4bf809ff68a8269c34bd5441962d0a7  contracts/published/http-api/equipment-observation-v2/vectors.json
47a222755710b3132b4137671af881db4cac997586c0eb3a7c8a9a60f0edcb11  docs/equipment-status-process-monitoring.md
543fa475102bfbc767bef8e658e59bfd631f67fb876ed5d032aa21c30ef9f9d4  docs/equipment-status-process-monitoring.zh-CN.md
ca56e4c8b672d05067c1394d9a832b9beed201ad04477b2c6735989205b661ef  frontend-js/src/app/equipment/api/observations.js
b2ac30ca6e7779ad16b8e5825ad150438e9d219678fa574d655dc706269ec688  frontend-js/src/app/equipment/components/observations/RecordList.vue
f89964f9802f9a99339981947864fcb405d2b5a61a68c746a0d979ea63a53341  frontend-js/src/app/equipment/locales/en-US.json
2a374840c98e82d808615502e80fa229d87a88230c30875f3dbd9ea1c4834970  frontend-js/src/app/equipment/locales/zh-CN.json
cd24870f3c2301acae453cf99ba40669414c018974b895b0420333ccdce96dbe  frontend-js/src/app/equipment/manifest.js
dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68  frontend-js/src/app/equipment/views/observations/admin.vue
d819f2b0452b6ec58cbc5b54d51b0e8577e3b5cf80d3f989c4d933a295e889ef  frontend-js/src/app/equipment/views/observations/cards.vue
086e8027db5990bda7d006b8a92bdd865fc1c1f8aea135dfb46631d034de41d0  frontend-js/src/app/equipment/views/observations/data.vue
144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5  frontend-js/src/app/monitor/api/observations.js
b082a1621082eeac8c2f4e2ef1c67611faff02590a3a5f4ee8255d80a48e3444  frontend-js/src/app/monitor/components/observations/CurveChart.vue
19865b25d524b65edcdf155fe2436a7efd921b3c7ef311749e215739d55c64a5  frontend-js/src/app/monitor/components/observations/EmptyAxes.vue
635c62812af6eb6b55938c9e03e6fa57217ce5eab097eb31ed9badee40a8fde8  frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue
6d950f4dfffd8fcd802b4c0d56a620149ba7c0445ec62ccec68ea7f06d463ff6  frontend-js/src/app/monitor/components/observations/curveSeries.js
d52f635dbe29d2be0b513e11e1905ac38e37cf51ebcd0a658f3dbc42db9b65e3  frontend-js/src/app/monitor/locales/en-US.json
5a7b13158220f97b33b7faa8715a4030be74881d1b369df9d5c8cc7b5432e689  frontend-js/src/app/monitor/locales/zh-CN.json
e8dfbec2c1537e33d9624cce8fff4c5c0c325b340eb08ec229a1a1f115212dc7  frontend-js/src/app/monitor/manifest.js
3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787  frontend-js/src/app/monitor/views/observations/admin.vue
a202167be58e577d4076273f1e98e1e9051b553469ac1afb4b0f8f90cfb1fd10  frontend-js/src/app/monitor/views/observations/curves.vue
11e3a81d8b0e425e83058fdf65da2eadb809d4239de49c0673846d20a38256ac  frontend-js/src/app/monitor/views/observations/data.vue
8786b58198a8f03de4aeb78b47b7c4def27bd355512cb246d23b960e14e7aa77  frontend-js/src/app/monitor/views/observations/energy.vue
787478e1fe28e183dcbc668c09bc0c6e4682c1e808f431a11e1f6dd957d72769  frontend-js/tests/module-registry/equipment-observation.test.mjs
e2918a4a63ebf7f923a7ee8f50399f5c4d110628e1eff0c223b6d424752aee8a  frontend-js/tests/module-registry/page-access.test.mjs
0a3c1ef166eae9dcd0303bc8450b3186962bb7e335ad835fbe6ccb45cc71c5de  frontend-js/tests/module-registry/registry.test.mjs
```
</details>

**5190 页面加载故障定位，尚未恢复。** 2026-11-17 约 12:53（上海时间），在独立临时 Chrome 标签只读复现正式 `http://127.0.0.1:5190/monitor/temperature` 白屏并记录浏览器实际脚本资源：`/node_modules/.vite/deps/chunk-QDYHHCQC.js?v=e9194e38`、`chunk-SU6QCEEU`、`chunk-NUTLW766`、`chunk-2NUMRAKG`、`chunk-ABXUQGM4`、`chunk-MTEXU75C`（后五者同目录、同 `?v=e9194e38`）均经只读 HTTP 确认为 **404**，而页面和部分 ECharts 顶层依赖为 200；这解释了为什么只看入口状态无法发现图表依赖缺失。正式工作树 `frontend-js/node_modules/.vite/deps/_metadata.json` 当时 `browserHash=a876c393`，与运行页面依赖请求的 `e9194e38` 不一致，表明现有 Vite 运行态与磁盘优化依赖产物不一致；尚未证明哪个操作造成此状态，不把可能原因写成定论。临时标签已关闭，未删除缓存、刷新原用户标签或停止 5190。隔离候选使用独立依赖缓存可以在真实 Chrome 进入温度、传动、清洗和新能耗页面，这不能代替正式 5190 的恢复与复验。

约 12:56 另开自有 5190 临时标签尝试浏览器强制刷新，白屏与同一批缺失依赖仍存在；不把普通／强制刷新当作已验证的恢复办法，未触碰用户原有标签。现有监听为用户 Vite/node，可能需协调其优化缓存及服务所有权，任何恢复步骤须先说明短时影响并遵守额外授权边界。

# R8-QA-001 返工进展

独立 Verification 以 SHA-256 `d5eb209ce0ea43e66e24aeae7ceaa58d035f633955e230e8da4ccd432bbac1f1` 的 checklist 记录 `qa_failed`，两条真实 SMA 写入仅引用任务点但提交其他指标时返回 `stored`；返工前的 r8 developer handoff 为本文件原 SHA-256 `51e5fafad2769d8baf6959c0cceebf7e922d67d0c68e21064de99f9c1e7b4f9f`，下方完整保留其实施及证据记录。获批 spec 仍为 SHA-256 `bedca6d06769879bed608376a3e0b88a3c6bc071d999afe42aae1bd96cd30cb8`。

当前信封没有声明引用的用途，也没有可供后端信赖的指标到 PLC 点映射：任务点既供任务归属也供指标使用，与漏报指标来源的请求，在请求和已存采样相同时不能区分。强制两个不同点会拒绝可共用的点；按上报值与任务值是否相等猜测来源也不能证明映射，并可能误拒已讨论的换算或常量。该语义已报协调者，PM 正评估修订、由 Human Owner 决定；本阶段未对正式源码、数据库或运行服务做新的修改，不声明缺陷已修复。任何标记只能表达发送方声明，不能凭标记证明实际映射执行。

不依赖最终选择的准备：在 `/private/tmp/arch-obs-r8-dev.F157ayJv/backend/tests/test_equipment_observation_r8.py` 暂存双目标 SMA 已保存回执重放及同事件不同内容冲突测试（SHA-256 `cb7fcf477f5b7ea2dfc93bce606a669823545083fa180946517c88c205845c8c`）。用项目 uv 和既有虚拟环境、仅虚构设置与不可连接的 MySQL 假端口 `9`，运行 `pytest -q -p no:cacheprovider -m no_db tests/test_equipment_observation_r8.py`：**12 passed**；首次直接运行因隔离副本没有 `.env`、应用设置缺失而未启动，补齐虚构设置后重跑通过。该测试未访问 dev。 `/private/tmp/arch-obs-r8-private.ZQFVM8IQ/dev_rework_probe.py`（SHA-256 `1570cf415ceb3cd0915d0a7e20446e5122749e067c99e6e7700c9095b21cdadd`）准备了后续两目标缺失引用的 HTTP、业务行与回执前后对账，并保留按唯一身份清理逻辑；目前仅通过语法检查，**尚未运行或写入 dev**。新方案定稿后须调整候选及该脚本，再执行受权范围内的定向回归、清理与全新交接。

# r8 Development 实施记录

Human Owner 批准 [r8 §10](spec.md#r8-approval)，批准后规格 SHA-256 为 `bedca6d06769879bed608376a3e0b88a3c6bc071d999afe42aae1bd96cd30cb8`，并授权对指定 dev 目标迁移、必要配置及合成联调，只清理本次测试数据。Human Owner 随后明确允许本次短暂重载现有 127.0.0.1:8000 后端；不包括停止其他进程或写入者。实施与独立 QA、Human Owner 最终验收分别记录。

1. 在独立候选中适配 r7、当前采集来源登记、单一迁移后继和配置化指标列，先执行无库、构建及离线 SQL 自检。
2. 核对正式树并行改动、前驱目标、已有进程和有效 profile，整合候选并验证旧目标仍可用；按获批目标执行前向迁移和必要配置，复核 guard 及既有数据。
3. 使用本轮唯一来源和身份完成合成双路/页面核对，记录精确对象并仅清理本轮数据；在正式树记录实际命令、结果和限制后交 fresh-context Verification。

## r8 实施与 DEV 自检

正式交付目录为仓库 `main` 工作树。先以 r7 QA3 候选和当前采集源码建立 `/private/tmp/arch-obs-r8-dev.F157ayJv`；未复制真实 `.env` 或私有 profile。独立候选适配来源登记、单双 revision guard、两张新主表和七表迁移、列表列配置；对原有可受影响测试按实际版本／路由更新断言。按获批 8000 短暂重载范围整合到正式树，整合前本次 62 个路径无并行未提交差异，逐文件比较与候选一致。

**dev 执行。** 迁移前只读确认目标 `127.0.0.1:3307 / industrial_level_2_system`、MySQL 8.4.6、`+08:00`、server UUID 的 SHA-256 前缀 `ac2319a3fdc8`、唯一 revision `7b9d1f3a5c7e`、七张新表无碰撞；应用账号对目标有 `ALL PRIVILEGES`。最近 30 秒无新采集事实仅是当时观察，未停止其他写入者。旧目标与旧 profile 在新版源码下的 `/api/v1/acquisition-data/options` 实测 HTTP 200。使用正式树的 `uv run --offline --frozen --no-sync alembic upgrade 8c0e2a4d6f18`，退出 0；迁移日志 SHA-256 `34241ee2e766cbbb77714e3462fe4496ea2ad3aafdfa777eb07af16d66e6dede`。执行后唯一 revision 为 `8c0e2a4d6f18`，表数由 57 增至 64，七张目标表及列表字段存在；原计划、实绩、采集历史、采集 latest、来源登记五表行数及 `CHECKSUM TABLE` 值一致，所有原表索引的结构摘要一致。

保留原私有 facts profile，新增目标相同、revision 为 8c 的 `plc-facts-target-8c0e2a4d6f18.json`（SHA-256 `a020d914afe4b54197736b8d2fd64465701b67c2f7ca8da9552694786fece29b`）；另新增 `observation-target-8c0e2a4d6f18.json`（SHA-256 `2dae4a626a6f97c584784fa9aa45f7244e55e3ec04e8312f5c33402cf3c5e83d`），设备和 producer 均为空，机器准入默认关闭。两文件位于用户私有 Application Support/aiis-ics-arch/dev 目录、均为 0600，精确路径由本机 `backend/.env` 的对应键确定；未把凭据或私有 profile 放进仓库。`.env` 只切换 `PLC_FACTS_V2_PROFILE_FILE` 并添加 `OBSERVATION_ENABLED`、`OBSERVATION_PROFILE_FILE`，其余解析后的键值逐项不变。旧 `.env` 备份在 `/private/tmp/arch-obs-r8-private.ZQFVM8IQ/backend-env-before`，0600；需保留至最终验收及不再需要恢复时，禁止纳入仓库。触发获准的 8000 热重载后，采集 options、admin 登录、空设备选项、全局指标配置及两个空管理列表均 HTTP 200；无机器凭据发现指标返回 401。原 5190 服务未停止，三个入口只读检查返回 HTML 200。

**合成 MySQL/HTTP 闭环。** 在相同 dev 库使用任务独有的设备、PLC、实例、代次、任务、指标和 producer，通过独立临时 API 及 profile 执行真实 HTTP。第三方最简请求及合成 SMA 全信封各自调用发现及两条 POST；实际核对回执、两目标槽位、同槽不同组、`0`、`false`、空字符串、整组覆盖后缺测、备注和复核、停写历史指标可见、卡片／曲线和相同事件重放。经 admin API 删除本轮来源后，当前任务变 unknown，原始事实和过程历史仍存在，已提交回执仍可重放；随后才按精确实例、代次、样本、记录、producer、槽位及配置键删除本轮自有对象，未按整表或共享设备清理。最终轮产生实时 2 条、历史 2 条、回执 6 条；四轮 `14d64f82c178`、`0980335c0cf3`、`406da997da79`、`da3959a89411` 按唯一身份逐表复核零残留。收尾时原五表行数及校验和和原索引摘要仍匹配迁移前，脱敏对账 `/private/tmp/arch-obs-r8-private.ZQFVM8IQ/dev-after-cleanup.json` SHA-256 `7de99ad6487966c04909d052bfdbbd3fef381a7cd278c3bd1a3f9820c4ddf89b`。

**实际浏览器自检。** 独立临时 API、两个仅回环 Vite 和 Chrome 157.0.8103.78，使用已有 admin 登录，未创建用户或更改权限。实际在中文页面选择实时两列、检查值；历史列可见；拖拽动态列宽、页面重载恢复与重置；温控卡和温度曲线画布、中英文切换；连接真实 8000 的空设备 profile 时 admin 仍能打开配置及空列表；无 pageerror。首轮因脚本定位隐藏表、第二轮因未等弹窗关闭动画而超时，均已按各自精确身份清理，修正测试脚本后第三轮通过；不把前两轮写成产品成功。截图保留给 QA：`/private/tmp/arch-obs-r8-private.ZQFVM8IQ/ui-da3959a89411-{latest-zh,history-zh,card-zh,curve-en,empty-admin}.png`，对应 SHA-256 顺序为 `d2c4928aa4612ca8c94ba367a6031dc12e392dec4d56683cf8d08251125a07a9`、`55c7f30523689b48d8e5a24f2eceb4b137d8a7212bd76c1a75e7e1565ba185be`、`da54df8a199678f77e6191df780a37e25a9b6f7d712e51ec50eeef4b6877e4f9`、`2535c3e600d9923583bc300b09a7ae372fbd35494ffabdaab60b21b873c45467`、`482454c523342fdf6d6ab5c792209d4df92596fbee38809a1fb9ec3edeecef07`。所有独立测试 API／Vite／Chrome 已停止；未操作其他进程。

| 检查 | 结果 |
| --- | --- |
| 正式树 `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs`，覆盖 `test_equipment_observation_{domain,r8}.py`、business integration migration、equipment temperature migration、legacy acquisition retirement、mapping migration、acquisition source/browse、plc facts v2 | 退出 0，160 passed、3 skipped。跳过项分别是 BE003 冻结候选测试、需独立任务 fixture 的采集浏览测试、BE012 保留前驱 runner；不称全部测试通过。 |
| 正式树 `pnpm test:modules` | 退出 0，67 passed；包含实际列表 SFC 设置与列宽和先前四项旧路由／权限断言。 |
| 正式树 `pnpm build --outDir /private/tmp/arch-obs-r8-dev.F157ayJv/formal-frontend-dist` | 退出 0，模块预检通过；保留 Vite 大 chunk 和外部 outDir 提示。 |
| 正式树对应 Python `compileall`、`git diff --check`、39 个新增文件 no-index whitespace 检查 | 退出 0。 |
| Alembic 唯一 head、`7b9d1f3a5c7e:8c0e2a4d6f18 --sql` | 退出 0；离线 SQL 仅创建七表／索引并更新版本，SHA-256 `16cbe885fc855c2245c2fb78e56b7d9754c30b87e04ef1a4f374c9fedd10ed51`。 |
| 三条机器 OpenAPI 路径与已发布 schema 对照；双语 JSON 对称；八份相关文档本地链接和锚点 | 退出 0；三路径一致，7 个 JSON 解析，134 个文件目标及 84 个片段均解析。 |
| 正式前端 5190、后端 8000 只读探针 | 运行中；采集 GET、admin 空 profile 和入口均成功，无凭据机器查询 401。 |

### 限制和 Verification 提示

本次是 Development 自检，不是独立 QA 或 Human Owner 最终验收。当前持久 OBS profile 故意没有设备和机器身份，管理员可配置全局指标，但真实卡片、曲线和写入要先按[手动验收说明](../../docs/equipment-status-process-monitoring.zh-CN.md#r8-manual-acceptance)配置实际或用户自己的独有测试设备/点位/producer；不要猜测真实 PLC。typed 业务接入当前关闭，未在 dev 实际以已采用 typed profile 写入；旧／新 guard 的错配和跨设备过滤已做无库测试，实际并发的来源切换／删除锁、A/B 迟到换单、多设备越权和所有卡片／曲线类别仍需独立 Verification 覆盖或如实说明。r7 隔离 MySQL runner 未指向本次真实 dev，未宣称该 runner 通过。未运行 SMA 或 DAA 产品、真实 PLC、生产部署或发布。

候选、截图、离线 SQL 和私有备份暂留 `/private/tmp/arch-obs-r8-dev.F157ayJv`、`/private/tmp/arch-obs-r8-private.ZQFVM8IQ` 供独立 QA 复核；包含敏感备份的目录及文件为私有权限，不输出或提交。待 Human Owner 最终验收且无证据／恢复依赖后由协调者核对归属回收；用户的两份持久 profile 和运行服务不属于临时清理对象。`/private/tmp/arch-obs-r8-pytest.ezwMJhRJ` 仅含本轮临时测试数据、无 QA 依赖，已回收。QA 请从正式树、获批 spec、下方 62 文件 SHA、真实 dev 目标及脱敏记录独立核验；不得把自检替代 QA verdict。

### 精确交付文件与 SHA-256

对下列按路径排序的 `SHA-256  相对路径\n` 文本再取 SHA-256，得到 `a501d2e221bbe64cdc8003c6c5eed31395b3393eaada570901ecb201a8210ece`；62/62 与候选相同。本清单仅列本次实现文件，不含 spec、角色记录和其他任务差异。

| 路径 | SHA-256 |
| --- | --- |
| `CODE_INDEX.md` | `f4477144739ec0eee571dfe0e0b19fded854ca4455bd09c505a14bd639ffd9a3` |
| `backend/alembic/versions/20261116_1800_8c0e2a4d6f18_add_equipment_observation.py` | `33fea415320944712c92898f82f11430a6b90b428978c307d23d2990b385cb14` |
| `backend/app/equipment_observation/README.md` | `1afc33de2d9186c740e66babf3142c5d07814e8d9bba5f7acef0d7d053db992e` |
| `backend/app/equipment_observation/README.zh-CN.md` | `c1df213dfd3976ff7d5d5254e618f6ef47277125a1339f691abcf09911e226fb` |
| `backend/app/equipment_observation/__init__.py` | `56fc319faab27f00444050a7f4cede5bfd82c40a776223482a9d0b6cb9b92130` |
| `backend/app/equipment_observation/api/__init__.py` | `77a668728ad2886630462f40fe5920f121ce342aaba26c2cc2934040570df252` |
| `backend/app/equipment_observation/api/routes.py` | `74a5de11d0004779b524dfc2100ce51189576cf95aa15087eec0cec77ead2373` |
| `backend/app/equipment_observation/domain.py` | `17a61fb2175db447a0fd31f6050a4a86a0585982d128fbc80017db54e4faa0bc` |
| `backend/app/equipment_observation/error_codes.py` | `662d6e34cdfd9c5df8fe39fa27408e591033b3e600dceee2058195806c130fd3` |
| `backend/app/equipment_observation/manifest.py` | `592adc32634ec1edce508deca9ccba6004cdef6bb64a5848ea9a548c09abe4c3` |
| `backend/app/equipment_observation/models/__init__.py` | `8a49f24867d27ae803823dc6d6f2253404437439bcbbfaff253b6797186b3c73` |
| `backend/app/equipment_observation/models/records.py` | `2353a65857297c3b30d35b17cfcb65e098ce5ee6af8ed5d34b0697949e88e914` |
| `backend/app/equipment_observation/profile.py` | `d3d283eef7527250838bc4dd351d0ddab2510e0eb609759d3ed689819646470f` |
| `backend/app/equipment_observation/schemas.py` | `5a6a990716d593890f2184d646278aefee899755df67e6d6bd5244c229195c90` |
| `backend/app/equipment_observation/services/__init__.py` | `877cf89acf402aedd0374737b6e5c80c355d914974d8e84c15b5409eb9da12de` |
| `backend/app/equipment_observation/services/configuration.py` | `1ddd94f3a0d8baf47057ee450eac45b5e28d6af3f32ce35833d933d04e3ced9d` |
| `backend/app/equipment_observation/services/ingest.py` | `2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34` |
| `backend/app/equipment_observation/services/reads.py` | `85fa8b78e1ee4b82001badf0c1e1af8e2e050eeaf577e90be7c15cb744e6f932` |
| `backend/app/plc_facts/README.md` | `25d3a11aef2c9abdddf2580d16de76f93cf83ed91c9acb4c3a007cd28ba55dcd` |
| `backend/app/plc_facts/README.zh-CN.md` | `940afbddb492d73619fa088b96e7ec28fc7a4cc05d55001e24f6c9ed7611ef7b` |
| `backend/app/plc_facts/crud/async_v2.py` | `5656ced4b98a154e7e16c1c0ece4a5e23fedd6ea53a70a9425157b0994ee4017` |
| `backend/app/plc_facts/crud/sync_v2_maintenance.py` | `ba26d3b21f3cce238d88c9aea961e410e4064928f4084888594170fa51aa12f9` |
| `backend/app/plc_facts/manifest.py` | `566856dddc489e306c339a12dcc0b5f17880c4479fae4998f5fcf84514514dc2` |
| `backend/app/plc_facts/services/observation_evidence.py` | `d8db96c3ed1004620b29c764b1346aad7ed2d350fc5bd1617d75445a1b084ad7` |
| `backend/app/plc_facts/v2_config.py` | `7052e20cb811c8a1b9763a9b020cd48ca09f4bee75aa97b7808ebc8b41357435` |
| `backend/common/integration/storage.py` | `353fbe6beff6a3a9f22331248ce0187b319908283a34c3556dd1a4d6ad957969` |
| `backend/tests/test_equipment_observation_domain.py` | `6cf8b6de25ef7bcb941216a6feeebc67f4e0408373825030f21108393f4a062a` |
| `backend/tests/test_equipment_observation_r8.py` | `d65e229cc80032773257b9ce5a60c7a5496f095fd9b9466b55514a4a7e21249f` |
| `backend/tests/test_equipment_temperature_migration.py` | `77647193275d39d990c314169688daec603ac386c420e66599929ebdd68bf1f4` |
| `backend/tests/test_legacy_acquisition_retirement.py` | `3d91dcd0ee951c2f70ff02215dd028391d5f6aaa1e26e09a7295b27943c1456f` |
| `backend/tests/test_mapping_migration.py` | `62ba395430dca3c83c0682344177ea9c8856cd0db4cf8b3c1eba184378646b88` |
| `backend/tests_mysql/test_equipment_observation_mysql.py` | `b8637aa7e67e37837deab15eecd606e6ab8c22e9e20687d1ff7160785b39242f` |
| `contracts/README.md` | `34f3b8ba6ffbe3f730dd3d8762c8b18f7f8b80c042323197e77e47d7f96351fb` |
| `contracts/README.zh-CN.md` | `ba08e026ba6f058faef755a67271c3e83021b67b3777e4be769d68c26fbbbd88` |
| `contracts/published/http-api/equipment-observation-v1/README.md` | `9f1ff72d3b598eaac1f989272f45f5e8010114c5ffef56b31cefe86d57e8a694` |
| `contracts/published/http-api/equipment-observation-v1/README.zh-CN.md` | `568de3dc8ba14f5380bd9ba43dd14191e67d277e52e08d57d593115a6b9e7989` |
| `contracts/published/http-api/equipment-observation-v1/example-profile.json` | `c07d02096fa2f8f0afc4a0826a5c6323aa8ed93b6fcd16686c36147f6c711f70` |
| `contracts/published/http-api/equipment-observation-v1/openapi.json` | `7a5bd636a75208dbaf65531bff9d72e9dae8d81765d73f2ae10631e745849c07` |
| `contracts/published/http-api/equipment-observation-v1/vectors.json` | `dd904d37d2a787c04afe14f13331c08b44ab54cb72708a37206be8be05456ed8` |
| `contracts/published/http-api/equipment-observation-v1/walkthrough.py` | `709dd9200f2df1e4294ff0ea83c5d7b8a9647d1304c0bf98788fad70ece8ce91` |
| `docs/equipment-status-process-monitoring.md` | `72e880398d6dc3ed366771048e57d8e5b0eca8c9629381481b8724ddcbd358ce` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `960c18c5012e95cd29368641e27363d3472bf0681360a904aa6ef5038f389bfa` |
| `frontend-js/src/app/equipment/api/observations.js` | `2de0a077040bcf684d0bc9f8163b73c1ad3cf19e1ae7ad33929f6feb1d1b5db5` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `b77b13a956cb17ee2d798fc1ccc0edf199288446238c78e242b048fd7234acbb` |
| `frontend-js/src/app/equipment/components/observations/columnModel.js` | `bcb9c4f4b433db6da0acdcb0f24d6dacafddbbf02930032c69679ecf94626cba` |
| `frontend-js/src/app/equipment/locales/en-US.json` | `dd26abd0948bc655f95883e58f42bb9324af266ff77b441f078576505c2865f0` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | `305702a1dd7a03f76fbdd7fbc3ef499f716b2119cf41b5c74c67afc96e3225ce` |
| `frontend-js/src/app/equipment/manifest.js` | `8ccc0f244d154ec0f9216142736b940daa630ff4cc722db426639d876faab96e` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `aa1d0f887281b60ff5d0517f216a9264a1ebc0d321466b1965f81c724392e591` |
| `frontend-js/src/app/equipment/views/observations/cards.vue` | `0f0f9330cae3d1c97fb941a36fc4886108a0d5ed2b9fef8a91e220f45506bcd9` |
| `frontend-js/src/app/monitor/api/observations.js` | `6d3ee0a8ad807f5c292e1857253b0d8d7ff6e19d173c540de2427792bfa4887d` |
| `frontend-js/src/app/monitor/components/observations/CurveChart.vue` | `167c0e55ca1d0135a90c2214d6498a52353cfa5d8643ddc68289d89e9bf215cb` |
| `frontend-js/src/app/monitor/components/observations/curveSeries.js` | `b092e99b878609f8cb107dd50922972cadd239ee3c4a13195948c5e8b2162d7d` |
| `frontend-js/src/app/monitor/locales/en-US.json` | `e8aec65ac4314240d233e5a0e263c73bad8d6f47dc33b8f1845f20f712e26534` |
| `frontend-js/src/app/monitor/locales/zh-CN.json` | `7fdabe4b01e7fc6d0e124307174e7283bb0dbf00335668da3180ac06c5f8a80b` |
| `frontend-js/src/app/monitor/manifest.js` | `fe604032a2ab8a81c6dfd20d8bc5d620fc631d502254a2a4e285526e81db9d85` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | `60494af0dc8ad6f7622d3db441e4db48045b2f399443759bbd7042769917e4b0` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | `b852627a9ca29de568a363ce7527a654c4bb0d9ce951f32f425e5592ad34ee34` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | `dcb8610373649c117d0f80842d068cfdcfcff303a0d3a9bc94c074a579b47d51` |
| `frontend-js/tests/module-registry/equipment-observation.test.mjs` | `eb957cb55b10596b0e0c896b26705a7db4ef0282d166394fb391062ea00b0bc5` |
| `frontend-js/tests/module-registry/page-access.test.mjs` | `8856ca5bf916bcca6dce9d0103fde81145d4d52bf3c8dfbfa1654e6a5f436501` |
| `frontend-js/tests/module-registry/registry.test.mjs` | `b88230eb4b0dab888d453604b1fb15bd3bd9cd0e60fef1e944154a531b75f02c` |

<details>
<summary>r7 及更早 Development 原记录</summary>

<!-- ARCH-OBS-001-r7-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r7 isolated source candidate to fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

以下 r6 D-06 及更早 Development 记录作为完整历史原字节保存。r7 交接正文保持原文，其中“前 23232 字节”的恢复说明对应本次修正前的文件布局；现在应提取以下两个 history 标记之间的全部字节，再按原 SHA-256 核对。此更正仅调整任务文档的顶层元数据和历史封装。

<details>
<summary>r6 D-06 及更早完整 Development 历史（23232 字节）</summary>

<!-- ARCH-OBS-001-r6-history-begin -->
Task ID: ARCH-OBS-001
Revision: r6
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: D-06 working-tree candidate to fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# D-06 第三方与 SMA 接入说明

2026-11-11（Asia/Shanghai）。按 [r6 §7.4 D-06 文档范围](spec.md#r6-d-06-第三方与-sma-接入说明)对读并更新中英文讨论稿。软件方案仍处于 `draft`。

## D-06 实施与 DEV 自检

两稿补充第三方每次必传的来源事件、采样时任务号、原采集时间及指标值，区分后端从接入配置补齐的字段、固定设备组的省略条件、实时和历史质量规则、显式 `null` 与缺测指标，以及来源事件和目标投递事件在重试时的不同作用。两稿说明 SMA 固定配置需由程序每次发送完整信封，GET 需要的集成身份和精确设备／组／目标准入、历史白名单及其与业务读权限的区别，并各自链接规格的字段规则、发现示例和两份第三方最简 JSON。

| 检查或命令 | 实际结果 |
| --- | --- |
| 内联 `python3` 对照 r6 规格与中英文稿，检查本地链接、标题与显式锚点、字段标识、原链接与 Mermaid | 退出 0。两稿各 39 个链接，合计 78 个本地链接解析成功；两个原 Mermaid 源码、原阅读锚点和所有原链接保留。两稿各自链接第三方字段规则、实时与历史最简示例、GET 示例。 |
| 内联 `python3` 解析规格 JSON 并检查两份第三方示例 | 退出 0。11 段 JSON 均可解析，原 9 段逐字节保留；两份新例的来源事件、任务号、原采集时间和指标一致，历史显式带 `quality: good`，实时省略质量。 |
| `git diff --no-index --check -- <编辑前讨论稿> <当前讨论稿>`（两稿各执行一次） | 两次均退出 1，表示存在内容差异；输出为空，未发现空白错误。 |
| `shasum -a 256`、内联 `python3` 字节比对 | 退出 0。规格摘要与 PM 交接一致，原 `checklist.md` 与编辑前字节一致。 |
| 内联 `python3` 移除本节并还原旧交接元数据 | 退出 0。恢复的 `tasks.md` 与 D-05 编辑前副本逐字节相同，旧交接及更早记录保留。 |
| `git diff --no-index --check -- <编辑前 tasks> <当前 tasks>` | 退出 1，表示存在内容差异；输出为空，未发现空白错误。 |

## D-06 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。本轮 Development 修改双语讨论稿和本记录，候选为当前工作树，规格为 PM 所有。下表摘要通过 `shasum -a 256` 核对。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `ea288e72715f4e29f6ec0f30431954935f23e3b1990538fc5624aa6eae32f25a` |
| `docs/equipment-status-process-monitoring.md` | `ac7970c856038a9cc289a167da714ca287d92c93ebeb5c5a0d951553185ac799` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `0b005b6b1077187438518830c4d4fea44eb5a8df3d8ace0c4dda6fcd807ec194` |

由主协调会话启动 fresh-context Verification。DEV 检查仅覆盖静态文档、JSON 和链接，未运行渲染、API、数据库或现场验证。本任务未修改代码或执行外部操作。既有通用任务讨论稿是本地链接依赖；协调者管理 `/private/tmp/aiis-arch-obs-001-r6-d06-yemwinwu` 编辑前对照，留给独立核验，核验后按其资源生命周期处理，Development 未另建临时资源。

## 历史 Development 记录（r6 D-05 及更早修订）

# D-05 完整方案审阅稿

2026-11-09（Asia/Shanghai）。交接范围为 [r6 §7.4 D-05 文档授权](spec.md#r6-d-05-完整方案审阅稿)。软件设计仍处于 `draft`。

## 实施与 DEV 自检（D-05）

按 D05-AC01 至 D05-AC04 对读双语稿与规格。两稿说明共用指标登记、两张值表的固定列、每目标每组的槽位和类型保留、卷号字符串、按任务查询历史及发现、写入、读取和管理接口。炉区 1 同源样本串起 `01/02/03` 与 `07/08` 的落库差异，表定义和完整请求与响应由规格维护。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 核对相对路径、标题、显式锚点、两稿的规格引用、页面预设及 `json.loads` 落库片段 | 退出 0。每稿 33 个链接，6 个旧阅读锚点和 2 个新锚点，4 页卡片、3 页历史预设和 6 条 Mermaid 连线。两路槽位及原类型值对应。 |
| 内联 `python3` 核对规格授权段及 `json.loads` | 退出 0。D-01 至 D-04 历史授权和验收正文匹配 r5 基线。9 段 JSON 可解析，发现结果、任务和卷号 `000042`、两路事件、同源任务与采集时间及字符串回执记录号通过比对。 |
| `git diff --binary HEAD -- . <文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` 比对协调者基线摘要 | 退出 0。六份索引、checklist、范围外跟踪差异和 6 个既有未跟踪文件匹配基线。 |
| `git diff --no-index --check -- "$before" "$after"`（双语指南和本记录）、`git diff --cached --quiet` | 空白检查均退出 1，表示有内容差异，输出为空。暂存区检查退出 0。 |
| 内联 `python3` 恢复下方 r5 元数据并比较原 `tasks.md` | 退出 0。旧正文及历史交接标题逐字节保留。去除 r5 元数据的引用前缀后，恢复摘要为 `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7`。 |

## D-05 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。交接对象为工作树的双语稿和本记录，按 `shasum -a 256` 核对以下规格及指南。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `b7ffda29b0ecb1631998ecff7611e54a76e5f88dcfcd0b2e368d23e7a7206512` |
| `docs/equipment-status-process-monitoring.md` | `c1af519d2eb5846fa9d70fea89002f116d77478a8e8393124729a40a228af2c7` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `4154d8df6cc66b6fc87a1017bd114c504199253b3bb83e1f49b9b5dd9c3686a7` |

由主协调会话启动 fresh-context Verification。DEV 检查为静态文档、样例及工作树对照，未运行渲染、API、数据库或现场验证。两份通用任务讨论稿是既有本地链接依赖。编辑前对照由协调者留至独立核验结束，Development 未另建临时资源。

## 历史 Development 记录（r5 D-04 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r5
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-04 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-04 从零开始的总体方案讨论稿

2026-11-09（Asia/Shanghai）。本交接限于 [r5 §7.4 D-04 文档范围](spec.md#r5-d-04-从零开始的总体方案讨论稿)，软件方案仍处于 `draft`。

## 实施与 DEV 自检（D-04）

双语指南按 D04-AC01 至 D04-AC04 对读。首版从项目配置和空库开始，以合成炉区 1 样本串起四页卡片、三页历史曲线、任务归属、SMA 两路和管理列表。首次现场启用按真实产线范围另行批准。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 核对两稿的相对链接、标题与显式锚点、预设表行和 Mermaid 源码 | 退出 0。两稿各 25 个链接、6 个既有阅读锚点、4 个设备状态预设、3 个历史页预设及 6 条 Mermaid 连线。两稿规格链接对应，接口路径和 JSON 由规格维护。 |
| 内联 `python3` 对照 r4 授权段与 `json.loads` | 退出 0。D-01 至 D-03 授权段正文匹配 r4 对照。6 段 JSON 均可解析，两路共用写入格式、来源任务、采集时间和映射，投递身份各自独立，加热就绪只进入实时。 |
| `git diff --binary HEAD -- . <文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` SHA-256 比对 | 退出 0。六份索引、checklist、范围外跟踪差异及 6 个既有未跟踪文件匹配协调者基线。 |
| `git diff --no-index --check -- "$before" "$after"`（双语指南及本记录），`git diff --cached --quiet` | 空白检查各退出 1，表示有内容差异，输出为空。暂存区检查退出 0。 |
| 内联 `python3` 恢复下方 r4 元数据引用并比较旧 `tasks.md` | 退出 0。原正文逐字节保留。去除 r4 元数据的引用前缀后，摘要匹配 r4 原记录 `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d`。 |

## D-04 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。候选为工作树中的双语指南及本 `tasks.md`。下列摘要通过 `shasum -a 256` 核对。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `cc1a481afc4b250e04e4daa33fcb6a29ae56531093fb9bb2d79e5a2fad295bf6` |
| `docs/equipment-status-process-monitoring.md` | `6b5ad2a36f60cc2ed7b7816c74aa0378d2be4daf4374a127a039014aa2ffe88d` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `2e6723a2e1ccf9e461654dfdbce053f038aa1e7310c6e590cd3e642d0d5a8e8e` |

由主协调会话启动 fresh-context Verification。DEV 自检限于静态文档、JSON 示例及工作树差异，未实测 Mermaid 渲染、软件运行或现场。两份既有通用任务讨论稿是本地链接依赖。编辑前对照由协调者留至独立核验结束，Development 未另建临时资源。

## 历史 Development 记录（r4 D-03 及 r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r4
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-03 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-03 任务归属和管理列表讨论稿

2026-11-09（Asia/Shanghai）。本交接限于 [r4 §7.4 D-03 文档范围](spec.md#r4-d-03-任务归属和管理列表讨论稿)，软件方案仍处于 `draft`。

## 实施与 DEV 自检（D-03）

两份指南更新至 r4。对照 D03-AC01 至 D03-AC04，核对了按原任务归属的采样与换单空态、SMA 一次映射和两路投递、管理员列表及备注和标记权限。两稿保留指标类型、单位、时区和历史留存规则。

| 检查 | 实际结果 |
| --- | --- |
| 内联 `python3` 检查相对路径、显式及标题锚点、双语规格链接、关键字段、历史授权及 `json.loads` | 退出 0。两稿各 23 个链接，共 46 个目标解析成功，既有阅读锚点保留。规格六段 JSON 可解析，两路写入示例任务号、原采集时间和映射一致，投递身份各自独立，两路均有采样任务号点位证据。D-01 和 D-02 授权段正文匹配 r3 对照。 |
| `git diff --no-index --stat` 与 `git diff --no-index --check`（当前文件与编辑前快照比较） | 每稿各 34 行新增、18 行删除。两稿及本记录的空白检查均退出 1，表示存在内容差异，输出为空。 |
| `cmp` 对照根 PLAN、双语 docs 索引、双语 plans 目录和 checklist 编辑前字节，`git diff --cached --quiet` | 均退出 0。 |
| 内联 `python3` 解开下方历史元数据引用，比较旧 `tasks.md` 字节 | 退出 0。恢复后 SHA-256 为 `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e`，原 r3 Development 正文逐字节保留。 |

## D-03 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。候选是工作树中的两稿及本 `tasks.md`，依据下列 PM 规格。用 `shasum -a 256` 核对摘要。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `5e8e9d7ffe670187afb142f5665525810313b69484384324a82df23832c0a8e3` |
| `docs/equipment-status-process-monitoring.md` | `5f9d498808d9589ef1a6d4785f78da8636cf28baae9276ee02a0a14490733e2a` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `fcd73dd295dc555170d0d855895478b8db40ec1a837c78f629c9b616ce4d0a47` |

由主协调会话启动 fresh-context Verification。自检限于静态文档和工作树，软件运行和 Mermaid 渲染未实测。编辑前对照由主协调会话保管至独立核验结束，Development 未另建临时资源。两份通用任务讨论稿是既有的本地链接依赖。

## 历史 Development 记录（r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r3
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: D-01 working-tree candidate to fresh-context Verification
> Workflow Mode: STD
> Execution Mode: agent_team_same_session

# D-01 设备状态与过程监控讨论稿

2026-11-07（Asia/Shanghai）。范围与批准见 [r3 §7.4](spec.md#74-长期阅读指南)，自检对应 D01-AC01 至 D01-AC04。r3 软件设计仍处于 `draft`，软件实施及现场采用分别审批。

## 实施记录

| 验收项 | D-01 交付 |
| --- | --- |
| D01-AC01 | 新建[中文讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md)与[英文讨论稿](../../docs/equipment-status-process-monitoring.md)。两稿互链，分别链接本规格，在[中文索引](../../docs/README.zh-CN.md)与[英文索引](../../docs/README.md)各增加一行。 |
| D01-AC02 | 用同一炉区的实测温度和设定温度说明指标登记、四页共用卡片、每卡 10 个启用指标上限、逐项新鲜度和独立曲线配置。 |
| D01-AC03 | 两稿用简图和正文走读 DAA 事实、SMA 标量映射、实时覆盖、历史追加和两路回执。历史白名单、选样间隔和持久留存各归采样与存储，曲线组负责展示。 |
| D01-AC04 | 具体接口、字段及 JSON 示例链接 r3。本文件记录 D-01 交接。 |

## DEV self-check

在交付工作树根目录执行。环境为 macOS 15.7.7、Python 3.9.6 和 Apple Git 2.50.1。

| 命令或核对方式 | 实际结果 |
| --- | --- |
| 逐节对读中英两稿及 r3 §2–§5、§7 | 五个主题、步骤与图示对应。炉区两标量、管理员配置、10 项上限、逐项采集时间、缺测、`0` 与 `false`、曲线缺口、独立投递和留存均已对照。 |
| 下方 `python3` 静态检查 | 退出 0。每稿 19 个本地链接，含 5 个阅读锚点。每个索引新增行有 2 个链接，总计 42 个目标解析成功。移除新增行后，两份索引各自匹配编辑前 SHA-256。初次运行把总数预设为 40，核对实际 42 个链接后更正检查计数。 |
| `git diff --check -- docs/README.md docs/README.zh-CN.md` | 退出 0。 |
| `git diff --no-index --check -- /dev/null "$guide"`（两篇新稿各运行一次） | 均退出 1，表示相对空文件存在差异。两次均无空白错误输出。 |
| 编辑前后分别执行 `git diff --binary`、`git status --porcelain=v1 --untracked-files=all`，用 `diff -u` 比较快照 | 差异退出 1。跟踪文件差异仅两条索引行及其 diff 元数据。新增路径为两份讨论稿和本记录。对照用通用任务讨论稿两份 SHA-256 相同。 |
| `shasum -a 256` 核对下表规格和候选文件 | 退出 0，规格摘要与 PM 交接值一致。 |

本地链接按相对路径、显式 HTML 锚点或 Markdown 标题 slug 检查。Mermaid 对照了源码节点与连线。当前环境 `command -v mmdc` 退出 1，图形渲染未实测。D-01 是 Markdown 交付，检查限于文档与工作树，软件编译、单测和运行验证属于软件实施范围。

<details>
<summary>可重跑的链接、结构与索引检查</summary>

```bash
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
import re

stem = 'equipment-status-process-monitoring'
docs = Path('docs')
expected_ids = ['metric-registry', 'latest-cards', 'history-curves', 'data-flow', 'adoption']
expected_indexes = {
    '': '01b40650b7f3fd06fc0fec7f7a2b657c2274a3200f8488228c59b7433801e156',
    '.zh-CN': '4bf114862b40e9474bfaef6b24cd179c6c3f7031b6c3148442ac6ccef366a35d',
}
link_pattern = r'\]\(([^()\s]+)\)'
all_links = 0
for lang, index_hash in expected_indexes.items():
    guide = docs / f'{stem}{lang}.md'
    other = '' if lang else '.zh-CN'
    source = guide.read_text()
    links = re.findall(link_pattern, source)
    assert re.findall(r'<a id="([^"]+)"', source) == expected_ids
    assert [link[1:] for link in links if link.startswith('#')] == expected_ids
    assert [source.count(token) for token in ('`furnaceZone1Actual`', '`furnaceZone1Set`', '`0`', '`false`', '10', '```mermaid')] == [1] * 6
    assert not re.search(r'/api/|^```json', source, re.M)
    assert source.count('```') == 2 and source.endswith('\n')
    assert f'{stem}{other}.md' in links and f'README{lang}.md' in links

    index = docs / f'README{lang}.md'
    index_lines = index.read_bytes().splitlines(keepends=True)
    rows = [row for row in index_lines if stem.encode() in row]
    assert len(rows) == 1 and rows[0].startswith(b'| ')
    assert sha256(b''.join(row for row in index_lines if row != rows[0])).hexdigest() == index_hash
    index_links = re.findall(link_pattern, rows[0].decode())
    assert index_links == [f'{stem}{lang}.md', f'{stem}{other}.md']
    for origin, targets in ((guide, links), (index, index_links)):
        for link in targets:
            path, _, anchor = link.partition('#')
            target = origin.parent / path if path else origin
            assert target.is_file(), (origin, link)
            if anchor:
                body = target.read_text()
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-')
                         for h in re.findall(r'^#{1,6} (.+)$', body, re.M)]
                assert f'<a id="{anchor}">' in body or anchor in slugs, (origin, link)
            all_links += 1
    print(f'{guide}: {len(links)} guide links, {len(index_links)} index links, 5 reading anchors, 1 index row')
assert all_links == 42, all_links
print(f'{all_links} local links resolved across both guides and index rows')
PY
```

</details>

## Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，基线 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。以工作树文件而非仅 HEAD 为验证对象。规格、讨论稿及任务记录为未跟踪文件，索引包含另一项工作原有的未提交行。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `c5b49be944d3ae40abd72ac77967b529afa6a449e0cf608a415872e486310391` |
| `docs/equipment-status-process-monitoring.md` | `738441be2a54cef103e714e03c6ae9ebb89e7b4debf31f393332aedba8c361b6` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `345fa0b94197ef14cb0bbc916ca3d0916f775ecb98ea008c9601162dc3d05041` |
| `docs/README.md` | `a74d088ca1802bc1906a929004cb73bc8c3a6adb19a66d4579f5b957ee17a673` |
| `docs/README.zh-CN.md` | `9bc039d9b9dc5c2261f6682485ff2facb623afee43c3d8b931ef09abf6d5c87a` |
| `docs/generic-task-workflow-discussion.md`（既有链接目标） | `b0913d0fe16627b9d7bbe1043b8b602ccee312b08915a70a68ed628fc7032fff` |
| `docs/generic-task-workflow-discussion.zh-CN.md`（既有链接目标） | `2e55a70064945d4836f4204bb7f9a7dba2151d3c76b78156aa88ca7416f39439` |

下一阶段由主协调会话启动 fresh-context Verification，对 r3 §7.4 D-01 按 D01-AC01 至 D01-AC04 独立验证。需从工作树读取新稿和既有未跟踪链接目标。后续整理交付内容时，这两个链接目标须随相应索引内容可用。

临时资源仅为本任务的 `/private/tmp/arch-obs-001-d01.WbzS9p` 前后对照快照，完成比较后回收。验证输入为仓库文件及本文记录。

# D-02 单位规则补充

2026-11-07（Asia/Shanghai）。D-02 状态为 `developer_handoff`，授权及验收项见 [r3 §7.4 D-02](spec.md#r3-d-02-单位规则补充)。r3 软件设计仍处于 `draft`。

## 实施与 DEV 自检

两份讨论稿仅在第 1 至 4 节补充单位说明。指标名称与两种语言共用的可选 `unit` 分开保存，前端组合指标项标题，值区仅显示格式化后的值。曲线组沿用同一物理量和单位，共用纵轴只标注一次单位，空单位省略标注。SMA 按 `metricKey` 上报原类型的 JSON 标量，两路按同一登记业务单位上报。

| 检查 | 实际结果 |
| --- | --- |
| 对照两稿与 r3 §3、§4.1、§4.2、§5 及 D02-AC01 至 D02-AC04 | 两稿均说明空单位、标题拼接与 `810.2` 值区示例、曲线轴和 SMA 上报规则。原有接口与 JSON 示例链接继续指向规格。 |
| 从上方 D-01 记录提取 `python3` 链接脚本执行 | 初次退出 1，原子串计数将 `810.2` 也计入 `10`。执行时经 `sed 's/source.count(token)/source.replace("810.2", "").count(token)/'` 排除该示例后退出 0。两稿各 19 个链接、5 个阅读锚点，含两条既有索引行共 42 个链接解析成功。 |
| 内联 `python3` 比较编辑前副本，按差异分段、链接、锚点及 Mermaid 围栏检查，并用 `json.loads` 解析规格示例 | 退出 0。两稿的差异各限于第 1 至 4 节，链接、锚点及 Mermaid 源码逐字节一致。规格和 QA 记录与 DEV 开始时的副本一致，规格中 6 段 JSON 可解析，看板示例将 `label` 与 `unit` 分开，两路温度值均为 JSON 数字。 |
| `git diff --binary`、`git status --porcelain=v1 --untracked-files=all` 与编辑前快照用 `cmp` 比较 | 均退出 0。三份本次交付文件在编辑前已经是未跟踪文件，内容差异另与编辑前副本比较。 |
| `git diff --no-index --check -- "$before" "$after"`（两稿及本记录分别与编辑前副本比较） | 三次均退出 1，表示内容存在差异，均无空白错误输出。 |
| `head -c 7255 plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md \| shasum -a 256` | 退出 0。摘要 `b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f` 匹配 D-01 原记录。 |

## D-02 Developer handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。以当前工作树文件为候选，`shasum -a 256` 核对结果如下。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `55c168a7120af682e98af4246fb0d8c192492d8d7830d7dddc14be379fe3d3a3` |
| `docs/equipment-status-process-monitoring.md` | `939db98596e85464552c8250d0322e659af923216becba83063d3a1e9c4400e3` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `9c032abe5be2f04acf6b05d2c9404eae425841938a01ac07379f3da7b639d22e` |

交主协调会话启动 fresh-context Verification，对 D02-AC01 至 D02-AC04 独立验证。本轮证据限于静态文档和工作树，未运行软件或渲染。既有通用任务讨论稿仍为工作树内的链接依赖。编辑前快照仅用于 DEV 比对，交接前回收。
<!-- ARCH-OBS-001-r6-history-end -->

</details>

# r7 Development 交接

2026-11-11（Asia/Shanghai）。状态：`developer_handoff`。Human Owner 的精确授权为“批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证”；完整规格 SHA-256 为 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。这份记录是 Development 自检与未完成验证的事实，不是独立 QA 结论或 Human Owner 最终验收。

## 来源、范围和实现

交付源码是独立目录 `runtime/arch-obs-001-r7/source`，起点为冻结基线 `runtime/arch-obs-001-r7/baseline`，基线 Git HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。基线清单含 888 个公共文件；协调者比对了 ARCH-ACQ-003 r2 已验收清单中的 53 个依赖文件，清单 SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。源码复制排除了真实环境文件、私有 profile、数据库、构建产物、依赖缓存与密钥。本次 57 个新增／修改文件逐项符合 §9.4；下表逐项列出候选 SHA-256。未将变更合入现有运行树。

实现了 `equipment_observation` 模块及显式后继 revision `5f7a9c1e3b26`，包括指标登记、两目标槽位、卡片和曲线配置、实时快照、过程历史及带任务证据的事务回执。SMA 和第三方使用同一发现接口及两个独立写入目标；身份、范围和任务归属由私有 profile 与 v2 事实校验。任务点年龄与每设备／组的采集值陈旧阈值分别配置。Web 四页卡片、三页曲线、两个管理员管理入口、双语及受范围保护的记录列表接入候选 API；原能耗和采集数据入口保留。机器合同、示例 profile、合成向量及回环可复跑走读位于 `contracts/published/http-api/equipment-observation-v1/`，两份讨论稿追加 r7 实际流程。

| 证据 | SHA-256 |
| --- | --- |
| 冻结基线树（对有序 `sha256  相对路径\n` 文本取 SHA-256） | `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f` |
| 候选树（相同算法，924 个公共文件） | `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402` |
| [r7-source.patch](evidence/r7-source.patch) | `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` |
| [r7-source-baseline.json](evidence/r7-source-baseline.json) | `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10` |
| 本记录追加前的 tasks.md 前缀（23232 字节） | `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3` |

补丁先以 `git apply --check --whitespace=error` 对冻结基线验证；再在 `/private/tmp/arch-obs-001-r7-dev-tq7d4aq3/patch-reproduction/check` 的基线副本实际应用，逐项比对 924 个候选文件 SHA-256，均匹配。证据 JSON 包含完整基线、候选及每个变更文件摘要；生成产物和依赖目录排除在树摘要外。上述 r6 及更早 `tasks.md` 字节逐字保留，可取前 23232 字节恢复。

<details><summary>57 个候选变更文件和 SHA-256</summary>

| 候选相对路径 | 类型 | SHA-256 |
| --- | --- | --- |
| `CODE_INDEX.md` | 修改 | `ea9afc17e95c692f0f9f06b3f5d292c5b3f84bc4c69a3f65abc9ba21dcfea11c` |
| `backend/alembic/versions/20261111_1800_5f7a9c1e3b26_add_equipment_observation.py` | 新增 | `77e28319827ec54257ef889ec7b4eda4ce7e29dc203035ea76b8e6529d96038a` |
| `backend/app/equipment_observation/README.md` | 新增 | `5af542dd1fd47f75937f41816fe2cbec95a2b9c0cdc296482e89ec44b0fa17d7` |
| `backend/app/equipment_observation/README.zh-CN.md` | 新增 | `61ca08d3c20ad18a3698a9e5c19fc170d29e748f7fa90d418c7405e4d9c4fde4` |
| `backend/app/equipment_observation/__init__.py` | 新增 | `56fc319faab27f00444050a7f4cede5bfd82c40a776223482a9d0b6cb9b92130` |
| `backend/app/equipment_observation/api/__init__.py` | 新增 | `77a668728ad2886630462f40fe5920f121ce342aaba26c2cc2934040570df252` |
| `backend/app/equipment_observation/api/routes.py` | 新增 | `5db2559282c98aed75c35f7736f79e69a06eb6a208fba30390d59e5fc74c374a` |
| `backend/app/equipment_observation/domain.py` | 新增 | `17a61fb2175db447a0fd31f6050a4a86a0585982d128fbc80017db54e4faa0bc` |
| `backend/app/equipment_observation/error_codes.py` | 新增 | `662d6e34cdfd9c5df8fe39fa27408e591033b3e600dceee2058195806c130fd3` |
| `backend/app/equipment_observation/manifest.py` | 新增 | `592adc32634ec1edce508deca9ccba6004cdef6bb64a5848ea9a548c09abe4c3` |
| `backend/app/equipment_observation/models/__init__.py` | 新增 | `8a49f24867d27ae803823dc6d6f2253404437439bcbbfaff253b6797186b3c73` |
| `backend/app/equipment_observation/models/records.py` | 新增 | `346a80dad24623f6f6bf70f72690870c42b94705fd86c963bcce42c4dc30a59e` |
| `backend/app/equipment_observation/profile.py` | 新增 | `65ca4b294d84e01e45f8b6b9ad20ca90e3078fcd95877e4a890ba1a8e2c88ba1` |
| `backend/app/equipment_observation/schemas.py` | 新增 | `1072841d8c535cd1dd54d6d446ddf70b859d73078ef71fabbc682c051dd96850` |
| `backend/app/equipment_observation/services/__init__.py` | 新增 | `877cf89acf402aedd0374737b6e5c80c355d914974d8e84c15b5409eb9da12de` |
| `backend/app/equipment_observation/services/configuration.py` | 新增 | `9278f71accaea1ae8df6affdb3835e5dd0dae0d78c2fda9aa499c1490ec10451` |
| `backend/app/equipment_observation/services/ingest.py` | 新增 | `2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34` |
| `backend/app/equipment_observation/services/reads.py` | 新增 | `c5e2939fb76187ce47db11bda849ba75292f85b14eb7d0d6098c3bfbf9c7980e` |
| `backend/app/plc_facts/README.md` | 修改 | `6ba8d94ba587f3fc106a37b2be12741b385602ec90f0cbcfbfd0bd5bb8e9b305` |
| `backend/app/plc_facts/README.zh-CN.md` | 修改 | `07b905c7970dbaa145c10d0f5f0c3354690ffdda725149532382f78453858713` |
| `backend/app/plc_facts/crud/async_v2.py` | 修改 | `4f39e0f4fa4ae612523377bafc0917ea249160d90350c30d062a4e47be0f6e76` |
| `backend/app/plc_facts/crud/sync_v2_maintenance.py` | 修改 | `ba26d3b21f3cce238d88c9aea961e410e4064928f4084888594170fa51aa12f9` |
| `backend/app/plc_facts/manifest.py` | 修改 | `79afed8eae956c82e14d7c28b489e76b51bfe58c105c8fd2e30cba54d7e689e3` |
| `backend/app/plc_facts/services/observation_evidence.py` | 新增 | `8defa9ed4fd38133debef1fd41f442664ba493e25e1f4aadcf8331ee7e8e2141` |
| `backend/app/plc_facts/v2_config.py` | 修改 | `233dcd6b033e664daec245f8b0a575c2c36c277fb5d8fa9569a989913162ec75` |
| `backend/common/integration/storage.py` | 修改 | `b230f7e1fb9288511abf0c1dffc07e954fcbe2b7ca0982b5ddeb2703f8b176d2` |
| `backend/tests/test_equipment_observation_domain.py` | 新增 | `98bdb98f65605aac04f461651143018fc6dfdce76524008bce2e523465e50c8d` |
| `backend/tests/test_equipment_temperature_migration.py` | 修改 | `3c611ab32eca25e6c749350f6305e423e29b579be35677c5fa2ce4ed16b8009f` |
| `backend/tests/test_legacy_acquisition_retirement.py` | 修改 | `57d8b37c815f269e7b7b90b57be3f9e0dee570ced556bf25fe49623018076c55` |
| `backend/tests/test_mapping_migration.py` | 修改 | `9b99ff37c4241c6b7dc67e943655229a3d80ac6eee8e0192a024f1ec0f60697f` |
| `backend/tests_mysql/test_equipment_observation_mysql.py` | 新增 | `4c3376b87c5393a5f301d7193f637655a3315b617700c1e6de512875c3423885` |
| `contracts/README.md` | 修改 | `ea4bb17979772a2f240ee23ac127ec6b68a36c8413a69882354ee2a072e5f924` |
| `contracts/README.zh-CN.md` | 修改 | `bcbb72e6c50fd65f3e5245641783f3d1a01a4b3a1f118309100b0066316e6386` |
| `contracts/published/http-api/equipment-observation-v1/README.md` | 新增 | `49ff29317e038a0b39b2bc86184f7a90383e956f840803071b7264391afcfa7a` |
| `contracts/published/http-api/equipment-observation-v1/README.zh-CN.md` | 新增 | `e0263e0ff2fb43ae19b0b6bafec13bbe64ca03a107bf2fcf79d9dca11f8770ec` |
| `contracts/published/http-api/equipment-observation-v1/example-profile.json` | 新增 | `061519aedb07594486383285d37e83010c9dc66631b2b5569674dc7f2da3265e` |
| `contracts/published/http-api/equipment-observation-v1/openapi.json` | 新增 | `7a5bd636a75208dbaf65531bff9d72e9dae8d81765d73f2ae10631e745849c07` |
| `contracts/published/http-api/equipment-observation-v1/vectors.json` | 新增 | `dd904d37d2a787c04afe14f13331c08b44ab54cb72708a37206be8be05456ed8` |
| `contracts/published/http-api/equipment-observation-v1/walkthrough.py` | 新增 | `79c2072ed1f31bce414715af06753505d23257c4ce5eafe15b0e4ea02876e7ee` |
| `docs/equipment-status-process-monitoring.md` | 修改 | `5ed0909de0273d0f5cfb3489cf4e7269f3671465080acf52dfdd8c343131494e` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | 修改 | `d4f15c10470e8f0b7c421ff170db5819ac3eb91c5c0f674a4d2751cf8bf606c8` |
| `frontend-js/src/app/equipment/api/observations.js` | 新增 | `ffb34494dd99d57ab4375ca55fcd87aa34ac14f12b5e886acbba53e41c7bc16d` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | 新增 | `66f4a3ae514917b5d055d1baebba3c89c692d39c7a2cf459f540f959c0e3f2cf` |
| `frontend-js/src/app/equipment/locales/en-US.json` | 修改 | `1e808aed676cfbced4b821ea229bfd84f7e606815b6e77d4884bdbde2a2ee4b0` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | 修改 | `238aa4b86e59d54556abfdf3ce2fed7e0cf6bd391873a56ed202d7ca9fbed6f3` |
| `frontend-js/src/app/equipment/manifest.js` | 修改 | `8ccc0f244d154ec0f9216142736b940daa630ff4cc722db426639d876faab96e` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | 新增 | `42d34402b53fc7012a86146f2442ba05c9d0e10d30d98e59990effe2e30cdc38` |
| `frontend-js/src/app/equipment/views/observations/cards.vue` | 新增 | `0f0f9330cae3d1c97fb941a36fc4886108a0d5ed2b9fef8a91e220f45506bcd9` |
| `frontend-js/src/app/monitor/api/observations.js` | 新增 | `6d3ee0a8ad807f5c292e1857253b0d8d7ff6e19d173c540de2427792bfa4887d` |
| `frontend-js/src/app/monitor/components/observations/CurveChart.vue` | 新增 | `167c0e55ca1d0135a90c2214d6498a52353cfa5d8643ddc68289d89e9bf215cb` |
| `frontend-js/src/app/monitor/components/observations/curveSeries.js` | 新增 | `b092e99b878609f8cb107dd50922972cadd239ee3c4a13195948c5e8b2162d7d` |
| `frontend-js/src/app/monitor/locales/en-US.json` | 修改 | `e8aec65ac4314240d233e5a0e263c73bad8d6f47dc33b8f1845f20f712e26534` |
| `frontend-js/src/app/monitor/locales/zh-CN.json` | 修改 | `7fdabe4b01e7fc6d0e124307174e7283bb0dbf00335668da3180ac06c5f8a80b` |
| `frontend-js/src/app/monitor/manifest.js` | 修改 | `fe604032a2ab8a81c6dfd20d8bc5d620fc631d502254a2a4e285526e81db9d85` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | 新增 | `08f5c558e55bac2877bdc18e408ffb40171318524b60f172e712b8c41e89b210` |
| `frontend-js/src/app/monitor/views/observations/curves.vue` | 新增 | `b852627a9ca29de568a363ce7527a654c4bb0d9ce951f32f425e5592ad34ee34` |
| `frontend-js/tests/module-registry/equipment-observation.test.mjs` | 新增 | `eb957cb55b10596b0e0c896b26705a7db4ef0282d166394fb391062ea00b0bc5` |

</details>

## DEV 自检和已观察结果

使用候选工作目录及仓库锁文件，Python 为 `uv run --offline --frozen --no-sync`，`PYTHONPATH` 显式指向候选 `backend`，复用只读依赖虚拟环境；前端使用候选独立的 `node_modules` 副本和 `pnpm_config_verify_deps_before_run=false`。未使用 3307、8000、5190 或真实 PLC/DAA/SMA。DEV 专属 MySQL 8.4.6：回环映射 13395、schema `arch_obs_r7_dev`、server UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`、业务会话 +08:00；API 18395、Web 15395 均回环。真实凭据和 profile 仅在仓库外测试私有目录。首次空库升级到新 head，随后在已有合成 v2 事实的同一隔离库对 r7 七表执行降级至 `4e6a8b0d2f14` 再升级；核对目标 UUID/schema/revision 和非空 `task_evidence` 列。未操作旧业务实例。

| DEV 检查和命令 | 实际结果 |
| --- | --- |
| `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql` | 退出 0；新增段的离线 SQL 包含七张表及回执任务证据。隔离 MySQL 空库升级和仅 r7 的降级／再升级均退出 0。 |
| `pytest -q -m no_db tests/test_equipment_observation_domain.py`（以上 uv 方式） | 退出 0：4 passed；覆盖任务号、原始类型、缺省和 null、两目标稳定事件、无效 UUID 及每组不同陈旧阈值。 |
| `pytest -q tests_mysql/test_equipment_observation_mysql.py`（由确认的 `OBS_FIXTURE_*`、专属 MySQL 和私有合成机器凭据驱动） | 退出 0：2 passed；实际 socket 与真 MySQL 验证未认证、越权、413/415、质量/空值、SMA 必填，A→B、B 缺测、迟到 A、旧包 stale、回执重试/冲突、历史同源去重、伪造引用／采样时间、0/false 及任务证据。测试自身先校验精确轮次、UUID、端口、schema、用户、MySQL 版本、时区及 revision。 |
| `python contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18395`（以 `OBS_DEMO_*` 私有合成凭据运行） | 实际执行退出 0；两份不同合成 v2 样本、第三方和 SMA 全信封各自独立 latest/history、发现、重试与任务证据详情、`000042` 的 `812.2/815.0` 卡片及曲线通过。完成边界测试后再次运行恢复 `000042`。 |
| 候选 ASGI + 真 MySQL 对两条管理员 PATCH | 退出 0；实时备注与历史备注／`reviewed` 均 HTTP 200、响应返回新值。另由协调者执行真实浏览器保存。 |
| `pnpm check:modules`、`pnpm build --outDir /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/frontend-dist` | 均退出 0；构建提示既有大 chunk 和外部 outDir 警告。 |
| `pnpm test:modules` | 退出 1：53 passed、4 failed。失败是两个既有测试文件中对退役 `monitor.realtime` 的四个固定路由／授权断言，均在原 §9.4 修改范围外；已保留原文件并提交协调者。 |
| 受影响后端 `pytest -q -m no_db tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_acquisition_facts_migration.py tests/test_business_integration_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_equipment_observation_domain.py`，所有 bootstrap 和 mock/projection 开关设置 False | 退出 1：133 passed、3 skipped、2 failed。一个既有测试固定迁移数 11，新增 head 后为 12；另一个既有测试将旧元数据表集合全等，未包含七张新表。前者文件不在 §9.4，后者虽可同步 head 但原授权仅允许 head 断言，故两处原断言均未改。初次运行另因合成 supervisor bootstrap 为 True 多失败一项，关闭后该项通过。 |
| 协调者的候选真实浏览器 DEV 检查 | `runtime/arch-obs-001-r7/output/playwright/dev-browser-result.json` 及 3 张 PNG：登录、双语指标编辑、四卡片页、三曲线页、任务筛选、同单位、两类记录详情及实际保存、普通读用户与管理 403、无 pageerror；这仍是 DEV 自检而非独立 QA。 |
| 文档及合同 | 新 OpenAPI 三条路径及所有 `$ref` 可解析；向量、示例 profile JSON 可解析且 profile 经实现校验通过；两稿、合同及新模块说明的相对路径链接均存在。 |

## Developer handoff：待独立复核和限制

请 fresh-context Verification 直接核对上述 `source`、规格 SHA、补丁／文件清单及 §9.5 验收项。独立轮次应使用另一个专属 MySQL（13396）和独立 API/Web 端口与私有 profile，不复用 DEV 数据或密钥。尤其复核旧 profile/旧 revision 与新 profile/新 revision 的实际读写、错配拒绝、旧 typed 接口在新 revision 的实库行为，以及空闲／未知／过期任务、两条受控产线、历史筛选、首用锁与 100 槽上限、并发／未知提交与独立补投；这些项目本 DEV 记录没有完整实库证据，不能视为已通过。所列 2 个旧后端断言和 4 个旧前端断言仍失败，是否扩展修订范围由 Human Owner 决定，勿将其当通过。

SMA 全信封由合成 HTTP 客户端发送，未运行 SMA 产品或连接 DAA/真实 PLC；没有进行性能、长时稳定性、真实数据库采用、发布或生产部署验证。截图和合成实例为 DEV 资产，协调者负责按本任务范围停止及回收；候选源码、冻结基线、任务记录和脱敏补丁需保留给 QA 与后续单独批准的整合。测试机私有 profile、测试账号、令牌和日志不进入交付。DEV 实际启动入口（环境文件和 profile 内容不展示）：在候选 `backend/` 导出仓库外 DEV `backend.env`、独立 facts／observation profile 路径、`UV_PROJECT_ENVIRONMENT` 和私有 `UV_CACHE_DIR`，设置候选 `PYTHONPATH`，执行 `uv run --offline --frozen --no-sync python main.py`，绑定 `127.0.0.1:18395`；在候选 `frontend-js/` 设置 `VITE_PROXY_TARGET=http://127.0.0.1:18395` 和隔离角色页面清单，执行 `pnpm exec vite --host 127.0.0.1 --port 15395 --strictPort`。协调者已停止这两个 DEV 进程并核实端口无监听；浏览器证据使用本机 Chrome headless/Playwright。


# r7 QA1 返工 Development 交接

2026-11-11（Asia/Shanghai）。同一获批 `ARCH-OBS-001 r7` §9 内按 QA1 的 1–4 项缺陷返工，状态 `developer_handoff`，交 fresh-context Verification 重新验证。规格 SHA-256 保持 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`；返工开始读取的 canonical QA1 checklist SHA-256 为 `3d9c5c749e35de3b596bacef9dbd5cc74e0c798c9232fb847f707dd4c1e35aca`，其 `qa_failed` 记录由 Verification 管理，本角色未修改。这个记录不授予 QA 结论或 Human Owner 验收。

## 改动与并发语义

1. 曲线保存时按稳定顺序对所引用指标行做 `FOR UPDATE` 并保留至提交；指标类型变更锁定同一指标行，并用锁定读取检查**所有**曲线组和系列引用，包括停用项。未首次使用的已引用数值指标不能改成布尔或字符串，解除全部引用后才可在原有规则下修改；已使用指标的类型和单位仍按原首用锁拒绝。单位兼容检查保留。
2. 两类管理员详情共用视图显示采集质量及其中文／英文值，与人工复核标记分开；对应列表质量显示也采用同一语言文本。
3. 管理员详情 GET 和 PATCH 的查询以记录 ID 与当前角色获准设备集共同限定；越权记录与不存在记录均为 404，显式带越权设备筛选的列表仍返回 403，写操作沿用同一受限详情查询。
4. 双语走读及机器合同补充后续 SMA 独立登录身份的 `plc-facts-read`、v2 `readScopes` 精确 PLC/DB 与观察写 Bearer 的区分、双路回执、SMA-004 后续 GET→POST、ARCH-ACQ-001 统筹、DAA-010、ARCH-BE-012 精确 provider/隔离独立验证及 Human Owner 最终验收、DAA-010 精确批准和新隔离 profile、逐 DB 的 SQLite/后端事实与回执确认及相关 API 与 SMA 产品执行的独立门槛。本版没有运行产品或真实现场链。

相对 QA1 候选仅以下 11 个允许文件发生变化；SHA-256 分别为 QA1 与本返工候选。完整基线到新候选的 57 文件差异及 924 文件摘要仍在下述新的 canonical 清单。其余源码字节不变。

| 相对交付源码路径 | QA1 SHA-256 | 返工 SHA-256 |
| --- | --- | --- |
| `backend/app/equipment_observation/api/routes.py` | `5db2559282c98aed75c35f7736f79e69a06eb6a208fba30390d59e5fc74c374a` | `547d571f9cf845c1a65d414eb193736aacf0751cacff4ef81d6de48fc2a7999e` |
| `backend/app/equipment_observation/services/configuration.py` | `9278f71accaea1ae8df6affdb3835e5dd0dae0d78c2fda9aa499c1490ec10451` | `c85202890990bcbb333e58bfa37cf89bb5aec7e10b1f80065e0a1c2ca6a82696` |
| `backend/app/equipment_observation/services/reads.py` | `c5e2939fb76187ce47db11bda849ba75292f85b14eb7d0d6098c3bfbf9c7980e` | `85fa8b78e1ee4b82001badf0c1e1af8e2e050eeaf577e90be7c15cb744e6f932` |
| `backend/tests_mysql/test_equipment_observation_mysql.py` | `4c3376b87c5393a5f301d7193f637655a3315b617700c1e6de512875c3423885` | `4e6928fd79f6b574b7c5b1af2c70852c8f613237edbf86da33d010aeecfcffdf` |
| `contracts/published/http-api/equipment-observation-v1/README.md` | `49ff29317e038a0b39b2bc86184f7a90383e956f840803071b7264391afcfa7a` | `e4b57b94e795258462a477a189f41c281d164e303b0f648e924b89dcc8e1ba05` |
| `contracts/published/http-api/equipment-observation-v1/README.zh-CN.md` | `e0263e0ff2fb43ae19b0b6bafec13bbe64ca03a107bf2fcf79d9dca11f8770ec` | `7d4484c21425cb185e2cb759d6316b77f2bd9e8231884f621e8e0cfb62a12eed` |
| `docs/equipment-status-process-monitoring.md` | `5ed0909de0273d0f5cfb3489cf4e7269f3671465080acf52dfdd8c343131494e` | `8b5e0a2f62fc55259486791a9eb42f722d3f1c86d016b6e64ee917fc8344647f` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `d4f15c10470e8f0b7c421ff170db5819ac3eb91c5c0f674a4d2751cf8bf606c8` | `fbf9061bb5b07724a1c17f99acbb18b4e1a7f745d8ce1a7e8ff03ab9677d3ef4` |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `66f4a3ae514917b5d055d1baebba3c89c692d39c7a2cf459f540f959c0e3f2cf` | `9d27c7507bdcf73be5514fec533b13b4b34035a8867706a559119df2a78bf4f3` |
| `frontend-js/src/app/equipment/locales/en-US.json` | `1e808aed676cfbced4b821ea229bfd84f7e606815b6e77d4884bdbde2a2ee4b0` | `861a7937509a221964a8b0ff0944260b86baf1c2d9fbfb9d2938c9b12b216c20` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | `238aa4b86e59d54556abfdf3ce2fed7e0cf6bd391873a56ed202d7ca9fbed6f3` | `c7a2be418b4bca75ea0a08180edf56d502a317468904de97691b66f6fa9072a9` |

## DEV 返工自检

DEV 专用 MySQL 8.4.6 的 UUID、库名 `arch_obs_r7_dev`、13395、+08:00 和 revision `5f7a9c1e3b26` 由协调者重新核对；候选 API `127.0.0.1:18395`、Web `127.0.0.1:15395`。未连接 QA 13396 或旧的 3307／8000／5190。

| 检查 | 真实结果 |
| --- | --- |
| `pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py`（明确 DEV round/UUID/port/schema/ACK，私有 profile 与合成凭据） | 退出 0，**5 passed**。新增三项真实 HTTP + MySQL 覆盖启用及停用曲线／系列的类型保护、解除引用和可编辑名称、首用后类型／单位保护；用两方向竞争同一指标行锁的事务验证曲线保存／类型更改串行化，检查等待及提交后结果；两类详情和 PATCH 的越权／不存在同 404、显式越权列表 403、被拒记录未变化。原两项写入/任务回归仍通过。 |
| 协调者真实 Chrome DEV 浏览器 | [返工结果](../../runtime/arch-obs-001-r7/output/playwright/dev-rework-browser-result.json)及[历史详情图](../../runtime/arch-obs-001-r7/output/playwright/dev-rework-task-000042-history-detail.png)：`000042` 的实时与历史详情均返回 `quality=good`；两处中文显示“采集质量／正常”、英文显示“Source quality／Good”，无 pageerror。未修改这些记录。 |
| 候选 `walkthrough.py --base-url http://127.0.0.1:18395` | 退出 0，第三方／合成 SMA 两目标与独立回执、task evidence、重试及 `000042` 卡片／曲线通过；边界测试结束后恢复 `000042`。 |
| `pnpm build --outDir <DEV私有目录>/frontend-rework-dist` | 退出 0；前置 `check:modules` 通过，28 路由，原有大 chunk 提示保留。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**；仍为 QA1 已列出的旧 `monitor.realtime` 固定路由／权限断言，文件未改。 |
| 原交接的受影响后端 `pytest -q -m no_db` 套件，所有 bootstrap、mock 和 projection 开关显式关闭 | 退出 1，**133 passed、3 skipped、2 failed**；仍是 QA1 记录的旧迁移数量与旧 metadata 全等断言，超出 §9.4 中允许的旧断言修改范围，保持原样。 |
| 双语讨论稿与合同本地链接、锚点及质量 i18n | 退出 0：115 条本地链接／锚点解析，两个语言的质量文本键存在。 |
| 原基线重建 | `git apply --check --whitespace=error` 退出 0；从原冻结 888 文件基线实际应用新补丁后，逐项重建的 924 个候选文件 SHA-256 全部一致。 |

## 新候选固定与复验 handoff

| 项 | SHA-256 |
| --- | --- |
| 新候选树（排序的 `sha256  相对路径\n` 文本摘要） | `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada` |
| [新 canonical 补丁](evidence/r7-source.patch) | `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4` |
| [新 canonical 基线与候选清单](evidence/r7-source-baseline.json) | `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f` |
| 返工前完整 tasks.md 前缀（40915 字节） | `21bfb30971cdaa3268cbf200b6a6e28691b9ec92f98e7efa5bb933990bb488f8` |

QA1 的原候选树为 `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402`；其原补丁 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` 与原清单 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10` 原字节保存在 [qa1-source](../../runtime/arch-obs-001-r7/output/qa1-source/)。上方 QA1 以前的记录均保持原字节，可截取本记录前 40915 字节还原；其中旧 23232 字节 r6 历史仍可按先前标记单独还原。

请由 fresh-context Verification 针对新固定候选重新检查 QA1 四项及受影响验收，QA 资源独立于 DEV。QA1 记录中的两条后端、四条前端旧断言仍失败，不能当通过或擅改范围。浏览器／MySQL 测试是 DEV 自检；未运行 SMA 产品、DAA、PLC 或真实 profile，也未实施生产发布或环境采用。DEV 服务和隔离资源由协调者按已批准归属停止与回收。


# r7 QA2 返工 Development 交接

2026-11-11（Asia/Shanghai）。按已批准的 `ARCH-OBS-001 r7` §9 对 QA2 唯一的 R7-AC06 管理界面本地化问题进行最小返工，状态 `developer_handoff`。规格 SHA-256 仍为 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`；本轮读取的 canonical QA2 checklist SHA-256 为 `e1b7255f8360fd4273e8def8309b1601bdb65670b048eade849ea6fae85a4967`，其 `qa_failed` 与 QA1 历史由 Verification 管理，Development 未修改。QA2 已关闭 QA1 四项，但最终 QA 与 Human Owner 验收需各自完成。

## 精确返工内容

历史列表的复核枚举用现有中英词条显示：`abnormal` 为“异常”／“Abnormal”，`reviewed` 为“已复核”／“Reviewed”，空值继续显示空白。详情表和指标配置表的名称表头随显示值使用 `nameZh`／`nameEn` 对应文案；卡片和曲线配置表的标题表头同样匹配 `titleZh`／`titleEn`。只改变显示，提交数据仍沿用原枚举。各表 `prop`、`nameZh`／`titleZh` 列宽偏好键及表宽工具均保留。

相对 QA2 仅有以下 3 个允许的前端组件发生变化，没有修改后端、合同、字典或旧测试。下列 SHA-256 可分别定位 QA2 候选和返工候选。

| 相对交付源码路径 | QA2 SHA-256 | 返工 SHA-256 |
| --- | --- | --- |
| `frontend-js/src/app/equipment/components/observations/RecordList.vue` | `9d27c7507bdcf73be5514fec533b13b4b34035a8867706a559119df2a78bf4f3` | `e1650bdb69611ce995b660c41967151da56d58957ba46ece45235bc2d5641c81` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `42d34402b53fc7012a86146f2442ba05c9d0e10d30d98e59990effe2e30cdc38` | `aa1d0f887281b60ff5d0517f216a9264a1ebc0d321466b1965f81c724392e591` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | `08f5c558e55bac2877bdc18e408ffb40171318524b60f172e712b8c41e89b210` | `60494af0dc8ad6f7622d3db441e4db48045b2f399443759bbd7042769917e4b0` |

## DEV 自检

| 命令或方法 | 实际结果 |
| --- | --- |
| 候选前端 `node /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/qa2-ui-targeted.cjs` | 退出 0。离线加载项目锁定的 `vue/compiler-sfc`、Vue 模板编译器及 SSR 渲染器，实际编译三个组件中相应列模板和读取现有词典。两种语言均核对 `abnormal`、`reviewed`、null、undefined、空字符串；对详情、指标、卡片、曲线四列分别核对中英表头与对应内容，并验证原 prop/列宽键。脚本无凭据，完整正文附下，SHA-256 `bfb25239f2f4d4ce72e5b058e77f43f973487c675f6eb4d8c2bf1e4bbbfdb883`。SSR 不是浏览器验证。 |
| `node --test tests/module-registry/equipment-observation.test.mjs` | 退出 0，**2 passed**。 |
| `pnpm check:modules` | 退出 0，28 个路由、10 个分组。 |
| `pnpm build --outDir /private/tmp/arch-obs-001-r7-dev-tq7d4aq3/qa2-rework-dist`（显式隔离页面授权及锁定依赖） | 退出 0；保留既有大 chunk 和 outDir 提示。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**。仍为 QA1/QA2 已识别的四个旧 `monitor.realtime` 路由与权限断言；本轮未修改这些旧测试。 |
| 补丁重建 | `git apply --check --whitespace=error` 退出 0；从 888 文件原冻结基线实际应用新补丁后，924 文件逐项 SHA-256 均匹配。 |

本轮仅做离线渲染、模块检查与构建；未启动或连接 DEV/QA MySQL、API、Web、浏览器、SMA、DAA 或真实 PLC，**没有对返工版做 DEV 浏览器复跑**。QA2 记录中的两项旧后端断言仍失败，本轮未改后端也未重跑该套件。临时测试脚本与构建产物由协调者在 QA3 不再需要后按资源生命周期回收。

## 新候选固定与 handoff

| 项 | SHA-256 |
| --- | --- |
| 新候选树（有序 `sha256  相对路径\n` 文本摘要） | `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf` |
| [新 canonical 补丁](evidence/r7-source.patch) | `d753328ceeb32cdd2cbd5387e221e14376403ef6024ea9cc0cf7adf7f5b00e46` |
| [新 canonical 清单](evidence/r7-source-baseline.json) | `df0145272f56505929e63e1c2a4c77d13b84acc88cead36359de5224f4f6d5e1` |
| 本轮追加前完整 tasks.md 前缀（49388 字节） | `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4` |

QA2 候选树为 `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada`；其原[补丁和清单](../../runtime/arch-obs-001-r7/output/qa2-source/) SHA-256 分别为 `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4` 和 `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f`。此前 QA1、QA2 交接内容及更早历史仍逐字节保存在本记录前 49388 字节。请 fresh-context Verification 在独立 QA3 环境验证中英文实际界面、空标记、列宽及受影响验收，不将本 DEV SSR 当作浏览器或 QA 通过。

<details><summary>本次离线 Vue SSR 定向检查原脚本</summary>

在候选 `frontend-js/` 下将以下内容另存为 `.cjs` 后运行；通过 `createRequire` 使用该项目锁定的依赖，无网络和数据库访问。

```javascript
/* Isolated, offline SSR probe of actual candidate column templates and dictionaries. */
const fs = require('node:fs')
const assert = require('node:assert/strict')
const path = require('node:path')
const { createRequire } = require('node:module')
const project = createRequire(path.join(process.cwd(), 'package.json'))
const { parse } = project('vue/compiler-sfc')
const { createSSRApp, defineComponent, h, compile } = project('vue')
const { renderToString } = project('vue/server-renderer')
const source = {
  records: 'src/app/equipment/components/observations/RecordList.vue',
  equipment: 'src/app/equipment/views/observations/admin.vue',
  monitor: 'src/app/monitor/views/observations/admin.vue'
}
const templates = Object.fromEntries(Object.entries(source).map(([key, file]) => {
  const result = parse(fs.readFileSync(file, 'utf8'), { filename: file })
  assert.deepEqual(result.errors, [])
  return [key, result.descriptor]
}))
const dicts = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale,
  JSON.parse(fs.readFileSync(`src/app/equipment/locales/${locale}.json`, 'utf8')).observation]))
function translator(locale) {
  return key => {
    const value = dicts[locale][key.replace('equipment.observation.', '')]
    assert.notEqual(value, undefined, `missing i18n key: ${key}`)
    return value
  }
}
function column(descriptor, prop) {
  const expression = new RegExp(`<el-table-column\\b[^>]*prop="${prop}"[^>]*>[\\s\\S]*?<\\/el-table-column>`)
  const matches = descriptor.template.content.match(expression)
  assert.ok(matches, `column ${prop} missing`)
  return matches[0]
}
const marker = templates.records.scriptSetup.content.match(/function reviewLabel\(value\)\s*\{[^}]*\}/)
assert.ok(marker, 'actual reviewLabel function missing')
async function render(template, locale, row, extra = {}) {
  const Column = defineComponent({
    props: ['prop', 'label', 'width'],
    setup(props, { slots }) {
      return () => h('section', { 'data-prop': props.prop, 'data-label': props.label, 'data-width': props.width },
        slots.default ? slots.default({ row }) : [])
    }
  })
  const t = translator(locale)
  const reviewLabel = new Function('t', `return (${marker[0]})`)(t)
  const app = createSSRApp({
    setup: () => ({ t, locale, reviewLabel, isHistory: true, ...extra }),
    render: compile(template)
  })
  app.component('el-table-column', Column)
  return renderToString(app)
}
;(async () => {
  const states = { 'zh-CN': { abnormal: '异常', reviewed: '已复核' }, 'en-US': { abnormal: 'Abnormal', reviewed: 'Reviewed' } }
  for (const locale of Object.keys(states)) {
    for (const [value, expected] of Object.entries(states[locale])) {
      const result = await render(column(templates.records, 'reviewMark'), locale, { reviewMark: value }, { columns: { widths: { reviewMark: 131 } } })
      assert.ok(result.includes(`>${expected}</section>`), result)
      assert.ok(result.includes('data-prop="reviewMark"') && result.includes('data-width="131"'), result)
    }
    for (const value of [null, undefined, '']) {
      const result = await render(column(templates.records, 'reviewMark'), locale, { reviewMark: value }, { columns: { widths: { reviewMark: 131 } } })
      assert.ok(result.endsWith('></section>'), result)
    }
  }
  const rows = { nameZh: '温度', nameEn: 'Temperature', titleZh: '炉区', titleEn: 'Zone' }
  const checks = [
    ['records', 'nameZh', 'detailColumns', 'name'],
    ['equipment', 'nameZh', 'metricColumns', 'name'],
    ['equipment', 'titleZh', 'cardColumns', 'title'],
    ['monitor', 'titleZh', 'columns', 'title']
  ]
  for (const [sourceKey, prop, widthKey, kind] of checks) {
    const template = column(templates[sourceKey], prop)
    assert.ok(template.includes(`:width="${widthKey}.widths.${prop}"`), 'stable width key changed')
    for (const locale of ['zh-CN', 'en-US']) {
      const data = await render(template, locale, rows, { [widthKey]: { widths: { [prop]: 183 } } })
      const lang = locale === 'en-US' ? 'En' : 'Zh'
      assert.ok(data.includes(`data-label="${dicts[locale][kind + lang]}"`), data)
      assert.ok(data.includes(`data-prop="${prop}"`) && data.includes('data-width="183"'), data)
      assert.ok(data.includes(`>${rows[kind + lang]}`), data)
    }
  }
  console.log('PASS actual Vue column SSR: both locales, reviewed/abnormal/empty, four bilingual headers/cells and stable width keys')
})().catch(error => { console.error(error); process.exitCode = 1 })
```

</details>

<!-- ARCH-OBS-001-r7-history-end -->
</details>

## 2026-11-18（Asia/Shanghai）ARCH-OBS-001 r12 操作手册

命名 Development `obs_r12_development` 按 [r12 §14](spec.md#r12-user-guide) 实施。正式交付对象为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树，基准 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，以当前工作树差异交付。仅新增双语手册、在双语文档索引各增加一行并追加本节。

### 实际文件

| 对象 | 内容 | 文档 SHA-256 |
| --- | --- | --- |
| [中文手册](../../docs/equipment-status-process-monitoring-guide.zh-CN.md) | 私有 profile、加热区、指标、两路槽、卡片／曲线、两路上报、数据列表和能耗 | `ee52df91fdf7556cd25d58564444ebe8806c67514d485ed3e0d0fe064e20c6a5` |
| [英文手册](../../docs/equipment-status-process-monitoring-guide.md) | 与中文版对应的操作和示例 | `4260bc998961a9abedce43bff812c3f911eea7d3eca635815833e00ca14e8d9e` |
| [中文索引](../../docs/README.zh-CN.md) | 新手册索引 | `a663bfebdf28f4c139d7568a7976a7ba46a637d5766b38de1fb2c1d5a2ca6a0e` |
| [英文索引](../../docs/README.md) | 新手册索引 | `523e5fb7b4a7beed573215f23ade9b3d8abb4fee36ec4a250a51caa0c0fc7876` |
| 本 `tasks.md` | 追加本轮 DEV 自检和交接 | 当前节 |

### DEV self-check

| 检查 | 命令和实测结果 |
| --- | --- |
| 表单与合同走读 | 使用 `rg -n`、`sed -n` 和 `node` 读取侧栏 manifest、配对 locale、设备配置和记录、过程曲线、能耗统计及表计组件；对照 `profile.py`、`machine_openapi.py`、`configuration.py`、`energy_statistics.py` 和 v2 合同。确认区域、卡片、曲线复用了不同含义的「指标键」，槽位采样组需手填，曲线任务号为输入框，表计配置查询后方可新增，能耗样本列在表计配置设置。 |
| 双语、链接、示例和路径 | `python3 -` 内联静态核验退出 0，16 个相对链接（含双语索引行与 r10 锚点）可达；两稿均有 7 节、共 4 段可解析的 JSON，正文和命令示例成对一致。5 条方法／路径匹配发布 OpenAPI，核对三路 POST 的必填／可用字段、采样偏移、质量、区间顺序及示例键值。占位域名为 `observation.example.invalid`，所有机器请求仅引用令牌变量。 |
| Shell 语法 | `python3 -` 提取代码围栏逐段运行 `bash -n`，6/6 语法检查退出 0。 |
| 差异、字节与范围 | `git diff --check -- docs/README.md docs/README.zh-CN.md plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md`，新手册另检查行尾空白。两份索引各 1 行新增。比较原任务记录 SHA-256，确认原字节为本文件的完整前缀。获批 spec SHA-256 为 `02c43085ec3ce66dc77101ff847d2a4ebd559aeafd2062808401a394d0f27adb`，既有 checklist SHA-256 为 `5de37a7bbfb528d897f17458ab85ce6825b266c85b676aa14c5c75c58904bcea`。 |

### r12 developer_handoff

交 fresh-context 命名 Verification，按 [r12 §14](spec.md#r12-user-guide) 的 R12-AC01–05 核对上述工作树、五项文件及本节实际记录。并行工作以自身差异为准。验证仅限源码与文档静态核对，未执行 HTTP、浏览器流程、数据库、迁移、配置修改、服务、Docker 或设备操作，无临时运行资源。使用者仍需由环境负责人配置真实授权范围，替换合成键、占位地址与时间。本轮证据仅覆盖手册，历史执行限制沿用原记录。独立 QA 与 Human Owner 最终验收各自待后续角色记录。
