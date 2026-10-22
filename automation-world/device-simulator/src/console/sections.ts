/** DAA同类分组叶子，真实DS六页；组件直接引用无远端动态加载。 */
import { Monitor,Setting,Grid,SetUp,DataLine,Document } from '@element-plus/icons-vue'
import Overview from '../app/simulator/views/overview/index.vue'
import Instances from '../app/simulator/views/instances/index.vue'
import Points from '../app/simulator/views/points/index.vue'
import Policies from '../app/simulator/views/policies/index.vue'
import Values from '../app/simulator/views/values/index.vue'
import Logs from '../app/simulator/views/logs/index.vue'
import type { ConsoleSectionManifest } from './types'
export const consoleSections:ConsoleSectionManifest[]=[
  {id:'overview',titleKey:'navigation.overview',icon:Monitor,order:1,component:Overview},
  {id:'instances',titleKey:'navigation.instances',icon:Setting,order:2,component:Instances},
  {id:'points',titleKey:'navigation.points',icon:Grid,order:3,component:Points},
  {id:'policies',titleKey:'navigation.policies',icon:SetUp,order:4,component:Policies},
  {id:'values',titleKey:'navigation.values',icon:DataLine,order:5,component:Values},
  {id:'logs',titleKey:'navigation.logs',icon:Document,order:6,component:Logs}
]
