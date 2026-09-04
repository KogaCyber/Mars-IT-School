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
  organizationSchema,
  setSchemaLocale,
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

function writeJsonLd(graph) {
  const existing = document.getElementById(JSONLD_ID)
  if (!graph) {
    existing?.remove()
    return
  }
  const script = existing || document.createElement('script')
  script.id = JSONLD_ID
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(graph)
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
    upsertMeta(
      'name',
      'robots',
      noindex
        ? 'noindex, nofollow'
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
    upsertMeta('property', 'og:image:alt', title || SITE.name)
    upsertMeta('property', 'og:locale', SITE.ogLocales[locale] || SITE.ogLocales[SITE.defaultLocale])
    if (meta.publishedAt) upsertMeta('property', 'article:published_time', meta.publishedAt)
    if (meta.modifiedAt) upsertMeta('property', 'article:modified_time', meta.modifiedAt)

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
