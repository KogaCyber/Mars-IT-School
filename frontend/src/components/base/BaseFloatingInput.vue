<script setup>
/**
 * Pastki chiziqli maydon: bo'sh bo'lganda sarlavha maydon o'rnida turadi,
 * to'ldirilganda esa kichrayib tepaga ko'tariladi (Figma: vakansiya arizasi).
 */
import { computed, useId } from 'vue'

defineProps({
  label: { type: String, required: true },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
  autocomplete: { type: String, default: null },
  inputmode: { type: String, default: null },
})

const model = defineModel({ type: String, required: true })
const id = useId()

const isFilled = computed(() => Boolean(model.value))
</script>

<template>
  <div class="relative pt-4">
    <label
      :for="id"
      class="pointer-events-none absolute left-0 origin-left transition-all duration-200"
      :class="
        isFilled
          ? 'text-brand top-0 text-[0.72rem] opacity-100'
          : 'text-lead top-4 text-white/55 opacity-100'
      "
    >
      {{ label }}
    </label>

    <input
      :id="id"
      v-model="model"
      :type="type"
      :required="required"
      :autocomplete="autocomplete"
      :inputmode="inputmode"
      :aria-invalid="Boolean(error) || undefined"
      :aria-describedby="error ? `${id}-error` : undefined"
      class="text-lead w-full border-0 border-b bg-transparent pb-2.5 text-white transition outline-none"
      :class="error ? 'border-brand' : 'border-white/15 focus:border-brand'"
    />

    <p v-if="error" :id="`${id}-error`" class="text-brand mt-2 text-[0.78rem]">{{ error }}</p>
  </div>
</template>
