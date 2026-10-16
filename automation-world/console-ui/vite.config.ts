/** Console UI 构建入口：独立端口，产物只写 CU dist。 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { sharedDesignProfileDev } from './scripts/shared-design-profile-dev.js'
export default defineConfig({
  plugins: [vue(), sharedDesignProfileDev()],
  server: { host: '0.0.0.0', port: 15193, strictPort: true },
  preview: { host: '0.0.0.0', port: 14193, strictPort: true },
  clearScreen: false
})
