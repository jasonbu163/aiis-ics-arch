<!--
  文件路径: /frontend-js/src/components/FullscreenToggle.vue
  功能描述: 全屏切换组件
  主要功能:
    - 切换浏览器全屏模式
    - 监听全屏状态变化
    - 支持日夜双模式
-->
<template>
  <div class="fullscreen-toggle" @click="toggleFullscreen">
    <el-icon :size="20">
      <FullScreen v-if="!isFullscreen" />
      <Aim v-else />
    </el-icon>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { FullScreen, Aim } from '@element-plus/icons-vue'

const isFullscreen = ref(false)

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch((err) => {
      console.error(`Error attempting to enable fullscreen: ${err.message}`)
    })
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.fullscreen-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-primary);
  border-radius: 999px;
  cursor: pointer;
  box-sizing: border-box;
  transition: all var(--transition-normal);
  color: var(--text-secondary);
}

.fullscreen-toggle:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--border-strong);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
</style>
