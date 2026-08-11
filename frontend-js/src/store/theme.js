/**
 * 文件路径: /frontend-js/src/store/theme.js
 * 功能描述: 主题状态管理
 * 主要功能:
 *   - 管理日间/夜间主题状态
 *   - 持久化主题设置
 *   - 动态切换 CSS 变量
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const savedTheme = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const isDark = ref(savedTheme ? savedTheme === 'dark' : prefersDark)
  const theme = computed(() => isDark.value ? 'dark' : 'light')

  const lightTheme = {
    '--bg-primary': '#f5f6f8',
    '--bg-secondary': '#edeff3',
    '--bg-tertiary': '#e6e9ef',
    '--bg-elevated': 'rgba(255, 255, 255, 0.9)',
    '--bg-overlay': 'rgba(255, 255, 255, 0.72)',
    '--bg-panel': 'rgba(255, 255, 255, 0.84)',
    '--bg-glow': 'radial-gradient(circle at top left, rgba(94, 106, 210, 0.18), transparent 40%)',
    '--text-primary': '#14171f',
    '--text-secondary': '#4e5562',
    '--text-tertiary': '#707887',
    '--text-muted': '#97a0af',
    '--text-inverse': '#f7f8f8',
    '--border-primary': 'rgba(17, 24, 39, 0.08)',
    '--border-secondary': 'rgba(17, 24, 39, 0.05)',
    '--border-strong': 'rgba(17, 24, 39, 0.12)',
    '--primary': '#5e6ad2',
    '--primary-light': '#717dff',
    '--primary-dark': '#4956bd',
    '--primary-subtle': 'rgba(94, 106, 210, 0.12)',
    '--success': '#27a644',
    '--warning': '#d97706',
    '--danger': '#dc2626',
    '--info': '#4f46e5',
    '--chart-area-strong': 'rgba(94, 106, 210, 0.28)',
    '--chart-area-weak': 'rgba(94, 106, 210, 0.08)',
    '--shadow-sm': '0 1px 2px rgba(15, 23, 42, 0.05)',
    '--shadow-md': '0 18px 40px rgba(15, 23, 42, 0.06)',
    '--shadow-lg': '0 24px 60px rgba(15, 23, 42, 0.12)',
    '--shadow-xl': '0 32px 80px rgba(15, 23, 42, 0.16)',
    '--shadow-card': '0 1px 0 rgba(255, 255, 255, 0.8) inset, 0 24px 50px rgba(15, 23, 42, 0.06)',
    '--card-bg': 'rgba(255, 255, 255, 0.8)',
    '--card-border': 'rgba(17, 24, 39, 0.08)',
    '--card-radius': '20px',
    '--sidebar-bg': 'rgba(255, 255, 255, 0.76)',
    '--sidebar-text': '#5b6270',
    '--sidebar-active': '#202430',
    '--sidebar-active-bg': 'rgba(17, 24, 39, 0.06)',
    '--header-bg': 'rgba(255, 255, 255, 0.68)',
    '--header-border': 'rgba(17, 24, 39, 0.07)',
    '--brand-logo-glow-light': 'rgba(255, 255, 255, 0.72)',
    '--brand-logo-glow-high-light': 'rgba(255, 255, 255, 0.92)',
    '--brand-logo-glow-accent': 'rgba(94, 106, 210, 0.18)',
    '--brand-logo-glow-none': 'transparent',
    '--brand-logo-glow-display': 'none',
  }

  const darkTheme = {
    '--bg-primary': '#08090a',
    '--bg-secondary': '#0f1011',
    '--bg-tertiary': '#161719',
    '--bg-elevated': 'rgba(25, 26, 27, 0.88)',
    '--bg-overlay': 'rgba(15, 16, 17, 0.7)',
    '--bg-panel': 'rgba(15, 16, 17, 0.88)',
    '--bg-glow': 'radial-gradient(circle at top left, rgba(113, 112, 255, 0.16), transparent 38%)',
    '--text-primary': '#f7f8f8',
    '--text-secondary': '#cfd4dc',
    '--text-tertiary': '#8a8f98',
    '--text-muted': '#62666d',
    '--text-inverse': '#08090a',
    '--border-primary': 'rgba(255, 255, 255, 0.08)',
    '--border-secondary': 'rgba(255, 255, 255, 0.05)',
    '--border-strong': 'rgba(255, 255, 255, 0.14)',
    '--primary': '#7170ff',
    '--primary-light': '#828fff',
    '--primary-dark': '#5e6ad2',
    '--primary-subtle': 'rgba(113, 112, 255, 0.14)',
    '--success': '#27a644',
    '--warning': '#d1a14a',
    '--danger': '#ef4444',
    '--info': '#7170ff',
    '--chart-area-strong': 'rgba(113, 112, 255, 0.32)',
    '--chart-area-weak': 'rgba(113, 112, 255, 0.1)',
    '--shadow-sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
    '--shadow-md': '0 18px 48px rgba(0, 0, 0, 0.32)',
    '--shadow-lg': '0 32px 80px rgba(0, 0, 0, 0.42)',
    '--shadow-xl': '0 48px 120px rgba(0, 0, 0, 0.52)',
    '--shadow-card': '0 0 0 1px rgba(255, 255, 255, 0.02) inset, 0 32px 70px rgba(0, 0, 0, 0.4)',
    '--card-bg': 'rgba(255, 255, 255, 0.03)',
    '--card-border': 'rgba(255, 255, 255, 0.08)',
    '--card-radius': '20px',
    '--sidebar-bg': 'rgba(15, 16, 17, 0.82)',
    '--sidebar-text': '#8a8f98',
    '--sidebar-active': '#f7f8f8',
    '--sidebar-active-bg': 'rgba(255, 255, 255, 0.05)',
    '--header-bg': 'rgba(15, 16, 17, 0.68)',
    '--header-border': 'rgba(255, 255, 255, 0.06)',
    '--brand-logo-glow-light': 'rgba(255, 255, 255, 0.64)',
    '--brand-logo-glow-high-light': 'rgba(255, 255, 255, 0.92)',
    '--brand-logo-glow-accent': 'rgba(113, 112, 255, 0.16)',
    '--brand-logo-glow-none': 'transparent',
    '--brand-logo-glow-display': 'grid',
  }

  const applyTheme = (dark) => {
    const root = document.documentElement
    const themeTokens = dark ? darkTheme : lightTheme
    
    Object.entries(themeTokens).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })
    
    root.setAttribute('data-theme', dark ? 'dark' : 'light')
    root.style.setProperty('color-scheme', dark ? 'dark' : 'light')
  }

  // 切换主题
  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    applyTheme(isDark.value)
  }

  // 设置主题
  const setTheme = (dark) => {
    isDark.value = dark
    localStorage.setItem('theme', dark ? 'dark' : 'light')
    applyTheme(dark)
  }

  // 初始化主题
  const initTheme = () => {
    applyTheme(isDark.value)
  }

  const listenToSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        setTheme(e.matches)
      }
    })
  }

  return {
    isDark,
    theme,
    toggleTheme,
    setTheme,
    initTheme,
    listenToSystemTheme,
  }
})
