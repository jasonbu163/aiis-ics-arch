/**
 * File Path: /automation-world/data-acquisition-agent/vite.config.ts
 * Description: Vite configuration for the Data Acquisition Agent console
 * Main Features:
 *   - Uses Vue with TypeScript
 *   - Exposes a stable dev server port for Tauri
 *   - Keeps build output local to control-agent/dist
 */
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  build: { outDir: process.env.DS_FRONTEND_OUT_DIR || "dist", emptyOutDir: true },
  envDir: false,
  plugins: [vue()],
  resolve: {
    alias: {
      '@aw-ui': fileURLToPath(new URL('../console-ui/src/ui/index.ts', import.meta.url)),
      '@aw-ui-styles': fileURLToPath(new URL('../console-ui/src/ui/styles/index.css', import.meta.url))
    },
    dedupe: ['vue', 'element-plus', '@element-plus/icons-vue', 'vue-i18n']
  },
  server: {
    host: '127.0.0.1',
    port: 15194,
    fs: { allow: [fileURLToPath(new URL('.', import.meta.url)), fileURLToPath(new URL('../console-ui/src/ui', import.meta.url))] },
    strictPort: true
  },
  preview: {
    host: '127.0.0.1',
    port: 14194,
    strictPort: true
  },
  clearScreen: false
})
