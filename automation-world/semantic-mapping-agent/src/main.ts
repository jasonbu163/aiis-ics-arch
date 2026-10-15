/**
 * File Path: /automation-world/semantic-mapping-agent/src/main.ts
 * Description: AIIS Semantic Mapping Agent Vue bootstrap and stylesheet assembly.
 * Main Features:
 *   - Loads shared and module styles before mounting the root Vue application
 */
import { createApp } from "vue";
import App from "./App.vue";
import "./styles.css";
import "./app/styles/shell.css";
import "./app/styles/shared.css";
import "./app/connection/styles.css";
import "./app/styles/responsive.css";

createApp(App).mount("#app");
