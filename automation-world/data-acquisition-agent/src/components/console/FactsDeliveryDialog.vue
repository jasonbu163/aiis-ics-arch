<!-- 上传设置、接入材料与投递弹窗；GET 读取结果和失败原因在当前弹窗显示。 -->
<template>
  <ElDialog v-if="local" :model-value="!!local.deliveryDialog" :title="t('common.delivery.' + titleKey)" class="daa-delivery-dialog" :class="{ 'daa-delivery-settings-dialog': local.deliveryDialog === 'settings' }" width="min(900px, 94vw)" append-to="#daa-feedback" :close-on-click-modal="false" @update:model-value="value => { if (!value) local!.deliveryDialog = null }">
    <template v-if="local.deliveryDialog === 'settings' && draft">
      <ElForm label-position="top" class="daa-local-form-grid" @submit.prevent>
        <ElFormItem :label="t('common.delivery.serverAddress')"><ElInput v-model="origin" :maxlength="2048" placeholder="http://127.0.0.1:8000" /></ElFormItem>
        <ElFormItem :label="t('common.delivery.path')"><ElInput v-model="draft.path" :maxlength="2048" /></ElFormItem>
        <ElFormItem :label="t('common.delivery.interval')"><ElInputNumber v-model="draft.intervalSeconds" :min="1" :max="3600" :precision="0" /></ElFormItem>
      </ElForm>
      <p class="daa-capability-note">{{ t('common.delivery.fullUrl') }}: {{ previewUrl || '—' }}</p>
      <p class="daa-capability-note">{{ t('common.delivery.addressNote') }}</p>
      <details class="daa-details" open>
        <summary>{{ t('common.delivery.source') }}</summary>
        <p class="daa-capability-note">{{ t('common.delivery.sourceEditNote') }}</p>
        <p class="daa-capability-note">{{ t('common.delivery.unsettledCount', { count: unsettledCount }) }}</p>
        <div class="daa-reporting-source-scroll">
          <table class="daa-reporting-source-table">
            <thead><tr><th scope="col">{{ t('common.delivery.localPlc') }}</th><th scope="col">{{ t('common.delivery.reportingEnabled') }}</th><th scope="col">{{ t('common.delivery.sourceInstance') }}</th><th scope="col">{{ t('common.delivery.sourcePlc') }}</th><th scope="col">{{ t('common.delivery.sourceGeneration') }}</th><th scope="col">{{ t('common.delivery.pasteRow') }}</th></tr></thead>
            <tbody><tr v-for="(source, index) in localSources" :key="source.localPlcId">
              <th scope="row"><strong>{{ source.name }}</strong><span class="muted-cell">{{ source.localPlcId }}</span><span class="muted-cell">{{ source.dbNumbers.map(n => `DB${n}`).join(', ') || '—' }}</span></th>
              <td><ElSwitch :model-value="editing[index].enabled && bindingValid(editing[index])" :aria-label="`${source.name} ${t('common.delivery.reportingEnabled')}`" :disabled="!bindingValid(editing[index])" inline-prompt :active-text="t('common.delivery.reportingOn')" :inactive-text="t('common.delivery.reportingOff')" @update:model-value="value => { editing[index].enabled = !!value }" /></td>
              <td><ElInput v-model="editing[index].instanceId" :aria-label="`${source.localPlcId} ${t('common.delivery.sourceInstance')}`" /></td>
              <td><ElInput v-model="editing[index].plcId" :aria-label="`${source.localPlcId} ${t('common.delivery.sourcePlc')}`" /></td>
              <td><ElInput v-model="editing[index].sourceGeneration" :aria-label="`${source.localPlcId} ${t('common.delivery.sourceGeneration')}`" /></td>
              <td><ConsoleActionButton label-key="common.delivery.pasteRow" @click="openPaste(source.localPlcId)" /></td>
            </tr></tbody>
          </table>
        </div>
        <div v-if="pastePlc" class="daa-reporting-paste">
          <p>{{ t('common.delivery.pasteFor', { plc: pastePlc }) }}</p>
          <ElInput v-model="pasted" type="textarea" :rows="3" :placeholder="t('common.delivery.pastePlaceholder')" />
          <div class="daa-delivery-actions"><ConsoleActionButton label-key="common.delivery.applyParameters" @click="applyParameters" /><ConsoleActionButton label-key="common.delivery.cancelPaste" @click="cancelPaste" /></div>
        </div>
        <ElAlert v-if="sourceError" :title="t('common.delivery.' + sourceError, { plc: sourceErrorPlc })" type="warning" :closable="false" show-icon />
      </details>
      <ElAlert v-if="local.deliverySaveError" :title="t(local.deliverySaveError === 'storage_pending' ? 'common.delivery.settingsPending' : local.deliverySaveError === 'delivery_settings_conflict' ? 'common.delivery.settingsConflict' : 'common.delivery.settingsSaveFailed')" :description="['storage_pending', 'delivery_settings_conflict'].includes(local.deliverySaveError) ? undefined : local.label(local.deliverySaveError)" type="error" :closable="false" show-icon />
      <div class="daa-delivery-actions"><ConsoleActionButton label-key="common.delivery.save" :disabled="local.busy || local.deliverySaveError === 'delivery_settings_conflict'" @click="save" /><ConsoleActionButton label-key="common.delivery.close" :disabled="local.busy" @click="local.deliveryDialog = null" /></div>
    </template>
    <template v-else>
      <template v-if="local.deliveryDialog === 'read'">
        <ElForm label-position="top" class="daa-local-form-grid" :disabled="local.busy" @submit.prevent>
          <ElFormItem :label="t('common.delivery.readMode')">
            <ElSelect v-model="local.factsReadMode" append-to="#daa-feedback">
              <ElOption v-for="mode in ['test', 'latest', 'changes', 'range', 'original']" :key="mode" :value="mode" :label="t('common.delivery.readModes.' + mode)" />
            </ElSelect>
          </ElFormItem>
          <template v-if="['range', 'original'].includes(local.factsReadMode)">
            <ElFormItem :label="t('common.delivery.readFrom')"><ElDatePicker v-model="local.factsReadFrom" type="datetime" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" :editable="false" append-to="#daa-feedback" /></ElFormItem>
            <ElFormItem :label="t('common.delivery.readTo')"><ElDatePicker v-model="local.factsReadTo" type="datetime" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" :editable="false" append-to="#daa-feedback" /></ElFormItem>
          </template>
        </ElForm>
        <div class="daa-delivery-actions">
          <ConsoleActionButton label-key="common.delivery.readRun" :disabled="local.busy" @click="local.testFacts()" />
          <ConsoleActionButton v-if="local.deliveryDetail?.hasMore" :label-key="local.deliveryDetail.pageBudgetReached ? 'common.delivery.readNewBudget' : 'common.delivery.readContinue'" :disabled="local.busy" @click="local.testFacts(true, !!local.deliveryDetail?.pageBudgetReached)" />
        </div>
        <ElAlert v-if="local.busy" :title="t('common.delivery.readWaiting')" type="info" :closable="false" show-icon />
        <ElAlert v-else-if="local.factsReadError" :title="t('common.delivery.readFailed')" :description="local.label(local.factsReadError)" type="error" :closable="false" show-icon />
        <template v-else-if="readStatus !== null">
          <ElAlert
            :title="t(readStatus === 200 ? 'common.delivery.readSucceeded' : 'common.delivery.readRejected', { status: readStatus })"
            :type="readStatus === 200 ? (local.deliveryDetail?.gap ? 'warning' : 'success') : 'error'"
            :description="readErrorCode ? local.label(readErrorCode) : undefined"
            :closable="false"
            show-icon
          />
          <p v-if="readStatus === 200" class="daa-capability-note">{{ t(local.deliveryDetail?.gap ? 'common.delivery.readGap' : local.deliveryDetail?.hasMore ? 'common.delivery.readMore' : 'common.delivery.readScanned') }} {{ t('common.delivery.page', { page: local.factsReadPage }) }}</p>
        </template>
      </template>
      <dl v-if="local.deliveryDialog === 'detail'" class="daa-local-facts"><template v-for="field in detailFields" :key="field.key"><dt>{{ t('common.delivery.' + field.label) }}</dt><dd>{{ field.key === 'state' ? t('common.delivery.states.' + String(local.deliveryDetail?.state)) : local.deliveryDetail?.[field.key] ?? '—' }}</dd></template></dl>
      <template v-if="canRebind"><p class="daa-capability-note">{{ t('common.delivery.newUrl') }}: {{ currentUrl }}</p><ConsoleActionButton label-key="common.delivery.confirmSameTargetButton" :disabled="local.busy" @click="local.rebindDelivery" /></template>
      <p v-if="historicalCommitted" class="daa-capability-note">{{ t('common.delivery.historical') }}</p>
      <p class="daa-capability-note">{{ t(local.deliveryDialog === 'read' ? 'common.delivery.readOnly' : 'common.delivery.originalNote') }}</p>
      <details v-if="local.deliveryDialog !== 'read' || (!local.busy && !local.factsReadError && readStatus !== null)" class="daa-details">
        <summary>{{ t('common.delivery.json') }}</summary><pre class="daa-sample-json">{{ rawDetail }}</pre>
      </details>
      <ConsoleActionButton label-key="common.delivery.close" @click="local.deliveryDialog = null" />
    </template>
  </ElDialog>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElAlert, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElDatePicker, ElSwitch } from 'element-plus'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import { type DeliverySettings, type ReportingBinding } from '../../services/factsDelivery'
import { formatSampleJson } from '../../console/sampleDetails'
import ConsoleActionButton from './ConsoleActionButton.vue'
const local = inject(localConsoleKey), { t } = useI18n()
const draft = ref<DeliverySettings | null>(local?.deliverySettings ? JSON.parse(JSON.stringify(local.deliverySettings)) : null)
const origin = ref(draft.value?.origin ?? '')
const localSources = computed(() => {
  const rows = [...(local?.sourceMaterial?.localSources ?? [])]
  for (const binding of draft.value?.bindings ?? []) if (!rows.some(row => row.localPlcId === binding.localPlcId)) rows.push({ localPlcId: binding.localPlcId, name: binding.localPlcId, dbNumbers: [] })
  return rows
})
type EditingBinding = ReportingBinding & { enabled: boolean }
const editing = ref<EditingBinding[]>(localSources.value.map(row => {
  const binding = draft.value?.bindings.find(b => b.localPlcId === row.localPlcId)
  return { localPlcId: row.localPlcId, instanceId: binding?.instanceId ?? '', plcId: binding?.plcId ?? '', sourceGeneration: binding?.sourceGeneration ?? '', enabled: !!binding && !(draft.value?.disabledLocalPlcs ?? []).includes(row.localPlcId) }
}))
const pasted = ref(''), pastePlc = ref(''), sourceError = ref(''), sourceErrorPlc = ref('')
const unsettledCount = computed(() => { const counts = local?.delivery?.sampleCounts; return counts ? counts.pending + counts.unknown + counts.needsProcessing : '—' })
// Match backend edge whitespace; /u rejects lone surrogates but accepts valid pairs.
function validId(s: unknown): s is string {
  return typeof s === 'string' && !!s &&
    !/[\u0000-\u001f\u007f\uD800-\uDFFF]|^\p{White_Space}|\p{White_Space}$/u.test(s) &&
    new TextEncoder().encode(s).length <= 128
}
function bindingValid(row: ReportingBinding) { return validId(row.instanceId) && validId(row.plcId) && validId(row.sourceGeneration) }
function openPaste(id: string) { pastePlc.value = id; pasted.value = ''; sourceError.value = '' }
function cancelPaste() { pastePlc.value = ''; pasted.value = ''; sourceError.value = '' }
function applyParameters() {
  try {
    const data: unknown = JSON.parse(pasted.value)
    const row = editing.value.find(item => item.localPlcId === pastePlc.value)
    if (!data || typeof data !== 'object' || Array.isArray(data) || !row) throw new Error('sourceInvalid')
    const d = data as Record<string, unknown>
    if (!validId(d.instanceId) || !validId(d.plcId) || !validId(d.sourceGeneration)) throw new Error('sourceInvalid')
    row.instanceId = d.instanceId; row.plcId = d.plcId; row.sourceGeneration = d.sourceGeneration
    cancelPaste()
  } catch { sourceErrorPlc.value = pastePlc.value; sourceError.value = 'sourceInvalid' }
}
const previewUrl = computed(() => origin.value ? origin.value.replace(/\/$/, '') + (draft.value?.path ?? '') : '')
const currentUrl = computed(() => local?.deliverySettings?.origin ? local.deliverySettings.origin + local.deliverySettings.path : '')
const canRebind = computed(() => local?.deliveryDialog === 'detail' && local.deliveryDetail?.state === 'unknown' && !!currentUrl.value && !!local.deliveryDetail?.origin && currentUrl.value !== local.deliveryDetail.origin)
const historicalCommitted = computed(() => { try { const raw = local?.deliveryDetail?.receipt; if (typeof raw !== 'string') return false; const receipt = JSON.parse(raw); return Array.isArray(receipt?.data?.results) && receipt.data.results.some((row: { confirmation?: string }) => row.confirmation === 'historical_committed') } catch { return false } })
const rawDetail = computed(() => { const detail = local?.deliveryDetail; const raw = detail?.responseUtf8; return typeof raw === 'string' ? formatSampleJson(raw) : JSON.stringify(detail, null, 2) })
const readStatus = computed(() => typeof local?.deliveryDetail?.status === 'number' ? local.deliveryDetail.status : null)
const readErrorCode = computed(() => {
    const result = local?.deliveryDetail?.result as { errorCode?: unknown } | undefined
    return typeof result?.errorCode === 'string' ? result.errorCode : ''
})
const detailFields = [{ key: 'batchId', label: 'batch' }, { key: 'plcId', label: 'plc' }, { key: 'dbNumber', label: 'db' }, { key: 'state', label: 'state' }, { key: 'origin', label: 'oldUrl' }, { key: 'bodySha256', label: 'bodyDigest' }, { key: 'lastError', label: 'reason' }]
const titleKey = computed(() => ({ settings: 'settings', detail: 'details', source: 'source', preview: 'preview', read: 'test' }[local?.deliveryDialog ?? 'detail']))
function save() {
  if (!draft.value || !local) return
  const bindings = editing.value.filter(row => row.instanceId || row.plcId || row.sourceGeneration)
  const invalid = bindings.find(row => !validId(row.instanceId) || !validId(row.plcId) || !validId(row.sourceGeneration))
  if (invalid) { sourceErrorPlc.value = invalid.localPlcId; sourceError.value = 'sourceInvalid'; return }
  if (new Set(bindings.map(row => row.plcId)).size !== bindings.length) { sourceError.value = 'sourceDuplicate'; return }
  const settings: DeliverySettings = { ...draft.value, origin: origin.value || null, bindings: bindings.map(({ enabled: _enabled, ...binding }) => binding), disabledLocalPlcs: editing.value.filter(row => !row.enabled || !bindingValid(row)).map(row => row.localPlcId) }
  sourceError.value = ''
  void local.saveDelivery(settings)
}
</script>
