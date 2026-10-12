<!--
  文件路径: /frontend-next-js/src/app/monitor/views/realtime/index.vue
  功能描述: 上位机 HMI 实时监控页面
  主要功能:
    - 从后端 HMI 业务 API 读取实时展示数据
    - 以多页签承载 HMI 电柜画面的只读复刻展示
    - 使用定时 GET 刷新，为后续 WebSocket 升级保留稳定入口
-->
<template>
  <div class="realtime-page page-layout">
    <BaseCard class="realtime-workspace-card" :title="$t('monitor.realtime.title')" v-loading="loading">
      <template #actions>
        <div class="realtime-actions">
          <el-tag :type="collectorTagType" effect="light">
            {{ collectorStatusText }}
          </el-tag>
          <ActionButton variant="refresh" :loading="loading" @click="loadRealtimeData">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.refresh') }}
          </ActionButton>
        </div>
      </template>

      <el-empty
        v-if="!latest.hasSnapshot"
        class="snapshot-empty"
        :description="$t('monitor.realtime.noSnapshot')"
      />

      <template v-else>
        <el-tabs v-model="activeTab" class="hmi-tabs">
          <el-tab-pane
            v-for="tab in hmiTabs"
            :key="tab.name"
            :label="$t(tab.labelKey)"
            :name="tab.name"
          >
            <HmiLineOverview
              v-if="tab.name === 'overview'"
              :payload="payload"
              :collector="collector"
              :latest="latest"
              :metrics="summaryMetrics"
              :recipe="recipe"
            />
            <HeatingZoneGrid
              v-else-if="tab.name === 'heating'"
              :payload="payload"
              :units="heatingUnits"
            />
            <MotorStatusMatrix
              v-else-if="tab.name === 'motorsA'"
              :payload="payload"
              :groups="motorGroupsA"
              :fallback-keys="motorFallbackKeys"
            />
            <MotorStatusMatrix
              v-else-if="tab.name === 'motorsB'"
              :payload="payload"
              :groups="motorGroupsB"
              :fallback-keys="motorFallbackKeys"
            />
            <CoilerTensionPanel
              v-else-if="tab.name === 'coiler'"
              :payload="payload"
              :panels="coilerPanels"
            />
            <PositionControlMatrix
              v-else-if="tab.name === 'position'"
              :payload="payload"
              :groups="positionGroups"
            />
          </el-tab-pane>
        </el-tabs>
      </template>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { getHmiRealtimeOverview } from '@/app/monitor/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import CoilerTensionPanel from '@/app/monitor/components/hmi/CoilerTensionPanel.vue'
import HeatingZoneGrid from '@/app/monitor/components/hmi/HeatingZoneGrid.vue'
import HmiLineOverview from '@/app/monitor/components/hmi/HmiLineOverview.vue'
import MotorStatusMatrix from '@/app/monitor/components/hmi/MotorStatusMatrix.vue'
import PositionControlMatrix from '@/app/monitor/components/hmi/PositionControlMatrix.vue'
import {
  coilerPanels,
  heatingUnits,
  hmiTabs,
  motorFallbackKeys,
  motorGroupsA,
  motorGroupsB,
  positionGroups,
  summaryMetrics
} from '@/app/monitor/components/hmi/hmiConfig'
import { readPoint } from '@/app/monitor/components/hmi/hmiUtils'

const { t } = useI18n()

const activeTab = ref('overview')
const loading = ref(false)
const latest = ref({})
const collector = ref({})
let refreshTimer = null

const payload = computed(() => latest.value.payload || {})

const recipe = computed(() => {
  const existingRecipe = latest.value.recipe || {}
  return {
    coilNumber: existingRecipe.coilNumber || readPoint(payload.value, 'CoilNo'),
    coilType: existingRecipe.coilType || readPoint(payload.value, 'CoilType'),
    width: existingRecipe.width ?? readPoint(payload.value, 'Width'),
    thickness: existingRecipe.thickness ?? readPoint(payload.value, 'Thickness')
  }
})

const collectorTagType = computed(() => {
  if (collector.value.status === 'running' && !collector.value.stale) return 'success'
  if (collector.value.status === 'starting') return 'warning'
  return 'danger'
})

const collectorStatusText = computed(() => {
  if (collector.value.stale) return t('monitor.realtime.collectorStatus.stale')
  const status = collector.value.status || 'stopped'
  return t(`monitor.realtime.collectorStatus.${status}`)
})

const loadRealtimeData = async () => {
  loading.value = true
  try {
    const overviewData = await getHmiRealtimeOverview({ deviceId: 1 })
    latest.value = overviewData || {}
    collector.value = overviewData?.collector || {}
  } catch (error) {
    console.error('Failed to load realtime monitor data:', error)
    ElMessage.error(t('monitor.realtime.loadFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRealtimeData()
  refreshTimer = setInterval(loadRealtimeData, 3000)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.realtime-page {
  display: flex;
  flex-direction: column;
}

.realtime-workspace-card :deep(.base-card__body) {
  display: grid;
  gap: 16px;
  padding: 20px;
}

.realtime-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.snapshot-empty {
  min-height: 360px;
}

.hmi-tabs {
  min-width: 0;
}

.hmi-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.hmi-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--border-secondary);
}

.hmi-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
  font-weight: 650;
}

.hmi-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary);
}

.hmi-tabs :deep(.el-tabs__active-bar) {
  background: var(--primary);
}

@media (max-width: 768px) {
  .realtime-workspace-card :deep(.base-card__body) {
    padding: 16px;
  }
}
</style>
