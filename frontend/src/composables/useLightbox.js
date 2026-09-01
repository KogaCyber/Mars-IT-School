/**
 * Butun sayt bo'yicha yagona rasm ko'ruvchi (lightbox).
 *
 * Holat modul darajasida saqlanadi — istalgan komponent `openLightbox()` bilan
 * suratlarni ochadi, ko'rsatishni esa `App.vue`dagi bitta `BaseLightbox`
 * bajaradi (har bir galereya o'z modalini takrorlamaydi).
 */
import { computed, ref } from 'vue'

/** @type {import('vue').Ref<{src: string, alt?: string}[]>} */
const images = ref([])
const index = ref(0)
const isOpen = ref(false)

/** Turli manbalarni (satr, `{src}`, `{image, caption}`) yagona ko'rinishga keltiradi. */
function normalize(item) {
  if (typeof item === 'string') return { src: item, alt: '' }
  return {
    src: item.src || item.image || item.url || '',
    alt: item.alt || item.caption || '',
  }
}

/**
 * @param {Array} list suratlar ro'yxati
 * @param {number} startIndex qaysi suratdan boshlansin
 */
export function openLightbox(list, startIndex = 0) {
  const items = (Array.isArray(list) ? list : [list]).map(normalize).filter((item) => item.src)
  if (!items.length) return

  images.value = items
  index.value = Math.min(Math.max(startIndex, 0), items.length - 1)
  isOpen.value = true
}

export function closeLightbox() {
  isOpen.value = false
}

export function useLightbox() {
  const current = computed(() => images.value[index.value] || null)

  /** Oldinga/orqaga aylanib o'tadi (oxiridan boshiga qaytadi). */
  function step(delta) {
    const count = images.value.length
    if (!count) return
    index.value = (index.value + delta + count) % count
  }

  return { images, index, isOpen, current, step, close: closeLightbox }
}
