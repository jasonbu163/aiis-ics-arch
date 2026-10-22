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
      <el-input v-if="modelValue.initial!==null&&modelValue.initial!==undefined" :model-value="initialText" data-testid="policy-initial" @change="setInitial" />
    </el-form-item>
    <div v-if="modelValue.rule" class="ds-form-grid">
      <el-form-item v-if="modelValue.mode==='fixed'" :label="t('simulator.fixedValue')">
        <el-input data-testid="rule-fixed" :model-value="String(modelValue.rule.fixedValue??'')" @change="setFixed" />
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
    <el-alert v-if="invalid" :title="t('simulator.errors.typed_value_invalid')" type="error" :closable="false" />
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Policy, Rule, Json } from '../../../services/deviceSimulator';
const props = defineProps<{
    modelValue: Policy;
    dataType?: string;
}>(), emit = defineEmits<{
    'update:modelValue': [
        value: Policy
    ];
}>(), { t } = useI18n(), invalid = ref(false);
const modes = ['hold', 'fixed', 'ramp', 'sine', 'random', 'toggle'], owners = ['none', 'client', 'ui', 'rule'], flags = ['clientRead', 'clientWrite', 'uiWrite', 'uiMaintenance'] as const;
const initialText = computed(() => String(props.modelValue.initial ?? ''));
function patch(change: Partial<Policy>) { emit('update:modelValue', { ...props.modelValue, ...change }); }
function parse(text: string): Json { if (props.dataType === 'BOOL') {
    if (!['true', 'false', '0', '1'].includes(text))
        throw Error();
    return text === 'true' || text === '1';
} if (props.dataType === 'CHAR' || props.dataType?.startsWith('STRING['))
    return text; const n = Number(text); if (!Number.isFinite(n) || !text.trim())
    throw Error(); return n; }
function setInitial(text: string) { try {
    patch({ initial: parse(text) });
    invalid.value = false;
}
catch {
    invalid.value = true;
} }
function setInitialEnabled(enabled: unknown) { patch({ initial: enabled ? (props.dataType === 'BOOL' ? false : props.dataType === 'CHAR' || props.dataType?.startsWith('STRING[') ? '' : 0) : null }); }
function setFixed(text: string) { try {
    rulePatch({ fixedValue: parse(text) });
    invalid.value = false;
}
catch {
    invalid.value = true;
} }
function rulePatch(change: Partial<Rule>) { if (props.modelValue.rule)
    patch({ rule: { ...props.modelValue.rule, ...change } }); }
function setMode(mode: string) { if (mode === 'inherit') {
    patch({ mode: null });
    return;
} if (mode === 'hold') {
    patch({ mode: 'hold', rule: null, owner: props.modelValue.owner === 'rule' ? 'none' : props.modelValue.owner });
    return;
} patch({ mode: mode as Policy['mode'], owner: 'rule', clientWrite: false, uiWrite: false, uiMaintenance: false, rule: { fixedValue: props.dataType === 'BOOL' ? false : 0, min: 0, max: 1, periodMs: 1000, phase: 0, seed: '', halfPeriodMs: 500, ...props.modelValue.rule, kind: mode as Rule['kind'] } }); }
</script>
