<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="rounded-block border border-dashed border-line px-6 py-20 text-center">
    <h3 class="font-wide text-xl font-bold text-white">{{ title }}</h3>
    <p v-if="description" class="mx-auto mt-3 max-w-md text-sm text-muted">{{ description }}</p>
    <div class="mt-6"><slot /></div>
  </div>
</template>
