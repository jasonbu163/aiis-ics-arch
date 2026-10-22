<!-- DAA 指标内容：使用 CU 公共卡片，不维护第二套卡片外观。 -->
<template>
  <CuCard :title="t(labelKey)" :compact="!featured">
    <div class="daa-metric">
      <strong>
        {{ value }}
      </strong>
      <small v-if="detail">
        {{ detail }}
      </small>
    </div>
  </CuCard>
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ConsoleCard as CuCard } from '@aw-ui'
defineProps<{
  detail?: string
  featured?: boolean
  labelKey: string
  value: string
}>()
const { t } = useI18n()
</script>
