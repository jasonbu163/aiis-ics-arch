/**
 * File Path: /control-agent/src/console/sections.ts
 * Description: Local section registry for the Control Agent operations console
 * Main Features:
 *   - Aggregates CA-owned section manifests
 *   - Orders sections for sidebar rendering
 *   - Avoids business-frontend menu or permission dependencies
 */
import collectionSectionManifest from '../app/collection/manifest'
import gatesSectionManifest from '../app/gates/manifest'
import plcSectionManifest from '../app/plc/manifest'
import runtimeSectionManifest from '../app/runtime/manifest'
import type { ConsoleSectionManifest } from './types'

export const consoleSections: ConsoleSectionManifest[] = [
  runtimeSectionManifest,
  collectionSectionManifest,
  plcSectionManifest,
  gatesSectionManifest
].sort((left, right) => left.order - right.order)
