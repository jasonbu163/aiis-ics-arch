<!-- 逐属性层级覆盖编辑；继承为null，不把默认开关伪装成显式授权。 -->
<template>
  <div class="console-stack" data-testid="policy-editor">
    <div class="ds-form-grid">
      <el-form-item :label="t('simulator.mode')">
        <el-select :model-value="modelValue.mode||'inherit'" data-testid="policy-mode" @update:model-value="setMode">
          <el-option value="inherit" :label="t('simulator.inherit')" />
          <el-option v-for="mode in modes" :key="mode" :value="mode" :label="t('simulator.modes.'+mode)" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('simulator.owner')">
        <el-select :model-value="modelValue.owner||'inherit'" data-testid="policy-owner" @update:model-value="patch({owner:$event==='inherit'?null:$event})">
          <el-option value="inherit" :label="t('simulator.inherit')" />
          <el-option v-for="owner in owners" :key="owner" :value="owner" :label="t('simulator.owners.'+owner)" />
        </el-select>
      </el-form-item>
      <el-form-item v-for="field in flags" :key="field" :label="t('simulator.'+field)">
        <el-select :model-value="modelValue[field]===null||modelValue[field]===undefined?'inherit':String(modelValue[field])" :data-testid="'policy-'+field" @update:model-value="patch({[field]:$event==='inherit'?null:$event==='true'})">
          <el-option value="inherit" :label="t('simulator.inherit')" />
          <el-option value="true" :label="t('simulator.allow')" />
          <el-option value="false" :label="t('simulator.deny')" />
        </el-select>
      </el-form-item>
    </div>
    <el-form-item :label="t('simulator.initial')">
      <el-checkbox data-testid="policy-initial-override" :model-value="modelValue.initial!==null&&modelValue.initial!==undefined" @update:model-value="setInitialEnabled">{{ t('simulator.override') }}</el-checkbox>
      <el-input v-if="modelValue.initial!==null&&modelValue.initial!==undefined" :model-value="initialText" data-testid="policy-initial" @update:model-value="setInitial" />
    </el-form-item>
    <div v-if="modelValue.rule" class="ds-form-grid">
      <el-form-item v-if="modelValue.mode==='fixed'" :label="t('simulator.fixedValue')">
        <el-input data-testid="rule-fixed" :model-value="fixedText" @update:model-value="setFixed" />
      </el-form-item>
      <template v-else>
        <el-form-item :label="t('simulator.minimum')">
          <el-input-number data-testid="rule-min" :model-value="modelValue.rule.min" @update:model-value="rulePatch({min:Number($event)})" />
        </el-form-item>
        <el-form-item :label="t('simulator.maximum')">
          <el-input-number data-testid="rule-max" :model-value="modelValue.rule.max" @update:model-value="rulePatch({max:Number($event)})" />
        </el-form-item>
        <el-form-item :label="t('simulator.periodMs')">
          <el-input-number data-testid="rule-periodMs" :model-value="modelValue.rule.periodMs" :min="100" @update:model-value="rulePatch({periodMs:Number($event)})" />
        </el-form-item>
        <el-form-item :label="t('simulator.phase')">
          <el-input-number data-testid="rule-phase" :model-value="modelValue.rule.phase" @update:model-value="rulePatch({phase:Number($event)})" />
        </el-form-item>
        <el-form-item v-if="modelValue.mode==='random'" :label="t('simulator.seed')">
          <el-input :model-value="modelValue.rule.seed" maxlength="100" @update:model-value="rulePatch({seed:$event})" />
        </el-form-item>
        <el-form-item v-if="modelValue.mode==='toggle'" :label="t('simulator.halfPeriodMs')">
          <el-input-number data-testid="rule-halfPeriodMs" :model-value="modelValue.rule.halfPeriodMs" :min="100" @update:model-value="rulePatch({halfPeriodMs:Number($event)})" />
        </el-form-item>
      </template>
    </div>
    <el-alert :title="t('simulator.editing.modeLinkHint')" type="info" :closable="false" />
    <el-alert v-if="invalid" :title="t('simulator.errors.typed_value_invalid')" type="error" :closable="false" />
  </div>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Policy, Rule } from '../../../services/deviceSimulator';
import { defaultScalar, modeChange, parseScalar } from '../policyEditing';
const props = defineProps<{ modelValue: Policy; dataType?: string }>();
const emit = defineEmits<{ 'update:modelValue': [value: Policy]; validity: [valid: boolean] }>();
const { t } = useI18n();
const modes = ['hold', 'fixed', 'ramp', 'sine', 'random', 'toggle'], owners = ['none', 'client', 'ui', 'rule'], flags = ['clientRead', 'clientWrite', 'uiWrite', 'uiMaintenance'] as const;
let lastInitial: unknown = undefined, lastFixed: unknown = undefined;
const initialText = ref(''), fixedText = ref(''), initialInvalid = ref(false), fixedInvalid = ref(false);
const invalid = computed(() => initialInvalid.value || fixedInvalid.value);
watch(() => props.modelValue.initial, value => { if (!Object.is(value,lastInitial)) { initialText.value = String(value ?? ''); initialInvalid.value = false; } }, { immediate: true });
watch(() => props.modelValue.rule?.fixedValue, value => { if (!Object.is(value,lastFixed)) { fixedText.value = String(value ?? ''); fixedInvalid.value = false; } }, { immediate: true });
watch(invalid, value => emit('validity', !value), { immediate: true, flush: 'sync' });
function patch(change: Partial<Policy>) { emit('update:modelValue', { ...props.modelValue, ...change }); }
function setInitial(text: string) {
    initialText.value = text;
    try { const value = parseScalar(props.dataType, text); initialInvalid.value = false; lastInitial=value; patch({ initial: value }); }
    catch { initialInvalid.value = true; }
}
function setFixed(text: string) {
    fixedText.value = text;
    try { const value = parseScalar(props.dataType, text); fixedInvalid.value = false; lastFixed=value; rulePatch({ fixedValue: value }); }
    catch { fixedInvalid.value = true; }
}
function setInitialEnabled(enabled: unknown) {
    initialInvalid.value = false;
    const value=enabled ? defaultScalar(props.dataType || 'INT') : null;
    lastInitial=undefined;initialText.value=String(value??'');patch({ initial:value });
}
function rulePatch(change: Partial<Rule>) { if (props.modelValue.rule) patch({ rule: { ...props.modelValue.rule, ...change } }); }
function setMode(mode: string) {
    fixedInvalid.value = false;
    patch(mode === 'inherit' ? { mode: null } : modeChange(mode as NonNullable<Policy['mode']>, props.dataType));
}
</script>
