<!-- 公共二级侧栏：宿主控制选择与翻译，展开和键盘焦点仅归当前实例。 -->
<template>
  <div ref="shell" class="agent-sidebar-shell" @keydown.capture="handleKeydown">
    <ElMenu ref="menu" :default-active="activeLeafId" :default-openeds="initialOpeneds" class="agent-menu" :class="{ 'agent-menu--grouped': hasGroups }" @select="selectLeaf" @open="openGroup" @close="closeGroup">
      <template v-for="item in items" :key="item.id">
        <ElSubMenu v-if="item.children?.length" :index="item.id" :teleported="false" :data-navigation-id="item.id" tabindex="0" :aria-label="item.label" :class="{ 'contains-active': activeParentId === item.id }">
          <template #title><ElIcon v-if="item.icon"><component :is="item.icon" /></ElIcon><span class="agent-menu__label">{{ item.label }}</span></template>
          <ElMenuItem v-for="child in item.children" :key="child.id" :index="child.id" :data-navigation-id="child.id" :data-parent-id="item.id" :tabindex="opened.includes(item.id) ? 0 : -1" :class="{ 'is-current': activeLeafId === child.id }" :aria-current="activeLeafId === child.id ? 'page' : undefined">
            <ElIcon v-if="child.icon"><component :is="child.icon" /></ElIcon><span class="agent-menu__label">{{ child.label }}</span>
          </ElMenuItem>
        </ElSubMenu>
        <ElMenuItem v-else :index="item.id" :data-navigation-id="item.id" tabindex="0" :class="{ 'is-current': activeLeafId === item.id }" :aria-current="activeLeafId === item.id ? 'page' : undefined">
          <ElIcon v-if="item.icon"><component :is="item.icon" /></ElIcon><span class="agent-menu__label">{{ item.label }}</span>
        </ElMenuItem>
      </template>
    </ElMenu>
    <div class="sidebar-footer-brand"><strong>{{ brand }}</strong><small>{{ detail }}</small></div>
  </div>
</template>
<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { ElIcon, ElMenu, ElMenuItem, ElSubMenu, type MenuInstance } from 'element-plus'
import type { NavigationItem } from '../types'
const props = defineProps<{ activeId: string; items: NavigationItem[]; brand: string; detail?: string }>()
const emit = defineEmits<{ select: [id: string] }>()
const shell = ref<HTMLElement>()
const menu = ref<MenuInstance>()
const hasGroups = computed(() => props.items.some(item => item.children?.length))
const activeLeafId = computed(() => props.items.some(item => item.children?.length ? item.children.some(child => child.id === props.activeId) : item.id === props.activeId) ? props.activeId : '')
const activeParentId = computed(() => props.items.find(item => item.children?.some(child => child.id === activeLeafId.value))?.id ?? '')
const initialOpeneds = activeParentId.value ? [activeParentId.value] : []
const opened = ref<string[]>([...initialOpeneds])
function openGroup(id: string) { if (!opened.value.includes(id)) opened.value.push(id) }
function elementFor(id: string) { return Array.from(shell.value?.querySelectorAll<HTMLElement>('[data-navigation-id]') ?? []).find(element => element.dataset.navigationId === id) }
function closeGroup(id: string) {
  const group = elementFor(id)
  if (group && group !== document.activeElement && group.contains(document.activeElement)) group.focus()
  opened.value = opened.value.filter(value => value !== id)
}
// 只观察稳定身份及父归属；翻译后的 items 重建不会重开手动折叠组或移动焦点。
watch([activeLeafId, activeParentId], async () => {
  await nextTick()
  if (activeParentId.value) menu.value?.open(activeParentId.value)
}, { immediate: true, flush: 'post' })
function selectLeaf(id: string) {
  emit('select', id)
  // Element Plus 的交互高亮是短暂内部状态；最终展示与 aria-current 只使用宿主 prop。
  nextTick(() => { if (activeLeafId.value) menu.value?.updateActiveIndex(activeLeafId.value) })
}
function visibleElements() {
  return Array.from(shell.value?.querySelectorAll<HTMLElement>('[data-navigation-id]') ?? []).filter(element => !element.dataset.parentId || opened.value.includes(element.dataset.parentId))
}
function handleKeydown(event: KeyboardEvent) {
  const target = event.target instanceof Element ? event.target.closest<HTMLElement>('[data-navigation-id]') : null
  if (!target || !shell.value?.contains(target)) return
  const keys = ['ArrowDown', 'ArrowUp', 'ArrowRight', 'ArrowLeft', 'Enter', ' ']
  if (!keys.includes(event.key)) return
  event.preventDefault()
  event.stopPropagation()
  const id = target.dataset.navigationId!
  const group = props.items.find(item => item.id === id && item.children?.length)
  const title = target.querySelector<HTMLElement>('.el-sub-menu__title')
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    const elements = visibleElements()
    const index = elements.indexOf(target)
    elements[index + (event.key === 'ArrowDown' ? 1 : -1)]?.focus()
  } else if (event.key === 'ArrowRight' && group) {
    menu.value?.open(id)
    nextTick(() => elementFor(group.children![0].id)?.focus())
  } else if (event.key === 'ArrowLeft') {
    if (target.dataset.parentId) elementFor(target.dataset.parentId)?.focus()
    else if (group && opened.value.includes(id)) title?.click()
  } else if ((event.key === 'Enter' || event.key === ' ') && !event.repeat) {
    // 统一通过一次 click 使用 EP 原有事件；阻止默认合成激活，避免 keydown/click 双发。
    if (group) title?.click()
    else target.click()
  }
}
</script>
