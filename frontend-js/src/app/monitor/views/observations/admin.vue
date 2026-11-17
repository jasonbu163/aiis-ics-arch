<!-- 过程曲线配置与历史记录管理。 -->
<template>
  <div class="page-layout">
    <BaseCard :title="t('monitor.observation.management')">
      <el-tabs v-model="active">
        <el-tab-pane :label="t('equipment.observation.curveConfig')" name="curves">
          <div class="table-actions">
            <ActionButton variant="primary" @click="open()">{{ t('equipment.observation.add') }}</ActionButton>
            <ActionButton @click="columns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
          </div>
          <el-table :key="columns.version.value" :data="rows" border @header-dragend="columns.onHeaderDragEnd">
            <el-table-column prop="curveGroupKey" :label="t('equipment.observation.key')" :width="columns.widths.curveGroupKey" :min-width="140" />
            <el-table-column prop="category" :label="t('equipment.observation.category')" :width="columns.widths.category" :min-width="110" />
            <el-table-column prop="titleZh" :label="t(locale.startsWith('en') ? 'equipment.observation.titleEn' : 'equipment.observation.titleZh')" :width="columns.widths.titleZh" :min-width="160">
              <template #default="{ row }">{{ locale.startsWith('en') ? row.titleEn : row.titleZh }}</template>
            </el-table-column>
            <el-table-column prop="enabled" :label="t('equipment.observation.enabled')" :width="columns.widths.enabled" :min-width="100" />
            <el-table-column :label="t('equipment.observation.actions')" width="120">
              <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open(row)">{{ t('equipment.observation.edit') }}</ActionButton></div></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane :label="t('monitor.observation.energyConfig')" name="energy">
          <EnergyAdmin v-if="active === 'energy'" kind="config" />
        </el-tab-pane>
      </el-tabs>
    </BaseCard>
    <el-dialog v-model="dialog" :title="t(editing ? 'equipment.observation.edit' : 'equipment.observation.add')"
      class="standard-form-dialog" width="min(680px, 94vw)">
      <el-form label-position="top">
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.curveGroupKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.category')">
          <el-select v-model="form.category">
            <el-option value="temperature" :label="t('equipment.temperature')" />
            <el-option value="drive" :label="t('equipment.drive')" />
            <el-option value="cleaning" :label="t('equipment.observation.cleaning')" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('equipment.observation.titleZh')"><el-input v-model="form.titleZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.titleEn')"><el-input v-model="form.titleEn" /></el-form-item>
        <el-form-item :label="t('equipment.observation.sortOrder')"><el-input-number v-model="form.sortOrder" /></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item :label="t('equipment.observation.items')">
          <div class="item-list">
            <div v-for="(item, index) in form.series" :key="index" class="item-row">
              <el-select v-model="item.metricKey" filterable>
                <el-option v-for="metric in available" :key="metric.metricKey" :value="metric.metricKey"
                  :label="locale.startsWith('en') ? metric.nameEn : metric.nameZh" />
              </el-select>
              <el-switch v-model="item.enabled" />
              <ActionButton size="small" @click="form.series.splice(index, 1)">{{ t('equipment.observation.remove') }}</ActionButton>
            </div>
            <ActionButton size="small" @click="form.series.push({ metricKey: '', enabled: true })">{{ t('equipment.observation.addItem') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
        <ActionButton variant="primary" :loading="saving" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import EnergyAdmin from '../../components/observations/EnergyAdmin.vue'
import { metrics } from '@/app/equipment/api/observations'
import { curves, createCurve, updateCurve } from '../../api/observations'

const { t, locale } = useI18n()
const columns = useTableColumnWidths('observation.curves', {
  curveGroupKey: { width: 180, minWidth: 140 }, category: { width: 130, minWidth: 110 },
  titleZh: { width: 220, minWidth: 160 }, enabled: { width: 120, minWidth: 100 }
})
const active = ref('curves')
const rows = ref([])
const metricRows = ref([])
const dialog = ref(false)
const editing = ref(false)
const saving = ref(false)
const form = reactive({})
const available = computed(() => metricRows.value.filter(metric => metric.category === form.category && metric.valueType === 'number'))
function open(row) {
  editing.value = !!row
  for (const key of Object.keys(form)) delete form[key]
  Object.assign(form, row ? JSON.parse(JSON.stringify(row)) : {
    curveGroupKey: '', category: 'temperature', titleZh: '', titleEn: '', enabled: true, sortOrder: 0, series: []
  })
  dialog.value = true
}
async function load() { [rows.value, metricRows.value] = await Promise.all([curves(), metrics()]) }
async function save() {
  saving.value = true
  try {
    const payload = JSON.parse(JSON.stringify(form))
    if (editing.value) { delete payload.curveGroupKey; await updateCurve(form.curveGroupKey, payload) }
    else await createCurve(payload)
    dialog.value = false
    await load()
  } finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
.item-list { display: grid; gap: 8px; width: 100%; }
.item-row { display: flex; align-items: center; gap: 10px; }
.item-row .el-select { flex: 1; }
</style>
