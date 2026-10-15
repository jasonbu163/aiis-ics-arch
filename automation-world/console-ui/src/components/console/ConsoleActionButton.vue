<!--
  File Path: /control-agent/src/components/console/ConsoleActionButton.vue
  Description: Standard action button for Control Agent console cards and toolbars
  Main Features:
    - Wraps Element Plus buttons with CA-owned action semantics
    - Normalizes icon, radius, sizing and tone for page actions
    - Keeps button labels behind the control-agent i18n namespace
-->
<template>
  <el-button
    :class="buttonClasses"
    :disabled="disabled"
    :loading="loading"
    :size="size"
    :type="buttonType"
    :title="title || undefined"
    @click="emit('click', $event)"
  >
    <template v-if="icon" #icon>
      <el-icon>
        <component :is="icon" />
      </el-icon>
    </template>
    <slot>{{ labelKey ? t(labelKey) : '' }}</slot>
  </el-button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useI18n } from 'vue-i18n'

type ConsoleActionTone = 'primary' | 'secondary' | 'success' | 'warning' | 'danger'

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    icon?: Component
    labelKey?: string
    loading?: boolean
    size?: 'small' | 'large'
    title?: string
    tone?: ConsoleActionTone
  }>(),
  {
    disabled: false,
    labelKey: '',
    loading: false,
    size: 'large',
    title: '',
    tone: 'secondary'
  }
)

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const { t } = useI18n()

const buttonClasses = computed(() => [
  'console-action-button',
  `console-action-button--${props.tone}`,
  `console-action-button--${props.size}`
])

const buttonType = computed(() => {
  if (props.tone === 'secondary') {
    return 'default'
  }

  return props.tone
})
</script>
