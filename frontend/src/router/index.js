/**
 * Sayt marshrutlari — Figma'dagi sahifalarga mos.
 * Barcha sahifalar lazy-load qilinadi (kichik boshlang'ich bundle).
 */
import { createRouter, createWebHistory } from 'vue-router'

import { COURSE_ALIASES, COURSE_ROUTES } from '@/data/courseAliases'
import { SITE, splitLocalePath } from '@/data/seoConfig'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

/**
 * Marshrutlar uchun asos yo'li — til prefiksini hisobga oladi.
 *
 * Ruscha va inglizcha sahifalar `/ru/...` va `/en/...` manzillarida yotadi
 * (`seoConfig.js:localeUrl`), chunki statik hostingda faqat shunday qilib
 * har bir tilga O'Z HTML fayli berish mumkin — JavaScript ishlatmaydigan
 * robotlar (GPTBot, ClaudeBot, PerplexityBot) uchun bu yagona yo'l.
 *
 * Prefiksni marshrut jadvaliga qo'shish o'rniga uni `history` asosiga
 * beramiz: router faqat toza yo'llarni ko'radi (`/kursy`), marshrut nomlari
 * va barcha `router-link`lar o'zgarishsiz qoladi, lekin manzil satrida
 * prefiks saqlanadi va ichki havolalar ham avtomatik prefiksli bo'ladi.
 */
function historyBase() {
  const raw = import.meta.env.BASE_URL || '/'
  if (typeof window === 'undefined') return raw
  const { locale } = splitLocalePath(window.location.pathname)
  if (locale === SITE.defaultLocale) return raw
  return `${raw.replace(/\/$/, '')}/${locale}/`
}

/**
 * Takrorlanuvchi kurs sahifalari: admin paneldagi slug alohida sahifaga
 * yo'naltiriladi (masalan `/kursy/programmirovanie` → `/kursy/it-razrabotka`),
 * shunda bitta kurs bitta URL'da qoladi.
 */
const aliasRoutes = Object.entries(COURSE_ALIASES).map(([from, to]) => ({
  path: `kursy/${from}`,
  redirect: { name: COURSE_ROUTES[to] || 'course', params: { slug: to } },
}))

/**
 * Sahifalar jadvali. Eksport qilinadi, chunki testlar marshrut nomlarini
 * tekshiradi: javob havolasi mavjud bo'lmagan sahifaga ketmasligi kerak.
 */
export const routes = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
      { path: 'o-nas', name: 'about', component: () => import('@/views/AboutView.vue') },
      { path: 'kursy', name: 'courses', component: () => import('@/views/CoursesView.vue') },
      {
        path: 'kursy/it-kids',
        name: 'course-it-kids',
        component: () => import('@/views/ItKidsView.vue'),
      },
      {
        path: 'kursy/it-razrabotka',
        name: 'course-it-razrabotka',
        component: () => import('@/views/ItDevView.vue'),
      },
      ...aliasRoutes,
      {
        path: 'kursy/:slug',
        name: 'course',
        component: () => import('@/views/CourseView.vue'),
        props: true,
      },
      {
        path: 'zayavka',
        name: 'application',
        component: () => import('@/views/ApplicationView.vue'),
      },
      { path: 'space', name: 'space', component: () => import('@/views/SpaceView.vue') },
      { path: 'test', name: 'quiz', component: () => import('@/views/QuizView.vue') },
      {
        // Manzilda natijaning MAXFIY kaliti turadi (`Submission.public_token`),
        // MongoDB `_id` si emas: ObjectId ketma-ket o'sadi va bitta havolani
        // bilgan odam boshqalarnikini taxmin qila olardi.
        path: 'test/rezultat/:token',
        name: 'quiz-result',
        component: () => import('@/views/QuizResultView.vue'),
        props: true,
      },
      { path: 'novosti', name: 'news', component: () => import('@/views/NewsView.vue') },
      {
        path: 'novosti/:slug',
        name: 'news-detail',
        component: () => import('@/views/NewsDetailView.vue'),
        props: true,
      },
      { path: 'vakansii', name: 'vacancies', component: () => import('@/views/VacanciesView.vue') },
      { path: 'kontakty', name: 'contacts', component: () => import('@/views/ContactsView.vue') },
      {
        path: 'kontakty/:slug',
        name: 'branch',
        component: () => import('@/views/BranchView.vue'),
        props: true,
      },
      {
        path: ':pathMatch(.*)*',
        name: 'not-found',
        component: () => import('@/views/NotFoundView.vue'),
      },
    ],
  },
]

export const router = createRouter({
  history: createWebHistory(historyBase()),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth', top: 96 }
    // Faqat so'rov parametri o'zgargan bo'lsa (masalan til almashganda
    // qo'shiladigan `?lang=`) sahifa o'z joyida qoladi — foydalanuvchi
    // o'qiyotgan bo'limidan tepaga otilib ketmaydi.
    if (to.path === from.path) return false
    return { top: 0 }
  },
})

export default router
