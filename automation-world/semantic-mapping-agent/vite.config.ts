/** SMA仅编译CU公共源码，依赖由SMA自有安装与dedupe解析。 */
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
const own = (path: string) => fileURLToPath(new URL(path, import.meta.url));
export default defineConfig({
  plugins: [vue()], clearScreen: false,
  resolve: {
    alias: [
      { find: "@aw-ui", replacement: own("../console-ui/src/ui/index.ts") },
      { find: "@aw-ui-styles", replacement: own("../console-ui/src/ui/styles/index.css") },
      { find: "vue", replacement: own("node_modules/vue") },
      { find: "element-plus", replacement: own("node_modules/element-plus") },
      { find: "@element-plus/icons-vue", replacement: own("node_modules/@element-plus/icons-vue") },
    ], dedupe: ["vue", "element-plus", "@element-plus/icons-vue"],
  },
  preview: { host: "127.0.0.1", port: 14192, strictPort: true },
  server: { host: "127.0.0.1", port: 15192, strictPort: true,
    fs: { allow: [own("."), own("../console-ui/src/ui")] },
  },
});
