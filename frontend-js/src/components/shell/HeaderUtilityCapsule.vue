<!--
  文件路径: /frontend-js/src/components/shell/HeaderUtilityCapsule.vue
  功能描述: 登录前后复用的顶部工具胶囊
  主要功能:
    - 统一展示当前时间、主题切换、全屏切换和语言切换
    - 支持登录页悬浮模式和主布局内联模式
    - 为登录后用户菜单预留插槽
-->
<template>
  <div :class="['header-utility-capsule', `header-utility-capsule--${variant}`]">
    <CurrentTime />
    <ThemeToggle />
    <FullscreenToggle />
    <LangSwitch class="header-utility-lang" />
    <slot />
  </div>
</template>

<script setup>
import CurrentTime from '@/components/CurrentTime.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import FullscreenToggle from '@/components/FullscreenToggle.vue'
import LangSwitch from '@/components/LangSwitch.vue'

defineProps({
  variant: {
    type: String,
    default: 'floating'
  }
})
</script>

<style scoped>
.header-utility-capsule {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.header-utility-capsule--floating {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 10;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--border-primary);
  border-radius: 22px;
  background: var(--header-glass-bg);
  box-shadow: var(--header-glass-shadow);
  backdrop-filter: blur(34px) saturate(1.08);
  -webkit-backdrop-filter: blur(34px) saturate(1.08);
}

.header-utility-capsule--inline {
  gap: 10px;
}

.header-utility-lang {
  margin-right: 2px;
}

@media (max-width: 980px) {
  .header-utility-capsule--floating {
    position: static;
    align-self: flex-end;
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .header-utility-capsule--floating {
    align-self: stretch;
  }

  .header-utility-capsule--inline {
    width: 100%;
    justify-content: space-between;
    gap: 8px;
  }
}
</style>
