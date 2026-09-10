/**
 * Sayt qaysi yo'l prefiksida turgani (`/` yoki `/maktab/`).
 *
 * Nega kerak: sayt domen ILDIZIDA emas, boshqa saytning ichki yo'lida ham
 * joylashtirilishi mumkin (masalan `core.marsit.uz/maktab/`). Vite build
 * vaqtida `base` ni biladi va faqat AKTIVLAR manzilini (`/maktab/assets/…`)
 * to'g'rilaydi. Qolgan uch joyni esa hech kim to'g'rilamaydi va ular
 * prefikssiz ishlab, 404 beradi:
 *
 *   1. `splitLocalePath()` — manzilning boshidan tilni o'qiydi. Prefiks
 *      olib tashlanmasa `/maktab/ru/kursy` da til «uz» deb aniqlanadi va
 *      router marshrutni topa olmaydi.
 *   2. `languageFromUrl()` — xuddi shu sabab: sayt ruscha manzilda ochilib,
 *      o'zbekcha kontent so'raydi.
 *   3. Sahifalar orasidagi to'liq o'tish (til almashtirgich, prerender
 *      qilingan HTML ichidagi `<a>` havolalari) — ular brauzerga manzil
 *      beradi, ya'ni prefiks ULARDA bo'lishi shart.
 *
 * Qiymat ikki manbadan olinadi, chunki bu modul ikki muhitda ishlaydi:
 * brauzerda (Vite `BASE_URL` ni build paytida qiymat bilan almashtiradi) va
 * Node'da (`scripts/generate-seo.mjs` — u yerda `import.meta.env` yo'q,
 * shuning uchun `VITE_BASE_PATH` muhit o'zgaruvchisi).
 */

const FROM_VITE =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || ''
const FROM_NODE =
  (globalThis.process && globalThis.process.env && globalThis.process.env.VITE_BASE_PATH) || ''

// Vite `BASE_URL` ni HAR DOIM beradi va prefiks berilmaganda u `/` bo'ladi —
// ya'ni "prefiks yo'q" degani. Shu sababli `/` qiymati Node fallback'ini
// bosib qo'ymasligi kerak: aks holda `generate-seo.mjs` bundle ichidan
// chaqirilganda prefiksni yo'qotardi.
const RAW_BASE = (FROM_VITE !== '/' ? FROM_VITE : '') || FROM_NODE || '/'

/**
 * Yo'l prefiksi boshida `/` bilan, oxirida `/` SIZ.
 * Domen ildizida — bo'sh satr, shunda `${BASE_PATH}${path}` doim to'g'ri chiqadi.
 */
export const BASE_PATH = `/${String(RAW_BASE).replace(/^\/+|\/+$/g, '')}`.replace(/^\/$/, '')

/** Sayt ichidagi yo'lga prefiksni qo'shadi (brauzerga beriladigan manzil uchun). */
export function withBase(path) {
  const clean = path === '/' ? '/' : `/${String(path).replace(/^\/+/, '')}`
  if (!BASE_PATH) return clean
  return clean === '/' ? `${BASE_PATH}/` : `${BASE_PATH}${clean}`
}

/**
 * Brauzerdagi manzildan prefiksni olib tashlaydi.
 *
 * Prefiks bo'lmasa yoki manzil unga mos kelmasa — manzil o'zgarishsiz
 * qaytadi: noto'g'ri kesish tilni yo'qotgandan ko'ra xavfsizroq.
 */
export function stripBase(pathname) {
  const value = String(pathname || '/')
  if (!BASE_PATH) return value
  if (value === BASE_PATH) return '/'
  return value.startsWith(`${BASE_PATH}/`) ? value.slice(BASE_PATH.length) : value
}
