<!-- 按字段作用域展示单项新增和编辑表单，草稿由字段管理页面管理。 -->
<template>
  <el-form :model="draft" :disabled="disabled" label-position="top" class="shared-field-form" @submit.prevent>
    <section class="field-form-section">
      <h3>{{ tr('dialog.definition') }}</h3>
      <div class="field-form-grid">
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
      </div>
    </section>
    <section v-for="group in groups" :key="group.name" class="field-form-section">
      <div class="field-form-heading">
        <h3>{{ tr('dialog.' + group.name) }}</h3>
        <el-tooltip placement="bottom-start" :trigger="['hover', 'focus']" :trigger-keys="[]">
          <template #content>
            <div class="field-form-help">
              <p v-for="hint in group.hints" :key="hint">{{ tr('fieldHelp.' + hint) }}</p>
            </div>
          </template>
          <el-button link native-type="button" class="field-form-help-trigger"
            :aria-label="tr('fieldHelp.label', { section: tr('dialog.' + group.name) })"
            @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
            <el-icon><QuestionFilled /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
      <div class="field-form-grid">
        <el-form-item v-if="group.name === 'usage' && settings.owners.length" :label="tr('owner')">
          <el-select v-model="draft.performanceOwner" @change="updateFieldOwner(draft)">
            <el-option v-for="owner in settings.owners" :key="owner" :value="owner" :label="tr('owners.' + owner)" />
          </el-select>
        </el-form-item>
        <el-form-item v-for="name in group.switches" :key="name">
          <el-checkbox v-model="draft[name]" :disabled="settingDisabled(draft, name)">
            {{ tr(name) }}
          </el-checkbox>
        </el-form-item>
        <el-form-item v-for="name in group.orders" :key="name" :label="tr(name)">
          <el-input-number v-model="draft[name]" :min="0" :max="65535" :precision="0" :value-on-clear="null" :placeholder="tr('slotDefault')" />
        </el-form-item>
      </div>
    </section>
  </el-form>
</template>

<script setup>
import { QuestionFilled } from '@element-plus/icons-vue'
import { fieldSettings, settingDisabled, updateFieldOwner } from '../../components/fieldSettings'

const props = defineProps({ tr: { type: Function, required: true }, kind: { type: String, default: 'shared' }, isNew: Boolean, disabled: Boolean })
const draft = defineModel({ type: Object, required: true })
const settings = fieldSettings[props.kind]
const groups = [
  {
    name: 'usage',
    switches: settings.switches.filter(name => !/^(plan|performance)/.test(name)),
    hints: [
      'enabled', 'nullable',
      ...(settings.owners.length ? ['manual', 'automated'] : []),
      ...(props.kind === 'shared' ? ['snapshot', 'snapshotAuto', 'writeback'] : [])
    ]
  },
  ...settings.orders.map(order => {
    const module = order === 'planOrder' ? 'plan' : 'performance'
    return { name: module, switches: settings.switches.filter(name => name.startsWith(module)), orders: [order], hints: [module, 'order'] }
  })
]
</script>

<style scoped>
.shared-field-form { display: grid; gap: 12px; }
.field-form-section { min-width: 0; padding: 14px 16px; border: 1px solid var(--border-secondary); border-radius: 12px; }
.field-form-section h3 { margin: 0 0 12px; color: var(--text-primary); font-size: 14px; font-weight: 590; }
.field-form-heading { display: flex; align-items: center; gap: 4px; margin-bottom: 12px; }
.field-form-heading h3 { margin: 0; }
.field-form-help-trigger.el-button { width: 24px; height: 24px; flex: 0 0 auto; font-size: 16px; }
.field-form-help { max-width: min(340px, calc(100vw - 56px)); white-space: normal; overflow-wrap: anywhere; }
.field-form-help p { margin: 0; }
.field-form-help p + p { margin-top: 6px; }
.field-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 16px; }
.field-form-grid :deep(.el-form-item) { min-width: 0; margin-bottom: 0; }
.field-form-grid :deep(.el-form-item__label) { height: auto; line-height: 1.4; white-space: normal; overflow-wrap: anywhere; }
.field-form-grid :deep(.el-input-number), .field-form-grid :deep(.el-select) { width: 100%; }
.field-form-grid :deep(.el-checkbox), .field-form-grid :deep(.el-checkbox__label) { height: auto; white-space: normal; }
@media (max-width: 520px) { .field-form-grid { grid-template-columns: minmax(0, 1fr); } }
</style>
