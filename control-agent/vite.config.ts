/**
 * File Path: /control-agent/vite.config.ts
 * Description: Vite configuration for the Control Agent console
 * Main Features:
 *   - Uses Vue with TypeScript
 *   - Exposes a stable dev server port for Tauri
 *   - Keeps build output local to control-agent/dist
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 15190,
    strictPort: true
  },
  preview: {
    host: '0.0.0.0',
    port: 14190
  },
  clearScreen: false
})
