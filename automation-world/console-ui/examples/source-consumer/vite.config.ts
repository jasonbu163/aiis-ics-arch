/** 独立消费者：只从 CU 公共入口编译，依赖由本工程统一解析。 */
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@aw-ui': fileURLToPath(new URL('../../src/ui/index.ts', import.meta.url)), '@aw-ui-styles': fileURLToPath(new URL('../../src/ui/styles/index.css', import.meta.url)) },
    dedupe: ['vue', 'element-plus', '@element-plus/icons-vue', 'vue-i18n']
  },
  server: { host: '127.0.0.1', port: 15194, strictPort: true, fs: { allow: ['../..'] } },
  preview: { host: '127.0.0.1', port: 14194, strictPort: true },
  build: { outDir: 'dist' }
})
