<!--
File Path: /automation-world/semantic-mapping-agent/src/components/BackToTopButton.vue
Description: Shared floating control for returning long TSS pages to the top.
Main Features: Appears after scrolling and respects reduced-motion preferences.
-->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

defineProps<{ label: string }>();
const visible = ref(false);

function updateVisibility() {
  visible.value = window.scrollY >= 160;
}

function scrollToTop() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" });
}

onMounted(() => {
  updateVisibility();
  window.addEventListener("scroll", updateVisibility, { passive: true });
});
onBeforeUnmount(() => window.removeEventListener("scroll", updateVisibility));
</script>

<template>
  <button
    v-if="visible"
    class="back-to-top"
    type="button"
    :aria-label="label"
    :title="label"
    @click="scrollToTop"
  >
    <span aria-hidden="true">↑</span>
  </button>
</template>

<style scoped>
.back-to-top {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 20;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: #fff;
  background: #23675c;
  border: 1px solid #174d45;
  border-radius: 50%;
  box-shadow: 0 6px 18px rgb(17 24 29 / 18%);
  font: inherit;
  font-size: 20px;
  cursor: pointer;
}

.back-to-top:hover,
.back-to-top:focus-visible {
  background: #174d45;
}

.back-to-top:focus-visible {
  outline: 3px solid #75a79c;
  outline-offset: 2px;
}

@media (max-width: 760px) {
  .back-to-top {
    right: 16px;
    bottom: 16px;
  }
}
</style>
