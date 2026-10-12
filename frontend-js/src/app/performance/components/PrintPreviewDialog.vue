<!--
  文件路径: /frontend-next-js/src/app/performance/components/PrintPreviewDialog.vue
  功能描述: Performance 模块共享打印预览弹窗，统一标签预览与浏览器打印输出
  主要功能:
    - 展示生产标签预览
    - 提供质量检查表
    - 将实际打印内容隔离为生产标签主体
    - 国际化 (i18n) 支持
-->
<template>
  <el-dialog
    v-model="visible"
    :title="$t('performance.common.printPreview')"
    width="880px"
    class="print-dialog"
    modal-class="performance-dialog-mask"
    destroy-on-close
  >
    <div class="print-preview" ref="printArea">
      <header class="label-header">
        <h2>{{ $t('performance.common.productionLabel') }}</h2>
        <div class="label-no">{{ $t('performance.common.labelNo') }}: {{ currentLabel.coilNo || '-' }}</div>
      </header>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.quality.basicInfo') }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('performance.coilNo')">{{ currentLabel.coilNo || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.grade')">{{ currentLabel.grade || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.weight')">{{ formatValue(currentLabel.weight, 'common.unit.ton', 4) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.thickness')">{{ formatValue(currentLabel.thickness, 'common.unit.mm', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.width')">{{ formatValue(currentLabel.width, 'common.unit.mm', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.totalLength')">{{ formatValue(currentLabel.totalLength, 'common.unit.m', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.diameter')">{{ formatValue(currentLabel.outerDiameter, 'common.unit.mm', 2) }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.common.productionRecord') }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('performance.common.operator')">{{ currentLabel.operator || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.shift')">{{ formatShift(currentLabel.shift) }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.tensionCurve') }}</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item :label="$t('performance.common.entryTension')">{{ formatValue(currentLabel.entryTension, 'performance.units.kN', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.entryLoopTension')">{{ formatValue(currentLabel.entryLoopTension, 'performance.units.kN', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.furnaceTension')">{{ formatValue(currentLabel.furnaceTension, 'performance.units.kN', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.exitLoopTension')">{{ formatValue(currentLabel.exitLoopTension, 'performance.units.kN', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.exitTension')" :span="2">{{ formatValue(currentLabel.exitTension, 'performance.units.kN', 2) }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.speedCurve') }}</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item :label="$t('performance.common.entrySpeed')">{{ formatValue(currentLabel.entrySpeed, 'common.unit.speed', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.furnaceSpeed')">{{ formatValue(currentLabel.furnaceSpeed, 'common.unit.speed', 2) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.exitSpeed')">{{ formatValue(currentLabel.exitSpeed, 'common.unit.speed', 2) }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.common.processParams') }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('performance.common.furnaceTemp')">{{ formatTemperature(currentLabel.furnaceTemp) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.table.duration')">{{ formatValue(currentLabel.residenceTime, 'common.unit.min', 0) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.dewPoint')">{{ formatValue(currentLabel.dewPoint, 'performance.units.celsius', 0) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.oxygenContent')">{{ currentLabel.oxygenContent || '-' }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <section class="label-section">
        <h3 class="label-section-title">{{ $t('performance.quality.inspectItems') }}</h3>
        <el-table :data="qualityData" border size="small" class="quality-table">
          <el-table-column prop="item" :label="$t('performance.quality.inspectItems')" />
          <el-table-column prop="standard" :label="$t('performance.quality.standard')" />
          <el-table-column prop="actual" :label="$t('performance.quality.actual')" />
          <el-table-column :label="$t('performance.quality.result')">
            <template #default="{ row }">
              <el-tag :type="row.result === 'qualified' ? 'success' : 'danger'" size="small">
                {{ $t(`performance.printQuality.results.${row.result}`) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <footer class="label-footer">
        <span>{{ $t('performance.common.printTime') }}: {{ currentPrintTime }}</span>
        <span>{{ $t('performance.common.operatorSign') }}: ________________</span>
      </footer>
    </div>

    <template #footer>
      <div class="vibe-dialog-footer">
        <ActionButton @click="visible = false">{{ $t('common.close') }}</ActionButton>
        <ActionButton variant="primary" @click="handleConfirmPrint">
          <el-icon><Printer /></el-icon>
          {{ $t('common.print') }}
        </ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Printer } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: Object,
    default: () => ({})
  },
  printTime: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const printArea = ref()
let printNode = null
let cleanupTimer = null

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const currentLabel = computed(() => props.label || {})

const formatDateTime = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

const currentPrintTime = computed(() => props.printTime || formatDateTime(new Date()))

const qualityData = computed(() => [
  {
    item: t('performance.printQuality.surfaceQuality'),
    standard: t('performance.printQuality.noDefect'),
    actual: t('performance.printQuality.noDefect'),
    result: 'qualified'
  },
  {
    item: t('performance.printQuality.thicknessDeviation'),
    standard: t('performance.printQuality.thicknessStandard'),
    actual: t('performance.printQuality.thicknessActual'),
    result: 'qualified'
  },
  {
    item: t('performance.printQuality.widthDeviation'),
    standard: t('performance.printQuality.widthStandard'),
    actual: t('performance.printQuality.widthActual'),
    result: 'qualified'
  },
  {
    item: t('performance.printQuality.flatness'),
    standard: t('performance.printQuality.flatnessStandard'),
    actual: t('performance.printQuality.flatnessActual'),
    result: 'qualified'
  }
])

const formatNumber = (value, precision = 2) => {
  if (value === null || value === undefined || value === '') return '-'
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return '-'
  return numberValue.toFixed(precision)
}

const formatValue = (value, unitKey, precision = 2) => {
  const formatted = formatNumber(value, precision)
  if (formatted === '-') return '-'
  return `${formatted} ${t(unitKey)}`
}

const formatShift = (value) => {
  if (!value) return '-'
  const shiftMap = {
    dayShift: 'performance.common.dayShift',
    middleShift: 'performance.common.middleShift',
    nightShift: 'performance.common.nightShift',
    白班: 'performance.common.dayShift',
    中班: 'performance.common.middleShift',
    夜班: 'performance.common.nightShift'
  }
  return t(shiftMap[value] || value)
}

const formatTemperature = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  return `${value}${t('performance.units.celsius')}`
}

const cleanupPrintNode = () => {
  if (cleanupTimer) {
    window.clearTimeout(cleanupTimer)
    cleanupTimer = null
  }
  window.removeEventListener('afterprint', cleanupPrintNode)
  printNode?.remove()
  printNode = null
  document.body.classList.remove('performance-printing')
}

const handleConfirmPrint = async () => {
  await nextTick()

  if (!printArea.value) return

  cleanupPrintNode()
  printNode = printArea.value.cloneNode(true)
  printNode.classList.add('performance-print-only')
  document.body.appendChild(printNode)
  document.body.classList.add('performance-printing')
  window.addEventListener('afterprint', cleanupPrintNode, { once: true })
  window.print()
  cleanupTimer = window.setTimeout(cleanupPrintNode, 1000)
}

onBeforeUnmount(() => {
  cleanupPrintNode()
})
</script>

<style scoped>
:global(.print-dialog.el-dialog) {
  overflow: hidden;
  background: var(--table-fixed-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
}

:global(.print-dialog .el-dialog__header) {
  min-height: 72px;
  margin: 0;
  padding: 0 32px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-secondary);
  background: var(--table-fixed-bg);
}

:global(.print-dialog .el-dialog__title) {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 650;
}

:global(.print-dialog .el-dialog__headerbtn) {
  top: 18px;
  right: 24px;
}

:global(.print-dialog .el-dialog__body) {
  max-height: min(70vh, 780px);
  padding: 28px 32px;
  overflow: auto;
  background: var(--table-fixed-bg);
}

:global(.print-dialog .el-dialog__footer) {
  padding: 18px 32px;
  border-top: 1px solid var(--border-secondary);
  background: var(--table-fixed-bg);
}

:global(.performance-dialog-mask) {
  background-color: var(--el-mask-color);
}

:global(.performance-print-only) {
  display: none;
}

.print-preview {
  padding: 28px;
  border: 1px solid var(--border-secondary);
  border-radius: calc(var(--card-radius) - 8px);
  background: var(--table-fixed-bg);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.label-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-secondary);
  text-align: center;
}

.label-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.25;
}

.label-no {
  color: var(--text-secondary);
  font-size: 14px;
}

.label-section {
  padding-top: 22px;
}

.label-section-title {
  margin: 0 0 14px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 650;
}

.print-preview :deep(.el-descriptions__body),
.print-preview :deep(.el-descriptions__label),
.print-preview :deep(.el-descriptions__content),
.quality-table :deep(.el-table__cell) {
  background: var(--table-fixed-bg) !important;
  color: var(--text-primary);
}

.print-preview :deep(.el-descriptions__label) {
  color: var(--text-secondary);
  font-weight: 560;
}

.quality-table {
  width: 100%;
}

.label-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--border-secondary);
  color: var(--text-secondary);
  font-size: 14px;
}

@media (max-width: 768px) {
  :global(.print-dialog.el-dialog) {
    width: calc(100vw - 24px) !important;
  }

  .label-footer {
    flex-direction: column;
  }
}

@media print {
  :global(body.performance-printing) {
    background: #ffffff !important;
  }

  :global(body.performance-printing *) {
    visibility: hidden !important;
  }

  :global(body.performance-printing .performance-print-only),
  :global(body.performance-printing .performance-print-only *) {
    visibility: visible !important;
  }

  :global(body.performance-printing .performance-print-only) {
    display: block !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: auto !important;
    margin: 0 !important;
    padding: 20px !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #ffffff !important;
    color: #000000 !important;
    page-break-inside: avoid !important;
  }

  :global(body.performance-printing .performance-print-only .label-header),
  :global(body.performance-printing .performance-print-only .label-section),
  :global(body.performance-printing .performance-print-only .label-footer),
  :global(body.performance-printing .performance-print-only .label-header h2),
  :global(body.performance-printing .performance-print-only .label-no),
  :global(body.performance-printing .performance-print-only .label-section-title) {
    color: #000000 !important;
  }

  :global(body.performance-printing .performance-print-only .label-header),
  :global(body.performance-printing .performance-print-only .label-footer) {
    border-color: #000000 !important;
  }

  :global(body.performance-printing .performance-print-only .label-footer) {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
  }

  :global(body.performance-printing .performance-print-only .label-footer span) {
    display: inline-block !important;
    white-space: nowrap !important;
  }

  :global(body.performance-printing .performance-print-only .el-table),
  :global(body.performance-printing .performance-print-only .el-table__inner-wrapper),
  :global(body.performance-printing .performance-print-only .el-table__header),
  :global(body.performance-printing .performance-print-only .el-table__body) {
    width: 100% !important;
    border-collapse: collapse !important;
    background: #ffffff !important;
    color: #000000 !important;
  }

  :global(body.performance-printing .performance-print-only .el-table__cell),
  :global(body.performance-printing .performance-print-only .el-table th.el-table__cell),
  :global(body.performance-printing .performance-print-only .el-descriptions__cell) {
    border: 1px solid #000000 !important;
    padding: 8px !important;
    background: #ffffff !important;
    color: #000000 !important;
  }

  :global(body.performance-printing .performance-print-only .el-tag) {
    border-color: #000000 !important;
    background: #ffffff !important;
    color: #000000 !important;
  }

  @page {
    size: A4;
    margin: 10mm;
  }
}
</style>
