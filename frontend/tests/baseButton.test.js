// @vitest-environment happy-dom
/**
 * `BaseButton` — saytdagi barcha CTA tugmalari shu komponentdan chiqadi.
 *
 * Asosiy xavf: `to` berilganda `RouterLink` `href` ni o'zi hisoblaydi, lekin
 * komponent tashqaridan `href` atributini ham uzatsa, u fallthrough atribut
 * sifatida hisoblangan manzilni bekor qiladi. Natijada `<a>` manzilsiz qoladi:
 * tab tartibiga tushmaydi (klaviatura bilan birorta tugmaga yetib bo'lmaydi),
 * «yangi oynada ochish» ishlamaydi, qidiruv robotlari havolani ko'rmaydi.
 * Shuning uchun har bir teg uchun atributlar alohida tekshiriladi.
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import BaseButton from '@/components/base/BaseButton.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div />' } },
    { path: '/zayavka', name: 'application', component: { template: '<div />' } },
  ],
})

function mountButton(props = {}) {
  return mount(BaseButton, {
    props,
    slots: { default: 'Bosim' },
    global: { plugins: [router] },
  })
}

describe('BaseButton', () => {
  it('`to` berilganda haqiqiy `href` li havola chiqaradi', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mountButton({ to: { name: 'application', query: { source: 'test' } } })
    const link = wrapper.get('a')

    expect(link.attributes('href')).toBe('/zayavka?source=test')
  })

  it('`href` berilganda tashqi havola sifatida `rel` qo’yadi', () => {
    const wrapper = mountButton({ href: 'https://t.me/marsitschool' })
    const link = wrapper.get('a')

    expect(link.attributes('href')).toBe('https://t.me/marsitschool')
    expect(link.attributes('rel')).toBe('noopener noreferrer')
  })

  it('manzilsiz holatda `type` li tugma bo’lib qoladi', () => {
    const wrapper = mountButton({ type: 'submit' })
    const button = wrapper.get('button')

    expect(button.attributes('type')).toBe('submit')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('yuklanayotganda tugma bloklanadi', () => {
    const button = mountButton({ loading: true }).get('button')

    expect(button.attributes('disabled')).toBeDefined()
    expect(button.attributes('aria-busy')).toBe('true')
  })

  it('havolaga `type` va `disabled` atributlari yopishmaydi', () => {
    const link = mountButton({ href: '#programma', disabled: true, type: 'submit' }).get('a')

    expect(link.attributes('type')).toBeUndefined()
    expect(link.attributes('disabled')).toBeUndefined()
  })
})
