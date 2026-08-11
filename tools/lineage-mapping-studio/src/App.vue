<template>
  <main class="studio-shell" :class="{ 'is-sidebar-hidden': !sidebarVisible }">
    <aside v-if="sidebarVisible" class="studio-sidebar">
      <section class="brand-panel">
        <div>
          <p class="eyebrow">{{ t('evidence') }}</p>
          <h1>{{ t('title') }}</h1>
          <p class="subtitle">{{ t('subtitle') }}</p>
        </div>
        <label class="language-select">
          <span>{{ t('language') }}</span>
          <select v-model="locale">
            <option value="zh-CN">中文</option>
            <option value="en-US">English</option>
          </select>
        </label>
      </section>

      <section class="tool-panel">
        <h2>{{ t('inputs') }}</h2>
        <button type="button" class="secondary-action" @click="loadDefaultInputs">
          {{ t('actions.loadInputs') }}
        </button>
        <FileInput :label="t('import.frontendSources')" accept=".csv" @loaded="loadFrontendSources" />
        <FileInput :label="t('import.frontendI18nRefs')" accept=".csv" @loaded="loadFrontendI18nRefs" />
        <FileInput :label="t('import.frontendComponentRefs')" accept=".csv" @loaded="loadFrontendComponentRefs" />
        <FileInput :label="t('import.frontendApiRefs')" accept=".csv" @loaded="loadFrontendApiRefs" />
        <FileInput :label="t('import.frontendApiUriRefs')" accept=".csv" @loaded="loadFrontendApiUriRefs" />
        <FileInput :label="t('import.frontendLinks')" accept=".csv" @loaded="loadFrontendLinks" />
        <FileInput :label="t('import.backendRoutes')" accept=".csv" @loaded="loadBackendRoutes" />
        <FileInput :label="t('import.backendRouteUriRefs')" accept=".csv" @loaded="loadBackendRouteUriRefs" />
        <FileInput :label="t('import.backendModels')" accept=".csv" @loaded="loadBackendModels" />
        <FileInput :label="t('import.backendRouteModelLinks')" accept=".csv" @loaded="loadBackendRouteModelLinks" />
        <FileInput :label="t('import.tableSchema')" accept=".json" @loaded="loadTableSchema" />
        <FileInput :label="t('import.lineageGraph')" accept=".json" @loaded="loadLineageGraph" />
      </section>

      <section class="tool-panel stats-grid">
        <div v-for="item in stats" :key="item.label" class="stat-item">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </section>

      <section class="tool-panel action-panel">
        <button type="button" class="primary-action" @click="handleBuildGraph">
          {{ t('actions.buildGraph') }}
        </button>
        <button type="button" @click="clearGraph">
          {{ t('actions.clear') }}
        </button>
        <p class="status-text">{{ statusText }}</p>
      </section>
    </aside>

    <section class="graph-panel">
      <div class="graph-toolbar">
        <div class="toolbar-title">
          <button type="button" class="sidebar-toggle" @click="toggleSidebar">
            {{ sidebarVisible ? t('actions.hideSidebar') : t('actions.showSidebar') }}
          </button>
          <h2>{{ t('graph') }}</h2>
        </div>
        <div class="toolbar-right">
          <p class="toolbar-status">{{ statusText }}</p>
          <form class="search-box" @submit.prevent="locateSearchResult">
            <input
              v-model.trim="searchTerm"
              type="search"
              :placeholder="t('search.placeholder')"
              :aria-label="t('search.label')"
            />
            <span>{{ t('search.count', { count: searchMatches.length }) }}</span>
            <button type="submit">{{ t('actions.locate') }}</button>
          </form>
          <div class="toolbar-actions">
            <button type="button" class="primary-action" @click="handleBuildGraph">
              {{ t('actions.buildGraph') }}
            </button>
            <button type="button" @click="resetViewport">
              {{ t('actions.fitGraph') }}
            </button>
            <button type="button" @click="clearGraph">
              {{ t('actions.clear') }}
            </button>
          </div>
          <div class="view-presets" :aria-label="t('viewPresets.label')">
            <button
              v-for="preset in viewPresets"
              :key="preset.key"
              type="button"
              :class="{ 'view-preset-active': activeViewPreset === preset.key }"
              @click="applyViewPreset(preset.hiddenKinds)"
            >
              {{ t(`viewPresets.${preset.key}`) }}
            </button>
          </div>
          <div class="legend">
            <button
              v-for="item in legend"
              :key="item.kind"
              type="button"
              :class="[
                `legend-filter legend-${item.kind}`,
                { 'legend-filter-hidden': hiddenKinds.has(item.kind) }
              ]"
              @click="toggleKindVisibility(item.kind)"
            >
              {{ item.label }}
            </button>
            <button type="button" class="legend-show-all" @click="showAllKinds">
              {{ t('actions.showAllKinds') }}
            </button>
          </div>
        </div>
      </div>

      <div
        ref="viewportRef"
        class="lineage-viewport"
        :class="{ 'is-panning': panState.active }"
        @wheel.prevent="handleWheel"
        @pointerdown="startPan"
        @pointermove="movePan"
        @pointerup="stopPan"
        @pointerleave="stopPan"
        @click="handleViewportClick"
      >
        <div
          v-if="visibleNodes.length"
          class="lineage-canvas"
          :style="{ width: `${canvasSize.width}px`, height: `${canvasSize.height}px` }"
        >
          <div class="lineage-canvas-stage" :style="canvasTransformStyle">
            <div
              v-for="lane in laneHeaders"
              :key="lane.kind"
              :class="['lane-header', { 'lane-header-hidden': hiddenKinds.has(lane.kind) }]"
              :style="{ transform: `translate(${lane.x}px, 0)` }"
            >
              {{ lane.label }}
            </div>
            <svg class="lineage-edges" :width="canvasSize.width" :height="canvasSize.height">
              <defs>
                <marker
                  id="edge-arrow"
                  markerWidth="8"
                  markerHeight="8"
                  refX="7"
                  refY="4"
                  orient="auto"
                >
                  <path d="M 0 0 L 8 4 L 0 8 z" />
                </marker>
              </defs>
              <path
                v-for="edge in edgeSegments"
                :key="edge.id"
                class="lineage-edge"
                :class="{ 'lineage-edge-active': selectedNodeId }"
                :d="edge.path"
                marker-end="url(#edge-arrow)"
              />
            </svg>
            <article
              v-for="node in visibleNodes"
              :key="node.id"
              :class="[
                `canvas-node canvas-${node.data?.kind || 'unknown'}`,
                {
                  'canvas-node-selected': node.id === selectedNodeId || (searchIsolationActive && searchMatchIds.has(node.id)),
                  'canvas-node-search-match': searchMatchIds.has(node.id)
                }
              ]"
              :style="{ transform: `translate(${node.position.x}px, ${node.position.y}px)` }"
              @click.stop="selectNode(node.id)"
            >
              <span class="node-meta">
                <b v-if="node.data?.ordinal">#{{ node.data.ordinal }}</b>
                {{ node.data?.kind }}
              </span>
              <strong>{{ node.data?.title }}</strong>
              <small>{{ node.data?.subtitle }}</small>
              <em v-if="node.data?.evidence">{{ node.data.evidence }}</em>
            </article>
          </div>
        </div>
        <div v-else class="empty-graph">
          {{ t('status.ready') }}
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, shallowRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { type Edge, type Node } from '@vue-flow/core'
import FileInput from './components/FileInput.vue'
import type { ImportedFiles, LineageGraph, StudioNodeData } from './types'
import { parseCsv, parseLineageGraph, parseTableSchema } from './utils/parsers'
import { buildGraph } from './utils/graph'

const { t, locale } = useI18n()

const imported = ref<ImportedFiles>({
  frontendSources: [],
  frontendI18nRefs: [],
  frontendComponentRefs: [],
  frontendApiRefs: [],
  frontendApiUriRefs: [],
  frontendLinks: [],
  backendRoutes: [],
  backendRouteUriRefs: [],
  backendModels: [],
  backendRouteModelLinks: []
})
const nodes = shallowRef<Node<StudioNodeData>[]>([])
const edges = shallowRef<Edge[]>([])
const selectedNodeId = ref('')
const searchTerm = ref('')
const searchIsolationActive = ref(false)
const defaultHiddenKinds = ['locale', 'i18n', 'field', 'plc']
const hiddenKinds = ref<Set<string>>(new Set(defaultHiddenKinds))
const sidebarVisible = ref(true)
const viewportRef = ref<HTMLElement | null>(null)
const zoom = ref(1)
const pan = reactive({ x: 40, y: 40 })
const panState = reactive({
  active: false,
  moved: false,
  pointerId: 0,
  startX: 0,
  startY: 0,
  originX: 0,
  originY: 0
})
const statusKey = ref('status.ready')
const statusMessage = ref('')
let graphReloadTimer: number | undefined
let graphSignature = ''
const laneOrder = ['locale', 'i18n', 'component', 'api', 'route', 'model', 'table', 'field', 'plc']
const laneWidth = 340
const laneHeaderHeight = 52
const viewPresets = [
  { key: 'core', hiddenKinds: ['locale', 'i18n', 'field', 'plc'] },
  { key: 'copy', hiddenKinds: ['field', 'plc'] },
  { key: 'fields', hiddenKinds: ['locale', 'i18n', 'plc'] },
  { key: 'plc', hiddenKinds: ['locale', 'i18n'] },
  { key: 'all', hiddenKinds: [] }
]

const defaultInputs = [
  { path: '/inputs/lineage_graph.json', load: loadLineageGraph }
]

const stats = computed(() => [
  { label: t('stats.frontendSources'), value: imported.value.frontendSources.length || imported.value.lineageGraph?.stats?.frontend_sources || 0 },
  { label: t('stats.frontendI18nRefs'), value: imported.value.frontendI18nRefs.length || imported.value.lineageGraph?.stats?.frontend_i18n_refs || 0 },
  { label: t('stats.frontendApiRefs'), value: imported.value.frontendApiRefs.length || imported.value.lineageGraph?.stats?.frontend_api_refs || 0 },
  { label: t('stats.frontendApiUriRefs'), value: imported.value.frontendApiUriRefs.length || imported.value.lineageGraph?.stats?.frontend_api_uri_refs || 0 },
  { label: t('stats.frontendLinks'), value: imported.value.frontendLinks.length || imported.value.lineageGraph?.stats?.frontend_links || 0 },
  { label: t('stats.backendRoutes'), value: imported.value.backendRoutes.length || imported.value.lineageGraph?.stats?.backend_routes || 0 },
  { label: t('stats.backendRouteUriRefs'), value: imported.value.backendRouteUriRefs.length || imported.value.lineageGraph?.stats?.backend_route_uri_refs || 0 },
  { label: t('stats.backendModels'), value: imported.value.backendModels.length || imported.value.lineageGraph?.stats?.backend_models || 0 },
  { label: t('stats.backendRouteModelLinks'), value: imported.value.backendRouteModelLinks.length },
  { label: t('stats.tables'), value: imported.value.tableSchema?.tables?.length ?? imported.value.lineageGraph?.stats?.table_schema_tables ?? 0 },
  { label: t('stats.xlsxBindings'), value: imported.value.lineageGraph?.stats?.xlsx_bindings ?? 0 },
  { label: t('stats.nodes'), value: nodes.value.length },
  { label: t('stats.edges'), value: edges.value.length }
])

const legend = computed(() => [
  { kind: 'locale', label: t('legend.locale') },
  { kind: 'i18n', label: t('legend.i18n') },
  { kind: 'component', label: t('legend.component') },
  { kind: 'api', label: t('legend.api') },
  { kind: 'route', label: t('legend.route') },
  { kind: 'model', label: t('legend.model') },
  { kind: 'table', label: t('legend.table') },
  { kind: 'field', label: t('legend.field') },
  { kind: 'plc', label: t('legend.plc') }
])

const normalizedSearchTerm = computed(() => searchTerm.value.trim().toLowerCase())

const searchMatches = computed(() => {
  if (!normalizedSearchTerm.value) {
    return []
  }
  return nodes.value.filter((node) => nodeMatchesSearch(node, normalizedSearchTerm.value))
})

const searchMatchIds = computed(() => new Set(searchMatches.value.map((node) => node.id)))

const searchIsolationNodeIds = computed(() => {
  if (!searchIsolationActive.value || !normalizedSearchTerm.value || !searchMatches.value.length) {
    return null
  }
  return searchMatchIds.value
})

const visibleKindOrder = computed(() => {
  if (searchIsolationNodeIds.value) {
    const visibleKinds = new Set(
      nodes.value
        .filter((node) => searchIsolationNodeIds.value?.has(node.id))
        .map((node) => node.data?.kind || 'unknown')
    )
    return laneOrder.filter((kind) => visibleKinds.has(kind))
  }
  return laneOrder.filter((kind) => !hiddenKinds.value.has(kind))
})

const laneHeaders = computed(() => visibleKindOrder.value.map((kind, index) => ({
  kind,
  label: legend.value.find((item) => item.kind === kind)?.label || kind,
  x: index * laneWidth
})))

const canvasSize = computed(() => {
  if (!visibleNodes.value.length) {
    return { width: 800, height: 520 }
  }
  const maxX = Math.max(...visibleNodes.value.map((node) => node.position.x))
  const maxY = Math.max(...visibleNodes.value.map((node) => node.position.y))
  return {
    width: Math.max(maxX + 320, Math.max(visibleKindOrder.value.length - 1, 0) * laneWidth + 320),
    height: maxY + 140
  }
})

const focusedNodeIds = computed(() => {
  if (!selectedNodeId.value) {
    return null
  }
  return collectDirectedLineageNodeIds(selectedNodeId.value, edges.value)
})

const visibleNodes = computed(() => {
  if (searchIsolationNodeIds.value) {
    return layoutColumnNodes(nodes.value.filter((node) => searchIsolationNodeIds.value?.has(node.id)))
  }
  const sourceNodes = focusedNodeIds.value
    ? nodes.value.filter((node) => focusedNodeIds.value?.has(node.id))
    : nodes.value
  return layoutColumnNodes(sourceNodes.filter((node) => !hiddenKinds.value.has(node.data?.kind || 'unknown')))
})

const visibleEdges = computed(() => {
  const visibleIds = new Set(visibleNodes.value.map((node) => node.id))
  return edges.value.filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target))
})

const canvasTransformStyle = computed(() => ({
  width: `${canvasSize.value.width}px`,
  height: `${canvasSize.value.height}px`,
  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom.value})`
}))

const edgeSegments = computed(() => {
  const nodeMap = new Map(visibleNodes.value.map((node) => [node.id, node]))
  return visibleEdges.value.flatMap((edge) => {
    const source = nodeMap.get(edge.source)
    const target = nodeMap.get(edge.target)
    if (!source || !target) {
      return []
    }
    const x1 = source.position.x + 220
    const y1 = source.position.y + 38
    const x2 = target.position.x
    const y2 = target.position.y + 38
    const midX = x1 + Math.max(80, (x2 - x1) / 2)
    return [
      {
        id: edge.id,
        path: `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`
      }
    ]
  })
})

const statusText = computed(() => statusMessage.value || t(statusKey.value))

const activeViewPreset = computed(() => {
  const hidden = [...hiddenKinds.value].sort().join('|')
  return viewPresets.find((preset) => [...preset.hiddenKinds].sort().join('|') === hidden)?.key || 'custom'
})

function loadFrontendSources(text: string) {
  imported.value.frontendSources = parseCsv(text)
}

function loadFrontendI18nRefs(text: string) {
  imported.value.frontendI18nRefs = parseCsv(text)
}

function loadFrontendComponentRefs(text: string) {
  imported.value.frontendComponentRefs = parseCsv(text)
}

function loadFrontendApiRefs(text: string) {
  imported.value.frontendApiRefs = parseCsv(text)
}

function loadFrontendApiUriRefs(text: string) {
  imported.value.frontendApiUriRefs = parseCsv(text)
}

function loadFrontendLinks(text: string) {
  imported.value.frontendLinks = parseCsv(text)
}

function loadBackendRoutes(text: string) {
  imported.value.backendRoutes = parseCsv(text)
}

function loadBackendRouteUriRefs(text: string) {
  imported.value.backendRouteUriRefs = parseCsv(text)
}

function loadBackendModels(text: string) {
  imported.value.backendModels = parseCsv(text)
}

function loadBackendRouteModelLinks(text: string) {
  imported.value.backendRouteModelLinks = parseCsv(text)
}

function loadTableSchema(text: string) {
  imported.value.tableSchema = parseTableSchema(text)
}

function loadLineageGraph(text: string) {
  imported.value.lineageGraph = parseLineageGraph(text)
  graphSignature = text
}

async function loadDefaultInputs() {
  const loaded: string[] = []
  const missing: string[] = []
  const failed: string[] = []

  for (const input of defaultInputs) {
    try {
      const response = await fetch(`${input.path}?t=${Date.now()}`, { cache: 'no-store' })
      if (response.status === 404) {
        missing.push(input.path)
        continue
      }
      if (!response.ok) {
        failed.push(`${input.path} (${response.status})`)
        continue
      }
      input.load(await response.text())
      loaded.push(input.path)
    } catch (error) {
      failed.push(`${input.path} (${error instanceof Error ? error.message : 'unknown'})`)
    }
  }

  if (failed.length) {
    statusMessage.value = t('status.inputLoadFailed', { files: failed.join(', ') })
    return
  }
  if (!loaded.length) {
    statusMessage.value = t('status.noDefaultInputs')
    return
  }
  statusMessage.value = missing.length
    ? t('status.defaultInputsLoadedWithMissing', { loaded: loaded.length, missing: missing.length })
    : t('status.defaultInputsLoaded', { loaded: loaded.length })
  if (imported.value.lineageGraph?.nodes.length) {
    applyLineageGraph(imported.value.lineageGraph)
    startGraphPolling()
    return
  }
  if (hasV4Evidence()) {
    await handleBuildGraph()
  }
}

async function handleBuildGraph() {
  statusMessage.value = ''
  if (!hasV4Evidence()) {
    statusKey.value = 'status.missingEvidence'
    return
  }
  const graph = buildGraph(imported.value)
  syncFlowState(graph.nodes, graph.edges)
  statusMessage.value = t('status.graphBuiltWithCounts', {
    nodes: graph.nodes.length,
    edges: graph.edges.length
  })
}

function hasV4Evidence() {
  return Boolean(
    imported.value.frontendComponentRefs.length ||
    imported.value.frontendApiRefs.length ||
    imported.value.frontendApiUriRefs.length ||
    imported.value.frontendLinks.length ||
    imported.value.backendRoutes.length ||
    imported.value.backendRouteUriRefs.length ||
    imported.value.backendModels.length ||
    imported.value.backendRouteModelLinks.length ||
    imported.value.tableSchema?.tables?.length
  )
}

function applyLineageGraph(graph: LineageGraph) {
  const nextNodes: Node<StudioNodeData>[] = graph.nodes.map((node) => ({
    id: node.id,
    type: 'lineage',
    position: node.position ?? { x: 0, y: 0 },
    class: `node-${node.kind}`,
    data: {
      title: node.title,
      label: node.title,
      subtitle: node.subtitle ?? '',
      kind: node.kind,
      evidence: node.evidence,
      ordinal: node.ordinal
    }
  }))
  const nextEdges: Edge[] = graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    data: { evidence: edge.evidence }
  }))
  syncFlowState(nextNodes, nextEdges)
  statusMessage.value = t('status.graphBuiltWithCounts', {
    nodes: nextNodes.length,
    edges: nextEdges.length
  })
}

function startGraphPolling() {
  window.clearInterval(graphReloadTimer)
  graphReloadTimer = window.setInterval(async () => {
    try {
      const response = await fetch(`/inputs/lineage_graph.json?t=${Date.now()}`, { cache: 'no-store' })
      if (!response.ok) {
        return
      }
      const text = await response.text()
      if (!text || text === graphSignature) {
        return
      }
      graphSignature = text
      const graph = parseLineageGraph(text)
      imported.value.lineageGraph = graph
      applyLineageGraph(graph)
    } catch {
      // The graph file may be absent while the watcher is regenerating it.
    }
  }, 2500)
}

function syncFlowState(nextNodes: Node<StudioNodeData>[], nextEdges: Edge[]) {
  nodes.value = nextNodes
  edges.value = nextEdges
  selectedNodeId.value = ''
  searchIsolationActive.value = false
  void nextTick(() => resetViewport())
}

function clearGraph() {
  syncFlowState([], [])
  hiddenKinds.value = new Set(defaultHiddenKinds)
  statusMessage.value = ''
  statusKey.value = 'status.ready'
}

function selectNode(nodeId: string) {
  searchIsolationActive.value = false
  revealNodeKind(nodeId)
  selectedNodeId.value = nodeId
  void nextTick(() => resetViewport())
  const node = nodes.value.find((item) => item.id === nodeId)
  statusMessage.value = t('status.focusedGraph', {
    node: node?.data?.title || nodeId,
    nodes: focusedNodeIds.value?.size ?? 0
  })
}

function resetFocus() {
  if (searchIsolationActive.value) {
    clearSearchIsolation()
    return
  }
  if (!selectedNodeId.value) {
    return
  }
  selectedNodeId.value = ''
  void nextTick(() => resetViewport())
  setGraphCountStatus()
}

function locateSearchResult() {
  if (!normalizedSearchTerm.value) {
    return
  }
  const [firstMatch] = searchMatches.value
  if (!firstMatch) {
    statusMessage.value = t('status.searchNoMatch', { term: searchTerm.value })
    return
  }
  searchIsolationActive.value = true
  selectedNodeId.value = ''
  void nextTick(() => resetViewport())
  statusMessage.value = t('status.searchIsolated', {
    count: searchMatches.value.length
  })
}

function applyViewPreset(kinds: string[]) {
  hiddenKinds.value = new Set(kinds)
  selectedNodeId.value = ''
  searchIsolationActive.value = false
  void nextTick(() => resetViewport())
}

function revealNodeKind(nodeId: string) {
  const node = nodes.value.find((item) => item.id === nodeId)
  const kind = node?.data?.kind || 'unknown'
  if (!hiddenKinds.value.has(kind)) {
    return
  }
  const nextHiddenKinds = new Set(hiddenKinds.value)
  nextHiddenKinds.delete(kind)
  hiddenKinds.value = nextHiddenKinds
}

function clearSearchIsolation() {
  searchIsolationActive.value = false
  selectedNodeId.value = ''
  void nextTick(() => resetViewport())
  setGraphCountStatus()
}

function setGraphCountStatus() {
  statusMessage.value = t('status.graphBuiltWithCounts', {
    nodes: nodes.value.length,
    edges: edges.value.length
  })
}

function resetViewport() {
  const viewport = viewportRef.value
  const width = viewport?.clientWidth || 1000
  const height = viewport?.clientHeight || 700
  if (!visibleNodes.value.length) {
    zoom.value = 1
    pan.x = 40
    pan.y = 40
    statusKey.value = 'status.graphFitted'
    return
  }
  const padding = 64
  const fitScale = Math.min(
    (width - padding) / Math.max(canvasSize.value.width, 1),
    (height - padding) / Math.max(canvasSize.value.height, 1)
  )
  const nextZoom = clamp(fitScale, 0.02, 1)
  zoom.value = nextZoom
  pan.x = Math.max(24, (width - canvasSize.value.width * nextZoom) / 2)
  pan.y = Math.max(24, (height - canvasSize.value.height * nextZoom) / 2)
  statusKey.value = 'status.graphFitted'
}

function handleWheel(event: WheelEvent) {
  if (!viewportRef.value) {
    return
  }
  const previousZoom = zoom.value
  const nextZoom = clamp(previousZoom * (event.deltaY < 0 ? 1.12 : 0.88), 0.02, 2.5)
  const rect = viewportRef.value.getBoundingClientRect()
  const pointerX = event.clientX - rect.left
  const pointerY = event.clientY - rect.top
  pan.x = pointerX - (pointerX - pan.x) * (nextZoom / previousZoom)
  pan.y = pointerY - (pointerY - pan.y) * (nextZoom / previousZoom)
  zoom.value = nextZoom
}

function startPan(event: PointerEvent) {
  if ((event.target as HTMLElement).closest('.canvas-node')) {
    return
  }
  panState.active = true
  panState.moved = false
  panState.pointerId = event.pointerId
  panState.startX = event.clientX
  panState.startY = event.clientY
  panState.originX = pan.x
  panState.originY = pan.y
  ;(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId)
}

function movePan(event: PointerEvent) {
  if (!panState.active) {
    return
  }
  const deltaX = event.clientX - panState.startX
  const deltaY = event.clientY - panState.startY
  if (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3) {
    panState.moved = true
  }
  pan.x = panState.originX + deltaX
  pan.y = panState.originY + deltaY
}

function stopPan(event: PointerEvent) {
  if (!panState.active) {
    return
  }
  if ((event.currentTarget as HTMLElement).hasPointerCapture?.(panState.pointerId)) {
    ;(event.currentTarget as HTMLElement).releasePointerCapture(panState.pointerId)
  }
  panState.active = false
}

function handleViewportClick(event: MouseEvent) {
  if (panState.moved || (event.target as HTMLElement).closest('.canvas-node')) {
    panState.moved = false
    return
  }
  resetFocus()
}

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
  void nextTick(() => resetViewport())
}

function toggleKindVisibility(kind: string) {
  searchIsolationActive.value = false
  const nextHiddenKinds = new Set(hiddenKinds.value)
  if (nextHiddenKinds.has(kind)) {
    nextHiddenKinds.delete(kind)
  } else {
    nextHiddenKinds.add(kind)
  }
  hiddenKinds.value = nextHiddenKinds
  void nextTick(() => resetViewport())
}

function showAllKinds() {
  const wasSearchIsolationActive = searchIsolationActive.value
  searchIsolationActive.value = false
  if (!hiddenKinds.value.size) {
    if (wasSearchIsolationActive) {
      void nextTick(() => resetViewport())
    }
    return
  }
  hiddenKinds.value = new Set()
  void nextTick(() => resetViewport())
}

function collectDirectedLineageNodeIds(startNodeId: string, sourceEdges: Edge[]) {
  const upstream = new Map<string, Set<string>>()
  const downstream = new Map<string, Set<string>>()
  for (const edge of sourceEdges) {
    if (!downstream.has(edge.source)) {
      downstream.set(edge.source, new Set())
    }
    if (!upstream.has(edge.target)) {
      upstream.set(edge.target, new Set())
    }
    downstream.get(edge.source)?.add(edge.target)
    upstream.get(edge.target)?.add(edge.source)
  }
  const visited = new Set<string>([startNodeId])
  collectReachable(startNodeId, upstream, visited)
  collectReachable(startNodeId, downstream, visited)
  return visited
}

function collectReachable(startNodeId: string, adjacency: Map<string, Set<string>>, visited: Set<string>) {
  const queue = [startNodeId]
  while (queue.length) {
    const current = queue.shift()
    if (!current) {
      continue
    }
    for (const next of adjacency.get(current) ?? []) {
      if (visited.has(next)) {
        continue
      }
      visited.add(next)
      queue.push(next)
    }
  }
}

function layoutColumnNodes(sourceNodes: Node<StudioNodeData>[]) {
  const grouped = new Map<string, Node<StudioNodeData>[]>()
  for (const node of sourceNodes) {
    const kind = node.data?.kind || 'unknown'
    if (!grouped.has(kind)) {
      grouped.set(kind, [])
    }
    grouped.get(kind)?.push(node)
  }
  const result: Node<StudioNodeData>[] = []
  for (const [laneIndex, kind] of visibleKindOrder.value.entries()) {
    const group = grouped.get(kind) ?? []
    if (!group.length) {
      continue
    }
    group.forEach((node, index) => {
      result.push({
        ...node,
        position: {
          x: laneIndex * laneWidth,
          y: laneHeaderHeight + index * 98
        }
      })
    })
  }
  return result
}

function nodeMatchesSearch(node: Node<StudioNodeData>, term: string) {
  return [
    node.id,
    node.data?.kind,
    node.data?.title,
    node.data?.subtitle,
    node.data?.evidence
  ]
    .filter(Boolean)
    .some((item) => String(item).toLowerCase().includes(term))
}

watch([normalizedSearchTerm, searchMatches], ([term, matches]) => {
  if (!searchIsolationActive.value) {
    return
  }
  if (!term) {
    clearSearchIsolation()
    return
  }
  if (!matches.length) {
    searchIsolationActive.value = false
    selectedNodeId.value = ''
    void nextTick(() => resetViewport())
    statusMessage.value = t('status.searchNoMatch', { term: searchTerm.value })
  }
})

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

onBeforeUnmount(() => {
  window.clearInterval(graphReloadTimer)
})
</script>
