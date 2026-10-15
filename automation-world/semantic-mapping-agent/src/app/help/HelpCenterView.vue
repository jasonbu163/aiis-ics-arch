<!-- SMA local bilingual startup and mapping boundary reader; no backend help updates. -->
<script setup lang="ts">
import type { LocaleMessages } from "../../locales";
defineProps<{ labels: LocaleMessages }>();
</script>
<template><section class="panel"><h2>{{ labels.helpCenterNav }}</h2><h3>{{ labels.smaHelpIdentity }}</h3><p>{{ labels.smaHelpStartup }}</p><h3>{{ labels.smaHelpMapping }}</h3><p>{{ labels.smaHelpBoundary }}</p></section></template>
