<!--
  文件路径: /frontend-next-js/src/app/auxiliary/views/shift/index.vue
  功能描述: 班组管理页面，管理生产班组和排班信息
-->
<template>
  <div class="shift-page page-layout">
    <BaseCard class="shift-main-card" :title="$t('auxiliary.shift.title')">
      <template #actions>
        <ActionButton variant="refresh" :loading="shiftLoading || loading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </ActionButton>
      </template>

      <section class="shift-tools-section">
        <div class="shift-filter-column">
          <BaseCard class="month-filter-card" :title="$t('auxiliary.shift.monthFilter')" compact>
            <el-form class="month-filter-form" label-position="top">
              <el-form-item :label="$t('auxiliary.shift.monthSelect')">
                <el-date-picker
                  v-model="selectedMonth"
                  type="month"
                  :placeholder="$t('auxiliary.shift.monthSelect')"
                  value-format="YYYY-MM"
                  @change="handleMonthChange"
                />
              </el-form-item>
            </el-form>
          </BaseCard>

          <BaseCard :title="$t('auxiliary.shift.rules')" compact>
            <template #actions>
              <ActionButton v-if="canManageShift" variant="secondary" size="small" @click="handleEditRule">
                {{ $t('common.edit') }}
              </ActionButton>
            </template>
            <div class="rule-content">
              <p class="rule-desc">{{ ruleDescription }}</p>
              <div class="rule-item">
                <span>{{ $t('auxiliary.shift.dayShift') }}</span>
                <strong>{{ formatRuleRange(shiftRule.dayShiftStart, shiftRule.dayShiftEnd) }}</strong>
              </div>
              <div v-if="shiftRule.shiftMode === 'three_shift'" class="rule-item">
                <span>{{ $t('auxiliary.shift.middleShift') }}</span>
                <strong>{{ formatRuleRange(shiftRule.middleShiftStart, shiftRule.middleShiftEnd) }}</strong>
              </div>
              <div class="rule-item">
                <span>{{ $t('auxiliary.shift.nightShift') }}</span>
                <strong>{{ formatRuleRange(shiftRule.nightShiftStart, shiftRule.nightShiftEnd) }}</strong>
              </div>
              <div class="rule-item">
                <span>{{ $t('auxiliary.shift.cycle') }}</span>
                <strong>{{ shiftRule.cycleName || $t('auxiliary.shift.fourThree') }}</strong>
              </div>
            </div>
          </BaseCard>
        </div>

        <div class="shift-side-column">
          <BaseCard :title="$t('auxiliary.shift.teamList')" compact>
            <template #actions>
              <ActionButton v-if="canManageShift" variant="primary" size="small" @click="handleAddTeam">
                <el-icon><Plus /></el-icon>
                {{ $t('common.add') }}
              </ActionButton>
            </template>
            <el-table v-loading="loading" :data="teamInfo" border class="vibe-table team-table">
              <el-table-column prop="teamName" :label="$t('auxiliary.shift.teamName')" min-width="90" />
              <el-table-column prop="leader" :label="$t('auxiliary.shift.leader')" min-width="90" />
              <el-table-column prop="members" :label="$t('auxiliary.shift.members')" width="80" align="right" />
              <el-table-column :label="$t('common.operation')" width="86" align="center">
                <template #default="{ row }">
                  <div class="row-actions">
                    <ActionButton v-if="canManageShift" variant="row" @click="handleEditTeam(row)">{{ $t('common.edit') }}</ActionButton>
                    <span v-else>-</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </BaseCard>
        </div>
      </section>

      <section class="schedule-content-section">
        <BaseCard class="calendar-card" :title="$t('auxiliary.shift.calendar')" compact>
          <template #actions>
            <div class="shift-legend">
              <span class="legend-item"><i class="dot day"></i>{{ $t('auxiliary.shift.dayShift') }}</span>
              <span class="legend-item"><i class="dot night"></i>{{ $t('auxiliary.shift.nightShift') }}</span>
            </div>
          </template>
          <el-calendar v-model="calendarDate">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <div class="day">{{ data.day.split('-')[2] }}</div>
                <div v-if="getShiftInfo(data.day)" class="shift-tags">
                  <el-tag
                    v-for="(info, index) in getShiftInfo(data.day)"
                    :key="index"
                    :type="getShiftType(info.shift)"
                    size="small"
                  >
                    {{ info.shiftName }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-calendar>
        </BaseCard>

        <BaseCard class="schedule-card" :title="$t('auxiliary.shift.schedule')" compact>
          <template #actions>
            <ActionButton v-if="canManageShift" variant="primary" size="small" @click="handleAddShift">
              <el-icon><Plus /></el-icon>
              {{ $t('common.add') }}
            </ActionButton>
          </template>
          <div class="table-scroll">
            <el-table v-loading="shiftLoading" :data="shiftList" border stripe class="vibe-table">
              <el-table-column prop="date" :label="$t('auxiliary.shift.date')" width="130" />
              <el-table-column :label="`${$t('auxiliary.shift.dayShift')} (${$t('auxiliary.shift.dayShiftTime')})`" min-width="180">
                <template #default="{ row }">
                  <el-tag type="success">{{ getTeamName(row.dayLeader) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="`${$t('auxiliary.shift.nightShift')} (${$t('auxiliary.shift.nightShiftTime')})`" min-width="180">
                <template #default="{ row }">
                  <el-tag type="info">{{ getTeamName(row.nightLeader) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="dayLeader" :label="$t('auxiliary.shift.dayShiftLeader')" width="130" />
              <el-table-column prop="nightLeader" :label="$t('auxiliary.shift.nightShiftLeader')" width="130" />
              <el-table-column :label="$t('common.operation')" width="100" align="center">
                <template #default="{ row }">
                  <div class="row-actions">
                    <ActionButton v-if="canManageShift" variant="row" @click="handleEditShift(row)">{{ $t('auxiliary.shift.adjust') }}</ActionButton>
                    <span v-else>-</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[7, 14, 31]"
            layout="total, sizes, prev, pager, next"
            class="pagination"
            @size-change="loadShifts"
            @current-change="loadShifts"
          />
        </BaseCard>
      </section>
    </BaseCard>

    <el-dialog v-model="teamDialogVisible" :title="teamDialogTitle" width="920px" class="standard-form-dialog" @close="handleTeamDialogClose">
      <el-form ref="teamFormRef" :model="teamForm" :rules="teamFormRules" label-position="top" class="standard-dialog-form">
        <section class="dialog-section">
          <h3>{{ $t('common.basicInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('auxiliary.shift.teamName')" prop="teamName">
              <el-input v-model="teamForm.teamName" :placeholder="$t('common.pleaseInput') + $t('auxiliary.shift.teamName')" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.leader')" prop="leader">
              <el-input v-model="teamForm.leader" :placeholder="$t('common.pleaseInput') + $t('auxiliary.shift.leader')" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.members')" prop="members">
              <el-input-number v-model="teamForm.members" :min="1" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.phone')" prop="phone">
              <el-input v-model="teamForm.phone" :placeholder="$t('common.pleaseInput') + $t('auxiliary.shift.phone')" />
            </el-form-item>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton variant="secondary" @click="teamDialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" @click="handleTeamSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="shiftDialogVisible" :title="shiftDialogTitle" width="920px" class="standard-form-dialog">
      <el-form :model="shiftForm" label-position="top" class="standard-dialog-form">
        <section class="dialog-section">
          <h3>{{ $t('auxiliary.shift.schedule') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('auxiliary.shift.date')">
              <el-date-picker
                v-model="shiftForm.date"
                type="date"
                value-format="YYYY-MM-DD"
                :placeholder="$t('common.pleaseSelect')"
                :disabled="Boolean(shiftForm.id)"
              />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.dayShiftGroup')">
              <el-select v-model="shiftForm.dayLeader" :placeholder="$t('common.pleaseSelect')">
                <el-option v-for="team in teamInfo" :key="team.id" :label="team.teamName" :value="team.leader" />
              </el-select>
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.nightShiftGroup')">
              <el-select v-model="shiftForm.nightLeader" :placeholder="$t('common.pleaseSelect')">
                <el-option v-for="team in teamInfo" :key="team.id" :label="team.teamName" :value="team.leader" />
              </el-select>
            </el-form-item>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton variant="secondary" @click="shiftDialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" @click="handleShiftSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="ruleDialogVisible" :title="$t('auxiliary.shift.ruleEdit')" width="920px" class="standard-form-dialog">
      <el-form :model="ruleForm" label-position="top" class="standard-dialog-form">
        <section class="dialog-section">
          <h3>{{ $t('auxiliary.shift.ruleConfig') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('auxiliary.shift.ruleMode')">
              <el-select v-model="ruleForm.shiftMode">
                <el-option :label="$t('auxiliary.shift.twoShift')" value="two_shift" />
                <el-option :label="$t('auxiliary.shift.threeShift')" value="three_shift" />
              </el-select>
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.cycle')">
              <el-input v-model="ruleForm.cycleName" :placeholder="$t('common.pleaseInput') + $t('auxiliary.shift.cycle')" />
            </el-form-item>
          </div>
        </section>
        <section class="dialog-section">
          <h3>{{ $t('auxiliary.shift.shiftTime') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('auxiliary.shift.dayShift')">
              <div class="time-range">
                <el-time-picker v-model="ruleForm.dayShiftStart" format="HH:mm" value-format="HH:mm" />
                <span class="time-separator">-</span>
                <el-time-picker v-model="ruleForm.dayShiftEnd" format="HH:mm" value-format="HH:mm" />
              </div>
            </el-form-item>
            <el-form-item v-if="ruleForm.shiftMode === 'three_shift'" :label="$t('auxiliary.shift.middleShift')">
              <div class="time-range">
                <el-time-picker v-model="ruleForm.middleShiftStart" format="HH:mm" value-format="HH:mm" />
                <span class="time-separator">-</span>
                <el-time-picker v-model="ruleForm.middleShiftEnd" format="HH:mm" value-format="HH:mm" />
              </div>
            </el-form-item>
            <el-form-item :label="$t('auxiliary.shift.nightShift')">
              <div class="time-range">
                <el-time-picker v-model="ruleForm.nightShiftStart" format="HH:mm" value-format="HH:mm" />
                <span class="time-separator">-</span>
                <el-time-picker v-model="ruleForm.nightShiftEnd" format="HH:mm" value-format="HH:mm" />
              </div>
            </el-form-item>
          </div>
        </section>
      </el-form>
      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton variant="secondary" @click="ruleDialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" @click="handleRuleSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  createShift,
  createShiftTeam,
  getShiftList,
  getShiftRule,
  getShiftTeamList,
  updateShift,
  updateShiftRule,
  updateShiftTeam
} from '@/app/auxiliary/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useUserStore } from '@/store/user'

const { t } = useI18n()
const userStore = useUserStore()

const currentDate = new Date()
const selectedMonth = ref(`${currentDate.getFullYear()}-${`${currentDate.getMonth() + 1}`.padStart(2, '0')}`)
const calendarDate = ref(currentDate)
const loading = ref(false)
const shiftLoading = ref(false)
const teamInfo = ref([])
const shiftList = ref([])
const canManageShift = computed(() => ['admin', 'supervisor'].includes(userStore.role))

const pagination = reactive({
  page: 1,
  pageSize: 31,
  total: 0
})

const teamDialogVisible = ref(false)
const teamFormRef = ref()
const teamForm = reactive({
  id: null,
  teamName: '',
  leader: '',
  members: 1,
  phone: ''
})

const shiftDialogVisible = ref(false)
const shiftForm = reactive({
  id: null,
  date: '',
  teamId: null,
  dayLeader: '',
  nightLeader: ''
})

const shiftRule = reactive({
  id: null,
  name: 'default',
  shiftMode: 'two_shift',
  cycleName: '',
  dayShiftStart: '08:00',
  dayShiftEnd: '20:00',
  middleShiftStart: '08:00',
  middleShiftEnd: '16:00',
  nightShiftStart: '20:00',
  nightShiftEnd: '08:00'
})

const ruleDialogVisible = ref(false)
const ruleForm = reactive({ ...shiftRule })

const teamDialogTitle = computed(() => {
  return `${teamForm.id ? t('common.edit') : t('common.add')}${t('auxiliary.shift.teamName')}`
})

const shiftDialogTitle = computed(() => {
  return shiftForm.id ? t('auxiliary.shift.adjust') : t('auxiliary.shift.addShift')
})

const ruleModeText = computed(() => {
  return shiftRule.shiftMode === 'three_shift' ? t('auxiliary.shift.threeShift') : t('auxiliary.shift.twoShift')
})

const ruleDescription = computed(() => {
  const cycle = shiftRule.cycleName || t('auxiliary.shift.fourThree')
  return t('auxiliary.shift.ruleDesc', { mode: ruleModeText.value, cycle })
})

const teamFormRules = computed(() => ({
  teamName: [{ required: true, message: t('common.pleaseInput') + t('auxiliary.shift.teamName'), trigger: 'blur' }],
  leader: [{ required: true, message: t('common.pleaseInput') + t('auxiliary.shift.leader'), trigger: 'blur' }]
}))

const formatLocalDate = (date) => {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

const monthRange = computed(() => {
  const [year, month] = selectedMonth.value.split('-').map(Number)
  const start = new Date(year, month - 1, 1)
  const end = new Date(year, month, 0)
  return {
    startDate: formatLocalDate(start),
    endDate: formatLocalDate(end)
  }
})

const loadTeams = async () => {
  loading.value = true
  try {
    const res = await getShiftTeamList({ page: 1, pageSize: 100 })
    teamInfo.value = res.items || []
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    loading.value = false
  }
}

const loadShifts = async () => {
  shiftLoading.value = true
  try {
    const res = await getShiftList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      startDate: monthRange.value.startDate,
      endDate: monthRange.value.endDate
    })
    shiftList.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    shiftLoading.value = false
  }
}

const loadShiftRule = async () => {
  try {
    const res = await getShiftRule()
    Object.assign(shiftRule, {
      id: res.id,
      name: res.name || 'default',
      shiftMode: res.shiftMode || 'two_shift',
      cycleName: res.cycleName || t('auxiliary.shift.fourThree'),
      dayShiftStart: res.dayShiftStart || '08:00',
      dayShiftEnd: res.dayShiftEnd || '20:00',
      middleShiftStart: res.middleShiftStart || '08:00',
      middleShiftEnd: res.middleShiftEnd || '16:00',
      nightShiftStart: res.nightShiftStart || '20:00',
      nightShiftEnd: res.nightShiftEnd || '08:00'
    })
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

const getTeamName = (leader) => {
  const team = teamInfo.value.find(item => item.leader === leader)
  return team ? team.teamName : leader || '-'
}

const getShiftInfo = (dateStr) => {
  const shift = shiftList.value.find(item => item.date === dateStr)
  if (!shift) return null

  const result = []
  if (shift.dayLeader) {
    result.push({ shift: 'day', shiftName: `${t('auxiliary.shift.dayShift')}: ${getTeamName(shift.dayLeader)}` })
  }
  if (shift.nightLeader) {
    result.push({ shift: 'night', shiftName: `${t('auxiliary.shift.nightShift')}: ${getTeamName(shift.nightLeader)}` })
  }
  return result.length ? result : null
}

const getShiftType = (shift) => {
  return shift === 'day' ? 'success' : 'info'
}

const formatRuleRange = (start, end) => {
  return `${start || '--:--'}-${end || '--:--'}`
}

const handleMonthChange = () => {
  calendarDate.value = new Date(`${selectedMonth.value}-01T00:00:00`)
  pagination.page = 1
  loadShifts()
}

const handleRefresh = () => {
  loadTeams()
  loadShifts()
  loadShiftRule()
}

const handleAddTeam = () => {
  if (!canManageShift.value) return
  Object.assign(teamForm, { id: null, teamName: '', leader: '', members: 1, phone: '' })
  teamDialogVisible.value = true
}

const handleEditTeam = (row) => {
  if (!canManageShift.value) return
  Object.assign(teamForm, { ...row })
  teamDialogVisible.value = true
}

const handleTeamSubmit = async () => {
  if (!canManageShift.value) return
  const valid = await teamFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (teamForm.id) {
      await updateShiftTeam(teamForm.id, teamForm)
    } else {
      await createShiftTeam(teamForm)
    }
    ElMessage.success(t('common.success'))
    teamDialogVisible.value = false
    loadTeams()
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

const handleTeamDialogClose = () => {
  teamFormRef.value?.resetFields()
}

const handleEditShift = (row) => {
  if (!canManageShift.value) return
  Object.assign(shiftForm, {
    id: row.id,
    date: row.date,
    teamId: row.teamId,
    dayLeader: row.dayLeader,
    nightLeader: row.nightLeader
  })
  shiftDialogVisible.value = true
}

const handleAddShift = () => {
  if (!canManageShift.value) return
  Object.assign(shiftForm, {
    id: null,
    date: '',
    teamId: teamInfo.value[0]?.id || null,
    dayLeader: teamInfo.value[0]?.leader || '',
    nightLeader: teamInfo.value[1]?.leader || ''
  })
  shiftDialogVisible.value = true
}

const handleShiftSubmit = async () => {
  if (!canManageShift.value) return
  if (!shiftForm.date) {
    ElMessage.error(t('auxiliary.shift.dateRequired'))
    return
  }
  const fallbackTeamId = shiftForm.teamId || teamInfo.value[0]?.id
  if (!fallbackTeamId) {
    ElMessage.error(t('auxiliary.shift.teamRequired'))
    return
  }

  try {
    if (shiftForm.id) {
      await updateShift(shiftForm.id, {
        dayLeader: shiftForm.dayLeader,
        nightLeader: shiftForm.nightLeader
      })
    } else {
      if (shiftList.value.some(item => item.date === shiftForm.date)) {
        ElMessage.error(t('auxiliary.shift.duplicateDate'))
        return
      }
      await createShift({
        date: shiftForm.date,
        teamId: fallbackTeamId,
        dayLeader: shiftForm.dayLeader,
        nightLeader: shiftForm.nightLeader
      })
    }
    ElMessage.success(t('common.success'))
    shiftDialogVisible.value = false
    loadShifts()
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

const handleEditRule = () => {
  if (!canManageShift.value) return
  Object.assign(ruleForm, { ...shiftRule })
  ruleDialogVisible.value = true
}

const handleRuleSubmit = async () => {
  if (!canManageShift.value || !shiftRule.id) return
  try {
    const payload = {
      name: ruleForm.name || 'default',
      shiftMode: ruleForm.shiftMode,
      cycleName: ruleForm.cycleName,
      dayShiftStart: ruleForm.dayShiftStart,
      dayShiftEnd: ruleForm.dayShiftEnd,
      middleShiftStart: ruleForm.shiftMode === 'three_shift' ? ruleForm.middleShiftStart : null,
      middleShiftEnd: ruleForm.shiftMode === 'three_shift' ? ruleForm.middleShiftEnd : null,
      nightShiftStart: ruleForm.nightShiftStart,
      nightShiftEnd: ruleForm.nightShiftEnd,
      status: 'active'
    }
    const res = await updateShiftRule(shiftRule.id, payload)
    Object.assign(shiftRule, {
      id: res.id,
      name: res.name,
      shiftMode: res.shiftMode,
      cycleName: res.cycleName,
      dayShiftStart: res.dayShiftStart,
      dayShiftEnd: res.dayShiftEnd,
      middleShiftStart: res.middleShiftStart || '08:00',
      middleShiftEnd: res.middleShiftEnd || '16:00',
      nightShiftStart: res.nightShiftStart,
      nightShiftEnd: res.nightShiftEnd
    })
    ElMessage.success(t('common.success'))
    ruleDialogVisible.value = false
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

onMounted(() => {
  loadTeams()
  loadShifts()
  loadShiftRule()
})
</script>

<style scoped>
.shift-page {
  display: block;
}

:deep(.shift-main-card > .base-card__body) {
  padding: 0;
}

:deep(.shift-main-card > .base-card__header) {
  min-height: 76px;
}

.shift-tools-section {
  display: grid;
  grid-template-columns: minmax(280px, 0.55fr) minmax(560px, 1.45fr);
  align-items: start;
  gap: 24px;
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.shift-filter-column,
.shift-side-column {
  display: grid;
  gap: 24px;
  align-content: start;
}

.month-filter-card {
  height: auto;
}

.month-filter-form :deep(.el-form-item) {
  margin: 0;
}

.month-filter-form :deep(.el-date-editor) {
  width: 100%;
}

.schedule-content-section {
  display: grid;
  gap: 24px;
  padding: 24px;
}

.calendar-card :deep(.base-card__body),
.schedule-card :deep(.base-card__body) {
  padding: 0;
}

.shift-legend {
  display: flex;
  gap: 14px;
  align-items: center;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 510;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.dot.day {
  background: var(--success);
}

.dot.night {
  background: var(--info);
}

.calendar-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 100%;
  padding: 6px;
}

.calendar-cell .day {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 590;
}

.shift-tags {
  display: grid;
  gap: 4px;
  align-content: start;
}

.rule-content {
  display: grid;
  gap: 10px;
}

.rule-desc {
  margin: 0 0 4px;
  color: var(--text-tertiary);
  font-size: 13px;
  line-height: 1.6;
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-top: 1px solid var(--border-secondary);
  color: var(--text-secondary);
  font-size: 13px;
}

.rule-item strong {
  color: var(--text-primary);
  font-weight: 590;
}

.team-table {
  width: 100%;
}

.table-scroll {
  padding: 24px 24px 0;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 18px 24px 24px;
}

.standard-dialog-form {
  display: grid;
  gap: 28px;
}

.dialog-section {
  display: grid;
  gap: 18px;
}

.dialog-section h3 {
  margin: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 680;
}

.dialog-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.dialog-form-grid :deep(.el-form-item) {
  margin: 0;
}

.dialog-form-grid :deep(.el-input-number),
.dialog-form-grid :deep(.el-select),
.dialog-form-grid :deep(.el-date-editor) {
  width: 100%;
}

.time-separator {
  color: var(--text-tertiary);
}

.time-range {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  width: 100%;
}

.time-range :deep(.el-date-editor) {
  width: 100%;
}

:deep(.el-calendar) {
  --el-calendar-border-color: var(--border-secondary);
  background: transparent;
}

:deep(.el-calendar__header) {
  padding: 18px 24px;
  border-bottom-color: var(--border-secondary);
}

:deep(.el-calendar__body) {
  padding: 0 24px 24px;
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 96px;
  padding: 0;
}

:deep(.el-calendar-table .el-calendar-day:hover) {
  background: var(--sidebar-active-bg);
}

:deep(.el-calendar-table td.is-selected) {
  background: var(--primary-subtle);
}

@media (max-width: 1280px) {
  .shift-tools-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dialog-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
