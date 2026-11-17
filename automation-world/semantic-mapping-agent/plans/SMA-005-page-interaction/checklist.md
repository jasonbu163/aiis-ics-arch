Task ID: SMA-005
Revision: r1
Status: qa_blocked
Owner Role: Verification
Allowed Writers: Verification
Handoff: Verification -> Human Owner（补齐本人执行的原生证据后再复核；最终验收由 Human Owner 决定）
Workflow Mode: STD

# 独立验证记录

## 结论与阻塞

2026-11-16（Asia/Shanghai），对 #4、#6 的精确交接进行 fresh-context 独立验证。当前没有发现可复现的范围内实现缺陷；**结论为 `qa_blocked`，不是 `qa_passed`**。用户要求后续窗口和交互测试由本人完成、测试只做 GET，故本轮未启动应用、GUI、HTTP 监听器或实际网络请求，也未调用实际 IPC 或读取默认 profile。AC01–AC04 的原生证据仍有缺口；下文给出可执行步骤及预期。Owner 提供结果后须按原规格核对，不能仅凭本记录推定通过。

开发记录中另有默认 profile 误写事件：见 [tasks.md](tasks.md#默认-profile-意外写入)。该记录称旧打包进程曾将默认库从 revision 0 提交至 2，事前无内容快照，不能推断可恢复原值。本轮未读取、恢复或覆盖该库；这不是本轮隔离测试的证据，后续处理由 Human Owner 决定。

## 输入、身份与范围

- 授权 [SMA-005 r1 spec](spec.md) 的当前 SHA-256 为 `730b6adc9fee5ee19f48f9428e4542d8565fef0d1e0404279e8ab366a6dbb8e5`；完整 [developer_handoff](tasks.md#developer_handoff) 的 SHA-256 为 `93c9a64b920b52bc55d91ad77d9d91eaaa97e16ad011eebe6055e039973ac016`。与交接一致，Human Owner 批准记录见 spec §6。
- 工作树 HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`。逐项复算 tasks 所列的 12 个交接源码和测试文件，摘要全部相等；只审计这 12 项相对 HEAD 的差异。仓库有其他并行任务的未提交内容，不能将整个 dirty worktree 当成本任务差异。
- 已读取根项目契约、canonical workflow、根/AW/SMA 的 README 与 PLAN、最近的 `src/app` README、完整 spec/tasks、候选 diff、关联运行源码和既有 [SMA-004 验证](../SMA-004-local-configuration/checklist.md)。任务表面按 `project-governance`、`frontend-ui`、`i18n-workflow`、`desktop-tauri`、`rust-runtime`、`backend-arch` 复核；OpenAPI 原始文档按本任务现有读取合同检查，不误套业务 API 信封。不修改规范或实现。当前 `SMA_PROFILE_DIR` 由进程环境设置且只接受绝对路径；SMA 的 `.local/dev` 此时不存在。与 DAA/DS 对齐的绝对/相对 `.local/dev` 支持属另行规划，不属于 SMA-005 r1；SMA-006 仍是草案。

## 验收标准核对

| 标准 | 本轮已核证据 | 仍需证据 |
| --- | --- | --- |
| AC01 | 源码：草稿复制后校验，门禁通过才调用一次 `fetch`，使用 `redirect: error`；测试入口不调用保存或连接变更事件。独立 Node 内存 fixture 断言 A 保持、B 地址、1 次模拟 GET、revision/document/事件不变。 | Owner 在隔离的正常 Tauri 窗口记录真实 A、B 的 GET、完整 SQLite 快照及目录/入选前后值；关闭进程重开仍为 A；事件计数为 0。Development 的隔离窗口自检声称 A/B 一次 GET 与 revision 1，尚未验证重开；那是 Development 证据，不替代独立验证。 |
| AC02 | 内存 fixture 覆盖非法主机/端口、关闭 HTTP、503、坏 JSON/缺字段、超时、模拟重定向失败、旧 B 改回 B 后的竞态、禁用 HTTP 保存和过期 revision 冲突。同步 watcher 使用递增 generation 丢弃旧响应；模拟不证明 WebView 的实际重定向或 SQLite 事务。 | Owner 对 B 做实际 GET-only 的非成功、非法文档、超时、拒绝重定向，核对重定向目标零请求；非法输入/HTTP 关闭零请求；旧 B→C 和改回 B 的迟到响应；HTTP 关闭下显式保存一次，以及通过另一份本地配置修改形成真实 revision 冲突、保持草稿与新快照。 |
| AC03 | 宿主移除旧偏好加载及 auto-start 调用；运行组件只暴露适用 pause/stop，列表不再连接 manual-run 入口，保留已保存预览。独立内存宿主探针模拟旧 auto-start=true，挂载并切到运行、映射页仅见 `get_api_first_mapping_runtime` 和 `load_local_configuration`，无执行/偏好读写；偏好未变。Node SSR 也检查中英 idle/running/paused 时按钮。 | Owner 在 HTTP 关闭/开启和旧偏好 true 的隔离窗口重开并观察页面、文件、日志、计数及目标监听器；验证真实保存配置预览、适用安全暂停/停止和状态日志读取。若当前隔离 runtime 是 idle，不能冒充已验证真实 running/paused；保留该受控状态缺口。启动及偏好调用计数的 native 观测需能从进程启动前覆盖，单凭重开后的文件散列或日志缺失不能冒充全程 IPC 计数。 |
| AC04 | 中英文 locale 静态对称及键解析随 `pnpm test` 通过；相关页面复用 CU 组件。 | Owner 在 1280×800、1024×720 分别检查中/英 × 明/暗、Tab/Enter 操作、可见焦点、目标地址和状态可读及无新增页面横溢，并在至少一个正常 Tauri 窗口完成保存/只测/重开/运行提示。静态和 SSR 结果不证明这些视觉与键盘要求。 |

### 原生运行准入的既有证据

本候选 Rust、Tauri 配置、锁文件及 CU 没有相对 HEAD 的差异。`app.rs`、`commands/mapping_runtime/mod.rs`、`commands/runtimes/mod.rs`、`services/local_configuration/mod.rs`、`services/mapping_runtime/mod.rs` 的 SHA-256 分别为 `d9636997572a0ab47e36e5da02ec98eb7822c8561c52435d5bf55d39b946ae92`、`fd5238ae84404c297bef26fb2a38f2a81d3a6599674b02fbc77708149cb89ed7`、`8a8cedea551494daa982cb6a9700eb5e53cc0d9b0483f36e2504b6f67f008af7`、`adc5c491e4d3f8e2601dcb7ce4a0339e7a59379c788ed28ffc1ad5edafbad871`、`3ec2e757d87f7ffc5e29dbd914257125dd934e43d8ca3248523c8f464d60c051`，与 SMA-004 tasks 的 Rust 交接摘要吻合；其 QA2 记录声明返工未改 Rust。源码中 manual 入口先拒绝，start/resume 的 command 先走 `admit_execution()`，正常 service 也先拒绝；pause/stop/status 仍委托原路径。

[SMA-004 AC09](../SMA-004-local-configuration/checklist.md) 的独立既有证据包括 manual command 在 HTTP false/true 的受控子进程零 accept、正常 manual/start/resume service 拒绝及旧 auto=true 的原生拒绝；该记录明确**没有**从 native DevTools 注入全部 IPC。本轮不重跑可能触发旧兼容网络路径的 Rust 集合，也不把源码、既有证据说成新做的原生直接 IPC 回归。

## 本轮实际检查

环境：macOS Darwin arm64，Node `v22.19.0`，pnpm `11.11.0`；工作目录为 SMA 项目。未安装依赖。先检查 tests：Vite `middlewareMode:true`、`hmr:false`、`ws:false`，不调用 `listen()`；网络与 IPC 为进程内 `fetch`/`window.__TAURI_INTERNALS__.invoke` fixture。以下是独立执行，不含真实 profile/服务。

| 命令或动作 | 结果与边界 |
| --- | --- |
| `git rev-parse HEAD`；`shasum -a 256` 对 spec、tasks 和 tasks 列明 12 项逐一重算 | 均与上面的精确交接一致。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false check` | 退出 0。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false test` | 退出 0，20 passed，0 failed；进程内模拟，不证明原生 SQLite/网络。 |
| `pnpm --config.verify-deps-before-run=false --config.update-notifier=false build --outDir /private/tmp/sma005-verification-build` | 退出 0；Vite 报依赖 PURE 注释与大于 500 kB chunk 提示。该 outDir 不自动清空，构建成功不声称其全部历史文件为本次产物。 |
| `git diff --check --` 后接交接 12 项 | 退出 0。 |
| `git diff --stat -- src-tauri/src src-tauri/tauri.conf.json package.json pnpm-lock.yaml ../console-ui` | 空输出；对应已跟踪保护面相对 HEAD 无差异。 |
| `node --input-type=module` 进程内 Vue/Vite 宿主探针 | 补充 `ssrContextKey` 后退出 0；记录下方输出。首次探针因测试 harness 未提供 SSR context 而退出 1，未形成产品缺陷或运行证据。探针以替身子组件和内存 renderer 运行，不能证明视觉或原生行为。 |
| Python 相对 Markdown 文件链接检查 | spec、tasks、checklist 的相对文件链接均存在，退出 0；仅检查文件，不验证标题锚点。 |
| 从本文件提取宿主探针并经 `zsh` 执行 | 退出 0，结果与下方一致；复核了记录内的完整复现命令。 |
| Owner 步骤静态检查 | Python `ast.parse` 检查 fixture 源码，`zsh -n` 检查两个准备步骤，`json.loads` 检查 overlay 和 startup 样本，均退出 0；fixture 和 Owner 步骤未执行。checklist 无尾随空格。 |

宿主探针结果：`{"result":"PASS","scenario":"host mount and navigation with old auto-start true","calls":["get_api_first_mapping_runtime","load_local_configuration"],"preferenceUnchanged":true,"fetch":"trap","transport":"in-process only"}`。用于复核的核心断言是禁止调用 `run_mapping_manual_once`、`start_api_first_mapping_runtime`、`resume_api_first_mapping_runtime`、`load_runtime_startup_preferences`、`save_runtime_startup_preferences`；旧偏好 fixture 是 `enabled:true`，HTTP `fetch` 是抛错陷阱。Vite middleware 和虚拟 UI/子组件只存在于进程内。

<details><summary>宿主探针的完整复现命令</summary>

```bash
node --input-type=module <<'NODE'
import assert from 'node:assert/strict';
import { createServer } from 'vite';
import vue from '@vitejs/plugin-vue';
import { createRenderer, h, reactive, nextTick, ssrContextKey } from 'vue';
const children=['ApiMaterialsPanel.vue','FactsTablePanel.vue','MappingConfigurationsPanel.vue','MappingValueRulesPanel.vue','TargetApiConfigurationPanel.vue'];
const server=await createServer({configFile:false,plugins:[{name:'qa-memory',enforce:'pre',resolveId(id){if(id==='@aw-ui')return '\0qa-ui';},load(id){if(id==='\0qa-ui')return `import {defineComponent,h} from 'vue';export const ConsoleCard=defineComponent({setup(p,{slots}){return()=>h('section',{},slots.default?.())}});export const ConsoleActionButton=defineComponent({setup(p,{slots}){return()=>h('button',{},slots.default?.())}});export const StatusCapsule=defineComponent({props:['label'],setup(p){return()=>h('span',p.label)}});`;},transform(code,id){if(children.some(name=>id.endsWith('/'+name)))return '<template><div /></template>'; }},vue()],resolve:{dedupe:['vue','element-plus']},ssr:{external:['vue','element-plus']},optimizeDeps:{noDiscovery:true,include:[],entries:[]},server:{middlewareMode:true,hmr:false,ws:false}});
const calls=[],beforeWindow=globalThis.window,beforeFetch=globalThis.fetch;
const pref={schemaVersion:1,runtimeAutoStart:{apiMappingRuntime:{enabled:true,factsPollingIntervalMs:1000}}},beforePref=JSON.stringify(pref);
const snapshot={schemaVersion:1,revision:1,updatedAt:'2026-11-16T00:00:00+08:00',document:{connection:{scheme:'http',host:'saved.invalid',port:9000},catalog:[],materials:[],targetApis:[],mappingValueRules:[],mappings:[],sourceMetadata:[]}};
const runtime={runtimeType:'api_first_mapping',status:'idle',runId:null,channel:null,profileId:null,profileVersion:null,profileHash:null,processedItems:0,successfulTransactions:0,failedTransactions:0,cursor:null,lastErrorCode:null,lastErrorMessage:null,logs:[]};
globalThis.fetch=()=>{throw Error('unexpected network');};globalThis.window={setInterval:()=>1,clearInterval:()=>{},localStorage:{getItem:()=>null,setItem:()=>{}},__TAURI_INTERNALS__:{invoke:async(command,args)=>{calls.push(command);if(command==='get_api_first_mapping_runtime')return structuredClone(runtime);if(command==='load_local_configuration')return structuredClone(snapshot);if(command==='load_runtime_startup_preferences')return structuredClone(pref);if(command==='save_runtime_startup_preferences'){Object.assign(pref,args);return;}throw Error('unexpected IPC '+command);}}};
const node=(type,text='')=>({type,text,children:[],parent:null,style:{},props:{}});const renderer=createRenderer({createElement:type=>node(type),createText:text=>node('#text',text),createComment:text=>node('#comment',text),setText:(el,text)=>el.text=text,setElementText:(el,text)=>el.text=text,parentNode:el=>el.parent,nextSibling:()=>null,patchProp:(el,key,prev,next)=>el.props[key]=next,insert(el,parent){el.parent=parent;parent.children.push(el);},remove(el){if(el.parent)el.parent.children=el.parent.children.filter(item=>item!==el);}});
try{const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');const {default:Panel}=await server.ssrLoadModule('/src/app/twin-facts/components/TwinJsonContractPanel.vue');const state=reactive({page:'backendConnection',view:''});const app=renderer.createApp({render:()=>h(Panel,{labels:getMessages('en-US'),enabled:true,page:state.page,view:state.view})});app.config.warnHandler=()=>{};app.provide(ssrContextKey,{modules:new Set()});app.mount(node('root'));await nextTick();await new Promise(r=>setImmediate(r));state.page='mappingRuntime';state.view='execution';await nextTick();await new Promise(r=>setImmediate(r));state.page='mappingIdentity';state.view='mappings';await nextTick();await new Promise(r=>setImmediate(r));const forbidden=['run_mapping_manual_once','start_api_first_mapping_runtime','resume_api_first_mapping_runtime','load_runtime_startup_preferences','save_runtime_startup_preferences'];assert.deepEqual(calls.filter(call=>forbidden.includes(call)),[]);assert.equal(JSON.stringify(pref),beforePref);assert.ok(calls.includes('get_api_first_mapping_runtime'));console.log(JSON.stringify({result:'PASS',scenario:'host mount and navigation with old auto-start true',calls,preferenceUnchanged:true,fetch:'trap',transport:'in-process only',note:'SSR-loaded host and stub children; no visual/native claim'}));app.unmount();}finally{globalThis.window=beforeWindow;globalThis.fetch=beforeFetch;await server.close();}
NODE
```

</details>

## Human Owner 可执行的隔离 GET 步骤

以下操作由 Owner 自己执行；没有要求测试 POST。这里使用可丢弃 `/private/tmp` profile 与两个本机 GET fixture，**不使用默认 SQLite、真实 Backend、DAA/DS profile 或 SMA `.local/dev`**。先确认交接的 12 项摘要仍与 tasks 相同，且无其他 SMA/Tauri dev 使用 15192；若端口 18592 或 18593 被占用，停止并说明，不静默换目标。测试期间保留终端输出、日志和隔离快照供复核。

### 1. Owner 自己准备一次性隔离目录和 fixture

在终端进入 SMA 项目，执行下列命令。打印的目录名需原样留存；后续另一终端需手工复制这个绝对路径设置 `SMA_QA_ROOT`。当前产品的 profile override 只支持绝对路径，不能写成 `.local/dev` 相对路径。

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/semantic-mapping-agent
export SMA_QA_ROOT="$(mktemp -d /private/tmp/sma005-owner.XXXXXX)"
printf 'SMA_QA_ROOT=%s\n' "$SMA_QA_ROOT"
mkdir -p "$SMA_QA_ROOT/profile"
export SMA_PROFILE_DIR="$SMA_QA_ROOT/profile"
export SMA_ENV_FILE="$SMA_QA_ROOT/owner.env"
export SMA_BACKEND_BASE_URL=''
export SMA_HTTP_ENABLED=false
printf 'SMA_HTTP_ENABLED=false\nSMA_BACKEND_BASE_URL=\n' > "$SMA_ENV_FILE"
cat > "$SMA_QA_ROOT/profile/runtime-startup.json" <<'JSON'
{"schemaVersion":1,"runtimeAutoStart":{"apiMappingRuntime":{"enabled":true,"factsPollingIntervalMs":1000}}}
JSON
cat > "$SMA_QA_ROOT/overlay.json" <<'JSON'
{"identifier":"com.aiis.aw.sma005.owner","app":{"windows":[{"label":"main","create":false,"title":"SMA-005 Owner Check","width":1280,"height":800,"minWidth":1024,"minHeight":720,"incognito":true}]}}
JSON
printf 'good\n' > "$SMA_QA_ROOT/mode"
```

上面仅由 Owner 为本次隔离 profile 写入合成旧偏好。overlay 使用独立标识与 incognito，因为 profile 只隔离 Rust 文件，不隔离普通 WKWebView 存储。下面的 fixture 对所有到达的常用 HTTP 方法记日志，只有 GET 有测试响应，不主动发送任何请求：

```bash
cat > "$SMA_QA_ROOT/fixture.py" <<'PY'
import json, os, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

root = Path(os.environ['SMA_QA_ROOT'])
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass
    def emit(self, status, body=b'', extra=None):
        try:
            self.send_response(status)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass
    def do_GET(self):
        print(f'{self.server.label} GET {self.path}', flush=True)
        if self.path != '/openapi.json':
            return self.emit(404)
        mode = (root / 'mode').read_text().strip() if self.server.label == 'B' else 'good'
        if mode == 'drop':
            self.close_connection = True
            return
        if mode == 'status':
            return self.emit(503)
        if mode == 'invalid':
            return self.emit(200, b'{')
        if mode == 'redirect':
            return self.emit(302, extra={'Location':'http://127.0.0.1:18593/redirected'})
        if mode == 'timeout':
            time.sleep(6.5)
        if mode == 'delay':
            time.sleep(3.5)
        version = '3.0.1' if mode == 'delay' else ('3.1.0' if self.server.label == 'B' else '3.0.3')
        doc = {'openapi':version,'info':{'title':'Owner QA','version':'1'},'paths':{'/qa':{'get':{'operationId':'qaGet','responses':{'200':{'description':'ok'}}}}}}
        return self.emit(200, json.dumps(doc).encode())
    def reject(self):
        print(f'{self.server.label} {self.command} {self.path}', flush=True)
        self.emit(405)
    do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = reject

servers = []
for label, port in [('B', 18592), ('A/C', 18593)]:
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.label = label
    servers.append(server)
for server in servers:
    threading.Thread(target=server.serve_forever, daemon=True).start()
print('READY B=18592 A/C=18593', flush=True)
threading.Event().wait()
PY
python3 -u "$SMA_QA_ROOT/fixture.py" > "$SMA_QA_ROOT/fixture.log" 2>&1 &
SMA_QA_PID=$!
```

用 `cat "$SMA_QA_ROOT/fixture.log"` 确认出现 `READY B=18592 A/C=18593` 且没有绑定错误。之后才在同一终端执行 `pnpm tauri dev --config "$SMA_QA_ROOT/overlay.json"`；确认窗口标题是 `SMA-005 Owner Check`、顶部 HTTP 关闭、没有配置错误。启动失败时停止，不改用已安装的旧 app。停止该进程后保留同一隔离 profile；再次启动前按步骤设置同一终端的 `SMA_HTTP_ENABLED`。

### 2. Owner 自己执行保存、只测与重开

1. 在 HTTP 关闭时，连接页设置 A：`http`、`127.0.0.1`、`18593`，点“保存连接”；确认成功，fixture 日志无请求。再把端口改成 B 的 `18592`，点“测试 OpenAPI”，应显示 HTTP 已关闭、B 测试地址，日志仍无新增。关闭 Tauri 进程。
2. 同一终端执行 `export SMA_HTTP_ENABLED=true`，再运行相同的 `pnpm tauri dev --config "$SMA_QA_ROOT/overlay.json"`。应恢复已保存的 A。为使目录与材料检查非空，在“API 材料”点“显式网络刷新（先预览）”，检查 `GET /qa` 清单后应用目录，勾选该项并点“保存入选”。这是对 A 的单次 `GET /openapi.json` 和明确的本地配置保存，不发送目标请求。
3. 在另一终端设置刚才打印的 `SMA_QA_ROOT` 绝对路径，运行 `sqlite3 -readonly "$SMA_QA_ROOT/profile/configuration.sqlite3" 'SELECT revision, document, updated_at FROM configuration WHERE singleton=1;' > "$SMA_QA_ROOT/before.txt"`。记录 fixture 日志当前行数和已保存目录/入选状态。若可打开该隔离窗口的 Web Inspector，在 Console 安装以下纯观察器；确认包装成功后清空计数，再测试 B。若不能观测，不把事件计数写成通过。

```js
window.__smaQa = { events: [], invokes: [] };
for (const name of ['sma-backend-connection-changing', 'sma-backend-connection-changed']) {
  window.addEventListener(name, () => window.__smaQa.events.push(name));
}
const originalInvoke = window.__TAURI_INTERNALS__.invoke;
const qaInvoke = function (command, ...args) {
  window.__smaQa.invokes.push(command);
  return originalInvoke.call(this, command, ...args);
};
window.__TAURI_INTERNALS__.invoke = qaInvoke;
window.__TAURI_INTERNALS__.invoke === qaInvoke;
```

4. 回连接页把端口改为 B `18592`，**只点“测试 OpenAPI”，不点保存**。预期显示 B、OpenAPI `3.1.0`、连接未保存；日志新增恰好 `B GET /openapi.json` 一行。Console 中 `window.__smaQa.events` 应为空，`window.__smaQa.invokes` 不含 `change_local_configuration`。再次用上面的只读 SQL 输出 `after.txt`，`cmp "$SMA_QA_ROOT/before.txt" "$SMA_QA_ROOT/after.txt"` 应无差异。关闭并重开相同隔离窗口，应恢复 A、目录和已选材料。重开会重置观察器，后续需要时重新安装。

### 3. Owner 自己执行失败、竞态与冲突

另一终端用 `printf 'status\n' > "$SMA_QA_ROOT/mode"`，再以 B 测试；依次把 mode 改为 `invalid`、`timeout`、`redirect`、`drop` 并各测一次。预期分别是非成功、无效响应、超时、无法连接或重定向、不可达提示；每次仅 B 的 `/openapi.json` 有一条 GET，特别检查没有 `A/C GET /redirected`。每次只测后 SQLite 快照不变。把 mode 改回 `good`。

输入主机 `bad host`、`127.0.0.1/path`、`user@127.0.0.1` 或无效端口，逐次测试应拒绝且 fixture 日志不增加。竞态一：mode 为 `delay` 时测 B，3.5 秒内改成 A/C `18593` 并测试；最终是 A/C 的 `3.0.3`，稍后 B 的 `3.0.1` 不得覆盖。竞态二：mode 为 `delay` 时测 B，立即改主机或端口再改回 B；将 mode 改为 `good` 后再测 B，最终保留新请求的 `3.1.0`。每次改变地址应立即清掉旧结果和目录。

真实冲突可只用同一隔离窗口产生：连接页留着未保存 B，切到“目标 API 配置”→“新建手工配置”，填 API 键 `qa_target`、名称 `QA Target`、方法 **GET**、相对路径 `/qa`、JSON 模板 `{}`；增加一个 `query` 参数，名称 `reading`、类型 `string`，保存本地配置。返回连接页，B 草稿仍在；点保存应报告配置已变化并保留 B。用只读 SQL 比较冲突前后，后者保留新目标和原 A、revision 不再增加。此步骤只保存本地配置，不调用目标。

关闭窗口，将 `SMA_HTTP_ENABLED=false` 后重开；确认地址 A，再改 B 并点“保存连接”。记下保存前后 revision，应恰好加 1，fixture 不增加请求；之后再重开应加载 B。不要用手写 SQL 修改数据库制造冲突。

### 4. Owner 自己检查运行与界面

- 在 HTTP false 和 true 的两次隔离启动中分别打开“映射运行”和“映射配置”：均显示“当前仅支持配置和预览，映射投递未启用”；启动、恢复、单次测试和自动启动设置无法通过鼠标、键盘或页面入口触发。状态、计数和日志可读；只有状态适用时才出现暂停/停止。检查 fixture 无新的目标请求。
- 可用上一步的 `qa_target` 创建一条纯本地映射：选择它，映射键 `qa_mapping`、名称 `QA Mapping`，将 `query:reading` 保持为事实绑定，填写合成 `sourceKey=qa-source`、`factName=reading`，保存后点“已保存配置预览”。确认预览可读，缺少真实事实值时保持缺失，fixture 无请求。若现有环境无法形成 running/paused，记录为未验证，不通过启动旧执行器来制造状态。
- 比较隔离 `runtime-startup.json` 在重开前后的 SHA-256 和内容，仍应是上述 `enabled:true`。同时检查本次进程日志中是否出现执行准入拒绝；这些只能作为辅助观察，不能单独证明从启动前到结束所有 IPC 的计数。内存探针与源码证据见上文。
- 在两个窗口尺寸 1280×800 与 1024×720 下，各检查中文/英文和明色/暗色四种组合；用 Tab/Enter 完成测试或保存，记录可见焦点、目标地址/状态、提示是否可读以及是否出现新的页面横向溢出。若窗口尺寸或启动前 IPC 无法精确观测，保留该项待复核。

测试完成后 Owner 可在原终端结束本次 fixture（确认 `$SMA_QA_PID` 为上述进程后执行 `kill "$SMA_QA_PID"`），保留隔离目录及输出直到复核完成。不得用这些操作恢复或覆盖默认 profile。

## 资源与 handoff

Verification 未回收任何资源。Development 交接列出的 `/private/tmp/sma005-dev.jmJkKx`、`/private/tmp/sma005-dev-build` 和任务专用 debug app 按其交接保留；本轮构建另使用 `/private/tmp/sma005-verification-build`。关键结论和限制已写在本文件，不以临时路径为唯一证据；后续由 coordinator 核实归属、占用与依赖后按 canonical workflow 收尾。

**交 Human Owner：**按上面 GET-only 隔离步骤提供观察与缺口；如遇实际不符，记录具体步骤和输出，交 Development 处理。当前没有 Human Owner 最终验收记录，也没有发布、部署、真实数据迁移或设备操作授权。
