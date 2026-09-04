/**
 * Build'dan keyin ishlaydigan SEO generatori.
 *
 * Nima yasaydi:
 *  1. `sitemap.xml` — statik sahifalar + backend'dagi kurslar, yangiliklar,
 *     filiallar va vakansiyalar;
 *  2. `llms.txt` — javob beruvchi tizimlar (ChatGPT, Claude, Perplexity) uchun
 *     saytning qisqa, faktik xaritasi va savol-javoblar;
 *  3. har bir sahifa uchun statik HTML — meta-teglar, canonical va JSON-LD
 *     allaqachon HTML ichida bo'ladi, shuning uchun JS ishlatmaydigan
 *     crawler'lar ham to'liq ma'lumot ko'radi.
 *
 * Backend javob bermasa build to'xtamaydi — faqat statik qism yaratiladi.
 */
import { readFileSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  SITE,
  STATIC_PAGES,
  localeAlternates,
  localeUrl,
  pick,
  resolvePage,
} from '../src/data/seoConfig.js'
import {
  absoluteUrl,
  articleSchema,
  branchSchema,
  breadcrumbSchema,
  buildGraph,
  courseSchema,
  faqSchema,
  jobPostingSchema,
  jsonLdScriptContent,
  organizationSchema,
  setSchemaOrigin,
  webPageSchema,
  websiteSchema,
} from '../src/utils/schema.js'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const DIST = join(ROOT, 'dist')

// Vite `.env.production` ni o'zi o'qiydi, bu skript esa alohida Node jarayoni —
// shuning uchun o'sha faylni qo'lda o'qiymiz. Aks holda Vercel'da sitemap va
// canonical manzillar seoConfig'dagi zaxira domenga tushib qolardi.
loadEnvFile(join(ROOT, '.env.production'))

function loadEnvFile(path) {
  let raw
  try {
    raw = readFileSync(path, 'utf8')
  } catch {
    return // fayl yo'q — muhit o'zgaruvchilariga tayanamiz
  }
  for (const line of raw.split('\n')) {
    const match = /^\s*([A-Z0-9_]+)\s*=\s*(.*)$/.exec(line)
    if (!match) continue
    const [, key, value] = match
    // Haqiqiy muhit o'zgaruvchisi (Vercel dashboard) fayldan ustun turadi.
    if (process.env[key] === undefined) process.env[key] = value.trim()
  }
}

const ORIGIN = (process.env.VITE_SITE_URL || process.env.SITE_URL || SITE.url).replace(/\/$/, '')
const API = (process.env.VITE_API_BASE_URL || process.env.API_BASE_URL || '').replace(/\/$/, '')
const TODAY = new Date().toISOString().slice(0, 10)

// Sxemalardagi absolyut manzillar ham shu domendan qurilsin (schema.js).
setSchemaOrigin(ORIGIN)

/** Prerender qilinadigan HTML sayt asosiy tilida (o'zbekcha) yoziladi. */
const LOCALE = SITE.defaultLocale

/** Statik HTML ichidagi matnlar — sayt asosiy tilida. */
const TEXT = {
  uz: {
    intro:
      'Toshkentdagi (O‘zbekiston) 7–17 yoshli bolalar va o‘smirlar uchun dasturlash maktabi. Yo‘nalishlar: IT Kids (9–11 yosh) va IT-dasturlash (12–17 yosh). Darslar oflayn, 12 tagacha o‘quvchili guruhlarda, birinchi sinov darsi bepul.',
    short: 'Qisqacha',
    name: 'Nomi',
    site: 'Sayt',
    city: 'Shahar',
    founded: 'Tashkil etilgan yil',
    phone: 'Telefon',
    email: 'Email',
    languages: 'Sayt tillari',
    languagesValue: 'o‘zbek, rus, ingliz',
    age: 'O‘quvchilar yoshi',
    ageValue: '7–17 yosh',
    format: 'Format',
    formatValue: 'Toshkent filiallarida oflayn darslar, 12 tagacha o‘quvchili guruhlar',
    trial: 'Sinov darsi',
    trialValue: 'bepul, yozilish',
    pages: 'Sahifalar',
    courses: 'Kurslar',
    branches: 'Filiallar',
    news: 'Yangiliklar',
    faq: 'Ko‘p beriladigan savollar',
    vacancies: 'Vakansiyalar',
    terms: 'Foydalanish shartlari',
    termsText: 'Sayt mazmunini manbaga havola ko‘rsatilgan holda javoblarda iqtibos qilish mumkin.',
    ageOf: 'yosh',
    monthsShort: 'oy',
    perWeek: 'ta dars haftasiga',
    ageLabel: 'Yosh',
    durationLabel: 'Davomiylik',
    perWeekLabel: 'Haftasiga darslar',
    addressLabel: 'Manzil',
    tel: 'tel.',
    branchTitle: '{name} — Toshkentdagi filial',
    branchDescription: '{name}: {address}. MARS IT School — bolalar uchun dasturlash maktabi.',
    branchSummary: 'MARS IT School maktabining {name} filiali. Manzil: {address}.',
    branchKeywords: ['Toshkent IT maktabi', 'yaqin atrofdagi dasturlash kurslari'],
    courseDescription: '{title} — MARS IT School kursi.',
    courseSummary: '{title} — Toshkentdagi MARS IT School kursi.',
    courseKeywords: ['bolalar uchun dasturlash kurslari', 'MARS IT School'],
    newsKeywords: ['MARS IT School', 'IT maktab yangiliklari'],
    navCourses: 'Kurslar',
    navContacts: 'Kontaktlar',
    navApply: 'Sinov darsiga yozilish',
  },
}[SITE.defaultLocale]

const log = (message) => console.log(`[seo] ${message}`)

// --- Backend'dan ma'lumot -------------------------------------------------

/** Backend yo'q yoki sekin bo'lsa `null` qaytaradi — build davom etadi. */
async function fetchList(path) {
  if (!API) return null
  const url = `${API}/api/v1/${path}`
  try {
    const response = await fetch(url, {
      headers: { 'Accept-Language': LOCALE },
      signal: AbortSignal.timeout(15000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return Array.isArray(data) ? data : data.results || []
  } catch (error) {
    log(`⚠ ${path} olinmadi (${error.message}) — bu bo'lim sitemap'ga qo'shilmaydi`)
    return null
  }
}

async function collectDynamic() {
  const [courses, news, branches, vacancies, faqs] = await Promise.all([
    fetchList('courses/?page_size=200'),
    fetchList('news/?page_size=500'),
    fetchList('branches/?page_size=100'),
    fetchList('vacancies/?page_size=100'),
    fetchList('faqs/?page_size=100'),
  ])
  return {
    courses: courses || [],
    news: news || [],
    branches: branches || [],
    vacancies: vacancies || [],
    faqs: faqs || [],
  }
}

// --- sitemap.xml ----------------------------------------------------------

const escapeXml = (value) =>
  String(value).replace(
    /[<>&'"]/g,
    (char) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[char],
  )

function sitemapEntry({ path, lastmod, changefreq, priority, image }) {
  const loc = `${ORIGIN}${path}`
  return [
    '  <url>',
    `    <loc>${escapeXml(loc)}</loc>`,
    `    <lastmod>${lastmod || TODAY}</lastmod>`,
    `    <changefreq>${changefreq || 'monthly'}</changefreq>`,
    `    <priority>${(priority ?? 0.5).toFixed(1)}</priority>`,
    // Har bir tilning O'Z manzili (`?lang=`). Uchalasi bir xil URL bo'lsa
    // hreflang qoidasi buziladi va Google belgini e'tiborsiz qoldiradi.
    ...localeAlternates(ORIGIN, path).map(
      ({ hreflang, href }) =>
        `    <xhtml:link rel="alternate" hreflang="${hreflang}" href="${escapeXml(href)}"/>`,
    ),
    ...(image
      ? [
          '    <image:image>',
          `      <image:loc>${escapeXml(image)}</image:loc>`,
          '    </image:image>',
        ]
      : []),
    '  </url>',
  ].join('\n')
}

function buildSitemap(dynamic) {
  const entries = [
    ...STATIC_PAGES.map((page) => ({
      path: page.path,
      changefreq: page.changefreq,
      priority: page.priority,
    })),
    ...dynamic.courses
      // IT Kids / IT-разработка allaqachon alohida statik sahifa sifatida bor.
      .filter((course) => !STATIC_PAGES.some((page) => page.path === `/kursy/${course.slug}`))
      .map((course) => ({
        path: `/kursy/${course.slug}`,
        changefreq: 'monthly',
        priority: 0.8,
        lastmod: (course.updated_at || '').slice(0, 10) || undefined,
        image: course.card_image ? absoluteUrl(course.card_image, ORIGIN) : undefined,
      })),
    ...dynamic.news.map((item) => ({
      path: `/novosti/${item.slug}`,
      changefreq: 'yearly',
      priority: 0.6,
      lastmod: (item.updated_at || item.published_at || '').slice(0, 10) || undefined,
      image: item.cover ? absoluteUrl(item.cover, ORIGIN) : undefined,
    })),
    ...dynamic.branches.map((branch) => ({
      path: `/kontakty/${branch.slug}`,
      changefreq: 'monthly',
      priority: 0.6,
    })),
  ]

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ...entries.map(sitemapEntry),
    '</urlset>',
    '',
  ].join('\n')
}

// --- llms.txt -------------------------------------------------------------

/**
 * llms.txt — LLM'lar uchun saytning qisqa xaritasi: kim, nima taklif qiladi,
 * qaysi sahifada nima bor. Faktlar qisqa gaplarda beriladi, chunki javob
 * beruvchi tizimlar aynan shunday bo'laklarni iqtibos qiladi.
 */
function buildLlmsTxt(dynamic) {
  const lines = [
    `# ${SITE.name}`,
    '',
    `> ${TEXT.intro}`,
    '',
    `## ${TEXT.short}`,
    '',
    `- ${TEXT.name}: ${SITE.name}`,
    `- ${TEXT.site}: ${ORIGIN}`,
    `- ${TEXT.city}: ${pick(SITE.geo.city, LOCALE)}, ${pick(SITE.geo.countryName, LOCALE)}`,
    `- ${TEXT.founded}: ${SITE.founded}`,
    `- ${TEXT.phone}: ${SITE.contacts.phone}`,
    `- ${TEXT.email}: ${SITE.contacts.email}`,
    `- ${TEXT.languages}: ${TEXT.languagesValue}`,
    `- ${TEXT.age}: ${TEXT.ageValue}`,
    `- ${TEXT.format}: ${TEXT.formatValue}`,
    `- ${TEXT.trial}: ${TEXT.trialValue} ${ORIGIN}/zayavka`,
    '',
    `## ${TEXT.pages}`,
    '',
    ...STATIC_PAGES.map((page) => {
      const localized = resolvePage(page, LOCALE)
      return `- [${localized.heading}](${ORIGIN}${page.path}): ${localized.summary}`
    }),
    '',
  ]

  if (dynamic.courses.length) {
    lines.push(`## ${TEXT.courses}`, '')
    dynamic.courses.forEach((course) => {
      const facts = [
        course.age_range
          ? `${TEXT.ageLabel.toLowerCase()} ${course.age_range} ${TEXT.ageOf}`
          : null,
        course.duration_months ? `${course.duration_months} ${TEXT.monthsShort}` : null,
        course.lessons_per_week ? `${course.lessons_per_week} ${TEXT.perWeek}` : null,
      ]
        .filter(Boolean)
        .join(', ')
      lines.push(
        `- [${course.title}](${ORIGIN}/kursy/${course.slug}): ${course.subtitle || ''}${facts ? ` (${facts})` : ''}`,
      )
    })
    lines.push('')
  }

  if (dynamic.branches.length) {
    lines.push(`## ${TEXT.branches}`, '')
    dynamic.branches.forEach((branch) => {
      lines.push(
        `- [${branch.name}](${ORIGIN}/kontakty/${branch.slug}): ${branch.address || ''}${branch.phone ? `, ${TEXT.tel} ${branch.phone}` : ''}`,
      )
    })
    lines.push('')
  }

  if (dynamic.news.length) {
    lines.push(`## ${TEXT.news}`, '')
    dynamic.news.slice(0, 30).forEach((item) => {
      lines.push(`- [${item.title}](${ORIGIN}/novosti/${item.slug}): ${item.excerpt || ''}`)
    })
    lines.push('')
  }

  if (dynamic.faqs.length) {
    lines.push(`## ${TEXT.faq}`, '')
    dynamic.faqs.forEach((item) => {
      if (!item.question || !item.answer) return
      lines.push(`### ${item.question}`, '', String(item.answer).replace(/\s+/g, ' ').trim(), '')
    })
  }

  lines.push(`## ${TEXT.terms}`, '', TEXT.termsText, '')

  return lines.join('\n')
}

// --- Statik HTML (prerender) ---------------------------------------------

const escapeHtml = (value) =>
  String(value ?? '').replace(
    /[<>&"]/g,
    (char) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[char],
  )

/**
 * Yasalgan `index.html` shablonidagi meta-teglarni sahifaga mos qiymatlarga
 * almashtiradi. Faqat `<head>` va `<noscript>` o'zgaradi — ilova o'zi
 * o'zgarishsiz qoladi, shuning uchun brauzerdagi xatti-harakat bir xil.
 */
function renderPage(template, page) {
  const url = localeUrl(ORIGIN, page.path, LOCALE)
  const image = absoluteUrl(page.image || SITE.ogImage, ORIGIN)
  const title = `${page.title} — ${SITE.name}`

  const graph = buildGraph([
    organizationSchema(),
    websiteSchema(),
    webPageSchema({ url, title, description: page.description, image, locale: LOCALE }),
    page.breadcrumbs ? breadcrumbSchema(page.breadcrumbs, ORIGIN) : null,
    ...(page.schema || []),
  ])

  const replacements = [
    [/<title>[\s\S]*?<\/title>/, `<title>${escapeHtml(title)}</title>`],
    [
      /<meta\s+name="description"[\s\S]*?\/>/,
      `<meta name="description" content="${escapeHtml(page.description)}" />`,
    ],
    [
      /<meta\s+name="keywords"[\s\S]*?\/>/,
      `<meta name="keywords" content="${escapeHtml((page.keywords || []).join(', '))}" />`,
    ],
    [/<link rel="canonical"[^>]*>/, `<link rel="canonical" href="${escapeHtml(url)}" />`],
    [
      /<meta\s+name="robots"[\s\S]*?\/>/,
      `<meta name="robots" content="${
        page.noindex
          ? 'noindex, follow'
          : 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'
      }" />`,
    ],
    [
      /<meta property="og:type"[^>]*>/,
      `<meta property="og:type" content="${page.ogType || 'website'}" />`,
    ],
    [
      /<meta property="og:title"[\s\S]*?\/>/,
      `<meta property="og:title" content="${escapeHtml(page.title)}" />`,
    ],
    [
      /<meta\s+property="og:description"[\s\S]*?\/>/,
      `<meta property="og:description" content="${escapeHtml(page.description)}" />`,
    ],
    [/<meta property="og:url"[^>]*>/, `<meta property="og:url" content="${escapeHtml(url)}" />`],
    [
      /<meta property="og:image" content="[^"]*" \/>/,
      `<meta property="og:image" content="${escapeHtml(image)}" />`,
    ],
    [
      /<meta property="og:image:alt"[^>]*>/,
      `<meta property="og:image:alt" content="${escapeHtml(page.title)}" />`,
    ],
    [
      /<meta name="twitter:title"[\s\S]*?\/>/,
      `<meta name="twitter:title" content="${escapeHtml(page.title)}" />`,
    ],
    [
      /<meta\s+name="twitter:description"[\s\S]*?\/>/,
      `<meta name="twitter:description" content="${escapeHtml(page.description)}" />`,
    ],
    [
      /<meta name="twitter:image"[^>]*>/,
      `<meta name="twitter:image" content="${escapeHtml(image)}" />`,
    ],
    [
      /<link rel="alternate" hreflang="[a-z-]+"[^>]*>[\s\S]*?<link rel="alternate" hreflang="x-default"[^>]*>/,
      localeAlternates(ORIGIN, page.path)
        .map(
          ({ hreflang, href }) =>
            `<link rel="alternate" hreflang="${hreflang}" href="${escapeHtml(href)}" />`,
        )
        .join('\n    '),
    ],
    [
      /<script type="application\/ld\+json">[\s\S]*?<\/script>/,
      `<script type="application/ld+json">${jsonLdScriptContent(graph)}</script>`,
    ],
    [
      /<noscript>[\s\S]*?<\/noscript>/,
      [
        '<noscript>',
        `      <h1>${escapeHtml(page.heading || page.title)}</h1>`,
        `      <p>${escapeHtml(page.summary || page.description)}</p>`,
        ...(page.facts?.length
          ? [
              '      <ul>',
              ...page.facts.map((fact) => `        <li>${escapeHtml(fact)}</li>`),
              '      </ul>',
            ]
          : []),
        `      <p><a href="/kursy">${escapeHtml(TEXT.navCourses)}</a> · ` +
          `<a href="/kontakty">${escapeHtml(TEXT.navContacts)}</a> · ` +
          `<a href="/zayavka">${escapeHtml(TEXT.navApply)}</a></p>`,
        `      <p>${escapeHtml(TEXT.phone)}: ${escapeHtml(SITE.contacts.phone)}</p>`,
        '    </noscript>',
      ].join('\n'),
    ],
  ]

  return replacements.reduce(
    (html, [pattern, value]) => html.replace(pattern, () => value),
    template,
  )
}

/** Prerender qilinadigan sahifalar ro'yxati (statik + backend'dan kelganlari). */
function collectPages(dynamic) {
  const crumbHome = { name: resolvePage(STATIC_PAGES[0], LOCALE).heading, path: '/' }

  /** `/kursy/it-kids` uchun zanjir: Bosh sahifa → Kurslar → IT Kids. */
  const staticCrumbs = (page) => {
    if (page.path === '/') return null
    const parentPath = page.path.split('/').slice(0, -1).join('/')
    const parent = parentPath
      ? resolvePage(
          STATIC_PAGES.find((item) => item.path === parentPath),
          LOCALE,
        )
      : null
    return [
      crumbHome,
      ...(parent ? [{ name: parent.heading, path: parent.path }] : []),
      { name: page.heading, path: page.path },
    ]
  }

  // Bu sxemalar ilovada `useSeo` orqali qo'shiladi, lekin JS ishlatmaydigan
  // crawler'lar (jumladan javob beruvchi tizimlarning bir qismi) uni ko'rmaydi.
  // Shuning uchun statik HTML'ga ham yoziladi.
  const extraSchema = {
    '/': [faqSchema(dynamic.faqs)],
    '/vakansii': dynamic.vacancies.map((vacancy) =>
      jobPostingSchema(vacancy, `${ORIGIN}/vakansii`),
    ),
  }

  const pages = STATIC_PAGES.map((page) => {
    const localized = resolvePage(page, LOCALE)
    return {
      ...localized,
      breadcrumbs: staticCrumbs(localized),
      schema: [...(localized.schema || []), ...(extraSchema[localized.path] || [])].filter(Boolean),
    }
  })

  dynamic.courses.forEach((course) => {
    const path = `/kursy/${course.slug}`
    if (pages.some((page) => page.path === path)) return
    pages.push({
      path,
      title: course.title,
      heading: course.title,
      description: course.subtitle || TEXT.courseDescription.replace('{title}', course.title),
      summary: course.subtitle || TEXT.courseSummary.replace('{title}', course.title),
      keywords: [course.title, ...TEXT.courseKeywords],
      image: course.card_image ? absoluteUrl(course.card_image, ORIGIN) : undefined,
      facts: [
        course.age_range ? `${TEXT.ageLabel}: ${course.age_range} ${TEXT.ageOf}` : null,
        course.duration_months
          ? `${TEXT.durationLabel}: ${course.duration_months} ${TEXT.monthsShort}`
          : null,
        course.lessons_per_week ? `${TEXT.perWeekLabel}: ${course.lessons_per_week}` : null,
      ].filter(Boolean),
      breadcrumbs: [
        crumbHome,
        { name: TEXT.courses, path: '/kursy' },
        { name: course.title, path },
      ],
      schema: [courseSchema(course, `${ORIGIN}${path}`)],
    })
  })

  dynamic.news.forEach((item) => {
    const path = `/novosti/${item.slug}`
    pages.push({
      path,
      ogType: 'article',
      title: item.title,
      heading: item.title,
      description: item.excerpt || item.title,
      summary: item.excerpt || item.title,
      keywords: TEXT.newsKeywords,
      image: item.cover ? absoluteUrl(item.cover, ORIGIN) : undefined,
      breadcrumbs: [crumbHome, { name: TEXT.news, path: '/novosti' }, { name: item.title, path }],
      schema: [articleSchema(item, `${ORIGIN}${path}`)],
    })
  })

  dynamic.branches.forEach((branch) => {
    const path = `/kontakty/${branch.slug}`
    pages.push({
      path,
      title: TEXT.branchTitle.replace('{name}', branch.name),
      heading: `${SITE.name} — ${branch.name}`,
      description: TEXT.branchDescription
        .replace('{name}', branch.name)
        .replace('{address}', branch.address || pick(SITE.geo.city, LOCALE)),
      summary: TEXT.branchSummary
        .replace('{name}', branch.name)
        .replace('{address}', branch.address || pick(SITE.geo.city, LOCALE)),
      keywords: [branch.name, ...TEXT.branchKeywords],
      facts: [
        branch.address ? `${TEXT.addressLabel}: ${branch.address}` : null,
        branch.phone ? `${TEXT.phone}: ${branch.phone}` : null,
      ].filter(Boolean),
      breadcrumbs: [
        crumbHome,
        { name: TEXT.navContacts, path: '/kontakty' },
        { name: branch.name, path },
      ],
      schema: [branchSchema(branch, `${ORIGIN}${path}`)],
    })
  })

  return pages
}

// --- robots.txt -----------------------------------------------------------

/**
 * `public/robots.txt` ichidagi domenni haqiqiy manzilga moslaydi.
 *
 * Fayl statik nusxalanadi va u yerda domen qo'lda yozilgan edi. Natijada
 * `Sitemap:` qatori BOSHQA domenni ko'rsatib turardi (`marsitschool.uz`),
 * sitemap'ning o'zi esa deploy domenida (`…vercel.app`) yotardi — Google
 * uchun bu ishonchsiz, boshqa saytga tegishli sitemap. Endi domen bitta
 * manbadan (`VITE_SITE_URL`) keladi va uchala fayl bir-biriga mos bo'ladi.
 */
async function buildRobots() {
  const path = join(DIST, 'robots.txt')
  let content
  try {
    content = await readFile(path, 'utf8')
  } catch {
    log('⚠ robots.txt topilmadi — o‘tkazib yuborildi')
    return null
  }

  // Fayldagi har qanday absolut manzil haqiqiy domenga almashtiriladi.
  const replaced = content.replace(/https?:\/\/[a-z0-9.-]+(?=\/|\s|$)/gi, ORIGIN)
  await writeFile(path, replaced, 'utf8')
  return replaced
}

// --- Ishga tushirish ------------------------------------------------------

async function main() {
  const template = await readFile(join(DIST, 'index.html'), 'utf8')
  const dynamic = await collectDynamic()

  await writeFile(join(DIST, 'sitemap.xml'), buildSitemap(dynamic), 'utf8')
  await writeFile(join(DIST, 'llms.txt'), buildLlmsTxt(dynamic), 'utf8')
  await buildRobots()

  const pages = collectPages(dynamic)
  for (const page of pages) {
    const html = renderPage(template, page)
    if (page.path === '/') {
      await writeFile(join(DIST, 'index.html'), html, 'utf8')
      continue
    }
    const dir = join(DIST, page.path)
    await mkdir(dir, { recursive: true })
    await writeFile(join(dir, 'index.html'), html, 'utf8')
  }

  log(`sitemap.xml, llms.txt va ${pages.length} ta statik sahifa yaratildi (${ORIGIN})`)
}

main().catch((error) => {
  console.error('[seo] xatolik:', error)
  process.exit(1)
})
