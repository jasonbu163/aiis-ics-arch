<!-- CU 私有列表范例：筛选、分页和增改使用内存样例，列宽作为独立本机偏好。 -->
<template>
  <ConsoleCard class="workbench-samples" :title="label('listTitle')" :help="label('listHelp')" :help-label="label('listHelpLabel')" :help-append-to="overlayTarget" :header-statuses="headerStatuses" :status-overflow-label="label('moreStatuses')">
    <template #actions>
      <ConsoleActionButton :label="label('add')" :icon="Plus" tone="primary" :disabled="state === 'loading'" @click="openEditor('create')" />
      <ConsoleActionButton :label="label('resetWidths')" :title="label('resetWidthsHelp')" @click="resetWidths" />
    </template>
    <template #refresh>
      <ConsoleActionButton :label="t('workbench.refresh')" :icon="Refresh" :loading="refreshing" @click="refreshList" />
    </template>
    <template #tools>
      <form class="workbench-list-filters" @submit.prevent="applyFilters">
        <ElInput v-model="filterDraft.name" :aria-label="label('name')" :placeholder="label('searchName')" clearable />
        <ElSelect v-model="filterDraft.kind" :aria-label="label('kind')" :placeholder="label('allKinds')" :append-to="overlayTarget">
          <ElOption value="" :label="label('allKinds')" />
          <ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="label(kind)" />
        </ElSelect>
        <ConsoleActionButton native-type="submit" :label="label('search')" tone="primary" />
        <ConsoleActionButton :label="label('resetFilters')" @click="resetFilters" />
      </form>
    </template>

    <div v-if="state === 'normal'" class="workbench-sample-table">
      <ElTable :key="tableVersion" class="aw-data-table" :aria-label="label('listTitle')" :data="pageRows" row-key="id" border stripe @header-dragend="resize">
        <ElTableColumn prop="name" :label="label('name')" :min-width="columnMinimums.name" :width="widths.name" />
        <ElTableColumn prop="kind" :label="label('kind')" :min-width="columnMinimums.kind" :width="widths.kind" />
        <ElTableColumn :label="label('actions')" :width="144" :resizable="false" align="center">
          <template #default="{ row }">
            <div class="console-row-actions">
              <ConsoleActionButton variant="row" tone="primary" :label="label('edit')" @click="openEditor('edit', row.id)" />
              <ConsoleActionButton variant="row" :label="label('details')" @click="openEditor('details', row.id)" />
            </div>
          </template>
        </ElTableColumn>
      </ElTable>
    </div>
    <div v-else class="aw-page-state workbench-list-state" :aria-busy="state === 'loading'">
      <template v-if="state === 'loading'">
        <ElIcon class="is-loading" :size="24"><Loading /></ElIcon>
        <p>{{ label('loadingNote') }}</p>
      </template>
      <ElEmpty v-else-if="state === 'empty'" :image-size="64" :description="label(scenario === 'empty' ? 'emptyNote' : 'noMatches')" />
      <template v-else>
        <p role="alert">{{ label('errorNote') }}</p>
        <ConsoleActionButton :label="label('retry')" tone="primary" @click="refreshList" />
      </template>
    </div>
    <p v-if="feedback" class="workbench-list-feedback" role="status">{{ label(feedback) }}</p>
    <template v-if="state === 'normal'" #footer>
      <ElPagination v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="pageSizes" :total="filteredRows.length" :pager-count="5" :append-size-to="overlayTarget" :aria-label="label('pagination')" layout="total, sizes, ->, prev, pager, next" @size-change="page = 1" />
    </template>
  </ConsoleCard>

  <ElDialog v-model="dialogOpen" :title="label(dialogMode === 'create' ? 'addTitle' : dialogMode === 'edit' ? 'dialogTitle' : 'details')" :append-to="overlayTarget" width="min(480px, calc(100vw - 24px))" :close-on-click-modal="false" destroy-on-close>
    <dl v-if="dialogMode === 'details'" class="workbench-list-details">
      <dt>{{ label('name') }}</dt><dd>{{ draft.name }}</dd>
      <dt>{{ label('kind') }}</dt><dd>{{ label(draft.kind) }}</dd>
    </dl>
    <ElForm v-else ref="editRef" :id="formId" class="aw-sample-form" :model="draft" :rules="rules" label-position="top" @submit.prevent="save">
      <ElFormItem prop="name" :label="label('name')"><ElInput v-model="draft.name" :placeholder="label('nameHint')" /></ElFormItem>
      <ElFormItem prop="kind" :label="label('kind')">
        <ElSelect v-model="draft.kind" :append-to="overlayTarget">
          <ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="label(kind)" />
        </ElSelect>
      </ElFormItem>
    </ElForm>
    <template #footer>
      <div class="aw-form-actions">
        <ConsoleActionButton :label="label(dialogMode === 'details' ? 'close' : 'cancel')" @click="dialogOpen = false" />
        <ConsoleActionButton v-if="dialogMode !== 'details'" :label="label('save')" tone="primary" native-type="submit" :form="formId" :loading="saving" />
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onDeactivated, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loading, Plus, Refresh } from '@element-plus/icons-vue'
import { ElDialog, ElEmpty, ElForm, ElFormItem, ElIcon, ElInput, ElOption, ElPagination, ElSelect, ElTable, ElTableColumn, type FormInstance, type FormRules } from 'element-plus'
import { ConsoleActionButton, ConsoleCard, useTableColumnWidths, type CardHeaderStatus } from '../ui'

const props = defineProps<{ scenario: 'normal' | 'loading' | 'empty' | 'error'; tableId: string }>()
const emit = defineEmits<{ recover: [] }>()
const { t, locale } = useI18n()
const label = (key: string) => t(`workbench.pageSamples.${key}`)
const overlayTarget = '#cu-page-sample-overlays'
const formId = `cu-list-form-${props.tableId}`
const columnMinimums = { name: 170, kind: 125 }
const { widths, tableVersion, resize, reset: resetWidths } = useTableColumnWidths('cu', props.tableId, columnMinimums)
const kinds = ['standard', 'compact'] as const
type Kind = typeof kinds[number]
type SampleRow = { id: number; name?: string; kind: Kind }
type DialogMode = 'create' | 'edit' | 'details'

// 样例数据只在工作台内存更新；初始名称随语言切换。
const rows = ref<SampleRow[]>(Array.from({ length: 12 }, (_, index) => ({
  id: index + 1, kind: index % 3 === 1 ? 'compact' : 'standard'
})))
let nextId = rows.value.length + 1
const rowName = (row: SampleRow) => row.name ?? label(`seed.${row.id - 1}`)
const filterDraft = reactive<{ name: string; kind: Kind | '' }>({ name: '', kind: '' })
const filters = ref({ ...filterDraft })
const page = ref(1)
const pageSizes = [5, 10]
const pageSize = ref(pageSizes[0])
const filteredRows = computed(() => rows.value.filter(row =>
  (!filters.value.kind || row.kind === filters.value.kind) &&
  rowName(row).toLocaleLowerCase(locale.value).includes(filters.value.name.toLocaleLowerCase(locale.value))
))
const pageRows = computed(() => filteredRows.value
  .slice((page.value - 1) * pageSize.value, page.value * pageSize.value)
  .map(row => ({ id: row.id, name: rowName(row), kind: label(row.kind) })))
const refreshing = ref(false)
const state = computed(() => {
  if (refreshing.value) return 'loading'
  if (props.scenario === 'normal' && filteredRows.value.length === 0) return 'empty'
  return props.scenario
})
const headerStatuses = computed<CardHeaderStatus[]>(() => [
  { id: 'list-state', label: label(state.value), tone: state.value === 'normal' ? 'success' : state.value === 'error' ? 'danger' : 'neutral' },
  { id: 'source', label: label('localSample') },
  { id: 'edit-lifetime', label: label('sessionEdits') }
])
const feedback = ref('')
const dialogOpen = ref(false)
const dialogMode = ref<DialogMode>('create')
const saving = ref(false)
const draft = reactive<{ name: string; kind: Kind }>({ name: '', kind: 'standard' })
const editRef = ref<FormInstance>()
let editingId: number | undefined
let refreshTimer: ReturnType<typeof setTimeout> | undefined

const rules = computed<FormRules>(() => ({
  name: [
    { required: true, whitespace: true, message: label('required'), trigger: 'blur' },
    { min: 2, max: 24, transform: (value: string) => value.trim(), message: label('length'), trigger: 'blur' }
  ],
  kind: [{ required: true, message: label('kindRequired'), trigger: 'change' }]
}))

watch(locale, () => {
  page.value = 1
  editRef.value?.clearValidate()
})
watch(() => filteredRows.value.length, total => {
  page.value = Math.min(page.value, Math.max(1, Math.ceil(total / pageSize.value)))
})
watch(() => props.scenario, stopRefresh)
onDeactivated(() => {
  stopRefresh()
  dialogOpen.value = false
})
onBeforeUnmount(stopRefresh)

function applyFilters() {
  filters.value = { ...filterDraft, name: filterDraft.name.trim() }
  page.value = 1
  feedback.value = ''
}
function resetFilters() {
  Object.assign(filterDraft, { name: '', kind: '' })
  applyFilters()
}
function stopRefresh() {
  clearTimeout(refreshTimer)
  refreshing.value = false
}
function refreshList() {
  if (refreshing.value) return
  feedback.value = ''
  refreshing.value = true
  refreshTimer = setTimeout(() => {
    refreshing.value = false
    if (props.scenario !== 'normal') emit('recover')
    feedback.value = 'refreshed'
  }, 450)
}
function openEditor(mode: DialogMode, id?: number) {
  const row = id === undefined ? undefined : rows.value.find(item => item.id === id)
  dialogMode.value = mode
  editingId = row?.id
  draft.name = row ? rowName(row) : ''
  draft.kind = row?.kind ?? 'standard'
  dialogOpen.value = true
}
async function save() {
  if (saving.value || !editRef.value) return
  saving.value = true
  const valid = await editRef.value.validate().catch(() => false)
  saving.value = false
  if (!valid || !dialogOpen.value) return
  const values = { name: draft.name.trim(), kind: draft.kind }
  if (dialogMode.value === 'create') {
    rows.value.unshift({ id: nextId++, ...values })
    resetFilters()
    if (props.scenario !== 'normal') emit('recover')
    feedback.value = 'created'
  } else {
    const row = rows.value.find(item => item.id === editingId)
    if (row) Object.assign(row, values)
    feedback.value = 'edited'
  }
  dialogOpen.value = false
}
</script>
