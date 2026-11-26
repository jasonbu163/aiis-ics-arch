<!-- 启用项目的独立现价、最新或按日历史及录入弹窗。 -->
<template>
  <div class="price-page page-layout">
    <BaseCard class="price-main-card" :title="t('energy.price.title')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" :disabled="!current.length || currentLoading || currentError" @click="openAdd">{{ t('energy.price.add') }}</ActionButton>
          <ActionButton variant="refresh" :loading="currentLoading || historyLoading" @click="refresh">{{ t('common.refresh') }}</ActionButton>
        </div>
      </template>
      <section class="price-editor-section" v-loading="currentLoading">
        <el-alert v-if="currentError" :title="t('energy.price.currentLoadError')" type="error" :closable="false" />
        <el-empty v-else-if="!currentLoading && !current.length" :description="tr('noEnabledItems')" />
        <div class="price-editor-grid">
          <article v-for="item in current" :key="item.itemKey" class="price-editor-item">
            <h3>{{ name(item) }}</h3>
            <strong class="price-value">{{ displayPrice(item.price) }}</strong>
            <span>{{ unit(item) }}</span>
            <span class="price-note">{{ item.observedAt ? businessDateTime(item.observedAt) : '—' }}</span>
            <span v-if="item.remark" class="price-note">{{ item.remark }}</span>
          </article>
        </div>
      </section>
      <BaseCard class="price-history-card" :title="t('energy.price.history')" compact>
        <template #actions>
          <div class="table-actions">
            <el-date-picker v-model="selectedDate" type="date" size="large" value-format="YYYY-MM-DD" clearable
              :placeholder="t('energy.price.historyLatest')" :aria-label="t('energy.price.historyDate')" @change="loadHistory" />
            <el-tooltip :content="t('energy.observation.resetWidths')" placement="top">
              <ActionButton @click="columns.reset()">{{ t('energy.observation.resetWidthsButton') }}</ActionButton>
            </el-tooltip>
          </div>
        </template>
        <el-alert v-if="historyError" :title="t('energy.price.historyLoadError')" type="error" :closable="false" />
        <div class="table-scroll">
          <el-table :key="columns.version.value" :data="history" row-key="hourStart" class="vibe-table" border v-loading="historyLoading"
            :empty-text="selectedDate ? t('energy.price.historyEmpty') : t('common.noData')" @header-dragend="columns.onHeaderDragEnd">
            <el-table-column prop="hourStart" :label="t('energy.price.hourStart')" :width="columns.widths.hourStart" :min-width="165">
              <template #default="{ row }">{{ businessDateTime(row.hourStart).slice(0, 16) }}</template>
            </el-table-column>
            <el-table-column v-for="item in historyColumns" :key="item.itemKey" :prop="columnKey(item)"
              :label="label(item)" :width="columns.widths[columnKey(item)]" :min-width="150">
              <template #default="{ row }">{{ displayPrice(valueFor(row, item.itemKey)?.price) }}</template>
            </el-table-column>
            <el-table-column prop="remark" :label="t('energy.price.remark')" :width="columns.widths.remark" :min-width="180">
              <template #default="{ row }">{{ row.remark || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('energy.observation.actions')" width="100" :resizable="false" align="center">
              <template #default="{ row }">
                <div v-if="historyColumns.some(item => valueFor(row, item.itemKey))" class="row-actions">
                  <ActionButton size="small" variant="row" @click="details = row">{{ tr('details') }}</ActionButton>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </BaseCard>
    </BaseCard>

    <el-dialog v-model="dialogVisible" :title="t('energy.price.add')" width="min(720px, calc(100vw - 24px))"
      class="standard-form-dialog compact-form-dialog" align-center :close-on-click-modal="true"
      :close-on-press-escape="!saving" :show-close="!saving" :before-close="beforeClose">
      <el-form :disabled="saving" label-position="top" @submit.prevent="save">
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('recordInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="t('energy.price.observedAt')">
              <el-date-picker v-model="observedAt" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" :editable="false"
                clearable :placeholder="t('energy.price.serverTimeHint')" />
            </el-form-item>
            <el-form-item :label="t('energy.price.remark')">
              <el-input v-model="remark" :maxlength="2000" clearable @update:model-value="remarkTouched = true" />
            </el-form-item>
          </div>
        </section>
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ tr('submittedPrices') }}</h3>
          <p class="price-form-hint">{{ tr('partialHint') }}</p>
          <div class="dialog-form-grid">
            <template v-for="item in formItems" :key="item.itemKey">
              <el-form-item :label="label(item)">
                <el-input v-model="item.price" inputmode="decimal" />
              </el-form-item>
              <el-form-item :label="tr('itemRemark', { name: name(item) })">
                <el-input v-model="item.remark" :maxlength="500" clearable @update:model-value="item.remarkTouched = true" />
              </el-form-item>
            </template>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialogVisible = false">{{ t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" :disabled="saving" @click="save">{{ t('common.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog :model-value="Boolean(details)" :title="tr('details')" width="min(690px, calc(100vw - 24px))"
      class="standard-form-dialog compact-form-dialog" align-center :close-on-click-modal="true"
      @update:model-value="details = null">
      <template v-if="details">
        <section v-for="item in detailItems" :key="item.itemKey" class="dialog-section">
          <h3 class="dialog-section__title">{{ label(item) }}</h3>
          <dl class="dialog-form-grid">
            <div><dt>{{ tr('priceValue') }}</dt><dd>{{ displayPrice(item.value.price) }}</dd></div>
            <div><dt>{{ t('energy.price.operator') }}</dt><dd>{{ item.value.operator }}</dd></div>
            <div><dt>{{ t('energy.price.observedAt') }}</dt><dd>{{ businessDateTime(item.value.observedAt) }}</dd></div>
            <div><dt>{{ t('energy.price.lastModified') }}</dt><dd>{{ businessDateTime(item.value.updatedAt) }}</dd></div>
            <div><dt>{{ t('energy.price.remark') }}</dt><dd>{{ item.value.remark || '—' }}</dd></div>
          </dl>
        </section>
      </template>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="details = null">{{ t('common.close') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { currentPrices, hourlyPrices, pricingItems, saveHourlyPrices } from '../api/pricing'
import { businessDate, businessDateTime, encodeObservedAt, priceItemName, priceItemUnit, validPrice } from '../components/energyPricing'

const { t, locale } = useI18n()
const tr = (key, args = {}) => t(`energy.pricing.${key}`, args)
const name = item => priceItemName(item, locale.value)
const unit = item => priceItemUnit(item, t)
const label = item => `${name(item)} (${unit(item)})`
const displayPrice = value => value == null ? '—' : new Intl.NumberFormat(locale.value, { maximumFractionDigits: 4 }).format(value)
const columnKey = item => `item:${item.itemKey}`
const current = shallowRef([])
const currentLoading = ref(false)
const currentError = ref(false)
const history = shallowRef([])
const historyColumns = shallowRef([])
const historyLoading = ref(false)
const historyError = ref(false)
const selectedDate = ref(null)
const observedAt = ref(null)
const remark = ref('')
const remarkTouched = ref(false)
const formItems = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const details = shallowRef(null)
const valueFor = (row, key) => Object.hasOwn(row.values, key) ? row.values[key] : null
const detailItems = computed(() => historyColumns.value
  .map(item => ({ ...item, value: valueFor(details.value, item.itemKey) })).filter(item => item.value))
let currentRequest = 0
let historyRequest = 0
let active = true

const columnDefinitions = {
  hourStart: { width: 165, minWidth: 165 }, remark: { width: 220, minWidth: 180 }
}
const columns = shallowRef(useTableColumnWidths('energy.price.history', columnDefinitions))
function initializeWidths(items) {
  const newItems = items.filter(item => !Object.hasOwn(columnDefinitions, columnKey(item)))
  if (!newItems.length) return
  for (const item of newItems) columnDefinitions[columnKey(item)] = { width: 162, minWidth: 150 }
  columns.value = useTableColumnWidths('energy.price.history', columnDefinitions)
}

async function loadCurrent() {
  const request = ++currentRequest
  currentLoading.value = true
  currentError.value = false
  try {
    const result = await currentPrices()
    if (!Array.isArray(result) || result.some(item => item.price !== null && !validPrice(item.price))) {
      throw new Error('invalid_current')
    }
    if (active && request === currentRequest) current.value = result
  } catch {
    if (active && request === currentRequest) {
      currentError.value = true
      ElMessage.error(t('energy.price.currentLoadError'))
    }
  } finally {
    if (active && request === currentRequest) currentLoading.value = false
  }
}

async function loadHistory() {
  const request = ++historyRequest
  historyLoading.value = true
  historyError.value = false
  history.value = []
  try {
    const date = selectedDate.value
    const params = date ? { date, page: 1, pageSize: 24 } : { page: 1, pageSize: 1 }
    const result = await hourlyPrices(params)
    if (active && request === historyRequest) {
      initializeWidths(result.columns)
      historyColumns.value = result.columns.filter(item => item.enabled)
      history.value = result.items
    }
  } catch {
    if (active && request === historyRequest) {
      historyError.value = true
      ElMessage.error(t('energy.price.historyLoadError'))
    }
  } finally {
    if (active && request === historyRequest) historyLoading.value = false
  }
}

async function loadDefinitions() {
  try {
    const items = await pricingItems()
    if (active) initializeWidths(items)
  } catch {
    // 历史查询独立提供可见列，项目列表只用于保留未显示列的偏好。
  }
}

function refresh() {
  return Promise.all([loadCurrent(), loadHistory(), loadDefinitions()])
}

function openAdd() {
  if (saving.value) return
  formItems.value = current.value.map(item => ({ ...item, price: '', remark: '', remarkTouched: false }))
  observedAt.value = null
  remark.value = ''
  remarkTouched.value = false
  dialogVisible.value = true
}

function beforeClose(done) {
  if (!saving.value) done()
}

async function save() {
  if (!dialogVisible.value || saving.value) return
  const entered = formItems.value.filter(item => item.price.trim())
  if (!entered.length) {
    ElMessage.warning(tr('atLeastOnePrice'))
    return
  }
  if (entered.some(item => !validPrice(item.price.trim()))) {
    ElMessage.error(t('energy.price.invalidPrice'))
    return
  }
  let observed
  try { observed = encodeObservedAt(observedAt.value) }
  catch { ElMessage.error(t('energy.price.invalidObservedAt')); return }
  const items = Object.fromEntries(entered.map(item => [item.itemKey, {
    price: item.price.trim(), ...(item.remarkTouched ? { remark: item.remark } : {})
  }]))
  saving.value = true
  try {
    const saved = await saveHourlyPrices({
      observedAt: observed, items, ...(remarkTouched.value ? { remark: remark.value } : {})
    })
    if (!active) return
    dialogVisible.value = false
    ElMessage.success(t('common.success'))
    selectedDate.value = businessDate(Object.values(saved.values)[0].observedAt)
    await refresh()
  } catch {
    if (active) ElMessage.error(tr('priceSaveError'))
  } finally {
    saving.value = false
  }
}

onMounted(refresh)
onBeforeUnmount(() => { active = false })
</script>

<style scoped>
.price-page {
  display: grid;
  align-content: start;
  min-width: 0;
  gap: var(--space-lg);
}
.price-main-card, .price-history-card { min-width: 0; height: auto; }
.price-page :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
.price-editor-section { display: grid; gap: var(--space-sm); margin-block-end: var(--space-lg); }
.price-editor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr)); gap: var(--space-md); }
.price-editor-item {
  display: grid;
  gap: var(--space-sm);
  min-width: 0;
  padding: var(--space-md);
  border: 1px solid var(--border-primary);
  border-radius: var(--card-radius);
  background: var(--bg-primary);
}
.price-editor-item h3 { margin: 0; font-size: 16px; font-weight: 590; overflow-wrap: anywhere; }
.price-value { font-size: 28px; color: var(--text-primary); overflow-wrap: anywhere; }
.price-note, .price-form-hint { color: var(--text-secondary); overflow-wrap: anywhere; }
.price-form-hint { margin: 0 0 var(--space-sm); }
.table-scroll { min-width: 0; overflow-x: auto; }
@media (max-width: 1279px) {
  :global(body:has(.price-page)) { min-width: 0; }
}
</style>
