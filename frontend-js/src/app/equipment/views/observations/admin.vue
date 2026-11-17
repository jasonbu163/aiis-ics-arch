<!-- 指标、槽位、卡片配置与实时快照管理。 -->
<template>
  <div class="page-layout">
    <BaseCard :title="t('equipment.observation.management')">
      <el-tabs v-model="active">
        <el-tab-pane :label="t('equipment.observation.groupConfig')" name="groups">
          <div class="table-actions">
            <ActionButton variant="primary" @click="open('group')">{{ t('equipment.observation.add') }}</ActionButton>
            <ActionButton @click="groupColumns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
          </div>
          <el-table :key="groupColumns.version.value" :data="groupRows" border @header-dragend="groupColumns.onHeaderDragEnd">
            <el-table-column prop="groupKey" :label="t('equipment.observation.key')" :width="groupColumns.widths.groupKey" :min-width="140" />
            <el-table-column prop="category" :label="t('equipment.observation.category')" :width="groupColumns.widths.category" :min-width="110" />
            <el-table-column prop="nameZh" :label="t('equipment.observation.nameZh')" :width="groupColumns.widths.nameZh" :min-width="140" />
            <el-table-column prop="nameEn" :label="t('equipment.observation.nameEn')" :width="groupColumns.widths.nameEn" :min-width="140" />
            <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="groupColumns.widths.enabled" :min-width="100" />
            <el-table-column :label="t('equipment.observation.actions')" width="120"><template #default="{ row }">
              <div class="row-actions"><ActionButton size="small" variant="row" @click="open('group', row)">{{ t('equipment.observation.edit') }}</ActionButton></div>
            </template></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane :label="t('equipment.observation.metricConfig')" name="metrics">
          <div class="table-actions">
            <ActionButton variant="primary" @click="open('metric')">{{ t('equipment.observation.add') }}</ActionButton>
            <ActionButton @click="metricColumns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
          </div>
          <el-table :key="metricColumns.version.value" :data="metricRows" border @header-dragend="metricColumns.onHeaderDragEnd">
            <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="metricColumns.widths.metricKey" :min-width="140" />
            <el-table-column prop="sourceGroupKey" :label="t('equipment.observation.group')" :width="metricColumns.widths.sourceGroupKey" :min-width="110" />
            <el-table-column prop="nameZh" :label="t(locale.startsWith('en') ? 'equipment.observation.nameEn' : 'equipment.observation.nameZh')" :width="metricColumns.widths.nameZh" :min-width="140">
              <template #default="{ row }">{{ locale.startsWith('en') ? row.nameEn : row.nameZh }}</template>
            </el-table-column>
            <el-table-column prop="valueType" :label="t('equipment.observation.type')" :width="metricColumns.widths.valueType" :min-width="90" />
            <el-table-column prop="unit" :label="t('equipment.observation.unit')" :width="metricColumns.widths.unit" :min-width="80" />
            <el-table-column :label="t('equipment.observation.actions')" width="120">
              <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open('metric', row)">{{ t('equipment.observation.edit') }}</ActionButton></div></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane :label="t('equipment.observation.slotConfig')" name="slots">
          <div class="table-actions config-toolbar">
            <el-select v-model="slotTarget"><el-option value="latest" :label="t('equipment.observation.latest')" /><el-option value="history" :label="t('equipment.observation.historyTarget')" /></el-select>
            <el-input v-model="slotGroup" :placeholder="t('equipment.observation.group')" />
            <ActionButton @click="loadSlots">{{ t('equipment.observation.search') }}</ActionButton>
            <ActionButton variant="primary" @click="open('slot')">{{ t('equipment.observation.add') }}</ActionButton>
            <ActionButton @click="slotColumns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
          </div>
          <el-table :key="slotColumns.version.value" :data="slotRows" border @header-dragend="slotColumns.onHeaderDragEnd">
            <el-table-column prop="slotNo" :label="t('equipment.observation.slot')" :width="slotColumns.widths.slotNo" :min-width="80" />
            <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="slotColumns.widths.metricKey" :min-width="140" />
            <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="slotColumns.widths.enabled" :min-width="100">
              <template #default="{ row }"><el-switch :model-value="row.enabled" @change="toggleSlot(row, $event)" /></template>
            </el-table-column>
            <el-table-column prop="firstUsedAt" :label="t('equipment.observation.sampledAt')" :width="slotColumns.widths.firstUsedAt" :min-width="170" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane :label="t('equipment.observation.cardConfig')" name="cards">
          <div class="table-actions">
            <ActionButton variant="primary" @click="open('card')">{{ t('equipment.observation.add') }}</ActionButton>
            <ActionButton @click="cardColumns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
          </div>
          <el-table :key="cardColumns.version.value" :data="cardRows" border @header-dragend="cardColumns.onHeaderDragEnd">
            <el-table-column prop="cardKey" :label="t('equipment.observation.key')" :width="cardColumns.widths.cardKey" :min-width="130" />
            <el-table-column prop="pageKey" :label="t('equipment.observation.page')" :width="cardColumns.widths.pageKey" :min-width="100" />
            <el-table-column prop="titleZh" :label="t(locale.startsWith('en') ? 'equipment.observation.titleEn' : 'equipment.observation.titleZh')" :width="cardColumns.widths.titleZh" :min-width="150">
              <template #default="{ row }">{{ locale.startsWith('en') ? row.titleEn : row.titleZh }}</template>
            </el-table-column>
            <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="cardColumns.widths.enabled" :min-width="100" />
            <el-table-column :label="t('equipment.observation.actions')" width="120">
              <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open('card', row)">{{ t('equipment.observation.edit') }}</ActionButton></div></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </BaseCard>
    <el-dialog v-model="dialog" :title="t(editing ? 'equipment.observation.edit' : 'equipment.observation.add')"
      class="standard-form-dialog" width="min(680px, 94vw)">
      <el-form v-if="mode === 'group'" label-position="top">
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.groupKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.category')"><el-select v-model="form.category">
          <el-option v-for="page in pages" :key="page.value" :value="page.value" :label="t(page.label)" />
        </el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.nameZh')"><el-input v-model="form.nameZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.nameEn')"><el-input v-model="form.nameEn" /></el-form-item>
        <el-form-item :label="t('equipment.observation.sortOrder')"><el-input-number v-model="form.sortOrder" /></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <el-form v-else-if="mode === 'metric'" label-position="top">
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.metricKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.group')"><el-select v-model="form.sourceGroupKey" :disabled="editing" @change="selectMetricGroup">
          <el-option v-for="group in groupRows" :key="group.groupKey" :value="group.groupKey" :label="locale.startsWith('en') ? group.nameEn : group.nameZh" />
        </el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.category')"><el-input v-model="form.category" disabled /></el-form-item>
        <el-form-item :label="t('equipment.observation.nameZh')"><el-input v-model="form.nameZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.nameEn')"><el-input v-model="form.nameEn" /></el-form-item>
        <el-form-item :label="t('equipment.observation.type')">
          <el-select v-model="form.valueType"><el-option v-for="type in ['number','boolean','string']" :key="type" :value="type" :label="t(`equipment.observation.${type}`)" /></el-select>
        </el-form-item>
        <el-form-item :label="t('equipment.observation.unit')"><el-input v-model="form.unit" clearable /></el-form-item>
        <el-form-item :label="t('equipment.observation.decimals')"><el-input-number v-model="form.decimals" :min="0" :max="12" /></el-form-item>
      </el-form>
      <el-form v-else-if="mode === 'slot'" label-position="top">
        <el-form-item :label="t('equipment.observation.target')"><el-select v-model="form.target"><el-option value="latest" :label="t('equipment.observation.latest')" /><el-option value="history" :label="t('equipment.observation.historyTarget')" /></el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.group')"><el-input v-model="form.groupKey" /></el-form-item>
        <el-form-item :label="t('equipment.observation.slot')"><el-input-number v-model="form.slotNo" :min="1" :max="100" /></el-form-item>
        <el-form-item :label="t('equipment.observation.key')"><el-select v-model="form.metricKey" filterable><el-option v-for="metric in metricRows.filter(m => m.sourceGroupKey === form.groupKey)" :key="metric.metricKey" :value="metric.metricKey" :label="locale.startsWith('en') ? metric.nameEn : metric.nameZh" /></el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <el-form v-else-if="mode === 'card'" label-position="top">
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.cardKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.page')"><el-select v-model="form.pageKey"><el-option v-for="page in pages" :key="page.value" :value="page.value" :label="t(page.label)" /></el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.titleZh')"><el-input v-model="form.titleZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.titleEn')"><el-input v-model="form.titleEn" /></el-form-item>
        <el-form-item :label="t('equipment.observation.sortOrder')"><el-input-number v-model="form.sortOrder" /></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item :label="t('equipment.observation.items')">
          <div class="item-list">
            <div v-for="(item, index) in form.items" :key="index" class="item-row">
              <el-select v-model="item.metricKey" filterable><el-option v-for="metric in metricRows" :key="metric.metricKey" :value="metric.metricKey" :label="locale.startsWith('en') ? metric.nameEn : metric.nameZh" /></el-select>
              <el-switch v-model="item.enabled" />
              <ActionButton size="small" @click="form.items.splice(index, 1)">{{ t('equipment.observation.remove') }}</ActionButton>
            </div>
            <ActionButton size="small" @click="form.items.push({ metricKey: '', enabled: true })">{{ t('equipment.observation.addItem') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
        <ActionButton variant="primary" :loading="saving" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { metrics, createMetric, updateMetric, metricGroups, createMetricGroup, updateMetricGroup, bindings, createBinding, updateBinding, cards, createCard, updateCard } from '../../api/observations'

const { t, locale } = useI18n()
const groupColumns = useTableColumnWidths('observation.groups', {
  groupKey: { width: 180, minWidth: 140 }, category: { width: 130, minWidth: 110 },
  nameZh: { width: 180, minWidth: 140 }, nameEn: { width: 180, minWidth: 140 }, enabled: { width: 110, minWidth: 100 }
})
const metricColumns = useTableColumnWidths('observation.metrics', {
  metricKey: { width: 180, minWidth: 140 }, sourceGroupKey: { width: 140, minWidth: 110 },
  nameZh: { width: 180, minWidth: 140 }, valueType: { width: 110, minWidth: 90 }, unit: { width: 90, minWidth: 80 }
})
const slotColumns = useTableColumnWidths('observation.slots', {
  slotNo: { width: 90, minWidth: 80 }, metricKey: { width: 180, minWidth: 140 },
  enabled: { width: 110, minWidth: 100 }, firstUsedAt: { width: 190, minWidth: 170 }
})
const cardColumns = useTableColumnWidths('observation.cards', {
  cardKey: { width: 170, minWidth: 130 }, pageKey: { width: 130, minWidth: 100 },
  titleZh: { width: 190, minWidth: 150 }, enabled: { width: 110, minWidth: 100 }
})
const active = ref('groups')
const groupRows = ref([])
const metricRows = ref([])
const slotRows = ref([])
const cardRows = ref([])
const slotTarget = ref('latest')
const slotGroup = ref('temperature')
const dialog = ref(false)
const saving = ref(false)
const editing = ref(false)
const mode = ref('')
const form = reactive({})
const pages = [
  { value: 'production', label: 'equipment.productionParameters' }, { value: 'cleaning', label: 'equipment.observation.cleaning' },
  { value: 'temperature', label: 'equipment.temperature' }, { value: 'drive', label: 'equipment.drive' }
]
function assign(data) { for (const key of Object.keys(form)) delete form[key]; Object.assign(form, data) }
function open(kind, row) {
  mode.value = kind
  editing.value = !!row
  if (row) assign(JSON.parse(JSON.stringify(row)))
  else if (kind === 'group') assign({ groupKey: '', category: 'production', nameZh: '', nameEn: '', enabled: true, sortOrder: 0 })
  else if (kind === 'metric') assign({ metricKey: '', sourceGroupKey: '', category: '', nameZh: '', nameEn: '', valueType: 'number', unit: '', decimals: null })
  else if (kind === 'slot') assign({ target: slotTarget.value, groupKey: slotGroup.value, slotNo: 1, metricKey: '', enabled: true })
  else assign({ cardKey: '', pageKey: 'production', titleZh: '', titleEn: '', enabled: true, sortOrder: 0, items: [] })
  dialog.value = true
}
async function loadSlots() { if (slotGroup.value) slotRows.value = (await bindings({ target: slotTarget.value, groupKey: slotGroup.value })).items }
function selectMetricGroup(key) { form.category = groupRows.value.find(group => group.groupKey === key)?.category || '' }
async function load() { [groupRows.value, metricRows.value, cardRows.value] = await Promise.all([metricGroups(), metrics(), cards()]); await loadSlots() }
async function toggleSlot(row, enabled) { await updateBinding(row.target, row.groupKey, row.slotNo, { enabled }); await loadSlots() }
async function save() {
  saving.value = true
  try {
    if (mode.value === 'group') {
      const payload = { ...form }
      if (editing.value) { delete payload.groupKey; await updateMetricGroup(form.groupKey, payload) }
      else await createMetricGroup(payload)
    } else if (mode.value === 'metric') {
      const payload = { ...form, unit: form.unit || null }
      if (editing.value) {
        delete payload.metricKey; delete payload.sourceGroupKey; delete payload.category
        await updateMetric(form.metricKey, payload)
      } else await createMetric(payload)
    } else if (mode.value === 'slot') {
      await createBinding({ ...form })
      slotTarget.value = form.target; slotGroup.value = form.groupKey
    } else {
      const payload = JSON.parse(JSON.stringify(form))
      if (editing.value) { delete payload.cardKey; await updateCard(form.cardKey, payload) }
      else await createCard(payload)
    }
    dialog.value = false
    await load()
  } finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
.config-toolbar { display: flex; flex-wrap: wrap; gap: 10px; }
.config-toolbar .el-select, .config-toolbar .el-input { width: 180px; }
.item-list { display: grid; gap: 8px; width: 100%; }
.item-row { display: flex; align-items: center; gap: 10px; }
.item-row .el-select { flex: 1; }
</style>
