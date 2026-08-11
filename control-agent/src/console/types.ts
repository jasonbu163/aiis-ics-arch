/**
 * File Path: /control-agent/src/console/types.ts
 * Description: Shared TypeScript contracts for the Control Agent console layer
 * Main Features:
 *   - Defines local console section ids
 *   - Defines section manifest metadata
 *   - Defines reusable metric and readiness item shapes
 */
import type { Component } from 'vue'

export type ConsoleSectionId = 'overview' | 'collection' | 'plc' | 'gates'

export interface ConsoleSectionManifest {
  id: ConsoleSectionId
  titleKey: string
  icon: Component
  order: number
  component: Component
}

export interface MetricItem {
  key: string
  labelKey: string
  value: string
}

export type OperationTone = 'ready' | 'observing' | 'locked' | 'blocked'

export interface OperationItem {
  key: string
  labelKey: string
  stateText: string
  detailText: string
  tone: OperationTone
}
