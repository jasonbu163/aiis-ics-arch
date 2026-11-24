<!-- 管理员维护质量模块的本地字段，不修改报告值。 -->
<template>
  <div class="page-layout">
    <BaseCard :title="label('title')" class="quality-field-card">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" :disabled="!config || loading || config.definitions.length >= 100" @click="open('new')">
            {{ label('add') }}
          </ActionButton>
          <el-tooltip :content="label('resetWidthsHint')" placement="top" :trigger="['hover', 'focus']">
            <ActionButton @click="columns.reset">{{ label('resetWidths') }}</ActionButton>
          </el-tooltip>
          <ActionButton :loading="loading" @click="load">{{ label('refresh') }}</ActionButton>
        </div>
      </template>
      <div class="filter-section">
        <el-form label-position="top" class="filter-form" @submit.prevent="search">
          <el-form-item :label="label('keyword')"><el-input v-model="keywords" clearable /></el-form-item>
          <el-form-item :label="label('enabled')">
            <el-select v-model="enabled" clearable>
              <el-option value="yes" :label="label('on')" />
              <el-option value="no" :label="label('off')" />
            </el-select>
          </el-form-item>
          <div class="filter-actions">
            <ActionButton variant="primary" native-type="submit">{{ $t('common.search') }}</ActionButton>
            <ActionButton @click="resetFilters">{{ $t('common.reset') }}</ActionButton>
          </div>
        </el-form>
      </div>
      <div class="table-scroll">
        <el-alert v-if="loadError" type="error" :title="loadError" :closable="false" role="alert" />
        <el-table v-else :key="columns.version.value" v-loading="loading" :data="visibleRows" row-key="name"
          stripe border class="vibe-table" :empty-text="label('empty')" @header-dragend="columns.onHeaderDragEnd">
          <el-table-column v-for="key in fieldColumns" :key="key" :prop="key" :label="label(key)"
            :width="columns.widths[key]" :min-width="90" show-overflow-tooltip>
            <template #default="{ row }">{{ columnValue(row, key) }}</template>
          </el-table-column>
          <el-table-column :label="label('actions')" width="150" :resizable="false" fixed="right">
            <template #default="{ row }">
              <div class="row-actions">
                <ActionButton variant="row" @click="open('view', row)">{{ label('view') }}</ActionButton>
                <ActionButton variant="row" @click="open('edit', row)">{{ label('edit') }}</ActionButton>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pagination-scroll">
        <el-pagination v-model:current-page="page" layout="total, prev, pager, next"
          :page-size="20" :total="filtered.length" />
      </div>
    </BaseCard>

    <el-dialog v-model="dialog" class="standard-form-dialog compact-form-dialog" width="min(720px, calc(100vw - 24px))" align-center
      :title="label(mode === 'new' ? 'add' : mode)" :show-close="false"
      :close-on-press-escape="!saving" :close-on-click-modal="false">
      <el-alert v-if="saveError" class="field-feedback" type="error" :title="saveError" :closable="false" role="alert" />
      <div v-if="conflicted" class="field-feedback">
        <ActionButton :loading="loading" @click="reloadForConflict">{{ label('reloadConflict') }}</ActionButton>
      </div>
      <div v-if="review" class="field-feedback">
        <p>{{ label('reviewConflict') }}</p>
        <pre>{{ review }}</pre>
      </div>
      <el-form v-if="draft" id="quality-local-field-form" label-position="top" @submit.prevent="submit">
        <QualityFieldForm v-model="draft" :is-new="mode === 'new'" :readonly="mode === 'view'" :disabled="saving" />
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialog = false">{{ label(mode === 'view' ? 'close' : 'cancel') }}</ActionButton>
          <ActionButton v-if="mode !== 'view'" variant="primary" native-type="submit" form="quality-local-field-form"
            :disabled="conflicted || loading" :loading="saving">{{ label('save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { getQualityFieldConfig, saveQualityFieldConfig } from '../../api'
import QualityFieldForm from '../../components/QualityFieldForm.vue'

const { t } = useI18n()
const label = key => t(`quality.localFields.${key}`)
const config = ref(null)
const loading = ref(false)
const loadError = ref('')
const dialog = ref(false)
const mode = ref('new')
const draft = ref(null)
const saving = ref(false)
const saveError = ref('')
const conflicted = ref(false)
const review = ref('')
const keywords = ref('')
const enabled = ref('')
const activeKeywords = ref('')
const activeEnabled = ref('')
const page = ref(1)
const fieldColumns = ['name', 'labelZh', 'labelEn', 'type', 'unit', 'linkText', 'enabled', 'visible', 'editable', 'order']
const columns = useTableColumnWidths('quality.local-fields', Object.fromEntries(fieldColumns.map(key => [key, {
  width: ['name', 'labelZh', 'labelEn', 'linkText'].includes(key) ? 155 : 104, minWidth: 90
}])))
const filtered = computed(() => (config.value?.definitions ?? []).filter(field =>
  (!activeKeywords.value || [field.name, ...Object.values(field.labels)].some(value => value.toLowerCase().includes(activeKeywords.value))) &&
  (!activeEnabled.value || field.enabled === (activeEnabled.value === 'yes'))
))
const visibleRows = computed(() => filtered.value.slice((page.value - 1) * 20, page.value * 20))
watch(filtered, rows => { page.value = Math.min(page.value, Math.max(1, Math.ceil(rows.length / 20))) })

function columnValue(field, key) {
  if (key === 'labelZh' || key === 'labelEn') return field.labels[key === 'labelZh' ? 'zh-CN' : 'en-US']
  if (key === 'type') return label(field.type)
  if (key === 'enabled') return label(field.enabled ? 'on' : 'off')
  if (typeof field[key] === 'boolean') return label(field[key] ? 'yes' : 'no')
  return field[key] ?? label('emptyValue')
}

function search() {
  activeKeywords.value = keywords.value.trim().toLowerCase()
  activeEnabled.value = enabled.value
  page.value = 1
}

function resetFilters() {
  keywords.value = ''
  enabled.value = ''
  search()
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    config.value = await getQualityFieldConfig()
    return true
  } catch {
    loadError.value = label('loadError')
    return false
  } finally {
    loading.value = false
  }
}

function open(action, field) {
  mode.value = action
  draft.value = field ? { ...field, labels: { ...field.labels } } : {
    name: '', labels: { 'zh-CN': '', 'en-US': '' }, type: 'string', unit: null,
    linkText: null, enabled: true, visible: true, editable: false, isNullable: true, order: 0
  }
  saveError.value = ''
  conflicted.value = false
  review.value = ''
  dialog.value = true
}

async function reloadForConflict() {
  if (!await load()) return
  const current = config.value.definitions.find(field => field.name === draft.value.name)
  review.value = current ? JSON.stringify(current, null, 2) : label('emptyValue')
  saveError.value = ''
  conflicted.value = false
}

async function submit() {
  if (mode.value === 'view' || conflicted.value || saving.value || loading.value || !draft.value) return
  saveError.value = ''
  const row = { ...draft.value, labels: { ...draft.value.labels } }
  row.name = row.name.trim()
  if (!/^[a-z][A-Za-z0-9_]{0,63}$/.test(row.name) || Object.values(row.labels).some(value => !value.trim())) {
    saveError.value = label('invalidDefinition')
    return
  }
  row.unit = row.unit?.trim() || null
  row.linkText = row.type === 'link' ? row.linkText?.trim() || null : null
  const definitions = config.value.definitions.slice()
  const index = definitions.findIndex(field => field.name === row.name)
  if (mode.value === 'new' && index >= 0) {
    saveError.value = label('duplicate')
    return
  }
  if (index < 0) definitions.push(row)
  else definitions[index] = row
  saving.value = true
  try {
    config.value = await saveQualityFieldConfig({ revision: config.value.revision, definitions })
    dialog.value = false
  } catch (error) {
    const code = error.response?.data?.errorCode
    conflicted.value = ['quality.config_revision_conflict', 'quality.commit_unknown'].includes(code) || !error.response
    saveError.value = label(conflicted.value ? 'conflict' : 'saveError')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.quality-field-card { height: auto; --quality-inset: 24px; container-type: inline-size; }
.quality-field-card :deep(.base-card__body) { padding: 0; }
.quality-field-card :deep(.base-card__header) { padding-inline: var(--quality-inset); }
.filter-section { padding: 16px var(--quality-inset); border-bottom: 1px solid var(--border-secondary); }
.filter-form { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr) auto; gap: 12px; align-items: end; }
.filter-form :deep(.el-select) { width: 100%; min-width: 0; }
.filter-actions { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; }
.filter-form :deep(.el-form-item) { min-width: 0; margin: 0; }
.table-scroll { padding: 20px var(--quality-inset) 0; overflow-x: auto; }
.pagination-scroll { padding: 18px var(--quality-inset) 24px; overflow-x: auto; }
.pagination-scroll :deep(.el-pagination) { justify-content: flex-end; width: max-content; min-width: 100%; }
.field-feedback { margin-bottom: 12px; }
.field-feedback pre { max-height: 180px; overflow: auto; white-space: pre-wrap; }
@container (max-width: 680px) {
  .filter-form { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .filter-form > :first-child, .filter-actions { grid-column: 1 / -1; }
}
@container (max-width: 550px) {
  .quality-field-card :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
  .quality-field-card :deep(.table-actions) { flex-wrap: wrap; }
}
@container (max-width: 400px) {
  .filter-form { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 600px) {
  .quality-field-card { --quality-inset: 16px; }
}
</style>
