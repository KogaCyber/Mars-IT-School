// @vitest-environment happy-dom
/**
 * Admin paneldagi «saytda ko'rsatilsin» belgisi.
 *
 * Ilgari o'chirilgan bo'lim API javobidan butunlay tushib qolardi, sayt esa
 * uni «panelda hech narsa yozilmagan» deb hisoblab, maketdagi standart matn
 * bilan ko'rsatishda davom etardi — ya'ni belgi hech narsani yashirmasdi.
 * Shuning uchun bu yerda blok haqiqatan DOM'dan yo'qolishi tekshiriladi.
 */
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { createI18n } from 'vue-i18n'
import { createMemoryHistory, createRouter } from 'vue-router'

import DirectionsSection from '@/components/courses/DirectionsSection.vue'
import { useContentStore } from '@/stores/content'

const i18n = createI18n({
  legacy: false,
  locale: 'ru',
  fallbackLocale: 'ru',
  missingWarn: false,
  fallbackWarn: false,
  messages: { ru: { courses: { directionsTitle: 'Направления' } } },
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
})

const mountDirections = () =>
  mount(DirectionsSection, {
    global: { plugins: [router, i18n], directives: { reveal: {} } },
  })

describe("bo'limni yashirish", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("«Скоро...» banneri o'chirilganda chizilmaydi", async () => {
    useContentStore().merge({
      'courses.directions': { is_published: true, items: [] },
      'courses.coming_soon': { is_published: false, items: [] },
    })

    const wrapper = mountDirections()

    expect(wrapper.find('section').exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'ComingSoonBanner' }).exists()).toBe(false)
  })

  it("belgi yoqilgan bo'lsa banner ko'rinadi", () => {
    useContentStore().merge({
      'courses.directions': { is_published: true, items: [] },
      'courses.coming_soon': { is_published: true, title: 'Скоро...', items: [] },
    })

    expect(mountDirections().text()).toContain('Скоро...')
  })

  it("«Yo'nalishlar» bo'limi o'chirilganda butun blok yo'qoladi", () => {
    useContentStore().merge({ 'courses.directions': { is_published: false, items: [] } })

    expect(mountDirections().find('section').exists()).toBe(false)
  })
})
