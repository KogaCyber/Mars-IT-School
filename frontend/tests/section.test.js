/**
 * Admin paneldan boshqariladigan bo'limlar.
 *
 * Asosiy talab: panelda matn kiritilmagan (yoki backend javob bermagan)
 * joyda sayt bo'sh sarlavha ko'rsatmasligi, maketdagi tarjimaga qaytishi
 * kerak — aks holda kontent to'ldirilmagan bo'lim saytda bo'sh chiziq
 * bo'lib qolardi.
 */
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

// `useSection` tarjimani `useI18n()` orqali oladi — testda uni maketdagi
// matnlar bilan almashtiramiz.
vi.mock('vue-i18n', async () => {
  const actual = await vi.importActual('vue-i18n')
  const i18n = actual.createI18n({
    legacy: false,
    locale: 'ru',
    messages: {
      ru: { home: { heroTitle: 'Учимся создавать будущее', heroText: 'Описание' } },
    },
  })
  return { ...actual, useI18n: () => i18n.global }
})

const { toCards, useSection, useSectionVisible } = await import('@/composables/useSection')
const { useContentStore } = await import('@/stores/content')

describe('useSection', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('admin paneldagi matnni qaytaradi', () => {
    useContentStore().merge({ 'home.hero': { title: 'Yangi sarlavha', items: [] } })

    const section = useSection('home.hero', { title: 'home.heroTitle' })

    expect(section.value.title).toBe('Yangi sarlavha')
  })

  it("bo'sh maydonda maketdagi tarjimaga qaytadi", () => {
    useContentStore().merge({ 'home.hero': { title: '', items: [] } })

    const section = useSection('home.hero', { title: 'home.heroTitle', text: 'home.heroText' })

    expect(section.value.title).toBe('Учимся создавать будущее')
    expect(section.value.text).toBe('Описание')
  })

  it("bo'lim umuman yuklanmagan bo'lsa ham ishlaydi", () => {
    const section = useSection('home.hero', { title: 'home.heroTitle' })

    expect(section.value.title).toBe('Учимся создавать будущее')
    expect(section.value.items).toEqual([])
    expect(section.value.image).toBeNull()
  })

  it("admin panelda o'chirilgan bo'lim ko'rinmaydi", () => {
    useContentStore().merge({ 'home.hero': { is_published: false, items: [] } })

    const section = useSection('home.hero', { title: 'home.heroTitle' })

    expect(section.value.visible).toBe(false)
    expect(useSectionVisible('home.hero').value).toBe(false)
  })

  it("yoqilgan (yoki hali yuklanmagan) bo'lim ko'rinadi", () => {
    useContentStore().merge({ 'home.hero': { is_published: true, items: [] } })

    expect(useSection('home.hero').value.visible).toBe(true)
    expect(useSectionVisible('home.hero').value).toBe(true)
    // Yuklanmagan bo'lim — maketdagi ko'rinish saqlanadi.
    expect(useSectionVisible('home.faq').value).toBe(true)
  })

  it("sarlavhani qatorlarga ajratadi (maketda ko'p qatorli)", () => {
    useContentStore().merge({ 'home.hero': { title: 'Birinchi\nIkkinchi', items: [] } })

    const section = useSection('home.hero')

    expect(section.value.titleLines).toEqual(['Birinchi', 'Ikkinchi'])
  })
})

describe('toCards', () => {
  const fallback = [
    { id: 'a', title: 'Maket', description: 'Maket matni', icon: 'book' },
    { id: 'b', title: 'Ikkinchi', description: '', icon: 'code' },
  ]

  it("element qo'shilmagan bo'lsa maketdagi ro'yxatni qaytaradi", () => {
    expect(toCards([], fallback)).toBe(fallback)
  })

  it('admin paneldagi kartochkalarni afzal ko\'radi', () => {
    const cards = toCards([{ title: 'Yangi', text: 'Matn', icon_name: 'feed' }], fallback)

    expect(cards).toHaveLength(1)
    expect(cards[0]).toMatchObject({ title: 'Yangi', description: 'Matn', icon: 'feed' })
  })

  it("ikonka ko'rsatilmasa maketdagi ikonka qoladi", () => {
    const cards = toCards([{ title: 'Yangi' }], fallback)

    expect(cards[0].icon).toBe('book')
  })
})
