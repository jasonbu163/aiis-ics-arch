Task ID: CU-009
Revision: r1
Workflow Mode: STD
Owner Role: Development
Status: developer_handoff
Handoff: CU-009 r1 当前交付工作树与以下 DEV self-check 交 fresh-context Verification；QA 和 Human Owner 最终验收待定。

# Development 实施与自检

## 候选及范围

- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`，未提交；同树另有 DAA-010 等并行改动。本任务没有回退其他改动。
- 修改公共 `LanguageSwitch.vue`、`ConsoleActionButton.vue`、`components.css`；工作台 `Workbench.vue` 和两份 `workbench.json`；DAA、DS 的 `src/components/shell/AgentTopbar.vue`；CU 与 source-consumer 的四份中英文 README。其余 CU PLAN / 目录索引由主协调维护。
- 语言按钮显示目标语言，刷新显式启用 `round-icon`；圆形模式的图标、加载图标和可访问名称由公共组件处理，原有普通按钮保留。DAA/DS 仍转发 `refresh-runtime` 并使用 `refreshBusy`；CU 样例只计数本地刷新事件。
- 写入前只读复查 DAA/DS 进程及 15191/15194：无匹配进程、无监听；公共 `@aw-ui` 源码直接在交付树修改。DAA-010 r5 采用其独立的采集、本地 SQLite、HTTP 上报及 Mac 隔离运行合同；本任务浏览器预览不提供那些链路的证据。

## DEV self-check

均在现有 Node v22.19.0、pnpm 11.11.0 和各工程现有 node_modules 下执行；没有安装依赖。五次命令各自从相应工程目录执行，输出分别置于任务临时目录，未覆盖原有 dist：

| 工程 | 命令 | 结果 |
| --- | --- | --- |
| CU | `pnpm build --outDir /private/tmp/cu009-r1-dev-KQq5vD/final/cu` | exit 0；含 design profile check、vue-tsc、Vite 构建 |
| 独立消费者 | `pnpm build --outDir /private/tmp/cu009-r1-dev-KQq5vD/final/consumer` | exit 0 |
| DAA | `pnpm build --outDir /private/tmp/cu009-r1-dev-KQq5vD/final/daa` | exit 0 |
| DS | `pnpm build --outDir /private/tmp/cu009-r1-dev-KQq5vD/final/ds` | exit 0 |
| SMA | `pnpm build --outDir /private/tmp/cu009-r1-dev-KQq5vD/final/sma` | exit 0 |

Vite 报告依赖中的 PURE 注释和大 chunk 提示；构建未失败。独立浏览器通过回环静态服务检查最终构建，DAA/DS 无原生桥接：

- CU、DAA、DS 的主题、语言、刷新按钮均为 44×44 CSS px 圆形；SMA 与消费者语言按钮同尺寸。中文目标 `EN`、英文目标 `中`，对应 tooltip 与可访问名称存在；刷新显示纯图标，标签分别为「刷新」和 `Refresh`。
- 1280×820 中文及明暗、960×640 英文侧栏展开/收起的五个宿主检查通过，未发现顶栏横向溢出、标题与操作重叠或按钮裁切；CU 另检 580×640。浏览器 Tab 到语言及刷新时焦点轮廓可见。
- CU 样例鼠标、Enter、Space 各使计数恰增 1；普通文字按钮仍为 40px 高、文案可见且原点击反馈有效。受控组件夹具中 loading 与 disabled 均阻止额外点击，loading 动画为 `rotating`、2s，且图标对辅助技术隐藏。
- Owner 指出刷新图标歪斜后，DOM 测量发现原圆形模式因 Element Plus 空文字 span 使 16px 图标中心左偏 4px；条件移除默认插槽后，最终空闲及忙态图标均为 20×20px、与 44px 按钮中心偏差 0px。空闲 SVG 的 CSS transform 为 `none`；忙态继续旋转。截图和测量脚本在下述临时目录，仅作附件，结论已记于此。
- 双语 workbench JSON 递归叶键均为 156，52 个静态 `t('workbench...')` 引用均存在；四份消费说明的 42 个相对文件链接均存在。`git diff --check` exit 0。未新增源码文件或改变目录结构，因此未改 `CODE_INDEX.md`。

## 精确实现面 SHA-256

```text
2a12a63c0a93c27db6fc0bcd30e97f7e790caf9610c9b0178c0edada6b1bfeb6  console-ui/src/ui/components/LanguageSwitch.vue
f2d20dbdf80fb36a0771d30ee686348d7c36ce15ce9d580debed680935ebdc1f  console-ui/src/ui/components/ConsoleActionButton.vue
8534599183338b62c04556d26c1f29f875e1c9611494013f7ebfd1d94d83ed74  console-ui/src/ui/styles/components.css
be4d2c30ea4dd98d9c6766146ce5bf990a3d2e6ec5606269521de45ec9b2a3c5  console-ui/src/workbench/Workbench.vue
7c7a2ada8272951ae31587f6ab6d162ce995518184fb3315b4288e6d118c107d  console-ui/src/locales/zh-CN/workbench.json
df79762c6d0b8e954cc9e168982543e04944c51c73578a295a3fbac1a0175d0a  console-ui/src/locales/en-US/workbench.json
589bd51b6588594548d7c216d3b686e087d4dadb29cc582fca0106980a4b77f9  data-acquisition-agent/src/components/shell/AgentTopbar.vue
dd8429c3ee2b947a0c918d8e8eb5bd0c06186669ced921ca435087a30115c9e6  device-simulator/src/components/shell/AgentTopbar.vue
ff3172582929ad256bcd9254a42d4f3e9df6114ba33e864c5ac9609e9fedbb6d  console-ui/README.md
7a2578d93b160b95f59ade1de7cf2dd64b8929c00e8ed2fd604d58f105b5c68f  console-ui/README.zh-CN.md
1a6f0c5944132001d0208edfa598b9d8a48747b85215fd2ba82c2af5e0bf6097  console-ui/examples/source-consumer/README.md
e4851dd72f8fcd4308778edf8221734cb2ac2dc38206f77631d8c2d584d47b32  console-ui/examples/source-consumer/README.zh-CN.md
```

## 限制、资源和交接

浏览器使用独立临时会话；静态预览的 favicon 请求返回 404，不影响顶栏。未启动 DAA/DS 原生 runtime，未连接设备、数据库或上报，也未测试已安装桌面程序；这些不属于 CU-009 r1。没有发布、部署或 Git 写入。

任务自有静态 HTTP 服务、Vite 夹具和浏览器会话均已停止。`/private/tmp/cu009-r1-dev-KQq5vD` 保留本任务构建、临时夹具、脚本及截图供 Verification 查看；它不是唯一证据，待 QA 和 Human Owner 收尾后由主协调核对并回收。交接对象为上述精确工作树文件与检查结果；Development 自检不是独立 QA verdict。
