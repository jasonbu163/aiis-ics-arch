<!-- 设备观察配置分类、筛选、列表和表单。 -->
<template>
  <div class="page-layout config-page">
    <BaseCard :title="tr('management')" compact>
      <el-radio-group :model-value="active" class="card-action-segmented" :aria-label="tr('management')" @change="selectTab">
        <el-radio-button v-for="item in tabs" :key="item" :value="item">{{ tr(item + 'Config') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <BaseCard :title="tr(active + 'Config')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" :disabled="saving || loading || failed" @click="open(active)">{{ tr('add') }}</ActionButton>
          <el-tooltip :content="tr('resetWidths')" placement="top">
            <ActionButton @click="columnsByTab[active].reset()">{{ tr('resetWidthsButton') }}</ActionButton>
          </el-tooltip>
        </div>
      </template>
      <el-form class="config-toolbar" label-position="top" @submit.prevent="search">
        <el-form-item v-if="active === 'group' || active === 'card'" :label="tr(active === 'group' ? 'category' : 'page')">
          <el-select v-model="draft.scope" clearable :placeholder="tr('allConfigs')">
            <el-option v-for="page in pages" :key="page.value" :value="page.value" :label="t(page.label)" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="active === 'slot'" :label="tr('target')">
          <el-select v-model="draft.target" clearable :placeholder="tr('allConfigs')">
            <el-option value="latest" :label="tr('latest')" /><el-option value="history" :label="tr('historyTarget')" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="active === 'metric' || active === 'slot'" :label="tr('group')">
          <el-select v-model="draft.scope" clearable filterable :placeholder="tr('allConfigs')">
            <el-option v-for="group in groupRows" :key="group.groupKey" :value="group.groupKey" :label="group.groupKey" />
          </el-select>
        </el-form-item>
        <el-form-item class="config-toolbar__keyword" :label="tr('configKeyword')"><el-input v-model="draft.keyword" clearable /></el-form-item>
        <el-form-item class="config-toolbar__actions">
          <div class="table-actions">
            <ActionButton variant="primary" @click="search">{{ tr('search') }}</ActionButton>
            <ActionButton @click="resetFilters">{{ t('common.reset') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-alert v-if="failed" type="error" show-icon :closable="false" :title="tr('loadFailed')">
        <ActionButton v-if="active === 'source'" size="small" @click="load">{{ tr('retryLoad') }}</ActionButton>
      </el-alert>
      <div v-else class="config-table" v-loading="loading">
        <el-table v-if="active === 'group'" :key="'group:' + groupColumns.version.value" :data="visibleRows" :empty-text="emptyText" border @header-dragend="groupColumns.onHeaderDragEnd">
          <el-table-column prop="groupKey" :label="t('equipment.observation.key')" :width="groupColumns.widths.groupKey" :min-width="140" />
          <el-table-column prop="category" :label="t('equipment.observation.category')" :width="groupColumns.widths.category" :min-width="110" />
          <el-table-column prop="nameZh" :label="t('equipment.observation.nameZh')" :width="groupColumns.widths.nameZh" :min-width="140" />
          <el-table-column prop="nameEn" :label="t('equipment.observation.nameEn')" :width="groupColumns.widths.nameEn" :min-width="140" />
          <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="groupColumns.widths.enabled" :min-width="100" />
          <el-table-column :label="t('equipment.observation.actions')" width="120"><template #default="{ row }">
            <div class="row-actions"><ActionButton size="small" variant="row" @click="open('group', row)">{{ t('equipment.observation.edit') }}</ActionButton></div>
          </template></el-table-column>
        </el-table>
        <el-table v-else-if="active === 'metric'" :key="'metric:' + metricColumns.version.value" :data="visibleRows" :empty-text="emptyText" border @header-dragend="metricColumns.onHeaderDragEnd">
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
        <el-table v-else-if="active === 'slot'" :key="'slot:' + slotColumns.version.value" :data="visibleRows" :empty-text="emptyText" border @header-dragend="slotColumns.onHeaderDragEnd">
          <el-table-column prop="target" :label="tr('target')" :width="slotColumns.widths.target" :min-width="110">
            <template #default="{ row }">{{ tr(row.target === 'latest' ? 'latest' : 'historyTarget') }}</template>
          </el-table-column>
          <el-table-column prop="groupKey" :label="tr('group')" :width="slotColumns.widths.groupKey" :min-width="140" />
          <el-table-column prop="slotNo" :label="t('equipment.observation.slot')" :width="slotColumns.widths.slotNo" :min-width="80" />
          <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="slotColumns.widths.metricKey" :min-width="140" />
          <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="slotColumns.widths.enabled" :min-width="100">
            <template #default="{ row }"><el-switch :model-value="row.enabled" :disabled="saving" @change="toggleSlot(row, $event)" /></template>
          </el-table-column>
          <el-table-column prop="firstUsedAt" :label="tr('firstUsedAt')" :width="slotColumns.widths.firstUsedAt" :min-width="170">
            <template #default="{ row }">{{ formatShanghaiDateTime(row.firstUsedAt) || '—' }}</template>
          </el-table-column>
        </el-table>
        <el-table v-else-if="active === 'card'" :key="'card:' + cardColumns.version.value" :data="visibleRows" :empty-text="emptyText" border @header-dragend="cardColumns.onHeaderDragEnd">
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
        <el-table v-else-if="active === 'source'" :key="'source:' + sourceColumns.version.value" row-key="sourceKey"
          :data="visibleRows" :empty-text="emptyText" border @header-dragend="sourceColumns.onHeaderDragEnd">
          <el-table-column prop="sourceKey" :label="tr('sourceKey')" :width="sourceColumns.widths.sourceKey" :min-width="140" />
          <el-table-column prop="name" :label="tr('sourceName')" :width="sourceColumns.widths.name" :min-width="140">
            <template #default="{ row }">{{ row.name || '—' }}</template>
          </el-table-column>
          <el-table-column prop="enabled" :label="tr('sourceStatus')" :width="sourceColumns.widths.enabled" :min-width="110">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'">{{ tr(row.enabled ? 'sourceEnabled' : 'sourceDisabled') }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="tr('actions')" width="240" :resizable="false">
            <template #default="{ row }">
              <div class="row-actions">
                <ActionButton variant="row" :disabled="saving || loading" @click="open('source', row)">{{ tr('edit') }}</ActionButton>
                <ActionButton size="small" :disabled="saving || loading" @click="changeSource(row, false)">
                  {{ tr(row.enabled ? 'disableSource' : 'enableSource') }}
                </ActionButton>
                <ActionButton variant="danger" size="small" :disabled="saving || loading" @click="changeSource(row, true)">
                  {{ tr('deleteSource') }}
                </ActionButton>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </BaseCard>
    <el-dialog v-model="dialog" :title="t(editing ? 'equipment.observation.edit' : 'equipment.observation.add')"
      class="standard-form-dialog observation-config-dialog" width="min(680px, 94vw)" align-center
      :show-close="false" :close-on-click-modal="false">
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
          <el-option v-for="group in groupRows" :key="group.groupKey" :value="group.groupKey"
            :label="t('equipment.observation.metricOptionLabel', { name: locale.startsWith('en') ? group.nameEn : group.nameZh, key: group.groupKey })" />
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
        <el-form-item :label="t('equipment.observation.group')"><el-input v-model="form.groupKey" @update:model-value="form.metricKey = ''" /></el-form-item>
        <el-form-item :label="t('equipment.observation.slot')"><el-input-number v-model="form.slotNo" :min="1" :max="100" /></el-form-item>
        <el-form-item :label="t('equipment.observation.key')"><el-select v-model="form.metricKey" filterable><el-option v-for="metric in metricRows.filter(m => m.sourceGroupKey === form.groupKey)" :key="metric.metricKey" :value="metric.metricKey" :label="metricOptionLabel(metric)" /></el-select></el-form-item>
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
              <el-select v-model="item.metricKey" filterable><el-option v-for="metric in metricRows" :key="metric.metricKey" :value="metric.metricKey" :label="metricOptionLabel(metric)" /></el-select>
              <el-switch v-model="item.enabled" />
              <ActionButton size="small" @click="form.items.splice(index, 1)">{{ t('equipment.observation.remove') }}</ActionButton>
            </div>
            <ActionButton size="small" @click="form.items.push({ metricKey: '', enabled: true })">{{ t('equipment.observation.addItem') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-form v-else-if="mode === 'source'" label-position="top" @submit.prevent="save">
        <el-form-item :label="tr('sourceKey')">
          <el-input v-model="form.sourceKey" :disabled="editing || saving" maxlength="64" />
          <small v-if="!editing">{{ tr('sourceKeyHint') }}</small>
        </el-form-item>
        <el-form-item :label="tr('sourceName')"><el-input v-model="form.name" :disabled="saving" maxlength="128" /></el-form-item>
        <el-form-item :label="tr('sourceStatus')"><el-switch v-model="form.enabled" :disabled="saving" /></el-form-item>
        <el-alert v-if="editing && !form.enabled" :title="tr('disableSourceHint')" type="warning" :closable="false" />
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" :disabled="(mode === 'slot' && (!form.target || !form.groupKey || !form.metricKey)) ||
            (mode === 'source' && !sourceKeyPattern.test(form.sourceKey))" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { metrics, createMetric, updateMetric, metricGroups, createMetricGroup, updateMetricGroup,
  bindings, createBinding, updateBinding, cards, createCard, updateCard,
  writeSources, createWriteSource, updateWriteSource, deleteWriteSource } from '../../api/observations'

const { t, locale } = useI18n()
const tr = key => t(`equipment.observation.${key}`)
const groupColumns = useTableColumnWidths('observation.groups', {
  groupKey: { width: 180, minWidth: 140 }, category: { width: 130, minWidth: 110 },
  nameZh: { width: 180, minWidth: 140 }, nameEn: { width: 180, minWidth: 140 }, enabled: { width: 110, minWidth: 100 }
})
const metricColumns = useTableColumnWidths('observation.metrics', {
  metricKey: { width: 180, minWidth: 140 }, sourceGroupKey: { width: 140, minWidth: 110 },
  nameZh: { width: 180, minWidth: 140 }, valueType: { width: 110, minWidth: 90 }, unit: { width: 90, minWidth: 80 }
})
const slotColumns = useTableColumnWidths('observation.slots', {
  target: { width: 120, minWidth: 110 }, groupKey: { width: 180, minWidth: 140 },
  slotNo: { width: 90, minWidth: 80 }, metricKey: { width: 180, minWidth: 140 },
  enabled: { width: 110, minWidth: 100 }, firstUsedAt: { width: 190, minWidth: 170 }
})
const cardColumns = useTableColumnWidths('observation.cards', {
  cardKey: { width: 170, minWidth: 130 }, pageKey: { width: 130, minWidth: 100 },
  titleZh: { width: 190, minWidth: 150 }, enabled: { width: 110, minWidth: 100 }
})
const sourceColumns = useTableColumnWidths('observation.writeSources', {
  sourceKey: { width: 190, minWidth: 140 }, name: { width: 190, minWidth: 140 }, enabled: { width: 145, minWidth: 110 }
})
const tabs = ['group', 'metric', 'slot', 'card', 'source']
const columnsByTab = { group: groupColumns, metric: metricColumns, slot: slotColumns, card: cardColumns, source: sourceColumns }
const sourceKeyPattern = /^[A-Za-z0-9_.-]{1,64}$/
const active = ref('group')
const groupRows = ref([])
const metricRows = ref([])
const slotRows = ref([])
const cardRows = ref([])
const sourceRows = ref([])
const blankFilters = () => ({ scope: '', target: '', keyword: '' })
const draft = reactive(blankFilters())
const submitted = reactive(Object.fromEntries(tabs.map(tab => [tab, blankFilters()])))
const loading = ref(false)
const failed = ref(false)
let requestId = 0
let mounted = true
const dialog = ref(false)
const saving = ref(false)
const editing = ref(false)
const mode = ref('')
const form = reactive({})
const pages = [
  { value: 'production', label: 'equipment.productionParameters' }, { value: 'cleaning', label: 'equipment.observation.cleaning' },
  { value: 'temperature', label: 'equipment.temperature' }, { value: 'drive', label: 'equipment.drive' }
]
const rowsByTab = { group: groupRows, metric: metricRows, slot: slotRows, card: cardRows, source: sourceRows }
const metricByKey = computed(() => new Map(metricRows.value.map(row => [row.metricKey, row])))
function metricOptionLabel(metric) {
  return t('equipment.observation.metricOptionLabel', {
    name: locale.value.startsWith('en') ? metric.nameEn : metric.nameZh,
    key: metric.metricKey
  })
}
const visibleRows = computed(() => {
  const { scope, keyword } = submitted[active.value]
  const needle = keyword.toLowerCase()
  return rowsByTab[active.value].value.filter(row => {
    switch (active.value) {
      case 'group': return (!scope || row.category === scope) && matches(needle, row.groupKey, row.nameZh, row.nameEn)
      case 'metric': return (!scope || row.sourceGroupKey === scope) && matches(needle, row.metricKey, row.nameZh, row.nameEn)
      case 'card': return (!scope || row.pageKey === scope) && matches(needle, row.cardKey, row.titleZh, row.titleEn)
      case 'source': return matches(needle, row.sourceKey, row.name)
      case 'slot': {
        const metric = metricByKey.value.get(row.metricKey)
        return matches(needle, row.metricKey, metric?.nameZh, metric?.nameEn)
      }
    }
  })
})
const emptyText = computed(() => loading.value ? t('common.loading') : tr(
  Object.values(submitted[active.value]).some(Boolean) ? 'noMatchingConfigs' : 'noConfigs'
))
function matches(needle, ...values) { return !needle || values.some(value => value?.toLowerCase().includes(needle)) }
function selectTab(tab) {
  if (active.value === tab) return
  dialog.value = false
  active.value = tab
  Object.assign(draft, submitted[tab])
  load()
}
function search() {
  dialog.value = false
  submitted[active.value] = { ...draft, keyword: draft.keyword.trim() }
  load()
}
function resetFilters() { Object.assign(draft, blankFilters()); search() }
function assign(data) { for (const key of Object.keys(form)) delete form[key]; Object.assign(form, data) }
function open(kind, row) {
  if (saving.value || loading.value || failed.value) return
  mode.value = kind
  editing.value = !!row
  if (row) assign(JSON.parse(JSON.stringify(row)))
  else if (kind === 'group') assign({ groupKey: '', category: 'production', nameZh: '', nameEn: '', enabled: true, sortOrder: 0 })
  else if (kind === 'metric') assign({ metricKey: '', sourceGroupKey: '', category: '', nameZh: '', nameEn: '', valueType: 'number', unit: '', decimals: null })
  else if (kind === 'slot') assign({ target: submitted.slot.target, groupKey: submitted.slot.scope, slotNo: 1, metricKey: '', enabled: true })
  else if (kind === 'source') assign({ sourceKey: '', name: '', enabled: true })
  else assign({ cardKey: '', pageKey: 'production', titleZh: '', titleEn: '', enabled: true, sortOrder: 0, items: [] })
  dialog.value = true
}
function selectMetricGroup(key) { form.category = groupRows.value.find(group => group.groupKey === key)?.category || '' }
async function load() {
  const id = ++requestId
  const tab = active.value
  const { scope, target } = submitted.slot
  loading.value = true
  failed.value = false
  try {
    if (tab === 'source') {
      const sources = await writeSources()
      if (id === requestId) sourceRows.value = sources
      return
    }
    const [groups, definitions, cardConfigs, slots] = await Promise.all([
      metricGroups(), metrics(), tab === 'card' ? cards() : null,
      tab === 'slot' ? bindings({ target: target || undefined, groupKey: scope || undefined }) : null
    ])
    if (id !== requestId) return
    groupRows.value = groups
    metricRows.value = definitions
    if (cardConfigs) cardRows.value = cardConfigs
    if (slots) slotRows.value = slots.items
  } catch {
    if (id === requestId) failed.value = true
  } finally {
    if (id === requestId) loading.value = false
  }
}
async function toggleSlot(row, enabled) {
  if (saving.value || loading.value || failed.value || !visibleRows.value.includes(row)) return
  saving.value = true
  try {
    await updateBinding(row.target, row.groupKey, row.slotNo, { enabled })
    if (mounted && active.value === 'slot') await load()
  } finally { saving.value = false }
}
function sourceError(error) {
  const conflict = error.response?.status === 409
  ElMessage.error(tr(conflict ? 'sourceConflict' : 'sourceSaveFailed'))
}
async function changeSource(row, remove) {
  if (active.value !== 'source' || saving.value || loading.value || failed.value || !visibleRows.value.includes(row)) return
  const key = row.sourceKey
  const enabled = !row.enabled
  saving.value = true
  try {
    if (remove || !enabled) {
      const action = remove ? 'deleteSource' : 'disableSource'
      try {
        await ElMessageBox.confirm(tr(action + 'Hint'), `${tr(action)} · ${key}`, {
          confirmButtonText: tr(action), cancelButtonText: tr('cancel'), type: 'warning'
        })
      } catch { return }
    }
    if (!mounted || active.value !== 'source' || !visibleRows.value.includes(row)) return
    if (remove) await deleteWriteSource(key)
    else await updateWriteSource(key, { enabled })
    if (mounted && active.value === 'source') await load()
  } catch (error) { sourceError(error) }
  finally { saving.value = false }
}
async function save() {
  if (!dialog.value || saving.value || (mode.value === 'source' && !sourceKeyPattern.test(form.sourceKey))) return
  const tab = active.value
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
    } else if (mode.value === 'source') {
      const { sourceKey, name, enabled } = form
      const payload = { name: name || null, enabled }
      if (editing.value) await updateWriteSource(sourceKey, payload)
      else await createWriteSource({ sourceKey, ...payload })
    } else {
      const payload = JSON.parse(JSON.stringify(form))
      if (editing.value) { delete payload.cardKey; await updateCard(form.cardKey, payload) }
      else await createCard(payload)
    }
    dialog.value = false
    if (mounted && active.value === tab) await load()
  } catch (error) {
    if (tab === 'source') sourceError(error)
    else throw error
  } finally { saving.value = false }
}
onMounted(load)
onBeforeUnmount(() => { mounted = false; requestId++; dialog.value = false })
</script>

<style scoped>
.config-page { display: flex; flex-direction: column; gap: var(--space-lg); min-width: 0; container: observation-config / inline-size; }
.config-page > :deep(.base-card) { height: auto; min-width: 0; }
.config-page :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
.config-page :deep(.card-action-segmented.el-radio-group) { flex-wrap: wrap; height: auto; }
.config-toolbar {
  --config-card-inset: var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 4px 16px;
  margin: 0 calc(-1 * var(--config-card-inset)) 16px;
  padding-inline: var(--config-card-inset);
  border-bottom: 1px solid var(--border-secondary);
}
.config-toolbar :deep(.el-form-item) { flex: 0 1 180px; min-width: 0; }
.config-toolbar :deep(.config-toolbar__keyword) { flex: 1 1 180px; }
.config-toolbar :deep(.config-toolbar__actions) { flex: 0 1 auto; margin-inline-start: auto; max-width: 100%; }
@media (max-width: 768px) {
  .config-toolbar { --config-card-inset: 18px; }
}
@container observation-config (max-width: 300px) {
  .config-toolbar { --config-card-inset: 8px; }
}
.config-toolbar :deep(.el-input), .config-toolbar :deep(.el-select) { width: 100%; }
.config-table { min-width: 0; min-height: 60px; }
.item-list { display: grid; gap: 8px; width: 100%; }
.item-row { display: flex; align-items: center; gap: 10px; }
.item-row .el-select { flex: 1; }

@container observation-config (max-width: 300px) {
  .config-page :deep(.base-card__header), .config-page :deep(.base-card__body) { padding-inline: 8px; }
  .config-page :deep(.base-card__title) { white-space: normal; overflow-wrap: anywhere; }
  .config-page :deep(.base-card__actions) { flex: 1 1 100%; min-width: 0; justify-content: flex-start; }
  .config-page :deep(.table-actions) { max-width: 100%; min-width: 0; justify-content: flex-start; }
  .config-page :deep(.table-actions .action-button) { min-width: 0; max-width: 100%; white-space: normal; overflow-wrap: anywhere; }
  .config-page :deep(.card-action-segmented.el-radio-group) { max-width: 100%; }
  .config-page :deep(.card-action-segmented .el-radio-button),
  .config-page :deep(.card-action-segmented .el-radio-button__inner) { min-width: 0; max-width: 100%; }
  .config-page :deep(.card-action-segmented .el-radio-button__inner) {
    height: auto; min-height: 26px; white-space: normal; overflow-wrap: anywhere;
  }
}
@media (max-width: 768px) {
  /* 展开侧栏时，为绝对定位的多行顶栏预留空间。 */
  @container observation-config (max-width: 300px) {
    .config-page > :deep(.base-card:first-child) { margin-block-start: 56px; }
  }
  @container observation-config (max-width: 250px) {
    .config-page > :deep(.base-card:first-child) { margin-block-start: 108px; }
  }
  @container observation-config (max-width: 200px) {
    .config-page > :deep(.base-card:first-child) { margin-block-start: 160px; }
  }
}
</style>
