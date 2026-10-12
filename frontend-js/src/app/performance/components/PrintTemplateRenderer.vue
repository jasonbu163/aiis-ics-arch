<!--
  文件路径: /frontend-next-js/src/app/performance/components/PrintTemplateRenderer.vue
  功能描述: Performance 打印模板普通 HTML 预览 renderer
  主要功能:
    - 按模板 schema 渲染标签主体
    - 支持单条和多条标签预览
    - 使用普通 HTML table/div 结构
    - 国际化 (i18n) 支持
-->
<template>
  <div
    class="print-template-renderer"
    :style="rendererStyle"
  >
    <article
      v-for="(label, index) in safeLabels"
      :key="label.id || label.coilNo || index"
      class="template-label-page"
      :class="{ 'template-label-page--enhanced': normalizedTemplate.appearance.enhanced }"
    >
      <header class="template-label-header">
        <h2>{{ templateTitle }}</h2>
        <div>{{ $t('performance.common.labelNo') }}: {{ label.coilNo || '-' }}</div>
      </header>

      <section
        v-for="sectionKey in visibleSections"
        :key="sectionKey"
        class="template-label-section"
      >
        <h3>{{ getSectionTitle(sectionKey, t) }}</h3>

        <table v-if="sectionKey === 'quality'" class="template-quality-table">
          <thead>
            <tr>
              <th>{{ $t('performance.quality.inspectItems') }}</th>
              <th>{{ $t('performance.quality.standard') }}</th>
              <th>{{ $t('performance.quality.actual') }}</th>
              <th>{{ $t('performance.quality.result') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in qualityRows" :key="row.item">
              <td>{{ row.item }}</td>
              <td>{{ row.standard }}</td>
              <td>{{ row.actual }}</td>
              <td>{{ row.result }}</td>
            </tr>
          </tbody>
        </table>

        <div v-else class="template-field-grid">
          <div
            v-for="field in getPrintFields(label, t)[sectionKey]"
            :key="field.label"
            class="template-field"
          >
            <span class="template-field-label">{{ field.label }}</span>
            <span class="template-field-value">{{ field.value }}</span>
          </div>
        </div>
      </section>

      <footer class="template-label-footer">
        <span>{{ $t('performance.common.printTime') }}: {{ currentPrintTime }}</span>
        <span>{{ $t('performance.common.operatorSign') }}: ________________</span>
      </footer>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  PRINT_SECTION_KEYS,
  getPrintFields,
  getPrintTemplateTitle,
  getQualityRows,
  getSectionTitle,
  normalizePrintTemplate
} from '@/app/performance/utils/print-template.mjs'

const props = defineProps({
  labels: {
    type: Array,
    default: () => []
  },
  template: {
    type: Object,
    default: () => ({})
  }
})

const { t } = useI18n()

const normalizedTemplate = computed(() => normalizePrintTemplate(props.template))
const safeLabels = computed(() => props.labels.filter(Boolean))
const qualityRows = computed(() => getQualityRows(t))
const currentPrintTime = computed(() => new Date().toLocaleString())
const templateTitle = computed(() => getPrintTemplateTitle(normalizedTemplate.value, t))

const visibleSections = computed(() => PRINT_SECTION_KEYS.filter(
  sectionKey => normalizedTemplate.value.sections[sectionKey]
))

const rendererStyle = computed(() => ({
  '--template-font-size': `${normalizedTemplate.value.fontSize}px`,
  '--template-scale': normalizedTemplate.value.scale / 100
}))
</script>

<style scoped>
.print-template-renderer {
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #000000;
  font-family: Arial, "Microsoft YaHei", sans-serif;
  font-size: var(--template-font-size);
  line-height: 1.45;
}

.template-label-page {
  width: 100%;
  padding: 24px;
  border: 1px solid #000000;
  background: #ffffff;
  transform: scale(var(--template-scale));
  transform-origin: top left;
}

.template-label-page--enhanced {
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}

.template-label-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #000000;
  text-align: center;
}

.template-label-header h2 {
  margin: 0;
  font-size: 1.6em;
  line-height: 1.2;
}

.template-label-section {
  padding-top: 16px;
}

.template-label-section h3 {
  margin: 0 0 10px;
  font-size: 1.15em;
}

.template-field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  border-top: 1px solid #000000;
  border-left: 1px solid #000000;
}

.template-field {
  display: grid;
  grid-template-columns: 40% 60%;
  min-height: 32px;
  border-right: 1px solid #000000;
  border-bottom: 1px solid #000000;
}

.template-field-label,
.template-field-value {
  padding: 8px;
  overflow-wrap: anywhere;
}

.template-field-label {
  border-right: 1px solid #000000;
  font-weight: 700;
}

.template-label-page--enhanced .template-field-label,
.template-label-page--enhanced .template-quality-table th {
  background: #f5f5f5;
  font-weight: 700;
}

.template-quality-table {
  width: 100%;
  border-collapse: collapse;
}

.template-quality-table th,
.template-quality-table td {
  border: 1px solid #000000;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

.template-label-footer {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #000000;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .template-field-grid {
    grid-template-columns: 1fr;
  }

  .template-label-footer {
    flex-direction: column;
    white-space: normal;
  }
}
</style>
