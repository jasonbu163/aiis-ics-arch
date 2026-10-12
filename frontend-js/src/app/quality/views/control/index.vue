<!--
  文件路径: /frontend-next-js/src/app/quality/views/control/index.vue
  功能描述: 质量控制页面，进行质量检验和缺陷记录
  主要功能:
    - 料卷基本信息展示
    - 质量检查项目录入
    - 缺陷记录管理
    - 质量总结和钢卷图片上传
-->
<template>
  <div class="quality-control-container page-layout">
    <BaseCard class="quality-card" :title="$t('quality.control.title', { coilNo: coilInfo.coilNo })">
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

      <div class="info-section">
        <h3>{{ $t('quality.control.basicInfo') }}</h3>
        <el-descriptions :column="4" border>
          <el-descriptions-item :label="$t('quality.control.fields.coilNo')">{{ coilInfo.coilNo }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.grade')">{{ coilInfo.grade }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.weight')">{{ coilInfo.weight }} {{ $t('common.unit.ton') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.productionTime')">{{ coilInfo.startTime }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.completeTime')">{{ coilInfo.endTime }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.operator')">{{ coilInfo.operator }}</el-descriptions-item>
          <el-descriptions-item :label="$t('quality.control.fields.shift')">{{ coilInfo.shift }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <div class="quality-section">
        <h3>{{ $t('quality.control.inspectionItems') }}</h3>
        <el-table :data="qualityItems" border stripe class="vibe-table">
          <el-table-column :label="$t('quality.control.fields.item')" width="200">
            <template #default="{ row }">{{ displayText(row.item) }}</template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.standard')" width="200">
            <template #default="{ row }">{{ displayText(row.standard) }}</template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.actualValue')" width="200">
            <template #default="{ row }">
              <el-input 
                v-model="row.actualValue" 
                :placeholder="$t('quality.control.placeholder.actualValue')"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.result')" width="150">
            <template #default="{ row }">
              <el-select v-model="row.result" :placeholder="$t('quality.control.placeholder.select')" style="width: 100%;">
                <el-option :label="$t('quality.control.result.qualified')" value="qualified" />
                <el-option :label="$t('quality.control.result.unqualified')" value="unqualified" />
                <el-option :label="$t('quality.control.result.recheck')" value="recheck" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.inspector')" width="150">
            <template #default="{ row }">
              <el-input v-model="row.inspector" :placeholder="$t('quality.control.placeholder.inspector')" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.inspectTime')" width="180">
            <template #default="{ row }">
              <el-date-picker
                v-model="row.inspectTime"
                type="datetime"
                :placeholder="$t('quality.control.placeholder.inspectTime')"
                style="width: 100%;"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.remark')" min-width="200">
            <template #default="{ row }">
              <el-input v-model="row.remark" :placeholder="$t('quality.control.placeholder.remark')" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <div class="defect-section">
        <div class="section-header">
          <h3>{{ $t('quality.control.defectRecords') }}</h3>
          <ActionButton variant="row" size="small" @click="handleAddDefect">
            <el-icon><Plus /></el-icon>
            {{ $t('quality.control.addDefect') }}
          </ActionButton>
        </div>
        <el-table :data="defectRecords" border stripe table-layout="fixed" class="vibe-table">
          <el-table-column prop="position" :label="$t('quality.control.fields.position')" width="180">
            <template #default="{ row }">
              <el-input v-model="row.position" :placeholder="$t('quality.control.placeholder.position')" />
            </template>
          </el-table-column>
          <el-table-column prop="defectType" :label="$t('quality.control.fields.defectType')" width="120">
            <template #default="{ row }">
              <el-select v-model="row.defectType" :placeholder="$t('quality.control.placeholder.select')" style="width: 100%;">
                <el-option :label="$t('quality.control.defectType.scratch')" value="scratch" />
                <el-option :label="$t('quality.control.defectType.scale')" value="scale" />
                <el-option :label="$t('quality.control.defectType.pit')" value="pit" />
                <el-option :label="$t('quality.control.defectType.wave')" value="wave" />
                <el-option :label="$t('quality.control.defectType.edgeCrack')" value="edgeCrack" />
                <el-option :label="$t('quality.control.defectType.other')" value="other" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="level" :label="$t('quality.control.fields.defectLevel')" width="100">
            <template #default="{ row }">
              <el-select v-model="row.level" :placeholder="$t('quality.control.placeholder.level')" style="width: 100%;">
                <el-option :label="$t('quality.control.level.light')" value="light" />
                <el-option :label="$t('quality.control.level.normal')" value="normal" />
                <el-option :label="$t('quality.control.level.severe')" value="severe" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="length" :label="$t('quality.control.fields.length')" width="100">
            <template #default="{ row }">
              <el-input-number v-model="row.length" :min="0" size="small" style="width: 100%;" />
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('quality.control.fields.description')" min-width="200">
            <template #default="{ row }">
              <el-input v-model="row.description" :placeholder="$t('quality.control.placeholder.description')" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('quality.control.fields.defectImage')" width="120">
            <template #default="{ row }">
              <div class="defect-image-cell">
                <el-upload
                  v-if="!row.imageUrl"
                  class="defect-uploader"
                  :show-file-list="false"
                  :auto-upload="false"
                  accept="image/*"
                  :on-change="(file) => handleDefectImageChange(row, file)"
                >
                  <el-icon class="upload-icon"><Plus /></el-icon>
                </el-upload>
                <div v-else class="image-preview-wrapper">
                  <img :src="row.imageUrl" class="preview-image" @click="handleImagePreview({ url: row.imageUrl })" />
                  <el-icon class="delete-icon" @click="row.imageUrl = ''"><Close /></el-icon>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="80" fixed="right">
            <template #default="{ $index }">
              <ActionButton variant="danger" size="small" @click="handleDeleteDefect($index)">
                {{ $t('common.delete') }}
              </ActionButton>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-divider />

      <div class="summary-section">
        <h3>{{ $t('quality.control.summary') }}</h3>
        <el-form :model="summaryForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('quality.control.fields.judgment')">
                <el-select v-model="summaryForm.judgment" :placeholder="$t('quality.control.placeholder.judgment')" style="width: 100%;">
                  <el-option :label="$t('quality.control.result.qualified')" value="qualified" />
                  <el-option :label="$t('quality.control.result.unqualified')" value="unqualified" />
                  <el-option :label="$t('quality.control.result.concession')" value="concession" />
                  <el-option :label="$t('quality.control.result.recheck')" value="recheck" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('quality.control.fields.qualityGrade')">
                <el-select v-model="summaryForm.grade" :placeholder="$t('quality.control.placeholder.qualityGrade')" style="width: 100%;">
                  <el-option :label="$t('quality.control.grade.excellent')" value="excellent" />
                  <el-option :label="$t('quality.control.grade.first')" value="first" />
                  <el-option :label="$t('quality.control.grade.qualified')" value="qualified" />
                  <el-option :label="$t('quality.control.grade.unqualified')" value="unqualified" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item :label="$t('quality.control.fields.comment')">
            <el-input
              v-model="summaryForm.comment"
              type="textarea"
              :rows="4"
              :placeholder="$t('quality.control.placeholder.comment')"
            />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('quality.control.fields.inspector')">
                <el-input v-model="summaryForm.inspector" :placeholder="$t('quality.control.placeholder.inspectorName')" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('quality.control.fields.inspectDate')">
                <el-date-picker
                  v-model="summaryForm.inspectDate"
                  type="date"
                  :placeholder="$t('quality.control.placeholder.inspectDate')"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <el-divider />

      <div class="coil-image-section">
        <h3>{{ $t('quality.control.coilImages') }}</h3>
        <el-upload
          v-model:file-list="coilImages"
          list-type="picture-card"
          :auto-upload="false"
          :limit="10"
          accept="image/*"
          multiple
          :on-preview="handleImagePreview"
          :on-exceed="handleExceed"
        >
          <el-icon><Plus /></el-icon>
          <template #tip>
            <div class="upload-tip">{{ $t('quality.control.uploadTip') }}</div>
          </template>
        </el-upload>
      </div>

      <el-dialog v-model="imagePreviewVisible" :title="$t('quality.control.imagePreview')" width="600px">
        <img :src="previewImageUrl" style="width: 100%;" :alt="$t('quality.control.previewAlt')" />
      </el-dialog>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getQualityById, createQuality, updateQuality } from '@/app/quality/api'
import { useUserStore } from '@/store/user'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t, te } = useI18n()
const saveLoading = ref(false)

const isNewRecord = route.params.id === 'new'

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

const qualityItems = ref([
  { item: 'quality.control.items.surfaceQuality', standard: 'quality.control.standards.surfaceQuality', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.thicknessDeviation', standard: 'quality.control.standards.thicknessDeviation', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.widthDeviation', standard: 'quality.control.standards.widthDeviation', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.flatness', standard: 'quality.control.standards.flatness', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.edgeQuality', standard: 'quality.control.standards.edgeQuality', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.coilShape', standard: 'quality.control.standards.coilShape', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.sideBending', standard: 'quality.control.standards.sideBending', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.tensileStrength', standard: 'quality.control.standards.tensileStrength', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.yieldStrength', standard: 'quality.control.standards.yieldStrength', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.elongation', standard: 'quality.control.standards.elongation', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.hardness', standard: 'quality.control.standards.hardness', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.bendingPerformance', standard: 'quality.control.standards.bendingPerformance', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.chemicalComposition', standard: 'quality.control.standards.chemicalComposition', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' },
  { item: 'quality.control.items.grainSize', standard: 'quality.control.standards.grainSize', actualValue: '', result: '', inspector: '', inspectTime: '', remark: '' }
])

const defectRecords = ref([])

const summaryForm = reactive({
  judgment: '',
  grade: '',
  comment: '',
  inspector: '',
  inspectDate: ''
})

const coilImages = ref([])
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const displayText = (value) => te(value) ? t(value) : value

const loadData = async () => {
  if (isNewRecord) {
    coilInfo.value = {
      coilNo: '',
      grade: '',
      spec: '',
      weight: 0,
      startTime: '',
      endTime: '',
      operator: '',
      shift: ''
    }
    summaryForm.inspector = userStore.username || ''
    summaryForm.inspectDate = new Date().toISOString().split('T')[0]
    return
  }
  
  const coilId = route.params.id
  try {
    const res = await getQualityById(coilId)
    if (res) {
      coilInfo.value = {
        coilNo: res.coilNo || '',
        grade: res.grade || '',
        spec: res.spec || '',
        weight: res.weight || 0,
        startTime: res.startTime || '',
        endTime: res.endTime || '',
        operator: res.operator || '',
        shift: res.shift || ''
      }
      
      if (res.qualityItems) {
        qualityItems.value = res.qualityItems
      }
      
      if (res.defects) {
        defectRecords.value = res.defects.map(d => ({
          id: d.id,
          position: d.position,
          defectType: d.defectType,
          level: d.level,
          length: d.length,
          description: d.description,
          imageUrl: d.imageUrl
        }))
      }
      
      summaryForm.judgment = res.judgment || ''
      summaryForm.grade = res.qualityGrade || ''
      summaryForm.comment = res.comment || ''
      summaryForm.inspector = res.inspector || userStore.username || ''
      summaryForm.inspectDate = res.inspectTime ? res.inspectTime.split('T')[0] : new Date().toISOString().split('T')[0]
      
      if (res.coilImages) {
        coilImages.value = res.coilImages.map((url, index) => ({
          name: `image-${index}`,
          url: url
        }))
      }
    }
  } catch (error) {
    console.error(t('quality.control.loadFailed'), error)
  }
}

const handleBack = () => {
  router.push('/quality/list')
}

const handleSave = async () => {
  try {
    await ElMessageBox.confirm(t('quality.control.confirmSave'), t('common.tip'), {
      type: 'info'
    })
    saveLoading.value = true
    
    const data = {
      coilNo: coilInfo.value.coilNo,
      grade: coilInfo.value.grade,
      spec: coilInfo.value.spec,
      weight: coilInfo.value.weight,
      startTime: coilInfo.value.startTime,
      endTime: coilInfo.value.endTime,
      operator: coilInfo.value.operator,
      shift: coilInfo.value.shift,
      qualityItems: qualityItems.value.map(item => ({
        ...item,
        item: displayText(item.item),
        standard: displayText(item.standard)
      })),
      judgment: summaryForm.judgment,
      qualityGrade: summaryForm.grade,
      comment: summaryForm.comment,
      inspector: summaryForm.inspector,
      inspectTime: summaryForm.inspectDate,
      coilImages: coilImages.value.map(f => f.url || f.response?.url).filter(Boolean),
      defects: defectRecords.value.map(d => ({
        position: d.position,
        defectType: d.defectType,
        level: d.level,
        length: d.length,
        description: d.description,
        imageUrl: d.imageUrl
      }))
    }
    
    if (isNewRecord) {
      await createQuality(data)
    } else {
      await updateQuality(route.params.id, data)
    }
    
    ElMessage.success(t('quality.control.saveSuccess'))
    router.push('/quality/list')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('quality.control.saveFailed'))
    }
  } finally {
    saveLoading.value = false
  }
}

const handleReset = () => {
  qualityItems.value.forEach(item => {
    item.actualValue = ''
    item.result = ''
    item.inspector = ''
    item.inspectTime = ''
    item.remark = ''
  })
  defectRecords.value = []
  coilImages.value = []
  summaryForm.judgment = ''
  summaryForm.grade = ''
  summaryForm.comment = ''
}

const handleAddDefect = () => {
  defectRecords.value.push({
    position: '',
    defectType: '',
    level: '',
    length: 0,
    description: '',
    imageUrl: ''
  })
}

const handleDeleteDefect = (index) => {
  defectRecords.value.splice(index, 1)
}

const handleDefectImageChange = (row, file) => {
  if (file.raw) {
    row.imageUrl = URL.createObjectURL(file.raw)
  }
}

const handleImagePreview = (file) => {
  previewImageUrl.value = file.url
  imagePreviewVisible.value = true
}

const handleExceed = () => {
  ElMessage.warning(t('quality.control.imageLimitExceeded'))
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.quality-control-container {
  height: 100%;
}

.info-section,
.quality-section,
.defect-section,
.summary-section,
.coil-image-section {
  margin: var(--space-lg) 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

h3 {
  margin: 0 0 var(--space-md) 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

:deep(.el-divider--horizontal) {
  margin: 24px 0;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
  background-color: var(--bg-secondary);
}

.upload-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: var(--space-sm);
}

.defect-image-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.defect-uploader {
  width: 60px;
  height: 60px;
  border: 1px dashed var(--border-primary);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: border-color var(--transition-normal);
}

.defect-uploader:hover {
  border-color: var(--primary);
}

.upload-icon {
  font-size: 20px;
  color: var(--text-tertiary);
}

.image-preview-wrapper {
  position: relative;
  width: 60px;
  height: 60px;
}

.preview-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
}

.delete-icon {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 18px;
  height: 18px;
  background: var(--danger);
  border-radius: 50%;
  color: var(--bg-primary);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.delete-icon:hover {
  background: var(--danger);
}

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
}

</style>
