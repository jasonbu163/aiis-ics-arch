<!-- 按质量字段配置展示、详情查看、人工新增和编辑任务质量结果。 -->
<template>
  <BaseCard class="quality-results-card">
    <template #title>
      <h3 class="card-title">{{ label('title') }}</h3>
      <el-tooltip placement="bottom-start" :trigger="['hover', 'focus']" :trigger-keys="[]">
        <template #content><div class="help-content">{{ label('timeZone') }}</div></template>
        <button class="help-trigger" type="button" :aria-label="label('timeZone')"
          @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
          <el-icon><QuestionFilled /></el-icon>
        </button>
      </el-tooltip>
    </template>
    <template #actions>
      <div class="table-actions">
        <ActionButton v-if="canWrite" variant="primary" :disabled="loading || !!listError" @click="openCreate">
          {{ label('create') }}
        </ActionButton>
        <el-tooltip :content="label('resetWidthsHint')" placement="top" :trigger="['hover', 'focus']">
          <ActionButton @click="columns.reset">{{ label('resetWidths') }}</ActionButton>
        </el-tooltip>
        <ActionButton :loading="loading" @click="load">{{ label('refresh') }}</ActionButton>
      </div>
    </template>
    <div class="filter-section">
      <el-form label-position="top" class="filter-form" @submit.prevent="search">
        <div class="filter-keywords">
          <el-form-item :label="label('taskNo')"><el-input v-model="filters.taskNo" clearable /></el-form-item>
          <el-form-item :label="label('targetKey')"><el-input v-model="filters.targetKey" clearable /></el-form-item>
        </div>
        <div class="filter-conditions">
          <el-form-item :label="label('createdFrom')">
            <el-date-picker v-model="filters.createdFrom" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" />
          </el-form-item>
          <el-form-item :label="label('createdTo')">
            <el-date-picker v-model="filters.createdTo" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" />
          </el-form-item>
          <div class="filter-actions">
            <ActionButton variant="primary" native-type="submit">{{ $t('common.search') }}</ActionButton>
            <ActionButton @click="resetFilters">{{ $t('common.reset') }}</ActionButton>
          </div>
        </div>
      </el-form>
    </div>
    <div class="table-scroll">
      <el-alert v-if="listError" type="error" :closable="false" :title="listError" role="alert" />
      <el-table
        v-else :key="columns.version" v-loading="loading" :data="rows" row-key="id" stripe border
        class="vibe-table" :empty-text="label('empty')" @header-dragend="columns.onHeaderDragEnd"
      >
        <el-table-column v-for="key in fixedKeys" :key="key" :prop="key" :label="label(key)"
          :width="columns.widths[key]" :min-width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ formatFixed(key, row[key]) }}</template>
        </el-table-column>
        <el-table-column v-for="field in visibleFields" :key="field.name" :prop="fieldKey(field)"
          :label="fieldLabel(field)" :width="columns.widths[fieldKey(field)]" :min-width="100" show-overflow-tooltip>
          <template #default="{ row }">
            <a v-if="field.type === 'link' && linkUrl(row.items[field.name])"
              :href="linkUrl(row.items[field.name])" target="_blank" rel="noopener noreferrer">
              {{ field.linkText || row.items[field.name] }}
            </a>
            <span v-else>{{ displayValue(field, row.items[field.name]) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="label('actions')" :width="canEdit ? 150 : 100" :resizable="false" fixed="right">
          <template #default="{ row }">
            <div class="row-actions">
              <ActionButton variant="row" @click="open(row.taskNo, false)">{{ label('details') }}</ActionButton>
              <ActionButton v-if="canEdit" variant="row" @click="open(row.taskNo, true)">{{ label('edit') }}</ActionButton>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pagination-scroll">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next" :total="total" @change="load" />
    </div>
  </BaseCard>

  <el-dialog v-model="dialogOpen" class="standard-form-dialog compact-form-dialog" width="min(760px, calc(100vw - 24px))" align-center
    :title="label(creating ? 'create' : editing ? 'edit' : 'details')" :close-on-click-modal="true"
    :close-on-press-escape="!saving" :before-close="beforeClose" :show-close="false" @closed="detailRequest++">
    <div v-loading="detailLoading" class="result-dialog-body">
      <el-alert v-if="detailError" type="error" :closable="false" :title="detailError" role="alert" />
      <ActionButton v-if="detailError && !record && !creating" @click="open(selectedTask, editing)">{{ label('refresh') }}</ActionButton>
      <el-form v-if="record || creating" id="quality-result-form" label-position="top"
        :disabled="saving" @submit.prevent="submit">
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ label('basicInfo') }}</h3>
          <div v-if="creating" class="dialog-form-grid">
            <el-form-item :label="label('taskNo')" required>
              <el-input v-model="identity.taskNo" maxlength="50" />
            </el-form-item>
            <el-form-item :label="label('targetKey')">
              <el-input v-model="identity.targetKey" maxlength="64" />
            </el-form-item>
          </div>
          <dl v-else class="dialog-form-grid">
            <div v-for="key in identityKeys" :key="key"><dt>{{ label(key) }}</dt><dd>{{ formatFixed(key, record[key]) }}</dd></div>
          </dl>
        </section>
        <section v-if="editing ? editableFields.length : fields.length" class="dialog-section">
          <h3 class="dialog-section__title">{{ label('resultFields') }}</h3>
          <div v-if="editing" class="dialog-form-grid">
            <el-form-item v-for="field in editableFields" :key="field.name" :label="fieldLabel(field)">
              <div class="result-input">
                <el-select v-if="field.type === 'boolean'" v-model="draft[field.name]" :empty-values="[]">
                  <el-option v-if="field.isNullable || (!creating && draft[field.name] === null)"
                    :value="null" :label="label('emptyValue')" />
                  <el-option :value="true" :label="label('yes')" />
                  <el-option :value="false" :label="label('no')" />
                </el-select>
                <el-input v-else :model-value="draft[field.name] ?? ''"
                  :type="field.type === 'link' ? 'url' : 'text'"
                  :inputmode="field.type === 'number' ? 'decimal' : undefined"
                  :maxlength="field.type === 'link' ? 2048 : field.type === 'string' ? 255 : undefined"
                  @update:model-value="draft[field.name] = $event" />
                <ActionButton v-if="field.isNullable && field.type !== 'boolean'" :disabled="saving" @click="draft[field.name] = null">
                  {{ label('clearValue') }}
                </ActionButton>
              </div>
            </el-form-item>
          </div>
          <dl v-else class="dialog-form-grid">
            <div v-for="field in fields" :key="field.name">
              <dt>{{ fieldLabel(field) }}</dt>
              <dd>
                <a v-if="field.type === 'link' && linkUrl(record.items[field.name])"
                  :href="linkUrl(record.items[field.name])" target="_blank" rel="noopener noreferrer">
                  {{ field.linkText || record.items[field.name] }}
                </a>
                <span v-else>{{ displayValue(field, record.items[field.name]) }}</span>
              </dd>
            </div>
          </dl>
        </section>
        <section v-if="record" class="dialog-section">
          <h3 class="dialog-section__title">{{ label('timeInfo') }}</h3>
          <dl class="dialog-form-grid">
            <div v-for="key in timeKeys" :key="key"><dt>{{ label(key) }}</dt><dd>{{ formatFixed(key, record[key]) }}</dd></div>
          </dl>
        </section>
      </el-form>
    </div>
    <template #footer>
      <div class="core-dialog-footer">
        <ActionButton :disabled="saving" @click="dialogOpen = false">{{ label(editing ? 'cancel' : 'close') }}</ActionButton>
        <ActionButton v-if="editing" variant="primary" native-type="submit" form="quality-result-form"
          :loading="saving" :disabled="detailLoading || (!record && !creating)">{{ label('save') }}</ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useUserStore } from '@/store/user'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { createQualityResult, getQualityResult, listQualityResults, saveQualityResult } from '../../api'

const { t, locale } = useI18n()
const label = key => t(`quality.results.${key}`)
const emptyFilters = () => ({ taskNo: '', targetKey: '', createdFrom: '', createdTo: '' })
const filters = reactive(emptyFilters())
let applied = emptyFilters()
const rows = ref([])
const fields = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const listError = ref('')
const identityKeys = ['taskNo', 'targetKey']
const timeKeys = ['createdAt', 'updatedAt']
const fixedKeys = [...identityKeys, ...timeKeys]
const fieldKey = field => `item.${field.name}`
const visibleFields = computed(() => fields.value.filter(field => field.visible))
const editableFields = computed(() => fields.value.filter(field => field.enabled !== false && field.editable))
const user = useUserStore()
const canWrite = computed(() => ['admin', 'supervisor', 'operator'].includes(user.role))
const canEdit = computed(() => canWrite.value && editableFields.value.length > 0)
const columns = shallowRef()
watch(() => visibleFields.value.map(fieldKey).join(','), () => {
  const layout = Object.fromEntries(fixedKeys.map(key => [key, { width: key.endsWith('At') ? 180 : 150, minWidth: 110 }]))
  for (const field of visibleFields.value) layout[fieldKey(field)] = { width: 155, minWidth: 100 }
  const bindings = useTableColumnWidths('quality.results', layout)
  columns.value = reactive(bindings)
}, { immediate: true })

let listRequest = 0
async function load() {
  const request = ++listRequest
  listError.value = ''
  loading.value = true
  try {
    const params = { ...Object.fromEntries(Object.entries(applied).filter(([, value]) => value)),
      page: page.value, pageSize: pageSize.value }
    const result = await listQualityResults(params)
    if (request !== listRequest) return
    if (page.value > 1 && page.value > result.totalPages) {
      page.value = Math.max(1, result.totalPages)
      return
    }
    rows.value = result.items
    total.value = result.total
    fields.value = result.fields
  } catch {
    if (request === listRequest) listError.value = label('loadError')
  } finally {
    if (request === listRequest) loading.value = false
  }
}

function search() {
  applied = { ...filters, taskNo: filters.taskNo.trim(), targetKey: filters.targetKey.trim() }
  if (page.value === 1) load()
  else page.value = 1
}

function resetFilters() {
  Object.assign(filters, emptyFilters())
  search()
}

function fieldLabel(field) {
  const name = field.labels[locale.value] || field.labels['en-US'] || field.name
  return field.unit ? `${name} (${field.unit})` : name
}

function formatFixed(key, value) {
  const isTimestamp = key === 'createdAt' || key === 'updatedAt'
  return isTimestamp && typeof value === 'string' && /^\d{4}-\d\d-\d\dT/.test(value)
    ? value.slice(0, 19).replace('T', ' ')
    : value ?? label('emptyValue')
}

function linkUrl(value) {
  if (typeof value !== 'string' || value.length > 2048 ||
    !/^https?:\/\//i.test(value) || /[\s\\\p{C}]/u.test(value)) return ''
  try {
    const url = new URL(value)
    const authority = value.slice(value.indexOf('://') + 3).split(/[/?#]/, 1)[0]
    if (authority && url.hostname && url.port !== '0' && !/[@%]/.test(authority)) return url.href
  } catch { /* 历史无效值保持不可点击。 */ }
  return ''
}

function displayValue(field, value) {
  if (value == null || field.type === 'link') return label('emptyValue')
  if (typeof value === 'boolean') return label(value ? 'yes' : 'no')
  return value
}

const dialogOpen = ref(false)
const editing = ref(false)
const creating = ref(false)
const detailLoading = ref(false)
const detailError = ref('')
const saving = ref(false)
const record = ref(null)
const selectedTask = ref('')
const identity = reactive({ taskNo: '', targetKey: '' })
const draft = ref({})
let detailRequest = 0
function openCreate() {
  ++detailRequest
  creating.value = true
  editing.value = true
  record.value = null
  detailLoading.value = false
  detailError.value = ''
  Object.assign(identity, { taskNo: '', targetKey: '' })
  draft.value = Object.create(null)
  dialogOpen.value = true
}

function beforeClose(done) {
  if (!saving.value) done()
}

async function open(taskNo, edit) {
  const request = ++detailRequest
  selectedTask.value = taskNo
  dialogOpen.value = true
  creating.value = false
  record.value = null
  detailError.value = ''
  editing.value = edit
  detailLoading.value = true
  try {
    const result = await getQualityResult(taskNo)
    if (request !== detailRequest) return
    record.value = result
    draft.value = { ...result.items }
  } catch {
    if (request === detailRequest) detailError.value = label('loadError')
  } finally {
    if (request === detailRequest) detailLoading.value = false
  }
}

async function submit() {
  if (!editing.value || !canWrite.value || saving.value || (!creating.value && !record.value)) return
  const create = creating.value
  const patch = []
  detailError.value = ''
  const taskNo = create ? identity.taskNo.trim() : record.value.taskNo
  const targetKey = identity.targetKey.trim()
  if (create && !/^[A-Za-z0-9._-]{1,50}$/.test(taskNo)) {
    detailError.value = label('invalidTaskNo')
    return
  }
  if (create && targetKey && !/^[A-Za-z0-9._-]{1,64}$/.test(targetKey)) {
    detailError.value = label('invalidTargetKey')
    return
  }
  for (const field of editableFields.value) {
    const key = field.name
    if (create && !Object.hasOwn(draft.value, key)) continue
    let value = draft.value[key] ?? null
    if (!create && value === (record.value.items[key] ?? null)) continue
    if (create && field.isNullable && value === '' && ['number', 'link'].includes(field.type)) value = null
    if (value != null && field.type === 'number') {
      if (!/^-?\d{1,10}(?:\.\d{1,4})?$/.test(String(value))) {
        detailError.value = label('invalidValue')
        return
      }
      value = Number(value)
    }
    if (value != null && field.type === 'link' && !linkUrl(value)) {
      detailError.value = label('invalidLink')
      return
    }
    if (create || value !== record.value.items[key]) patch.push([key, value])
  }
  if (!create && !patch.length) {
    dialogOpen.value = false
    return
  }
  saving.value = true
  try {
    const body = { taskNo, items: Object.fromEntries(patch) }
    if (create) {
      if (targetKey) body.targetKey = targetKey
      await createQualityResult(body)
    } else {
      await saveQualityResult(body)
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    const response = error?.response
    const code = response?.data?.errorCode
    const message = code === 'quality.task_no_conflict' ? 'taskNoConflict'
      : response?.status === 422 ? 'createInvalid'
      : response?.status === 401 ? 'createUnauthenticated'
      : response?.status === 403 ? 'createForbidden'
      : 'createUnknown'
    detailError.value = label(create ? message : 'saveError')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.quality-results-card { height: auto; --quality-inset: 24px; container-type: inline-size; }
.quality-results-card :deep(.base-card__body) { padding: 0; }
.quality-results-card :deep(.base-card__header) { padding-inline: var(--quality-inset); }
.filter-section { padding: 16px var(--quality-inset); border-bottom: 1px solid var(--border-secondary); }
.filter-form { display: flex; flex-wrap: wrap; align-items: end; gap: 12px; }
.filter-keywords, .filter-conditions { display: grid; align-items: end; min-width: 0; gap: 12px; }
.filter-keywords { grid-template-columns: repeat(2, minmax(0, 1fr)); flex: 1 1 240px; }
.filter-conditions { grid-template-columns: repeat(2, minmax(160px, 1fr)) max-content; flex: 2 1 500px; }
.filter-actions { display: flex; justify-content: flex-end; gap: 8px; }
.filter-form :deep(.el-form-item) { min-width: 0; margin: 0; }
.filter-form :deep(.el-date-editor) { width: 100%; }
.card-title { margin: 0; color: var(--text-primary); font-size: 16px; font-weight: 590; line-height: 1.35; overflow-wrap: anywhere; }
.help-trigger { display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 50%; background: transparent; color: var(--text-secondary); font-size: 16px; cursor: pointer; }
.help-trigger:hover { color: var(--primary); }
.help-trigger:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.help-content { max-width: min(340px, calc(100vw - 56px)); white-space: normal; overflow-wrap: anywhere; }
.table-scroll { padding: 20px var(--quality-inset) 0; overflow-x: auto; }
.pagination-scroll { padding: 18px var(--quality-inset) 24px; overflow-x: auto; }
.pagination-scroll :deep(.el-pagination) { justify-content: flex-end; width: max-content; min-width: 100%; }
.result-dialog-body { min-height: 60px; }
.result-input { display: flex; flex-wrap: wrap; gap: 8px; flex: 1; min-width: 0; }
.result-input :deep(.el-input) { flex: 1 1 120px; min-width: 0; }
a { color: var(--primary); text-decoration: underline; }
@container (max-width: 650px) {
  .filter-conditions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .filter-actions { grid-column: 1 / -1; }
  .quality-results-card :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
  .quality-results-card :deep(.table-actions) { flex-wrap: wrap; }
}
@media (max-width: 600px) {
  .quality-results-card { --quality-inset: 16px; }
}
</style>
