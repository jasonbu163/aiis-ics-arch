<!-- 上传设置、接入材料与投递弹窗；GET 读取结果和失败原因在当前弹窗显示。 -->
<template>
  <ElDialog v-if="local" :model-value="!!local.deliveryDialog" :title="t('common.delivery.' + titleKey)" class="daa-delivery-dialog" width="min(900px, 94vw)" append-to="#daa-feedback" :close-on-click-modal="false" @update:model-value="value => { if (!value) local!.deliveryDialog = null }">
    <template v-if="local.deliveryDialog === 'settings' && draft">
      <ElForm label-position="top" class="daa-local-form-grid" @submit.prevent>
        <ElFormItem :label="t('common.delivery.origin')"><ElInput v-model="origin" :maxlength="2048" /></ElFormItem><ElFormItem :label="t('common.delivery.interval')"><ElInputNumber v-model="draft.intervalSeconds" :min="1" :max="3600" :precision="0" /></ElFormItem><ElFormItem :label="t('common.delivery.target')"><ElInput v-model="target" :maxlength="128" /></ElFormItem><ElFormItem :label="t('common.delivery.adoptionReference')"><ElInput v-model="draft.adoptionReference" :maxlength="2048" /></ElFormItem>
      </ElForm>
      <p class="daa-capability-note">{{ t('common.delivery.adoptionNote') }}</p>
      <section v-for="source in choices" :key="source.plcId" class="daa-delivery-source"><ElCheckbox v-model="source.checked" :disabled="!source.sourceGeneration">{{ source.plcId }}</ElCheckbox><dl class="daa-local-facts"><dt>{{ t('common.delivery.generation') }}</dt><dd>{{ source.sourceGeneration || '—' }}</dd><dt>{{ t('common.delivery.definitionDigest') }}</dt><dd>{{ source.definitionSetDigest }}</dd><dt>{{ t('common.delivery.contextDigest') }}</dt><dd>{{ source.contextSha256 }}</dd></dl><div class="daa-local-form-grid"><ElFormItem :label="t('common.delivery.sequenceFrom')"><ElInput v-model="source.sequenceFrom" :maxlength="19" /></ElFormItem><ElFormItem :label="t('common.delivery.sequenceThrough')"><ElInput v-model="source.sequenceThrough" :maxlength="19" /></ElFormItem><ElFormItem :label="t('common.delivery.sourceReference')"><ElInput v-model="source.reference" :maxlength="2048" /></ElFormItem></div></section>
      <details class="daa-details"><summary>{{ t('common.delivery.contractPins') }}</summary><pre class="daa-sample-json">{{ JSON.stringify(CONTRACT_PINS, null, 2) }}</pre></details>
      <div class="daa-delivery-actions"><ConsoleActionButton label-key="common.delivery.save" :disabled="local.busy" @click="save" /><ConsoleActionButton label-key="common.delivery.close" :disabled="local.busy" @click="local.deliveryDialog = null" /></div>
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
import { ElAlert, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElCheckbox, ElSelect, ElOption, ElDatePicker } from 'element-plus'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import { CONTRACT_PINS, type DeliverySettings } from '../../services/factsDelivery'
import { formatSampleJson } from '../../console/sampleDetails'
import ConsoleActionButton from './ConsoleActionButton.vue'
const local = inject(localConsoleKey), { t } = useI18n()
const draft = ref<DeliverySettings | null>(local?.deliverySettings ? JSON.parse(JSON.stringify(local.deliverySettings)) : null)
const origin = ref(draft.value?.origin ?? ''), target = ref(draft.value?.targetId ?? '')
const choices = ref((local?.sourceMaterial?.sources ?? []).map(s => { const old = draft.value?.sources.find(p => p.plcId === s.plcId); return { ...s, checked: !!old, sequenceFrom: old?.sequenceFrom ?? '1', sequenceThrough: old?.sequenceThrough ?? '9223372036854775806', reference: old?.reference ?? '' } }))
const historicalCommitted = computed(() => { try { const raw = local?.deliveryDetail?.receipt; if (typeof raw !== 'string') return false; const receipt = JSON.parse(raw); return Array.isArray(receipt?.data?.results) && receipt.data.results.some((row: { confirmation?: string }) => row.confirmation === 'historical_committed') } catch { return false } })
const rawDetail = computed(() => { const detail = local?.deliveryDetail; const raw = detail?.responseUtf8 ?? detail?.body ?? detail?.receipt; return typeof raw === 'string' ? formatSampleJson(raw) : JSON.stringify(detail, null, 2) })
const readStatus = computed(() => typeof local?.deliveryDetail?.status === 'number' ? local.deliveryDetail.status : null)
const readErrorCode = computed(() => {
    const result = local?.deliveryDetail?.result as { errorCode?: unknown } | undefined
    return typeof result?.errorCode === 'string' ? result.errorCode : ''
})
const detailFields = [{ key: 'batchId', label: 'batch' }, { key: 'state', label: 'state' }, { key: 'requestDigest', label: 'requestDigest' }, { key: 'bodySha256', label: 'bodyDigest' }, { key: 'lastError', label: 'reason' }]
const titleKey = computed(() => ({ settings: 'settings', detail: 'details', source: 'source', preview: 'preview', read: 'test' }[local?.deliveryDialog ?? 'detail']))
function save() { if (!draft.value || !local) return; const settings: DeliverySettings = { ...draft.value, targetId: target.value || null, origin: origin.value || null, contractPins: { ...CONTRACT_PINS }, sources: choices.value.filter(s => s.checked && s.sourceGeneration).map(s => ({ plcId: s.plcId, sourceGeneration: s.sourceGeneration!, definitionSetDigest: s.definitionSetDigest, contextSha256: s.contextSha256, sequenceFrom: s.sequenceFrom, sequenceThrough: s.sequenceThrough, reference: s.reference })) }; void local.saveDelivery(settings) }
</script>
