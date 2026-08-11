<template>
  <label class="file-input">
    <span>{{ label }}</span>
    <input type="file" :accept="accept" @change="handleChange" />
  </label>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  accept: string
}>()

const emit = defineEmits<{
  loaded: [text: string]
}>()

async function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) {
    return
  }
  emit('loaded', await file.text())
}
</script>
