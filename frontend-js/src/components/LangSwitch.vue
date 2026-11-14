<!--
  文件路径: /frontend-js/src/components/LangSwitch.vue
  功能描述: 语言切换组件
  主要功能:
    - 在圆形按钮内显示目标语言并切换应用语言
    - 持久化语言设置到 localStorage
    - 支持日夜双模式
-->
<template>
  <button
    class="lang-switch"
    type="button"
    :title="switchLabel"
    :aria-label="switchLabel"
    @click="toggleLocale"
  >
    {{ isChinese ? t('language.switchToEnglishShort') : t('language.switchToChineseShort') }}
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '@/store'

const { locale, t } = useI18n()
const localeStore = useLocaleStore()
const isChinese = computed(() => locale.value === 'zh-CN')
const switchLabel = computed(() => isChinese.value
  ? t('language.switchToEnglish')
  : t('language.switchToChinese')
)

const toggleLocale = () => {
  localeStore.setLocale(isChinese.value ? 'en-US' : 'zh-CN')
}
</script>

<style scoped>
.lang-switch {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  width: 44px;
  height: 44px;
  padding: 0;
  box-sizing: border-box;
  font-size: 13px;
  font-weight: 590;
  line-height: 1;
  color: var(--text-secondary);
  background: var(--card-bg);
  border: 1px solid var(--border-primary);
  border-radius: 999px;
  cursor: pointer;
  user-select: none;
}

.lang-switch:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.lang-switch:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 3px;
}
</style>
