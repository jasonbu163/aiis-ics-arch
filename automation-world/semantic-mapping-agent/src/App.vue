<!-- SMA消费CU公共壳层；主题、语言、导航与业务状态由本应用持有。 -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ElConfigProvider } from "element-plus";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import en from "element-plus/es/locale/lang/en";
import { AgentLayout, AgentSidebar, AgentTopbar, ThemeToggle, LanguageSwitch, StatusCapsule, type NavigationItem } from "@aw-ui";
import { ConnectionModuleView, loadAppDefaults } from "./app/connection";
import { loadLocalConfiguration } from "./app/twin-facts/api/localConfiguration";
import { externalIoEnabled } from "./app/connection/api";
import type { AppPage } from "./app/navigation";
import { isTauriRuntime } from "./app/tauri";
import { TwinFactsModuleView } from "./app/twin-facts";
import BackToTopButton from "./components/BackToTopButton.vue";
import { getMessages } from "./locales";
import { useUiPreferences } from "./console/uiPreferences";
const { theme, locale, sidebarHidden } = useUiPreferences();
const labels = computed(() => getMessages(locale.value));
const activePage = ref<AppPage>("backendConnection");
const activeView = ref("");
const ready = ref(false);
const configurationError = ref("");
const ioEnabled = ref(false);
const resolve = (key: string) => (labels.value as unknown as Record<string, string>)[key] ?? key;
const leaves = [
  { id: "connection", page: "backendConnection", view: "", label: "navBackendConnection" },
  { id: "source-facts", page: "twinFacts", view: "contract", label: "factsTableTitle" },
  { id: "api-materials", page: "mappingIdentity", view: "apiMaterials", label: "apiMaterialsTitle" },
  { id: "target-apis", page: "mappingIdentity", view: "targetApis", label: "targetApiConfigurationTitle" },
  { id: "value-rules", page: "mappingIdentity", view: "valueRules", label: "mappingValueRulesTitle" },
  { id: "mappings", page: "mappingIdentity", view: "mappings", label: "mappingConfigurationsTitle" },
  { id: "runtime", page: "mappingRuntime", view: "execution", label: "mappingExecutionTitle" },
] as const;
const activeId = computed(() => leaves.find(item => item.page === activePage.value && item.view === activeView.value)?.id ?? "connection");
const groups = [
  { id: "connection-group", label: "navConnectionGroup", ids: ["connection"] },
  { id: "facts-group", label: "sourceFactsWorkspace", ids: ["source-facts"] },
  { id: "interfaces-group", label: "navInterfacesGroup", ids: ["api-materials", "target-apis"] },
  { id: "mappings-group", label: "navMappingGroup", ids: ["value-rules", "mappings"] },
  { id: "runtime-group", label: "mappingRuntimeWorkspace", ids: ["runtime"] },
];
const navigation = computed<NavigationItem[]>(() => groups.map(group => ({ id: group.id, label: resolve(group.label), children: leaves.filter(leaf => group.ids.includes(leaf.id)).map(leaf => ({ id: leaf.id, label: resolve(leaf.label) })) })));
const title = computed(() => resolve(leaves.find(item => item.id === activeId.value)!.label));
function select(id: string) { const leaf = leaves.find(item => item.id === id); if (leaf) { activePage.value = leaf.page; activeView.value = leaf.view; } }
onMounted(async () => { try { await loadAppDefaults(); ioEnabled.value = externalIoEnabled(); if (isTauriRuntime()) await loadLocalConfiguration(); } catch (error) { configurationError.value = String(error); } finally { ready.value = true; } });
</script>
<template>
  <ElConfigProvider :locale="locale === 'zh-CN' ? zhCn : en">
    <div id="sma-overlays" class="aw-ui sma-overlays" :data-aw-theme="theme" />
    <AgentLayout :theme="theme" :sidebar-hidden="sidebarHidden">
      <template #sidebar><AgentSidebar :items="navigation" :active-id="activeId" :brand="labels.appTitle" :detail="labels.subtitle" @select="select" /></template>
      <template #topbar>
        <AgentTopbar :title="title" :subtitle="labels.eyebrow" :sidebar-hidden="sidebarHidden" :sidebar-label="sidebarHidden ? labels.expandSidebar : labels.collapseSidebar" @toggle-sidebar="sidebarHidden = !sidebarHidden">
          <template #actions>
            <StatusCapsule :label="ioEnabled ? labels.httpEnabled : labels.httpDisabled" :tone="ioEnabled ? 'warning' : 'neutral'" />
            <ThemeToggle :theme="theme" :label="theme === 'light' ? labels.switchToDark : labels.switchToLight" @toggle="theme = theme === 'light' ? 'dark' : 'light'" />
            <LanguageSwitch :locale="locale" :zh-label="labels.languageChineseShort" :en-label="labels.languageEnglishShort" :label="labels.languageToggle" @toggle="locale = locale === 'zh-CN' ? 'en-US' : 'zh-CN'" />
          </template>
        </AgentTopbar>
      </template>
      <section class="sma-content workspace">
        <p class="hint io-notice" role="status">{{ labels.localConfigurationOnly }}</p>
        <p v-if="configurationError" class="warning" role="alert">{{ labels.localConfigurationFailed }} {{ configurationError }}</p>
        <p v-if="!ioEnabled" class="hint io-notice" role="status">{{ labels.externalIoDisabled }}</p>
        <p v-if="!ready" role="status">{{ labels.loading }}</p>
        <div v-if="ready" v-show="activePage === 'backendConnection'"><ConnectionModuleView :labels="labels" /></div>
        <div v-if="ready" v-show="activePage !== 'backendConnection'"><TwinFactsModuleView :labels="labels" :enabled="isTauriRuntime()" :page="activePage" :view="activeView" /></div>
      </section>
      <BackToTopButton :label="labels.backToTop" />
    </AgentLayout>
  </ElConfigProvider>
</template>
