<!-- 按字段作用域展示单项新增和编辑表单，草稿由字段管理页面管理。 -->
<template>
  <el-form :model="draft" :disabled="disabled" label-position="top" class="shared-field-form" @submit.prevent>
    <el-form-item :label="tr('fieldName')"><el-input v-model="draft.name" :disabled="!isNew" maxlength="64" /></el-form-item>
    <el-form-item :label="tr('slot')"><el-input-number v-model="draft.slotNo" :min="1" :max="100" :precision="0" :disabled="!isNew" /></el-form-item>
    <el-form-item :label="tr('type')">
      <el-select v-model="draft.type" :disabled="!isNew">
        <el-option v-for="type in ['string','number','boolean']" :key="type" :value="type" :label="tr('types.' + type)" />
      </el-select>
    </el-form-item>
    <el-form-item :label="tr('labelZh')"><el-input v-model="draft.labels['zh-CN']" maxlength="128" /></el-form-item>
    <el-form-item :label="tr('labelEn')"><el-input v-model="draft.labels['en-US']" maxlength="128" /></el-form-item>
    <el-form-item :label="tr('unit')"><el-input v-model="draft.unit" :disabled="!isNew" maxlength="32" /></el-form-item>
    <el-form-item v-if="settings.owners.length" :label="tr('owner')">
      <el-select v-model="draft.performanceOwner" @change="updateFieldOwner(draft)">
        <el-option v-for="owner in settings.owners" :key="owner" :value="owner" :label="tr('owners.' + owner)" />
      </el-select>
    </el-form-item>
    <el-form-item v-for="name in settings.switches" :key="name">
      <el-checkbox v-model="draft[name]" :disabled="settingDisabled(draft, name)">
        {{ tr(name) }}
      </el-checkbox>
    </el-form-item>
    <el-form-item v-for="name in settings.orders" :key="name" :label="tr(name)">
      <el-input-number v-model="draft[name]" :min="0" :max="65535" :precision="0" :value-on-clear="null" :placeholder="tr('slotDefault')" />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { fieldSettings, settingDisabled, updateFieldOwner } from '../../components/fieldSettings'

const props = defineProps({ tr: { type: Function, required: true }, kind: { type: String, default: 'shared' }, isNew: Boolean, disabled: Boolean })
const draft = defineModel({ type: Object, required: true })
const settings = fieldSettings[props.kind]
</script>

<style scoped>
.shared-field-form { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px 12px; }
.shared-field-form :deep(.el-form-item) { min-width: 0; margin-bottom: 0; }
.shared-field-form :deep(.el-input-number) { width: 100%; }
@media (max-width: 680px) { .shared-field-form { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 420px) { .shared-field-form { grid-template-columns: minmax(0, 1fr); } }
</style>
