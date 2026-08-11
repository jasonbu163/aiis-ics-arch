/**
 * File Path: /control-agent/src/app/plc/manifest.ts
 * Description: PLC diagnostics section manifest for the Control Agent console
 * Main Features:
 *   - Declares the local PLC diagnostics section id and title key
 *   - Binds the section to its Vue view component
 *   - Keeps PLC diagnostics navigation local to the Tauri console
 */
import { Cpu } from '@element-plus/icons-vue'
import PlcDiagnosticsView from './views/diagnostics/index.vue'
import type { ConsoleSectionManifest } from '../../console/types'

export const plcSectionManifest = {
  id: 'plc',
  titleKey: 'navigation.plc',
  icon: Cpu,
  order: 30,
  component: PlcDiagnosticsView
} satisfies ConsoleSectionManifest

export default plcSectionManifest
