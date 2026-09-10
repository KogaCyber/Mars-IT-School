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

function rawBase() {
  const fromVite =
    (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.BASE_URL) || ''
  const fromNode =
    (globalThis.process && globalThis.process.env && globalThis.process.env.VITE_BASE_PATH) || ''

  // Vite `BASE_URL` ni HAR DOIM beradi va prefiks berilmaganda u `/` bo'ladi —
  // ya'ni "prefiks yo'q" degani. Shu sababli `/` qiymati Node fallback'ini
  // bosib qo'ymasligi kerak.
  return (fromVite !== '/' ? fromVite : '') || fromNode || '/'
}

/**
 * Yo'l prefiksi boshida `/` bilan, oxirida `/` SIZ.
 * Domen ildizida — bo'sh satr, shunda `${basePath()}${path}` doim to'g'ri chiqadi.
 *
 * Qiymat ATAYLAB har chaqiruvda hisoblanadi, modul yuklanganda EMAS:
 * `scripts/generate-seo.mjs` `.env.production` ni O'ZI o'qiydi, importlar esa
 * undan oldin bajariladi. Bir marta hisoblanganda prefiks hali muhitda
 * bo'lmasdi va prerender qilingan HTML'dagi havolalar prefikssiz chiqib
 * ketardi — build yashil, sayt esa 404. Brauzerda bu bepul: Vite `BASE_URL`
 * ni build vaqtida o'zgarmas qiymatga almashtiradi.
 */
export function basePath() {
  return `/${String(rawBase()).replace(/^\/+|\/+$/g, '')}`.replace(/^\/$/, '')
}

/** Sayt ichidagi yo'lga prefiksni qo'shadi (brauzerga beriladigan manzil uchun). */
export function withBase(path) {
  const prefix = basePath()
  const clean = path === '/' ? '/' : `/${String(path).replace(/^\/+/, '')}`
  if (!prefix) return clean
  return clean === '/' ? `${prefix}/` : `${prefix}${clean}`
}

/**
 * Brauzerdagi manzildan prefiksni olib tashlaydi.
 *
 * Prefiks bo'lmasa yoki manzil unga mos kelmasa — manzil o'zgarishsiz
 * qaytadi: noto'g'ri kesish tilni yo'qotgandan ko'ra xavfsizroq.
 */
export function stripBase(pathname) {
  const prefix = basePath()
  const value = String(pathname || '/')
  if (!prefix) return value
  if (value === prefix) return '/'
  return value.startsWith(`${prefix}/`) ? value.slice(prefix.length) : value
}
