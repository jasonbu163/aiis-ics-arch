/**
 * File Path: /automation-world/data-acquisition-agent/src/main.ts
 * Description: Vue application bootstrap for the Data Acquisition Agent console
 * Main Features:
 *   - Creates the Vue app
 *   - Installs Element Plus for the operations console shell
 *   - Installs the local i18n instance
 *   - Loads CU public styles before host page layouts
 */
import { createApp, defineComponent, h } from 'vue'
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
import { initializeBootstrap } from './services/localAcquisition'
import { i18n } from './locales'
import '@aw-ui-styles'
import './styles/app.css'

async function mountConsole() {
await initializeBootstrap()
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
  ElRow,
  ElTable,
  ElTableColumn,
  ElTag
]

for (const component of elementPlusComponents) {
  app.use(component)
}

// 旧 TableShell 仍用原分页合同；只将 sizes 弹层放入宿主显式主题容器。
app.component('ElPagination', defineComponent({
  name: 'DaaPagination',
  inheritAttrs: false,
  setup(_, { attrs, slots }) {
    return () => h(ElPagination, { ...attrs, appendSizeTo: '#daa-feedback' }, slots)
  }
}))

app.use(i18n).mount('#app')

}
void mountConsole().catch(() => { const root=document.getElementById('app');if(root)root.textContent=i18n.global.t('common.local.bootstrapFailed') })
