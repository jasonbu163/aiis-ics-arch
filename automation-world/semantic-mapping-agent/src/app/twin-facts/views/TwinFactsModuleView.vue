<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/views/TwinFactsModuleView.vue
Description: Twin-facts module composition root.
Main Features: Owns JSON fact authoring, inspection, mapping, and both managed runtimes.
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
