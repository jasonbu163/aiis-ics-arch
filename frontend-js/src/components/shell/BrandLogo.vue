<!--
  文件路径: /frontend-js/src/components/shell/BrandLogo.vue
  功能描述: 使用 i18n 文本渲染公开 Core 标识，不携带项目 Logo 资产。
-->
<template>
  <span :class="['brand-logo-shell', 'brand-logo-shell--' + variant]">
    <span class="brand-logo-text">{{ $t('common.systemTitle') }}</span>
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'shell'
  }
})
</script>

<style scoped>
.brand-logo-shell {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: var(--text-primary);
  text-align: center;
}

.brand-logo-text {
  max-width: 100%;
  overflow: hidden;
  color: inherit;
  font-size: clamp(0.8rem, 1.8vw, 1.2rem);
  font-weight: 650;
  letter-spacing: -0.02em;
  line-height: 1.15;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-logo-shell--hero .brand-logo-text {
  font-size: clamp(1.25rem, 2.5vw, 2rem);
}
</style>
