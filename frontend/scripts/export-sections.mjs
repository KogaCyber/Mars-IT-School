/**
 * Maketdagi joriy matnlarni admin panel uchun «urug'» faylga eksport qiladi.
 *
 * Ilgari sayt matnlari faqat frontend kodida (`i18n/messages`, `data/*.js`)
 * turardi. Endi ular admin paneldan boshqariladi, lekin panel bo'sh ochilmasligi
 * kerak — kontent kirituvchi odam saytda turgan matnni ko'rib, o'shani
 * tahrirlashi lozim. Shuning uchun joriy matnlar backend'ga bir marta
 * ko'chiriladi:
 *
 *   npx vite-node scripts/export-sections.mjs
 *
 * Natija: backend/apps/core/fixtures/section_defaults.json
 * Uni `python manage.py sync_sections` bo'limlarni birinchi yaratganda o'qiydi.
 *
 * Rasmlar ko'chirilmaydi: admin panelda rasm yuklanmagan bo'lsa, sayt
 * loyihadagi maket rasmini ko'rsatadi.
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import aboutMessages from '@/i18n/messages/about.js'
import commonMessages from '@/i18n/messages/common.js'
import contactsMessages from '@/i18n/messages/contacts.js'
import coursesMessages from '@/i18n/messages/courses.js'
import footerMessages from '@/i18n/messages/footer.js'
import formsMessages from '@/i18n/messages/forms.js'
import homeMessages from '@/i18n/messages/home.js'
import newsMessages from '@/i18n/messages/news.js'
import pagesMessages from '@/i18n/messages/pages.js'
import quizMessages from '@/i18n/messages/quiz.js'
import spaceMessages from '@/i18n/messages/space.js'
import vacanciesMessages from '@/i18n/messages/vacancies.js'

import { COMING_SOON, DIRECTIONS } from '@/data/directions.js'
import {
  IT_DEV_FACTS,
  IT_DEV_GALLERY,
  IT_DEV_STAGES,
  IT_DEV_STAGES_SUMMARY,
  IT_DEV_TOPICS,
} from '@/data/itDev.js'
import {
  IT_KIDS_FACTS,
  IT_KIDS_GALLERY,
  IT_KIDS_STAGES,
  IT_KIDS_STAGES_SUMMARY,
  IT_KIDS_TOPICS,
} from '@/data/itKids.js'
import {
  SPACE_FEATURES,
  SPACE_GAMIFICATION,
  SPACE_PARENTS,
  SPACE_PREMIUM,
  SPACE_SHOP,
} from '@/data/spacePlatform.js'
import { localize } from '@/i18n/localize.js'

const LANGS = ['ru', 'uz', 'en']

const MESSAGES = {
  about: aboutMessages,
  common: commonMessages,
  contacts: contactsMessages,
  courses: coursesMessages,
  footer: footerMessages,
  forms: formsMessages,
  home: homeMessages,
  news: newsMessages,
  pages: pagesMessages,
  quiz: quizMessages,
  space: spaceMessages,
  vacancies: vacanciesMessages,
}

/** `'home.heroTitle'` → { ru, uz, en } */
function fromMessages(path) {
  const [bundle, key] = path.split('.')
  const source = MESSAGES[bundle]
  if (!source) throw new Error(`Noma'lum tarjima to'plami: ${bundle}`)
  return Object.fromEntries(LANGS.map((lang) => [lang, source[lang]?.[key] ?? '']))
}

/** `L()` qiymatini yoki oddiy satrni uch tilga yoyadi. */
function fromValue(value) {
  return Object.fromEntries(LANGS.map((lang) => [lang, localize(value, lang) ?? '']))
}

/** { title: 'home.heroTitle' } → { title_ru, title_uz, title_en } */
function buildFields(map) {
  const result = {}
  for (const [field, source] of Object.entries(map)) {
    const values = typeof source === 'string' ? fromMessages(source) : fromValue(source)
    for (const lang of LANGS) {
      const value = values[lang]
      if (value) result[`${field}_${lang}`] = Array.isArray(value) ? value.join('\n') : value
    }
  }
  return result
}

/** Element ro'yxatini uch tilli maydonlarga yoyadi. */
function buildItems(items, map) {
  return items.map((item) => {
    const fields = {}
    for (const [field, pick] of Object.entries(map)) {
      const raw = pick(item)
      if (raw === undefined || raw === null || raw === '') continue
      if (field === 'icon_name' || field === 'url') {
        fields[field] = String(raw)
        continue
      }
      const values = fromValue(raw)
      for (const lang of LANGS) {
        const value = values[lang]
        if (value) fields[`${field}_${lang}`] = Array.isArray(value) ? value.join('\n') : value
      }
    }
    return fields
  })
}

const STAGE_MAP = {
  value: (stage) => stage.number,
  title: (stage) => stage.title,
  label: (stage) => stage.duration,
  text: (stage) => stage.description,
  list: (stage) => stage.topics,
  note: (stage) => stage.result,
  icon_name: (stage) => (stage.tools || []).join(','),
}
const CARD_MAP = {
  title: (card) => card.title,
  text: (card) => card.description,
  icon_name: (card) => card.icon ?? card.id,
}
const FACT_MAP = { value: (fact) => fact.value, label: (fact) => fact.label }
const GALLERY_MAP = { text: (image) => image.alt }

const sections = {
  // ------------------------------ Bosh sahifa ------------------------------
  'home.hero': {
    fields: buildFields({
      title: 'home.heroTitle',
      text: 'home.heroText',
      subtitle: 'home.heroTextSecond',
      button_label: 'common.trialLesson',
      button2_label: 'common.viewCourses',
    }),
  },
  'home.advantages': {
    fields: buildFields({
      eyebrow: 'home.advantagesEyebrow',
      title: 'home.advantagesTitle',
      text: 'home.advantagesText',
    }),
  },
  'home.space': {
    fields: buildFields({
      eyebrow: 'home.spaceEyebrow',
      title: 'home.spaceTitle',
      text: 'home.spaceText',
    }),
  },
  'home.news': {
    fields: buildFields({
      eyebrow: 'home.newsEyebrow',
      title: 'home.newsTitle',
      button_label: 'home.newsAll',
    }),
  },
  'home.team': {
    fields: buildFields({ eyebrow: 'home.teamEyebrow', title: 'home.teamTitle' }),
  },
  'home.reviews': {
    fields: buildFields({
      eyebrow: 'home.reviewsEyebrow',
      title: 'home.reviewsTitle',
      text: 'home.reviewsText',
    }),
  },
  'home.faq': {
    fields: buildFields({ eyebrow: 'home.faqEyebrow', title: 'home.faqTitle' }),
  },

  // ----------------------------- Biz haqimizda -----------------------------
  'about.hero': { fields: buildFields({ title: 'about.heroTitle' }) },
  'about.future': {
    fields: buildFields({
      eyebrow: 'about.futureEyebrow',
      title: 'about.futureTitle',
      text: 'about.futureText',
      note: 'about.futureNote',
    }),
  },
  'about.skills': {
    fields: buildFields({ eyebrow: 'about.skillsEyebrow', title: 'about.skillsTitle' }),
  },
  'about.demoday': {
    fields: buildFields({
      eyebrow: 'about.demoDayEyebrow',
      title: 'about.demoDayTitle',
      text: 'about.demoDayText',
    }),
  },
  'about.school': {
    fields: buildFields({
      eyebrow: 'about.schoolEyebrow',
      title: 'about.schoolTitle',
      button_label: 'about.watchVideo',
    }),
  },
  'about.founders': {
    fields: buildFields({ eyebrow: 'about.foundersEyebrow', title: 'about.foundersTitle' }),
  },
  'about.teachers': {
    fields: buildFields({
      eyebrow: 'about.teachersEyebrow',
      title: 'about.teachersTitle',
      text: 'about.teachersText',
    }),
  },

  // -------------------------------- Kurslar --------------------------------
  'courses.hero': {
    fields: buildFields({
      title: 'pages.coursesHeroTitle',
      button_label: 'common.trialLesson',
    }),
  },
  'courses.directions': {
    fields: buildFields({ title: 'courses.directionsTitle' }),
    items: buildItems(DIRECTIONS, {
      title: (item) => item.title,
      label: (item) => item.subtitle,
      text: (item) => item.description,
      value: (item) => item.ageRange,
      url: (item) => `/kursy/${item.slug}`,
      icon_name: (item) => (item.tech || []).join(','),
    }),
  },
  'courses.coming_soon': {
    fields: buildFields({ title: COMING_SOON.title, text: COMING_SOON.description }),
  },

  // -------------------------------- IT Kids --------------------------------
  'itkids.hero': {
    fields: buildFields({
      title: 'courses.itKidsHeroTitle',
      button_label: 'common.trialLesson',
      button2_label: 'courses.programButton',
    }),
  },
  'itkids.facts': { items: buildItems(IT_KIDS_FACTS, FACT_MAP) },
  'itkids.about': {
    fields: buildFields({
      eyebrow: 'courses.aboutEyebrow',
      title: 'courses.itKidsAboutTitle',
      text: 'courses.itKidsAboutDescription',
    }),
    items: buildItems(IT_KIDS_TOPICS, CARD_MAP),
  },
  'itkids.stages': {
    fields: buildFields({
      eyebrow: 'courses.programEyebrow',
      title: 'courses.stagesTitle',
      text: 'courses.stagesDescription',
      note: IT_KIDS_STAGES_SUMMARY,
    }),
    items: buildItems(IT_KIDS_STAGES, STAGE_MAP),
  },
  'itkids.gallery': {
    fields: buildFields({
      eyebrow: 'courses.galleryEyebrow',
      title: 'courses.galleryTitle',
      text: 'courses.galleryDescription',
    }),
    items: buildItems(IT_KIDS_GALLERY, GALLERY_MAP),
  },

  // ----------------------------- IT dasturlash -----------------------------
  'itdev.hero': {
    fields: buildFields({
      title: 'courses.itDevHeroTitle',
      text: 'courses.itDevHeroDescription',
      button_label: 'common.trialLesson',
      button2_label: 'courses.programButton',
    }),
  },
  'itdev.facts': { items: buildItems(IT_DEV_FACTS, FACT_MAP) },
  'itdev.about': {
    fields: buildFields({
      eyebrow: 'courses.aboutEyebrow',
      title: 'courses.itDevAboutTitle',
      text: 'courses.itDevAboutDescription',
    }),
    items: buildItems(IT_DEV_TOPICS, CARD_MAP),
  },
  'itdev.stages': {
    fields: buildFields({
      eyebrow: 'courses.programEyebrow',
      title: 'courses.stagesTitle',
      text: 'courses.stagesDescription',
      note: IT_DEV_STAGES_SUMMARY,
    }),
    items: buildItems(IT_DEV_STAGES, STAGE_MAP),
  },
  'itdev.gallery': {
    fields: buildFields({
      eyebrow: 'courses.galleryEyebrow',
      title: 'courses.galleryTitle',
      text: 'courses.galleryDescription',
    }),
    items: buildItems(IT_DEV_GALLERY, GALLERY_MAP),
  },

  // --------------------------------- SPACE ---------------------------------
  'space.hero': {
    fields: buildFields({ title: 'space.heroTitle', button_label: 'space.heroButton' }),
  },
  'space.features': {
    fields: buildFields({
      eyebrow: 'space.featuresEyebrow',
      title: 'space.featuresTitle',
      text: 'space.featuresText',
    }),
    items: buildItems(SPACE_FEATURES, CARD_MAP),
  },
  'space.gamification': {
    fields: buildFields({
      eyebrow: 'space.gamificationEyebrow',
      title: 'space.gamificationTitle',
      text: 'space.gamificationText',
    }),
    items: buildItems(SPACE_GAMIFICATION, CARD_MAP),
  },
  'space.premium': {
    fields: buildFields({
      eyebrow: 'space.premiumEyebrow',
      title: 'space.premiumTitle',
      text: 'space.premiumText',
      note: 'space.premiumNote',
      button_label: 'space.premiumButton',
    }),
    items: buildItems(SPACE_PREMIUM, CARD_MAP),
  },
  'space.shop': {
    fields: buildFields({
      eyebrow: 'space.shopEyebrow',
      title: 'space.shopTitle',
      text: 'space.shopText',
      button_label: 'space.shopButton',
      subtitle: 'space.shopCollectTitle',
      note: 'space.shopCollectText',
    }),
    items: buildItems(SPACE_SHOP, {
      title: (item) => item.title,
      value: (item) => String(item.price),
      icon_name: (item) => item.image,
    }),
  },
  'space.parents': {
    fields: buildFields({
      eyebrow: 'space.parentsEyebrow',
      title: 'space.parentsTitle',
      text: 'space.parentsText',
    }),
    items: buildItems(SPACE_PARENTS, CARD_MAP),
  },
  'space.application': {
    fields: buildFields({
      eyebrow: 'space.applicationEyebrow',
      title: 'space.applicationTitle',
      text: 'space.applicationText',
    }),
  },

  // ------------------------------ Yangiliklar ------------------------------
  'news.hero': {
    fields: buildFields({
      title: 'pages.newsHeroTitle',
      text: 'pages.newsHeroDescription',
    }),
  },
  'news.list': {
    fields: buildFields({
      eyebrow: 'news.eyebrow',
      title: 'news.title',
      subtitle: 'news.emptyTitle',
      note: 'news.emptyDescription',
    }),
  },

  // ------------------------------- Kontaktlar ------------------------------
  'contacts.hero': {
    fields: buildFields({
      title: 'contacts.heroTitle',
      button_label: 'common.trialLesson',
    }),
  },
  'contacts.info': {
    fields: buildFields({
      eyebrow: 'contacts.infoEyebrow',
      title: 'contacts.infoTitle',
      text: 'contacts.infoText',
    }),
  },
  'contacts.branches': {
    fields: buildFields({
      eyebrow: 'contacts.branchesEyebrow',
      title: 'contacts.branchesTitle',
      text: 'contacts.branchesHint',
      note: 'contacts.branchesEmpty',
    }),
  },
  'contacts.trial': {
    fields: buildFields({
      title: 'contacts.trialTitle',
      text: 'contacts.trialDescription',
    }),
  },

  // ------------------------------ Vakansiyalar -----------------------------
  'vacancies.hero': {
    fields: buildFields({
      title: 'vacancies.heroTitle',
      text: 'vacancies.heroDescription',
    }),
  },
  'vacancies.list': {
    fields: buildFields({
      eyebrow: 'vacancies.eyebrow',
      title: 'vacancies.title',
      text: 'vacancies.lead',
      subtitle: 'vacancies.emptyTitle',
      note: 'vacancies.emptyDescription',
    }),
  },

  // ---------------------------------- Test ---------------------------------
  'quiz.intro': {
    fields: buildFields({
      title: 'quiz.greetingFallback',
      subtitle: 'quiz.greeting',
      text: 'quiz.intro',
    }),
  },
  'quiz.contact': {
    fields: buildFields({
      title: 'quiz.almostDone',
      text: 'quiz.contactText',
      button_label: 'quiz.showResult',
    }),
  },
  'quiz.result': {
    fields: buildFields({
      title: 'quiz.resultTitle',
      eyebrow: 'quiz.skillsEyebrow',
      subtitle: 'quiz.skillsSubtitle',
      text: 'quiz.topSkillsTitle',
    }),
  },

  // --------------------------------- Umumiy --------------------------------
  'common.trial': {
    fields: buildFields({
      eyebrow: 'forms.trialEyebrow',
      title: 'forms.trialTitle',
      text: 'forms.trialDescription',
    }),
  },
  'common.buttons': {
    fields: buildFields({
      button_label: 'common.trialLesson',
      button2_label: 'common.viewCourses',
    }),
  },
  'common.footer': {
    fields: buildFields({ text: 'footer.tagline', note: 'footer.rights' }),
  },
}

const target = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../backend/apps/core/fixtures/section_defaults.json',
)
mkdirSync(dirname(target), { recursive: true })
writeFileSync(target, `${JSON.stringify(sections, null, 2)}\n`, 'utf8')

const items = Object.values(sections).reduce((sum, s) => sum + (s.items?.length ?? 0), 0)
console.log(`${Object.keys(sections).length} ta bo'lim, ${items} ta element → ${target}`)
