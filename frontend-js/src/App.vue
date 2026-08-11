<!--
  文件路径: /frontend-js/src/App.vue
  功能描述: 应用根组件，提供路由视图容器
  主要功能:
    - 路由视图渲染
    - 全局样式定义
-->
<template>
  <el-config-provider :locale="locale" :message="messageConfig">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

const { locale: i18nLocale } = useI18n()

const locale = computed(() => {
  return i18nLocale.value === 'zh-CN' ? zhCn : en
})

const messageConfig = {
  placement: 'bottom',
  offset: 24
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
}

body {
  font-family: var(--font-sans);
}

#app {
  position: relative;
}
</style>
