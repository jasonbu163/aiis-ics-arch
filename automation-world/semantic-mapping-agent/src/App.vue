<!-- SMA消费CU公共壳层；主题、语言、导航与业务状态由本应用持有。 -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { Connection, DataAnalysis, Document, Grid, Link, Operation, Setting, Share, Tickets, VideoPlay } from "@element-plus/icons-vue";
import { ElConfigProvider } from "element-plus";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import en from "element-plus/es/locale/lang/en";
import { AgentLayout, AgentSidebar, AgentTopbar, ThemeToggle, LanguageSwitch, StatusCapsule, type NavigationItem } from "@aw-ui";
import { ConnectionModuleView, loadAppDefaults } from "./app/connection";
import { loadLocalConfiguration } from "./app/twin-facts/api/localConfiguration";
import { externalIoEnabled } from "./app/connection/api";
import { isTauriRuntime } from "./app/tauri";
import ConfigurationManagementPanel from "./app/configuration-management/components/ConfigurationManagementPanel.vue";
import FactSourcesPage from "./app/http-mapping/components/FactSourcesPage.vue";
import FactPointsPage from "./app/http-mapping/components/FactPointsPage.vue";
import TargetApisPage from "./app/http-mapping/components/TargetApisPage.vue";
import ValueRulesPage from "./app/http-mapping/components/ValueRulesPage.vue";
import MappingsPage from "./app/http-mapping/components/MappingsPage.vue";
import RuntimePage from "./app/http-mapping/components/RuntimePage.vue";
import { provideHttpMessages } from "./app/http-mapping/messages";
import BackToTopButton from "./components/BackToTopButton.vue";
import { getMessages } from "./locales";
import { useUiPreferences } from "./console/uiPreferences";
const { theme, locale, sidebarHidden } = useUiPreferences();
const labels = computed(() => getMessages(locale.value));
const ui = provideHttpMessages(locale);
const activeId = ref("connection");
const ready = ref(false);
const configurationError = ref("");
const ioEnabled = ref(false);
const native = isTauriRuntime();
const navigation = computed<NavigationItem[]>(() => [
  { id: "workbench-group", label: labels.value.navWorkbenchGroup, icon: Connection, children: [
    { id: "connection", label: labels.value.navBackendConnection, icon: Link },
    { id: "configuration", label: ui.value.configuration, icon: Document },
    { id: "runtime", label: ui.value.runtime, icon: VideoPlay },
  ] },
  { id: "facts-group", label: ui.value.sourceFacts, icon: DataAnalysis, children: [
    { id: "fact-sources", label: ui.value.factSources, icon: Connection },
    { id: "fact-points", label: ui.value.factPoints, icon: Tickets },
  ] },
  { id: "interfaces-group", label: labels.value.navInterfacesGroup, icon: Grid, children: [
    { id: "target-apis", label: ui.value.targetApis, icon: Setting },
  ] },
  { id: "mappings-group", label: labels.value.navMappingGroup, icon: Share, children: [
    { id: "value-rules", label: ui.value.valueRules, icon: Operation },
    { id: "mappings", label: ui.value.mappings, icon: Share },
  ] },
]);
const title = computed(() => navigation.value.flatMap(group => group.children ?? []).find(leaf => leaf.id === activeId.value)?.label ?? "");
function select(id: string) {
  if (navigation.value.some(group => group.children?.some(leaf => leaf.id === id))) activeId.value = id;
}
onMounted(async () => {
  try {
    await loadAppDefaults();
    ioEnabled.value = externalIoEnabled();
    if (native) await loadLocalConfiguration();
  } catch (error) {
    configurationError.value = String(error);
  } finally {
    ready.value = true;
  }
});
</script>
<template>
  <ElConfigProvider :locale="locale === 'zh-CN' ? zhCn : en">
    <div id="sma-overlays" class="aw-ui aw-ui--dense sma-overlays" :data-aw-theme="theme" />
    <AgentLayout class="aw-ui--dense" :theme="theme" :sidebar-hidden="sidebarHidden">
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
        <p v-if="configurationError" class="warning" role="alert">{{ labels.localConfigurationFailed }} {{ configurationError }}</p>
        <p v-if="!native" class="hint io-notice" role="status">{{ ui.desktopRequired }}</p>
        <p v-else-if="!ioEnabled" class="hint io-notice" role="status">{{ ui.httpDisabled }}</p>
        <p v-if="!ready" role="status">{{ labels.loading }}</p>
        <template v-else>
          <div v-show="activeId === 'connection'"><ConnectionModuleView :labels="labels" /></div>
          <ConfigurationManagementPanel v-if="activeId === 'configuration'" :labels="labels" />
          <RuntimePage v-else-if="activeId === 'runtime'" :native="native" :io-enabled="ioEnabled" />
          <FactSourcesPage v-else-if="activeId === 'fact-sources'" :io-enabled="ioEnabled" />
          <FactPointsPage v-else-if="activeId === 'fact-points'" :native="native" />
          <TargetApisPage v-else-if="activeId === 'target-apis'" :io-enabled="ioEnabled" />
          <ValueRulesPage v-else-if="activeId === 'value-rules'" />
          <MappingsPage v-else-if="activeId === 'mappings'" :io-enabled="ioEnabled" />
        </template>
      </section>
      <BackToTopButton :label="labels.backToTop" />
    </AgentLayout>
  </ElConfigProvider>
</template>
