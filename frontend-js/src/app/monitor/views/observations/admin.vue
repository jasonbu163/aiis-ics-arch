<!-- 过程监控曲线配置、筛选与表单。 -->
<template>
  <div class="page-layout config-page">
    <BaseCard :title="t('monitor.observation.management')" compact>
      <el-radio-group model-value="curves" class="card-action-segmented"
        :aria-label="t('monitor.observation.management')">
        <el-radio-button value="curves">{{ tr('curveConfig') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <BaseCard :title="tr('curveConfig')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" :disabled="saving || loading || failed" @click="open()">{{ tr('add') }}</ActionButton>
          <el-tooltip :content="tr('resetWidths')" placement="top">
            <ActionButton @click="columns.reset">{{ tr('resetWidthsButton') }}</ActionButton>
          </el-tooltip>
        </div>
      </template>
      <el-form class="config-toolbar" label-position="top" @submit.prevent="search">
        <el-form-item :label="tr('category')">
          <el-select v-model="draft.category" clearable :placeholder="tr('allConfigs')">
            <el-option v-for="(label, category) in categories" :key="category" :value="category" :label="t(label)" />
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
      <el-alert v-if="failed" type="error" show-icon :closable="false" :title="tr('loadFailed')" />
      <div v-else class="config-table" v-loading="loading">
        <el-table :key="columns.version.value" :data="visibleRows" :empty-text="emptyText" border @header-dragend="columns.onHeaderDragEnd">
        <el-table-column prop="curveGroupKey" :label="t('equipment.observation.key')" :width="columns.widths.curveGroupKey" :min-width="140" />
        <el-table-column prop="category" :label="t('equipment.observation.category')" :width="columns.widths.category" :min-width="110">
            <template #default="{ row }">{{ t(categories[row.category]) }}</template>
          </el-table-column>
        <el-table-column prop="titleZh" :label="t(locale.startsWith('en') ? 'equipment.observation.titleEn' : 'equipment.observation.titleZh')" :width="columns.widths.titleZh" :min-width="160">
          <template #default="{ row }">{{ locale.startsWith('en') ? row.titleEn : row.titleZh }}</template>
        </el-table-column>
        <el-table-column prop="series" :label="tr('items')" :width="columns.widths.series" :min-width="160">
            <template #default="{ row }">{{ row.series.map(metricLabel).join(' / ') || '—' }}</template>
          </el-table-column>
          <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="columns.widths.enabled" :min-width="100" />
        <el-table-column :label="t('equipment.observation.actions')" width="120">
          <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open(row)">{{ t('equipment.observation.edit') }}</ActionButton></div></template>
        </el-table-column>
        </el-table>
      </div>
    </BaseCard>
    <el-dialog v-model="dialog" :title="t(editing ? 'equipment.observation.edit' : 'equipment.observation.add')"
      class="standard-form-dialog compact-form-dialog" width="min(680px, 94vw)" align-center
      :show-close="false" :close-on-click-modal="true" :before-close="beforeClose">
      <el-form label-position="top" class="dialog-form-grid">
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.curveGroupKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.category')">
          <el-select v-model="form.category">
            <el-option value="temperature" :label="t('equipment.temperature')" />
            <el-option value="drive" :label="t('equipment.drive')" />
            <el-option value="cleaning" :label="t('equipment.observation.cleaning')" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('equipment.observation.titleZh')"><el-input v-model="form.titleZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.titleEn')"><el-input v-model="form.titleEn" /></el-form-item>
        <el-form-item :label="t('equipment.observation.sortOrder')"><el-input-number v-model="form.sortOrder" /></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item :label="t('equipment.observation.items')">
          <div class="item-list">
            <div v-for="(item, index) in form.series" :key="index" class="item-row">
              <el-select v-model="item.metricKey" filterable>
                <el-option v-for="metric in available" :key="metric.metricKey" :value="metric.metricKey"
                  :label="t('equipment.observation.metricOptionLabel', { name: locale.startsWith('en') ? metric.nameEn : metric.nameZh, key: metric.metricKey })" />
              </el-select>
              <el-select v-model="item.lineStyle" class="series-line-style" :aria-label="t('monitor.observation.lineStyle')">
                <el-option value="solid" :label="t('monitor.observation.lineSolid')" />
                <el-option value="dashed" :label="t('monitor.observation.lineDashed')" />
              </el-select>
              <el-switch v-model="item.enabled" />
              <ActionButton size="small" @click="form.series.splice(index, 1)">{{ t('equipment.observation.remove') }}</ActionButton>
            </div>
            <ActionButton size="small" @click="form.series.push({ metricKey: '', enabled: true, lineStyle: 'solid' })">{{ t('equipment.observation.addItem') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { metrics } from '@/app/equipment/api/observations'
import { curves, createCurve, updateCurve } from '../../api/observations'

const { t, locale } = useI18n()
const tr = key => t(`equipment.observation.${key}`)
const categories = { temperature: 'equipment.temperature', drive: 'equipment.drive', cleaning: 'equipment.observation.cleaning' }
const columns = useTableColumnWidths('observation.curves', {
  curveGroupKey: { width: 180, minWidth: 140 }, category: { width: 130, minWidth: 110 },
  titleZh: { width: 220, minWidth: 160 }, series: { width: 210, minWidth: 160 }, enabled: { width: 120, minWidth: 100 }
})
const draft = reactive({ category: '', keyword: '' })
const submitted = ref({ ...draft })
const loading = ref(false)
const failed = ref(false)
let generation = 0
const rows = ref([])
const metricRows = ref([])
const dialog = ref(false)
const editing = ref(false)
const saving = ref(false)
const form = reactive({})
const available = computed(() => metricRows.value.filter(metric => metric.category === form.category && metric.valueType === 'number'))
const metricsByKey = computed(() => new Map(metricRows.value.map(metric => [metric.metricKey, metric])))
function metricLabel(item) {
  const metric = metricsByKey.value.get(item.metricKey)
  return (locale.value.startsWith('en') ? metric?.nameEn : metric?.nameZh) || item.metricKey
}
const visibleRows = computed(() => {
  const keyword = submitted.value.keyword.toLowerCase()
  return rows.value.filter(row => !keyword || [row.curveGroupKey, row.titleZh, row.titleEn]
    .some(value => value?.toLowerCase().includes(keyword)))
})
const emptyText = computed(() => loading.value ? t('common.loading') :
  tr(Object.values(submitted.value).some(Boolean) ? 'noMatchingConfigs' : 'noConfigs'))
function search() {
  dialog.value = false
  submitted.value = { ...draft, keyword: draft.keyword.trim() }
  load()
}
function resetFilters() { Object.assign(draft, { category: '', keyword: '' }); search() }
function open(row) {
  if (saving.value || loading.value || failed.value) return
  editing.value = !!row
  for (const key of Object.keys(form)) delete form[key]
  Object.assign(form, row ? JSON.parse(JSON.stringify(row)) : {
    curveGroupKey: '', category: submitted.value.category || 'temperature', titleZh: '', titleEn: '', enabled: true, sortOrder: 0, series: []
  })
  form.series = form.series.map(item => ({ lineStyle: 'solid', ...item }))
  dialog.value = true
}
async function load() {
  const id = ++generation
  loading.value = true
  failed.value = false
  try {
    const [curveRows, definitions] = await Promise.all([curves({ category: submitted.value.category || undefined }), metrics()])
    if (id !== generation) return
    rows.value = curveRows
    metricRows.value = definitions
  } catch {
    if (id === generation) failed.value = true
  } finally {
    if (id === generation) loading.value = false
  }
}
function beforeClose(done) { if (!saving.value) done() }
async function save() {
  if (!dialog.value || saving.value) return
  saving.value = true
  try {
    const payload = JSON.parse(JSON.stringify(form))
    if (editing.value) { delete payload.curveGroupKey; await updateCurve(form.curveGroupKey, payload) }
    else await createCurve(payload)
    dialog.value = false
    await load()
  } finally { saving.value = false }
}
onMounted(load)
onBeforeUnmount(() => { generation++; dialog.value = false })
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
.item-row .el-select { flex: 1; min-width: 110px; }
.item-row .series-line-style { flex: 0 1 110px; }
.item-row { flex-wrap: wrap; }

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
