<!-- DS 导航薄适配：公共 Sidebar 管理分组/焦点，宿主拥有翻译与叶子状态。 -->
<template>
  <CuSidebar
    :active-id="activeSection"
    :items="items"
    :brand="t('common.app.title')"
    :detail="identityDetail"
    @select="select"
  />
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AgentSidebar as CuSidebar, type NavigationItem } from '@aw-ui'
import type { ConsoleSectionId, ConsoleSectionManifest } from '../../console/types'
const props = defineProps<{
  activeSection: ConsoleSectionId
  identityDetail: string
  sections: ConsoleSectionManifest[]
}>()
const emit = defineEmits<{
  'select-section': [
    section: ConsoleSectionId
  ]
}>()
const { t } = useI18n()
const items = computed<NavigationItem[]>(() => {
  const leaves = props.sections.map(s => ({ id: s.id, label: t(s.titleKey), icon: s.icon }))
  return [leaves.find(i=>i.id==='overview')!,{id:'configuration',label:t('navigation.configuration'),children:leaves.filter(i=>['instances','points','policies'].includes(i.id))},...leaves.filter(i=>['values','logs'].includes(i.id))]
})
function select(id: string) {
  const s = props.sections.find(s => s.id === id)
  if (s)
    emit('select-section', s.id)
}
</script>
