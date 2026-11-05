Task ID: ARCH-AW-008
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 -> Human Owner 文档最终验收；F-QA1-001经新的fresh-context独立增量核验关闭，AC01–AC20文档通过；第1–6节QA1失败历史保留，当前QA2证据见第7节；未授予Owner接受或软件实施
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-AW-008 r1 独立文档核验（QA1历史；当前QA2见第7节）

## 1. Verdict、身份与验证边界

2026-11-04，本轮独立文档核验结论为 **qa_failed**：AC01–AC18、AC20 通过；AC19 因运行原理图的事实／执行意图边界冲突未通过，缺陷为 F-QA1-001。没有环境 blocker；没有将未执行的软件条件记为通过。

实际 Verification 为 `/root/arch_aw008_verification_1`，由主协调在 Development `/root/arch_aw008_development` 完成 `developer_handoff` 后，以 `agent_type="verification"`、`fork_turns="none"` 启动。本上下文没有继承 Development 对话推理，独立读取批准 spec、tasks、冻结候选、实施前字节、交付 diff 和 DEV 报告；DEV 报告只是输入，以下检查独立执行。实际 agent inventory 同时显示 Development 已完成、本 Verification 正在运行；它不提供模型或 effort 的独立运行观测。

读取了根 AGENTS、README 双语、PLAN 双语，`.codex/agents/verification.toml`、canonical lifecycle，以及 docs／contracts 的最近 README／PLAN、plans catalog、相关 AW／DAA／SMA 的 README／PLAN和本任务完整 bundle。使用 `project-governance`、`aiis`（含 CONTRACTS）、`backend-arch`（响应／认证边界）核验本轮文档表面；没有以这些 skill 实施修复或执行未来软件任务。

本角色只创建本 `checklist.md`；没有写 spec、tasks、设计／合同、源码、测试、配置或证据目录。只使用现有文本、只读 Git 和 Python 标准库。没有项目导入、项目测试／构建／安装、应用启动、网络／API、真实 env／SQLite／profile 读取、DS／PLC、Docker、迁移、Git refs／推送或外发消息。与主协调的内部串行 handoff 不等于对外发送。

## 2. 精确批准、输入指纹与环境

范围依据为 [owner_approved r1 spec](spec.md)，Human Owner 2026-11-04 精确批准原话及批准前 SHA 见其第12节。本轮只核验其17路径文档范围内的 AC01–AC20；B01–B08、D01–D08是后续分别批准的软件条件。本任务的文档终验也不授权软件、实际联调、迁移或设备动作。

工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`。只读 `git rev-parse HEAD --show-toplevel` 退出0：HEAD 为 `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；这是共享脏树参考，并非本任务独占提交。环境为 macOS 15.7.7 arm64、zsh、Python 3.9.6（Agent 文本辅助，未冒充项目运行时）。独立命令观测时点包括 `2026-11-04T11:39:58.180993+08:00`、`2026-11-04T11:46:55.635524+08:00`。

持久输入证据根为 `/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/arch-aw-008-r1-docs-20261104/`，以下路径均相对此根。它不是本角色创建的临时输出；关键结果同时保存在本 checklist，不只依赖外部目录。

| 输入 | SHA-256／核对结果 |
| --- | --- |
| `approval-record.json` | `8f1965471d418c40afaf79f62a3ee16cfa4aedd83d47ba787228107f311d170e`；批准原话、Task ID、Revision和当前spec摘要一致 |
| `baseline-manifest.json` | `976a079dd45230f607e3bd1eb96a47aebc8745e9ef35bc61e92bc6e89f6df5bd`；3208安全路径，17路径allowlist，真实env／数据库类预先排除 |
| `handoff-manifest.json` | `dcaa6de1f20580e0e32da62c09cc27f88bc82b46c9ed34618b533bd9e3c22837`；12个冻结输入 |
| `development/delivery-sha256.json` | `aa092653411091504f3c1e3ed93a3217a0d1bf298209eb8a4b77350d7feedab9`；11个DEV交付文件 |
| `development/owned-vs-before.diff` | `3065a45661c7cb1b81ee957b0615017692acb69f73a5d46185c2e847557640fc`；独立重建完整diff逐字节一致 |
| `development/dev-check-report.json` | `79fdde2957a7ad67bbeeaf3643bb181ff950e81a2f850eb9607df65404ec2124`；仅作为DEV输入，未代替本轮QA |
| 根 `AGENTS.md` | `eceaf1f2fbaa4e4ba6d60554cfb52579fa8ec8c8205a6e8f3f7a267ed2b579be` |
| `.codex/agents/verification.toml` | `ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`；普通文件，配置model为gpt-6.1-sol、effort为max；不宣称独立确认运行值或平台ACL |
| canonical workflow | `5d49f61f8c8315bf97ee06e9c24943dcab7680df008580986a95b527f8b0f5d4`；项目入口为symlink；本轮是contract_only合同控制 |

以下每个源文件的 live 字节均与 `handoff/` 对应快照及 manifest SHA 相同；spec还与 `approved-spec.md` 相同。核验开始及记录结论前均重查，没有候选漂移。

| 源文件 | QA1候选 SHA-256 |
| --- | --- |
| `spec.md` | `4ed8396e3413846bb68d3246455130dd4610ae2ffb4fdc36a9f62666993d26df` |
| `tasks.md` | `8d9aed3e1f027c5fff6375c2d6967f0abebd3156906d1b3d72f33b7b06ab7e73` |
| `docs/AIIS_DAA_Detailed_Design.md` | `1ef581cbafca9d67fe117699079311c1691dafbcdfe0edfbc9f302a0d4f11049` |
| `docs/AIIS_SMA_Detailed_Design.md` | `50fd86acc3047c8dffc6767be03d27454b9364534a4dbd55d6704682f48a82c7` |
| `docs/AIIS_AW_Runtime_Design.md` | `87aa433c419d675cb7933333afc765b793aa3ecd32dad95ec4548fe50754b3f3` |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | `11896142e369f9025ece9e63f0a45b006fcb640f6740261aae1a5f77280733cd` |
| `docs/README.md` | `5571ec1cab54ae66dd4e7d37f81827ebc32e6c01ff8a049b9e302d0f0f938231` |
| `docs/README.zh-CN.md` | `f817dafb5b59ea989e59a61c35f83cca31886d0d2caf4adb659c50113c3ef042` |
| `contracts/demands/automation-world-facts-integration.md` | `b0d2cedadebe267f9a5f7accd03e66e8d4c0e25c5f02ac298afdac192cd8d965` |
| `contracts/demands/automation-world-facts-integration.zh-CN.md` | `406db9016ee34353a12dbcb32d6e47f5424220eff046d9e88b98637aee6610af` |
| `contracts/README.md` | `ba4503a2780a04221ef021a057545ba67b6256fb3c44f08644914a6254bd7733` |
| `contracts/README.zh-CN.md` | `5bc6890161fcd3b62386296d5dbecac150acc09fac31189d5e49d7c178b873be` |

## 3. AC01–AC20 独立核验

正文定位以共同需求合同为中心；对应[中文需求](../../contracts/demands/automation-world-facts-integration.zh-CN.md)与[英文需求](../../contracts/demands/automation-world-facts-integration.md)已逐段对照，不能仅用JSON相等替代翻译语义审阅。

| AC | 结果 | 独立证据与判断 |
| --- | --- | --- |
| AC01 | 通过 | spec为owner_approved r1、tasks为developer_handoff r1；批准SHA、17路径、逐阶段角色权威一致。本checklist在实际DEV交接后由新上下文创建，旧任务QA不转移。本任务PLAN/catalog行在核验中如实为qa_in_progress，无假终验。 |
| AC02 | 通过 | DAA§1／§13、SMA§1／§3、共同需求§1区分已接受受控阶段B、DAA上传未接通、冻结CA直库、旧表和认证GET／POST及Backend-held路线。定点只读源码确认uploadAvailable=false、本地样本v2／manifest同轮提交、旧latest唯一键PLC/DB/group、Projection标量读取及温控actor参与幂等。没有读取真实库来推定现状。 |
| AC03 | 通过 | 共同需求§2／§9、DAA§10.1／§10.6和SMA§7.2明确匿名一写两读与模块自有typed目标，现有认证／权限／设备scope保持；客户端声明不证明所有权，不按UA绕过，不伪造admin或提供任意表SQL。运行原理图的另一个CA连接问题按AC19单列F-QA1-001。 |
| AC04 | 通过 | 共同需求§3逐项对应本地v2字段、稳定point/sample/cycle/batch、原样mapping keys、源代次／十进制序号、managed ASCII及legacy原名。坏质量仍有定义、缺值、原时间和reason；正式类型／null矩阵责任留provider。 |
| AC05 | 通过 | 共同需求§4三包主例包括A的DB71/88同轮、B同号DB独立轮；两片仅到一片场景不标轮完成；预期点集合、manifest与样本身份独立脚本一致。独立组例有文字说明，跨PLC不比较seq，不虚构同步帧。 |
| AC06 | 通过 | 共同需求§3、DAA§10.3区分原payload/manifest/context字节SHA、传输contentDigest和冻结requestDigest，声明自引用排除／规范化／向量需正式冻结；不以重新序列化冒充原文，不重写历史。 |
| AC07 | 通过 | 共同需求§5及DAA§6／§10.1规定提交后回执、逐成员摘要／created／duplicate、manifest完成范围与本地短事务单调ACK；HTTP200/202、日志、仅入队不是可靠事实／业务确认。丢响应或本地ACK失败保持原冻结身份。 |
| AC08 | 通过 | 共同需求§5矩阵覆盖重复／异内容／expired／历史证明／unknown、合法与过期混合、他批已确认但旧批未终结；unknown先恢复，证明无新增提交且获准退休后方可派生，原样本身份／内容及非法成员仍保护。409/410/503样例不假ACK、不假回滚。 |
| AC09 | 通过 | 共同需求§6及DAA§10.1按点原子比较有效来源／定义／本点更高seq／未到期；同DB多组不整包覆盖。首次采用、旧代次截止／新基线及CAS／等效机制归provider精确spec；opaque字符串与晚到HTTP不授权接管。latest例保留逐点原sample／代次／seq／定义版本。 |
| AC10 | 通过 | 共同需求§6、DAA§10.4和SMA§5采用最近结果，新bad替代当前值并保留新时间／reason；旧好值另标历史。缺点不删、停用需有效声明，无声明只能陈旧／到期；定义变化局部暂停，quality／新鲜度／保留期分别判断。 |
| AC11 | 通过 | 共同需求§7、DAA§10.2、SMA§4／§9–10区分range页游标与changes接收cursor，绑定过滤／模式／版本；晚采集补传和较小ID晚提交反例说明maxID不安全，空页不证完整。超窗／改过滤／删材料有gap与显式新基线，接收cursor不冒充处理checkpoint或源序完整前缀。 |
| AC12 | 通过 | 双语共同需求§8、DAA§10.5、SMA§12及AW两文一致采用上海+08原observedAt，默认且最多三自然月，可更短不更长，达到截止不可读；三个月末／闰年例及毫秒独立计算一致。旧UTC文字修订不迁移库、不给历史整体加八小时。 |
| AC13 | 通过 | 共同需求§8及DAA§10.5规定整包原文按最早成员截止、latest逐点到期；等效投影另证不暴露过期点，区分投影与原SHA。逻辑不可读、有界物理清理和备份／介质职责分开；最小证明有限保留、历史ACK不复活值，后端拒绝不授权清理本地未确认引用。 |
| AC14 | 通过 | 共同需求§9、DAA§10.6、SMA§7.2／§11–12分开事实ACK与业务ACK，event/producer／mappingRevision／sourceRefs及请求／回执关联一致。可靠业务记录默认永久、无自动TTL且自带实际值与必要来源；raw清理不级联业务或未完成outbox，缺输入过期不能补造记录。 |
| AC15 | 通过 | 共同需求§10明确引用spec§8完整B01–B08：正式schema／摘要／来源／限额／迁移、旧CA/Projection兼容、并发latest／安全cursor、清理和有限证明、另批隔离库／fresh QA及固定交接材料。全部是后续标准，没有实际软件pass或上线声称。 |
| AC16 | 通过 | DAA§4／§6–9／§12／§16与共同需求§10承接D01–D08；单一匿名目标／独立周期、Rust owner全实例单在途、有界最新优先与公平历史、独立启停／容量／启动停止、真实UI状态与手册／必要增量证据清楚；旧profile和原样本保护不重开整套B测试。 |
| AC17 | 通过 | 共同需求§10及两详细设计§16明确先固定provider正式版本，双方各自精确批准后可并行；真实HTTP联调待Backend就绪与隔离授权。SMA和全部业务模块、自动启动／现场不是DAA首版阶段C前置。 |
| AC18 | 通过 | 新需求位于contracts/demands，双语元数据同Contract ID／demand-r1／proposed；docs和contracts索引对称。候选endpoint／合法JSON不冒充可执行schema、provider接受、实现或部署；未来published与真实源对齐责任明确。 |
| AC19 | **未通过** | 独立JSON／围栏／表格／本地链接锚点／双语／日期／保护面检查通过；但[运行原理§2](../../docs/AIIS_AW_Runtime_Design.md#2-职责边界)图中B节点缩成raw/latest后，业务请求／CA执行意图／执行回执仍指向B，见F-QA1-001。图文一致性未满足，不能用静态计数通过替代。 |
| AC20 | 通过 | tasks保留DEV自检，本checklist是新fresh-context QA1，Owner文档终验待定。本轮只写checklist，不修改实现或进行软件／库／配置／API／设备／发布动作；并行脏树不被声称为本任务代码变更或全树未变。 |

## 4. 独立命令、结果及保护审计

所有命令在交付工作树执行。Q02／Q03／Q04使用 `python3 - <<'PY'` 内联标准库，只读路径和stdout，不创建检查器文件、不调用DEV检查器。本节记录实际方法、关键原始输出和退出码；下面Q02代码保留为可复制的结构核验命令。

| 编号 | 实际命令／检查 | 退出码与结果 |
| --- | --- | --- |
| Q01 | `git rev-parse HEAD --show-toplevel`；Python `hashlib.sha256(Path.read_bytes())`核对12个live／handoff／manifest、批准快照与证据输入摘要 | 0；12/12一致，spec批准快照一致，精确SHA见§2 |
| Q02 | 下面内联stdlib结构检查：独立围栏状态机、严格JSON（拒绝重复键／非有限常量）、GFM本地heading／显式anchor、表格列数／分隔行、双语对象、月末算法 | 0；交付24 JSON／800表格行／183本地链接；含spec31／918／203；双语11对象相等；3日期例相等；`ERRORS []` |
| Q03 | Python独立解析中文需求11个JSON，断言样本／manifest／cycle／预期点、跨PLC同DB、bad缺值／reason、缺片不完整、请求与ACK摘要／范围、latest来源、history样本、业务值／时间／回执；英文对象由Q02完整相等覆盖 | 0；`SEMANTIC_EXAMPLE_CHECKS 18`，18项均true；这是文档示例关系检查，不是API／schema／运行测试 |
| Q04 | Python依delivery指纹顺序，从before原字节重建各文件`difflib.unified_diff(..., fromfile='before/'+n, tofile='delivery/'+n)`，以单个空行连接各file diff；核对持久diff；检查DS原段、已批准历史及安全基线 | 0；完整diff逐字节相等，SHA `3065a45661c7cb1b81ee957b0615017692acb69f73a5d46185c2e847557640fc`；保护结果如下 |
| Q05 | `git diff --check -- docs/AIIS_DAA_Detailed_Design.md docs/AIIS_SMA_Detailed_Design.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/README.md docs/README.zh-CN.md contracts/README.md contracts/README.zh-CN.md contracts/demands/automation-world-facts-integration.md contracts/demands/automation-world-facts-integration.zh-CN.md plans/ARCH-AW-008-stage-c-facts-contract/tasks.md` | 0，无输出；仅检查空白，不用HEAD混合diff判本轮归属 |
| Q06 | 定点`rg -n`／`sed -n`读取DAA local_sample/runtime/commands、CU公开导航、SMA README／material store／record_success、Backend monitor Model／route／response／Projection／温控Service | 源文与AC02对应；一次猜测SMA `src-tauri/src/infrastructure/http`不存在，rg返回2，随后用`rg --files`确认现有路径并重读；另一次精确snapshot字面搜索无匹配返回1，不据此声称接口不存在。没有运行代码／HTTP |
| Q07 | `nl -ba docs/AIIS_AW_Runtime_Design.md`的24–51行与before原图、正文角色表对照，提取四份设计全部4个Mermaid块逐边审阅 | 读取退出0；人工语义判定发现F-QA1-001；未运行Mermaid渲染或宣称视觉／完整语法验证通过 |

Q02可复制命令（输出限定为统计与错误，不输出业务数据）：

```bash
python3 - <<'PY'
from pathlib import Path
import json, re, unicodedata, urllib.parse, calendar, datetime
r = Path.cwd()
e = Path('/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/arch-aw-008-r1-docs-20261104')
files = list(json.loads((e/'development/delivery-sha256.json').read_text()))
spec = 'plans/ARCH-AW-008-stage-c-facts-contract/spec.md'
errors, objects, stats, text, anchors = [], {}, {}, {}, {}
def pairs(items):
    out = {}
    for key, value in items:
        if key in out: raise ValueError('duplicate JSON key')
        out[key] = value
    return out
def nonfinite(value): raise ValueError('nonfinite JSON')
for n in files+[spec]:
    objects[n], text[n], fence, code = [], [], None, []
    for i, line in enumerate((r/n).read_text().splitlines(), 1):
        m = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if m and m[1][0] == fence[0] and len(m[1]) >= len(fence) and not m[2].strip():
                if lang.lower() == 'json':
                    try: objects[n].append(json.loads('\n'.join(code), object_pairs_hook=pairs, parse_constant=nonfinite))
                    except Exception as ex: errors.append((n, 'JSON', str(ex)))
                fence, code = None, []
            else: code.append(line)
        elif m: fence, lang = m[1], m[2].strip()
        else: text[n].append((i, line))
    if fence: errors.append((n, 'unclosed fence'))
    rows, table = 0, []
    for i, line in text[n]+[(0, '')]:
        if line.strip().startswith('|'):
            cells = re.split(r'(?<!\\)\|', line.strip())[1:-1]
            table.append((i, cells)); rows += 1
        elif table:
            if len(table) < 2 or any(len(c) != len(table[0][1]) for _, c in table):
                errors.append((n, table[0][0], 'table width/header'))
            elif not all(re.fullmatch(r'\s*:?-+:?\s*', s) for s in table[1][1]):
                errors.append((n, table[1][0], 'table separator'))
            table = []
    stats[n] = dict(json=len(objects[n]), tableRows=rows, localLinks=0)
def ids(path):
    if path in anchors: return anchors[path]
    body = path.read_text(); found = set(re.findall(r'<a\s+(?:name|id)=[\"\']([^\"\']+)', body)); seen = {}
    for line in body.splitlines():
        m = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not m: continue
        s = re.sub(r'<[^>]+>', '', m[1]).replace('`', '').lower()
        s = ''.join(c for c in s if c in '_-' or not unicodedata.category(c).startswith(('P','S')))
        s = re.sub(r'\s', '-', s); count = seen.get(s, 0); seen[s] = count+1
        found.add(s+('-'+str(count) if count else ''))
    anchors[path] = found; return found
for n, lines in text.items():
    for i, line in lines:
        for m in re.finditer(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', line):
            raw = m[1].strip('<>'); u = urllib.parse.urlsplit(raw)
            if u.scheme or u.netloc: continue
            stats[n]['localLinks'] += 1
            p = ((r/n).parent/urllib.parse.unquote(u.path)).resolve() if u.path else r/n
            if not p.exists(): errors.append((n, i, 'missing link', raw))
            elif u.fragment and (not p.is_file() or urllib.parse.unquote(u.fragment) not in ids(p)):
                errors.append((n, i, 'missing anchor', raw))
a = 'contracts/demands/automation-world-facts-integration.md'
b = 'contracts/demands/automation-world-facts-integration.zh-CN.md'
if objects[a] != objects[b]: errors.append('bilingual JSON mismatch')
print('DOC_STATS', json.dumps(stats, ensure_ascii=False))
for label, names in [('DELIVERY_TOTALS', files), ('INCLUDING_SPEC_TOTALS', files+[spec])]:
    print(label, {k:sum(stats[n][k] for n in names) for k in ['json','tableRows','localLinks']})
print('BILINGUAL_JSON_EQUAL', objects[a] == objects[b])
for source, target in [('2026-01-31T12:00:00.123+08:00','2026-04-30T12:00:00.123+08:00'), ('2023-11-30T06:00:00.000+08:00','2024-02-29T06:00:00.000+08:00'), ('2024-11-30T06:00:00.000+08:00','2025-02-28T06:00:00.000+08:00')]:
    t = datetime.datetime.fromisoformat(source); y, m = divmod(t.year*12+t.month-1+3, 12); m += 1
    result = t.replace(year=y, month=m, day=min(t.day, calendar.monthrange(y,m)[1])).isoformat(timespec='milliseconds')
    print('MONTH_CASE', source, result, result == target)
    if result != target: errors.append(('month', source, result))
print('ERRORS', json.dumps(errors, ensure_ascii=False))
raise SystemExit(bool(errors))
PY
```

Q04保护及并行审计：

- Runtime从 `<a id="ds"></a>` 到文件结尾的6760字节与before相同，SHA为`e243853ed0575ba3efe3b81173953bc0bdd56102f89a390113a0cd5aaf5bc111`；白皮书从 `### 13.3 DS：` 到第14节前的2273字节相同，SHA为`d49a0ebab26741c7c00fcca8a108f2d08cff4c30b25569a1e9305869216a2b4c`。
- 原ARCH-AW-002的3文件、003的3文件、007的4文件，以及DAA-002／003／004各3文件、DAA-007的19文件，与基线指纹全部相同。没有重标旧批准／QA／验收。扫描中DS产品路径无变化。
- 在安全基线3208路径中，观测3096相同、97变化、15缺失；没有追加读取任何被基线排除的真实env／数据库。97变化中的13个是已有allowlist路径，另84个为CODE_INDEX、AW索引、SMA46、Backend2、Field Flow31等并行表面；15缺失均位于SMA。491份所查非本任务／非SMA和Field Flow的旧task文件保持，另外两个AW catalog是并行变化。后续共享树还可能继续变化，以上是该次指纹观测，不是全树无变化声明。
- 四个根PLAN/catalog文件中，本任务行已机械同步到qa_in_progress；同一文件还出现并行ARCH-BE-010草案行，不归本任务。11份DEV文档以before及handoff单独核验，不将这些并行差异算为本任务owned变化，不回退他人改动。
- 本轮初次直接拼接diff因漏掉DEV报告中的文件间空行而不相等；确认格式差异后按文件间单空行独立重建，完整字节与SHA相等。这是检查器输出格式的纠正，没有修改候选或把差异掩盖掉。

## 5. F-QA1-001：运行原理图混淆事实节点与CA业务执行链

严重性：P2；状态：**open，需Development修复**；对应：AC19，spec§3.2对Runtime的有限同步及CA保留边界。

精确证据为 [AIIS_AW_Runtime_Design.md](../../docs/AIIS_AW_Runtime_Design.md#2-职责边界) 的42、47、48、50行：

```text
42 LOCAL -->|匿名事实 API / 可靠ACK| B[Backend raw / latest]
47 X -->|提交业务请求| B
48 B -->|领取有效执行意图| CA[CA 执行]
50 CA -->|执行回执| B
```

before原图的B是通用 `B[本系统 Backend]`。本轮将B收窄为短期raw/latest，并新增专门业务Service节点BIZ，却保留业务请求、执行意图领取和执行回执连接B。读图会得到“业务请求和CA执行状态进入事实raw/latest”的关系，而同文32–34行要求CA输入为经校验、持久化且具备执行资格的意图，Backend还有业务校验／领取／回执职责；共同需求又将事实接收和模块typed业务事务分开。该问题是本次改图产生的语义回归，不是要求新增或复验CA功能。

修复所需结果：在已批准文档范围内，让通用Backend／业务执行意图状态与raw/latest事实职责在图中表达一致，核对三条原CA边的目标／来源；保持原CA范围，不引入新实现。QA不指定必须新增某个模块或物理表，也没有代替Development改图。修复后应重查图文和局部链接／围栏，提供新文件SHA和精确交接；新的fresh-context QA复核修正候选并保留本轮失败历史。

## 6. 限制、验收审计、资源与下一gate

| 表面 | 本轮实际结论 | 后续gate |
| --- | --- | --- |
| 文档候选 | 19项AC通过，AC19有F-QA1-001，整体qa_failed | 串行返Development修图、新handoff、新fresh-context QA |
| 文档最终验收 | **未发生** | 修复并QA通过后由Human Owner决定，不由QA授予 |
| 正式provider合同／schema／算法 | 仍为后续软件任务责任；当前demands/proposed | Backend自有精确spec与批准；共同语义实变回PM修订 |
| Backend B01–B08、DAA D01–D08 | 只核验标准定义，未执行、未判软件pass | 两端分别批准并可并行；Backend固定就绪后另批实际联调 |
| SMA／模块业务闭环 | 设计及各自后续责任，未验证运行 | 独立spec／实现／QA；不作为DAA首版前置 |
| Mermaid／外链 | 4个Mermaid块做文本及图文审阅，未渲染；未访问外链 | 不宣称图形视觉／完整语法或远端可达性证据；当前语义缺陷仍须修复 |
| SQLite／profile及现场 | 通过不访问／不写入保持本轮边界；未读取真实数据去宣称全库字节不变 | 原阶段B资料继续保留；未来迁移／设备／生产／部署另批 |

环境没有阻止必要文档核验；未来未获批的软件、现场和渲染事项没有被包装成当前缺证通过。本角色没有修复任何候选、启动运行资源或新建临时目录，因而没有本角色需回收的应用、库或构建产物。主协调保留既有持久before／approval／handoff／Development证据供返工和Owner审阅；不得在QA1失败后清掉唯一原候选或diff。资源收尾与通知仍由主协调按canonical workflow办理，未重复启动execution window或发送邮件。

本轮handoff给主协调：保持本checklist的QA1失败证据，返回Development处理F-QA1-001；不得将本候选登记为qa_passed或owner_accepted。修复后重开新fresh-context Verification，验证结果最终只交Human Owner做文档终验。当前仍无Human Owner最终验收记录。

写入后回读审计：实际从本文件提取Q02的bash围栏，用`subprocess.run(['zsh','-c',cmd])`原样复跑，`RECORDED_Q02_EXIT 0`，24／800／183与含spec31／918／203及三日期结果保持，`ERRORS []`。另将本checklist加入相同结构检查输入，`CHECKLIST_STRUCTURE_EXIT 0`、`ERRORS []`；新checklist的链接／围栏／表格通过。`git diff --check -- plans/ARCH-AW-008-stage-c-facts-contract/checklist.md`退出0；最后一次12个冻结输入SHA复核为`FINAL_FROZEN_INPUT_MISMATCH []`。这些静态通过不关闭F-QA1-001。

## 7. QA2：F-QA1-001返工后的独立增量核验（2026-11-04）

### 7.1 当前verdict、身份与QA1历史保全

本轮结论为 **qa_passed，仅ARCH-AW-008 r1文档范围**。F-QA1-001由本次独立Verification判定为closed；AC19在QA1失败、返工后于QA2通过，其他19项保留QA1独立证据并按本节核对可沿用性。没有当前文档blocker；Human Owner文档最终验收未发生，Backend B01–B08／DAA D01–D08未执行、未记软件通过。

实际新Verification为`/root/arch_aw008_verification_2`，由主协调在同一Development返工handoff后以`agent_type="verification"`、`fork_turns="none"`调用。本上下文没有继承Development对话推理，读取的是当前仓库、批准记录、完整spec/tasks/QA1 checklist、冻结候选、实际diff及可用DEV报告。实际`collaboration.list_agents`显示Development和QA1均completed、本QA2 running；该观测不证明模型／effort运行值或平台ACL，仍是contract_only控制。未派生其他agent。

重新读取根AGENTS、README／PLAN双语、verification.toml及canonical workflow，最近docs／contracts README、contracts PLAN双语和plans catalog；检查候选祖先目录，未发现更近AGENTS.md。加载`project-governance`、`aiis`及BLUEPRINT／CONTRACTS，另以`backend-arch`及LAYERS／AUTH_SECURITY／RESPONSE_CONTRACT复核本次图的Service、事务与权限边界；不加载没有被本次返工触及的UI、Rust、Tauri或工具实现skill。后端规范没有被用来恢复Celery或运行软件检查。

第1–6节保留QA1全部验收、命令、失败、缺陷和限制的原文。仅本文件顶部当前Status、Handoff及总标题更新；原三行如下，结合本节之前的字节可精确恢复QA1完整快照。QA1原独立结论不改为首次通过，原F-QA1-001的open描述保留为该轮历史。

```text
Status: qa_failed
Handoff: QA1 -> Development；先修复 F-QA1-001 并形成新的精确 developer_handoff，再由新的 fresh-context Verification 复核；Human Owner 文档最终验收待定
# ARCH-AW-008 r1 独立文档核验（QA1）
```

QA2写入前，仓库checklist与持久`qa1-checklist.md`逐字节相等，SHA为`62e148b8344c318ae893d1da7df866fff2ac4d08eceef989f71b29bd813ce4d9`。本轮只写本checklist；不改任何候选或旧证据。

### 7.2 精确输入、环境和候选一致性

持久证据根仍为第2节同一目录，以下路径相对此根。环境独立观测：macOS 15.7.7 arm64、zsh、Python 3.9.6，`2026-11-04T11:59:45.090258+08:00`；Python只作Agent标准库文本辅助，不导入项目。只读HEAD仍为`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，交付树仍为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；它不是任务独占commit。

| 当前返工输入 | QA2独立SHA-256 |
| --- | --- |
| `handoff-rework-1-manifest.json` | `97d8d5ef1dd52bd78fb9595e33cbfd18d54665eb39b14af6a009e4c6dfa99d49` |
| `development/rework-1/delivery-sha256.json` | `7bb82dba240d6422d4eefcf9827026356dae6bd1d0de08ff7c85e2700c1778c0` |
| `development/rework-1/delta-vs-qa1.diff` | `333795d77e4ddbafae4f853229350b66e2031f1b4b827538a3d98f9ea77102a3` |
| `development/rework-1/increment-check-report.json` | `4b7533cbe79b0e257c1ee3b4415c8aed924bbb634c84a6ce260c8f7359bc0654`；DEV自检仅作为输入 |
| 新Runtime源文 | `f87a3ef641a287731f73b3336c37b10977840b2609a99fc3ec27b534f1575d42` |
| 新tasks源文 | `a7a0f50ae4fc3c05ce8dfafd8277ce8445a7c6181e61a8eff0ea156814a3cfa1` |

批准spec仍为`4ed8396e3413846bb68d3246455130dd4610ae2ffb4fdc36a9f62666993d26df`，与live、原handoff、新handoff-rework-1及approved-spec.md一致；approval-record原话与本轮精确授权一致。新manifest的12份输入均与交付树和新快照一致。仅Runtime、tasks相对QA1变化；另10份输入（spec及9份设计／合同／索引）与第2节QA1表逐文件相同。11份新DEV交付与新delivery清单完全一致，没有用临时副本代替正式交付。

第2节的approval／baseline／原handoff、原DEV delivery／owned diff／report共6份旧输入保持原SHA；加上QA1完整快照及本轮4份新输入，总共11个证据pin全部匹配。原handoff的12份冻结文件也逐一匹配其原manifest；before/的13份原文件逐一匹配原baseline指纹。根AGENTS、verification.toml及canonical workflow的SHA仍分别与第2节相同；前两者普通文件、workflow入口为symlink。

### 7.3 独立命令、增量与结构结果

以下命令均实际执行，除本checklist写入外只读文本／只读Git并向stdout输出；未调用任何Development检查器。Q2-A完整命令保存在下方，Q2-B为另一次独立内联stdlib检查，方法和关键断言列明，不以DEV报告计数充当QA执行结果。

| 编号 | 实际命令／方法 | 退出码与关键结果 |
| --- | --- | --- |
| Q2-A | 下方`python3 -B - <<'PY'`：固定11证据SHA，核对原／新镜像和live、before、批准spec、QA1完整字节；独立重建两文件delta，检查Runtime四行及tasks只追加 | 0；11个pin、原12、新12、before13均匹配；未改10；Runtime四行替换；tasks前缀完整，追加36行／4254字节；delta字节及SHA完全相同；四处Runtime DS段6760字节一致；`ERRORS []` |
| Q2-B | `python3 -B - <<'PY'`：对Runtime／tasks以独立围栏状态机跳过代码、逐表检查列宽与分隔行、生成GFM标题／显式anchor核查本地链接；分割Mermaid `-->` 的两端和可选标签，检查B节点入出边／CA领取及回执／原节点集合 | 0；Runtime为14本地链接／71表格行／6围栏块，tasks为2／66／0；合计16链接／137表格行；11条不同图边；原节点集合保持，raw/latest仅事实链、CA有效意图与独立回执断言均true；`ERRORS []` |
| Q2-C | `cat docs/AIIS_AW_Runtime_Design.md`；Python按标题提取白皮书§4／§9–10、DAA§1–2／§10.6、SMA§2–3／§7.2、双语需求§1–2；`sed -n '603,628p' docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md`；`cat contracts/demands/control-agent/high-risk-authorization-gate.zh-CN.md`并对照contracts README | 0；人工逐边与角色／权限／独立合同对照支持F1关闭，具体判断见§7.4；其余三个未变Mermaid图已在DAA／SMA所读段内，无新增同类连接 |
| Q2-D | `git diff --check -- docs/AIIS_AW_Runtime_Design.md plans/ARCH-AW-008-stage-c-facts-contract/tasks.md` | 0，无输出；仅空白检查，不以共享HEAD混合diff认定归属 |
| Q2-E | `git rev-parse HEAD --show-toplevel`；Python `platform.mac_ver()`／`platform.machine()`／`platform.python_version()`与`datetime`；`collaboration.list_agents` | 0／成功返回；环境／HEAD及角色时序如§7.1–7.2；不据配置冒称运行model或ACL |

Q2-A可复制的实际命令：

```bash
python3 -B - <<'PY'
from pathlib import Path
import hashlib, json, difflib
r=Path.cwd()
e=Path('/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/arch-aw-008-r1-docs-20261104')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
pins={
 'approval-record.json':'8f1965471d418c40afaf79f62a3ee16cfa4aedd83d47ba787228107f311d170e',
 'baseline-manifest.json':'976a079dd45230f607e3bd1eb96a47aebc8745e9ef35bc61e92bc6e89f6df5bd',
 'handoff-manifest.json':'dcaa6de1f20580e0e32da62c09cc27f88bc82b46c9ed34618b533bd9e3c22837',
 'development/delivery-sha256.json':'aa092653411091504f3c1e3ed93a3217a0d1bf298209eb8a4b77350d7feedab9',
 'development/owned-vs-before.diff':'3065a45661c7cb1b81ee957b0615017692acb69f73a5d46185c2e847557640fc',
 'development/dev-check-report.json':'79fdde2957a7ad67bbeeaf3643bb181ff950e81a2f850eb9607df65404ec2124',
 'qa1-checklist.md':'62e148b8344c318ae893d1da7df866fff2ac4d08eceef989f71b29bd813ce4d9',
 'handoff-rework-1-manifest.json':'97d8d5ef1dd52bd78fb9595e33cbfd18d54665eb39b14af6a009e4c6dfa99d49',
 'development/rework-1/delivery-sha256.json':'7bb82dba240d6422d4eefcf9827026356dae6bd1d0de08ff7c85e2700c1778c0',
 'development/rework-1/delta-vs-qa1.diff':'333795d77e4ddbafae4f853229350b66e2031f1b4b827538a3d98f9ea77102a3',
 'development/rework-1/increment-check-report.json':'4b7533cbe79b0e257c1ee3b4415c8aed924bbb634c84a6ce260c8f7359bc0654'
}
assert all(sha(e/n)==v for n,v in pins.items())
old=json.loads((e/'handoff-manifest.json').read_text())['sourceFiles']
new=json.loads((e/'handoff-rework-1-manifest.json').read_text())['sourceFiles']
assert len(old)==len(new)==12 and old.keys()==new.keys()
assert all(sha(e/'handoff'/n)==v for n,v in old.items())
assert all(sha(r/n)==v==sha(e/'handoff-rework-1'/n) for n,v in new.items())
changed=[n for n in new if old[n]!=new[n]]
assert set(changed)=={'docs/AIIS_AW_Runtime_Design.md','plans/ARCH-AW-008-stage-c-facts-contract/tasks.md'}
assert json.loads((e/'development/rework-1/delivery-sha256.json').read_text())=={n:v for n,v in new.items() if not n.endswith('/spec.md')}
spec='plans/ARCH-AW-008-stage-c-facts-contract/spec.md'
assert sha(e/'approved-spec.md')==new[spec]=='4ed8396e3413846bb68d3246455130dd4610ae2ffb4fdc36a9f62666993d26df'
base=json.loads((e/'baseline-manifest.json').read_text())
before=list((e/'before').rglob('*'))
before=[p for p in before if p.is_file()]
assert len(before)==13
assert all(sha(p)==base['files'][str(p.relative_to(e/'before'))]['sha256'] for p in before)
assert (r/'plans/ARCH-AW-008-stage-c-facts-contract/checklist.md').read_bytes()==(e/'qa1-checklist.md').read_bytes()
runtime='docs/AIIS_AW_Runtime_Design.md'
tasks='plans/ARCH-AW-008-stage-c-facts-contract/tasks.md'
a=(e/'handoff'/runtime).read_text()
b=(r/runtime).read_text()
replacements=[
 ('BIZ[Backend 业务 Service]','BIZ[Backend 业务 / 意图 Service]'),
 ('X -->|提交业务请求| B\n','X -->|提交业务请求| BIZ\n'),
 ('B -->|领取有效执行意图| CA[CA 执行]','BIZ -->|领取已校验持久的有效执行意图| CA[CA 执行]'),
 ('CA -->|执行回执| B\n','CA -->|执行回执 - 独立合同| BIZ\n')
]
expected=a
for source,target in replacements:
    assert expected.count(source)==1
    expected=expected.replace(source,target)
assert expected==b
ops=[(tag,i,j,k,l) for tag,i,j,k,l in difflib.SequenceMatcher(None,a.splitlines(),b.splitlines(),autojunk=False).get_opcodes() if tag!='equal']
assert sum(j-i for _,i,j,k,l in ops)==sum(l-k for _,i,j,k,l in ops)==4
at=(e/'handoff'/tasks).read_bytes(); bt=(r/tasks).read_bytes()
assert bt.startswith(at) and bt[len(at):].startswith('\n## 7. QA1返工与新的developer_handoff'.encode())
parts=[]
for n in (runtime,tasks):
    parts.append(''.join(difflib.unified_diff((e/'handoff'/n).read_text().splitlines(keepends=True),(r/n).read_text().splitlines(keepends=True),fromfile='qa1-handoff/'+n,tofile='rework-1/'+n)))
actual='\n'.join(parts).encode()
assert actual==(e/'development/rework-1/delta-vs-qa1.diff').read_bytes()
for scope in (e/'before',e/'handoff',e/'handoff-rework-1',r):
    s=(scope/runtime).read_bytes(); seg=s[s.index(b'<a id="ds"></a>'):]
    assert len(seg)==6760 and hashlib.sha256(seg).hexdigest()=='e243853ed0575ba3efe3b81173953bc0bdd56102f89a390113a0cd5aaf5bc111'
print('EVIDENCE_PIN_MATCH',len(pins))
print('ORIGINAL_SNAPSHOT_MATCH',len(old),'NEW_LIVE_SNAPSHOT_MATCH',len(new),'UNCHANGED_SOURCES',len(new)-len(changed))
print('BEFORE_SNAPSHOT_MATCH',len(before),'APPROVED_SPEC_MATCH',True,'QA1_CHECKLIST_EXACT',True)
print('RUNTIME_LINES_REPLACED',4,'TASKS_PREFIX_PRESERVED',True,'APPEND_LINES',len(bt[len(at):].splitlines()),'APPEND_BYTES',len(bt)-len(at))
print('DELTA_EXACT',True,'DELTA_SHA256',hashlib.sha256(actual).hexdigest(),'DS_BYTES',len(seg))
print('RUNTIME_SHA256',new[runtime],'TASKS_SHA256',new[tasks])
print('ERRORS',[])
PY
```

该命令的checklist直接相等断言针对QA2写入前执行时点；QA2追加后不应再要求整个live checklist等于QA1。回读审计改为取第7节之前的前缀，恢复§7.1明确保留的原Status／Handoff／标题，再与QA1快照逐字节比较；不删除QA2去伪造相等。

Q2-B关键图边断言及实际输出摘要：

```text
B节点全部关联边：LOCAL -> B；B -> SMA
CA全部输入：BIZ -> CA，领取已校验持久的有效执行意图
CA全部输出：CA -> PLC，受控写入与确认；CA -> BIZ，执行回执 - 独立合同
X -> BIZ，提交业务请求
SMA -> BIZ，模块 typed API / 独立业务ACK
GRAPH_RAW_LATEST_FACT_ONLY True
CA_ELIGIBLE_INTENT_AND_INDEPENDENT_RECEIPT True
NODE_SET_UNCHANGED True
ERRORS []
```

### 7.4 F-QA1-001关闭依据及未扩大边界

Runtime现行44、47、48、50行正好是四行替换：既有BIZ节点改称Backend业务／意图Service；X业务请求改连BIZ；CA领取改来自BIZ且明确已校验、持久、有效；CA执行回执改回BIZ并显式标独立合同。B仍只接DAA本地已提交事实、向SMA提供latest/history，事实可靠ACK和模块独立业务ACK的两段含义保留。

该修改与Runtime§2角色表及§8一致：Backend负责业务校验、持久化及执行资格，CA主动领取，入库不自动可执行；草稿／取消／过期不能领取，原子领取／租约、现场条件、受控写入／设备确认、unknown核实仍归CA独立执行合同。图中BIZ到CA的箭头表示被领取的有效输入，与正文要求CA发起领取一致，不表示Backend向运行中CA推送设备动作。

白皮书§4的“第三方→本系统校验并持久化→CA原子领取→设备→CA回执”及§13的有效意图／范围／确认／unknown链与新图一致；DAA§1–2／§10.6、SMA§2／§7.2及双语需求§1–2仍分别限制DAA采集、SMA typed API与业务独立事务。contracts README及既有高危授权需求保留Backend不遥控运行中CA、授权不代替本地执行的边界；旧CAF门禁合同不因此被当前新CA目标替换或视为已接通。

匿名标签只在事实接入边，既有业务／管理认证不变；新需求明确设备控制不在匿名通道。没有增加节点、CA功能、物理表、公开设备接口或匿名控制许可。合并的BIZ只是现有Backend业务与意图责任的图示边界，不额外规定物理存储或改变各合同保留策略。Runtime§8及其余正文原字节未改，原CA受控I/O边也未改。

据上述新候选、精确差异和独立边界审阅，**F-QA1-001于QA2关闭**。不是Development自行关闭，也不是以图边计数代替语义判断；原QA1发现及qa_failed完整保留。

### 7.5 AC01–AC20当前状态与证据沿用

“沿用QA1”均指第3节相应AC独立核验及第4节真实命令证据；它们通过§7.2的10个未改输入和原证据SHA关联到当前候选。未重新解析未改JSON、重算未改日期或重复阶段B／软件测试。Runtime非图正文完全未改、tasks旧前缀完整，故保留未受影响的原证据；表中标明本轮实际追加判断。

| AC | QA1历史 | 当前文档结果 | 当前证据链与QA2影响检查 |
| --- | --- | --- | --- |
| AC01 | 通过 | 通过 | QA1§3 AC01；Q2-A批准spec／12文件身份与tasks追加；§7.1实际新角色／串行handoff及当前metadata，无假Owner接受 |
| AC02 | 通过 | 通过 | QA1§3 AC02／Q06；DAA／SMA现状及Runtime非图正文SHA不变；不重新运行源码或读库 |
| AC03 | 通过 | 通过 | QA1§3 AC03；Q2-B／Q2-C及§7.4追加复核匿名事实与独立业务／CA权限，未扩匿名设备控制 |
| AC04 | 通过 | 通过 | QA1§3 AC04；共同需求／DAA／SMA同SHA，四行图修改不改身份／类型／命名规则 |
| AC05 | 通过 | 通过 | QA1§3 AC05、Q02／Q03；全部JSON及manifest示例所在文件同SHA，无新增JSON |
| AC06 | 通过 | 通过 | QA1§3 AC06；三类摘要／历史原文条款同SHA；Q2-A仅文本哈希，不重编码历史 |
| AC07 | 通过 | 通过 | QA1§3 AC07；回执合同未变；§7.4复核事实ACK／业务ACK图边保持独立 |
| AC08 | 通过 | 通过 | QA1§3 AC08及Q03；矩阵／错误示例原字节不变，无重记软件故障测试 |
| AC09 | 通过 | 通过 | QA1§3 AC09；逐点latest／源代次／CAS及聚合条款不变，B节点不再承担执行意图 |
| AC10 | 通过 | 通过 | QA1§3 AC10；质量／定义／停用／新鲜度正文同SHA |
| AC11 | 通过 | 通过 | QA1§3 AC11及Q03；history／cursor／checkpoint条款及例子同SHA，Runtime B到SMA读取边保留 |
| AC12 | 通过 | 通过 | QA1§3 AC12及Q02三日期例；上海三自然月及全部日期原字节不变 |
| AC13 | 通过 | 通过 | QA1§3 AC13；原文／投影／逐点截止／有限证明正文不变；不从BIZ合并标签推导新保留期限 |
| AC14 | 通过 | 通过 | QA1§3 AC14；Q2-C／§7.4复核两段持久确认、typed业务永久值和CA独立执行回执分开 |
| AC15 | 通过 | 通过 | QA1§3 AC15；spec B01–B08及共同需求§10同SHA，只是后续软件条件 |
| AC16 | 通过 | 通过 | QA1§3 AC16；spec D01–D08／DAA条款同SHA，未执行或预记通过 |
| AC17 | 通过 | 通过 | QA1§3 AC17；后续各自批准／Backend就绪及实际联调gate不变；tasks§7仍明确另批 |
| AC18 | 通过 | 通过 | QA1§3 AC18；双语demands/proposed和索引同SHA，没有provider发布／schema／实现宣称 |
| AC19 | 未通过，F1 open | **QA2通过，F1 closed** | QA1§4旧JSON／双语／日期证据沿用；Q2-A精确diff／保护、Q2-B局部结构／图边及Q2-C人工跨文档边界判断关闭本次唯一失败 |
| AC20 | 通过 | 通过 | QA1§3 AC20；DEV tasks完整历史＋新handoff与本次fresh-context记录分别存在；只写checklist，无软件／配置／库／设备动作 |

### 7.6 限制、资源、验收审计与handoff

本轮仅验证四行图修正、tasks追加以及旧证据可沿用性，没有重新扫描全树3208路径。QA1的3096／97／15是该轮共享树观测，不能当作QA2当前全树统计；SMA／Field Flow／Backend及索引并行工作继续保持其独立归属，本角色不回退、不合并，也不宣称全树未变。

Mermaid只做文本围栏、边关系和图文审阅，**未渲染**，没有视觉或完整Mermaid解析器证据；未访问外链。原24份交付JSON／31份含spec的语法、示例关系18项、双语对象11份及三日期例通过QA1原证据和精确未改SHA保留，不能描述为QA2新跑的整套验证。真实SQLite／env／profile始终未读未写，不用访问这些资料证明“全库字节不变”。

| 验收表面 | 当前真实状态 | 下一gate |
| --- | --- | --- |
| ARCH-AW-008 r1文档AC01–AC20 | QA2 qa_passed；F1关闭，QA1 qa_failed保留 | Human Owner决定文档最终验收 |
| Human Owner文档最终验收 | pending，未授予owner_accepted | 只可记录Human Owner真实决定 |
| Backend／DAA软件与B01–B08／D01–D08 | 未执行、未接受；当前仅定义后续条件 | 各自精确spec／批准、正式合同及真实软件／联调证据 |
| SMA／模块业务及CA执行功能 | 不由本轮新增、实现或运行验证 | 各自独立合同／批准／验收 |
| 发布／部署／数据库迁移／真实设备 | 未授权、未执行 | 具体动作独立批准 |

没有项目导入、测试／构建／安装、应用／监听进程、网络／API／DB、DS／PLC、Docker、迁移、Git写入或外发消息。没有本角色新建的检查器、临时源码、运行库或构建资源；只更新本checklist。原before／approval／QA1与返工镜像、manifest、DEV报告及diff仍有Owner审阅和追溯依赖，应继续保留，不在本轮清理。long-task-notifier及资源收尾仍由主协调办理，本角色未重复启动或发送通知。

本轮handoff由主协调转交Human Owner：**独立文档qa_passed，AC01–AC20当前通过；F-QA1-001 closed；QA1完整失败历史保留；Human Owner文档最终验收待定。** 只允许据此机械同步本任务PLAN/catalog摘要，不表示阶段C软件完成，也不触发Backend／DAA自动接续实施或实际联调。

QA2写入后回读审计：取第7节之前的QA1前缀，只恢复§7.1列明的三行，所得完整字节SHA仍为`62e148b8344c318ae893d1da7df866fff2ac4d08eceef989f71b29bd813ce4d9`，与持久QA1原快照逐字节一致。实际提取本文件Q2-A bash围栏，通过`subprocess.run(['zsh','-c',command])`复跑；仅将原“写入前live checklist相等”断言换为上述恢复前缀摘要断言，其余候选／旧证据／delta／DS检查不改，`RECORDED_Q2_A_REPLAY_EXIT 0`，11／12／12／10／13、四行／36行／4254字节结果保持。另以独立stdlib围栏／表格／本地链接解析器检查本checklist，得到5个本地链接、109表格行、5围栏块，`ERRORS []`；最后12份源／新快照再次核对为`FINAL_FROZEN_INPUT_MISMATCH []`。`git diff --check -- plans/ARCH-AW-008-stage-c-facts-contract/checklist.md`实际退出0。全部为文档与历史保全检查，没有新增软件或Mermaid渲染证据。
