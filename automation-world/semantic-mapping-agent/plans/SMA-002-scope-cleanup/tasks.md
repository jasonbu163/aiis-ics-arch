Task ID: SMA-002
Revision: r1
Status: developer_handoff
Handoff: Development -> fresh-context Verification; exact SMA-002 r1 working-tree candidate af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session

# SMA-002 r1 Development

批准：2026-11-04 Human Owner 精确批准 SMA-002 r1；spec SHA256 `39026c2905a52f2c8289322c9849501e3dc4144e61f689ea565bae5c58ec5931`。正式交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，本任务不提交或推送。

## 基线与计划

已读根 AGENTS、README/PLAN pair、canonical workflow、development.toml、SMA README/PLAN/catalog、spec（初始bundle仅spec）与相关实现。初始源码无SMA实现dirty；SMA README pair及规划文档、根CODE_INDEX已有dirty，其它应用存在并行修改，全部保留。完整基线SHA、status及既有diff暂存 `/private/tmp/sma-002-r1-dev/`，最终在此记录必要摘要与候选清单。

1. 拆出mapping-only启动偏好，保全v1磁盘旧段 → 验证兼容、默认gate及零外发。
2. 清退事实写入、Simulation及帮助全链，保全HTTP映射/JSON-XLSX交换 → 引用闭包审计、前端/Rust回归。
3. 触达事实表接入公共列宽/上海时间，更新稳定文档与精确结构索引 → check/test/build/fmt/test与隔离UI/native有界smoke。
4. 记录实际变更、命令、限制及精确developer_handoff，交fresh Verification。

仅loopback fixture允许HTTP；不读写真正.env/profile/app-data、数据库或设备。所有PLAN/catalog/AW索引由root机械同步，本Development不写。

## 实施结果与保全证据

- 正式交付仍为本工作树 `automation-world/semantic-mapping-agent/`，未建立其它交付源码副本、未commit/push。SMA源码60个新增/修改/删除文件详见末尾完整SHA清单；另仅增量改根CODE_INDEX的SMA行及本tasks。保留初始README/索引已有dirty；PLAN/catalog/AW状态由root机械同步。未改spec、checklist、其它应用、Backend、skills、角色、身份、15192/14192或capability。
- `mappingStartup.ts`从原Simulation store拆出Mapping-only状态。IPC只暴露mapping；Rust私有DiskPreferences/DiskAutoStart以Value惰性保留v1旧段，无执行者。加载不改写；保存先读取/校验已有磁盘文件，损坏或未知版本禁止覆盖，随后只替换mapping；新文件旧段中性停用。历史interval保全，调度仍用每个Mapping的interval。旧simulation=true不进入前端/服务。
- 清退事实定义/值写入facade、store方法、事件、弹窗、导入/模板/Preview/Apply。保留GET合同/事实查询、分页/筛选/刷新、映射选点和只读值导出；missing来源保持null。保留目标API/材料/规则/映射JSON-XLSX模板、导入预览/显式应用、导出及通用file_export。原Mapping域文件SHA `0862e7955dfa141f68501eaff2df8ac05cb7f33e09e8f4753424917e46fd9eee`、通用file_export service SHA `39737373ce9d72037dcfbf8b5ca92d9c8f6ca5025335cf08f5f627978b725fa1`均与基线相同。
- 清退Simulation页/组件/store、规则facade/类型、轮询和启动分支，Rust服务五文件、state注册、五个producer IPC实现/注册及专属测试；chrono-tz仅原generator/专属测试引用，移除后Cargo自然裁剪其独占phf0.12链。chrono仍被Mapping时间类型校验/公共时间入口使用，保留。
- 清退HelpCenterView、registry分组/page IDs、helpKey/helpTopicId元数据、help.css/import和无调用中英键；基线SMA HelpCenterView仅展示本地labels、无Markdown import；原TSS完整帮助此前已过滤，SMA现有源码无markdown-it调用，故清退markdown-it、配套@types及闲置传递依赖，并同步package/lock。xlsx仍有两类真实文件交换调用及测试，保留。`contracts/collection_facts`与`domain/collection_facts`旧定义解析/生产模块仅互相引用，无剩余调用，删除并剪注册；根contracts模块入口保留为空的说明模块。
- CSS仅按引用裁剪退役组件形成的孤立selector及已无调用的projection selector，保留与本次退役无因果的其它既有样式；source外未按TSS关键词清扫。`src/app/styles/shared.css`最终无改动。完整被删selector/locale键的临时审计JSON在任务tmp中，永久事实由本记录和Git diff保留。
- 实际重写的源事实表使用公共`tableWidths.ts`，表ID `source-facts`，普通字段ID `name/sourceKey/factKind/dataType/value/updatedAt/rowVersion`。最小宽度100，updatedAt160；横向滚动，稳定ID本机持久化与恢复默认。已触达源事实updatedAt和runtime事件timestamp统一用`time.ts`按上海到秒显示，原值title保留精度，无时区/缺失/单调数不猜日期。Rust运行事件公共生成入口改+08:00并保留毫秒；外部Backend审计原值不改写。未修改其余配置表内容/时间展示，交SMA-003复用helpers并承担剩余页展示。
- 原固定snapshot POST、保存Backend地址、lease/审计、单次/连续调度和错误/ambiguous语义保留。Mapping service diff仅公共日历时间函数名/调用替换。Native smoke发现原多根子组件上的v-show不生效，已在本次触达装配层用稳定div承载v-show，避免同屏叠出其它配置子页；不重建组件、不丢父store状态。

## DEV self-check（不属于QA verdict）

所有命令在SMA根执行，项目pnpm11.11.0/Cargo；未安装Agent辅助依赖。命令级`--config.verify-deps-before-run=false --config.update-notifier=false`只绕开pnpm11在sandbox中反复自动安装检查，不修改项目配置；普通用户入口仍为`pnpm tauri dev`。

| 命令 / 检查 | 实际结果 |
| --- | --- |
| `CI=true pnpm install --offline --lockfile-only --ignore-scripts --config.update-notifier=false` | 0；只移除闲置markdown依赖及锁项 |
| `CI=true pnpm install --frozen-lockfile --config.update-notifier=false`（escalated） | 0；恢复SMA自身62个锁定包，无新增依赖 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false check` | 0；最终vue-tsc通过 |
| 同前缀 `test` | 0；6个Node测试通过 |
| 同前缀 `build` | 0；85 modules；index-Xw74Hoxi.js 652.52kB（gzip213.71kB）；既有>500kB chunk warning保留，不为本任务扩展拆包 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 0 |
| `SMA_ENV_FILE=/private/tmp/sma-002-r1-dev/disabled.env SMA_HTTP_ENABLED=true cargo test --manifest-path src-tauri/Cargo.toml --locked`（escalated，仅自身loopback） | 0；11 continuous + 3 manual/pure + 3 startup/gate/time = 17个命名测试；gate子进程单独false且loopback listener accept=WouldBlock |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md` | 0 |
| Python仅检查4份已修改README的相对Markdown链接 | 0，无坏链接 |
| native偏好加载前后原文字节比较 | 相同；SHA `b555777d1eb66953b137ac77fdaf398d40422ed900dce34e4db03e2ae17422e9` |
| `pnpm tauri dev`，显式隔离env/profile、HTTP=false、空Backend | 实际启动，15192 Vite + Tauri进程及JSONL三阶段已观察；DEV Ctrl-C结束，命令会话返回0，伴随child ELIFECYCLE终止提示；未把该未打包进程冒充可点击native证据 |
| 同隔离环境 `pnpm tauri build --debug --bundles app` | 最终0，生成项目debug.app；产品/identifier未变 |

初始环境失败如实保留：直接pnpm check触发自动安装，出现registry元数据fetch失败/无TTY；offline frozen install缓存缺vue tarball退出1，获授权escalated项目安装后解决。第一次sandbox Rust测试7个loopback监听因OS PermissionDenied失败，使用明确fixture授权的escalated重跑通过，无自动审批拒绝。开发中间类型检查未收敛时失败，已修正全部引用/文案；新增pure request测试最初误断言域层path已替换（实际保持template+path_parameters到HTTP adapter），仅纠正测试后通过，未改合同。

新增Node覆盖：missing来源null、只读查询/筛选/分页捕获均GET、退休facade闭包；三类JSON/XLSX模板/导出/解析及显式preview/apply分离；只读值导出null保真；列宽最小值/稳定ID/跨表隔离/持久化/reset；上海跨日、毫秒原值/缺失；中英键与所有可达labels/manifest。Rust保留原HTTP单次/持续fixture，新增五种类型fact/constant、四种位置、必填/类型/合法值拒绝；v1旧段惰性/保全、load字节不变、新文件默认false、损坏/未知版本save拒绝；默认gate关闭实际command在HTTP前拒绝。

### UI / Native 有界观察

- Chrome仅本任务临时tab `http://127.0.0.1:15192`，默认gate关闭、连接字段为空；中英连接/事实/材料/目标/规则/映射/运行页可达，无事实写入口或Help/Simulation页。事实列真实拖拽220→304px，reload后仍304，恢复默认后220；随后关闭临时tab，未保存Backend或业务配置。浏览器验证单独列明，不当作native证明。
- CUA按产品名/未打包进程名均Invalid app；项目生成的.app按完整路径可选。第一个隔离.app实际点击了中文所有保留页、英文事实/运行页；Mapping旧enabled=true且HTTP=false仍Idle/0计数。事实刷新产生日志`SMA_EXTERNAL_IO_DISABLED`，手动start在空Backend处返回`BACKEND_HOST_REQUIRED`，没有将拒绝改成成功。
- **最终冻结.app**为 `/private/tmp/sma-002-r1-dev/final/AIIS Semantic Mapping Agent.app`；二进制SHA `d63c090aff1fa8da511e586c730dfbd250c135f2b0fd9c7b5647944d92570ad7`，与正式工作树Tauri最终bundle二进制完全相同。03:36:34.983Z启动日志external_io_enabled=false/backend_configured=false，偏好mapping_autostart=true；CUA实际观察中英运行页、英文事实及四个配置子页，最终英文为`Processed facts 0`，运行状态Idle。先完成CUA summary，再精确路径查PID30726并SIGTERM；会话143为主动收尾；之后仅进程检查，不再AX/getApp，已无存活进程。
- 最终构建产物只用于本机smoke，未签发/分发/发布。普通pnpm tauri dev的启动与同候选.app的页面点击是两组证据；未宣称普通dev进程已直接被CUA点击。没有真实Backend/Target/PLC/DB验证；无系统级网络抓包。

### UI工具退出后自动重启事件（交QA独立评估）

首次.app在约03:32Z完成`pressKey(super+q)`后，Development调用`getAXState()`确认退出；该调用自动重新启动同一临时.app，界面回到初始中文连接。再次退出动作被工具以app改变提示拒绝；随即结束CUA，通过精确临时.app路径确认新PID22404并SIGTERM，未在重启实例执行业务操作。其原启动隔离环境不能自动视为继承，不能宣称全程均证明隔离。

按root明确要求进行了有界只读影响核对：源码及本地tauri2.11.3 path实现表明无override时默认.env为SMA根`.env`，默认profile为 `~/Library/Application Support/com.aiis.aw.semanticmappingagent`。只stat相关.env（不存在）、默认profile/偏好/当日日志元数据，并只读取重启时段日志的事件、gate/backend布尔和结果，无地址/密钥输出。默认profile原目录出生于2026-11-02、仅含logs；`runtime-startup.json`不存在。默认`logs/runtime.jsonl.2026-11-04` birthtime=03:32:16.899175Z、mtime=03:32:17.767431Z，size1147，为当次新文件；三条事件为sma_started/defaults_loaded/startup_preferences_loaded，gate=false/backend=false/mapping_autostart=false，ready/loaded。后续最终隔离smoke后该默认日志mtime仍未变化。默认目录和文件未删除或回写。

可证实新增默认日志、没有该默认偏好文件、代码与日志无运行/外发迹象。没有此前hash，不能绝对证明系统WebView或其它缓存均未触及；未做系统网络捕获，不给绝对零网络证明。此事件及风险不由Development判为QA通过或Owner接受。最终测试已改为CUA summary后用精确进程收尾，避免重复激活。

## AC覆盖与限制交接

| AC | DEV已覆盖证据 / 限制 |
| --- | --- |
| AC01 | source store只读+missing回归、退休facade/事件闭包、GET请求捕获、JSON/XLSX值导出；mapping原选点保留。没有真实Backend联调 |
| AC02 | producer UI/store/API/types/五IPC/state/service及专属测试/依赖均剪除；仅Rust磁盘DTO与fixtures留旧段 |
| AC03 | v1 enabled/3456ms、legacy opaque段、load字节、save仅mapping、新文件false、损坏/未来版本拒绝及gate command零连接测试；native开启偏好仍Idle |
| AC04 | 页面/导航/help元数据/locale/CSS/markdown依赖闭包，源码与构建成功；OS默认菜单Help不是内置帮助中心 |
| AC05 | 五类型、fact/constant、四位置、缺失/类型/合法值拒绝、纯preview与三资源JSON/XLSX交换回归；保留通用save链。浏览器/native未连接外部fixture交互，发送由隔离Rust fixture证明 |
| AC06 | 原单次2例+continuous11例保留，新增pure类型例；含lease拒绝、failed/ambiguous不盲重放、逐项等待、fresh facts/静态Mapping；不是当前本仓Backend配套证明 |
| AC07 | 中英浏览器+真实macOS最终debug.app保留页，触达事实表列宽/时间helper及runtime日期，原生进程已退出；退出确认工具副作用如上单列，QA需独立评估，不预设接受 |
| AC08 | 最终check/test/build/fmt/test全部0，README链接/diff检查通过，实际文件SHA/依赖引用及资源下列；并行dirty保留。真实profile除已报告工具自动重启新增默认日志事件外未主动业务操作 |

## 临时资源与保留条件

`/private/tmp/sma-002-r1-dev/`为本任务独占：baseline status/SHA/已有patch、candidate清单、各检查日志、删除selector/locale审计JSON、disabled.env、native-profile（仅legacy fixture+日志）、首轮.app和final/.app。源码唯一交付在正式工作树；这些都不是替代交付。SMA自身node_modules/dist/src-tauri/target是已忽略项目验证产物，未借用CU依赖。15192及两次.app进程均已收尾，没有常驻fixture。默认日志是自动重启事件的实际残留，不作为本任务可回收临时资源，不删除或改写。

QA/Owner仍需读取本任务日志/.app复现，所以暂不回收自有tmp及final.app；Owner最终接受后由root核对无运行/后续依赖再按workflow清理。所有关键命令、结果、风险、二进制及源码SHA已在此持久记录，临时日志不是唯一证据。

## Developer handoff

精确范围 **SMA-002 r1**；正式候选为本工作树、无新commit，基础HEAD见上。源/稳定文档变更清单60项的紧凑JSON（路径排序，before/after SHA/null三元组，UTF-8，separators=(',',':')）SHA256为 **`af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2`**。计算digest前，为下表SMA相对路径添加 `automation-world/semantic-mapping-agent/` 前缀，按工作树相对路径排序，再编码上述before/after三元组。该digest排除协调者PLAN/catalog、任务角色文档及共享CODE_INDEX；根CODE_INDEX只对SMA条目增量修改。本tasks为Development事实，下面提供精确文件清单。最终自检后未再修改产品源码，最终.app对应此候选。

下一gate：root启动新的命名Verification，fresh context（`fork_turns="none"`），读取approved spec、本tasks、当前工作树/diff与上述证据独立创建checklist。此handoff仅DEV self-check，不是QA verdict、Human Owner接受、SMA-003软件批准或真实业务闭环。

### 实际修改/新增/删除文件与SHA256

路径相对SMA根；before为本轮实际消费基线（含最初已有README dirty），after为最终候选，`—`表示不存在。

| 文件 | Before SHA256 | After SHA256 |
| --- | --- | --- |
| `README.md` | `fe54376d3b01622328bd9005406c44fa59fe449bc952a8d812f49802b84af367` | `c9c4647fba2327ebbcfbdc162d1c979f2d256e53660462edb996587e5d110f93` |
| `README.zh-CN.md` | `cff6ebbf1efa4fa79de50a6e92e4650d8da3db612303b6f38d7263087f98ada2` | `cb246fcd88db8a9a09c37323e89063bed11b72e70a948e458f347a4798fa022f` |
| `package.json` | `634052dbfaebcf7a6aff37501664164e756c502275e194228c0a0363c1d4937d` | `7c444320226a4ec44fad28489f294fec7fab8d8015f413117ea157618b7fa916` |
| `pnpm-lock.yaml` | `d3456f97209ddddba349d991610b5d7af1060ef53b8e3b44050be85bf926a436` | `a1e3e2399b521a105e76b1a5d2d825a3492bdffe9864eb3f63a7ee49342f6215` |
| `src-tauri/Cargo.lock` | `efca557c38cb520e046a36a3017357b54e297f43641b99d4dc3760f52dc4e2fa` | `dc1923b8f55f5da6135a871de7fa442feee965f3efae626e5c192724b20078de` |
| `src-tauri/Cargo.toml` | `4474ec9348d0245e36385cd9ad0db3ce323ed0e28082b3eb0868ae6764116f85` | `538115044ed4346a61ccbdb7d25ef3b7b53e97766af7f2e48f0ee9d316dd5eeb` |
| `src-tauri/src/app.rs` | `966cfe1fb7d5e82ec0731528f282af857768575125859cbaf2b859cad7cce70e` | `75e948aa760c91b30f7a9ffecae4d2b34ad55858987915f6328daa2e3bdbf4d0` |
| `src-tauri/src/commands/runtimes/mod.rs` | `cb455156879ddf9c7c80460bc395120d6ed647248bae9e59190ee4c655f48da8` | `cbba860713699e75232aeb521ed8fd5b82659b9988b4bd3e86dcf5e85031d757` |
| `src-tauri/src/config/runtime_startup.rs` | `b1bf186eb19380dda40517895ab74b6dbe51e18cd26a9ac1e94fb1a19a91aa16` | `9d03f6d0d8ef948b16c2d36a4d29d8542898cb2e463d0f006184122f26511a3e` |
| `src-tauri/src/contracts/collection_facts/mod.rs` | `3c33fcf1935e815afe76437217c6ecff89b2772ed307750bb96f298620fd393a` | `—` |
| `src-tauri/src/contracts/mod.rs` | `7687b4bf381dfc77511e29934fa2fec05fd67bab838c0e56c6ab0a5111c4d069` | `d853c7269bf7d448a3991152c9159898acaa921780ff363d7f31064e8761b045` |
| `src-tauri/src/domain/collection_facts/mod.rs` | `36b53ff71a1e57421a8caa02aaaa5fbc56c009fe2b99d2ea094e0e0ccadc4995` | `—` |
| `src-tauri/src/domain/mod.rs` | `3436c7bf3c52d0d4c13b7d037c4848aac951fa53778f425479d6ba094d312a2e` | `c11feb77a0ab981dd2527d50eab8594d199ded7e337d3c1e86fbe808afc74987` |
| `src-tauri/src/domain/runtime/mod.rs` | `e3deec6bf0c4edeb2a9c982fd200668d3e0f0be3a86f6adac2e93d59df69512f` | `762f9efa46d0724b07e652f604456e008f076ce1b444ac3ededda7056e8bbe88` |
| `src-tauri/src/services/mapping_runtime/mod.rs` | `70d823277640082588932b2f3f2f5cecbbc63dcb3b8119c55567e716f79a5394` | `4348cced7e0d965d9c07410b1b2f526e390f6762d3e743b6a9fab51494543454` |
| `src-tauri/src/services/mod.rs` | `f1d5f1d06501a2040cd53684c4f4e3d2d118b5db4ef2c4d7d28b098dc436245b` | `203bf09d4bfc1812e1beae1b657fddc0dade16b9542d245ff7f2761af2e31484` |
| `src-tauri/src/services/simulation/collection.rs` | `3d852c95a1c89fe1364182f7c03e8ac031f1302140066d3c40ccba7b939f77a0` | `—` |
| `src-tauri/src/services/simulation/generator.rs` | `f30657382ae369ff567c8ccdaf1afc9a712f04d762517edf4d4ddc400db55a5d` | `—` |
| `src-tauri/src/services/simulation/mod.rs` | `337221ae12ce2ce7f9018a23ed82badc3b36ea62a7ecbd61fc037fd04e089846` | `—` |
| `src-tauri/src/services/simulation/model.rs` | `2bcb8385454c6ab936e955439c0a999f4f11d381c52893d9983f1b9a0400a394` | `—` |
| `src-tauri/src/services/simulation/state.rs` | `a4734e9e0cd7d5c9161f187f207ce232745a52a6e6eef60642cc0dbd13d0b204` | `—` |
| `src-tauri/tests/collection_simulation_tests.rs` | `4c58cd843ca4158a43e25c9ab64e2b09810157a35d21254187c539bb93f1784d` | `—` |
| `src-tauri/tests/mapping_runtime_continuous_tests.rs` | `2993ca2647bd74e75cb2b8441997976fb3317445d71b88bd05170934443c12d6` | `9468947f828ec4200f1d2c4d62789fa4bf41d387e575286092706f4413fe304c` |
| `src-tauri/tests/mapping_runtime_manual_run_tests.rs` | `27d7e38306f3e8bf44f48a9296d78c1c5b0f700435e13410d74389cc9361fcd5` | `578e5834825c30c0ee496d60b471c24abbf28d2c68e081621e5c0c1f23c1bf56` |
| `src-tauri/tests/startup_cleanup_tests.rs` | `—` | `10b44878e2d84e6e471e5a675619f7136586caa13f3083b54526b3439f859895` |
| `src/App.vue` | `2019c851ebd4dab8725905fcaa24d128fd619d71c1f0ba66e69b48515b152bfc` | `ed6c777197397bc16e85cb8c0e2f0a2a375349bf9ab7d1b5d4e9f5afd782afea` |
| `src/app/README.md` | `50a64b043b748392bab870f81220abb3c14c5bd04a163e202a647a2f34b81c12` | `24bcb95c74c67733c90fec3102748cda97627408a946932ef531122ce32a82fb` |
| `src/app/README.zh-CN.md` | `a1c13e6ee8b73af562786b16ad36ff2bafd858073d0d0b6da0e9d6fc59c70d33` | `be71d89b1cf7ec2b75aeb8d2f880c9259dbadf9f881ab7793db5fad9a94665f3` |
| `src/app/connection/manifest.ts` | `dfb68624492309cabca3cb886daf13e26ec741908c61924052385d9fe62399cc` | `a4a44385665097e91a4e764b3ba13f0e061caf401d46317b9e0fddecf107e40f` |
| `src/app/help/HelpCenterView.vue` | `834b2b7076bd019aba9698e02b4eaf9ac717c2b939b6caa4d610b60289239e38` | `—` |
| `src/app/navigation.ts` | `877a035ebe7bb4934cbaf5b707ade352c6b982129bd8639d34b67eb429b875f6` | `2c8632e0d961fe3dc06927cacc7130ba92332c06ca38957456ab3378cf043489` |
| `src/app/registry.ts` | `cf94fd52a0d3cc810dac5427909c2310fe3056392bbe96ba830c6196dea74efb` | `ab7c7a18adfe32ace4924418bec5eec2404790c63f95d09f29d80c42c08dead2` |
| `src/app/styles/responsive.css` | `d141b9dd5dd8ee7507ca1b26894708952facc70513e530ca8b005a7aab81c0f0` | `6ff3587993f06f5ba351a28e7eeaca12f3e66583c31d66bab676da94465a4373` |
| `src/app/styles/shell.css` | `098f9e8255d8b9abca7c0722f9467a3d48a36a39f01a1f984a1901997ba2cf17` | `64781d2fe77a33126a744024a680139b9fbe095c69447ec67de329a337cfb2e8` |
| `src/app/twin-facts/api/index.ts` | `7d4b736665a8035528ebc18c5d1cb514b2eefe926bd841357438142e0f566943` | `bb76706720ad13771422ebba64b97f611898c7d9992339abca09d9665b3ad0a2` |
| `src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue` | `37b6c35bada89ea7f49f82041d188f39b504ad061b55acbbac6ffdd2e75c12f4` | `ff95c95b03ff1f0050bad7145e28d7daa8148187e52796a051355d6031838e22` |
| `src/app/twin-facts/components/FactBatchOperationsDialog.vue` | `80e8007fca7728016858a7de90eb4e5cfabc01d156c740cdff4d050f7f9e7648` | `—` |
| `src/app/twin-facts/components/FactDefinitionDialog.vue` | `f1a128797ed87d2269d207a12bb232747031c8d98c691f570828f7a606456f5a` | `—` |
| `src/app/twin-facts/components/FactValueDialog.vue` | `267a5173eab8bb037e53d63d597f7c903e820576828892b58e868b21508bf334` | `—` |
| `src/app/twin-facts/components/FactsTablePanel.vue` | `a28b421027dbd01c9ec5b840d453fc64a5c162df4cc487204813b0f72aeb04b5` | `7e2f12d844c16f436e2021b6d3a5fae31dec28288194eccc1cce6109c27880c8` |
| `src/app/twin-facts/components/SingleFactRuntimePanel.vue` | `b63a54b93467e6e11c5201d125ed088278285507d92342a956e7d50a7b737495` | `—` |
| `src/app/twin-facts/components/TwinJsonContractPanel.vue` | `e6164d2932c94f32af524f9ae813df9edacb03291a4bc4a084bef76712b6005a` | `71b2e4b399fe8d713ec250bbabd78822f276e8070743541fe7d4f1ff65659bde` |
| `src/app/twin-facts/locales/en-US.json` | `f4a7cffbf17d50041bc35b535ba38d7df1288183c00530d2a56903fe080eeeb7` | `a52f7a5a5e510f7a111fb1303544a25cf3c5df7c5fae7b406a0b9481acb0777d` |
| `src/app/twin-facts/locales/zh-CN.json` | `3822a415d1a447621aea228db0f6e302bae5f716b8772c69be2389d494028c09` | `3349f0e6e8de1af380c4055d0c5e5bf310ba945fcd84ea676126da43f44dc037` |
| `src/app/twin-facts/manifest.ts` | `6b36187f10272b889d91fec2dec3e31d510dd61c3f2c7d2fd51be483aaa81b05` | `f9766354da79cf006327b3317e13434ea546b029be0111d9aa7e411606853d97` |
| `src/app/twin-facts/store/apiFirstMappingRuntime.ts` | `4f893c9eae9b47dbad3cc398c975ad14427723018ff4b8411a299565949fec89` | `039d235c65f9398fbd1d3f7ade77ab7861cb13c1a3ab1838216ebf0a3754ea9f` |
| `src/app/twin-facts/store/collectionFacts.ts` | `528e28637e10322faf90b1641ffa2e4650cddc4979db79dae004d0462c055666` | `ce52417a5e5bb3a54da78c8c9dc3af5ff88760e0d58b237676dc47e1719e0f41` |
| `src/app/twin-facts/store/mappingStartup.ts` | `—` | `3975dd795dd35ec0122a2ae9365d33b643520f0409d3ec2dfb80bb785cdf03de` |
| `src/app/twin-facts/store/singleFactRuntime.ts` | `2ffd97c651807695773d14cf8d1974bc8f049fff95e581060b058cbe3527e73e` | `—` |
| `src/app/twin-facts/types.ts` | `07ba95ed7f5aeda59aa9d09fd9772285e99a9ec51b50afa590be37b09fe374f6` | `14631cd37791baca6d9f9002bcc1a93d3511e2018922f6cb043fb85a5a33196a` |
| `src/app/twin-facts/utils/collectionFactFiles.ts` | `37cab9029dd9b7a2290548201c39c6df86676e167e04c4d4e03c779cfbdb067a` | `3cae33dd285af239d19affcc0c14bf5b6810e44bc744919d1dfb41929fa7d115` |
| `src/app/twin-facts/views/TwinFactsModuleView.vue` | `86fc26cd293a2b80fa1441998823c7d1445550514a2285b8dde862cf5b9e3b04` | `cdc24a894a08231407b3ad73ef12dc3d92774250c57ab3d3b57f3139b5e6d541` |
| `src/console/tableWidths.ts` | `—` | `bf50df871aab635f6aa5f9795596ee0cfade7fd17c40e21a4cd7f596105bdfe8` |
| `src/console/time.ts` | `—` | `eea7e4df392779508789787ec0fa53d84fbd6827dd48b06c6efe08046a257b17` |
| `src/locales/common/en-US.json` | `fee456c63edce51704e900532ebf70f5c477c554f8818b4dba8b6ccf5b5305df` | `dd72599bdad188099044031514dc5d255da5d7755ad9636f9c5955309710424c` |
| `src/locales/common/zh-CN.json` | `8889723b479746dc837311462d504128d43ef3896523211be1242e0a2eec2361` | `839b21ffbcc5cfec9d4d8deb682977cbfabb388e539be23babfb1e825806fa6b` |
| `src/locales/index.ts` | `31fd0fb55eabb3fb71578fe29a231d43ad9b2963b98aa9a2c69dc3758da41066` | `ea95f3354825a76738c129587f7815439d7c120a6e6372fc2f94038a68c071f0` |
| `src/styles.css` | `a1244ffaaa59adc5b31407ace96cc364054267cfea7f616b5da7a95d0d6b2eda` | `fb85bfd1e90e07e485bb59466743c067ef4ca76235dad44821b658db6f36b91a` |
| `src/styles/help.css` | `6388f0ffb475f18e3cf99d48a7f60500c4cac3d41992a50cfa399ab27771c9dc` | `—` |
| `tests/cleanup.test.mjs` | `—` | `7c55e2ead7c592c2ceda777a6cb286dffff1d82e45114433add17f26dd51a4ed` |

### 原始输出的校验摘要

原始日志可在上述tmp读取；以下哈希及实际结果已持久化。

| 日志 | SHA256 |
| --- | --- |
| `check.log` | `aacdfedc485449151e8f0cedfb8264a7d15047256a7b3c3a4a9e848e28e7b178` |
| `node-test.log` | `38bbfa4bb14e26b9957d7528daa2e2d248df4e7658b92514d5c6c6afafa8bdf9` |
| `build.log` | `f3f346e52b5a1d0085cc45c335aa67b1576d082112a3cdfa6fe32d5be63e2a4d` |
| `fmt.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rust-test.log` | `52063338fd8bc0330ed6d71d5121db79741e332d4cf672393cf12674f4eda600` |
| `tauri-build-final.log` | `4bc3bdb709ec451c32ffe018c98b8599eae80dd14acf918911c865852cbae5f0` |
