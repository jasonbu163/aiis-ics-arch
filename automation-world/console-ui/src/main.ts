/** CU 私有应用启动：安装工作台 i18n，公共 UI 无启动副作用。 */
import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import './ui/styles/index.css'
import './workbench/workbench.css'
import App from './App.vue'
import { i18n } from './locales'
createApp(App).use(i18n).mount('#app')
