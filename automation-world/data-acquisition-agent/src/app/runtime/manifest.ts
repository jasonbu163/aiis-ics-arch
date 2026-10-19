/**
 * File Path: /automation-world/data-acquisition-agent/src/app/runtime/manifest.ts
 * Description: Runtime overview section manifest for the Data Acquisition Agent console
 * Main Features:
 *   - Declares the local overview section id and title key
 *   - Binds the section to its Vue view component
 *   - Keeps navigation metadata local to the DAA UI
 */
import { DataBoard } from '@element-plus/icons-vue'
import RuntimeOverviewView from './views/overview/index.vue'
import type { ConsoleSectionManifest } from '../../console/types'

export const runtimeSectionManifest = {
  id: 'workbench',
  titleKey: 'navigation.workbench',
  icon: DataBoard,
  order: 10,
  component: RuntimeOverviewView
} satisfies ConsoleSectionManifest

export default runtimeSectionManifest
