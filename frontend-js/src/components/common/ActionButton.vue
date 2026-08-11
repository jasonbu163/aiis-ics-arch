<!--
  文件路径: /frontend-js/src/components/common/ActionButton.vue
  功能描述: 通用操作按钮组件，统一页面级、卡片级与表格行内按钮语义
  主要功能:
    - 提供 primary / secondary / refresh / row / danger / success / warning 语义
    - 统一大按钮与小按钮两档尺寸
    - 避免页面重复定义按钮高度、圆角、间距与字号
-->
<template>
  <el-button v-bind="$attrs" :type="elementType" :class="buttonClass">
    <slot />
  </el-button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'secondary',
    validator: (value) => ['primary', 'secondary', 'refresh', 'row', 'danger', 'success', 'warning'].includes(value)
  },
  size: {
    type: String,
    default: 'large',
    validator: (value) => ['large', 'small'].includes(value)
  }
})

const elementType = computed(() => {
  if (props.variant === 'primary' || props.variant === 'row') return 'primary'
  if (['danger', 'success', 'warning'].includes(props.variant)) return props.variant
  return undefined
})

const resolvedSize = computed(() => {
  if (props.variant === 'row') return 'small'
  return props.size
})

const buttonClass = computed(() => ['action-button', `action-button--${props.variant}`, `action-button--${resolvedSize.value}`])
</script>
