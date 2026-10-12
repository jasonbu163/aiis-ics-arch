<!--
  文件路径: /frontend-next-js/src/app/performance/components/TransformModeTabs.vue
  功能描述: 实绩分卷 / 合卷模式切换控件
  主要功能:
    - 提供 split 与 merge 两个稳定模式
    - 通过 v-model 向工作台同步当前 transform 类型
-->
<template>
  <div class="transform-mode-tabs">
    <el-radio-group :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)">
      <el-radio-button value="split">{{ $t('performance.splitWorkbench.modes.split') }}</el-radio-button>
      <el-radio-button value="merge">{{ $t('performance.splitWorkbench.modes.merge') }}</el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
    validator: (value) => ['split', 'merge'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
.transform-mode-tabs {
  display: flex;
  align-items: center;
  min-width: 0;
}
</style>
