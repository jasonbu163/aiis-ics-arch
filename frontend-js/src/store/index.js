/**
 * 文件路径: /frontend-js/src/store/index.js
 * 功能描述: Pinia 全局 UI 状态
 * 主要功能:
 *   - 应用 UI 状态管理
 *   - 语言设置管理
 *
 * 说明:
 *   - 认证状态统一使用 /frontend-js/src/store/user.js
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import i18n from '@/locales'

export const useAppStore = defineStore('app', () => {
  const collapsed = ref(false)

  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value
  }

  return {
    collapsed,
    toggleCollapsed
  }
})

export const useLocaleStore = defineStore('locale', () => {
  const locale = ref(localStorage.getItem('locale') || 'zh-CN')

  const setLocale = (newLocale) => {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
    // 直接修改 i18n 全局实例的 locale
    if (i18n.global) {
      i18n.global.locale.value = newLocale
    }
  }

  return {
    locale,
    setLocale
  }
})
