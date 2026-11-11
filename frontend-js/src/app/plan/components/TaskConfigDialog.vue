<!-- 两个业务入口共同维护共享定义及当前模块本地定义。 -->
<template>
  <el-dialog v-model="open" :title="tr('fieldSettings')" width="92%" class="standard-form-dialog" @open="load">
    <p>{{ tr('configVersion') }}: {{ config?.fieldConfigVersion }} / {{ tr('revision') }}: {{ config?.configRevision }}</p>
    <div class="table-scroll">
      <el-table :data="rows" border stripe class="vibe-table">
        <el-table-column :label="tr('scope')" width="160">
          <template #default="{ row }">
            <el-select v-model="row.scope" :disabled="!row._new">
              <el-option :label="tr('shared')" value="shared_sync" />
              <el-option :label="tr('local')" :value="`${kind}_local`" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column :label="tr('slot')" width="95"><template #default="{ row }"><el-input-number v-model="row.slotNo" :min="1" :max="100" :disabled="!row._new" controls-position="right" /></template></el-table-column>
        <el-table-column :label="tr('fieldName')" min-width="150"><template #default="{ row }"><el-input v-model="row.name" :disabled="!row._new" /></template></el-table-column>
        <el-table-column :label="tr('type')" width="125"><template #default="{ row }"><el-select v-model="row.type" :disabled="!row._new"><el-option v-for="type in types" :key="type" :value="type" :label="tr(`types.${type}`)" /></el-select></template></el-table-column>
        <el-table-column :label="tr('labelZh')" min-width="150"><template #default="{ row }"><el-input v-model="row.labels['zh-CN']" /></template></el-table-column>
        <el-table-column :label="tr('labelEn')" min-width="150"><template #default="{ row }"><el-input v-model="row.labels['en-US']" /></template></el-table-column>
        <el-table-column :label="tr('unit')" width="110"><template #default="{ row }"><el-input v-model="row.unit" :disabled="!row._new" /></template></el-table-column>
        <el-table-column :label="tr('owner')" width="170"><template #default="{ row }"><el-select v-model="row.performanceOwner" :disabled="row.scope === 'plan_local'" clearable><el-option v-for="owner in owners" :key="owner" :value="owner" :label="tr(`owners.${owner}`)" /></el-select></template></el-table-column>
        <el-table-column v-for="name in boolNames" :key="name" :label="tr(name)" width="105"><template #default="{ row }"><el-checkbox v-model="row[name]" /></template></el-table-column>
        <el-table-column :label="tr('columnOrder')" width="130"><template #default="{ row }"><el-input-number v-model="row[orderName]" :min="0" :max="65535" controls-position="right" /></template></el-table-column>
      </el-table>
    </div>
    <template #footer>
      <el-button @click="addRow">{{ tr('addField') }}</el-button>
      <el-button @click="open = false">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="save">{{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
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
const user = useUserStore()
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
  try { localStorage.setItem(draftKey, JSON.stringify({ version: config.value.fieldConfigVersion, revision: config.value.configRevision, rows: value })) } catch { /* 本机偏好不可用不影响业务。 */ }
}, { deep: true })
onMounted(() => { if (user.isAdmin && readDraft()) open.value = true })
</script>
