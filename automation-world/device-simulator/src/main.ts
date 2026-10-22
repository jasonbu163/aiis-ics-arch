/** 从冻结DAA装配派生：显式EP组件、公共CU主题和DS i18n；不启动采集链。 */
import { createApp,defineComponent,h } from 'vue'
import { ElAlert,ElButton,ElCheckbox,ElConfigProvider,ElDescriptions,ElDescriptionsItem,ElDialog,ElEmpty,ElForm,ElFormItem,ElInput,ElInputNumber,ElOption,ElPagination,ElSelect,ElSwitch,ElTable,ElTableColumn,ElTag,ElTabs,ElTabPane,ElTree } from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import { i18n } from './locales'
import '@aw-ui-styles'
import './styles/app.css'
const app=createApp(App)
for(const component of [ElAlert,ElButton,ElCheckbox,ElConfigProvider,ElDescriptions,ElDescriptionsItem,ElDialog,ElEmpty,ElForm,ElFormItem,ElInput,ElInputNumber,ElOption,ElSelect,ElSwitch,ElTable,ElTableColumn,ElTag,ElTabs,ElTabPane,ElTree])app.use(component)
app.component('ElPagination',defineComponent({name:'DsPagination',inheritAttrs:false,setup(_,{attrs,slots}){return()=>h(ElPagination,{...attrs,appendSizeTo:'#ds-feedback'},slots)}}))
app.use(i18n).mount('#app')
