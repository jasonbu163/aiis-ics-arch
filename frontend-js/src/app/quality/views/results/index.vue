<!-- 质量列表入口保留原页面权限，并显式提供历史检验切换。 -->
<template>
  <div class="page-layout quality-results-entry">
    <template v-if="legacy">
      <div class="table-actions history-actions">
        <ActionButton @click="router.push({ name: 'QualityList' })">{{ $t('quality.results.backToResults') }}</ActionButton>
      </div>
      <LegacyQualityList />
    </template>
    <QualityList v-else @legacy="router.push({ name: 'QualityList', query: { view: 'legacy' } })" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'
import LegacyQualityList from '../list/index.vue'
import QualityList from './QualityList.vue'

const route = useRoute()
const router = useRouter()
const legacy = computed(() => route.query.view === 'legacy')
</script>

<style scoped>
.history-actions { margin-bottom: 12px; }
</style>
