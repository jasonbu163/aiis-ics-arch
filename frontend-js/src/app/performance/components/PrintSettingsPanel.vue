<!--
  文件路径: /frontend-next-js/src/app/performance/components/PrintSettingsPanel.vue
  功能描述: Performance 打印模板设置面板
  主要功能:
    - 设置纸张、方向、边距、字号和缩放
    - 设置标签区块显示开关
    - 国际化 (i18n) 支持
-->
<template>
  <div class="print-settings-panel">
    <section class="settings-section">
      <h3>{{ $t('performance.printSettings.layout') }}</h3>
      <div class="settings-grid">
        <el-form-item class="setting-field-wide" :label="$t('performance.printSettings.labelTitle')">
          <el-input
            :model-value="template.title"
            :maxlength="40"
            clearable
            :placeholder="$t('performance.common.productionLabel')"
            @update:model-value="updateField('title', $event)"
          />
        </el-form-item>

        <el-form-item :label="$t('performance.printSettings.paper')">
          <el-select
            :model-value="template.paper"
            @update:model-value="updateField('paper', $event)"
          >
            <el-option
              v-for="option in paperOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('performance.printSettings.orientation')">
          <el-radio-group
            :model-value="template.orientation"
            @update:model-value="updateField('orientation', $event)"
          >
            <el-radio-button label="portrait">{{ $t('performance.printSettings.portrait') }}</el-radio-button>
            <el-radio-button label="landscape">{{ $t('performance.printSettings.landscape') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('performance.printSettings.fontSize')">
          <el-input-number
            :model-value="template.fontSize"
            :min="9"
            :max="18"
            :step="1"
            @update:model-value="updateField('fontSize', $event)"
          />
        </el-form-item>

        <el-form-item :label="$t('performance.printSettings.scale')">
          <el-slider
            :model-value="template.scale"
            :min="70"
            :max="130"
            :step="5"
            show-input
            @update:model-value="updateField('scale', $event)"
          />
        </el-form-item>
      </div>
    </section>

    <section class="settings-section">
      <h3>{{ $t('performance.printSettings.margin') }}</h3>
      <div class="margin-grid">
        <el-form-item
          v-for="item in marginItems"
          :key="item.key"
          :label="item.label"
        >
          <el-input-number
            :model-value="template.margin[item.key]"
            :min="0"
            :max="50"
            :step="1"
            @update:model-value="updateMargin(item.key, $event)"
          />
        </el-form-item>
      </div>
    </section>

    <section class="settings-section">
      <h3>{{ $t('performance.printSettings.appearance') }}</h3>
      <el-form-item class="appearance-switch" :label="$t('performance.printSettings.enhancedStyle')">
        <el-switch
          :model-value="template.appearance.enhanced"
          @update:model-value="updateAppearance('enhanced', $event)"
        />
      </el-form-item>
    </section>

    <section class="settings-section">
      <h3>{{ $t('performance.printSettings.sections') }}</h3>
      <div class="section-switches">
        <el-checkbox
          v-for="section in sectionOptions"
          :key="section.key"
          :model-value="template.sections[section.key]"
          @update:model-value="updateSection(section.key, $event)"
        >
          {{ section.label }}
        </el-checkbox>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  PRINT_SECTION_KEYS,
  getSectionTitle,
  normalizePrintTemplate
} from '@/app/performance/utils/print-template.mjs'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const template = computed(() => normalizePrintTemplate(props.modelValue))

const paperOptions = computed(() => [
  { label: 'A4', value: 'A4' },
  { label: 'A5', value: 'A5' },
  { label: t('performance.printSettings.labelPaper'), value: 'label' }
])

const marginItems = computed(() => [
  { key: 'top', label: t('performance.printSettings.marginTop') },
  { key: 'right', label: t('performance.printSettings.marginRight') },
  { key: 'bottom', label: t('performance.printSettings.marginBottom') },
  { key: 'left', label: t('performance.printSettings.marginLeft') }
])

const sectionOptions = computed(() => PRINT_SECTION_KEYS.map(sectionKey => ({
  key: sectionKey,
  label: getSectionTitle(sectionKey, t)
})))

const emitTemplate = (nextTemplate) => {
  emit('update:modelValue', normalizePrintTemplate(nextTemplate))
}

const updateField = (key, value) => {
  emitTemplate({
    ...template.value,
    [key]: value
  })
}

const updateMargin = (key, value) => {
  emitTemplate({
    ...template.value,
    margin: {
      ...template.value.margin,
      [key]: value
    }
  })
}

const updateAppearance = (key, value) => {
  emitTemplate({
    ...template.value,
    appearance: {
      ...template.value.appearance,
      [key]: Boolean(value)
    }
  })
}

const updateSection = (key, value) => {
  emitTemplate({
    ...template.value,
    sections: {
      ...template.value.sections,
      [key]: Boolean(value)
    }
  })
}
</script>

<style scoped>
.print-settings-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.settings-section h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 650;
}

.settings-grid,
.margin-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.settings-grid :deep(.el-form-item),
.margin-grid :deep(.el-form-item) {
  margin-bottom: 0;
}

.settings-grid :deep(.el-slider) {
  width: 100%;
}

.setting-field-wide {
  grid-column: 1 / -1;
}

.section-switches {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 14px;
}

.section-switches :deep(.el-checkbox) {
  margin-right: 0;
}

.appearance-switch {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .settings-grid,
  .margin-grid,
  .section-switches {
    grid-template-columns: 1fr;
  }
}
</style>
