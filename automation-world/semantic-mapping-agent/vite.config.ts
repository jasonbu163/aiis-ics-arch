import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  clearScreen: false,
  preview: { host: "127.0.0.1", port: 14192, strictPort: true },
  server: {
    host: "127.0.0.1",
    port: 15192,
    strictPort: true,
  },
});
