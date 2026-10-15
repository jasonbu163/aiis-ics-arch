<!--
  File Path: /control-agent/src/components/shell/RuntimeStatusCapsule.vue
  Description: Compact runtime mode capsule for the Control Agent topbar
  Main Features:
    - Shows the current CA mode or write-mode status in the topbar
    - Uses CA theme tokens only
    - Does not represent business session state
-->
<template>
  <div class="runtime-status-capsule">
    <span class="status-dot" aria-hidden="true"></span>
    <span>{{ statusText }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  statusText: string
}>()
</script>
