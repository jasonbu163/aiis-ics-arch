import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import enUS from './locales/en-US/studio.json'
import zhCN from './locales/zh-CN/studio.json'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'
import './styles.css'

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages: {
    'en-US': enUS,
    'zh-CN': zhCN
  }
})

createApp(App).use(i18n).mount('#app')
