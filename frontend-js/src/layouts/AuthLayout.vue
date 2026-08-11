<!--
  文件路径: /frontend-js/src/layouts/AuthLayout.vue
  功能描述: 未登录状态应用壳层
  主要功能:
    - 承载登录前页面内容
    - 显示未登录顶部工具胶囊
    - 保持登录页背景与装饰布局
-->
<template>
  <div class="auth-layout">
    <HeaderUtilityCapsule />

    <main class="auth-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <div class="decoration decoration-1"></div>
    <div class="decoration decoration-2"></div>
    <div class="decoration decoration-3"></div>
  </div>
</template>

<script setup>
import HeaderUtilityCapsule from '@/components/shell/HeaderUtilityCapsule.vue'
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background:
    radial-gradient(circle at top left, rgba(113, 112, 255, 0.14), transparent 34%),
    radial-gradient(circle at bottom right, rgba(94, 106, 210, 0.12), transparent 32%),
    var(--bg-primary);
  position: relative;
  overflow: hidden;
}

.auth-content {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  justify-content: center;
}

.decoration {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(90px);
}

.decoration-1 {
  width: 320px;
  height: 320px;
  top: -80px;
  left: -60px;
  background: rgba(94, 106, 210, 0.16);
}

.decoration-2 {
  width: 220px;
  height: 220px;
  bottom: -70px;
  right: 8%;
  background: rgba(113, 112, 255, 0.1);
}

.decoration-3 {
  width: 180px;
  height: 180px;
  top: 30%;
  right: -40px;
  background: rgba(39, 166, 68, 0.08);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 980px) {
  .auth-layout {
    flex-direction: column;
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .auth-layout {
    align-items: stretch;
    justify-content: flex-start;
    padding: 16px;
  }

  .auth-content {
    display: block;
  }

  .decoration-1,
  .decoration-2,
  .decoration-3 {
    display: none;
  }
}
</style>
