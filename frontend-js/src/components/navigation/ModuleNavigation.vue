<!-- 文件路径: /frontend-js/src/components/navigation/ModuleNavigation.vue
     功能描述: 通用两级导航渲染；标题响应语言切换，图标未知或缺失时使用 Menu。 -->
<template>
  <el-sub-menu v-for="group in groups" :key="group.name" :index="group.name">
    <template #title>
      <el-icon><component :is="iconFor(group.icon)" /></el-icon>
      <span>{{ $t(group.titleKey) }}</span>
    </template>
    <el-menu-item v-for="leaf in group.children" :key="leaf.name" :index="leaf.path">
      <el-icon><component :is="iconFor(leaf.icon)" /></el-icon>
      <span>{{ $t(leaf.titleKey) }}</span>
    </el-menu-item>
  </el-sub-menu>
</template>

<script setup>
import * as icons from '@element-plus/icons-vue'
import { resolveNavigationIcon } from '@/app/moduleManifest'

defineProps({ groups: { type: Array, required: true } })
const iconFor = name => resolveNavigationIcon(name, icons, icons.Menu)
</script>
