Task ID: ARCH-BE-005
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: B第一轮五场景真实MySQL自检通过并清理专用栈；最终token比较已重检原始反射及正负边界；交fresh Verification第二轮，既有A与全部失败历史保留
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 批准、工作树与基线

Human Owner批准：“明白了，批准 ARCH-BE-005 r2，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
批准spec SHA256：`fa2ea5caabb61b46149b9d72630224d6eff3bda7e0b3a1fa15df126b60012586`。
工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；C0/HEAD：`363b297bffe65e020108f5504766b4fb1ec3b381`。
实际执行角色：`development`；profile为contract_only，不宣称平台ACL或强制路由。

首次实现写入前已建立专属资源 `/private/tmp/arch-be-005-r2-development/`，保存非env源码基线副本、
`baseline-files.json`（每文件SHA256）、`git-status.txt`与`c0.txt`。生成命令为
`python3 /private/tmp/arch-be-005-baseline.py`，exit 0。基线包含主协调者批准收据与owner_approved索引；
排除真实env、.git、依赖目录、构建/日志/运行数据。首次rglob记录6242文件，发现control-agent target缓存后，仅在自建证据目录按git ls-files -co --exclude-standard过滤，保留998个原始源码/文档快照；未影响仓库或实现。现有dirty及十模块192个手工复制Python文件均保留，
Git总diff不代表本任务增量；最终任务delta相对本基线生成。

# 实施计划

1. Core五字段、公共合同、StrEnum与预检 → 静态/对象冲突和合同正负例。
2. C0+窄patch生成C2，冻结14表Core；仅叠加合成E → 15/16表、Core指纹及接入矩阵。
3. F回迁既定切片、唯一价格owner、42表后继和8descriptor → 完整no_db与离线迁移检查。
4. shift规则null兼容、双语说明与索引 → 前端check/test/build及合成浏览器检查。
5. 增量审计与DEV self-check → 精确handoff到fresh-context Verification。

仅执行公开隔离源码、无DB连接/写入、无Docker、无真实API/Projection/PLC、无env修改、无提交/推送。
B测试可准备源码，不执行；A通过不等于整体QA或最终验收。

# 执行证据

初始dev_planned时尚未执行实现或项目行为验证；实际已执行结果见下方安全检查点，其中记录实际文件、命令、结果、限制与风险。

## r2历史：Core阶段阻塞（2026-10-14）

初始五字段/BusinessException/最终route hook及只读AST预检已写入；C0派生C2候选生成成功，尚未冻结/通过。
`run_python(C2, check_source + import_model_packages + create_app + configure_mappers)`在DB连接禁用guard下exit 1：
`stage=undeclared-dependency,module=system,identifier=requires:monitor,location=app/system/crud/async_projection_mapping.py:15`。
该行在C0即存在`from app.monitor.models.monitor import PlcDbBlockRawSnapshot`，system manifest无requires，
monitor manifest无exports。r2要求所有跨owner声明且私有import失败，同时C2要求monitor manifest保持C0、
Core patch仅五文件，system文件不在allowlist。已交主协调者/PM裁定，暂停C2/E及涉及扩大Core的写入，
没有添加豁免/中央默认依赖或改system。主协调者明确允许继续独立的r2 F业务/前端/离线迁移准备。
C2候选清单及log：`/private/tmp/arch-be-005-r2-development/C2/core-files.json`、`C2-first.log`。

先行纯合同/依赖/HTTP冲突单测（公开C2候选、`uv run --frozen --no-sync python`调用pytest，
`--noconftest -q -m no_db`仅三份新聚焦测试，DB connect/raw_connection均patch为拒绝）结果exit 1，
25 passed/1 failed：新增camelCase测试漏计既有SuccessResponse.timestamp；将修正测试以保留现有字段。
这不是完整A/no_db结果，也未跳过任何既有套件。日志`core-unit-first.log`。
首次误用系统Python3.9 compile命令因系统pycache路径PermissionError退出1；未导入项目/无DB，
后续项目行为检查统一使用fixture中的项目uv锁环境及tmp pycache，不用该失败作为编译证明。

## r2独立F切片准备与安全检查点

在主协调者允许的独立r2面内，已准备以下源码增量；这不是F通过或最终handoff：

- 十业务模块及auxiliary/monitor入口保持薄，防止HR disabled前提前执行API。
- `common/data_keys.py`仅旧源本批literal引用的传递闭包；`common/error_codes.py`仅15个仍有引用的legacy成员。
- 现auxiliary已验收6个价格文件迁至energy，仅替换包路径；移除energy孤立旧in/out/query schema；
  auxiliary价格文件移出，后续测试/manifest/稳定说明尚待同步，暂不声称可组合。
- auxiliary只回迁四实体、三个schema、CRUD/Service、现17方法路由切片；普通GET不自动seed规则/班次，
  规则无行走成功null，显式写动作事务移到Service，CRUD不commit，稳定本地StrEnum错误不泄漏SQL。
- monitor只回迁HistoryProcessCurve/HistoryEnergyConsumption、批准10个API/Schema/CRUD/Service文件；
  Core models/monitor.py及collector/realtime链不改。移除GET生成持久化样本；事实guard仍monitor，
  业务两GET局部独立monitor-business-read。未恢复其余12模型/HTTP ingest/运行writer。

来源命令：`python3 /private/tmp/arch-be-005-r2-development/prepare_business.py`，exit 0，仅静态AST/文件编辑。
该脚本不是项目行为验证。实际文件名单当前暂存`current-delta-files.json`；其中4个PLAN、2个catalog和
并行新增`plans/ARCH-AW-001-agent-foundation/spec.md`为其他协调者变更，不归本Development。
任务实现仍未完成manifest/version/exports、跨owner import、42表successor、前端null与双语文档，
因此没有执行F应用组合或完整no_db，A尚未通过。C2/E不通过的原因按上节保留，待PM裁定。


## r2历史：安全检查点自检与当时转交

- 项目uv公开C2候选纯新测试复跑：26 passed，exit 0；保留3条未注册no_db marker warning。
  `core-unit-corrected.log`。命令等价`uv run --frozen --no-sync python -c <DB拒绝guard + pytest.main([--noconftest,-q,-m,no_db,三份新test_module_*.py])>`；
  实际guard及公开参数由`tests/module_admission_fixtures.py:run_python/public_environment`给出。
- 项目uv环境的`compile(source_bytes, path, "exec")`遍历本任务当前61个现存触达Python源码：exit 0；
  `source-compile.log`。它仅语法编译，不是完整compileall/ASGI/F验证。
- 协调者54个protected文件SHA256全部unchanged，包含三旧migration、settings/database/auth/CA/锁文件及历史bundle。
- 当前保全清单`r2-checkpoint-delta.json`有71个本任务文件（含删除和tasks）；精确delta patch为
  `r2-checkpoint-delta.patch`。4个PLAN/2个catalog及AW001并行spec不计入本任务。

当前精确Revision仍为r2，工作树HEAD未变，无commit。本状态为`dev_blocked`，转交主协调者/PM处理
C2合同矛盾并取得必要的精确新Revision批准，不是`developer_handoff`到QA。全部实现写入已停在安全检查点。
C2候选未冻结、E尚未运行、F仍准备中，A完整no_db/迁移/权限/Projection/前端/文档未验证；B未授权未执行。
已知风险是当前中间态manifest/test旧import尚未同步，不能直接用于启动/采用。所有临时资源归本任务：
`/private/tmp/arch-be-005-r2-development/`（baseline、C2候选、脚本、uv-cache/pycache、日志、delta）及
`/private/tmp/arch-be-005-baseline.py`，保留供后续开发/独立审计；未创建分支/worktree/后台进程。


# r3恢复开发（2026-10-14）

Human Owner原话：“批准 ARCH-BE-005 r3，继续 STD 源码开发”。最新approved spec SHA256：
`6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`。
上方r2 dev_blocked/26通过/61编译为历史安全检查点，当前Revision为r3并恢复implementation_in_progress。
继续使用原998源码baseline及原r2增量；追加允许system两个文件和C2 monitor manifest窄overlay，
纯Model原定义/同class重导出分类统一使用model_requires，runtime Service/DTO/key继续requires。
B真实DB、在线迁移、Docker及真实运行边界未变。后续A结果记录于本节以后。

# r3 A Developer handoff（2026-10-14，当前结果）

本节取代上方历史中间态的当前性；r2的dev_blocked、26单测/61语法编译及71文件checkpoint仍按当时事实保留，绝非最终结果。
当前为精确r3 `developer_handoff`；HEAD仍为C0，无commit，交fresh-context Verification独立复核A。
批准spec仍为 `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`。
DEV自检A已完成；B未授权/未执行，整体QA、最终验收、运行采用均未授予。

## 实际实现及精确增量

- Core五字段/v1公开符号/有界legacy清单、同一BusinessException的稳定StrEnum窄扩、纯stdlib裸CLI与源码/对象冲突预检已完成。公开Core符号和Settings访问实际参与校验；新模块不能借user私有CRUD或动态import绕过。
- r3 system只改manifest合同字段与raw Model公开import一行；Model原定义/薄重导出按符号分类，models/CRUD/Service统一model_requires。disabled提供方Model仍可用；真实Service依赖、runtime环和缺失provider严格阻断；disabled非Model export只静态查存在，不eager import未安装runtime。
- 十模块、auxiliary四实体、monitor两历史实体/10文件切片完成；价格两表/六类实现唯一归energy，三API wire/权限/精度/时间与小时原子upsert保留。HR仍disabled；Core monitor事实链未改，业务两GET独立monitor-business-read，普通规则/历史GET不seed。
- 唯一后继 `d2f4a6b8c0e2`（down `b8d0f2a4c6e8`）显式42表与索引，无autogenerate/create_all/seed；三旧revision字节未改。
- shift null清空规则、不显示假默认时段、不允许Edit/PUT，双语提示；已有规则加载/保存/加载失败/PUT失败均用实际编译SFC运行回归。同步16份稳定Markdown与CODE_INDEX，不改旧验收bundle或失效历史plans。

完整文件、每文件before/after SHA及新增/删除身份：`/private/tmp/arch-be-005-r2-development/r3-delta.json`；
逐行基线差异：同目录`r3-delta.patch`。二者在本tasks末次写入后生成；最终SHA由交接消息及`handoff-integrity.json`给出，避免本文件自引用hash。
基线998文件清单SHA：`fd532d733ef1ecc0f023e2ae7555d5955139a10f114e68cada55cc4f63280709`。
不将Git总diff归己；4个PLAN/2个catalog、本spec批准收据及并行AW001文件差异另存`r3-excluded-coordinator-delta.json`。
原`r2-checkpoint-delta.*`是冻结历史，71文件/暂停时结果；r3-delta包含其后tasks措辞修正、r3实现、文档和全部末次测试增量。

## A真实命令、结果和证据

以下日志均位于`/private/tmp/arch-be-005-r2-development/`。项目执行复用backend既有uv/uv.lock环境；公开fixture排除真实.env、依赖/cache/运行数据，公开.env*.example仅供原Settings示例断言。公开参数统一由`tests/module_admission_fixtures.py:public_environment`提供，writer/mock/bootstrap关闭，MySQL占位127.0.0.1:1。`run_python`在所有collection/测试代码之前patch同步Engine.connect/raw_connection与AsyncEngine.connect为拒绝；原共享conftest保留，no_db早退有效，无create/drop/create_all或SQLite。

| 检查/实际入口 | exit与实际结果 | 证据 |
| --- | --- | --- |
| 完整项目pytest，`run_python(F, pytest.main(['-q','-m','no_db', '--basetemp', 专属路径]))`，底层`uv run --frozen --no-sync python` | 最初246 passed/20 failed/30 deselected，修正公开示例与旧Core预期；第二267/30通过，第三280/30通过；新增接入负例后286/30通过，末次286 passed/30 deselected，74.99s，exit0 | `no-db-first-r3.log`、`no-db-second-r3.log`、`no-db-third-r3.log`、`no-db-final-r3.log`、`no-db-handoff-r3.log`、最终`no-db-final-delivery.log` |
| 末次同进程`compileall.compile_dir('.',quiet=1)`后完整no_db | exit0，触达Python均编译；不是系统Python3.9证明 | `F-final-delivery/`与最终no_db log |
| Core sanitization/依赖/公开符号/Model分类/disabled/runtime/metadata环、Table extend_existing、路由/错误/权限冲突负矩阵 | 全部包含在286完整套件通过；C2仍运行C0原四份清理断言，无删断言/skip/xfail | `backend/tests/test_module_*.py`、`final-profiles/` |
| `python3 final_profiles.py`（stdlib编排，项目uv guarded子进程） | exit0；C2/E1/E2/F为14/15/16/58表，50/52/54/161个method+path，0/0/0/8个descriptor；E Core所有文件hash不变，三消费者组合原14签名不变 | `final-profiles/{C2,E1,E2,F}/metadata-routes.json`、各profile.json/core-files.json、C2.log/E1.log/E2.log/F.log |
| E显式migration recorder重放/降回Core | exit0；E1=15、E2=16逐表签名一致，各自降回14，Core不变 | `e-replay.py`、`E1-migration.log`、`E2-migration.log` |
| E独立实际ASGI/Schema/Service，合成Session边界；E组合额外Model/DTO/key | exit0；camelCase POST→GET、自有StrEnum、空/未知grants拒绝、read-only grant拒POST、Service失败rollback；组合summary公开DTO/key与probeId读回 | 完整套件`test_e_public_asgi_camelcase_module_error_grants_and_transaction`；`e-combined-api.py`、`e-combined-api.log` |
| 四revision recorder+MySQL dialect CreateTable/CreateIndex编译、42撤回/旧16签名 | exit0，完整58逐表约束/index/type签名对照metadata，downgrade仅42；限定本任务四revision/F fixture，无全仓永久58上限 | `test_business_module_migration.py`包含于286 |
| `uv ... python -m alembic upgrade head --sql`及`downgrade d2f4a6b8c0e2:b8d0f2a4c6e8 --sql`，**仅offline** | exit0，无连接或apply | `compile-offline-r3.log`、`upgrade-r3.sql`、`downgrade-r3.sql` |
| `pnpm --config.verify-deps-before-run=false check:modules` | exit0 | `frontend-check-final.log` |
| 同工具链`test:modules` | 最初44通过；补双语实际SFC PUT错误后46 passed/0fail，exit0 | `frontend-tests-final.log`、最终`frontend-tests-handoff.log` |
| 同工具链`build`，process参数两个公开空page grants与mock false | exit0，仅既有largechunk warning | `frontend-build-final.log` |
| `uv ... pytest --noconftest --collect-only -q tests_mysql` + compileall tests_mysql，置DB拒绝guard | exit0，2入口收集；未调用测试函数/连接或迁移 | `mysql-entry-collection.log` |
| 文档新增链接/精确delta whitespace/git diff --check/spec hash/54 protected | exit0；16份稳定Markdown无失效本地链接，54均unchanged | `handoff-integrity.json` |

前端使用专属公开副本与既有项目node_modules符号链接，无依赖安装/锁变更。初次pnpm验证依赖尝试网络但失败exit1，之后命令flag禁自动依赖验证；初次build缺公开grants按既有合同失败exit1，补process公开数组后通过。Playwright CLI npx在无网络环境无结果，Ctrl-C exit130；改用CUA Chrome。
实际浏览器127.0.0.1:5197只监听合成Vite harness，真实shift SFC/ElementPlus/i18n/主题；API与user使用专属stub。390×844 null中/英×日/夜四组合无Edit/无假默认时段/提示不溢出；已有English/light 07/19规则→Edit→真实dialog→修改cycle→stub保存Success及显示更新。浏览器失败提示未额外执行；实际编译SFC运行测试覆盖中英GET异常及PUT异常（保留dialog/已保存规则且显示翻译error），不是仅源码字符串断言。截图在工具对话证据，未另存本地截图。listener已停止Ctrl-C130，tab已关、viewport已复原；未访问真实API。

## C0/Core patch/C2/E/F重建

以仓库根为cwd，`python3 backend/tests/module_admission_fixtures.py --profile C2 --output <新的专属空路径>`生成C0 git读取+八项批准patch（五Core/system两文件/monitor C0窄overlay）。
E1用`--profile E`；E2再加`--summary`；F用`--profile F`。不需要git checkout/reset，不读真实env、不运行DB。公开配置、guard与项目uv调用见生成器`run_python`，CLI裸调用仅help。F完整pytest命令如上表，原共享conftest不删除。
C0为`363b297bffe65e020108f5504766b4fb1ec3b381`；C2精确源/patch文件清单`final-profiles/C2/core-files.json` SHA `334e8c53797ab412c4dd5892c716f08f912acd7f91dfed2106a372e0cbe98ec6`，聚合`core-patch.diff` SHA `317937d0e08efaf1461227c13a405e865da43e2539eb03689df3dd2cc2fe07b1`。
E1/E2保持相同Core清单；合成消费者源码与各自migration SHA在`admission_probe-files.json`/`admission_summary-files.json`。metadata-routes SHA依次：C2 `8a1134a624dea04e317dc543519eeb5600c081e055f64e5e4bc879686ac51c8e`；E1 `26ffc5938415e5e821bd2170c909534dcde3f68fb42ff0a84f66d3fa7c94d88e`；E2 `8e223572fe5175191460b04898e314162c9fb22e52b8756564f3cf8761a16c21`；F `f8f17a199f891e7ab651359621e2983d8f644350570dc3ca87909e3ef83845a7`。
`final_profiles.py`/`e-replay.py`/`e-combined-api.py`均保留作为本次断言复建证据；脚本输出目标已有时应改为新的专属路径，不覆盖证据。最终源文件审计以r3-delta为准；metadata报告生成后只追加B测试入口、测试精确revision选择与文档/SFC测试，生产metadata/Core无后改。

## B待授权执行准备（未执行）

已准备allowlist内`backend/tests_mysql/test_module_admission.py`及`test_business_module_reintegration.py`，只语法编译/guarded collection。无新conftest、依赖、SQL建库、drop/create_all、默认连接；全函数只有显式指名才运行，不在默认tests testpaths内。
主协调者候选独立Compose project `arch-be005-r3-proof`、`mysql:8.4.6`、127.0.0.1动态映射端口、新卷；草案归`/private/tmp/arch-be005-r3-b-proposal/`，Development未执行。现有database-only/env/3307/用户卷不复用。

| 场景/生成profile | TEST_MYSQL_DATABASE及逐库ACK必须相同 | 起点与测试动作 |
| --- | --- | --- |
| e1 / E1 | be005_admission_e1_proof | 明确已建空schema→base到E1 head→15表反射、合成User记录checksum→真实API/唯一并发/失败rollback→Core记录仍在 |
| e2 / E2 | be005_admission_e2_proof | 独立空schema→base到E2 head→16表、同User保持、组合Model/DTO/key/API、真实FK拒绝及回滚 |
| f_empty / F | be005_reintegration_proof | 独立空schema→base到d2 head→58表反射→合成User/业务fixtures→各enabled业务owner代表读写、只读三owner与auxiliary四实体/reports跨表/价格同小时并发→默认HR404及仅内存manifest启用副本CRUD |
| f_upgrade / F | be005_existing_head_proof | 独立空schema→旧b8 head→显式User/旧追加价/小时价→旧16逐表checksum→d2 head→checksum不变→同业务矩阵，旧2020价格仍在 |
| f_rehearsal / F | be005_rehearsal_proof | 独立空schema→旧b8/上述三类记录→生成副本临时失败revision（重复users表）→失败返回非0、revision仍b8、旧16 checksum不变→移除自建失败文件→正常head→显式downgrade b8只撤42且保留旧16→再次upgrade并反射 |

每场景各生成新的公开源码副本，E副本额外复制以上两个tests_mysql源文件到自身tests_mysql（不是复制共享conftest）。
process环境使用生成器public_environment并覆盖获批的`MYSQL_HOST=127.0.0.1`、动态`MYSQL_PORT`、专用受限MYSQL_USER/PASSWORD、`TEST_MYSQL_DATABASE`；`MYSQL_DATABASE`保持不同公共占位。ROOT参数只为Settings类型占位，不使用root连接；不要将口令写入文档/命令行/日志。另须`TESTING=True`、BACKEND_MOCK/PROJECTION_RUNNER及ADMIN/SUPERVISOR/OPERATOR_BOOTSTRAP全部False、`ARCH_BE005_ALLOW_MYSQL=I_CONFIRM_DISPOSABLE`、`ARCH_BE005_ACK_DATABASE=<该场景库名>`、`ARCH_BE005_ACK_ENDPOINT=127.0.0.1:<动态端口>`、`ARCH_BE005_MYSQL_SCENARIO=<场景>`、`PYTHONPATH=<公开profile>`、`UV_PROJECT_ENVIRONMENT=<既有backend/.venv>`。
在该profile cwd，获批后命令为：

```text
uv run --frozen --no-sync pytest --noconftest -q tests_mysql/test_module_admission.py                  # e1或e2
uv run --frozen --no-sync pytest --noconftest -q tests_mysql/test_business_module_reintegration.py   # 各F场景
```

入口先校验逐库身份/公开profile/无.env/127.0.0.1 endpoint/空schema/MySQL精确8.4.6再迁移，不建/drop schema、不清理volume。合成数据保留供审计；最终drop五库/移除任务新卷等必须列入独立获批清理清单。
这些是可执行准备，**B没有任何pass**。真实连接/反射、MySQL defaults/约束/index兼容、全部业务序列、HR启用副本、并发或失败语义可能在实际B暴露问题，届时在原scope修复并复测。MySQL DDL非事务：临时失败revision只证明首条冲突DDL的失败传播和原记录/revision保持，不证明42表中途部分DDL自动rollback；显式downgrade演练是另一步且会删除新增业务数据，不用于已有数据生产回退。空库初始化业务规则仍须消费项目显式配置，不新增创建规则API/GET seed。

## DEV self-check与后续gate

- A全部源码/离线/no_db/前端自检已执行并通过；完整文件delta、Core/profile hashes、原安全断言及protected54保全可供独立复核。
- 未连接/写任何DB（含SQLite）、未在线Alembic/真实API/Projection/PLC、未Docker/改env/依赖/提交/推送；仅offline SQL与合成Session/浏览器stub。
- trusted-source AST预检不是安全沙箱；动态import fail-closed，manifest不是ACL。58仅本任务F专用预期，C2/E仍证明追加模块无需Core改动。
- 临时资源：`/private/tmp/arch-be-005-r2-development/`（baseline、历史/最终fixture、SQL、脚本、logs、pycache/uv-cache、frontend dist及node_modules链接）和`/private/tmp/arch-be-005-baseline.py`，保留供fresh QA；未建worktree/branch。自建监听/浏览器均已关闭。父协调者的protected证据与B提案草案不归本Development修改/清理。
- 交fresh-context Verification只复核本精确r3 A及B准备事实；B授权前保持AC-007/008与AC-r2-006真实MySQL gate未验证，Human Owner保留最终验收。

# r3 fresh QA第一次失败后的返工实施记录

已完整消费checklist（SHA389341c7f3e7788be5e8e735fb9ec68ad7ed7faa47306a4d59b37d44f5ac1b62）与QA两个repro源码/日志及输入。独立verdict为qa_failed，原286/46通过不是A通过。F-001：错误StrEnum识别依赖类名含Error/预先声明，Failure=Core值且空声明可漏检；F-002：裸Model名覆盖且限定relationship路径被截短，合法同名Item指向错误owner。返工在原r3允许面内，不改spec/checklist/索引/protected。
首次132文件handoff与delta证据保持原文件，副本另存`/private/tmp/arch-be-005-r2-development/rework-qa1/prior-*`；沿原998 baseline/C0。先补真实反例与同族边界、修复AST符号解析，再重建C2/E/F/完整no_db/compile。数据库、Docker与B仍禁止。

# r3 第一次QA失败返工后的Developer handoff（历史）

本次仍为已批准r3，spec SHA `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`；
HEAD/C0/原998文件baseline不变。独立QA第一次`qa_failed`及F-001/F-002事实继续有效并保留，
checklist SHA仍为`389341c7f3e7788be5e8e735fb9ec68ad7ed7faa47306a4d59b37d44f5ac1b62`，Development未改该文件。
本节只记录返工DEV self-check，交协调者另启fresh-context Verification，不宣称修复后QA或最终验收。

## 返工实现与边界

相对首次132文件handoff仅改变五文件：`backend/app/module_preflight.py`、
`backend/tests/test_module_admission.py`、`backend/app/MODULE_CONTRACT.md`及中文pair、所属`tasks.md`。
无新表/API/配置/依赖/权限/业务规则，也没有改spec/checklist/六索引/并行AW001。

- F-001：沿实际BusinessException构造参数追踪原StrEnum，支持import/构造器/枚举别名、限定module、薄重导出、空StrEnum基类、局部literal变量及工厂实际调用参数。枚举类名/文件名不决定错误语义；未用于异常、未被错误声明claim的普通领域`ErrorStatus='active'`合法。实际错误枚举全成员与manifest.error_codes对照，namespace/Core/其他owner冲突仍阻断。
- 工厂优先沿调用点对应实参追踪具体枚举，具体枚举注解只在其他来源不可用时辅助定位。泛型`StrEnum`或无注解本身不拒绝；真实ASGI正例及改成Core冲突值的负例均覆盖，不建立强制注解/类名/文件名合同。只有源码/调用点仍无法定位具体枚举时产生`error-source`（例如把请求的opaque字符串直接传给异常工厂），不因无法分类而静默跳过。该只读literal预检不是Python沙箱或任意动态数据流证明。
- F-002：mapped class按限定原定义建索引，relationship保留模块路径/原class，不截短成可覆盖的裸名。合法原路径及SQLAlchemy唯一后缀定位到同一Probe；原薄重导出identity不变。裸名同名歧义明确失败；provider目录从summary之前改到之后仍组合通过，没有补虚假summary依赖。
- 别名跟踪复用按源码内容key的有界AST缓存；源文件变化不会沿用旧AST。旧Settings/private-import定位断言保留。

当前preflight SHA `ca6a4b8db459ae55eca519fa2df41e59bb6eb1f4d7faa92c9aa7b4c37dce7e52`；
接入测试SHA `7f0030cb2eba9e5c73be4ce82919084a24f050fb2922af1ec23b9ff15576d387`。

## 返工真实验证

专属证据在`/private/tmp/arch-be-005-r2-development/rework-qa1/`。仍使用公开process Settings、既有uv锁环境和生成器DB拒绝guard，无真实.env/DB/Docker/B操作。

| 实际检查 | exit与结果/证据 |
| --- | --- |
| 首次聚焦 | exit4，在conftest加载时发现既有performance错误工厂参数未定位；保留`focused.log`，不是通过结果。后修正来源解析，无legacy白名单豁免。 |
| 第二次聚焦 | exit1，41 passed/1 failed；薄赋值追踪把原私有Settings负例提前报export。修正解析fallback，不改原private-setting断言；`focused-2.log`。 |
| 第三次聚焦完整接入 | exit0，43 passed，25.76s；`focused-3.log`。之后追加扫描顺序与工厂边界。 |
| actual factory/限定关系聚焦 | exit0，19 passed/32按-k deselected，19.71s；泛型/无注解调用点正例、实际ASGI自有错误输出、同路径Core冲突及同名限定关系通过；`focused-factory.log`。随后仅补实际来源不可定位的负例。 |
| 中间完整no_db | exit0，297/30、300/30；`full-no-db.log`、`full-no-db-final.log`，均为相应当时源代码结果，不替代末次。 |
| **末次完整compileall + no_db** | `verified_checks.py`在全新公开`F-verified/`中通过run_python调用`uv run --frozen --no-sync python`，先compileall全树再原样`pytest.main(['-q','-m','no_db','--basetemp',专属路径])`；**304 passed/30 deselected，236.51s，exit0**；`full-no-db-verified.log`。未缩套件/删断言/skip/xfail；原shared conftest no_db早退，拒绝所有SQLAlchemy DB连接。 |
| QA两原始输入末次复跑 | 从只读QA输入复制到`repros-final/`，只叠当前批准preflight修复；enum原反例source/metadata/create_app均正确error-namespace阻断，qualified关系source/完整App/configure_mappers/Probe identity/SQL编译通过；`enum-class-name-final.log`、`qualified-relationship-final.log`，各exit0。原QA程序/输入/log未改。 |
| 新C2/E1/E2/F组合 | `profiles-verified.py` exit0，生成全新`profiles-verified/`；14/15/16/58表、0/0/0/8 descriptor，E Core文件冻结相同，E/F原14表签名不变，原C0四份sanitization断言仍在完整套件执行。 |
| E1/E2显式迁移recorder/E2组合ASGI/CLI | `replay_final.py` guarded项目uv，15/16逐表signature parity、各降回14；E2真实ASGI对合成Session的POST→GET/DTO/key/错误/权限/失败rollback；CLI裸help/显式source检查均exit0；`E1-migration-final.log`、`E2-migration-final.log`、`E2-asgi-final.log`、`cli-final.log`。无在线迁移。 |
| 完整性与文档 | 新总delta/五文件返工delta、diff新增空白、文档链接、git diff --check、54保护指纹/spec/checklist/首次handoff证据核对exit0，见新`r3-rework1-integrity.json`。 |

前端源码/测试和B两个入口本轮零变化；首次DEV前端46/check/build/合成浏览器证据及第一次独立QA46/check/build结果按原事实保留，本轮未冒称另做前端浏览器/构建。offline SQL与三旧migration零变化；原DEV offline日志保留，末次完整304仍包含42表recorder/MySQL dialect编译/降回旧16/价格/Projection等影响面回归。新QA仍应独立补齐此前未运行的浏览器/offline CLI/E2等必要A项。

## 新指纹、历史保全与后续gate

原`r3-delta.json` SHA `c2e56630d9cdca21ed3c674c13850865c3fced27e3064bfbf17b73196f1fc622`、
`r3-delta.patch` SHA `8657ca565d17d3e2af74aeae81e09ef47b69fcc7f2d5ded1b55fc8a3a372e81e`、
`handoff-integrity.json`、原`final-profiles/`全部原路径原字节保留，仍表示首次handoff历史。
本次原998 baseline→当前全量132文件使用独立`r3-rework1-delta.json/.patch`；
首次handoff→本次五文件使用`r3-rework1-only-delta.json`与`r3-rework1-only.patch`，
完整性结果为`r3-rework1-integrity.json`（均在DEV证据根）。它们在tasks末次写入后生成，精确SHA归该integrity及交接消息，不把自引用hash写回tasks。

新C2 `core-files.json` SHA `c64890f898101d5eb66731c513373a615053bb8acc204f0084272c8bc7c52028`；
`core-patch.diff` SHA `fa64efd112704e6c6aa49c4d7040064827d68f5647b2fe5e576d5ef925c47574`。
四profile metadata-routes SHA分别仍为原C2 `8a1134a624dea04e317dc543519eeb5600c081e055f64e5e4bc879686ac51c8e`、
E1 `26ffc5938415e5e821bd2170c909534dcde3f68fb42ff0a84f66d3fa7c94d88e`、
E2 `8e223572fe5175191460b04898e314162c9fb22e52b8756564f3cf8761a16c21`、
F `f8f17a199f891e7ab651359621e2983d8f644350570dc3ca87909e3ef83845a7`；新patch未改变表/路由/descriptor合同。
复建仍用原生成器C0+八项overlay命令；改用新的空output。具体本轮payload/脚本/log及before-rework快照均保留在rework-qa1，不覆盖第一轮证据。

仍无DB/SQLite/在线Alembic/Docker/真实API/Projection/PLC/env/依赖/commit/push。B五场景入口及运行提案只静态准备，未运行且无pass；AC-007/008与AC-r2-006真实MySQL gate未验证。
当前为**Development developer_handoff**，不沿旧286/46或本轮304给QA verdict；协调者另启fresh Verification后才更新独立结论。
新增临时资源仅`rework-qa1/`及四个`r3-rework1-*`delta/patch与integrity文件，没有listener/tab/branch/worktree；保留全部历史与返工证据供新QA。

# r3 第二轮QA失败后的返工实施记录

完整消费第二轮checklist SHA7068c3ed97c939455a126d9533f14c5cfb0b994e7c195b8e556d52e4c5acd8c7、extra_error_boundary_checks.py、extra-error-boundaries.json及两个失败输入/log。F-003为普通package/relative ImportFrom子模块别名误报error-source；F-004为CODE_INDEX旧auxiliary小时Model字面路径。按原批准r3修复，保留两轮QA失败及全部既有DEV delta/profile/log，不改spec/checklist。

入口先保存AGENTS/CODE_INDEX/README pair及ROADMAP pair当前字节与SHA，见`/private/tmp/arch-be-005-r2-development/rework-qa2/shared-entry.json`和`shared-entry/`。四根文档含获批AW001并行增量，ROADMAP pair为其R7批准同步；原132 after当前仅128匹配，绝不回退/归己。52项backend/DB/auth/locks保护仍匹配；ROADMAP两项另作共享状态，不宣称54全部静止。

首次tasks更新辅助Python命令因stdin编码SyntaxError退出1，随即用精确patch记录本节；此前只已完成批准的预检修复和CODE_INDEX一行修正，不把该失败当作项目检查。当前修改仍仅预检、批准接入测试、CODE_INDEX一条路径和tasks；无新规则/命名/注解限制，按Python显式package绑定优先与子模块fallback解析。新证据只入rework-qa2和r3-rework2-*，保留旧998 baseline/C0及原历史纯BE delta。B/DB/Docker/env/依赖/部署/提交/推送继续禁止。

# r3 第二轮QA失败返工后的Developer handoff（当前）

精确Revision仍为获批r3，spec SHA `6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`；HEAD/C0及原998源码baseline不变。完整消费第二轮QA后，仅在原allowlist修复。两轮独立qa_failed及原132文件/第一次返工证据均保留；当前checklist SHA `7068c3ed97c939455a126d9533f14c5cfb0b994e7c195b8e556d52e4c5acd8c7`未由Development改写。本节是DEV self-check交接，不是QA verdict或Human Owner验收。

## 本轮精确实现面

仅四文件：`backend/app/module_preflight.py`、`backend/tests/test_module_admission.py`、`CODE_INDEX.md`一条既有路径、所属`tasks.md`。不改合同/spec/checklist/六索引/业务API/迁移/依赖/真实env；不回退AW001。

- F-003：literal ImportFrom先解析package实际显式绑定与薄重导出的原定义；package未绑定名称时按Python子模块fallback解析。绝对/相对模块别名和显式package别名均支持，没有error_codes文件名、枚举类名或注解白名单。显式Model/DTO/函数绑定优先于同名子模块，保留原对象identity及requires/model_requires分类。
- 同形式Core错误碰撞仍报error-namespace；合法普通domain状态枚举不误判；第一轮Failure空声明与qualified同名Model原反例继续通过预期正负检查。
- 补查disabled runtime边界时真实观察到缺provider的Service错误来源被提前激活（`inactive-observation.log`，exit2）。统一复用runtime inactive判定：disabled Service/API及其subpackage入口不激活未安装的runtime requires；安全models/Model闭包和根模块入口仍严格检查，来源可定位的本地非法错误仍阻断。新增缺失/disabled provider、Service/API子包入口、root/models严格负例；enabled消费者仍严格依赖。未增加模块命名豁免，也未eager import disabled Service/provider runtime。
- F-004：CODE_INDEX仅将小时价格Model路径`backend/app/auxiliary/models/energy_price_hour.py`改为`backend/app/energy/models/energy_price_hour.py`；完整当前文件等于入口AW组合快照的一次精确替换，保留全部相邻AW行。

最终preflight SHA `0035aaf4c4421d65f7ef15eb86f5337c92cdef57c20fbf727234be06f3e7787f`；接入测试SHA `c58c2029979e958d09fcd7f53dbf48024c4ea8b4c5285a14514a37be0561246d`；CODE_INDEX SHA `95cfbd1752d4e725f485aa135e79eabecd90213fce99c1d1adca430041046ad1`。

## 最终真实检查

证据均在`/private/tmp/arch-be-005-r2-development/rework-qa2/`。使用公开无.env的独立源码fixture、项目既有uv/uv.lock和DB连接拒绝guard；没有SQLite建表、在线迁移或缩减完整no_db套件。

| 实际命令/检查 | 退出码、结果与证据 |
| --- | --- |
| `python3 rework-qa2/focused.py`及同guard聚焦末次用例 | exit0，31 passed/36按-k deselected，36.26s；`focused-final.log`。包含package/relative/explicit绑定正例、同形式Core冲突、Model/DTO/函数原定义、inactive/strict边界。 |
| 中间完整no_db | exit0，311 passed/30 deselected，266.74s；`full-no-db-verified.log`。这是inactive修复前结果，不替代下一行末次验证。 |
| `python3 rework-qa2/full-final.py` | exit0；全新`F-final/`先compileall全树，再经`run_python`调用项目`uv run --frozen --no-sync python`执行完整`pytest.main(['-q','-m','no_db','--basetemp',专属路径])`；**319 passed/30 deselected，274.84s**；`full-no-db-final.log`。未删断言/skip/xfail；同轮编译通过。 |
| `python3 rework-qa2/profiles-final.py` | exit0；新`profiles-final/`的C2/E1/E2/F为14/15/16/58表和0/0/0/8 descriptor，E冻结Core源码相同，E/F旧14表签名不变；`profiles-final.log`。 |
| `python3 rework-qa2/replay_final.py` | exit0；QA2六个原始边界真实App/Service、package/relative Core冲突负例、QA1两个原反例、inactive观察原例均按预期；`boundary-*.log`、`original-*.log`、`inactive-runtime-final.log`。原QA输入/log只读，副本仅overlay当前预检。 |
| 同上E与离线检查 | exit0；E1/E2 recorder逐表15/16 parity及降回14；E2合成ASGI真实API/DTO/key/权限/异常与事务rollback；裸CLI/help/显式source；Alembic真实CLI的upgrade/downgrade `--sql`离线编译。分别`E1-migration.log`、`E2-migration.log`、`E2-ASGI.log`、`CLI.log`、`offline-upgrade.log`、`offline-downgrade.log`。不apply任何SQL。 |
| 分层增量/文档/保护审计 | `python3 rework-qa2/final_audit.py`，exit0；四文件only delta、共享六文档、128当前BE路径指纹、52保护、spec/checklist/旧证据、相对文档链接、patch新增空白及git diff --check；结果见`r3-rework2-integrity.json`。 |

前端源码/测试本轮零变；原DEV46测试/check/build/合成浏览器与前两轮QA46/check/build事实保留，本轮未另启浏览器或伪称独立前端结果。下一fresh Verification须实际补齐合成前端浏览器矩阵（null中英/明暗/窄屏、已有规则Edit/save及失败提示），并独立核对全部A；不以319替代浏览器或B真实MySQL结果。

## 分层审计、重建与未授权边界

原`r3-delta.*`132文件、`handoff-integrity.json`、`r3-rework1-*`、旧`final-profiles/`及两轮QA全部原路径原字节保留。本轮使用独立`r3-rework2-only-delta.json`/`r3-rework2-only.patch`记录入口快照→当前四文件；`r3-rework2-current-fingerprints.json`记录128非共享BE路径及六共享文档的当前组合状态；`r3-rework2-integrity.json`记录精确hash。它们在tasks末次写入后生成，hash归该integrity与交接消息，不回写自引用hash。

原132路径中的AGENTS/CODE_INDEX/README pair已含批准AW增量，单列入口/当前/旧纯BE fingerprint；128非共享路径中仅预检、接入测试、tasks三项为本轮增量，其余125保持第一次返工handoff after。ROADMAP pair为AW获批R7变化，入口到当前保持；其他52保护项字节不变。不把当前全Git diff或AW变化归BE，也不伪造132全部仍由本任务独占。

新C2 `core-files.json` SHA `9396972f06181157f523f8d0f05b35a7ecda741d92cd12e328512185a328d78f`，`core-patch.diff` SHA `08947c51e44b3e7ff90a8d96a1233faf5c5428396809e661b23898b32bf030d8`。四profile metadata-routes仍分别为C2 `8a1134a624dea04e317dc543519eeb5600c081e055f64e5e4bc879686ac51c8e`、E1 `26ffc5938415e5e821bd2170c909534dcde3f68fb42ff0a84f66d3fa7c94d88e`、E2 `8e223572fe5175191460b04898e314162c9fb22e52b8756564f3cf8761a16c21`、F `f8f17a199f891e7ab651359621e2983d8f644350570dc3ca87909e3ef83845a7`。
复建仍用`python3 backend/tests/module_admission_fixtures.py --profile C2|E|F --output <新的空目录>`；E2加`--summary`。C0+八项批准overlay和C2 sanitization不变；具体重建、guard和验证payload保存在本轮三个脚本中。

未连接/写任何DB（含SQLite）、未在线Alembic/真实API/Projection/PLC、未Docker/改env/依赖/提交/推送。B两入口及五独立schema/ACK/环境/命令沿上方准备，仍未运行、没有pass。用户“真实DB测试前先Alembic升最新”的条件已由入口迁移先于CRUD满足；旧head场景明确old head→合成旧记录→latest→新业务检查，此提醒不构成真实库升级授权。AC-007/008与AC-r2-006真实MySQL gate仍未验证。

当前为**Development developer_handoff**，协调者另启fresh-context Verification。新增资源仅本轮tmp证据及新r3-rework2文件，无listener/browser/tab/branch/worktree；全部保留供复核。AST静态定位仍不是Python安全沙箱或任意动态数据流证明；inactive runtime来源只在该运行面真正启用后严格激活，metadata闭包从未豁免。

# r3 B第一轮恢复与具体动作批准收据（2026-10-16）

主协调者转递Human Owner明确原话：“批准，按现有隔离 MySQL 方案完成 BE005 两轮验证及专用资源清理；温控采用逐样本保存。同时按 STD 修订 BE003 r3，先给我确认 spec，暂不改接口代码。”本Development仅接续BE005 r3 B第一轮；不修改BE003规格或新接口。B具体动作授权覆盖已审阅提案的本地独立MySQL8.4.6、五个空schema、合成数据/迁移/约束/并发/回退及本project新资源清理。第二轮由协调者准备并交fresh-context Verification独立执行。

批准spec SHA仍为`6a0edd601b172f34039c67fd70c48a86b5d98e32b897bd43a8e7cbf037a3b53d`。本轮入口HEAD为`1a5aa2d2fe7089b5671218865238cfaa240f9a30`；C2历史C0仍固定`363b297bffe65e020108f5504766b4fb1ec3b381`，不将新HEAD或并行Console UI变化归为BE005增量。入口tasks SHA为`59a71c4b810659dc4755ad4ec23792868ddc0138bb26a0da4f10ac89ab7aa87e`，checklist SHA为`6f106797f4e62b5295e26acad35e9e006a1c2f027e88fe0eae25fe0e41d7259d`。

本轮基线、非秘密文件快照与操作证据目录为`/private/tmp/arch-be005-r3-b-development/`；入口`baseline-files.json`记录1577个非忽略、非env文件，`git-status.txt`保留并行dirty。已核对上次DEV128非共享BE路径全部指纹相同；上次fresh QA的654个backend/frontend文件仅backend PLAN pair为协调者索引差异，其余652相同。因此既有A独立319 no_db及前端证据适用于本轮入口，未从头重做A。后续若真实B暴露缺陷，先保存失败并报告协调者，按影响面必要复测。

写入前完整阅读根AGENTS/README/PLAN pair、canonical workflow、Development TOML、完整BE005 bundle、backend/app及auxiliary/energy/monitor说明/PLAN、七份backend-arch references、两份Docker skills、两个tests_mysql入口、profile生成器及提案四文件。提案文件均匹配`proposal-files.json`，proof SHA为`c36e3c80a243907d8c2cf0c20d1c140e30b59000f929a967f924c28de572978a`。初始化SQL只建空schema/受限用户权限，真实结构由每场景入口先执行Alembic；不用create_all/stamp，共享破坏性conftest不参与。

首次sandbox `proof.py assert-absent` exit1；只读诊断明确本机`unix:///Users/jason/.docker/run/docker.sock`被sandbox拒绝。以Owner已批准动作申请工具权限升级后assert-absent exit0；未遇auto-review拒绝。另精确inspect卷`arch-be005-r3-proof_proof_mysql_data`及网络`arch-be005-r3-proof_default`均不存在（各exit1/no such resource），避免采用无标签同名资源。prepare --round1已完成五个公开profile及两个0600随机secret；口令不输出/不写入命令或文档，保留供第二轮，最终由协调者清理。当前尚无DB测试通过事实，第一轮实际结果继续追加于后。

# r3 B第一轮 Developer handoff（2026-10-16，当前）

本节是Development self-check及精确交接，不授予QA verdict或Human Owner最终验收。第一轮五场景真实MySQL均exit0，专用栈已清理；第二轮尚未prepare或启动，由协调者重新创建新空栈并实际启动fresh-context Verification。上方全部A/B未授权文字及失败记录保留为当时事实，当前性以本节和B批准收据为准。

## 本轮精确变更与失败保全

仓库增量仅`backend/tests_mysql/test_module_admission.py`、`backend/tests_mysql/test_business_module_reintegration.py`及本tasks。生产API、Service、Model、预检、profile生成器、旧三migration/新d2迁移、真实env、依赖/lock、spec/checklist和六索引均未由本Development改动。六索引/BE003 draft与Console UI等并行变化单列，不据Git总diff归己；HEAD仍为`1a5aa2d2fe7089b5671218865238cfaa240f9a30`，无commit/push/refs。

第一轮在同一批准方案中先后使用七个新空卷尝试；前六次失败及其实际执行源码、日志、results原字节保存在提案根的`round-1-attempt-1`至`round-1-attempt-6`。每次均先停止测试、down专用新栈、核对专用标签和精确卷/网络不存在，再prepare新的round-1；没有清空/采用既有库，没有覆盖失败证据。归档旧新路径与SHA分别在DEV证据目录`attempt1-archive.json`至`attempt6-archive.json`，执行源码副本在`attempt-*/`；第二、三次失败后仅相应E1/F-empty公开副本叠加只读反射核对helper，另保存失败时真正执行的源码，明确区分后续audit overlay。

| 尝试 | 实际失败与最小修复；不是生产迁移/业务缺陷结论 |
| --- | --- |
| 1 | E1已真实base→d4→e1；反射差集仅`control_agent_gate_tokens`。测试metadata只导入普通Registry及TokenBlacklist，遗漏显式安全边界Model；添加ControlAgentGateToken导入，完整表集合断言保留。 |
| 2 | MySQL将unique Index同时反射为unique constraint（sys_dicts.dict_type）；expected unique集合合并UniqueConstraint与unique=True Index，仍exact比较并保留索引名/列/unique核验。 |
| 3 | E1/E2通过；F迁移到d2后NUMERIC/DECIMAL显示名不同；同精度/scale规范化，仅裸Numeric()按MySQL实际默认DECIMAL(10,0)。BOOL/TINYINT(1)原规范化保留；不同precision/scale/unsigned仍拒绝。当前F58表只读反射收敛后才重建。 |
| 4 | E1/E2通过；F到maintenance POST，领域`code='B001'`被helper误当信封code。仅dict且code/message/data三键齐全时验共享信封，bare/list保持；源码核对同时修正报告totalCoils和设备processParams两个既有camelCase测试期待，数值/关系断言不缩减。 |
| 5 | 维保POST后下一独立请求GET404；测试override缺真实get_db的成功commit/异常rollback。仅复制现有依赖生命周期及autoflush=False，跨请求持久化断言和直接Service失败rollback均保留，不改生产事务。 |
| 6 | F其他全部业务矩阵通过，到HR副本CRUD404；测试改manifest后复用首次关闭状态缓存router。测试显式启用副本后reload(app.router)并构造新App，finally恢复manifest/组合缓存；正常组合HR404保留，不宣称热启用或改源码开关。 |

另补证据持久化：每次真实Alembic命令、exit及脱敏输出写公开profile的`migration-commands.jsonl`，不改变非0传播；每次checksum写`checksum-snapshots.jsonl`；演练首条DDL失败脱敏stderr写`migration-failure.log`。完整反射额外比较server default、FK ondelete/onupdate及Check SQL，实际type/null/PK/FK/unique/index/check原断言保持。无新增业务/表/API或运行配置。

## 第七次完整真实执行（round1最终运行）

沿原`proof.py`与Compose/SQL，project=`arch-be005-r3-proof`，固定镜像`mysql:8.4.6`，本地Unix socket，最终端口`127.0.0.1:54767`（已关闭）。镜像arm64/linux，ID/digest=`sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`。实际五库连接身份均`be005_proof@%`，只获这五schema权限；不使用root连接。原runtime DB、3307、真实env/PLC/Projection/bootstrap均未触及。最终身份/版本/表集合/revision与SHOW GRANTS保存于`final-target-audit.json`，其只读核验exit0。

每场景以对应公开profile为cwd，真实入口均为`uv run --frozen --no-sync python -m pytest --noconftest -q tests_mysql/<入口>`，复用既有backend/.venv/uv.lock；无安装或构建。E两个入口为test_module_admission.py，F为test_business_module_reintegration.py。TESTING=True，mock/Projection/bootstrap=False，逐库/endpoint ACK匹配；初始化SQL只创建空schema及受限用户权限，先Alembic再业务API/Service。所有业务HTTP均进程内ASGI，无API listener。

| 场景/schema | 真实结果、迁移/反射/数据/业务事实 |
| --- | --- |
| E1 / be005_admission_e1_proof | exit0，1 passed/2.18s；base→d4→e1a3c5e7b9d1，15表逐表比较；真实POST→GET、自有错误/权限、同unique并发一成功一rollback；14 Core表两次checksum完全相同。 |
| E2 / be005_admission_e2_proof | exit0，1 passed/2.17s；base→d4→e1→e2a4c6e8b0d2，16表；公开Model/DTO/key组合API，真实缺失provider FK拒绝且rollback、唯一并发；14 Core表两次checksum相同。 |
| F空库 / be005_reintegration_proof | exit0，1 passed/12.05s；base→d4→a6→b8→d2f4a6b8c0e2，58表；auxiliary四实体、project/maintenance/plan/performance/quality/reports代表写入及独立请求读回，reports跨StopRecord、plan↔performance/quality关系、dashboard/equipment/monitor合成fixture读取，价格三API及同小时并发整组一致/唯一行，唯一冲突Service rollback；默认HR404，显式重建启用副本HR部门CRUD。 |
| F旧head / be005_existing_head_proof | exit0，1 passed/13.60s；先base→b8，再显式合成User+旧追加价+2020小时价；16表逐表checksum在d2升级前后完全相同；完整F业务矩阵通过，最后两个legacy价格原remark仍在。 |
| F演练 / be005_rehearsal_proof | exit0，1 passed/13.24s；base→b8+上述合成旧记录；临时副本revision首条重复users DDL实际exit1/MySQL1050，revision仍b8、16表checksum不变；删除自建失败文件后正常升d2，显式downgrade b8仅撤42且旧16保持，再upgrade d2及58表反射通过；5份16表checksum全部相同。 |

结果为`round-1/results.json`与五个`*.log`，摘要为DEV证据目录`round1-summary.json`。每profile反射报告`schema-reflection.json`保存真实columns/defaults/FK/unique/index/Checks；各profile的migration/checksum日志保留逐次实际输出。首DDL失败不证明MySQL中途DDL自动rollback；downgrade仅为获批可丢弃副本演练，会丢新增业务数据，不用于现有现场回退。

## 最终表达式比较加严与证据版本区别

协调者review指出初版expression全串lower/去空白及宽括号regex可能混同字符串或AND/OR分组。实际五场景执行的admission测试SHA为`43c61d2eba0b8681593ac6fa297dd69f3cd39d779a4ebddc388d3ce53edc1514`，business测试SHA为`3d9a1bd4ec676e76394315f91850e6c4fa0b4220dcf437bcb8214206b4a36d6a`；这些原执行副本和真实反射报告均未覆写。

清理后仅加严admission测试expression：token级保留单/双引号literal原内容/大小写/空格和未知非空白字符，返回token tuple以保存token边界；只规范化literal外语法、已观察_utf8mb4标记/current_timestamp↔now、完整冗余外层及三token简单原子比较括号，不剥含AND/OR/NOT或嵌套函数的非冗余分组。最终admission测试SHA为`1cd71e770ef8cfa71e175b53bcdef9943562748d90f170586229a2bad864b03d`，business SHA不变。

`expression-recheck.py`直接从最终源码AST抽取实际函数，14项正负expression边界及3项type边界exit0：Active/active、A B/AB、quoted括号、None/0/NULL、0/1、不同AND/OR/NOT分组、token边界/未知字符、不同precision/scale/unsigned保持不等，已观察MySQL等价表达式同等。`run-captured-recheck.py`在公开uv环境、DB连接拒绝guard下，对原五schema真实反射逐项重检最终函数：E1 159列default/2 checks、E2 162/2、各F 688/16，合计2385列default/52 checks，全部零不等；三个子进程exit0。原始反射SHA固定于`raw-reflection-sha256.json`，未改raw数据。

此项明确是**已保存真实反射的加严比较重检**，不是最终token版本又连接MySQL或重新执行五场景。最终两个测试源码已单独compileall exit0、collect-only 2项/exit0，输出为`compile-token-final.log`、`collect-token-final.log`。第二轮fresh Verification须在全新MySQL上使用最终源码完整执行，不能把本轮重检冒称该独立验证。

## 精确命令、清理、限制与第二轮输入

最终一轮实际操作依次为以下原提案命令；除检查资源不存在的inspect返回预期1外均exit0：

```text
python3 /private/tmp/arch-be005-r3-b-proposal/proof.py assert-absent
python3 /private/tmp/arch-be005-r3-b-proposal/proof.py prepare --round 1
docker compose --env-file /dev/null --project-directory /private/tmp/arch-be005-r3-b-proposal -p arch-be005-r3-proof -f /private/tmp/arch-be005-r3-b-proposal/compose.yaml config --quiet
docker compose --env-file /dev/null --project-directory /private/tmp/arch-be005-r3-b-proposal -p arch-be005-r3-proof -f /private/tmp/arch-be005-r3-b-proposal/compose.yaml up -d --wait --wait-timeout 180 mysql
python3 /private/tmp/arch-be005-r3-b-proposal/proof.py run --round 1
docker compose --env-file /dev/null --project-directory /private/tmp/arch-be005-r3-b-proposal -p arch-be005-r3-proof -f /private/tmp/arch-be005-r3-b-proposal/compose.yaml down --volumes --remove-orphans
```

最终日志分别为DEV目录`attempt6-project-absent.log`、`prepare-retry6.log`、`compose-config-retry6.log`、`compose-up-retry6.log`、`proof-run-retry6.log`、`compose-down-final.log`。更早六次尝试命令同形，真实run均exit1，归档/清理exit0；首次prepare工具yield后未保留其独立终态退出码，仅据完整产物记录完成，不补造退出码，后续六次prepare退出码均实际获取0。所有实际命令、环境安全字段/内部Alembic命令与日志索引归`commands.jsonl`及各profile日志。

最终容器ID=`434a56aeb451243fbc6a4719d00f843a792686e4d0bde22f58002e153c54f832`；网络ID=`2d52ac438f8122047287f586bb8d4a7f0568370d55e14d402eb79c515bd8b72a`，新卷精确名`arch-be005-r3-proof_proof_mysql_data`。每次创建前精确同名资源不存在；各次identity与up日志证明本轮创建。最终down exit0，`cleanup-audit.py` exit0：本project标签容器/卷/网络全部为空，精确卷/网络inspect各exit1/not found。仅这些本轮新资源被删除；镜像保留，没有prune、其他容器/卷删除或真实库变更。

保留提案根两个secret文件，权限均0600，内容未进入命令/文档/log；仅给第二轮使用，最终由协调者删除。DEV新建临时资源仅本证据目录及提案根round-1/六个attempt归档/uv-cache/pycache/secret（无其他worktree/branch/listener）；全部非秘密测试输出保留审计，真实数据库合成数据随卷销毁。旧A/失败QA/原baseline等资源未清理。

第二轮输入：同一approved r3/spec SHA、当前HEAD、最终两个test SHA、未变生成器SHA=`e840f495ea61ce4f307b17c97d43b2ca399e6c3f69d5de2734e0f6da175d8798`、未变preflight SHA=`0035aaf4c4421d65f7ef15eb86f5337c92cdef57c20fbf727234be06f3e7787f`、原提案根四文件及同一C0。协调者先确认标签及精确名称均absent，再原helper prepare --round2/config/up；fresh Verification独立读取完整bundle/diff并run --round2，结束后按独立职责交协调者清理。不得复用round1任何数据库状态、将token重检当真实第二轮或将DEV结果写为QA结论。

本轮生产/A源码指纹仍适用；实际差异仅两MySQL测试与tasks，未重跑全319/前端且不冒称新独立A结果。范围匹配compile/collect、最终函数边界与原反射重检、文档/增量diff及保护指纹已执行；最终tasks/delta/完整证据SHA由`developer-handoff.json`和交接消息给出，避免自引用。已知边界仍包括AST预检不是沙箱、文本schema比较仅针对本次C2/E/F既有表达式、未验证生产/现场/备份恢复/真实mapping/PLC、未经Human Owner最终验收。
