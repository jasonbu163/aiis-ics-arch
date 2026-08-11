/**
 * File Path: /control-agent/src/env.d.ts
 * Description: Type declarations for Vite and Vue single-file components
 * Main Features:
 *   - Registers Vite client types
 *   - Allows importing .vue files in TypeScript
 */
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>
  export default component
}
