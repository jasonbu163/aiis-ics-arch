<!--
  文件路径: /frontend-next-js/src/app/plan/components/PlanFormDialog.vue
  功能描述: 生产计划表单弹窗组件
  主要功能:
    - 新增、编辑、查看生产计划
    - 表单校验与字段联动
    - 计划状态下的只读控制
-->
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="900px"
    @close="handleClose"
    destroy-on-close
    class="standard-form-dialog plan-dialog"
    modal-class="plan-dialog-mask"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="computedRules"
      label-position="top"
      class="standard-dialog-form plan-form"
      :disabled="isReadOnly"
      :hide-required-asterisk="isReadOnly"
    >
      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.basicInfo') }}</h3>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item :label="$t('plan.coilNo')" prop="coilNo">
              <el-input v-model="form.coilNo" :placeholder="$t('plan.rules.coilNoRequired')">
                <template #prefix><el-icon><Tickets /></el-icon></template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.steelGrade')" prop="grade">
              <el-input v-model="form.grade" :placeholder="$t('plan.rules.gradeRequired')">
                <template #prefix><el-icon><PriceTag /></el-icon></template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.materialStatus')" prop="materialStatus">
              <el-select v-model="form.materialStatus" :placeholder="$t('plan.rules.materialStatusRequired')" style="width: 100%">
                <el-option :label="$t('plan.materialStatusMap.degreasing')" value="degreasing" />
                <el-option :label="$t('plan.materialStatusMap.annealing')" value="annealing" />
                <el-option :label="$t('plan.materialStatusMap.tension')" value="tension" />
                <el-option :label="$t('plan.materialStatusMap.special')" value="special" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item :label="$t('plan.spec')" prop="spec">
              <el-input v-model="form.spec" :placeholder="$t('plan.specPlaceholder')">
                <template #prefix>
                  <el-icon><Grid /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('plan.weight') + ' (' + $t('common.unit.ton') + ')'" prop="weight">
              <el-input-number v-model="form.weight" :min="0" :precision="3" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.sizeParams') }}</h3>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item :label="$t('plan.width') + ' (' + $t('common.unit.mm') + ')'" prop="width">
              <el-input-number v-model="form.width" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.thickness') + ' (' + $t('common.unit.mm') + ')'" prop="thickness">
              <el-input-number v-model="form.thickness" :min="0" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.density')" prop="density">
              <el-input-number v-model="form.density" :min="0" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.entryLength')" prop="entryLength">
              <el-input-number v-model="form.entryLength" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.planForm.tensionGiven') }}</h3>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.uncoiler1Tension')" prop="uncoiler1Tension">
              <el-input-number v-model="form.uncoiler1Tension" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.exitTension')" prop="exitTension">
              <el-input-number v-model="form.exitTension" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.process1Tension')" prop="process1Tension">
              <el-input-number v-model="form.process1Tension" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.entryLoopTension')" prop="entryLoopTension">
              <el-input-number v-model="form.entryLoopTension" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('plan.planForm.exitLoopTension')" prop="exitLoopTension">
              <el-input-number v-model="form.exitLoopTension" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.planForm.unitTension') }}</h3>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item :label="$t('plan.planForm.entryUnitTension')" prop="entryUnitTension">
              <el-input-number v-model="form.entryUnitTension" :min="0" :precision="4" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('plan.planForm.entryLoopUnitTension')" prop="entryLoopUnitTension">
              <el-input-number v-model="form.entryLoopUnitTension" :min="0" :precision="4" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item :label="$t('plan.planForm.processUnitTension')" prop="processUnitTension">
              <el-input-number v-model="form.processUnitTension" :min="0" :precision="4" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('plan.planForm.exitLoopUnitTension')" prop="exitLoopUnitTension">
              <el-input-number v-model="form.exitLoopUnitTension" :min="0" :precision="4" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item :label="$t('plan.planForm.exitUnitTension')" prop="exitUnitTension">
              <el-input-number v-model="form.exitUnitTension" :min="0" :precision="4" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.otherInfo') }}</h3>
        <el-row>
          <el-col :span="24">
            <el-form-item :label="$t('plan.remark')" prop="remark">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="3"
                :placeholder="$t('plan.remark')"
                show-word-limit
                maxlength="500"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </section>
    </el-form>
    <template #footer>
      <div class="vibe-dialog-footer">
        <ActionButton @click="visible = false">
          <el-icon><Close /></el-icon>
          {{ $t('common.cancel') }}
        </ActionButton>
        <ActionButton
          v-if="showSaveButton"
          variant="primary"
          @click="handleSubmit"
          :loading="submitLoading"
        >
          <el-icon><Check /></el-icon>
          {{ $t('common.save') }}
        </ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Tickets,
  PriceTag,
  Grid,
  Close,
  Check
} from '@element-plus/icons-vue'
import { createPlan, updatePlan } from '@/app/plan/api'
import ActionButton from '@/components/common/ActionButton.vue'

const { t } = useI18n()

const emit = defineEmits(['success'])
const visible = ref(false)
const title = ref('')
const formRef = ref()
const submitLoading = ref(false)
const mode = ref('add')
const rowStatus = ref('')

const getErrorMessage = (error, fallback) => {
  return error?.response?.data?.detail || error?.message || fallback
}

const parsePlanNumber = (value) => Number.parseFloat(String(value || 0))

const stringifyPlanNumber = (value) => String(value ?? '')

// 只有在 add 或 edit 模式且状态为 planned 时才可编辑
const isReadOnly = computed(() => {
  if (mode.value === 'add') return false
  if (mode.value === 'view') return true
  // edit 模式下，非 planned 状态强制只读
  return rowStatus.value !== 'planned'
})

// 是否显示保存按钮
const showSaveButton = computed(() => !isReadOnly.value)

const form = reactive({
  id: null,
  coilNo: '',
  grade: '',
  spec: '',
  weight: undefined,
  thickness: undefined,
  width: undefined,
  materialStatus: '',
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
  remark: ''
})

const computedRules = computed(() => ({
  materialStatus: [
    { required: true, message: t('plan.rules.materialStatusRequired'), trigger: 'change' }
  ],
  coilNo: [
    { required: true, message: t('plan.rules.coilNoRequired'), trigger: 'blur' },
    { min: 1, max: 50, message: t('plan.rules.coilNoLength'), trigger: 'blur' }
  ],
  grade: [
    { required: true, message: t('plan.rules.gradeRequired'), trigger: 'blur' },
    { min: 1, max: 20, message: t('plan.rules.gradeLength'), trigger: 'blur' }
  ],
  spec: [
    { required: true, message: t('plan.rules.specRequired'), trigger: 'blur' }
  ],
  weight: [
    { required: true, message: t('plan.rules.weightRequired'), trigger: 'blur' },
    { type: 'number', min: 0, message: t('plan.rules.weightMin'), trigger: 'blur' }
  ],
  thickness: [
    { required: true, message: t('plan.rules.thicknessRequired'), trigger: 'blur' },
    { type: 'number', min: 0, message: t('plan.rules.thicknessMin'), trigger: 'blur' }
  ],
  width: [
    { required: true, message: t('plan.rules.widthRequired'), trigger: 'blur' },
    { type: 'number', min: 1, message: t('plan.rules.widthMin'), trigger: 'blur' }
  ]
}))

const open = (type, row = null) => {
  mode.value = type
  rowStatus.value = row?.status || ''

  if (type === 'add') {
    title.value = t('plan.add')
  } else if (type === 'edit') {
    title.value = t('plan.edit')
  } else {
    title.value = t('common.detail')
  }

  visible.value = true

  if ((type === 'edit' || type === 'view') && row) {
    form.id = row.id
    form.coilNo = row.coilNo
    form.grade = row.grade
    form.spec = row.spec || ''
    form.weight = parsePlanNumber(row.weight)
    form.thickness = parsePlanNumber(row.thickness)
    form.width = parsePlanNumber(row.width)
    form.materialStatus = row.materialStatus || ''
    form.density = parsePlanNumber(row.density)
    form.entryLength = parsePlanNumber(row.entryLength)
    form.uncoiler1Tension = parsePlanNumber(row.uncoiler1Tension)
    form.exitTension = parsePlanNumber(row.exitTension)
    form.process1Tension = parsePlanNumber(row.process1Tension)
    form.entryLoopTension = parsePlanNumber(row.entryLoopTension)
    form.exitLoopTension = parsePlanNumber(row.exitLoopTension)
    form.entryUnitTension = parsePlanNumber(row.entryUnitTension)
    form.entryLoopUnitTension = parsePlanNumber(row.entryLoopUnitTension)
    form.processUnitTension = parsePlanNumber(row.processUnitTension)
    form.exitLoopUnitTension = parsePlanNumber(row.exitLoopUnitTension)
    form.exitUnitTension = parsePlanNumber(row.exitUnitTension)
    form.remark = row.remark || ''
  } else {
    form.id = null
    form.coilNo = ''
    form.grade = ''
    form.spec = ''
    form.weight = undefined
    form.thickness = undefined
    form.width = undefined
    form.materialStatus = ''
    form.density = 0
    form.entryLength = 0
    form.uncoiler1Tension = 0
    form.exitTension = 0
    form.process1Tension = 0
    form.entryLoopTension = 0
    form.exitLoopTension = 0
    form.entryUnitTension = 0
    form.entryLoopUnitTension = 0
    form.processUnitTension = 0
    form.exitLoopUnitTension = 0
    form.exitUnitTension = 0
    form.remark = ''
  }
}

const handleClose = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const submitData = {
          coilNo: form.coilNo.trim(),
          grade: form.grade.trim(),
          spec: form.spec.trim(),
          weight: stringifyPlanNumber(form.weight),
          thickness: stringifyPlanNumber(form.thickness),
          width: stringifyPlanNumber(form.width),
          materialStatus: form.materialStatus,
          density: stringifyPlanNumber(form.density),
          entryLength: stringifyPlanNumber(form.entryLength),
          uncoiler1Tension: stringifyPlanNumber(form.uncoiler1Tension),
          exitTension: stringifyPlanNumber(form.exitTension),
          process1Tension: stringifyPlanNumber(form.process1Tension),
          entryLoopTension: stringifyPlanNumber(form.entryLoopTension),
          exitLoopTension: stringifyPlanNumber(form.exitLoopTension),
          entryUnitTension: stringifyPlanNumber(form.entryUnitTension),
          entryLoopUnitTension: stringifyPlanNumber(form.entryLoopUnitTension),
          processUnitTension: stringifyPlanNumber(form.processUnitTension),
          exitLoopUnitTension: stringifyPlanNumber(form.exitLoopUnitTension),
          exitUnitTension: stringifyPlanNumber(form.exitUnitTension),
          remark: form.remark?.trim() || undefined
        }

        if (form.id) {
          await updatePlan(form.id, submitData)
        } else {
          await createPlan(submitData)
        }

        ElMessage.success(t('plan.messages.saveSuccess'))
        visible.value = false
        emit('success')
      } catch (error) {
        ElMessage.error(getErrorMessage(error, t('common.saveError')))
      } finally {
        submitLoading.value = false
      }
    }
  })
}

defineExpose({
  open
})
</script>

<style scoped>
.plan-form {
  gap: 28px;
}

.plan-form :deep(.el-row) {
  row-gap: 18px;
}

.plan-form :deep(.el-row + .el-row) {
  margin-top: 18px;
}

.plan-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.plan-form :deep(.el-form-item__label) {
  height: auto;
  margin-bottom: 8px;
  padding: 0;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 520;
  line-height: 1.35;
}

.plan-form :deep(.el-input__prefix) {
  color: var(--text-secondary);
}

.plan-form :deep(.el-input__wrapper),
.plan-form :deep(.el-select__wrapper),
.plan-form :deep(.el-input-number .el-input__wrapper),
.plan-form :deep(.el-textarea__inner) {
  min-height: 42px;
  background: var(--table-fixed-bg);
  border-radius: 10px;
  box-shadow: 0 0 0 1px var(--border-secondary) inset;
}

.plan-form :deep(.el-input-number) {
  width: 100%;
}

.plan-form :deep(.el-input-number .el-input__inner) {
  text-align: left;
}

.plan-form :deep(.el-input__wrapper:hover),
.plan-form :deep(.el-select__wrapper:hover),
.plan-form :deep(.el-input-number .el-input__wrapper:hover),
.plan-form :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px var(--border-primary) inset;
}

.plan-form :deep(.el-input.is-disabled .el-input__wrapper),
.plan-form :deep(.el-input-number.is-disabled .el-input__wrapper),
.plan-form :deep(.el-select__wrapper.is-disabled),
.plan-form :deep(.el-textarea.is-disabled .el-textarea__inner) {
  background: var(--bg-primary);
  box-shadow: 0 0 0 1px var(--border-secondary) inset;
}

.plan-form :deep(.el-input.is-disabled .el-input__inner),
.plan-form :deep(.el-input-number.is-disabled .el-input__inner),
.plan-form :deep(.el-select__wrapper.is-disabled .el-select__placeholder),
.plan-form :deep(.el-textarea.is-disabled .el-textarea__inner) {
  color: var(--text-secondary);
  -webkit-text-fill-color: var(--text-secondary);
}

.plan-form :deep(.el-input-number.is-disabled .el-input-number__decrease),
.plan-form :deep(.el-input-number.is-disabled .el-input-number__increase) {
  display: none;
}

:global(.plan-dialog .el-dialog__body) {
  max-height: 66vh;
  overflow-y: auto;
}

:global(.plan-dialog-mask) {
  background-color: var(--el-mask-color);
}

@media (max-width: 960px) {
  :global(.plan-dialog) {
    width: calc(100vw - 32px) !important;
  }
}
</style>
