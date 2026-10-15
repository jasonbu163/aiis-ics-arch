<!-- 文件路径: /frontend-js/src/app/auxiliary/views/price/index.vue
  功能描述: 只读当前价、上海自然日小时历史与整组价格新增弹窗。 -->
<template>
  <div class="price-page page-layout">
    <BaseCard class="price-main-card" :title="$t('auxiliary.price.title')">
      <template #actions>
        <ActionButton variant="refresh" :loading="currentLoading || historyLoading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>{{ $t('common.refresh') }}
        </ActionButton>
      </template>
      <section class="price-editor-section" v-loading="currentLoading">
        <el-alert v-if="currentError" :title="$t('auxiliary.price.currentLoadError')" type="error" :closable="false" />
        <div class="price-editor-grid">
          <article v-for="item in priceTypes" :key="item.key" class="price-editor-item">
            <h3>{{ $t(`auxiliary.price.${item.key}`) }}</h3>
            <strong class="price-value">{{ currentPrice == null ? $t('auxiliary.price.currentEmpty') : displayPrice(currentPrice[item.key + 'Price']) }}</strong>
            <span>{{ $t(`auxiliary.price.units.${item.unit}`) }}</span>
            <span class="price-note">{{ currentPrice?.[item.key + 'Remark'] || '—' }}</span>
          </article>
        </div>
      </section>
      <section class="price-history-section">
        <div class="section-title-row">
          <h3>{{ $t('auxiliary.price.history') }}</h3>
          <div class="table-actions">
            <el-date-picker v-model="selectedDate" type="date" size="large" value-format="YYYY-MM-DD" :clearable="false"
              :aria-label="$t('auxiliary.price.historyDate')" @change="loadHistory" />
            <ActionButton variant="primary" @click="openAdd">{{ $t('auxiliary.price.add') }}</ActionButton>
          </div>
        </div>
        <el-alert v-if="historyError" :title="$t('auxiliary.price.historyLoadError')" type="error" :closable="false" />
        <div class="table-scroll">
          <el-table :data="priceHistory" class="vibe-table" border v-loading="historyLoading" :empty-text="$t('auxiliary.price.historyEmpty')">
            <el-table-column prop="observedAt" :label="$t('auxiliary.price.observedAt')" width="185">
              <template #default="{ row }">{{ businessDateTime(row.observedAt) }}</template>
            </el-table-column>
            <el-table-column prop="hourStart" :label="$t('auxiliary.price.hourStart')" width="100">
              <template #default="{ row }">{{ businessDateTime(row.hourStart).slice(11, 16) }}</template>
            </el-table-column>
            <el-table-column prop="updatedAt" :label="$t('auxiliary.price.lastModified')" width="185">
              <template #default="{ row }">{{ businessDateTime(row.updatedAt) }}</template>
            </el-table-column>
            <el-table-column v-for="item in priceTypes" :key="item.key" :prop="item.key + 'Price'"
              :label="`${$t('auxiliary.price.' + item.key)} (${$t('auxiliary.price.units.' + item.unit)})`" width="170">
              <template #default="{ row }">{{ displayPrice(row[item.key + 'Price']) }}</template>
            </el-table-column>
            <el-table-column prop="operator" :label="$t('auxiliary.price.operator')" width="120" />
            <el-table-column prop="remark" :label="$t('auxiliary.price.remark')" min-width="220" />
          </el-table>
        </div>
      </section>
    </BaseCard>
    <el-dialog v-model="dialogVisible" :title="$t('auxiliary.price.add')" width="720px" class="standard-form-dialog"
      :close-on-click-modal="!saveLoading" :close-on-press-escape="!saveLoading" :show-close="!saveLoading" :before-close="beforeClose">
      <el-form ref="formRef" :model="form" :rules="rules" :disabled="saveLoading" label-position="top" class="price-dialog-form">
        <el-form-item :label="$t('auxiliary.price.observedAt')">
          <el-date-picker v-model="form.observedAt" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss"
            :editable="false" clearable :disabled="saveLoading" :placeholder="$t('auxiliary.price.serverTimeHint')" />
        </el-form-item>
        <el-alert :title="$t('auxiliary.price.serverTimeHint')" type="info" :closable="false" />
        <el-alert :title="$t('auxiliary.price.overwriteHint')" type="warning" :closable="false" />
        <template v-for="item in priceTypes" :key="item.key">
          <el-form-item :label="$t('auxiliary.price.' + item.key)" :prop="item.key + 'Price'">
            <el-input v-model="form[item.key + 'Price']" inputmode="decimal" />
          </el-form-item>
          <el-form-item :label="$t('auxiliary.price.' + item.key + 'Remark')" :prop="item.key + 'Remark'">
            <el-input v-model="form[item.key + 'Remark']" :maxlength="500" show-word-limit />
          </el-form-item>
        </template>
        <el-form-item :label="$t('auxiliary.price.remark')" prop="remark">
          <el-input v-model="form.remark" type="textarea" :maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saveLoading" @click="cancelAdd">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saveLoading" :disabled="saveLoading" @click="handleSave">{{ $t('common.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getCurrentPrice, createPrice, getPriceList } from '@/app/auxiliary/api'

const { t, locale } = useI18n()
const businessParts = value => Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
}).formatToParts(new Date(value)).map(part => [part.type, part.value]))
const businessDate = value => { const p = businessParts(value); return `${p.year}-${p.month}-${p.day}` }
const businessDateTime = value => { const p = businessParts(value); return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}:${p.second}` }
// Resolve picker civil fields in Shanghai independently of the browser timezone.
// Multiple instants in a repeated hour choose the earliest (fold=0); gaps are invalid.
const encodeObservedAt = value => {
  if (!value) return null
  const civil = Date.parse(`${value}Z`)
  if (!Number.isFinite(civil)) throw new Error('invalid_observed_at')
  const offsets = new Set()
  for (let hour = -14; hour <= 14; hour++) {
    const sample = civil + hour * 3600000
    offsets.add(Date.parse(`${businessDateTime(sample).replace(' ', 'T')}Z`) - sample)
  }
  const candidates = [...offsets].map(offset => civil - offset)
    .filter(instant => businessDateTime(instant).replace(' ', 'T') === value)
  if (!candidates.length) throw new Error('nonexistent_observed_at')
  return new Date(Math.min(...candidates)).toISOString()
}
const displayPrice = value => new Intl.NumberFormat(locale.value, { minimumFractionDigits: 4, maximumFractionDigits: 4 }).format(Number(value))
const priceTypes = [{ key: 'electric', unit: 'electric' }, { key: 'hydrogen', unit: 'gas' }, { key: 'argon', unit: 'gas' }]
const priceFields = priceTypes.map(item => item.key + 'Price')
const blankForm = () => ({ observedAt: null, electricPrice: '', hydrogenPrice: '', argonPrice: '', electricRemark: '', hydrogenRemark: '', argonRemark: '', remark: '' })
const form = reactive(blankForm())
const formRef = ref()
const dialogVisible = ref(false)
const saveLoading = ref(false)
const currentPrice = ref(null)
const currentLoading = ref(false)
const currentError = ref(false)
const historyLoading = ref(false)
const historyError = ref(false)
const priceHistory = ref([])
const selectedDate = ref(businessDate(Date.now()))
let currentRequest = 0, historyRequest = 0, alive = true

// Keep decimal lexemes until the backend validates; never silently round user input.
const validPrice = value => typeof value === 'number' || typeof value === 'string'
  ? /^[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(String(value)) && Number(value) >= 0 && Number(value) <= 999999.9999
    && !/\.[0-9]{4}[0-9]*[1-9]/.test(String(value)) : false
const rules = Object.fromEntries(priceFields.map(field => [field, [{
  validator: (_rule, value, callback) => callback(validPrice(value) ? undefined : new Error(t('auxiliary.price.invalidPrice'))), trigger: 'blur'
}]]))
for (const field of ['electricRemark', 'hydrogenRemark', 'argonRemark', 'remark']) rules[field] = [{ max: field === 'remark' ? 2000 : 500, message: t('auxiliary.price.remarkTooLong'), trigger: 'blur' }]

const loadCurrent = async () => {
  const request = ++currentRequest
  currentLoading.value = true
  currentError.value = false
  try {
    const record = await getCurrentPrice()
    if (!alive || request !== currentRequest) return
    if (record != null && priceFields.some(field => !validPrice(record[field]))) throw new Error('invalid_current')
    currentPrice.value = record
  } catch (error) {
    if (alive && request === currentRequest) { currentError.value = true; ElMessage.error(t('auxiliary.price.currentLoadError')) }
  } finally { if (alive && request === currentRequest) currentLoading.value = false }
}
const loadHistory = async () => {
  const request = ++historyRequest, date = selectedDate.value
  historyLoading.value = true
  historyError.value = false
  priceHistory.value = []
  try {
    const result = await getPriceList({ date, page: 1, pageSize: 24 })
    if (alive && request === historyRequest && date === selectedDate.value) priceHistory.value = result.items
  } catch (error) {
    if (alive && request === historyRequest && date === selectedDate.value) { historyError.value = true; ElMessage.error(t('auxiliary.price.historyLoadError')) }
  } finally { if (alive && request === historyRequest && date === selectedDate.value) historyLoading.value = false }
}
const handleRefresh = () => Promise.all([loadCurrent(), loadHistory()])
const openAdd = () => { if (saveLoading.value) return; Object.assign(form, blankForm()); formRef.value?.clearValidate?.(); dialogVisible.value = true }
const cancelAdd = () => { if (!saveLoading.value) dialogVisible.value = false }
const beforeClose = done => { if (!saveLoading.value) done() }
const handleSave = async () => {
  if (!dialogVisible.value || !formRef.value || saveLoading.value) return
  saveLoading.value = true
  const snapshot = { ...form }
  try {
    try { if (await formRef.value.validate() === false) return } catch (error) { return }
    if (priceFields.some(field => !validPrice(snapshot[field]))) { ElMessage.error(t('auxiliary.price.invalidPrice')); return }
    try { snapshot.observedAt = encodeObservedAt(snapshot.observedAt) }
    catch (error) { ElMessage.error(t('auxiliary.price.invalidObservedAt')); return }
    let record
    try { record = await createPrice(snapshot) }
    catch (error) { if (alive) ElMessage.error(t('common.error')); return }
    if (!alive) return
    dialogVisible.value = false
    ElMessage.success(t('common.success'))
    selectedDate.value = businessDate(record.observedAt)
    // POST historical data is never assigned to current. Each GET owns its error feedback.
    await handleRefresh()
  } finally { if (alive) saveLoading.value = false }
}
onMounted(handleRefresh)
onBeforeUnmount(() => { alive = false; currentRequest++; historyRequest++ })
</script>

<style scoped>
.price-page {
  animation: fadeIn var(--transition-normal);
}

.price-main-card :deep(.base-card__body) {
  padding: 0;
}

.price-editor-section,
.price-history-section {
  padding: 28px 32px;
}

.price-history-section {
  border-top: 1px solid var(--border-secondary);
}

.price-editor-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.price-editor-item {
  display: grid;
  gap: 16px;
  padding: 22px;
  border: 1px solid var(--border-primary);
  border-radius: var(--card-radius);
  background: var(--bg-primary);
}

.price-editor-item__header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-secondary);
}

.price-editor-item__header h3,
.section-title-row h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 760;
}

.price-editor-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--border-primary);
  border-radius: 10px;
  color: var(--primary);
  background: var(--bg-tertiary);
}

.price-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.price-form :deep(.el-input-number) {
  width: 100%;
}

.price-unit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid var(--border-secondary);
  border-radius: 12px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
}

.price-unit-row strong {
  color: var(--text-primary);
  font-weight: 700;
}

.section-title-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }
.price-value { font-size: 28px; color: var(--text-primary); }
.price-note { color: var(--text-secondary); overflow-wrap: anywhere; }
.price-dialog-form { display: grid; gap: 16px; }
.price-dialog-form :deep(.el-date-editor) { max-width: 100%; }
@media (max-width: 600px) { .price-editor-section, .price-history-section { padding: 20px 16px; } }

@media (max-width: 1200px) {
  .price-editor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
