<!-- SMA root assembles the inherited HTTP workspaces and isolated local startup state. -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ConnectionModuleView, loadAppDefaults } from "./app/connection";
import { externalIoEnabled } from "./app/connection/api";
import HelpCenterView from "./app/help/HelpCenterView.vue";
import { pageManifests, workspaceManifests } from "./app/registry";
import type { AppPage } from "./app/navigation";
import { isTauriRuntime } from "./app/tauri";
import { TwinFactsModuleView } from "./app/twin-facts";
import BackToTopButton from "./components/BackToTopButton.vue";
import { DEFAULT_LOCALE, getMessages } from "./locales";
import type { LocaleKey } from "./locales";
const locale = ref<LocaleKey>(DEFAULT_LOCALE);
const labels = computed(() => getMessages(locale.value));
const activePage = ref<AppPage>("backendConnection");
const activeView = ref("contract");
const ready = ref(false);
const ioEnabled = ref(false);
const sidebarCollapsed = ref(false);
const page = computed(() => pageManifests.find(p => p.id === activePage.value));
const resolve = (key: string) => (labels.value as unknown as Record<string, string>)[key] ?? key;
function select(id: AppPage) { activePage.value = id; activeView.value = page.value?.views?.[0]?.id ?? ""; }
onMounted(async () => { await loadAppDefaults(); ioEnabled.value = externalIoEnabled(); ready.value = true; });
</script>
<template>
 <main class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
  <aside v-if="!sidebarCollapsed" class="sidebar">
   <div class="brand-block"><p class="eyebrow">{{ labels.eyebrow }}</p><h1>{{ labels.appTitle }}</h1><p class="subtitle">{{ labels.subtitle }}</p></div>
   <nav class="sidebar-nav" :aria-label="labels.navigation">
    <div v-for="workspace in workspaceManifests" :key="workspace.id" class="nav-group"><p class="nav-item">{{ resolve(workspace.labelKey) }}</p><div class="nav-submenu"><button v-for="item in workspace.pages" :key="item.id" class="nav-subitem" :class="{ active: activePage === item.id }" @click="select(item.id)">{{ resolve(item.labelKey) }}</button></div></div>
   </nav>
   <div class="sidebar-footer"><span class="status-dot" />{{ labels.scaffoldStatus }}</div>
  </aside>
  <section class="main-surface">
   <header class="content-topbar"><div class="title-group"><button class="sidebar-toggle" :aria-label="labels.collapseSidebar" @click="sidebarCollapsed = !sidebarCollapsed">☰</button><h2>{{ page ? resolve(page.labelKey) : labels.helpCenterNav }}</h2></div><button class="icon-action" :aria-label="labels.languageToggle" @click="locale = locale === 'zh-CN' ? 'en-US' : 'zh-CN'">{{ locale === 'zh-CN' ? 'EN' : '中' }}</button></header>
   <section class="workspace">
    <p v-if="!ioEnabled" class="hint" role="status">{{ labels.externalIoDisabled }}</p>
    <ConnectionModuleView v-if="ready && activePage === 'backendConnection'" :labels="labels" />
    <HelpCenterView v-if="activePage === 'helpQuickStart'" :labels="labels" />
    <nav v-if="page?.views?.length" class="workspace-segmented"><button v-for="view in page.views" :key="view.id" :class="{ active: activeView === view.id }" @click="activeView = view.id">{{ resolve(view.labelKey) }}</button></nav>
    <div v-if="ready" v-show="!['backendConnection', 'helpQuickStart'].includes(activePage)"><TwinFactsModuleView :labels="labels" :enabled="isTauriRuntime()" :page="activePage" :view="activeView" /></div>
   </section>
  </section>
  <BackToTopButton :label="labels.backToTop" />
 </main>
</template>
