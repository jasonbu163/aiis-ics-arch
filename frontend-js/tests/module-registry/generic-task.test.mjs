/** 执行通用任务 SFC setup，验证历史列、角色入口、草稿与动作重试。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'
import { formatShanghaiDateTime } from '../../src/utils/date.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const source = await readFile(`${root}/src/app/plan/components/TaskPage.vue`, 'utf8')
const { descriptor } = parse(source)
const executable = compileScript(descriptor, { id:'task-page-test' }).content
  .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
    if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
    return `const ${binding} = deps[${JSON.stringify(module)}]`
  }).replace('export default', 'return')
const make = new Function('deps', executable)
const tick = async () => { await vue.nextTick(); await Promise.resolve(); await vue.nextTick() }
const field = (enabled, name='completedLength') => ({scope:'shared_sync',slotNo:3,name,type:'number',labels:{'zh-CN':'反馈','en-US':'Feedback'},enabled,planVisible:true,performanceVisible:true,planOrder:3,performanceOrder:3,performanceOwner:'automated',syncEnabled:true,planEditable:false,performanceEditable:false})

function page(kind, role='admin') {
  const local = new Map(), hooks=[], calls=[]
  globalThis.localStorage={getItem:key=>local.get(key) ?? null,setItem:(key,value)=>local.set(key,value),removeItem:key=>local.delete(key)}
  const old = { id:'1',taskNo:'GT1-RUN-A',targetKey:'LINE-01',fieldConfigVersion:3,productionStatus:'running',hasPlan:true,syncValues:{completedLength:50},localValues:{} }
  const active = { ...old,id:'2',taskNo:'GT1-RUN-B',fieldConfigVersion:4,syncValues:{} }
  const api = {
    getConfig: async (_module, version) => ({fieldConfigVersion:version || 4,configRevision:'4',fields:[field(version === 3)]}),
    list: async params => { calls.push(params); return {items:[old,active],total:2} },
    detail: async id => ({ ...old, id }),
    upsert: async body => { calls.push(body) },
    action: async () => {},
    supplement: async () => {}
  }
  const user={role,isAdmin:role==='admin',username:'fixture',hasPageAccess:()=>true}
  const customVue={...vue,onMounted: fn => hooks.push(fn)}
  const deps={vue:customVue,'vue-i18n':{useI18n:()=>({t:key=>key,te:()=>true,locale:vue.ref('en-US')})},
    'element-plus':{ElMessage:{error(){},success(){}},ElMessageBox:{prompt:async()=>({value:'evidence'})}},
    '@element-plus/icons-vue':{Setting:{}},'@/store/user':{useUserStore:()=>user},
    '@/utils/tableColumnWidths':{useTableColumnWidths},'@/utils/date':{formatShanghaiDateTime},
    '@/components/common/BaseCard.vue':{},'@/components/common/ActionButton.vue':{},'./TaskConfigDialog.vue':{}}
  const effect=vue.effectScope()
  const state=effect.run(()=>make(deps).setup({kind,api},{expose(){}}))
  return {state,api,user,local,calls,mount:async()=>{await hooks[0]();await tick()},close:()=>{effect.stop();delete globalThis.localStorage}}
}

test('actual page keeps the historical visible slot while the active version disables it', async () => {
  const p=page('performance')
  try {
    await p.mount()
    assert.deepEqual(p.state.visibleFields.value.map(p.state.fieldKey), ['shared_sync.03'])
    assert.equal(p.state.displayValue(p.state.items.value[0].syncValues.completedLength),'50')
    assert.equal(p.state.displayValue(false),'performance.workflow.no')
    assert.equal(p.state.displayValue(0),'0')
    assert.equal(p.state.configAvailable.value,true)
  } finally { p.close() }
})

test('actual plan form retains a changed draft and clears it after success', async () => {
  const p=page('plan')
  try {
    await p.mount(); await p.state.newPlan()
    p.state.form.value.taskNo='GT1-RUN-A'; p.state.form.value.targetKey='LINE-01'; await tick()
    assert.match(p.local.get('aiis-ics:task-draft:plan:fixture'),/GT1-RUN-A/)
    await p.state.save(); await tick()
    assert.equal(p.local.has('aiis-ics:task-draft:plan:fixture'),false)
    assert.equal(p.calls.at(-1).taskNo,undefined) // last call reloads list
    assert.ok(p.calls.some(value=>value.taskNo==='GT1-RUN-A' && value.targetKey==='LINE-01'))
  } finally { p.close() }
})
