<!--
  文件路径: /frontend-next-js/src/app/performance/components/PerformancePlanLinkDialog.vue
  功能描述: 实绩与计划显式回链弹窗
  主要功能:
    - 展示未计划实绩的计划候选
    - 调用后端完成同步观察、手动关联和计划回补
    - 不在前端推断或写入 Plan / Performance 关系
-->
<template>
  <el-dialog
    v-model="visible"
    :title="$t('performance.planLink.title')"
    width="960px"
    class="standard-form-dialog performance-plan-link-dialog"
    modal-class="performance-dialog-mask"
    destroy-on-close
    @closed="handleClosed"
  >
    <section class="dialog-section">
      <h3 class="dialog-section__title">{{ $t('performance.planLink.performanceSummary') }}</h3>
      <el-descriptions :column="3" border>
        <el-descriptions-item :label="$t('performance.coilNo')">
          {{ performance?.coilNo || '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.grade')">
          {{ performance?.grade || '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.planLink.planId')">
          {{ performance?.planId || '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.recordSource')">
          {{ formatRecordSource(performance?.recordSource) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.observationStatus')">
          {{ formatObservationStatus(performance?.observationStatus) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.spec')">
          {{ performance?.spec || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </section>

    <el-alert
      v-if="linkResult"
      class="plan-link-result"
      :type="linkResult.linked ? 'success' : 'info'"
      :title="formatLinkResult(linkResult)"
      show-icon
      :closable="false"
    />

    <el-tabs v-model="activeTab" class="plan-link-tabs">
      <el-tab-pane :label="$t('performance.planLink.candidatesTab')" name="candidates">
        <div class="plan-link-toolbar">
          <ActionButton variant="refresh" size="small" :loading="candidateLoading" @click="loadCandidates">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.refresh') }}
          </ActionButton>
          <ActionButton variant="primary" size="small" :loading="actionLoading" @click="handleSyncObservation">
            <el-icon><Connection /></el-icon>
            {{ $t('performance.planLink.syncObservation') }}
          </ActionButton>
        </div>

        <el-table
          :data="candidates"
          v-loading="candidateLoading"
          border
          stripe
          class="vibe-table plan-link-candidate-table"
          empty-text="-"
          @row-click="handleCandidateRowClick"
        >
          <el-table-column width="56" align="center">
            <template #default="{ row }">
              <el-radio v-model="selectedPlanId" :label="row.id">
                <span class="radio-silent-label"></span>
              </el-radio>
            </template>
          </el-table-column>
          <el-table-column prop="id" :label="$t('performance.planLink.planId')" width="90" />
          <el-table-column prop="coilNo" :label="$t('plan.coilNo')" min-width="150" />
          <el-table-column prop="grade" :label="$t('plan.steelGrade')" width="120" />
          <el-table-column prop="spec" :label="$t('plan.spec')" min-width="140" />
          <el-table-column prop="weight" :label="$t('plan.weight')" width="110" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.weight, 4) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" :label="$t('plan.status')" width="120">
            <template #default="{ row }">
              <PlanStatusTag :status="row.status" size="small" />
            </template>
          </el-table-column>
        </el-table>

        <div class="plan-link-footer-actions">
          <ActionButton
            variant="primary"
            size="small"
            :disabled="!selectedPlanId"
            :loading="actionLoading"
            @click="handleLinkSelectedPlan"
          >
            <el-icon><Check /></el-icon>
            {{ $t('performance.planLink.linkSelected') }}
          </ActionButton>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('performance.planLink.backfillTab')" name="backfill">
        <el-form
          ref="backfillFormRef"
          :model="backfillForm"
          :rules="backfillRules"
          label-position="top"
          class="standard-dialog-form plan-backfill-form"
        >
          <section class="dialog-section">
            <h3 class="dialog-section__title">{{ $t('plan.basicInfo') }}</h3>
            <div class="dialog-form-grid">
              <el-form-item :label="$t('plan.coilNo')" prop="coilNo">
                <el-input v-model="backfillForm.coilNo" disabled />
              </el-form-item>
              <el-form-item :label="$t('plan.steelGrade')" prop="grade">
                <el-input v-model="backfillForm.grade" :placeholder="$t('plan.rules.gradeRequired')" />
              </el-form-item>
              <el-form-item :label="$t('plan.materialStatus')" prop="materialStatus">
                <el-select v-model="backfillForm.materialStatus" :placeholder="$t('plan.rules.materialStatusRequired')">
                  <el-option
                    v-for="(label, key) in $tm('plan.materialStatusMap')"
                    :key="key"
                    :label="label"
                    :value="key"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="$t('plan.spec')" prop="spec">
                <el-input v-model="backfillForm.spec" :placeholder="$t('plan.specPlaceholder')" />
              </el-form-item>
              <el-form-item :label="$t('plan.weight') + ' (' + $t('common.unit.ton') + ')'" prop="weight">
                <el-input-number v-model="backfillForm.weight" :min="0" :precision="4" :step="0.1" :value-on-clear="null" clearable />
              </el-form-item>
              <el-form-item :label="$t('plan.thickness') + ' (' + $t('common.unit.mm') + ')'" prop="thickness">
                <el-input-number v-model="backfillForm.thickness" :min="0" :precision="2" :step="0.1" :value-on-clear="null" clearable />
              </el-form-item>
              <el-form-item :label="$t('plan.width') + ' (' + $t('common.unit.mm') + ')'" prop="width">
                <el-input-number v-model="backfillForm.width" :min="0" :precision="2" :step="1" :value-on-clear="null" clearable />
              </el-form-item>
              <el-form-item :label="$t('plan.priority')" prop="priority">
                <el-input-number v-model="backfillForm.priority" :min="1" :max="10" :precision="0" :step="1" />
              </el-form-item>
              <el-form-item class="form-item-wide" :label="$t('plan.remark')" prop="remark">
                <el-input v-model="backfillForm.remark" type="textarea" :rows="3" :placeholder="$t('plan.remark')" maxlength="500" show-word-limit />
              </el-form-item>
            </div>
          </section>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="vibe-dialog-footer">
        <ActionButton @click="visible = false">
          <el-icon><Close /></el-icon>
          {{ $t('common.close') }}
        </ActionButton>
        <ActionButton
          v-if="activeTab === 'backfill'"
          variant="primary"
          :loading="actionLoading"
          @click="handleBackfill"
        >
          <el-icon><Check /></el-icon>
          {{ $t('performance.planLink.backfillSubmit') }}
        </ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  backfillPlanFromPerformance,
  getPlanLinkCandidates,
  linkPlanToPerformance,
  syncPlanObservation
} from '@/app/plan/api'
import PlanStatusTag from '@/app/plan/components/PlanStatusTag.vue'
import ActionButton from '@/components/common/ActionButton.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  performance: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'linked'])
const { t } = useI18n()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const activeTab = ref('candidates')
const candidateLoading = ref(false)
const actionLoading = ref(false)
const candidates = ref([])
const selectedPlanId = ref(null)
const linkResult = ref(null)
const backfillFormRef = ref()

const backfillForm = reactive({
  coilNo: '',
  grade: '',
  spec: '',
  weight: null,
  thickness: null,
  width: null,
  materialStatus: 'special',
  density: 0,
  entryLength: 0,
  uncoiler1Tension: 0,
  exitTension: 0,
  process1Tension: 0,
  entryLoopTension: 0,
  exitLoopTension: 0,
  entryUnitTension: 0,
  entryLoopUnitTension: 0,
  processUnitTension: 0,
  exitLoopUnitTension: 0,
  exitUnitTension: 0,
  priority: 5,
  remark: ''
})

const hasValue = (value) => value !== null && value !== undefined && value !== ''

const normalizeNumber = (value) => {
  if (!hasValue(value)) return null
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : null
}

const stringifyNumber = (value) => String(value ?? '')

const getErrorMessage = (error, fallback) => error?.message || fallback

const backfillRules = computed(() => ({
  coilNo: [{ required: true, message: t('plan.rules.coilNoRequired'), trigger: 'blur' }],
  grade: [{ required: true, message: t('plan.rules.gradeRequired'), trigger: 'blur' }],
  spec: [{ required: true, message: t('plan.rules.specRequired'), trigger: 'blur' }],
  weight: [{ required: true, message: t('plan.rules.weightRequired'), trigger: 'blur' }],
  thickness: [{ required: true, message: t('plan.rules.thicknessRequired'), trigger: 'blur' }],
  width: [{ required: true, message: t('plan.rules.widthRequired'), trigger: 'blur' }],
  materialStatus: [{ required: true, message: t('plan.rules.materialStatusRequired'), trigger: 'change' }]
}))

const resetBackfillForm = () => {
  const performance = props.performance || {}
  backfillForm.coilNo = performance.coilNo || ''
  backfillForm.grade = performance.grade || ''
  backfillForm.spec = performance.spec || ''
  backfillForm.weight = normalizeNumber(performance.weight)
  backfillForm.thickness = null
  backfillForm.width = null
  backfillForm.materialStatus = 'special'
  backfillForm.density = 0
  backfillForm.entryLength = 0
  backfillForm.uncoiler1Tension = 0
  backfillForm.exitTension = 0
  backfillForm.process1Tension = 0
  backfillForm.entryLoopTension = 0
  backfillForm.exitLoopTension = 0
  backfillForm.entryUnitTension = 0
  backfillForm.entryLoopUnitTension = 0
  backfillForm.processUnitTension = 0
  backfillForm.exitLoopUnitTension = 0
  backfillForm.exitUnitTension = 0
  backfillForm.priority = 5
  backfillForm.remark = ''
}

const loadCandidates = async () => {
  if (!props.performance?.id) return
  candidateLoading.value = true
  try {
    const result = await getPlanLinkCandidates(props.performance.id)
    candidates.value = result?.candidates || []
    selectedPlanId.value = candidates.value.length === 1 ? candidates.value[0].id : null
    linkResult.value = {
      action: candidates.value.length ? 'candidate_loaded' : 'no_matching_plan',
      linked: false,
      candidateCount: result?.candidateCount ?? candidates.value.length
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('performance.planLink.messages.candidateLoadFailed')))
  } finally {
    candidateLoading.value = false
  }
}

const handleCandidateRowClick = (row) => {
  selectedPlanId.value = row.id
}

const handleLinkedResult = (result, successKey) => {
  linkResult.value = result
  if (result?.linked) {
    ElMessage.success(t(successKey))
    emit('linked', result)
    visible.value = false
  }
}

const handleSyncObservation = async () => {
  if (!props.performance?.id) return
  actionLoading.value = true
  try {
    const result = await syncPlanObservation(props.performance.id)
    handleLinkedResult(result, 'performance.planLink.messages.syncSuccess')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('performance.planLink.messages.syncFailed')))
  } finally {
    actionLoading.value = false
  }
}

const handleLinkSelectedPlan = async () => {
  if (!props.performance?.id || !selectedPlanId.value) return
  actionLoading.value = true
  try {
    const result = await linkPlanToPerformance(props.performance.id, selectedPlanId.value)
    handleLinkedResult(result, 'performance.planLink.messages.linkSuccess')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('performance.planLink.messages.linkFailed')))
  } finally {
    actionLoading.value = false
  }
}

const handleBackfill = async () => {
  if (!props.performance?.id || !backfillFormRef.value) return
  await backfillFormRef.value.validate(async (valid) => {
    if (!valid) return
    actionLoading.value = true
    try {
      const payload = {
        coilNo: backfillForm.coilNo.trim(),
        grade: backfillForm.grade.trim(),
        spec: backfillForm.spec.trim(),
        weight: stringifyNumber(backfillForm.weight),
        thickness: stringifyNumber(backfillForm.thickness),
        width: stringifyNumber(backfillForm.width),
        materialStatus: backfillForm.materialStatus,
        density: stringifyNumber(backfillForm.density),
        entryLength: stringifyNumber(backfillForm.entryLength),
        uncoiler1Tension: stringifyNumber(backfillForm.uncoiler1Tension),
        exitTension: stringifyNumber(backfillForm.exitTension),
        process1Tension: stringifyNumber(backfillForm.process1Tension),
        entryLoopTension: stringifyNumber(backfillForm.entryLoopTension),
        exitLoopTension: stringifyNumber(backfillForm.exitLoopTension),
        entryUnitTension: stringifyNumber(backfillForm.entryUnitTension),
        entryLoopUnitTension: stringifyNumber(backfillForm.entryLoopUnitTension),
        processUnitTension: stringifyNumber(backfillForm.processUnitTension),
        exitLoopUnitTension: stringifyNumber(backfillForm.exitLoopUnitTension),
        exitUnitTension: stringifyNumber(backfillForm.exitUnitTension),
        priority: backfillForm.priority,
        remark: backfillForm.remark?.trim() || undefined
      }
      const result = await backfillPlanFromPerformance(props.performance.id, payload)
      handleLinkedResult(result, 'performance.planLink.messages.backfillSuccess')
    } catch (error) {
      ElMessage.error(getErrorMessage(error, t('performance.planLink.messages.backfillFailed')))
    } finally {
      actionLoading.value = false
    }
  })
}

const formatNumber = (value, precision) => {
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue.toFixed(precision) : '-'
}

const formatRecordSource = (recordSource) => {
  if (!recordSource) return '-'
  const key = `performance.recordSources.${recordSource}`
  const translated = t(key)
  return translated === key ? recordSource : translated
}

const formatObservationStatus = (status) => {
  const key = `performance.observationStatusMap.${status || 'manual_historical'}`
  const translated = t(key)
  return translated === key ? (status || '-') : translated
}

const formatLinkResult = (result) => {
  const action = result?.action || 'unknown'
  const key = `performance.planLink.actionMap.${action}`
  const translated = t(key)
  const actionText = translated === key ? action : translated
  const count = result?.candidateCount ?? 0
  if (result?.linked) {
    return t('performance.planLink.resultLinked', { action: actionText, planId: result.planId || '-' })
  }
  return t('performance.planLink.resultNotLinked', { action: actionText, count })
}

const handleClosed = () => {
  activeTab.value = 'candidates'
  candidateLoading.value = false
  actionLoading.value = false
  candidates.value = []
  selectedPlanId.value = null
  linkResult.value = null
  backfillFormRef.value?.resetFields()
}

watch(
  () => props.modelValue,
  (opened) => {
    if (!opened) return
    resetBackfillForm()
    loadCandidates()
  }
)
</script>

<style scoped>
.plan-link-result {
  margin-bottom: 18px;
}

.plan-link-tabs {
  margin-top: 4px;
}

.plan-link-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 14px;
}

.plan-link-candidate-table {
  width: 100%;
}

.radio-silent-label {
  display: inline-block;
  width: 0;
  overflow: hidden;
}

.plan-link-footer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.plan-backfill-form {
  gap: 18px;
}

.plan-backfill-form :deep(.dialog-form-grid) {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px 20px;
}

.plan-backfill-form :deep(.el-input-number),
.plan-backfill-form :deep(.el-select) {
  width: 100%;
}

.form-item-wide {
  grid-column: 1 / -1;
}

@media (max-width: 960px) {
  .plan-backfill-form :deep(.dialog-form-grid) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .plan-link-toolbar {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .plan-backfill-form :deep(.dialog-form-grid) {
    grid-template-columns: 1fr;
  }
}
</style>
