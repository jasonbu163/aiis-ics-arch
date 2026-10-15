<!--
  File Path: /control-agent/src/App.vue
  Description: Composition root for the Control Agent operations console
  Main Features:
    - Installs the Element Plus locale provider
    - Mounts the CA-owned shell layout and section views
    - Keeps runtime state and Tauri actions in the app composition layer
-->
<template>
  <el-config-provider :locale="elementLocale">
    <AgentLayout
      :active-section="activeSection"
      :backend-status-text="backendStatusText"
      :is-dark-theme="isDarkTheme"
      :locale-switch-label="localeSwitchLabel"
      :mode-status-text="modeStatusText"
      :runtime-snapshot="runtimeSnapshot"
      :sections="consoleSections"
      :theme-switch-label="themeSwitchLabel"
      @refresh-runtime="refreshRuntime"
      @select-section="handleSectionSelect"
      @toggle-locale="toggleLocale"
      @toggle-theme="toggleTheme"
    >
      <RuntimeOverviewView
        v-if="activeSection === 'overview'"
        :database-config-text="databaseConfigText"
        :generated-at-text="generatedAtText"
        :local-heartbeat-text="localHeartbeatText"
        :operation-items="operationItems"
        :runtime-snapshot="runtimeSnapshot"
        :summary-items="summaryItems"
      />

      <CollectionStatusView
        v-else-if="activeSection === 'collection'"
        :collection-control-busy="collectionControlBusy"
        :collection-control-result="collectionControlResult"
        :collection-control-result-description="collectionControlResultDescription"
        :collection-control-result-title="collectionControlResultTitle"
        :collection-control-result-type="collectionControlResultType"
        :collection-durations-text="collectionDurationsText"
        :collection-gate-items="collectionGateItems"
        :collection-message-text="collectionMessageText"
        :collection-metric-items="collectionMetricItems"
        :collection-page="collectionPage"
        :collection-page-size="collectionPageSize"
        :collection-start-disabled="collectionStartDisabled"
        :collection-status-text="collectionStatusText"
        :collection-stop-disabled="collectionStopDisabled"
        :confirm-start-collection="confirmStartCollection"
        :confirm-stop-collection="confirmStopCollection"
        :format-collection-timing="formatCollectionTiming"
        :format-group-counts="formatGroupCounts"
        :format-optional="formatOptional"
        :format-plc-endpoint="formatPlcEndpoint"
        :is-plc-control-disabled="isPlcControlDisabled"
        :paged-collection-groups="pagedCollectionGroups"
        :plc-control-disabled-reason="plcControlDisabledReason"
        :plc-collection-status-text="plcCollectionStatusText"
        :plc-runtime-status-text="plcRuntimeStatusText"
        :plc-sample-status-text="plcSampleStatusText"
        :runtime-snapshot="runtimeSnapshot"
        :run-plc-control="runPlcControl"
        :snapshot-policy-message-text="snapshotPolicyMessageText"
        :snapshot-policy-point-text="snapshotPolicyPointText"
        :snapshot-policy-retention-text="snapshotPolicyRetentionText"
        :snapshot-policy-status-text="snapshotPolicyStatusText"
        :snapshot-policy-validation-text="snapshotPolicyValidationText"
        :status-tag-type="statusTagType"
        :table-page-size-options="tablePageSizeOptions"
        @update:collection-page="setCollectionPage"
        @update:collection-page-size="setCollectionPageSize"
      />

      <PlcDiagnosticsView
        v-else-if="activeSection === 'plc'"
        :format-plc-endpoint="formatPlcEndpoint"
        :read-plc-sample-once="readPlcSampleOnce"
        :paged-plc-samples="pagedPlcSamples"
        :plc-contract-status-text="plcContractStatusText"
        :plc-endpoint-probe-text="plcEndpointProbeText"
        :plc-endpoint-text="plcEndpointText"
        :plc-read-busy="plcReadBusy"
        :plc-read-disabled-reason="plcReadDisabledReason"
        :plc-read-message="plcReadMessage"
        :plc-read-message-type="plcReadMessageType"
        :plc-read-start-disabled="plcReadStartDisabled"
        :plc-sample-value-count="plcSampleValueCount"
        :plc-sample-read-text="plcSampleReadText"
        :plc-collection-status-text="plcCollectionStatusText"
        :plc-runtime-status-text="plcRuntimeStatusText"
        :plc-sample-status-text="plcSampleStatusText"
        :point-contract-issues-text="pointContractIssuesText"
        :readable-writable-text="readableWritableText"
        :runtime-snapshot="runtimeSnapshot"
        :selected-plc-collection-status-text="selectedPlcCollectionStatusText"
        :selected-plc-key="selectedPlcKey"
        :selected-plc-point-summary-text="selectedPlcPointSummaryText"
        :selected-plc-runtime-status-text="selectedPlcRuntimeStatusText"
        :selected-plc-target-label="selectedPlcTargetLabel"
        :sample-page="samplePage"
        :sample-page-size="samplePageSize"
        :status-tag-type="statusTagType"
        :table-page-size-options="tablePageSizeOptions"
        @update:sample-page="setSamplePage"
        @update:sample-page-size="setSamplePageSize"
        @update:selected-plc-key="setSelectedPlcKey"
      />

      <AuthorizationGateView
        v-else-if="activeSection === 'gates'"
        :authorization-gate-status-text="authorizationGateStatusText"
        :authorization-gate-upper-system-text="authorizationGateUpperSystemText"
        :authorization-self-test-text="authorizationSelfTestText"
        :runtime-snapshot="runtimeSnapshot"
      />
    </AgentLayout>

    <ConsoleOperationDialog
      v-model="operationDialogVisible"
      :cancel-label-key="operationDialog.cancelLabelKey"
      :confirm-label-key="operationDialog.confirmLabelKey"
      :loading="operationDialogBusy"
      :message-key="operationDialog.messageKey"
      :message-params="operationDialog.messageParams"
      :title-key="operationDialog.titleKey"
      :confirm-tone="operationDialog.confirmTone"
      :tone="operationDialog.tone"
      @confirm="confirmOperationDialog"
    />
  </el-config-provider>
</template>

<script setup lang="ts">
import AgentLayout from './layouts/AgentLayout.vue'
import CollectionStatusView from './app/collection/views/status/index.vue'
import AuthorizationGateView from './app/gates/views/authorization/index.vue'
import PlcDiagnosticsView from './app/plc/views/diagnostics/index.vue'
import RuntimeOverviewView from './app/runtime/views/overview/index.vue'
import ConsoleOperationDialog from './components/console/ConsoleOperationDialog.vue'
import { consoleSections } from './console/sections'
import { useControlAgentConsole } from './console/composables/useControlAgentConsole'

const {
  activeSection,
  authorizationGateStatusText,
  authorizationGateUpperSystemText,
  authorizationSelfTestText,
  backendStatusText,
  collectionControlBusy,
  collectionControlResult,
  collectionControlResultDescription,
  collectionControlResultTitle,
  collectionControlResultType,
  collectionDurationsText,
  collectionGateItems,
  collectionMessageText,
  collectionMetricItems,
  collectionPage,
  collectionPageSize,
  collectionStartDisabled,
  collectionStatusText,
  collectionStopDisabled,
  confirmOperationDialog,
  confirmStartCollection,
  confirmStopCollection,
  databaseConfigText,
  elementLocale,
  formatCollectionTiming,
  formatGroupCounts,
  formatOptional,
  formatPlcEndpoint,
  generatedAtText,
  handleSectionSelect,
  isDarkTheme,
  isPlcControlDisabled,
  plcControlDisabledReason,
  localHeartbeatText,
  localeSwitchLabel,
  modeStatusText,
  operationDialog,
  operationDialogBusy,
  operationDialogVisible,
  operationItems,
  pagedCollectionGroups,
  pagedPlcSamples,
  plcCollectionStatusText,
  plcContractStatusText,
  plcEndpointProbeText,
  plcEndpointText,
  plcReadBusy,
  plcReadDisabledReason,
  plcReadMessage,
  plcReadMessageType,
  plcReadStartDisabled,
  plcSampleValueCount,
  plcRuntimeStatusText,
  plcSampleStatusText,
  plcSampleReadText,
  pointContractIssuesText,
  readableWritableText,
  readPlcSampleOnce,
  refreshRuntime,
  runtimeSnapshot,
  samplePage,
  samplePageSize,
  selectedPlcCollectionStatusText,
  selectedPlcKey,
  selectedPlcPointSummaryText,
  selectedPlcRuntimeStatusText,
  selectedPlcTargetLabel,
  setSelectedPlcKey,
  setCollectionPageSize,
  setSamplePageSize,
  snapshotPolicyMessageText,
  snapshotPolicyPointText,
  snapshotPolicyRetentionText,
  snapshotPolicyStatusText,
  snapshotPolicyValidationText,
  statusTagType,
  runPlcControl,
  summaryItems,
  tablePageSizeOptions,
  themeSwitchLabel,
  toggleLocale,
  toggleTheme
} = useControlAgentConsole()

function setCollectionPage(page: number) {
  collectionPage.value = page
}

function setSamplePage(page: number) {
  samplePage.value = page
}
</script>
