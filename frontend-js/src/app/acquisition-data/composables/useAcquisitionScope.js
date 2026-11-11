/** 文件路径: /frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js
 * 功能描述: 加载 PLC/DB 可读选项、隔离迟到响应，并按壳层实际高度适配本页。 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { getOptions } from '../api/index'

export const requestStatus = error => (error?.response?.status ?? error?.code) === 403 ? 'forbidden' : 'error'
export const rawValue = value => value === undefined ? '—' : JSON.stringify(value)
export const qualityKey = point => point.quality === 'bad' ? (point.reason === 'missing' ? 'missing' : 'bad') : 'good'
export const sourceKey = source => ['daa', 'external'].includes(source) ? source : 'unrecorded'

export function useAcquisitionScope() {
  const pageRoot = ref(null)
  const pagePadding = ref(0)
  const options = ref([])
  const optionsState = ref('loading')
  const plcId = ref('')
  const dbNumber = ref(null)
  const dbNumbers = computed(() => plcId.value
    ? options.value.find(item => item.plcId === plcId.value)?.dbNumbers || []
    : [...new Set(options.value.flatMap(item => item.dbNumbers))].sort((a, b) => a - b))
  const selection = () => ({
    ...(plcId.value ? { plcId: plcId.value } : {}),
    ...(typeof dbNumber.value === 'number' ? { dbNumber: dbNumber.value } : {})
  })
  let sequence = 0
  let layoutObserver

  // 壳层顶栏高度随宽度和文案变化；仅读取几何并调整本页，不更改壳层状态。
  function updatePagePadding() {
    const root = pageRoot.value
    const main = root?.closest('main')
    const header = main?.parentElement?.querySelector('header.header')
    if (!root || !main || !header) return
    const naturalTop = root.getBoundingClientRect().top + main.scrollTop
    pagePadding.value = Math.max(0, Math.ceil(header.getBoundingClientRect().bottom - naturalTop + 8))
  }
  watch(plcId, () => {
    if (typeof dbNumber.value === 'number' && !dbNumbers.value.includes(dbNumber.value)) dbNumber.value = null
  }, { flush: 'sync' })

  async function loadOptions() {
    const current = ++sequence
    options.value = []
    plcId.value = ''
    dbNumber.value = null
    optionsState.value = 'loading'
    try {
      const data = await getOptions()
      if (current !== sequence) return
      options.value = data.items
      optionsState.value = 'ready'
    } catch (error) {
      if (current !== sequence) return
      optionsState.value = requestStatus(error)
    }
  }

  onMounted(() => {
    const main = pageRoot.value?.closest('main')
    const header = main?.parentElement?.querySelector('header.header')
    if (main && header) {
      layoutObserver = new ResizeObserver(updatePagePadding)
      layoutObserver.observe(main)
      layoutObserver.observe(header)
      layoutObserver.observe(pageRoot.value)
      updatePagePadding()
    }
    loadOptions()
  })
  onBeforeUnmount(() => { sequence++; layoutObserver?.disconnect() })
  return { pageRoot, pagePadding, options, optionsState, plcId, dbNumber, dbNumbers, selection, loadOptions }
}
