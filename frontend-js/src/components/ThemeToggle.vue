<!--
  文件路径: /frontend-js/src/components/ThemeToggle.vue
  功能描述: 主题切换组件 (日间/夜间模式)
  主要功能:
    - 切换日间极简模式和夜间工业模式
    - 持久化主题设置
    - 平滑过渡动画
-->
<template>
  <div
    class="theme-toggle"
    :class="{ 'is-dark': isDark }"
    @click="toggleTheme"
    :title="isDark ? $t('common.switchToLight') : $t('common.switchToDark')"
  >
    <el-icon :size="20">
      <Moon />
    </el-icon>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/store/theme'
import { Moon } from '@element-plus/icons-vue'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: 1px solid var(--border-primary);
  border-radius: 999px;
  background: var(--card-bg);
  color: var(--text-secondary);
  cursor: pointer;
  box-sizing: border-box;
  transition: all var(--transition-normal);
  user-select: none;
}

.theme-toggle:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.theme-toggle.is-dark {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-primary);
}

.theme-toggle.is-dark:hover {
  background: var(--primary-light);
  border-color: var(--primary-light);
  color: var(--text-primary);
}
</style>
