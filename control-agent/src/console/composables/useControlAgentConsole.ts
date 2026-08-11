/**
 * File Path: /control-agent/src/console/composables/useControlAgentConsole.ts
 * Description: Composition state aggregator for the Control Agent operations console
 * Main Features:
 *   - Owns runtime snapshot loading and backend probing
 *   - Owns local section state, pagination and PLC control actions
 *   - Keeps Tauri command usage centralized outside view components
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  fallbackSnapshot,
  enablePlcPersistence,
  loadRuntimeSnapshot,
  pausePlcPersistence,
  probeBackend,
  readPlcSamplesOnceForPlc,
  startPlcCollection,
  startPlcRead,
  stopPlcCollection,
  stopPlcRead,
  type BackendProbeResult,
  type PlcCollectionTarget,
  type PlcCollectionControlResult,
  type PlcRuntimeUnitSnapshot,
  type RuntimeSnapshot
} from '../../services/runtimeSnapshot'
import type { ConsoleSectionId, MetricItem, OperationItem } from '../types'
import { useAgentLocale } from './useAgentLocale'
import { useAgentTheme } from './useAgentTheme'

type OperationDialogState = {
  cancelLabelKey: string
  confirmLabelKey: string
  messageKey: string
  messageParams?: Record<string, string | number>
  titleKey: string
  confirmTone?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  tone: 'warning' | 'info'
}

const defaultOperationDialog: OperationDialogState = {
  cancelLabelKey: 'common.operationDialog.cancel',
  confirmLabelKey: 'common.operationDialog.confirm',
  messageKey: 'common.operationDialog.message',
  titleKey: 'common.operationDialog.title',
  tone: 'warning'
}

export function useControlAgentConsole() {
  const { t } = useI18n()
  const { elementLocale, localeSwitchLabel, toggleLocale } = useAgentLocale()
  const { isDarkTheme, themeSwitchLabel, toggleTheme } = useAgentTheme()

  const activeSection = ref<ConsoleSectionId>('overview')
  const samplePage = ref(1)
  const samplePageSize = ref(5)
  const collectionPage = ref(1)
  const collectionPageSize = ref(5)
  const tablePageSizeOptions = [5, 10, 15, 20]

  const runtimeSnapshot = ref<RuntimeSnapshot>(fallbackSnapshot)
  const selectedPlcKey = ref<PlcCollectionTarget>('all')
  const backendProbe = ref<BackendProbeResult>({
    status: 'skipped',
    latencyMs: null
  })
  const collectionControlBusy = ref(false)
  const collectionControlResult = ref<PlcCollectionControlResult | null>(null)
  const plcReadBusy = ref(false)
  const plcReadMessage = ref('')
  const plcReadMessageType = ref<'success' | 'warning' | 'error' | 'info'>('info')
  const operationDialog = ref<OperationDialogState>(defaultOperationDialog)
  const operationDialogAction = ref<(() => Promise<void>) | null>(null)
  const operationDialogBusy = ref(false)
  const operationDialogVisible = ref(false)

  const summaryItems = computed<MetricItem[]>(() => [
    {
      key: 'raw',
      labelKey: 'collection.rawSnapshots',
      value: String(runtimeSnapshot.value.plcCollectionStatus.rawSnapshotCount)
    },
    {
      key: 'latest',
      labelKey: 'collection.latestGroupCount',
      value: String(runtimeSnapshot.value.plcCollectionStatus.latestGroupCount)
    },
    {
      key: 'samples',
      labelKey: 'collection.sampleCount',
      value: String(runtimeSnapshot.value.plcCollectionStatus.collectorState.sampleCount)
    },
    {
      key: 'failures',
      labelKey: 'collection.failureCount',
      value: String(runtimeSnapshot.value.plcCollectionStatus.collectorState.failureCount)
    }
  ])

  const plcCollectionWriteModeEnabled = computed(() => {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    return (
      gates.plcWriteAllowed &&
      gates.writeGateErrors.length === 0
    )
  })

  const plcUnits = computed(() => runtimeSnapshot.value.plcCollectionStatus.plcUnits)

  const selectedPlcUnit = computed(() => {
    if (selectedPlcKey.value === 'all') {
      return null
    }

    return plcUnits.value.find((unit) => unit.plcKey === selectedPlcKey.value) ?? null
  })

  const selectedPlcTargetLabel = computed(() => formatPlcTarget(selectedPlcKey.value))

  const selectedPlcRuntimeStatusText = computed(() => {
    return selectedPlcUnit.value
      ? plcRuntimeStatusText(selectedPlcUnit.value.readState)
      : plcRuntimeStatusText(runtimeSnapshot.value.plcCollectionStatus.runtimeStatus)
  })

  const selectedPlcCollectionStatusText = computed(() => {
    return selectedPlcUnit.value
      ? plcCollectionStatusText(selectedPlcUnit.value.collectionState)
      : plcRuntimeStatusText(runtimeSnapshot.value.plcCollectionStatus.runtimeStatus)
  })

  const selectedPlcPointSummaryText = computed(() => {
    return selectedPlcUnit.value
      ? t('plc.selectedPointValues', {
          groups: selectedPlcUnit.value.groupCount,
          points: selectedPlcUnit.value.pointCount
        })
      : t('plc.aggregatePointValues', {
          groups: runtimeSnapshot.value.plcPointContract.groupCount,
          points: runtimeSnapshot.value.plcPointContract.pointCount
        })
  })

  const modeStatusText = computed(() => {
    if (plcCollectionWriteModeEnabled.value) {
      return t('runtime.status.mode.plcCollectionWrite')
    }

    return t(`runtime.status.mode.${runtimeSnapshot.value.mode}`)
  })

  const operationItems = computed<OperationItem[]>(() => {
    const snapshot = runtimeSnapshot.value
    const sampleRead = snapshot.plcSampleRead
    const gate = snapshot.authorizationGate
    const databaseReady = snapshot.databaseEnabled && snapshot.databaseConfigured

    return [
      {
        key: 'database',
        labelKey: 'runtime.operations.database',
        stateText: databaseReady ? t('runtime.operations.ready') : t('runtime.operations.locked'),
        detailText: databaseReady
          ? t('runtime.operations.databaseCollectionReadyDetail')
          : t('runtime.operations.databaseCollectionLockedDetail'),
        tone: databaseReady ? 'ready' : 'locked'
      },
      {
        key: 'plc',
        labelKey: 'runtime.operations.plc',
        stateText: sampleRead.succeeded
          ? t('runtime.operations.ready')
          : sampleRead.attempted
            ? t('runtime.operations.blocked')
            : t('runtime.operations.observing'),
        detailText: sampleRead.succeeded
          ? t('runtime.operations.plcReadyDetail', {
              driver: sampleRead.driver,
              count: sampleRead.sampleCount,
              latency: sampleRead.latencyMs
            })
          : t('runtime.operations.plcPendingDetail', { driver: sampleRead.driver }),
        tone: sampleRead.succeeded ? 'ready' : sampleRead.attempted ? 'blocked' : 'observing'
      },
      {
        key: 'authorization',
        labelKey: 'runtime.operations.authorization',
        stateText: gate.enabled ? t('runtime.operations.ready') : t('runtime.operations.observing'),
        detailText: gate.enabled
          ? t('runtime.operations.authorizationEnabledDetail')
          : t('runtime.operations.authorizationDisabledDetail'),
        tone: gate.enabled ? 'ready' : 'observing'
      }
    ]
  })

  const collectionMetricItems = computed<MetricItem[]>(() => {
    const status = runtimeSnapshot.value.plcCollectionStatus
    const collector = status.collectorState

    return [
      {
        key: 'raw',
        labelKey: 'collection.rawSnapshots',
        value: String(status.rawSnapshotCount)
      },
      {
        key: 'latest',
        labelKey: 'collection.latestGroupCount',
        value: String(status.latestGroupCount)
      },
      {
        key: 'samples',
        labelKey: 'collection.sampleCount',
        value: String(collector.sampleCount)
      },
      {
        key: 'failures',
        labelKey: 'collection.failureCount',
        value: String(collector.failureCount)
      }
    ]
  })

  const collectionGateItems = computed<OperationItem[]>(() => {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates
    const items = [
      {
        key: 'collection',
        labelKey: 'collection.gates.collection',
        enabled: gates.plcReadAllowed,
        detailKey: 'collection.gateDetails.collection'
      },
      {
        key: 'write',
        labelKey: 'collection.gates.write',
        enabled: gates.plcWriteAllowed && gates.writeGateErrors.length === 0,
        detailKey: 'collection.gateDetails.write'
      },
      {
        key: 'loop',
        labelKey: 'collection.gates.loop',
        enabled: gates.autostartMode !== 'stopped',
        detailKey: 'collection.gateDetails.loop'
      },
      {
        key: 'database',
        labelKey: 'collection.gates.database',
        enabled: gates.databaseEnabled && gates.databaseConfigured,
        detailKey: 'collection.gateDetails.database'
      },
      {
        key: 'readOnly',
        labelKey: 'collection.gates.readOnly',
        enabled: !gates.databaseReadOnly,
        detailKey: 'collection.gateDetails.readOnly'
      }
    ]

    return items.map((item) => ({
      key: item.key,
      labelKey: item.labelKey,
      stateText: item.enabled ? t('runtime.operations.ready') : t('runtime.operations.locked'),
      detailText: t(item.detailKey, {
        driver: gates.driver,
        interval: gates.intervalMs,
        collector: gates.collectorKey
      }),
      tone: item.enabled ? 'ready' : 'locked'
    }))
  })

  const pagedPlcSamples = computed(() => {
    if (runtimeSnapshot.value.plcSampleRead.plcKey !== selectedPlcKey.value) {
      return []
    }

    return paginate(runtimeSnapshot.value.plcSampleRead.values, samplePage.value, samplePageSize.value)
  })

  const plcSampleValueCount = computed(() => {
    return runtimeSnapshot.value.plcSampleRead.plcKey === selectedPlcKey.value
      ? runtimeSnapshot.value.plcSampleRead.values.length
      : 0
  })

  const pagedCollectionGroups = computed(() => {
    return paginate(
      runtimeSnapshot.value.plcCollectionStatus.latestGroups,
      collectionPage.value,
      collectionPageSize.value
    )
  })

  const isTauriRuntime = computed(() => Boolean(window.__TAURI_INTERNALS__))

  const collectionStartDisabled = computed(() => {
    const targetUnits = plcUnits.value
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    return (
      !isTauriRuntime.value ||
      collectionControlBusy.value ||
      targetUnits.length === 0 ||
      gates.readGateErrors.length > 0 ||
      gates.writeGateErrors.length > 0 ||
      targetUnits.every((unit) => unit.collectionState === 'collecting')
    )
  })

  const collectionStopDisabled = computed(() => {
    const targetUnits = plcUnits.value

    return (
      !isTauriRuntime.value ||
      collectionControlBusy.value ||
      targetUnits.length === 0 ||
      !targetUnits.some((unit) => ['starting', 'running', 'stopping'].includes(unit.readState))
    )
  })

  const plcReadStartDisabled = computed(() => {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    return (
      !isTauriRuntime.value ||
      selectedPlcUnit.value === null ||
      gates.readGateErrors.length > 0 ||
      plcReadBusy.value
    )
  })

  const plcReadDisabledReason = computed(() => {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    if (!isTauriRuntime.value) {
      return t('plc.controls.disabledReasons.runtime')
    }

    if (selectedPlcUnit.value === null) {
      return t('plc.controls.targetRequired')
    }

    if (gates.readGateErrors.length > 0) {
      return t('plc.controls.disabledReasons.readGate')
    }

    if (plcReadBusy.value) {
      return t('plc.controls.disabledReasons.busy')
    }

    return ''
  })

  const collectionControlResultType = computed<'success' | 'warning' | 'error' | 'info'>(() => {
    const result = collectionControlResult.value

    if (!result) {
      return 'info'
    }

    if (result.accepted) {
      return 'success'
    }

    if (result.status === 'failed') {
      return 'error'
    }

    return 'warning'
  })

  const collectionControlResultTitle = computed(() => {
    const result = collectionControlResult.value

    if (!result) {
      return ''
    }

    return t('collection.controls.resultTitle', {
      action: t(`collection.controls.actions.${result.action}`),
      status: result.status,
      target: formatPlcTarget(result.target)
    })
  })

  const collectionControlResultDescription = computed(() => {
    const result = collectionControlResult.value

    if (!result) {
      return ''
    }

    const gateErrors = result.gateErrors.length > 0 ? result.gateErrors.join(' / ') : '-'

    return t('collection.controls.resultDescription', {
      message: collectionControlMessage(result.message),
      gates: gateErrors,
      target: formatPlcTarget(result.target),
      affected: result.affectedPlcKeys.length > 0 ? result.affectedPlcKeys.join(', ') : '-'
    })
  })

  const backendStatusText = computed(() => {
    if (backendProbe.value.status === 'online' && backendProbe.value.latencyMs !== null) {
      return t('runtime.status.backend.onlineWithLatency', { latency: backendProbe.value.latencyMs })
    }

    return t(`runtime.status.backend.${backendProbe.value.status}`)
  })

  const generatedAtText = computed(() => {
    return new Date(runtimeSnapshot.value.generatedAtUnixSeconds * 1000).toLocaleString()
  })

  const localHeartbeatText = computed(() => {
    return t('runtime.facts.heartbeatStatus', {
      status: runtimeSnapshot.value.agentHeartbeat.status,
      seconds: runtimeSnapshot.value.agentHeartbeat.uptimeSeconds
    })
  })

  const databaseConfigText = computed(() => {
    return formatConfigState(
      runtimeSnapshot.value.databaseEnabled,
      runtimeSnapshot.value.databaseConfigured
    )
  })

  const plcContractStatusText = computed(() => {
    if (runtimeSnapshot.value.plcPointContract.loaded) {
      return t('plc.states.contract.loaded')
    }

    if (runtimeSnapshot.value.plcPointContract.exists) {
      return t('plc.states.contract.failed')
    }

    return t('plc.states.contract.missing')
  })

  const plcEndpointText = computed(() => {
    if (selectedPlcUnit.value) {
      return formatPlcEndpoint(selectedPlcUnit.value)
    }

    if (plcUnits.value.length > 0) {
      return t('plc.endpointMultiple', { count: plcUnits.value.length })
    }

    const contract = runtimeSnapshot.value.plcPointContract
    const probe = runtimeSnapshot.value.plcEndpointProbe
    const host = probe.host || contract.endpointIp
    const port = probe.port || contract.endpointPort
    const rack = probe.rack || contract.endpointRack
    const slot = probe.slot || contract.endpointSlot

    if (!host) {
      return t('plc.states.contract.noEndpoint')
    }

    return `${host}:${port} / ${t('plc.rack')} ${rack} / ${t('plc.slot')} ${slot}`
  })

  const plcEndpointProbeText = computed(() => {
    if (selectedPlcUnit.value) {
      return t('plc.runtimeUnitStatus', {
        status: plcRuntimeStatusText(selectedPlcUnit.value.runtimeState)
      })
    }

    if (plcUnits.value.length > 0) {
      return t('plc.endpointProbeMultiple', { count: plcUnits.value.length })
    }

    const probe = runtimeSnapshot.value.plcEndpointProbe

    if (!probe.enabled) {
      return t('plc.states.endpoint.idle')
    }

    if (probe.reachable) {
      return t('plc.states.endpoint.reachableWithLatency', { latency: probe.latencyMs })
    }

    return t('plc.states.endpoint.unreachable')
  })

  const plcSampleReadText = computed(() => {
    const sampleRead = runtimeSnapshot.value.plcSampleRead

    if (!sampleRead.enabled) {
      return t('plc.states.sample.disabled')
    }

    if (selectedPlcKey.value === 'all') {
      return t('plc.selectOneForSample')
    }

    if (sampleRead.plcKey !== selectedPlcKey.value) {
      return t('plc.states.sample.pendingForTarget', {
        plcKey: selectedPlcTargetLabel.value
      })
    }

    if (sampleRead.succeeded) {
      return t('plc.states.sample.succeededWithLatency', {
        plcKey: sampleRead.plcKey || selectedPlcTargetLabel.value,
        count: sampleRead.sampleCount,
        latency: sampleRead.latencyMs
      })
    }

    if (sampleRead.attempted) {
      return t('plc.states.sample.failed')
    }

    return t('plc.states.sample.idle')
  })

  const readableWritableText = computed(() => {
    const contract = runtimeSnapshot.value.plcPointContract

    return `${t('plc.readable')}: ${contract.readableCount} / ${t('plc.writable')}: ${contract.writableCount}`
  })

  const pointContractIssuesText = computed(() => {
    const contract = runtimeSnapshot.value.plcPointContract

    return `${t('plc.missingRequired')}: ${contract.missingRequiredCount} / ${t('plc.unsupportedTypes')}: ${contract.unsupportedTypeCount}`
  })

  const collectionStatusText = computed(() => {
    const collection = runtimeSnapshot.value.plcCollectionStatus
    const state = collection.collectorState

    if (!collection.loaded) {
      return t('collection.states.summary.notLoaded')
    }

    if (!state.loaded) {
      return t('collection.states.summary.noCollectorState')
    }

    return `${plcRuntimeStatusText(collection.runtimeStatus)} / ${collection.gates.driver} / ${collection.gates.intervalMs} ms`
  })

  const collectionDurationsText = computed(() => {
    const state = runtimeSnapshot.value.plcCollectionStatus.collectorState

    return t('collection.durationValues', {
      collect: state.lastCollectDurationMs,
      write: state.lastWriteDurationMs,
      delay: state.lastLoopDelayMs
    })
  })

  const collectionMessageText = computed(() => {
    const collection = runtimeSnapshot.value.plcCollectionStatus

    if (collection.errorMessage) {
      return collection.errorMessage
    }

    if (!collection.loaded) {
      return t('collection.messages.notLoaded')
    }

    if (!collection.collectorState.loaded) {
      return t('collection.messages.noCollectorState')
    }

    return t('collection.messages.statusOnly')
  })

  const snapshotPolicyStatusText = computed(() => {
    const policy = runtimeSnapshot.value.plcCollectionStatus.snapshotPolicy

    if (policy.loaded) {
      return t('collection.snapshotPolicy.loaded', { version: policy.version || '-' })
    }

    if (policy.exists) {
      return t('collection.snapshotPolicy.loadedWithWarnings')
    }

    return t('collection.snapshotPolicy.missing')
  })

  const snapshotPolicyRetentionText = computed(() => {
    const policy = runtimeSnapshot.value.plcCollectionStatus.snapshotPolicy

    return t('collection.snapshotPolicy.retentionValues', {
      raw: policy.rawHotRetentionDays
    })
  })

  const snapshotPolicyPointText = computed(() => {
    const policy = runtimeSnapshot.value.plcCollectionStatus.snapshotPolicy

    return t('collection.snapshotPolicy.pointValues', {
      full: policy.fullDecodedPointCount,
      policy: policy.policyPointCount,
      raw: policy.rawSelectedPointCount,
      latest: policy.latestSelectedPointCount,
      every: policy.everySampleCount,
      change: policy.onChangeCount
    })
  })

  const snapshotPolicyValidationText = computed(() => {
    const policy = runtimeSnapshot.value.plcCollectionStatus.snapshotPolicy

    return t('collection.snapshotPolicy.validationValues', {
      missing: policy.missingPolicyPointCount,
      unknown: policy.unknownPointCount,
      invalid: policy.invalidPolicyCount
    })
  })

  const snapshotPolicyMessageText = computed(() => {
    const policy = runtimeSnapshot.value.plcCollectionStatus.snapshotPolicy

    if (policy.errorMessage) {
      return policy.errorMessage
    }

    if (policy.loaded) {
      return t('collection.snapshotPolicy.messages.loaded')
    }

    return t('collection.snapshotPolicy.messages.pending')
  })

  const authorizationGateStatusText = computed(() => {
    const gate = runtimeSnapshot.value.authorizationGate
    const enabledText = gate.enabled ? t('runtime.status.config.enabled') : t('runtime.status.config.disabled')
    const highRiskText = gate.highRiskAuthRequired
      ? t('gates.highRiskRequired')
      : t('gates.highRiskNotRequired')
    const failClosedText = gate.failClosed
      ? t('gates.failClosed')
      : t('gates.failOpen')

    return `${enabledText} / ${highRiskText} / ${failClosedText}`
  })

  const authorizationGateUpperSystemText = computed(() => {
    const gate = runtimeSnapshot.value.authorizationGate
    const configuredText = gate.upperSystemUrlConfigured
      ? t('runtime.status.config.configured')
      : t('runtime.status.config.unconfigured')

    return `${configuredText} / ${t('gates.timeoutMs', { timeout: gate.timeoutMs })}`
  })

  const authorizationSelfTestText = computed(() => {
    const selfTest = runtimeSnapshot.value.authorizationGate.selfTest

    if (!selfTest.attempted) {
      return t('gates.selfTestDisabled')
    }

    if (selfTest.passed) {
      return t('gates.selfTestPassed', {
        result: selfTest.result
      })
    }

    return t('gates.selfTestFailed', {
      result: selfTest.result || selfTest.errorMessage
    })
  })

  async function refreshRuntime() {
    runtimeSnapshot.value = await loadRuntimeSnapshot()
    synchronizeSelectedPlcKey()
    backendProbe.value = await probeBackend(runtimeSnapshot.value)
  }

  async function confirmStartCollection() {
    const target: PlcCollectionTarget = 'all'

    openOperationDialog(
      {
        cancelLabelKey: 'collection.controls.cancel',
        confirmLabelKey: 'collection.controls.confirmStart',
        messageKey: 'collection.controls.startConfirmMessage',
        messageParams: { target: formatPlcTarget(target) },
        titleKey: 'collection.controls.startConfirmTitle',
        tone: 'warning'
      },
      async () => {
        await runCollectionControl('start_collection', target)
      }
    )
  }

  async function confirmStopCollection() {
    const target: PlcCollectionTarget = 'all'

    openOperationDialog(
      {
        cancelLabelKey: 'collection.controls.cancel',
        confirmLabelKey: 'collection.controls.confirmStop',
        confirmTone: 'warning',
        messageKey: 'collection.controls.stopConfirmMessage',
        messageParams: { target: formatPlcTarget(target) },
        titleKey: 'collection.controls.stopConfirmTitle',
        tone: 'warning'
      },
      async () => {
        await runCollectionControl('stop_collection', target)
      }
    )
  }

  async function runCollectionControl(
    action: 'start_collection' | 'stop_collection',
    target: PlcCollectionTarget = 'all'
  ) {
    collectionControlBusy.value = true

    try {
      const result =
        action === 'start_collection'
          ? await startPlcCollection(target)
          : await stopPlcCollection(target)
      collectionControlResult.value = result
      await refreshRuntime()

      ElMessage({
        type: result.accepted ? 'success' : 'warning',
        message: collectionControlMessage(result.message)
      })
    } finally {
      collectionControlBusy.value = false
    }
  }

  type PlcControlAction =
    | 'start_read'
    | 'stop_read'
    | 'enable_persistence'
    | 'pause_persistence'

  async function runPlcControl(
    action: PlcControlAction,
    target: PlcCollectionTarget
  ) {
    collectionControlBusy.value = true

    try {
      const result =
        action === 'start_read'
          ? await startPlcRead(target)
          : action === 'stop_read'
            ? await stopPlcRead(target)
            : action === 'enable_persistence'
              ? await enablePlcPersistence(target)
              : await pausePlcPersistence(target)
      collectionControlResult.value = result
      await refreshRuntime()
      ElMessage({
        type: result.accepted ? 'success' : 'warning',
        message: collectionControlMessage(result.message)
      })
      return result
    } finally {
      collectionControlBusy.value = false
    }
  }

  async function readPlcSampleOnce() {
    await runPlcReadOnce()

    ElMessage({
      type: plcReadMessageType.value,
      message: plcReadMessage.value
    })
  }

  function openOperationDialog(state: OperationDialogState, action: () => Promise<void>) {
    operationDialog.value = state
    operationDialogAction.value = action
    operationDialogVisible.value = true
  }

  async function confirmOperationDialog() {
    const action = operationDialogAction.value

    if (!action || operationDialogBusy.value) {
      return
    }

    operationDialogBusy.value = true

    try {
      await action()
      operationDialogVisible.value = false
      operationDialogAction.value = null
    } finally {
      operationDialogBusy.value = false
    }
  }

  async function runPlcReadOnce(): Promise<boolean> {
    const target = selectedPlcKey.value

    if (plcReadBusy.value || target === 'all') {
      return false
    }

    plcReadBusy.value = true

    try {
      const result = await readPlcSamplesOnceForPlc(target)
      runtimeSnapshot.value = {
        ...runtimeSnapshot.value,
        plcSampleRead: result
      }

      if (result.succeeded) {
        plcReadMessage.value = t('plc.controls.succeeded', {
          count: result.sampleCount,
          latency: result.latencyMs
        })
      } else if (result.attempted) {
        plcReadMessage.value = result.errorMessage
          ? t('plc.controls.failed', { error: result.errorMessage })
          : t('plc.controls.failedUnknown')
      } else {
        plcReadMessage.value = result.errorMessage
          ? t('plc.controls.notAttemptedWithReason', { error: result.errorMessage })
          : t('plc.controls.notAttempted')
      }
      plcReadMessageType.value = result.succeeded
        ? 'success'
        : result.attempted
          ? 'error'
          : 'warning'
      return result.succeeded
    } catch (error) {
      plcReadMessage.value = error instanceof Error ? error.message : String(error)
      plcReadMessageType.value = 'error'
      return false
    } finally {
      plcReadBusy.value = false
    }
  }

  function handleSectionSelect(index: ConsoleSectionId) {
    activeSection.value = index
  }

  function setCollectionPageSize(pageSize: number) {
    collectionPageSize.value = pageSize
    collectionPage.value = 1
  }

  function setSamplePageSize(pageSize: number) {
    samplePageSize.value = pageSize
    samplePage.value = 1
  }

  function setSelectedPlcKey(value: string) {
    if (value !== 'all' && !plcUnits.value.some((unit) => unit.plcKey === value)) {
      return
    }

    if (selectedPlcKey.value === value) {
      return
    }

    selectedPlcKey.value = value
    samplePage.value = 1
    collectionPage.value = 1
    collectionControlResult.value = null

    plcReadMessage.value = ''
    plcReadMessageType.value = 'info'
  }

  function paginate<T>(items: T[], page: number, pageSize: number) {
    const start = (page - 1) * pageSize
    return items.slice(start, start + pageSize)
  }

  function formatConfigState(enabled: boolean, configured: boolean) {
    const enabledText = enabled ? t('runtime.status.config.enabled') : t('runtime.status.config.disabled')
    const configuredText = configured ? t('runtime.status.config.configured') : t('runtime.status.config.unconfigured')

    return `${enabledText} / ${configuredText}`
  }

  function formatOptional(value: string) {
    return value || '-'
  }

  function formatPlcTarget(target: PlcCollectionTarget) {
    return target === 'all' ? t('collection.targets.all') : target
  }

  function formatPlcEndpoint(unit: PlcRuntimeUnitSnapshot) {
    return `${unit.endpoint.host}:${unit.endpoint.port} / ${t('plc.rack')} ${unit.endpoint.rack} / ${t('plc.slot')} ${unit.endpoint.slot}`
  }

  function plcRuntimeStatusText(status: string) {
    return translateStatus('plc.states.runtime', status)
  }

  function plcCollectionStatusText(status: string) {
    return translateStatus('collection.states.unit', status)
  }

  function plcSampleStatusText(status: string) {
    return translateStatus('plc.states.sampleUnit', status)
  }

  function translateStatus(namespace: string, status: string) {
    const key = `${namespace}.${status}`
    const translated = t(key)

    return translated === key ? status : translated
  }

  function synchronizeSelectedPlcKey() {
    if (plcUnits.value.length === 0) {
      selectedPlcKey.value = 'all'
      return
    }

    if (
      selectedPlcKey.value === 'all' ||
      !plcUnits.value.some((unit) => unit.plcKey === selectedPlcKey.value)
    ) {
      selectedPlcKey.value = plcUnits.value[0].plcKey
    }
  }

  function isPlcControlDisabled(
    action: 'start_read' | 'stop_read' | 'enable_persistence' | 'pause_persistence',
    unit: PlcRuntimeUnitSnapshot
  ) {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    if (!isTauriRuntime.value || collectionControlBusy.value) {
      return true
    }

    if (action === 'start_read') {
      return gates.readGateErrors.length > 0 || ['starting', 'running'].includes(unit.readState)
    }

    if (action === 'stop_read') {
      return !['starting', 'running', 'stopping'].includes(unit.readState)
    }

    if (action === 'enable_persistence') {
      return (
        gates.writeGateErrors.length > 0 ||
        unit.readState !== 'running' ||
        unit.persistenceState === 'enabled'
      )
    }

    return unit.persistenceState === 'paused'
  }

  function plcControlDisabledReason(
    action: 'start_read' | 'stop_read' | 'enable_persistence' | 'pause_persistence',
    unit: PlcRuntimeUnitSnapshot
  ) {
    const gates = runtimeSnapshot.value.plcCollectionStatus.gates

    if (!isTauriRuntime.value) {
      return t('collection.controls.reasons.runtime')
    }

    if (collectionControlBusy.value) {
      return t('collection.controls.reasons.busy')
    }

    if (action === 'start_read' && gates.readGateErrors.length > 0) {
      return t('collection.controls.reasons.readGate')
    }

    if (action === 'stop_read' && !['starting', 'running', 'stopping'].includes(unit.readState)) {
      return t('collection.controls.reasons.readNotRunning')
    }

    if (action === 'enable_persistence') {
      if (gates.writeGateErrors.length > 0) {
        return t('collection.controls.reasons.writeGate')
      }
      if (unit.readState !== 'running') {
        return t('collection.controls.reasons.readPrerequisite')
      }
      if (unit.persistenceState === 'enabled') {
        return t('collection.controls.reasons.alreadyEnabled')
      }
    }

    if (action === 'pause_persistence' && unit.persistenceState === 'paused') {
      return t('collection.controls.reasons.notEnabled')
    }

    return ''
  }

  function formatGroupCounts(decodedCount: number, unsupportedCount: number) {
    return t('collection.countValues', {
      decoded: decodedCount,
      unsupported: unsupportedCount
    })
  }

  function formatCollectionTiming(collectedAt: string, readDurationMs: number) {
    const durationText = readDurationMs > 0 ? `${readDurationMs} ms` : ''

    return [collectedAt, durationText].filter(Boolean).join(' / ') || '-'
  }

  function collectionControlMessage(message: string) {
    const key = `collection.controls.messages.${message}`
    const translated = t(key)

    return translated === key ? message : translated
  }

  function statusTagType(status: string) {
    if (['succeeded', 'completed', 'ready', 'active', 'good', 'all_good'].includes(status)) {
      return 'success'
    }

    if (['failed', 'error', 'cancelled', 'stale'].includes(status)) {
      return 'danger'
    }

    if (['claimed', 'executing', 'running', 'partial'].includes(status)) {
      return 'warning'
    }

    return 'info'
  }

  onMounted(() => {
    void refreshRuntime()
  })

  return {
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
    confirmStartCollection,
    confirmStopCollection,
    databaseConfigText,
    elementLocale,
    formatCollectionTiming,
    formatGroupCounts,
    formatOptional,
    generatedAtText,
    handleSectionSelect,
    isDarkTheme,
    localHeartbeatText,
    localeSwitchLabel,
    modeStatusText,
    operationDialog,
    operationDialogBusy,
    operationDialogVisible,
    confirmOperationDialog,
    pagedCollectionGroups,
    pagedPlcSamples,
    plcSampleValueCount,
    plcContractStatusText,
    plcEndpointProbeText,
    plcEndpointText,
    plcReadBusy,
    plcReadDisabledReason,
    plcReadMessage,
    plcReadMessageType,
    plcReadStartDisabled,
    readPlcSampleOnce,
    plcSampleReadText,
    pointContractIssuesText,
    readableWritableText,
    refreshRuntime,
    runtimeSnapshot,
    selectedPlcKey,
    selectedPlcTargetLabel,
    selectedPlcRuntimeStatusText,
    selectedPlcCollectionStatusText,
    selectedPlcPointSummaryText,
    setSelectedPlcKey,
    formatPlcEndpoint,
    plcRuntimeStatusText,
    plcCollectionStatusText,
    plcSampleStatusText,
    samplePage,
    samplePageSize,
    setCollectionPageSize,
    setSamplePageSize,
    snapshotPolicyMessageText,
    snapshotPolicyPointText,
    snapshotPolicyRetentionText,
    snapshotPolicyStatusText,
    snapshotPolicyValidationText,
    statusTagType,
    isPlcControlDisabled,
    plcControlDisabledReason,
    runPlcControl,
    summaryItems,
    tablePageSizeOptions,
    themeSwitchLabel,
    toggleLocale,
    toggleTheme,
    operationItems
  }
}
