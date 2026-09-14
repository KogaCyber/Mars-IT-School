/**
 * Sayt bo'ylab yagona SEO manbasi.
 *
 * Bu fayl ikki joyda ishlatiladi:
 *  1. Ish vaqtida — `useSeo()` orqali sahifa meta-teglari va JSON-LD;
 *  2. Build vaqtida — `scripts/generate-seo.mjs` sitemap.xml, llms.txt va
 *     statik HTML (prerender) yasashda.
 *
 * Shuning uchun bu yerda faqat toza ma'lumot bo'ladi — brauzer API'lari yo'q,
 * Node ham shu faylni to'g'ridan-to'g'ri import qila oladi.
 *
 * Matnli maydonlar uch tilda beriladi: `L(uz, ru, en)`. Kerakli tilni
 * `resolvePage()` yoki `pick()` tanlaydi.
 */

import { stripBase } from './basePath.js'

/** Uch tilli qiymat. */
export const L = (uz, ru, en) => ({ uz, ru, en })

export { basePath, stripBase, withBase } from './basePath.js'

/**
 * Sahifaning MA'LUM BIR TILDAGI manzili.
 *
 * Nega yo'l prefiksi (`/ru/kursy`), `?lang=ru` emas:
 *
 *  1. Statik hostingda (Vercel) so'rov parametri BOSHQA fayl bera olmaydi —
 *     `?lang=ru` bilan kelgan robotga ham o'zbekcha HTML ketardi. Ya'ni
 *     hreflang uchta manzilni e'lon qilardi-yu, uchalasi ham bir xil tildagi
 *     sahifani qaytarardi.
 *  2. Javob beruvchi tizimlarning aksariyati (GPTBot, ClaudeBot,
 *     PerplexityBot, CCBot) JavaScript'ni UMUMAN ishlatmaydi. Ular uchun
 *     saytning ruscha va inglizcha versiyasi mavjud emas edi — bu Toshkent
 *     uchun eng katta yo'qotish, chunki qidiruvlarning katta qismi ruscha.
 *
 * Yo'l prefiksi bilan har bir til o'z faylida (`dist/ru/kursy/index.html`)
 * yotadi va JS'siz ham to'liq o'qiladi. Asosiy til (uz) prefikssiz qoladi,
 * shuning uchun mavjud havolalar o'zgarmaydi.
 */
export function localeUrl(origin, path, locale) {
  return `${origin}${localePath(path, locale)}`
}

/** Sahifaning ma'lum bir tildagi YO'LI (domensiz). */
export function localePath(path, locale) {
  const clean = path === '/' ? '/' : `/${String(path).replace(/^\/+|\/+$/g, '')}`
  if (locale === SITE.defaultLocale || !SITE.locales.includes(locale)) return clean
  return clean === '/' ? `/${locale}` : `/${locale}${clean}`
}

/**
 * Manzildan til prefiksini ajratadi.
 * @returns {{locale: string, path: string}}
 */
export function splitLocalePath(pathname) {
  // Sayt domen ildizida turmasligi mumkin (`/maktab/ru/kursy`) — prefiks
  // olib tashlanmasa til `sc`/`ma` kabi bo'lakdan qidirilib, topilmay qolardi.
  const clean = stripBase(pathname)
  const match = /^\/([a-z]{2})(\/|$)/.exec(clean)
  const code = match?.[1]
  if (code && code !== SITE.defaultLocale && SITE.locales.includes(code)) {
    const rest = clean.slice(code.length + 1) || '/'
    return { locale: code, path: rest.startsWith('/') ? rest : `/${rest}` }
  }
  return { locale: SITE.defaultLocale, path: clean }
}

/** Sahifaning barcha til variantlari — `hreflang` va sitemap uchun. */
export function localeAlternates(origin, path) {
  return [
    ...SITE.locales.map((code) => ({ hreflang: code, href: localeUrl(origin, path, code) })),
    { hreflang: 'x-default', href: localeUrl(origin, path, SITE.defaultLocale) },
  ]
}

export const SITE = {
  name: 'MARS IT School',
  legalName: 'MARS IT School',
  /** Production manzili — `.env` dagi VITE_SITE_URL bundan ustun turadi. */
  url: 'https://marsitschool.uz',
  logo: '/logo-mars.png',
  ogImage: '/og-image.png',
  themeColor: '#0B0B0F',
  defaultLocale: 'uz',
  locales: ['uz', 'ru', 'en'],
  /** og:locale uchun to'liq kodlar. */
  ogLocales: { uz: 'uz_UZ', ru: 'ru_RU', en: 'en_US' },
  twitter: '@marsitschool',
  founded: '2019',
  geo: {
    country: 'UZ',
    countryName: L('O‘zbekiston', 'Узбекистан', 'Uzbekistan'),
    region: 'UZ-TK',
    city: L('Toshkent', 'Ташкент', 'Tashkent'),
    latitude: 41.311081,
    longitude: 69.240562,
    placename: 'Tashkent',
  },
  contacts: {
    phone: '+998 78 777 77 57',
    email: 'info@marsitschool.uz',
  },
  /**
   * Odamlar maktabni qanday nomlaydi.
   *
   * Qidiruvda «MARS IT School» deb yozadiganlar oz. Ko'pchilik «IT o'quv
   * markazi», «IT kurslar», «kompyuter kurslari», «учебный центр» deb
   * qidiradi. Bu nomlar `Organization.alternateName`ga, llms.txt'ga va
   * sahifa kalit so'zlariga tushadi — shunda maktab aynan shu so'rovlar
   * bo'yicha ham topiladi.
   */
  alternateNames: [
    'MARS IT',
    'Mars IT School Tashkent',
    'MARS IT o‘quv markazi',
    'MARS IT kurslari',
    'МАРС АЙТИ',
    'MARS IT учебный центр',
    'MARS IT школа программирования',
  ],
  /**
   * Toshkentning maktab xizmat ko'rsatadigan tumanlari — lokal qidiruv (GEO)
   * uchun. «Chilonzorda IT kurslari» kabi so'rovlar aynan shu ro'yxat orqali
   * mos keladi.
   */
  districts: L(
    ['Yunusobod', 'Chilonzor', 'Mirobod', 'Shayxontohur', 'Yashnobod', 'Sergeli', 'Mirzo Ulug‘bek'],
    ['Юнусабадский', 'Чиланзарский', 'Мирабадский', 'Шайхантахурский', 'Яшнабадский', 'Сергелийский', 'Мирзо-Улугбекский'],
    ['Yunusabad', 'Chilanzar', 'Mirabad', 'Shaykhantakhur', 'Yashnabad', 'Sergeli', 'Mirzo Ulugbek'],
  ),
  /** Qabul va darslar vaqti — LocalBusiness sxemasi va lokal qidiruv uchun. */
  openingHours: [
    { days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], opens: '09:00', closes: '20:00' },
    { days: ['Saturday'], opens: '09:00', closes: '18:00' },
  ],
  social: [
    'https://t.me/marsitschool',
    'https://www.instagram.com/marsitschool',
    'https://www.youtube.com/@marsitschool',
  ],
  /** Sayt tavsifi — llms.txt va tashkilot sxemasi uchun. */
  tagline: L(
    'Toshkentdagi 7–17 yoshli bolalar va o‘smirlar uchun dasturlash maktabi.',
    'Школа программирования для детей и подростков 7–17 лет в Ташкенте.',
    'A programming school for children and teenagers aged 7–17 in Tashkent.',
  ),
}

/**
 * Uch tilli qiymatdan kerakli tildagisini oladi. Oddiy satr bo'lsa —
 * o'zini qaytaradi, shuning uchun har qanday maydonda ishlatish mumkin.
 */
export function pick(value, locale = SITE.defaultLocale) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value[locale] ?? value[SITE.defaultLocale] ?? Object.values(value)[0]
  }
  return value
}

/** Sitemap'ga tushmaydigan, indeksatsiyaga yopiq yo'llar. */
export const NOINDEX_PATTERNS = [/^\/test\/rezultat\//]

/** @returns {boolean} */
export function isNoindexPath(path) {
  return NOINDEX_PATTERNS.some((pattern) => pattern.test(path))
}
