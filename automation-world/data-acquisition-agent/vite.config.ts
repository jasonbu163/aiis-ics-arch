/**
 * File Path: /automation-world/data-acquisition-agent/vite.config.ts
 * Description: Vite configuration for the Data Acquisition Agent console
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
    host: '127.0.0.1',
    port: 15191,
    strictPort: true
  },
  preview: {
    host: '127.0.0.1',
    port: 14191,
    strictPort: true
  },
  clearScreen: false
})
