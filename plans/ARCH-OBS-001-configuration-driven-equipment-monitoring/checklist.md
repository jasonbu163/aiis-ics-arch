Task ID: ARCH-OBS-001
Revision: r11
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r11 §13 续办范围 qa_passed；交 Human Owner 最终验收，原 R10 其余未穷尽条件继续保留
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r11 §13.2–13.4 R11-AC01–06，及 QA4 所列 R10-AC01–11 已证／未证边界；contract_only

# r11 QA2 独立 Verification：qa_passed

2026-11-17（Asia/Shanghai）。本轮由新的 fresh-context Verification 接收 R11-QA-001 返工 handoff；独立读取项目契约、角色合同、任务 bundle、相关源码／差异和可用测试输出，按 `aiis`、`project-governance`、`backend-arch`、`frontend-ui`、`i18n-workflow`、`docker-expert`、`docker-project-ops` 的适用边界验证，仅维护本 checklist。Human Owner 对 r11 §13 的批准见 [§13.6](spec.md#r11-approval)。**R11-QA-001 已按下述实际授权复验关闭；R11-AC01–06 在本次获批续办范围通过，最终 verdict 为 `qa_passed`。** 未发现需要返回 Development 的新实现 failure。原 r10 QA4 `qa_blocked` 及 r11 QA1 `qa_failed` 均按历史事实保留；本轮不自动把原 R10-AC01–11 全部改判通过，也不代表 Human Owner 最终验收。

## 精确交付、环境与隔离

- 工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，工作树另有并行变更，未归入本任务。核对 spec SHA-256 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`、tasks SHA-256 `ca0e06030c2507fdea23e8e141752736d9ba866639d06d6c4b31bf3c8b1b5ffe`、写入本节前完整 checklist SHA-256 `0b45a548c236245b20816d061827465186d49113077821a2be0d7a45d167c959`；按 tasks 有序清单逐项核对正式源码 65/65，清单摘要 `b3d52719cb1c99c329ac015e1bb5886efb3b86837481989b4d886b80d9dd194f`；临时材料 34/34，清单摘要 `b05b4590ef9e70cbda98e7c7f3029933fa9dfd433c69d5983174b5cfed7fef03`。副本清单中 507/507 文件字节同时与交付源码一致；副本另有 10 个先前存在且未列入源码清单的 `.pyc`，逐个与对应源码编译代码结构比较一致。后续进程设置 `PYTHONDONTWRITEBYTECODE=1`、`PYTHONPYCACHEPREFIX=/dev/null`，不依赖这些字节码；未读取真实 `.env` 或私有 profile。
- macOS 15.7.7 / Darwin 24.6.0 arm64，项目虚拟环境 Python 3.13.3、uv 0.7.8、Docker 29.7.2；隔离实例 MySQL 8.4.6、`linux/arm64`、上海偏移 28800 秒。沙箱中只读 `docker inspect` 返回 socket permission denied；经受控提升后核验并进行本次获批目标操作。完整容器 ID `58c935ee29f4e782204fb20a1866a4f0733a882cb68da4df84b0a26ef9f01c40`，名称 `arch-obs-r10-qa-20261117-a1`，镜像 `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`，宿主绑定仅 `127.0.0.1:13316`，MySQL UUID SHA-256 前缀 `c6c91aa0c925`。datadir 为独占 tmpfs；仅本任务 `/private/tmp/arch-obs-r11-8O97SDOg/root-secret`、`root.cnf` 以只读 bind 挂载。标签 `org.aiis.task=ARCH-OBS-001-r11`、`org.aiis.owner=09288a7cd3c808268127fc4b07092011` 与所有权记录相符。目录为 0700，检查的凭据为 0600；不输出凭据。桥接网络不等于完全网络隔离。
- 逐库直接连接实际账号并读取 `SHOW GRANTS FOR CURRENT_USER()`：`@@partial_revokes=0`、`CURRENT_ROLE()=NONE`，恰为一条全局 USAGE 与三个下划线经字面转义的 schema 授权，每个权限精确为 `SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, LOCK TABLES`；旧的未转义范围不存在，三个合法库均可连接。这关闭 R11-QA-001。相似名字仅做字符串 LIKE 正反例，没有创建、连接或声称拒绝了其他实际数据库。
- 每次合成迁移、写入、标记、受控恢复及监督检查前核验容器、实际 UUID／版本／时差／schema／账号／授权及相应写入方状态；活动写入方负例有意保持一笔本任务事务并撤销。运行配置由清空后的显式环境提供，数据库 settings 异步／同步地址均指向本任务回环端口及 schema，其他数据库禁用；`.env` 解析路径为副本内不存在的文件。未连接或操作 3307 dev、其他容器、真实配置、现有服务、SMA／DAA／PLC。

## R11 验收结果

| 验收 | 独立结果及精确边界 |
| --- | --- |
| AC01 范围与隔离 | **通过本轮操作范围。** 精确批准、候选、容器／镜像／端口／UUID／挂载／账号、三个 schema 和写入前静默检查如上；R11-QA-001 已关闭。实际跨 schema 拒绝未测试，桥接网络不宣称完全隔离。 |
| AC02 带旧行升级 | **通过本轮合成数据范围。** main 初始 r8 的 11 张表全部行和 `SHOW CREATE TABLE` 与基线一致；5 个 r8 原请求按旧 `normalize`／`fingerprint` 函数重算，指纹、source key、回执及结果 ID 5/5 一致。独立运行正式在线 Alembic `8c0e2a4d6f18 → 9d1f3a5c7e20` 退出 0。六张 r8 归档逐行一致，按表名和 MySQL 自动外键名变更规范化后完整 DDL／索引／约束 6/6 一致；四张新配置表逐行一致。三条历史事件逐行核对 ID、设备、任务、真实合成采样微秒、质量、来源键、回执、值、备注、复核及创建／更新时间，未合并两条同刻事件；新实时表初始 0。五条旧回执原字段、v1/r8 标记一致；旧能耗量／曲线／价格／小时价格四表的行和 DDL 均一致。新表主键、唯一键、任务／时刻和外键索引以 `information_schema.STATISTICS` 独立读取。旧时间为自造、明确的上海原采样时间。 |
| AC03 旧回执 | **通过本轮合成重放范围。** 使用真实 FastAPI 路由、真实 Bearer 认证和隔离 MySQL，五份原请求各重放两次，均返回原 outcome／recordId、`resultVersion=r8` 及对应 latest/history 归档位置；回执／新快照／过程／两归档计数前后均为 `(5,0,3,2,3)`。另提交新 r10 实时事件 ID `1`，与旧档案 ID `1` 同时存在且按表可区分。为避免写入其他文件，合成 profile 经正式 `parse_profile` 在内存解析后注入路由，未覆盖真实 Bearer 校验或 DB；这不验证 profile 文件加载，也不是回环 HTTP、SMA 产品或来源血缘证明。 |
| AC04 保全恢复及保护 | **通过本轮合成场景。** main 写入新快照及新指标／槽／卡后，六张 r10 表的恢复前合成行摘要 `53606aa2305ec227c90b08a1383f9dd7d7b7a2df81df9184372a85359d30cbe9`；正式带 `obs_r10_writers_quiesced=yes` 和 `obs_r10_restore_preserved=yes` 的在线 downgrade 退出 0。六张 r8 原表全部行及原 DDL 复原，六张 `_r10_preserved` 表逐行等于恢复前，含新样本和配置；四张旧能耗／价格表不变。r10 新增表仍保留，不能表述为彻底清除 r10 或现场回退就绪。guard 中保持活动合成事务并不给静默确认，正式迁移拒绝；另测旧时间未确认、归档目标碰撞及恢复目的地碰撞均拒绝、revision 和已核对数据不变；仅对自建、空、DDL／无引用核准的归档标记精确删除，恢复标记留存。迁移本身依赖显式静默确认，此负例不证明给出虚假确认时会自动识别写入方。recovery 中真实六表原子 `RENAME` 后立即注入受控异常，revision 仍 r8，六旧名消失、六归档的行及 DDL 与基线一致，旧回执保留；一次明确监督的守卫复验因归档已存在拒绝，版本、全部表名、归档行／DDL 和回执不变。该异常不是断电、进程强杀或全部 DDL 故障证明；未 stamp、盲目重试或自动清理现场。 |
| AC05 双语说明 | **通过静态文档范围。** 两份前端 README 的工作树 diff 只触及指定来源说明；四设备路由指向 cards，三类过程路由指向 curves，当前页面不使用该 URL 来源切换；中英文均指向各自语言的 v2 合同及 r10 指南，四个新增本地目标及显式锚点可解析，`git diff --check` 退出 0。此项不等于重新运行浏览器或真实来源接入。 |
| AC06 交接与资源 | **通过本轮交接及回收范围。** 与 Development 自检分离并保留原 QA 完整字节；协调者依 §13.2 核实并回收指定容器和专属目录，Verification 独立只读确认容器、监听和目录均不存在，详见下方回收复核；最终验收由 Human Owner 决定。 |

## 命令及证据方法

- `git rev-parse HEAD`、`git diff -- frontend-js/README.md frontend-js/README.zh-CN.md`、`git diff --check -- ...`、内联 Python 的 SHA-256／本地链接及显式锚点检查：退出 0；只计 65 项交付和两份直接说明，不把并行工作归入。
- 只读 `docker inspect`、`docker image inspect`、`backend/.venv/bin/python -B /private/tmp/arch-obs-r11-8O97SDOg/audit_grants.py` 及独立 PyMySQL `SHOW GRANTS`／目标／角色／时差／静默检查：提升后退出 0。迁移前 main r8，11 张基线表行数依次为实时 2、过程 3、回执 5、指标 2、槽 4、卡 1、曲线 1、旧能耗量／曲线／价格／小时价格各 1；guard/recovery 空。合成基线 SHA-256 `1cfdaad0f872e8d26a16b645fdc50cfaec13029684797cee3b2b7adde07bfa22`，历史 r8 函数参考 SHA-256 `2e0ded43b9f002577b8c2e17732dbb6d30f2f64765c84d7076d2a45b1c02ea34`；前者的 11/11 行集／DDL 与真实 MySQL 对账，后者三项函数 AST 与当前 replay 一致。
- 在仅含显式变量的环境及核验过的临时源码副本中，使用项目 `.venv/bin/python -B -m alembic -x obs_r10_writers_quiesced=yes -x obs_r10_legacy_time_basis=verified_shanghai_observed upgrade 9d1f3a5c7e20` 执行 main 正式在线迁移，退出 0；之后独立 Python／SQL 逐行、DDL 和索引对账，退出 0。真实 SQLAlchemy/MySQL 数据，非 SQLite 或离线 SQL。
- 内联 Python 以正式 `parse_profile` 创建进程内合成配置，通过 `httpx.ASGITransport` 调实际机器路由、真实 Bearer 校验和实际 MySQL：旧请求 5×2、新样本和合成配置退出 0；无外部 HTTP socket，未运行 SMA。
- 同环境执行 `python -B -m alembic -x obs_r10_writers_quiesced=yes -x obs_r10_restore_preserved=yes downgrade 8c0e2a4d6f18`，退出 0；恢复前后逐表全行对账退出 0。guard/recovery 分别用 `python -B -m alembic upgrade 8c0e2a4d6f18` 从空库走完整正式链并用独立内联事务导入／对账 11 表合成基线，均退出 0。guard 的各拒绝命令按实际预期退出 1，精确检查错误文本并核对状态；自建归档标记 DDL SHA-256 `c93efb9a3dc404730d3505d8ebabc735bf46f2929213d8b17d2f76cac185b3fe`，恢复碰撞标记 DDL SHA-256 `1d651b9d7f6530b98c11a952e9cf6471b9c8a27e05d244eeef5c339782331369`。recovery 的受控 `qa_interrupt_child.py` 在真实 RENAME 后按预期退出 1，唯一一次监督守卫复验也按预期退出 1，均保留实际部分状态。
- 本轮没有重跑 QA4 的浏览器、前端构建、85 项模块测试或后端 147 项 no_db 测试；其命令／结果仅作为下方历史证据，不写成本轮实测。合成验证和 QA4 证据均不能代表现场或生产证明。

## 原 R10-AC01–11 仍需保留的边界

| 项 | 与 QA4 对照后的状态 |
| --- | --- |
| AC01 | 先前合成来源和部分鉴权有证；并发、完整身份／权限矩阵及实际 SMA 产品未证。 |
| AC02 | 先前整包、缺测、0／false 与浏览器断点有证；完整配置与异常组合未穷尽。 |
| AC03 | 本轮补得隔离 MySQL 上旧指纹、归档定位、无重复及重叠 ID 证据；原项其他竞争及完整组合不能因此自动判为全部通过。 |
| AC04 | 本轮核对迁移后表和索引；能耗槽 100／101、跨连接首用及全部旧槽解码仍未独立穷尽。 |
| AC05 | QA4 的实际 SFC 合成任务选择证据保留；真实浏览器多设备、同刻、重载及轮询组合未穷尽。 |
| AC06 | QA4 的合成累计 6／增量 5 证据保留；跨日、换表／重置及全部缺测未穷尽。 |
| AC07 | QA4 的合成 operator 和管理入口证据保留；全部授权矩阵及浏览器管理保存未穷尽。 |
| AC08 | QA4 的正式空态及独立 Vite 合成链证据保留；失败重试、所有已配置空图及完整动态导入链未穷尽。 |
| AC09 | 本轮补得带旧行的实际在线迁移、逐行／DDL／旧能耗价格保全和受控恢复、中断保护；旧统计切换／重复统计及其他 QA4 未穷尽条件不因本轮自动通过。 |
| AC10 | 本轮补正并静态核对两份前端说明；全部文档链接和相关回归仍未穷尽。 |
| AC11 | QA4 的 no_db、合成 MySQL／HTTP、浏览器断点证据保留；全部类别／时序精度、真实 DAA／跨 DB 未验证。 |

## 结束前资源状态与交接

最后只读清点时三个 schema 均无活动事务或其他活动 SQL；QA 所有测试进程和连接已关闭，未创建临时 profile 文件，本角色已结束对容器和私有目录的使用。`obs_r11_main` 为 r8 revision、73 表，原实时／过程／回执 2／3／6，六张 r10 保全表分别为实时 1、过程 3、指标 3、槽 5、卡 2、曲线 1；r10 额外表仍在。`obs_r11_guard` 为 r10 revision、74 表，空的自建 `equipment_status_r10_preserved` 碰撞标记保留。`obs_r11_recovery` 为 r8 revision、64 表，六张 r8 归档保留且旧原表名不存在，是有意制造的中断现场。它们均只含本任务合成数据，不能据此推断其他目标状态。

供协调者按既有批准核对及回收的精确对象：完整容器 ID、镜像、两个标签、回环绑定、tmpfs 和两项只读挂载见上文；唯一任务私有目录为 `/private/tmp/arch-obs-r11-8O97SDOg`。关键脱敏对账、命令、约束、结果和限制已持久写入本节，不以临时文件作为唯一证据。协调者应重新独立核验容器／目录归属、无活动写入和无后续依赖，再仅回收该容器和目录；不触及其他容器、卷、服务或真实配置。完成后请反馈实际结果，由 Verification 独立只读核验并记录最终 verdict；Human Owner 最终验收仍待其本人决定。

## 最终回收复核与 verdict

协调者反馈：回收前重新核对本节完整容器 ID、名称、镜像、task/owner 标签、端口、独占 tmpfs、两项只读任务挂载、MySQL UUID SHA-256 前缀及无活动 SQL／事务；对该精确 ID 执行 `docker stop`、`docker rm` 均退出 0，再核对专属目录及 ownership 后精确移除目录和其中临时凭据。协调者报告未操作其他容器、卷、3307/dev 或项目配置。

本 Verification 随后独立只读复核：Docker server `29.7.2` 可响应；对完整 ID 与名称分别执行 `docker inspect --type container` 均退出 1 且为 `No such object`；`/usr/sbin/lsof -nP -iTCP:13316 -sTCP:LISTEN` 退出 1、无输出，表示无监听；`/private/tmp/arch-obs-r11-8O97SDOg` 不存在且不是符号链接。首次组合只读复核在已确认容器不存在后，因精简 PATH 未含 `/usr/sbin` 找不到 `lsof` 而退出 1；补全 PATH、以绝对路径只读复核端口与目录后退出 0，该问题不涉及容器或数据写入。回收前后的关键脱敏数据及限制均已保存在本节。

**ARCH-OBS-001 r11 §13 的独立 Verification verdict：`qa_passed`。** R11-AC01–06 和 R11-QA-001 的返工复验按上表在获批合成范围完成，无新实现 failure。此 verdict 交 Human Owner 作最终验收；它不授予 Owner 验收，也不将原 R10-AC01–11 的未穷尽条件、实际 SMA／DAA／PLC、现场或生产采用自动判为通过。原 r10 QA4 的旧数据隔离缺口已有本轮补测，历史 `qa_blocked` 记录不被改写。

以下是写入前完整 checklist 原始字节，SHA-256 `0b45a548c236245b20816d061827465186d49113077821a2be0d7a45d167c959`；原 r11 QA1、r10 QA4 及更早所有证据和 verdict 不变。

---

Task ID: ARCH-OBS-001
Revision: r11
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R11-QA-001 隔离准备问题返回 Development；新 developer_handoff 后由 fresh-context Verification 重验；Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r11 §13.2–13.4 R11-AC01–06，并复核 QA4 中 R10-AC01–11 的覆盖边界；contract_only

# r11 独立 Verification：qa_failed

2026-11-17（Asia/Shanghai）。**Verdict：`qa_failed`。** 写入前只读预检发现指定隔离实例测试账号的数据库级授权具有通配符范围，不能证实交接所称仅授权三个精确 schema。该问题属于 **Development 的临时测试环境准备和交接**，不是本次发现的业务源码实现缺陷。按 §13 的权限最小化和身份不一致即停止规则，本轮未执行任何迁移、合成写入、重放、降级、碰撞构造或清理；因此 R11-AC02–04 及原 R10-AC03/09 的旧数据路径仍未验证，不能以工具准备或下列只读检查代替实测。目标保留，交 Development 在已批准 r11 范围返工；之后须固定新 handoff 并由新的 fresh-context Verification 独立复验。最终验收由 Human Owner 决定。

## R11-QA-001：测试账号的 schema 授权并非精确名称

- 当前测试账号以 `SHOW GRANTS FOR CURRENT_USER` 只读返回 4 条授权：一条全局 `USAGE`，以及分别对 `obs_r11_guard`、`obs_r11_main`、`obs_r11_recovery` 的数据库级 `ALL PRIVILEGES`；三条授权的名称均含**未转义的下划线**。例如脱敏后的范围为 ``ON `obs_r11_main`.*``；无全局 ALL 权限。只读 `SELECT @@partial_revokes` 结果为 `0`。
- [MySQL 8.4 GRANT 官方说明](https://dev.mysql.com/doc/refman/8.4/en/grant.html)规定：在数据库级授权且 `partial_revokes` 未启用时，未转义的 `_` 是匹配单个字符的通配符，而不是固定下划线。因此这三条授权还匹配其他相应名称；这与本轮 [Development handoff](tasks.md) “仅对三个 schema 授权”的声明不一致，也不满足 §13.2 的最小权限目标。MySQL 8.4 已弃用该通配符功能，但当前实例仍按上述语义处理。
- `SHOW DATABASES` 在该测试账号下只显示三个任务 schema、`information_schema` 和 `performance_schema`；本轮**没有发现**额外匹配的实际 schema，也没有创建其他 schema 测试通配符，更不声称有任何现有 dev 数据被访问。桥接网络不是完全隔离，授权模式仍须准确收窄。
- 检查临时准备材料 `initialize_target.py:21` 和 `create_target.py:66` 可见按原 schema 名直接生成数据库级 GRANT，未转义 `_`；这解释了上述观测。问题定位于一次性测试资源准备，**未判定业务迁移／API 实现失败**。Verification 未修改授权、辅助脚本、源码或配置。
- 返工应在获批的同一任务范围内把账号权限限制到三个精确 schema，记录实际修改和独立可验证的精确授权状态，重新固定临时材料与候选身份并交新的 Verification；若需要改变目标、范围、验收或风险，回 PM 修订并重新批准。不得借本问题访问 3307、其他容器或真实服务。

## 交付身份与只读证据

- 初始 `shasum -a 256 .../{spec,tasks,checklist}.md`：分别为 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`、`da0c2bc14802c8893342e5429ec20a13df338fcb867d3bd591526ff7308cb8a9`、`7599d30b39d3b1b98e915bc06348b0e83e23f17b4bad8ee16fbb5e4e1e704830`；均与本次精确交接相符。按 tasks 的行序重新计算：正式源码候选 **65/65** 匹配，清单整体 `b3d52719cb1c99c329ac015e1bb5886efb3b86837481989b4d886b80d9dd194f`；临时材料 **27/27** 匹配，整体 `0f953351c0c43e7ff046b5e7d4e3b324dd72f25191c4a4e49a1c5f1ea60a5a6d`。临时源码清单 **507/507** 同时与正式工作树对应文件和清单摘要一致。工作树有并行修改；未把清单外内容归入本候选。
- macOS Darwin arm64；MySQL `8.4.6`、`linux/arm64`。沙箱内 `docker inspect` 对 Docker socket 返回 `permission denied`；获准提升后对完整容器 ID 只读 `docker inspect --format ... 58c935ee29f4e782204fb20a1866a4f0733a882cb68da4df84b0a26ef9f01c40` 退出 0：名称、镜像 `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`、运行状态、`127.0.0.1:13316` 绑定、独占 datadir tmpfs 相符。只读检查标签、两个只读凭据 bind mount、容器 hostname、实际 UUID SHA-256 前缀 `c6c91aa0c925` 与 +08:00 数据库时差相符；不把 bridge 说成完全隔离。私有目录 `0700`，ownership 及检查的三个凭据文件 `0600`，所有者为当前用户；未输出凭据。
- 对同一目标执行审阅过的 `backend/.venv/bin/python /private/tmp/arch-obs-r11-8O97SDOg/audit_final.py`，提升后退出 0：`obs_r11_main` revision `8c0e2a4d6f18`；旧实时 2、过程 3、回执 5、指标 2、槽 4、卡片 1、曲线 1，旧能耗量／曲线／价格／小时价格各 1；`obs_r11_guard`、`obs_r11_recovery` 均无表且无 revision。基线 SHA-256 `1cfdaad0f872e8d26a16b645fdc50cfaec13029684797cee3b2b7adde07bfa22`。
- 另以只读 Python/SQL 独立读取基线中 **11/11 表全部行及 SHOW CREATE TABLE** 并与已持久基线逐项比较，全部相符；核实主 schema 时点上开放事务和其他活动语句各 0。提取历史 r8 文件的 `_fields`、`normalize`、`fingerprint`，与当前 v1 实现 AST 比较 3/3 一致；按旧函数从五份合成原请求重算的指纹与基线及 MySQL 回执 **5/5** 相符。这是迁移前只读证据，**不是**迁移后回执重放证据；合成 task evidence 不证明真实来源血缘。
- 我的首次只读授权断言要求授权名的下划线经转义，退出 1 并报告 `unexpected grant scope`；随后用 `SHOW GRANTS FOR CURRENT_USER`、`SELECT @@partial_revokes`、`SHOW DATABASES` 分别只读核对并确认上述 R11-QA-001。该失败没有导致重试写入。初始身份审计和本轮其余操作均未连接或复制 `127.0.0.1:3307` 的 dev 数据。

## R11 验收结果

| 验收项 | 本轮独立结果 |
| --- | --- |
| AC01 范围与隔离 | **失败：R11-QA-001。** 容器、镜像、端口、UUID、schema、目录权限和源码副本检查如上；测试账号授权范围不能证明仅限三个精确 schema，停止后续写入。 |
| AC02 带旧行升级 | **未执行。** 仅完成 r8 旧数据 11 表逐行及 DDL 只读基线对账；没有执行正式在线 r8→r10，也没有迁移后索引和数据比较。 |
| AC03 旧回执 | **未执行。** 5/5 旧指纹在迁移前重算匹配，但没有运行 ASGI 或 HTTP、旧请求重放、ID 重叠及无重复写入测试。 |
| AC04 保全恢复及保护 | **未执行。** 未创建新样本／碰撞，未做恢复、未静默／时间守卫或真实 DDL 中断测试；没有清理、stamp、自动重试或修改授权。 |
| AC05 双语说明 | **通过本次文档范围检查。** 对比正式工作树与 HEAD 的两份 README，只有指定观察来源说明改变；其前后无关内容字节一致。四设备路由指向 cards，三类监控指向 curves，相关页面调用现行 observation API 且未发现 URL 数据源切换；v2 合同注明来源无关、不能声称 SMA/PLC 已接入。两语言各两个新增本地链接存在，两个 r10 显式锚点可解析；`git diff --check -- frontend-js/README.md frontend-js/README.zh-CN.md` 退出 0。此项不证明页面运行或产品接入。 |
| AC06 交接与资源 | **部分完成。** 本记录与 Development 自检分开，QA4 及更早完整原文字节附后；未回收容器或临时目录，待返工／新 QA 的证据依赖解除后由协调者按已批准流程核身份再处理。Human Owner 最终验收未进行。 |

## 原 R10-AC01–11 的复核边界

本轮没有重跑 QA4 的浏览器、HTTP、SFC 或 no_db 测试，以下仅按附后的 QA4 原记录保留其已证及未穷尽状态，不提升为全面通过：

| 项 | QA4 保留状态及尚缺 |
| --- | --- |
| AC01 | 部分：合成来源及部分授权已测；并发、完整身份矩阵和 SMA 产品未证。 |
| AC02 | 部分：整包、缺测、0/false 及浏览器断点有证；完整配置与异常组合未穷尽。 |
| AC03 | 部分且旧回执阻塞：普通重试等有证；r8 旧指纹迁移后重放、归档定位及无重复写仍缺。 |
| AC04 | 部分：三表及部分能耗配置有证；能耗槽 100/101、跨连接首用和旧槽解码未穷尽。 |
| AC05 | 部分：实际 SFC 合成任务选择有证；真实浏览器多设备、同刻、重载及轮询组合未穷尽。 |
| AC06 | 部分：合成累计 6／增量 5 有证；跨日、换表／重置及全部缺测未穷尽。 |
| AC07 | 部分：合成 operator 和管理入口有证；全部授权矩阵及管理保存未穷尽。 |
| AC08 | 部分：正式空态及独立 Vite 合成数据路径有证；失败重试、所有已配置空图及完整动态导入链未穷尽。 |
| AC09 | 阻塞：旧数据带行在线迁移、恢复与中断处理仍未实际验证。 |
| AC10 | 部分：QA4 保留的证据与本轮 AC05 文档检查分开；未穷尽全部链接和回归。 |
| AC11 | 部分：no_db、合成 MySQL/HTTP 和浏览器断点有证；全部时序精度及真实 DAA／跨 DB 未验证。 |

## 资源与 handoff

隔离容器 `58c935ee29f4e782204fb20a1866a4f0733a882cb68da4df84b0a26ef9f01c40` 仍运行；任务专属 `/private/tmp/arch-obs-r11-8O97SDOg` 保留。主 schema 仍为 r8 基线，另外两个 schema 在只读审计时为空；本轮未清理、更改账号、迁移或写入数据库。容器及目录是返工／复验依赖，协调者在新 QA 结束、证据持久化并确认无依赖后，按完整 ID、镜像、标签、挂载、端口、UUID 和写入方重新核验，才可按既有获批范围回收。目标状态若发生变化须先重新审计，不按名称自动清理。

将 R11-QA-001 返回 Development；其新 handoff 后重新启动 fresh-context Verification 执行 §13 未完成的独立实测。结果交 Human Owner 作最终验收；本结果不代表 Human Owner 已接受、真实 SMA／DAA／PLC、现场、生产部署或发布。下方原 QA4 checklist 在本轮写入前 SHA-256 为 `7599d30b39d3b1b98e915bc06348b0e83e23f17b4bad8ee16fbb5e4e1e704830`，其全部原字节及先前历史保留，QA4 仍为 `qa_blocked`。

---

Task ID: ARCH-OBS-001
Revision: r10
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R10-AC09 带旧数据的迁移和恢复、R10-AC03 的真实旧回执路径缺少获准隔离目标；交 Human Owner／协调者决定后续验证，最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r10 §12.9 R10-AC01–11；contract_only

# r10 QA4 独立 Verification：qa_blocked

2026-11-17（Asia/Shanghai）。实际命名的 Verification 使用 fresh context，独立核对工作树、角色合同、r10 bundle、相关实现、公开合同、diff 和测试；按 project-governance、aiis、backend-arch、frontend-ui、i18n-workflow、code-document-indexer 的适用验证边界工作。本轮只维护本 checklist；各项测试证据与 Development 自检分开，保留此前全部失败及历史。Human Owner 批准的范围和目标见 [spec §12.10](spec.md#r10-approval)。

**Verdict：`qa_blocked`，不是 `qa_passed`。** QA3 的 R10-QA-008、009 原复现已关闭；本轮未确认新的范围内实现失败。R10-AC09 要求带旧值的保全迁移和恢复，以及 R10-AC03 旧回执实际重放：指定 dev 当前旧 OBS 行和回执为空，已有授权不包括另一个数据库或 Docker；在现存 dev 装入旧数据再降级/重升会影响已采用目标，不能安全替代隔离验证。须有 Human Owner 明确批准的隔离实例、一次性 schema 和可销毁范围后复验；隔离方案见下。其他未穷尽项在逐项表中列明，不将缺少证据写成通过。结果只交 Human Owner／协调者进入下一 gate；不代表 Owner 最终验收或 SMA、DAA、PLC、现场及生产接入。

## 精确候选、环境与旧缺陷

- 交付工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；工作树有与本任务并行的其他修改。批准 spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`，Development tasks SHA-256 `5cf8f8b6d79998ec1f507202e45c6306bbaee47d4026b2f220c8ebb5cf87287b`，写入前 checklist SHA-256 `c71a6ff741600b5db30e96cd9bc58ceaa1c8eda411bde26715096181775d7b11`。按 tasks 的有序清单逐项复算 **63/63 匹配**，清单整体 `8512aaecbd8610cae2d44cf02014b7bb643dddea48bf0876d4866d5eb41fb6ea`；没有把其他并行变更归入候选。
- macOS 15.7.7 arm64、Node 22.19.0、pnpm 11.11.0、uv 0.7.8、锁定 Python 3.13.3。指定 `127.0.0.1:3307 / industrial_level_2_system` 只读确认 MySQL 8.4.6、UUID SHA-256 前缀 `ac2319a3fdc8`、唯一 revision `9d1f3a5c7e20`、时区偏移 28800 秒。沙箱普通连接返回 `Operation not permitted`；经受控提权后只读核验及明确获批的合成联调成功。每次创建合成对象前核对目标及活动写入方，所见活动 SQL、最近五分钟采集事实、开放事务均为 0；这只是当时观测，非未来写入保证。
- **R10-QA-008 原复现关闭。** [模块英文 README](../../backend/app/equipment_observation/README.md) 与[中文 README](../../backend/app/equipment_observation/README.zh-CN.md) 均将 v2 描述为来源无关当前合同，`observedAt`、三主表、设备／表计权限与独立能耗清晰；v1 与任务点证据标作历史重放边界，不宣称已完成 SMA 产品或 PLC 接入。
- **R10-QA-009 原复现关闭。** 独立 Node 内存脚本编译执行正式 [EnergyAdmin.vue](../../frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue) 的实际 setup，以可控 Promise 依次模拟 A→B 表计逆序、组 two→three 逆序和第 2→3 页逆序：最终各显示 B／three／第 3 页。将 B 配置表单身份改成 A 后保存，实际调用目标仍为 B/G/reading；样本表单改 ID 后保存实际目标仍为打开时的 B 行 ID。旧 A 响应未覆盖 B。独立重跑模块测试还覆盖迟到错误、取消编辑、保存竞态及旧配置不能为新表计发重复样本请求；这是实际 SFC 逻辑＋合成 API，不将其说成正式浏览器网络乱序实测。
- QA1–QA3 的既有复现及后续结果保留于下方原文；本轮 85 项模块测试中包括旧微秒、授权重放、列顺序、双语区域名、统计页竞态、过期时间与同名图例回归。独立 SFC 测试另验证手选 A 遇新最近 B 仍保持 A，恢复跟随后显示 B，切设备后清手选并显示 C；该测试是合成状态与实际组件，不是完整多设备浏览器证明。

## R10-AC01–11 独立结果

| 验收 | 本轮结果、证据和剩余边界 |
| --- | --- |
| AC01 来源与授权 | 部分验证：真实回环 HTTP＋指定 MySQL，任务独有 external 与模拟 SMA 身份完成发现和两路写入；未知空组拒绝，缩小区域／指标授权后旧事件 403，恢复后原回执一致。项目 no_db 路由夹具覆盖 other 身份及错误类型；未操作 SMA 产品，也未穷尽并发身份。 |
| AC02 整包与缺测 | 部分验证：独立 HTTP 每轮四份整包产生最新 1 行、历史 6 行，包含空整包缺测、禁用历史指标 skipped 和 0／false 的相关测试；实际 API 查询到的缺测在浏览器图中形成断点。完整配置矩阵和所有异常未穷尽。 |
| AC03 幂等／旧回执 | 部分验证，旧数据路径阻塞：本轮两路重试、权限撤销／恢复和历史微秒样本在真实 MySQL＋回环 HTTP 验证；no_db 夹具含合成 v1 原回执。当前目标没有真实 r8 存量回执，未独立验证带原旧指纹、归档定位及无二次写入的迁移后重放；隔离要求见下。 |
| AC04 三表／配置 | 部分验证：代码／迁移及定向测试检查三表、真实时间和配置；本轮两表计同键使用累计与增量，表一同时含瞬时量，均通过真实 HTTP。能耗槽 100／101、跨连接首用竞争和全部旧槽解码未独立穷尽。 |
| AC05 任务选择 | 部分验证：实际 cards SFC 合成测试验证手选保持、跟随恢复及设备切换，no_db 测试覆盖同刻相关逻辑；浏览器使用单台合成设备。真实浏览器中的多设备／同刻／重载和全部轮询组合仍未证明；最近采样不代表生产或空闲事实。 |
| AC06 能耗口径 | 部分验证：真实 MySQL＋回环 HTTP 独立获得累计 `1006−1000=6` 与增量 `2+3=5`，并配置瞬时量；no_db 测试覆盖边界、间隔和部分质量条件。跨日、换表／重置和全部缺测组合未穷尽。 |
| AC07 页面与权限 | 部分验证：正式 5190 admin 可见模块内管理及过程／能耗数据分区；独立 Vite 的合成 admin 读取真实 MySQL 过程 6 行和两表计 1000/1006、2/3，切换区域有效。独立正式源码 API 的一次性真实 operator 登录后，进程局部授权下设备、过程、能耗读取 200，另一设备／表计各 403，三项管理 403；相同身份在无 grant 的另一进程三类读均 403。独立 Vite 登录可见授权设备及表计、绘出曲线，管理菜单不显示，管理 URL 重定向。此账户和权限仅作用于本轮临时 profile／进程，未覆盖所有授权矩阵；浏览器管理保存未在本轮执行。 |
| AC08 卡顿和空图 | 部分验证：用户正常 Chrome profile 的本轮自有标签，在正式 5190 通过四个菜单和四个直接路由进入温度、传动、清洗、能耗；当前正式 profile 无可访问设备／表计，温度空态有通用 X/Y 轴与原因。另在独立 Vite＋只读合成 admin API＋指定 MySQL 上，已配置温度图且无样本时显示范围空轴、°C 与“暂无数据”；第三方／模拟 SMA HTTP 写入后同一页面点查询，显示双区域及真实合成值，移除一区再全选可恢复。该数据到达链不是正式 5190／8000，也不是 SMA 产品。失败后重试、所有类别的已配置空图及完整动态导入故障链未独立覆盖。 |
| AC09 无损迁移／旧能耗 | **阻塞：**已只读比较当前保护表行数／checksum，并保留 QA1 对 Development 迁移快照的比较；当前旧 OBS 源和回执无样本，本轮没有带旧数据重新迁移、故障中断恢复或回退。旧能耗和价格数据仅做保全对账，未把 checksum 当作恢复证明。解除条件见下。 |
| AC10 交接／双语 | 部分验证：63 项交接摘要、模块双语 README 当前合同、locale 双语键集合和浏览器页面已核；原 QA 历史与权限／产品边界保留。前端根 README 的范围外旧描述见下，全部文档链接及相关回归未独立穷尽。 |
| AC11 原采样时间／断点 | 部分验证：项目 no_db 测试覆盖缺失／无偏移／无损微秒与同刻、顺序等；本轮真实 MySQL／HTTP 返回空样本断点、`123001`／`123002` 微秒并以合成数据在浏览器观察断点。未在正式 5190 完成全部类别的 T1 备注后移、迟到／同刻及所有精度范围；真实 DAA／跨 DB 联调未执行。 |

## 命令、环境、资源与保全

- `frontend-js/`：`pnpm_config_verify_deps_before_run=false pnpm test:modules` 退出 0，85 passed；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa4-dist` 退出 0，2262 modules；外部输出目录及大 chunk 警告保留。实际 SFC 独立可控 Promise 及任务选择脚本各退出 0。equipment 中英各 147 键、monitor 各 258 键，集合相等。
- `backend/`：`PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa4-uv LOG_DIR=/private/tmp/arch-obs-r10-qa4-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=qa_unused MYSQL_PASSWORD=qa_unused MYSQL_DATABASE=qa_unused MYSQL_ROOT_USER=qa_unused MYSQL_ROOT_PASSWORD=qa_unused TEST_MYSQL_DATABASE=qa_unused_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line --basetemp=/private/tmp/arch-obs-r10-qa4-pytest tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_energy_price_api.py`：退出 0，147 passed、1 skipped、1 warning；skip 为冻结 BE003 候选，warning 为 SQLite datetime adapter 弃用。该结果不是 MySQL 迁移证明。
- 文档链接：`python3 /private/tmp/arch-obs-r10-private.j0jFyKfK/check_docs.py` 退出 0，六份公开说明中的 150 个本地文件目标存在；另以只读 Python 检查两份模块 README 的 10 个本地路径及显式锚点，退出 0、缺失 0。前者只查文件存在，不宣称遍历所有片段锚点。
- 真 MySQL 合成验证复用经审计的 Development 夹具思路，复制和改编到本轮专属 `/private/tmp/arch-obs-r10-qa4-{http,ui,operator,arrival}-*`，不改项目 `.env`、源码或既有 profile。`PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa4-uv ADMIN_BOOTSTRAP_USERNAME=fixture ADMIN_BOOTSTRAP_PASSWORD=fixture-only JWT_SECRET_KEY=fixture-only uv run --offline --frozen --no-sync python <本轮目录>/fixture.py --execute-dev-http-fixture ARCH-OBS-001-r10` 各次退出 0。独立 API 机器 Bearer 走实际认证，配置阶段 admin 为合成身份；普通角色专场使用正式 `main:app`、真实密码验证及临时用户，权限仅由进程环境和临时 profile 指定。临时 Vite 使用正式源码的本轮副本及自有缓存，不能冒充正式 5190。
- 四轮自有合成对象和回执按随机身份、记录 ID、绑定及引用核验后清理为 0；operator 凭据仅用于进程／浏览器、账号按精确 ID 和用户名清理，未记录口令。三轮各 15 张、普通角色轮 17 张保护表前后行数／checksum 一致，含计划／实绩、采集事实、旧能耗／曲线、价格、r8 档案，普通角色轮另含 users／token_blacklist。已停止自有 API/Vite、删除各次临时 profile，Chrome 自有标签已关闭；没有改正式角色权限、重启 8000／5190、迁移数据库或访问 SMA／DAA／PLC。MySQL 自增值可能前移，未重置。关键观察已记录本 checklist；本轮临时源码副本、缓存和日志由协调者确认无依赖后回收，不是唯一证据。
- 范围外观察：未修改的 [frontend-js/README.md](../../frontend-js/README.md#business-observation-source-selection) 和 [README.zh-CN.md](../../frontend-js/README.zh-CN.md#业务观测来源选择) 仍称设备三看板及 monitor 曲线使用 URL `dataSource=legacy|http` 并默认 legacy；当前 manifest 分别指向 `observations/cards.vue` 和 `observations/curves.vue`，这两个页面不消费该参数。此根 README 不在 §12.9 明列的直接责任面，记录供 PM／协调者判断后续范围，不擅自修改，也不单凭此项扩大本轮交付。

## 带旧数据迁移的最小隔离复验提案（未授权、未执行）

当前只获准上述 dev schema；不得在 3307 另建 schema、降级或清理现有库。只读 `SHOW GRANTS` 汇总：当前应用账号有两条 grant，其中存在 `ALL PRIVILEGES`，没有全局 `*.*` ALL；这不能证明对另一目标有创建或删除权限，也不构成授权。本机 PATH 中找到 mysql 客户端，未找到 `mysqld`。可审查的后续方案：

1. 先取得 Human Owner 对**独立** MySQL 8.4.6 测试实例、仅监听回环的空闲端口、专用临时目录／凭据及一次性 `obs_r10_qa4_<随机后缀>` schema 的明确批准；独立 UUID、端口、datadir、账号和进程配置均与 3307 dev 分开，禁止连接或复制现有真实数据。无可用独立服务端时先提供该资源；不以 Docker 或其他数据库作为未经批准的降级方案。
2. 从空目标用正式迁移建到 `8c0e2a4d6f18`，只造可追踪合成 r8 设备多组不同时刻行、同刻历史事件、槽配置、备注／复核、旧指纹回执、旧能耗与价格行；明确旧时间是上海原采样时间。快照和逐行基线独立保存并核对。未满足写入方停机、时区、旧时间依据和归档目标不存在的负例应明确拒绝。
3. 只对该隔离目标使用带 `obs_r10_writers_quiesced=yes` 和 `obs_r10_legacy_time_basis=verified_shanghai_observed` 的在线 Alembic 后继，逐项对账 r8 归档、ID／回执定位、逐组时间／值／备注、历史不合并、旧能耗／价格和旧回执重放无重复写入；验证新旧数值 ID 重叠时仍按版本定位。在新样本保全并核对后，用 `obs_r10_writers_quiesced=yes` 与 `obs_r10_restore_preserved=yes` 在相同隔离目标验证受控恢复；另对独立重建的临时目标注入中断和目标碰撞，检查显式阻止与可恢复步骤。
4. 操作前后核对 UUID／端口／schema，证据汇总写入 checklist；停止仅本次拥有的进程并核对无后续证据依赖，再按获批的精确实例、数据目录与 schema 回收。测试前不申请或使用现有库的迁移／清理权限。该计划不表示隔离资源已存在、批准已取得或迁移恢复已通过。

## Handoff

将本 `qa_blocked`、AC03／AC09 隔离验证解除条件及其余未覆盖项交 Human Owner／协调者；若后续发现实现失败，应保留证据并返 Development 后重新进行 fresh-context Verification。Human Owner 最终验收 pending。以下为本轮写入前完整 checklist 原始字节，SHA-256 `c71a6ff741600b5db30e96cd9bc58ceaa1c8eda411bde26715096181775d7b11`，QA1–3 及更早 verdict 不变。

---

Task ID: ARCH-OBS-001
Revision: r10
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R10-QA-008–009 返回 Development；返工后对新 handoff 启动 fresh-context Verification；Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r10 §12.9 R10-AC01–11；contract_only

# r10 QA3 独立 Verification：qa_failed

2026-11-17（Asia/Shanghai）。实际命名 Verification 以 fresh context 接收 QA2 返工 handoff，按根契约、canonical lifecycle、r10 规格、角色记录、实际实现与可用 diff／测试输出独立复核；按 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 的适用边界验证，仅写本 checklist。Human Owner 对精确 r10 §12 与指定 dev 目标的授权见 [spec §12.10](spec.md#r10-approval)。QA2 三项原复现及 QA1 四项相应复验见下；本轮发现 **R10-QA-008、R10-QA-009**，结论为 **qa_failed**，返 Development。未执行 Human Owner 最终验收。

## 精确候选与环境

- 正式 `main` 工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，其他任务有并行未提交改动；不将其全部归属本任务。spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`，QA2 返工 tasks SHA-256 `e28e4946ab61f95b6fceccec40913bb8695a1e1a0f3918938c4956fe6c6b7227`，写入前完整 QA2 checklist SHA-256 `673dc33d2d4c7ae146da213d1defb0c29a4f39cab9bb69ef052127910f2e1bd8`。逐项核对 handoff 清单 61/61 字节摘要一致；按 handoff 顺序的 `SHA-256  相对路径\n` 清单摘要为 `dab8569947134f5c331a1d71d111f5f86ac819b2518169cee97e41bea12104ad`。
- QA-008 涉及的模块英文／中文 README 不在这份 61 项清单中，但位于获批 `backend/app/equipment_observation/**`，且属于当前工作树的模块说明；本轮只读时 SHA-256 分别为 `1afc33de2d9186c740e66babf3142c5d07814e8d9bba5f7acef0d7d053db992e`、`c1df213dfd3976ff7d5d5254e618f6ef47277125a1339f691abcf09911e226fb`。QA-009 的 `EnergyAdmin.vue` 摘要为 `8bbb08b46eb61fed0a282944851ee8c3805aad03bd4fadcff78d4e5e9bf25b37`，在 61 项清单内。
- macOS Darwin 24.6.0 arm64、uv 0.7.8、Node 22.19.0、pnpm 11.11.0。实际 dev 目标为 `127.0.0.1:3307 / industrial_level_2_system`；独立只读核对 MySQL 8.4.6、服务器 UUID SHA-256 前缀 `ac2319a3fdc8`、上海偏移 28800 秒、唯一 revision `9d1f3a5c7e20`。沙箱内连接被系统拒绝；对明确授权目标的受限提权获准后进行只读及本轮事务测试。未输出机器凭据或私有 profile。

## QA2 与 QA1 原复现复验

| 编号 | 本轮证据与边界 |
| --- | --- |
| R10-QA-005 | **原两条复现关闭。** 独立重跑正式前端 SFC 定向测试：A/B 定义倒序和旧错误、同名指标跨组及旧样本／分页／汇总迟到均通过；另用可控 promise 驱动实际 `energy.vue`，验证指标、范围、表计切换及组件卸载后迟到响应或错误不覆盖当前状态。此结论限统计页；下方 QA-009 是管理组件的独立缺陷。 |
| R10-QA-006 | **原复现关闭。** 独立编译实际卡片模板并做双语 SSR：陈旧值 0 的原 UTC 微秒时间换算上海时间显示到秒，`false` 保留，非法时间显示 `—`；MySQL 合成读取亦返回陈旧状态与原采样时间。正式浏览器当前没有可访问设备，未观察真实账号下的有值过期卡片。 |
| R10-QA-007 | **原复现关闭。** 独立运行实际 SFC 和项目 ECharts SVG SSR，两个区域与指标显示名均相同时图例仍可区分；隐藏一区只隐藏其同刻主线和散点，二区不受影响；改语言重绘后选择保留且可恢复。正式定向测试另验证 tooltip 区域名及特殊字符转义；本轮未在浏览器复现 hover。 |
| R10-QA-001 | 原两个相差 998 微秒的输入经正式 `splitObservedPoints` 独立返回两个有序线点、0 个同刻点；ECharts 定向测试同时覆盖真正同刻、缺测和广时间范围提示。交接声明的极宽时间范围浮点坐标精度限制仍成立。 |
| R10-QA-002 | 实际路由、实际机器 Bearer 校验、授权真实 MySQL 和事务隔离的随机 `external`／模拟 `sma`／`other` 身份，分别对 latest/history 验证首次 200、原文重放 200、指标撤权 403、恢复后返回原回执；未知组与错误类型拒绝，未产生额外回执或业务行。ASGI transport 和内存 profile 不是正式 8000 的真实用户权限或 SMA 产品投递。 |
| R10-QA-003 | 正式实际 SFC 定向测试在本轮重跑通过：20／10／未指定的能耗列按 10／20／未指定排序，编辑顺序经合成 API 保存；不代表正式浏览器已经保存配置。管理组件表计切换的新竞态见 QA-009。 |
| R10-QA-004 | 正式实际路由 SQLite 夹具重新运行中英文区域名和重命名测试，实际组件区域选择使用显示名并保留稳定键；本轮 ECharts 独立测试亦验证语言变化。夹具人类身份由依赖覆盖，非正式用户权限验证。 |

## 新失败项

### R10-QA-008：模块双语 README 把历史 PLC 证据前提写成当前模块合同

关联 R10-AC01、AC10、§12 和模块长期说明。[英文 README](../../backend/app/equipment_observation/README.md) 与 [中文 README](../../backend/app/equipment_observation/README.zh-CN.md) 只链接 r8／v1，且无版本限定地声称本模块依赖 `plc_facts` 任务证据、回执保存任务点证据。批准的 [r10 §12](spec.md#r10-source-independent-energy) 和 [v2 合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md) 明确新事件无需 PLC／DAA 事实或任务点证据；本轮无 PLC 事实的三类合成身份实际通过两路写入。读模块入口的人会被引向旧合同并误认为必须建立 PLC 证据。应在返工中准确区分当前 v2 行为与历史 v1／旧回执兼容，保留历史事实；本 QA 未修改说明。

### R10-QA-009：能耗管理表计切换后旧响应可显示并保存到另一表计

关联 R10-AC06、AC07、§12.3／12.7。[EnergyAdmin.vue](../../frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue) 的 `load()` 在 `await energyConfigs(...)`、`await energyAdminSamples(...)` 后直接赋当前状态，表计 watcher 不使旧请求失效，也不核对发起时的表计、组和分页。使用项目 `vue/compiler-sfc` 编译**实际组件 setup**，以可控 promise 和合成 API 分别执行：

1. 配置模式先选 A 再选 B；B 配置先返回，A 后返回。结果 `selectedMeter=B, clickedRowMeter=A`；打开显示的 A 行并保存列表顺序，合成 `updateEnergyConfig` 实际收到目标 A，而屏幕当前选择仍为 B。
2. 样本模式先请求 A，再切 B；B 行先返回，A 行后返回。结果 `selectedMeter=B, configMeter=B, displayedRows=[A-row]`；打开该行并保存备注时，合成 `updateEnergySample` 实际收到 A 的记录 ID。
3. 当 A 的配置在 B 已选中后迟到，旧 `load()` 在第一次 await 之后还会重新读取当前 `meter.value` 发起 B 的样本请求，可能将 A 配置与 B 样本混合。

上述是实际组件逻辑和合成接口的受控乱序证据；未修改真实表计、配置或记录，也未声称正式浏览器已出现该时序。它不同于 QA-005 的统计页修复；在真实使用中可能误导管理员对另一表计配置或记录操作。返工应覆盖配置、样本、筛选／分页和迟到错误／保存身份等受影响路径，再由新的独立 QA 复验。

## 验收逐项结果

| 验收 | 本轮结果及未完成边界 |
| --- | --- |
| R10-AC01 | 部分验证：真实 MySQL 外层事务中三类合成身份发现及两路写入、未知组／类型拒绝、撤权重放通过；非全部授权、并发与真实机器组合。QA-008 的模块入口错误影响接入说明。 |
| R10-AC02 | 部分验证：本轮原值 0／false、两路写入和拒绝无额外行；先前 QA1 的整包替换、缺测和 no-history 证据原样保留，未在本轮穷尽所有情形。 |
| R10-AC03 | 部分验证：本轮三类模拟身份两路重试和撤权恢复通过；真实 r8 既存回执当前目标为空，未独立重放；跨连接竞争未证明。 |
| R10-AC04 | 部分验证：授权 MySQL 独立试验设备绑定槽 100 接受、101 被 `ck_obs_r10_binding_scope` 拒绝并回滚；能耗 100／101、并发首次使用及全部旧值解码未独立穷尽。 |
| R10-AC05 | 部分验证：实际 API 的合成过期值保留原时间，模板双语 SSR 正确；正式登录账号无设备，手选保持、跟随恢复、切设备、同刻并列及刷新未在真实浏览器独立覆盖。最近采样不代表生产或空闲。 |
| R10-AC06 | **失败：R10-QA-009。** 统计页原 QA-005 路径已关闭；前轮累计／增量样例与 no-db 结果保留。跨日、换表、重置和全部缺测组合未独立穷尽。 |
| R10-AC07 | **失败：R10-QA-009。** QA-003／004／007 原路径复验通过；正式 admin 能看到两级菜单及过程／能耗管理分区。正式普通用户权限、可配置对象的完整浏览器管理与多区域交互仍未覆盖。 |
| R10-AC08 | 部分验证：同一用户 Chrome profile 新建独占标签，温度直达；传动、清洗、能耗通过菜单及直达均打开；真实账号分别显示无设备／无表计原因，温度空图实见通用 X/Y 轴；本轮浏览器 error 日志为空。未触碰用户原标签。因正式 profile 无对象，配置存在无样本、失败重试、真实数据到达／断线及全部菜单路径仍未由本轮正式浏览器证明。 |
| R10-AC09 | 部分验证：本轮前后保护表行数与 checksum 一致；源码迁移含保全归档及恢复前置检查。当前旧相关表无样本，本 QA 未执行带旧数据迁移、真实恢复或中断恢复；Development 预演／迁移快照只是可用历史证据，不当作本轮独立执行。 |
| R10-AC10 | **失败：R10-QA-008。** v2 公开合同与双语使用说明有 r10／旧版区分，模块双语 README 未同步。61 项源码交接清单及本轮资源／授权边界已核对；未对全部文档链接做独立全量检查。 |
| R10-AC11 | 部分验证：QA-001 原微秒复现关闭，相关 no-db 测试含同刻、缺测、顺序和时间入参；正式浏览器真实数据曲线断线、真实 DAA 摘要与跨 DB 未验证。 |

## 命令、结果与保全

- `python3` 解析 [tasks QA2 返工 61 项清单](tasks.md)，逐项 SHA-256、路径及有序清单整体摘要比对：61/61 一致；`git diff --check` 退出 0。`equipment` locale 中英各 147 键、`monitor` 各 258 键，键集合相同。
- `backend/`：`PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa3-uv LOG_DIR=/private/tmp/arch-obs-r10-qa3-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=qa_unused MYSQL_PASSWORD=qa_unused MYSQL_DATABASE=qa_unused MYSQL_ROOT_USER=qa_unused MYSQL_ROOT_PASSWORD=qa_unused TEST_MYSQL_DATABASE=qa_unused_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line --basetemp=/private/tmp/arch-obs-r10-qa3-pytest tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_energy_price_api.py`：退出 0，147 passed、1 skipped、1 warning；skip 为冻结 BE003 候选，warning 为 SQLite datetime adapter 弃用。这是本轮独立执行现有测试，不把 Development 自检当本 QA 执行。
- `frontend-js/`：`pnpm_config_verify_deps_before_run=false pnpm test:modules` 退出 0，81 passed；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa3-dist` 退出 0、2262 模块，外部 outDir 和大 chunk 提示保留。另以 `node --input-type=module` 内存脚本编译实际 SFC、运行 Vue SSR／ECharts SSR 和可控 promise：具体触发及结果见两表与 QA-009；未添加测试文件或修改实现。首个独立能耗脚本误引 `@vue/compiler-sfc`，因 pnpm 布局退出 1；改为项目实际 `vue/compiler-sfc` 后退出 0。
- `backend/` 的 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa3-uv LOG_DIR=/private/tmp/arch-obs-r10-qa3-log uv run --offline --frozen --no-sync python -` 内存脚本先校验目标、revision、唯一随机键与碰撞，再在单连接外层事务中写自有区域、指标、槽和卡片，通过 ASGI 实际路由、随机 Bearer 与内存 profile 调用三类模拟身份；每请求的 AsyncSession 使用 savepoint，业务 commit 不提交外层事务。事务内回执／实时／历史为 6／3／3；整体 rollback 后按自有区域、指标、槽、卡片、producer、设备逐项复查均为 0。人类卡片读取仅以 dependency override 模拟 admin，不证明正式权限；单连接不证明跨连接竞争。MySQL 自增计数可能因回滚前移，未重置。
- 单独槽位边界脚本中，100 插入成功、101 触发 MySQL CHECK；MySQL 驱动将 3819 映射为 `OperationalError`，脚本原只捕获 `IntegrityError`，因此退出 1，并由 `finally` 回滚。随后按该轮随机前缀逐表复核零残留；这是测试脚本异常分类，不是把退出 1 写成测试通过。
- 两轮后独立只读 `SELECT COUNT(*)`／`CHECKSUM TABLE` 对账：计划 2／485881418、实绩 2／2822084073、采集历史 73／1987086524、latest 6／1581760304、来源 3／3609128620、价格 1／677733245 与 3／1315366414，均与本轮前及 QA2 一致；三张新主表、回执、区域、指标、槽、卡片、曲线和能耗配置均 0／0。checksum 不等于备份或恢复验证。未新建 schema／Docker、未 DDL、未修改持久 profile、未停止或重启 8000／5190 或其他服务，未操作 SMA／DAA 产品、真实 PLC、生产或发布。
- 本轮临时 `/private/tmp/arch-obs-r10-qa3-{uv,log,pytest,dist}` 为 QA 测试资源，关键结论已写本文件；按 canonical workflow 由协调者在确认归属与依赖后回收。Development 暂留候选与私有恢复材料仍由协调者管理，QA 不回收。

## 交接

将 **R10-QA-008、R10-QA-009** 和本表未完成的证据交 Development；修复后固定新 handoff，再由新的 fresh-context Verification 复验。所有缺口不得当作通过；QA 结果不代表 Human Owner 最终验收或现场、生产采用。

以下完整保留写入前 QA2 checklist 的原始字节（含 QA1、r8 及更早历史），原 SHA-256 `673dc33d2d4c7ae146da213d1defb0c29a4f39cab9bb69ef052127910f2e1bd8`，先前 verdict 不变。

---

Task ID: ARCH-OBS-001
Revision: r10
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R10-QA-005–007 返回 Development；新 handoff 后以 fresh-context Verification 复验；Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r10 §12.9 R10-AC01–11；contract_only

# r10 QA2 独立 Verification：qa_failed

2026-11-17（Asia/Shanghai），实际命名的 Verification 以 fresh context 接收 QA1 返工 handoff；读取项目契约、任务 bundle、相关实现、diff 和可用测试结果，按 project-governance、aiis、backend-arch、frontend-ui、i18n-workflow 和 code-document-indexer 的相关验证边界执行，仅写本 checklist。Human Owner 对 r10 §12 及指定 dev 目标的批准见 [spec §12.10](spec.md#r10-approval)。本轮 verdict 是 **qa_failed**：QA1 四个原始复现已关闭，但新发现 R10-QA-005–007，且部分验收仍未覆盖；交 Development 返工，不代表 Human Owner 最终验收。

## 精确对象与环境

- 正式交付工作树 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，有其他任务并行未提交改动；未把其余差异归入本交接。spec SHA-256 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`；返工 tasks SHA-256 `ddb36e0d9c284be4433b80d01d1471b0731166fccd5dbc8f266fae97bcedacbc`；写入前 QA1 checklist SHA-256 `d30c929766f3f6f4fdd4b066694565c0c319e02190f2401528b35b6416d9fb78`。逐项核对返工 handoff 清单 61/61 一致，清单整体 SHA-256 `90195c854713c4d93503d996c49e298a2c7d61c2bda9ce4d59c87bf2fbfb9ea0`。
- macOS Darwin 24.6.0 arm64、uv 0.7.8、Node 22.19.0、pnpm 11.11.0；后端通过项目已锁定环境执行。授权 dev 为 `127.0.0.1:3307 / industrial_level_2_system`，只读核对 MySQL 8.4.6、服务器 UUID SHA-256 前缀 `ac2319a3fdc8`、上海偏移 28800 秒、唯一 revision `9d1f3a5c7e20`。沙箱内回环连接返回 `OperationalError`；使用系统审批允许的受限提权连接后成功，没有绕过拒绝。

## QA1 原始缺陷复验

| 缺陷 | 本轮结论及证据 |
| --- | --- |
| R10-QA-001 | **原复现关闭。** 从正式 frontend-js 以 `node --input-type=module` 调用实际 `splitObservedPoints`，原 QA1 的两个相差 998 微秒样本返回两条有序 line、0 条 simultaneous，保留两个原始时间。项目 ECharts SVG SSR 测试还覆盖 1 微秒、真实同刻和缺测。极长时间范围的数值坐标精度限制及缩小范围提示是交接中声明的限制，不能把本次复验扩大成所有时间范围均已证明。 |
| R10-QA-002 | **原复现关闭。** 实际 FastAPI 路由 + ASGI HTTP + 授权真实 MySQL、独有合成机器身份与真实 Bearer 校验；latest/history 各为首次 200、原文重试 200、区域撤权 403、指标撤权 403、恢复后原回执 200。事务内分别 1 实时、1 历史、2 回执；外层回滚后本轮身份对象为 0。该合成客户端不是 SMA 产品，ASGI transport 不是正式 8000 的用户权限测试。 |
| R10-QA-003 | **原复现关闭。** 本轮独立重跑正式 `equipment-observation-columns.test.mjs` 的实际 SFC setup 测试，20／10／空顺序按 10／20／空显示并验证编辑保存；不是正式浏览器配置保存证明。 |
| R10-QA-004 | **原复现关闭。** 实际路由内存夹具验证区域中英文名及重命名，实际 CurveChart setup 验证区域下拉显示 `groupLabel` 并保留稳定键。下方 R10-QA-007 是同名图例／提示的独立缺陷，不撤销该下拉名称复验结果。 |

## 新失败项

### R10-QA-005：能耗切换时旧表计定义或旧组数据覆盖新选择

关联 R10-AC06、AC07、§12.3／12.6／12.7。[energy.vue](../../frontend-js/src/app/monitor/views/observations/energy.vue) 的 `loadDefinitions` 在异步完成后直接更新当前定义；组变更时没有直接递增请求代次，而不同组可配置相同 `metricKey`。以 `node --input-type=module`、项目 `vue/compiler-sfc` 编译实际 SFC setup，使用可控延迟的合成 API，独立复现两条路径：

1. 先选择表计 A、再选择 B，B 的定义先返回、A 后返回；实际结果为 `selectedMeter=B, group=groupA, metric=readingA, definition=Meter A`。
2. A 组请求未返回时切换到同名指标的 B 组，再返回 A 的样本；实际结果为 `selectedGroup=B, summarySource=A, chartTitle=B, chartValue=111`。

因此页面可把旧表计定义或旧组值放在当前选择之下，不能可靠按 `(meterId, groupKey, metricKey)` 解释。结果来自实际组件逻辑和合成 API，不是已登录浏览器或真实表计证据。

### R10-QA-006：过期卡片未显示真实采样时间

关联 R10-AC05、§12.4。实际 [cards.vue](../../frontend-js/src/app/equipment/views/observations/cards.vue) 显示 stale 标签，但模板未读取服务返回的 `observedAt`。使用项目 Vue 编译实际模板并进行 SSR，传入含真实 `observedAt` 的合成过期卡片：`staleLabelRendered=true`、`observedTimestampRendered=false`、`templateMentionsObservedAt=false`。该项违反“数据过期标注真实时间和已过期”的要求；这是模板与 SSR 证据，当前正式 profile 无可访问设备，尚未实浏览器复现有值过期卡。

### R10-QA-007：不同区域的同名曲线无法辨认并被图例一起隐藏

关联 R10-AC07／AC08、§12.7。实际 [CurveChart.vue](../../frontend-js/src/app/monitor/components/observations/CurveChart.vue) 用指标 `label` 作为 series 和 legend 名，tooltip 也只显示该名称。以两个不同区域、同名“Actual temperature”的合成配置执行实际组件和项目 ECharts SVG SSR：legend 与 series 名均重复，tooltip 不含任一对应区域名称；对同名图例执行一次 `legendToggleSelect` 后，ECharts 将两条 series 均标记为 filtered。区域多选虽已显示双语区域名，图中的同名曲线仍不能分别识别或控制。该证据为实际图表组件的 SSR，不冒充正式浏览器多区域闭环。

## 验收逐项结论

| 验收 | 本轮结果及剩余边界 |
| --- | --- |
| R10-AC01 | 部分通过：QA-002 原撤权重放已关闭；QA1 合成 MySQL 证据和本轮测试不覆盖所有身份／并发组合。 |
| R10-AC02 | 部分验证：沿用 QA1 已记录的独立合成包、替换和缺测证据；本轮未穷尽所有配置及真实现场来源。 |
| R10-AC03 | 部分验证：两路原回执权限已复验；旧 r8 真正已存回执重放、跨连接竞争仍未独立证明。 |
| R10-AC04 | 部分验证：模型／迁移和定向测试可查；100／101 槽、并发首次使用与旧值解码未独立穷尽。 |
| R10-AC05 | **失败：R10-QA-006。** 正式登录的手选保持、跟随恢复、设备切换、同刻并列和刷新仍未覆盖。 |
| R10-AC06 | **失败：R10-QA-005。** QA1 合成累计／增量例子保留；跨日、重置／换表和全部缺测组合仍未穷尽。 |
| R10-AC07 | **失败：R10-QA-005、007。** QA-003／004 原复现关闭；正式普通用户、实际多区域交互和全部权限矩阵未覆盖。 |
| R10-AC08 | **失败：R10-QA-007；其余部分验证。** 正式 5190 同一 Chrome 用户配置中新建的独占标签继承用户已登录 admin 会话；从菜单及直接路由进入温度、传动、清洗、能耗四页，均可见对应页。当前无可访问设备／表计，温度页实见通用空 X/Y 轴和原因；未验证配置存在无样本、接口失败重试、真实合成数据到达及多区域断线恢复。原用户标签未接管或覆盖，独占标签已关闭。 |
| R10-AC09 | 部分验证：本轮保护表行数及 checksum 与测试前一致；QA1 比较过 DEV 的迁移前后脱敏快照。旧实时和配置当时为空，未独立执行带旧数据迁移、回退或中断恢复。 |
| R10-AC10 | 部分验证：精确源码清单、授权目标与边界已核对；未重新验证全部文档链接、机器合同和所有回归。 |
| R10-AC11 | 部分验证：QA-001 原复现关闭；时序、缺测和时间入参由定向无库测试及 QA1 合成 MySQL 证据覆盖一部分。正式浏览器真实数据断线、所有精度范围和真实 DAA／跨 DB 未验证。 |

## 本轮命令、保全与资源

- 正式 backend 使用虚构 MySQL 占位环境并禁止 pytest cache：`PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa2-uv LOG_DIR=/private/tmp/arch-obs-r10-qa2-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=qa_unused MYSQL_PASSWORD=qa_unused MYSQL_DATABASE=qa_unused MYSQL_ROOT_USER=qa_unused MYSQL_ROOT_PASSWORD=qa_unused TEST_MYSQL_DATABASE=qa_unused_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line --basetemp=/private/tmp/arch-obs-r10-qa2-pytest tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_energy_price_api.py`：退出 0，147 passed、1 skipped、1 warning；skip 为冻结 BE003 候选，warning 为 SQLite datetime adapter 弃用。
- 正式 frontend-js：`pnpm_config_verify_deps_before_run=false pnpm test:modules` 退出 0，75 passed；`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa2-dist` 退出 0，2262 模块；有外部 outDir 和大 chunk 提示。`git diff --check` 退出 0。
- MySQL 验证以 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa2-uv LOG_DIR=/private/tmp/arch-obs-r10-qa2-log uv run --offline --frozen --no-sync python -` 执行内存脚本：先核对 schema、UUID、revision、时区与随机身份无碰撞；使用单连接外层事务和 session savepoint，调用正式路由、实际机器认证及真实 MySQL，两路复验后关闭 session 并整体 rollback，再以该唯一身份查询零残留。未新建 schema／容器、未 DDL、未写正式 profile，未启动／停止用户服务。回滚不重置 MySQL 自增计数，计数可能前移；未修改已有业务行。
- 事务前／后 `SELECT COUNT(*)` 与 `CHECKSUM TABLE` 一致：采集历史 73／1987086524、latest 6／1581760304、来源 3／3609128620；价格表 1／677733245、3／1315366414；旧能耗和旧曲线各 0／0；三张新主表、回执、区域和能耗配置各 0／0。校验和用于本轮对账，不代替备份或恢复测试。
- F005–007 使用 `node --input-type=module` 加项目 Vue compiler／server renderer 和 ECharts SSR；请求时序、输入及输出记录于失败项。无需启动额外 API 或读取用户 token。正式浏览器原标签曾显示属于另一会话，未接管；随后按同一 Chrome 配置创建自有新标签进行只读导航。
- 本轮 `/private/tmp/arch-obs-r10-qa2-{uv,log,pytest,dist}` 是 QA 自有临时资源；关键结论已写本文件，独立 QA 不回收，后续由协调者按资源规则核实归属与依赖。Development 留存的私有恢复资料仍由协调者保管，不输出其内容。本轮未操作 SMA／DAA 产品、真实 PLC、生产或发布。

## 交接

将 R10-QA-005–007 及上述未覆盖项交 Development；完成返工并固定新 handoff 后，由新的 fresh-context Verification 复验缺陷及剩余 R10-AC01–11。QA1、r8 与更早历史的原始字节完整保留如下；Human Owner 最终验收仍待独立 QA 及其本人决定。

---

Task ID: ARCH-OBS-001
Revision: r10
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R10-QA-001–004 返回 Development；新 developer_handoff 后重新启动 fresh-context Verification；Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r10 §12.9 R10-AC01–11；contract_only

# r10 QA1 独立 Verification：qa_failed

2026-11-17（Asia/Shanghai），实际命名的 Verification 在 fresh context 接收 r10 Development handoff，独立检查正式交付工作树、任务 bundle、实现、差异、可用测试与获准 dev 目标。按 project-governance、aiis、backend-arch、frontend-ui、i18n-workflow、code-document-indexer 的适用边界验证；仅维护本 checklist。Human Owner 的精确 r10 批准与 dev 目标授权见 [spec §12.10](spec.md#r10-approval)；未操作 SMA 产品或真实 PLC。角色合同为 contract_only。

**Verdict：qa_failed。** 发现 R10-QA-001 至 R10-QA-004，返 Development。Human Owner 随后自行登录正式 5190，独立 QA 已在该正式 admin 会话检查四页菜单、直达与无设备／表计空态；真实数据曲线、已配置无样本、失败重试及普通用户权限仍未覆盖。原 r8 qa_failed 和全部历史逐字节保留在本节之后；本 verdict 不授予 Human Owner 最终验收。

## 精确对象和环境

- 正式 main 工作树 HEAD 21cd789277695bbafaa55c24e39261fc7247f9b0，存在其他并行未提交变更。获批 [spec.md](spec.md) SHA-256 667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623；Development [tasks.md](tasks.md) 3d1787b44d6c9c7028f94219a3f8a2828a37144de8b831cbf149cb5890785fd4；本轮写入前完整 r8 checklist SHA-256 d5eb209ce0ea43e66e24aeae7ceaa58d035f633955e230e8da4ccd432bbac1f1。交接的 60 个文件逐项摘要全部匹配，有序 SHA-256 及相对路径清单摘要 a7a9ba7ca57b121736559c6e9c902a55c3c7f662f1f50d407c08c12e594de279。已审查相关实现、迁移、合同和受影响测试差异；未将工作树其余并行差异归属于本任务。
- macOS 15.7.7 arm64；项目锁定 Python 3.13.3、uv 0.7.8、Node 22.19.0、pnpm 11.11.0。dev 为 127.0.0.1:3307 / industrial_level_2_system，MySQL 8.4.6、服务器 UUID SHA-256 前缀 ac2319a3fdc8、会话偏移 28800 秒、唯一 revision 9d1f3a5c7e20。
- 沙箱内对 8000/5190 普通回环探测退出 7；对已授权本机目标的受限提权只读请求均返回 HTTP 200，提权未被拒绝。最初正式 Chrome 标签停在登录页，Human Owner 后来自行登录；QA 未读取或输入凭据，也未重启已有进程。

## 失败项

### R10-QA-001：不同微秒时刻被误判为同刻

**关联 R10-AC11、§12.1–12.2。** 从正式 frontend-js 目录执行实际 [curveSeries.js](../../frontend-js/src/app/monitor/components/observations/curveSeries.js)：

    node --input-type=module -e "import {splitObservedPoints} from './src/app/monitor/components/observations/curveSeries.js'; const points = [{observedAt:'2026-11-17T10:00:00.123001+08:00',value:10},{observedAt:'2026-11-17T10:00:00.123999+08:00',value:20}]; console.log(JSON.stringify({inputs:points,output:splitObservedPoints(points,null)}))"

退出 0，实际 line 为 [[1794880800123,null]]，simultaneous 为 [[1794880800123,10],[1794880800123,20]]。两份真实时间相差 998 微秒，却因 Date.parse 精度被判为同一 X 时刻并断线。合同只把真实相同时刻的不同事件并列，曲线应按原 observedAt 表达事件顺序；这是实际组件辅助函数复现，尚非正式浏览器端到端图形证据。

### R10-QA-002：v2 已存回执绕过当前区域／指标权限

**关联 R10-AC01、R10-AC03、§12.5。** 内存 SQLite、实际路由和真实机器 Bearer 校验的合成夹具中，先用同一 producer 的完整 grant 向 latest 和 history 各提交整包，均得 200；将 grant 收窄至 heatZone1/actual 后，用各自相同 event ID 和原正文重试，两路仍 200 并返回原回执。history 回执的 skipped 仍包含已撤销的 production/coil 和 driveRoll1/ready；原完整正文改用新 event ID 返回 403。latest 对只含保留区域的新事件也因全部可替换范围授权不足返回 403。实际 [ingest_v2.py](../../backend/app/equipment_observation/services/ingest_v2.py) 在逐区域／指标授权前返回已有回执。

对照矩阵：全部设备／目标 grant 撤销后 latest 为 403；energy 指标或组 grant 撤销后旧事件为 403；禁用 producer 后 latest/energy 均 403；合成 r8 v1 原回执初次重放 200、撤销该指标后 403。history 新事件仅提交仍获准的区域为 200，不作为失败。测试只变更夹具内存 profile，不是正式 profile 或真实权限变更。

可复现方式：使用 tests/test_equipment_observation_r10_flow.py 的 app_and_db 内存夹具，向 /api/v1/integration/monitor/history-samples POST 其 document('permission-replay')；把 producer.grants 收窄为 target=history 且 groupKey=heatZone1 的 grant；以原文再 POST，随后将 eventId 改为 permission-new 再 POST。实际状态依次 200、200、403，第二次返回被撤销组的 skipped；上文扩展矩阵恢复实际 authenticate 再运行。该夹具中的旧回执由测试合成，不能冒充真实 r8 归档。

### R10-QA-003：能耗管理列排序未按配置生效

**关联 R10-AC07、§12.3、§12.7。** 用项目 vue/compiler-sfc 编译执行实际 [EnergyAdmin.vue](../../frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue) 的 setup，合成配置按槽位返回 A(slotNo=1,listVisible=true,listOrder=20)、B(slotNo=2,listVisible=true,listOrder=10)。实际 visibleColumns 顺序仍为 A(20), B(10)，而不是配置顺序 B, A；模板中也无 form.listOrder 编辑控件。能耗配置接口按 group_key、slot_no 返回，组件只过滤 listVisible；写入开关与列表可见性虽分离，列表顺序未按独立设置生效。本检查是实际 SFC setup 的合成组件测试，不冒充已登录浏览器操作。

### R10-QA-004：曲线区域多选未显示双语区域名称

**关联 R10-AC07、§12.3、§12.7。** 实际路由的内存 SQLite 夹具中将 heatZone1 区域双语名设为“一号加热区 / Heating Zone One”，中英文 GET /monitor/history-curves 的 series 均仅返回稳定 groupKey=heatZone1 和指标 label；改名为“重命名一区 / Renamed Zone One”后结果仍相同。实际 [CurveChart.vue](../../frontend-js/src/app/monitor/components/observations/CurveChart.vue) 的区域选项以 key 作为 label，故两种语言与改名后均显示稳定键而非配置区域名。见 [reads.py](../../backend/app/equipment_observation/services/reads.py)。此项为路由夹具及模板证据，尚无正式浏览器双语实测。

## 验收逐项结果

| 验收 | 结果与证据边界 |
| --- | --- |
| R10-AC01 | **失败：R10-QA-002。** 独立 MySQL + 回环 HTTP 夹具中，synthetic sma／external／other 三种身份各完成发现和两路 POST；未知空组、错误类型、部分授权整包清空被拒。夹具类型不代表 SMA 产品。 |
| R10-AC02 | **部分验证。** MySQL/HTTP 覆盖整包替换、0／false／空字符串、空包、过滤跳过、stale、同刻异值冲突及坏质量历史拒绝；定向无库测试另覆盖 no_history_metrics。未穷尽所有设备／组配置或真实身份组合。 |
| R10-AC03 | **失败：R10-QA-002。** 同目标同事件原请求返回原回执；显式空组改省略后 409；历史同刻不同事件两行及迟到断点可读。v1 重放及权限收窄只在合成 SQLite 旧回执夹具重验，当前 dev 的旧回执／归档为空，未独立重放真实 r8 回执。 |
| R10-AC04 | **部分验证。** 审查迁移和模型，新的设备／任务唯一键、observed_at、三主表及独立能耗表配置可见；两表计同键不同模式通过合成 MySQL HTTP。未独立穷尽 100/101 槽、并发首用锁及全部旧值解码。 |
| R10-AC05 | **未完成。** 源码及定向测试涉及最近采样与过期；未以正式登录用户独立验证手选保持、跟随恢复、设备切换、同刻并列及刷新。不能把最近采样称为生产或空闲事实。 |
| R10-AC06 | **部分验证。** 独立 MySQL/HTTP 以两块合成表计得到累计 1006−1000=6、增量 2+3=5、瞬时量无用量；模拟 reader 的越权表计及管理接口 403。无库测试覆盖缺边界、缺单位、坏质量、下降、重叠和缺段；跨日、重置／换表、所有缺测及并发组合未独立穷尽。 |
| R10-AC07 | **失败：R10-QA-003、004。** 正式 admin 的两级菜单与过程／能耗数据管理分区可见；源码／自动测试覆盖一部分读范围。正式普通用户、多区域实际交互、列宽及全部授权矩阵未复验。 |
| R10-AC08 | **部分验证。** 正式 admin Chrome 通过菜单与直接 URL 分别进入温度、传动、清洗、能耗四页；前三页显示“暂无可访问设备”，能耗显示“暂无可访问表计”。温度及能耗页实见通用空 X/Y 轴，无虚构时间／数值刻度；两次读取浏览器 error 日志均为空。因正式 profile 当前无设备／表计，未覆盖已配置无样本、请求失败重试、真实数据到达、多区域或断点恢复，不能将四页空态冒充完整闭环。 |
| R10-AC09 | **部分验证。** 对照 Development 留存的迁移前后脱敏快照：9 张保护表的行数及 checksum 对应一致，6 张 r8 源表与归档对应一致；r8 主表和配置当时均为空。实际 dev 当前查询及本轮事务前后对账见下；这不代替独立带数据迁移、可恢复性／中断恢复或全部索引对账。未执行 DDL、降级或恢复。 |
| R10-AC10 | **部分验证。** 正式源码 60/60 摘要一致；运行中 8000 的 5 条公开机器路径存在，三条 POST request schema 与 v2 发布 schema 相同；双语 locale 键对称。真实 SMA/DAA/PLC、生产与 Human Owner 验收均未证明；未独立跑全量链接或全部回归。 |
| R10-AC11 | **失败：R10-QA-001。** 三路缺失 observedAt 的 HTTP 负例拒绝；无库测试覆盖 null、无偏移、不能无损保存微秒；MySQL 合成过程 T2 后补 T1、备注修改、同刻两事件及缺测点的 API 原时序可读。源码显示采集完整样本摘要 max(observed)，observed 从所有点读取，包括 bad；未实际接入 DAA／跨 DB。曲线微秒误判及正式浏览器断线闭环未通过。 |

## 独立命令、数据库对账及资源

- 正式 backend 使用下述命令；所有 MYSQL 值为无连接的合成占位，端口 1；没有输出私有凭据：

    PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/arch-obs-r10-qa-uv LOG_DIR=/private/tmp/arch-obs-r10-qa-log MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 MYSQL_USER=qa_unused MYSQL_PASSWORD=qa_unused MYSQL_DATABASE=qa_unused MYSQL_ROOT_USER=qa_unused MYSQL_ROOT_PASSWORD=qa_unused TEST_MYSQL_DATABASE=qa_unused_test OBSERVATION_ENABLED=false uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --tb=line --basetemp=/private/tmp/arch-obs-r10-qa-pytest tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_energy_price_api.py

  退出 0，**139 passed、1 skipped、1 warning**。skip 是固定 BE003 候选；warning 是 SQLite datetime adapter 弃用。no_db 避免触发仓库破坏性建库 fixture。最初未指定 UV_CACHE_DIR 时因默认缓存沙箱权限退出 2，改用任务缓存后成功；没有安装依赖。
- 前端 pnpm_config_verify_deps_before_run=false pnpm test:modules：退出 0，**69 passed**。pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-obs-r10-qa-dist：退出 0，2262 模块，保留外部 outDir 和大 chunk 提示。git diff --check 退出 0；equipment locale 中英各 147 键、monitor 各 257 键，集合相等。
- 项目运行时 uv run --offline --frozen --no-sync python - 执行本轮独立合成 HTTP harness：使用真实 127.0.0.1 临时回环监听、真实 MySQL 和正式 OBS 路由；目标 UUID/schema/revision 及唯一随机键先校验，配置信息经 admin HTTP 写入一个外层事务；机器凭据随机且以内存 profile 认证，人类身份通过 dependency override 模拟，API 提交仅释放 savepoint。退出前停止本轮临时 HTTP server、整体 rollback，再按生成的唯一身份查询六类对象零残留。随机键仅保存在进程内，未持久记录；事务不证明跨连接并发或真实用户权限。MySQL 自增计数可能因回滚而前移，未重置。该测试无 DDL，未改已有配置、业务记录或用户进程。
- 本轮 MySQL 事务前／后 SELECT COUNT 和 CHECKSUM TABLE：plc_facts_history 73／1987086524，plc_facts_latest 6／1581760304，plc_source_registry 3／3609128620，energy_prices 1／677733245，energy_price_hours 3／1315366414；旧能耗量与旧过程曲线各 0／0。三张新主表、回执、新区域及能耗配置测试后均 0／0。计划 plan_main 2／485881418、实绩 performance_main 2／2822084073 与迁移前脱敏快照相同。checksum 是对账证据，不等同备份恢复。
- 读取并比较 Development 的 cutover-before.json 和 cutover-after.json，SHA-256 分别为 a16de1d842bed92cc6e020a58e487974263266f5b269f69fbda6700ec7890026、1bb92940d21c956b494e3beb626463b1f350ac0de84096145e52104644fdc069：9 个保护表及 6 个源表／归档的记录行数和 checksum 成对一致。该比较使用迁移时 DEV 留存快照，并非本 QA 亲历迁移。
- 在真实 dev 只读调用采集 async/sync target_now：9d 目标匹配，8c 错配均拒绝；typed integration 允许版本列表包含 9d，未以已采用 typed profile 执行真实写入或维护清理。运行时公开 OpenAPI 的 5 条机器路径存在，3 条 POST schema 与发布 v2 对应请求体一致。
- 正式浏览器经菜单和直达检查 /monitor/temperature、/monitor/drive、/monitor/cleaning、/monitor/consumption，过程数据管理的“过程样本”和“能耗样本”标签可切换。检查后返回用户原来的设备数据管理页。无设备／表计空态以实际页面和温度／能耗截图观察为依据，截图未另存；关键观察已写本节，非截图或 DOM 单独证明真实数据曲线闭环。
- QA 新建 /private/tmp/arch-obs-r10-qa-dist、/private/tmp/arch-obs-r10-qa-uv、/private/tmp/arch-obs-r10-qa-log、/private/tmp/arch-obs-r10-qa-pytest 供本轮构建和验证；关键结论已写本节，复验不再依赖时由协调者核实归属后回收。Development 暂留候选 /private/tmp/arch-obs-r10-dev.jt9Ah6Pc 与私有证据／恢复目录 /private/tmp/arch-obs-r10-private.j0jFyKfK 仍有复验和恢复依赖，不由本 QA 删除；私有备份内容不输出或提交。

## 返工与下一 gate

将 R10-QA-001–004 及上述未覆盖项交 Development；返工后固定新 handoff 与摘要，再由新的 fresh-context Verification 复验相应负例及 R10-AC01–11 尚未完成的证据。正式账号下仍须补证已配置空图、失败重试、真实合成数据和普通用户权限；带旧数据迁移回退、跨连接竞争、旧已存回执真实重放和指定目标剩余守卫按授权及可用资源补证。任何 QA 结果均不替代 Human Owner 最终验收、SMA 产品、真实 PLC、现场或生产验证。

## 保留的 r8 及更早 Verification 历史

以下为本轮写入前 checklist 的完整原始字节（SHA-256 d5eb209ce0ea43e66e24aeae7ceaa58d035f633955e230e8da4ccd432bbac1f1），r8 原 verdict 不变。

<!-- ARCH-OBS-001-r10-history-begin -->
Task ID: ARCH-OBS-001
Revision: r8
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: R8-QA-001 返 Development；返工后对精确新 handoff 重新启动 fresh-context Verification；Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r8 §10.7 R8-AC01–08；contract_only

# r8 独立 Verification：qa_failed

2026-11-16（Asia/Shanghai）。本轮由实际命名 `verification` 的 fresh context 接收 r8 Development handoff；按根 `AGENTS.md`、canonical lifecycle workflow、角色合同、任务 bundle、实现和 diff 独立验证。适用 shared skills 为 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`。本轮只写本 checklist；不存在平台 ACL 或强制路由声明。Human Owner 对 r8 §10 和指定 dev 迁移、必要配置、合成数据及仅清理测试数据的批准见 [spec §10.8](spec.md#r8-approval)；随后单独授权的 8000 短暂重载由 Development 执行，本轮没有重启或停止已有服务。

**Verdict：`qa_failed`。** 两条 SMA 写入路径都可在 `sourceRefs` 只含任务点、没有任何其他映射用点引用时返回 `stored` 并持久化。此失败返 Development。下表其余部分列出实测通过和未覆盖范围，不把局部成功或 Development 自检写成整项通过。最终验收只能由 Human Owner 在修复及独立复验后决定。

## 候选、环境与身份

- 正式工作树 `main`、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。批准后 [spec](spec.md) SHA-256 `bedca6d06769879bed608376a3e0b88a3c6bc071d999afe42aae1bd96cd30cb8`；[tasks](tasks.md) `51e5fafad2769d8baf6959c0cceebf7e922d67d0c68e21064de99f9c1e7b4f9f`。Development 清单的 62/62 文件逐项匹配，排序 `SHA-256  path\n` 的集合摘要 `a501d2e221bbe64cdc8003c6c5eed31395b3393eaada570901ecb201a8210ece`。交接前后复算一致。
- r7 冻结基线清单 888/888、候选清单 924/924 文件摘要均匹配；r7 patch SHA-256 `d753328ceeb32cdd2cbd5387e221e14376403ef6024ea9cc0cf7adf7f5b00e46` 与历史 QA3 一致。r8 62 文件相对 r7 清单为 24 同字节、34 适配、4 新增。该追溯不把 r7 隔离 QA 代替本轮 QA。
- 本机 macOS 15.7.7 arm64、uv 0.7.8、Python 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.78、Playwright 1.64.0-alpha-1789764292000。只读重查唯一源码 head 和 dev 数据库 revision 均为 `8c0e2a4d6f18`；MySQL 8.4.6，`127.0.0.1:3307 / industrial_level_2_system`，服务器 UUID 摘要前缀 `ac2319a3fdc8`，时区偏移 28800 秒。七张新表、主键、唯一键、时间索引及列表列在 information_schema 中可见，`list_visible` 为非空默认 0、`list_order` 可空。
- 实际 8000 使用的新 facts 和 OBS 私有 profile 权限均为 0600、revision 均为 8c；OBS 设备及 producer 均为空。只读 HTTP 实测现有 8000 的管理员登录、采集 options、空设备选项、全局指标配置、列设置和两个空列表均 200，匿名机器发现 401；5190 三个入口返回 HTML 200。未显示凭据或私有配置内容。

## R8-QA-001：SMA 映射用点引用可全部省略

**合同及边界。** [spec §10.4](spec.md#r8-dev-integration) 要求任务点和映射点来自同一份已入库样本，无法证明的新事件不得新增记录；[机器合同](../../contracts/published/http-api/equipment-observation-v1/README.zh-CN.md) 明确 `sourceRefs` 至少包括绑定任务点及映射用点。每个实验的真实 v2 样本有 `q8-task`（任务 STRING）和 `q8-value`（REAL）；下列 SMA 上报的指标不是单纯任务号，但唯一引用均为 `q8-task`。两个请求使用各自已启用的 QA 专用 SMA 身份和已登记当前来源；无需暴露 Bearer。

**实时复现。** 以独立 fixture `q8-f435e88b7d8b` 向 `/api/v1/integration/equipment/latest-snapshots` POST，实际请求、响应及随即独立 SQL 读取如下；请求只有一个任务点引用，未提交 `q8-value` 等映射点引用：

```json
{
  "request": {
    "contractVersion": "aiis.metric-ingest/v1",
    "producerId": "q8-f435e88b7d8b-sma",
    "eventId": "q8-f435e88b7d8b-task-only-reference",
    "mappingId": "q8-f435e88b7d8b-mapsma",
    "mappingRevision": "r1",
    "sourceRefs": [
      {
        "kind": "plc_fact",
        "instanceId": "q8-f435e88b7d8b-insta",
        "plcId": "q8-f435e88b7d8b-plca",
        "sampleId": "q8-f435e88b7d8b-sample-a2",
        "pointId": "q8-task",
        "sourceGeneration": "q8-f435e88b7d8b-gena"
      }
    ],
    "data": {
      "equipmentId": "q8-f435e88b7d8b-linea",
      "groupKey": "q8-f435e88b7d8b-temp",
      "taskNo": "000F435E88B7D8BA",
      "sampledAt": "2026-11-16T16:14:11+08:00",
      "quality": "good",
      "values": {
        "q8-f435e88b7d8b-actual": 0,
        "q8-f435e88b7d8b-set": 10,
        "q8-f435e88b7d8b-ready": false,
        "q8-f435e88b7d8b-text": ""
      }
    }
  },
  "httpStatus": 200,
  "response": {
    "code": 200,
    "message": "success",
    "data": {
      "target": "latest",
      "producerId": "q8-f435e88b7d8b-sma",
      "eventId": "q8-f435e88b7d8b-task-only-reference",
      "outcome": "stored",
      "recordId": "18"
    }
  },
  "database": {
    "receiptId": 48,
    "outcome": "stored",
    "recordId": 18,
    "sourceRefs": [
      {
        "kind": "plc_fact",
        "plcId": "q8-f435e88b7d8b-plca",
        "pointId": "q8-task",
        "sampleId": "q8-f435e88b7d8b-sample-a2",
        "instanceId": "q8-f435e88b7d8b-insta",
        "sourceGeneration": "q8-f435e88b7d8b-gena"
      }
    ],
    "localValues": {
      "01": 0,
      "02": 10,
      "03": false,
      "04": ""
    }
  }
}
```

HTTP 200、`outcome=stored`；SQL 找到 receipt 48 和主表行 18，回执仅记录该任务点引用，槽值为 `01=0, 02=10, 03=false, 04=""`。这是对既有本轮 QA 行的整组覆盖，不是无副作用的解析成功。

**历史复现。** 以另一独立 fixture `q8-2dc38d09de02` 向 `/api/v1/integration/monitor/history-samples` POST，同样只有任务点引用：

```json
{
  "request": {
    "contractVersion": "aiis.metric-ingest/v1",
    "producerId": "q8-2dc38d09de02-sma",
    "eventId": "q8-2dc38d09de02-task-only-history",
    "mappingId": "q8-2dc38d09de02-mapsma",
    "mappingRevision": "r1",
    "sourceRefs": [
      {
        "kind": "plc_fact",
        "instanceId": "q8-2dc38d09de02-insta",
        "plcId": "q8-2dc38d09de02-plca",
        "sampleId": "q8-2dc38d09de02-sample-a2",
        "pointId": "q8-task",
        "sourceGeneration": "q8-2dc38d09de02-gena"
      }
    ],
    "data": {
      "equipmentId": "q8-2dc38d09de02-linea",
      "groupKey": "q8-2dc38d09de02-temp",
      "taskNo": "0002DC38D09DE02A",
      "sampledAt": "2026-11-16T16:18:24+08:00",
      "quality": "good",
      "values": {
        "q8-2dc38d09de02-actual": 0,
        "q8-2dc38d09de02-set": 10
      }
    }
  },
  "httpStatus": 200,
  "response": {
    "code": 200,
    "message": "success",
    "data": {
      "target": "history",
      "producerId": "q8-2dc38d09de02-sma",
      "eventId": "q8-2dc38d09de02-task-only-history",
      "outcome": "stored",
      "recordId": "29"
    }
  },
  "database": {
    "receiptId": 75,
    "outcome": "stored",
    "recordId": 29,
    "sourceRefs": [
      {
        "kind": "plc_fact",
        "plcId": "q8-2dc38d09de02-plca",
        "pointId": "q8-task",
        "sampleId": "q8-2dc38d09de02-sample-a2",
        "instanceId": "q8-2dc38d09de02-insta",
        "sourceGeneration": "q8-2dc38d09de02-gena"
      }
    ],
    "localValues": {
      "07": 0,
      "08": 10
    }
  }
}
```

HTTP 200、`outcome=stored`；SQL 找到 receipt 75 和新增过程历史行 29，回执只含任务点，槽值 `07=0, 08=10`。两轮 QA 专属对象均已按下文精确清理。

[证据服务](../../backend/app/plc_facts/services/observation_evidence.py) 的 `confirm_task` 校验了传入引用是否存在、同一身份及任务点是否出现，但未要求存在任何非任务的映射用点引用；[入口](../../backend/app/equipment_observation/services/ingest.py) 两路共享该服务。上面的实测**只证明可省略全部映射用点引用仍被接受**。现有请求与 profile 未提供经可信登记的 `metricKey → PLC pointId` 映射，不能仅凭这份信封证明每个指标实际使用哪个点；是否需要增加此种逐指标证明及其合同边界由 Development/PM 按已批准范围判断，不能把简单增加一个无关点引用视为已完成逐指标语义校验。

## 验收核对

| 项目 | 结果与实际边界 |
| --- | --- |
| R8-AC01 基线与迁移 | **部分验证。** 清单、r7 来源、唯一 head、新七表和主要索引符合上文；原 `plan_main`、`performance_main`、`plc_facts_history`、`plc_facts_latest`、`plc_source_registry` 的现有行数及 `CHECKSUM TABLE` 与 Development 迁移前脱敏快照逐项一致。未重新执行迁移、未独立复算迁移前所有原表索引摘要，也未验证数据库备份恢复；`.env` 私有备份不是数据库恢复证明。 |
| R8-AC02 列表与列设置 | **部分验证。** 真实双设备、同槽不同组与两目标不同槽位；`0`、`false`、空字符串、缺项、历史停写后列及原值、列显示独立于写入开关、两种语言和单位经 HTTP/SQL、组件测试或 Chrome 核对。Chrome 拖拽实时指标列并刷新恢复、复位；未独立覆盖所有筛选分页、历史表列宽及页面请求竞态的每种组合。 |
| R8-AC03 权限与管理 | **定向通过。** admin 配置可用；operator 管理请求 403，机器 Bearer 调管理员接口 401。另一设备有实际行但 admin 列表总数只含授权设备，越权筛选 403、越权详情和 PATCH 404。两类白名单外 PATCH 422；实时备注覆盖后保留、历史标记保存。空设备 admin 全局配置接口和空列表 200。 |
| R8-AC04 采集适配 | **失败：R8-QA-001。** 当前登记 PLC/实例/代次、实际采集、任务前导零、空闲、坏质量及超龄 unknown、事实过期 410、A→B 和迟到 A、来源接管、旧代次拒绝、新代次激活及删除后公开历史保留均真实测到。第四轮在 QA 私有后端用时序钩子只暂停真实事务：写入通过 `confirm_task` 持共享锁时删除等待，释放后写入确认且删除成功；反向让真实删除持锁，写入等待，删除提交后写入 409。不是跨 DB 归属证明。 |
| R8-AC05 外部 HTTP | **失败：R8-QA-001。** 两种身份实际 GET 发现及两路 POST；第三方最简缺省补齐、两路独立事件、重放、相同事件异内容 409、同源历史 `already_stored`、类型／坏质量拒绝、原值/回执、同组整包覆盖及遗漏项消失已测。单位取自发现结果；采样间隔由发送方负责，未运行真实 SMA 发送端证明间隔。 |
| R8-AC06 页面闭环 | **部分验证。** 独立 Chrome 打开四卡片页和温度、传动、清洗三曲线页，画布存在；中英文切换及历史停写列通过，0 pageerror。首次列宽脚本未滚入横向视口，未写入偏好；滚入后实测拖动、刷新恢复及复位成功。未在本轮实测所有空态视觉、10 项上限、曲线显示与留存独立切换、同单位纵轴文字及旧能耗/采集入口的完整交互。 |
| R8-AC07 兼容与测试 | **部分验证。** 定向后端无库 160 passed、3 skipped，前端 67 passed、构建通过；三项 skip 见下。实际 dev 的 async/sync 目标守卫接受 8c，旧 7b 和未知 revision 错配均 503；设备 typed 只读目标探针接受 8c、旧版错配拒绝。旧版 profile + 旧版数据库的本轮实库组合未测；typed 真实采用配置关闭，未执行 typed 写入或真实维护清理。未运行全仓套件。 |
| R8-AC08 交接边界 | **证据已记录，整体 verdict 仍失败。** dev DDL/配置由 Development 在授权下执行，本轮只做独立只读对账与有所有权的合成写入清理。合成 SMA HTTP 并非 SMA 产品投递；未运行 DAA、真实 PLC、生产部署或发布。 |

## 检查与命令

- 正式树 `env PYTHONDONTWRITEBYTECODE=1 ... uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db -rs --basetemp=<QA 临时目录> tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_business_integration_migration.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_acquisition_source_registry.py tests/test_acquisition_data_browse.py tests/test_plc_facts_v2.py`，禁用 admin/supervisor/operator bootstrap 及 mock，退出 0：160 passed、3 skipped。跳过原因依次为 BE003 冻结候选、独立采集浏览 fixture、BE012 保留前驱 runner。`-m no_db` 防止触发 `conftest.py` 的破坏性数据库 fixture。
- 正式树 `pnpm_config_verify_deps_before_run=false pnpm test:modules` 退出 0：67 passed；`pnpm build --outDir <QA 临时目录>/frontend-dist` 退出 0，2254 模块，预检 23 routes/9 groups；保留外部 outDir 与大 chunk 提示。Python 对受影响源码 `compileall -q` 退出 0；跟踪文件 `git diff --check` 退出 0；equipment 双语 139/139 键、monitor 209/209 键对称。并非全量代码或文档链接检查。
- 五轮均使用本 QA 的隔离临时 API、随机唯一设备/PLC/实例/代次/任务/指标/producer，预检无碰撞，以真实 HTTP 及 MySQL 执行；第二轮用本轮构建的静态前端和私有回环代理启动独立 Chrome。第三及第五轮分别故意断言应拒绝缺少映射点引用，实际 `stored` 后以退出 1 记录产品失败；第一轮退出 1 是浏览器拖拽前未滚入视口的测试定位问题，第二轮改进测试定位后通过。第四轮额外注入仅控制等待时序的 QA 包装，未修改正式实现。
- 本机回环在默认沙箱最初报 `Operation not permitted`，针对 Human Owner 已明确授权的目标申请执行后成功。最终只读核对五轮专用 PLC/设备/producer 主键残留 0，七表当前计数均 0；五张旧表（计划 2、实绩 2、事实历史 73、latest 6、来源 3）行数与校验和匹配迁移前脱敏快照。MySQL 的自增计数可能因合成插入而前进；未重置计数、未清表、未降级。

## QA 对象与资源收尾

下表列出本轮创建并已按身份定向删除的主键；`fact_history` 为采集历史行 ID。各轮创建的两台设备、PLC、实例、代次分别为 `<fixture>-linea/-lineb`、`-plca/-plcb`、`-insta/-instb`、`-gena/-genb`；接管的新身份为 `-insta-next/-gena-next`。任务为 `000` + fixture 12 位后缀大写 + `A` 或 `B`。来源登记主键是两台 PLC；latest 点表复合键是对应 PLC、DB 62000/62001 和 `q8-task`/`q8-value`。对应六个指标为 `<fixture>-actual/-set/-ready/-text/-speed/-clean`；四卡键为 `<fixture>-card-production/-cleaning/-temperature/-drive`，三曲线键为 `<fixture>-curve-temperature/-drive/-cleaning`。槽位主键为本 fixture 的 `temp` 组 latest 1–4、history 7–8，`drive` 组 latest 1/history 9，`clean` 组 latest 1/history 9。逐行清理前核验所属设备、任务、生产者、来源及代次，不使用整表删除。

| 轮次 | fixture | 实时主表 ID | 历史主表 ID | 回执 ID | 采集历史 ID | 原五表对账一致 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `q8-9319ad33d01e` | 11, 10, 9, 12 | 12, 11, 9, 10 | 26, 32, 30, 28, 25, 33, 31, 29, 27 | 106, 107, 108 | 是 |
| 2 | `q8-f583f792d913` | 15, 14, 13, 17, 16 | 16, 15, 13, 17, 14 | 35, 41, 39, 44, 37, 34, 42, 43, 40, 38, 45, 36 | 109, 110, 112, 113, 114, 115, 111 | 是 |
| 3 | `q8-f435e88b7d8b` | 20, 19, 18, 22, 21 | 21, 20, 22, 18, 19 | 47, 54, 52, 57, 50, 46, 55, 56, 53, 51, 58, 49, 48 | 116, 117, 119, 120, 121, 122, 118 | 是 |
| 4 | `q8-c2d5e896784c` | 25, 24, 23, 27, 26 | 26, 25, 23, 27, 24 | 60, 66, 64, 69, 62, 59, 67, 71, 68, 65, 63, 70, 61 | 123, 124, 126, 127, 128, 129, 125 | 是 |
| 5 | `q8-2dc38d09de02` | 30, 29, 28, 32, 31 | 31, 30, 32, 28, 29 | 73, 81, 79, 77, 85, 76, 75, 72, 82, 87, 84, 80, 78, 86, 83, 74 | 133, 130, 131, 134, 135, 136, 137, 138, 132 | 是 |

所有 QA API、静态代理与 Chrome 由本轮创建并停止，五个 API 端口 55179、55523、55971、56113、56315 经 `lsof` 均无监听。原 3307、8000、5190 仍在监听，未操作其进程。QA 临时 facts/OBS profile 与浏览器登录输入文件已删除；私有 `0700` 目录 `/private/tmp/arch-obs-r8-qa.H0ylvl7j` 保留 QA 脚本、五份脱敏结果、日志和构建以供返工复核，保留至修复后的独立复验完成后由协调者核对归属回收。关键缺陷及精确主键已持久化在本 checklist，不依赖该临时目录。当前第五轮脚本 SHA-256 `fe14a3e6776810119609274b1572dc9e27beba122ea023aef15078c5b7ab9455`；`result-round3.json` `bb73b8be186438b7d3ea755b73d4c0f0049b0b158a4c6ef419957b40c5866647`，`result.json` `b265a71d2c40f5a94a094ebba04d8a3c6d1539b9115a6a85d67f42740889d460`。历史 Development 临时备份/截图不属本 QA 清理对象。

## 返工与后续 gate

将 R8-QA-001 的两条真实 HTTP 与数据库证据返 Development，在合同允许的精确范围内处理后交新 handoff；再以 fresh-context Verification 重验两种目标及相关负例，并补齐上表未覆盖的验收项。采样间隔真实发送、旧版本目标实库、已采用 typed 业务、全量测试、现场 SMA/DAA/PLC、长期容量/生产运行仍未由本轮证明。Human Owner 的最终验收尚未发生。

## 保留的 r7 及更早 Verification 历史

以下原 checklist 全部字节保留，原 SHA-256 `49816d01e11ad6049fc815cca1088dffdef13ddbfca42b26c8971e71d80540fa`；其 r7 verdict 只适用于当时隔离候选。

<!-- ARCH-OBS-001-r8-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA3 交 Human Owner 对精确隔离候选作最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA3 独立验证

2026-11-11（Asia/Shanghai）。命名 `verification` 以 fresh context 接收 [r7 QA2 返工交接](tasks.md#r7-qa2-返工-development-交接)。按根与最近作用域的工程契约、canonical lifecycle workflow、角色合同和任务三文件核验，采用 `project-governance`、`aiis`、`backend-arch`、`frontend-ui` 与 `i18n-workflow`。本轮复验三处 Vue 差异，使用与 DEV、QA2 分离的合成实例运行 HTTP、SQL 和 Chrome。经字节对照确认适用的 QA1／QA2 独立证据在下文引用。角色权责为 `contract_only`。 [Human Owner 批准](spec.md#r7-acceptance)

## QA3 候选与隔离环境

| 对象 | 证据 |
| --- | --- |
| 获批规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。批准原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| 精确交接 | `tasks.md` SHA-256 `13599c36c486980da5880c353b9b91aaef1e61795b9af83d16b6b7a592421911`，新段自第 470 行起。原 49388 字节前缀 SHA-256 `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4`。 |
| 冻结基线与正式候选 | `runtime/arch-obs-001-r7/baseline` 为 HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 的获批补充源码，888 文件树 SHA-256 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。`runtime/arch-obs-001-r7/source` 为 924 文件候选，有序 `sha256  相对路径\n` 摘要 `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf`。全部 57 个基线差异逐项符合 §9.4。 |
| 重建与 QA2 差异 | [canonical 补丁](evidence/r7-source.patch) SHA-256 `d753328ceeb32cdd2cbd5387e221e14376403ef6024ea9cc0cf7adf7f5b00e46`，[清单](evidence/r7-source-baseline.json) SHA-256 `df0145272f56505929e63e1c2a4c77d13b84acc88cead36359de5224f4f6d5e1`。使用冻结副本分别应用 [QA2 补丁](../../runtime/arch-obs-001-r7/output/qa2-source/r7-source.patch) 与当前补丁，逐项重建匹配各自 924 文件。与 QA2 相比，仅设备共用 `RecordList.vue`、设备 `views/observations/admin.vue`、过程 `views/observations/admin.vue` 三个获准文件变化。复核列仅改变显示，名称／标题的表头随单元格语言选择，原 `prop`、保存路径及列宽键保留。其他 921 文件与 QA2 逐字节一致，包含后端、迁移、合同、权限装配、词典和测试。 |
| QA3 专属数据库 | MySQL 8.4.6，`aiis-arch-obs-001-r7-qa`，`127.0.0.1:13396`，`arch_obs_r7_qa`，专属账号 `arch_obs_r7_qa_app`。走读前 SQL 实测 UUID `bfbc0a82-dda1-11f1-a9fe-ba45c7e74587`、会话偏移 28800 秒、revision `5f7a9c1e3b26`。协调者的该目标预检为 0 表，迁移日志显示空库显式升级，末段为 `4e6a8b0d2f14 → 5f7a9c1e3b26`。独立 SQL 查得七张 r7 表。DEV 和 QA1／QA2 目标与证据见下方历史。 |
| QA3 实际 Web 与 API | Web `127.0.0.1:15396`，FastAPI `127.0.0.1:18396`。两端初次默认沙箱探测退出 7，经允许的本机回环访问均返回 200。`lsof` 实查两个监听进程的 cwd 分别为交付候选的 `frontend-js/` 和 `backend/`。由协调者用隔离 profile 启动 `python main.py` 和 `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort`，Web mock 关闭。独立 Chrome 从正常登录入口发起业务请求，相关响应与 MySQL 的新行一致。 |
| 工具 | macOS 15.7.7 arm64、Apple Git 2.50.1、uv 0.7.8、CPython 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39、Playwright 1.64.0-alpha-1789764292000。 |

## QA3 验收结果

| 验收项 | 结果与证据 |
| --- | --- |
| R7-AC01 源码与隔离 | **通过 §9.5 的可复核性要求。** 哈希、冻结基线重建、57 个允许差异、运行目录、隔离目标、回收与实际构建均可核对。两项后端和四项前端旧断言的失败保留，见命令记录。 |
| R7-AC02 迁移和兼容 | **通过。** QA3 新库通过当前 head 和七表核对，v2 新写与观察写读取实测成功。已重建的 QA2 与当前候选的后端、迁移、旧合同字节一致。带数据升级、旧／新 profile 各自匹配、错配拒绝、旧 typed 数据及回执、受控维护和只撤七表的隔离降级采用原独立证据。QA3 未重复降级。 [QA2](#r7-qa2-独立验证) · [QA1](#r7-qa1-独立验证) |
| R7-AC03 接入合同 | **通过。** QA3 实际调用两身份的指标发现 GET、最简第三方及完整合成 SMA 信封的两路 POST。四条新回执和槽位对应见下。错误或停用凭据、越权、显式 `null`、坏质量、禁用指标、字段及类型负例采用相同后端的 QA2 独立 HTTP 证据。 [QA2](#r7-qa2-独立验证) |
| R7-AC04 任务证据 | **通过。** QA3 两份新合成事实实际通过 v2 HTTP 接收，任务点原值与 API、MySQL、Web 任务号均为文本 `000042`，有两次各自的来源证据。换单、迟到 A、B 缺组、空闲／未知／过期／错绑、伪造引用和前导零卷号使用相同实现的 QA2 独立证据。 [QA2](#r7-qa2-独立验证) |
| R7-AC05 数据与重试 | **通过。** QA3 同一实时行从第三方覆盖到合成 SMA，历史分别追加，四回执持久，第三方原事件实时重放返回相同回执。MySQL 证实独立槽位和布尔 `false`。旧包、冲突、同源去重、断连重放、独立补投、首用锁、100 槽上限及数值 `0` 的实库证据来自相同后端的 QA2。 [QA2](#r7-qa2-独立验证) |
| R7-AC06 页面与权限 | **通过。** QA2 两项返工缺陷在 Chrome 关闭。两种详情、三张配置表的中英表头及内容一致，历史两种标记和空值按语言显示，采集质量独立，实际 PATCH、详情与列表 GET 和 MySQL 均保留原枚举。六处受影响列均验证拖拽、双语间保留、重开／刷新及复位。温控卡片与曲线用新数据复跑。其余卡片／曲线页、两条产线、既有及退役入口、管理员设备约束、编辑白名单和读／机器角色拒绝由 QA2 的独立 Chrome／HTTP／SQL 证据与本轮字节差异共同支撑。 [QA3 浏览器结果](../../runtime/arch-obs-001-r7/output/playwright/qa3-browser-result.json) · [QA2](#r7-qa2-独立验证) |
| R7-AC07 交接与复跑 | **通过。** 用 `000042` 将新的合成事实、请求、回执、MySQL 值与 Web 对照。重读双语走读与机器合同，SMA 独立读身份、`plc-facts-read`、PLC/DB `readScopes`、两路观察写 Bearer、SMA-004 产品投递、DAA-010 和精确 provider 审批与联调步骤均有入口。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#后续-sma-取数和-daa-联调前置条件) · [英文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.md#prerequisites-for-future-sma-reads-and-daa-integration) |

## QA3 Chrome 返工复验

Chrome 通过 `/login` 登录隔离管理员，真实登录 POST 返回 200。Playwright 脚本退出 0，8 组检查通过，0 pageerror。管理页用 `000042` 筛选后读取实际 API，按返回记录 ID 对照表格行。截图在对应表头、卡片、曲线或弹窗可见时采集，设置 `animations: 'disabled'`，同一状态连续两张 PNG 字节一致后保留，并目视复核全部 14 张。JSON SHA-256 `ed0fd9b94e78109b0c6de0efb8bd921e8f38f562416360e52353664b8c8ec750`，内含每张 PNG 的 SHA-256。 [浏览器结果](../../runtime/arch-obs-001-r7/output/playwright/qa3-browser-result.json)

| 表面 | 中文表头／单元格 | 英文表头／单元格 | 实际列宽 px |
| --- | --- | --- | --- |
| 指标配置 | 中文名称／实际温度 | English name／Actual temperature | 180 → 240 → 180 |
| 卡片配置 | 中文标题／加热区 1 | English title／Heating Zone 1 | 190 → 250 → 190 |
| 曲线配置 | 中文标题／加热区 1 | English title／Heating Zone 1 | 220 → 280 → 220 |
| 实时快照详情 | 中文名称／实际温度 (°C) | English name／Actual temperature (°C) | 180 → 240 → 180 |
| 过程历史详情 | 中文名称／实际温度 (°C) | English name／Actual temperature (°C) | 180 → 240 → 180 |
| 过程历史列表 | 复核标记／异常、已复核、空白 | Review flag／Abnormal、Reviewed、空白 | 130 → 190 → 130 |

各配置表用稳定 `nameZh`／`titleZh` 偏好键，详情用各自 `nameZh`，历史列表用 `reviewMark`。拖动后通过语言切换及重载页面或重开详情保持中间宽度，恢复默认后 DOM 宽度复位且对应本机键清除。两详情的 `quality=good` 分别显示为「采集质量／正常」与「Source quality／Good」。 [实时详情中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-latest-detail-zh.png) · [历史详情英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-history-detail-en.png) · [指标配置英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-metrics-en.png) · [卡片配置中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-cards-zh.png) · [曲线配置英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-curves-en.png)

中文下拉保存了历史行 4 的 `abnormal` 和行 3 的 `reviewed`。两次 PATCH 均为 HTTP 200、`application/json`，请求和响应 `reviewMark` 保持英文枚举，重新读列表及打开详情均保留。未标记对照行 2 的 GET 为 `null`。SQL 对三行读回 `NULL`、`reviewed`、`abnormal`，各行的 `quality` 均为 `good`，采集槽位与回执 ID 与对应样本一致。 [历史列表中文](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-history-marks-zh.png) · [历史列表英文](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-history-marks-en.png)

## QA3 合成任务 000042 走读

在候选 `backend/` 执行 `uv run --offline --frozen --no-sync python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`，以私有合成凭据运行并退出 0。走读仅使用 Python 标准库。该次命令未传隔离项目环境位置，uv 创建了无项目依赖的临时 `.venv`，交协调者回收。运行中 API 使用协调者单独准备的锁定项目环境。走读脚本以 200 验证两份 v2 事实、两种身份的历史指标发现、四次 POST、实时重放和卡片／曲线／详情读回。两份事实均为 `plc-01/DB42`，绑定点 `point-active-task-no` 为 `"000042"`。以专属 MySQL 客户端执行只读事务，对照四个回执、任务证据与值表行。

| 来源 | 两路请求及绑定任务点证据 | MySQL 回执与值 |
| --- | --- | --- |
| 第三方 | 原事件 `vendor-1794383023214123`，证据样本 `demo-external-1794383023214123`，原时刻 `2026-11-11T15:43:32.000000+08:00`。实时省略质量和固定接入字段，历史显式 `quality=good`。两路实测／设定均为 811.2／815.0。 | 实时／历史均 `stored`，回执 ID 5／6，结果行 1／3。实时重放响应等于原回执。历史槽位 `{"07":811.2,"08":815.0}`。 |
| 合成 SMA | 完整信封事件 `demo-latest-1794383023214123`／`demo-history-1794383023214123` 共用样本 `demo-sma-1794383023214123` 和原时刻 `2026-11-11T15:43:42.000000+08:00`。 | 两路均 `stored`，回执 ID 7／8，结果行 1／4。实时覆盖行 1 后槽位 `{"01":812.2,"02":815.0,"03":false}`，历史行 4 追加 `{"07":812.2,"08":815.0}`。 |

Chrome 的当前任务为 `000042`，炉区 1 卡片读取 812.2／815.0。截图时合成采样已超过陈旧阈值，卡片显示 `Stale`。过程曲线查询使用同一任务号，实际温度序列读出 811.2／812.2，设定温度 815.0。两份走读间的缺样在 ECharts 两个序列均有 `null`，`connectNulls=false`，共用一个 °C 纵轴。 [温控卡片](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-temperature-card.png) · [温度曲线](../../runtime/arch-obs-001-r7/output/playwright/qa3-000042-temperature-curve.png)

## QA3 命令与已知测试结果

| 检查 | 结果 |
| --- | --- |
| `shasum -a 256`、内联 `python3` 文件树与清单比对、冻结副本 `git apply --check --whitespace=error` 及 `git apply --whitespace=error` | 退出 0。重建 QA2 和当前候选，两个 924 文件树各自完全一致。QA1 补丁及候选清单也匹配存档摘要。设备 131、过程 209 个双语键逐项对称。 |
| `node --test tests/module-registry/equipment-observation.test.mjs` | 退出 0，2 通过。覆盖四卡片和三历史页装配、受限管理路由及历史缺样断点。 |
| `pnpm_config_verify_deps_before_run=false pnpm check:modules` | 退出 0，28 路由、10 分组。初次未禁用依赖预检，pnpm 的尝试重装因无 TTY 中止，退出 1。 |
| `pnpm_config_verify_deps_before_run=false pnpm build --outDir <QA3 私有目录>/qa3-dist` | 在显式隔离页面授权 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='["equipment.temperature","monitor.temperature"]'`、`VITE_OPERATOR_PAGE_ACCESS_JSON='[]'` 和 mock 关闭条件下退出 0，转换 2314 模块。保留外部 outDir 和大 chunk 提示。首次缺少两个页面授权环境变量，构建按既有配置校验退出 1。 |
| `pnpm_config_verify_deps_before_run=false pnpm test:modules` | 退出 1，53 通过、4 失败。仍为 `page-access.test.mjs` 第 37、139 行与 `registry.test.mjs` 第 249、299 行的旧路由、访问清单或可见叶子断言，涉及已按 §9.1 退役的 `monitor.realtime`。 |
| QA2 受影响后端八文件 `pytest -q -p no:cacheprovider -m no_db` | QA2 退出 1，133 通过、3 跳过、2 失败。本轮后端及测试字节一致，未重跑该套件。两项失败为 `test_business_integration_migration.py::test_exact_chained_64_71_75_stages_and_four_table_parity` 的旧迁移文件数量，以及 `test_legacy_acquisition_retirement.py::test_single_head_and_metadata_retire_only_nine_tables` 的旧 metadata 全集。六项旧断言的更改均超出 §9.4 的既有测试允许范围，保留失败结果。 |
| Playwright `node <QA3 私有目录>/qa3-browser.mjs`、走读和 `mysql --defaults-extra-file=<QA3 私有 client.cnf> --batch --raw --skip-column-names` | 均退出 0。私有脚本及设置文件中的凭据未输出。SQL 验证限 `START TRANSACTION READ ONLY` 后查询 `metric_ingest_receipts`、两值表及 `INFORMATION_SCHEMA.TABLES`。可核查结果保留在本节、走读与浏览器证据中。 |

## QA3 收尾与 handoff

协调者按本轮归属停止专属 API 与 Vite，退出码分别为 0 与 1（SIGINT），`lsof` 确认两个端口无监听。核对容器 ID `9e4289b11f2ed9878e57177d53ceaab5ae2f75bb920408b8368e7e569db86f55`、任务／轮次标签、端口、SQL UUID 和 schema 后，协调者执行 `docker stop --timeout 5 <精确 ID>`、`docker rm <精确 ID>`、`docker volume rm aiis-arch-obs-001-r7-qa-db`，均退出 0。协调者复查任务标签匹配的容器与卷均已不存在，13395／13396／18395／18396／15395／15396 均无监听。QA3 私有凭据、日志和生成目录交协调者按归属收尾。验收证据保留在隔离交付源码、冻结基线、两份 canonical 源码证据、QA1／QA2 补丁与清单、QA3 14 张 PNG 及 JSON 和本记录中。

**ARCH-OBS-001 r7 QA3 为 `qa_passed`，覆盖 R7-AC01–07。** QA2 的两项本地化缺陷已关闭，无待返工或阻塞的 r7 验收项。两项后端与四项前端旧断言失败继续作为已知测试限制。交 Human Owner 对树摘要 `a54e4a777e728ffef3d4a7a14e0d74ca0b93c1111eb18ccae15e8cb495a4c7bf` 的隔离候选作最终验收，目前待决定。

本结论覆盖合成 v2 HTTP、第三方直连和合成 SMA 完整信封，以及隔离 Web 和 MySQL。实际 SMA 产品取数与投递、DAA、PLC、真实 profile、现有运行环境采用、性能和长时运行、源码整合、部署和发布各依后续批准验证。3307／8000／5190 不在本轮操作范围。原 QA2 断连重放证据覆盖客户端未知结果，数据库提交层故障注入未执行。

## r7 QA2 与更早独立验证记录

以下标记之间逐字节保留 QA3 写入前的 checklist 全部 74241 字节，SHA-256 `e1b7255f8360fd4273e8def8309b1601bdb65670b048eade849ea6fae85a4967`。

<!-- ARCH-OBS-001-r7-qa2-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA2 的 R7-AC06 管理界面本地化缺陷返回 Development，后续交 fresh-context Verification 复验
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA2 独立验证

2026-11-11（Asia/Shanghai）。以实际命名 `verification`、fresh context 接收 [r7 QA1 返工交接](tasks.md#r7-qa1-返工-development-交接)。依据 [Human Owner 对 r7 §9 的精确批准](spec.md#r7-acceptance)，在任务指定的隔离源码和 QA 实例上复验。按根与最近作用域工程契约、canonical lifecycle workflow、角色合同和任务三文件执行，使用 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`。角色权限为 `contract_only`。

## 候选与环境

| 对象 | 本轮证据 |
| --- | --- |
| 批准规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。批准原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| 返工交接 | `tasks.md` SHA-256 `157ccac9ceb5b9ae9482f7070161d9779075bd1e79346311fa77de201df68bc4`，返工记录从第 414 行起。 |
| 冻结基线 | `runtime/arch-obs-001-r7/baseline`，来源 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，888 文件的有序 SHA-256 树摘要 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。 |
| 正式隔离候选 | `runtime/arch-obs-001-r7/source`，924 文件的有序 SHA-256 树摘要 `82d8af23ebd68b56b88ee0dc9fcbfad806eb78446dacf4ec80d4f92bfbf2eada`。逐项扫描目录并核对文件摘要，57 个基线差异符合 §9.4。相对 QA1 仅返工交接列出的 11 个获准文件变化。 |
| 差异重建 | [canonical 补丁](evidence/r7-source.patch) SHA-256 `ff25fe4907deec1491dd7022dcaf81c8a00aba83c41b8b997504f63e009f02f4`，[清单](evidence/r7-source-baseline.json) SHA-256 `54e70feb81f36c7b0826c195d9a43ee982a965de0cc9459db3e51e1469b6015f`。冻结副本上 `git apply --check --whitespace=error` 和 `git apply --whitespace=error` 均退出 0，重建的 924 文件逐项匹配。QA1 的原补丁和清单各自哈希仍分别为 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb` 和 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10`。 [QA1 源码证据原件](../../runtime/arch-obs-001-r7/output/qa1-source/) |
| QA 隔离 | 实查 MySQL 8.4.6、`aiis-arch-obs-001-r7-qa`、`127.0.0.1:13396`、`arch_obs_r7_qa`、专用账号 `arch_obs_r7_qa_app`、UUID `01c83fe8-dd98-11f1-bbe4-d675dcc2c00b`、会话偏移 +28800 秒。复用 QA1 降级后带合成事实的库，由 `4e6a8b0d2f14` 升至 `5f7a9c1e3b26`，确认七张 r7 表。FastAPI `127.0.0.1:18396`，Vite `127.0.0.1:15396`。新增清洗、传动授权和间隔，以及只准入第一线的 admin 对照，均使用仓库外 QA 私有合成配置。 |
| DEV 隔离 | [Development 交接](tasks.md#r7-development-交接)记录 MySQL 8.4.6、`127.0.0.1:13395`、`arch_obs_r7_dev`、UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`、+08:00、API 18395、Web 15395，空库至新 head、受控降级和再升级。DEV 的测试为其自检，本轮独立测试使用 QA 目标。 |
| 工具与收尾 | macOS 15.7.7 arm64、uv 0.7.8、锁定 Python 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39 与 Playwright。Verification 停止 QA API/Web，`lsof` 确认 18396、15396 无监听。协调者核对精确 ID、标签和端口后已停止并删除 DEV/QA 两个任务容器及 `aiis-arch-obs-001-r7-dev-db`、`aiis-arch-obs-001-r7-qa-db` 卷，操作退出 0，复核 13395、13396、18395、18396、15395、15396 均无监听，也无本轮任务容器或卷。 |

## 验收结果

| 验收项 | 独立结果 |
| --- | --- |
| R7-AC01 源码与隔离 | **通过 §9.5 的可复核性要求。** 候选、基线、补丁、真实启动目录、允许差异、两轮隔离与回收、静态检查和构建均有可复核结果。受影响套件仍有后端 2 项、前端 4 项失败，见下表。实际新增七表和旧页面退役符合 r7，六项旧断言仍然失败。 |
| R7-AC02 迁移和兼容 | **通过。** QA1 的空库起步、旧/新匹配读写、错配及未知版本拒绝、维护计划和仅撤七表的降级证据保留。本轮独立重验带合成旧事实的 QA 库升至新 head、七表存在、新 profile 的 v2 写读和 typed 写入，以及 QA1 的 typed 事件重放返回原记录的 `duplicate`。新写分别为 `qa2-compat-new` 和 `qa2-typed-new`，typed 记录及回执 ID 3。相关采集、兼容性及迁移实现与 QA1 字节相同。 |
| R7-AC03 接入合同 | **通过。** QA2 两身份实际发现、两目标写入和 MySQL 数据对应；第三方可省略字段，显式空实时质量保存为 `unknown`，SMA 缺完整信封拒绝。缺凭据/无效、停用/越权、媒体类型、超长、禁用指标、类型、历史白名单及坏/空质量按独立行为用例复测，历史缺省质量的域用例通过。 |
| R7-AC04 任务证据 | **通过。** 新合成 `QA2-A` 到 `QA2-B` 换单、B 单缺组、晚到 A 按原任务和六位小数原采集时间留存。空闲、过期、错点、未知、伪造引用或原时刻及未获证明的第三方任务被按合同处理。生产实库及 Chrome 均保留文本卷号 `000042`。 |
| R7-AC05 数据与重试 | **通过。** 独立 HTTP/MySQL 验证新建、覆盖同 ID、`stale`、事件冲突、同源历史 `already_stored` 和两目标分开确认。A 单实时成功后历史仍为 0，历史客户端发送后关闭连接，读取到已入库的 1 条，再重放返回该行，实时回执不变。100 槽占满、停用仍占位、超限 422、重复绑定 409，首用后类型/单位更新拒绝，启停保留首用时间。实库保存 JSON 数字 `0`、布尔 `false` 和卷号字符串。 |
| R7-AC06 页面与权限 | **失败。** QA1 的曲线引用、两类详情采集质量和详情设备范围三项均关闭。实际 Chrome 的四卡片、三个带值曲线页、第二条产线、两类分页列表、管理字段编辑、拖拽和重置、入口与角色行为均按下述证据验证。另发现管理页面本地化缺陷，详见返工项。 |
| R7-AC07 交接与复跑 | **通过。** `000042` 的两份合成 v2 事实、第三方省略版与 SMA 完整信封、四次回执、库值及页面相互对应。双语走读及机器合同明确 SMA 独立登录的 `plc-facts-read` 和按 PLC/DB 的 `readScopes`，观察写 Bearer 另授设备/组/目标/指标权限。写明 SMA-004 产品 GET→POST、ARCH-ACQ-001、精确 ARCH-BE-012 provider/合同及隔离独立 QA 与 Owner 验收、精确 DAA-010 批准及新隔离 profile。联调按每个 PLC/DB 对照 SQLite 原样本和冻结请求、后端历史和 latest、回执和 SQLite 持久确认，再核对 SMA 映射和两路观察写入。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#后续-sma-取数和-daa-联调前置条件) · [英文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.md#prerequisites-for-future-sma-reads-and-daa-integration) |

## 命令与结果

| 命令或方法 | 本轮观察 |
| --- | --- |
| 候选 `backend/` 的 `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql`，守卫 QA 目标后的 `alembic upgrade 5f7a9c1e3b26` | 均退出 0。离线 DDL 和数据库都核对七表。通过私有环境运行候选 `python main.py`。 |
| `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py` | 退出 0，**5 passed**。测试自身先核验 round/UUID/端口/schema/账号/时区/revision。实测双向竞争同指标行锁、曲线保存等待后拒绝布尔引用、类型修改等待后拒绝已提交的曲线引用。另独立通过 HTTP 对启用曲线、停用曲线、启用组内的停用序列逐项 PATCH，均为 409 `equipment_observation.curve_items`，读取类型仍是 `number`，清除引用后 PATCH 200 可变为 `boolean`。 |
| 两组实际设备范围对照 | 用限 `line-01` 的管理员，允许范围的详情（实时 10、历史 8）GET 200。第二条线的真实记录（实时 4、历史 2）和不存在的 999999999，在两类 GET/PATCH 的四个组合均返回 HTTP 404、`application/json` 及逐组相同的响应体 `equipment_observation.not_found`。显式请求第二线的列表均为 403。拒绝前后的第二线有序 SQL 行导出 SHA-256 均为 `98a11060abb9ccb3187563268ed91c2b433149713e426cf0eceb14e147916d98`。 |
| `uv run --offline --frozen --no-sync pytest -q -p no:cacheprovider -m no_db` 受影响后端八个测试文件，按 QA1 同组 | 所有 bootstrap、mock 和 projection 开关关闭后退出 1，**133 passed、3 skipped、2 failed**。业务迁移测试 `test_exact_chained_64_71_75_stages_and_four_table_parity` 固定 11 个迁移文件，候选为 12。旧采集退役测试 `test_single_head_and_metadata_retire_only_nine_tables` 仍断言旧 metadata 表全集。首跑留有 QA supervisor bootstrap 开关，旧隔离守卫测试额外失败，关闭后已通过。 |
| `pnpm check:modules`、`pnpm build --outDir <QA 私有构建目录>`、`node --test tests/module-registry/equipment-observation.test.mjs` | 均退出 0。28 路由、10 组、新定向用例 2 passed。沿用候选已装锁定依赖，设置 `pnpm_config_verify_deps_before_run=false` 禁止依赖预检尝试重装，构建保留已有大 chunk 提示。 |
| `pnpm test:modules` | 退出 1，**53 passed、4 failed**。原 `page-access.test.mjs` 第 37、139 行和 `registry.test.mjs` 第 249、299 行固定旧 `monitor.realtime`、访问清单或叶子集合。QA1 已证实冻结基线的对应后端旧断言和 Web 断言通过。两项后端与四项前端旧断言的修改超出 §9.4 的精确旧测试范围，保留现状。 |
| Python AST、JSON、Markdown 和 i18n 检查 | 候选 27 个变更 Python 文件解析通过。三条 OpenAPI 路径及全部内部 `$ref`、请求向量和示例 profile JSON 通过解析。设备 131 个和过程 209 个 locale 键的双语集合一致。11 个变更 Markdown 检查 266 个相对链接和锚点，新增失效 0。81 个缺失都来自冻结子集原有的 `CODE_INDEX.md` 外部模块目标，基线已有相同缺项。新索引的代码路径存在。 |
| 候选 Web 和真实 Chrome | `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort` 代理到 18396。Playwright 10 组脚本断言通过，0 pageerror。实际拖拽两类列表均为 150→231 px，刷新恢复 231 px，重置 150 px。普通 supervisor 登录可读温控，管理页被拒，直接请求管理 API 为 403，机器凭据为 401。两种管理详情的实际 GET 和保存响应为 `quality=good`，DOM 在中英文分别出现「采集质量／正常」和「Source quality／Good」。最新备注和历史备注／`reviewed` 均实际 PATCH 200，重新打开保留。 [独立浏览器 DOM 与接口结果](../../runtime/arch-obs-001-r7/output/playwright/qa2-browser-result.json) |

浏览器结果 JSON SHA-256 `72e1ed6a218c45194147d19f1777c2baa27f71c31014cb299ce2867b7b4e5c92`。部分详情 PNG 采于进入动画，仅显示底层列表，曲线 PNG 也处于初始绘制。详情及曲线值以实际 DOM、ECharts option 与 HTTP 数据记录判定。缺测断点的回归由 QA1 证据与本轮定向模块用例支持。

## 合成任务 000042 的请求、回执和显示

在 QA 候选从 `backend/` 运行 `python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`（使用锁定 uv 和 QA 合成凭据），退出 0。实测两份 v2 事实均在 `plc-01/DB42`，`point-active-task-no` 的值为 `"000042"`。下列回执和槽位由 MySQL 只读查询确认。

| 来源 | 两路请求及任务证据 | 回执和库值 |
| --- | --- | --- |
| 第三方 | 原事件 `vendor-1794381796282315`，任务点关联 v2 样本 `demo-external-1794381796282315`，原时刻 `2026-11-11T15:23:05.000000+08:00`。实时为最简请求，历史明确提供 `quality=good`。两路均报实测 811.2、设定 815.0。 | 目标 `latest`、`history` 均 `stored`，回执 ID 17、18，值表行 10、7。实时重放返回同一回执。历史槽位 `{"07":811.2,"08":815.0}`。 |
| 合成 SMA | 完整信封使用 `demo-latest-1794381796282315` 和 `demo-history-1794381796282315`，两者共用 `demo-sma-1794381796282315` 和原时刻 `2026-11-11T15:23:15.000000+08:00`，任务点及数值引用来自已入库事实。 | 两路均 `stored`，回执 ID 19、20，值表行 10、8。较新样本覆盖同一实时行，槽位 `{"01":812.2,"02":815.0,"03":false}`，历史独立追加 `{"07":812.2,"08":815.0}`。 |

同一轮合成清洗 36.5、传动 48.75 分别实写 latest 槽 01 和 history 槽 07，来源样本分别为 `qa2-group-cleaning-1794381791699658`、`qa2-group-drive-1794381791699659`。生产槽位为 `{"01":"000042","02":0,"03":false}`。Chrome 的四个设备页读回上述生产、清洗、传动、温控值。历史温度两序列共用一条 °C 轴，清洗和传动各一条 Hz 轴。第二产线在同一温控页显示 `000043 / 727.0`。 [温控设备页](../../runtime/arch-obs-001-r7/output/playwright/qa2-task-000042-temperature.png) · [曲线和卡片读值](../../runtime/arch-obs-001-r7/output/playwright/qa2-browser-result.json)

## R7-AC06 返工项

1. **历史列表的复核值未本地化。** QA2 实际 Chrome 将 `000042` 温控记录标为已复核并保存，切换中文后，历史列表「复核标记」仍显示内部枚举 `reviewed`。共用组件对该列直接显示 `reviewMark`，该组件的详情下拉与现有字典已有「已复核」和「异常」。按 §9.1、R13 和根 AGENTS §5，普通管理列表也需用中英文显示复核状态，并与采集质量列区分。复验应涵盖中文「已复核／异常」、英文「Reviewed／Abnormal」及未标记状态，保存继续使用既有键。 [实际中文历史列表](../../runtime/arch-obs-001-r7/output/playwright/qa2-task-000042-history-detail-zh.png) · [列表列定义](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L28)
2. **英文名称和标题列的表头与数据语言不符。** 静态对照模板和英文 locale 后确认，两类详情共用表以及指标配置表固定表头 `nameZh`（Chinese name），英文时单元格取 `nameEn`。卡片和曲线配置表固定表头 `titleZh`（Chinese title），英文时单元格取 `titleEn`。这些列的表头需准确描述当前展示的名称或标题，复验两种语言下的对应表头及单元格，同时检查既有列宽偏好。此项依据模板与词典，QA2 的浏览器脚本未断言这些表头。 [共用详情](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L47) · [指标配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/views/observations/admin.vue#L14) · [卡片配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/views/observations/admin.vue#L49) · [曲线配置](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/monitor/views/observations/admin.vue#L14) · [英文词典](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/locales/en-US.json#L108)

## Verdict 与 handoff

**ARCH-OBS-001 r7 QA2 为 `qa_failed`。** 原 QA1 四项均已关闭。R7-AC06 本轮发现的两处管理页面本地化问题返回 Development，按同一获准范围固定新候选后交 fresh-context Verification。Human Owner 最终验收待后续 QA。两项后端和四项前端旧断言失败仍需在交接中可见。

本轮实际操作限于批准的隔离 MySQL、API、Web 以及合成事实和请求。现场 PLC、DAA、SMA 产品取数和投递、真实 profile、3307／8000／5190、生产采用、性能与长时运行、整合、发布和部署均未验证。断连用例验证发送方未知结果及回执重放，未注入数据库提交层故障。必要 SQL、HTTP 和命令证据已固化于本记录。保留隔离候选、冻结基线、源码补丁与清单、QA1 原证据及脱敏浏览器产物供复验和 Owner 审核，复验新建同一批准范围内的独立 QA 目标。私有 QA/DEV 凭据、日志和构建目录由协调者按归属收尾，结论无需依赖其保留。

## r7 QA1 与更早独立验证记录

以下标记之间保留 QA2 写入前的 checklist 全部 57315 字节，SHA-256 `3d9c5c749e35de3b596bacef9dbd5cc74e0c798c9232fb847f707dd4c1e35aca`。

<!-- ARCH-OBS-001-r7-qa1-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r7
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r7 QA1 实现与交接说明缺口返回 Development 返工，复验通过后由 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r7 §9.5 R7-AC01–07

# r7 QA1 独立验证

2026-11-11（Asia/Shanghai）。以 `verification` 命名角色、fresh context 接收精确的 r7 交接。独立读取根及最近作用域的 AGENTS、README／PLAN、canonical workflow、Verification TOML、任务三文件、候选源码、补丁和 DEV 证据。按 `project-governance`、`aiis`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 复核。独立轮次使用自己的合成数据与凭据。角色权责为 `contract_only`。 [批准规格](spec.md#r7-acceptance) · [Development 交接](tasks.md#r7-development-交接)

## 精确候选与环境

| 对象 | 独立核对 |
| --- | --- |
| 批准规格 | SHA-256 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。Human Owner 原话「批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证」。 |
| Development 交接 | SHA-256 `21bfb30971cdaa3268cbf200b6a6e28691b9ec92f98e7efa5bb933990bb488f8`。最初接收的摘要为 `41512d35b31aeb33e841abf715efa95e07316926b7906d70d56aa5c283b2e078`。Development 随后同步顶层 r7 元数据。当前 r7 交接从第 306 行起，候选与补丁摘要未变。独立确认旧 23232 字节历史仍匹配 `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3`。 |
| 正式隔离源码候选 | `runtime/arch-obs-001-r7/source`。924 文件的路径排序 `sha256  path\n` 树摘要 `e7db1a69d1f083bb1a89fd0504ad2e7554ef40c26624b9f7fbd930e7824b4402`。 |
| 冻结基线 | `runtime/arch-obs-001-r7/baseline`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。888 文件树摘要 `4b3a43509e79325dde6fbe124392e858f2381878dab98063068e090d3f65730f`。ARCH-ACQ-003 r2 QA2 已验收清单与冻结补充的 53 个路径逐项匹配。 |
| 公开差异 | [补丁](evidence/r7-source.patch) SHA-256 `eddb124065562d81227835899f675edd6f3594afdc9f5e1a9469bc2ed9e4c3cb`，[清单](evidence/r7-source-baseline.json) SHA-256 `8eb48a6e1d91e2a158e1726674502c5df3d39b4a90e18334eac3af120b872d10`。逐项匹配 57 个差异与 §9.4。对冻结基线临时副本执行 `git apply --check --whitespace=error` 和 `git apply --whitespace=error` 均退出 0，重建的 924 文件逐项匹配。 |
| QA 隔离目标 | MySQL `8.4.6`，`aiis-arch-obs-001-r7-qa`，`127.0.0.1:13396`，专属账号及 schema `arch_obs_r7_qa`，UUID `01c83fe8-dd98-11f1-bbe4-d675dcc2c00b`，会话偏移 `28800` 秒。FastAPI `127.0.0.1:18396`，Vite `127.0.0.1:15396`。迁移前实查 0 表。 |
| DEV 隔离目标 | 交接记录的 `127.0.0.1:13395`，schema `arch_obs_r7_dev`，UUID `c9a8a3ed-dd91-11f1-8e90-e27dd38db63b`，API `18395`、Web `15395`，空库 → 新 revision → 受控降级与再升级。该轮为 Development 自检。 |
| 工具链和资源 | macOS 15.7.7 arm64、uv 0.7.8、Python 3.13.3、Node 22.19.0、pnpm 11.11.0、Chrome 157.0.8103.39、Playwright。后端以 `uv run --offline --frozen --no-sync` 读取现有锁定依赖，Web 用候选的锁定依赖。QA 账号和 profile 使用仓库外专属目录。QA API／Vite 已停止，`lsof` 核对 18396／15396 无监听。两轮独立 MySQL 和卷保留供返工后复验，QA 库最后为旧 revision。保留候选、冻结基线、补丁和下列脱敏证据；协调者在复验不再依赖时核对归属并回收。 |

## 验收结果

| 验收项 | 独立结果 |
| --- | --- |
| R7-AC01 源码与隔离 | 源码、补丁、环境及回收状态均可复核。离线 DDL、manifest 预检、构建和本轮新增用例通过。受影响套件仍有 2 项后端、4 项前端失败，冻结基线的同组断言通过，详见下文。 |
| R7-AC02 迁移和兼容 | 通过。空 QA 库升级到 `4e6a8b0d2f14`，以旧 profile 写读 v2 样本，写入 typed 温控数据及回执，维护只读计划成功。带样本升级到 `5f7a9c1e3b26`，旧四表按行导出逐字节一致，仅增七表。旧 profile／新 revision 与未知 profile revision 的 v2 写、v2 读、typed 写均返回 503。新 revision 上旧 profile 的维护计划退出 1，新 profile 的计划退出 0。新 profile 的 v2 写读及 typed 写入通过，重放旧 typed 事件返回同一回执记录及合同规定的 `duplicate`。最后仅降级 r7，表集合恢复且旧四表逐字节一致。 |
| R7-AC03 接入合同 | 通过。第三方与合成 SMA 均成功通过发现 GET 和两目标 POST。无效或无凭据 401，停用和越权 403，超长／错媒体类型 413／415，禁用指标、非法类型、历史空值／坏质量和 SMA 信封缺字段的 HTTP 响应均为 422；历史缺省质量由 domain 用例验证拒绝。实时显式空质量保存为 `unknown`；发现仅列当前授权与启用键，历史采用白名单。 |
| R7-AC04 任务证据 | 通过。由 v2 HTTP 接收合成事实，切 B 后只显示 B 的缺测，晚到 A 存在 A 单，按 A 查询保留六位小数与 +08:00。绑定点缺失、过期、空闲分别验证，错点或无法证明的第三方任务及 SMA 伪造引用、错误原时刻被拒绝。生产样本的卷号 `"000042"` 读回保留前导零。 |
| R7-AC05 数据与重试 | 通过。真实 MySQL 观察新建、覆盖同 ID、`stale` 回执、冲突 409、同源历史 `already_stored`、两目标各自回执。A 实时提交后历史仍为 0；独立历史请求发完即关闭连接且不读取响应，历史变为 1，重放返回该同一行，实时回执保持原值。实测 100 槽余量 0，禁用仍占位，第 101 槽 422、重复绑定 409，首用后类型／单位变更 409，槽位停启保留首次使用时间。 |
| R7-AC06 页面与权限 | **失败。** 真实 Chrome 核对四卡片、三曲线、双语、两个管理列表的编辑、列宽、入口与普通读者权限；两条合成产线复用同一页面。发现曲线引用类型不变量、两个详情的采集质量和详情设备范围三个缺陷，见下文。 |
| R7-AC07 交接与复跑 | **失败。** 实际走读与 MySQL、页面对应通过。交付说明没有写清后续 SMA 取数身份，也没有给出 DAA-010 的联调范围和前置条件。 |

## 独立命令与脱敏证据

- 候选后端以 `uv run --offline --frozen --no-sync alembic upgrade 4e6a8b0d2f14:5f7a9c1e3b26 --sql` 生成七张新增表，退出 0。对专属 QA 实例依次运行 `alembic upgrade 4e6a8b0d2f14`、`alembic upgrade 5f7a9c1e3b26`、`alembic downgrade 4e6a8b0d2f14`，均退出 0。旧阶段合成事件 `qa-compat-old`、`qa-typed-old`，新阶段 `qa-compat-new`、`qa-typed-new`，两个 typed 回执分别引用记录 1、2。迁移前后 `plc_facts_history`、`plc_facts_latest`、`equipment_temperature_samples`、`equipment_integration_receipts` 的有序行导出 SHA-256 同为 `fa480d7441bed7f20994dba6540cbf1ade7aa7c906e06742cac51aa2235d67c8`，后续读写后降级前后同为 `71fb0aae94a87298ff34439f758104d78bb5f3796fb01a6299715e80a11f738e`。空库链分段执行，在旧 revision 装配样本后续升。维护执行 `python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan`，明确 alias、UUID、schema、revision 与批准引用，两个匹配 profile 均回报 0 候选，错配拒绝；无 `--apply`。
- 在候选 `backend/` 显式 `python main.py --maintenance bootstrap-users` 建立合成账号，然后 `python main.py` 运行 API。受影响后端 `pytest -q -p no:cacheprovider -m no_db --basetemp=<私有目录>/candidate-pytest` 覆盖 `test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_acquisition_facts_migration.py`、`test_business_integration_migration.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_equipment_observation_domain.py`，结果 **133 passed、3 skipped、2 failed**，退出 1。三个 skip 对应需专属 ACQ-003 夹具的旧实库用例，以及固定候选的 BE-003 和 BE-012 B 两个历史用例；另以目标 UUID/schema/端口/账户和轮次 ACK 运行 `pytest -q -p no:cacheprovider tests_mysql/test_equipment_observation_mysql.py`，**2 passed**，退出 0。
- 候选前端 `pnpm check:modules` 退出 0，注册 28 routes、10 groups。`pnpm build --outDir <私有目录>/frontend-dist` 使用显式 supervisor/operator 页面清单，退出 0，保留既有大 chunk 提示。`pnpm test:modules` **53 passed、4 failed**，退出 1。以同依赖运行冻结基线的两个相关后端断言，**2 passed**；冻结基线 `node --test tests/module-registry/{page-access,registry}.test.mjs`，**21 passed**。候选设备与过程 locale 分别 128／209 个键，双语集合一致；三条新 OpenAPI 路径、全部内部引用及样例 JSON 解析通过，变更行的 40 个本地文件链接有效。
- 实际运行 `python ../contracts/published/http-api/equipment-observation-v1/walkthrough.py --base-url http://127.0.0.1:18396`，退出 0。第二次走读的第三方 v2 样本 `demo-external-1794380100142868` 于 `2026-11-11T14:54:49.000000+08:00`，两路 `stored` 回执行 ID 分别 1、6。SMA 合成客户端的 v2 样本 `demo-sma-1794380100142868` 于 `2026-11-11T14:54:59.000000+08:00`，两路 `stored` 回执行 ID 分别 1、7。按 `metric_ingest_receipts` 查询的两个 caller 的各自两路 `task_evidence` 分别指向各自同一采集样本和 `point-active-task-no`。数据库实际温控快照槽位 `{"01":812.2,"02":815.0,"03":false}`，SMA 历史 `{"07":812.2,"08":815.0}`，第三方历史 `{"07":811.2,"08":815.0}`。生产快照为 `{"01":"000042","02":0,"03":false}`。第二产线使用 `plc-qa-02/DB77/qa-other-task` 和独立历史规则，任务 `000043` 的温控快照 `727/730/false`、历史仅 `{"07":727}`。两个调用者的 HTTP 凭据均为合成私有凭据。
- 真实 Chrome 访问候选 `pnpm exec vite --host 127.0.0.1 --port 15396 --strictPort`。四个设备页实际渲染，包括跨页线速度 0、活动 false、缺测和陈旧；温控页切换第二产线显示 `000043 / 727.0`。三过程曲线页面有 ECharts canvas，清洗和传动展示本轮配置的空序列；温度组仅一条 °C 纵轴、两序列且缺采样时插入 null；读取 `000042` 的 `811.2/812.2` 和 `815.0`。最新和历史两张表各完成实际拖拽 `150 → 231 px`、刷新恢复 `231 px` 和重置 `150 px`。两条备注实际 PATCH 200，重新打开仍在；历史标记为 `reviewed`。普通 supervisor 可读温控、无法进入管理页，直接 HTTP 管理操作 403；机器凭据管理操作 401。能耗和采集数据入口可用，退役路径重定向且无菜单入口。浏览器未捕获 pageerror。 [浏览器证据](../../runtime/arch-obs-001-r7/output/playwright/qa-browser-result.json) · [温控](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-temperature.png) · [曲线](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-temperature-history.png) · [历史详情](../../runtime/arch-obs-001-r7/output/playwright/qa-task-000042-history-detail.png)

## 缺陷与待处理的回归断言

1. **R7-AC06／R11，已启用曲线可保留布尔指标。** 管理员 POST 创建未首次入库的 Hz 数值指标 `qaCurveMutation`，将其加入启用的传动曲线 `qa-mutation`。随后 PATCH `/api/v1/equipment/metric-configs/qaCurveMutation`，发送 `{"valueType":"boolean"}`，候选返回 HTTP 200 并将类型改为 `boolean`。GET `/api/v1/monitor/curve-configs?category=drive` 仍显示该启用序列。R11 要求已登记的数值型指标，更新入口需维持该条件。 [指标更新实现](../../runtime/arch-obs-001-r7/source/backend/app/equipment_observation/services/configuration.py#L54)
2. **R7-AC06／R13，两类详情缺采集质量。** Chrome 打开 `000042` 温控的实时和历史详情，详情 API 与保存响应均含 `quality: good`。两个 dialog 的 `Source quality` 文本计数均为 0。列表有质量列，详情包含来源、指标、备注及历史复核标记，仍缺规格要求的采集质量。 [共用详情模板](../../runtime/arch-obs-001-r7/source/frontend-js/src/app/equipment/components/observations/RecordList.vue#L33)
3. **R7-AC06／§9.1，管理详情先按全局 ID 查记录。** 用私有 profile 将 admin 的设备范围限制为 `line-01`，GET 和 PATCH 实际存在且越权的第二产线快照 `5` 和历史 `4` 均返回 403，同类不存在的 `99999999` 均返回 404，显式设备越权列表返回 403。详情通过 `db.get(model, identity)` 后才检查设备，违反服务端先限制设备再查询的要求，并可据响应区分越权记录是否存在。 [详情实现](../../runtime/arch-obs-001-r7/source/backend/app/equipment_observation/services/reads.py#L145)
4. **R7-AC07，后续取数和联调交接缺项。** 双语走读、机器合同和 r7 handoff 说明了后续真实 SMA 产品、DAA 接线与实际启用分别批准，但没有规定后续 SMA 取数身份／读范围，也没有指出 DAA-010 联调的范围、前置条件和与本轮合成 HTTP 验证的接口。该条需补交接说明。 [中文走读](../../runtime/arch-obs-001-r7/source/docs/equipment-status-process-monitoring.zh-CN.md#r7-walkthrough) · [机器合同](../../runtime/arch-obs-001-r7/source/contracts/published/http-api/equipment-observation-v1/README.zh-CN.md)
5. **R7-AC01，候选现有套件六项回归断言失败。** `test_business_integration_migration.py::test_exact_chained_64_71_75_stages_and_four_table_parity` 固定 11 个迁移文件，候选为 12。`test_legacy_acquisition_retirement.py::test_single_head_and_metadata_retire_only_nine_tables` 的旧元数据全集断言因新增七表失败。Web 的 `page-access.test.mjs` 第 37、139 行及 `registry.test.mjs` 第 249、299 行断言旧 `monitor.realtime`、访问清单或原可见叶子集合。真实路由已按 §9.1 退役，真实迁移仅增七表。这六项仍为失败测试，涉及的旧断言或文件超出 §9.4 当前授权的既有测试改动范围，保留原样；任何扩大范围由 PM 和 Human Owner 处理。

## Verdict 和 handoff

**`qa_failed`。** R7-AC06 的三个实现问题与 R7-AC07 的交接说明缺项返回 Development。返工交接应固定新候选摘要、保留本轮记录，并以 fresh-context Verification 重查变更及相关验收。r7 的 Human Owner 最终验收仍待后续 QA 结果。

本轮使用合成 v2 HTTP、合成 SMA 完整信封及第三方 HTTP。未运行真实 SMA 产品、DAA、PLC 或真实 profile，未访问 3307／8000／5190。网络断开覆盖客户端未知结果及重放，未注入 MySQL 提交层故障。生产采用、性能、长时间运行、发布、合并和部署仍需各自授权及验证。

## r6 及更早独立验证历史

下列标记之间为 r7 追加前的原文件 42053 字节，SHA-256 `e70ee2bf4b110eee84e5385d898fa1dea155debbc6ce44783ce03d972f9baab5`，原文逐字节保留。

<!-- ARCH-OBS-001-r6-checklist-history-begin -->
Task ID: ARCH-OBS-001
Revision: r6
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: ARCH-OBS-001 r6 §7.4 D-06 文档交 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r6 §7.4 D-06

# D-06 Verification

2026-11-11（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。按 [r6 §7.4 D-06 文档范围](spec.md#r6-d-06-第三方与-sma-接入说明)和 [D-06 Development 交接](tasks.md#d-06-developer-handoff)核验当前工作树候选。交付路径为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，分支 `main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。静态核验环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1 和系统 Python 3.9.6。

| 候选 | 核验 SHA-256 |
| --- | --- |
| [r6 规格](spec.md) | `ea288e72715f4e29f6ec0f30431954935f23e3b1990538fc5624aa6eae32f25a` |
| [Development 记录](tasks.md) | `8e64a7398d552dde18baf242e15274648b0e9b4eaa0a3bf26737387f1740dca3` |
| [英文审阅稿](../../docs/equipment-status-process-monitoring.md) | `ac7970c856038a9cc289a167da714ca287d92c93ebeb5c5a0d951553185ac799` |
| [中文审阅稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `0b005b6b1077187438518830c4d4fea44eb5a8df3d8ace0c4dda6fcd807ec194` |

## D-06 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D06-AC01 字段规则 | 通过 | SMA 每次发送完整信封，包括可预先配置的固定字段和真实 `plc_fact` 来源。第三方每次提供 `external_event`、稳定的 `sourceEventId`、采样时已确认的 `taskNo`、带偏移的原 `sampledAt` 及至少一项准入指标。接入绑定补齐 `producerId`、`sourceId`、成对的 `mappingId` 和 `mappingRevision`，协议缺省为 `aiis.metric-ingest/v1`。仅单设备单组固定身份可省略设备与组，多设备或多组必须提供两项。第三方实时的 `quality` 省略或显式 `null` 均记为 `unknown`，历史必须据实明确提供 `good`。缺测指标省略键，指标值 `null` 导致整包拒绝，`0` 和 `false` 保留。两稿说明系统管理字段的边界并链接规格。 [字段规则](spec.md#third-party-ingest-fields) |
| D06-AC02 权限与发现 | 通过 | GET 必传 `equipmentId`、`groupKey` 与 `target`，需要已认证、启用并获准写入该设备、组和目标的集成身份。未认证为 `401`，已认证但停用或越权为 `403`，均不返回定义。获准但没有可写指标时，`definitions` 为空。指标准入、目标启用槽位与组归属取交集，历史再取设备和组的白名单。返回指标键、类型和可选单位，已存值及内部槽位不返回。业务读和管理员入口分别校验，POST 重新校验准入。 [发现 GET](spec.md#指标发现示例) |
| D06-AC03 最简请求与回执 | 通过 | 两个示例使用获准双目标且绑定固定设备、组和来源的同一身份，共用 `vendor-sample-42`、原任务 `000042`、原时间 `2026-11-11T09:30:00.123+08:00` 和数字指标 `furnaceZone1Actual`。历史比实时多显式 `quality: "good"`。两条 POST 路径与九段原 JSON 保留，完整 SMA 请求仍各有投递号和任务号点位证据。第三方来源事件号跨目标及重试稳定，投递 `eventId` 按目标区分，调用方可显式复用或始终省略。既有回执按其映射信息核对规范化内容，映射版本更新后仍可返回原结果，内容变化则冲突。两稿均链接字段规则和两个样例。 [最简实时请求](spec.md#third-party-latest-example) · [最简历史请求](spec.md#third-party-history-example) |
| D06-AC04 文档边界 | 通过 | r6 软件设计仍为 `draft`。核验前，与 D-05 对照的本任务差异为 PM 规格、双语指南及 Development 交接。D-01 至 D-05 的规格授权与验收正文和 Development 历史保留，原 QA 历史已归档于下方。六份索引的 ARCH-OBS-001 行在 QA 写入前仍对应 D-05，交协调者按本结论同步对应行。双语根 PLAN 和任务目录另有 ARCH-ACQ-003 的并行验收更新。 |

## D-06 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`git diff --cached --quiet`、`shasum -a 256` | 退出 0。工作树、暂存区状态及四项候选摘要符合交接。五份任务相关文档为工作树未跟踪文件，内容用编辑前副本核对。 |
| `diff -u` 逐文件对读，内联 `python3` 用 `hashlib.sha256` 和字节比对核对 11 个编辑前路径 | 正文比较退出 1，符合预期差异。首次将并行索引更新一并断言为字节相同，退出 1。复核后按 ARCH-OBS-001 行及 ARCH-ACQ-003 差异分开比较，退出 0。四份 D-05 对照摘要匹配原核验记录，D-01 至 D-05 授权和验收正文、D-05 至更早的 DEV 正文、QA 写入前的历史 checklist 均保留。 |
| 内联 `python3` 用 `json.loads` 检查围栏并比对字段、标量类型和时间偏移 | 退出 0。11 段 JSON 均可解析，无重复键或非 JSON 数值。九段原 JSON 逐字节一致。两个新请求满足固定接入的最少键集合，历史指标在 GET 示例的可写集合内。 |
| 内联 `python3` 核对相对路径、显式 ID、Unicode 标题锚点、双语规格链接及 Mermaid 源码 | 首次链接检查的 `Counter` 比较在 Python 3.9 退出 1，改用多重集差后退出 0。两稿各 39 个本地链接，规格 12 个、DEV 10 个、历史 QA 58 个、六份索引相关行 14 个，写入前共 172 个本地链接解析成功。两稿的规格链接集合一致，旧链接和显式锚点保留，两段 Mermaid 源码逐字节一致。 |
| `git diff --no-index --check -- <编辑前文件> <候选文件>`、`git diff --check -- <六份索引>` | 四项候选空白检查均退出 1，符合预期内容差异，且无空白错误输出。索引空白检查退出 0。 |

## D-06 结论与交接

**ARCH-OBS-001 r6 §7.4 D-06 文档为 `qa_passed`。** D06-AC01 至 D06-AC04 全部通过。无阻塞和返工项。交 Human Owner 对上述精确候选作 D-06 文档最终验收，当前待验收。

本轮核验限于工作树中的 Markdown、样例、相对链接及图表源码。Mermaid 渲染和外链可用性未验证。凭据选型、正式 OpenAPI、代码、数据库、HTTP 运行行为及现场启用属于后续范围。两份通用任务讨论稿是既有本地链接依赖。编辑前副本由协调者管理，关键结论与候选摘要已记录，QA 无需另保留临时产物。

## 历史 Verification 记录（r6 D-05 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r6
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r6 §7.4 D-05 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r6 §7.4 D-05

# D-05 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立对读根工程契约及作用域索引、完整任务 bundle、双语审阅稿、编辑前差异及 DEV 自检，依据 [r6 §7.4 D-05 文档授权](spec.md#r6-d-05-完整方案审阅稿)和 [D-05 Development 交接](tasks.md#d-05-developer-handoff)核验。候选位于 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main` 工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。静态检查环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1 和 Python 3.9.6。

| 候选 | 核验 SHA-256 |
| --- | --- |
| [r6 规格](spec.md) | `b7ffda29b0ecb1631998ecff7611e54a76e5f88dcfcd0b2e368d23e7a7206512` |
| [Development 记录](tasks.md) | `cbbc9dd5a6f1c5d0508e63bbc3759a6e0a510831e97e51dfb590ae37ee918dfe` |
| [英文审阅稿](../../docs/equipment-status-process-monitoring.md) | `c1af519d2eb5846fa9d70fea89002f116d77478a8e8393124729a40a228af2c7` |
| [中文审阅稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `4154d8df6cc66b6fc87a1017bd114c504199253b3bb83e1f49b9b5dd9c3686a7` |

## D-05 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D05-AC01 原理与表 | 通过 | 两张值表定义固定列、候选 MySQL 类型、主键、唯一键与索引。实时唯一键为 `(equipment_id, task_no, group_key)`，较新样本替换采集字段时保留行 `id` 和备注。历史独立追加，以原任务、设备、组、采集时间和样本身份去重，任务索引为 `(task_no, sampled_at, id)`。两稿都说明共用指标登记、每目标每组各 100 个逻辑槽位、各表的 `local_values JSON`、首次成功存值锁定、停用仍占位及恢复原关联。回执按目标、生产者和事件区分。 [表定义](spec.md#33-本地槽位与物理表) |
| D05-AC02 接口与样例 | 通过 | 发现 GET 返回当前获准的键、类型及可选单位，历史受白名单限制。两条 POST 共用 `aiis.metric-ingest/v1`，路径区分目标。温控示例共用任务 `000042`、原帧 `sample-42`、任务号点位证据及 `2026-11-07T09:30:00.123+08:00`，各用独立事件号。历史发现的两个数字与历史请求一致。实时另含布尔就绪。按绑定核对实际 JSON 槽位，实时 `01/02/03`、历史 `07/08`、生产组卷号和状态 `01/02`。回执样例的 `recordId` 为字符串，两路各自持久确认与重试。两稿区分 SMA、业务读用户和管理员入口。 [发现、写入与回执](spec.md#5-sma-指标发现和写入接口) · [查询及配置](spec.md#4-前端查询和管理接口) |
| D05-AC03 任务与卷号 | 通过 | `task_no` 是固定业务字段，`id` 标识单行。`values.coilNo` 是可选字符串指标，前导零 `"000042"` 经样例落库映射保留。返工用新任务号，迟到样本仍归采样时任务，历史按任务查询和稳定分页。四页卡片、三页曲线、单位规则和独立永久历史留存保留。后端对两个管理列表核验登录、admin 及设备访问范围，实时仅备注，历史仅备注及与采集质量分开的管理标记。 [任务与换单](spec.md#32-任务归属和换单) · [管理权限](spec.md#43-实时快照与过程历史管理) |
| D05-AC04 新建与交付范围 | 通过 | 首版从空库及获准写入开始，依次定稿合同和合成样本、建设后端、并行开发前端与 SMA、隔离验证，首次现场启用另批。两稿互链并链接 r6 规格。D-01 至 D-04 原授权和验收段逐字节匹配 r5，历史角色记录可恢复。相对编辑前的 D-05 变更限于规格、两稿及角色记录，六份索引在 QA 写入前保持原摘要，交协调者同步对应行。 [首次启用与顺序](spec.md#71-首次启用与数据起点) |

## 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256`、`git diff --cached --quiet` | 退出 0。分支、HEAD、四项候选摘要匹配，暂存区无差异。 |
| 内联 `python3` 使用 `json.loads` 解析 JSON 并按键、类型和目标投影槽位 | 退出 0。九段 JSON 围栏及五份内联槽位对象通过。r5 的登记、卡片、卡片项响应和曲线示例保持原字节，两条温控上报只替换示例任务号。 |
| 内联 `python3` 核对相对路径、显式 ID、Unicode 标题锚点和 Mermaid 连线 | 退出 0。双语稿各 33 个本地链接，其中各 30 个带锚点。每稿六个旧入口加两个新入口，六条 Mermaid 连线与 r5 一致。QA 写入前，双语稿、三份角色文档和六份索引的相关行共 147 个本地链接均解析成功。 |
| `diff -u`、`git diff --no-index --check`（编辑前后四项候选）及 `git diff --check`（六份索引） | `diff -u` 退出 1，符合预期内容变化。四项候选空白检查均退出 1，输出为空。索引空白检查退出 0。 |
| `git diff --binary HEAD -- .` 排除 11 个文档路径、`git ls-files --others --exclude-standard -z` 及内联 `python3` 对照基线 | 原聚合比较退出 1。交接后，另一个任务更新 DAA 的双语 Stage C 手册及 DAA-008 的 `tasks.md`。当前范围外跟踪差异 SHA-256 为 `8cdf5c020d2956aa88583c47ac069e67d6e2b4ec21a28bdec14efeaacb3a43d9`。用已有手册原文和 DAA-008 记录的 129,501 字节原前缀，经管道运行 `git diff --no-index --binary` 重建这三份文档的原差异。重建比较退出 0，聚合 SHA-256 与基线 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb` 一致。范围外未跟踪仍为同六条路径，其中四份原字节一致，两份通用任务讨论稿有同期更新，当前所需锚点均可解析。基线清单 SHA-256 为 `e5b9abffbf1d65be1606c124f58b5677713ed1c774d446f0db38f2a1aa7e63ed`。 |
| 内联 `python3` 对照历史字节并去除旧元数据的引用前缀 | 退出 0。规格 D-01 至 D-04 授权及验收段 SHA-256 为 `74b96043dbec1f1f82c1321fc40971232af338d88cf084ebbf2bebf7b5561479`。恢复的 r5 Development 摘要为 `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7`。下方 r5 QA 历史可恢复至原摘要 `2693750db155673c791806bbe71dcb143a57e2142f8766485a74af1da46f8010`，原 r4 与 r3 摘要也匹配。 |

## D-05 结论与交接

**ARCH-OBS-001 r6 §7.4 D-05 文档为 `qa_passed`。** D05-AC01 至 D05-AC04 全部通过，无阻塞或返工项。交 Human Owner 对上述候选作 D-05 文档最终验收，当前待验收。D-01 至 D-04 的结论归原候选和角色记录。

本轮证据限于 Markdown、JSON、Mermaid 源码和工作树。`command -v mmdc` 退出 1，Mermaid 图形未渲染。本轮依据 §7.4 的局部文档授权，旧整包检查器的整体软件批准条件不适用于本轮。软件方案仍为 `draft`，DDL、OpenAPI 发布、实施、运行及现场采用按各自范围审批。两份通用任务讨论稿为本地链接依赖。关键证据已写入本节，编辑前对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r5 D-04 及更早修订）

> Task ID: ARCH-OBS-001
> Revision: r5
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r5 §7.4 D-04 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r5 §7.4 D-04

# D-04 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 与 PLAN、最近作用域索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。按 [r5 §7.4 D-04 文档授权](spec.md#r5-d-04-从零开始的总体方案讨论稿)和 [D-04 Development 交接](tasks.md#d-04-developer-handoff)核验。

## D-04 候选与环境

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。以下 SHA-256 与精确交接一致。

| 工作树文件 | SHA-256 |
| --- | --- |
| [规格](spec.md) | `cc1a481afc4b250e04e4daa33fcb6a29ae56531093fb9bb2d79e5a2fad295bf6` |
| [Development 记录](tasks.md) | `b06257104f812b7ce497ed59fc0cc4beb97470e37105d52854d1ce2965f203b7` |
| [英文讨论稿](../../docs/equipment-status-process-monitoring.md) | `6b5ad2a36f60cc2ed7b7816c74aa0378d2be4daf4374a127a039014aa2ffe88d` |
| [中文讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md) | `2e6723a2e1ccf9e461654dfdbce053f038aa1e7310c6e590cd3e642d0d5a8e8e` |

## D-04 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D04-AC01 首次启用 | 通过 | 先装配配置、从空库开始，首次获准后开启写入准入。首份验证通过且归属已确认任务的样本建立该组快照，首份同时符合历史白名单及选样条件的样本追加历史。无合格样本时实时呈空态或缺测，历史为空。换到 B 单后，符合条件的迟到 A 单样本仍按原任务与原采集时间处理。现行范围已移除旧数据兼容、迁移、切换和采集时间下界。 [首次启用](spec.md#71-首次启用与数据起点) · [任务归属](spec.md#32-任务归属和换单) |
| D04-AC02 项目预设 | 通过 | 三份正文均有生产参数、清洗、温控、传动四页卡片与温度、传动、清洗三页曲线组预设。双语标题和绑定对应，生产参数单指标卡片与固定卷号及卷状态分开。炉区 1 登记并贯通实际温度 810.2 °C、设定温度 815.0 °C、可选布尔就绪与共用单位的历史曲线，就绪值只进入实时。 [四页卡片](spec.md#2-设备状态四页) · [炉区指标与响应](spec.md#41-卡片配置和响应) · [三页曲线](spec.md#42-过程监控曲线组) |
| D04-AC03 共用规则 | 通过 | `metricKey` 稳定，写入保留 JSON 标量类型。可选共用单位用于标题或共用纵轴，值区只显示值。历史按独立白名单及间隔选样并永久保存。PLC 现场任务号证据随原采样保留，SMA 一次映射，分实时覆盖与历史追加两路并独立确认及重试。后端校验两个管理列表的权限，实时只改备注且覆盖保留备注，历史只改备注及管理标记。接口与 JSON 保持在规格内。 [SMA 合同](spec.md#5-sma-指标发现和写入接口) · [管理编辑边界](spec.md#43-实时快照与过程历史管理) |
| D04-AC04 顺序与范围 | 通过 | 双语指南互链并链接 r5 规格。顺序为合同和合成样本、后端、前端与 SMA 并行、空库受控验证，首次现场验证及启用另按真实产线批准。四项候选及 QA 记录是核验范围内的差异，六个索引在核验时仍对应编辑前对照，交协调者按结论同步对应行。历史授权和原角色证据已核对。 [实施与验证顺序](spec.md#72-首版实施与验证顺序) |

## D-04 命令与结果

| 命令或方法 | 实测结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256`、`git diff --cached --quiet` | 退出 0。分支、HEAD、四项候选摘要匹配，暂存区无差异。 |
| `diff -u` 对读规格和双语指南，内联 `python3` 字节比较、`git diff --binary HEAD -- . <排除 11 个文档路径>` 及 `git ls-files --others --exclude-standard -z` | `diff -u` 退出 1，预期正文有差异。Python 退出 0。QA 写入前，11 个对照路径只变动候选表中的四项。范围外跟踪差异的 SHA-256 为 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb`。范围外六个未跟踪文件的路径及内容摘要均与基线匹配，包括 DAA 的两份批准对照、两份 profile 源码和两份通用任务讨论稿。基线清单 SHA-256 为 `bc4b66f0dce2c0a1dabbebb3705e25f67ee8a82c8d3acb0629abc063ab274cdc`。 |
| 内联 `python3` 按相对路径、显式 ID 和 Markdown 标题解析链接 | 退出 0。每稿 25 个本地链接、22 个带锚点链接，均可解析。各保留六个阅读锚点，核对五个新增及三个替换目标。规格、Development、历史 checklist 及六个索引对应行的本地链接均可解析。初次检查仅以指南文件名匹配索引行，补充任务目录匹配后重跑通过。 |
| 内联 `python3` 使用 `json.loads` 严格解析并比对六段围栏，核对 Mermaid 源码和预设表 | 退出 0。登记和两路上报示例与 r4 逐字节相同，卡片、响应与曲线示例仅标题变化。两路共享 `JOB-20261107-001`、`sample-42`、采样任务点位、映射和带 `+08:00` 的原采集时间，`eventId` 各自独立。两路温度为 JSON 数字，布尔就绪仅实时，响应分开保留 `label` 和 `unit`。两稿各四页卡片、三页曲线及六条连线，Mermaid 源码保留原字节。 |
| `git diff --no-index --check -- <编辑前副本> <当前文件>`、`git diff --check -- <六份索引>` | 四项候选的前后比较各退出 1，输出为空。六份索引检查退出 0。 |
| 内联 `python3` 对照规格历史段并去除旧角色元数据的引用前缀后比较 SHA-256 | 退出 0。D-01 至 D-03 的规格授权及验收段原字节保留，SHA-256 为 `8917f42bd212d4c604ae503072e3c4ca0cd682d02916ea1db6469905136fd527`。恢复的 r4 `tasks.md` 与原摘要 `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d` 一致，下方 r4 历史核验记录可恢复至原摘要 `bdeb52c71f4341f00f57fed736df6b19df401d2719590ca9cdaf33ab4ec869fb`。r3 历史核验的原摘要 `42464b8c1774bf6e3211619f84286d26add9c28f93bb9bfdba08c6b1ae82750e` 也匹配。 |

## D-04 结论与交接

**ARCH-OBS-001 r5 §7.4 D-04 文档为 `qa_passed`，D04-AC01 至 D04-AC04 全部通过。** 无阻塞或返工项。交 Human Owner 对四项精确候选作 D-04 文档最终验收，当前待验收。D-01 的 Owner 验收与 D-02、D-03 的文档 QA 保留在各自历史记录。

本轮采用 §7.4 局部文档验收。旧整包检查器按整体软件批准流程检查。r5 软件方案为 `draft`，构建、运行、数据库和现场操作属于后续范围。Mermaid 核验限于源码，`command -v mmdc` 退出 1。两份既有通用任务讨论稿须随工作树供本地链接解析。关键证据已记在本节，编辑前临时对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r4 D-03 与 r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r4
> Status: qa_passed
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: ARCH-OBS-001 r4 §7.4 D-03 文档交 Human Owner 最终验收
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r4 §7.4 D-03

# D-03 Verification

2026-11-09（Asia/Shanghai）。fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域的索引、完整任务 bundle、双语指南、编辑前差异及 DEV 自检。核验范围以 [r4 §7.4 D-03 文档授权](spec.md#r4-d-03-任务归属和管理列表讨论稿)及 [D-03 Development 交接](tasks.md#d-03-developer-handoff)为准。r4 软件方案处于 `draft`。

## D-03 候选与环境

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。macOS 15.7.7（arm64）、Apple Git 2.50.1、系统 Python 3.9.6 用于本地文档静态检查。四项 SHA-256 均与交接一致，候选取自工作树。

| 文件 | SHA-256 |
| --- | --- |
| [spec.md](spec.md) | `5e8e9d7ffe670187afb142f5665525810313b69484384324a82df23832c0a8e3` |
| [tasks.md](tasks.md) | `d9f2290baeaad1c57cd653739ec6d2afd66515daa602c9aeb340a0a01176560d` |
| [英文指南](../../docs/equipment-status-process-monitoring.md) | `5f9d498808d9589ef1a6d4785f78da8636cf28baae9276ee02a0a14490733e2a` |
| [中文指南](../../docs/equipment-status-process-monitoring.zh-CN.md) | `fcd73dd295dc555170d0d855895478b8db40ec1a837c78f629c9b616ce4d0a47` |

## D-03 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D03-AC01 任务归属 | 通过 | 规范化时去首尾空格并将英文字母大写，项目内任务号唯一，库内用 `task_no`，API 用 `taskNo`。PLC 在开工或换单时更新 `activeTaskNo`，DAA 在采样时留存可核验证据。按设备、任务和组定位快照，卡片只读现场确认的当前任务。现场从 A 切到 B 后，晚到的 A 单仅影响 A 单快照，符合规则的历史仍按 A 单和原采集时间追加并可按原任务查询。B 单缺组显示缺测，现场空闲和任务归属不明各有空态。 [任务归属与换单](spec.md#32-任务归属和换单) · [中文数据流](../../docs/equipment-status-process-monitoring.zh-CN.md#data-flow) · [英文数据流](../../docs/equipment-status-process-monitoring.md#data-flow) |
| D03-AC02 SMA 两路 | 通过 | 一次映射的同源样本按独立周期和指标集合组成实时覆盖与历史追加，历史按组白名单独立选样。各目标使用独立的稳定事件身份和持久回执，分别确认及按原身份重试。六段 JSON 可解析，其中两路写入共享 `sample-42`、采样任务点位证据、映射版本、`JOB-20261107-001` 和带 `+08:00` 的原采集时间，分别使用 `temperature-42-latest` 与 `temperature-42-history`。两路温度均为 JSON 数字，布尔就绪值仅出现在实时。 [采样策略](spec.md#31-首版采样组与历史指标) · [写入示例和回执](spec.md#5-sma-指标发现和写入接口) |
| D03-AC03 管理列表 | 通过 | 实时快照列表归设备状态，过程历史列表归过程监控，入口仅向 admin 显示。两表按任务号、设备或产线及组筛选，历史另按采集时段筛选，后端分页。固定列为任务号、设备、组、采集时间及数据状态，详情按配置显示指标名称、单位和采集值。后端对列表、详情和编辑校验登录、admin 和设备访问范围，并拒绝编辑白名单外字段。实时仅可改备注，SMA 更新同一快照的采集字段时保留备注。历史可编辑备注及异常、已复核标记，管理标记与采集质量独立，原始值更正另立后续范围。 [管理接口](spec.md#43-实时快照与过程历史管理) · [中文管理列表](../../docs/equipment-status-process-monitoring.zh-CN.md#admin-lists) · [英文管理列表](../../docs/equipment-status-process-monitoring.md#admin-lists) |
| D03-AC04 文档与历史证据 | 通过 | 两稿逐节对读一致，保留原链接和阅读锚点，新增 D-03 范围、任务归属、管理接口及管理列表入口。接口与 JSON 仍由规格维护。可选共用单位、标题和数值分工、曲线纵轴、上海时区、切换时间下界及永久历史留存的口径可核对。候选差异仅在规格、Development 记录及双语指南。D-01、D-02 的授权段逐字节保留，两份 r3 角色记录的旧元数据去掉引用前缀后均可与原文件逐字节比对。 |

## D-03 命令与结果

| 命令或方法 | 结果 |
| --- | --- |
| `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256 <四项候选>`、`git diff --cached --quiet` | 均退出 0，工作树身份及摘要匹配，暂存区无变更。 |
| `diff -u <编辑前副本> <工作树文件>`、内联 `python3` 字节比较 | 规格和两稿差异均在 D-03 方案内。编辑前 11 路径中，QA 写入前仅上表四项内容变化，六份索引字节一致。r3 的两个授权段一致。去除历史元数据的引用前缀后，旧 `tasks.md` SHA-256 为 `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e`，旧 `checklist.md` 为 `42464b8c1774bf6e3211619f84286d26add9c28f93bb9bfdba08c6b1ae82750e`，均与编辑前副本一致。 |
| `git diff --binary HEAD -- . <11 项文档路径排除>`、`git ls-files --others --exclude-standard -z`、内联 `python3` SHA-256 核对 | 退出 0。文档范围外的跟踪文件差异 SHA-256 为 `f1e02a2d24c691777bb0238ba77b59e5ece7ed65ba20140f6b213332967b0ecb`，范围外六个未跟踪文件的路径及摘要均与编辑前基线一致。 |
| 内联 `python3` 解析相对路径、显式锚点及 Unicode 标题、校对 Mermaid 源码和 `json.loads` | 退出 0。每稿 23 个本地链接（20 个带锚点）、6 个阅读锚点、6 条 Mermaid 连线。三份角色文档与六份索引相关行的本地链接可解析。六段 JSON 均通过解析，前四段和 r3 逐字节一致，写入示例的内容差异限于共享映射 ID、任务号和采样任务点位证据。首次链接检查使用了 Python 3.9 不支持的 `Counter` 比较，改用多重集差后重跑通过。 |
| `git diff --no-index --check -- <编辑前副本> <当前文件>`、`git diff --check -- <六份索引>` | 规格、两稿和两份角色记录相对编辑前各退出 1，表示有内容差异，输出为空。索引空白检查退出 0。 |

## D-03 结论与交接

**ARCH-OBS-001 r4 §7.4 D-03 文档为 `qa_passed`，D03-AC01 至 D03-AC04 全部通过。** 无阻塞或返工项。交 Human Owner 对本节四项精确候选作 D-03 文档最终验收。D-01 的 Owner 验收及 D-02 的文档 QA 见下方历史记录，D-02 仍待 Owner 验收。

验证限于本地静态文档、样例和工作树。两份既有通用任务讨论稿是本地链接依赖。Mermaid 复核限于源码（`command -v mmdc` 退出 1）。软件构建、运行、数据库及现场验证属于后续独立审批。旧整包检查器要求规格整体为 `owner_approved`，本轮采用 §7.4 的局部文档验收口径。关键证据已记在本节，编辑前对照由协调者管理，QA 无需保留临时产物。

## 历史 Verification 记录（r3 D-01、D-02）

> Task ID: ARCH-OBS-001
> Revision: r3
> Status: owner_accepted
> Owner Role: QA / Verification
> Allowed Writers: QA / Verification, Human Owner
> Handoff: Human Owner 已最终验收 r3 §7.4 D-01 文档
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Verification Scope: r3 §7.4 D-01

# D-01 设备状态与过程监控讨论稿独立验收

2026-11-07（Asia/Shanghai）。本轮由 fresh-context Verification 独立读取根工程契约、双语 README 和 PLAN、最近作用域的文档索引、[r3 规格](spec.md)、[Development 交接](tasks.md)、两份指南及工作树差异。依据 [r3 §7.4](spec.md#74-长期阅读指南) 记录的 Human Owner 授权验证 D01-AC01 至 D01-AC04。r3 软件方案处于 `draft`，软件验收项 AC01 至 AC07 归后续独立审批的范围。

## 候选与环境

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。本地 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。以下 SHA-256 均与交接值相符。

| 工作树相对路径 | SHA-256 |
| --- | --- |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md` | `c5b49be944d3ae40abd72ac77967b529afa6a449e0cf608a415872e486310391` |
| `plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md` | `b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f` |
| `docs/equipment-status-process-monitoring.md` | `738441be2a54cef103e714e03c6ae9ebb89e7b4debf31f393332aedba8c361b6` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `345fa0b94197ef14cb0bbc916ca3d0916f775ecb98ea008c9601162dc3d05041` |
| `docs/README.md` | `a74d088ca1802bc1906a929004cb73bc8c3a6adb19a66d4579f5b957ee17a673` |
| `docs/README.zh-CN.md` | `9bc039d9b9dc5c2261f6682485ff2facb623afee43c3d8b931ef09abf6d5c87a` |
| `docs/generic-task-workflow-discussion.md`（既有链接目标） | `b0913d0fe16627b9d7bbe1043b8b602ccee312b08915a70a68ed628fc7032fff` |
| `docs/generic-task-workflow-discussion.zh-CN.md`（既有链接目标） | `2e55a70064945d4836f4204bb7f9a7dba2151d3c76b78156aa88ca7416f39439` |

## 验收检查

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| D01-AC01 文档与链接 | 通过 | 两稿互链，并各自链接文档目录、r3 规格及 §7.4。双语索引新增行均可到达两份指南。两稿开头一致标明 D-01 讨论稿范围、软件草案状态和后续审批。42 个相对链接目标解析成功，其中 32 个有锚点。[中文稿](../../docs/equipment-status-process-monitoring.zh-CN.md) · [英文稿](../../docs/equipment-status-process-monitoring.md) · [中文索引](../../docs/README.zh-CN.md#索引) · [英文索引](../../docs/README.md#index) |
| D01-AC02 管理员配置 | 通过 | 两稿均先登记炉区 1 的 `furnaceZone1Actual` 和 `furnaceZone1Set`，再配置四页共用的卡片和温度历史曲线组。卡片支持设置双语标题、启用、排序、唯一的有序指标及逐项开关，每卡最多 10 个启用指标。曲线组对同一对 °C 指标配置有序、可独立启用的两条序列，按原采集时间查询已存样本，缺样时留空。[中文卡片](../../docs/equipment-status-process-monitoring.zh-CN.md#latest-cards) · [中文曲线](../../docs/equipment-status-process-monitoring.zh-CN.md#history-curves) · [英文卡片](../../docs/equipment-status-process-monitoring.md#latest-cards) · [英文曲线](../../docs/equipment-status-process-monitoring.md#history-curves) |
| D01-AC03 上报与留存 | 通过 | 两稿用稳定指标键表示同一次来源采样中的独立标量。实时按设备和采样组整份替换并防旧包覆盖，历史按产线和组独立选样、追加并永久保留。历史白名单和采样间隔归采样策略，曲线启用、隐藏及编辑只影响展示。两路各有投递身份与持久回执，历史重试由回执去重。[中文数据流](../../docs/equipment-status-process-monitoring.zh-CN.md#data-flow) · [英文数据流](../../docs/equipment-status-process-monitoring.md#data-flow) |
| D01-AC04 权威边界 | 通过 | 两稿将管理与查询路径、字段及 JSON 示例交给 r3 §4、§4.1、§4.2 和 §5，正文保留概念及两项指标键示例。逐字节复核确认 D-01 候选为两份新指南、两条索引新增行和 Development 记录。本 checklist 的结论限于 D-01。[配置接口与示例](spec.md#4-前端查询和管理接口) · [SMA 接口与示例](spec.md#5-sma-指标发现和写入接口) · [Development 交接](tasks.md#developer-handoff) |

## 命令与结果

| 命令或方法 | 结果 |
| --- | --- |
| `git symbolic-ref --short HEAD`、`git rev-parse HEAD`、`shasum -a 256`（上表八项） | 均退出 0，分支、HEAD 和八项摘要与交接一致。 |
| 独立 `python3` 内联检查相对路径、Unicode 标题锚点和显式 `id` | 退出 0。每稿 19 个链接、5 个阅读入口，新增索引行各 2 个链接。两稿引用相同的 11 个规格目标，并各自解析对应语言通用任务讨论稿的 `field-config-alignment`。 |
| 独立 `python3` 解析 r3 的 JSON 围栏并比较 Mermaid 源码的边 | 退出 0。r3 的 6 个 JSON 示例均可解析，炉区指标键贯穿卡片、响应、曲线和两路上报。实时示例额外携带布尔就绪值，两路原采集时间一致、事件身份不同。两稿的 Mermaid 各有 6 条边，均将事实经 SMA 分流至快照和历史。 |
| `git diff -- docs/README.md docs/README.zh-CN.md` 和独立 `python3` 字节比较 | 均退出 0。每份索引删除 D-01 单行后，所得 SHA-256 与 Development 编辑前摘要一致。再移除对应既有通用讨论稿索引行后，与 `git show HEAD:<path>` 的字节完全一致。两个通用讨论稿文件的摘要与交接值一致。 |
| `git diff --cached --quiet`、`git diff --check -- docs/README.md docs/README.zh-CN.md` | 均退出 0。暂存区无变更，索引差异无空白错误。 |
| `git diff --no-index --check -- /dev/null "$guide"`（两稿各一次） | 均退出 1，表示与空文件存在差异，输出均为空。两稿各 73 行。 |
| `sed -n '42,89p' plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/tasks.md \| bash` | 退出 0，交接所附 DEV 静态检查重跑得到 42 个解析成功的链接。独立检查结果见本表其他行。 |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh .`（写入本记录前） | 退出 1。对本 bundle，检查器要求整份 `spec.md` 为 `owner_approved`，并要求根双语任务目录列出已存在的 `tasks.md`、以固定词标记当时尚未创建的 `checklist.md`。§7.4 是局部批准，根任务目录记录的是 r3 软件草案。D-01 以 §7.4 的授权和验收项判定。 |

## 原独立 QA 结论与交接

**D-01 `qa_passed`，D01-AC01 至 D01-AC04 全部通过。** 当前无 D-01 阻塞或返工项，交 Human Owner 对该文档切片作最终验收，当前为待验收。

链接结论以当前交付工作树为准，两份通用任务讨论稿仍是既有未跟踪链接依赖。交接记录的临时快照目录经检查已不存在，复核依据为工作树文件、摘要及本记录。

`command -v mmdc` 退出 1，Mermaid 复核限于源码，图形渲染未实测。软件构建、运行测试、数据库与现场验证归各自后续审批范围。

## Human Owner 最终验收

2026-11-07（Asia/Shanghai），Human Owner 在会话中确认。

> 这份讨论稿可以验收了。接下来按 r3 把首版实施拆一下吧，前端、后端和 SMA 分别要做什么，先做哪块、怎么验收？先定实施顺序，不改代码。

**ARCH-OBS-001 r3 §7.4 D-01 为 `owner_accepted`。** 验收对象是 `main` 工作树（HEAD `bcafa89fa31bdf62329bced89baebc193323a739`）中本记录「候选与环境」所列的双语讨论稿和对应的两条索引新增行。登记前用 `python3` 核对 `spec.md`、`tasks.md`、双语讨论稿及双语文档索引的六项 SHA-256，均与原 QA 记录一致，退出 0。原 `qa_passed` 记录的 SHA-256 为 `2e46fef791708a465a529322c64d5fbdf9194bfca2a205982d2f53c30a20a92f`，原 QA 结论与证据保留。

两份既有通用任务讨论稿在原 QA 后内容摘要已变化，`rg` 核对两份目标均保有 `field-config-alignment` 锚点。它们是 D-01 的外部文档链接依赖，表中摘要仍对应原 QA 时点。本次为终验登记及候选身份核对。

后续请求为只读梳理首版实施顺序。r3 软件方案仍处于 `draft`，实施和现场采用各按对应范围审批。

## D-02 Verification

2026-11-07（Asia/Shanghai）。独立 fresh-context Verification 按 [r3 §7.4 D-02 授权](spec.md#r3-d-02-单位规则补充)和 [D-02 Development 交接](tasks.md#d-02-developer-handoff)复核单位规则补充。文件顶部状态与前 8,597 字节的记录归 D-01 原候选，保留其 `owner_accepted`。r3 软件方案为 `draft`。

### D-02 候选

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。环境为 macOS 15.7.7（arm64）、Apple Git 2.50.1、Python 3.9.6。

| 文件 | SHA-256 |
| --- | --- |
| `spec.md` | `55c168a7120af682e98af4246fb0d8c192492d8d7830d7dddc14be379fe3d3a3` |
| `tasks.md` | `23ce97cc466c0be4ccf0ad2d66f310b3ee194ff13c8285f3c97a58bd649f714e` |
| `docs/equipment-status-process-monitoring.md` | `939db98596e85464552c8250d0322e659af923216becba83063d3a1e9c4400e3` |
| `docs/equipment-status-process-monitoring.zh-CN.md` | `9c032abe5be2f04acf6b05d2c9404eae425841938a01ac07379f3da7b639d22e` |

### D-02 验收

| 验收项 | 结果 | 独立证据 |
| --- | --- | --- |
| D02-AC01 | 通过 | 规格 §3、§4.1 和两稿 §1–2 一致。中英文名称独立保存，共用可留空的 `unit`。指标项标题组合为「实际温度（°C）」或「Actual temperature (°C)」，留空或省略单位时仅显示名称。值区只显示格式化值，两稿均以 `810.2` 为例。 |
| D02-AC02 | 通过 | 规格 §4.2 和两稿 §3 都按同一物理量和单位组织曲线组。同单位序列共用纵轴时标注一次单位，留空或省略单位时纵轴省去单位标注。 |
| D02-AC03 | 通过 | 规格 §5 和两稿 §4 一致。SMA 按 `metricKey` 上报原类型的 JSON 标量，实时快照和历史追加使用同一登记业务单位。两条拟定 POST 路径保持原样，响应示例分别保留 `label` 和 `unit`。六段 JSON 逐字节匹配编辑前摘要，两路温度均为 JSON 数字，实时就绪值为布尔值。 |
| D02-AC04 | 通过 | 两稿仍以规格 §4、§4.1、§4.2、§5 为接口和示例入口。两稿各 19 个链接，双语索引行各 2 个链接，共 42 个本地目标解析成功，含 32 个带锚点链接。逆向比对还原三个 D-01 正文摘要，双语索引仍匹配原候选摘要。D-02 正文差异限于单位说明及对应验收，角色记录为追加。 |

### D-02 命令与结果

- `git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256` 均退出 0，分支、HEAD 和四项候选摘要匹配。`git diff --cached --quiet` 退出 0。
- `git apply --reverse --check <D-02 对照 diff>` 退出 0。独立 `python3` 在内存中按 hunk 逆向还原双语正文各 4 段及规格 6 段，三个摘要均匹配 D-01 候选表，退出 0。D-01 的规格授权区（去尾部空白）、Development 前 7,255 字节及原 checklist 前 8,597 字节的 SHA-256 分别为 `2f62127c7744fc4fa19490d16789f43a8d8663bda121e0c9e6a27325aadec78b`、`b694674ef4a3a28df1c3b0ce491dc5631b5efe007dbcfe6321cdf46e777d1d2f`、`6cec7377c6b8956c7896cf8e6958a75578be4107b7ee9245f982ec04167a9663`，匹配对应历史基线。
- 独立 `python3` 使用 `hashlib.sha256`、`json.loads` 核对六段围栏的原字节及标量类型，用 `pathlib` 核对本地路径、显式锚点和 Unicode 标题锚点，退出 0。两稿各自的 `field-config-alignment` 依赖在当前工作树可解析。
- `git diff --check -- PLAN.md PLAN.zh-CN.md docs/README.md docs/README.zh-CN.md plans/README.md plans/README.zh-CN.md` 退出 0。四份未跟踪候选分别运行 `git diff --no-index --check -- /dev/null <文件>`，均退出 1，输出为空，差异来自文件存在。
- `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh .` 退出 1。对本 bundle，检查器要求整份规格为 `owner_approved`，且目录链接须精确使用无锚点 `checklist.md`。实际局部批准和 D-01 验收由 §7.4 与 checklist 记录，双语目录的 D-01 锚点有效。本次以 D-02 局部批准和实测链接判定。

### D-02 结论与交接

**D-02 `qa_passed`。** D02-AC01 至 D02-AC04 全部通过，无阻塞或返工项。交 Human Owner 对本节所列候选的 D-02 文档补充作最终验收，当前待验收。

验证限于本地 Markdown、JSON 和工作树。`command -v mmdc` 退出 1，原 Mermaid 源码经差异核验，图形渲染留在文档检查范围之外。软件构建、运行、数据库与现场验证归各自后续审批。两份通用任务讨论稿及 DAA 同期工作属于独立变更。必要复核证据为工作树候选、本节摘要和保留的 D-01 记录，验证无须保留临时产物。
<!-- ARCH-OBS-001-r6-checklist-history-end -->
<!-- ARCH-OBS-001-r7-qa1-checklist-history-end -->
<!-- ARCH-OBS-001-r7-qa2-checklist-history-end -->

## 2026-11-17：r11 QA2 后的 R10 进程内补证

按 Human Owner 已批准的 r10 §12.9 及 r11 对原 R10 条件的保留，由同一独立 Verification 对实际交付源码补做下列限定验证。本节是额外证据，不改写上方 r11 §13 `qa_passed`、r10 QA4 当时的 `qa_blocked`、任何更早 verdict 或 Human Owner 最终验收状态；它不自动把整个 R10-AC01–11 判为通过。未发现需要返 Development 的新实现 failure。

本轮执行限定为本机进程内合成数据、实际源码函数、假会话和实际 Vue SFC／ECharts SVG SSR；**未连接或创建外部数据库，未执行数据库 DDL，未运行 Docker，未连接或修改 3307/dev、现有服务、真实 `.env` 或持久 profile，未改源码、测试、配置、spec 或 tasks。** Python 使用项目 `.venv/bin/python` 3.13.3、`env -i`、`-B`、`PYTHONDONTWRITEBYTECODE=1` 和 `PYTHONPYCACHEPREFIX=/dev/null`；进程审计禁止网络连接、监听、地址解析和 INET socket，异步事件循环仅允许自身 AF_UNIX socketpair。需要 ORM 模型时以进程内虚拟 `database.Base` 替代真实 engine，需要设置路径时用不存在路径的进程内 `settings` 替身。Node 使用项目依赖、v22.19.0 和空环境变量启动；调用的 API 均为进程内合成函数，没有浏览器或 HTTP 监听。**Fake session 提供的排序、分页、提交和行是测试替身，不等同实际 MySQL 查询、事务、CHECK 或锁。**

### 实际执行结果

| 范围 | 输入、实际断言与退出结果 |
| --- | --- |
| R10-AC06 统计纯函数 | 用实际 `observed_time` 和 `summarize`：`2026-11-16T16:00:00Z` 转为上海 `2026-11-17 00:00`；次日同刻为区间末，乱序输入累计 1000→1006 得 6，1000→1000 为合法 0。空样本为 `boundary_missing`、空值和 `unknown` 质量为 `bad_or_missing_sample`，均 `amount=None`；未确认连续性为 `continuity_unknown`，读数下降为 `counter_decreased`。跨上海午夜 23:30→00:30 的真实增量完整区间为 2，对单日 00:00→01:00 查询拒绝猜分摊并返回 `cross_boundary`；该完整区间的合法 0 仍为 0。进程退出 0，属于纯函数／时间输入证据，不证明现场换表识别或数据库查询。 |
| R10-AC04／06 能耗读取 | 实际 `energy_reads.summary`／`sample_data` 使用假会话：表计 A/B 相同 `reading` 键分别对应槽 01／02，旧值各为 1000／100；A 已确认连续性汇总 6，B 未确认连续性返回 `continuity_unknown` 且无用量。检查实际 SQL 对 meter/group 的过滤表达式，假会话按目标供应行。退出 0；不证明真实数据库执行过滤，也不证明跨连接锁。 |
| R10-AC04 槽和锁定 | 实际 Pydantic `EnergyMetric` 接受槽 100、拒绝 0／101；`EnergyMetricPatch` 接受 100、拒绝 101。实际 `save_energy_metric` 在假会话和 `first_used_at` 已有值时，对 slot、measurement mode、unit、quantity key 的不同新值均返回 409 `metric_in_use`，对象不变且无 fake commit；未使用项允许修改单位。检查服务发出的语句带 `FOR UPDATE`。退出 0；仅为应用校验和假会话证据，不冒充 MySQL 约束执行、锁竞争或持久历史读取。 |
| R10-AC05 读函数 | 实际 `task_candidates`／`latest_cards` 配合假会话及假目标时钟：同设备同刻 TASK-A／TASK-B 的查询要求按 `observed_at DESC, task_no ASC`，合成有序结果显示 `tied=true` 且默认 TASK-A；A 缺值不借用 B 的 99，手选 B 显示 99，另一设备默认 TASK-D 值 44，不存在的手选返回 404。退出 0；假会话自行提供过滤及排序结果，不能证明 MySQL 实际排序或 collation。 |
| R10-AC05 页面生命周期 | 编译并执行实际 `cards.vue` setup：同刻默认 TASK-A 显示 tied；手选 TASK-B 后新最近 TASK-C 到达，手选仍为 B；清除手选恢复 C。手选 B 不再可用时显示 unavailable、清空数据且不静默回退；切设备后清手选并显示该设备 TASK-D；销毁再创建组件默认跟随 TASK-C，定时器数量归零。退出 0；API 为合成函数，无浏览器或网络。 |
| R10-AC07 配置 | 实际 `validate_items` 在假会话下接受 10 启用项及 10 启用＋1 停用项、拒绝 11 启用项；同单位温度序列可通过，`°C`／`K` 混合拒绝 `curve_units`。另对实际 `save_group`／`create_metric`／`create_binding`／`save_display` 使用进程内对象存储：创建两区域，改双语名、停用、设置排序并重启；创建两指标、同指标 latest/history 槽 1／7 及双指标卡，9 次 fake commit 被调用。退出 0；这不证明真实持久化、角色鉴权、HTTP 或浏览器管理。 |
| R10-AC11 三类读函数与分页 | 实际 `reads.curves` 使用假会话对温度／传动／清洗分别读取：T2（ID 1）先到、T1（ID 2）迟到且 T1 的 `updated_at` 更晚时，三类均返回 ID `2→1`；另一组合 T0／缺测 T1／同刻 T2 两事件返回 ID `3,4,1,5` 和 `present=true,false,true,true`。实际 `samples` 请求两页，假会话按所请求的 `observed_at DESC,id DESC` 返回 `[5,1]`／`[4,3]`，无重复遗漏。退出 0；SQL 排序表达式已检查，但 fake session 执行排序／分页，不能报告为真实 MySQL 分页证明。 |
| R10-AC11 实际图表 | 对温度 `°C`、传动 `Hz`、清洗 `bar`，分别编译实际 `CurveChart.vue`，使用项目 ECharts SVG SSR：有序 T1／T2 读数 11／12 顺序显示，缺测形成 `null` 断点，同刻两事件 12／13 分别保留在同一 X 坐标，`connectNulls=false`，Y 轴单位对应。退出 0；输入为合成且已排序，不证明浏览器、网络或数据库。测试驱动重复释放图表导致三条 ECharts `Instance ... has been disposed` 提示；它们来自本次辅助驱动，非业务错误。 |
| R10-AC11 单 DB 摘要 | 实际 PLC facts v2 parser、`insert_sample` 和 `summary` 使用合成完整单 DB 样本与 fake capture：good 点为 `12:00:01.100000+08:00`，较晚 bad 点为 `12:00:02.200000+08:00`；生成的摘要 `sampledAt` 为后者、点数 2。退出 0；没有真实 DAA／PLC、数据库或跨 DB 传递证明。 |

### 执行身份、异常与剩余 gate

- 上表 Python 分别通过 `env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/dev/null <backend/.venv/bin/python> -B -` 从 stdin 执行，退出 0；前端分别通过 `env -i PATH=/usr/bin:/bin TZ=Asia/Shanghai <node-v22.19.0> --input-type=module -` 从 stdin 执行实际 cards 与 CurveChart 源码，退出 0。相关输入和断言已如上持久化；本角色没有创建临时脚本、凭据或需协调者回收的新资源。
- AC04／07 辅助驱动的首次尝试已执行同步 schema 断言，但在异步服务断言前退出 1：审计钩子误把 asyncio 自身 AF_UNIX socketpair 当作外部网络禁止，事件循环未启动。将禁止范围精确改为外部连接／监听／DNS／INET 后重新运行，业务断言退出 0；这是测试驱动初始化问题，非实现 failure，也没有数据库副作用。
- 首次追加后历史字节审计将本节新增的空行误算进旧文件前缀，断言退出 1；按实际字节边界重算旧前缀为 193,434 字节，SHA-256 与下方写入前摘要一致。该错误只在内存中比较，没有修改历史记录。
- 规格 SHA-256 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`，tasks SHA-256 `ca0e06030c2507fdea23e8e141752736d9ba866639d06d6c4b31bf3c8b1b5ffe`；上方 r11 正式 65 项中的受测 OBS 源码／组件摘要与交接一致。单 DB 摘要调用的 [PLC facts CRUD](../../backend/app/plc_facts/crud/async_v2.py) 是工作树并行改动，不归入本任务 65 项；本次实际读取 SHA-256 `5656ced4b98a154e7e16c1c0ece4a5e23fedd6ea53a70a9425157b0994ee4017`。其余直接参与该探针的 `services/async_v2.py`、`v2_domain.py`、`schemas/v2.py` 摘要分别为 `ea0c6aa1489fb627ed106fac6960325a26bb883e100fca14fcd5703b25f307da`、`cd1d769220121a8d224fc744c728586c52a3582ef44e982d785ffa7bfc8c9ed4`、`bacb325276206eae193b0c34f0c68af15fb2818d48616c272cafe6a62d380f17`；该证据仅针对当时源码和 fake capture，不将并行文件归入本任务。
- **仍未完成的明确证据边界：** AC08 的真实浏览器配合真实接口验证其余已配置空图／单位、无点、失败重试及数据到达恢复，原动态导入故障的根因亦未凭本轮定位；AC09 当前 r10 下旧入口与新统计并存的真实接口数据对照未做。AC04 的 MySQL 实际 CHECK／跨连接锁与持久槽解码、AC05／AC11 的真实数据库排序／同刻分页，以及 AC07 的真实持久配置和浏览器管理操作均不能由 fake session 自动证明；是否需要哪些实库子项应按明确验收文字和既有独立证据判定，不无条件要求穷举所有并发或权限组合。要补上述真实接口／浏览器或 MySQL 证据，须先核对当时已有授权和可用目标；r11 一次性容器已回收，本节不提出或取得新授权。
- 本轮证据交协调者和 Human Owner；**r11 §13 仍为 scoped `qa_passed`，不能据此宣称整个 r10 已通过或 Human Owner 已最终验收。** 原 r10 QA4 的历史 `qa_blocked` 和此前记录完整保留；真实 SMA／DAA／PLC、跨 DB 联调、现场、生产与发布继续各按独立范围处理。

本节写入前完整 checklist SHA-256 `b41fd0f735e46e50cd8a1b5d88472eeac6d4ca4026aae64dcc2807b5943f6190`，其原始字节全部保留在本节之前。


## 2026-11-17：r11 QA2 后的 R10 回环 HTTP／浏览器补证

本节由同一独立 Verification 在 r10 已批准范围继续补证。协调者转达 PM 对 §12.8／§12.9 与 §13.2 的适用核实：r10 的定向 `no_db`／浏览器验证涵盖仅存在于测试进程的 SQLite 内存夹具及其建表，r11 不取消 r10 既有批准。当前操作限任务独有内存夹具、合成用户及数据、独立回环 FastAPI／Vite 和浏览器；这是既有批准适用性的澄清，不改 spec 或旧 verdict。上节列出的旧／新接口并存及部分 AC08 缺口以本节实际结果更新；完整 r10 verdict 待后续针对剩余明确条件逐项判断。r11 §13 `qa_passed`、r10 QA4 历史 `qa_blocked` 和全部历史字节保持原样。

### 环境与替身

- 先逐项核对 handoff 65 文件 **65/65 一致**，清单整体 SHA-256 `b3d52719cb1c99c329ac015e1bb5886efb3b86837481989b4d886b80d9dd194f`；spec `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`、tasks `ca0e06030c2507fdea23e8e141752736d9ba866639d06d6c4b31bf3c8b1b5ffe`。后端 `app`、前端 `src` 副本分别与交付树递归比较相同，`main.py`、`settings.py` 和 `vite.config.js` 字节相同。副本未复制真实 `.env`、运行 profile、数据库或源码树的编译缓存；复制的并行源码不因此归本任务。
- 后端以项目 `.venv` Python 3.13.3、`env -i` 运行副本的正式 `main:app`，进程审计钩子禁止全部出站 `socket.connect` 与非 `:memory:` 的 SQLite 连接。同步 SQLite 内存连接经实际 SQLAlchemy 会话及异步适配器执行查询，`PRAGMA database_list` 的主库文件名为空；测试专用身份、profile、机器认证、`get_db` 和 MySQL 目标守卫按进程替换。故这是**实际 HTTP 路由／业务逻辑＋SQLite 内存表**，不证明真实认证、MySQL 守卫、MySQL CHECK／锁或持久数据库。模拟时钟固定为上海 2026-11-17 12:30。空环境中的 MySQL 主机／端口仅为不可用占位，审计钩子阻断连接。
- 专用 Vite 以项目 Node 22.19.0 和现有依赖运行源码副本，测试 wrapper 仅指定本任务端口、代理和缓存目录；`strictPort` 下监听 `127.0.0.1:5173`，代理到任务 API `127.0.0.1:52632`。Playwright CLI 驱动独立、非用户 profile 的 headless Chrome，仅允许本轮 Vite origin 并限制 DNS／后台网络。浏览器本地 token 和管理员角色为测试合成状态，不代表真实登录。图表结果来自真实浏览器页面的 HTTP 响应和实际 ECharts `getOption()`，不是截图或 DOM 单独冒充接口链。

### 实际补证

| 项 | 命令／操作和独立观察 |
| --- | --- |
| AC08 四类空图 | 浏览器按真实菜单／直达操作，经 `history-curves` 实际 HTTP 200 获取温度、传动、清洗的已配置空系列；实际 ECharts 各有 `time` X 轴、`value` Y 轴，单位分别为 `°C`、`rpm`、`pH`，序列均空且页面显示“暂无数据”。能耗页面的 `samples`／`summary` 均 200、返回空行及 `amount=null`、`latest=null`／`boundary_missing`；实际图的两轴同上、单位 `kWh`、空序列，页面显示缺边界和“暂无数据”。辅助脚本 `range.js`、`empty_categories.js`、`empty_energy.js` 均退出 0；本轮没有记录各图 X 轴 min／max，不能声称精确范围边界已由图表实测。 |
| AC08 缺测、失败与到达 | 经实际 `/integration/monitor/history-samples` POST 合成一区 123 后，浏览器查询返回一区 `present=true,value=123`、二区 `present=false,value=null`；ECharts 分别为 123 和 null。用真实区域标签控件只保留二区后，图保留 `°C`、该系列为 null、页面“暂无数据”，没有借一区值。对过程曲线及能耗样本各由测试中间件注入**一次真实 HTTP 503**：浏览器显示“读取失败，请重试”，点击重试后各实际请求 200、提示消失并恢复结果。随后通过能耗 POST 写入 1020／1026，浏览器样本及汇总均 200、显示最新 1026／用量 6 kWh，ECharts 有对应两个点；通过过程 POST 写入合成传动 72 rpm 和清洗 7.2 pH，两个页面实际 HTTP 与 ECharts 各有该点。503 是任务辅助中间件注入，非真实服务故障。控制台 4 条 error 均对应两次注入 503 的资源错误及 Axios 错误。 |
| AC09 旧／新统计 | `verify_api.py` 退出 0。经回环 HTTP 调实际旧 `/monitor/energy` 和新 `/energy/consumption/summary`：旧能耗合成行电量 12、缺失氮气按旧既有合同显示 0，旧曲线值 99；新表空区间 `amount/latest=null`。实际新能耗 POST 1000／1006 后，新统计 `amount=6, latest=1006`，旧完整响应前后相同，内存表计数旧 1、新 2，例中未混算。该证据为内存 SQLite 下的实际旧／新路由，不证明 MySQL 中执行旧接口、实际切换或生产数据。上方 r11 的真实隔离 MySQL 在线迁移／逐行对账／受控恢复是不同试验，不能把两者合并冒称同一次 MySQL 端到端。 |
| AC04／05／07／11 额外 HTTP | `verify_more.py` 退出 0：实际 latest POST 后，同刻任务 `000010`／`000020` 返回 `tied=true`、按任务号排序，较旧包返回 `stale`；4 条历史按采样时间降序分页为 ID `1,3`／`2,4`，同刻两事件无重复遗漏。管理员合成区域真实 API 完成创建、改名、停用、排序、启用；能耗配置槽 100 返回 200、101 返回 422，已使用项的槽／单位／模式／物理量四种变更分别 409。数据库均为 SQLite、身份／守卫为替身；SQLite 的 `FOR UPDATE` 不证明 MySQL 真实行锁或并发竞争。 |

### 异常、资源和交接

- 首次进程在正式应用与合成内存库初始化后，绑定回环临时端口被沙箱拒绝 `PermissionError: [Errno 1] Operation not permitted`，进程退出 1、该次内存库随之销毁；明确获准提升后才启动本轮服务。温度到达辅助脚本首次因“线”同时匹配页面及下拉节点而被 Playwright 严格定位拒绝，限定主区域后实际查询通过；均为测试环境／定位问题，非实现 failure。
- Chrome 临时 profile **曾在本任务私有目录落地自身内部 `History`、`Cookies`、`Web Data`、`Login Data` 及两个 `.db` 文件**；它们不是业务库，但不能把本轮描述为从未产生任何磁盘数据库文件。专属会话关闭后，精确 profile `/private/tmp/arch-obs-r11-browser.8qPfEZ6U/playwright_chromiumdev_profile-UkRAts` 已不存在，按常见 DB 文件名查任务目录无残留；不宣称对所有可能格式做了取证。Vite PID 12935 和 API PID 12909 只在命令行、端口归属核对后分别 SIGTERM，Vite 退出 0、API 退出 **143**，不是优雅退出；Python `resource_tracker` 提示 24 个 semaphore objects 待清理，其实际清理结果未独立证明。只读 `ps` 检查两进程及 Playwright PID 12990 不存在，`lsof` 检查 5173／52632 无监听，按任务目录路径搜索无匹配进程；进程结束后 SQLite 内存库随之销毁。未操作其他浏览器、现有服务、3307/dev、Docker、真实配置或设备。
- 本任务私有目录 `/private/tmp/arch-obs-r11-browser.8qPfEZ6U` 归 `jason`、模式 0700；内含源码副本、测试辅助脚本、日志和 Vite 缓存，`frontend/node_modules` 只是指向工作树既有依赖的符号链接。关键结果已写本节；由协调者确认目录身份、无进程／后续证据依赖后**仅回收该目录本身，不能跟随链接删除项目依赖**。本角色已结束对以上服务及浏览器的使用，后续若补验须重新建立并记录资源。真实 SMA／DAA／PLC、现场、生产与发布仍不属于本合成验收。

本节写入前完整 checklist 为 202,980 字节、SHA-256 `1e0dfedbce8cb75084d1f85c5a3da018fb3973011e56588c9fa906cac0acc5b7`，其原始字节完整保留在本节之前。


## 2026-11-17：R10 补证续轮与当前合成范围 verdict

在上节证据持久化后，按协调者的同一已批准内存边界重建独立进程，补 §12.8／AC08 与 AC11。正式源码、spec、tasks、用户配置和任何持久业务数据库未改；本角色只追加 checklist 和本任务临时辅助文件。此前旧字节、r11 scoped `qa_passed`、r10 QA4 历史 `qa_blocked` 均不倒写。

### 本续轮的实际证据

- **AC08 无配置。** `unconfigured.js` 退出 0：有合成设备 `line`、指定时间范围时，真实回环 `history-curves` 返回 200 和空 `groups`，浏览器显示“尚未配置启用的曲线，请联系管理员”，通用 X／Y 轴实际 border 均为 1px。有合成表计 `meter1`、无指标配置时，真实 `definitions` 返回 200／空数组，浏览器显示“尚未配置表计指标，请联系管理员”及同样的通用 X／Y 轴。这是实际 Chrome／Vite／FastAPI 和 SQLite 内存数据，用户、profile、目标守卫为测试替身。
- **AC11 T2、迟到 T1 与备注。** `timing.py` 退出 0：通过正式 POST 先写 08:20 的 T2（ID 1），后补 08:10 的 T1（ID 2），实际 PATCH T1 备注；T2 `updatedAt=08:30:00`，T1 `updatedAt=11:57:38`，三类真实 HTTP 曲线均按 T1(ID 2)→T2(ID 1) 返回，而非按 ID 或更新时间。再写 08:15 的空整包（ID 3）及 08:20 第二真实事件（ID 4），温度值为 `121,null,122,123`，传动为 `71,null,72,73`，清洗为 `7.1,null,7.2,7.3`；三类均按 ID `2,3,1,4` 返回，空样本 `present=false`，两个 T2 时刻相同而 ID 不同。此处测试时钟固定为 08:30；SQLite 的 `CURRENT_TIMESTAMP` 是 UTC，本次只利用它与合成写入时间比较先后，**不据此证明 SQLite／MySQL 的上海时间生成或持久化语义**。
- **真实浏览器图表与精确范围。** `axes_and_series.js` 最终退出 0：对三类过程图和能耗空图均选择上海 `10:00–11:00`，实际 ECharts X 轴 `min=7200000,max=10800000` 毫秒（相对组件采用的 UTC 当日原点），Y 单位依次 `°C`、`rpm`、`pH`、`kWh`；空样本接口实际 200。三类另选择 `08:00–09:00`，实际轴 `min=0,max=3600000`，经真实 HTTP 返回上述按 observedAt 的点，实际 ECharts 将缺测画为 null、`connectNulls=false`，两个同刻真实值位于同一 X 坐标的独立点。与上节相比，本续轮补到了实际图表时间轴数值；不是仅检查静态 DOM。
- **辅助脚本异常。** 第一次轴测试在从 `08–09` 改到 `10–11` 时先改起点，暂时出现起点晚于旧终点，控件保留旧起点；脚本又可能抓到切类别的自动旧请求，观察到的实际范围为 `08–11`，断言停止。限定合法的中间输入顺序并对准确 `from/to` 匹配响应后重验。中间一次辅助谓词使用 `URL`，因 Playwright CLI 的回调沙箱无该全局而报 `ReferenceError`；改为匹配实际编码后的请求字符串，再得到上段结果。两项均是辅助驱动问题，未作为产品失败或伪称首次通过。

### 对当前 R10-AC01–11 合成验收的综合核对

| 项 | 已有独立证据和仍须保持的解释 |
| --- | --- |
| AC01 | QA1／QA3／QA4 对三类**合成**来源、发现／两路写入、未知组／类型、撤权及覆盖授权有真实 MySQL／HTTP 或实际路由证据；不将模拟身份当真实 SMA 产品。 |
| AC02 | 先前独立真实 MySQL／HTTP 和 `no_db` 定向测试覆盖整包替换、0／false／空字符串、缺测、stale、冲突、空包、历史过滤及 no-history；本续轮的空整包形成真实 SQLite 历史缺测点。 |
| AC03 | QA 既有新请求重试／冲突和两路证据，与 r11 **真实隔离 MySQL** 上五份旧原请求重放、旧／新 ID 重叠及计数不增长共同保留；这些顺序执行不证明同时竞争下只写一次。 |
| AC04 | r11 对实际 MySQL 迁移后 DDL、索引和旧配置／值逐行对账；本次实际 SQLite HTTP 和此前应用层检查补槽 100／101 及已使用字段 409。SQLite 的约束和 `FOR UPDATE` 不等同 MySQL CHECK 或跨连接锁；下方特定并发事务条件仍未证。 |
| AC05 | 先前实际 SFC／合成 API 验证手选、跟随、切设备、重载及不借值；本次 SQLite／实际 HTTP 补同刻任务排序与迟到 stale。不是多设备真实 MySQL 浏览器全链。 |
| AC06 | QA1／QA4 真实 MySQL HTTP 的累计 6、增量 5、瞬时量与此前纯函数跨上海日、0／缺测／质量／下降／不猜分摊共同保留；同事件并发防重复及配置与写入的特定竞争见下。现场换表确认仍在实际表计启用时按项目规则处理，不纳入本合成 gate。 |
| AC07 | QA4 的真实合成 operator 登录／范围和菜单、浏览器区域切换、实际 SFC 10／11 项与异单位检查，加本次 SQLite／HTTP 管理区域启停排序；当前测试的 admin 是依赖替身，不把它当真实认证。未穷举所有身份矩阵或浏览器管理组合，不因此自行制造额外无限 gate。 |
| AC08 | 本节及上节补了无配置、四类已配置空轴／单位与实际范围、所选区域无点、过程／能耗 503 重试和四类合成数据到达；QA4 另有真实浏览器从四个菜单及直接路由进入正式服务的历史证据。原故障的缺失 Vite 优化依赖与浏览器 hash／磁盘 hash 不一致见 Development 的历史定位记录；QA4 观察到恢复，但本角色未独立复现故障前态，也未证明触发该不一致的具体操作，不将此说成新的实现 failure 或已经独立证明全部根因。 |
| AC09 | r11 真实隔离 MySQL 完成带旧行升级、逐行／DDL／索引／价格对账、旧回执重放和受控恢复；上节另用 SQLite 上实际旧／新 HTTP 和两套合成表验证示例口径分离。该旧／新接口对照没有在同一迁移后的 MySQL 实例上执行，不把两次试验合并为一次 MySQL 端到端；旧接口空汇总按既有规则为 0，新接口缺测仍为 null。 |
| AC10 | 65 项身份、两份 r11 README、既有双语键／链接及合成环境与清理边界均有各轮记录；真实产品、现场、部署和 Owner 最终验收不由 QA 推断。 |
| AC11 | 本续轮补三类真实 HTTP 的 T2→T1→备注、空包断点和同刻点，以及真实浏览器 ECharts；实际数据使用 SQLite、测试身份／目标守卫和合成时钟。此前 QA1 有 MySQL 过程时序，纯进程测试有单 DB 摘要最晚 bad 点；不将其说成真实 DAA、PLC 或跨 DB 联调。 |

### 当前 verdict、必要缺口与资源

**当前 r10 交付的合成验收 verdict：`qa_blocked`。** 不是因为真实 SMA／DAA／PLC、生产部署、无限身份矩阵或不能重现已消失的历史故障前态；这些不应被冒充本次合成验收的额外无限门槛。明确尚缺的有：

1. [§12.3](spec.md#r10-source-independent-energy) 明确要求**首次能耗写入与语义配置变更并发时，绑定、first-used 标记和样本在事务中一致**。现有独立证据为顺序写入后的 409、fake session、SQLite 和真实 MySQL 的单连接事务；未见该特定双连接竞争的独立实测，不能以 SQLite 假锁替代。
2. [§12.6](spec.md#r10-source-independent-energy) 明确要求校验重放和并发且不重复计费。顺序重复／旧回执已证，但未见同一能耗事件的真实 MySQL 并发重放及业务行／回执／统计不重复的独立验证；这是有限的具体竞争条件，不是穷举所有并发组合。

最小后续证据是按当时批准与资源边界，针对上述两条条件使用合成数据、实际 MySQL 两个独立事务／连接做可复核对照，核验提交结果、首次使用语义、业务行／回执和统计数量，并按实际结果处理；同时若要声称迁移后 MySQL 上旧／新统计同实例并行，也须补其相应直接证据。r11 指定隔离容器已回收，协调者本轮明确禁止连接 dev 或创建／连接其他外部数据库，所以不能在当前委派边界自行补该 MySQL 实测。没有发现新的实现 failure；若后续实测失败，按角色交 Development，重新 handoff 后独立复验。该 `qa_blocked` 是本次综合判断，**不改写上方 r10 QA4 当时的历史结论，不改变 r11 §13 的 scoped `qa_passed`，也不是 Human Owner 最终验收。**

第二轮仅使用 `/private/tmp/arch-obs-r11-browser.8qPfEZ6U/phase2` 及同一任务源码副本：API `127.0.0.1:54706` PID 13640、Vite `127.0.0.1:5173` PID 13647、Playwright 会话 PID 13653。浏览器关闭后其专属 profile 仍存在；本 Verification 按协调者明确指示，在核实 owner `jason`、模式 0700、无进程命令行及 `lsof` 占用后，**由本角色**精确删除 `/private/tmp/arch-obs-r11-browser.8qPfEZ6U/phase2/playwright_chromiumdev_profile-0GibKx`，并验证路径不存在；该动作并非协调者亲自执行，角色分工不严谨的事实如实保留。Vite SIGTERM 退出 0；API SIGINT 后打印 `QA_API_STOPPED`、退出 130，内存 SQLite 随进程销毁。只读 `ps`／`lsof` 均未见上述 PID、监听端口及指向任务目录的进程；任务目录按常见 DB 文件名未见残留。第一轮 `resource_tracker` 提示的 24 项 semaphore 是否全部清理仍未独立证实。其余私有目录及源码／依赖符号链接仍保留，已结束使用，由协调者核实身份、证据无依赖后回收；不得沿符号链接删除项目 `node_modules`。

本节写入前 checklist 的 210,901 字节及 SHA-256 `4c149662e9a0255ce49aab18a51ec32464a93a7e1840816b9bdac80dede7d7d2` 完整保留在本节之前。


## 2026-11-17：r10 授权 dev 的独立并发补验（清理前）

本续轮依据 Human Owner 对 [r10 §12.10](spec.md#r10-approval) 的既有 dev 授权及 PM 对 r11 隔离续办已结束、不取消 r10 原批准的适用核实，由同一实际命名 Verification 独立执行；这是 r10 授权 dev 的新补验，不是先前 r11 独立容器。先固定清理前事实；协调者负责清理本轮精确合成数据，清理后的独立只读核验和当前 r10 最终 QA verdict 待续。原 r10 QA4 和上方综合 qa_blocked、r11 scoped qa_passed 与全部历史字节不倒写。

### 身份、隔离与预检

- 实际连接仅限 127.0.0.1:3307 / industrial_level_2_system；MySQL 8.4.6、UUID SHA-256 前缀 ac2319a3fdc8、唯一 Alembic revision 9d1f3a5c7e20、实际时差 +28800 秒。普通应用账号无全局 PROCESS，另用现有管理账号只读核验：三次快照活动 InnoDB 事务及目标 schema 活动 SQL 均 0；唯一 MySQL Daemon 是 event_scheduler，目标 schema 无启用事件。宿主 3307 客户端为项目 backend 8000 的 Python 进程和 DBX，SMA 相关进程名扫描无匹配；均为时点观察，不保证其他进程未来不写。未接管 8000／5190，未操作 Docker、真实 SMA／DAA／PLC。
- 交付候选 65/65 摘要匹配；任务源码副本的 app、common、core、database、projection 和入口逐目录／字节匹配，排除真实环境文件、profile 和数据库文件。进程以 env -i 启动，仅读取现有设置中连接所需凭据并以显式目标注入进程，禁用其他 DB 目标，审计钩子阻断非 127.0.0.1:3307 连接；不输出或写出真实凭据。任务目录为 0700，随机合成 profile、token、台账和辅助材料为 0600。调用交付源码实际 service、profile 解析／Bearer 校验和 MySQL 目标守卫，通过独立 AsyncSession；不是回环 HTTP。
- 随机 producer r10qa_p_fd00058e1e2c0c91、group r10qa_g_fd00058e1e2c0c91，四个随机 meter／metric 和五个事件精确键预先写入 ownership.json；21 个相关身份字段只读扫描无碰撞。清理前共四项配置、回执 ID 262/264/265、样本 ID 49/50/51。回执五个外键引用表中仅本轮能耗样本引用 3 条，其余实时／过程及两旧归档表均 0；其他 producer 对本轮能耗结果 ID 的逻辑引用 0。故障事件、旧形态事件和槽 101 负例均无持久行。
- 预检最初因只读进程列表含非 UTF-8 字节、以及权限解析器未还原 MySQL 授权对象中的字面转义下划线而各停止一次；容错解码及只读 SHOW GRANTS 证实应用账号对精确 schema 有所需 DML 后复核通过。两次均在 dev 业务写入之前。

### 实测结果

| 条件 | 独立结果 |
| --- | --- |
| 首次写入先持锁 | 独立 MySQL 连接 263827/263830；performance_schema.data_lock_waits 实见配置变更等待写入持有的配置行锁。释放后实际 service 写槽 01=1000 并提交回执／样本，变更单位返回 409 metric_in_use；模式 cumulative、单位 kWh 与 first-used 保持一致。样本 49／回执 262。 |
| 配置变更先持锁 | 独立连接 263841/263838 实见写入等待配置锁；先提交槽 02／interval／MWh 后，不带区间的旧形态写入 422 invalid_time_range、无回执／样本。受控在回执 flush 后注入异常，service 返回 503 not_ready 并回滚；该事件回执／样本均无、first-used 仍空。随后另一合法区间事件以槽 02=5 写入，之后改已用槽 409；样本 50／回执 264。此 503 为明确测试注入。 |
| MySQL 槽边界 | 实际 service 写入槽 100 成功；绕过 Pydantic 的槽 101 INSERT 被真实 MySQL CHECK 以错误 3819 拒绝，事务回滚、无 101 行。 |
| 同一能耗事件并发 | 辅助驱动第一次在放行前因 innodb_trx 即时快照未见两个事务而停止，两事务取消回滚、该事件无回执／样本。独立只读锁诊断证明 data_locks 立即见两锁、innodb_trx 约 150 ms 后才显示两事务；诊断回滚。确认状态后有界轮询监督继续，连接 263892/263893 同时持回执表锁、两事务可见后放行。263892 的 service 返回 stored／recordId 51，263893 抛 ObservationError(503, not_ready)；仅样本 51／回执 265 一份，实际统计 amount=5。不是 HTTP 抓包，状态和原因来自实际 service 异常及测试包装。 |
| 实际死锁及监督重试 | MySQL 最近死锁的两个线程均与本轮匹配：263893 持回执 uq_obs_receipt_event gap 锁并等待能耗配置 PRIMARY 行锁；263892 持配置行锁并等待回执索引 insert-intention gap 锁；263893 被选为牺牲者。确认事件原文指纹、唯一回执／样本和无外部引用后，仅一次监督原文重试返回原 stored／recordId 51；仅一次异正文重试返回 409 event_conflict，前后行及引用不变。原死锁和 503 保留，不说成两次并发均立即成功。公开 v2 合同允许 503 后原事件重试，并未明确要求两个同时在途请求均立即 200；在本次重试返回原回执、无重复写和用量不重复的条件下，不单凭瞬时 503 自行增加验收条件，也不掩盖该可恢复并发限制。 |

### 清理前保护表对账

测试前及清理前 count/checksum 如下；21 张均为 InnoDB。三张目标表仅增加本轮对象，其余 18 张一致。目标中不存在 metric_ingest_receipts_r8_archive，未假定其存在。

| 表 | 测试前 count / checksum | 清理前 count / checksum |
| --- | --- | --- |
| plan_main | 2 / 485881418 | 2 / 485881418 |
| performance_main | 2 / 2822084073 | 2 / 2822084073 |
| plc_facts_history | 73 / 1987086524 | 73 / 1987086524 |
| plc_facts_latest | 6 / 1581760304 | 6 / 1581760304 |
| plc_source_registry | 3 / 3609128620 | 3 / 3609128620 |
| monitor_history_energy_consumptions | 0 / 0 | 0 / 0 |
| monitor_history_process_curves | 0 / 0 | 0 / 0 |
| energy_prices | 1 / 677733245 | 1 / 677733245 |
| energy_price_hours | 3 / 1315366414 | 3 / 1315366414 |
| equipment_status_main | 0 / 0 | 0 / 0 |
| process_monitor_main | 0 / 0 | 0 / 0 |
| equipment_metric_groups | 0 / 0 | 0 / 0 |
| equipment_metric_configs | 0 / 0 | 0 / 0 |
| equipment_metric_slot_bindings | 0 / 0 | 0 / 0 |
| equipment_card_configs | 0 / 0 | 0 / 0 |
| monitor_curve_group_configs | 0 / 0 | 0 / 0 |
| energy_metric_configs | 0 / 0 | 4 / 3767580418 |
| energy_consumption_main | 0 / 0 | 3 / 33615935 |
| metric_ingest_receipts | 0 / 0 | 3 / 139784682 |
| equipment_status_r8_archive | 0 / 0 | 0 / 0 |
| process_monitor_r8_archive | 0 / 0 | 0 / 0 |

清理前脱敏引用及 21 表对账 before-cleanup.json SHA-256 0dcf593b13ddcb5ea54fc15ca0cf74123ac0cda789321bf18412f2aaa4f6e925；原并发结果与匹配死锁 replay-evidence.json SHA-256 6bf5ec3e7ae207acbf960f6fb2e104a5269748cc6683e5d3f2d130d9f83fafbd；原文重试／冲突 supervised-retry-results.json SHA-256 ac66c47e39c3480288c7e95af0c40850f70d9bf49eeddf53d64e26af1f4a433c。关键事实已持久写入本节，临时文件不作为唯一证据。

供协调者审阅的 coordinator_cleanup.py SHA-256 b3702a397853f67b8ddab4e4695a380db3b3fb72337b309703fad8144fe76764：只读 --check 已退出 0；--execute 仅供协调者重新核验后使用，事务内锁定并逐键删除本轮 3 样本、3 回执、4 配置，每次核影响行数，异常回滚且提交结果不明时停止，不重置自增。Verification 没有执行删除。清理后由 Verification 只读核对精确键归零及 21 表恢复基线，再形成当前 r10 verdict。MySQL 自增值可能前移。

本节写入前完整 checklist SHA-256 9e5679bfef423badcbcfe7acaa9b2d69e57804d400d20e41b55d407cf5635945，全部原始字节保留。


### 协调者清理后的独立复核与当前 r10 verdict

协调者报告其独立执行清理脚本 --check 和 --execute 均退出 0，并在同一事务精确删除本轮 3 样本、3 回执、4 配置；Verification 未执行删除。本角色随后仅只读连接同一精确目标执行 final_audit.py after，退出 0：四项配置、回执 262/264/265、样本 49/50/51 及全部预声明身份键均为 0；五个回执外键引用表和其他能耗结果引用均为 0，21 个相关身份字段无残留；活动 InnoDB 事务、目标活动 SQL 和锁等待均为 0。上表 21 张保护表的 count/checksum **全部恢复测试前基线**。脱敏 after-cleanup.json SHA-256 71c1ea772733ecd0f9e252dded44b8212a2158ce5ad3420cd2151ac7a4991d52；这是精确键与被检查表的结果，不声称自增序列未前移或对全部数据库对象做了穷举。

**当前 ARCH-OBS-001 r10 交付的有界合成验收 verdict：qa_passed。** 综合上方各轮独立证据，原综合 qa_blocked 所列两项具体 MySQL 并发条件现已补证：配置变更／首次写入两种顺序均观察到真实双连接锁等待，并保持样本、槽和首次使用含义一致；相同能耗事件真实并发时只形成一份回执与样本，统计不重复，受监督原文重试返回原回执，异正文为 409。回执 flush 后受控故障也验证共同回滚。该结论结合先前真实 MySQL 带旧行迁移／恢复、真实浏览器及 HTTP、SQLite 和进程内合成测试；各自证据边界见对应记录，不能把这些不同试验说成单次全链。

真实竞争中一次 service 返回 503 not_ready 的 MySQL 死锁事实完整保留：该请求遇到锁竞争，不能说已证明目标身份错误或提交结果未知。公开 v2 合同允许 503 后以相同事件重试，已批准验收没有明确保证两个同时在途请求都立即 200；本轮原文重试和去重结果符合所验证的恢复及不重复要求，因此不单凭该一次可恢复 503 判为合同失败。它仍是可观察的竞争窗口和调用方必须按合同重试的运行限制，不代表系统不会发生死锁，也不证明所有并发情况。

限制保持明确：旧／新统计同一迁移后 MySQL 实例的并行接口对照未执行，以免污染共享旧统计；现有直接接口对照使用 SQLite，r11 的旧 MySQL 表／价格保全另有独立实测。历史 Vite 故障前态未由本角色独立复现，Development 记录了缺失优化依赖及 hash 不一致，具体触发操作未证。第一轮浏览器补验的 resource_tracker 24 项信号量提示是否全部清理未独立证实。上述限制不冒充 MySQL 同实例全链、真实 SMA／DAA／PLC、现场联调、生产部署或发布证明；这些按各自范围处理。原 r10 QA4 和此前综合 qa_blocked 保留为当时证据，r11 §13 scoped qa_passed 不变；本项 QA 交 Human Owner 最终验收，不自行授予 owner_accepted。

本角色已结束对本轮 dev 目标及任务私有目录的使用；目录 /private/tmp/arch-obs-r10-concurrency.Pr8fMiuZ 内的合成 profile／token、源码副本和日志由协调者核实归属、无证据依赖后回收，本角色不执行资源回收。最终核对 65/65 候选文件与交接一致，spec SHA-256 b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff、tasks SHA-256 ca0e06030c2507fdea23e8e141752736d9ba866639d06d6c4b31bf3c8b1b5ffe 未变。本节写入前 checklist 为 228,292 字节、SHA-256 84d4a4b4b5aa96c122b0e20bcb2780ec24a3d36148516495568db322d5ff3a63，其完整原始字节保留。


### r10 并发补验临时目录收尾复核

协调者报告：在核对目录所有者、0700 权限、ownership 的 task／nonce／cleanupOwner 和 lsof 无占用后，精确回收本任务目录 /private/tmp/arch-obs-r10-concurrency.Pr8fMiuZ，含本轮合成 token／profile，未跟随符号链接。Verification 随后仅只读使用 Python os.path.lexists 核对该精确路径不存在且不是残留符号链接，退出 0；未访问数据库或重跑测试。上方 r10 有界合成 qa_passed、r11 §13 scoped qa_passed 和全部历史 verdict 不变，Human Owner 最终验收仍待决定。

本节写入前 checklist 为 231,898 字节、SHA-256 a7274934f0c7fcfb79b484fd4573411bda74fcb137f5e37ca3927d3647d0de04，其原始字节完整保留。
