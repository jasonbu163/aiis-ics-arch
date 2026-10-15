<!--
  File Path: /control-agent/src/app/gates/views/authorization/index.vue
  Description: Authorization gate diagnostics view for the Control Agent console
  Main Features:
    - Displays upper-system gate configuration
    - Displays local authorization self-test diagnostics
    - Does not implement login or user-session behavior
-->
<template>
  <section id="gates" class="console-section">
    <ConsoleCard :icon="Key" title-key="gates.sectionTitle">
      <ConsoleInfoGrid :column="2">
        <el-descriptions-item :label="t('gates.status')">
          {{ authorizationGateStatusText }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.upperSystem')">
          {{ authorizationGateUpperSystemText }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.selfTest')">
          {{ authorizationSelfTestText }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.provider')">
          {{ runtimeSnapshot.authorizationGate.selfTest.provider }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.operator')">
          {{ runtimeSnapshot.authorizationGate.selfTest.operatorId }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.actionScope')">
          {{ runtimeSnapshot.authorizationGate.selfTest.actionScope }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.resource')">
          {{ runtimeSnapshot.authorizationGate.selfTest.resourceId }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('gates.approval')">
          {{ runtimeSnapshot.authorizationGate.selfTest.approvalId }}
        </el-descriptions-item>
      </ConsoleInfoGrid>
    </ConsoleCard>
  </section>
</template>

<script setup lang="ts">
import { Key } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ConsoleCard from '../../../../components/console/ConsoleCard.vue'
import ConsoleInfoGrid from '../../../../components/console/ConsoleInfoGrid.vue'
import type { RuntimeSnapshot } from '../../../../services/runtimeSnapshot'

defineProps<{
  authorizationGateStatusText: string
  authorizationGateUpperSystemText: string
  authorizationSelfTestText: string
  runtimeSnapshot: RuntimeSnapshot
}>()

const { t } = useI18n()
</script>
