<!--
  文件路径: /frontend-next-js/src/app/maintenance/components/MaintenanceCompleteDialog.vue
  功能描述: 完成保养操作对话框组件
  主要功能:
    - 展示待保养设备信息
    - 记录实际完成时间、操作人和备注
    - 提交更新并将状态回归正常
-->
<template>
  <el-dialog
    v-model="visible"
    :title="$t('maintenance.log.dialog.completeTitle')"
    width="920px"
    class="standard-form-dialog"
    destroy-on-close
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="standard-dialog-form">
      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.equipmentInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item :label="$t('maintenance.log.dialog.equipmentName')">
            <el-input v-model="form.maintenanceName" disabled />
          </el-form-item>
          <el-form-item class="form-item-wide" :label="$t('maintenance.log.dialog.maintenanceContent')">
            <el-input v-model="form.content" type="textarea" :rows="3" disabled />
          </el-form-item>
        </div>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.timeInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item :label="$t('maintenance.log.dialog.completeDate')" prop="completeDate">
            <el-date-picker
              v-model="form.completeDate"
              type="datetime"
              :placeholder="$t('maintenance.log.dialog.completeDatePlaceholder')"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.dialog.operator')" prop="operator">
            <el-input v-model="form.operator" :placeholder="$t('maintenance.log.dialog.operatorPlaceholder')" />
          </el-form-item>
          <el-form-item class="form-item-wide" :label="$t('maintenance.log.dialog.completeRemark')" prop="remark">
            <el-input v-model="form.remark" type="textarea" :rows="3" :placeholder="$t('maintenance.log.dialog.completeRemarkPlaceholder')" />
          </el-form-item>
        </div>
      </section>
    </el-form>

    <template #footer>
      <div class="vibe-dialog-footer">
        <ActionButton variant="secondary" @click="visible = false">{{ $t('common.cancel') }}</ActionButton>
        <ActionButton variant="primary" :loading="loading" @click="handleSubmit">{{ $t('common.confirm') }}</ActionButton>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'

const { t } = useI18n()

const props = defineProps({
  modelValue: Boolean,
  rowData: {
    type: Object,
    default: () => ({})
  },
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref()
const form = reactive({
  id: null,
  maintenanceName: '',
  content: '',
  completeDate: '',
  operator: '',
  remark: ''
})

const rules = computed(() => ({
  completeDate: [
    { required: true, message: t('common.pleaseSelect'), trigger: 'change' }
  ],
  operator: [
    { required: true, message: t('common.pleaseInput'), trigger: 'blur' }
  ]
}))

watch(() => props.rowData, (newVal) => {
  if (newVal && newVal.id) {
    form.id = newVal.id
    form.maintenanceName = newVal.maintenanceName
    form.content = newVal.content
    form.completeDate = new Date().toISOString().replace('T', ' ').slice(0, 19)
    form.operator = newVal.operator || ''
    form.remark = ''
  }
}, { immediate: true })

const handleClose = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      emit('submit', { ...form })
    }
  })
}
</script>
