<!--
  文件路径: /frontend-next-js/src/app/plan/components/PlanStatusTag.vue
  功能描述: 计划状态标签业务组件
  主要功能:
    - 统一计划状态到 Element Plus 标签类型的映射
    - 通过 i18n 显示计划状态文案
    - 为计划列表与 Dashboard 提供一致状态展示
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
  status: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'default'
  }
})

const { t } = useI18n()

const statusTypeMap = {
  planned: 'info',
  observed: 'success',
  closed: 'info',
  cancelled: 'warning',
  deleted: 'info'
}

const tagType = computed(() => statusTypeMap[props.status] || 'info')

const label = computed(() => {
  if (!props.status) return '-'

  const key = `plan.statusMap.${props.status}`
  const translated = t(key)

  return translated === key ? props.status : translated
})
</script>
