<!--
  文件路径: /frontend-next-js/src/app/maintenance/components/MaintenanceFormDialog.vue
  功能描述: 保养记录新增/编辑对话框组件
  主要功能:
    - 设备选择与自动填充信息
    - 保养内容与周期编辑
    - 表单校验与国际化支持
-->
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="920px"
    class="standard-form-dialog"
    destroy-on-close
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="standard-dialog-form">
      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.equipmentInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item class="form-item-wide" :label="$t('maintenance.log.dialog.selectEquipment')" prop="maintenanceId">
            <el-select
              v-model="form.maintenanceId"
              :placeholder="$t('maintenance.log.dialog.equipmentNamePlaceholder')"
              filterable
              @change="handleEquipmentChange"
            >
              <el-option
                v-for="item in equipmentList"
                :key="item.id"
                :label="`${item.name} (${item.code})`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.dialog.equipmentName')">
            <el-input v-model="form.maintenanceName" :placeholder="$t('maintenance.log.dialog.equipmentNameAuto')" disabled />
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.dialog.equipmentCode')">
            <el-input v-model="form.maintenanceCode" :placeholder="$t('maintenance.log.dialog.equipmentNameAuto')" disabled />
          </el-form-item>
        </div>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.maintenanceInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item :label="$t('maintenance.log.dialog.maintenanceType')" prop="maintenanceType">
            <el-select v-model="form.maintenanceType" :placeholder="$t('maintenance.log.dialog.maintenanceTypePlaceholder')">
              <el-option :label="$t('maintenance.log.type.daily')" value="daily" />
              <el-option :label="$t('maintenance.log.type.level1')" value="level1" />
              <el-option :label="$t('maintenance.log.type.level2')" value="level2" />
              <el-option :label="$t('maintenance.log.type.level3')" value="level3" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.dialog.cycleDays')" prop="cycleDays">
            <el-input-number v-model="form.cycleDays" :min="1" :max="365" />
          </el-form-item>
          <el-form-item class="form-item-wide" :label="$t('maintenance.log.dialog.maintenanceContent')" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="3"
              :placeholder="$t('maintenance.log.dialog.maintenanceContentPlaceholder')"
            />
          </el-form-item>
        </div>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.timeInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item :label="$t('maintenance.log.dialog.lastDate')" prop="lastDate">
            <el-date-picker
              v-model="form.lastDate"
              type="date"
              :placeholder="$t('maintenance.log.dialog.lastDatePlaceholder')"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.dialog.operator')" prop="operator">
            <el-input v-model="form.operator" :placeholder="$t('maintenance.log.dialog.operatorPlaceholder')" clearable />
          </el-form-item>
        </div>
      </section>

      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('maintenance.log.dialog.otherInfo') }}</h3>
        <div class="dialog-form-grid">
          <el-form-item class="form-item-wide" :label="$t('maintenance.log.dialog.remark')" prop="remark">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="3"
              :placeholder="$t('maintenance.log.dialog.remarkPlaceholder')"
            />
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
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import { getMaintenanceItems } from '@/app/maintenance/api'

const { t } = useI18n()

const props = defineProps({
  modelValue: Boolean,
  title: String,
  formData: {
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
  maintenanceId: null,
  maintenanceName: '',
  maintenanceCode: '',
  maintenanceType: '',
  content: '',
  lastDate: '',
  cycleDays: 30,
  operator: '',
  remark: ''
})

const equipmentList = ref([])

const rules = computed(() => ({
  maintenanceId: [
    { required: true, message: t('maintenance.log.rules.equipmentRequired'), trigger: 'change' }
  ],
  maintenanceType: [
    { required: true, message: t('maintenance.log.rules.typeRequired'), trigger: 'change' }
  ],
  content: [
    { required: true, message: t('maintenance.log.rules.contentRequired'), trigger: 'blur' }
  ],
  lastDate: [
    { required: true, message: t('maintenance.log.rules.lastDateRequired'), trigger: 'change' }
  ],
  cycleDays: [
    { required: true, message: t('maintenance.log.rules.cycleRequired'), trigger: 'blur' }
  ]
}))

watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.keys(form).forEach(key => {
      form[key] = newVal[key] !== undefined ? newVal[key] : (key === 'cycleDays' ? 30 : '')
    })
  }
}, { immediate: true, deep: true })

const loadEquipmentList = async () => {
  try {
    const res = await getMaintenanceItems({ page: 1, pageSize: 100 })
    equipmentList.value = res.items || []
  } catch (error) {
    console.error('加载设备列表失败:', error)
  }
}

const handleEquipmentChange = (val) => {
  const selected = equipmentList.value.find(item => item.id === val)
  if (selected) {
    form.maintenanceName = selected.name
    form.maintenanceCode = selected.code
  }
}

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

onMounted(() => {
  loadEquipmentList()
})
</script>
