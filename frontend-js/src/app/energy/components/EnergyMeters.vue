<!-- 从表计管理工作区维护表计定义与登录角色可读范围。 -->
<template>
  <BaseCard :title="meter('title')">
    <template #actions>
      <div class="table-actions">
        <ActionButton variant="primary" :disabled="loading || saving || failed" @click="openEditor()">{{ tr('add') }}</ActionButton>
        <el-tooltip :content="tr('resetWidths')" placement="top">
          <ActionButton @click="columns.reset()">{{ tr('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <el-form class="meter-toolbar" label-position="top" @submit.prevent="keyword = draft.trim().toLowerCase()">
      <el-form-item class="meter-toolbar__keyword" :label="tr('configKeyword')">
        <el-input v-model="draft" clearable />
      </el-form-item>
      <el-form-item class="meter-toolbar__actions">
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
      :empty-text="meter(rows.length ? 'noMatching' : 'empty')" row-key="meterId" border
      @header-dragend="resizeColumn">
      <el-table-column prop="meterId" :label="meter('key')" :min-width="columns.widths.meterId" />
      <el-table-column prop="nameZh" :label="meter('nameZh')" :min-width="columns.widths.nameZh" />
      <el-table-column prop="nameEn" :label="meter('nameEn')" :min-width="columns.widths.nameEn" />
      <el-table-column prop="readRoles" :label="meter('roles')" :min-width="columns.widths.readRoles">
        <template #default="{ row }">{{ row.readRoles.map(roleLabel).join(' / ') || '—' }}</template>
      </el-table-column>
      <el-table-column :label="tr('actions')" width="100" align="center" :resizable="false">
        <template #default="{ row }">
          <div class="row-actions">
            <ActionButton size="small" variant="row" :disabled="saving || loading" @click="openEditor(row)">{{ tr('edit') }}</ActionButton>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="meter(editing ? 'editTitle' : 'addTitle')" align-center
      class="standard-form-dialog compact-form-dialog" width="min(560px, calc(100vw - 32px))"
      :show-close="false" :close-on-click-modal="true">
      <el-form label-position="top" @submit.prevent="save">
        <fieldset class="meter-section">
          <legend>{{ meter('basic') }}</legend>
          <el-form-item :label="meter('key')">
            <el-input v-model="form.meterId" :disabled="editing || saving" maxlength="64" />
          </el-form-item>
          <el-form-item :label="meter('nameZh')">
            <el-input v-model="form.nameZh" :disabled="saving" maxlength="128" />
          </el-form-item>
          <el-form-item :label="meter('nameEn')">
            <el-input v-model="form.nameEn" :disabled="saving" maxlength="128" />
          </el-form-item>
        </fieldset>
        <fieldset class="meter-section">
          <legend>{{ meter('roles') }}</legend>
          <el-checkbox-group v-model="form.readRoles" :disabled="saving" :aria-label="meter('roles')">
            <el-checkbox v-for="role in roleOptions" :key="role" :value="role">{{ roleLabel(role) }}</el-checkbox>
          </el-checkbox-group>
        </fieldset>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="dialog = false">{{ tr('cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" :disabled="!valid" @click="save">{{ tr('save') }}</ActionButton>
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
import { createEnergyMeter, energyMeters, updateEnergyMeter } from '../api/observations'

const { t, te } = useI18n()
const tr = key => t(`energy.observation.${key}`)
const meter = key => t(`energy.meters.${key}`)
const roleLabel = role => te(`system.roles.${role}`) ? t(`system.roles.${role}`) : role
const columns = useTableColumnWidths('energy.meters', {
  meterId: { width: 155, minWidth: 140 }, nameZh: { width: 135, minWidth: 125 },
  nameEn: { width: 135, minWidth: 125 }, readRoles: { width: 160, minWidth: 140 }
})
const rows = ref([])
const draft = ref('')
const keyword = ref('')
const loading = ref(false)
const saving = ref(false)
const failed = ref(false)
const dialog = ref(false)
const editing = ref(null)
const form = reactive({ meterId: '', nameZh: '', nameEn: '', readRoles: [] })
const valid = computed(() => form.meterId.length > 0 && form.meterId === form.meterId.trim()
  && form.nameZh.trim() && form.nameEn.trim())
const roleOptions = computed(() => [...new Set(['admin', 'supervisor', 'operator',
  ...rows.value.flatMap(row => row.readRoles), ...form.readRoles])])
const visibleRows = computed(() => rows.value.filter(row =>
  [row.meterId, row.nameZh, row.nameEn, ...row.readRoles].some(value => value.toLowerCase().includes(keyword.value))
))

function resizeColumn(newWidth, oldWidth, column) {
  // 保存拖动偏移，表格继续按可用宽度分配各列的剩余空间。
  columns.onHeaderDragEnd(columns.widths[column.property] + newWidth - oldWidth, oldWidth, column)
  column.width = undefined
}

function resetFilters() {
  draft.value = ''
  keyword.value = ''
}

function openEditor(row) {
  editing.value = row || null
  Object.assign(form, row
    ? { ...row, readRoles: [...row.readRoles] }
    : { meterId: '', nameZh: '', nameEn: '', readRoles: ['admin'] })
  dialog.value = true
}

async function load() {
  if (loading.value) return
  loading.value = true
  failed.value = false
  try {
    rows.value = await energyMeters()
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!dialog.value || !valid.value || saving.value) return
  const { meterId, nameZh, nameEn, readRoles } = form
  const current = editing.value
  const data = current ? { meterId } : { meterId, nameZh, nameEn, readRoles }
  if (current) {
    if (nameZh !== current.nameZh) data.nameZh = nameZh
    if (nameEn !== current.nameEn) data.nameEn = nameEn
    if (readRoles.length !== current.readRoles.length || readRoles.some(role => !current.readRoles.includes(role))) {
      data.readRoles = readRoles
    }
    if (Object.keys(data).length === 1) {
      dialog.value = false
      return
    }
  }
  saving.value = true
  try {
    await (current ? updateEnergyMeter(data) : createEnergyMeter(data))
    dialog.value = false
    await load()
  } catch (error) {
    ElMessage.error(meter(error.response?.status === 409 ? 'conflict' : 'saveFailed'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.meter-toolbar {
  --meter-card-inset: 24px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: var(--space-xs) var(--space-md);
  margin: 0 calc(-1 * var(--meter-card-inset)) var(--space-md);
  padding-inline: var(--meter-card-inset);
  border-bottom: 1px solid var(--border-secondary);
}
.meter-toolbar__keyword { flex: 1 1 180px; min-width: 0; }
.meter-toolbar__actions { margin-inline-start: auto; max-width: 100%; }
@media (max-width: 768px) {
  .meter-toolbar { --meter-card-inset: 18px; }
}
.meter-section { border: 0; margin: 0; padding: 0; min-inline-size: 0; }
.meter-section legend { font-weight: 600; margin-block-end: var(--space-sm); }
.meter-section + .meter-section { border-block-start: 1px solid var(--border-secondary); padding-block-start: var(--space-sm); }
</style>
