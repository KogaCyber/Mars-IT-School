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
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { withBase } from '../src/data/basePath.js'
import { COURSE_ALIASES } from '../src/data/courseAliases.js'
import {
  SITE,
  STATIC_PAGES,
  localeAlternates,
  localePath,
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
  offerCatalogSchema,
  organizationSchema,
  setSchemaLocale,
  setSchemaOrigin,
  webPageSchema,
  websiteSchema,
} from '../src/utils/schema.js'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
// Production deploy'da (Vercel) `SEO_STRICT=1` qo'yiladi: backend javob
// bermasa build to'xtaydi va eski, to'liq sitemap saytda qolib turadi.
// Lokalda va CI'da backend umuman bo'lmaydi — u yerda build to'xtamaydi,
// faqat ko'zga tashlanadigan ogohlantirish chiqadi.
const SEO_STRICT = process.env.SEO_STRICT === '1'
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

/**
 * Prerender qilinadigan tillar.
 *
 * Ilgari faqat asosiy til (uz) yasalardi va `hreflang` ruscha hamda inglizcha
 * manzillarni e'lon qilsa-da, o'sha manzillar AYNAN O'SHA o'zbekcha HTML'ni
 * qaytarardi. Javob beruvchi tizimlarning aksariyati (GPTBot, ClaudeBot,
 * PerplexityBot, CCBot) JavaScript ishlatmaydi — ular uchun saytning ruscha
 * versiyasi umuman mavjud emas edi. Toshkent uchun bu eng katta yo'qotish:
 * qidiruvlarning katta qismi ruscha.
 */
const LOCALES = SITE.locales

/** Statik HTML ichidagi matnlar — har bir til uchun alohida. */
const TEXTS = {
  uz: {
    intro:
      'MARS IT School — Toshkentdagi (O‘zbekiston) 7–17 yoshli bolalar va o‘smirlar uchun IT o‘quv markazi va dasturlash maktabi. Yo‘nalishlar: IT Kids (9–11 yosh) va IT-dasturlash (12–17 yosh). Darslar oflayn, 12 tagacha o‘quvchili guruhlarda, birinchi sinov darsi bepul.',
    short: 'Qisqacha',
    name: 'Nomi',
    alsoKnownAs: 'Yana shunday nomlanadi',
    site: 'Sayt',
    city: 'Shahar',
    districts: 'Tumanlar',
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
    branchTitle: '{name} — Toshkentdagi IT o‘quv markazi filiali',
    branchDescription:
      '{name}: {address}. MARS IT School — bolalar uchun IT o‘quv markazi va dasturlash maktabi.',
    branchSummary: 'MARS IT School maktabining {name} filiali. Manzil: {address}.',
    branchKeywords: [
      'Toshkent IT maktabi',
      'yaqin atrofdagi IT o‘quv markazi',
      'yaqin atrofdagi dasturlash kurslari',
    ],
    courseDescription: '{title} — MARS IT School kursi.',
    courseSummary: '{title} — Toshkentdagi MARS IT School kursi.',
    courseKeywords: ['bolalar uchun dasturlash kurslari', 'IT kurslar Toshkent', 'MARS IT School'],
    newsKeywords: ['MARS IT School', 'IT maktab yangiliklari'],
    navCourses: 'Kurslar',
    navContacts: 'Kontaktlar',
    navApply: 'Sinov darsiga yozilish',
  },
  ru: {
    intro:
      'MARS IT School — IT учебный центр и школа программирования для детей и подростков 7–17 лет в Ташкенте (Узбекистан). Направления: IT Kids (9–11 лет) и IT-разработка (12–17 лет). Занятия офлайн, в группах до 12 учеников, первое пробное занятие бесплатное.',
    short: 'Кратко',
    name: 'Название',
    alsoKnownAs: 'Также известен как',
    site: 'Сайт',
    city: 'Город',
    districts: 'Районы',
    founded: 'Год основания',
    phone: 'Телефон',
    email: 'Email',
    languages: 'Языки сайта',
    languagesValue: 'узбекский, русский, английский',
    age: 'Возраст учеников',
    ageValue: '7–17 лет',
    format: 'Формат',
    formatValue: 'Офлайн-занятия в филиалах Ташкента, группы до 12 учеников',
    trial: 'Пробное занятие',
    trialValue: 'бесплатно, запись',
    pages: 'Страницы',
    courses: 'Курсы',
    branches: 'Филиалы',
    news: 'Новости',
    faq: 'Частые вопросы',
    vacancies: 'Вакансии',
    terms: 'Условия использования',
    termsText:
      'Содержимое сайта можно цитировать в ответах при указании ссылки на источник.',
    ageOf: 'лет',
    monthsShort: 'мес.',
    perWeek: 'занятия в неделю',
    ageLabel: 'Возраст',
    durationLabel: 'Длительность',
    perWeekLabel: 'Занятий в неделю',
    addressLabel: 'Адрес',
    tel: 'тел.',
    branchTitle: '{name} — филиал IT учебного центра в Ташкенте',
    branchDescription:
      '{name}: {address}. MARS IT School — IT учебный центр и школа программирования для детей.',
    branchSummary: 'Филиал {name} школы MARS IT School. Адрес: {address}.',
    branchKeywords: [
      'IT школа Ташкент',
      'IT учебный центр рядом со мной',
      'курсы программирования рядом',
    ],
    courseDescription: '{title} — курс MARS IT School.',
    courseSummary: '{title} — курс MARS IT School в Ташкенте.',
    courseKeywords: ['курсы программирования для детей', 'IT курсы Ташкент', 'MARS IT School'],
    newsKeywords: ['MARS IT School', 'новости IT школы'],
    navCourses: 'Курсы',
    navContacts: 'Контакты',
    navApply: 'Записаться на пробное занятие',
  },
  en: {
    intro:
      'MARS IT School is an IT training center and programming school for children and teenagers aged 7–17 in Tashkent, Uzbekistan. Tracks: IT Kids (ages 9–11) and IT Development (ages 12–17). Classes are offline, in groups of up to 12 students, and the first trial lesson is free.',
    short: 'At a glance',
    name: 'Name',
    alsoKnownAs: 'Also known as',
    site: 'Website',
    city: 'City',
    districts: 'Districts',
    founded: 'Founded',
    phone: 'Phone',
    email: 'Email',
    languages: 'Site languages',
    languagesValue: 'Uzbek, Russian, English',
    age: 'Student age',
    ageValue: '7–17 years',
    format: 'Format',
    formatValue: 'On-site classes in Tashkent branches, groups of up to 12 students',
    trial: 'Trial lesson',
    trialValue: 'free, book at',
    pages: 'Pages',
    courses: 'Courses',
    branches: 'Branches',
    news: 'News',
    faq: 'Frequently asked questions',
    vacancies: 'Careers',
    terms: 'Usage terms',
    termsText: 'Site content may be quoted in answers with a link to the source.',
    ageOf: 'years',
    monthsShort: 'months',
    perWeek: 'lessons per week',
    ageLabel: 'Age',
    durationLabel: 'Duration',
    perWeekLabel: 'Lessons per week',
    addressLabel: 'Address',
    tel: 'tel.',
    branchTitle: '{name} — an IT training center branch in Tashkent',
    branchDescription:
      '{name}: {address}. MARS IT School is an IT training center and programming school for children.',
    branchSummary: 'The {name} branch of MARS IT School. Address: {address}.',
    branchKeywords: ['IT school Tashkent', 'IT training center near me', 'coding courses near me'],
    courseDescription: '{title} — a MARS IT School course.',
    courseSummary: '{title} — a MARS IT School course in Tashkent.',
    courseKeywords: ['coding courses for kids', 'IT courses Tashkent', 'MARS IT School'],
    newsKeywords: ['MARS IT School', 'IT school news'],
    navCourses: 'Courses',
    navContacts: 'Contacts',
    navApply: 'Book a trial lesson',
  },
}

/**
 * Vercel topa olmagan manzil uchun sahifa (`dist/404.html`).
 *
 * `vercel.json` dagi rewrite'lar faqat MA'LUM bo'limlarga (`/kursy/...`,
 * `/novosti/...`, `/kontakty/...`, `/test/...`) taalluqli. Qolgan har qanday
 * manzil shu faylga tushadi va Vercel uni HTTP 404 bilan beradi.
 *
 * Nega muhim: ilgari rewrite HAMMA narsani `index.html` ga yuborardi, ya'ni
 * mavjud bo'lmagan istalgan manzil 200 bilan bosh sahifaning HTML'ini
 * qaytarardi («soft 404»). Qidiruv tizimi uchun bu — cheksiz sondagi
 * dublikat sahifa, ular indeksga tushib, byudjetni yeb qo'yardi.
 */
const NOT_FOUND_TEXT = {
  uz: {
    title: 'Sahifa topilmadi',
    description: 'Bunday sahifa yo‘q. Bosh sahifaga qayting yoki kurslar katalogini ko‘ring.',
  },
  ru: {
    title: 'Страница не найдена',
    description: 'Такой страницы нет. Вернитесь на главную или посмотрите каталог курсов.',
  },
  en: {
    title: 'Page not found',
    description: 'This page does not exist. Return to the home page or browse the course catalogue.',
  },
}

/** Kurs slug'lari: alohida sahifasi bor variantga yo'naltiriladiganlari. */
const ALIAS_SLUGS = new Set(Object.keys(COURSE_ALIASES))

const log = (message) => console.log(`[seo] ${message}`)


// --- Backend'dan ma'lumot -------------------------------------------------

/** Backend yo'q yoki sekin bo'lsa `null` qaytaradi — build davom etadi. */
async function fetchList(path, locale) {
  if (!API) return null
  const url = `${API}/api/v1/${path}`
  try {
    const response = await fetch(url, {
      headers: { 'Accept-Language': locale },
      signal: AbortSignal.timeout(15000),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return Array.isArray(data) ? data : data.results || []
  } catch (error) {
    log(`⚠ ${path} [${locale}] olinmadi (${error.message}) — bu bo'lim sitemap'ga qo'shilmaydi`)
    return null
  }
}

/**
 * Bitta til uchun backend kontenti.
 *
 * Har bir til alohida so'raladi: kurs nomlari, yangilik sarlavhalari va FAQ
 * javoblari tarjima qilingan. Ilgari faqat asosiy til olinardi va ruscha
 * sahifalar ham o'zbekcha matn bilan yasalardi.
 */
async function collectDynamic(locale) {
  const [courses, news, branches, vacancies, faqs] = await Promise.all([
    fetchList('courses/?page_size=200', locale),
    fetchList('news/?page_size=500', locale),
    fetchList('branches/?page_size=100', locale),
    fetchList('vacancies/?page_size=100', locale),
    fetchList('faqs/?page_size=100', locale),
  ])

  // Backend javob bermagan bo'limlar alohida sanaladi: ular sitemap'ga
  // tushmaydi, ya'ni kurs va yangilik sahifalari Google uchun ko'rinmay
  // qoladi. Ilgari bu faqat ogohlantirish edi va build muvaffaqiyatli
  // tugagani uchun hech kim sezmasdi (`SEO_STRICT` pastda).
  const failed = [
    ['courses', courses],
    ['news', news],
    ['branches', branches],
    ['vacancies', vacancies],
    ['faqs', faqs],
  ]
    .filter(([, value]) => value === null)
    .map(([name]) => name)

  return {
    // Alohida sahifasi bor kursning admin paneldagi dublikat slug'i
    // (`programmirovanie` → `it-razrabotka`) hamma joydan chiqarib
    // tashlanadi: sitemap'dan ham, prerender'dan ham, llms.txt'dan ham.
    // Aks holda bitta kurs ikkita manzilda, ikkita canonical bilan
    // indekslanardi — qidiruv tizimi uchun bu dublikat kontent va
    // reyting ikkiga bo'linardi.
    courses: (courses || []).filter((course) => !ALIAS_SLUGS.has(course.slug)),
    news: news || [],
    branches: branches || [],
    vacancies: vacancies || [],
    faqs: faqs || [],
    failed,
  }
}

// --- sitemap.xml ----------------------------------------------------------

const escapeXml = (value) =>
  String(value).replace(
    /[<>&'"]/g,
    (char) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[char],
  )

/**
 * Bitta yo'l — uchta yozuv (har bir til uchun). Har bir yozuv ichida barcha
 * tillarning `hreflang` havolalari takrorlanadi: qoida bo'yicha til
 * variantlari bir-biriga O'ZARO ishora qilishi shart, aks holda Google
 * belgilarni butunlay e'tiborsiz qoldiradi.
 */
function sitemapEntries({ path, lastmod, changefreq, priority, image }) {
  const alternates = localeAlternates(ORIGIN, path)
  return LOCALES.map((locale) =>
    [
      '  <url>',
      `    <loc>${escapeXml(localeUrl(ORIGIN, path, locale))}</loc>`,
      `    <lastmod>${lastmod || TODAY}</lastmod>`,
      `    <changefreq>${changefreq || 'monthly'}</changefreq>`,
      `    <priority>${(priority ?? 0.5).toFixed(1)}</priority>`,
      ...alternates.map(
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
    ].join('\n'),
  ).join('\n')
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
      priority: 0.7,
    })),
  ]

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ...entries.map(sitemapEntries),
    '</urlset>',
    '',
  ].join('\n')
}

// --- llms.txt -------------------------------------------------------------

/**
 * llms.txt — LLM'lar uchun saytning qisqa xaritasi: kim, nima taklif qiladi,
 * qaysi sahifada nima bor. Faktlar qisqa gaplarda beriladi, chunki javob
 * beruvchi tizimlar aynan shunday bo'laklarni iqtibos qiladi.
 *
 * Har bir til uchun alohida yasaladi: `/llms.txt` (uz), `/ru/llms.txt`,
 * `/en/llms.txt`.
 */
function buildLlmsTxt(dynamic, locale) {
  const TEXT = TEXTS[locale]
  const url = (path) => localeUrl(ORIGIN, path, locale)

  const lines = [
    `# ${SITE.name}`,
    '',
    `> ${TEXT.intro}`,
    '',
    `## ${TEXT.short}`,
    '',
    `- ${TEXT.name}: ${SITE.name}`,
    `- ${TEXT.alsoKnownAs}: ${SITE.alternateNames.join(', ')}`,
    `- ${TEXT.site}: ${url('/')}`,
    `- ${TEXT.city}: ${pick(SITE.geo.city, locale)}, ${pick(SITE.geo.countryName, locale)}`,
    `- ${TEXT.districts}: ${pick(SITE.districts, locale).join(', ')}`,
    `- ${TEXT.founded}: ${SITE.founded}`,
    `- ${TEXT.phone}: ${SITE.contacts.phone}`,
    `- ${TEXT.email}: ${SITE.contacts.email}`,
    `- ${TEXT.languages}: ${TEXT.languagesValue}`,
    `- ${TEXT.age}: ${TEXT.ageValue}`,
    `- ${TEXT.format}: ${TEXT.formatValue}`,
    `- ${TEXT.trial}: ${TEXT.trialValue} ${url('/zayavka')}`,
    '',
    `## ${TEXT.pages}`,
    '',
    ...STATIC_PAGES.map((page) => {
      const localized = resolvePage(page, locale)
      return `- [${localized.heading}](${url(page.path)}): ${localized.summary}`
    }),
    '',
  ]

  if (dynamic.courses.length) {
    lines.push(`## ${TEXT.courses}`, '')
    dynamic.courses.forEach((course) => {
      const facts = [
        course.age_range ? `${TEXT.ageLabel.toLowerCase()} ${course.age_range}` : null,
        course.duration_months ? `${course.duration_months} ${TEXT.monthsShort}` : null,
        course.lessons_per_week ? `${course.lessons_per_week} ${TEXT.perWeek}` : null,
      ]
        .filter(Boolean)
        .join(', ')
      lines.push(
        `- [${course.title}](${url(`/kursy/${course.slug}`)}): ${course.subtitle || ''}${facts ? ` (${facts})` : ''}`,
      )
    })
    lines.push('')
  }

  if (dynamic.branches.length) {
    lines.push(`## ${TEXT.branches}`, '')
    dynamic.branches.forEach((branch) => {
      lines.push(
        `- [${branch.name}](${url(`/kontakty/${branch.slug}`)}): ${branch.address || ''}${branch.phone ? `, ${TEXT.tel} ${branch.phone}` : ''}`,
      )
    })
    lines.push('')
  }

  if (dynamic.vacancies.length) {
    lines.push(`## ${TEXT.vacancies}`, '')
    dynamic.vacancies.forEach((vacancy) => {
      lines.push(`- ${vacancy.title}: ${url('/vakansii')}`)
    })
    lines.push('')
  }

  if (dynamic.news.length) {
    lines.push(`## ${TEXT.news}`, '')
    dynamic.news.slice(0, 30).forEach((item) => {
      lines.push(`- [${item.title}](${url(`/novosti/${item.slug}`)}): ${item.excerpt || ''}`)
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
 * Meta-tavsifni 160 belgigacha qisqartiradi.
 *
 * `useSeo.js` da AYNAN shu qoida bor, lekin prerender uni qo'llamasdi:
 * natijada bitta sahifaning statik HTML'idagi tavsif (165 belgi) ilova
 * yuklangach almashadigan tavsifdan farq qilardi. Qidiruv roboti birinchisini,
 * brauzer ikkinchisini ko'rardi.
 */
function trimDescription(text, limit = 160) {
  const value = String(text || '')
    .replace(/\s+/g, ' ')
    .trim()
  if (value.length <= limit) return value
  return `${value.slice(0, limit - 1).replace(/[\s,.;:\u2014-]+$/, '')}\u2026`
}

/**
 * Yasalgan `index.html` shablonidagi meta-teglarni sahifaga mos qiymatlarga
 * almashtiradi. Faqat `<head>` va `<noscript>` o'zgaradi — ilova o'zi
 * o'zgarishsiz qoladi, shuning uchun brauzerdagi xatti-harakat bir xil.
 */
function renderPage(template, page, locale) {
  const TEXT = TEXTS[locale]
  const url = localeUrl(ORIGIN, page.path, locale)
  const image = absoluteUrl(page.image || SITE.ogImage, ORIGIN)
  const title = `${page.title} — ${SITE.name}`
  const description = trimDescription(page.description)

  // Sxemalar ham shu tilda quriladi (shahar nomi, tavsiflar, `inLanguage`).
  setSchemaLocale(locale)

  const graph = buildGraph([
    organizationSchema(),
    websiteSchema(),
    webPageSchema({ url, title, description, image, locale }),
    page.breadcrumbs ? breadcrumbSchema(page.breadcrumbs, ORIGIN) : null,
    ...(page.schema || []),
  ])

  // Bu havolalar HTML ichida qoladi va JS ishlatmaydigan robotlar aynan
  // ulardan yuradi — ya'ni ular brauzer manzili, sayt ichidagi yo'l emas.
  // Sayt yo'l prefiksida tursa (`/maktab/`) prefiks shu yerda qo'shiladi.
  const nav = (path, label) =>
    `<a href="${escapeHtml(withBase(localePath(path, locale)))}">${escapeHtml(label)}</a>`

  const replacements = [
    // `<html lang>` — ilova yuklanmasdan turib ham to'g'ri til ko'rsatilsin.
    [/<html lang="[a-z-]+"/, `<html lang="${locale}"`],
    [/<title>[\s\S]*?<\/title>/, `<title>${escapeHtml(title)}</title>`],
    [
      /<meta\s+name="description"[\s\S]*?\/>/,
      `<meta name="description" content="${escapeHtml(description)}" />`,
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
      `<meta property="og:description" content="${escapeHtml(description)}" />`,
    ],
    [/<meta property="og:url"[^>]*>/, `<meta property="og:url" content="${escapeHtml(url)}" />`],
    [
      /<meta property="og:image" content="[^"]*" \/>/,
      `<meta property="og:image" content="${escapeHtml(image)}" />`,
    ],
    // O'lchamlar shablonda 1200×630 deb qotirilgan — bu FAQAT standart
    // `og-image.png` uchun to'g'ri. Kurs yoki yangilik sahifasida rasm admin
    // paneldan keladi va o'lchami boshqacha bo'ladi; yolg'on o'lcham bilan
    // Telegram va Facebook oldindan ko'rishni noto'g'ri kesardi. Rasm
    // standartdan farq qilsa — o'lchamlarni umuman e'lon qilmaymiz.
    [
      /\s*<meta property="og:image:width"[^>]*>\s*<meta property="og:image:height"[^>]*>/,
      image === absoluteUrl(SITE.ogImage, ORIGIN)
        ? '\n    <meta property="og:image:width" content="1200" />\n    <meta property="og:image:height" content="630" />'
        : '',
    ],
    [
      /<meta property="og:image:alt"[^>]*>/,
      `<meta property="og:image:alt" content="${escapeHtml(page.title)}" />`,
    ],
    [
      /<meta property="og:locale" content="[^"]*" \/>/,
      `<meta property="og:locale" content="${SITE.ogLocales[locale]}" />`,
    ],
    // `og:locale:alternate` shablonda QATTIQ yozilgan (ru_RU, en_US) va ilgari
    // almashtirilmasdan qolardi: ruscha sahifada asosiy til ham, muqobil til
    // ham `ru_RU` bo'lib, o'zbekcha versiya umuman e'lon qilinmasdi. Endi
    // ro'yxat joriy tilni CHIQARIB TASHLAB qayta quriladi.
    [
      /<meta property="og:locale:alternate" content="[^"]*" \/>\s*<meta property="og:locale:alternate" content="[^"]*" \/>/,
      LOCALES.filter((code) => code !== locale)
        .map((code) => `<meta property="og:locale:alternate" content="${SITE.ogLocales[code]}" />`)
        .join('\n    '),
    ],
    [
      /<meta name="twitter:title"[\s\S]*?\/>/,
      `<meta name="twitter:title" content="${escapeHtml(page.title)}" />`,
    ],
    [
      /<meta\s+name="twitter:description"[\s\S]*?\/>/,
      `<meta name="twitter:description" content="${escapeHtml(description)}" />`,
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
        `      <p>${escapeHtml(page.summary || description)}</p>`,
        ...(page.facts?.length
          ? [
              '      <ul>',
              ...page.facts.map((fact) => `        <li>${escapeHtml(fact)}</li>`),
              '      </ul>',
            ]
          : []),
        `      <p>${nav('/kursy', TEXT.navCourses)} · ${nav('/kontakty', TEXT.navContacts)} · ${nav('/zayavka', TEXT.navApply)}</p>`,
        `      <p>${escapeHtml(TEXT.phone)}: <a href="tel:${escapeHtml(SITE.contacts.phone.replace(/[^+\d]/g, ''))}">${escapeHtml(SITE.contacts.phone)}</a></p>`,
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
function collectPages(dynamic, locale) {
  // Sxemalar shu yerda quriladi, ya'ni til `renderPage` dan OLDIN
  // o'rnatilishi shart — aks holda ruscha sahifadagi `Course` va `Branch`
  // tugunlarida shahar nomi va tavsiflar o'zbekcha qolib ketardi.
  setSchemaLocale(locale)
  const TEXT = TEXTS[locale]
  const crumbHome = { name: resolvePage(STATIC_PAGES[0], locale).heading, path: '/' }

  /** `/kursy/it-kids` uchun zanjir: Bosh sahifa → Kurslar → IT Kids. */
  const staticCrumbs = (page) => {
    if (page.path === '/') return null
    const parentPath = page.path.split('/').slice(0, -1).join('/')
    const parent = parentPath
      ? resolvePage(
          STATIC_PAGES.find((item) => item.path === parentPath),
          locale,
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
    '/': [faqSchema(dynamic.faqs), offerCatalogSchema(dynamic.courses, ORIGIN, locale)],
    '/kursy': [offerCatalogSchema(dynamic.courses, ORIGIN, locale)],
    '/kontakty': dynamic.branches.map((branch) =>
      branchSchema(branch, localeUrl(ORIGIN, `/kontakty/${branch.slug}`, locale)),
    ),
    '/vakansii': dynamic.vacancies.map((vacancy) =>
      jobPostingSchema(vacancy, localeUrl(ORIGIN, '/vakansii', locale)),
    ),
  }

  const pages = STATIC_PAGES.map((page) => {
    const localized = resolvePage(page, locale)
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
        course.age_range ? `${TEXT.ageLabel}: ${course.age_range}` : null,
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
      schema: [courseSchema(course, localeUrl(ORIGIN, path, locale))],
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
      schema: [articleSchema(item, localeUrl(ORIGIN, path, locale))],
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
        .replace('{address}', branch.address || pick(SITE.geo.city, locale)),
      summary: TEXT.branchSummary
        .replace('{name}', branch.name)
        .replace('{address}', branch.address || pick(SITE.geo.city, locale)),
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
      schema: [branchSchema(branch, localeUrl(ORIGIN, path, locale))],
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

/** Faylni yo'l bo'yicha yozadi (kerakli papkalarni yaratib). */
async function writePage(pathname, html) {
  const target = pathname === '/' ? DIST : join(DIST, pathname)
  await mkdir(target, { recursive: true })
  await writeFile(join(target, 'index.html'), html, 'utf8')
}

/**
 * `public/` dagi fayllarga ABSOLYUT havolalarga sayt prefiksini qo'shadi.
 *
 * Vite `base` ni HTML va o'zi qayta ishlagan aktivlarga qo'llaydi, lekin
 * ikki joyga TEGMAYDI:
 *
 *   1. CSS ichidagi `url(/fonts/...)` — `public/` dagi faylga absolyut
 *      havola. Yig'ilgan CSS'da u o'zgarishsiz qoladi.
 *   2. `site.webmanifest` — u shunchaki nusxalanadi, ichidagi `start_url`,
 *      `scope`, `id` va ikonka manzillari o'qilmaydi.
 *
 * Natijada sayt ildizda emas, `/school/` da turganda brauzer `/fonts/...`
 * va `/favicon.svg` ni SO'RAYDI, u yerda esa boshqa saytning HTML'i yotadi.
 * Shrift buzilgan deb hisoblanadi ("invalid sfntVersion" — aslida `<!DO`),
 * manifest ikonkasi esa umuman yuklanmaydi.
 *
 * Prefiks bo'lmasa hech narsa o'zgarmaydi.
 */
async function applyBasePrefix() {
  const prefix = withBase('/').replace(/\/$/, '')
  if (!prefix) return 0

  let patched = 0

  // Prefiks allaqachon qo'yilgan manzilga ikkinchi marta qo'shilmasin.
  const rewrite = (text, pattern) =>
    text.replace(pattern, (match, path) =>
      path.startsWith(`${prefix}/`) ? match : match.replace(path, `${prefix}${path}`),
    )

  const cssDir = join(DIST, 'assets')
  let cssFiles
  try {
    cssFiles = (await readdir(cssDir)).filter((name) => name.endsWith('.css'))
  } catch {
    // `assets/` papkasi yo'q — yig'ilmagan dist, qo'shadigan narsa ham yo'q.
    cssFiles = []
  }

  for (const name of cssFiles) {
    const file = join(cssDir, name)
    const before = await readFile(file, 'utf8')
    const after = rewrite(before, /url\((\/[^)"']+)\)/g)
    if (after !== before) {
      await writeFile(file, after, 'utf8')
      patched += 1
    }
  }

  const manifest = join(DIST, 'site.webmanifest')
  try {
    const before = await readFile(manifest, 'utf8')
    const after = rewrite(before, /"(\/[^"]*)"/g)
    if (after !== before) {
      await writeFile(manifest, after, 'utf8')
      patched += 1
    }
  } catch {
    /* manifest yo'q — muammo emas */
  }

  return patched
}

async function main() {
  const template = await readFile(join(DIST, 'index.html'), 'utf8')

  // Har bir til uchun backend kontenti alohida olinadi.
  const byLocale = Object.fromEntries(
    await Promise.all(LOCALES.map(async (locale) => [locale, await collectDynamic(locale)])),
  )
  const base = byLocale[SITE.defaultLocale]

  // Sitemap bitta: slug'lar tillarda bir xil, manzillar esa har bir til uchun
  // alohida yozuv sifatida chiqadi.
  await writeFile(join(DIST, 'sitemap.xml'), buildSitemap(base), 'utf8')
  await buildRobots()

  let total = 0
  for (const locale of LOCALES) {
    const dynamic = byLocale[locale]
    const prefix = localePath('/', locale)
    const localeDir = prefix === '/' ? DIST : join(DIST, prefix.slice(1))
    await mkdir(localeDir, { recursive: true })

    await writeFile(join(localeDir, 'llms.txt'), buildLlmsTxt(dynamic, locale), 'utf8')

    for (const page of collectPages(dynamic, locale)) {
      await writePage(localePath(page.path, locale), renderPage(template, page, locale))
      total += 1
    }
  }

  // Topilmagan manzil uchun sahifa. Faqat asosiy tilda: Vercel `404.html` ni
  // butun sayt bo'ylab bitta fayldan beradi, til esa ilova yuklangach
  // manzildagi prefiksga qarab o'zi to'g'rilanadi (`i18n/language.js`).
  const notFound = NOT_FOUND_TEXT[SITE.defaultLocale]
  const notFoundHtml = renderPage(
    template,
    {
      path: '/404',
      noindex: true,
      title: notFound.title,
      heading: notFound.title,
      description: notFound.description,
      summary: notFound.description,
      keywords: [],
    },
    SITE.defaultLocale,
  )
    // `canonical` va `hreflang` olib tashlanadi: ular MAVJUD manzilni
    // ko'rsatishi shart, `/404` esa hech qachon mavjud emas. Sahifa
    // baribir `noindex`, lekin yolg'on belgilarni qoldirishning ma'nosi yo'q.
    .replace(/\s*<link rel="canonical"[^>]*>/, '')
    .replace(/\s*<link rel="alternate" hreflang="[a-z-]+"[^>]*>/g, '')
  await writeFile(join(DIST, '404.html'), notFoundHtml, 'utf8')

  const patched = await applyBasePrefix()
  if (patched) log(`yo'l prefiksi ${patched} ta faylga qo'shildi (CSS / manifest)`)

  log(`sitemap.xml, llms.txt (${LOCALES.length} til) va ${total} ta statik sahifa yaratildi (${ORIGIN})`)

  const failed = base.failed
  if (!failed.length) return

  // API manzili berilgan, lekin backend javob bermadi — bu deploy'dagi
  // haqiqiy nosozlik, "shunchaki lokal muhit" emas.
  const list = failed.join(', ')
  const message =
    `Backend javob bermadi (${list}) — sitemap.xml faqat statik sahifalardan iborat. ` +
    'Kurs, yangilik va filial sahifalari qidiruv tizimlariga ko‘rinmaydi.'

  if (SEO_STRICT) {
    console.error(`[seo] XATOLIK: ${message}`)
    process.exit(1)
  }

  console.warn(`\n[seo] ⚠️  DIQQAT: ${message}\n`)
}

main().catch((error) => {
  console.error('[seo] xatolik:', error)
  process.exit(1)
})
