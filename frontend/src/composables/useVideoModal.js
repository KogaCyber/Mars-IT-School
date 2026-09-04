/**
 * Butun sayt bo'yicha yagona video ko'ruvchi (modal).
 *
 * Holat modul darajasida saqlanadi — istalgan komponent `openVideo(url)` bilan
 * videoni ochadi, ko'rsatishni esa `App.vue`dagi bitta `BaseVideoModal`
 * bajaradi. Foydalanuvchi saytdan chiqib ketmaydi: YouTube/Vimeo havolalari
 * `iframe` ichida, to'g'ridan-to'g'ri fayllar esa `<video>` orqali o'ynatiladi.
 */
import { computed, ref } from 'vue'

const source = ref('')
const title = ref('')
const isOpen = ref(false)

/** YouTube havolasining barcha ko'rinishlaridan video ID'sini ajratadi. */
function youtubeId(url) {
  const patterns = [
    /youtu\.be\/([\w-]{6,})/,
    /youtube\.com\/(?:watch\?(?:.*&)?v=)([\w-]{6,})/,
    /youtube\.com\/(?:embed|v|shorts|live)\/([\w-]{6,})/,
  ]

  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  return ''
}

function vimeoId(url) {
  const match = url.match(/vimeo\.com\/(?:video\/)?(\d+)/)
  return match ? match[1] : ''
}

/** Havolaning boshlanishidagi vaqt belgisi (`?t=90`, `#t=1m30s`). */
function startSeconds(url) {
  const match = url.match(/[?&#]t=(?:(\d+)m)?(\d+)m?s?/)
  if (!match) return 0
  return Number(match[1] || 0) * 60 + Number(match[2] || 0)
}

/**
 * Havolani ichki pleyer uchun tavsifga aylantiradi.
 * @returns {{kind: 'embed'|'file', src: string} | null}
 */
export function resolveVideo(url) {
  const value = String(url || '').trim()
  if (!value) return null

  const yt = youtubeId(value)
  if (yt) {
    const start = startSeconds(value)
    const params = new URLSearchParams({ autoplay: '1', rel: '0', modestbranding: '1' })
    if (start) params.set('start', String(start))
    return { kind: 'embed', src: `https://www.youtube-nocookie.com/embed/${yt}?${params}` }
  }

  const vimeo = vimeoId(value)
  if (vimeo) {
    return { kind: 'embed', src: `https://player.vimeo.com/video/${vimeo}?autoplay=1` }
  }

  if (/\.(mp4|webm|ogv|ogg|mov|m4v)(\?|#|$)/i.test(value)) {
    return { kind: 'file', src: value }
  }

  // Noma'lum manba ichki pleyerda OCHILMAYDI.
  //
  // Ilgari bu yerda ixtiyoriy havola `iframe` ichiga qo'yilardi. Ikki muammo:
  // productionda CSP `frame-src` faqat YouTube va Vimeo'ga ruxsat beradi, ya'ni
  // modal ochilib ichi bo'sh qolardi; ikkinchidan admin paneldagi har qanday
  // havola sayt ichida chizilib, foydalanuvchi uchun bizning kontentimizdek
  // ko'rinardi. Endi `null` qaytadi — chaqiruvchi tomon (`isPlayable`) tugmani
  // ko'rsatmaydi va havola oddiy tashqi havola bo'lib qoladi.
  return null
}

/** Havola ichki pleyerda ochilishi mumkinmi (aks holda oddiy havola qoladi). */
export function isPlayable(url) {
  return Boolean(resolveVideo(url))
}

/**
 * @param {string} url video havolasi
 * @param {string} [label] ekran o'quvchilar uchun nom
 */
export function openVideo(url, label = '') {
  const resolved = resolveVideo(url)
  if (!resolved) return

  source.value = url
  title.value = label
  isOpen.value = true
}

export function closeVideo() {
  isOpen.value = false
  // `iframe` darhol o'chirilmasa ovoz modal yopilgach ham davom etardi.
  source.value = ''
}

export function useVideoModal() {
  const video = computed(() => resolveVideo(source.value))
  return { isOpen, title, video, close: closeVideo }
}
