<!-- 配置管理中的单价项目定义、查询、启停和显示设置。 -->
<template>
  <BaseCard :title="tr('items')">
    <template #actions>
      <div class="table-actions">
        <ActionButton variant="primary" :disabled="loading || saving || failed" @click="openEditor()">{{ tr('addItem') }}</ActionButton>
        <el-tooltip :content="t('energy.observation.resetWidths')" placement="top">
          <ActionButton @click="columns.reset()">{{ t('energy.observation.resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <el-form class="pricing-search table-actions" inline @submit.prevent="keyword = draft.trim().toLowerCase()">
      <el-form-item :label="t('energy.observation.configKeyword')">
        <el-input v-model="draft" clearable />
      </el-form-item>
      <el-form-item>
        <ActionButton variant="primary" native-type="submit">{{ t('energy.observation.search') }}</ActionButton>
        <ActionButton @click="draft = keyword = ''">{{ t('common.reset') }}</ActionButton>
      </el-form-item>
    </el-form>
    <el-alert v-if="failed" type="error" :title="tr('itemsLoadError')" :closable="false">
      <ActionButton size="small" @click="load">{{ t('common.refresh') }}</ActionButton>
    </el-alert>
    <el-table v-else :key="columns.version.value" v-loading="loading" :data="visibleRows" row-key="itemKey" border
      class="vibe-table" :empty-text="t('common.noData')" @header-dragend="columns.onHeaderDragEnd">
      <el-table-column prop="itemKey" :label="tr('itemKey')" :width="columns.widths.itemKey" :min-width="135" />
      <el-table-column prop="nameZh" :label="tr('nameZh')" :width="columns.widths.nameZh" :min-width="145" />
      <el-table-column prop="nameEn" :label="tr('nameEn')" :width="columns.widths.nameEn" :min-width="145" />
      <el-table-column prop="unit" :label="tr('unit')" :width="columns.widths.unit" :min-width="120">
        <template #default="{ row }">{{ unitLabel(row) }}</template>
      </el-table-column>
      <el-table-column prop="sortOrder" :label="tr('sortOrder')" :width="columns.widths.sortOrder" :min-width="92" />
      <el-table-column prop="enabled" :label="tr('status')" :width="columns.widths.enabled" :min-width="105">
        <template #default="{ row }">{{ tr(row.enabled ? 'enabled' : 'disabled') }}</template>
      </el-table-column>
      <el-table-column :label="t('energy.observation.actions')" width="100" :resizable="false" align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <ActionButton size="small" variant="row" :disabled="saving || loading" @click="openEditor(row)">{{ t('energy.observation.edit') }}</ActionButton>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="tr(editing ? 'editItem' : 'addItem')" align-center
      class="standard-form-dialog compact-form-dialog" width="min(630px, calc(100vw - 32px))"
      :show-close="!saving" :close-on-click-modal="true" :close-on-press-escape="!saving" :before-close="beforeClose">
      <el-form label-position="top" :disabled="saving" @submit.prevent="save">
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('itemDefinition') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="tr('itemKey')">
              <el-input v-model="form.itemKey" :disabled="Boolean(editing)" maxlength="128" required />
            </el-form-item>
            <el-form-item :label="tr('unit')">
              <el-input v-model="form.unit" maxlength="128" required />
              <small v-if="editing">{{ tr('unitHint') }}</small>
            </el-form-item>
            <el-form-item :label="tr('nameZh')">
              <el-input v-model="form.nameZh" maxlength="128" />
            </el-form-item>
            <el-form-item :label="tr('nameEn')">
              <el-input v-model="form.nameEn" maxlength="128" />
            </el-form-item>
          </div>
          <small>{{ tr('nameHint') }}</small>
        </section>
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('displaySettings') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="tr('sortOrder')">
              <el-input-number v-model="form.sortOrder" :step="1" step-strictly
                :min="Number.MIN_SAFE_INTEGER" :max="Number.MAX_SAFE_INTEGER" />
            </el-form-item>
            <el-form-item :label="tr('status')">
              <el-switch v-model="form.enabled" :active-text="tr('enabled')" :inactive-text="tr('disabled')" />
            </el-form-item>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialog = false">{{ t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :disabled="!valid" :loading="saving" @click="save">{{ t('common.save') }}</ActionButton>
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
import { createPricingItem, pricingItems, updatePricingItem } from '../api/pricing'
import { priceItemUnit } from './energyPricing'

const { t } = useI18n()
const unitLabel = item => priceItemUnit(item, t)
const tr = key => t(`energy.pricing.${key}`)
const columns = useTableColumnWidths('energy.price.items', {
  itemKey: { width: 135, minWidth: 135 }, nameZh: { width: 145, minWidth: 145 },
  nameEn: { width: 145, minWidth: 145 }, unit: { width: 120, minWidth: 120 },
  sortOrder: { width: 92, minWidth: 92 }, enabled: { width: 105, minWidth: 105 }
})
const rows = ref([])
const draft = ref('')
const keyword = ref('')
const loading = ref(false)
const saving = ref(false)
const failed = ref(false)
const dialog = ref(false)
const editing = ref(null)
const blank = () => ({ itemKey: '', nameZh: '', nameEn: '', unit: '', sortOrder: 0, enabled: true })
const form = reactive(blank())
const valid = computed(() => form.itemKey.trim() && form.unit.trim() && (form.nameZh.trim() || form.nameEn.trim())
  && Number.isSafeInteger(form.sortOrder) && !saving.value)
const visibleRows = computed(() => rows.value.filter(row =>
  [row.itemKey, row.nameZh, row.nameEn, row.unit].some(value => value?.toLowerCase().includes(keyword.value))
))

function beforeClose(done) {
  if (!saving.value) done()
}

function openEditor(row) {
  editing.value = row || null
  Object.assign(form, row ? { ...row, nameZh: row.nameZh || '', nameEn: row.nameEn || '' } : blank())
  dialog.value = true
}

async function load() {
  loading.value = true
  failed.value = false
  try {
    rows.value = await pricingItems()
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!dialog.value || !valid.value) return
  const data = {
    nameZh: form.nameZh.trim() || null, nameEn: form.nameEn.trim() || null, unit: form.unit.trim(),
    sortOrder: form.sortOrder, enabled: form.enabled
  }
  const item = editing.value
  saving.value = true
  try {
    await (item ? updatePricingItem(item.itemKey, data) : createPricingItem({ itemKey: form.itemKey.trim(), ...data }))
    dialog.value = false
    ElMessage.success(t('common.success'))
    await load()
  } catch (error) {
    const code = error.response?.data?.errorCode
    ElMessage.error(tr(code === 'energy.pricing_item_exists' ? 'itemConflict' : code === 'energy.pricing_unit_in_use' ? 'unitHint' : 'itemSaveError'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.pricing-search {
  justify-content: flex-start;
  flex-wrap: wrap;
}
.pricing-search .el-form-item { margin-bottom: var(--space-sm); }
</style>
