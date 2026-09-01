<script setup>
import { computed, useId } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  autocomplete: { type: String, default: null },
  /**
   * `pill` — standart to'ldirilgan maydon;
   * `line` — faqat pastki chiziqli maydon (Figma: «Бесплатная консультация»),
   * bunda sarlavha maydon ichida placeholder sifatida ko'rinadi.
   */
  variant: { type: String, default: 'pill' },
})

const model = defineModel({ type: String, required: true })
const id = useId()

const isLine = computed(() => props.variant === 'line')

/** `line` ko'rinishida sarlavha ekranda ko'rinmaydi — placeholder uni almashtiradi. */
const inputPlaceholder = computed(() => props.placeholder || (isLine.value ? props.label : ''))

const inputClass = computed(() =>
  isLine.value
    ? [
        'w-full border-0 border-b bg-transparent px-0 py-[0.9em] text-white transition',
        'placeholder:text-white/55 focus:outline-none disabled:opacity-60',
        props.error ? 'border-brand' : 'border-white/15 focus:border-brand',
      ]
    : [
        'rounded-pill bg-surface w-full border px-6 py-4 text-base text-white transition',
        'placeholder:text-muted focus:outline-none disabled:opacity-60',
        props.error ? 'border-brand' : 'border-line focus:border-brand',
      ],
)
</script>

<template>
  <div class="w-full">
    <label v-if="label" :for="id" :class="isLine ? 'sr-only' : 'mb-2 block text-sm text-white/70'">
      {{ label }}
      <span v-if="required && !isLine" class="text-brand" aria-hidden="true">*</span>
    </label>

    <input
      :id="id"
      v-model="model"
      :type="type"
      :placeholder="inputPlaceholder"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :aria-invalid="Boolean(error) || undefined"
      :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
      :class="inputClass"
    />

    <p
      v-if="error"
      :id="`${id}-error`"
      class="text-brand mt-2 text-sm"
      :class="{ 'pl-4': !isLine }"
    >
      {{ error }}
    </p>
    <p
      v-else-if="hint"
      :id="`${id}-hint`"
      class="text-muted mt-2 text-sm"
      :class="{ 'pl-4': !isLine }"
    >
      {{ hint }}
    </p>
  </div>
</template>
