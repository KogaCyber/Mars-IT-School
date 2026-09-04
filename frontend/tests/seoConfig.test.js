/**
 * hreflang manzillari.
 *
 * Regressiya qo'rig'i: ilgari uchala til BIR XIL URL'ni ko'rsatardi va bu
 * hreflang qoidasini buzardi — Google belgini e'tiborsiz qoldirib, saytdan
 * faqat bitta tilni indekslardi.
 */
import { describe, expect, it } from 'vitest'

import { SITE, localeAlternates, localeUrl } from '@/data/seoConfig'

const ORIGIN = 'https://marsitschool.uz'

describe('localeUrl', () => {
  it('asosiy til parametrsiz qoladi', () => {
    expect(localeUrl(ORIGIN, '/o-nas', SITE.defaultLocale)).toBe(`${ORIGIN}/o-nas`)
  })

  it('boshqa tillarga `?lang=` qo\'shadi', () => {
    expect(localeUrl(ORIGIN, '/o-nas', 'ru')).toBe(`${ORIGIN}/o-nas?lang=ru`)
    expect(localeUrl(ORIGIN, '/o-nas', 'en')).toBe(`${ORIGIN}/o-nas?lang=en`)
  })

  it('bosh sahifada ham to\'g\'ri ishlaydi', () => {
    expect(localeUrl(ORIGIN, '/', SITE.defaultLocale)).toBe(`${ORIGIN}/`)
    expect(localeUrl(ORIGIN, '/', 'ru')).toBe(`${ORIGIN}/?lang=ru`)
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
