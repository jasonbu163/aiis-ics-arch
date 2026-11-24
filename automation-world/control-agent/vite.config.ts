// CA 开发入口与 CU 公共源码解析。
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const local = (path: string) => fileURLToPath(new URL(path, import.meta.url))

export default defineConfig({
  envDir: false,
  plugins: [vue()],
  resolve: {
    alias: [
      { find: '@aw-ui', replacement: local('../console-ui/src/ui/index.ts') },
      { find: '@aw-ui-styles', replacement: local('../console-ui/src/ui/styles/index.css') },
      { find: 'vue', replacement: local('./node_modules/vue') },
      { find: 'element-plus', replacement: local('./node_modules/element-plus') },
      { find: '@element-plus/icons-vue', replacement: local('./node_modules/@element-plus/icons-vue') }
    ],
    dedupe: ['vue', 'element-plus', '@element-plus/icons-vue']
  },
  server: {
    host: '127.0.0.1',
    port: 15190,
    strictPort: true,
    fs: { allow: [local('.'), local('../console-ui/src/ui')] }
  },
  preview: { host: '127.0.0.1', port: 14190, strictPort: true },
  clearScreen: false
})
