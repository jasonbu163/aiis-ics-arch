# 阶段 C 事实投递手册

[English](STAGE_C_GUIDE.md)

**本页说明 DS → DAA → 本地 SQLite 采集及 DAA-010 样本上报。** ARCH-ACQ-004 r2 精确候选已通过隔离独立验证；下方 r3/r4 单表步骤仅适用于已采用该合同的目标。ARCH-ACQ-004 r4 整体状态及实际环境采用以各自任务记录和授权为准；DAA 原生界面与 Windows 按各自记录处理。本手册不代表实际环境已切换。后半部分保留 DAA-008 B-RUN-01 联调历史。[阶段 B 验收](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 规格](plans/DAA-010-sample-facts-upload/spec.md)

## 已有项目 dev 配置时

如 DS 和 DAA 已分别使用各自的 `.local/dev`，且模拟 PLC、DB、点位和采集组已配置，先核对两应用实际选中的 profile、端点与现有配置，继续使用原目录；不必按下方隔离示例重新建目录或重新导入点表。实际后端采用和初始化按获批目标执行，先查看[项目 dev 启动说明](../../INITIALIZATION.zh-CN.md#宿主机源码开发与-database-only)及[r3/r4 单表迁移与恢复](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md#r3-单表迁移与恢复)及 [r2 前驱迁移、导入与恢复](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md#r2-候选迁移导入与恢复冻结前驱工具)。

已有待传或结果未知样本时，先核对并保全采样时的原实例 ID、PLC ID、DB 和代次；已冻结或尝试过的样本，还应核对并保留详情中已有的目标、正文和回执。待传样本可能尚未冻结，其目标、正文或回执为空并不表示丢失；不要用当前设置猜测或改写原身份。复用后端已有活跃来源时，核对它与原队列身份一致；已知旧代次不能重新登记时，先处理旧队列，新代次仅用于新采样，不给旧样本换身份。确认目标已采用后，从[来源登记与单样本核对](../../docs/acquisition-data-guide.zh-CN.md#7-从采集到上报核对一份样本)和下方第 5–7 节继续。开始上报会逐份处理可发送队列，可能不止一份。

## 隔离环境操作

### 1. 选择环境

使用新建并显式选择的 DS profile、DAA profile 和获准的隔离后端目标。启动前核对实际地址及端口是否空闲；下表只是示例，不表示服务正在运行。使用现有项目 dev 后端、MySQL 或 `.local/dev` profile 前，须取得 [DAA-010 第 7 节](plans/DAA-010-sample-facts-upload/spec.md#7-交接实际采用和-windows-后续)的具体运行批准，才能登记、迁入或上报。

| 用途 | 示例地址 |
| --- | --- |
| DAA 后端地址 | `http://127.0.0.1:38117` |
| 项目 Web | `http://127.0.0.1:5190` |
| 隔离 MySQL，仅供后端使用 | `127.0.0.1:33317` |
| 本例 DS 模拟 PLC 的 S7 监听 | `127.0.0.1:31281` |

本地采集练习只需 DS 与 DAA；其他服务按各自获准环境启动。详见[项目初始化](../../INITIALIZATION.zh-CN.md)。

### 2. 启动 DS 和 DAA

各应用分别读取自身目录的 `.env`。本例选择各自项目目录下新建的 `.local/daa-v2-isolated`，配置时将以下模板的 `/absolute/path/to/aiis-ics-arch` 换成仓库实际绝对路径。

```dotenv
# automation-world/device-simulator/.env
DS_PROFILE_DIR=/absolute/path/to/aiis-ics-arch/automation-world/device-simulator/.local/daa-v2-isolated
```

```dotenv
# automation-world/data-acquisition-agent/.env
DAA_PROFILE_DIR=/absolute/path/to/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-v2-isolated
```

已有 `.env` 先核对对应键。路径写绝对字面值，不展开 `~` 或环境变量。终端中已导出的非空 `DS_PROFILE_DIR` 或 `DAA_PROFILE_DIR` 优先于 `.env`；DAA 的 `DAA_ENV_FILE` 还能改选环境文件。曾在当前终端设置这些变量时，先核对其值，清除不再需要的旧选择后再启动。各应用使用相互独立的 profile。

Windows 10/11 x64 后续实测时，在 DAA 目录用 PowerShell 选择独立的本机绝对路径，例如 `$env:DAA_PROFILE_DIR = 'C:\DAA\isolated'`，再执行 `pnpm tauri dev`。该说明不是 Windows 原生构建、热 journal 或设备验证结论；实际测试及结果按 DAA-010 AC08 记录。

从仓库根目录分别在两个终端标签运行以下命令。`mkdir` 不会覆盖已有 profile；如果同名目录已存在，先核对并选择另一个新名称。

```zsh
cd automation-world/device-simulator
mkdir -p .local
mkdir .local/daa-v2-isolated
pnpm tauri dev
```

```zsh
cd automation-world/data-acquisition-agent
mkdir -p .local
mkdir .local/daa-v2-isolated
pnpm tauri dev
```

两程序已经使用上述 profile 运行时可直接继续。全新 profile 的实例和 PLC 列表为空，既有 profile 按下述版本和批准规则处理。DAA 的配置和采样分别存于 `local-acquisition-v1/config.sqlite` 与 `runtime.sqlite`，DS 配置存于 `device-simulator-v1/config.sqlite`。保留已有 `.local` 配置、样本及历史归档；换一个空 profile 会建立新的配置和历史。 [DAA 存储](README.zh-CN.md#配置权威与启动) · [DS 存储](../device-simulator/README.zh-CN.md)

### 3. 在 DS 配置一台模拟 PLC

本例使用仓库内两个受控文本样例：[minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) 和 [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt)。在文件选择器中同时选择这两个文件。已有同名实例时先核对端点和 DB，从未完成的步骤继续。

1. 在 DS 的“配置中心 → 实例”创建 `DEV-PLC-A`，IPv4 为 `127.0.0.1`、端口为 `31281`、机架 `0`、槽位 `1`、客户端 TSAP 为十进制 `256`。完成编辑并点顶部“保存草稿”。本例 rack/slot 对应 Called TSAP `257`。
2. 打开“DB 点位”，选择 `DEV-PLC-A`。在“多源 DB / UDT 导入”同时选上面两个文件，来源保持“作为新来源”，点“扫描声明”。勾选 `MinimalImport`，目标选“新增 DB”，DB 号填 `21`。`MinimalPayload` 会自动关联，核对无缺失提示后点“预览导入差异”，确认导入并保存草稿。
3. 选择导入的 DB21，点“预览标准地址”并确认，核对 DB 长度为 `8` 字节及下表地址。勾选三个点，点“预览所选点命名”，核对后确认。新导入的 DB 和三个点默认启用。
4. 打开“模拟与读写策略”，选该实例和 DB21。逐点“编辑策略”，将模式设为“保持”、唯一写入来源设为“无写入 owner”、客户端读取设为“允许”，其余三种写入设为“禁止”。勾选“DS 显式初值”的“显式覆盖”，分别输入下表初值，每次点“完成编辑”。勾选这三个点，点“保存草稿并确认所选初值/策略”。
5. 顶部依次点“保存草稿”和“保存为版本”，核对并确认。回“配置中心 → 实例 → 配置版本与加载”，选 `DEV-PLC-A`，在新版本行点“预览加载”，核对清单并勾选确认，点“确认加载并保持停止”。到“工作台”启动该实例，再到“在线值”核对下表。

| 原始点位路径 | 类型 | DB21 地址 | DS 显式初值 |
| --- | --- | --- | --- |
| `payload.ready` | BOOL | `0.0` | `false` |
| `payload.count` | INT | `2` | `0` |
| `payload.temperature` | REAL | `4` | `12.5` |

以上地址是此样例的标准布局推算结果。源文件中的声明初值和 `BEGIN` 不作为 DS 初值导入。保存草稿、保存版本、加载和启动是独立操作。[DS 操作手册](../device-simulator/USER_GUIDE.zh-CN.md)

### 4. 在 DAA 配置并检查本地样本

1. 在“PLC 配置”添加并启用 `DEV-PLC-A`，填写 `127.0.0.1:31281`、机架 `0`、插槽 `1`，完成编辑并保存草稿。
2. 打开“点位与采集组配置”，选择该 PLC，展开“源文件与完整结构”，同时选择第 3 节的两个文件。勾选 `MinimalImport` 并填 DB 编号 `21`，预览导入差异，再确认导入并保存。
3. 选择 `MinimalImport · DB21`，展开“辅助地址推算”，点“预览标准布局偏移”，核对上表地址及长度 `8`，再点“确认非人工偏移”。
4. 展开“采集组与周期”，添加一个启用的采集组，例如 `G1_1000`，周期设为 `1000 ms`。在点表勾选上述三个点，点击该组的“将已选点启用并分配本组”。保存草稿，点“激活配置”并确认。
5. 到“工作台”对 `DEV-PLC-A` 点“连接”，成功后点“开始采集”。采集约 5 秒后点“暂停采集”。打开“上报与存储 → 本地历史”，查询并打开一份 DB21 样本，核对三个点的值和质量。上报保持停止。

### 5. 现有目录与新上报

新空 DAA profile 建立 config2/runtime4，启动时采集和上报均停止，上报来源为空。未绑定时仍可采集；这些样本标为「仅本地记录」，之后填写绑定也不会自动排入上报队列。符合原打开条件的冷态 runtime2/3 继续使用同一目录进行本地采集及历史查看，不自动升级上报。

ARCH-ACQ-004 r2 候选对通过原结构、身份和完整检查的 runtime4 提供同目录兼容：保持数据库 inode、原采集配置、样本及冻结正文，将上报身份独立保存。既有可上报记录保留原身份及目标规则。该精确候选已通过隔离独立验证，实际目标采用仍需单独完成；不能推定真实 profile 已完成升级。[QA5 记录](../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa5)

若显示初始化/身份升级未完成或凭据不匹配，停止并保留整个原目录、数据库、journal、sentinel 和 staging，留待核对；不要手动删除、重建或复制文件冒充原 profile。

不要删除 journal、marker 或凭据，不复制 sealed 文件冒充原 profile，也不要用旧二进制打开新版库。未知 schema、缺库、身份或时间不符时按提示保留原件。实际 `.local/dev` 采用、备份、目标切换和回退另行批准。

### 6. 登记来源并开始上报

1. 在获准后端，以管理员进入 Web「采集数据 → 来源配置」，按目标实际采用的版本操作：

   - **已采用 r3/r4 单表的目标：**每台 PLC 登记一行，填写 `plcId`、`instanceId`、`sourceGeneration` 和 `sourceType`（DAA 选 `daa`）。`sourceType` 仅用于标注和展示，不参与 POST 准入，也不放入样本正文。POST 准入核对前三项标识。`dbNumber` 仍是样本字段和查询筛选项，不登记 DB 读写清单。保存后复制该行仅含三项标识的「接入参数」。
   - **尚未切换的旧 r2 目标：**登记类型 `daa`、PLC ID、实例 ID、来源代次和明确授权上报的 DB，并另行授权需要读取的 DB。该目标继续按既有 DB 写入和读取范围运行。保存后复制「接入参数」。

   两种目标均为新来源选择从未使用过的新代次；如有原队列并复用已有活跃来源，先核对原身份。
2. 在 DAA「上报与存储 → 上报设置 → 上报来源」，每台本机 PLC 一行，分别手填或粘贴实例 ID、上报 PLC ID 和来源代次。不同 PLC 可以使用相同或不同实例 ID；同一上报 PLC 更换实例时须使用新代次。支持仅包含三项的 JSON，也兼容旧的带 `dbNumbers` JSON；界面的 DB 始终来自本机已生效采集配置，粘贴材料不修改 DB。暂不绑定的三项均留空。保存不会验证后端或启动上报。填写服务地址（含端口）和路径，默认路径 `/api/v1/integration/plc-facts/samples`，核对完整 URL；异机时填后端机器地址，`127.0.0.1` 是 DAA 本机。上报间隔 1–3600 秒，默认 5 秒。
3. 保存绑定后重新采集一轮，再逐项核对目标、合同以及每个实例 / PLC / DB / 代次（含符合条件的历史待传来源），显式开始或继续上报。每个 POST 提交一份完整 PLC/DB 样本；实时和补传共用身份、原字节及回执规则。页面区分待上报、结果未知、需处理和已确认；历史 v1 确认不计入 v2。只有匹配原请求的有效 `committed` / `created|duplicate` 回执才确认，HTTP 状态或 GET 读回不能代替回执。[当前开发合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
   在“上报记录”按状态筛选，每条记录可分别打开“查看样本”和“投递详情”；前者显示采集时保存的点值、质量和配置上下文，后者显示目标、正文摘要与只读回执。列表的 PLC 名称来自当前已保存配置，历史身份以 PLC ID 为准；找不到名称时显示 ID。状态统计变化时列表会重新读取，也可手动刷新。列宽可拖动并恢复默认。
   “本地存储”显示运行库与回滚日志占用、待上报字节、最早待上报时间和当前生效的保留期。展开的策略表单显示草稿值；修改后，使用页面顶部配置栏保存草稿并显式激活。没有活动配置时不推断生效策略。本地历史与运行事件位于页面下方的折叠区。
4. 另用后端 GET 或项目 Web 核对。已采用单表的目标须核对 PLC 登记及查询条件；有符合条件事实的 DB 无须登记读取清单即可读回。未切换的 r2 目标仍须确保既有读取范围覆盖该 PLC/DB。当前开发合同免机器 Bearer。自定义 POST 路径不能推导 GET 地址，需向部署方确认读取地址；无法读取时仍可查看本地样本、请求及回执。

### 7. 暂停、目标变更与恢复

暂停阻止新派发，在途请求仍按原尝试结算。重开后采集和上报均停止。改地址或路径会暂停上报；核对新目标来源登记后显式继续，从未发送的样本可使用新 URL，已冻结正文保持原字节。已尝试但未确认的样本继续绑定旧 URL；可恢复旧地址继续，或打开结果未知样本的投递详情，按实际部署配置核对旧、新 URL 指向同一个 provider 逻辑目标和同一个数据库，并确认来源登记，再点“核对同一目标并继续原样本”。该操作记录地址和确认，不制造回执；后续仍以原身份、原字节重试。通达、版本相同或 GET 读回不足以证明同一数据库。无法确认时保留待核对，不向不同数据库或新来源代次改投。

## 历史记录 · DAA-008 B-RUN-01

从“M01 启动方式”到本页末尾均为原样保留的历史 v1 联调材料，包括旧 `/batches` 命令、凭据、目标标识、读取与恢复规则，只供追溯，不作为上述 v2 流程的操作指令。资源和命令描述当次环境，不推断其当前状态。[批准记录](plans/DAA-008-reliable-facts-upload/spec.md#r4-b01-f7-owner-approval) · [运行记录](plans/DAA-008-reliable-facts-upload/tasks.md)

<a id="m01-launch"></a>

## M01 启动方式

DAA 是一个独立的采集应用。M01 用另一个独立应用 DS（Device Simulator）提供 C008-A/B 两个模拟 PLC。若本次隔离 DS 已运行且这两个实例均就绪，只启动 DAA。若两者都要启动，同一个终端窗口开两个标签页或分屏即可，因为每条 `pnpm tauri dev` 都会在前台持续运行。日常单独使用 DAA 时，在 DAA 项目目录运行 `pnpm tauri dev`，按需在 DAA 自己的 `.env` 中填写 `DAA_PROFILE_DIR`。 [日常启动说明](README.zh-CN.md)

**本次 M01 无需编辑任一项目根目录的 `.env`。** DAA 专用文件 `.local/daa-008-r2-b01-ops/config/daa-launch.env` 已在 DAA 项目目录下备好，内容仅为下面一行。

```dotenv
DAA_PROFILE_DIR=/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01
```

下面的变量只传给各自的启动进程。DAA 通过 `DAA_ENV_FILE` 选中专用文件，并用进程 `DAA_PROFILE_DIR` 固定本次目录。终端若已有 `DAA_PLC_READ_ALLOWED`，命令会停在提示处，先核对继承设置。

```zsh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent &&
if [ "${DAA_PLC_READ_ALLOWED+x}" = x ]; then
  printf '%s\n' '此终端已设置 DAA_PLC_READ_ALLOWED，请先核对继承的启动配置。'
else
  DAA_ENV_FILE="$PWD/.local/daa-008-r2-b01-ops/config/daa-launch.env" \
  DAA_PROFILE_DIR="$PWD/.local/daa-008-r2-b01" \
  pnpm tauri dev
fi
```

需要启动 DS 时，在另一个标签页执行以下命令。DS 进程用 `DS_PROFILE_DIR` 固定本次目录，启动时仍按获批例外自动读取自身根目录的 `.env`。由程序自行读取即可，若文件不可读或不是有效 UTF-8，停止并报告。 [DS 读取例外](plans/DAA-008-reliable-facts-upload/spec.md#r3-ds-env-exception)

```zsh
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator &&
  DS_PROFILE_DIR="$PWD/.local/daa-008-r2-b01" pnpm tauri dev
```

## 协调方准备与运行边界

沿用已核验的 B01 路径、端口和候选。遇到非预期目录、端口占用、symlink 或候选漂移时暂停并核对。DAA 封存后的隔离 profile 使用原位置。 [B01 资源和停止条件](plans/DAA-008-reliable-facts-upload/tasks.md#b01-proposal)

| 项目               | 本次固定值                                                                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DAA 最终 profile D | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01`                                                   |
| DS 最终 profile S  | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator/.local/daa-008-r2-b01`                                                         |
| 私有操作/证据根 O  | `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/daa-008-r2-b01-ops`；0700，新配置 0600                            |
| DS 两实例          | C008-A / C008-B，新 GUI 生成真实 UUID 后记录；S7 `127.0.0.1:31281` / `:31282`，rack0/slot1，Calling TSAP256/Called257，连接16/握手4                          |
| API / DAA origin   | upstream `127.0.0.1:18283`，单 worker 无 reload；固定三 API relay origin `http://127.0.0.1:18281`，不直接更换 origin                                         |
| MySQL / 目标       | `mysql:8.4.6`，`127.0.0.1:13381`；alias `daa008-r2-b01-db`，schema `daa008_r2_b01`，targetAlias/targetId `daa008-r2-b01`                               |
| Docker 新资源      | container `daa008-r2-b01-mysql`、volume `daa008-r2-b01-data`、network `daa008-r2-b01-net`，label `aiis.task=DAA-008-r2-b01`，无自动 restart              |
| schema / 时间      | 仅 `0a2c4e6f8b10` / BE009-B / 71 应用表（另 alembic_version）；F7 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`；RR、上海 +08:00 |
| 期限 / 容量        | 原值 3 自然月；稳定 proof 120 天；新批 24h 准入另计。后端采用 budgets 1073741824 value bytes / 1000000 proof rows                                                |
| 普通前端监听       | DAA15191、DS15194，Tauri 配置不改；新 profile 中启动均停止                                                                                                       |

协调方和后端责任方按以下边界准备及运行：

1. 冻结 tasks 列明的 DAA、backend/三机器合同、DS/runtime/shared-core/锁文件候选，核新增资源为空、端口可用及现有依赖。只为新专用库建账号和 schema，显式 base→`0a2c4e6f8b10`，不 `upgrade head` 到 BE010。root 仅建库/账号/授权；`daa008_migrator` 仅专用 schema 迁移权限，随后停用运行凭据。`daa008_app` / `daa008_maint` 各有全71表及 alembic_version SELECT、仅7 facts表 DML，无 DDL/GRANT/跨库；核 metadata 可见、F7/版本/RR/+28800 秒。其余64空应用表不写，不启用客户业务。新随机口令/HMAC 不交 DAA，不恢复 BE009 旧容器或旧口令。
2. O 中的新私有技术文件、`backend_runner.py` 和 `facts_relay.py` 已用于就绪检查。`observe_new_profile.py` 在 M01 材料交接后按约定准备。临时夹具在使用前审阅并冻结 SHA、参数和守卫。后端 `Settings`、`FactsSettings` 明确读取 backend/.env，maintenance CLI 还显式合并两份 dotenv；`uv --env-file` 不能隔离。runner 须在任何项目导入前阻断 Pydantic 和显式 dotenv 读取，只加载本次私有合成配置，双核13381/schema/账号，失败无 fallback。调用正式 Alembic API / `MaintenanceOptions`+`execute` / `main.app`，保留 CLI 的 enable/精确 confirm/target/epoch/adoption/CAS/批准责任字段；Uvicorn 单 worker、无 reload，所有 bootstrap/mock/Projection/旧 writer 关闭。这些夹具用于本次隔离联调。
3. relay 固定三路径 `/api/v1/integration/plc-facts/{batches,latest,history}`，仅 upstream18283、无代理/重试/改写。协调方最多 arm 一次：锁定实际 batchID/digest/bodySHA，只有完整、严格匹配的上游 committed ACK 才丢该次下游回执，随后原样透传相同身份重试。它不代写 ACK。M03/04 仅停/恢复本次 relay，API/DB 保留同一目标；详细限额/超时/日志见 tasks。

## Owner M01–M05 原生操作

Owner 亲自启动/点击；准备方不代操作 GUI，不用 SQLite DML 预置配置。每段只采 5–10 秒后暂停：两 PLC 的1秒组约产生2轮/秒，上报1秒约发1批/秒，不能持续采着等待清零。不要求瞬时点中 unknown，也不预定固定样本总数。

### M01｜新配置及来源交接

1. 按[启动方式](#m01-launch)打开所需应用。首次使用隔离 profile 时，确认 DS 实例和 DAA PLC 列表为空，均未连接、采集或上报。若已有本次配置，先核对是否为同一隔离 profile 及对应的 C008-A/B，再从未完成的步骤继续。发现其他记录时暂停核对路径，保留数据库。
2. 若同一隔离 DS 已运行 C008-A/B，核对上表两个 S7 端点和本步 DB、点位及读写配置后直接到第 3 步。首次配置时，在 DS“配置中心→实例”新建 C008-A/B，填上表端点。每实例一次选取公开 [minimal.db](src-tauri/tests/fixtures/source-import-minimal/minimal.db) 与 [minimal.udt](src-tauri/tests/fixtures/source-import-minimal/minimal.udt)，只选 MinimalImport，DB号 **21**。点“预览标准地址”→确认，核长度 **8**；勾3点“预览所选点命名”→确认（不手写技术名）。在DB点位核DB及3点均启用并保存；再到“模拟与读写策略”逐点设客户端读取允许、模式“保持”、owner“无写入 owner”、三类写入禁止；初值选显式覆盖并填下表。完成编辑后选3点“保存草稿并确认所选初值/策略”，再保存草稿→保存为版本→停止态预览加载并确认→工作台 Start 两实例。文件 BEGIN/声明初值不执行。
3. DAA“PLC配置”新建同名两PLC及上表端点、启用；“点位与采集组”每PLC选同一DB/UDT对，填DB21，预览并确认导入。“预览标准布局偏移”→“确认非人工偏移”，核表。每PLC新增启用组 `G1_1000`，周期 **1000ms**，将3点逐点设为该组并启用，保存草稿→显式激活配置。无需重复已接受的导入边界/改名测试。
4. 工作台分别连接两PLC，开始采集约5秒后暂停。**上报不要启动**。上报与存储→“查看接入材料”，交准备方；先停在这里等后端采用收据。

| DB21 point          | 类型 / 地址 | A 初值 | B 初值 |
| ------------------- | ----------- | ------ | ------ |
| payload.ready       | Bool / 0.0  | false  | true   |
| payload.count       | Int / 2     | 0      | 202    |
| payload.temperature | Real / 4    | 12.5   | 25.0   |

准备方负责一次新库 RO 导出：停采停传、排空在途，journal/WAL/SHM 均无；独立 mode=ro/query_only 短快照，仅本次新 runtime 和已交接 instanceId，无 immutable/nolock/ATTACH/写/恢复，不取得、释放或绕过产品 ProfileLock。busy/hot/身份/状态/关联变化即停。导出同一已commit快照 context **原UTF8与原SHA**、revision/cycle/sample/source/seq关系，重算SHA，新文件不覆盖。GUI JSON是格式化展示，没有原串下载；Owner不写/重排JSON。

后端责任方核材料，按每PLC先 plan 后 apply：全新 binding revision=0、seqFrom=1；首次生成实际 storageEpoch/adoptionId，第二PLC使用同一epoch/第一次返回adoptionId/相同budgets；provider seqThrough固定 **9223372036854775806**。填真实 UUID/摘要后签 binding-receipt；不预造、不用 DS UUID 替代 DAA PLC ID。仅此新profile自seq1开始，不采用旧历史。DAA不持MySQL/HMAC凭据。采用和scope完成前不上报。

### M02｜首次真实投递及停采独立上传

1. 收到 binding-receipt 后在“上报设置”填 origin `http://127.0.0.1:18281`、targetId `daa008-r2-b01`、实际采用引用；只勾两个已核来源，逐项填其 seqFrom=1 / seqThrough=9223372036854775806 / reference。周期 **1秒**，保存；固定合同摘要只读。
2. 选PLC→“读取测试（GET）”。初次 latest 合法空只说明尚无可读值，不证明旧POST失败。历史“查询”后看“原轮只读包预览”，再在工作台显式“开始上报”。等可靠确认样本增加，核 false、0、REAL 及两PLC同DB21互不串值，GET永不充当ACK。
3. 首次链核后先“暂停上报”，按协调方提示在DS工作台短暂停A；DAA A开始采集至多5秒→暂停→断开，两PLC最终停采/断开后显式“继续上报”，看已有积压独立上报。设备停止产生的 bad/null 按真实结果记录；未出现就记未覆盖，不伪造/反复等待。协调方随后恢复DS A，为M03准备。一次已commit丢ACK由协调方完成，Owner不用抢unknown或重复点按钮。

### M03｜有限API不可达与恢复

协调方停止relay **20秒**，上游API/DB不动。Owner重连两PLC，开始采5–10秒→暂停。应有本地积压，无伪确认；收到恢复通知后保持停采观察。

已有 frozen/unknown 先按同ID/时间/digest/原体恢复，不能为“最新”弃旧批。协调方只对**新冻结机会**记录至少4次有积压的 latest/history 3:1机会（计入当前streak相位），核旧seq补raw不会覆盖新latest。第一条恢复TCP/POST不承诺最新。有限数据/4机会不足如实记缺口，不加长成压测，不重复StageB。

### M04｜积压退出与停态重开（仅一次）

协调方再次停relay，至重开停态checkpoint、最长 **180秒**；超时中止此case并正常恢复，记未覆盖、不要求Owner重做。Owner两PLC采约5秒→暂停。协调方先核实确有pending/冻结未决，记录checkpoint并通知后，Owner正常 **Cmd+Q** 退出DAA一次。若未产生未决则停记未覆盖，不反复要求退出。协调方闭库核账后，用**同D/同env/同命令**重开DAA，不点任何开始按钮。

核两PLC未连接/未采集/未上报，历史和队列仍在。协调方核原payload/manifest/context/ID/SHA及已冻batch原体/时间/digest/成员守恒，再恢复relay；Owner显式“继续上报”。只对确有冻结的checkpoint声称冻结恢复；未冻pending另记。确认后应无重复事实。不要kill进程、删journal/marker或换profile求过。

### M05｜详情、原生界面和结束

上报与存储打开一个投递详情看原回执/状态，选PLC读取latest及固定上海时间范围original一页。确认待确认总样本＝待冻结＋已冻结＋需处理，可靠确认另列，多片不重复；有blocked/expired/review不能只显示“运行”。同一详情在中英文、明暗和窄窗看间距/可读性，拖一列、翻页后看记忆并恢复默认；保留实际截图，未覆盖项单列。复杂游标扫描由协调方核，Owner不手写SQL/JSON。

正常退出双应用，通知协调方收尾；本步骤不代表阶段C最终验收或删除许可。

## 后续账核与资源收尾

后端责任方提供全部7 facts表账，不能只有HTTP200：stream_state、source_bindings、batches、sample_receipts、raw_samples、cycles、latest_points（表名均带 `plc_facts_` 前缀）。关联 instance/PLC/generation/cycle/sample/part/point，而非只按名称或DB。核原文SHA/定义/值/quality、observed/saved/committed/expires/proof时间、完整轮及局部回执独立质量、发布(commitSerial,ordinal)、seq、引用与幂等。M04闭库与重开后本地原账/可靠ACK逐项对应。

协调方仅做tasks列明的一次ACK丢失、一次≤2秒专用锁busy及一次独立合成非采用source拒绝；不改Owner批或伪造回执。历史latest8/changes8/projection8/original1每页，最多20页/次，至少一次小页游标衔接。gap/过窗/mismatch/scanBudgetReached不是完成，显式新预算才能继续，GET只read_result。原值三自然月/120天proof核精确算式及cleanup plan，不改系统时钟/SQL播种旧proof，不声称已等待实际过期；复杂父链/本地崩溃/大回执沿用同SHA A证据，未取得真实HTTP覆盖的项如实保留。

协调方只正常停止本次登记PID/子PID、短连接及新容器；**保留D/S、MySQL新卷、O证据至Owner门禁和后续依赖解除**。B-RUN-01若明确获批，后续无运行/证据依赖时可按已记录ID+label仅移除本轮新container/network及自有可再生缓存，权限来自该批准。MySQL volume/profile删除仍不在本批准中，须另行点名；必要O证据、可再运行helpers/私有配置和volume再运行所需凭据继续保留。QA/验收本身不授权删除。无down -v/prune，不动原profile/历史/.env/B007/失败证据或任务外资源。私有env/HMAC/原文不进入公开仓。存在unknown、SHA/schema/time/source/容量/锁/恢复异常即停新采集/派发，保留原件交责任方，不手工ACK/清队列。

## 本地恢复与原合同限度

新空 profile 建 config SQLite v2/runtime SQLite v3；样本/manifest 仍 v2，context 仍 v1。未知组合、缺库、WAL、身份/时间/schema 不符或链接均拒绝。支持 Unix 身份协议的平台仅对真正新建 profile 安装 `profile-contract.json`，绑定 canonical 路径、目录/双库身份及已知 schema。初始化先写 sentinel，再 no-replace 安装；残留 sentinel/staging 一律拒绝，不自动修复。初始化报错不称完成；末次目录同步报错后，下次可见的完整凭据可以独立走 sealed cold 全检，但不追认前次 fsync 成功，也不构成掉电耐久证明。

仅有效 sealed profile、原始 SQLite 扩展错误精确 776、单个对应 journal、未漂移的同伴库和真实 profile 锁全部成立，才尝试一次原生 rollback。恢复及 sealed cold 均在业务日志/actor 前完成同等级只读账本全检。后续错误分别说明“恢复写入可能已发生”和“已执行原生恢复写入，业务准入失败”。保留完整 profile 并报告稳定诊断；不要删 journal/marker 或手工标已确认。

既有 v2 和未封存 r1 v3 永不补封；无全部辅助文件且无 hot 时保持原 cold 行为，需要凭据而缺失时拒绝 hot 恢复，坏凭据不降级。本格式不能识别启动前外部彻底删除所有 marker 的历史，运维仍禁止删 marker 降级。移动/复制/替换 sealed profile 通常改变绑定并被拒绝；SHA/inode 不是认证，不能完整防止恶意原地编辑或伪造 journal。不支持 Unix 身份的平台保持 unsealed cold 并拒绝 Unix 凭据；macOS 合成验证不证明 Linux、Windows 或掉电保证。回退使用原兼容 profile/版本，不用旧程序打开新 sealed 数据。

## 人工读取核对

读取弹窗提供 latest（每页 8 点）、明确从最早现存基线开始的 changes（每页 8 项）、固定上海时间范围的 projection（每页 8 项）与 original（每页 1 项）。范围为左闭右开，按 `Asia/Shanghai` 输入。界面显示到秒，原 wire 字符串保留精度。

每次明确操作只读一页，最多 2 MiB。“继续”保留 opaque cursor 与筛选；达到 20 页后提示未完成，必须明确开启新预算继续。空页、`scanBudgetReached` 不等于完成；gap、cursor 过窗或不匹配显示核对未完成，需明确重选固定范围或最早基线。不会悄然跳 tail，也不保存 SMA checkpoint。核对只写 `read_result` 诊断，绝不确认 batch。原响应 JSON 不重造数字词法。

两处投递卡按不重复的本地样本计数：待确认总数＝待冻结＋已冻结待确认＋需处理，同一样本多片或多批不会增加样本数。已冻结包含已准备、发送中、重试和结果未知；阻塞、过期未确认及人工复核归需处理，可靠确认另列。

投递队列、上传事件和采集日志分别查看。列表默认 20 条，可选 10/20/50，有界 cursor 分页。列宽按稳定字段保存本机偏好，可恢复默认，不更改业务配置。

## 失败停在哪里

- 超时、坏 UTF-8/JSON、截断、错误媒体类型、成员/摘要不符、ACK 本地落盘失败，均保留原冻结请求为 unknown。继续时重发相同目标、ID、创建时间、摘要及字节。GET 永不替代 ACK。
- 只有严格有效的可靠终结拒绝，才允许原成员合法子集带父 token 派生，父链最多八层；unknown 父不能退休。token、点值和 body 不写日志。
- 原值按 provider 的自然月规则到期；保留证明可确认历史提交并明确 `valueReadable=false`。证明/token 到期进入复核，不改时间、换身份或删除待传样本。
- 真实未决请求存在时，拒绝变更目标/origin/合同/source 声明。只有从未冻结的来源待采用诊断，才可在匹配的 CAS 材料更新后重评估。同 URL 被静默换库不能依靠不存在的 epoch/adoption 字段自动识别。
- 物理预算包含 SQLite/journal、请求、回执、元数据及额外 32 MiB ACK 恢复预留。高水停止新采样/新冻结并保留恢复机会；真实 I/O 故障仍可能 unknown。pending、blocked、unknown 及有引用材料不因保留期删除。
- 初始化辅助分配子预算 256KiB 包含在既有额外 32MiB ACK 恢复预留中：实际 allocated 计入已用量，同时等额扣减剩余预留，不双计；旧页 journal 与维护/系统预留仍各自计算。
- 暂停禁止新派发，在途请求按有界时限收尾并持久有效结果。正常退出保留未决身份；包括原生恢复在内的重开不自启采集/上传。r1 原失败保留为历史证据，r2 路径仅适用于本轮新 sealed profile。
