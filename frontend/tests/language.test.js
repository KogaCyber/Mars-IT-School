/**
 * Til holati.
 *
 * Bu yerda qaytib kelmasligi kerak bo'lgan xatolik tekshiriladi: manzildagi
 * `?lang=` parametri BOSHLANG'ICH tilni beradi, lekin foydalanuvchi tilni
 * almashtirgach ustunlikni yo'qotishi shart. Aks holda HTTP klient har bir
 * so'rovda yana manzildagi tilni yuborardi — interfeys tarjima bo'lardi-yu,
 * backend kontenti eski tilda qolardi.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'

/** Har bir test uchun modulni toza holatda (manzil bilan) yuklaydi. */
async function loadLanguageModule(search = '') {
  vi.resetModules()
  vi.stubGlobal('window', { location: { search } })
  return import('@/i18n/language')
}

describe('getLanguage', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it("manzildagi ?lang= ni boshlang'ich til sifatida oladi", async () => {
    const { getLanguage } = await loadLanguageModule('?lang=ru')
    expect(getLanguage()).toBe('ru')
  })

  it("noma'lum til e'tiborsiz qoldiriladi", async () => {
    const { getLanguage, DEFAULT_LANGUAGE } = await loadLanguageModule('?lang=de')
    expect(getLanguage()).toBe(DEFAULT_LANGUAGE)
  })

  it('tanlangan til manzildagi ?lang= dan ustun turadi', async () => {
    const { getLanguage, setLanguage } = await loadLanguageModule('?lang=ru')
    expect(getLanguage()).toBe('ru')

    setLanguage('en')
    expect(getLanguage()).toBe('en')
  })

  it("qo'llab-quvvatlanmaydigan tilga o'tmaydi", async () => {
    const { getLanguage, setLanguage } = await loadLanguageModule('?lang=en')
    setLanguage('fr')
    expect(getLanguage()).toBe('en')
  })
})
