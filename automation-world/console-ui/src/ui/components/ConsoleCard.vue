<!-- 公共卡片：标题、主状态与操作三段对齐，支持工具栏及页脚。 -->
<template>
  <section class="console-card" :class="{ 'console-card--compact': compact }">
    <header class="console-card__header" :class="{ 'console-card__header--managed': headerStatuses?.length || $slots.refresh }">
      <div class="console-card__title-wrap">
        <span v-if="icon" class="console-card__icon"><ElIcon><component :is="icon" /></ElIcon></span>
        <h2>{{ title }}</h2>
        <ElTooltip v-if="help" :content="help" :trigger="['hover', 'focus']" placement="top" :append-to="helpAppendTo" popper-class="console-card-help-popper">
          <button type="button" class="console-card__help" :aria-label="helpLabel || title">?</button>
        </ElTooltip>
        <slot name="title-aside" />
      </div>
      <div v-if="headerStatuses?.length || $slots.refresh" class="console-card__header-controls">
        <div v-if="primaryStatus" class="console-card__header-statuses" aria-live="polite">
          <ElPopover
            v-if="headerStatuses && headerStatuses.length > 1"
            ref="statusPopover"
            :append-to="helpAppendTo"
            :trigger="['hover', 'click']"
            placement="bottom-end"
            role="dialog"
            :title="statusOverflowLabel"
            width="max-content"
            popper-class="console-card-status-popper"
            :show-arrow="false"
            :offset="4"
            :hide-after="140"
          >
            <template #reference>
              <button
                type="button"
                class="console-card__status-trigger"
                :aria-label="statusOverflowLabel ? `${primaryStatus.label} · ${statusOverflowLabel}` : undefined"
                @keydown.esc.stop="statusPopover?.hide()"
                @blur="statusPopover?.hide()"
              >
                <StatusCapsule :label="primaryStatus.label" :tone="primaryStatus.tone">
                  <span class="console-card__status-mark" aria-hidden="true" />
                </StatusCapsule>
              </button>
            </template>
            <ul class="console-card__status-list">
              <li v-for="status in headerStatuses" :key="status.id">
                <StatusCapsule :label="status.label" :tone="status.tone" />
              </li>
            </ul>
          </ElPopover>
          <StatusCapsule v-else :label="primaryStatus.label" :tone="primaryStatus.tone" />
        </div>
        <div v-if="$slots.actions || $slots.refresh" class="console-card__button-group">
          <div v-if="$slots.actions" class="console-card__actions"><slot name="actions" /></div>
          <div v-if="$slots.refresh" class="console-card__refresh"><slot name="refresh" /></div>
        </div>
      </div>
      <div v-else-if="$slots.actions" class="console-card__actions"><slot name="actions" /></div>
    </header>
    <div v-if="$slots.status" class="console-card__status" aria-live="polite"><slot name="status" /></div>
    <div v-if="$slots.tools" class="console-card__tools"><slot name="tools" /></div>
    <div class="console-card__body"><slot /></div>
    <footer v-if="$slots.footer" class="console-card__footer"><slot name="footer" /></footer>
  </section>
</template>
<script setup lang="ts">
import { computed, onDeactivated, ref, type Component } from 'vue'
import { ElIcon, ElPopover, ElTooltip } from 'element-plus'
import StatusCapsule from './StatusCapsule.vue'
import type { CardHeaderStatus } from '../types'

const props = defineProps<{
  title: string
  icon?: Component
  compact?: boolean
  help?: string
  helpLabel?: string
  helpAppendTo?: string
  headerStatuses?: readonly CardHeaderStatus[]
  statusOverflowLabel?: string
}>()
const primaryStatus = computed(() => props.headerStatuses?.[0])
const statusPopover = ref<InstanceType<typeof ElPopover>>()
onDeactivated(() => statusPopover.value?.hide())
</script>
