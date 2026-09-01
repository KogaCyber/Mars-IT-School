/**
 * Schema.org (JSON-LD) tuzuvchilari.
 *
 * Nega kerak: qidiruv tizimlari uchun — boy natijalar (rich results),
 * generativ javoblar (ChatGPT, Perplexity, AI Overviews) uchun — sahifadagi
 * faktlarni bir xilda o'qish imkoni. Barcha funksiyalar sof: brauzer API'siz,
 * shuning uchun build skriptida ham ishlaydi.
 */
// Nisbiy yo'l (`@/` emas) — bu faylni build skripti Node'da to'g'ridan-to'g'ri import qiladi.
import { SITE, pick } from '../data/seoConfig.js'

/**
 * Sxemalarda shahar/mamlakat nomi va matnlar sayt tiliga bog'liq.
 * `setSchemaLocale()` uni til almashganda yangilaydi.
 */
let schemaLocale = SITE.defaultLocale

export function setSchemaLocale(locale) {
  if (SITE.locales.includes(locale)) schemaLocale = locale
}

/** Joriy sxema tili. */
export const schemaLang = () => schemaLocale

/** Uch tilli qiymatni joriy sxema tilida beradi. */
const loc = (value) => pick(value, schemaLocale)

/** Sxemalarda ishlatiladigan qisqa matnlar. */
const SCHEMA_TEXT = {
  uz: {
    orgDescription:
      'Toshkentdagi 7–17 yoshli bolalar va o‘smirlar uchun dasturlash maktabi: veb-dasturlash, Python, o‘yin yaratish va robototexnika.',
    audience: 'Bolalar va o‘smirlar',
  },
  ru: {
    orgDescription:
      'Школа программирования для детей и подростков 7–17 лет в Ташкенте: веб-разработка, Python, создание игр и робототехника.',
    audience: 'Дети и подростки',
  },
  en: {
    orgDescription:
      'A programming school for children and teenagers aged 7–17 in Tashkent: web development, Python, game creation and robotics.',
    audience: 'Children and teenagers',
  },
}

const text = (key) => (SCHEMA_TEXT[schemaLocale] || SCHEMA_TEXT[SITE.defaultLocale])[key]

/** Nisbiy manzilni absolyutga aylantiradi. */
export function absoluteUrl(path = '/', origin = SITE.url) {
  if (!path) return origin
  if (/^https?:\/\//i.test(path)) return path
  return `${String(origin).replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}

const ORG_ID = () => `${SITE.url}/#organization`
const SITE_ID = () => `${SITE.url}/#website`

/** Maktabning o'zi — barcha boshqa tugunlar shu `@id`ga havola qiladi. */
export function organizationSchema(overrides = {}) {
  return {
    '@type': ['EducationalOrganization', 'LocalBusiness'],
    '@id': ORG_ID(),
    name: SITE.name,
    legalName: SITE.legalName,
    url: SITE.url,
    logo: { '@type': 'ImageObject', url: absoluteUrl(SITE.logo), width: 500, height: 500 },
    image: absoluteUrl(SITE.ogImage),
    description: text('orgDescription'),
    foundingDate: SITE.founded,
    email: SITE.contacts.email,
    telephone: SITE.contacts.phone,
    priceRange: '$$',
    areaServed: { '@type': 'City', name: loc(SITE.geo.city) },
    address: {
      '@type': 'PostalAddress',
      addressCountry: SITE.geo.country,
      addressRegion: loc(SITE.geo.city),
      addressLocality: loc(SITE.geo.city),
    },
    geo: {
      '@type': 'GeoCoordinates',
      latitude: SITE.geo.latitude,
      longitude: SITE.geo.longitude,
    },
    sameAs: SITE.social,
    knowsLanguage: SITE.locales,
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: SITE.contacts.phone,
      email: SITE.contacts.email,
      contactType: 'customer service',
      areaServed: SITE.geo.country,
      availableLanguage: ['Russian', 'Uzbek', 'English'],
    },
    ...overrides,
  }
}

/** Sayt + ichki qidiruv (qidiruv natijasida sitelinks searchbox uchun). */
export function websiteSchema() {
  return {
    '@type': 'WebSite',
    '@id': SITE_ID(),
    url: SITE.url,
    name: SITE.name,
    inLanguage: schemaLocale,
    publisher: { '@id': ORG_ID() },
  }
}

/** Sahifaning o'zi. */
export function webPageSchema({ url, title, description, image, locale, datePublished }) {
  return {
    '@type': 'WebPage',
    '@id': `${url}#webpage`,
    url,
    name: title,
    description,
    inLanguage: locale || schemaLocale,
    isPartOf: { '@id': SITE_ID() },
    about: { '@id': ORG_ID() },
    ...(image ? { primaryImageOfPage: { '@type': 'ImageObject', url: image } } : {}),
    ...(datePublished ? { datePublished } : {}),
  }
}

/**
 * Non-havola zanjiri.
 * @param {Array<{name: string, path: string}>} items
 */
export function breadcrumbSchema(items, origin = SITE.url) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: absoluteUrl(item.path, origin),
    })),
  }
}

/** FAQ bloki — AEO'ning asosiy formati (savol → qisqa javob). */
export function faqSchema(items) {
  const list = (items || [])
    .map((item) => ({ q: item.question || item.title, a: item.answer || item.body }))
    .filter((item) => item.q && item.a)
  if (!list.length) return null
  return {
    '@type': 'FAQPage',
    mainEntity: list.map((item) => ({
      '@type': 'Question',
      name: String(item.q),
      acceptedAnswer: { '@type': 'Answer', text: String(item.a) },
    })),
  }
}

/** Kurs — `Course` + `CourseInstance` (jadval va formatsiz rich result chiqmaydi). */
export function courseSchema(course, url) {
  if (!course) return null
  const audience =
    course.age_from || course.age_to
      ? {
          '@type': 'PeopleAudience',
          audienceType: text('audience'),
          ...(course.age_from ? { suggestedMinAge: course.age_from } : {}),
          ...(course.age_to ? { suggestedMaxAge: course.age_to } : {}),
        }
      : undefined

  return {
    '@type': 'Course',
    '@id': `${url}#course`,
    name: course.title,
    description: course.subtitle || course.description || '',
    url,
    inLanguage: schemaLocale,
    provider: { '@id': ORG_ID() },
    ...(course.card_image || course.hero_image
      ? { image: course.hero_image || course.card_image }
      : {}),
    ...(audience ? { audience } : {}),
    ...(course.price
      ? {
          offers: {
            '@type': 'Offer',
            price: String(course.price).replace(/[^\d.]/g, ''),
            priceCurrency: 'UZS',
            category: 'Paid',
            availability: 'https://schema.org/InStock',
            url,
          },
        }
      : { isAccessibleForFree: false }),
    hasCourseInstance: {
      '@type': 'CourseInstance',
      courseMode: 'Onsite',
      courseWorkload: course.lessons_per_week ? `PT${course.lessons_per_week * 90}M` : undefined,
      location: {
        '@type': 'Place',
        name: `${SITE.name}, ${loc(SITE.geo.city)}`,
        address: {
          '@type': 'PostalAddress',
          addressLocality: loc(SITE.geo.city),
          addressCountry: SITE.geo.country,
        },
      },
      ...(course.duration_months ? { duration: `P${course.duration_months}M` } : {}),
    },
  }
}

/** Yangilik / maqola. */
export function articleSchema(news, url) {
  if (!news) return null
  return {
    '@type': 'NewsArticle',
    '@id': `${url}#article`,
    headline: news.title,
    description: news.excerpt || '',
    url,
    ...(news.cover ? { image: [news.cover] } : {}),
    datePublished: news.published_at,
    dateModified: news.updated_at || news.published_at,
    inLanguage: schemaLocale,
    author: { '@id': ORG_ID() },
    publisher: { '@id': ORG_ID() },
    mainEntityOfPage: { '@type': 'WebPage', '@id': `${url}#webpage` },
    ...(news.reading_minutes ? { timeRequired: `PT${news.reading_minutes}M` } : {}),
  }
}

/** Filial — lokal qidiruv (GEO) uchun asosiy tugun. */
export function branchSchema(branch, url) {
  if (!branch) return null
  return {
    '@type': 'EducationalOrganization',
    '@id': `${url}#branch`,
    name: `${SITE.name} — ${branch.name}`,
    parentOrganization: { '@id': ORG_ID() },
    url,
    ...(branch.phone ? { telephone: branch.phone } : {}),
    ...(branch.image || branch.cover ? { image: branch.cover || branch.image } : {}),
    address: {
      '@type': 'PostalAddress',
      streetAddress: branch.address || '',
      addressLocality: loc(SITE.geo.city),
      addressRegion: loc(SITE.geo.city),
      addressCountry: SITE.geo.country,
    },
    ...(branch.latitude && branch.longitude
      ? {
          geo: {
            '@type': 'GeoCoordinates',
            latitude: branch.latitude,
            longitude: branch.longitude,
          },
        }
      : {}),
  }
}

/** Vakansiya. */
export function jobPostingSchema(vacancy, url) {
  if (!vacancy) return null
  return {
    '@type': 'JobPosting',
    title: vacancy.title,
    description: vacancy.description || vacancy.excerpt || vacancy.title,
    url,
    datePosted: vacancy.created_at || vacancy.published_at,
    ...(vacancy.employment_type ? { employmentType: vacancy.employment_type } : {}),
    hiringOrganization: { '@id': ORG_ID() },
    jobLocation: {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: loc(SITE.geo.city),
        addressCountry: SITE.geo.country,
      },
    },
  }
}

/** Ro'yxat sahifalari (kurslar, yangiliklar) — ItemList. */
export function itemListSchema(items, { url, name }) {
  const list = (items || []).filter((item) => item && item.url)
  if (!list.length) return null
  return {
    '@type': 'ItemList',
    '@id': `${url}#list`,
    name,
    numberOfItems: list.length,
    itemListElement: list.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      url: item.url,
      name: item.name,
    })),
  }
}

/**
 * Bir nechta tugunni bitta `@graph`ga yig'adi — sahifada bitta JSON-LD blok
 * bo'lgani qidiruv tizimlari uchun ham, hajm uchun ham afzal.
 */
export function buildGraph(nodes) {
  const graph = nodes.filter(Boolean)
  if (!graph.length) return null
  return { '@context': 'https://schema.org', '@graph': graph }
}
