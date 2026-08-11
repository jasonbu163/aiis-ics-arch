<!--
  文件路径: /frontend-js/src/components/LangSwitch.vue
  功能描述: 语言切换组件
  主要功能:
    - 切换应用语言
    - 持久化语言设置到 localStorage
    - 支持日夜双模式
-->
<template>
  <div class="lang-switch" @click="toggleLocale">
    <span class="lang-text" :class="{ active: locale === 'zh-CN' }">中</span>
    <span class="lang-divider">/</span>
    <span class="lang-text" :class="{ active: locale === 'en-US' }">EN</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '@/store'

const { locale } = useI18n()
const localeStore = useLocaleStore()

const toggleLocale = () => {
  const newLocale = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  localeStore.setLocale(newLocale)
}
</script>

<style scoped>
.lang-switch {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  box-sizing: border-box;
  font-size: 13px;
  font-weight: 510;
  gap: 4px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-primary);
  border-radius: 999px;
  cursor: pointer;
  transition: all var(--transition-normal);
  user-select: none;
}

.lang-switch:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
}

.lang-text {
  color: var(--text-tertiary);
  transition: all var(--transition-normal);
  padding: 2px 4px;
  border-radius: 4px;
}

.lang-text.active {
  color: var(--primary);
  font-weight: 590;
}

.lang-divider {
  color: var(--text-muted);
  font-weight: 400;
}

</style>
