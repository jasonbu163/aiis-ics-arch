/**
 * File Path: /control-agent/src/main.ts
 * Description: Vue application bootstrap for the Control Agent console
 * Main Features:
 *   - Creates the Vue app
 *   - Installs Element Plus for the operations console shell
 *   - Installs the local i18n instance
 *   - Loads global theme and application styles
 */
import { createApp } from 'vue'
import {
  ElAlert,
  ElAside,
  ElButton,
  ElCol,
  ElConfigProvider,
  ElContainer,
  ElDescriptions,
  ElDescriptionsItem,
  ElHeader,
  ElIcon,
  ElMain,
  ElMenu,
  ElMenuItem,
  ElPagination,
  ElRow,
  ElTable,
  ElTableColumn,
  ElTag
} from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import { i18n } from './locales'
import './styles/theme.css'
import './styles/app.css'

const app = createApp(App)

const elementPlusComponents = [
  ElAlert,
  ElAside,
  ElButton,
  ElCol,
  ElConfigProvider,
  ElContainer,
  ElDescriptions,
  ElDescriptionsItem,
  ElHeader,
  ElIcon,
  ElMain,
  ElMenu,
  ElMenuItem,
  ElPagination,
  ElRow,
  ElTable,
  ElTableColumn,
  ElTag
]

for (const component of elementPlusComponents) {
  app.use(component)
}

app.use(i18n).mount('#app')
