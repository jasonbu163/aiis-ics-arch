/** 消费端自己创建 Vue/i18n；只导入公共代码、样式和自有应用。 */
import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import 'element-plus/dist/index.css'
import '@aw-ui-styles'
import App from './App.vue'
import en from './locales/en-US.json'
import zh from './locales/zh-CN.json'
const i18n = createI18n({ legacy: false, locale: 'en-US', fallbackLocale: 'en-US', messages: { 'en-US': en, 'zh-CN': zh } })
createApp(App).use(i18n).mount('#app')
