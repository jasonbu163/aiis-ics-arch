<!--
  File Path: /control-agent/src/app/runtime/views/overview/index.vue
  Description: Runtime overview view for the Control Agent console
  Main Features:
    - Shows runtime identity, counts and readiness signals
    - Displays the runtime snapshot descriptions
    - Receives all runtime data from the console composition root
-->
<template>
  <section id="overview" class="console-section">
    <MetricGrid
      accessibility-label-key="runtime.overview.ariaLabel"
      featured-label-key="runtime.overview.runtime"
      :featured-value="runtimeSnapshot.agentName"
      :featured-detail="`${runtimeSnapshot.version} · ${runtimeSnapshot.accessMode}`"
      :items="summaryItems"
    />

    <ReadinessGrid accessibility-label-key="runtime.operations.ariaLabel" :items="operationItems" />

    <el-row :gutter="16">
      <el-col :lg="24" :md="24">
        <ConsoleCard :icon="Monitor" title-key="runtime.sectionTitle">
          <ConsoleInfoGrid>
            <el-descriptions-item :label="t('runtime.facts.agent')">
              {{ runtimeSnapshot.agentName }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('runtime.facts.backend')">
              {{ runtimeSnapshot.backendBaseUrl }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('runtime.facts.accessMode')">
              {{ runtimeSnapshot.accessMode }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('runtime.facts.database')">
              {{ databaseConfigText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('runtime.facts.generatedAt')">
              {{ generatedAtText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('runtime.facts.localHeartbeat')">
              {{ localHeartbeatText }}
            </el-descriptions-item>
          </ConsoleInfoGrid>
        </ConsoleCard>
      </el-col>
    </el-row>
  </section>
</template>

<script setup lang="ts">
import { Monitor } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import MetricGrid from '../../../../components/common/MetricGrid.vue'
import ConsoleCard from '../../../../components/console/ConsoleCard.vue'
import ConsoleInfoGrid from '../../../../components/console/ConsoleInfoGrid.vue'
import ReadinessGrid from '../../../../components/console/ReadinessGrid.vue'
import type { MetricItem, OperationItem } from '../../../../console/types'
import type { RuntimeSnapshot } from '../../../../services/runtimeSnapshot'

defineProps<{
  databaseConfigText: string
  generatedAtText: string
  localHeartbeatText: string
  operationItems: OperationItem[]
  runtimeSnapshot: RuntimeSnapshot
  summaryItems: MetricItem[]
}>()

const { t } = useI18n()
</script>
