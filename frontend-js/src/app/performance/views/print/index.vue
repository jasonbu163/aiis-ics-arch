<!--
  文件路径: /frontend-next-js/src/app/performance/views/print/index.vue
  功能描述: Performance 打印设置页面，配置标签模板并触发浏览器打印预览
  主要功能:
    - 打印模板标题、纸张、方向、边距、字号、缩放和区块配置
    - 普通 HTML/CSS 模板预览
    - 当前模板预览浏览器打印
    - 国际化 (i18n) 支持
    - 日夜模式 (Theme) 适配
-->
<template>
  <div class="performance-print-page page-layout">
    <BaseCard class="print-settings-card" :title="$t('performance.printSettings.title')">
      <div class="print-workspace">
        <section class="settings-block">
          <div class="section-heading">
            <h3>{{ $t('performance.printSettings.templateSettings') }}</h3>
          </div>
          <PrintSettingsPanel v-model="template" />
        </section>

        <section class="preview-block">
          <div class="section-heading">
            <h3>{{ $t('performance.printSettings.templatePreview') }}</h3>
            <ActionButton
              size="small"
              variant="secondary"
              :disabled="!previewLabels.length"
              :loading="printing"
              @click="handlePrintPreviewLabels"
            >
              <el-icon><Printer /></el-icon>
              {{ $t('common.print') }}
            </ActionButton>
          </div>

          <div class="template-preview-shell">
            <PrintTemplateRenderer
              v-if="previewLabels.length"
              :labels="previewLabels"
              :template="normalizedTemplate"
            />
            <el-empty
              v-else
              :description="$t('performance.printSettings.noPreview')"
            />
          </div>
        </section>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Printer } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import PrintSettingsPanel from '@/app/performance/components/PrintSettingsPanel.vue'
import PrintTemplateRenderer from '@/app/performance/components/PrintTemplateRenderer.vue'
import { getPrintData } from '@/app/performance/api'
import { createPerformancePrintDocument } from '@/app/performance/utils/print-document.mjs'
import {
  createPrintPreviewSampleLabel,
  loadStoredPrintTemplate,
  normalizePrintTemplate,
  saveStoredPrintTemplate
} from '@/app/performance/utils/print-template.mjs'

const { t } = useI18n()
const route = useRoute()

const printing = ref(false)
const previewLabels = ref([createPrintPreviewSampleLabel()])
const template = ref(loadStoredPrintTemplate())

const normalizedTemplate = computed(() => normalizePrintTemplate(template.value))

const loadPreviewByPerformanceId = async (performanceId) => {
  try {
    const label = await getPrintData(performanceId)
    previewLabels.value = label ? [label] : [createPrintPreviewSampleLabel()]
  } catch (error) {
    console.error('获取预览数据失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
    previewLabels.value = [createPrintPreviewSampleLabel()]
  }
}

const handlePrintPreviewLabels = async () => {
  if (!previewLabels.value.length) return
  printing.value = true
  try {
    await createPerformancePrintDocument(previewLabels.value, normalizedTemplate.value, t)
  } finally {
    printing.value = false
  }
}

watch(template, (value) => {
  saveStoredPrintTemplate(value)
}, { deep: true })

onMounted(() => {
  const performanceId = Array.isArray(route.query.performanceId)
    ? route.query.performanceId[0]
    : route.query.performanceId

  if (performanceId) {
    loadPreviewByPerformanceId(performanceId)
  }
})
</script>

<style scoped>
.performance-print-page {
  animation: fadeIn var(--transition-normal);
}

.print-settings-card :deep(.base-card__body) {
  padding: 0;
}

.print-settings-card :deep(.base-card__header) {
  min-height: 76px;
}

.print-workspace {
  display: grid;
  grid-template-columns: minmax(360px, 0.75fr) minmax(0, 1.25fr);
  min-height: calc(100vh - 190px);
}

.settings-block,
.preview-block {
  min-width: 0;
}

.settings-block {
  border-right: 1px solid var(--border-secondary);
  padding-bottom: 24px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 58px;
  padding: 0 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.section-heading h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 650;
}

.section-heading span {
  color: var(--text-secondary);
  font-size: 13px;
}

.settings-block :deep(.print-settings-panel) {
  padding: 24px;
}

.preview-block {
  min-height: 0;
}

.template-preview-shell {
  max-height: 760px;
  padding: 24px;
  overflow: auto;
  background: var(--bg-secondary);
}

@media (max-width: 1280px) {
  .print-workspace {
    grid-template-columns: 1fr;
  }

  .settings-block {
    border-right: 0;
    border-bottom: 1px solid var(--border-secondary);
  }
}
</style>
