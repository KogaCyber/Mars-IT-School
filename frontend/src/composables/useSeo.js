/**
 * Sahifa meta-teglarini, canonical/hreflang havolalarini va JSON-LD'ni boshqaradi.
 *
 * SPA'da `<head>` faqat JavaScript orqali o'zgaradi, shuning uchun bu yerda
 * hamma narsa bitta joyda yig'ilgan:
 *  - SEO: title, description, canonical, robots, hreflang;
 *  - ijtimoiy tarmoqlar: Open Graph + Twitter Card;
 *  - AEO/LLMO: Schema.org JSON-LD (`@graph`) — javob beruvchi tizimlar sahifadagi
 *    faktlarni shu yerdan aniq o'qiydi.
 *
 * Build vaqtida `scripts/generate-seo.mjs` shu ma'lumotdan statik HTML yasaydi,
 * shuning uchun JS ishlatmaydigan crawler'lar ham to'liq meta ko'radi.
 */
import { watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { SITE, findStaticPage, isNoindexPath, localeAlternates, localeUrl } from '@/data/seoConfig'
import { useSiteStore } from '@/stores/site'
import {
  absoluteUrl,
  breadcrumbSchema,
  buildGraph,
  jsonLdScriptContent,
  organizationSchema,
  setSchemaLocale,
  setSchemaOrigin,
  webPageSchema,
  websiteSchema,
} from '@/utils/schema'

const JSONLD_ID = 'seo-jsonld'

/**
 * Canonical uchun sayt manzili. `.env` dagi qiymat ustun, lekin u lokal manzilda
 * qolib ketgan bo'lsa (tez-tez uchraydigan xato) — brauzerdagi haqiqiy domen olinadi,
 * aks holda productionda canonical `localhost`ga ishora qilib qolardi.
 */
function siteOrigin() {
  const host = typeof window !== 'undefined' ? window.location.origin : ''
  const fromEnv = String(import.meta.env.VITE_SITE_URL || '').replace(/\/$/, '')
  const envIsLocal = /localhost|127\.0\.0\.1/.test(fromEnv)
  const hostIsLocal = /localhost|127\.0\.0\.1/.test(host)
  if (fromEnv && !(envIsLocal && host && !hostIsLocal)) return fromEnv
  return host || SITE.url
}

function upsertMeta(attr, key, content) {
  if (!content) return
  const head = document.head
  let tag = head.querySelector(`meta[${attr}="${key}"]`)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute(attr, key)
    head.appendChild(tag)
  }
  tag.setAttribute('content', String(content))
}

function upsertLink(rel, href, extra = {}) {
  if (!href) return
  const head = document.head
  const selector = extra.hreflang
    ? `link[rel="${rel}"][hreflang="${extra.hreflang}"]`
    : `link[rel="${rel}"]:not([hreflang])`
  let tag = head.querySelector(selector)
  if (!tag) {
    tag = document.createElement('link')
    tag.setAttribute('rel', rel)
    Object.entries(extra).forEach(([name, value]) => tag.setAttribute(name, value))
    head.appendChild(tag)
  }
  tag.setAttribute('href', href)
}

/**
 * Bir xil nomdagi bir nechta meta-teg (`og:locale:alternate`) — ro'yxatni
 * to'liq qayta yozadi. `upsertMeta` bunga yaramaydi: u faqat BIRINCHISINI
 * topib yangilaydi, qolganlari shablondan qolib ketardi.
 */
function replaceMetaList(property, values) {
  const head = document.head
  head.querySelectorAll(`meta[property="${property}"]`).forEach((tag) => tag.remove())
  values.forEach((value) => {
    const tag = document.createElement('meta')
    tag.setAttribute('property', property)
    tag.setAttribute('content', value)
    head.appendChild(tag)
  })
}

/** Sahifaga tegishli bo'lmagan meta-tegni olib tashlaydi. */
function removeMeta(attr, key) {
  document.head.querySelector(`meta[${attr}="${key}"]`)?.remove()
}

function writeJsonLd(graph) {
  const existing = document.getElementById(JSONLD_ID)
  if (!graph) {
    existing?.remove()
    return
  }
  const script = existing || document.createElement('script')
  script.id = JSONLD_ID
  script.type = 'application/ld+json'
  // `textContent` HTML'ni tahlil qilmaydi, lekin bir xil seriyalashdan
  // foydalanamiz: prerender bilan natija bir xil bo'lsin va kimdir keyinchalik
  // buni `innerHTML` ga o'zgartirsa ham xavf paydo bo'lmasin.
  script.textContent = jsonLdScriptContent(graph)
  if (!existing) document.head.appendChild(script)
}

/** Meta-tavsif uzun bo'lsa qidiruv natijasida kesiladi — 160 belgigacha qisqartiramiz. */
function trim(text, limit = 160) {
  const value = String(text || '')
    .replace(/\s+/g, ' ')
    .trim()
  if (value.length <= limit) return value
  return `${value.slice(0, limit - 1).replace(/[\s,.;:—-]+$/, '')}…`
}

/**
 * @param {() => {
 *   title?: string,
 *   description?: string,
 *   image?: string,
 *   keywords?: string[],
 *   type?: 'website'|'article',
 *   noindex?: boolean,
 *   publishedAt?: string,
 *   modifiedAt?: string,
 *   breadcrumbs?: Array<{name: string, path: string}>,
 *   schema?: object|object[],
 * }} source
 */
export function useSeo(source) {
  const route = useRoute()
  const site = useSiteStore()
  const { t } = useI18n()

  watchEffect(() => {
    const meta = source() || {}
    const origin = siteOrigin()
    const path = route.path

    // Statik sahifa uchun oldindan yozilgan matn — sahifa o'zi bermasa zaxira bo'ladi.
    // JSON-LD ichidagi `@id`, `url` va rasm manzillari ham AYNAN shu domendan
    // qurilishi kerak — canonical bilan farq qilsa qidiruv tizimi ularni
    // boshqa sayt deb hisoblaydi.
    setSchemaOrigin(origin)

    const locale = site.language || SITE.defaultLocale
    // Canonical — AYNAN shu tildagi sahifa manzili. Uch til bir xil manzilni
    // ko'rsatsa Google ularni dublikat deb hisoblardi (seoConfig.js:localeUrl).
    const url = localeUrl(origin, path, locale)
    // JSON-LD ichidagi matnlar ham sayt tiliga ergashadi.
    setSchemaLocale(locale)
    const preset = findStaticPage(path, locale) || {}
    const title = meta.title || preset.title
    const description = trim(meta.description || preset.description)
    const keywords = meta.keywords || preset.keywords
    const image = absoluteUrl(meta.image || preset.image || SITE.ogImage, origin)
    const noindex = meta.noindex ?? isNoindexPath(path)

    // --- Asosiy ---
    document.title = title
      ? `${title} — ${SITE.name}`
      : `${SITE.name} — ${preset.title || t('seo.defaultTitle')}`
    document.documentElement.lang = locale

    upsertMeta('name', 'description', description)
    if (keywords?.length) upsertMeta('name', 'keywords', keywords.join(', '))
    else removeMeta('name', 'keywords')
    upsertMeta(
      'name',
      'robots',
      // `follow` — sahifa indeksga tushmaydi, lekin undagi ichki havolalar
      // baribir kuzatiladi. `generate-seo.mjs` ham aynan shu qiymatni yozadi;
      // ilgari ikkalasi farq qilardi (`nofollow` va `follow`).
      noindex
        ? 'noindex, follow'
        : 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1',
    )

    // --- Canonical va tillar ---
    upsertLink('canonical', url)
    localeAlternates(origin, path).forEach(({ hreflang, href }) => {
      upsertLink('alternate', href, { hreflang })
    })

    // --- Open Graph ---
    upsertMeta('property', 'og:type', meta.type || 'website')
    upsertMeta('property', 'og:site_name', SITE.name)
    upsertMeta('property', 'og:title', title || SITE.name)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:url', url)
    upsertMeta('property', 'og:image', image)
    // Shablondagi 1200×630 faqat standart `og-image.png` ga tegishli. Kurs yoki
    // yangilik rasmida o'lcham boshqacha — yolg'on qiymat qolsa Telegram va
    // Facebook oldindan ko'rishni noto'g'ri kesadi.
    if (image === absoluteUrl(SITE.ogImage, origin)) {
      upsertMeta('property', 'og:image:width', '1200')
      upsertMeta('property', 'og:image:height', '630')
    } else {
      removeMeta('property', 'og:image:width')
      removeMeta('property', 'og:image:height')
    }
    upsertMeta('property', 'og:image:alt', title || SITE.name)
    upsertMeta(
      'property',
      'og:locale',
      SITE.ogLocales[locale] || SITE.ogLocales[SITE.defaultLocale],
    )
    // Muqobil tillar — joriy tildan TASHQARI qolganlari. Shablonda ular
    // qattiq yozilgan (`ru_RU`, `en_US`), ya'ni ruscha sahifada asosiy til ham,
    // muqobil til ham `ru_RU` bo'lib qolardi.
    replaceMetaList(
      'og:locale:alternate',
      SITE.locales.filter((code) => code !== locale).map((code) => SITE.ogLocales[code]),
    )

    // Yangilikdan boshqa sahifaga o'tilganda maqola sanalari qolib ketmasin:
    // `<head>` SPA'da bir marta yasaladi va tozalanmasa oldingi sahifaning
    // sanasi yangi sahifada ham turaverardi.
    if (meta.publishedAt) upsertMeta('property', 'article:published_time', meta.publishedAt)
    else removeMeta('property', 'article:published_time')
    if (meta.modifiedAt) upsertMeta('property', 'article:modified_time', meta.modifiedAt)
    else removeMeta('property', 'article:modified_time')

    // --- Twitter / X ---
    upsertMeta('name', 'twitter:card', 'summary_large_image')
    upsertMeta('name', 'twitter:site', SITE.twitter)
    upsertMeta('name', 'twitter:title', title || SITE.name)
    upsertMeta('name', 'twitter:description', description)
    upsertMeta('name', 'twitter:image', image)

    // --- Structured data ---
    const extra = Array.isArray(meta.schema) ? meta.schema : meta.schema ? [meta.schema] : []
    writeJsonLd(
      buildGraph([
        organizationSchema(),
        websiteSchema(),
        webPageSchema({ url, title, description, image, locale }),
        meta.breadcrumbs?.length ? breadcrumbSchema(meta.breadcrumbs, origin) : null,
        ...extra,
      ]),
    )
  })

  // JSON-LD ataylab tozalanmaydi: har bir sahifada `useSeo` chaqiriladi va
  // blokni butunlay qayta yozadi. Unmount'da o'chirish esa sahifalar
  // almashuvida strukturali ma'lumotni bir zumga yo'qotishi mumkin edi.
}
