<!--
  文件路径: /frontend-next-js/src/app/performance/views/quality/index.vue
  功能描述: 质量控制页面，进行产品质量检查与记录
  主要功能:
    - 料卷基本信息展示
    - 质量检查项目录入（表面质量、尺寸、力学性能等）
    - 缺陷记录管理
    - 质量总结与判定
    - 质量等级评定
    - 国际化 (i18n) 支持
    - 日夜模式 (Theme) 适配
-->
<template>
  <div class="quality-control-container page-layout">
    <BaseCard class="quality-card" :title="`${$t('performance.qualityControl')} - ${coilInfo.coilNo}`">
      <template #actions>
        <div class="table-actions">
          <ActionButton @click="handleBack">
            <el-icon><ArrowLeft /></el-icon>
            {{ $t('common.back') }}
          </ActionButton>
          <ActionButton variant="primary" @click="handleSave" :loading="saveLoading">
            <el-icon><Check /></el-icon>
            {{ $t('common.save') }}
          </ActionButton>
          <ActionButton @click="handleReset">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.reset') }}
          </ActionButton>
        </div>
      </template>

      <!-- 料卷基本信息 -->
      <div class="info-section">
        <h3 class="section-title">{{ $t('performance.quality.basicInfo') }}</h3>
        <el-descriptions :column="4" border>
          <el-descriptions-item :label="$t('performance.coilNo')">{{ coilInfo.coilNo }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.grade')">{{ coilInfo.grade }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.weight')">{{ coilInfo.weight }} {{ $t('common.unit.ton') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.startTime')">{{ coilInfo.startTime }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.endTime')">{{ coilInfo.endTime }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.operator')">{{ coilInfo.operator }}</el-descriptions-item>
          <el-descriptions-item :label="$t('performance.common.shift')">{{ coilInfo.shift }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <!-- 质量检查项目 -->
      <div class="quality-section">
        <h3 class="section-title">{{ $t('performance.quality.inspectItems') }}</h3>
        <el-table :data="qualityItems" border stripe class="vibe-table">
          <el-table-column :label="$t('performance.quality.inspectItems')" width="200">
            <template #default="{ row }">
              {{ $t(`quality.control.items.${row.itemKey}`) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.quality.standard')" width="200">
            <template #default="{ row }">
              {{ $t(`quality.control.standards.${row.standardKey}`) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.quality.actual')" width="200">
            <template #default="{ row }">
              <el-input 
                v-model="row.actualValue" 
                :placeholder="$t('performance.form.placeholder', { label: $t('performance.quality.actual') })"
                :disabled="row.disabled"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.quality.result')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.result" :placeholder="$t('performance.common.select')" style="width: 100%;">
                <el-option :label="$t('quality.control.result.qualified')" value="qualified" />
                <el-option :label="$t('quality.control.result.unqualified')" value="unqualified" />
                <el-option :label="$t('quality.control.result.recheck')" value="recheck" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.quality.inspector')" width="150">
            <template #default="{ row }">
              <el-input v-model="row.inspector" :placeholder="$t('performance.quality.inspector')" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.quality.time')" width="180">
            <template #default="{ row }">
              <el-date-picker
                v-model="row.inspectTime"
                type="datetime"
                :placeholder="$t('performance.common.selectTime')"
                style="width: 100%;"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.form.remark')" min-width="200">
            <template #default="{ row }">
              <el-input v-model="row.remark" :placeholder="$t('performance.form.remark')" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <!-- 缺陷记录 -->
      <div class="defect-section">
        <div class="section-header">
          <h3 class="section-title">{{ $t('performance.quality.defectRecords') }}</h3>
          <ActionButton variant="row" size="small" @click="handleAddDefect">
            <el-icon><Plus /></el-icon>
            {{ $t('common.add') }}
          </ActionButton>
        </div>
        <el-table :data="defectRecords" border stripe class="vibe-table">
          <el-table-column prop="position" :label="$t('performance.quality.position')" width="150">
            <template #default="{ row }">
              <el-input v-model="row.position" :placeholder="$t('performance.quality.position')" />
            </template>
          </el-table-column>
          <el-table-column prop="type" :label="$t('performance.quality.defectType')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.type" :placeholder="$t('performance.common.select')" style="width: 100%;">
                <el-option :label="$t('quality.control.defectType.scratch')" value="scratch" />
                <el-option :label="$t('quality.control.defectType.scale')" value="scale" />
                <el-option :label="$t('quality.control.defectType.pit')" value="pit" />
                <el-option :label="$t('quality.control.defectType.wave')" value="wave" />
                <el-option :label="$t('quality.control.defectType.edgeCrack')" value="edgeCrack" />
                <el-option :label="$t('quality.control.defectType.other')" value="other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="level" :label="$t('performance.quality.level')" width="120">
            <template #default="{ row }">
              <el-select v-model="row.level" :placeholder="$t('performance.quality.level')" style="width: 100%;">
                <el-option :label="$t('quality.control.level.light')" value="light" />
                <el-option :label="$t('quality.control.level.normal')" value="normal" />
                <el-option :label="$t('quality.control.level.severe')" value="severe" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="length" :label="$t('performance.quality.length')" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.length" :min="0" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('performance.common.description')" min-width="200">
            <template #default="{ row }">
              <el-input v-model="row.description" :placeholder="$t('performance.common.description')" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.table.operation')" width="100">
            <template #default="{ $index }">
              <ActionButton variant="danger" size="small" @click="handleDeleteDefect($index)">
                {{ $t('common.delete') }}
              </ActionButton>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <!-- 质量总结 -->
      <div class="summary-section">
        <h3 class="section-title">{{ $t('performance.quality.summary') }}</h3>
        <el-form :model="summaryForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('performance.quality.judgment')">
                <el-select v-model="summaryForm.judgment" :placeholder="$t('performance.form.selectPlaceholder', { label: $t('performance.quality.judgment') })" style="width: 100%;">
                  <el-option :label="$t('quality.control.result.qualified')" value="qualified" />
                  <el-option :label="$t('quality.control.result.unqualified')" value="unqualified" />
                  <el-option :label="$t('quality.control.result.concession')" value="concession" />
                  <el-option :label="$t('quality.control.result.recheck')" value="recheck" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('performance.quality.qualityGrade')">
                <el-select v-model="summaryForm.grade" :placeholder="$t('performance.form.selectPlaceholder', { label: $t('performance.quality.qualityGrade') })" style="width: 100%;">
                  <el-option :label="$t('quality.control.grade.excellent')" value="excellent" />
                  <el-option :label="$t('quality.control.grade.first')" value="first" />
                  <el-option :label="$t('quality.control.grade.qualified')" value="qualified" />
                  <el-option :label="$t('quality.control.grade.unqualified')" value="unqualified" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item :label="$t('performance.quality.comment')">
            <el-input
              v-model="summaryForm.comment"
              type="textarea"
              :rows="4"
              :placeholder="$t('performance.form.placeholder', { label: $t('performance.quality.comment') })"
            />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('performance.quality.inspector')">
                <el-input v-model="summaryForm.inspector" :placeholder="$t('performance.quality.inspector')" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('performance.common.date')">
                <el-date-picker
                  v-model="summaryForm.inspectDate"
                  type="date"
                  :placeholder="$t('performance.common.selectDate')"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPerformanceById } from '@/app/performance/api'
import { getQualityList, getQualityById, createQuality, updateQuality } from '@/app/quality/api'
import { useUserStore } from '@/store/user'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const saveLoading = ref(false)
const qualityId = ref(null)

const getDefaultInspectDate = () => new Date().toISOString().split('T')[0]
const formatInspectTime = (value) => (value ? `${value}T00:00:00` : null)
const QUALITY_ITEM_KEYS = [
  'surfaceQuality',
  'thicknessDeviation',
  'widthDeviation',
  'flatness',
  'edgeQuality',
  'coilShape',
  'sideBending',
  'tensileStrength',
  'yieldStrength',
  'elongation',
  'hardness',
  'bendingPerformance',
  'chemicalComposition',
  'grainSize'
]
const LEGACY_RESULT_MAP = {
  '合格': 'qualified',
  '不合格': 'unqualified',
  '待复检': 'recheck',
  '让步接收': 'concession'
}
const LEGACY_GRADE_MAP = {
  '优等品': 'excellent',
  '一等品': 'first',
  '合格品': 'qualified',
  '不合格品': 'unqualified'
}
const LEGACY_LEVEL_MAP = {
  '轻微': 'light',
  '一般': 'normal',
  '严重': 'severe'
}
const LEGACY_DEFECT_TYPE_MAP = {
  '表面划伤': 'scratch',
  '氧化皮': 'scale',
  '凹坑': 'pit',
  '波浪': 'wave',
  '边裂': 'edgeCrack',
  '其他': 'other'
}
const LEGACY_ITEM_MAP = {
  '表面质量': 'surfaceQuality',
  '厚度偏差': 'thicknessDeviation',
  '宽度偏差': 'widthDeviation',
  '平整度': 'flatness',
  '边部质量': 'edgeQuality',
  '卷形': 'coilShape',
  '侧边弯曲度': 'sideBending',
  '抗拉强度': 'tensileStrength',
  '屈服强度': 'yieldStrength',
  '断后伸长率': 'elongation',
  '硬度': 'hardness',
  '弯曲性能': 'bendingPerformance',
  '化学成分': 'chemicalComposition',
  '晶粒度': 'grainSize'
}
const toCanonicalValue = (value, legacyMap) => legacyMap[value] || value || ''
const createDefaultQualityItems = () => QUALITY_ITEM_KEYS.map(itemKey => ({
  itemKey,
  standardKey: itemKey,
  actualValue: '',
  result: '',
  inspector: '',
  inspectTime: '',
  remark: ''
}))
const normalizeQualityItems = (items = []) => {
  if (!items.length) {
    return createDefaultQualityItems()
  }

  return items.map((item, index) => {
    const fallbackKey = QUALITY_ITEM_KEYS[index] || item.itemKey || ''
    const itemKey = item.itemKey || LEGACY_ITEM_MAP[item.item] || fallbackKey
    return {
      itemKey,
      standardKey: item.standardKey || itemKey,
      actualValue: item.actualValue || '',
      result: toCanonicalValue(item.result, LEGACY_RESULT_MAP),
      inspector: item.inspector || '',
      inspectTime: item.inspectTime || '',
      remark: item.remark || ''
    }
  })
}

// 料卷基本信息
const coilInfo = ref({
  coilNo: '',
  grade: '',
  spec: '',
  weight: 0,
  startTime: '',
  endTime: '',
  operator: '',
  shift: ''
})

// 质量检查项目
const qualityItems = ref(createDefaultQualityItems())

// 缺陷记录
const defectRecords = ref([])

// 质量总结
const summaryForm = reactive({
  judgment: '',
  grade: '',
  comment: '',
  inspector: '',
  inspectDate: ''
})

// 加载数据
const loadData = async () => {
  try {
    const performance = await getPerformanceById(route.params.id)

    coilInfo.value = {
      coilNo: performance.coilNo || '',
      grade: performance.grade || '',
      spec: performance.spec || '',
      weight: performance.weight || 0,
      startTime: performance.startTime || '',
      endTime: performance.endTime || '',
      operator: performance.operator || '',
      shift: performance.shift || ''
    }

    summaryForm.inspector = userStore.username || ''
    summaryForm.inspectDate = getDefaultInspectDate()

    if (!coilInfo.value.coilNo) {
      return
    }

    const existing = await getQualityList({
      coilNo: coilInfo.value.coilNo,
      pageSize: 1
    })

    const currentRecord = existing?.items?.[0]
    if (!currentRecord?.id) {
      return
    }

    qualityId.value = currentRecord.id
    const detail = await getQualityById(currentRecord.id)

    if (detail?.qualityItems?.length) {
      qualityItems.value = normalizeQualityItems(detail.qualityItems)
    }

    defectRecords.value = (detail?.defects || []).map(defect => ({
      id: defect.id,
      position: defect.position,
      type: toCanonicalValue(defect.defectType, LEGACY_DEFECT_TYPE_MAP),
      level: toCanonicalValue(defect.level, LEGACY_LEVEL_MAP),
      length: defect.length,
      description: defect.description
    }))

    summaryForm.judgment = toCanonicalValue(detail.judgment, LEGACY_RESULT_MAP)
    summaryForm.grade = toCanonicalValue(detail.qualityGrade, LEGACY_GRADE_MAP)
    summaryForm.comment = detail.comment || ''
    summaryForm.inspector = detail.inspector || userStore.username || ''
    summaryForm.inspectDate = detail.inspectTime ? detail.inspectTime.split('T')[0] : summaryForm.inspectDate
  } catch (error) {
    console.error('加载质量数据失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
  }
}

// 返回
const handleBack = () => {
  router.push('/performance/list')
}

// 保存
const handleSave = async () => {
  try {
    await ElMessageBox.confirm(t('performance.messages.confirmSave'), t('common.tip'), {
      type: 'info'
    })
    
    saveLoading.value = true

    const payload = {
      coilNo: coilInfo.value.coilNo,
      grade: coilInfo.value.grade,
      spec: coilInfo.value.spec,
      weight: coilInfo.value.weight,
      startTime: coilInfo.value.startTime || null,
      endTime: coilInfo.value.endTime || null,
      operator: coilInfo.value.operator || null,
      shift: coilInfo.value.shift || null,
      qualityItems: qualityItems.value,
      judgment: summaryForm.judgment || null,
      qualityGrade: summaryForm.grade || null,
      comment: summaryForm.comment,
      inspector: summaryForm.inspector,
      inspectTime: formatInspectTime(summaryForm.inspectDate),
      defects: defectRecords.value.map(defect => ({
        position: defect.position,
        defectType: defect.type || null,
        level: defect.level || null,
        length: defect.length,
        description: defect.description
      }))
    }

    if (qualityId.value) {
      const updated = await updateQuality(qualityId.value, payload)
      qualityId.value = updated?.id || qualityId.value
    } else {
      const created = await createQuality(payload)
      qualityId.value = created?.id || null
    }
    
    ElMessage.success(t('performance.messages.saveSuccess'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存质量信息失败:', error)
      ElMessage.error(t('quality.control.saveFailed'))
    }
  } finally {
    saveLoading.value = false
  }
}

// 重置
const handleReset = () => {
  qualityItems.value = createDefaultQualityItems()
  
  defectRecords.value = []
  
  summaryForm.judgment = ''
  summaryForm.grade = ''
  summaryForm.comment = ''
  summaryForm.inspector = userStore.username || ''
  summaryForm.inspectDate = getDefaultInspectDate()
}

// 添加缺陷
const handleAddDefect = () => {
  defectRecords.value.push({
    position: '',
    type: '',
    level: '',
    length: 0,
    description: ''
  })
}

// 删除缺陷
const handleDeleteDefect = (index) => {
  defectRecords.value.splice(index, 1)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.quality-control-container {
  height: 100%;
  animation: fadeIn var(--transition-normal);
}

.info-section,
.quality-section,
.defect-section,
.summary-section {
  margin: var(--space-lg) 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.section-title {
  margin: 0 0 var(--space-md) 0;
  font-size: 16px;
  font-weight: 590;
  color: var(--text-primary);
}

:deep(.el-divider--horizontal) {
  margin: 24px 0;
  border-top: 1px solid var(--border-primary);
}

:deep(.el-descriptions__label) {
  font-weight: 500;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
}

:deep(.el-descriptions__content) {
  color: var(--text-primary);
  background-color: var(--bg-primary);
}

</style>
