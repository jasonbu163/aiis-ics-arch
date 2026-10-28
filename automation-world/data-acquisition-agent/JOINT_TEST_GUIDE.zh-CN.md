# DAA–DS 阶段 B 联调操作手册（试行 r2）

[English](JOINT_TEST_GUIDE.md) · [DAA-007 r2 spec](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) · [DAA](README.zh-CN.md) · [DS操作手册](../device-simulator/USER_GUIDE.zh-CN.md)

**r2已精确批准；供P2冻结后的Owner操作，M01–M09全部not_run。** r1时间/存储整改保留，r2增量为源码.env/profile、普通UI显式读取准入、标准Tauri入口和YAML常驻链退役。实际自检/候选见[tasks](plans/DAA-007-ds-joint-validation-and-time-contract/tasks.md)，只有coordinator确认P2 freeze并交付手册后才操作原生窗口。预期不是测试结果，Owner观察、闭库RO对账、fresh Verification及最终验收分别记录。

**升级限制。** 新版仅对真正新空profile初始化上海时间双库v2。旧UTC v1、缺失/未知合同写前只读拒绝，原配置/历史/raw/SHA保留，不自动迁移或旁建。原profile须用原兼容版本，迁移/降级另批。local-acquisition-v1只是目录定位。本轮只沿用原Owner合成profile，不用默认目录，不创建第三套profile，不复制DEV fixture/测试库。

## P00｜一次性配置与运行前核对

正式源码 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`（dirty，本任务增量独立记录），r2候选以tasks freeze清单为准；运行中无热改。原RUN_ROOT=`/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run`。B0仅确认两个原profile仍为空、非symlink且未开库。Owner启动前再次确认归属/状态和15191/15194/30102/30103端口；冲突停步，不kill未知进程、不改端口求过。

DS当前版本、DS-001 r1及ARCH-AW-005 r5已于2026-10-27被Owner接受，见[既有接受记录](../device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)。旧QA4/DS-001/DIRECT与本r2 DS bootstrap增量分别保留，DS独立QA例外不转移至本任务。r1规划227 DS/158 DAA/12 core的漂移与只读归因见tasks历史；本r2按新before/51实现清单/保护审计固定候选，不用旧pass代替新delta。

Owner在两个应用根目录分别手工将 `.env.example` 复制为 `.env` 后编辑；**已有.env不覆盖**，只核对/编辑自己的活动profile键。Agent不读写这些真实文件。一次填入：

DAA：`automation-world/data-acquisition-agent/.env`

```dotenv
DAA_PROFILE_DIR=/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run/daa-profile
```

DS：`automation-world/device-simulator/.env`

```dotenv
DS_PROFILE_DIR=/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run/ds-profile
```

两键只选择存储根：非空进程 > 自身.env非空值 > 原默认，空键不是新空目录。仅绝对字面路径，无父目录穿越/symlink，不展开`~`/`$VAR`/`${VAR}`或执行shell；一层配对引号、重复键首项生效。不存在默认.env可用默认；显式DAA_ENV_FILE错误、默认.env不可读/非UTF-8和非法profile都写前拒绝，不降级。DS没有DS_ENV_FILE。Vite envDir:false保持。dev/build不会自动隔离数据；安装版.env发现/分发不在本次支持内。

一次检查各启动终端曾继承的覆盖键，勿输出整份环境或凭据。若原r1 `DAA_ENV_FILE` 仍指向RUN_ROOT/daa.env，它优先于应用根.env；该旧合成文件是历史材料，Agent不改/删。Owner按需一次 `unset DAA_ENV_FILE DAA_PROFILE_DIR DS_PROFILE_DIR`，仅在有旧覆盖时做；若进程 `DAA_RUNTIME_MODE=legacy_snapshot` 残留也按需unset。旧YAML locator已忽略，普通启动不读/散列它们，不迁入PLC_1。

普通native无需.env读授权。Owner可从自有.env一次删除旧DAA_PLC_READ_ALLOWED或理解其true/false均忽略。高级同名**进程**键确实缺失才默认允许后续UI动作；合法true不额外禁止，false/空/非法/不可解码均拒绝读，文件true不能覆盖deny。此次普通联调要求记录进程读键未设置；如有无意继承覆盖，Owner按需一次 `unset DAA_PLC_READ_ALLOWED`，不以文件true修复，不每次带长命令。保留停止初态与启用/地址/激活/容量/日志/时间保护。

| 运行前记录 | 待Owner实际确认 |
| --- | --- |
| 版本/驱动 | 新freeze候选；DAA Tauri build.features=[rust-snap7-driver]、local-validation关；DS native-s7、test-automation关 |
| 配置来源 | 两个根.env实际profile解析路径及来源，普通进程读键未设置；无默认/旧库误选 |
| 归属/端口 | 原Owner两个profile仍符合P00前置，15191/15194/30102/30103无冲突 |
| 初态 | DS/DAA无连接、无运行/启采；空DAA无PLC_1，无新迁入receipt |
| 数据保护 | 真实现场/默认库不操作；旧UTC门禁与v2/上海时间证据见tasks，不让Owner试开旧库 |

## M01｜正常短命令启动两个桌面程序

完成一次性.env配置并获coordinator freeze通知后，每个终端仅执行：

终端A：

```sh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator
pnpm tauri dev
```

终端B：

```sh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent
pnpm tauri dev
```

DAA的Tauri配置统一携带已有rust-snap7-driver（Snap7为S7通信编译实现），DS沿用native-s7，不手填feature/驱动别名。记录实际命令、候选/features、解析profile及来源、普通进程读键未设置、两个应用停止初态。预期原生双窗口、空DS实例与空DAA PLC列表、无S7监听/连接/启采（Vite端口可监听）。存在对象/历史表示需先核路径/归属，不能删库求空。PLC端点、点位/组/周期等业务配置在UI+SQLite，保存/激活/加载与工作台连接/启采/暂停/断开分开，无全局SQLite读取开关、无自动启动/运行意图恢复。

## M02｜在 DS 建立两台可区分的模拟 PLC

先完成 A 的配置及静态核对，B 可在 M06 时再建立，避免第一次同时操作两台。

1. DS“配置中心 → 实例”：新建 `B007-A`，端点 `127.0.0.1:30102`；rack `0`、slot `1`、Calling TSAP 十进制 `256`（0x0100），对应 Called TSAP `257`（0x0101），连接/握手上限保持 `16/4`。**保留编辑 → 保存候选**。
2. “DB 点位”选择该实例，按 [DS 手册 §3](../device-simulator/USER_GUIDE.zh-CN.md#3-多-db--udt-只读导入)同时选下列只读来源，扫描后只勾 `Alpha` 和 `Beta`：
   - `automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-multi-db/multi.db`
   - 同目录 `types.udt`；Alpha 不依赖 UDT，Beta 的闭包仅选择 `Measure`。
3. Alpha 填 DB `71`，Beta 填 DB `88`；预览并确认导入。每 DB 分别“预览标准地址 → 确认”，再核命名。不要选择 Gamma/Delta/Epsilon/Zeta，不修改来源文件。
4. 在策略页逐点设置下表，点启用、客户端读取全部允许；未写明的写入禁止。DS 初值必须显式设置，`count := 7` 及 `BEGIN` 不作为导入初值。保存并确认所选初值/策略。表内技术名为预期候选，两端按地址核对，不要求 UUID 相同。

| DB / 长度 | 原路径 / 类型 / 地址 | 技术名 | A 的 DS 初值 | B 的 DS 初值 | 策略 |
| --- | --- | --- | --- | --- | --- |
| 71 / 4 B | ready / BOOL / 0.0 | DB71_ready_Bool | false | false | 布尔翻转、owner规则；翻转半周期1000ms（完整周期2000ms），通用periodMs填2000、phase=0；三类写入禁止 |
| 71 / 4 B | count / INT / 2 | DB71_count_Int | 101 | 202 | 保持、owner界面、界面普通写允许 |
| 88 / 8 B | unit.running / BOOL / 0.0 | DB88_unit_running_Bool | false | true | 保持、owner无、三类写入禁止 |
| 88 / 8 B | unit.value / REAL / 2 | DB88_unit_value_Real | 12.5 | 25.0 | 保持、owner界面、界面普通写允许 |
| 88 / 8 B | bytes[3] / BYTE / 6 | DB88_B6_Byte | 18 | 86 | 保持、owner无、三类写入禁止 |
| 88 / 8 B | bytes[4] / BYTE / 7 | DB88_B7_Byte | 52 | 120 | 保持、owner无、三类写入禁止 |

5. toggle按`halfPeriodMs`每半周期翻转，界面没有`base`字段；false是初始化值，不是持续规则参数。其余规则字段保留既定合法默认值。DS“实例”：选最新保存版本 → 预览加载与保值 → 核对六点/DB号/长度/初值 → 确认加载并保持停止。到“工作台”显式启动 A；随后**暂停规则**，保持 S7 服务可读。
6. “在线值”核六点。count/REAL/BYTE 应等于本次加载的表中值；ready 启动后可能已翻转，以暂停后的实际快照为准。记录 loaded 版本，保存候选不等于已加载。

失败时保留错误：地址/命名未确认先回相应步骤；策略未确认先核所选点；读被拒绝先核客户端读取和启用，不开放无关写权限。

## M03｜在 DAA 配置第一台 PLC、点位和组

1. DAA“配置中心 → PLC 配置”：新增 `B007-A`，`127.0.0.1`、端口 `30102`、rack `0` / slot `1`；PLC 启用。超时保留既定默认，保存草稿。保存不会连接。
2. “点位与采集组配置”选 A，在“来源文件与完整结构”同时选 M02 的两份来源；确认识别 6 DB/3 UDT，只勾 Alpha/Beta，分别填 71/88。预览完整差异 → 确认导入。
3. 依次选 Alpha、Beta，“辅助地址推算 → 预览标准布局偏移 → 确认非人工偏移”。核对 M02 的长度/地址/类型及六个技术名；人工地址不要批量覆盖。
4. 展开“采集组与周期”：添加并启用 `Fast_500`（500 ms）、`Slow_1000`（1000 ms），保存草稿。逐点编辑弹窗：两个 BOOL 分配 Fast，INT/REAL/两个 BYTE 分配 Slow；六点均启用，保持已确认地址。每点只归一个组。
5. 使用逐点弹窗分组，不使用“将当前筛选点分配到组”给全体误分组；表头勾选用于命名选择，不等于采集开关。保存草稿后检查每行组/启用/地址，再显式“激活配置”并确认。
6. 核运行配置已应用且仍未连接、未启采。若提示 pending 名称、组缺失、未确认地址、dirty 或编辑中，修正所指对象再预览/保存，不重复激活猜测。

## M04｜连接、单点核对与首次采集

1. DAA“工作台”只对 A 点“连接”，等操作完成。DS A 应新增一条 DAA 会话。需要时用 DAA 连接测试及点位的单点诊断核 M02 值；诊断复用连接，不另建长期客户端。
2. DS 保持规则暂停；DAA A 点“开始采集”，等约10秒，再“暂停采集”。暂停采集通常保留连接；“断开”是另一个动作。
3. “上报与存储 → 本地历史”查 A：Fast/Slow 都有新历史，DB71/88 都出现；“查看样本”弹窗打开原包、完整轮 manifest、配置上下文。核来源 `s7`、质量 `good`、待传 `pending`、原文 SHA。
4. 按 PLC/DB/原路径/地址/类型比对 DS 暂停后的实际值。JSON 点字典按 DAA point ID，不能凭另一端 UUID 查找。REAL 本例取可精确表达的12.5/25.0；动态浮点以后按类型精度核。

一轮组采集跨两个 DB，预期一轮两份 DB 样本、同一个 cycle ID 和完整 manifest；Fast 两个BOOL，Slow 四个其它点。组间/跨 DB 读取不是 PLC 原子快照。序号在一个 PLC 的多个组之间共用，筛选某组有跳号正常。你不必手算全部记录，协调者在最终正常退出后做只读同库对账。

## M05｜变化值与不同采集周期

1. DS A“恢复规则”；DAA A 再“开始采集”。约15秒内 ready 应有 true/false 两类正常历史，unit.running 保持当前设置。
2. DS A 在线值对 count 用**普通写入**，将101改为111；对 REAL 将12.5改为13.25。逐项核 loaded revision/旧值及确认提示。该操作是 DS 界面写内存，DAA 仍只通过 S7 读取。
3. 等数秒，再暂停 DS 规则，记录当前 DS 快照；DAA 新正常样本应读到111/13.25，旧样本仍保留旧值，不回写历史。
4. Fast/Slow 的实际采集间隔应分别接近500/1000ms，正常稳定区间 Fast 轮次约为 Slow 两倍。UI 约1Hz刷新不能证明采样频率；协调者按实际组轮起止和读/保存耗时对账，不要求毫秒硬实时或从一页行数算比值。

## M06｜第二台 PLC 与同号 DB 隔离

1. 保留 A，按 M02 建 DS `B007-B`，仅端口改为 `30103`，采用表中 B 初值；加载、启动并暂停 B 规则。
2. DAA 暂停 A 采集，按 M03 新增 B，端口30103；相同来源、DB71/88、两组及六点。保存/激活后检查 A 的草稿、ID、地址和历史保留；激活可能更新运行版本，按工作台实际状态重新连接/开始，不能当作自动恢复。
3. 分别连接并启动两台 DAA PLC。核 DS 每实例各一条 DAA 会话，B count/REAL/BYTE 为202/25.0/86/120，A 为本次实际运行值，历史按 PLC 筛选不串值。
4. 正常采集数秒后，在 A 做一次单点诊断；B 继续、A 仍复用其连接。除本轮两条 DAA 会话外不启动其它客户端，避免用连接总数误判复用。

## M07｜断线、另一台持续运行与恢复

1. 两台采集中，在 DS 仅**停止 A**，B 保持服务。记录动作时间，等约5秒，观察 DAA A 进入故障/重连状态，B 仍有新的正常历史。
2. DAA A 的失败样本若有，应为明确错误质量/null及原因；断线期间也可能没有提交轮。不得把上次好值标成新好样本，也不承诺补回未读到的 PLC 值。
3. 在 DS 重新启动 A；DAA 若仍保留连接/采集意图，应在退避窗口内重新连接并出现新的 good 样本。当前退避上限含抖动约36秒，观察窗口给到45秒；超出先记错误/意图/时间，不反复点连接或换端口。
4. 核 B 始终继续；A 的 hold 值是否保留按 DS 的同进程停止/重启语义核对。DS“重置运行值”、退出重开会涉及初始化，本步骤不代替这些动作。

## M08｜时间、历史筛选与详情

1. DAA 逐台“暂停采集”，等在途轮完成。查每台/每组/质量，翻一次页、打开任意样本详情；待传仍是 pending，不能上报、ACK或清队列。
2. 采集/保存等业务时间在普通界面按上海时间 `YYYY-MM-DD HH:mm:ss` 显示到秒；原包/普通 IPC 中的新时间携带 `+08:00`，毫秒原值仍保留。savedAt 是保存事实，不是刷新时间。
3. 日期时间选择器按上海日历选择覆盖本轮采集的起止；边界规范为起始秒`.000`至结束秒`.999`的闭区间，结束秒内的毫秒样本不能漏掉。已知样本应能查到；起始晚于结束应明确报错，清空后恢复查询。重复刷新不改变原样本时间、值或 SHA。
4. 历史表拖动一个普通列边界，翻页/筛选/离页再回来应保留；“恢复默认列宽”只清本表偏好。再拖一次，留待 M09 重开核本机记忆。选择/操作列可以固定宽度。
5. 记录一个 A、一个 B 的 sampleId/cycleId/SHA及对应组；展开 manifest/context 后关闭。无需拷贝全部大 JSON 或手工操作 SQLite。

开发负责非本机上海时区环境的定向检查，不要求你改系统时区；旧 UTC 门禁也使用开发自造库验证，不能尝试改默认库时间。

## M09｜正常退出、重开与交接

1. DAA 两台都暂停采集、断开；等 DS 两台 DAA 会话释放。确认没有未保存编辑，前置 DAA 窗口，Cmd+Q 正常退出一次；不要强杀。回复“**M09首次退出完成**”，先保持DAA关闭；协调者只读记录首次闭库基线后会通知可重开，用于证明下一步未改旧样本，不要求你重做采集。
2. 收到首次对账已记录的通知后，用 M01 **相同.env和原Owner profile** 重开 DAA，不重新生成 env 或profile。预期两台配置、六点各自分组、历史及所记 sampleId/SHA 保留；两台均未连接、未启采。历史表列宽记忆仍在，恢复默认后正常。
3. 查询历史、打开所记两份样本，随后再正常退出 DAA，供协调者对隔离双库、日志和原字节做只读对账。DS 两台停止后正常退出；不要求反复三轮关窗。
4. 保留本批次数据直到问题核对及最终验收。协调者先归档必要证据，确认无运行/后续依赖后，只清本任务自有数据；不删默认目录、不清共享target、不删除原DB/UDT。

M09另记录实际解析profile/来源、相同r2候选/features、普通进程读键未设置及停止初态。首次退出后等待DEV只读checkpoint通知，再同profile一次重开；不重复M02–M08。

## 常见阻断

| 现象 | 先核对 |
| --- | --- |
| `driver_unavailable` | 核对普通pnpm tauri dev所用正式候选及Tauri build.features，local-validation关闭 |
| 连接失败/持续重连 | DS是否已加载并启动，所选PLC、端口、rack/slot和TSAP是否一致；保存候选本身不启动监听 |
| `bad_read` / 值为null | 同号DB是否实际存在，地址和长度、点启用及客户端读取权限；先暂停规则对照实际loaded配置 |
| 激活按钮不可用 | 当前弹窗、未保存草稿、点位组、pending技术名、地址确认及错误提示；表头勾选不是启采 |
| 旧时间合同/未知schema提示 | 保留原库，停止使用该profile做新版联调，回P00核新目录；不清库、不改时间、不改schema |

## 反馈记录与定稿

填写实际结果；未操作写 `not_run`，受阻写 `blocked`，记录阶段编号、页面、按钮、原输入、实际提示及大致时间。可反馈文字，截图按需要提供，不要求替工具编造结果。

| 阶段 | 操作人/批次 | 实际结果（初始 not_run） | 问题/复核范围 |
| --- | --- | --- | --- |
| P00 | 待填 | not_run | 版本、DS基线、路径及端口 |
| M01–M03 | 待填 | not_run | 启动、DS配置、DAA配置 |
| M04–M05 | 待填 | not_run | 静态/动态值、周期 |
| M06–M07 | 待填 | not_run | 多PLC、连接与恢复 |
| M08–M09 | 待填 | not_run | 时间、历史、正常重开 |

先以试行版走一次，问题只修受影响项并补录复核。Development 自检、Owner 原生观察、退出后只读对账、新 fresh-context Verification 和 Owner 最终接受分别记录；独立核验不伪称由工具操作了窗口，也不重复整套 DS/DAA 压测。手册步骤实测可用并经 Owner 确认后才定稿。

DAA-007 接受不自动代验 DS-001 或旧 DAA 任务；阶段 B 汇总关闭需相应有限基线与本闭环证据、Owner明确接受。阶段 C 可靠上报、后端/SMA、真实 PLC、生产数据库/API和现场切换继续另立范围。
