/**
 * hreflang manzillari.
 *
 * Regressiya qo'rig'i: ilgari uchala til BIR XIL URL'ni ko'rsatardi va bu
 * hreflang qoidasini buzardi — Google belgini e'tiborsiz qoldirib, saytdan
 * faqat bitta tilni indekslardi.
 */
import { describe, expect, it } from 'vitest'

import { SITE, localeAlternates, localePath, localeUrl, splitLocalePath } from '@/data/seoConfig'

const ORIGIN = 'https://marsitschool.uz'

describe('localeUrl', () => {
  it('asosiy til parametrsiz qoladi', () => {
    expect(localeUrl(ORIGIN, '/o-nas', SITE.defaultLocale)).toBe(`${ORIGIN}/o-nas`)
  })

  it("boshqa tillar YO'L PREFIKSI bilan beriladi", () => {
    // So'rov parametri emas, aynan prefiks: statik hostingda faqat shunday
    // qilib har bir tilga o'z HTML fayli beriladi (JS ishlatmaydigan
    // robotlar uchun bu yagona yo'l).
    expect(localeUrl(ORIGIN, '/o-nas', 'ru')).toBe(`${ORIGIN}/ru/o-nas`)
    expect(localeUrl(ORIGIN, '/o-nas', 'en')).toBe(`${ORIGIN}/en/o-nas`)
  })

  it("bosh sahifada ham to'g'ri ishlaydi", () => {
    expect(localeUrl(ORIGIN, '/', SITE.defaultLocale)).toBe(`${ORIGIN}/`)
    expect(localeUrl(ORIGIN, '/', 'ru')).toBe(`${ORIGIN}/ru`)
  })

  it('noma\'lum til asosiy tilga tushadi', () => {
    expect(localeUrl(ORIGIN, '/kursy', 'de')).toBe(`${ORIGIN}/kursy`)
  })
})

describe('splitLocalePath', () => {
  it('prefiksni ajratadi', () => {
    expect(splitLocalePath('/ru/kursy')).toEqual({ locale: 'ru', path: '/kursy' })
    expect(splitLocalePath('/en')).toEqual({ locale: 'en', path: '/' })
  })

  it('prefikssiz manzil asosiy tilda qoladi', () => {
    expect(splitLocalePath('/kursy')).toEqual({ locale: SITE.defaultLocale, path: '/kursy' })
  })

  it("til kodiga o'xshash slug'ni prefiks deb o'ylamaydi", () => {
    // `/uz` asosiy til — prefiks emas; boshqa ikki harfli bo'lak ham emas.
    expect(splitLocalePath('/kursy/it-kids')).toEqual({
      locale: SITE.defaultLocale,
      path: '/kursy/it-kids',
    })
  })

  it('localePath bilan teskari amal bajariladi', () => {
    for (const locale of SITE.locales) {
      const full = localePath('/kontakty', locale)
      expect(splitLocalePath(full)).toEqual({ locale, path: '/kontakty' })
    }
  })
})

describe('localeAlternates', () => {
  const alternates = localeAlternates(ORIGIN, '/kursy')

  it('har bir til uchun bitta yozuv va x-default beradi', () => {
    expect(alternates.map((item) => item.hreflang)).toEqual([...SITE.locales, 'x-default'])
  })

  it('tillarning manzillari BIR-BIRIDAN FARQ QILADI', () => {
    const perLocale = alternates.filter((item) => item.hreflang !== 'x-default')
    const unique = new Set(perLocale.map((item) => item.href))
    expect(unique.size).toBe(perLocale.length)
  })

  it('x-default asosiy tilga ishora qiladi', () => {
    const xDefault = alternates.find((item) => item.hreflang === 'x-default')
    expect(xDefault.href).toBe(localeUrl(ORIGIN, '/kursy', SITE.defaultLocale))
  })
})
