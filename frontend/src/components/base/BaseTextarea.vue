<script setup>
import { useId } from 'vue'

defineProps({
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  rows: { type: Number, default: 4 },
  maxlength: { type: Number, default: 1000 },
})

const model = defineModel({ type: String, required: true })
const id = useId()
</script>

<template>
  <div class="w-full">
    <label v-if="label" :for="id" class="mb-2 block text-sm text-white/70">{{ label }}</label>

    <textarea
      :id="id"
      v-model="model"
      :rows="rows"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :aria-invalid="Boolean(error) || undefined"
      class="w-full resize-y rounded-card border bg-surface px-6 py-4 text-base text-white transition placeholder:text-muted focus:outline-none"
      :class="error ? 'border-brand' : 'border-line focus:border-brand'"
    />

    <p v-if="error" class="mt-2 pl-4 text-sm text-brand">{{ error }}</p>
  </div>
</template>
