<!-- 能耗曲线配置工作区，含筛选、列宽及四组字段的编辑弹窗。 -->
<template>
  <BaseCard :title="tr('title')">
    <template #actions>
      <div class="table-actions">
        <ActionButton variant="primary" :disabled="loading || !!loadError || saving || !meters.length" @click="open()">
          {{ obs('add') }}
        </ActionButton>
        <el-tooltip :content="obs('resetWidths')" placement="top">
          <ActionButton @click="columns.reset()">{{ obs('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <el-form class="curve-filters" label-position="top" @submit.prevent="search">
      <el-form-item :label="obs('meter')">
        <el-select v-model="draft.meterId" clearable filterable :placeholder="obs('allConfigs')">
          <el-option v-for="meter in meters" :key="meter.meterId" :value="meter.meterId" :label="name(meter)" />
        </el-select>
      </el-form-item>
      <el-form-item class="curve-filters__keyword" :label="obs('configKeyword')"><el-input v-model="draft.keyword" clearable /></el-form-item>
      <el-form-item class="curve-filters__actions">
        <div class="table-actions">
          <ActionButton variant="primary" native-type="submit">{{ obs('search') }}</ActionButton>
          <ActionButton @click="resetFilters">{{ t('common.reset') }}</ActionButton>
        </div>
      </el-form-item>
    </el-form>
    <el-alert v-if="loadError" :title="obs('loadFailed')" type="error" :closable="false" show-icon>
      <ActionButton size="small" @click="load">{{ obs('retry') }}</ActionButton>
    </el-alert>
    <el-table v-else :key="columns.version.value" v-loading="loading" :data="visibleRows"
      :empty-text="emptyText" row-key="curveGroupKey" border @header-dragend="resizeColumn">
      <el-table-column prop="curveGroupKey" :label="tr('key')" :min-width="columns.widths.curveGroupKey" />
      <el-table-column prop="titleZh" :label="tr('groupTitle')" :min-width="columns.widths.titleZh">
        <template #default="{ row }">{{ curveTitle(row, locale) }}</template>
      </el-table-column>
      <el-table-column prop="meterId" :label="obs('meter')" :min-width="columns.widths.meterId">
        <template #default="{ row }">{{ meterLabel(row.meterId) }}</template>
      </el-table-column>
      <el-table-column prop="groupKey" :label="obs('group')" :min-width="columns.widths.groupKey" />
      <el-table-column prop="series" :label="tr('series')" :min-width="columns.widths.series">
        <template #default="{ row }">
          <div v-for="item in row.series" :key="item.metricKey">
            {{ metricLabel(row, item.metricKey) }} · {{ tr(item.lineStyle) }}
            <template v-if="!item.enabled"> · {{ tr('inactive') }}</template>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="sortOrder" :label="tr('sortOrder')" :min-width="columns.widths.sortOrder" />
      <el-table-column prop="enabled" :label="tr('status')" :min-width="columns.widths.enabled">
        <template #default="{ row }">{{ tr(row.enabled ? 'active' : 'inactive') }}</template>
      </el-table-column>
      <el-table-column :label="obs('actions')" width="100" :resizable="false">
        <template #default="{ row }">
          <div class="row-actions">
            <ActionButton variant="row" size="small" :disabled="loading || saving" @click="open(row)">{{ obs('edit') }}</ActionButton>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="tr(original ? 'editTitle' : 'addTitle')"
      class="standard-form-dialog compact-form-dialog" width="min(720px, calc(100vw - 32px))" align-center
      :show-close="false" :close-on-click-modal="true" :before-close="beforeClose">
      <el-form label-position="top" :disabled="saving" @submit.prevent="save">
        <el-alert v-if="formIssue" class="curve-form-issue" :title="tr(formIssue)" type="error" :closable="false" show-icon />
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('basic') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="tr('key')"><el-input v-model="form.curveGroupKey" maxlength="64" :disabled="!!original" /></el-form-item>
            <el-form-item :label="tr('titleZh')"><el-input v-model="form.titleZh" maxlength="128" /></el-form-item>
            <el-form-item :label="tr('titleEn')"><el-input v-model="form.titleEn" maxlength="128" /></el-form-item>
          </div>
        </section>
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('dataRange') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="obs('meter')">
              <el-select v-model="form.meterId" filterable @change="changeMeter">
                <el-option v-for="meter in meters" :key="meter.meterId" :value="meter.meterId" :label="name(meter)" />
              </el-select>
            </el-form-item>
            <el-form-item :label="obs('group')">
              <el-select v-model="form.groupKey" filterable @change="form.series = []">
                <el-option v-for="group in formGroups" :key="group" :value="group" :label="group" />
              </el-select>
            </el-form-item>
          </div>
        </section>
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('series') }}</h3>
          <el-alert v-if="original && originalIssue" :title="tr('repairConfig')"
            type="warning" show-icon :closable="false" class="curve-form-issue" />
          <div class="series-editor">
            <div v-for="(item, index) in form.series" :key="index" class="series-row">
              <el-select v-model="item.metricKey" filterable :placeholder="obs('selectMetric')" :aria-label="obs('metric')">
                <el-option v-for="metric in formMetrics" :key="metric.metricKey" :value="metric.metricKey"
                  :label="obs('metricOptionLabel', { name: name(metric), key: metric.metricKey })" />
              </el-select>
              <el-select v-model="item.lineStyle" class="series-style" :aria-label="tr('lineStyle')">
                <el-option value="solid" :label="tr('solid')" />
                <el-option value="dashed" :label="tr('dashed')" />
              </el-select>
              <el-switch v-model="item.enabled" :aria-label="tr('seriesEnabled')" />
              <div class="table-actions">
                <ActionButton size="small" :disabled="index === 0" @click="moveSeries(index, -1)">{{ tr('up') }}</ActionButton>
                <ActionButton size="small" :disabled="index === form.series.length - 1" @click="moveSeries(index, 1)">{{ tr('down') }}</ActionButton>
                <ActionButton size="small" @click="form.series.splice(index, 1)">{{ tr('remove') }}</ActionButton>
              </div>
            </div>
            <div>
              <ActionButton size="small" :disabled="!formMetrics.length"
                @click="form.series.push({ metricKey: '', enabled: true, lineStyle: 'solid' })">{{ tr('addSeries') }}</ActionButton>
            </div>
          </div>
        </section>
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('display') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="tr('sortOrder')">
              <el-input-number v-model="form.sortOrder" :min="Number.MIN_SAFE_INTEGER" :max="Number.MAX_SAFE_INTEGER" :precision="0" />
            </el-form-item>
            <el-form-item :label="obs('enabled')"><el-switch v-model="form.enabled" /></el-form-item>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialog = false">{{ obs('cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" @click="save">{{ obs('save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </BaseCard>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { createEnergyCurveGroup, energyConfigs, energyCurveGroups, energyMeters, updateEnergyCurveGroup } from '../api/observations'
import { curveIssue, curveTitle } from './energyCurveGroups'

const { t, locale } = useI18n()
const tr = key => t(`energy.curves.${key}`)
const obs = (key, params) => t(`energy.observation.${key}`, params || {})
const name = item => (locale.value.startsWith('en') ? item.nameEn || item.nameZh : item.nameZh || item.nameEn) || item.meterId
const columns = useTableColumnWidths('energy.curve-groups', {
  curveGroupKey: { width: 165, minWidth: 120 }, titleZh: { width: 160, minWidth: 110 },
  meterId: { width: 150, minWidth: 100 }, groupKey: { width: 135, minWidth: 100 },
  series: { width: 230, minWidth: 130 }, sortOrder: { width: 90, minWidth: 72 }, enabled: { width: 100, minWidth: 80 }
})
const draft = reactive({ meterId: '', keyword: '' })
const submitted = ref({ ...draft })
const rows = ref([]), meters = ref([]), definitions = ref([])
const loading = ref(true), loadError = ref(false), saving = ref(false), dialog = ref(false)
const form = reactive({}), original = ref(null), formIssue = ref('')
const meterLabel = id => name(meters.value.find(meter => meter.meterId === id) || { meterId: id })
const availableFor = (meter, group) => definitions.value.filter(item => item.meterId === meter && item.groupKey === group)
const formMetrics = computed(() => availableFor(form.meterId, form.groupKey).filter(item => item.valueType === 'number'))
const formGroups = computed(() => [...new Set(definitions.value.filter(item => item.meterId === form.meterId).map(item => item.groupKey))])
const originalIssue = computed(() => curveIssue(original.value.series, availableFor(original.value.meterId, original.value.groupKey)))
const visibleRows = computed(() => {
  const keyword = submitted.value.keyword
  return rows.value.filter(row => !keyword || [row.curveGroupKey, row.titleZh, row.titleEn, row.groupKey,
    meterLabel(row.meterId), ...row.series.flatMap(item => [item.metricKey, metricLabel(row, item.metricKey)])]
    .some(value => value.toLowerCase().includes(keyword)))
})
const emptyText = computed(() => loading.value ? t('common.loading') : !meters.value.length ? obs('noMeters') :
  obs(submitted.value.meterId || submitted.value.keyword ? 'noMatchingConfigs' : 'noConfigs'))
let generation = 0
let alive = true

function resizeColumn(newWidth, oldWidth, column) {
  // 保留弹性列的拖动增量，切换工作区后仍按相同规则分配剩余空间。
  columns.onHeaderDragEnd(columns.widths[column.property] + newWidth - oldWidth, oldWidth, column)
  column.width = undefined
}
function metricLabel(row, key) {
  const metric = availableFor(row.meterId, row.groupKey).find(item => item.metricKey === key)
  return metric ? obs('metricOptionLabel', { name: name(metric), key }) : key
}
async function load() {
  const request = ++generation
  loading.value = true
  loadError.value = false
  try {
    const [configs, catalog, metrics] = await Promise.all([
      energyCurveGroups({ meterId: submitted.value.meterId || undefined }), energyMeters(), energyConfigs()
    ])
    if (request !== generation) return
    rows.value = configs
    meters.value = catalog.filter(meter => meter.readRoles.includes('admin'))
    definitions.value = metrics
  } catch {
    if (request === generation) loadError.value = true
  } finally {
    if (request === generation) loading.value = false
  }
}
function search() {
  submitted.value = { meterId: draft.meterId, keyword: draft.keyword.trim().toLowerCase() }
  return load()
}
function resetFilters() {
  Object.assign(draft, { meterId: '', keyword: '' })
  return search()
}
function open(row) {
  original.value = row || null
  formIssue.value = ''
  const meter = submitted.value.meterId || meters.value[0]?.meterId || ''
  Object.assign(form, row ? { ...row, series: row.series.map(item => ({ ...item })) } : {
    curveGroupKey: '', titleZh: '', titleEn: '', meterId: meter, groupKey: '', sortOrder: 0, enabled: true, series: []
  })
  if (!row) changeMeter()
  dialog.value = true
}
function changeMeter() {
  form.groupKey = formGroups.value[0] || ''
  form.series = []
}
function moveSeries(index, offset) {
  const [item] = form.series.splice(index, 1)
  form.series.splice(index + offset, 0, item)
}
function beforeClose(done) {
  if (!saving.value) done()
}
async function save() {
  if (saving.value || !dialog.value) return
  formIssue.value = !form.curveGroupKey || !form.meterId || !form.groupKey || !Number.isSafeInteger(form.sortOrder) ? 'invalidFields' :
    !form.titleZh.trim() && !form.titleEn.trim() ? 'missingTitle' : curveIssue(form.series, formMetrics.value)
  if (formIssue.value) return
  const { curveGroupKey, ...payload } = form
  saving.value = true
  try {
    if (original.value) {
      const changes = Object.fromEntries(Object.entries(payload).filter(([key, value]) =>
        JSON.stringify(original.value[key]) !== JSON.stringify(value)))
      if (Object.keys(changes).length) await updateEnergyCurveGroup(curveGroupKey, changes)
    } else {
      await createEnergyCurveGroup({ curveGroupKey, ...payload })
    }
    if (alive) {
      dialog.value = false
      await load()
    }
  } catch (error) {
    if (!alive) return
    const reason = error.response?.data?.errorCode
    if (reason === 'equipment_observation.configuration_conflict') formIssue.value = 'conflict'
    else if (reason === 'equipment_observation.curve_units') formIssue.value = 'mixedUnits'
    else if (reason === 'equipment_observation.curve_items') formIssue.value = 'invalidMetrics'
    else if (reason === 'equipment_observation.invalid_request') formIssue.value = 'invalidFields'
    else formIssue.value = 'saveFailed'
  } finally {
    saving.value = false
  }
}
onMounted(load)
onBeforeUnmount(() => { alive = false; generation++ })
</script>

<style scoped>
.curve-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 4px var(--space-md);
  margin: 0 calc(-1 * var(--space-lg)) var(--space-md);
  padding-inline: var(--space-lg);
  border-bottom: 1px solid var(--border-secondary);
}
.curve-filters :deep(.el-form-item) { flex: 0 1 180px; min-width: 0; }
.curve-filters :deep(.curve-filters__keyword) { flex: 1 1 180px; }
.curve-filters :deep(.curve-filters__actions) { flex: 0 1 auto; margin-inline-start: auto; }
.curve-filters :deep(.el-input), .curve-filters :deep(.el-select) { width: 100%; }
.curve-form-issue { margin-block-end: var(--space-sm); }
.series-editor { display: grid; gap: var(--space-sm); }
.series-row { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-sm); }
.series-row .el-select { flex: 1 1 155px; min-width: 0; }
.series-row .series-style { flex: 0 1 105px; }
.series-row .table-actions { flex-wrap: wrap; }
</style>
