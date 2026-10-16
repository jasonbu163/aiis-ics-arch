/** CU 私有开发通道：显式提交完整快照，版本冲突不重试；仅内存保存应用结果和 HMR 页面状态。 */
import { ref, type Ref } from 'vue'
import { normalizeProfile, type DesignProfile } from '../ui/design-profile.js'

interface SharedDesignState {
  profile: Ref<DesignProfile>
  section: Ref<string>
  pending: Ref<boolean>
  available: Ref<boolean>
  result: Ref<string>
  initialized: boolean
  revision: string
  token: string
}
const endpoint = '/__cu/design-profile'
const failures = ['protected', 'invalid_request', 'invalid_profile', 'conflict', 'io_failed']
let state: SharedDesignState | undefined = import.meta.hot?.data.sharedDesignState
if (import.meta.hot) import.meta.hot.dispose(data => { data.sharedDesignState = state })

async function connect(current: SharedDesignState) {
  if (!import.meta.env.DEV) { current.result.value = 'unsupported'; return }
  try {
    const response = await fetch(endpoint, { headers: { 'X-CU-Request': 'design-profile' }, cache: 'no-store', credentials: 'same-origin' })
    const body = await response.json()
    if (!response.ok || typeof body.revision !== 'string' || typeof body.token !== 'string') throw new Error('unavailable')
    current.revision = body.revision
    current.token = body.token
    current.available.value = true
    current.result.value = ''
  } catch { current.result.value = 'unavailable' }
}
export function useSharedDesignProfile(defaults: unknown) {
  if (!state) state = {
    profile: ref(normalizeProfile(defaults)), section: ref('shell'), pending: ref(false),
    available: ref(false), result: ref('connecting'), initialized: false, revision: '', token: ''
  }
  const current = state
  if (!current.initialized) { current.initialized = true; void connect(current) }
  async function applyShared(input: unknown) {
    if (!current.available.value || current.pending.value) return
    let profile: DesignProfile
    try { profile = normalizeProfile(input) }
    catch { current.result.value = 'invalid_profile'; return }
    current.pending.value = true
    current.result.value = 'applying'
    try {
      const response = await fetch(endpoint, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CU-Session': current.token },
        body: JSON.stringify({ profile, expectedRevision: current.revision })
      })
      const body = await response.json()
      if (!response.ok) {
        current.result.value = failures.includes(body.code) ? body.code : 'network_failed'
        if (['conflict', 'io_failed', 'protected', 'network_failed'].includes(current.result.value)) current.available.value = false
        return
      }
      if (typeof body.revision !== 'string') throw new Error('invalid_response')
      current.revision = body.revision
      current.result.value = 'applied'
    } catch { current.result.value = 'network_failed'; current.available.value = false }
    finally { current.pending.value = false }
  }
  return { ...current, applyShared }
}
