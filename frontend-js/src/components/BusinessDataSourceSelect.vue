<!-- 业务来源与设备输入原语；仅更新选择，不访问设备目录或业务API。 -->
<template>
  <div class="business-data-source">
    <el-select :model-value="modelValue.dataSource" :aria-label="t('common.businessDataSource.label')" @update:model-value="changeSource">
      <el-option value="legacy" :label="t('common.businessDataSource.legacy')" />
      <el-option value="http" :label="t('common.businessDataSource.http')" />
    </el-select>
    <el-input v-if="modelValue.dataSource === 'http'" :model-value="modelValue.equipmentId"
      :placeholder="t('common.businessDataSource.equipment')" :aria-label="t('common.businessDataSource.equipment')"
      maxlength="128" clearable @update:model-value="changeEquipment" />
    <span role="status">{{ notice }}</span>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const props = defineProps({ modelValue: { type: Object, required: true } })
const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()
const notice = computed(() => !props.modelValue.valid ? t('common.businessDataSource.invalid')
  : props.modelValue.dataSource === 'legacy' ? t('common.businessDataSource.legacyNotice')
  : !props.modelValue.ready ? t('common.businessDataSource.chooseEquipment') : '')
const changeSource = value => emit('update:modelValue', { ...props.modelValue, dataSource: value })
const changeEquipment = value => emit('update:modelValue', { ...props.modelValue, equipmentId: value })
</script>
<style scoped>
.business-data-source { display:flex; flex-wrap:wrap; gap:12px; align-items:center; padding:16px 24px; }
.business-data-source :deep(.el-select), .business-data-source :deep(.el-input) { width:220px; max-width:100%; }
.business-data-source span { color:var(--text-secondary); font-size:13px; }
@media (max-width:768px) { .business-data-source { padding:16px; } }
</style>
