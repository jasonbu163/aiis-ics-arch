/**
 * File Path: /control-agent/src/app/collection/manifest.ts
 * Description: PLC collection status section manifest for the Control Agent console
 * Main Features:
 *   - Declares the local collection section id and title key
 *   - Binds the section to its Vue view component
 *   - Keeps collection UI routing independent from the business frontend
 */
import { Operation } from '@element-plus/icons-vue'
import CollectionStatusView from './views/status/index.vue'
import type { ConsoleSectionManifest } from '../../console/types'

export const collectionSectionManifest = {
  id: 'collection',
  titleKey: 'navigation.collection',
  icon: Operation,
  order: 20,
  component: CollectionStatusView
} satisfies ConsoleSectionManifest

export default collectionSectionManifest
