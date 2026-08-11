<!--
  文件路径: /frontend-js/src/components/common/BaseCard.vue
  功能描述: 通用卡片容器组件
  主要功能:
    - 统一圆角、边框、背景与暗色模式样式
    - 提供标题区、图标区、操作区和内容区插槽
    - 标题区与内容区使用分隔线形成一致的信息层级
-->
<template>
  <section class="base-card" :class="{ 'base-card--compact': compact }">
    <header v-if="hasHeader" class="base-card__header">
      <div class="base-card__title-wrap">
        <span v-if="$slots.icon" class="base-card__icon">
          <slot name="icon" />
        </span>
        <h3 v-if="title" class="base-card__title">{{ title }}</h3>
        <slot v-else name="title" />
      </div>
      <div v-if="$slots.actions" class="base-card__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="base-card__body" :class="bodyClass">
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  compact: {
    type: Boolean,
    default: false
  },
  bodyClass: {
    type: [String, Array, Object],
    default: ''
  }
})

const slots = useSlots()
const hasHeader = computed(() => props.title || slots.title || slots.icon || slots.actions)
</script>

<style scoped>
.base-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  background: var(--card-bg);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.base-card:hover {
  border-color: var(--border-primary);
  box-shadow: var(--shadow-md);
}

.base-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 68px;
  padding: 0 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.base-card__title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.base-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  color: var(--primary);
}

.base-card__title {
  margin: 0;
  overflow: hidden;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 590;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.base-card__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex: 0 0 auto;
}

.base-card__body {
  flex: 1;
  padding: 24px;
  min-width: 0;
}

.base-card--compact .base-card__header {
  min-height: 56px;
  padding: 0 18px;
}

.base-card--compact .base-card__body {
  padding: 18px;
}

@media (max-width: 768px) {
  .base-card__header {
    min-height: 60px;
    padding: 0 18px;
  }

  .base-card__body {
    padding: 18px;
  }
}
</style>
