/** 点位与采集组叶页元数据；业务动作仍由根状态提供。 */
import {Grid} from '@element-plus/icons-vue'
import PointsView from './views/points/index.vue'
import type {ConsoleSectionManifest} from '../../console/types'
export default {id:'points-groups',titleKey:'navigation.pointsGroups',icon:Grid,order:30,component:PointsView} satisfies ConsoleSectionManifest
