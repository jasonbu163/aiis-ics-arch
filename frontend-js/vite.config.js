import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { checkPageAccess } from './scripts/check-page-access.mjs'

export default defineConfig(async ({ mode }) => {
  // 加载环境变量
  await checkPageAccess(process.cwd(), mode)
  const env = loadEnv(mode, process.cwd(), '')
  const appPort = parseInt(env.VITE_APP_PORT) || 5190
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) {
              return
            }

            if (id.includes('echarts')) {
              return 'vendor-echarts'
            }

            if (id.includes('element-plus')) {
              return 'vendor-element-plus'
            }

            if (id.includes('@element-plus/icons-vue')) {
              return 'vendor-element-icons'
            }

            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vendor-vue'
            }
          }
        }
      }
    },
    server: {
      port: appPort,
      open: env.VITE_OPEN_BROWSER === 'true',
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
})
