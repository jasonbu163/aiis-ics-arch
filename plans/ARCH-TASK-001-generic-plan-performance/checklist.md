# ARCH-TASK-001 r3 第六次交接独立验证 · 2026-11-18

Status: qa_passed
Handoff: Human Owner 最终验收。R3-QA-F04 已在本次精确交付复验通过。

**交接身份。** 正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。从仓库根目录执行 `git rev-parse HEAD` 和 `shasum -a 256`，spec 为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`，tasks 为 `0fe87d9bb496196dc9e182d781c410d9ad2fa9b123fa902dbec071d2fc9841dc`，旧 checklist 为 `ad6a213c69522b3bd1df6e33e1bf81c8f0ecb9bbfe6a8c1c6e8435a495d46516`。证据目录 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307` 下 `development-delivery-r3-f04-files.sha256` 的 SHA-256 为 `223220e938ac3a6360658e60a53b96b5474cb71bbafd0ff9470774151df9d8f1`；用 `shasum -a 256 -c` 复算 60/60。与 QA5 的 `development-delivery-r3-shared-page-final-files.sha256` 逐行比较，仅 async_fields.py 和 test_generic_task_flow.py 改变。正式树 git diff --check 退出 0。原清单全文保存在下方。

**本轮新证据。** 正式树使用项目 Python 3.13 与内存 SQLite 验证 HTTP/ASGI。以下 W 为 `/private/tmp/arch-task-001-r2.FeZuND`。

- 根目录运行 `/bin/zsh "$W/f04-repro.sh" backend`，正常和隐藏 use 查询均 409，GET 仍读回原值。历史红例记录的原候选为 409/200，原值不可见；本轮直接重放新候选。脚本 f04-qa-repro.py 的 SHA-256 为 `249465eaa7402218712c29dfd83711ce075eb34cecaba65ac1a5d0c2a9a40cf2`。
- `/bin/zsh "$W/run-r3-time-tests.sh" backend tests/test_generic_task_flow.py tests/test_generic_task_source.py`，50 passed。覆盖正常 use、已停用/无值、隐藏创建引用、两主表和历史批次、更新/状态、未知绑定、真正未用字段释放/重用、旧任务仅 GET、删后旧载荷返回 422、审计异常 503。MySQL 方言三个查询均带 FOR UPDATE。模块 AST/真实 Registry 命令 `/bin/zsh "$W/f04-preflight.sh" backend` 退出 0，两侧历史主表和批次按 task 域表合同查询，未反向导入 plan/performance ORM。禁用 performance 或同时禁用两模块可装配，单独禁用 plan 按原依赖拒绝。
- 下列独立 20 例测试以正式模块和当前 HTTP 路由执行，每例独立内存库。两个模块分别测共享及本地已停用字段，分别在创建、旧单改状态、旧单同值提交、纯读及查询抛错时删除。隐藏 use 后创建绑定及状态更新各返回 409；正常同值 POST 后为 409，纯读后为 200，历史表读异常为 503。前后 GET 完全一致，失败时修订号不变。结果 20/20，退出 0。
- MySQL 8.4.6 实库语义复核使用本机受保护的 3307 配置和只读事务，验证目标身份、单一迁移 head 和 +08:00，通过后用生产代码生成三条 SELECT，仅移除 FOR UPDATE 以保持非锁定读，逐条执行并回滚。计划和实绩均有命中，历史批次无命中，三条均可执行，非数据破坏演练。首次沙盒回环被拒，放行同一本机只读命令后退出 0。真实两种交错写和配置单例锁等待仍以原 3307 证据为准，更新先行 200/409，删除先行 200/422，新增槽占用为零。所有写路径先锁配置单例，随后再取任务/行锁；删除核验、发布和业务 use 各自处于同一事务。此次没有在正在使用的 dev 上重跑并发写入。
- 对旧单，若添加字段后仅发生一次同值 POST，而唯一对应 use 事后被选择性抹去，创建版 use 仍在，且任务值、状态、更新时间均无变化，现有模型无法从持久数据识别这次破坏。正常 POST 的事务台账、迁入历史基线以及存在独立证据时的保守拒绝是本次 verdict 的适用条件。

**完整后端回归。** 在 backend 执行 `/bin/zsh "$W/run-r3-time-tests.sh" . tests/test_generic_task*.py tests/test_{business_integration_storage,plc_facts_v2,acquisition_data_browse,acquisition_source_registry,equipment_observation_r10_flow,equipment_observation_r10,equipment_observation_r8,equipment_temperature_migration,legacy_acquisition_retirement,mapping_migration,business_integration_api,mapping_api}.py`，423 passed、14 skipped、1 条既有 SQLite datetime 适配警告，124.02 秒，退出 0。开发窗口中 r3-f04-backend-tests.log、r3-f04-frontend-tests.log、r3-f04-formal-build.log 的摘要分别为 `939e3050a7771f04d32b0c9b6eb43984009b7ff4b935165d4dfb27594c755244`、`d9acb52f67535544135b333fa5e9425f378077e1f68afd4c8437f347ba74deb4`、`bfd33a6cd16e7285f9210b07c282d01821f9f98e2ed779e23ae65042d70447ce`。

**验收范围。** R2-AC01–11 依照第五次检查矩阵及本轮后端定向回归，涵盖规范化、容量、局部更新、新建、补建、回写、时区、事务、查询、权限及当前字段定义；MySQL 满容量来自早前已记录的验证。R2-AC12 的两个菜单分别访问 plan/shared-fields 和 performance/shared-fields，共用同一页面，列表保留各自本地入口。本轮逐文件一致并核对 manifest，两侧语言、尺寸、非管理员拒绝、列宽和草稿采用 QA5 独立 Chrome 结果，持久副本 qa5-shared-page-browser.json 与原 browser.json 均复算 `5fb905b445e38597da1a96bb7ed44988b5a906dea03611b87af1294fe3299817`。R2-AC13 本轮通过。R2-AC14 使用既有迁移/保护数据记录及本轮隔离链、退役行为回归。R2-AC15 综合采用后端定向回归、QA5 正式前端 92/92、构建及独立浏览器证据。R3-AC01–04 使用精确清单与迁移链、PLC Facts、设备及业务时间守卫的合成回归。R3-AC05–06 对照此前获准的备份、迁移及保护对账；R3-AC07 使用上述正式后端和逐字节不变的前端证据。原有全局权限审计基线失败及历史 skips 详见前轮。

实库与自检输出的 SHA-256 已重新计算。migration-operation.json 为 `6ffcaeb668275a16cea4ee48e1122c61eb56ecdb5827222306c65c4d118e16e7`，dev-protected-data-reconciliation-final.json 为 `4b5988a7c83006d784df558a4937f46e9421ded7eef7afdd52014bde3d46a640`，dev-api-delete-concurrency.json 为 `0c85f3a99bdff064f51642b1472185b176ab04f519a622917aef0cef26067dc3`，backup-validated.json 为 `8615642c7bcdd9289988c7595bababdb635865ec8522d74f8224e00d77f24856`。未做恢复演练、PLC/SMA/CA 实机联调或生产部署。未改 dev 配置、profile、服务或手工验收任务。本轮探针从 stdin 执行，没有新建探针文件或后台进程。W、QA5 浏览器目录和此前构建由协调者确认无其他依赖后回收，实库证据及备份按原保留条件。无本轮 blocker。

**持久证据。** 协调者将 W 中的 8 个脚本与开发日志逐字节复制到 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/qa6-retained/`，复算 8/8 均符合该目录的 `sha256.json`。QA5 的脱敏浏览器输出位于同级 `qa5-shared-page-browser.json`。核对上述证据可直接使用持久副本；命令中的 W 记录当时的执行位置。

<details><summary>独立矩阵和实库只读探针的完整命令（从根目录运行）</summary>

```sh
cd backend && env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests TESTING=true MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 .venv/bin/python -B - <<'PY'
import asyncio,sys
from unittest.mock import patch
sys.path.append('tests')
import test_generic_task_flow as f
async def run(route,group,kind,mode):
    async for h,_,_,_ in f.client.__wrapped__():
        scope={'shared':'shared_sync','plan':'plan_local','performance':'performance_local'}[group]
        if mode!='created': await f.put(h,route,'GTR3-QA6')
        cfg=await f.configure(h,group,f.field(scope,7,'checkold',enabled=False,**({} if group=='plan' else {'performanceOwner':'automated'})))
        if mode=='created': await f.put(h,route,'GTR3-QA6')
        if mode=='changed': await f.put(h,route,'GTR3-QA6',productionStatus='error')
        if mode=='unchanged': assert (await f.put(h,route,'GTR3-QA6'))['outcome']=='unchanged'
        before=await f.get(h,route,'GTR3-QA6')
        old=f.Transactions.execute
        async def changed(self,q):
            if mode=='fault' and 'FROM '+kind+'_main LEFT OUTER JOIN' in str(q): raise RuntimeError('read failed')
            if mode in ('created','changed') and 'FROM task_field_config_uses' in str(q): q=q.where(False)
            return await old(self,q)
        with patch.object(f.Transactions,'execute',changed):
            resp=await h.post(f.CONFIG+'/delete',json=dict(scope=scope,slotNo=7,name='checkold',configRevision=cfg['configRevision']))
        expected=503 if mode=='fault' else 200 if mode=='read' else 409
        assert resp.status_code==expected,(kind,group,mode,resp.status_code)
        assert before==await f.get(h,route,'GTR3-QA6')
        if expected!=200: assert cfg['configRevision']==f.data(await h.get(f.CONFIG,params={'module':kind}))['configRevision']
async def main():
    for route,kind in [(f.PLAN,'plan'),(f.PERF,'performance')]:
        for group in ('shared',kind):
            for mode in ('created','changed','unchanged','read','fault'): await run(route,group,kind,mode)
    print('20/20')
asyncio.run(main())
PY
```

```sh
cd backend && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:/private/tmp/arch-task-001-r2.FeZuND .venv/bin/python -B - <<'PY'
import asyncio
from types import SimpleNamespace
from datetime import datetime
from window_shared import config,read_session,NEW
from app.task.services.async_fields import _verify_subject_history
from sqlalchemy import select,func
from app.task.models.fields import FieldConfigState
with read_session(config(),NEW) as (db,_):
    version=db.execute(select(FieldConfigState.active_version)).scalar_one()
    class Capture:
        async def execute(self,q):
            c=q.compile(dialect=db.dialect,compile_kwargs={'literal_binds':True})
            sql=str(c)
            assert sql.endswith(' FOR UPDATE')
            hit=db.exec_driver_sql(sql.removesuffix(' FOR UPDATE')).first()
            print(sql.split('FROM ')[1].split()[0], 'read_ok', bool(hit))
            return SimpleNamespace(first=lambda:None)
    active=SimpleNamespace(config_version=version,slot_no=1,scope='shared_sync',created_at=datetime(2099,1,1))
    asyncio.run(_verify_subject_history(Capture(),('plan','performance','dispatch'),[active],active))
PY
```

</details>

---


# ARCH-TASK-001 r3 第五次交接独立复验

Status: qa_failed
Handoff: Development 修复 R3-QA-F04 后重新交接。Human Owner 最终验收待后续独立 Verification。

## R3-QA-F04 · 已用字段在使用记录缺失时被删除

规格 R2-12 和 R2-AC13 要求历史使用证据不完整时保守拒绝删除。在正式树的 ASGI 路由、独立内存 SQLite 中，经 API 建立共享字段、写入计划槽值。完整使用证据时，删除返回 409。随后单独让使用记录的 SELECT 返回空，保留实际计划、绑定版本、字段定义及所有槽值。同一删除请求返回 HTTP 200、outcome=deleted、configVersion=3、configRevision="3"。原计划 GET 的 items 从 {"qaUsed":"retained"} 变为 {}。期望 409 task.field_in_use，字段仍可见。测试没有改写数据库使用记录，也未访问 dev。该缺失场景是故障注入，无证据表明 3307 实际丢失记录。

定位于 backend/app/task/services/async_fields.py 的 delete_field。函数核对版本连续性、各版本定义数量、字段身份和 FieldConfigUse。如果实际使用行缺失，它未从仍可查询的任务绑定版本或历史批次识别矛盾，就发布删除后的配置。Development 应覆盖共享与各自本地作用域，保持无引用定义的正常删除。

在 backend 目录以项目 .venv/bin/python -B 从标准输入运行，环境 TESTING=true、MYSQL_HOST=127.0.0.1、MYSQL_PORT=1。以下为可复核运行体。原观察脚本打印实际返回，退出 0；若将预期 409 设为断言，则当前候选失败。

```python
import asyncio
import sys
from unittest.mock import patch

sys.path.append("tests")
import test_generic_task_flow as f

async def verify():
    async for http, _, _, _ in f.client.__wrapped__():
        cfg = await f.configure(http, "shared", f.field(
            "shared_sync", 1, "qaUsed", performanceOwner="order_snapshot"))
        await f.put(http, f.PLAN, "GTR3-QA5-F04", items={"qaUsed": "retained"})
        payload = dict(scope="shared_sync", slotNo=1, name="qaUsed",
                       configRevision=cfg["configRevision"])
        route = f.CONFIG + "/delete"
        print((await http.post(route, json=payload)).status_code)
        execute = f.Transactions.execute

        async def missing_use(self, query):
            if "FROM task_field_config_uses" in str(query):
                query = query.where(False)
            return await execute(self, query)

        with patch.object(f.Transactions, "execute", missing_use):
            result = await http.post(route, json=payload)
            print(result.status_code, result.json()["data"])
            print((await f.get(http, f.PLAN, "GTR3-QA5-F04"))["items"])

asyncio.run(verify())
```

## 输入、环境及复验范围

- 正式未提交工作树 HEAD f7c5608c0e433612b15821a578a7ef3e4f155cdb。shasum -a 256 核对 spec、tasks、开始前 checklist，分别为 9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff、f5440239c494f6399808924be6cc499b7e63ce18b90481a6400159b13a82f794、b138a65826030964ea45fdbe5a97c2d0a1c2997f2f1fececebb1864e58d70690。第五次交接 60 项清单 development-delivery-r3-shared-page-final-files.sha256 的摘要为 ec18f34757a115dc3d5a4e3c61d9c71dd2eabbb710af62e459c02bbe82d5a6ae。由根目录使用 shasum -a 256 -c 校验正式文件。并行工作树另有范围外差异。
- 后端在 backend 运行 /bin/zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh .，参数为 tests/test_generic_task*.py 及 tasks.md 首轮列明的 12 个保护回归模块。项目 Python 3.13，合成占位环境、无 MySQL 连接、pytest no_db。406 passed、14 skipped、1 条已有 SQLite datetime 警告；会话退出 0。跳过项按原任务记录，包括已退役行为、历史基线和显式外部夹具。首次单独探针用 sys.path.insert(0,"tests") 与 tests/app 重名导致导入失败，改为 append 后得到上述 API 观察。
- 前端在 frontend-js 执行 TZ=America/New_York pnpm --config.verify-deps-before-run=false test:modules，92/92 通过。使用两个空非管理员授权数组、mock=false、/api/v1 执行同一 pnpm 的 build --outDir /private/tmp/gtr3-qa5-j81/dist，模块预检及 Vite 构建退出 0，有既有大块提示。单模块装配及显式 grant 下共同拒绝共享页面属 Registry 测试证据。
- 对正式 5190/8000 独立运行 backend/.venv/bin/python -B /private/tmp/gtr3-qa5-j81/run-live-shared-page.py，退出 0。探针复用经复核的只读浏览器脚本，仅更换输出位置；Chrome 157 独立上下文，中英各 1360/390 像素，共 64 次真实 GET、6 次登录、4 次本机拦截的 409，零真实业务写。两入口均读取相同定义，两个列表只显示各自本地管理弹窗，冲突保留草稿、取消丢弃，两个非管理员的菜单均隐藏且两个直链均拒绝。桌面横滚 1206 px，拖宽 190→235，切换保留并恢复 190；窄屏滚动 1940/1912 px，页卡顶部 194、标题 214，位于顶栏底 186 之下。现场保存未执行，共享 API 持久化路径在独立 ASGI/SQLite 中真实发布和读回；指南、路由和共用编辑器均指向对应入口。浏览器已退出，输出 SHA-256 5fb905b445e38597da1a96bb7ed44988b5a906dea03611b87af1294fe3299817。临时产物可在交接后回收。
- R2-AC01 至 AC11 的独立隔离套件覆盖规范化、100+100 槽、局部更新、补建、快照、回写、状态、采集时间、回滚、目标、分页及配置切换。固定 +08:00、精确小数和正负零的历史回归在本轮通过。MySQL 满容量来自历史 r1；并发、真实事务与保护数据对账沿用 tasks.md 所列 3307 切换证据。本轮未重复实库写入。R2-AC12 见浏览器与 Registry。R2-AC13 失败。R2-AC14 依据原迁移记录及本轮链/410 隔离回归，未重复切换。R2-AC15 有后端、OpenAPI、前端构建与真实浏览器证据，整体验收因 AC13 失败。
- R3-AC01 至 AC04 依据精确交付清单、迁移及受保护 revision 的定向测试；R3-AC05、06 对应已记录切换前后证据（migration-operation.json、dev-protected-data-reconciliation-final.json 等），本轮未重跑迁移、实库并发、保护探针或恢复演练。R3-AC07 定向回归及正式构建通过，新增独立 AC13 反例阻止交付。历史基线的权限闭包审计失败仍按原记录。本轮未更改私有配置、服务、PLC 或两个手工任务号。

以下保留第四次交接暂停、前三次 r3 失败及 r1 验证历史。

---

# ARCH-TASK-001 r3 第四次交接 · 独立 Verification 暂停

Status: qa_blocked
Handoff: 协调者及 PM 根据 Human Owner 最新页面要求处理范围和 Revision，待新的精确 Development handoff 后重新开始独立 QA。

Human Owner 在真实页面澄清了导航与命名要求。计划、实绩导航下各需一个“共享字段管理”独立页面入口，共用页面和后端。两张列表的本地入口统一命名“本地字段管理”。本轮正式源码的 TaskPage.vue 在列表操作区打开共享设置弹窗。原 r2 的 R2-11 曾允许同一页面或组件；此处记录 Owner 新澄清及交付即将变更，未判为原规格实现失败。

**已独立核对。** 2026-11-18，在正式工作树使用 shasum -a 256 核对批准 spec 摘要 9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff、第四次 handoff tasks 摘要 632e6d5706050620f8576f7fc907b35acd68ddd4b23adcdfb047a8ab8ab08402、原 checklist 摘要 f09042ae6caf12e6d5a4b6f3651bd2da19e91576fbc1ffb63637fe393dbfd30c，以及 development-delivery-r3-f03-files.sha256 摘要 b32cf52e8e76245adfff149804d480552a199f31909ff67570122bb18df19822。以 Python hashlib 对清单全部 53 项逐项复算，均相符。默认沙箱下 curl 的两个 HTTP 状态输出为 000；获准访问本机后，curl -fsS 实测 8000/openapi.json 和 5190/ 均为 200，退出 0。源码阅读涉及任务数值、时间、HTTP 适配及列表设置入口。

**尚未验完。** 本轮未连接 3307 独立确认 head 或备份及保护数据，未复验 F01、F02、F03 的运行时行为。R2-AC01–15 和 R3-AC01–07 均未完成独立验收。权限审计旧失败、SQLite、MySQL、浏览器和构建结果仍归各自历史轮次。Owner 暂停指令到达时没有在途请求、自有服务或浏览器进程。本轮实际业务写入、字段操作和浏览器交互均为零；空的自有临时目录已回收。原三轮 r3 qa_failed 和 r1 历史全文保留如下。Human Owner 最终验收待后续交接。

---

Task ID: ARCH-TASK-001
Revision: r3
Status: qa_failed
Owner Role: QA / Verification
Handoff: Development 修复 R3-QA-F03，再交独立 Verification。

# r3 第三次独立验证 · 2026-11-18

**R3-QA-F03：等值数字重报推进更新时间。** 正式树 ASGI 入口、内存 SQLite、独立 pytest 探针。在计划本地配置 number 字段 amount，向 /integration/plans/upsert 发送两个 application/json 原始正文：

```json
{"taskNo":"ZERO","items":{"amount":0}}
{"taskNo":"ZERO","items":{"amount":-0.0}}
```

第一份返回 created、amount=0、updatedAt=2026-11-18T17:14:06.317475+08:00。第二份返回 updated、amount=0、updatedAt=2026-11-18T17:14:06.320163+08:00。R2-04 要求相同业务值重发保持时间并返回 unchanged。domain.py 的 encode_value 把带负号的 Decimal 零编码为字符串 -0，其他零编码为 0；读取均得到整数 0，比较 JSON 槽位时却不同。F03 影响 AC02，其他路径使用同一编码函数，尚须复核实绩和共享回写。此次复验没有向真实库写业务或配置。返工应覆盖历史存量的两种零表示。

**交接身份。** shasum -a 256 核对 spec 9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff，tasks 4fb6a10d14cf496d2820f71f8dea2e71706645fa882d8a8fc2aa920d96c03f41，原 checklist 2cf7f94ae1340e3662ed038771eb68bd1b2f12cafb69e03f43510a4e78d23025，f02 清单 eb36d9abbfd7e9622b8cd5ec6944a1c20e2bea4f61eb5f154e041b27c6669158。正式树 shasum -a 256 -c 清单为 53/53，git diff --check 通过。以下原有历史按字节保留。

**本轮实际验证。** 临时窗口 Q=/private/tmp/arch-task001-qa3r3.W0e4y6，保留供 Development/下一轮 QA，之后协调者可清理。开发运行器 W=/private/tmp/arch-task-001-r2.FeZuND。主要结论持久记录于本节。

- backend 下 TESTING=true MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 PYTHONPATH=.:tests PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -s -q -c pytest.ini -p no:cacheprovider $Q/test_equal_zero.py --tb=short，退出 1，1 failed。
- backend 下 /bin/zsh $W/run-r3-time-tests.sh . tests/test_generic_task*.py 加 tasks 首轮所列 12 个回归模块，退出 0，405 passed、14 skipped、1 条 SQLite datetime 弃用提示。fixture 使用无效 MySQL 端口、SQLite/合成依赖。F02 原始 HTTP 字节覆盖计划、实绩、集成和登录人工四个入口，对指定超精度输入整包拒绝、合法值通过，认证与严格元数据测试通过。F01 在夏、冬、当前、偏移、微秒、边界和日期区间通过。F02 本轮没有重新向真实 MySQL 发写请求。
- 同运行器单跑 tests/test_business_module_permissions.py，退出 1，1 passed、1 failed。全局审计断言为 /api/v1/acquisition-data/options、plc_facts、空权限集，和此前基线记录同一路径。审计文件与相应 acquisition_data 目录相对 HEAD 无差异，未见 r3 任务路由触发该失败。
- frontend-js 下 TZ=America/New_York pnpm --config.verify-deps-before-run=false test:modules，退出 0，90/90。此次未重跑构建。
- backend/.venv/bin/python -B $Q/run-live-r3-f01.py 与 $Q/run-live-r3.py 均退出 0。复用已检查的驱动，报告重定向到 Q，以独立真实 Chrome 157 context 登录 5190，仅允许登录与 GET。上海/纽约时区列表同为 1990-07-01 08:00:00，两组各核对三项详情和六条真实读请求。两页在 1360/390px 的标题、筛选、表格顺序正确，可按合成号查询，局部/共享设置及语言切换通过，26 个 API 请求，业务写入 0。列宽拖动持久化本轮未独立实测。
- curl 检查 8000/openapi.json 为 200。backend/.venv/bin/python -B $Q/reconcile.py 退出 0，3307、MySQL 8.4.6、固定 +08、运行 head ae20b4d6f831 及 profile 身份断言通过。只读事务比对迁移后合成前摘要，原计划 2、实绩 2、批次 2、历史引用 6、历史版本 3、历史定义 10、PLC 历史 107、latest 6，逐组 SHA 相同。设备配置当前为 1 组和 2 项。没有操作设备、服务或手动示例。

| 验收项 | 独立证据与剩余限制 |
|---|---|
| R2-AC01 | SQLite 槽位容量及跨组同名回归通过，未重复 MySQL 物理容量试验。 |
| R2-AC02 | F03 失败。超精度、类型、清空和混合包的既有 ASGI 回归通过。 |
| R2-AC03 / 04 | 无计划补建、回填优先级和快照在隔离套件覆盖。未重新实库写入。 |
| R2-AC05 / 06 | 合并、状态回写、独立时间及恢复 running 的隔离回归通过；新增 F03 对共享数值的影响待返工覆盖。 |
| R2-AC07 | 固定偏移、历史时间及查询隔离回归通过；现有历史合成实绩在真实浏览器显示通过。 |
| R2-AC08 | SQLite 回滚和锁查询顺序有测试，本轮无真实 MySQL 故障和交错写重演。 |
| R2-AC09 / 10 | 隔离回归覆盖目标冲突、无 token、权限、分页、示例，真实浏览器覆盖登录查询。 |
| R2-AC11 | 当前定义、使用和展示的隔离测试通过；无本轮实库配置切换。 |
| R2-AC12 | 两页两尺寸、共享和本地设置、双语真实浏览器通过。列宽跨页持久化、冲突不丢草稿仍待完整实测。 |
| R2-AC13 | 槽位删除与使用保护的 SQLite/锁语句测试通过，实库删除竞态未重跑。 |
| R2-AC14 | 独立校验旧记录及 PLC 摘要。迁移/旧接口测试属于隔离回归，未重做切换。 |
| R2-AC15 | 定向后端与前端模块完成；真实写入、事务并发、列宽和正式构建尚待完整验证。 |
| R3-AC01 | 53 项摘要及迁移/守卫定向回归通过；整体 r2 业务因 F03 失败。 |
| R3-AC02 / 03 / 04 | 合成 revision、异步/同步 target 守卫、设备时序及采用证据的既有定向回归通过；仅为合成环境覆盖。 |
| R3-AC05 / 06 | 切换已有 Development 记录。本轮检查活动 profile/head 和上述历史摘要，未独立复演备份恢复、现场和设备写入。 |
| R3-AC07 | 隔离回归、浏览器和读库见上。全局权限审计单列，尚未满足全部验收。 |

**结论：qa_failed。** 先将 F03 返回 Development。修复后须重新交接精确源文件清单，复验业务值等同和时间语义，并完成仍缺的真库/浏览器验收。Human Owner 最终验收待独立 QA 通过后决定。

---

Task ID: ARCH-TASK-001
Revision: r3
Status: qa_failed
Owner Role: QA / Verification
Handoff: Development 修复 R3-QA-F02 后重新交付，供 fresh Verification 复验。

# r3 第二次独立验证 · 2026-11-18

正式树 HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。规格 SHA-256 为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`，第二次 tasks 为 `72e9e1cab9b65f0f9866d7361c9415645acd2ca935ef135cf823bbfa262e8931`，原 checklist 为 `14085a57b6f556343e954d610f9f7c7e88a64a743944ddb829aa977127607bf2`。本节以下保留其完整原文。正式树执行 `shasum -a 256 -c backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-f01-files.sha256`，53/53 一致，清单 SHA 为 `e35290177b913b9327096305461a5e18ac5f119dfac059d2ecae517726e849ee`。

## R3-QA-F02 · 超精度 JSON 数值获准写入

R2-01、R2-AC02 要求 number 最多四位小数，超限须整包拒绝。正式 8000 的 `POST /api/v1/integration/plans/upsert`，无 Bearer，Content-Type 为 application/json。使用 `httpx.post(..., content=body)` 发送以下原始文本，数字以文本拼入，客户端未做浮点转换。

```json
{"taskNo":"GTR3-QA-9E05CCD4","remark":"QA-precision","items":{"gtr3C9EF6AActual":9999999999.0001001}}
```

复用既有启用的共享 number 字段，slot 90、isNullable 和 syncEnabled 为 true，实绩归属 automated。请求前按同号 GET 验证该字段为 null，备注为 QA-retained。预期 HTTP 422 且二者保持。实际 HTTP 200，再 GET 返回 9999999999.0001 和 QA-precision。原始 7 位小数被舍入并保存，混合包中的另一字段也已写入。正常 HTTP 复现，未直接写数据库。应用层对已解析的数值执行 `Decimal(str(value))`；计划与实绩调用同一 item_patch / encode_value。此次实库失败复现在计划入口，实绩入口需在返工回归中单独覆盖。

独立内存 HTTP 复现补充：正式 backend 下执行 `zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh . -o asyncio_mode=auto --import-mode=prepend -o 'pythonpath=. tests' -s /private/tmp/arch-task-r3-qa2/test_precision_extra.py`，两项缺陷复现断言通过，退出 0。计划与实绩的正常路由均对原文 9999999999.0001001 和 1e-400 返回 200，同属 F02；两端均接受 9999999999，拒绝 10000000000、true、字符串 "123" 及 1.00001（422）。临时测试位于项目外触发两条 pytest 标记注册警告。此检查仅使用 SQLite 内存库。

## 本轮命令与覆盖

- `backend/.venv/bin/python -B /private/tmp/arch-task-r3-qa2/probe.py` 退出 1，最后断言为上述 422/原备注。失败前已通过 F01 的三条正常 HTTP 输入、MySQL 8.4.6 的 3307 只读事务逐项核对与当前 head 身份守卫。1990 夏 UTC、冬 UTC 与夏 -04:00 分别保存并返回 08:00:00、08:00:00 和 08:30:00.123456，均 +08:00。无计划建实绩、补建计划继承 running、实绩 unchanged 时修复计划 error、completed 再 running、并发分别更新备注和共享值、显式 null 同步皆通过。仅上述一条 QA 号两表留存。
- 正式 backend 中执行 `zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh . tests/test_generic_task*.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_acquisition_source_registry.py tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r8.py tests/test_equipment_temperature_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_business_integration_api.py tests/test_mapping_api.py tests/test_business_module_permissions.py`，401 passed、14 skipped、1 failed，退出 1。工具仅设置隔离 fixture、127.0.0.1:1、TESTING=true、no_db、关闭缓存；SQLite 时间适配器有一条弃用提示。F01 当前时间、精度、存储上下界和两个列表筛选回归通过。唯一失败是权限闭包断言 `('/api/v1/acquisition-data/options', 'plc_facts', set())`，与交接中登记的基线一致，未证实它是本次 r3 变更引入或实际匿名访问成功。未将整组计为通过。
- 正式 frontend-js 执行 `TZ=America/New_York pnpm --config.verify-deps-before-run=false test:modules`，90 passed、0 skipped；同一 pnpm 的 `build --outDir /private/tmp/arch-task-r3-qa2/dist` 成功，保留 Vite 大块警告，均退出 0。
- `backend/.venv/bin/python -B /private/tmp/arch-task-r3-qa2/run-live-r3-f01.py` 与同目录 `run-live-r3.py` 各退出 0。真实 Chrome 157 的上海与纽约两上下文均在实绩列表读到 1990-07-01 08:00:00，详情三个值正确。计划/实绩分别用 1360 和 390 宽度检查三段布局、真实筛选、共享/本地字段与双语入口；26 次实际 API 请求，两个独立登录均 200，浏览器业务写入 0。

## 验收范围与下一次交接

R2-AC02 因 F02 失败。R2-AC03/05/06/07/08 的上述子场景获实库证据，R2-AC12 部分获浏览器证据。定向集覆盖 R2-AC01–15 的部分路径及 R3 的迁移和三个兼容守卫；本轮 100 槽是 SQLite 功能结果，r1 的 MySQL 物理满槽属于历史。R2-AC01、03–15 及 R3-AC01–07 均未在本轮逐项完整签收。真实 MySQL 两表间故障回滚、删除竞态、全量列宽交互、全部保护对象与备份逐项独立对账仍须复核。已知失败后依协调者指示停止业务写入并交 Development。保留预留手工订单、既有两计划/实绩/批次、并行设备配置和 QA 合成记录；本轮没执行迁移、恢复、清理或 PLC 操作。临时目录及日志供返工复验对照，复验结束后由协调者回收。Human Owner 最终验收待后续交接。

---

Task ID: ARCH-TASK-001
Revision: r3
Status: qa_failed
Owner Role: QA / Verification
Handoff: Development 修复 R3-QA-F01 后重新交接，重新执行 fresh Verification。

# r3 首次独立验证

2026-11-18，正式工作树 HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。对规格、Development 交接、原 checklist 和候选清单执行 `shasum -a 256`，退出 0。摘要依次为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`、`15e871add6ee71b17c34cdbc3d1abb5162a182bae9d54f3c9aa27fbde395d605`、`673a6abe5aaae4533be6cf4a43583ed7ac1762a54ce0c05b0aa4f56f65095ae1`、`71a4835b7c6998f031ba38a55d1d7fdfc1636e603f6fce0c773821c6ad047d3c`。正式树根运行 `set -o pipefail; shasum -a 256 -c /private/tmp/arch-task-001-r2.FeZuND/candidate-inventory.sha256 | rg -c ': OK$'`，退出 0，53/53 相符。

## R3-QA-F01 · 合法时间未按固定 +08:00 保存和输出

R2-03 与 R2-AC07 要求有偏移的输入按项目东八区保存并输出 `+08:00`。正式后端接受 `1990-07-01T00:00:00Z`。期望入库前墙钟值为 `08:00:00`，输出 `1990-07-01T08:00:00+08:00`。实际入库前为 `09:00:00`，输出 `1990-07-01T09:00:00+09:00`。原因是 `backend/app/task/domain.py` 第 8、39、51–52 行使用地区的历史夏令时偏移。实绩服务的 observedAt、startedAt、completedAt，以及任务列表时间边界，共用这一转换。未对实际数据库作写入推断。

正式 `backend/` 内运行以下无数据库复现，断言退出 **1**。

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -c "from app.performance.schemas.workflow import PerformanceUpsert; from app.task.domain import local_time,wire_time; v=PerformanceUpsert(taskNo='GTR3-QA-TIME',observedAt='1990-07-01T00:00:00Z').observedAt; dt=local_time(v); print('stored=',dt,'wire=',wire_time(dt)); assert wire_time(dt)=='1990-07-01T08:00:00+08:00'"
```

另用相同函数分别代入 1990-01-01、1990-07-01、2026-07-01 三个 UTC 零点，退出 0，输出小时和偏移依次为 08/+08、09/+09、08/+08。近期日期测试无法发现该缺陷。

**判定与范围。** R2-AC07 失败，整份 r3 返回 Development。R3-AC01 只完成候选文件摘要检查。R2-AC01–06、08–15 和 R3-AC01–07 的完整验收留待重新交接。此轮未执行实库 HTTP 写入、浏览器操作、数据库测试、迁移、服务或配置变更，未生成或删除任何测试任务、字段、设备配置。两条预留手工任务不受影响。本轮没有独立验证全槽 MySQL、备份恢复或采集角色审计。下一轮需在重新交接的正式树核对全部条目，并检查历史偏移输入、普通日期及时间筛选等价性。Human Owner 最终验收仍待后续交接。

---

## 历史记录 · r1 原文

Task ID: ARCH-TASK-001
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA4 通过 r1 第四次精确交接的字段设置、使用说明及相关前端复验，结果交 Human Owner 最终验收。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Acceptance Chain Reference: spec.md 第 9、10 节及 Development Lifecycle Workflow

# QA1 独立验证

2026-11-11 Asia/Shanghai。Verification 以 fresh context 接收精确 r1 handoff，独立读取根契约、作用域文档、角色 TOML、canonical workflow、任务 bundle、正式实现、候选 diff 和自检输出。使用 `project-governance`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 核对交付，使用隔离 Playwright Chrome 实测页面。

正式交付为 HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 上的未提交工作树。复算规格 SHA-256 为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`，交接记录为 `c838151c211e1a5b5dfb9705180e3c26210f706c78735f8ba108913038e943a9`。复算候选 manifest `3c0f74dc50845551daec07ad8f0958ec13a3324edf02b9dc3f392ea1f0200ba5`、patch `90a8aff9863c6bfef9571c33ac0b49e5dc84fb6e00fe721f48d08fff1b640cf6`。101 个实施路径与冻结清单、`tasks.md` 逐项 SHA-256 一致，范围外差异 0。反向 patch 仅以 `--check` 验证可匹配正式源码。工作树内另有其他任务的既存变更。 [批准规格](spec.md) · [Development handoff](tasks.md#developer_handoff--arch-task-001-r1) · [冻结 manifest](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/candidate-digests.json) · [冻结 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/approved-source-candidate.patch)

## 验收矩阵

| 条目 | QA1 结果 | 独立证据 |
| --- | --- | --- |
| AC01 迁移和模型 | 通过 | 对照获批的一次实际迁移 journal、退出 0、前驱 `4e6a8b0d2f14` 与新 head `5f7a9c1e3b25`。在同一 dev 只读事务复核 MySQL 8.4.6、3307、服务器身份摘要、上海偏移 +28800 秒与唯一 head。迁移前 19 张旧表皆空，21 个组内 FK、组外 0。6 张新表及 50 张保留表当前 DDL 共 56 项对账一致。用 MySQL 方言核对六个 ORM 表体及六条显式索引与迁移定义相符，旧表退出模型注册，独立质量模型保留。迁移前后 11 个保护表数据摘要、13 个行数一致。当前重查 9 个数据摘要仍一致，其余 2 个采集表含已批准的唯一合成样本。 |
| AC02 JSON 容量与并发 | 通过 | 两张主表各通过 SQL 默认空对象、两个 JSON 列各 100 值和 255 个四字节字符的往返。两个列各提交数组和 101 项对象，合计八次由 MySQL CHECK 拒绝，错误 3819。探针事务回滚后两表均 0 行。HTTP 拒绝非法字段和伪布尔，允许可空人工槽清空。两会话并发成功，保留自动速度 40 和人工 `false`。 |
| AC03 计划更新 | 通过 | 先建 B 后建 A。规范化重发为同一 ID、同创建与更新时间。部分更新只改订单号，重复不推进时间。无效字段、操作员写计划、写反馈槽以及领取后改订单分别拒绝，核对已存值和时间。 |
| AC04 领取 | 通过 | 两个独立请求并发，A 优先，仅一个 `claimed`，另一为 `target_busy`。同请求重试保留批次和冻结订单参数。已登记的第二目标和第二执行者复用同 ID 均为 409。空队列 `no_task`。同优先级验证先建先领，源码确认 SQL 最后以 ID 升序处理相同创建时间。 |
| AC05 批次和人工动作 | 通过 | A/B 回执使用各自原批次和序号 41/42。确认重复保持第一次时间且生产仍未上报，错序及旧批次 409。异常继续占用，主管核验后退回暂停，普通保存仍暂停，保存并恢复后领到新批次和更新后的冻结值。并发同一人工动作分别为 `applied` 与 `duplicate`，改原请求内容为 409。取消和核验动作证据逐项读回。 |
| AC06 角色与集成 | 通过 | 三类账号在临时 grants 下访问两列表和配置。未登录 401，8000 无相应 grants 的主管和操作员 403。独立进程分别只授 `plan`、只授 `performance`，补建均 403。操作员可写人工实绩，无法写计划、补建、读核验详情或保存配置。主管无法保存配置。未登记 MES、SMA 和 8000 关闭的三个集成查询拒绝。登记来源的合成集成请求免前端 token。混合越权包拒绝后原值和时间一致。 |
| AC07 实绩回写与原子性 | 通过 | A 12/11/重复 12/冲突 12 后先处理 B1，再补 A13。A 反馈 300→1200，目标保持 1200、速度 0、人工 `true`。B 反馈保持 50、人工 `false`。A14 为 `already_completed`，核对忽略报告前后全量详情和时间。独立 18001 注入故障发生在 MySQL 已执行 `performance_main` 第一条 DML 之后，响应 503 `task.unavailable`。S0-B 两侧详情、序号及更新时间完全一致，正常 18000 原包重试后才由序号 2/长度 60 更新为 3/61。 |
| AC08 无计划补建 | 通过 | S0-B/S1-B 使用不同 RUN。各先上报无计划、快照订单空，普通建计划 409。默认关闭与显式开启回填分别得到空反馈和 50，均为 `not_required`、绑定 v3 并保留 `running`。补建重试同一 ID，订单锁定、备注可编辑、无待领任务。序号 2 各回写 60，实绩仍只有原反馈槽。 |
| AC09 配置修订 | **失败，QA-F01** | 显示改名 v3/rev3→v3/rev4，两端共享；停用 v4/rev5 后旧 v3 继续回写，新 v4 拒绝停用槽；原槽恢复 v5/rev6。改已占用槽位及复用历史键被拒。过期请求的 HTTP 409 状态正确，跨业务版本的错误键与规格不符。 |
| AC10 列表和浏览器 | **失败，QA-F02、QA-F03** | 独立 Chrome 的三角色实际登录、默认页、详情、配置、英文、人工表单提交和权限均通过。浏览器置于纽约时区仍显示上海秒级时间。筛选、草稿、列宽刷新恢复和重置通过，实测 150→210→210 像素。API 分页次序及正常精确筛选通过。列表 API 接受无显式时区的数字字符串，且带尾随空格的目标键能命中同一记录。 |
| AC11 切换回归 | 通过 | 正常 8000 和 18000 的 16 条通用任务路径及引用 schema 与合同逐项一致。23 个保护方法均仍注册，旧入口族退出，六次旧路由直调为预期 404/405。独立质量 GET 200。既有合成 DAA 样本 seq 1 原包重放 200 `duplicate`，改内容 409，operator 可读最新 3 点和历史 1 条及详情，两个采集页面均发实际 HTTP 200。正常 8000 排除合成范围并读回原有 2 点。设备和监控的四条保护集成路径仍在，采用与写入保持既有关闭范围。 |
| AC12 检查与证据 | 已执行，产品判定见失败项 | 模块、模型、源码编译、定向单元、前端模块检查及构建均通过。独立 HTTP、MySQL、浏览器和一次事务中断证据已固化。复核迁移 journal、保护性前置核对与原空表恢复顺序，恢复步骤仅审阅。 |

## QA-F01 过期配置错误键

AC09 和规格 §6 要求管理员过期配置保存返回 `409 task.config_revision_conflict`。管理员在 v3/rev3 取得配置，另一提交先修改标签至 v3/rev4，再发布停用共享 03 的 v4/rev5。重放以下首次编辑请求。

```http
PUT /api/v1/task-field-configs
Content-Type: application/json

{"module":"plan","fieldConfigVersion":3,"configRevision":"3","changes":[{"scope":"shared_sync","slotNo":3,"labels":{"zh-CN":"合成生产米数","en-US":"QA metres produced"}}]}
```

实际为 HTTP 409、`code:409`、`data:null`、`errorCode:"task.field_version_conflict"`。同请求在 v3/rev4 时正确返回 `task.config_revision_conflict`。保存入口先比较业务版本，在比较管理员修订号前返回另一错误。请按规格复验两种过期条件。 [配置 Service](../../backend/app/task/services/async_fields.py#L104) · [HTTP 证据](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-http.json)

## QA-F02 创建时间筛选接受未带时区的数字字符串

AC10 和规格 §6 的时间参数要求显式携带时区，实际注册 OpenAPI 为 `date-time`。在正常验收 API 对 `GET /api/v1/plans` 与 `GET /api/v1/performances` 发送下表请求。均携带相同管理员 token 和 `taskNo=GT1-QA92A69E81-A`。请复验两模块的两个时间参数保持同一边界。

| 参数值 | 两模块实际结果 |
| --- | --- |
| `createdFrom=2026-11-11T15:19:58.000000+08:00` | 200，`total=1`，加号经 URL 编码 |
| `createdFrom=2026-11-11T07:19:58.000000Z` | 200，`total=1` |
| `createdFrom=1794381599` 或 `createdTo=1794381599` | 均 200，分别 `total=0` 和 `total=1` |
| `createdFrom=2026-11-11T15:19:59` 或同值 `createdTo` | 均 422 `task.invalid_request` |

路由先把原始 query 交给 datetime coercion，后续上海转换只看到已解析的日期。补充观察为带 `+08:00` 的七位小数秒 `2026-11-11T15:19:59.1234567+08:00` 也返回 200，结果与六位 `.123456` 相同。规格规定保留最多六位，本项 verdict 依据无显式时区的数字输入。 [计划列表路由](../../backend/app/plan/api/routes.py#L17) · [实绩列表路由](../../backend/app/performance/api/routes.py#L17) · [时间探针](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-time-filters.json) · [合法时区对照](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-filter-controls.json)

## QA-F03 列表目标键尾随空格仍匹配

AC10 及规格 R03/R04/R08 要求有效目标键、按原样精确匹配。在上述两条 GET 使用同一合成任务号，`targetKey=LINE-01` 与 `targetKey=LINE-01%20` 均返回 HTTP 200、`total=1`。小写 `line-01` 为 200、`total=0`。实际 schema 为 `ascii_bin`，列表将原始输入直接用于 SQL 等值查询，未应用任务目标标识校验。请复验尾空格不能命中记录。 [计划过滤](../../backend/app/plan/services/async_workflow.py#L170) · [实绩过滤](../../backend/app/performance/services/async_workflow.py#L48) · [目标键对照](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-filter-controls.json)

## 命令与环境

- macOS arm64，Python 3.13.3（项目 `backend/.venv`）、uv 0.7.8、Node v22.19.0、pnpm 11.11.0、独立 Chrome 157.0.8103.39。正式进程使用 8000/5190，合成验收使用回环 18000/15190。短期凭据仅进程内使用，QA 证据不保存凭据。Playwright CLI 离线缓存缺包，退出 1，复用本机已安装的 Playwright 模块驱动独立 Chrome，未访问共享浏览器。
- 以 `TESTING=True` 和合成 DB 端口 1 运行 `.venv/bin/python -B -m app.module_preflight --project-root . --check-only`、`.venv/bin/alembic heads`，退出 0。用 Python `compile()` 编译 60 个候选 Python 文件，MySQL 方言编译比较六张模型表及索引，退出 0。校对 234 个本地相对链接目标，未缺失。 `git diff --check` 与 `git apply --reverse --check <冻结 patch>` 退出 0。
- 同一无 DB 环境执行 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --basetemp=<QA 临时路径>/pytest-fixtures tests/test_generic_task_source.py tests/test_business_module_permissions.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_openapi_router_tags.py`，退出 0，124 passed、10 skipped。重跑显式提供独立 `/private/tmp` basetemp 及已保存的 ARCH-ACQ-002 历史公开 fixture、示例和 Git 根。两次早期结果分别为 122/10/2 和 123/10/1，失败是历史 runner 要求专用基目录及 C2 历史源码未显式配置。跳过项和 Development 记录的历史 QA3 私有导入规则冲突仍属其原历史验证面，本轮未宣称全量回归通过。
- `pnpm check:modules`、`pnpm test:modules`、`pnpm build --outDir <QA 临时目录>` 均退出 0。57 个模块测试通过，构建有 Vite 大 chunk 提示。使用两组空 grants、mock 关闭和本机 API 相对路径的构建配置。
- 在正式 backend 工作目录运行项目 `.venv/bin/python -B` 调用 QA 临时脚本 `workflow_probe.py`、`db_probe.py`、`fault_probe.py`、`run_browser.py`、`regression_probe.py`。主 HTTP 探针实际 153 请求并以 1 退出，对应 QA-F01。DB、故障、浏览器、回归均退出 0。浏览器记录 49 个 API 响应，旧路由及采集回归另记录 16 次 HTTP。两个补充只读探针合计 26 次 GET，见 QA-F02、QA-F03。DB 读证据归一化 `SHOW CREATE TABLE` 的自增计数后比较，保留结构检查。运行时验证无重新迁移，故障注入无真实 PLC 或网络断连。
- 证据保存在本机 ignored 目录 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/`。迁移 journal SHA-256 `ae208eb864fbc09a12d81646907d14775dd18e1783991279461643bf0d2d39b7` 已与操作记录核对。 [实际切换](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/operation.json) · [迁移 journal](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/alembic-upgrade.log) · [MySQL 对账和容量](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-db.json) · [事务及缺授予](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-transaction.json) · [浏览器](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-browser.json) · [受保护路由和采集](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-regressions.json)

## 合成资源与交接

QA1 合成任务号为 `GT1-QA92A69E81-A`、`GT1-QA92A69E81-B`、`GT1-QA92A69E81S0-B`、`GT1-QA92A69E81S1-B`、`GT1-QA92A69E81X-A`、`GT1-QA92A69E81X-B`、`GT1-QA92A69E81N-A`。对应计划 7、实绩 5、批次 4、人工动作 4。字段配置从空 v1/rev1 开始，最终 v5/rev6，v2/v3/v4/v5 分别含 4/6/6/6 定义。故障重试后 S0-B 为序号 3、长度 61。浏览器仅在 B 写入 QA 备注，管理员保存为无变化。回滚探针 `GT1-QA92A69E81CAP-A` 确认 0 行。仅重放原 DAA 合成样本 `GT1-DEVFB8B5B-SAMPLE`、序号 1，历史 ID `5`，未创建新样本。

独立 Chrome 上下文、浏览器和两轮 18001 进程均已停止。QA 私有脚本和临时构建在 `/private/tmp/arch-task-001-r1-qa.L5elEI` 与 `/private/tmp/arch-task-001-r1-qa-build.pReIol`。协调者按已批准范围保留 QA1 合成记录和临时验收进程供返工复现，并在复验所需证据持久化后负责统一停写和精确清理。清理前需核对任务集合、字段版本及已登记采集身份。切换恢复继续依赖协调者保留的私有旧表 DDL、依赖顺序及配置备份。

QA1 verdict 为 **`qa_failed`**。QA-F01、QA-F02、QA-F03 为当前正式交付的可复现偏差，交协调者转回 Development。无独立环境 blocker。QA1 对受控现有 dev 的结果留给 Human Owner 最终验收。真实设备、DAA/SMA/CA/FF 联调、生产和长稳运行无本轮实证。Verification 仓库唯一写入为本 checklist。

## QA2 独立验证

2026-11-11 Asia/Shanghai。fresh-context Verification 独立核对根和相关模块契约、角色 TOML、canonical workflow、完整任务 bundle、正式源码、两次交接差异和可用测试证据。复验使用 `project-governance` 和 `backend-arch`，覆盖 r1 第二次交接的 API 返工、受保护入口、当前 schema 与合成数据。QA1 已通过且交付未变的浏览器及业务闭环证据继续有效。

正式工作树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。复算获批 `spec.md` SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`、第二次交接 `tasks.md` SHA-256 `15d46e1f79f8688be601f746886e8367a85fac03152cbb9372bad3120992a60f`、更新前 QA1 checklist SHA-256 `a9e72c9e907c99e068b69301913481d5a5ff4889450d19b4587e8173abd18772`。QA1 正文自 `# QA1 独立验证` 起原字节 SHA-256 `5e18a63ce3610eec9645a91e58acf8ba67b6b85cd0a5a8f9d60fa2a0228d4823`，原文和历史 verdict 保留。

独立比对两次 manifest、累积 patch、10 份首轮源文件和当前正式工作树。101 个路径集合和正式文件摘要全部匹配，10 个后端文件有变化、91 个摘要不变。变化限列表参数及精确匹配、集成时间参数、配置修订冲突、manifest 导出及定向回归。第二次 manifest SHA-256 `5c8b9cda15bbca659100679abc01dc8819fd3b94e1fcd42e9b82215a534170c3`，patch SHA-256 `65814e55dc9d09549c15edd7861be14be8dce51030b2d8b4e077d537a321d96e`。 [第二次交接](tasks.md#第二次-developer_handoff--arch-task-001-r1) · [正式源码摘要](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source-digests.json) · [累积 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source.patch)

### 验收复核

| 验收项 | QA2 结论 | 证据 |
| --- | --- | --- |
| AC01 迁移与模型 | 通过 | 既有 `127.0.0.1:3307` 的只读事务确认服务器身份摘要、MySQL 8.4.6、上海时钟偏移 28800 秒、唯一已应用 `5f7a9c1e3b25`。读取六张任务表及 50 张保留表 `SHOW CREATE TABLE`，归一化自增计数后均与已核对的迁移后证据一致。源码 preflight 和 Alembic heads 通过。迁移执行证据沿用 QA1。 |
| AC02–AC08 | 通过 | 沿用 QA1 的容量及并发、计划更新、领取和批次动作、角色、实绩事务、两种补建路径证据。本轮重放 A 的真实回执与最终快照验证调整后的 API 仍按原时刻判定幂等，已完成后的序号 14 继续 `already_completed`。正常入口拒绝无授予人员和关闭的集成查询。 |
| AC09 配置修订 | 通过，QA-F01 关闭 | 计划和实绩管理员入口分别实测四组 `fieldConfigVersion`/`configRevision`。`3/"3"`、`4/"5"`、`5/"5"` 均 HTTP 409 `task.config_revision_conflict`，`4/"6"` 为 409 `task.field_version_conflict`。当前 `5/"6"` 空修改均 200。两页当前和 v3 配置完整 `data` 复核前后一致。QA1 的仅展示改名、业务发布、历史回写、恢复和冲突键证据保留。 |
| AC10 列表与浏览器 | 通过，QA-F02、QA-F03 关闭 | 两个列表四个时间参数的正负 epoch、无时区、七位小数、非法时区和尾随垃圾共 28 项均为 422 `task.invalid_request`。按 A 两侧实际 `createdAt` 测试 `+08:00` 和等价 `Z`，共 16 项，逐微秒核对起点含、终点不含。`LINE-01` 返回 A，`line-01` 为 200 空集，尾随空格、前导空格、控制字符、全角、空和超长共 14 项为 422。登录、默认页、筛选、角色、双语、列宽及草稿继续引用 QA1 的真实浏览器证据。Human Owner 后来提出的共用列表分段和时间提示位置由后续交接核验。 |
| AC11 切换回归 | 通过 | 正常 `8000` 及测试 `18000` 的运行 OpenAPI 均 HTTP 200，16 路径和 12 个引用 schema 与发布候选一致，原 23 个保护方法均在。正常质量和采集最新列表读取 200，三个退役入口直调 404，三个正常关闭的任务集成查询 403。已通过的采集样本重放、采集历史和浏览器回归沿用 QA1。 |
| AC12 检查与证据 | 通过 | 正式后端定向无库测试 130 passed、10 skipped。返工路径编译、模块 preflight、源码唯一 head、反向 patch 与空白检查均通过。实测 HTTP 和 MySQL 结果见本节。前端构建和恢复步骤保留 QA1 证据。 |

对模拟 CA/FF 回执 `ackObservedAt` 和 SMA `observedAt`、`startedAt`、`completedAt` 的 48 次非法字段探针均 HTTP 422 `task.invalid_request`。请求体探针覆盖 JSON 数字和字符串 epoch、缺时区、过精度及非法偏移。原 A 回执与序号 13 快照分别用 `+08:00`、等价 `Z` 重放，四次 HTTP 200 `duplicate`。在原 A 已完成的前提下，两种时区写法附显式 `startedAt` 重放序号 14，均 HTTP 200 `already_completed`。PLC 首次接收时间、实绩采样时间、序号、业务值、更新时间及四份字段配置的完整响应 `data` 均保持。A 的计划目标和反馈均为 1200、实绩速度 0、人工结果 `true`、序号 13。B 反馈 50、速度 40、人工结果 `false`、序号 3。MySQL 只读再次核对两单槽位文本以及 QA1 合成计数 7 计划、5 实绩、4 批次、4 动作。当前配置 v5/rev6，定义版本 v2/v3/v4/v5 分别为 4/6/6/6 条。

### 命令、限制与交接

- macOS 15.7.7 arm64，Python 3.13.3，uv 0.7.8。项目 `backend/.venv`，合成 API `18000`，正常 API `8000`，现有 dev MySQL `3307`。初次默认沙盒直连 loopback 被拒绝，经本机验证权限执行。初次 HTTP 探针把既有质量入口的信封套用任务接口 `timestamp` 断言，退出 1，收窄至任务入口后完整重跑退出 0。QA2 探针不改业务记录、配置或采集事实，不执行迁移，凭据不进入输出和任务文档。
- 正式 `backend/` 下，设置 `TESTING=True MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 PYTHONDONTWRITEBYTECODE=1`，执行 `.venv/bin/python -B -m app.module_preflight --project-root . --check-only` 与 `.venv/bin/python -B -m alembic heads`，均退出 0。`git diff --check`、`git apply --reverse --check backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source.patch`、10 个返工 Python 文件的 `compile()` 与文本行尾检查均退出 0。
- 同一无 DB 环境使用 ARCH-ACQ-002 历史公开 backend、同源夹具目录和正式 `ARCH_BE005_REPOSITORY`，运行 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --basetemp=/private/tmp/arch-task-001-r1-qa2.ArBQRb/pytest tests/test_generic_task_source.py tests/test_business_module_permissions.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_openapi_router_tags.py --tb=short`，退出 0，130 passed、10 skipped，40.13 秒。全量回归和原历史 QA3 私有导入限制仍保留首次交接记录的边界。
- 正式 `backend/` 下分别执行 `.venv/bin/python -B /private/tmp/arch-task-001-r1-qa2.ArBQRb/http_recheck.py` 与 `.venv/bin/python -B /private/tmp/arch-task-001-r1-qa2.ArBQRb/schema_read.py`。前者独立实际 HTTP 166 次，56 次 200、8 次 409、90 次 422、2 次 401、7 次 403、3 次 404，见上方分项。后者 `SET TRANSACTION READ ONLY` 后执行版本、表 DDL 和合成标记的查询并回滚，退出 0。辅助脚本和脱敏请求摘要在该任务临时目录，验收结论及必要结果已固化在本清单。正式验收进程、夹具和独立证据由协调者按最终复核和清理安排接续。

QA2 对精确 r1 第二次交接的 verdict 为 **`qa_passed`**。QA-F01、QA-F02、QA-F03 已关闭，无 blocker。验收结果交 Human Owner。后续页面布局反馈仍需对应交接复核，最终验收待 Human Owner 决定。现场设备、DAA/SMA/CA/FF 原生联调、生产和长稳运行仍在本轮证据范围之外。Verification 在仓库中只更新本清单。

## QA3 独立验证

2026-11-11 Asia/Shanghai。Verification 以 fresh context 独立读取根契约、前端作用域文档、角色 TOML、canonical workflow、完整任务 bundle、正式源码、两次交接差异及 Development 测试输出。使用 `project-governance`、`frontend-ui`、`i18n-workflow`。本轮复验 r1 第三次交接的 AC10 共用列表布局及相关 AC12 前端检查。其他标准沿用 QA1 和 QA2 证据。

正式源码工作树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，交付范围未提交。复算 `spec.md` SHA-256 为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`，第三次交接 `tasks.md` 为 `e32b4495588b9af67917b6b0933c5eaec17aec1024f686d0fd571e9172ba8058`，更新前 QA2 checklist 为 `d90e366168a618bf11dd1e00ebb93598f8dfde8fffe269878ab066e3d7a58b06`。QA1 和 QA2 正文自 `# QA1 独立验证` 起的原字节 SHA-256 为 `47bb517a31e3546bbd938997c18b8662da27faa27b7ca030477111668d0f84df`，本次原样保留。

第三次 manifest SHA-256 为 `0c7bf1422c1e3638581af87ac1184bb7adba9a543dd01224b8ad3fc59f1a94e1`，累积 patch 为 `19703fb48d7df6b18e610b4d3e01240ba2b690bd103933460b549859235055da`。正式树与 manifest 101/101 路径摘要一致，路径集合与第二次交接相同，唯一变化为 `TaskPage.vue`，当前 SHA-256 `a7e6f0d63893190efa45af8bb1ceaa34764682e24ddad8dfbd6906d37416c748`。从两个累积 patch 重建该 SFC 对比，差异为标题帮助、筛选和分页布局及壳层留白。两个路由的入口继续共用该组件。`git apply --reverse --check` 和 `git diff --check` 均退出 0。 [第三次交接](tasks.md#第三次-developer_handoff--arch-task-001-r1-共用列表布局) · [正式源码摘要](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff3-source-digests.json) · [累积 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff3-source.patch)

### 验收复核

| 验收项 | QA3 结论 | 独立证据 |
| --- | --- | --- |
| AC10 三段与桌面紧凑布局 | 通过 | 在正式 `http://127.0.0.1:5190` 复核 `/plan/list`、`/performance/list`。`1280×900` 展开侧栏，中英文各页均为同一卡片内的标题与操作、独立筛选、表格与分页。两个分隔线可见，筛选四列横排，查询与重置靠右。筛选段高 164 px，表格自 y=325 开始。壳层顶部区域结束于 y=84，卡片从 y=92 开始。 |
| AC10 窄屏换行与壳层 | 通过 | `430×920` 经真实按钮收起侧栏后，两路由中英文筛选均为单列，输入和操作均在卡片及视口宽度内，查询与重置左对齐。卡片顶部 y=194，壳层顶部区域结束于 y=186。问号可命中，文档宽为 430 px，表格和分页分设横向滚动容器。 |
| AC10 双语时间提示 | 通过 | 两页分别使用各模块 `workflow.timeZone`，两模块各自的 83 个工作流键中英文顶层集合一致。使用真实壳层语言开关，两种视口共八组均验证标题旁问号、精确中文「业务时间：上海时间（UTC+08:00）」和英文「Business time: Shanghai (UTC+08:00)」。悬停时问号未获焦点，鼠标移开并确认提示消失后，通过 `Shift+Tab` 使问号进入 `:focus-visible`，提示再次出现，按 Esc 后消失。八组正文均无常驻时区说明。 |
| AC10 查询与重置 | 通过 | 登录响应 200，进入默认 `/plan/list`。两视口与两语言下，按 QA1 合成任务号查询，各页真实列表 GET 响应均 HTTP 200、`code=200`、`total=1`，对应行渲染。点击重置后任务号输入清空，后续 GET 不含 `taskNo`，计划、实绩分别回到 7 和 5 条。 |
| AC12 前端模块、构建及链接 | 通过 | 正式 `frontend-js/` 的 `pnpm check:modules`、`pnpm test:modules`、`pnpm build --outDir <QA3 临时目录>/dist` 均退出 0。57 passed、0 failed、0 skipped。保留两条测试夹具无活动实例的 `onBeforeUnmount` 警告和 Vite 大 chunk 提示。QA3 新增相对链接及目标标题存在。 |

### 命令、限制与交接

- 环境为 macOS 15.7.7 arm64、Node v22.19.0、pnpm 11.11.0、独立 Chrome 157.0.8103.39 与本机 Playwright `1.64.0-alpha-1789764292000`。初次默认沙盒的 loopback `curl` 退出 7，端口存在监听，经本机验证权限重试后 HTTP 200。浏览器探针由正式 `backend/` 的 `.venv/bin/python -B` 读取项目登录配置，经 stdin 传至 `node /private/tmp/arch-task-001-qa3.D5wkLU/browser.cjs <脱敏 JSON 路径>`，退出 0。只保存路径、聚合数量、提示和界面几何，浏览器 context 和进程已关闭。
- 浏览器记录 56 个 API GET 和一次登录 POST，应用页面异常与额外业务写请求均为 0。正常 `8000` / `5190` 服务未重启或改配，QA3 未调用临时验收端口。该轮使用已留存 QA1 夹具，只执行列表和配置读取，无任务、配置或采集写入，无迁移和清理。脱敏 JSON 的 SHA-256 为 `81fa407e757de814708de78888db7c0db96c538f65de43e94f6777aee7594ab7`，保存在本机 ignored 证据目录。 [独立浏览器证据](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/qa3-browser-layout.json)
- 前端检查使用 `pnpm_config_verify_deps_before_run=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1`。构建和测试日志位于 `/private/tmp/arch-task-001-qa3-build.r9jZ8m`。两处 QA3 临时目录仅用于复查命令和构建日志，持久结果已写入本清单与本机证据，交协调者确认归属后回收。
- 独立浏览器复验结束后，协调者按已批准的范围清理合成夹具和临时验收进程。协调者证据记录 `18000` / `15190` 已停，常规 `8000` / `5190` 均为 HTTP 200，计划及实绩均为 0 条，字段配置回到 v1/rev1 且无字段定义。清理后 50 个保护表结构、11 个数据摘要、13 个行数对账通过，正常采集读取 2 点。 [进程收尾](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/acceptance-process-cleanup.json) · [清理后复核](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/final-protected-runtime-check.json)
- 旧卷材报表及实绩打印入口在 r1 §7 R09 一次性切换中退役。该范围同时撤下旧报表依赖的 `print_records` 和旧实绩关系，通用报表重建另立范围。 [获批切换规格](spec.md#7-旧卷材一次性切换)

QA3 对精确 r1 第三次交接的 verdict 为 **`qa_passed`**，无 blocker。结果交 Human Owner 做最终验收。QA1 和 QA2 的历史限制继续适用，现场设备、DAA/SMA/CA/FF 原生联调、生产部署和长稳运行仍待对应范围验证。正式交付中 Verification 唯一更新为本清单。

## QA4 独立验证

2026-11-14 Asia/Shanghai。Verification 以 fresh context 接收第四次 `developer_handoff`，独立读取根契约、canonical workflow、角色 TOML、前端作用域、完整任务 bundle、正式实现、差异及 Development 检查输出。使用 `project-governance`、`frontend-ui`、`i18n-workflow`，以本机 Playwright 驱动独立 Chrome。范围为 R04、AC09–AC10 的字段设置与使用说明，以及相应 AC12 前端检查。此前的业务、数据库和回归矩阵沿用 QA1–QA3。

正式工作树 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`。核对获批 `spec.md` SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`、第四次交接 `tasks.md` `6f4f6a7f9d21b225c81891d2a4ab74f59f5cdd8dba16be2fe58c5d391d445bcd`、更新前 QA3 checklist `9ceac9dfb4dcfdbf23293c0666ab61343dd07accf80b784312fab81a93d959c4`。QA1–QA3 正文自 `# QA1 独立验证` 起的原字节 SHA-256 为 `d8f231fedb373ab41788149207a7be138236b45ff0e0fabfb3f83e5ce86fd4bf`，原样保留。

第四次 scoped manifest SHA-256 为 `62d5e4bcf902766c09ce272320c43e5f6dcde2ea488b39a78fae101ac3f4a866`，patch 为 `35a4ade8fb10660b08c101cfc2b6079034772cc6a83ec8acb9ffcb801fd6894f`，共用弹窗 SFC 为 `84f4691cb6fcd9cab3936b8e6a572cbc7c3294dff5a8d0adfe65a79984787d54`。正式工作树 8/8 路径摘要匹配，独立临时副本反向恢复 8/8 preimage，正向重放 8/8 postimage。检查范围按第四次交接的实施前摘要判定，保留工作树其他并行差异。验证收尾时工作树 HEAD 已前进至 `21cd789277695bbafaa55c24e39261fc7247f9b0`，再次复算 8/8 交付文件、spec 与 tasks 摘要，均匹配原交接，正式树反向 patch 检查仍退出 0。 [第四次交接](tasks.md#第四次-developer_handoff--arch-task-001-r1-字段设置) · [范围清单](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/field-settings-20261114/dev-scoped-manifest.json) · [范围差异](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/field-settings-20261114/dev-scoped.patch)

### 验收复核

| 验收项 | QA4 结论 | 独立证据 |
| --- | --- | --- |
| R04 / AC10 末列与视口 | 通过 | 正常 `5190` 的 `/plan/list`、`/performance/list` 在 `1470×796`、`430×920` 分别使用真实语言开关复核中英文，共 8 组。横滚到右端后输入 65535，末列表头文字、输入区和数字增减控件两侧均通过 DOM 命中检查，横向滚动条可见，页面宽度等于视口。稳定字段键仅桌面固定。 |
| R04 / AC10 列宽与本机草稿 | 通过 | 两页桌面分别实际拖动弹窗字段键列，宽度 190 → 232 px，关闭重开后仍为 232 px，恢复后为 190 px。隔离浏览器分别预置两页主表任务号列为 205 px，确认重置弹窗后显示宽度和本机偏好仍为 205 px。恢复默认保留尚未提交的顺序值。8 组均验证只在新增未保存行出现“移除草稿”，移除并关闭重开后不复活，已有其他编辑继续保留，仅新增后又移除则清除无变化草稿。 |
| R04 / AC09 / AC10 保存请求 | 通过 | 直接从正常 `8000` 读取 v3/rev3，计划 4 项、实绩 5 项，两侧共享定义相同，前后完整响应一致。24 次 PUT 均由浏览器拦截，各 8 次对应当前模块顺序值 65535、清空为 `null`、已保存字段仅提交 `enabled:false`（加 scope/slotNo 标识）。现有顺序值均为空，清空用例在拦截层将实际 GET 的单项顺序模拟为 65535 再通过控件清空，正确显示“按槽位 / Use slot”。保存请求均包含模块及实际版本和修订号。真实业务写入为 0，版本发布证据沿用 QA2。 |
| R04 / AC09 / AC10 使用说明 | 通过 | 对照两页实际六项勾选、三类字段组与三种实绩归属，核对“启用”、新旧版本、退用和复启、展示修订叠加、共享回写条件、下发必填参数和目标/版本映射。用源码确认未开放第三方集成时人工新建计划也校验目标版本与映射，DAA 采集和 SMA 或 CA / Field Flow 上报职责与合同一致。中英文 README 的指南链接及指南到公开合同的链接均有效。 |
| AC12 前端回归 | 通过 | `pnpm check:modules`、`pnpm test:modules` 和隔离 `pnpm build` 均退出 0，62 passed、0 failed、0 skipped。两模块各 87 个 workflow 顶层键，中英文完整键结构相同，弹窗 literal key 和四个新增键均可解析。 |

### 命令、限制与交接

- macOS 15.7.7 arm64，Node v22.19.0、pnpm 11.11.0、Chrome 157.0.8103.78 和本机 Playwright `1.64.0-alpha-1789764292000`。默认沙盒探测回环失败，使用本机验证权限后正常服务 `5190/login` 与 `8000/openapi.json` 均 HTTP 200。CLI 离线缓存没有 `@playwright/cli`，使用本机已有 Playwright 模块。QA 探针早期登录字段和 DOM 时序断言退出 1，修正临时探针后完整运行退出 0，应用源码未改。
- 在 `backend/` 由 `.venv/bin/python -B` 从项目设置读取管理员登录配置，经 stdin 传给 `node /private/tmp/arch-task-001-qa4.VL1pcw/browser.cjs <脱敏 JSON 路径>`。浏览器经正常 UI 登录一次，转发 148 个业务 GET，另直连 API 前后各读取两次配置；真实业务写入、意外写入请求和页面异常均为 0。独立浏览器及 context 已关闭，证据无凭据、任务号或真实字段名。浏览器结果 SHA-256 为 `b22f6a34bb3ee8f7075ea993c94c30d5bbb473c4e8d89562028ab0e212fe7945`。 [独立浏览器证据](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/field-settings-20261114/qa4-browser.json)
- `git diff --check`、`git apply --reverse --check --whitespace=error-all <scoped patch>` 和 `python3 /private/tmp/arch-task-001-qa4.VL1pcw/scope.py` 均退出 0。前端使用项目锁定依赖与 `pnpm_config_verify_deps_before_run=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1`，构建输出写入 `/private/tmp/arch-task-001-qa4.VL1pcw/dist`。模块测试输出两条既有测试夹具的 Vue 生命周期警告，构建有 Vite 大 chunk 提示。
- 本轮未执行真实配置发布、数据库写入、迁移、服务重启或现场操作。后端验收矩阵、设备原生联调、部署及长稳运行沿用既有范围和证据边界。临时探针、日志和构建保留在上述 QA4 临时目录，持久结论及脱敏结果已落盘，临时目录交协调者按任务资源规则回收。

QA4 对 **ARCH-TASK-001 r1 第四次交接**的 verdict 为 **`qa_passed`**，无 blocker。结果交 Human Owner 最终验收。Verification 仅更新本清单和上述本机脱敏浏览器证据。
