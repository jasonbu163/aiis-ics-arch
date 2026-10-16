<!-- CU 私有有限方案编辑：同屏预览、显式草稿与仅源码开发态固定公共样式应用。 -->
<template>
  <Teleport to="body">
    <div id="cu-color-overlays" class="aw-ui cu-color-overlays" :data-aw-theme="theme" :style="previewVariables"></div>
  </Teleport>
  <ConsoleCard class="design-profile-editor" :title="t('workbench.designProfile.title')">
    <p class="workbench-preview-note">{{ t('workbench.designProfile.note') }}</p>
    <ElForm label-position="top" :disabled="sharedPending" @submit.prevent>
      <ElFormItem :label="t('workbench.designProfile.mode', { mode: t(`workbench.${theme}`) })">
        <ElRadioGroup :model-value="theme" :aria-label="t('workbench.designProfile.chooseMode')" @update:model-value="emit('update:theme', $event as UiTheme)">
          <ElRadioButton v-for="palette in palettes" :key="palette" :value="palette">{{ t(`workbench.${palette}`) }}</ElRadioButton>
        </ElRadioGroup>
      </ElFormItem>
      <fieldset class="design-profile-palette">
        <legend>{{ t(`workbench.${theme}`) }}</legend>
        <ElFormItem v-for="field in PALETTE_FIELDS" :key="field" :label="t(`workbench.designProfile.fields.${field}`)" :error="validation.error === `themes.${theme}.${field}` ? t('workbench.designProfile.colorInvalid') : undefined">
          <div class="design-profile-color-row">
            <span class="design-profile-swatch" :style="{ backgroundColor: validProfile.themes[theme][field] }" aria-hidden="true"></span>
            <ElColorPicker :model-value="modelValue.themes[theme][field]" color-format="hex" :show-alpha="false" :aria-label="t('workbench.designProfile.pickColor', { field: t(`workbench.designProfile.fields.${field}`) })" append-to="#cu-color-overlays" popper-class="cu-color-picker-popup" @update:model-value="updateColor(theme, field, $event || '')" @active-change="$event && updateColor(theme, field, $event)" />
            <ElInput :model-value="modelValue.themes[theme][field]" :aria-label="`${t(`workbench.${theme}`)} ${t(`workbench.designProfile.fields.${field}`)} HEX`" @update:model-value="updateColor(theme, field, $event)" />
          </div>
          <small class="design-profile-color-help">{{ t(`workbench.designProfile.uses.${field}`) }}</small>
        </ElFormItem>
      </fieldset>
      <div class="design-profile-shared">
        <ElFormItem v-for="(range, field) in NUMBER_FIELDS" :key="field" :label="`${t(`workbench.designProfile.fields.${field}`)} (${range[0]}–${range[1]} px)`">
          <ElInputNumber :model-value="modelValue.shared[field]" :min="range[0]" :max="range[1]" :step="1" :precision="0" :aria-label="t(`workbench.designProfile.fields.${field}`)" @update:model-value="updateNumber(field, $event)" />
        </ElFormItem>
        <ElFormItem :label="t('workbench.designProfile.fields.tableDensity')">
          <ElSelect :model-value="modelValue.shared.tableDensity" :teleported="false" :aria-label="t('workbench.designProfile.fields.tableDensity')" @update:model-value="updateDensity">
            <ElOption v-for="value in densities" :key="value" :value="value" :label="t(`workbench.pageSamples.${value}`)" />
          </ElSelect>
        </ElFormItem>
      </div>
    </ElForm>
    <p v-if="validation.error" class="design-profile-error" role="alert">{{ t('workbench.designProfile.invalid', { field: errorLabel }) }}</p>
    <div class="aw-form-actions design-profile-actions">
      <ConsoleActionButton :disabled="!!validation.error || sharedPending" :label="t('workbench.designProfile.save')" @click="saveDraft" />
      <ConsoleActionButton :disabled="sharedPending" :label="t('workbench.designProfile.restore')" @click="restoreDraft" />
      <ConsoleActionButton :disabled="sharedPending" :label="t('workbench.designProfile.reset')" @click="resetDefault" />
      <ConsoleActionButton tone="primary" :disabled="!!validation.error || sharedPending" :label="t('workbench.designProfile.export')" @click="exportJSON" />
    </div>
    <p class="workbench-preview-note">{{ t('workbench.designProfile.sharedNote') }}</p>
    <ConsoleActionButton tone="primary" :disabled="!!validation.error || sharedPending || !sharedAvailable" :label="t(sharedPending ? 'workbench.designProfile.shared.applyingLabel' : 'workbench.designProfile.shared.apply')" @click="applyShared(modelValue)" />
    <p v-if="sharedResult" role="status" aria-live="polite" class="workbench-preview-note">{{ t(`workbench.designProfile.shared.${sharedResult}`) }}</p>
    <p v-if="feedback" role="status" class="workbench-preview-note">{{ t(`workbench.designProfile.${feedback}`) }}</p>
    <template v-if="exported">
      <p class="workbench-preview-note">{{ t('workbench.designProfile.exportNote') }}</p>
      <ElInput type="textarea" :rows="8" :model-value="exported" readonly :aria-label="t('workbench.designProfile.exportText')" />
    </template>
  </ConsoleCard>
</template>
<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElRadioGroup, ElRadioButton, ElColorPicker } from 'element-plus'
import { ConsoleCard, ConsoleActionButton, type UiTheme } from '../ui'
import defaults from '../ui/styles/design-profile.json'
import { useSharedDesignProfile } from './useSharedDesignProfile'
import { normalizeProfile, profileJSON, PALETTE_FIELDS, NUMBER_FIELDS, type DesignProfile, type PaletteField, type NumberField } from '../ui/design-profile.js'
const props = defineProps<{ modelValue: DesignProfile; theme: UiTheme; validProfile: DesignProfile; previewVariables: Record<string, string> }>()
const emit = defineEmits<{ 'update:modelValue': [value: DesignProfile]; 'update:theme': [value: UiTheme] }>()
const { t } = useI18n()
const { pending: sharedPending, available: sharedAvailable, result: sharedResult, applyShared } = useSharedDesignProfile(defaults)
const palettes = ['light', 'dark'] as const
const densities = ['standard', 'compact'] as const
const draftKey = 'cu.design-profile.draft.v1'
const feedback = ref('')
const exported = ref('')
const validation = computed(() => {
  try { return { value: normalizeProfile(props.modelValue), error: '' } }
  catch (error) { return { value: undefined, error: error instanceof Error ? error.message : 'profile' } }
})
const errorLabel = computed(() => {
  const parts = validation.value.error.split('.')
  return parts[0] === 'themes' ? `${t(`workbench.${parts[1]}`)} · ${t(`workbench.designProfile.fields.${parts[2]}`)}` : parts[0] === 'shared' ? t(`workbench.designProfile.fields.${parts[1]}`) : validation.value.error
})
watch(() => props.modelValue, () => { exported.value = ''; feedback.value = '' }, { deep: true })
function updateColor(palette: 'light' | 'dark', field: PaletteField, value: string) {
  emit('update:modelValue', { ...props.modelValue, themes: { ...props.modelValue.themes, [palette]: { ...props.modelValue.themes[palette], [field]: value } } })
}
function updateNumber(field: NumberField, value: number | undefined) {
  emit('update:modelValue', { ...props.modelValue, shared: { ...props.modelValue.shared, [field]: value ?? NaN } })
}
function updateDensity(value: 'standard' | 'compact') {
  emit('update:modelValue', { ...props.modelValue, shared: { ...props.modelValue.shared, tableDensity: value } })
}
function saveDraft() {
  if (!validation.value.value) return
  try { localStorage.setItem(draftKey, profileJSON(validation.value.value)); feedback.value = 'saved' }
  catch { feedback.value = 'storageFailed' }
}
// 父级更新后的下一轮不应抹去显式恢复/重置反馈。
async function apply(value: DesignProfile, message: string) {
  emit('update:modelValue', value)
  await nextTick()
  feedback.value = message
}
function restoreDraft() {
  let raw: string | null
  try { raw = localStorage.getItem(draftKey) }
  catch { void apply(normalizeProfile(defaults), 'storageFailed'); return }
  if (raw === null) { void apply(normalizeProfile(defaults), 'missing'); return }
  try { void apply(normalizeProfile(JSON.parse(raw)), 'restored') }
  catch { void apply(normalizeProfile(defaults), 'badDraft') }
}
function resetDefault() {
  let message = 'resetDone'
  try { localStorage.removeItem(draftKey) } catch { message = 'storageFailed' }
  void apply(normalizeProfile(defaults), message)
}
function exportJSON() {
  if (!validation.value.value) return
  exported.value = profileJSON(validation.value.value)
  feedback.value = 'exported'
}
</script>
