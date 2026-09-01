/**
 * Sayt marshrutlari — Figma'dagi sahifalarga mos.
 * Barcha sahifalar lazy-load qilinadi (kichik boshlang'ich bundle).
 */
import { createRouter, createWebHistory } from 'vue-router'

import { COURSE_ALIASES, COURSE_ROUTES } from '@/data/courseAliases'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

/**
 * Takrorlanuvchi kurs sahifalari: admin paneldagi slug alohida sahifaga
 * yo'naltiriladi (masalan `/kursy/programmirovanie` → `/kursy/it-razrabotka`),
 * shunda bitta kurs bitta URL'da qoladi.
 */
const aliasRoutes = Object.entries(COURSE_ALIASES).map(([from, to]) => ({
  path: `kursy/${from}`,
  redirect: { name: COURSE_ROUTES[to] || 'course', params: { slug: to } },
}))

const routes = [
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
        path: 'test/rezultat/:id',
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
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth', top: 96 }
    return { top: 0 }
  },
})

export default router
