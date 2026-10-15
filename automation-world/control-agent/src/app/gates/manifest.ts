/**
 * File Path: /control-agent/src/app/gates/manifest.ts
 * Description: Authorization gate diagnostics section manifest for the Control Agent console
 * Main Features:
 *   - Declares the local authorization gate section id and title key
 *   - Binds the section to its Vue view component
 *   - Keeps authorization self-test diagnostics separate from login concerns
 */
import { Key } from '@element-plus/icons-vue'
import AuthorizationGateView from './views/authorization/index.vue'
import type { ConsoleSectionManifest } from '../../console/types'

export const gatesSectionManifest = {
  id: 'gates',
  titleKey: 'navigation.gates',
  icon: Key,
  order: 40,
  component: AuthorizationGateView
} satisfies ConsoleSectionManifest

export default gatesSectionManifest
