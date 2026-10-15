Task ID: ARCH-BE-005
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已明确批准ARCH-BE-005 r3，交Development按STD续做A源码阶段并更新tasks.md；B数据库及Docker仍未授权

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 回迁修复和模块接入合同的纯Model依赖分类、Core声明及C2覆盖一致性修正
Owner: aiis-ics-arch 后端可复用业务模块及Core模块接入合同
Depends On: ARCH-BE-002 r3 owner_accepted, ARCH-BE-004 r2 owner_accepted
Related Task: ARCH-BE-003, ARCH-FE-003, ARCH-MIG-001
Acceptance Chain Reference: ARCH-BE-005 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-14
Updated: 2026-10-14

# r3 范围批准收据（2026-10-14）

主协调者转递Human Owner异步明确答复原话：“批准 ARCH-BE-005 r3，继续 STD 源码开发”。
批准对象为刚提交的r3候选，SHA256 `f9a745d66b56c84879d19e8c122489ea86c1ec410b24cfd5044905c109221588`。
据此记录精确r3为`owner_approved`，交Development按既有r3范围和allowlist续做A源码开发/检查并
更新所属tasks.md。提问中已明示数据库和Docker仍不执行，本次批准沿用该限制：B数据库/在线迁移/
Docker及相关具体运行动作尚未授权，A源码检查通过后仍需另行确认；不据局部通过宣称整体QA或最终验收。
本次只记录批准，不改变需求、AC、allowlist、风险或r2/r1历史。下方待批准/draft文字保留为当时事实，
当前状态以顶部元数据及本收据为准；fresh-context Verification与Human Owner最终验收继续按STD后续gate。

# r3 当前待批准增量

本r3只纠正r2 A源码预检发现的依赖分类和Core覆盖矛盾，不新增业务功能、表、API或运行操作。
r2批准收据及其全文、r1全文在下方逐字保留；本节与r2完整合同构成候选r3，冲突仅在下述明确
增量内以本节为准。r2原有14/15/16/58表profiles、42表后继/三旧migration保护、价格单owner、
HR关闭、monitor业务独立权限、排班null小适配、本地Projection和其他需求/AC/排除项保持。
Human Owner只批准过r2；本r3尚未批准。Development已暂停写入并保留现场，tasks仍为r2事实记录，
PM只改本spec，不改tasks/checklist或实现；需要Human Owner批准精确r3后再续相应Development。
B数据库与Docker禁令保持，A源码阶段完成后仍须另行具体确认，r3不提前授权。

## 裁定依据：不存在严格满足原r2的零增量路径

- C0 `363b297bffe65e020108f5504766b4fb1ec3b381`及当前
  `backend/app/system/crud/async_projection_mapping.py:15`均从
  `app.monitor.models.monitor`导入PlcDbBlockRawSnapshot，仅在get_raw_device_identity构造ORM查询；
  没有调用monitor API/Service或采集runtime。当前system manifest无依赖声明，monitor manifest无exports。
- Development [tasks](tasks.md)记录实际C2预检失败：`stage=undeclared-dependency,module=system,
  identifier=requires:monitor`，位置为上述import。PM只读确认源码原因，未重跑App/预检。
- r2明文禁止漏声明和私有import，legacy默认只是空依赖/空exports，不是豁免；monitor事实Model也
  不在r2显式user类型的Core例外中。C2只允许五个Core patch，且monitor manifest必须为C0；
  system manifest/CRUD又不在r2允许面。绕过报错、推断中央依赖或放宽legacy均不合法。
- r2还把dashboard→plan、plan→performance、reports→auxiliary/plan/performance明列runtime边；
  已读对应CRUD/Service import实际同样都是Plan/Performance/StopRecord Model。因此不能只给system
  特例。本r3显式修订通用分类及旧边，作为实质变更提交批准，不冒称r2已有授权。

## R3-001 只按公开符号类别扩展model_requires

`model_requires`在r2原“model包/FK/relationship闭包”之外，增加消费者在API/CRUD/Service等文件
中直接引用提供方公开SQLAlchemy Model定义的情形。分类按符号原定义/薄重导出追踪，不能按import
所在目录猜测；必须确认来自目标声明的models_package且是同一ORM映射实体，不把任意名为Model
的类或无法定位的符号降级。只扩这一类，DTO、纯key和其他类别不顺带改变r2规则。

纯Model引用用model_requires即可：提供方manifest/models_package/exports必须存在且兼容、
Model可安全导入，提供方API可disabled；消费者只能执行其已获批SQL/事务，不能由此取得对方API
权限、DDL权或采集writer。消费可执行Service/handler/函数仍必须requires且提供方enabled，
runtime缺失/disabled/循环仍阻断。若模块显式同时声明requires，同一owner仍受enabled条件限制，
不因预检认出Model就静默删除该声明；FK/关系继续参与model闭包与owner检查。
漏依赖/失效export/私有import/无法判定仍定位失败，不新增中央业务名单或Core事实类型豁免。
disabled消费者的model闭包仍必需，runtime inactive规则及order/BE001配置策略均沿r2。

以下替换r2明示边，而非事后把它们说成原本不是runtime；目前确认仅Model的边从requires移出，
并并入model_requires。若DEV发现真实非Model执行调用，按实际另外声明requires，不自动放过。

| 消费方 | r3声明的Model依赖 | runtime requires处理 |
| --- | --- | --- |
| dashboard | plan | 当前仅Plan引用，删除r2对应runtime边。 |
| plan | performance | 当前仅Performance引用；保留Plan/Performance双向metadata闭包。 |
| reports | auxiliary、plan、performance | 当前StopRecord/Plan/Performance引用，删除r2对应三条runtime边；已有FK边并入同一闭包。 |
| performance | plan | 原FK/relationship model依赖保留，非新增runtime边。 |
| system | monitor | 新增仅PlcDbBlockRawSnapshot定义/查询依赖，requires不新增monitor。 |

提供方公开入口仍是既有薄model包：plan.models:Plan、performance.models:Performance、
auxiliary.models:StopRecord、monitor.models:PlcDbBlockRawSnapshot，均加`app.`前缀写入exports。
前三项和业务import调整已在r2允许面；第四项只公开这个已存在的Core原始事实Model，不新增Model、
业务表或可执行能力。`app/monitor/models/__init__.py`在C0已重导出该class，C2无需修改该文件。

## R3-002 精确新增源文件允许面与C2 overlay

不增加新源码文件。只在r2既有允许面外增加下面两个system文件；monitor manifest的F修改已在r2
允许面，本次新增的是它在C2中相对C0的明确窄overlay。其他Core源文件不因这次阻塞扩大范围。

| 精确文件/生成项 | r3允许差异 |
| --- | --- |
| `backend/app/system/manifest.py` | 显式v1，model_requires=("monitor",)，requires保持空；其原enabled/order/router/models_package/permissions不变，不自动导出system内部Service。 |
| `backend/app/system/crud/async_projection_mapping.py` | 仅将一处import改为`from app.monitor.models import PlcDbBlockRawSnapshot`；SQL、事务、调用者、返回和权限行为不变。 |
| C2中的 `app/monitor/manifest.py`（来源文件为`backend/app/monitor/manifest.py`） | 以C0 manifest为底，仅显式v1/空依赖和exports=("app.monitor.models:PlcDbBlockRawSnapshot",)；保留C0 enabled/order、两Core事实router聚合、models_package和monitor permission。不得从F复制monitor-business-read、业务route/Model。 |

C2由原五个Core patch扩为五文件加以上三项源路径，记录精确overlay patch/hash及C0来源；
monitor routes/models包与三Model定义仍为C0。F中的monitor manifest保留r2业务key/聚合与本公开
Model export。既有`module_preflight.py`只实现R3-001分类，`module_contract.py`/MODULE_CONTRACT
双语只同步语义/来源；C2生成器和既有依赖/接入测试只补上述overlay及矩阵，均在r2允许面。
不得依此改app/router、role resolver、schema-maintenance业务、数据库层或已发布迁移。

schema_maintenance已有StrEnum值`schema_maintenance_status_failed`、`schema_maintenance_action_failed`
继续作为r2有界Core兼容清单，保留wire和同一BusinessException；不为了新模块命名范式改旧错误、
schema维护HTTP行为、其Service或新增通用响应平台。

## r3追加验收、阶段事实与下一gate

r2所有AC与A/B门槛保留，依赖分类相关项目按R3-001替换，再加以下定向证据：

| AC | 批准后A阶段必需证据 |
| --- | --- |
| AC-r3-001 分类 | 同一个公开Model分别从models、CRUD、Service导入均校验model_requires；提供方disabled仍可导入/组合。实际可执行Service引用在提供方disabled时仍失败，不能按文件位置或名称伪装Model。 |
| AC-r3-002 声明/导出 | system→monitor显式model依赖和公开raw Model入口通过；删除model_requires、移除目标manifest/models_package/export、退回私有import分别定位失败。相同Model重导出对象/表owner不变，未增加任何事实写入能力。 |
| AC-r3-003 本批一致 | dashboard/plan/reports旧runtime边按表显式迁为model边；漏声明仍失败，Plan/Performance合法metadata环保留；requires真正执行依赖图/自依赖/循环及原disabled规则回归通过。 |
| AC-r3-004 C2/E/F | C2 overlay差异只为上述三项加原五Core patch，14表签名/事实API/权限不变；冻结后E Core文件指纹仍不变且15/16表，F仍58表；不可跳过Core sanitization或用legacy名单掩盖本次依赖。 |
| AC-r3-005 兼容/交接 | 两个schema维护legacy错误wire不变；源码/新旧依赖与接入回归、文档/指纹/diff和原完整A检查完成后交fresh-context Verification。此前局部通过不能替代完整A，更不能替代B/最终验收。 |

Development原r2记录：C2/E完整A尚未通过/冻结，单次预检已失败。主协调者转递的后续阶段事实为
54个保护文件无变化、新聚焦单测26通过、61个Python编译通过，当前已全部停写保全；这些是DEV
局部证据，不是独立QA或整体源码通过，PM未复跑，不据此解除B数据库/Docker禁令。
本r3新增风险是误把Model读取当成可执行调用豁免，以及C2误带入monitor业务面；以符号原定义、
显式依赖/公开export、三项overlay差异和正负矩阵控制。其他r2风险与回退边界保持。

2026-10-14 r3：主协调者依据Development真实阻塞请求PM最小裁定。PM消费approved r2、现有tasks、
C0/当前system引用、两个manifest、monitor重导出、预检分类和schema维护错误源码，形成本draft。
r2批准不移转为r3批准；Human Owner尚需重新确认本精确r3，再由Development续tasks记录，
随后fresh-context Verification与最终验收。PM仅写本spec，无实现/测试/DB/Docker操作。

# r2 已批准规格与批准收据（全文保留；当前待批准增量见r3）

Task ID: ARCH-BE-005
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已明确批准ARCH-BE-005 r2按STD进入Development；创建tasks.md并实施A源码阶段，源码检查通过后再提交B数据库/Docker具体动作确认

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 回迁业务修复及可复现的后端模块公共依赖、声明依赖、冲突预检与干净Core接入合同
Owner: aiis-ics-arch 后端可复用业务模块及Core模块接入合同
Depends On: ARCH-BE-002 r3 owner_accepted, ARCH-BE-004 r2 owner_accepted
Related Task: ARCH-BE-003, ARCH-FE-003, ARCH-MIG-001
Acceptance Chain Reference: ARCH-BE-005 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-14
Updated: 2026-10-14

# r2 范围批准收据（2026-10-14）

主协调者转递Human Owner精确原话：“明白了，批准 ARCH-BE-005 r2，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
据此记录当前精确r2为`owner_approved`，交Development创建tasks.md，按本规格既有allowlist实施A
源码/测试/文档及离线检查。B数据库、在线迁移、Docker与相关具体运行动作尚未授权，源码检查通过
后由主协调者另行提交确认；保留原A/B验收和未验证gate，不把A通过写成整体QA通过或最终验收。
本收据未改变需求、验收、allowlist或风险。下方draft/待批准文字及r1原文保留为形成规格时的历史事实，
当前批准状态以顶部元数据和本收据为准；QA、Human Owner最终验收与发布/部署授权仍分别经过后续gate。

# r2 当前有效提案

Human Owner最新要求把公共依赖合同、跨模块依赖、冲突检查和干净Core接入验收补入本任务，先确认
规格再改代码。本r2仍为draft；不是对r1或r2的实施批准，也没有新API字段/迁移/运行批准。
本节定义r2增量，连同下方r1的业务范围、42新增/58总表、价格三API/唯一owner、HR关闭、monitor
业务独立权限、规则null最小前端兼容、本地Projection事务、A/B阶段和排除项构成完整r2。
r1原文逐字保留为历史；涉及新接入机制、公共符号归属、allowlist和验收的冲突，以本节为准。
PM本轮仅修改本spec；不创建tasks/checklist，不执行App import、项目行为测试、DB或Docker。
主协调者随后只机械同步原六个PLAN/catalog索引，Human Owner仍需批准精确r2。

## R2-001 “放入app即可接入”的保证与前提

对符合 `aiis.backend-module/v1` 的普通模块，在已验证兼容的Core源码/依赖锁版本上，消费者只需
加入 `app/<module>/`、声明所需模块、提供显式Alembic增量并在迁移完成后重启，即可发现路由、
metadata和权限声明；无需改app/router、中央模块名单、权限resolver或全局业务枚举。
本任务一次性补Core接入机制，后续合规模块不应重复补Core。保证以预检和以下A/B证据为准，
不表示所有旧目录或任意Python代码都可直接运行，也不承诺跨任意Core版本的二进制/源码兼容。
依赖包必须已在消费者批准的环境内；不自动安装包、DDL、seed、授权、启用运行writer或热卸载。
user/control_agent仍显式装配，普通模块不能借manifest替换认证/设备控制边界。

现行缺口依据：ModuleManifest只有name/enabled/order/routers/models_package/permissions；
common.exceptions.BusinessException构造及core.registrar异常handler都读取error_code.value；
test_module_structure既要求固定Core模块集合，又要求十业务目录不存在。因此当前通过旧基线
只能证明公开Core被裁剪，不能证明新模块接入；不能仅把允许目录改为本次十个就宣称扩展完成。

## R2-002 持久公共Python合同与业务归属

批准后新增双语 `backend/app/MODULE_CONTRACT.md` / `MODULE_CONTRACT.zh-CN.md`，由app/backend
README链接，归backend PLAN管理。它是本语言运行时的持久接入手册，不复制根contracts跨运行时
合同，不把本任务一次性42表/客户规则写成Core公共API。合同版本常量及机器可检查的公共符号清单
放 `backend/app/module_contract.py`；它不是业务模块中央名单或自动包管理器。

| v1公共入口 | 稳定范围与禁止依赖 |
| --- | --- |
| `app.module_registry.ModuleManifest` | 本节字段和发现/disabled语义；内部以`_`开头helper不是模块API。 |
| `database` | Base、TimestampMixin、IntPk、Timestamp、UpdatedAt；get_db/get_db_session与get_sync_db/get_sync_db_context/create_sync_session的既有签名、session归属。API只用异步、Projection只用同步；模块不持有全局Session、不直接依赖engine/root_engine或其内部初始化。 |
| `common.schema_base`、`common.response` | ApiSchema、to_camel；SuccessResponse、StandardResponse、serialize_api_data及现有字段/别名规则。现有分页形状不在本次统一重写；类的内部实现不构成扩展点。 |
| `common.exceptions`、`core.deps` | BusinessException；get_current_user、get_current_active_admin、require_permissions及现有认证/权限语义。不得导入role resolver内部表或改用户模型来注册模块。 |
| `app.user`既有类型 | `app.user.models.user:User`、`app.user.schemas.user_out:UserResponse`为显式Core安全边界提供的只读类型入口，允许当前import路径；不是普通模块requires目标。用户写入仍经既有安全API，不向业务模块公开任意user CRUD。 |
| `common.log`、`settings` | log_event/logger现有调用和脱敏规则；只读取已存在公开设置BACKEND_MOCK_ENABLED，不因模块接入修改Settings。其他既有设置仅限本批兼容清单；新模块需新增运行配置时另行规格，不在import时读取真实env/连接外部系统。 |
| 可选旧CRUD helper | `common.async_crud_base:BaseService`、`common.sync_crud_base:SyncBaseCRUD`既有get/list/create/update/delete签名及不commit语义可复用，不要求新模块继承。 |
| 可选Projection合同 | `projection.registry`的ProjectionHandlerDescriptor/Input/GroupIdentity/InvocationContext及既有公开字段；只能声明本地同步目标，runner/runtime内部非公共依赖。 |

以上符号由签名/字段/响应回归锁定在v1；破坏性变化需新合同版本和独立批准。版本标识不替代uv.lock、
数据库版本或迁移版本；框架第三方包以消费者锁文件为准，不包装为新通用SDK。
下方r1的common.data_keys及15个ErrorCode补回只作为本批旧源码的有界legacy兼容面；在文档/机器
清单明确符号、业务owner和旧key，不让未来模块继续向common追加领域枚举、错误或状态。

新模块将状态/规则放自己domain或data_keys，将错误定义为模块自有StrEnum；新错误值采用
`<module>.<stable_key>`，例如 `admission_probe.invalid_value`，不接受临时自然语言字符串作错误标识。
BusinessException窄扩为接收Core ErrorCode和模块StrEnum，检查非空字符串值，保留error_code/code/
message属性和现有HTTP200+code/message/data:null/errorCode响应；handler继续正确序列化.value。
不改认证HTTP语义、全局成功壳、错误平台或外部ingest合同。裸str/非字符串Enum值是编程错误，预检/
测试明确失败。当前legacy snake_case key保持wire兼容；模块重导出同一legacy枚举不算新错误owner。

跨模块只消费被提供方manifest.exports声明的模型/Schema/纯key或Service公开符号。建议入口分别为
`models/__init__.py`、`schemas/__init__.py`、`services/__init__.py`或模块`data_keys.py`/`error_codes.py`，
按实际需要薄重导出；manifest只放字符串，不为发现而导入Service。禁止跨owner导入内部CRUD或
未导出的实现文件；纯重导出不新建Model/Table，也不能让包入口提前导入API或触发运行副作用。
字符串FK/ORM关系也必须有可定位的目标table/class owner和metadata依赖声明，不能靠偶然导入成功。

## R2-003 最小manifest字段与两种依赖

在现有字段上只增加以下五项；不是包版本解析器或插件安装系统。本批所有触达manifest明确填写
版本和实际依赖；未变化旧manifest兼容默认值，但不豁免缺失依赖/冲突检查。
声明值使用可静态读取的字符串/tuple/bool/int字面量，不从Service、运行配置或动态扫描计算。

| 字段 / 缺省 | 候选规则 |
| --- | --- |
| `core_contract: str = "aiis.backend-module/v1"` | 精确标识；空值/未知版本拒绝。缺省视为v1并在诊断标记legacy_default，不宣称已验证未来版本。 |
| `requires: tuple[str,...] = ()` | enabled模块API/Service/同步descriptor实际执行所需的普通模块名；直接依赖逐项声明，不能只靠传递依赖。名称精确、非空、无重复、不含自身；不允许user/control_agent或任意包/URL充当普通依赖。 |
| `model_requires: tuple[str,...] = ()` | 本模块model包、FK/relationship解析需要的其他普通model owner；disabled模块也必须满足。名称规则同上，目标必须有有效manifest和models_package；不要求目标enabled。 |
| `exports: tuple[str,...] = ()` | 本owner公开的精确`module:attribute`符号，路径必须归本owner。可引用同一class的重导出；声明存在/可解析且import-safe，不接受通配符或任意动态import。 |
| `error_codes: tuple[str,...] = ()` | 本owner公开稳定错误值，与模块本地StrEnum实际值一致；和Core/其他owner核对唯一性。legacy同一枚举引用按原定义归属，不再声明第二owner。 |

enabled requires目标缺失/没有manifest/disabled/不兼容均在接入预检失败，报告依赖链；runtime图
只对enabled执行闭包检查有向环，给出完整环路。disabled模块不检查其未执行API的runtime依赖是否
安装/开启，但名称/self/重复仍校验，诊断明确inactive；它的包入口和metadata闭包必须可安全导入。
故disabled不是完全无依赖承诺，更不能用disabled吞掉model或manifest内部错误。
上述非法接入组合是阻断错误；和BE001配置中的unknown/disabled权限key `WARNING + ignore`
分开处理，后者继续原有解析/子集/过滤策略，不能被依赖预检改成自动授权或配置阻断。
metadata闭包中的纯字符串FK/双向relationship可有环；它表示模型共同存在，不代表Python import
拓扑。全部model定义加载后才解析关系；真实Python循环、未声明目标/导出缺失仍失败。
`order`始终只是原有稳定装配优先级，不能偷偷变成依赖排序。依赖校验先完成；需要的模型加载闭包
不改变原router `(order,name)`顺序，不依赖提高order掩盖导入错误。

本批静态已确认的最小runtime边：dashboard→plan，plan→performance，reports→auxiliary/plan/
performance；其余模块无普通跨owner执行import时保持空。metadata边至少performance→plan、
plan→performance、reports→performance；user FK/类型属于上述显式Core公共合同，不作普通依赖。
dashboard/plan/reports直接使用的Plan/Performance/StopRecord改从提供方公开exports取，双方manifest
如实声明。DEV还须核对FK、relative import和其他实际引用；证据发现新边先列清，不能默认中央补依赖。

源码接入预检解析literal import/from、相对import、manifest路径和字符串FK/关系的owner；未声明
跨owner依赖或未导出的内部符号必须报文件/行/符号，不等到首请求失败。动态`__import__`/importlib/
exec拼接业务路径不在v1直接接入保证内，预检标记unsupported并失败，不能默许不检查。
这属于规范检查，不是Python沙箱；可信模块import仍可执行任意Python，静态检查不能证明其无全部副作用。

## R2-004 冲突预检与真实装配核对

新增 `app/module_preflight.py` 提供只读源码预检和组合后的对象核对；不改变“无manifest则跳过、
内部import失败则报错”的边界。可用 `uv run python -m app.module_preflight --project-root <隔离backend>
--check-only` 输出脱敏结构化诊断；裸入口/--help只帮助，不读env、不导入App/运行配置、不建文件。
正常发现共用同一校验逻辑；最终FastAPI组合后、服务ready前核对实际routes。失败不顺序覆盖、静默
跳过或让部分registry结果被当作可用；至少给stage/module/文件或import path/冲突标识/双方owner。

| 标识 | r2冲突判定 |
| --- | --- |
| 模块与声明入口 | name与直接package一致且唯一；同一manifest中重复router路径/models_package声明、两owner声明同一router对象或同一model包失败。缺声明不为它猜中央名单。 |
| 最终HTTP method/path | 展开include_router与API prefix，包含user/CA显式入口、根health及框架文档路径；同方法同规范化路径重复失败，参数名差异如`/{id}`与`/{item_id}`仍同形。不同方法可共用path。静态`/current`与参数`/{id}`合法共存，不把所有可能匹配的重叠一概拒绝；保留原明确装配顺序并测试静态分派。 |
| Model/table owner | 按原Model定义模块、mapper/Table对象和schema+tablename核对，不只数Base.metadata。不同Model/Table定义占同一标识失败，extend_existing不能绕过；同一class被另一包重导出保持原owner，不当第二张表/第二owner。FK指向的owner必须存在/已声明。 |
| permission key | manifest.permissions声明key的功能owner；本批修复后普通key只一个owner，保护显式user/control_agent keys。真实重复claim报定位错误；消费公共类型或引用guard不形成新owner，更不自动授予账号权限。role resolver原“any enabled owner”算法保留，其兼容单测不作为允许新模块重复claim的依据。 |
| 业务错误值/导出 | 新模块命名空间、声明值与本地StrEnum一致；不同逻辑定义复用Core/其他模块值失败，同一class/legacy key重导出不算冲突；同owner错误声明重复和失效export报错。 |

价格冲突在本批显式收敛：energy拥有两表、三route和两price permission；auxiliary只声明非价格
auxiliary key，旧energy的auxiliary claim/旧route/旧Model退下。不得用冲突白名单保留两套价格。
monitor仍单owner，但monitor与monitor-business-read表面隔离；HR仍disabled，models校验照常。
普通发现/预检不DDL、seed、connect、启动worker或更改mapping；不得声称预检替代独立QA/运行证据。

## R2-005 可复现的干净Core接入profiles

不把58表回迁应用改名为“干净Core”。DEV在任务tmp构造以下三个profile，并在tasks交付明确
文件清单/来源、每文件SHA256、迁移清单、参数/命令及生成测试fixture的源码；QA独立重建。

| Profile | 来源、组成与冻结边界 |
| --- | --- |
| C2：升级合同后的Core-only | 原Core来源固定当前已核对Git `363b297bffe65e020108f5504766b4fb1ec3b381`（C0）；复制backend的common/core/database/projection、入口/settings/pyproject/uv.lock/alembic配置，以及app的user/system/control_agent/schema_maintenance/monitor/aiis_demo和app组合入口。只叠加本r2批准的module_registry/module_contract/module_preflight、BusinessException/registrar窄合同patch。monitor使用C0事实21文件/3Model；其manifest/routes/models包用C0版本，避免带回两业务查询。common/error_codes用C0 Core枚举，common/data_keys完全不进入。只保留原d4e6f8a0b2c4 root，metadata14表；价格两后继及42表后继不拷入此fixture，但原仓文件保持。 |
| E：消费者接入 | C2文件清单冻结后，仅加入合成app模块及它们的显式Alembic revision；不再修改C2任何文件、中央名单、resolver、common错误/状态或配置。测试配置由公开fixture/子进程显式参数注入，不携带真实env。 |
| F：完整回迁应用 | r1明确的10模块+auxiliary/monitor切片、42新增/58总表及三旧migration原文，按完整r2机制验证；它和C2/E分别记录metadata集合，不能相互替代。 |

C2生成器必须按C0 Git tree和上述精确覆盖清单建立`core-files.json`/`profile.json`，标记每条来源
为C0或r2 Core patch及patch hash；先通过Core-only sanitization再冻结。生成器不得把当前完整业务
目录一股脑复制后仅跳过失败测试，也不能靠在C2补legacy common符号使样板通过。
C2是明确合成验收profile，不是恢复/修改工作树、重写发布tag或交付新的实体release源码。

合成模块从本地aiis_demo package骨架派生，仅在tmp生成，保留七包且无runtime/seed；给出完整文件
内容和指纹：`admission_probe`包含manifest、api/routes、models/item、schemas/item、crud/async_item、
services/async_item、domain、error_codes及各`__init__.py`；拥有admission_probe_items一表，GET/POST
`/admission-probe/items`、独立read/manage权限、模块自有状态/StrEnum错误/camelCase输入输出。
`admission_summary`包含同样真实所需分层，拥有admission_summary_notes一表和probe外键，显式
requires/model_requires probe，使用probe声明的Model/DTO/纯key exports，验证依赖组合与事务。
两模块都不得import本批legacy common.data_keys或补回的15个ErrorCode。
tmp显式migration候选E1=`e1a3c5e7b9d1`/down=d4e6f8a0b2c4只建probe表，E2=`e2a4c6e8b0d2`/
down=E1只建summary表；独立E为15表，组合E为16表。它们只属测试fixture，不写主迁移链、不发布。

负例从该fixture分别改变一项：缺/无manifest依赖、enabled消费者依赖disabled提供方、self/重复/
runtime循环、未知合同版本、漏requires、缺model_requires/导出或私有import、重复router/model/
表/permission/error、同形参数path、碰Core显式route；给出输入、定位诊断与非零退出。
正例覆盖独立模块、声明组合、关闭消费者API仍有metadata、disabled模型依赖仍存在、合法双向
metadata关系、唯一class重导出、静态/参数path共存，以及未知/空grants不授权。

Core sanitization测试只在C2证明14表/干净目录与退役runtime边界；消费者接入测试在E按fixture
声明动态期待增量，F按本任务58表核对。当前固定Core集合/业务目录absent断言迁入对应C2 profile
执行，不能删除、skip/xfail、缩套件或把十模块名单塞进Core注册逻辑来伪装可扩展。

## R2-006 精确新增allowlist与实施次序

在r1 allowlist之外只增以下文件/表面；其余r1保护继续有效。r1关于module_registry/common异常/
registrar不得改的排除仅在下列窄范围被本r2替代；不连带授权数据库engine、auth或resolver重构。

| 文件 | 批准后用途 |
| --- | --- |
| `backend/app/module_registry.py` | 五个声明字段、兼容默认、依赖/owner校验调用；不维护新业务中央名单，不改变order/显式安全装配。 |
| `backend/app/module_contract.py`、`module_preflight.py` | 公共版本/符号与legacy兼容清单，源码预检及对象冲突检查；无env/外部副作用的模块CLI，不新增backend/scripts入口。 |
| `backend/common/exceptions.py` | BusinessException接收StrEnum的窄扩、验证稳定值；保留现有构造参数/属性。 |
| `backend/core/registrar.py` | 最终app组合后的只读冲突检查hook；如确需则窄适配模块StrEnum的错误序列化，原HTTP/壳/认证不变。 |
| `backend/app/{dashboard,energy,equipment,hr,maintenance,performance,plan,project,quality,reports,auxiliary,monitor}/manifest.py`及现有七包入口 | 声明实际version/依赖/exports/errors、薄公开重导出和必要跨ownerimport路径调整；仅当前业务，不新增能力。可新增各模块`data_keys.py`/`error_codes.py`承载其自有公开纯key，但不得新增规则或去改旧API错误值。 |
| `backend/app/MODULE_CONTRACT.md` / `MODULE_CONTRACT.zh-CN.md` | v1持久公共符号、依赖/冲突、三profile验证和版本/运行限制；根/backend/app README及AGENTS/CODE_INDEX增量沿r1精确范围。 |
| `backend/tests/test_module_{contract,dependencies,conflicts,admission}.py`、`backend/tests/module_admission_fixtures.py` | 新增纯合同、声明/冲突和C2/E/F profile生成/指纹及ASGI回归，合成源码与migration只生成到tmp。 |
| `backend/tests/test_response_contract.py`、`test_role_api_permission_startup.py` | 既有错误StrEnum兼容/权限语义回归，保留BE001配置warning/ignore、等级及admin边界。 |
| `backend/tests_mysql/test_module_admission.py` | 独立显式MySQL E profile迁移/读写/并发/回滚，不进入共享建库/drop/create_all fixture。执行仍另批。 |

实施按“Core窄合同+预检→C2冻结→E源码接入→F业务回迁验证→另批B真实MySQL”交接。
任何阶段需要改app/router、resolver、依赖/lock或新的业务表/规则均回PM新Revision，不把技术实现
选择冒充已有Human Owner决定。tasks/checklist只由后续对应角色在精确r2 gate后创建。

## r2新增验收与风险

r1 AC-001..009完整保留并将目标Revision替换为r2；再要求以下证据，A/B授权边界不变。

| AC | 必需证据 |
| --- | --- |
| AC-r2-001 公共合同 | A：MODULE_CONTRACT双语与机器版本/符号一致，签名/字段/成功壳/camelCase回归；Core和模块StrEnum失败响应一致、legacy key不变，无新增全局业务枚举依赖。 |
| AC-r2-002 依赖 | A：上列正/负矩阵和定位诊断通过；漏声明/私有import不能因当前全模块恰好存在而通过；runtime DAG与metadata闭包分别验证、order不变、HR disabled安全导入。 |
| AC-r2-003 冲突 | A：最终Core+模块method/path、同形参数、router/model/table owner/permission/error冲突均有失败反例；合法静态path与重导出通过；价格两表三route仅energy owner。 |
| AC-r2-004 干净接入 | A：QA独立按C0+Core patch重建C2并冻结；E加入前后Core文件SHA256全一致，独立/组合为15/16表，原14表签名不变；E用自有key/错误/权限完成ASGI输入/输出/错误/拒权，未借F的legacy common修补。Core sanitization与可扩展消费者测试均实际执行。 |
| AC-r2-005 完整回迁 | A：F全部58表与r1功能/前端空态/8descriptor/价格保护回归通过；C2/E通过不能替代F。完整no_db、编译、文档/指纹/diff及原前端check/test/build等必要检查如实记录。 |
| AC-r2-006 真实接入 | B：另批MySQL8.4.6分别对E空库迁移、独立/组合API真实POST→GET、模块自有错误/权限、FK/唯一约束及失败回滚；C2核心记录保持；F继续r1 AC-007/008的真实42表迁移/价格保留和跨模块读写。SQLite/stub/offline不能替代，两profile目标/清理身份分别记录。 |
| AC-r2-007 交接 | 完整r2 approved spec、tasks、C0/Core patch/fixture/完整任务diff指纹及A/B命令/退出码交fresh-context Verification；B未授权或未执行时保留gate，整体不写qa_passed/owner_accepted。 |

新增风险是公共版本默认被误读为任意兼容、漏依赖被当前大应用掩盖、静态预检被误称沙箱、错误/
权限标识冲突，以及C2偷偷带入业务公共修补。以明确支持范围、runtime/metadata分开、同壳StrEnum、
最终对象检查和C0+C2+E指纹控制；不引入包管理、自动安装、复杂插件生命周期或新的响应平台。
模块合同升级是本r2新增的实质范围；r1业务与真实运行 gate不缩减。Skill handoff沿r1 aiis/
project-governance/backend-arch（模块、分层、响应、数据、迁移、认证、测试）；前端窄面继续
frontend-ui/i18n-workflow。这里没有backend/scripts新入口，若后续需要必须新Revision并加载
backend-script-tooling；不宣称本轮已运行预检、构造profile或验证接入成功。

2026-10-14 r2：Human Owner授权补规格，PM只读核对当前r1、治理/模块文档、真实manifest、异常/
响应、注册/role策略、模型关系和固定Core测试，形成以上待批准提案；r1历史完整保留。
未发生r2范围批准、Development/QA、MySQL或Docker操作。下一gate：Human Owner批准精确r2。

# r1 历史草案（原文完整保留，不单独生效）

Task ID: ARCH-BE-005
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending；仅获准创建修复规格，提交精确 ARCH-BE-005 r1 给 Human Owner 范围批准，再交 Development

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 已复制后端业务模块的依赖、唯一 owner、显式 Schema、隔离读写及规则空态兼容修复
Owner: aiis-ics-arch 后端可复用业务模块及共享数据合同
Depends On: ARCH-BE-002 r3 owner_accepted, ARCH-BE-004 r2 owner_accepted
Related Task: ARCH-BE-003, ARCH-FE-003, ARCH-MIG-001
Acceptance Chain Reference: ARCH-BE-005 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-14
Updated: 2026-10-14

# 1. 目标、授权与证据等级

Human Owner 要求“落新的修复 spec”，并说明新规格做什么、为什么迁回的模块不能马上使用。
本 r1 只形成可审查的修复范围；此前对方向的认可及本次落稿授权不构成尚未提交 r1 的范围批准。
PM 本轮只写本文件，不创建 tasks/checklist，不修改实现、测试、环境、旧任务或迁移。
主协调者仅按 draft 机械同步根/backend PLAN pair 与根 plans catalog pair。
依赖已验收的[BE002价格基线](../ARCH-BE-002-energy-price-api/checklist.md)和
[BE004小时合同](../ARCH-BE-004-energy-price-hourly-history/spec.md)及其
[验收记录](../ARCH-BE-004-energy-price-hourly-history/checklist.md)；
[BE003 r2](../ARCH-BE-003-mapping-service-api-pilot/spec.md)继续作为独立未批准任务保留。

目标是把已复制的业务源码接回现行 Core：补齐公共依赖，选择性补回必要业务切片，合并价格 owner，
为明确表集合新增后继迁移，并分别证明源码可组合和隔离 MySQL 真实可读写；同时补排班规则null空态的最小前端兼容。
这不是从头重写业务规则，也不是把全部旧客户能力、数据和运行配置直接恢复。

目标工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；旧源仅只读参考
`/Users/jason/Desktop/DreamCode/vibe-l2-front-end/backend`。主协调者已静态比较以下十个目录的
192 个 Python 文件与旧源逐字一致：dashboard、energy、equipment、hr、maintenance、performance、
plan、project、quality、reports。复制成功只能证明文件相同，不能证明依赖闭合、路由唯一或数据库存在。
本规格另外用静态源码/AST 核对表、依赖、接口声明和前端空态消费；没有执行应用 import、启动、项目
测试、SQL、在线迁移、Docker、真实 env/DB 或 Projection。下文表数均为源码候选，未声称已建表。

# 2. 为什么复制后不能即用

| 根因 | 已核对证据 | 必要修复与限制 |
| --- | --- | --- |
| 公共业务字典缺失 | `common/data_keys.py` 当前不存在；六模块共19处 import，例：`app/hr/services/async_hr.py:19`、`app/performance/domain.py:13`、`app/plan/services/async_service.py:37`。 | 补回本批使用的稳定 key、兼容别名和纯规范化函数，不复制运行配置或业务数据。 |
| disabled 模块的包入口提前导入路由 | `app/hr/manifest.py:14` 为 False，但 `app/hr/__init__.py:15` 导入 API；Python 加载 manifest 前先执行包入口，间接触发上述缺失依赖。 | 修薄模块入口；保留 HR disabled 和 Model 可导入。Registry 内部依赖错误仍显式失败，不能吞异常或静默跳过。 |
| 错误码合同被 Core 精简 | 当前 `common/error_codes.py` 缺已复制业务引用的16个枚举成员；例：`app/project/services/async_project.py:44`、`app/quality/services/async_quality.py:108`。 | 启动正常也可能在实际失败分支 AttributeError；补仍有调用的稳定错误码，移除被替换旧价格分支的悬空引用。 |
| 跨模块 Model 尚未迁回 | `app/reports/crud/async_efficiency.py:13` 和 `services/async_efficiency.py:16` 依赖 `app.auxiliary.models.auxiliary.StopRecord`，当前 auxiliary 只有价格。 | 选择性恢复辅助非价格四模型及对应接口，保留已验收价格实现再迁 owner，不能整目录覆盖。 |
| monitor 仍为精简 Core | 当前21个 Python 文件仅含采集状态/raw/latest；旧源35个，温度/能耗/曲线切片不在当前树。 | 只恢复本规格两业务模型和两查询链；Core事实、CA合同和其他旧模型不得被覆盖。 |
| 价格存在两个 owner | `app/energy/models/energy_price.py:20` 与 auxiliary 均声明 energy_prices；旧 `energy/api/routes.py` 与已验收辅助模块重复三条 URL。 | 可能在 metadata 导入报重复表，或同方法/路径由装配顺序决定处理者；将已验收实现迁到 energy，唯一 Model/route owner。 |
| Schema 没有随源码迁回 | 当前迁移仅 `d4e6f8a0b2c4 -> a6c8e0f2b4d6 -> b8d0f2a4c6e8`，只覆盖16表。`tests/test_core_migration_baseline.py:208` 也仍断言该集合。 | 新业务表必须用后继 Alembic 准备；Registry/metadata 不建表。能启动并不能排除首个真实查询报表不存在。 |
| 旧源有普通 GET 写库 | 旧 auxiliary `services/async_auxiliary.py:51..78` 自动生成班次/默认规则；旧 monitor 两 Service 在 mock 分支写业务样本。 | 本 r1 显著提出只读查询纠偏；禁止把复制的默认班制、空表造数当成已批准规则。可见空态差异见§5。 |
| 权限和运行证据尚未收敛 | 新 manifest 的权限可用 owner 增多，monitor 原 key 只代表事实读取；真实运行配置/映射/数据未检查。 | 审查每条实际挂载接口的 guard；不自动修改任何真实 grants，不把 mock/stub、用户文件复制或旧任务通过当成本次验证。 |

# 3. 功能 owner 与迁移清单

## R-001 已复制十模块

后端按领域功能、数据及事务归属组织；前端目录/菜单不是裁剪后端的依据。HR 名称保留，
hr/project/reports 均保留。下表接口只指当前 manifest 已声明的 router；文件中未挂载的组不自动上线。
内部 API -> async Service/CRUD -> AsyncSession；现有同步业务链保留，纯规则可复用。

| Owner | 本批保留/修复的现有功能与接口族 | Model / 表集合 |
| --- | --- | --- |
| dashboard | 9个现有 GET：stats、production-trend、quality-distribution、oee-analysis、temperature-trend、energy-consumption、downtime-analysis、production-status、recent-plans；prefix `/dashboard`。 | daily_production_stats、quality_grade_stats、downtime_records、production_status_records、temperature_zone_records（5） |
| energy | 价格持久化、当前价、按日/分页历史及整小时保存；只挂载§4三个 API。 | energy_prices、energy_price_hours（既有2表，不新增） |
| equipment | GET `/equipment/drive`、`/equipment/temperature-control`、`/equipment/production-parameters`；保留三个同步采样 Service/descriptor。 | equipment_drive、equipment_temperature、equipment_production_parameters（3） |
| hr | 部门、员工、考勤及统计、招聘及统计；现有 `/hr/health`、`/departments`、`/employees`、`/attendances`、`/recruitments` 路由定义保留，正常组合仍全部关闭。 | departments、employees、attendances、recruitments、applicants（5） |
| maintenance | 当前 `/items`、`/maintenance-logs` CRUD 与查询筛选。 | maintenance、maintenance_logs（2） |
| performance | `/performances`、`/splits`、`/performance-transforms` 现有人工 CRUD、过程数据读取、push-down、拆分/合并、有效重量及lineage；保留四个同步descriptor。 | performance_main、performance_split、performance_process_temperature、performance_process_tension、performance_process_speed、performance_push_down_record、performance_transform、performance_lineage（8） |
| plan | `/plans` CRUD、XLSX模板/导入/导出、现有linkage候选/观察同步/关联/回填；不增加新采集入口。 | plans（1） |
| project | `/project/list`、`/{project_id}`、`/create`、`/stats/overview`；无前端页面仍保留。 | projects、project_tasks、project_milestones（3） |
| quality | 现有 `/quality`、`/defects` 检验、缺陷及SPC查询；保留与reports不同数据owner。 | quality_inspections、quality_defect_records、quality_spc_measurements（3） |
| reports | manifest现有 reports、assessment、efficiency、print、target 五组router；报告/统计、考核、打印记录和目标维护保留。其 `quality_router` 当前未列入manifest，继续不挂载。 | quality_records、defect_records、performance_targets、assessments、production_reports、print_records（6） |

模块原有 enabled 状态保留：HR=False，其余表中模块=True；不通过修复临时关闭其他模块来隐藏错误。
这不是各模块业务成熟度或现场适用性的验收；原有真实规则只作兼容基线，不扩成新的客户流程。

## R-002 公共依赖与错误码

新增 `backend/common/data_keys.py`，优先复用旧源本批实际引用的纯枚举、normalize和storage_values
闭包：计划/实绩状态与来源、有效重量/lineage/时长、质量等级/缺陷、维护类型、HR状态、停机原因、
目标类型/周期。保持稳定英文key、原有兼容别名和已用函数签名；不新增数据库字典seed或运行side effect。

补回仍被使用的15个ErrorCode成员：PERFORMANCE_INVALID_TIME_RANGE；PLAN_INVALID_COIL_NO、
PLAN_COIL_ALREADY_EXISTS、PLAN_LINK_CANDIDATE_CONFLICT、PLAN_NOT_FOUND、PLAN_COIL_CONFLICT、
PLAN_XLSX_UNSUPPORTED_CONFLICT_STRATEGY、PLAN_PERFORMANCE_NOT_FOUND、PLAN_PERFORMANCE_ALREADY_LINKED、
PLAN_PERFORMANCE_NOT_UNPLANNED、PLAN_INVALID_STATE、PLAN_XLSX_VALIDATION_FAILED；PROJECT_NOT_FOUND；
QUALITY_INSPECTION_NOT_FOUND、QUALITY_DEFECT_NOT_FOUND。值沿用旧源稳定key，不改全局异常HTTP语义。
第16个ENERGY_PRICE_NOT_FOUND来自旧价格详情分支；该分支不再挂载，随旧实现退下，不为它恢复新API。
所有有效源码引用均需闭合；不得保留可能在失败分支触发AttributeError的悬空枚举。

## R-003 auxiliary 非价格业务

只合并旧 `models/auxiliary.py` 的 ShiftTeam、Shift、ShiftRule、StopRecord 四实体及
`schemas/auxiliary_{in,out,query}.py`、`crud/async_auxiliary.py`、`services/async_auxiliary.py`
所需切片。API保持现有 `/shift-teams`、`/shifts`、`/stop-records` 各五个CRUD方法，以及
GET `/shift-rules`、PUT `/shift-rules/{id}`；不增加默认规则创建或批量自动排班平台。
移入独立 `api/auxiliary.py`，`api/routes.py` 仅聚合；StopRecord保留原import路径供reports使用。
Service控制显式写事务，CRUD不commit；处理业务异常沿当前共享组件，响应不泄漏SQL/内部异常详情。
成功输出沿现有共享信封和camelCase，避免复制旧bare-response/中文message形成第二套合同；已有字段含义保持。

## R-004 monitor 选择性合并

保留现有 MonitorCollectorState、PlcDbBlockRawSnapshot、PlcDbBlockLatestSnapshot 三模型原定义，
以及 GET `/monitor/collector/status`、GET `/monitor/realtime/latest`、其Core查询/采集治理链。
仅加入旧 HistoryProcessCurve、HistoryEnergyConsumption，保留原表名与字段/索引含义；放入
`models/business_history.py` 并由models包显式导出，不用旧17模型文件覆盖当前3模型文件。
仅合并 `api/{temperature,energy}.py`、`schemas/{temperature,energy}.py`、
`services/{async_temperature,async_energy,sync_process_curve}.py`、
`crud/{async_temperature,async_energy,sync_process_curve}.py`，聚合两条原业务GET：
`/monitor/temperature?date=YYYY-MM-DD`、`/monitor/energy?timeRange=...`；保持已有数据字段与空列表含义。
恢复曲线同步descriptor只证明可发现/可注册，不增加HTTP曲线写入、能耗采集writer或运行映射。

旧monitor另外12个Model不纳入：MonitorTemperature、MonitorEnergy、DeviceDrive、DeviceTemperature、
DeviceTitanium，五个MonitorHmi*Status实体，HistoryAlarmEvent、HistoryProductionTracking。
对应旧五张deprecated表、五张HMI表、报警/生产tracking表及HMI API/Service不迁回；没有依赖证据不能
顺带恢复。新增依赖若确需这些切片，先给具体引用回PM新Revision，不靠增加模型使导入偶然通过。

# 4. R-005 价格迁到 energy，完整保护已验收合同

将当前 auxiliary 已验收的 `api/energy_price.py`、`schemas/energy_price.py`、
`crud/async_energy_price.py`、`services/async_energy_price.py`、两个价格Model原能力迁至energy。
energy为唯一价格Model/事务/route owner；auxiliary只归非价格辅助业务。前端仍可叫auxiliary/price，
本批不改价格页面、前端目录、pageId或facade。删除/替换因本次迁移产生的重复定义及孤立旧价格文件；
若保留兼容import，只能重导出同一class，不能再声明Table、router或第二套实现。

保持 GET `/energy/current`、GET `/energy`、POST `/energy` 恰好一次挂载，URL/prefix、字段、信封不变。
价格读写权限仍分别为energy-price-read/manage；旧auxiliary key不授予价格读写，详情/DELETE不恢复。
保留BE004 r2全部小时合同：observedAt一次取时/拒未来、Asia/Shanghai IANA/fold=0归桶、UTC存储/
带offset输出、同小时原子整组覆盖及createdAt/id保留、跨小时新增、date/分页/排序、current截止现在、
无记录null、不补小时、原始Decimal精度/四位与范围/0/备注/actor/事务/并发边界及F-001回归。
旧energy的硬编码默认价、追加写入、默认补零和较宽权限不得覆盖已验收实现。
energy_prices原始行、energy_price_hours小时历史均保留；本次owner迁移本身不执行数据重写/归并。
BE002/BE004历史bundle原样保留，不能改写其当时owner或通过证据。

# 5. R-006 本 r1 待批准的可见差异与权限

以下是本r1方案，尚无Human Owner确认，批准整份r1才授权实施；不冒称旧行为已符合现契约。

| 可审查差异 | r1候选合同与采用限制 |
| --- | --- |
| 普通GET不再造业务数据 | 去掉auxiliary空查询自动班次seed和默认ShiftRule写入；班次空列表正常返回，规则空表GET返回共享成功信封data:null。旧默认“四班三运转”等不自动写入。规则已有行时沿既有GET/PUT。首次业务规则初始化另走显式data gate，不借schema创建。 |
| 规则空态前端最小兼容 | 当前 `frontend-js/src/app/auxiliary/views/shift/index.vue:415..429` 直接读res.id，data:null会进入catch。本r1纳入该页loader、提示和保存边界小适配：null为合法“未配置”，不报加载失败、不把默认08:00/20:00或“四班三运转”冒充已保存规则；无rule id时不开放规则编辑/保存、不发误写PUT。已有规则的加载/修改保持；新增提示用auxiliary双语locale。没有创建规则API，本批不新增该能力，首次规则初始化仍须后续明确动作；不重做排班、班组或日历业务。 |
| monitor诊断mock隔离 | 去掉温度/能耗GET将样本写入真实业务表的路径。保留Service显式BACKEND_MOCK_ENABLED开关时，只允许内存诊断返回/合成fixture；mock关闭时只读真实已存行，不制造默认曲线/能耗记录。 |
| monitor业务读取独立授权 | 建议新key `monitor-business-read` 仅保护温度/能耗两GET；原monitor key仍只保护两Core事实GET。调整局部router聚合避免业务GET被旧顶层monitor guard意外扩大或额外要求两key。其manifest声明两key，不改resolver。 |
| 其他业务权限可追溯 | 逐个核对实际挂载method/path/owner/guard：dashboard、equipment、maintenance、performance、plan、project、quality、reports沿各manifest既有key；auxiliary非价格沿auxiliary。HR继续disabled；既有裸登录或额外actor限制如发现与manifest不一致，给出证据回PM，不擅自升/降权。 |

真实env、公开example、用户/角色表和sup/op数组不自动修改；既有未知/disabled key变为可用owner的
影响须在DEV handoff列明，运行采用前由Human Owner审查实际grants。admin、401/403、operator子集、
disabled404及安全边界语义保留。新接口定义并不授予任何实际账号权限。

# 6. R-007 Schema 后继与精确表集合

保留既有14表Core root：users、token_blacklist、sys_dicts、sys_dict_items、projection_mapping_sets、
projection_mapping_revisions、projection_mapping_bindings、projection_mapping_audit_events、
projection_runtime_cursors、projection_runtime_audit_events、control_agent_gate_tokens、
monitor_collector_states、plc_db_block_raw_snapshots、plc_db_block_latest_snapshots。
再保留energy_prices、energy_price_hours，合计既有16表及其约束/索引/数据。

新增集合严格为§3表中除energy外九owner的36表，加auxiliary的shift_teams、shifts、shift_rules、
stop_records四表，加monitor_history_process_curves、monitor_history_energy_consumptions两表。
因此本r1候选是新增42表、完整metadata58表；HR虽disabled，其5表仍参加Model/Schema一致性验收。
与旧源表定义逐项核对类型、非空、默认、FK、unique、check、index；不单以表数相同当作一致。

新增唯一后继候选 `20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py`，
revision=`d2f4a6b8c0e2`，down_revision=`b8d0f2a4c6e8`。三份既有revision字节保持；
不复制旧项目migration graph、不改已发布root，不使用create_all/stamp、autogenerate直接覆盖基线。
upgrade仅新42表及其索引/约束；downgrade仅撤本增量且明确会丢新增业务数据，旧16表不动。
若DEV开始时head/上述表集合发生变化，先回PM校正Revision，不能私自改接链或增减表。
Schema不携带账号、默认班制、计划、样本或客户业务seed；普通import/Registry/启动/GET不执行DDL。
本规格不授权真实历史导入或价格归并；只有合成数据进入后续可丢弃验证目标。

# 7. R-008 Projection 与关联任务边界

恢复equipment三个、performance四个、monitor一个旧同步descriptor的发现/注册兼容，核对8个
handler key唯一、owner正确、输入/来源合同可解析；不新增第9个目标或8条HTTP ingest。
原 `projection/runner.py` 本地同一Session的业务写+cursor+audit事务保留，不改成HTTP调用，
不启动runner、不发布/回滚真实mapping、不启现场writer、不改变CA/PLC配置或事实层schema。
测试中的合成事务回归不表示现场点位/发布绑定可用，现有来源白名单不自动转化为部署授权。

本批恢复设备/业务读面后，BE003 r2所述“当前没有equipment/温控GET”和基于16表head的候选allowlist
已需要重新核对。由其PM在本批基线稳定后修订/重新提交精确Revision；本任务不改BE003，也不继承
其未批准的sampleId/receipt/设备scope/温控逐样本或小时策略。SMA、DAA、AWfacts、ROADMAP、Tauri后续另案。

# 8. 后续 Development 精确 allowlist

本轮PM写入仅本spec。下表只有精确r1获批后才是Development候选实施面；不是backend/**授权。
模块目录只授权本节列出的文件类型及以上修复，不允许附加新业务规则。DEV首次写入前在tasks列
实际文件/基线指纹和源到目标映射；共享dirty、用户复制、其他任务原增量不得reset或据git总diff归己。

| 表面 | 允许文件/目录边界 |
| --- | --- |
| 十个已复制模块 | `backend/app/{dashboard,energy,equipment,hr,maintenance,performance,plan,project,quality,reports}/` 内当前192个`.py`文件，仅入口、manifest、既有API/Schema/CRUD/Service/Model依赖修复和上述price替换；不增加其他endpoint/seed。允许因本次price替换删除孤立旧price_in/out/query文件。 |
| energy新增价格文件 | `api/energy_price.py`、`schemas/energy_price.py`、`models/energy_price_hour.py`，以及本模块各现有`__init__.py`/routes/manifest；现有同名Model/CRUD/Service承接已验收实现。 |
| auxiliary合并 | `__init__.py`、`manifest.py`、`api/{__init__,routes,auxiliary}.py`、`models/{__init__,auxiliary}.py`、`schemas/{__init__,auxiliary_in,auxiliary_out,auxiliary_query}.py`、`crud/{__init__,async_auxiliary}.py`、`services/{__init__,async_auxiliary}.py`；原价格六类文件仅迁出/删除或单定义重导出。 |
| monitor合并 | `__init__.py`、`manifest.py`、`api/routes.py`；§3 R-004列明的10个API/Schema/Service/CRUD文件、`models/business_history.py`及对应包`__init__.py`；Core models/monitor.py、collector/realtime链均受保护。 |
| 公共依赖/迁移 | `backend/common/data_keys.py`、`backend/common/error_codes.py`；§6唯一新successor文件。不改common响应/异常平台、Alembic env、database/core基础设施。 |
| 新聚焦验证 | `backend/tests/test_business_module_reintegration.py`、`test_business_module_migration.py`、`test_business_module_permissions.py`、`test_auxiliary_business.py`、`test_monitor_business.py`；`backend/tests_mysql/test_business_module_reintegration.py` 独立真实MySQL入口，禁止依赖共享破坏性conftest。 |
| 排班规则空态小适配 | `frontend-js/src/app/auxiliary/views/shift/index.vue`、`frontend-js/src/app/auxiliary/locales/en-US.json`、`frontend-js/src/app/auxiliary/locales/zh-CN.json`；新增窄回归 `frontend-js/tests/module-registry/shift-rule-empty-state.test.mjs`。仅处理null loader/未配置提示/不可误提交及已有规则回归，不改API facade、其他页面、权限或默认班制。 |
| 既有必要预期 | `backend/tests/test_module_{registry,structure}.py`、`test_openapi_router_tags.py`、`test_core_migration_baseline.py`、`test_celery_retirement.py`、`test_monitor_frontend_permissions.py`、`test_energy_price_{api,service,migration}.py`、`test_projection_control_plane_registration.py`、`test_projection_runtime.py`；仅同步本范围模块/owner/表/路由预期，保持原安全与退役runtime断言。 |
| 稳定说明/DEV事实 | 根`AGENTS.md`、根/backend/app的README英文/中文pair，auxiliary README pair及energy/monitor README pair，`CODE_INDEX.md`；仅同步公共业务owner、价格位置、58表候选/运行门槛；本任务`tasks.md`。迭代状态继续由backend PLAN归属，不批量建空模块任务。 |

表中模块内缩写均相对该行模块根；花括号为有限集合。根/backend PLAN pair与根plans catalog pair
由主协调者机械同步；现有auxiliary PLAN/catalog的旧验收记录保留。Verification在handoff后只写本任务
checklist。其他文件、旧源仓库、既有任务bundle、表列空态适配之外的前端、settings、env/example、auth/permission resolver、
app/router.py、module_registry.py、Projection/runtime、CA、依赖/lock、Docker/CI/打包均不在修改面。

# 9. 两阶段验收，不能只以能启动结案

| AC | 阶段与必需证据 |
| --- | --- |
| AC-001 / R-001..004 | A：公开隔离源码下manifest/package/API/model完整导入和ASGI app组合；依赖无缺失。HR不挂路由但5表Model安全导入，demo仍disabled；Registry内部错误负例仍显式失败。 |
| AC-002 / R-005..006 | A：真实ASGI method/path唯一清单、OpenAPI无重复；价格仅energy owner且三API不变；Core事实guard不变、monitor新key独立、各新增业务guard和401/403/disabled矩阵通过；不改env/grants。 |
| AC-003 / R-002..006 | A：全部有效ErrorCode引用闭合；规范化key兼容；BE002/004全部价格回归含原始小数、时间/DST/派生下界、空值/0、排序、整组覆盖及失败事务；auxiliary/monitor普通GET零写入，mock-off只读。实际SFC回归证明规则null无报错、明确未配置、不显示伪配置/不误提交；已有规则加载/PUT与API失败提示不退化，双语key对称。 |
| AC-004 / R-007 | A：单root/head/history、三旧revision指纹不变；recorder/offline upgrade/downgrade与58表metadata完整签名对照，原14表子集和价格两后继断言保留；无duplicate Table、无额外12个monitor Model、无seed/隐式DDL。 |
| AC-005 / R-008 | A：8个现有descriptor可发现/注册且唯一；原本地business+cursor+audit原子性回归不退化；差异证明无HTTP替换、真实mapping发布或runner启动。 |
| AC-006 / 全范围 | A：公开隔离fixture内完整 `uv run pytest -q -m no_db`、触达Python compileall、上述聚焦/注册/迁移/权限回归、文档新增链接与diff-check通过；前端 `pnpm check:modules`、`pnpm test:modules`、`pnpm build`，合成null fixture中英文空态/禁保存与日夜窄屏浏览器检查通过。原“禁止客户残留”只精确调整为本规格批准的公开集合，不能删除保护断言或缩套件掩盖失败。 |
| AC-007 / R-007 | B：经具体动作授权的可丢弃MySQL8.4.6，分别证明空库base→新head，及旧head带合成价格/核心记录→新head；实际58表签名/外键/约束/索引一致，原16表记录/校验和与价格历史不变；迁移失败/回退演练仅作用于可丢弃副本。 |
| AC-008 / R-001..006 | B：BACKEND_MOCK_ENABLED=False、独立session的真实Service/API读写：每个enabled owner至少一条真实读取和该owner现有写入代表路径；只读equipment/dashboard/monitor由显式合成fixture准备、API读取核对。auxiliary四实体及reports跨StopRecord、plan↔performance/quality关系、价格POST→GET/current/history与同小时并发整组覆盖必测；HR正常组合404，测试显式启用副本方可验证其CRUD，不改源码开关。 |
| AC-009 / 交接 | Development提交精确r1、完整文件/增量diff/命令退出码/阶段限制与资源；fresh-context Verification独立复核A+B并记录verdict/未解阻塞，Human Owner保留最终验收。源码通过不能代替B或空库前端采用兼容证据。 |

A使用任务专属`/private/tmp`副本、公开占位Settings及项目既有uv/lockfile，排除真实.env、日志、导出、
运行数据；Projection/mock/bootstrap关闭。no_db/依赖override明确隔离现有autouse建库/drop/create_all
fixture。此时的“启动”仅指受控应用组合/隔离生命周期证据，不代表当前运行进程已reload或连库成功。

B在A通过后执行，但本r1草案/后续源码范围批准均不自动授权Docker up/down/build、建库/清理、在线
迁移、服务监听或真实业务写入。执行前另提交实例/库/volume/端口、可丢弃声明、起始revision、合成
fixtures、精确命令、回退/清理清单，由Human Owner批准具体动作；不提供或公开秘密连接串。
TESTING=True本身不是隔离证明，SQLite/stub不替代MySQL。真实运行授权未到时可完成A并分阶段交接，
但AC-007/008保持未验证gate，整体不能记qa_passed/owner_accepted或“迁回模块均可用”。

# 10. 风险、待决事项、handoff与历史

主要风险是价格重复owner/回退丢历史、旧权限key扩大授权、空库默认规则行为变化、42表迁移与Model
不一致、把源码descriptor误当现场已发布映射，以及共享dirty被覆盖。以唯一owner、旧16表/三revision
保护、明确空态差异、逐表签名、两阶段隔离和任务增量指纹控制。源码回退只撤本任务增量；实际
downgrade丢新增业务数据，已有数据后不得把downgrade作为默认回退，备份/恢复另行批准。

| 尚待决定/验证 | 当前处理 |
| --- | --- |
| 精确r1范围批准 | 本文件全部是draft；§5 null空态、诊断mock纠偏、monitor-business-read为可审查proposal，须随r1批准，不能推断此前已批准。 |
| 首次真实排班规则初始化 | null兼容已纳入r1候选，尚未实施；首次业务规则由谁/通过何种既有显式配置动作初始化仍待运行采用gate。本批空态可见且禁误提交，不承诺空库可直接创建规则，不通过GET seed或新CRUD平台解决。 |
| MySQL具体运行目标 | B的实例与动作授权尚未提供；不是要求用户现在设计SQL或交出口令，主协调者在A后提交可执行清单。 |
| 客户专属隐含依赖 | 若受影响路径需要未列模型、设备地址/客户资源或新的业务规则，停止该部分，记录具体引用回PM，不以“全迁回”扩范围。 |
| BE003后续 | 基线稳定后其PM重核r2位置/现有GET/表/head及Q-005；本任务不替其作温控粒度/新API批准。 |

排除真实旧数据迁移/价格归并、规则空态之外的前端改造、完整HR启用、reports未挂quality组、旧monitor12模型/HMI、
新的HTTP ingest/机器身份/receipt平台、设备管理或新采集writer、Celery/Redis/Worker、现场CA/PLC、
SMA/DAA/AWfacts/ROADMAP/Tauri、通用规则重构、依赖安装、部署/发布/Git refs或推送。

PM使用aiis、project-governance，仅只读参考backend-arch。Development/Verification必须使用
backend-arch的LAYERS、RESPONSE_CONTRACT、MODULE_REGISTRATION、DATABASE_AND_MIGRATIONS、
DATA_GOVERNANCE、AUTH_SECURITY、OPERATIONS_TESTING；排班空态小适配遵循frontend-ui的FRAMEWORK/
DESIGN及i18n-workflow，沿用现有JS/主题/控件，后端可见错误key兼容也用i18n-workflow；结构/
CODE_INDEX用code-document-indexer。B如实际涉及Docker再加载docker-expert+docker-project-ops；
新增backend/scripts不在当前allowlist，需要新Revision并路由backend-script-tooling。PM不替技术角色执行。

2026-10-14：根据Human Owner创建新修复规格的请求，确认Task ID未冲突后形成ARCH-BE-005 r1 draft。
本轮仅有PM规格/静态事实，不含Development self-check、独立QA、真实schema/runtime验证或最终验收。
下一gate为Human Owner批准精确r1；此后Development创建tasks，handoff后主协调者实际启动fresh-context
Verification创建checklist。角色为contract_only，主会话、bundle与diff审计是必要控制，不宣称ACL或强制路由。
