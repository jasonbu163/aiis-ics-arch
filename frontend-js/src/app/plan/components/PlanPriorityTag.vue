<!--
  文件路径: /frontend-js/src/app/plan/components/PlanPriorityTag.vue
  功能描述: 计划优先级标签业务组件
  主要功能:
    - 统一计划优先级到 Element Plus 标签类型的映射
    - 通过 i18n 显示计划优先级文案
    - 为计划列表与看板提供一致优先级展示
-->
<template>
  <el-tag :type="tagType" :size="size">
    {{ label }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  priority: {
    type: [Number, String],
    default: ''
  },
  size: {
    type: String,
    default: 'default'
  }
})

const { t } = useI18n()

const priorityKeyMap = {
  1: 'low',
  5: 'normal',
  8: 'high',
  10: 'urgent'
}

const priorityTypeMap = {
  1: 'info',
  5: 'primary',
  8: 'warning',
  10: 'danger'
}

const normalizedPriority = computed(() => String(props.priority))
const priorityKey = computed(() => priorityKeyMap[normalizedPriority.value])
const tagType = computed(() => priorityTypeMap[normalizedPriority.value] || 'info')

const label = computed(() => {
  if (props.priority === '' || props.priority === null || props.priority === undefined) return '-'
  if (!priorityKey.value) return String(props.priority)

  const key = `plan.priorityMap.${priorityKey.value}`
  const translated = t(key)

  return translated === key ? String(props.priority) : translated
})
</script>
