<!-- 手工/导入点的独立显示名、描述和地址编辑；源结构不冒充手工证明。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.pointEditor')" :append-to-body="false" width="min(760px, calc(100vw - 32px))" :close-on-click-modal="false" @close="cancel">
    <el-form v-if="form" label-position="top" class="ds-form-grid" data-testid="point-editor">
      <el-form-item :label="t('simulator.name')">
        <el-input v-model="form.name" data-testid="point-name" maxlength="100" />
      </el-form-item>
      <el-form-item :label="t('simulator.displayName')">
        <el-input v-model="form.displayName" data-testid="point-legacy-display-name" maxlength="200" />
      </el-form-item>
      <el-form-item :label="t('simulator.displayNameZh')">
        <el-input v-model="displayNameZh" data-testid="point-display-name-zh" />
      </el-form-item>
      <el-form-item :label="t('simulator.displayNameEn')">
        <el-input v-model="displayNameEn" data-testid="point-display-name-en" />
      </el-form-item>
      <el-form-item :label="t('simulator.pointDescription')">
        <el-input v-model="description" data-testid="point-description" type="textarea" />
      </el-form-item>
      <el-form-item :label="t('simulator.dataType')">
        <el-select v-model="kind" data-testid="point-type" :disabled="!form.manual">
          <el-option v-for="type in types" :key="type" :value="type" :label="type" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="kind==='STRING'" :label="t('simulator.stringLength')">
        <el-input-number v-model="stringLength" :min="1" :max="254" :disabled="!form.manual" />
      </el-form-item>
      <el-form-item :label="t('simulator.byte')">
        <el-input-number v-model="form.byte" data-testid="point-byte" :min="0" :max="65535" />
      </el-form-item>
      <el-form-item v-if="kind==='BOOL'" :label="t('simulator.bit')">
        <el-input-number v-model="form.bit" data-testid="point-bit" :min="0" :max="7" />
      </el-form-item>
      <el-form-item :label="t('simulator.manualReason')">
        <el-input v-model="form.manualReason" data-testid="point-reason" maxlength="1000" />
      </el-form-item>
      <el-form-item :label="t('simulator.enabled')">
        <el-switch v-model="form.enabled" />
      </el-form-item>
      <el-alert v-if="invalid" :title="t('simulator.errors.point_parameters')" type="error" :closable="false" />
      <el-alert v-if="invalidMetadata" :title="t('simulator.errors.point_metadata_bytes')" type="error" :closable="false" />
    </el-form>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="point-cancel" @click="cancel" />
      <ConsoleActionButton label-key="simulator.keepChanges" tone="primary" data-testid="point-confirm" @click="commit" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { inject, ref, watch, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Point } from '../../../services/deviceSimulator';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{
    modelValue: boolean;
    point: Point | null;
}>(), emit = defineEmits<{
    'update:modelValue': [
        value: boolean
    ];
    confirm: [
        point: Point
    ];
}>();
const { t } = useI18n(), local = inject(simulatorKey)!, form = ref<Point | null>(null), invalid = ref(false), kind = ref('BOOL'), stringLength = ref(20);
const displayNameZh = ref(''), displayNameEn = ref(''), description = ref(''), invalidMetadata = ref(false);
const types = ['BOOL', 'BYTE', 'USINT', 'CHAR', 'WORD', 'UINT', 'INT', 'DWORD', 'UDINT', 'DINT', 'REAL', 'STRING'];
function cleanup() { local.editing = false; local.finishEditor = null; local.discardEditor = null; }
function cancel() { cleanup(); emit('update:modelValue', false); }
function commit() { if (!form.value) return false;
    const addressChanged = form.value.byte !== props.point?.byte || form.value.bit !== props.point?.bit;
    const originalType = props.point?.dataType ?? '';
    const originalKind = originalType.startsWith('STRING[') ? 'STRING' : originalType;
    const typeChanged = kind.value !== originalKind || (kind.value === 'STRING' && stringLength.value !== Number(originalType.match(/STRING\[(\d+)\]/)?.[1] || 20));
    const addressRequired = addressChanged || typeChanged || (form.value.manual && !props.point?.name);
    if ((!form.value.name && (form.value.manual || props.point?.name)) || (addressRequired && (form.value.byte === null || !form.value.manualReason.trim()))) {
    invalid.value = true;
    return false;
} const bytes = (value: string) => new TextEncoder().encode(value).length;
    invalid.value = false;
    invalidMetadata.value = bytes(displayNameZh.value) > 256 || bytes(displayNameEn.value) > 256 || bytes(description.value) > 500;
    if (invalidMetadata.value) return false;
    if (displayNameZh.value || displayNameEn.value) form.value.displayNames = { 'zh-CN': displayNameZh.value, 'en-US': displayNameEn.value };
    else delete form.value.displayNames;
    if (description.value) form.value.description = description.value;
    else delete form.value.description;
    if (typeChanged) form.value.dataType = kind.value === 'STRING' ? `STRING[${stringLength.value}]` : kind.value;
    if (typeChanged || addressChanged) {
        if (kind.value !== 'BOOL') form.value.bit = null;
        else if (form.value.bit === null) form.value.bit = 0;
    }
    emit('confirm', JSON.parse(JSON.stringify(form.value))); cancel(); return true; }
watch(() => props.modelValue, open => { if (open && props.point) {
    form.value = JSON.parse(JSON.stringify(props.point));
    displayNameZh.value = props.point.displayNames?.['zh-CN'] ?? '';
    displayNameEn.value = props.point.displayNames?.['en-US'] ?? '';
    description.value = props.point.description ?? '';
    kind.value = props.point.dataType.startsWith('STRING[') ? 'STRING' : props.point.dataType;
    stringLength.value = Number(props.point.dataType.match(/STRING\[(\d+)\]/)?.[1] || 20);
    invalid.value = false;
    invalidMetadata.value = false;
    local.editing = true;
    local.finishEditor = commit;
    local.discardEditor = cancel;
}
else
    cleanup(); });
onBeforeUnmount(cleanup);
</script>
