/** 计划与实绩页面根据固定顶栏实际高度保留内容位置。 */
import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useTaskPagePadding() {
  const pageRoot = ref(null)
  const pagePadding = ref(0)
  let layoutObserver
  onMounted(() => {
    const root = pageRoot.value
    const main = root?.closest('main')
    const header = main?.parentElement?.querySelector('header.header')
    if (!main || !header) return
    function updatePagePadding() {
      const naturalTop = root.getBoundingClientRect().top + main.scrollTop
      pagePadding.value = Math.max(0, Math.ceil(header.getBoundingClientRect().bottom - naturalTop + 8))
    }
    if (typeof ResizeObserver !== 'undefined') {
      layoutObserver = new ResizeObserver(updatePagePadding)
      layoutObserver.observe(main)
      layoutObserver.observe(header)
      layoutObserver.observe(root)
    }
    updatePagePadding()
  })
  onBeforeUnmount(() => layoutObserver?.disconnect())
  return { pageRoot, pagePadding }
}
