<script setup>
/** Universal tugma: `to` berilsa RouterLink, `href` berilsa <a>, aks holda <button>. */
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary | outline | ghost | white
  size: { type: String, default: 'md' }, // sm | md | lg
  to: { type: [String, Object], default: null },
  href: { type: String, default: null },
  type: { type: String, default: 'button' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
})

const tag = computed(() => (props.to ? 'RouterLink' : props.href ? 'a' : 'button'))

/**
 * Tegga xos atributlar.
 *
 * `RouterLink` `href` ni manzildan o'zi hisoblaydi. Agar bu yerdan `href`
 * (hatto `null`/`undefined` bo'lsa ham) uzatilsa, u fallthrough atribut
 * sifatida RouterLink hisoblaganini BEKOR QILADI va `<a>` manzilsiz qoladi:
 * bunday havola tab tartibiga tushmaydi (klaviatura bilan birorta tugmaga
 * yetib bo'lmaydi), «yangi oynada ochish» ishlamaydi va qidiruv robotlari
 * ichki havolalarni ko'rmaydi. Shu sababli atribut qo'shilmaydi — o'chirilmaydi.
 */
const attrs = computed(() => {
  if (tag.value === 'RouterLink') return { to: props.to }
  if (tag.value === 'a') return { href: props.href, rel: 'noopener noreferrer' }
  return { type: props.type, disabled: props.disabled || props.loading }
})

const VARIANTS = {
  primary: 'bg-brand text-white hover:bg-brand-hover',
  outline: 'border border-white/25 text-white hover:border-white hover:bg-white/5',
  ghost: 'text-white hover:bg-white/10',
  white: 'bg-white text-ink hover:bg-white/90',
}

const SIZES = {
  sm: 'px-[1.6em] py-[0.7em] text-[var(--text-small)]',
  md: 'px-[2em] py-[1em]',
  lg: 'px-[2.5em] py-[1.15em]',
}

const classes = computed(() => [
  'press inline-flex cursor-pointer items-center justify-center gap-2 rounded-pill font-medium transition',
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand',
  'disabled:cursor-not-allowed disabled:opacity-60',
  VARIANTS[props.variant] ?? VARIANTS.primary,
  SIZES[props.size] ?? SIZES.md,
  props.block ? 'w-full' : '',
])
</script>

<template>
  <component :is="tag" v-bind="attrs" :aria-busy="loading || undefined" :class="classes">
    <span
      v-if="loading"
      class="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
      aria-hidden="true"
    />
    <slot />
  </component>
</template>
