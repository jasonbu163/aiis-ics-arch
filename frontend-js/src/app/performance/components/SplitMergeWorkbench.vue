<!--
  文件路径: /frontend-next-js/src/app/performance/components/SplitMergeWorkbench.vue
  功能描述: F23 r1 工作台残留兼容包装
  主要功能:
    - 保留批准路径下的组件名，避免旧引用断裂
    - 将分/合卷交互迁移到 r2 标准弹窗组件
    - 不再作为 /performance/split 主页面大工作台使用
-->
<template>
  <SplitMergeActionDialog
    v-model="visible"
    :candidates="candidates"
    :summaries="summaries"
    :loading-sources="loadingSources"
    @submitted="emit('submitted', $event)"
    @refresh-sources="emit('refreshSources')"
  />
</template>

<script setup>
import { ref } from 'vue'
import SplitMergeActionDialog from './SplitMergeActionDialog.vue'

defineProps({
  candidates: {
    type: Array,
    default: () => []
  },
  summaries: {
    type: Object,
    default: () => ({})
  },
  loadingSources: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submitted', 'refreshSources'])
const visible = ref(false)

const open = () => {
  visible.value = true
}

defineExpose({ open })
</script>
