<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/views/TwinFactsModuleView.vue
Description: Twin-facts module composition root.
Main Features: Composes read-only source facts, mapping configuration, and HTTP mapping runtime.
-->
<script setup lang="ts">
import type { LocaleMessages } from "../../../locales";
import type { AppPage } from "../../navigation";
import TwinJsonContractPanel from "../components/TwinJsonContractPanel.vue";

defineProps<{
  labels: LocaleMessages;
  enabled: boolean;
  page: AppPage;
  view: string;
}>();
</script>

<template>
  <TwinJsonContractPanel :labels="labels" :enabled="enabled" :page="page" :view="view" />
</template>
