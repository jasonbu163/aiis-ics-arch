<!--
  文件路径: /frontend-next-js/src/app/auxiliary/views/price/index.vue
  功能描述: 能耗单价设置页面
  主要功能:
    - 设置电能、氢气、氩气的单价
    - 查看历史价格记录
    - 保存价格设置
-->
<template>
  <div class="price-page page-layout">
    <BaseCard class="price-main-card" :title="$t('auxiliary.price.title')">
      <template #actions>
        <ActionButton variant="refresh" :loading="currentLoading || historyLoading" :disabled="formBusy || historyLoading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </ActionButton>
        <ActionButton variant="primary" :loading="saveLoading" :disabled="formBusy || historyLoading" @click="handleSave">
          <el-icon><Check /></el-icon>
          {{ $t('common.save') }}
        </ActionButton>
      </template>

      <section class="price-editor-section" v-loading="currentLoading">
        <el-alert v-if="currentEmpty" :title="$t('auxiliary.price.currentEmpty')" type="info" :closable="false" />
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          :disabled="formBusy"
          label-position="top"
          class="price-form"
        >
          <div class="price-editor-grid">
            <article class="price-editor-item">
              <div class="price-editor-item__header">
                <span class="price-editor-icon">
                  <el-icon><Lightning /></el-icon>
                </span>
                <h3>{{ $t('auxiliary.price.electric') }}</h3>
              </div>
              <el-form-item :label="$t('auxiliary.price.price')" prop="electricPrice">
                <el-input-number v-model="form.electricPrice" :min="0" :precision="4" :step="0.01" />
              </el-form-item>
              <div class="price-unit-row">
                <span>{{ $t('auxiliary.price.unit') }}</span>
                <strong>{{ $t('auxiliary.price.units.electric') }}</strong>
              </div>
              <el-form-item :label="$t('auxiliary.price.remark')">
                <el-input v-model="form.electricRemark" :placeholder="$t('auxiliary.price.electricRemark')" />
              </el-form-item>
            </article>

            <article class="price-editor-item">
              <div class="price-editor-item__header">
                <span class="price-editor-icon">
                  <el-icon><WindPower /></el-icon>
                </span>
                <h3>{{ $t('auxiliary.price.hydrogen') }}</h3>
              </div>
              <el-form-item :label="$t('auxiliary.price.price')" prop="hydrogenPrice">
                <el-input-number v-model="form.hydrogenPrice" :min="0" :precision="4" :step="0.1" />
              </el-form-item>
              <div class="price-unit-row">
                <span>{{ $t('auxiliary.price.unit') }}</span>
                <strong>{{ $t('auxiliary.price.units.gas') }}</strong>
              </div>
              <el-form-item :label="$t('auxiliary.price.remark')">
                <el-input v-model="form.hydrogenRemark" :placeholder="$t('auxiliary.price.hydrogenRemark')" />
              </el-form-item>
            </article>

            <article class="price-editor-item">
              <div class="price-editor-item__header">
                <span class="price-editor-icon">
                  <el-icon><Aim /></el-icon>
                </span>
                <h3>{{ $t('auxiliary.price.argon') }}</h3>
              </div>
              <el-form-item :label="$t('auxiliary.price.price')" prop="argonPrice">
                <el-input-number v-model="form.argonPrice" :min="0" :precision="4" :step="0.1" />
              </el-form-item>
              <div class="price-unit-row">
                <span>{{ $t('auxiliary.price.unit') }}</span>
                <strong>{{ $t('auxiliary.price.units.gas') }}</strong>
              </div>
              <el-form-item :label="$t('auxiliary.price.remark')">
                <el-input v-model="form.argonRemark" :placeholder="$t('auxiliary.price.argonRemark')" />
              </el-form-item>
            </article>
          </div>
        </el-form>
      </section>

      <section class="price-history-section">
        <div class="section-title-row">
          <h3>{{ $t('auxiliary.price.history') }}</h3>
        </div>
        <div class="table-scroll">
          <el-table :data="priceHistory" class="vibe-table" border v-loading="historyLoading">
            <el-table-column prop="createdAt" :label="$t('auxiliary.price.updateTime')" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column prop="electricPrice" :label="`${$t('auxiliary.price.electric')}(${$t('auxiliary.price.units.electric')})`" width="160">
              <template #default="{ row }">
                {{ Number(row.electricPrice).toFixed(4) }}
              </template>
            </el-table-column>
            <el-table-column prop="hydrogenPrice" :label="`${$t('auxiliary.price.hydrogen')}(${$t('auxiliary.price.units.gas')})`" width="160">
              <template #default="{ row }">
                {{ Number(row.hydrogenPrice).toFixed(4) }}
              </template>
            </el-table-column>
            <el-table-column prop="argonPrice" :label="`${$t('auxiliary.price.argon')}(${$t('auxiliary.price.units.gas')})`" width="160">
              <template #default="{ row }">
                {{ Number(row.argonPrice).toFixed(4) }}
              </template>
            </el-table-column>
            <el-table-column prop="operator" :label="$t('auxiliary.price.operator')" width="120" />
            <el-table-column prop="remark" :label="$t('auxiliary.price.remark')" min-width="220" />
          </el-table>
        </div>
      </section>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getCurrentPrice, createPrice, getPriceList } from '@/app/auxiliary/api'
import { formatDateTime } from '@/utils/date'

const { t } = useI18n()
const formRef = ref()
const currentLoading = ref(false)
const saveLoading = ref(false)
const historyLoading = ref(false)
const currentEmpty = ref(false)
const formBusy = computed(() => currentLoading.value || saveLoading.value)
const priceFields = ['electricPrice', 'hydrogenPrice', 'argonPrice']
const form = reactive({
  electricPrice: undefined,
  hydrogenPrice: undefined,
  argonPrice: undefined,
  electricRemark: '',
  hydrogenRemark: '',
  argonRemark: ''
})

const normalizePrice = value => {
  if (typeof value !== 'number' && typeof value !== 'string') return undefined
  if (typeof value === 'string' && !value.trim()) return undefined
  const price = Number(value)
  return Number.isFinite(price) && price >= 0 ? price : undefined
}
const rules = Object.fromEntries(priceFields.map(field => [field, [{
  validator: (_rule, value, callback) => callback(normalizePrice(value) === undefined
    ? new Error(t('auxiliary.price.invalidPrice')) : undefined),
  trigger: 'blur'
}]]))
const priceHistory = ref([])

const loadCurrent = async () => {
  currentLoading.value = true
  try {
    const record = await getCurrentPrice()
    if (record == null) {
      Object.assign(form, {
        electricPrice: undefined, hydrogenPrice: undefined, argonPrice: undefined,
        electricRemark: '', hydrogenRemark: '', argonRemark: ''
      })
      currentEmpty.value = true
      return
    }
    const prices = Object.fromEntries(priceFields.map(field => [field, normalizePrice(record[field])]))
    if (priceFields.some(field => prices[field] === undefined)) throw new Error('Invalid current price')
    Object.assign(form, prices, {
      electricRemark: record.electricRemark || '',
      hydrogenRemark: record.hydrogenRemark || '',
      argonRemark: record.argonRemark || ''
    })
    currentEmpty.value = false
  } catch (error) {
    ElMessage.error(t('auxiliary.price.currentLoadError'))
  } finally {
    currentLoading.value = false
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res = await getPriceList({ page: 1, pageSize: 10 })
    priceHistory.value = res.items || []
  } catch (error) {
    ElMessage.error(t('auxiliary.price.historyLoadError'))
  } finally {
    historyLoading.value = false
  }
}

const handleSave = async () => {
  if (!formRef.value || formBusy.value || historyLoading.value) return
  // 校验开始即锁定本次提交，避免异步校验期间重复点击。
  saveLoading.value = true
  try {
    try {
      if (await formRef.value.validate() === false) return
    } catch (error) {
      return
    }
    const snapshot = { ...form }
    for (const field of priceFields) {
      snapshot[field] = normalizePrice(snapshot[field])
      if (snapshot[field] === undefined) {
        ElMessage.error(t('auxiliary.price.invalidPrice'))
        return
      }
    }
    const remarks = []
    if (snapshot.electricRemark) remarks.push(`${t('auxiliary.price.electric')}: ${snapshot.electricRemark}`)
    if (snapshot.hydrogenRemark) remarks.push(`${t('auxiliary.price.hydrogen')}: ${snapshot.hydrogenRemark}`)
    if (snapshot.argonRemark) remarks.push(`${t('auxiliary.price.argon')}: ${snapshot.argonRemark}`)
    await createPrice({
      ...snapshot,
      remark: remarks.length > 0 ? remarks.join('; ') : t('auxiliary.price.priceAdjustment')
    })
    Object.assign(form, snapshot)
    currentEmpty.value = false
    ElMessage.success(t('common.success'))
    // 历史刷新自行反馈错误；成功保存的快照不再被固定 mock 或旧 GET 覆盖。
    await loadHistory()
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    saveLoading.value = false
  }
}

const handleRefresh = async () => {
  if (formBusy.value || historyLoading.value) return
  await Promise.all([loadCurrent(), loadHistory()])
}

onMounted(handleRefresh)
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

.section-title-row {
  margin-bottom: 18px;
}

@media (max-width: 1200px) {
  .price-editor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
