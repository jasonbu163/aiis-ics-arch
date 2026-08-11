/**
 * 文件路径: /frontend-js/src/main.js
 * 功能描述: Vue 应用入口文件，初始化应用和全局插件
 * 主要功能:
 *   - 创建 Vue 应用实例
 *   - 注册 Element Plus 组件和图标
 *   - 配置 Pinia 状态管理
 *   - 配置 Vue Router 路由
 *   - 初始化主题系统
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {
  Aim,
  ArrowLeft,
  ArrowUp,
  Box,
  Briefcase,
  Calendar,
  Check,
  Checked,
  CircleCheck,
  Clock,
  Close,
  Coin,
  Collection,
  Connection,
  Cpu,
  DataAnalysis,
  DataBoard,
  DataLine,
  Delete,
  Document,
  Download,
  Edit,
  EditPen,
  Expand,
  Files,
  Finished,
  Flag,
  Fold,
  Folder,
  FullScreen,
  Grid,
  House,
  Lightning,
  List,
  Loading,
  Lock,
  Monitor,
  Moon,
  Notebook,
  Odometer,
  OfficeBuilding,
  Operation,
  Platform,
  Plus,
  PriceTag,
  Printer,
  Promotion,
  Refresh,
  RefreshRight,
  ScaleToOriginal,
  Scissor,
  Search,
  SetUp,
  Setting,
  Stamp,
  Star,
  Sunny,
  Sunrise,
  Switch,
  SwitchButton,
  Tickets,
  Timer,
  Tools,
  TrendCharts,
  Trophy,
  Upload,
  User,
  UserFilled,
  VideoCamera,
  VideoPause,
  VideoPlay,
  View,
  Warning,
  WindPower,
} from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'
import './styles/theme.css'
import i18n from './locales'
import { useThemeStore } from './store/theme'

const app = createApp(App)

const elementPlusIcons = {
  Aim,
  ArrowLeft,
  ArrowUp,
  Box,
  Briefcase,
  Calendar,
  Check,
  Checked,
  CircleCheck,
  Clock,
  Close,
  Coin,
  Collection,
  Connection,
  Cpu,
  DataAnalysis,
  DataBoard,
  DataLine,
  Delete,
  Document,
  Download,
  Edit,
  EditPen,
  Expand,
  Files,
  Finished,
  Flag,
  Fold,
  Folder,
  FullScreen,
  Grid,
  House,
  Lightning,
  List,
  Loading,
  Lock,
  Monitor,
  Moon,
  Notebook,
  Odometer,
  OfficeBuilding,
  Operation,
  Platform,
  Plus,
  PriceTag,
  Printer,
  Promotion,
  Refresh,
  RefreshRight,
  ScaleToOriginal,
  Scissor,
  Search,
  SetUp,
  Setting,
  Stamp,
  Star,
  Sunny,
  Sunrise,
  Switch,
  SwitchButton,
  Tickets,
  Timer,
  Tools,
  TrendCharts,
  Trophy,
  Upload,
  User,
  UserFilled,
  VideoCamera,
  VideoPause,
  VideoPlay,
  View,
  Warning,
  WindPower,
}

for (const [key, component] of Object.entries(elementPlusIcons)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(i18n)

// 初始化主题
const themeStore = useThemeStore()
themeStore.initTheme()
themeStore.listenToSystemTheme()

app.mount('#app')
