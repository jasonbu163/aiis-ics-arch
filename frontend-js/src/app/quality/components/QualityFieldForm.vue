<!-- 质量字段定义表单。已定义字段的键、类型和单位固定。 -->
<template>
  <div class="quality-field-form">
    <section class="dialog-section">
      <h3 class="dialog-section__title">{{ label('definition') }}</h3>
      <dl v-if="readonly" class="dialog-form-grid">
        <div v-for="row in definitionRows" :key="row.key">
          <dt>{{ label(row.key) }}</dt><dd>{{ row.value || label('emptyValue') }}</dd>
        </div>
      </dl>
      <div v-else class="dialog-form-grid">
        <el-form-item :label="label('name')">
          <el-input v-model="field.name" :disabled="disabled || !isNew" maxlength="64" />
        </el-form-item>
        <el-form-item :label="label('type')">
          <el-select v-model="field.type" :disabled="disabled || !isNew">
            <el-option v-for="type in types" :key="type" :value="type" :label="label(type)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="label('labelZh')">
          <el-input v-model="field.labels['zh-CN']" :disabled="disabled" maxlength="128" />
        </el-form-item>
        <el-form-item :label="label('labelEn')">
          <el-input v-model="field.labels['en-US']" :disabled="disabled" maxlength="128" />
        </el-form-item>
        <el-form-item v-if="field.type === 'link'" :label="label('linkText')">
          <el-input v-model="field.linkText" :disabled="disabled" :placeholder="label('linkPlaceholder')" maxlength="128" />
        </el-form-item>
        <el-form-item :label="label('unit')">
          <el-input v-model="field.unit" :disabled="disabled || !isNew" maxlength="64" />
        </el-form-item>
      </div>
    </section>
    <section class="dialog-section">
      <h3 class="dialog-section__title">{{ label('usage') }}</h3>
      <dl v-if="readonly" class="dialog-form-grid">
        <div v-for="key in toggles" :key="key">
          <dt>{{ label(key) }}</dt><dd>{{ label(field[key] ? 'yes' : 'no') }}</dd>
        </div>
        <div><dt>{{ label('order') }}</dt><dd>{{ field.order }}</dd></div>
      </dl>
      <div v-else class="dialog-form-grid">
        <el-form-item v-for="key in toggles" :key="key">
          <el-checkbox v-model="field[key]" :disabled="disabled">{{ label(key) }}</el-checkbox>
        </el-form-item>
        <el-form-item :label="label('order')">
          <el-input-number v-model="field.order" :disabled="disabled" :min="0" :max="65535" :precision="0" />
        </el-form-item>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const field = defineModel({ type: Object, required: true })
defineProps({ isNew: Boolean, disabled: Boolean, readonly: Boolean })
const { t } = useI18n()
const label = key => t(`quality.localFields.${key}`)
const types = ['string', 'number', 'boolean', 'link']
const toggles = ['enabled', 'visible', 'editable', 'isNullable']
const definitionRows = computed(() => [
  { key: 'name', value: field.value.name },
  { key: 'type', value: label(field.value.type) },
  { key: 'labelZh', value: field.value.labels['zh-CN'] },
  { key: 'labelEn', value: field.value.labels['en-US'] },
  ...(field.value.type === 'link' ? [{ key: 'linkText', value: field.value.linkText }] : []),
  { key: 'unit', value: field.value.unit }
])
</script>
