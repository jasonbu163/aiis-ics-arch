<!-- 两个业务入口共同维护共享定义及当前模块本地定义。 -->
<template>
  <el-dialog v-model="open" :title="tr('fieldSettings')" width="calc(100% - 32px)" align-center class="standard-form-dialog task-field-config-dialog" @open="load">
    <div class="config-toolbar">
      <span>{{ tr('configVersion') }}: {{ config?.fieldConfigVersion }} / {{ tr('revision') }}: {{ config?.configRevision }}</span>
      <el-button @click="columns.reset">{{ tr('resetConfigWidths') }}</el-button>
    </div>
    <p class="config-hint">{{ tr('configHint') }}</p>
    <div class="config-table-wrap">
      <el-table :key="columns.version.value" :data="rows" border stripe scrollbar-always-on max-height="min(52vh, 560px)" class="vibe-table config-table" @header-dragend="columns.onHeaderDragEnd">
        <el-table-column prop="name" :label="tr('fieldName')" :width="columns.widths.name" :min-width="columnDefinitions.name.minWidth" :fixed="isNarrow ? false : 'left'">
          <template #default="{ row }">
            <div class="field-key-cell">
              <el-input v-model="row.name" :disabled="!row._new" :title="row.name || undefined" />
              <el-button v-if="row._new" link type="danger" @click="removeDraft(row)">{{ tr('removeDraft') }}</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="scope" :label="tr('scope')" :width="columns.widths.scope" :min-width="columnDefinitions.scope.minWidth">
          <template #default="{ row }">
            <el-select v-model="row.scope" :disabled="!row._new">
              <el-option :label="tr('shared')" value="shared_sync" />
              <el-option :label="tr('local')" :value="`${kind}_local`" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="slotNo" :label="tr('slot')" :width="columns.widths.slotNo" :min-width="columnDefinitions.slotNo.minWidth"><template #default="{ row }"><el-input-number v-model="row.slotNo" :min="1" :max="100" :disabled="!row._new" controls-position="right" /></template></el-table-column>
        <el-table-column prop="type" :label="tr('type')" :width="columns.widths.type" :min-width="columnDefinitions.type.minWidth"><template #default="{ row }"><el-select v-model="row.type" :disabled="!row._new"><el-option v-for="type in types" :key="type" :value="type" :label="tr(`types.${type}`)" /></el-select></template></el-table-column>
        <el-table-column prop="labelZh" :label="tr('labelZh')" :width="columns.widths.labelZh" :min-width="columnDefinitions.labelZh.minWidth"><template #default="{ row }"><el-input v-model="row.labels['zh-CN']" /></template></el-table-column>
        <el-table-column prop="labelEn" :label="tr('labelEn')" :width="columns.widths.labelEn" :min-width="columnDefinitions.labelEn.minWidth"><template #default="{ row }"><el-input v-model="row.labels['en-US']" /></template></el-table-column>
        <el-table-column prop="unit" :label="tr('unit')" :width="columns.widths.unit" :min-width="columnDefinitions.unit.minWidth"><template #default="{ row }"><el-input v-model="row.unit" :disabled="!row._new" /></template></el-table-column>
        <el-table-column prop="performanceOwner" :label="tr('owner')" :width="columns.widths.performanceOwner" :min-width="columnDefinitions.performanceOwner.minWidth"><template #default="{ row }"><el-select v-model="row.performanceOwner" :disabled="row.scope === 'plan_local'" clearable><el-option v-for="owner in owners" :key="owner" :value="owner" :label="tr(`owners.${owner}`)" /></el-select></template></el-table-column>
        <el-table-column v-for="name in boolNames" :key="name" :prop="name" :label="tr(name)" :width="columns.widths[name]" :min-width="columnDefinitions[name].minWidth"><template #default="{ row }"><el-checkbox v-model="row[name]" /></template></el-table-column>
        <el-table-column prop="columnOrder" :label="tr('columnOrder')" :width="columns.widths.columnOrder" :min-width="columnDefinitions.columnOrder.minWidth"><template #default="{ row }"><el-input-number v-model="row[orderName]" :min="0" :max="65535" :precision="0" :value-on-clear="null" :placeholder="tr('slotDefault')" controls-position="right" /></template></el-table-column>
      </el-table>
    </div>
    <template #footer>
      <div class="config-footer">
        <el-button @click="addRow">{{ tr('addField') }}</el-button>
        <el-button @click="open = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ $t('common.save') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
const props = defineProps({ kind: { type: String, required: true }, api: { type: Object, required: true } })
const emit = defineEmits(['saved'])
const { t, te } = useI18n()
const tr = key => t(`${props.kind}.workflow.${key}`)
const open = defineModel({ type: Boolean, default: false })
const config = ref(null)
const rows = ref([])
const original = ref([])
const saving = ref(false)
const hydrated = ref(false)
const isNarrow = ref(false)
let viewportQuery
function updateViewport(event) { isNarrow.value = event.matches }
const user = useUserStore()
const columnDefinitions = {
  name:{width:190,minWidth:150}, scope:{width:150,minWidth:120}, slotNo:{width:110,minWidth:90},
  type:{width:130,minWidth:100}, labelZh:{width:160,minWidth:120}, labelEn:{width:160,minWidth:120},
  unit:{width:110,minWidth:90}, performanceOwner:{width:170,minWidth:140},
  enabled:{width:105,minWidth:85}, isNullable:{width:105,minWidth:85}, syncEnabled:{width:105,minWidth:85},
  planEditable:{width:120,minWidth:95}, performanceEditable:{width:130,minWidth:105},
  planVisible:{width:105,minWidth:85}, performanceVisible:{width:115,minWidth:95}, columnOrder:{width:160,minWidth:140}
}
const columns = useTableColumnWidths(`generic-task.field-settings.${props.kind}`, columnDefinitions)
const draftKey = `aiis-ics:task-config-draft:${props.kind}:${user.username}`
function readDraft() { try { return JSON.parse(localStorage.getItem(draftKey)) } catch { return null } }
function clearDraft() { try { localStorage.removeItem(draftKey) } catch { /* 本机偏好不可用不影响业务。 */ } }
const types = ['string', 'number', 'boolean']
const owners = ['order_snapshot', 'automated', 'manual']
const orderName = computed(() => props.kind === 'plan' ? 'planOrder' : 'performanceOrder')
const boolNames = computed(() => ['enabled', 'isNullable', 'syncEnabled', 'planEditable', 'performanceEditable', props.kind === 'plan' ? 'planVisible' : 'performanceVisible'])
const clone = value => JSON.parse(JSON.stringify(value))
function error(error) {
  const key = error.response?.data?.errorCode?.replace('task.', '')
  ElMessage.error(key && te(`${props.kind}.workflow.errors.${key}`) ? tr(`errors.${key}`) : tr('requestFailed'))
}
async function load() {
  hydrated.value = false
  try {
    config.value = await props.api.getConfig(props.kind)
    original.value = clone(config.value.fields)
    const draft = readDraft()
    rows.value = draft?.version === config.value.fieldConfigVersion && draft?.revision === config.value.configRevision ? draft.rows : clone(config.value.fields)
    hydrated.value = true
  } catch (e) { error(e); open.value = false }
}
function addRow() {
  const used = new Set(rows.value.filter(x => x.scope === `${props.kind}_local`).map(x => x.slotNo))
  let slot = 1
  while (used.has(slot) && slot <= 100) slot++
  if (slot > 100) return ElMessage.error(tr('noSlots'))
  rows.value.push({ _new: true, scope: `${props.kind}_local`, slotNo: slot, name: '', type: 'string', labels: { 'zh-CN': '', 'en-US': '' }, unit: null,
    enabled: false, isNullable: false, syncEnabled: false, planEditable: false, performanceEditable: false,
    performanceOwner: props.kind === 'plan' ? null : 'manual', planVisible: false, performanceVisible: false, planOrder: null, performanceOrder: null })
}
function removeDraft(row) {
  if (!row._new) return
  const index = rows.value.indexOf(row)
  if (index >= 0) rows.value.splice(index, 1)
}
async function save() {
  const fields = ['name','type','unit','enabled','isNullable','syncEnabled','planEditable','performanceEditable','performanceOwner',
    props.kind === 'plan' ? 'planVisible' : 'performanceVisible', orderName.value]
  const changes = rows.value.map(row => {
    const before = original.value.find(x => x.scope === row.scope && x.slotNo === row.slotNo)
    const result = { scope: row.scope, slotNo: row.slotNo }
    for (const key of fields) if (!before || row[key] !== before[key]) result[key] = row[key]
    if (!before || JSON.stringify(row.labels) !== JSON.stringify(before.labels)) result.labels = row.labels
    return result
  }).filter(row => Object.keys(row).length > 2)
  saving.value = true
  try {
    await props.api.saveConfig({ module: props.kind, fieldConfigVersion: config.value.fieldConfigVersion,
      configRevision: config.value.configRevision, changes })
    ElMessage.success(tr('saved')); hydrated.value = false; open.value = false; clearDraft(); emit('saved')
  } catch (e) { error(e) } finally { saving.value = false }
}
watch(rows, value => {
  if (!hydrated.value || !open.value || !config.value) return
  try {
    if (JSON.stringify(value) === JSON.stringify(original.value)) localStorage.removeItem(draftKey)
    else localStorage.setItem(draftKey, JSON.stringify({ version: config.value.fieldConfigVersion, revision: config.value.configRevision, rows: value }))
  } catch { /* 本机偏好不可用不影响业务。 */ }
}, { deep: true })
onMounted(() => {
  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    viewportQuery = window.matchMedia('(max-width: 600px)')
    updateViewport(viewportQuery)
    viewportQuery.addEventListener('change', updateViewport)
  }
  if (user.isAdmin && readDraft()) open.value = true
})
onBeforeUnmount(() => viewportQuery?.removeEventListener('change', updateViewport))
</script>

<style scoped>
/* 宽表弹窗保留标准外壳，但独立限制尺寸和内部滚动。 */
:global(.standard-form-dialog.task-field-config-dialog.el-dialog) { max-width: min(1400px, calc(100vw - 32px)); max-height: calc(100vh - 32px); max-height: calc(100dvh - 32px); display: flex; flex-direction: column; }
:global(.standard-form-dialog.task-field-config-dialog .el-dialog__header), :global(.standard-form-dialog.task-field-config-dialog .el-dialog__footer) { flex: 0 0 auto; }
:global(.standard-form-dialog.task-field-config-dialog .el-dialog__body) { min-height: 0; overflow-y: auto; }
.config-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.config-hint { margin: 12px 0; color: var(--text-secondary); line-height: 1.5; }
.config-table-wrap { width: 100%; min-width: 0; overflow-x: auto; }
.config-table :deep(.el-input-number), .config-table :deep(.el-select), .config-table :deep(.el-input) { width: 100%; max-width: 100%; }
.field-key-cell { display: flex; flex-direction: column; align-items: stretch; gap: 4px; }
.field-key-cell :deep(.el-button) { align-self: flex-start; }
.config-footer { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; }
.config-footer :deep(.el-button + .el-button) { margin-left: 0; }
@media (max-width: 600px) {
  :global(.standard-form-dialog.task-field-config-dialog .el-dialog__header) { min-height: 64px; padding: 20px 24px; }
  :global(.standard-form-dialog.task-field-config-dialog .el-dialog__body) { padding: 16px; }
  :global(.standard-form-dialog.task-field-config-dialog .el-dialog__footer) { padding: 16px; }
}
</style>
