<!--
  文件路径: /frontend-js/src/components/CurrentTime.vue
  功能描述: 当前时间显示组件
  主要功能:
    - 实时显示当前日期时间
    - 支持日夜模式适配
    - 自动每秒更新
-->
<template>
  <div class="current-time">{{ formattedTime }}</div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const currentTime = ref(new Date())
let timeTimer = null

// 根据当前语言格式化时间
const formattedTime = computed(() => {
  const date = currentTime.value
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  
  // 根据语言选择不同的日期格式
  if (locale.value === 'zh-CN') {
    return date.toLocaleString('zh-CN', options)
  } else {
    return date.toLocaleString('en-US', options)
  }
})

const updateTime = () => {
  currentTime.value = new Date()
}

onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
})
</script>

<style scoped>
.current-time {
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: center;
  height: 44px;
  box-sizing: border-box;
  font-size: 12px;
  font-weight: 510;
  color: var(--text-secondary);
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 999px;
  border: 1px solid var(--border-primary);
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
  transition: all var(--transition-normal);
}
</style>
