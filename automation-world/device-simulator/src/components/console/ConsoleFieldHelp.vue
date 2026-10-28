<!-- 字段旁问号提示：悬停或键盘聚焦查看解释，复用Element Plus与主题token。 -->
<template>
  <ElTooltip :content="text" placement="top" popper-class="ds-help-tooltip" :show-after="150" :trigger="['hover', 'focus']">
    <button type="button" class="ds-field-help" :aria-label="t('simulator.helpFor', {field: label})">
      <ElIcon><QuestionFilled /></ElIcon>
    </button>
  </ElTooltip>
</template>
<script setup lang="ts">
import { ElIcon, ElTooltip } from 'element-plus';
import { QuestionFilled } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
defineProps<{ label: string; text: string }>();
const { t } = useI18n();
</script>
