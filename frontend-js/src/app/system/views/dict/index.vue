<!--
  文件路径: /frontend-js/src/app/system/views/dict/index.vue
  功能描述: Projection 映射设置控制台。
  主要功能:
    - 展示 handler catalog 下的已发布 revision 与历史
    - 通过既有控制面 API 编辑 draft binding 并执行生命周期动作
    - 不访问 PLC、YAML、数据库或 Projection runner
-->
<template>
  <section class="projection-mapping-page page-layout" v-loading="loading">
    <BaseCard :title="t('system.mapping.title')" class="mapping-workspace-card">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" :disabled="!selectedHandler" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            {{ t('system.mapping.createDraft') }}
          </ActionButton>
          <ActionButton variant="refresh" :loading="loading" @click="loadWorkspace">
            <el-icon><Refresh /></el-icon>
            {{ t('system.mapping.refresh') }}
          </ActionButton>
        </div>
      </template>

      <section class="handler-selection-section">
        <h3>{{ t('system.mapping.selectHandler') }}</h3>
        <p class="handler-selection-notice">{{ t('system.mapping.catalogNotice') }}</p>
        <div v-if="handlers.length" class="mapping-context-grid">
          <div class="context-field">
            <span>{{ t('system.mapping.ownerModule') }}</span>
            <el-select
              v-model="selectedOwnerModule"
              class="context-select"
              :placeholder="t('system.mapping.selectOwnerModule')"
              @change="handleOwnerModuleChange"
            >
              <el-option
                v-for="ownerModule in ownerModuleOptions"
                :key="ownerModule"
                :label="ownerModule"
                :value="ownerModule"
              />
            </el-select>
          </div>
          <div class="context-field">
            <span>{{ t('system.mapping.handler') }}</span>
            <el-select
              v-model="selectedHandlerKey"
              class="context-select"
              :placeholder="t('system.mapping.selectHandler')"
              @change="handleHandlerChange"
            >
              <el-option
                v-for="handler in handlerOptions"
                :key="handler.handlerKey"
                :label="handler.handlerKey"
                :value="handler.handlerKey"
              />
            </el-select>
          </div>
          <div class="context-field">
            <span>{{ t('system.mapping.handlerVersion') }}</span>
            <el-input :model-value="selectedHandler?.handlerVersion ?? '—'" disabled />
          </div>
        </div>
        <el-empty v-else :description="t('system.mapping.noHandler')" :image-size="80" />
      </section>

      <section v-if="selectedHandler" class="mapping-workspace-section">
        <div class="mapping-workspace-grid">
          <aside class="revision-pane">
            <div class="section-heading">
              <h3>{{ t('system.mapping.revisionHistory') }}</h3>
            </div>

            <section class="summary-card published-summary-card">
              <header>
                <h4>{{ t('system.mapping.currentPublished') }}</h4>
                <div class="summary-card__header-actions">
                  <el-tag :type="currentPublished?.revision ? 'success' : 'info'">
                    {{ currentPublished?.revision ? statusLabel(currentPublished.revision.status) : t('system.mapping.noPublished') }}
                  </el-tag>
                  <el-select
                    v-if="hasMultipleMappingSets"
                    v-model="selectedSetId"
                    class="mapping-set-select"
                    :placeholder="t('system.mapping.selectMappingSet')"
                    @change="loadSelectedSet"
                  >
                    <el-option
                      v-for="mappingSet in selectedHandlerSets"
                      :key="mappingSet.id"
                      :label="mappingSetLabel(mappingSet)"
                      :value="mappingSet.id"
                    />
                  </el-select>
                </div>
              </header>
              <div class="summary-card__body summary-grid">
                <div><span>{{ t('system.mapping.revision') }}</span><strong>{{ currentPublished?.revision ? `#${currentPublished.revision.revisionNo}` : '—' }}</strong></div>
                <div><span>{{ t('system.mapping.dbGroup') }}</span><strong>{{ publishedGroupCount }}</strong></div>
                <div><span>{{ t('system.mapping.bindings') }}</span><strong>{{ publishedBindingCount }}</strong></div>
                <div><span>{{ t('system.mapping.publishedAt') }}</span><strong>{{ formatDateTime(currentPublished?.revision?.publishedAt) }}</strong></div>
              </div>
            </section>

            <div v-if="selectedSetDetail" class="table-scroll revision-table-scroll">
              <el-table :data="revisions" class="core-table" row-key="id" :row-class-name="revisionRowClassName" @row-click="selectRevision">
                <el-table-column prop="revisionNo" :label="t('system.mapping.revision')" width="92">
                  <template #default="{ row }">#{{ row.revisionNo }}</template>
                </el-table-column>
                <el-table-column prop="status" :label="t('system.mapping.status')" width="112">
                  <template #default="{ row }">
                    <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="createdAt" :label="t('system.mapping.createdAt')" min-width="152">
                  <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.operation')" width="230">
                  <template #default="{ row }">
                    <div class="row-actions" @click.stop>
                      <ActionButton v-if="row.status !== 'draft'" variant="row" @click="copyRevision(row)">
                        {{ t('system.mapping.copyDraft') }}
                      </ActionButton>
                      <ActionButton
                        v-if="canRollback(row)"
                        variant="warning"
                        size="small"
                        @click="rollbackRevision(row)"
                      >
                        {{ t('system.mapping.rollback') }}
                      </ActionButton>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else :description="t('system.mapping.selectMappingSet')" :image-size="80" />
          </aside>

          <section class="editor-pane">
          <div class="section-heading section-heading--editor">
            <h3>{{ t('system.mapping.draftEditor') }}</h3>
            <div v-if="selectedRevision" class="draft-actions">
              <ActionButton
                variant="secondary"
                size="small"
                :disabled="!isEditableDraft"
                :loading="actionLoading"
                @click="saveBindings"
              >
                {{ t('system.mapping.saveBindings') }}
              </ActionButton>
              <ActionButton
                variant="primary"
                size="small"
                :disabled="!isEditableDraft"
                :loading="actionLoading"
                @click="validateRevision"
              >
                {{ t('system.mapping.validate') }}
              </ActionButton>
              <ActionButton
                variant="success"
                size="small"
                :disabled="!canPublish"
                :loading="actionLoading"
                @click="publishRevision"
              >
                {{ t('system.mapping.publish') }}
              </ActionButton>
            </div>
          </div>

          <el-empty v-if="!selectedRevision" :description="t('system.mapping.noRevision')" />
          <template v-else>

            <section class="summary-card revision-summary-card">
              <header>
                <h4>{{ t('system.mapping.currentRevision') }}</h4>
                <el-tag :type="statusTagType(selectedRevision.status)">{{ statusLabel(selectedRevision.status) }}</el-tag>
              </header>
              <div class="summary-card__body summary-grid">
                <div><span>{{ t('system.mapping.revision') }}</span><strong>#{{ selectedRevision.revisionNo }}</strong></div>
                <div><span>{{ t('system.mapping.handlerVersion') }}</span><strong>{{ selectedRevision.handlerVersion || '—' }}</strong></div>
                <div><span>{{ t('system.mapping.createdAt') }}</span><strong>{{ formatDateTime(selectedRevision.createdAt) }}</strong></div>
                <div><span>{{ t('system.mapping.publishedAt') }}</span><strong>{{ formatDateTime(selectedRevision.publishedAt) }}</strong></div>
              </div>
            </section>

            <el-alert
              v-if="!isEditableDraft"
              :title="t('system.mapping.draftOnly')"
              type="info"
              :closable="false"
              show-icon
            />

            <div class="binding-editor__header">
              <el-tag class="binding-editor__count-tag" type="info" effect="plain">
                {{ t('system.mapping.candidateGroupCount', { count: availableCandidateGroups.length }) }}
              </el-tag>
              <span class="binding-editor__guidance">{{ t('system.mapping.bindingGuidance') }}</span>
            </div>

            <div class="binding-editor">
              <el-form label-position="top" class="mapping-form">
                <el-form-item
                  v-for="(input, index) in handlerInputs"
                  :key="input.inputKey"
                  class="binding-row"
                  :class="{ 'binding-row--separated': index > 0 }"
                >
                  <template #label>
                    <span>{{ input.inputKey }}</span>
                    <el-tag size="small" :type="input.required ? 'danger' : 'info'">
                      {{ input.required ? t('system.mapping.required') : t('system.mapping.optional') }}
                    </el-tag>
                    <span class="input-type">{{ t('system.mapping.type') }}: {{ input.type }}</span>
                  </template>
                  <div class="binding-row-fields">
                    <div class="binding-column">
                      <span class="binding-column__title">{{ t('system.mapping.dbGroup') }}</span>
                      <span class="field-hint field-hint--placeholder" aria-hidden="true">&nbsp;</span>
                      <el-select
                        v-model="inputGroups[input.inputKey]"
                        filterable
                        :clearable="!input.required"
                        :disabled="!isEditableDraft"
                        :placeholder="t('system.mapping.selectDbGroup')"
                        class="db-group-select"
                        @change="handleInputGroupChange(input)"
                      >
                        <el-option
                          v-for="group in availableGroupsForInput(input)"
                          :key="groupIdentityKey(group)"
                          :label="groupOptionLabel(group)"
                          :value="groupIdentityKey(group)"
                        >
                          <div class="point-option">
                            <strong>{{ groupLabel(group) }}</strong>
                            <span>{{ groupRoleLabel(group) }}</span>
                          </div>
                        </el-option>
                      </el-select>
                    </div>
                    <div class="binding-column">
                      <span class="binding-column__title">{{ t('system.mapping.candidatePoint') }}</span>
                      <p v-if="!inputGroups[input.inputKey]" class="field-hint">{{ t('system.mapping.selectGroupFirst') }}</p>
                      <p v-else-if="candidateFailedForInput(input)" class="field-hint">{{ t('system.mapping.candidateLoadFailed') }}</p>
                      <p
                        v-else-if="!candidateLoadingForInput(input) && !candidatesForInput(input).length"
                        class="field-hint"
                      >
                        {{ t('system.mapping.noCandidates') }}
                      </p>
                      <span v-else class="field-hint field-hint--placeholder" aria-hidden="true">&nbsp;</span>
                      <el-select
                        v-model="draftBindings[input.inputKey]"
                        filterable
                        :disabled="!isEditableDraft || !inputGroups[input.inputKey]"
                        :loading="candidateLoadingForInput(input)"
                        :placeholder="t('system.mapping.selectPoint')"
                        class="point-select"
                      >
                        <el-option
                          v-for="point in candidatesForInput(input)"
                          :key="pointIdentityKey(point)"
                          :label="pointLabel(point)"
                          :value="pointIdentityKey(point)"
                        >
                          <div class="point-option">
                            <strong>{{ point.pointName }}</strong>
                            <span>({{ point.plcKey }}, DB{{ point.dbNumber }}, {{ point.groupName }})</span>
                            <small>{{ point.description || point.sourceName || point.plcDataType }}</small>
                          </div>
                        </el-option>
                      </el-select>
                    </div>
                  </div>
                </el-form-item>
              </el-form>
            </div>

            <div class="mapping-detail-grid">
              <section class="detail-panel">
                <h4>{{ t('system.mapping.validation') }}</h4>
                <el-tag v-if="validationReport" :type="validationReport.valid ? 'success' : 'danger'">
                  {{ validationReport.valid ? t('system.mapping.validationValid') : t('system.mapping.validationInvalid') }}
                </el-tag>
                <span v-else class="muted-copy">{{ t('system.mapping.validationPending') }}</span>
                <ul v-if="validationErrors.length" class="validation-errors">
                  <li v-for="error in validationErrors" :key="error">{{ t('system.mapping.validationError', { code: error }) }}</li>
                </ul>
              </section>
              <section class="detail-panel">
                <h4>{{ t('system.mapping.auditSummary') }}</h4>
                <dl>
                  <div><dt>{{ t('system.mapping.createdBy') }}</dt><dd>{{ selectedRevision.createdByUserId ?? '—' }}</dd></div>
                  <div><dt>{{ t('system.mapping.validatedBy') }}</dt><dd>{{ selectedRevision.validatedByUserId ?? '—' }}</dd></div>
                  <div><dt>{{ t('system.mapping.publishedBy') }}</dt><dd>{{ selectedRevision.publishedByUserId ?? '—' }}</dd></div>
                  <div><dt>{{ t('system.mapping.changeNote') }}</dt><dd>{{ selectedRevision.changeNote || '—' }}</dd></div>
                </dl>
              </section>
            </div>
          </template>
          </section>
        </div>
      </section>
    </BaseCard>

    <el-dialog v-model="createDialogVisible" :title="t('system.mapping.createDraftTitle')" width="720px" class="standard-form-dialog">
      <p class="dialog-hint">{{ t('system.mapping.createDraftHint', { handler: selectedHandlerKey || '—' }) }}</p>
      <el-form label-position="top" class="standard-dialog-form">
        <el-form-item :label="t('system.mapping.changeNote')">
          <el-input v-model="createForm.changeNote" type="textarea" :rows="2" :placeholder="t('system.mapping.changeNotePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="createDialogVisible = false">{{ t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="actionLoading" :disabled="!selectedHandler" @click="createDraft">
            {{ t('system.mapping.createDraft') }}
          </ActionButton>
        </div>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import {
  copyProjectionMappingRevision,
  createProjectionMappingSet,
  getProjectionCandidates,
  getProjectionCurrentRevision,
  getProjectionHandlers,
  getProjectionMappingSet,
  getProjectionMappingSets,
  publishProjectionMappingRevision,
  replaceProjectionMappingBindings,
  rollbackProjectionMappingRevision,
  validateProjectionMappingRevision
} from '@/app/system/api'

const { t } = useI18n()
const loading = ref(false)
const actionLoading = ref(false)
const handlers = ref([])
const mappingSets = ref([])
const selectedOwnerModule = ref('')
const selectedHandlerKey = ref('')
const selectedSetId = ref(null)
const selectedSetDetail = ref(null)
const currentPublished = ref(null)
const selectedRevisionId = ref(null)
const createDialogVisible = ref(false)
const createForm = reactive({ changeNote: '' })
const draftBindings = reactive({})
const inputGroups = reactive({})
const candidateGroups = reactive({})

const ownerModuleOptions = computed(() => [...new Set(handlers.value.map(handler => handler.ownerModule).filter(Boolean))])
const handlerOptions = computed(() => selectedOwnerModule.value
  ? handlers.value.filter(handler => handler.ownerModule === selectedOwnerModule.value)
  : handlers.value
)
const selectedHandler = computed(() => handlers.value.find(handler => handler.handlerKey === selectedHandlerKey.value) || null)
const selectedHandlerSets = computed(() => mappingSets.value.filter(mappingSet => mappingSet.handlerKey === selectedHandlerKey.value))
const hasMultipleMappingSets = computed(() => selectedHandlerSets.value.length > 1)
const revisions = computed(() => [...(selectedSetDetail.value?.revisions || [])].sort((left, right) => right.revisionNo - left.revisionNo))
const selectedRevision = computed(() => revisions.value.find(revision => revision.id === selectedRevisionId.value) || null)
const handlerInputs = computed(() => selectedHandler.value?.inputs || [])
const isEditableDraft = computed(() => selectedRevision.value?.status === 'draft')
const validationReport = computed(() => selectedRevision.value?.validationReport || null)
const validationErrors = computed(() => validationReport.value?.errors || [])
const canPublish = computed(() => selectedRevision.value?.status === 'validated' && validationReport.value?.valid === true)
const createDefaultGroups = computed(() => selectedHandler.value?.allowedGroupIdentities || [])
const createDefaultGroup = computed(() => createDefaultGroups.value.length === 1 ? createDefaultGroups.value[0] : null)
const primaryGroupIdentity = computed(() => selectedSetDetail.value
  ? {
      plcKey: selectedSetDetail.value.plcKey,
      dbNumber: selectedSetDetail.value.dbNumber,
      groupName: selectedSetDetail.value.groupName
    }
  : null
)
const auxiliaryGroups = computed(() => (selectedHandler.value?.auxiliaryGroupIdentities || [])
  .filter(group => group.plcKey === selectedSetDetail.value?.plcKey)
)
const availableCandidateGroups = computed(() => deduplicateGroups([
  primaryGroupIdentity.value,
  ...auxiliaryGroups.value
].filter(Boolean)))
const publishedBindings = computed(() => currentPublished.value?.revision?.bindings || [])
const publishedBindingCount = computed(() => publishedBindings.value.length)
const publishedGroupCount = computed(() => deduplicateGroups(publishedBindings.value).length)

const groupIdentityKey = (group) => `${group.plcKey}|${group.dbNumber}|${group.groupName}`
const pointIdentityKey = (point) => `${point.plcKey}|${point.dbNumber}|${point.groupName}|${point.pointName}`

const parseGroupIdentity = (groupKey) => {
  const [plcKey, dbNumber, groupName] = groupKey.split('|')
  return { plcKey, dbNumber: Number(dbNumber), groupName }
}

const mappingSetLabel = (mappingSet) => `${mappingSet.plcKey} · DB${mappingSet.dbNumber} · ${mappingSet.groupName}`
const groupLabel = (group) => `${group.plcKey} · DB${group.dbNumber} · ${group.groupName}`
const groupRoleLabel = () => t('system.mapping.dbGroupOption')
const groupOptionLabel = (group) => `${groupLabel(group)} · ${groupRoleLabel(group)}`
const pointLabel = (point) => `${point.pointName} (${point.plcKey} · DB${point.dbNumber} · ${point.groupName})`
const statusLabel = (status) => t(`system.mapping.statusMap.${status}`)
const statusTagType = (status) => ({ draft: 'info', validated: 'warning', published: 'success', retired: 'info' }[status] || 'info')
const formatDateTime = (value) => value ? new Date(value).toLocaleString() : '—'

function deduplicateGroups(groups) {
  const seen = new Set()
  return groups.filter(group => {
    const key = groupIdentityKey(group)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

const clearReactiveRecord = (record) => {
  for (const key of Object.keys(record)) {
    delete record[key]
  }
}

const resetDraftBindings = () => {
  clearReactiveRecord(draftBindings)
  clearReactiveRecord(inputGroups)
  for (const input of handlerInputs.value) {
    draftBindings[input.inputKey] = ''
  }
}

const resetCandidateGroups = () => {
  clearReactiveRecord(candidateGroups)
}

const resetSelectedWorkspace = () => {
  selectedSetId.value = null
  selectedSetDetail.value = null
  currentPublished.value = null
  selectedRevisionId.value = null
  resetCandidateGroups()
  resetDraftBindings()
}

const syncSelectedHandlerFromCatalog = () => {
  if (!handlers.value.length) {
    selectedOwnerModule.value = ''
    selectedHandlerKey.value = ''
    resetSelectedWorkspace()
    return
  }

  const currentHandler = handlers.value.find(handler => handler.handlerKey === selectedHandlerKey.value)
  if (!currentHandler) {
    selectedHandlerKey.value = handlers.value[0].handlerKey
  }

  if (selectedHandler.value?.ownerModule) {
    selectedOwnerModule.value = selectedHandler.value.ownerModule
  } else if (!selectedOwnerModule.value && ownerModuleOptions.value.length) {
    selectedOwnerModule.value = ownerModuleOptions.value[0]
  }
}

const selectSingleSetForSelectedHandler = async () => {
  selectedSetId.value = selectedHandlerSets.value.length === 1 ? selectedHandlerSets.value[0].id : null
  if (selectedSetId.value) {
    await loadSelectedSet()
    return
  }
  selectedSetDetail.value = null
  currentPublished.value = null
  selectedRevisionId.value = null
  resetCandidateGroups()
  resetDraftBindings()
}

const handleHandlerChange = async () => {
  resetSelectedWorkspace()
  await selectSingleSetForSelectedHandler()
}

const handleOwnerModuleChange = async () => {
  if (!handlerOptions.value.some(handler => handler.handlerKey === selectedHandlerKey.value)) {
    selectedHandlerKey.value = handlerOptions.value[0]?.handlerKey || ''
  }
  await handleHandlerChange()
}

const availableGroupsForInput = (input) => {
  if (!primaryGroupIdentity.value) return []
  return input.required
    ? [primaryGroupIdentity.value]
    : availableCandidateGroups.value
}

const candidatesForInput = (input) => {
  const groupKey = inputGroups[input.inputKey]
  return groupKey ? candidateGroups[groupKey]?.items || [] : []
}

const candidateLoadingForInput = (input) => {
  const groupKey = inputGroups[input.inputKey]
  return Boolean(groupKey && candidateGroups[groupKey]?.loading)
}

const candidateFailedForInput = (input) => {
  const groupKey = inputGroups[input.inputKey]
  return Boolean(groupKey && candidateGroups[groupKey]?.error)
}

const resolveInputGroup = (input) => {
  const groupKey = inputGroups[input.inputKey]
  if (!groupKey) return null
  return availableGroupsForInput(input).find(group => groupIdentityKey(group) === groupKey) || parseGroupIdentity(groupKey)
}

const ensureGroupCandidates = async (group) => {
  if (!group || !selectedHandler.value) return
  const groupKey = groupIdentityKey(group)
  if (!candidateGroups[groupKey]) {
    candidateGroups[groupKey] = { items: [], loading: false, loaded: false, error: false }
  }
  const catalogState = candidateGroups[groupKey]
  if (catalogState.loading || catalogState.loaded) return

  catalogState.loading = true
  catalogState.error = false
  try {
    const catalog = await getProjectionCandidates({
      plcKey: group.plcKey,
      dbNumber: group.dbNumber,
      groupName: group.groupName,
      handlerKey: selectedHandler.value.handlerKey
    })
    catalogState.items = catalog.items || []
    catalogState.loaded = true
  } catch {
    catalogState.items = []
    catalogState.error = true
  } finally {
    catalogState.loading = false
  }
}

const ensureSelectedGroupCandidates = async () => {
  const groups = handlerInputs.value
    .map(input => resolveInputGroup(input))
    .filter(Boolean)
  await Promise.all(deduplicateGroups(groups).map(group => ensureGroupCandidates(group)))
}

const handleInputGroupChange = async (input) => {
  draftBindings[input.inputKey] = ''
  const group = resolveInputGroup(input)
  if (group) {
    await ensureGroupCandidates(group)
  }
}

const loadWorkspace = async () => {
  loading.value = true
  try {
    const [handlerCatalog, mappingSetCatalog] = await Promise.all([
      getProjectionHandlers(),
      getProjectionMappingSets()
    ])
    handlers.value = handlerCatalog.items || []
    mappingSets.value = mappingSetCatalog.items || []
    syncSelectedHandlerFromCatalog()
    if (!selectedHandlerSets.value.some(mappingSet => mappingSet.id === selectedSetId.value)) {
      selectedSetId.value = selectedHandlerSets.value.length === 1 ? selectedHandlerSets.value[0].id : null
    }
    if (selectedSetId.value) {
      await loadSelectedSet()
    } else {
      selectedSetDetail.value = null
      currentPublished.value = null
      selectedRevisionId.value = null
      resetCandidateGroups()
      resetDraftBindings()
    }
  } catch {
    ElMessage.error(t('system.mapping.loadFailed'))
  } finally {
    loading.value = false
  }
}

const loadSelectedSet = async () => {
  if (!selectedSetId.value) return
  try {
    const [detail, current] = await Promise.all([
      getProjectionMappingSet(selectedSetId.value),
      getProjectionCurrentRevision(selectedSetId.value)
    ])
    selectedSetDetail.value = detail
    currentPublished.value = current
    resetCandidateGroups()
    const draft = revisions.value.find(revision => revision.status === 'draft')
    const nextRevision = draft || current?.revision || revisions.value[0]
    if (nextRevision) {
      await selectRevision(nextRevision)
    } else {
      selectedRevisionId.value = null
      resetDraftBindings()
    }
  } catch {
    selectedSetDetail.value = null
    currentPublished.value = null
    ElMessage.error(t('system.mapping.loadFailed'))
  }
}

const selectRevision = async (revision) => {
  if (!revision) return
  selectedRevisionId.value = revision.id
  resetDraftBindings()
  for (const input of handlerInputs.value) {
    const binding = (revision.bindings || []).find(item => item.inputKey === input.inputKey)
    draftBindings[input.inputKey] = binding ? pointIdentityKey(binding) : ''
    if (binding) {
      inputGroups[input.inputKey] = groupIdentityKey(binding)
    }
  }
  await ensureSelectedGroupCandidates()
}

const revisionRowClassName = ({ row }) => row.id === selectedRevisionId.value ? 'is-selected-revision' : ''

const operationSucceeded = async (operation) => {
  selectedHandlerKey.value = operation.mappingSet.handlerKey
  selectedSetId.value = operation.mappingSet.id
  mappingSets.value = await getProjectionMappingSets().then(result => result.items || [])
  syncSelectedHandlerFromCatalog()
  await loadSelectedSet()
  selectedRevisionId.value = operation.revision.id
  await selectRevision(revisions.value.find(revision => revision.id === operation.revision.id))
  ElMessage.success(t('system.mapping.actionSuccess'))
}

const openCreateDialog = () => {
  createForm.changeNote = ''
  createDialogVisible.value = true
}

const createDraft = async () => {
  if (!selectedHandler.value) return
  const identity = createDefaultGroup.value
  if (!identity) {
    ElMessage.warning(t('system.mapping.defaultIdentityMissing'))
    return
  }
  actionLoading.value = true
  try {
    const operation = await createProjectionMappingSet({
      ...identity,
      handlerKey: selectedHandler.value.handlerKey,
      changeNote: createForm.changeNote || null
    })
    createDialogVisible.value = false
    createForm.changeNote = ''
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

const bindingsPayload = () => ({
  bindings: handlerInputs.value
    .map(input => {
      const selection = draftBindings[input.inputKey]
      if (!selection) return null
      const [plcKey, dbNumber, groupName, pointName] = selection.split('|')
      return { plcKey, dbNumber: Number(dbNumber), groupName, pointName, inputKey: input.inputKey }
    })
    .filter(Boolean)
})

const saveBindings = async () => {
  if (!selectedRevision.value) return
  const missingRequiredInput = handlerInputs.value.find(input => input.required && !draftBindings[input.inputKey])
  if (missingRequiredInput) {
    ElMessage.warning(t('system.mapping.requiredPointMissing', { inputKey: missingRequiredInput.inputKey }))
    return
  }
  actionLoading.value = true
  try {
    const operation = await replaceProjectionMappingBindings(selectedRevision.value.id, bindingsPayload())
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

const validateRevision = async () => {
  if (!selectedRevision.value) return
  actionLoading.value = true
  try {
    const operation = await validateProjectionMappingRevision(selectedRevision.value.id)
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

const publishRevision = async () => {
  if (!selectedRevision.value) return
  await ElMessageBox.confirm(
    t('system.mapping.publishConfirm', { revisionNo: selectedRevision.value.revisionNo }),
    t('common.tip'),
    { type: 'warning' }
  )
  actionLoading.value = true
  try {
    const operation = await publishProjectionMappingRevision(selectedRevision.value.id)
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

const copyRevision = async (revision) => {
  await ElMessageBox.confirm(
    t('system.mapping.copyConfirm', { revisionNo: revision.revisionNo }),
    t('common.tip'),
    { type: 'warning' }
  )
  actionLoading.value = true
  try {
    const operation = await copyProjectionMappingRevision(revision.id, { changeNote: null })
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

const canRollback = (revision) => (
  selectedSetDetail.value?.activePublishedRevisionId !== revision.id && ['validated', 'retired'].includes(revision.status)
)

const rollbackRevision = async (revision) => {
  if (!selectedSetDetail.value) return
  await ElMessageBox.confirm(
    t('system.mapping.rollbackConfirm', { revisionNo: revision.revisionNo }),
    t('common.tip'),
    { type: 'warning' }
  )
  actionLoading.value = true
  try {
    const operation = await rollbackProjectionMappingRevision(selectedSetDetail.value.id, {
      revisionId: revision.id,
      changeNote: null
    })
    await operationSucceeded(operation)
  } finally {
    actionLoading.value = false
  }
}

onMounted(loadWorkspace)
</script>

<style scoped>
.projection-mapping-page {
  display: grid;
  gap: 20px;
}

.dialog-hint,
.field-hint,
.muted-copy {
  color: var(--text-secondary);
}

.mapping-workspace-card :deep(.base-card__body) {
  padding: 0;
}

.handler-selection-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.handler-selection-section h3,
.section-heading h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 590;
}

.handler-selection-notice {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.mapping-context-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 14px;
}

.context-field,
.summary-grid > div {
  min-width: 0;
}

.context-field span,
.summary-grid span {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 12px;
}

.summary-grid strong {
  display: block;
  overflow: hidden;
  color: var(--text-primary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-select {
  width: 100%;
}

.mapping-workspace-section {
  padding: 24px;
}

.mapping-workspace-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 20px;
}

.revision-pane,
.editor-pane {
  min-width: 0;
}

.editor-pane {
  border-left: 1px solid var(--border-secondary);
  padding-left: 20px;
}

.mapping-set-select {
  width: 220px;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-heading--editor {
  align-items: center;
}

.summary-card {
  overflow: hidden;
  margin-bottom: 16px;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.summary-card header,
.summary-card__header-actions {
  display: flex;
  align-items: center;
}

.summary-card header {
  justify-content: space-between;
  gap: 12px;
  min-height: 42px;
  padding: 0 14px;
  border-bottom: 1px solid var(--border-secondary);
}

.summary-card h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 590;
}

.summary-card__header-actions {
  gap: 10px;
}

.summary-card__body {
  padding: 12px 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.revision-table-scroll {
  min-height: 260px;
}

.draft-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.binding-editor {
  width: 100%;
  padding-top: 18px;
  border-top: 1px solid var(--border-secondary);
}

.binding-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 40px;
  margin-bottom: 14px;
  padding: 8px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.binding-editor__count-tag {
  flex: 0 0 auto;
}

.binding-editor__guidance {
  min-width: 0;
  color: var(--text-secondary);
  font-size: 12px;
  text-align: right;
}

.binding-row-fields {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: start;
  gap: 14px;
}

.binding-row {
  width: 100%;
  margin-bottom: 0;
  padding: 18px 0;
}

.binding-row:first-child {
  padding-top: 0;
}

.binding-row--separated {
  border-top: 1px solid var(--border-secondary);
}

:deep(.binding-row .el-form-item__label) {
  display: flex;
  align-items: center;
  min-width: 0;
}

.binding-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.binding-column__title {
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 590;
}

.db-group-select,
.point-select {
  width: 100%;
}

.point-option {
  display: grid;
  gap: 2px;
}

.point-option span,
.point-option small {
  color: var(--text-secondary);
}

.input-type {
  margin-left: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.field-hint {
  min-height: 18px;
  margin: 0 0 6px;
  font-size: 12px;
}

.field-hint--placeholder {
  display: block;
}

:deep(.revision-table-scroll .is-selected-revision > td.el-table__cell) {
  background: var(--bg-tertiary);
}

.mapping-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid var(--border-secondary);
}

.detail-panel {
  min-width: 0;
}

.detail-panel h4 {
  margin: 0 0 12px;
  color: var(--text-primary);
  font-size: 14px;
}

.validation-errors {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--danger);
}

.detail-panel dl {
  display: grid;
  gap: 8px;
  margin: 0;
}

.detail-panel dl > div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.detail-panel dt {
  color: var(--text-secondary);
}

.detail-panel dd {
  margin: 0;
  color: var(--text-primary);
}

.dialog-hint {
  margin-top: 0;
}

@media (max-width: 1100px) {
  .mapping-workspace-grid,
  .mapping-detail-grid {
    grid-template-columns: 1fr;
  }

  .editor-pane {
    border-left: 0;
    border-top: 1px solid var(--border-secondary);
    padding-top: 20px;
    padding-left: 0;
  }

  .mapping-context-grid,
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .mapping-context-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .section-heading,
  .section-heading--editor {
    flex-direction: column;
    align-items: stretch;
  }

  .mapping-set-select {
    width: 100%;
  }

  .binding-editor__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .binding-editor__guidance {
    text-align: left;
  }

  .binding-row-fields {
    grid-template-columns: 1fr;
  }
}
</style>
