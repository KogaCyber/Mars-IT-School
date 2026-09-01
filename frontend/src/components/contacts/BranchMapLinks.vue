<script setup>
/**
 * Filialni xaritada ochish tugmalari — Yandex Maps va Google Maps.
 *
 * Har bir xizmat uchun admin panelda alohida havola bor
 * (`map_url_yandex`, `map_url_google`). Havola kiritilmagan bo'lsa,
 * manzil koordinatalaridan avtomatik quriladi.
 */
import { computed } from 'vue'

const props = defineProps({
  branch: { type: Object, required: true },
})

const hasCoords = computed(() => Boolean(props.branch.latitude && props.branch.longitude))

const yandexUrl = computed(() => {
  if (props.branch.map_url_yandex) return props.branch.map_url_yandex
  if (!hasCoords.value) return ''
  return `https://yandex.uz/maps/?pt=${props.branch.longitude},${props.branch.latitude}&z=17&l=map`
})

const googleUrl = computed(() => {
  if (props.branch.map_url_google) return props.branch.map_url_google
  if (!hasCoords.value) return ''
  return `https://www.google.com/maps/search/?api=1&query=${props.branch.latitude},${props.branch.longitude}`
})
</script>

<template>
  <div v-if="yandexUrl || googleUrl" class="grid grid-cols-2 gap-3">
    <a
      v-if="yandexUrl"
      :href="yandexUrl"
      target="_blank"
      rel="noopener"
      class="btn-map rounded-pill bg-surface hover:bg-surface-2 flex items-center justify-center gap-2.5 px-4 py-[1.05em] text-center font-bold whitespace-nowrap text-white transition"
    >
      <svg class="size-[1.35em] shrink-0" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2.5a7 7 0 0 0-7 7c0 5 7 12 7 12s7-7 7-12a7 7 0 0 0-7-7Z" fill="#FC3F1D" />
        <circle cx="12" cy="9.5" r="2.6" fill="#fff" />
      </svg>
      Yandex Maps
    </a>

    <a
      v-if="googleUrl"
      :href="googleUrl"
      target="_blank"
      rel="noopener"
      class="btn-map rounded-pill bg-surface hover:bg-surface-2 flex items-center justify-center gap-2.5 px-4 py-[1.05em] text-center font-bold whitespace-nowrap text-white transition"
    >
      <svg class="size-[1.35em] shrink-0" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2.5a7 7 0 0 0-7 7c0 5 7 12 7 12s7-7 7-12a7 7 0 0 0-7-7Z" fill="#34A853" />
        <path d="M5.6 6.2A7 7 0 0 1 12 2.5c2 0 3.8.8 5 2.2L12 9.5 5.6 6.2Z" fill="#4285F4" />
        <path d="M5 9.5a7 7 0 0 1 .6-3.3L12 9.5l-4.4 5.2A16 16 0 0 1 5 9.5Z" fill="#FBBC04" />
        <path d="M12 21.5s-2.2-2.2-4.1-5l4.1-7 5 2.7c0 4.6-5 9.3-5 9.3Z" fill="#EA4335" />
        <circle cx="12" cy="9.5" r="2.6" fill="#fff" />
      </svg>
      Google Maps
    </a>
  </div>
</template>

<style scoped>
/* Yozuv doim bitta qatorda tursin — kartochka torayganda kichrayadi */
.btn-map {
  font-size: clamp(0.8125rem, 0.83vw, 1rem);
}
</style>
