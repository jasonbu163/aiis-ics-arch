<!--
  File Path: /control-agent/src/components/console/ConsoleCard.vue
  Description: Standard card shell for Control Agent console sections
  Main Features:
    - Provides header, actions, body and optional footer slots
    - Supports two-segment and three-segment page skeletons
    - Keeps title text in the control-agent i18n namespace
-->
<template>
  <section
    class="console-card"
    :class="{
      'console-card--compact': compact,
      'console-card--segmented': hasTools || hasFooter
    }"
  >
    <header class="console-card__header" :class="{ 'console-card__header--split': hasActions }">
      <div class="console-card__title-wrap">
        <span v-if="icon" class="console-card__icon">
          <el-icon>
            <component :is="icon" />
          </el-icon>
        </span>
        <h2>{{ t(titleKey) }}</h2>
      </div>
      <div v-if="hasActions" class="console-card__actions">
        <slot name="actions" />
      </div>
    </header>

    <div v-if="hasTools" class="console-card__tools">
      <slot name="tools" />
    </div>

    <div class="console-card__body" :class="bodyClass">
      <slot />
    </div>

    <footer v-if="hasFooter" class="console-card__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, useSlots, type Component } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps<{
  bodyClass?: string
  compact?: boolean
  icon?: Component
  titleKey: string
}>()

const { t } = useI18n()
const slots = useSlots()
const hasActions = computed(() => Boolean(slots.actions))
const hasTools = computed(() => Boolean(slots.tools))
const hasFooter = computed(() => Boolean(slots.footer))
</script>
