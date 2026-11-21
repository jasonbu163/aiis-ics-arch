<!-- 计划和实绩内独立的本地字段入口，与共享页使用同一字段管理实现。 -->
<template>
  <FieldManagement :key="module" :module="module" :scope="module === 'plan' ? 'plan_local' : 'performance_local'" />
</template>

<script setup>
import FieldManagement from '../shared-fields/index.vue'

defineProps({ module: { type: String, required: true } })
</script>
