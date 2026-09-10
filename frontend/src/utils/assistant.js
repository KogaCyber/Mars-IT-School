/**
 * Yordamchining «miyasi»: savolga sayt ma'lumotlaridan javob topadi.
 *
 * Javob quyidagi tartibda qidiriladi — birinchi topilgani qaytadi:
 *
 *   1. Jonli ma'lumot bo'yicha savollar (`dynamicAnswer`): filiallar, kurslar,
 *      narx, dars jadvali, o'qituvchilar, vakansiyalar, yangiliklar. Bu yerda
 *      javob API'dan kelgan haqiqiy qiymatlardan yig'iladi — «nechta filial
 *      bor», «Yashnabod'da filial bormi», «narxi qancha» kabi savollar shu
 *      yo'ldan javob oladi.
 *   2. Tayyor mavzular (`assistantFaq.js`) — sinov darsi, noutbuk kerakmi va
 *      hokazo. Mavzuda `intent` bo'lsa, javob baribir jonli ma'lumotdan
 *      yig'iladi — statik matn faqat API yiqilganda ishlatiladi.
 *   3. Sayt matnlari bo'yicha qidiruv (`buildCorpus`): kurs tavsiflari,
 *      yangiliklar, vakansiyalar, sahifalardagi savol-javoblar.
 *   4. Hech nima topilmasa — menejerga yo'naltirish.
 *
 * Savol xato yozilgan yoki qo'shimchali bo'lsa ham topiladi: solishtirish
 * `assistantSearch.js` dagi o'zak + Levenshtein orqali ketadi.
 */
import { ASSISTANT_FALLBACK, ASSISTANT_TOPICS } from '@/data/assistantFaq'
import { courseRouteTo } from '@/data/courseAliases'
import { REPLIES, REPLY_SOURCE } from '@/data/assistantReplies'
import { DIRECTIONS } from '@/data/directions'
import { IT_DEV_FAQ } from '@/data/itDev'
import { IT_KIDS_FAQ } from '@/data/itKids'
import { localize } from '@/i18n/localize'
import { EMPTY_DATA } from '@/utils/assistantData'
import { bestMatch, findBest, mentions, tokenize } from '@/utils/assistantSearch'
import { formatDate, formatPrice } from '@/utils/format'

/** Mavzu va savol turini aniqlaydigan so'zlar (uchala til birga). */
const WORDS = {
  branch: ['filial', 'manzil', 'филиал', 'адрес', 'branch', 'address', 'ofis', 'офис', 'markaz'],
  course: ['kurs', 'yonalish', 'курс', 'направление', 'course', 'dastur', 'программа', 'program'],
  teacher: [
    'oqituvchi',
    'ustoz',
    'murabbiy',
    'преподаватель',
    'преподает',
    'преподают',
    'учитель',
    'teacher',
    'teach',
    'mentor',
  ],
  vacancy: ['vakansiya', 'вакансия', 'ish', 'работа', 'job', 'vacancy', 'rezyume', 'резюме'],
  news: ['yangilik', 'новости', 'новость', 'news'],
  price: [
    'narx',
    'pul',
    'tolov',
    'turadi',
    'chegirma',
    'цена',
    'стоимость',
    'стоит',
    'оплата',
    'скидка',
    'price',
    'cost',
    'fee',
    'discount',
  ],
  count: ['nechta', 'necha', 'qancha', 'сколько', 'количество', 'many'],
  where: ['qayer', 'qaerda', 'joylashgan', 'где', 'расположен', 'where', 'location'],
  exists: ['bormi', 'mavjud', 'ochilgan', 'есть', 'имеется', 'открыт', 'available', 'ochiq'],
  age: ['yosh', 'yoshdan', 'yoshli', 'возраст', 'лет', 'age', 'old'],
  social: ['instagram', 'telegram', 'youtube', 'facebook', 'ijtimoiy', 'соцсети', 'social'],
  schedule: [
    'jadval',
    'dars',
    'davomiylik',
    'soat',
    'kun',
    'расписание',
    'занятие',
    'урок',
    'длительность',
    'schedule',
    'lesson',
    'duration',
    'class',
  ],
}

/** Savol turini bildiruvchi so'zlar — nom izlashda hisobga olinmaydi. */
const SERVICE_WORDS = Object.values(WORDS).flat()

/**
 * Faqat savol turi haqidagi so'zlar. Yozuv nomini izlashda mavzu nomlari
 * («o'qituvchi» — ham lavozim, ham vakansiya nomi) kesilmasligi kerak,
 * shu sababli ro'yxat torroq.
 */
const QUESTION_WORDS = [
  ...WORDS.count,
  ...WORDS.where,
  ...WORDS.exists,
  ...WORDS.age,
  ...WORDS.price,
  ...WORDS.schedule,
  ...WORDS.social,
]

/**
 * Kursga havola.
 *
 * Havola HAR DOIM `courseRouteTo()` orqali yasaladi: admin paneldagi slug
 * («programmirovanie») maketga mos alohida sahifaga («/kursy/it-razrabotka»)
 * o'giriladi. Ilgari havola to'g'ridan-to'g'ri `{ name: 'course', slug }`
 * qilib yasalardi va marshrut nomi bo'yicha ochilgani uchun yo'naltirish
 * ishlamay, tashrifchi dizaynsiz umumiy sahifaga tushib qolardi.
 *
 * @param {{slug: string, title?: string}} course
 */
function courseLink(course) {
  return { label: course.title, ...courseRouteTo(course.slug) }
}

/** Bo'sh o'rinlarni to'ldiradi: `{name}` → qiymat. */
function fill(template, values) {
  return String(template).replace(/\{(\w+)\}/g, (whole, key) =>
    values[key] === undefined || values[key] === null ? '' : String(values[key]),
  )
}

/**
 * Shablonni joriy tilga o'girib, o'rinlarini to'ldiradi.
 * Chetdagi bo'shliqlar ATAYLAB saqlanadi — ba'zi shablonlar oldingi gapga
 * ulanadi (' Telefon: …'), tozalash esa javob yig'ilgach bir marta bo'ladi.
 */
function say(template, values, locale) {
  return fill(localize(template, locale), values)
}

/** Tayyor javobni tozalaydi: ortiqcha bo'shliq va bo'sh qatorlar. */
function finish(answer) {
  return {
    ...answer,
    text: String(answer.text)
      .replace(/[ \t]{2,}/g, ' ')
      .replace(/[ \t]+\n/g, '\n')
      .trim(),
  }
}

/** «A, B va C» ko'rinishidagi ro'yxat. */
function joinNames(names, locale) {
  if (names.length <= 1) return names.join('')
  const last = names[names.length - 1]
  const conjunction = { uz: ' va ', ru: ' и ', en: ' and ' }[locale] || ' va '
  return names.slice(0, -1).join(', ') + conjunction + last
}

/** Uzun matnni birinchi jumlalari bilan qisqartiradi. */
function shorten(text, limit = 260) {
  const value = String(text || '')
    .replace(/\s+/g, ' ')
    .trim()
  if (value.length <= limit) return value

  const cut = value.slice(0, limit)
  const stop = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('! '), cut.lastIndexOf('? '))
  return stop > 80 ? cut.slice(0, stop + 1) : `${cut.trim()}…`
}

/** Telegram havolasidan foydalanuvchi nomi (@marsitschool). */
function telegramHandle(url) {
  const match = String(url || '').match(/t\.me\/([\w_]+)/i)
  return match ? `@${match[1]}` : ''
}

/** Statik javoblardagi kontakt o'rinlarini sayt sozlamalari bilan to'ldiradi. */
function fillContacts(text, settings = {}) {
  const values = {
    phone: settings.phone || '',
    telegram: telegramHandle(settings.telegram_url),
    email: settings.email || '',
  }

  return (
    text
      .replace(/\{(phone|telegram|email)\}/g, (whole, key) => values[key] || whole)
      // Kontakt topilmasa jumlada osilib qolgan bo'lakni olib tashlaymiz.
      .replace(/[^.!?]*\{(phone|telegram|email)\}[^.!?]*[.!?]?\s*/g, '')
      .replace(/[ \t]{2,}/g, ' ')
      .trim()
  )
}

/* ------------------------------------------------------------------------ */
/* Jonli ma'lumot bo'yicha javoblar                                          */
/* ------------------------------------------------------------------------ */

/**
 * Savolda nomi tilga olingan yozuvlarni topadi.
 *
 * @param {Array<string>} tokens savol o'zaklari
 * @param {Array<object>} items qidiriladigan yozuvlar
 * @param {Array<string>} fields nom saqlanadigan maydonlar
 * @param {Array<string>} [exclude] nom bo'la olmaydigan so'zlar
 */
function matchByName(tokens, items, fields, exclude = SERVICE_WORDS) {
  const excluded = tokenize(exclude.join(' '), { keepStopWords: true })
  const candidates = tokens.filter((token) => token.length >= 3 && bestMatch(token, excluded) < 0.8)

  const found = []
  const matched = new Set()

  for (const item of items) {
    const itemTokens = tokenize(fields.map((field) => item[field] || '').join(' '))
    for (const token of candidates) {
      // 0.6 — «Chilanzar» ↔ «Chilonzor» kabi ikki harflik farqni ham qabul
      // qiladi; bunday yon berish faqat uzun so'zlarda ishlaydi.
      if (bestMatch(token, itemTokens) >= 0.6) {
        found.push(item)
        matched.add(token)
        break
      }
    }
  }

  return { found, unknown: candidates.filter((token) => !matched.has(token)) }
}

/**
 * Joy nomiga o'xshamaydigan so'zlar — fe'l qo'shimchalari bilan tugaydiganlar.
 * «Qibrayda filial ochasizmi?» savolida «ochasiz» joy nomi emas.
 */
const VERB_TAIL = /(siz|san|miz|ydi|adi|yapti|moqda|ing|ladi)$/

/** Nomga o'xshagan so'zlarni bosh harf bilan qaytaradi. */
function placeNames(stems) {
  return stems
    .filter((stem) => stem.length >= 4 && !VERB_TAIL.test(stem))
    .map((stem) => stem.charAt(0).toUpperCase() + stem.slice(1))
}

/** Manzil va mo'ljal ko'pincha bir joyni ikki xil yozadi — takrorlamaymiz. */
function isSamePlace(first, second) {
  if (!first || !second) return false
  const a = new Set(tokenize(first, { keepStopWords: true }))
  const b = tokenize(second, { keepStopWords: true })
  if (b.length === 0) return false
  const shared = b.filter((token) => a.has(token)).length
  return shared / b.length >= 0.5
}

function branchLine(branch) {
  return `• ${branch.name}${branch.address ? ` — ${branch.address}` : ''}`
}

function branchDetail(branch, locale) {
  const extra = [
    branch.landmark && !isSamePlace(branch.address, branch.landmark)
      ? say(REPLIES.branchLandmark, { landmark: branch.landmark }, locale)
      : '',
    branch.working_hours ? say(REPLIES.branchHours, { hours: branch.working_hours }, locale) : '',
    branch.phone ? say(REPLIES.branchPhone, { phone: branch.phone }, locale) : '',
  ]
    .filter(Boolean)
    .join(' ')

  return say(
    REPLIES.branchOne,
    { name: branch.name, address: branch.address, extra: extra ? ` ${extra}` : '' },
    locale,
  )
}

function branchAnswer(tokens, data, locale) {
  const branches = data.branches
  if (branches.length === 0) return null

  const names = branches.map((branch) => branch.name)
  const list = branches.map(branchLine).join('\n')
  const contacts = [{ label: localize(CONTACT_LINK.label, locale), name: 'contacts' }]

  const { found, unknown } = matchByName(tokens, branches, ['name', 'address', 'landmark'])
  const missing = placeNames(unknown).slice(0, 3)

  // «Yashnabodda filial bormi?» — nomi aytilgan, lekin bunday filial yo'q.
  if (found.length === 0 && missing.length > 0) {
    return {
      id: 'branch-missing',
      text: say(
        REPLIES.branchMissing,
        { names: joinNames(missing, locale), count: branches.length, list },
        locale,
      ),
      links: contacts,
    }
  }

  if (found.length > 0) {
    return {
      id: 'branch-detail',
      text: found
        .slice(0, 3)
        .map((branch) => branchDetail(branch, locale))
        .join('\n'),
      links: found
        .slice(0, 3)
        .map((branch) => ({ label: branch.name, name: 'branch', params: { slug: branch.slug } })),
    }
  }

  if (mentions(tokens, WORDS.count)) {
    return {
      id: 'branch-count',
      text: say(
        REPLIES.branchCount,
        { count: branches.length, names: joinNames(names, locale) },
        locale,
      ),
      links: contacts,
    }
  }

  return {
    id: 'branch-list',
    text: say(REPLIES.branchList, { count: branches.length, list }, locale),
    links: contacts,
  }
}

/** Dars davomiyligi ro'yxatda kelmasa — bu gap tushib qoladi. */
function courseMinutes(course, locale) {
  return course.lesson_duration_minutes
    ? say(REPLIES.courseMinutes, { minutes: course.lesson_duration_minutes }, locale)
    : ''
}

/** Bitta kurs bo'yicha qisqa ma'lumot: yosh, davomiylik, narx. */
function courseFacts(course, locale) {
  return {
    id: 'course-detail',
    text: say(
      REPLIES.courseOne,
      {
        title: course.title,
        age: course.age_range,
        months: course.duration_months,
        lessons: course.lessons_per_week,
        minutes: courseMinutes(course, locale),
        price: Number(course.price)
          ? say(REPLIES.coursePriceTail, { price: formatPrice(course.price) }, locale)
          : '',
      },
      locale,
    ),
    links: [courseLink(course)],
  }
}

function coursePrice(course, locale) {
  return say(
    REPLIES.coursePriceLine,
    { title: course.title, price: formatPrice(course.price) },
    locale,
  )
}

function courseAnswer(question, tokens, data, locale, settings) {
  const courses = data.courses
  if (courses.length === 0) return null

  const links = courses.slice(0, 3).map(courseLink)

  // Narx — API'dagi haqiqiy oylik to'lov.
  if (mentions(tokens, WORDS.price)) {
    const priced = courses.filter((course) => Number(course.price) > 0)
    if (priced.length > 0) {
      return {
        id: 'course-price',
        text: fillContacts(
          say(
            REPLIES.coursePrices,
            {
              list: priced.map((course) => coursePrice(course, locale)).join('\n'),
              phone: '{phone}',
            },
            locale,
          ),
          settings,
        ),
        links,
      }
    }
  }

  // Dars jadvali — davomiylik va haftadagi darslar soni.
  if (mentions(tokens, WORDS.schedule) && !mentions(tokens, WORDS.branch)) {
    return {
      id: 'course-schedule',
      text: say(
        REPLIES.schedule,
        {
          list: courses
            .map((course) =>
              say(
                REPLIES.scheduleLine,
                {
                  title: course.title,
                  lessons: course.lessons_per_week,
                  months: course.duration_months,
                  minutes: courseMinutes(course, locale),
                },
                locale,
              ),
            )
            .join('\n'),
        },
        locale,
      ),
      links,
    }
  }

  const { found } = matchByName(
    tokens,
    courses,
    ['title', 'subtitle'],
    [...WORDS.course, ...QUESTION_WORDS],
  )
  if (found.length > 0) return courseFacts(found[0], locale)

  return {
    id: 'course-list',
    text: say(
      REPLIES.courseList,
      {
        count: courses.length,
        list: courses
          .map((course) =>
            say(
              REPLIES.courseLine,
              {
                title: course.title,
                age: course.age_range,
                months: course.duration_months,
                lessons: course.lessons_per_week,
              },
              locale,
            ),
          )
          .join('\n'),
      },
      locale,
    ),
    links,
  }
}

/** Ijtimoiy tarmoq havolalari — sayt sozlamalaridan. */
function socialAnswer(tokens, settings, locale) {
  const networks = [
    { key: 'telegram_url', label: 'Telegram', words: ['telegram'] },
    { key: 'instagram_url', label: 'Instagram', words: ['instagram'] },
    { key: 'youtube_url', label: 'YouTube', words: ['youtube'] },
    { key: 'facebook_url', label: 'Facebook', words: ['facebook'] },
  ].filter((network) => settings?.[network.key])

  if (networks.length === 0) return null

  const asked = networks.filter((network) => mentions(tokens, network.words))
  const shown = asked.length > 0 ? asked : networks

  return {
    id: 'social',
    text: say(
      REPLIES.socialList,
      { list: shown.map((network) => `• ${network.label}: ${settings[network.key]}`).join('\n') },
      locale,
    ),
    links: [],
  }
}

function ageAnswer(data, locale) {
  const courses = data.courses.filter((course) => course.age_range)
  if (courses.length === 0) return null

  return {
    id: 'course-age',
    text: say(
      REPLIES.ageList,
      {
        list: courses
          .map((course) =>
            say(REPLIES.ageLine, { title: course.title, age: course.age_range }, locale),
          )
          .join('\n'),
      },
      locale,
    ),
    links: courses.slice(0, 3).map(courseLink),
  }
}

function teacherAnswer(tokens, data, locale) {
  const teachers = data.teachers
  if (teachers.length === 0) return null

  return {
    id: 'teachers',
    text: say(
      REPLIES.teacherList,
      {
        count: teachers.length,
        list: teachers
          .map((teacher) =>
            say(
              REPLIES.teacherLine,
              {
                name: teacher.full_name,
                badge: teacher.badge || teacher.position || '',
                years: teacher.experience_years || 0,
              },
              locale,
            ).replace(/\s*,\s*,/g, ','),
          )
          .join('\n'),
      },
      locale,
    ),
    links: [{ label: localize(ABOUT_LINK.label, locale), name: 'about' }],
  }
}

function vacancyAnswer(data, locale, tokens = []) {
  const open = data.vacancies.filter((vacancy) => vacancy.is_open !== false)
  const link = [{ label: localize(VACANCY_LINK.label, locale), name: 'vacancies' }]

  // Aniq vakansiya nomi aytilgan bo'lsa — faqat o'sha haqida.
  const named = matchByName(tokens, open, ['title'], [...WORDS.vacancy, ...QUESTION_WORDS]).found[0]
  if (named) {
    const salary = named.salary_from
      ? `${named.salary_from}${named.salary_to ? `–${named.salary_to}` : ''} ${named.salary_currency || ''}`.trim()
      : ''
    return {
      id: 'vacancy-detail',
      text: say(
        REPLIES.vacancyOne,
        {
          title: named.title,
          text: shorten(named.description || '', 220),
          extra: [named.branch_name, salary].filter(Boolean).join(', '),
        },
        locale,
      ),
      links: link,
    }
  }

  if (open.length === 0) {
    return { id: 'vacancy-none', text: localize(REPLIES.vacancyNone, locale), links: link }
  }

  return {
    id: 'vacancies',
    text: say(
      REPLIES.vacancyList,
      {
        count: open.length,
        list: open
          .map((vacancy) => {
            const parts = [
              vacancy.branch_name,
              vacancy.salary_from
                ? `${vacancy.salary_from}${vacancy.salary_to ? `–${vacancy.salary_to}` : ''} ${vacancy.salary_currency || ''}`.trim()
                : '',
            ].filter(Boolean)
            return say(
              REPLIES.vacancyLine,
              { title: vacancy.title, extra: parts.length ? ` — ${parts.join(', ')}` : '' },
              locale,
            )
          })
          .join('\n'),
      },
      locale,
    ),
    links: link,
  }
}

function newsAnswer(data, locale) {
  const items = data.news.slice(0, 3)
  if (items.length === 0) return null

  return {
    id: 'news',
    text: say(
      REPLIES.newsList,
      {
        list: items
          .map((item) =>
            say(
              REPLIES.newsLine,
              { title: item.title, date: formatDate(item.published_at, locale) },
              locale,
            ),
          )
          .join('\n'),
      },
      locale,
    ),
    links: items.map((item) => ({
      label: shorten(item.title, 40),
      name: 'news-detail',
      params: { slug: item.slug },
    })),
  }
}

/**
 * Savol aniq bir narsa haqidami — filial nomi, narx, yosh, vakansiya?
 * Bunday savollarga jonli ma'lumot bilan javob beriladi va u tayyor
 * matnlardan ustun turadi (statik matn eskirgan bo'lishi mumkin).
 */
function specificAnswer(question, tokens, data, locale, settings) {
  if (mentions(tokens, WORDS.social)) {
    const answer = socialAnswer(tokens, settings, locale)
    if (answer) return answer
  }

  if (mentions(tokens, WORDS.branch)) {
    const answer = branchAnswer(tokens, data, locale)
    if (answer) return answer
  }

  if (mentions(tokens, WORDS.vacancy)) {
    const answer = vacancyAnswer(data, locale, tokens)
    if (answer) return answer
  }

  if (mentions(tokens, WORDS.teacher)) {
    const answer = teacherAnswer(tokens, data, locale)
    if (answer) return answer
  }

  if (mentions(tokens, WORDS.news)) {
    const answer = newsAnswer(data, locale)
    if (answer) return answer
  }

  if (mentions(tokens, WORDS.price)) {
    const answer = courseAnswer(question, tokens, data, locale, settings)
    if (answer) return answer
  }

  // Kurs nomi to'g'ridan-to'g'ri aytilgan bo'lsa («IT Kids necha yoshdan?»).
  const course = matchByName(tokens, data.courses, ['title'], [...WORDS.course, ...QUESTION_WORDS])
    .found[0]
  if (course) {
    if (mentions(tokens, WORDS.age)) return ageAnswer(data, locale)
    return courseAnswer(question, tokens, data, locale, settings)
  }

  if (mentions(tokens, WORDS.age)) {
    const answer = ageAnswer(data, locale)
    if (answer) return answer
  }

  // Filial nomi «filial» so'zisiz aytilgan bo'lishi mumkin: «Chilonzorda
  // dars bormi?» — shuning uchun nomlar alohida tekshiriladi.
  const { found } = matchByName(tokens, data.branches, ['name'])
  if (found.length > 0) {
    return {
      id: 'branch-detail',
      text: found
        .slice(0, 2)
        .map((branch) => branchDetail(branch, locale))
        .join('\n'),
      links: found.slice(0, 2).map((branch) => ({
        label: branch.name,
        name: 'branch',
        params: { slug: branch.slug },
      })),
    }
  }

  return null
}

/**
 * Tayyor mavzuning javobini jonli ma'lumot bilan almashtiradi.
 * Ma'lumot yuklanmagan bo'lsa — `null`, ya'ni statik matn qoladi.
 */
function intentAnswer(topic, question, tokens, data, locale, settings) {
  switch (topic.intent) {
    case 'branches':
      return branchAnswer(tokens, data, locale)
    case 'vacancies':
      return vacancyAnswer(data, locale, tokens)
    case 'teachers':
      return teacherAnswer(tokens, data, locale)
    case 'age':
      return ageAnswer(data, locale)
    case 'course': {
      // Mavzu aynan bir kurs haqida: tavsif tayyor matndan, raqamlar API'dan.
      const course =
        matchByName(tokens, data.courses, ['title'], [...WORDS.course, ...QUESTION_WORDS])
          .found[0] || data.courses.find((item) => (topic.courseSlugs || []).includes(item.slug))
      if (!course) return courseAnswer(question, tokens, data, locale, settings)

      const facts = courseFacts(course, locale)
      return {
        id: `${topic.id}-course`,
        text: `${fillContacts(localize(topic.answer, locale), settings)}\n${facts.text}`,
        links: facts.links,
      }
    }
    case 'price':
    case 'schedule':
    case 'courses':
      return courseAnswer(question, tokens, data, locale, settings)
    default:
      return null
  }
}

/* ------------------------------------------------------------------------ */
/* Sayt matnlari bo'yicha qidiruv                                            */
/* ------------------------------------------------------------------------ */

const CONTACT_LINK = ASSISTANT_TOPICS.find((topic) => topic.id === 'branches').links[0]
const ABOUT_LINK = ASSISTANT_TOPICS.find((topic) => topic.id === 'about').links[0]
const VACANCY_LINK = ASSISTANT_TOPICS.find((topic) => topic.id === 'vacancies').links[0]

/**
 * Qidiriladigan hujjatlar: API'dan kelgan yozuvlar va sahifalardagi matnlar.
 * Har bir hujjatda tayyor javob (`answer`) va kerakli havola turadi.
 */
export function buildCorpus(data, locale) {
  const documents = []

  for (const course of data.courses) {
    documents.push({
      title: course.title,
      text: [course.subtitle, course.description].filter(Boolean).join(' '),
      answer: shorten([course.subtitle, course.description].filter(Boolean).join(' ')),
      links: [courseLink(course)],
    })
  }

  for (const item of data.news) {
    documents.push({
      title: item.title,
      text: item.excerpt || '',
      answer: `${item.title}. ${shorten(item.excerpt || '')}`,
      quote: true,
      links: [{ label: item.title, name: 'news-detail', params: { slug: item.slug } }],
    })
  }

  for (const vacancy of data.vacancies) {
    documents.push({
      title: vacancy.title,
      text: [vacancy.description, vacancy.requirements, vacancy.conditions]
        .filter(Boolean)
        .join(' '),
      answer: `${vacancy.title}. ${shorten(vacancy.description || '')}`,
      quote: true,
      links: [{ label: localize(VACANCY_LINK.label, locale), name: 'vacancies' }],
    })
  }

  for (const teacher of data.teachers) {
    documents.push({
      title: teacher.full_name,
      text: [teacher.badge, teacher.company, (teacher.skills || []).map((s) => s.name).join(' ')]
        .filter(Boolean)
        .join(' '),
      answer: [teacher.full_name, teacher.badge, teacher.company].filter(Boolean).join(' — '),
      links: [{ label: localize(ABOUT_LINK.label, locale), name: 'about' }],
    })
  }

  // Sahifalardagi qat'iy matnlar — yo'nalish tavsiflari va savol-javoblar.
  for (const direction of DIRECTIONS) {
    const title = localize(direction.title, locale)
    const text = [localize(direction.subtitle, locale), localize(direction.description, locale)]
      .filter(Boolean)
      .join(' ')
    documents.push({
      title,
      text,
      answer: shorten(text),
      links: [courseLink({ slug: direction.slug, title })],
    })
  }

  for (const item of [...IT_KIDS_FAQ, ...IT_DEV_FAQ]) {
    documents.push({
      title: localize(item.question, locale),
      text: localize(item.answer, locale),
      answer: localize(item.answer, locale),
      links: [],
    })
  }

  for (const topic of ASSISTANT_TOPICS) {
    documents.push({
      title: topic.chip ? localize(topic.chip, locale) : '',
      text: localize(topic.answer, locale),
      answer: localize(topic.answer, locale),
      links: (topic.links || []).map((link) => ({ ...link, label: localize(link.label, locale) })),
    })
  }

  return documents
}

/* ------------------------------------------------------------------------ */
/* Tayyor mavzular                                                           */
/* ------------------------------------------------------------------------ */

/** Savolga eng mos tayyor mavzu (topilmasa `null`). */
export function matchTopic(question) {
  const tokens = tokenize(question)
  if (tokens.length === 0) return null

  let best = null
  let bestScore = 0

  for (const topic of ASSISTANT_TOPICS) {
    let score = 0

    for (const keyword of topic.keywords) {
      const keywordTokens = tokenize(keyword, { keepStopWords: true })
      if (keywordTokens.length === 0) continue

      // Ko'p so'zli kalit («it kids») — barcha so'zi topilsa, bittalikdan kuchli.
      let total = 0
      let matchedLength = 0
      for (const part of keywordTokens) {
        let best = 0
        for (const token of tokens) {
          const value = bestMatch(part, [token])
          if (value > best) {
            best = value
            matchedLength = Math.max(matchedLength, token.length)
          }
        }
        total += best
      }
      const average = total / keywordTokens.length
      if (average < 0.8) continue

      // Oxirgi qo'shiluvchi — teng ballar uchun: uzunroq so'zga tushgan
      // moslik aniqroq («robototexnika» ↔ «robot», «o'rganasizmi» ↔ «o'rgan» emas).
      score = Math.max(
        score,
        average * keywordTokens.length * (1 + keyword.length / 40) + matchedLength / 1000,
      )
    }

    if (score > bestScore) {
      best = topic
      bestScore = score
    }
  }

  return best
}

export function topicById(id) {
  return ASSISTANT_TOPICS.find((topic) => topic.id === id) || null
}

/** Mavzuni javobga aylantiradi. */
function topicAnswer(topic, locale, settings) {
  return {
    id: topic.id,
    text: fillContacts(localize(topic.answer, locale), settings),
    links: (topic.links || []).map((link) => ({ ...link, label: localize(link.label, locale) })),
  }
}

/* ------------------------------------------------------------------------ */

/**
 * Savolga javob.
 *
 * @param {string} question foydalanuvchi matni
 * @param {{locale: string, settings?: object, data?: object, topic?: object}} context
 *        `data` — `loadAssistantData()` natijasi; `topic` berilsa qidiruv
 *        o'tkazilmaydi (chiplar shu yo'ldan yuradi).
 * @returns {{id: string, text: string, links: Array}}
 */
export function answerQuestion(question, { locale = 'uz', settings, data, topic } = {}) {
  const facts = data || EMPTY_DATA
  const tokens = tokenize(question)

  // Chip bosilgan: mavzu ma'lum, lekin javob baribir jonli ma'lumotdan.
  if (topic) {
    return finish(
      intentAnswer(topic, question, tokens, facts, locale, settings) ||
        topicAnswer(topic, locale, settings),
    )
  }

  const specific = specificAnswer(question, tokens, facts, locale, settings)
  if (specific) return finish(specific)

  const matched = matchTopic(question)
  if (matched) {
    return finish(
      intentAnswer(matched, question, tokens, facts, locale, settings) ||
        topicAnswer(matched, locale, settings),
    )
  }

  // Umumiy savol («darslar qanday o'tadi?») — kurslar ro'yxatidan.
  if (mentions(tokens, WORDS.course) || mentions(tokens, WORDS.schedule)) {
    const answer = courseAnswer(question, tokens, facts, locale, settings)
    if (answer) return finish(answer)
  }

  const document = findBest(question, buildCorpus(facts, locale))
  if (document) {
    return finish({
      id: 'search',
      text: document.quote
        ? `${localize(REPLY_SOURCE, locale)}${document.answer}`
        : document.answer,
      links: document.links || [],
    })
  }

  return finish(topicAnswer(ASSISTANT_FALLBACK, locale, settings))
}
