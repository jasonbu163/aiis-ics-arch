<!--
  文件路径: /frontend-next-js/src/app/performance/components/SplitMergeActionDialog.vue
  功能描述: 分卷管理页的分/合卷标准弹窗
  主要功能:
    - 在弹窗内切换 split / merge 模式
    - 复用来源选择、卷重分配和 lineage 审计摘要组件
    - 通过模块 API facade 提交 B17 transform 请求
-->
<template>
  <el-dialog
    v-model="visible"
    class="standard-form-dialog split-merge-action-dialog"
    :title="$t('performance.splitManagement.dialog.title')"
    width="min(1040px, 94vw)"
    destroy-on-close
    :before-close="handleBeforeClose"
  >
    <div class="split-merge-action-dialog__content">
      <div class="split-merge-action-dialog__toolbar">
        <TransformModeTabs :model-value="mode" @update:model-value="handleModeChange" />
        <ActionButton variant="refresh" size="small" :loading="loadingSources" @click="emit('refreshSources')">
          {{ $t('common.refresh') }}
        </ActionButton>
      </div>

      <PerformanceSourcePicker
        :mode="mode"
        :candidates="candidates"
        :selected-ids="selectedSourceIds"
        :summaries="dialogSummaries"
        :loading="loadingSources"
        @update:selected-ids="handleSourceChange"
        @refresh="emit('refreshSources')"
      />

      <AllocationEditor
        :mode="mode"
        :split-targets="splitTargets"
        :merge-target="mergeTarget"
        :merge-allocations="mergeAllocations"
        :selected-sources="selectedSources"
        :summaries="dialogSummaries"
        @add-split-target="addSplitTarget"
        @remove-split-target="removeSplitTarget"
        @update-split-target="updateSplitTarget"
        @update-merge-target="updateMergeTarget"
        @update-merge-allocation="updateMergeAllocation"
      />

      <el-form label-position="top">
        <el-form-item :label="$t('performance.splitWorkbench.submit.reason')">
          <el-input
            v-model="reason"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('performance.splitWorkbench.submit.reasonPlaceholder')"
          />
        </el-form-item>
      </el-form>

      <LineageAuditSummary
        :transform="latestTransform"
        :error-code="businessErrorCode"
      />
    </div>

    <template #footer>
      <div class="split-merge-action-dialog__footer">
        <ActionButton variant="secondary" @click="requestClose">
          {{ $t('common.cancel') }}
        </ActionButton>
        <ActionButton variant="primary" :loading="submitting" @click="handleSubmit">
          {{ $t(`performance.splitWorkbench.actions.submit.${mode}`) }}
        </ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import TransformModeTabs from './TransformModeTabs.vue'
import PerformanceSourcePicker from './PerformanceSourcePicker.vue'
import AllocationEditor from './AllocationEditor.vue'
import LineageAuditSummary from './LineageAuditSummary.vue'
import {
  createMergeTransform,
  createSplitTransform,
  getPerformanceLineageSummary
} from '@/app/performance/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  candidates: {
    type: Array,
    default: () => []
  },
  summaries: {
    type: Object,
    default: () => ({})
  },
  loadingSources: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submitted', 'refreshSources'])
const { t, te } = useI18n()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const mode = ref('split')
const selectedSourceIds = ref([])
const dialogSummaries = reactive({})
const splitTargets = ref([])
const mergeTarget = ref(createMergeTarget())
const mergeAllocations = ref([])
const reason = ref('')
const submitting = ref(false)
const latestTransform = ref(null)
const businessErrorCode = ref('')

const selectedSources = computed(() => selectedSourceIds.value
  .map((id) => props.candidates.find((item) => item.id === id))
  .filter(Boolean))

const createSplitTarget = () => ({
  clientId: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  coilNo: '',
  allocatedWeight: null,
  grade: '',
  spec: '',
  remark: ''
})

function createMergeTarget() {
  return {
    coilNo: '',
    grade: '',
    spec: '',
    remark: ''
  }
}

watch(() => props.summaries, (summaries) => {
  Object.keys(dialogSummaries).forEach((key) => {
    delete dialogSummaries[key]
  })
  Object.entries(summaries || {}).forEach(([key, value]) => {
    dialogSummaries[key] = value
  })
}, { deep: true, immediate: true })

watch(() => props.modelValue, (opened) => {
  if (opened && splitTargets.value.length === 0) {
    splitTargets.value = [createSplitTarget()]
  }
})

const loadSummaries = async (ids) => {
  const uniqueIds = [...new Set(ids.filter((id) => id !== null && id !== undefined))]
  await Promise.all(uniqueIds.map(async (id) => {
    try {
      dialogSummaries[id] = await getPerformanceLineageSummary(id)
    } catch (error) {
      const fallback = props.candidates.find((item) => item.id === id) || {}
      dialogSummaries[id] = {
        performanceId: id,
        effectiveWeight: fallback.effectiveWeight ?? fallback.weight ?? null,
        effectiveWeightSource: fallback.effectiveWeightSource || '',
        committedSourceAllocatedWeight: fallback.committedSourceAllocatedWeight ?? null,
        availableWeight: fallback.availableWeight ?? null,
        errorCode: error?.errorCode || 'lineage_summary_unavailable'
      }
      businessErrorCode.value = dialogSummaries[id].errorCode
    }
  }))
}

const handleSourceChange = async (ids) => {
  selectedSourceIds.value = ids
  await loadSummaries(ids)
  syncMergeAllocations()
}

const syncMergeAllocations = () => {
  mergeAllocations.value = selectedSourceIds.value.map((performanceId) => {
    const existing = mergeAllocations.value.find((item) => item.performanceId === performanceId)
    return existing || {
      performanceId,
      allocatedWeight: null
    }
  })
}

const addSplitTarget = () => {
  splitTargets.value = [...splitTargets.value, createSplitTarget()]
}

const removeSplitTarget = (clientId) => {
  splitTargets.value = splitTargets.value.filter((item) => item.clientId !== clientId)
}

const updateSplitTarget = ({ clientId, field, value }) => {
  splitTargets.value = splitTargets.value.map((item) => (
    item.clientId === clientId ? { ...item, [field]: value } : item
  ))
}

const updateMergeTarget = ({ field, value }) => {
  mergeTarget.value = {
    ...mergeTarget.value,
    [field]: value
  }
}

const updateMergeAllocation = ({ performanceId, allocatedWeight }) => {
  mergeAllocations.value = mergeAllocations.value.map((item) => (
    item.performanceId === performanceId ? { ...item, allocatedWeight } : item
  ))
}

const isBlank = (value) => value === null || value === undefined || String(value).trim() === ''

const parseRequiredWeight = (value) => {
  if (isBlank(value)) return null
  const numericValue = Number(value)
  return Number.isFinite(numericValue) && numericValue > 0 ? numericValue : null
}

const cleanOptionalString = (value) => (isBlank(value) ? null : String(value).trim())

const hasValue = (value) => !isBlank(value)

const hasDirtySplitDraft = () => (
  selectedSourceIds.value.length > 0 ||
  splitTargets.value.length > 1 ||
  splitTargets.value.some((target) => (
    hasValue(target.coilNo) ||
    hasValue(target.allocatedWeight) ||
    hasValue(target.grade) ||
    hasValue(target.spec) ||
    hasValue(target.remark)
  ))
)

const hasDirtyMergeDraft = () => (
  selectedSourceIds.value.length > 0 ||
  mergeAllocations.value.some((source) => hasValue(source.allocatedWeight)) ||
  Object.values(mergeTarget.value).some((value) => hasValue(value))
)

const hasDirtyDraft = () => (
  hasValue(reason.value) ||
  (mode.value === 'split' ? hasDirtySplitDraft() : hasDirtyMergeDraft())
)

const resetDraft = (nextMode = mode.value) => {
  mode.value = nextMode
  selectedSourceIds.value = []
  mergeAllocations.value = []
  mergeTarget.value = createMergeTarget()
  splitTargets.value = [createSplitTarget()]
  reason.value = ''
  businessErrorCode.value = ''
}

const handleModeChange = async (nextMode) => {
  if (nextMode === mode.value) return

  if (!hasDirtyDraft()) {
    resetDraft(nextMode)
    latestTransform.value = null
    return
  }

  try {
    await confirmDraftLoss()
    resetDraft(nextMode)
    latestTransform.value = null
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      throw error
    }
  }
}

const confirmDraftLoss = () => ElMessageBox.confirm(
  t('performance.splitWorkbench.confirmModeSwitch.message'),
  t('performance.splitWorkbench.confirmModeSwitch.title'),
  {
    confirmButtonText: t('performance.splitWorkbench.confirmModeSwitch.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }
)

const requestClose = async () => {
  if (!hasDirtyDraft()) {
    visible.value = false
    return
  }

  try {
    await confirmDraftLoss()
    visible.value = false
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      throw error
    }
  }
}

const handleBeforeClose = async (done) => {
  if (!hasDirtyDraft()) {
    done()
    return
  }

  try {
    await confirmDraftLoss()
    done()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      throw error
    }
  }
}

const validateSplit = () => {
  if (selectedSourceIds.value.length !== 1) return 'splitSourceRequired'
  const validTargetCount = splitTargets.value.filter((target) => (
    !isBlank(target.coilNo) && parseRequiredWeight(target.allocatedWeight) !== null
  )).length
  if (validTargetCount < 2) return 'splitTargetsRequired'

  const invalidTarget = splitTargets.value.some((target) => {
    const allocatedWeight = parseRequiredWeight(target.allocatedWeight)
    return isBlank(target.coilNo) || allocatedWeight === null
  })

  return invalidTarget ? 'splitTargetInvalid' : ''
}

const validateMerge = () => {
  if (selectedSourceIds.value.length < 2) return 'mergeSourcesRequired'
  if (isBlank(mergeTarget.value.coilNo)) return 'mergeTargetRequired'

  const invalidSource = mergeAllocations.value.length !== selectedSourceIds.value.length ||
    mergeAllocations.value.some((source) => parseRequiredWeight(source.allocatedWeight) === null)

  return invalidSource ? 'mergeAllocationInvalid' : ''
}

const buildSplitPayload = () => ({
  sourcePerformanceId: selectedSourceIds.value[0],
  targets: splitTargets.value.map((target) => ({
    coilNo: String(target.coilNo).trim(),
    allocatedWeight: parseRequiredWeight(target.allocatedWeight),
    grade: cleanOptionalString(target.grade),
    spec: cleanOptionalString(target.spec),
    remark: cleanOptionalString(target.remark)
  })),
  reason: cleanOptionalString(reason.value)
})

const buildMergePayload = () => ({
  sources: mergeAllocations.value.map((source) => ({
    performanceId: source.performanceId,
    allocatedWeight: parseRequiredWeight(source.allocatedWeight)
  })),
  target: {
    coilNo: String(mergeTarget.value.coilNo).trim(),
    grade: cleanOptionalString(mergeTarget.value.grade),
    spec: cleanOptionalString(mergeTarget.value.spec),
    remark: cleanOptionalString(mergeTarget.value.remark)
  },
  reason: cleanOptionalString(reason.value)
})

const refreshAfterTransform = async (transform) => {
  const lineageIds = (transform?.lineageEntries || [])
    .map((entry) => entry.performanceId)
    .filter((id) => id !== null && id !== undefined)
  await loadSummaries([...selectedSourceIds.value, ...lineageIds])
}

const handleSubmit = async () => {
  const validationKey = mode.value === 'split' ? validateSplit() : validateMerge()
  if (validationKey) {
    ElMessage.warning(t(`performance.splitWorkbench.validation.${validationKey}`))
    return
  }

  submitting.value = true
  businessErrorCode.value = ''

  try {
    const payload = mode.value === 'split' ? buildSplitPayload() : buildMergePayload()
    const transform = mode.value === 'split'
      ? await createSplitTransform(payload)
      : await createMergeTransform(payload)

    latestTransform.value = transform
    await refreshAfterTransform(transform)
    resetDraft()
    emit('submitted', transform)
    ElMessage.success(t('performance.splitWorkbench.messages.submitSuccess'))
  } catch (error) {
    businessErrorCode.value = error?.errorCode || 'transform_submit_failed'
    ElMessage.error(formatError(businessErrorCode.value))
  } finally {
    submitting.value = false
  }
}

const formatError = (errorCode) => {
  const key = `performance.splitWorkbench.errors.${errorCode}`
  return te(key) ? t(key) : errorCode
}
</script>

<style scoped>
.split-merge-action-dialog__content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.split-merge-action-dialog__toolbar,
.split-merge-action-dialog__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.split-merge-action-dialog__footer {
  justify-content: flex-end;
}
</style>
