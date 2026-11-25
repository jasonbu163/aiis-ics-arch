<!-- 能耗写入来源的独立登记、查询、启停和逻辑删除。 -->
<template>
  <BaseCard :title="source('title')" class="energy-write-sources">
    <template #actions>
      <div class="table-actions">
        <ActionButton variant="primary" :disabled="loading || saving || failed" @click="openEditor()">{{ tr('add') }}</ActionButton>
        <el-tooltip :content="tr('resetWidths')" placement="top">
          <ActionButton @click="columns.reset()">{{ tr('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <el-form class="source-toolbar" label-position="top" @submit.prevent="keyword = draft.trim().toLowerCase()">
      <el-form-item class="source-toolbar__keyword" :label="tr('configKeyword')">
        <el-input v-model="draft" clearable />
      </el-form-item>
      <el-form-item class="source-toolbar__actions">
        <div class="table-actions">
          <ActionButton variant="primary" native-type="submit">{{ tr('search') }}</ActionButton>
          <ActionButton @click="resetFilters">{{ t('common.reset') }}</ActionButton>
        </div>
      </el-form-item>
    </el-form>
    <el-alert v-if="failed" type="error" show-icon :title="tr('loadFailed')" :closable="false">
      <ActionButton size="small" @click="load">{{ tr('retry') }}</ActionButton>
    </el-alert>
    <el-table v-else :key="columns.version.value" v-loading="loading" :data="visibleRows"
      :empty-text="source(rows.length ? 'noMatching' : 'empty')" row-key="sourceKey" border
      @header-dragend="columns.onHeaderDragEnd">
      <el-table-column prop="sourceKey" :label="source('key')" :width="columns.widths.sourceKey" :min-width="140" />
      <el-table-column prop="name" :label="source('name')" :width="columns.widths.name" :min-width="125">
        <template #default="{ row }">{{ row.name || '—' }}</template>
      </el-table-column>
      <el-table-column prop="enabled" :label="source('status')" :width="columns.widths.enabled" :min-width="90">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">{{ source(row.enabled ? 'enabled' : 'disabled') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="tr('actions')" width="230" :resizable="false">
        <template #default="{ row }">
          <div class="row-actions">
            <ActionButton variant="row" :disabled="saving || loading" @click="openEditor(row)">{{ tr('edit') }}</ActionButton>
            <ActionButton size="small" :disabled="saving || loading" @click="changeSource(row)">
              {{ source(row.enabled ? 'disable' : 'enable') }}
            </ActionButton>
            <ActionButton variant="danger" size="small" :disabled="saving || loading" @click="changeSource(row, true)">
              {{ source('remove') }}
            </ActionButton>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="source(editing ? 'editTitle' : 'addTitle')" align-center
      class="standard-form-dialog compact-form-dialog" width="min(540px, calc(100vw - 32px))"
      :show-close="false" :close-on-click-modal="true">
      <el-form label-position="top" @submit.prevent="save">
        <el-form-item :label="source('key')">
          <el-input v-model="form.sourceKey" :disabled="editing || saving" maxlength="64" />
          <small v-if="!editing">{{ source('keyHint') }}</small>
        </el-form-item>
        <el-form-item :label="source('name')"><el-input v-model="form.name" :disabled="saving" maxlength="128" /></el-form-item>
        <el-form-item :label="source('status')">
          <el-switch v-model="form.enabled" :aria-label="source('status')" :disabled="saving" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="dialog = false">{{ tr('cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" :disabled="!sourceKeyPattern.test(form.sourceKey)"
            @click="save">{{ tr('save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="confirmationOpen" :title="source(deleting ? 'removeTitle' : 'disableTitle')" align-center
      class="standard-form-dialog compact-form-dialog" width="min(540px, calc(100vw - 32px))"
      :show-close="false" :close-on-click-modal="true">
      <p>{{ t(`energy.writeSources.${deleting ? 'removeHint' : 'disableHint'}`, { key: pendingSource?.sourceKey }) }}</p>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="confirmationOpen = false">{{ tr('cancel') }}</ActionButton>
          <ActionButton :variant="deleting ? 'danger' : 'primary'" :loading="saving" @click="confirmChange">
            {{ source(deleting ? 'remove' : 'disable') }}
          </ActionButton>
        </div>
      </template>
    </el-dialog>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { createEnergyWriteSource, deleteEnergyWriteSource, energyWriteSources, updateEnergyWriteSource } from '../api/observations'

const { t } = useI18n()
const tr = key => t(`energy.observation.${key}`)
const source = key => t(`energy.writeSources.${key}`)
const columns = useTableColumnWidths('energy.writeSources', {
  sourceKey: { width: 185, minWidth: 140 }, name: { width: 150, minWidth: 125 }, enabled: { width: 105, minWidth: 90 }
})
const sourceKeyPattern = /^[A-Za-z0-9_.-]{1,64}$/
const rows = ref([])
const draft = ref('')
const keyword = ref('')
const loading = ref(false)
const saving = ref(false)
const failed = ref(false)
const dialog = ref(false)
const confirmationOpen = ref(false)
const pendingSource = ref(null)
const deleting = ref(false)
const editing = ref(false)
const form = reactive({ sourceKey: '', name: '', enabled: true })
const visibleRows = computed(() => rows.value.filter(row =>
  [row.sourceKey, row.name].some(value => value?.toLowerCase().includes(keyword.value))
))

async function load() {
  if (loading.value) return
  loading.value = true
  failed.value = false
  try {
    rows.value = await energyWriteSources()
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  draft.value = ''
  keyword.value = ''
}

function openEditor(row) {
  editing.value = !!row
  Object.assign(form, { sourceKey: row?.sourceKey ?? '', name: row?.name ?? '', enabled: row?.enabled ?? true })
  dialog.value = true
}

async function mutate(action) {
  if (saving.value) return
  saving.value = true
  try {
    await action()
    dialog.value = false
    confirmationOpen.value = false
    await load()
  } catch (error) {
    ElMessage.error(source(error.response?.status === 409 ? 'conflict' : 'saveFailed'))
  } finally {
    saving.value = false
  }
}

function save() {
  if (!dialog.value || !sourceKeyPattern.test(form.sourceKey)) return
  const { sourceKey, name, enabled } = form
  const data = { name: name || null, enabled }
  return mutate(() => editing.value ? updateEnergyWriteSource(sourceKey, data) : createEnergyWriteSource({ sourceKey, ...data }))
}

function changeSource(row, remove = false) {
  if (!remove && !row.enabled) return mutate(() => updateEnergyWriteSource(row.sourceKey, { enabled: true }))
  pendingSource.value = row
  deleting.value = remove
  confirmationOpen.value = true
}

function confirmChange() {
  if (!confirmationOpen.value) return
  const key = pendingSource.value.sourceKey
  return mutate(() => deleting.value ? deleteEnergyWriteSource(key) : updateEnergyWriteSource(key, { enabled: false }))
}

onMounted(load)
</script>

<style scoped>
.energy-write-sources { container: energy-write-sources / inline-size; }
.source-toolbar {
  --source-card-inset: var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 4px 16px;
  margin: 0 calc(-1 * var(--source-card-inset)) 16px;
  padding-inline: var(--source-card-inset);
  border-bottom: 1px solid var(--border-secondary);
}
.source-toolbar .source-toolbar__keyword { flex: 1 1 180px; min-width: 0; }
.source-toolbar .source-toolbar__actions { margin-inline-start: auto; }
@container energy-write-sources (max-width: 1020px) {
  .source-toolbar { --source-card-inset: 18px; }
}
@container energy-write-sources (max-width: 560px) {
  .source-toolbar { --source-card-inset: 8px; }
}
</style>
