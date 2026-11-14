/** 启动开关的 IPC 交互和中英文组件渲染；不连接设备或后端。 */
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const ts = require('typescript'), vue = require('vue'), sfc = require('vue/compiler-sfc')
const text = path => readFileSync(new URL(path, import.meta.url), 'utf8')
const transpile = source => ts.transpileModule(source, { compilerOptions:{ module:ts.ModuleKind.CommonJS, target:ts.ScriptTarget.ES2020 } }).outputText

test('switches save only their next-start preference and preserve state on failure', async t => {
  const calls = [], scope = vue.effectScope(), mod = { exports:{} }
  let current = { schemaVersion:1, autoCollect:false, autoReport:false }, fail = ''
  const localCall = async (command, request = {}) => {
    calls.push({ command, request })
    if (command === 'daa_get_startup_settings') return { settings:{...current}, errors:{} }
    if (command === 'daa_save_startup_settings') {
      if (fail) throw new Error(fail)
      current = {...request}; return { settings:{...current}, errors:{} }
    }
    throw new Error(`unexpected operation ${command}`)
  }
  const source = transpile(text('../src/console/composables/useLocalAcquisitionConsole.ts'))
  new Function('require','module','exports',source)(id => {
    if (id === 'vue') return {...vue,onMounted(){},onUnmounted(){}}
    if (id === 'vue-i18n') return {useI18n:()=>({t:key=>key,te:()=>false})}
    if (id === 'element-plus') return {ElMessageBox:{}}
    if (id.endsWith('/localAcquisition')) return {bootstrap:{localStorage:true,origin:'native'},localCall,LocalCommandError:class extends Error{}}
    if (id.endsWith('/factsDelivery') || id.endsWith('/time')) return {}
    throw new Error(id)
  }, mod, mod.exports)
  const local=scope.run(()=>mod.exports.useLocalAcquisitionConsole()); t.after(()=>scope.stop())
  await local.loadStartup(); await local.saveStartup('autoCollect',true)
  assert.deepEqual(current,{schemaVersion:1,autoCollect:true,autoReport:false})
  assert.equal(local.startupSaved,true)
  fail='storage_busy'; await local.saveStartup('autoReport',true)
  assert.equal(local.startup.settings.autoReport,false); assert.equal(local.startupError,'storage_busy')
  fail='storage_pending'; await local.saveStartup('autoReport',true)
  assert.equal(local.startup,null); assert.equal(local.startupError,'startup_settings_pending')
  fail=''; await local.loadStartup(); assert.equal(local.startup.settings.autoReport,false)
  assert.deepEqual(calls.map(call=>call.command),['daa_get_startup_settings','daa_save_startup_settings','daa_save_startup_settings','daa_save_startup_settings','daa_get_startup_settings'])
})

test('startup card renders independent switches and help in both languages', async () => {
  const { createI18n } = require('vue-i18n'), { renderToString } = require('vue/server-renderer')
  const injection = Symbol('local'), descriptor=sfc.parse(text('../src/components/console/StartupSettings.vue')).descriptor
  const code=transpile(sfc.compileScript(descriptor,{id:'startup-test',inlineTemplate:true}).content), mod={exports:{}}
  new Function('require','module','exports',code)(id=>{
    if (id==='vue' || id==='vue-i18n' || id==='element-plus' || id==='@element-plus/icons-vue') return require(id)
    if (id.endsWith('/useLocalAcquisitionConsole')) return {localConsoleKey:injection}
    throw new Error(id)
  },mod,mod.exports)
  for (const [locale, expected] of [['zh-CN',['启动设置','启动后自动采集','启动后自动上报']],['en-US',['Startup settings','Collect after startup','Report after startup']]]) {
    const app=vue.createSSRApp(mod.exports.default)
    app.use(require('element-plus').ElIcon); app.use(require('element-plus').ElAlert); app.use(require('element-plus').ElButton)
    app.use(createI18n({legacy:false,locale,messages:{[locale]:{common:JSON.parse(text(`../src/locales/${locale}/common.json`))}}}))
    app.provide(injection,{startup:{settings:{autoCollect:false,autoReport:true},errors:{}},startupBusy:false,bootstrap:{uploadAvailable:true}})
    const html=await renderToString(app)
    for(const label of expected) assert.ok(html.includes(label),`${locale}: ${label}`)
    assert.match(html,/aria-describedby="daa-startup-help"/)
    assert.equal((html.match(/role="switch"/g)||[]).length,2)
  }
})

test('startup card help, collapse and each switch respond independently', async t => {
  const { createI18n }=require('vue-i18n'), injection=Symbol('local'), calls=[]
  for(const [locale,title,helpLabel,collapseLabel,expandLabel,collectLabel,reportLabel] of [
    ['zh-CN','启动设置','启动设置说明','折叠启动设置','展开启动设置','启动后自动采集','启动后自动上报'],
    ['en-US','Startup settings','About startup settings','Collapse startup settings','Expand startup settings','Collect after startup','Report after startup'],
  ]){
  calls.length=0
  const owner=vue.reactive({startup:{settings:{autoCollect:false,autoReport:false},errors:{}},startupBusy:false,startupError:'',startupSaved:false,bootstrap:{uploadAvailable:true},saveStartup(field,value){calls.push([field,value]);this.startup.settings[field]=value}})
  const Switch=vue.defineComponent({props:['modelValue','disabled'],emits:['change'],setup(props,{emit,attrs}){return ()=>vue.h('button',{role:'switch','aria-label':attrs['aria-label'],disabled:props.disabled,onClick:()=>emit('change',!props.modelValue)})}})
  const descriptor=sfc.parse(text('../src/components/console/StartupSettings.vue')).descriptor
  const code=transpile(sfc.compileScript(descriptor,{id:'startup-interaction',inlineTemplate:true}).content),mod={exports:{}}
  new Function('require','module','exports',code)(id=>{
    if(id==='element-plus') return {...require(id),ElSwitch:Switch}
    if(id==='vue'||id==='vue-i18n'||id==='@element-plus/icons-vue') return require(id)
    if(id.endsWith('/useLocalAcquisitionConsole')) return {localConsoleKey:injection}
    throw new Error(id)
  },mod,mod.exports)
  const node=(type,text='')=>({type,text,style:{display:''},props:{},children:[],parent:null})
  const renderer=vue.createRenderer({createElement:node,createText:text=>node('#text',text),createComment:text=>node('#comment',text),setText(el,text){el.text=text},setElementText(el,text){el.text=text},patchProp(el,key,_old,value){el.props[key]=value},insert(child,parent,anchor){child.parent=parent;const old=parent.children.indexOf(child);if(old>=0)parent.children.splice(old,1);const i=anchor?parent.children.indexOf(anchor):-1;if(i>=0)parent.children.splice(i,0,child);else parent.children.push(child)},remove(el){if(el.parent){const i=el.parent.children.indexOf(el);if(i>=0)el.parent.children.splice(i,1)}},parentNode:el=>el.parent,nextSibling:el=>{if(!el.parent)return null;const i=el.parent.children.indexOf(el);return el.parent.children[i+1]||null}})
  const root=node('root'),app=renderer.createApp(mod.exports.default)
  app.use(createI18n({legacy:false,locale,messages:{[locale]:{common:JSON.parse(text(`../src/locales/${locale}/common.json`))}}}))
  for(const name of ['el-icon','el-alert','el-button']) app.component(name,vue.defineComponent({setup(_,{slots}){return ()=>vue.h('div',slots.default?.())}}))
  app.provide(injection,owner);app.mount(root);t.after(()=>app.unmount())
  const all=(n,predicate)=>[...(predicate(n)?[n]:[]),...n.children.flatMap(c=>all(c,predicate))]
  const byLabel=label=>all(root,n=>n.props['aria-label']===label)[0]
  const help=byLabel(helpLabel);help.props.onFocus();await vue.nextTick();assert.equal(help.props['aria-expanded'],true)
  help.props.onBlur();await vue.nextTick();assert.equal(help.props['aria-expanded'],false)
  help.parent.props.onMouseenter();await vue.nextTick();assert.equal(help.props['aria-expanded'],true)
  help.parent.props.onMouseleave();await vue.nextTick();assert.equal(help.props['aria-expanded'],false)
  byLabel(collectLabel).props.onClick();await vue.nextTick()
  byLabel(reportLabel).props.onClick();await vue.nextTick()
  assert.deepEqual(calls,[['autoCollect',true],['autoReport',true]])
  help.props.onClick();await vue.nextTick();assert.equal(help.props['aria-expanded'],true)
  byLabel(collapseLabel).props.onClick();await vue.nextTick()
  assert.equal(all(root,n=>n.props.id==='daa-startup-body').length,0)
  assert.equal(byLabel(helpLabel),undefined)
  assert.equal(all(root,n=>n.props.id==='daa-startup-help').length,0)
  byLabel(expandLabel).props.onClick();await vue.nextTick()
  assert.equal(all(root,n=>n.props.id==='daa-startup-body').length,1)
  const reopened=byLabel(helpLabel);assert.equal(reopened.props['aria-expanded'],false)
  reopened.props.onFocus();await vue.nextTick();assert.equal(reopened.props['aria-expanded'],true)
  const titleButton=all(root,n=>n.type==='button' && n.text===title)[0]
  titleButton.props.onClick();await vue.nextTick();assert.equal(byLabel(helpLabel),undefined)
  byLabel(expandLabel).props.onClick();await vue.nextTick();assert.equal(byLabel(helpLabel).props['aria-expanded'],false)
  }
})

test('both reporting panels render the requested action and destination in both languages', async () => {
  const {createI18n,useI18n}=require('vue-i18n'),{renderToString}=require('vue/server-renderer'),key=Symbol('local')
  const Card=vue.defineComponent({props:['titleKey'],setup(props,{slots}){const {t}=useI18n();return ()=>vue.h('section',[vue.h('h2',t(props.titleKey)),slots.actions?.(),slots.tools?.(),slots.default?.()])}})
  const Action=vue.defineComponent({props:['labelKey'],setup(props){const {t}=useI18n();return ()=>vue.h('button',t(props.labelKey))}})
  const Empty=vue.defineComponent({setup(){return ()=>vue.h('div')}})
  const descriptor=sfc.parse(text('../src/components/console/FactsDeliveryPanel.vue')).descriptor
  const code=transpile(sfc.compileScript(descriptor,{id:'report-panel',inlineTemplate:true}).content),mod={exports:{}}
  new Function('require','module','exports',code)(id=>{
    if(id==='vue'||id==='vue-i18n')return require(id)
    if(id==='element-plus')return Object.fromEntries(['ElAlert','ElDialog','ElTable','ElTableColumn','ElSelect','ElOption'].map(name=>[name,Empty]))
    if(id.endsWith('/useLocalAcquisitionConsole'))return {localConsoleKey:key}
    if(id.endsWith('/time'))return {formatBusinessTime:value=>value||'—'}
    if(id.endsWith('/tableWidths'))return {widthKey:()=>'',loadWidths:(_storage,_key,columns)=>Object.fromEntries(columns.map(c=>[c.id,c.width])),saveWidth:()=>({}),resetWidths:()=>({})}
    if(id.endsWith('/ConsoleCard.vue'))return {default:Card}
    if(id.endsWith('/ConsoleActionButton.vue'))return {default:Action}
    if(id.endsWith('.vue'))return {default:Empty}
    throw new Error(id)
  },mod,mod.exports)
  const origin='http://127.0.0.1:8000/'+ 'very-long-path/'.repeat(8), stamp='2026-11-14 11:46:56'
  for(const locale of ['zh-CN','en-US'])for(const configure of [false,true]){
    const app=vue.createSSRApp(mod.exports.default,{configure})
    app.use(createI18n({legacy:false,locale,messages:{[locale]:{common:JSON.parse(text(`../src/locales/${locale}/common.json`))}}}))
    app.provide(key,{bootstrap:{uploadAvailable:true},busy:false,delivery:{running:false,state:'stopped',origin,lastAcknowledgedAt:stamp,historicalV1Acknowledged:0,sampleCounts:{pending:0,unknown:0,needsProcessing:0,acknowledged:7}},deliveryCursors:[null],deliveryPageNumber:1,deliveryPageSize:20,deliveryState:'',label:s=>s||'—'})
    const html=await renderToString(app)
    assert.ok(html.includes(locale==='zh-CN'?'启动上报':'Start reporting'))
    assert.ok(html.includes(origin));assert.ok(html.includes(stamp));assert.ok(html.indexOf(origin)<html.indexOf(stamp))
  }
  assert.match(text('../src/styles/app.css'),/\.daa-reporting-destination\s*\{\s*display:grid;\s*grid-template-columns:max-content minmax\(0,1fr\)/)
  assert.match(text('../src/App.vue'),/<ConfigRevisionBar v-if="activeSection !== 'workbench'"/)
  const overview=text('../src/app/runtime/views/overview/index.vue')
  assert.ok(overview.indexOf('daa-local-metrics')<overview.indexOf('<StartupSettings') && overview.indexOf('<StartupSettings')<overview.indexOf('<FactsDeliveryPanel'))
})

test('report refresh failure is independent, hides stale values on both pages, and leaves safe pause', async t => {
  const {createI18n,useI18n}=require('vue-i18n'),{renderToString}=require('vue/server-renderer')
  const scope=vue.effectScope(),calls=[],ownerModule={exports:{}}
  let collectionFails=false,reportFails=false,saveFails='',commandFails='',stamp='2026-11-14 11:00:01',deferredRead=null
  let report={running:true,state:'running',origin:'http://fixture.invalid/unique-target',lastAcknowledgedAt:'2026-11-14 10:59:59',historicalV1Acknowledged:2,sampleCounts:{pending:13,unknown:0,needsProcessing:0,acknowledged:7}}
  let settings={identityMode:'per_plc',settingsRevision:'r1',origin:'http://fixture.invalid/unique-target',path:'/samples'}
  const material={contractVersion:'plc-facts/v2',sources:[{instanceId:'instance',plcId:'plc',dbNumber:21,sourceGeneration:'gen'}]}
  const config={draft:{plcs:[],dbs:[],groups:[],points:[],sources:[]},active:'rev1',issues:[]}
  const facts={
    getDeliverySnapshot:async()=>{if(deferredRead){const read=deferredRead;deferredRead=null;read.started();return read.value}if(reportFails)throw Error('storage_busy');return {...report}},
    getDeliverySettings:async()=>({...settings}),getFactsSourceMaterial:async()=>material,
    saveDeliverySettings:async next=>{calls.push('save');report={...report,running:false,state:'stopped',origin:next.origin};if(saveFails)throw Error(saveFails);settings={...next,settingsRevision:'r2'};return {...settings}},
    setDelivery:async action=>{calls.push(action);report={...report,running:action!=='pause',state:action==='pause'?'stopped':'running'};if(commandFails===action)throw Error('storage_busy');return {...report}},
    rebindDelivery:async()=>{calls.push('rebind');if(commandFails==='rebind')throw Error('storage_busy');return {...report}},
    getDelivery:async()=>({batchId:'sample',origin:settings.origin}),
  }
  const localCall=async command=>{if(command!=='daa_get_local_snapshot')throw Error(command);if(collectionFails)throw Error('read_failed');return {configuration:config,plcs:[],capacity:{pendingCount:0,state:'ready'},generatedAt:stamp}}
  new Function('require','module','exports',transpile(text('../src/console/composables/useLocalAcquisitionConsole.ts')))(id=>{
    if(id==='vue')return {...vue,onMounted(){},onUnmounted(){}}
    if(id==='vue-i18n')return {useI18n:()=>({t:key=>key,te:()=>false})}
    if(id==='element-plus')return {ElMessageBox:{confirm:async()=>{}}}
    if(id.endsWith('/localAcquisition'))return {bootstrap:{localStorage:true,origin:'native',uploadAvailable:true},localCall,LocalCommandError:class extends Error{}}
    if(id.endsWith('/factsDelivery'))return facts
    if(id.endsWith('/time'))return {}
    throw Error(id)
  },ownerModule,ownerModule.exports)
  const previousDocument=globalThis.document;globalThis.document={querySelector:()=>null}
  t.after(()=>{if(previousDocument===undefined)delete globalThis.document;else globalThis.document=previousDocument})
  const local=scope.run(()=>ownerModule.exports.useLocalAcquisitionConsole());t.after(()=>scope.stop())
  const Card=vue.defineComponent({props:['titleKey'],setup(props,{slots}){const {t}=useI18n();return ()=>vue.h('section',[vue.h('h2',t(props.titleKey)),slots.actions?.(),slots.tools?.(),slots.default?.()])}})
  const Action=vue.defineComponent({props:['labelKey','disabled'],setup(props){const {t}=useI18n();return ()=>vue.h('button',{disabled:props.disabled},t(props.labelKey))}})
  const Alert=vue.defineComponent({props:['title','description'],setup(props){return ()=>vue.h('aside',{role:'alert'},[props.title,props.description])}})
  const Empty=vue.defineComponent({setup(){return ()=>null}})
  const descriptor=sfc.parse(text('../src/components/console/FactsDeliveryPanel.vue')).descriptor,mod={exports:{}}
  new Function('require','module','exports',transpile(sfc.compileScript(descriptor,{id:'report-refresh',inlineTemplate:true}).content))(id=>{
    if(id==='vue'||id==='vue-i18n')return require(id)
    if(id==='element-plus')return {ElAlert:Alert,ElDialog:Empty,ElTable:Empty,ElTableColumn:Empty,ElSelect:Empty,ElOption:Empty}
    if(id.endsWith('/useLocalAcquisitionConsole'))return ownerModule.exports
    if(id.endsWith('/time'))return {formatBusinessTime:value=>value||'—'}
    if(id.endsWith('/tableWidths'))return {widthKey:()=>'',loadWidths:()=>({}),saveWidth:()=>({}),resetWidths:()=>({})}
    if(id.endsWith('/ConsoleCard.vue'))return {default:Card}
    if(id.endsWith('/ConsoleActionButton.vue'))return {default:Action}
    if(id.endsWith('.vue'))return {default:Empty}
    throw Error(id)
  },mod,mod.exports)
  const render=async(locale,configure)=>{
    const app=vue.createSSRApp(mod.exports.default,{configure})
    app.use(createI18n({legacy:false,locale,messages:{[locale]:{common:JSON.parse(text(`../src/locales/${locale}/common.json`))}}}))
    app.provide(ownerModule.exports.localConsoleKey,local)
    return renderToString(app)
  }
  assert.match(text('../src/app/runtime/views/overview/index.vue'),/<FactsDeliveryPanel\s*\/>/)
  assert.match(text('../src/app/collection/views/storage/index.vue'),/<FactsDeliveryPanel configure\s*\/>/)
  await local.refresh()
  assert.equal(local.delivery.sampleCounts.pending,13)
  stamp='2026-11-14 11:04:22';reportFails=true
  await local.refresh()
  assert.equal(local.snapshot.generatedAt,stamp)
  assert.equal(local.snapshotError,'')
  assert.equal(local.deliverySnapshotError,'storage_busy')
  for(const locale of ['zh-CN','en-US'])for(const configure of [false,true]){
    const html=await render(locale,configure)
    assert.ok(html.includes(locale==='zh-CN'?'上报状态暂不可用':'Reporting status is unavailable'))
    assert.ok(html.includes(locale==='zh-CN'?'暂停上报':'Pause delivery'))
    assert.ok(!html.includes(locale==='zh-CN'?'>启动上报</button>':'>Start reporting</button>'))
    assert.ok(!html.includes('http://fixture.invalid/unique-target'))
    assert.ok(!html.includes('2026-11-14 10:59:59'))
    assert.ok(!html.includes('2026-11-14 11:04:22'))
    assert.ok(!html.includes('>13</strong>')&&!html.includes('>7</strong>'))
  }
  await local.deliveryControl('start')
  assert.equal(local.error,'delivery_snapshot_unavailable');assert.deepEqual(calls,[])
  await local.deliveryControl('pause')
  assert.deepEqual(calls,['pause']);assert.equal(local.deliverySnapshotError,'')
  reportFails=false;await local.refresh()
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.state,'stopped')
  for(const locale of ['zh-CN','en-US'])for(const configure of [false,true]){
    const html=await render(locale,configure)
    assert.ok(html.includes(locale==='zh-CN'?'启动上报':'Start reporting'))
    assert.ok(html.includes('http://fixture.invalid/unique-target'))
    assert.ok(!html.includes(locale==='zh-CN'?'上报状态暂不可用':'Reporting status is unavailable'))
  }
  collectionFails=true;report={...report,sampleCounts:{...report.sampleCounts,pending:42}}
  await local.refresh()
  assert.equal(local.snapshotError,'read_failed');assert.equal(local.deliverySnapshotError,'')
  assert.equal(local.delivery.sampleCounts.pending,42)

  // QA2 F-004：设置已保存并暂停，后续快照读取失败时不能显示旧上报状态。
  collectionFails=false;report={...report,running:true,state:'running',origin:'http://fixture.invalid/unique-target'}
  await local.refresh();local.deliverySettings={...settings};local.deliveryDialog='settings'
  reportFails=true
  await local.saveDelivery({...settings,origin:'http://fixture.invalid/new-target'})
  assert.equal(local.deliverySettings.origin,'http://fixture.invalid/new-target')
  assert.equal(local.deliverySnapshotError,'storage_busy');assert.equal(local.deliveryDialog,null)
  for(const locale of ['zh-CN','en-US'])for(const configure of [false,true]){
    const html=await render(locale,configure)
    assert.ok(html.includes(locale==='zh-CN'?'上报状态暂不可用':'Reporting status is unavailable'))
    assert.ok(html.includes(locale==='zh-CN'?'暂停上报':'Pause delivery'))
    assert.ok(!html.includes('http://fixture.invalid/unique-target')&&!html.includes('2026-11-14 10:59:59'))
    assert.ok(!html.includes('>42</strong>')&&!html.includes('>7</strong>'))
    assert.ok(!html.includes(locale==='zh-CN'?'>启动上报</button>':'>Start reporting</button>'))
  }
  const beforeStart=calls.length;await local.deliveryControl('start');assert.equal(calls.length,beforeStart)
  reportFails=false;await local.refresh()
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.origin,'http://fixture.invalid/new-target');assert.equal(local.delivery.running,false)

  // 保存结果未知时也不能把保存前状态作为当前状态。
  saveFails='storage_pending';local.deliverySettings={...settings};local.deliveryDialog='settings'
  await local.saveDelivery({...settings,origin:'http://fixture.invalid/pending-target'})
  assert.equal(local.deliverySaveError,'storage_pending');assert.equal(local.deliverySnapshotError,'storage_pending')
  saveFails='';await local.refresh();assert.equal(local.deliverySnapshotError,'')

  // 启动/暂停/改绑 IPC 可能已经改变运行状态后才因返回快照失败。
  for(const action of ['start','pause','rebind']){
    commandFails=action
    if(action==='rebind'){local.deliveryDetail={batchId:'sample',origin:'http://fixture.invalid/old-target'};await local.rebindDelivery()}
    else await local.deliveryControl(action)
    assert.equal(local.deliverySnapshotError,'storage_busy',action)
    const before=calls.length;await local.deliveryControl('start');assert.equal(calls.length,before)
    commandFails='';await local.refresh();assert.equal(local.deliverySnapshotError,'')
  }

  // 保存期间先前发出的轮询迟到，即使它成功也不能恢复旧目标。
  let resolveOld,signalStarted
  const oldStarted=new Promise(resolve=>{signalStarted=resolve})
  const oldValue=new Promise(resolve=>{resolveOld=resolve})
  const oldSnapshot={...report,origin:'http://fixture.invalid/stale-poll'}
  deferredRead={started:signalStarted,value:oldValue}
  const pendingRefresh=local.refresh();await oldStarted
  local.deliverySettings={...settings};reportFails=true
  await local.saveDelivery({...settings,origin:'http://fixture.invalid/final-target'})
  assert.equal(local.deliverySnapshotError,'storage_busy')
  resolveOld(oldSnapshot);await pendingRefresh
  assert.equal(local.deliverySnapshotError,'storage_busy')
  assert.notEqual(local.delivery?.origin,'http://fixture.invalid/stale-poll')
  reportFails=false;await local.refresh()
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.origin,'http://fixture.invalid/final-target')

  // 即使上一轮读取失败迟到，也不能污染保存成功后的新快照。
  let rejectOld,signalSecond
  const secondStarted=new Promise(resolve=>{signalSecond=resolve})
  const oldFailure=new Promise((_resolve,reject)=>{rejectOld=reject})
  deferredRead={started:signalSecond,value:oldFailure}
  const lateFailure=local.refresh();await secondStarted
  local.deliverySettings={...settings}
  await local.saveDelivery({...settings,origin:'http://fixture.invalid/saved-target'})
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.origin,'http://fixture.invalid/saved-target')
  rejectOld(Error('storage_busy'));await lateFailure
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.origin,'http://fixture.invalid/saved-target')

  // 保存已改变目标、后续读取尚未返回的期间也不得呈现旧状态。
  let resolveSaved,signalSaved
  const savedReadStarted=new Promise(resolve=>{signalSaved=resolve})
  const savedRead=new Promise(resolve=>{resolveSaved=resolve})
  deferredRead={started:signalSaved,value:savedRead};local.deliverySettings={...settings}
  const saving=local.saveDelivery({...settings,origin:'http://fixture.invalid/waiting-target'})
  await savedReadStarted
  assert.equal(local.deliverySnapshotError,'delivery_snapshot_unavailable')
  const duringSave=await render('zh-CN',false)
  assert.ok(duringSave.includes('上报状态暂不可用')&&!duringSave.includes('http://fixture.invalid/saved-target'))
  resolveSaved({...report});await saving
  assert.equal(local.deliverySnapshotError,'');assert.equal(local.delivery.origin,'http://fixture.invalid/waiting-target')
})
