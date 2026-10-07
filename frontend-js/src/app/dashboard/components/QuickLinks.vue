<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/QuickLinks.vue
  功能描述: Dashboard 快捷入口组件
  主要功能:
    - 展示常用功能快捷入口
    - 支持点击跳转
    - 支持日夜模式适配
    - 支持国际化（英文键名翻译）
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.quickLinks')">
    <div class="quick-links">
      <div class="quick-link-item" v-for="link in translatedQuickLinks" :key="link.nameKey" @click="$router.push(link.path)">
        <div class="link-icon-wrapper" :style="{ background: link.bgColor }">
          <el-icon :size="24"><component :is="link.icon" /></el-icon>
        </div>
        <span>{{ link.name }}</span>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()

const props = defineProps({
  quickLinks: {
    type: Array,
    required: true,
    default: () => []
  }
})

// 将英文键名翻译成当前语言
const translatedQuickLinks = computed(() => {
  return props.quickLinks.map(link => ({
    ...link,
    name: t(`dashboard.quickLinkItems.${link.nameKey}`)
  }))
})
</script>

<style scoped>
.quick-links { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; }

.quick-link-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.quick-link-item:hover { background: rgba(255, 255, 255, 0.05); transform: translateY(-3px); border-color: var(--border-primary); box-shadow: var(--shadow-md); }

.link-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: var(--bg-primary);
  margin-bottom: 8px;
}

.quick-link-item span { font-size: 13px; color: var(--text-secondary); font-weight: 510; text-align: center; }

@media (max-width: 1400px) { .quick-links { grid-template-columns: repeat(3, 1fr); } }

@media (max-width: 768px) {
  .quick-links { grid-template-columns: repeat(2, 1fr); }
}

[data-theme="dark"] .quick-link-item:hover { box-shadow: 0 24px 48px rgba(0, 0, 0, 0.28); }
</style>
