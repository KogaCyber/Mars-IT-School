// @vitest-environment happy-dom
/**
 * `useAutoReveal` — skrolldagi paydo bo'lish animatsiyasi.
 *
 * Bu kod kontentni ATAYLAB yashiradi (`.reveal` → `opacity: 0`) va uni
 * ekranga kirganda ochadi. Shuning uchun undagi har qanday xatolik
 * to'g'ridan-to'g'ri "sahifaning bir qismi ko'rinmay qoldi" degani.
 *
 * Ilgari aynan shunday bo'lgan: manzil o'zgarganda (til almashtirish yoki
 * `#anchor` ga sakrash — ikkalasida ham komponentlar mount holicha qoladi)
 * kuzatuv qaytadan yig'ilardi, lekin `reveal` sinfi bor elementlar
 * "qo'lda yozilgan" deb hisoblanib chetlab o'tilardi. Natijada hali
 * ochilmagan bloklar butunlay ko'rinmas bo'lib qolardi.
 */
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h, nextTick, reactive } from 'vue'

import { useAutoReveal } from '@/composables/useAutoReveal'

/** Kuzatilayotgan elementlarni ushlab turadigan soxta IntersectionObserver. */
const observed = new Set()

class FakeIntersectionObserver {
  observe(el) {
    observed.add(el)
  }
  unobserve(el) {
    observed.delete(el)
  }
  disconnect() {
    observed.clear()
  }
}

// Haqiqiy `useRoute()` kabi reaktiv — aks holda manzil kuzatuvchisi ishlamaydi.
const route = reactive({ fullPath: '/' })
vi.mock('vue-router', () => ({ useRoute: () => route }))

/** Element ekranning qayerida turishini boshqarish uchun. */
function place(el, { top, height = 100, width = 800 }) {
  el.getBoundingClientRect = () => ({
    top,
    bottom: top + height,
    left: 0,
    right: width,
    width,
    height,
  })
}

const Host = defineComponent({
  setup: () => useAutoReveal('#main'),
  render: () => h('div'),
})

/** `scan()` `requestAnimationFrame` ichida ishlaydi — uni kutib olamiz. */
async function settle() {
  await nextTick()
  await new Promise((resolve) => requestAnimationFrame(() => setTimeout(resolve, 0)))
  await nextTick()
}

describe('useAutoReveal', () => {
  beforeEach(() => {
    observed.clear()
    route.fullPath = '/'
    vi.stubGlobal('IntersectionObserver', FakeIntersectionObserver)
    window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} })
    Object.defineProperty(window, 'innerHeight', { value: 800, configurable: true })
    Object.defineProperty(window, 'innerWidth', { value: 1200, configurable: true })
    document.body.innerHTML = '<div id="main"><section id="a"></section></div>'
  })

  it('ekran ostidagi blokni kuzatuvga oladi', async () => {
    const block = document.querySelector('#a')
    place(block, { top: 900 })

    const wrapper = mount(Host, { attachTo: document.body })
    await settle()

    expect(block.classList.contains('reveal')).toBe(true)
    expect(observed.has(block)).toBe(true)
    wrapper.unmount()
  })

  it('manzil o‘zgargach hali ochilmagan blok kuzatuvsiz qolmaydi', async () => {
    const block = document.querySelector('#a')
    place(block, { top: 900 })

    const wrapper = mount(Host, { attachTo: document.body })
    await settle()
    expect(block.classList.contains('reveal')).toBe(true)

    // Til almashtirish: yo'l o'sha-o'sha, komponentlar mount holicha qoladi.
    route.fullPath = '/?lang=ru'
    await settle()

    // Bu blok hamon kuzatuvda — aks holda u abadiy ko'rinmas bo'lib qolardi.
    expect(observed.has(block)).toBe(true)
    wrapper.unmount()
  })

  it('manzil o‘zgargach ekrandan chiqib ketgan blok darhol ochiladi', async () => {
    const block = document.querySelector('#a')
    place(block, { top: 900 })

    const wrapper = mount(Host, { attachTo: document.body })
    await settle()
    expect(block.classList.contains('is-revealed')).toBe(false)

    // Foydalanuvchi `#anchor` orqali pastga sakradi — blok tepada qoldi.
    place(block, { top: -1200 })
    route.fullPath = '/#programma'
    await settle()

    expect(block.classList.contains('is-revealed')).toBe(true)
    wrapper.unmount()
  })

  it('qo‘lda `v-reveal` yozilgan elementga tegmaydi', async () => {
    const block = document.querySelector('#a')
    place(block, { top: 900 })
    // Direktiva o'z kuzatuvchisi va zaxira taymerini shu yerda saqlaydi.
    block._reveal = { observer: { disconnect() {} }, timer: 0 }

    const wrapper = mount(Host, { attachTo: document.body })
    await settle()

    expect(observed.has(block)).toBe(false)
    wrapper.unmount()
  })

  it('allaqachon ochilgan blokni qayta yashirmaydi', async () => {
    const block = document.querySelector('#a')
    place(block, { top: 900 })

    const wrapper = mount(Host, { attachTo: document.body })
    await settle()
    block.classList.add('is-revealed')

    route.fullPath = '/?lang=en'
    await settle()

    expect(block.classList.contains('is-revealed')).toBe(true)
    wrapper.unmount()
  })
})
