<!-- 计划、实绩与共享字段共用的管理表格、草稿和保存流程。 -->
<template>
  <div v-loading="loading" class="task-field-editor">
    <div class="config-toolbar">
      <span v-if="config">{{ tr('configVersion') }}: {{ config?.configVersion }} / {{ tr('revision') }}: {{ config?.configRevision }}</span>
      <el-button @click="columns.reset">{{ tr('resetConfigWidths') }}</el-button>
    </div>
    <p class="config-hint">{{ tr('configHint') }}</p>
    <el-alert v-if="conflict" :title="tr('errors.config_revision_conflict')" type="warning" :closable="false" show-icon />
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
        <el-table-column prop="slotNo" :label="tr('slot')" :width="columns.widths.slotNo" :min-width="columnDefinitions.slotNo.minWidth"><template #default="{ row }"><el-input-number v-model="row.slotNo" :min="1" :max="100" :disabled="!row._new" controls-position="right" /></template></el-table-column>
        <el-table-column prop="type" :label="tr('type')" :width="columns.widths.type" :min-width="columnDefinitions.type.minWidth"><template #default="{ row }"><el-select v-model="row.type" :disabled="!row._new"><el-option v-for="type in types" :key="type" :value="type" :label="tr(`types.${type}`)" /></el-select></template></el-table-column>
        <el-table-column prop="labelZh" :label="tr('labelZh')" :width="columns.widths.labelZh" :min-width="columnDefinitions.labelZh.minWidth"><template #default="{ row }"><el-input v-model="row.labels['zh-CN']" /></template></el-table-column>
        <el-table-column prop="labelEn" :label="tr('labelEn')" :width="columns.widths.labelEn" :min-width="columnDefinitions.labelEn.minWidth"><template #default="{ row }"><el-input v-model="row.labels['en-US']" /></template></el-table-column>
        <el-table-column prop="unit" :label="tr('unit')" :width="columns.widths.unit" :min-width="columnDefinitions.unit.minWidth"><template #default="{ row }"><el-input v-model="row.unit" :disabled="!row._new" /></template></el-table-column>
        <el-table-column v-if="kind !== 'plan'" prop="performanceOwner" :label="tr('owner')" :width="columns.widths.performanceOwner" :min-width="definition('performanceOwner').minWidth">
          <template #default="{ row }">
            <el-select v-model="row.performanceOwner" @change="changeOwner(row)">
              <el-option v-for="owner in owners" :key="owner" :value="owner" :label="tr(`owners.${owner}`)" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column v-for="name in boolNames" :key="name" :prop="name" :label="tr(name)" :width="columns.widths[name]" :min-width="definition(name).minWidth">
          <template #default="{ row }"><el-checkbox v-model="row[name]" :disabled="optionDisabled(row, name)" /></template>
        </el-table-column>
        <el-table-column v-for="name in orderNames" :key="name" :prop="name" :label="tr(name)" :width="columns.widths[name]" :min-width="definition(name).minWidth">
          <template #default="{ row }"><el-input-number v-model="row[name]" :min="0" :max="65535" :precision="0" :value-on-clear="null" :placeholder="tr('slotDefault')" controls-position="right" /></template>
        </el-table-column>
        <el-table-column :label="tr('actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-popconfirm v-if="!row._new" :title="tr('confirmFieldDelete')" :confirm-button-text="tr('deleteField')" :cancel-button-text="$t('common.cancel')" @confirm="deleteSaved(row)">
              <template #reference><el-button link type="danger" :disabled="saving">{{ tr('deleteField') }}</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="config-footer">
      <el-button :disabled="!config || loading || saving" @click="addRow">{{ tr('addField') }}</el-button>
      <el-button @click="cancel">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" :disabled="!config || loading" :loading="saving" @click="save">{{ $t('common.save') }}</el-button>
    </div>
  </div>
</template>
<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'

const props = defineProps({ kind: { type: String, required: true }, module: { type: String, required: true },
  api: { type: Object, required: true } })
const emit = defineEmits(['saved', 'deleted', 'cancel'])
const { t, te } = useI18n()
const tr = key => t(`${props.module}.workflow.${key}`)
const scope = computed(() => props.kind === 'shared' ? 'shared_sync' : `${props.kind}_local`)
const config = ref(null), rows = ref([]), original = ref([])
const loading = ref(false), saving = ref(false), conflict = ref(false)
const types = ['string', 'number', 'boolean']
const owners = computed(() => props.kind === 'shared' ? ['order_snapshot', 'automated', 'manual'] : ['automated', 'manual'])

const isNarrow = ref(false)
let viewportQuery
function updateViewport(event) { isNarrow.value = event.matches }
const columnDefinitions = {
  name:{width:190,minWidth:150}, slotNo:{width:110,minWidth:90},
  type:{width:130,minWidth:100}, labelZh:{width:160,minWidth:120}, labelEn:{width:160,minWidth:120},
  unit:{width:110,minWidth:90}, performanceOwner:{width:170,minWidth:140},
  enabled:{width:105,minWidth:85}, isNullable:{width:105,minWidth:85}, syncEnabled:{width:110,minWidth:85},
  planEditable:{width:120,minWidth:95}, performanceEditable:{width:130,minWidth:105},
  planVisible:{width:105,minWidth:85}, performanceVisible:{width:115,minWidth:95},
  planOrder:{width:160,minWidth:140}, performanceOrder:{width:160,minWidth:140}
}
const definition = key => columnDefinitions[key]
const columns = useTableColumnWidths(`generic-task.field-settings.${props.kind}`, columnDefinitions)
const boolNames = computed(() => [
  'enabled', 'isNullable',
  ...(props.kind === 'shared' ? ['syncEnabled'] : []),
  ...(props.kind !== 'performance' ? ['planEditable', 'planVisible'] : []),
  ...(props.kind !== 'plan' ? ['performanceEditable', 'performanceVisible'] : [])
])
const orderNames = computed(() => props.kind === 'shared' ? ['planOrder', 'performanceOrder'] : [`${props.kind}Order`])
const clone = value => JSON.parse(JSON.stringify(value))

function optionDisabled(row, name) {
  return (name === 'performanceEditable' && row.performanceOwner !== 'manual')
    || (name === 'syncEnabled' && row.performanceOwner === 'order_snapshot')
}
function changeOwner(row) {
  if (row.performanceOwner !== 'manual') row.performanceEditable = false
  if (row.performanceOwner === 'order_snapshot') row.syncEnabled = false
}
function showError(error) {
  const key = error.response?.data?.errorCode?.replace('task.', '')
  if (key === 'config_revision_conflict') conflict.value = true
  const detail = error.response?.data?.details?.reason
  if (key === 'field_in_use' && detail === 'active_mapping_reference') {
    ElMessage.error(tr('errors.active_mapping_reference'))
    return
  }
  ElMessage.error(key && te(`${props.module}.workflow.errors.${key}`) ? tr(`errors.${key}`) : tr('requestFailed'))
}
function adopt(result) {
  config.value = result
  original.value = result.fields.filter(field => field.scope === scope.value)
  rows.value = clone(original.value)
  conflict.value = false
}
let loadId = 0
async function load() {
  const id = ++loadId
  loading.value = true
  try {
    const result = await props.api.getConfig(props.module)
    if (id === loadId) adopt(result)
  } catch (error) {
    if (id === loadId) showError(error)
  } finally {
    if (id === loadId) loading.value = false
  }
}
function cancel() {
  rows.value = clone(original.value)
  conflict.value = false
  emit('cancel')
  if (props.kind === 'shared') return load()
}
function addRow() {
  const used = new Set(rows.value.map(field => field.slotNo))
  let slot = 1
  while (used.has(slot)) slot++
  if (slot > 100) {
    ElMessage.error(tr('noSlots'))
    return
  }
  rows.value.push({ _new: true, scope: scope.value, slotNo: slot, name: '', type: 'string',
    labels: { 'zh-CN': '', 'en-US': '' }, unit: null, ...Object.fromEntries(boolNames.value.map(name => [name, false])),
    performanceOwner: props.kind === 'plan' ? null : 'manual',
    ...Object.fromEntries(orderNames.value.map(name => [name, null])) })
}
function removeDraft(row) {
  rows.value = rows.value.filter(field => field !== row)
}
function changes() {
  const keys = ['name', 'type', 'unit', ...boolNames.value, ...orderNames.value]
  if (props.kind !== 'plan') keys.push('performanceOwner')
  return rows.value.map(row => {
    const before = original.value.find(field => field.slotNo === row.slotNo)
    const patch = { scope: scope.value, slotNo: row.slotNo }
    for (const key of keys) if (!before || row[key] !== before[key]) patch[key] = row[key]
    if (!before || JSON.stringify(row.labels) !== JSON.stringify(before.labels)) patch.labels = row.labels
    return patch
  }).filter(patch => Object.keys(patch).length > 2)
}
async function save() {
  saving.value = true
  try {
    const result = await props.api.saveConfig({ module: props.kind, configRevision: config.value.configRevision, changes: changes() })
    adopt(result)
    ElMessage.success(tr('saved'))
    emit('saved')
  } catch (error) { showError(error) } finally { saving.value = false }
}
async function deleteSaved(row) {
  saving.value = true
  try {
    const result = await props.api.deleteField({ scope: scope.value, slotNo: row.slotNo, name: row.name,
      configRevision: config.value.configRevision })
    config.value = { ...config.value, configVersion: result.configVersion, configRevision: result.configRevision }
    rows.value = rows.value.filter(field => field !== row)
    original.value = original.value.filter(field => field.slotNo !== row.slotNo)
    ElMessage.success(tr('deletedField'))
    emit('deleted')
  } catch (error) { showError(error) } finally { saving.value = false }
}
onMounted(() => {
  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    viewportQuery = window.matchMedia('(max-width: 600px)')
    updateViewport(viewportQuery)
    viewportQuery.addEventListener('change', updateViewport)
  }
  load()
})
onBeforeUnmount(() => {
  ++loadId
  viewportQuery?.removeEventListener('change', updateViewport)
})
</script>

<style scoped>
.config-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.config-hint { margin: 12px 0; color: var(--text-secondary); line-height: 1.5; }
.config-table-wrap { width: 100%; min-width: 0; overflow-x: auto; }
.config-table :deep(.el-input-number), .config-table :deep(.el-select), .config-table :deep(.el-input) { width: 100%; max-width: 100%; }
.field-key-cell { display: flex; flex-direction: column; align-items: stretch; gap: 4px; }
.field-key-cell :deep(.el-button) { align-self: flex-start; }
.config-footer { margin-top: 16px; display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; }
.config-footer :deep(.el-button + .el-button) { margin-left: 0; }
</style>
