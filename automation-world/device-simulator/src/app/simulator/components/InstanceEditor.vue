<!-- DS实例编辑沿DAA弹层/表单范式；取消不保存，后端仍复核全部参数。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.instanceEditor')" :append-to-body="false" width="min(680px, calc(100vw - 32px))" :close-on-click-modal="false" @close="cancel">
    <el-form v-if="form" label-position="top" data-testid="instance-editor" class="ds-form-grid">
      <el-form-item :label="t('simulator.name')">
        <el-input v-model="form.name" data-testid="instance-name" maxlength="100" />
      </el-form-item>
      <el-form-item :label="t('simulator.host')">
        <el-input v-model="form.host" data-testid="instance-host" />
      </el-form-item>
      <el-form-item :label="t('simulator.port')">
        <el-input-number v-model="form.port" data-testid="instance-port" :min="1" :max="65535" />
      </el-form-item>
      <el-form-item :label="t('simulator.rack')">
        <el-input-number v-model="form.rack" :min="0" :max="7" />
      </el-form-item>
      <el-form-item :label="t('simulator.slot')">
        <el-input-number v-model="form.slot" :min="0" :max="31" />
      </el-form-item>
      <el-form-item :label="t('simulator.callingTsap')">
        <el-input-number v-model="form.callingTsap" :min="0" :max="65535" />
      </el-form-item>
      <el-form-item :label="t('simulator.maxConnections')">
        <el-input-number v-model="form.maxConnections" :min="1" :max="64" />
      </el-form-item>
      <el-form-item :label="t('simulator.maxHandshakes')">
        <el-input-number v-model="form.maxHandshakes" :min="1" :max="16" />
      </el-form-item>
      <el-alert v-if="invalid" :title="t('simulator.errors.instance_parameters')" type="error" :closable="false" />
    </el-form>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="instance-cancel" @click="cancel" />
      <ConsoleActionButton label-key="simulator.keepChanges" tone="primary" data-testid="instance-confirm" @click="commit" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { inject, ref, watch, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Instance } from '../../../services/deviceSimulator';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{
    modelValue: boolean;
    instance: Instance | null;
}>();
const emit = defineEmits<{
    'update:modelValue': [
        value: boolean
    ];
    confirm: [
        instance: Instance
    ];
}>();
const { t } = useI18n(), local = inject(simulatorKey)!, form = ref<Instance | null>(null), invalid = ref(false);
function cleanup() { local.editing = false; local.finishEditor = null; local.discardEditor = null; }
function cancel() { cleanup(); emit('update:modelValue', false); }
function commit() { if (!form.value || !form.value.name.trim() || !/^127\.(\d{1,3}\.){2}\d{1,3}$/.test(form.value.host)) {
    invalid.value = true;
    return false;
} emit('confirm', JSON.parse(JSON.stringify(form.value))); cancel(); return true; }
watch(() => props.modelValue, open => { if (open && props.instance) {
    form.value = JSON.parse(JSON.stringify(props.instance));
    invalid.value = false;
    local.editing = true;
    local.finishEditor = commit;
    local.discardEditor = cancel;
}
else
    cleanup(); });
onBeforeUnmount(cleanup);
</script>
