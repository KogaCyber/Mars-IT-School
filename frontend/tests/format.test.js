/** Telefon va sana formatlash — formalar aynan shu funksiyalarga tayanadi. */
import { describe, expect, it } from 'vitest'

import { formatDate, formatPhone, formatPrice, isValidPhone, toPhonePayload } from '@/utils/format'

describe('formatPhone', () => {
  it("raqamni +998 90 123 45 67 ko'rinishiga keltiradi", () => {
    expect(formatPhone('901234567')).toBe('+998 90 123 45 67')
    expect(formatPhone('+998901234567')).toBe('+998 90 123 45 67')
    expect(formatPhone('998 90 123-45-67')).toBe('+998 90 123 45 67')
  })

  it("yozilayotgan paytdagi chala raqamni ham chiroyli ko'rsatadi", () => {
    expect(formatPhone('90')).toBe('+998 90')
    expect(formatPhone('9012')).toBe('+998 90 12')
  })

  it("9 ta raqamdan ortig'ini qabul qilmaydi", () => {
    expect(formatPhone('9012345678888')).toBe('+998 90 123 45 67')
  })

  it("bo'sh qiymatda ham buzilmaydi", () => {
    expect(formatPhone('')).toBe('+998')
    expect(formatPhone(null)).toBe('+998')
  })
})

describe('toPhonePayload va isValidPhone', () => {
  it('serverga +998XXXXXXXXX yuboradi', () => {
    expect(toPhonePayload('+998 90 123 45 67')).toBe('+998901234567')
  })

  it("to'liq raqamni haqiqiy deb biladi", () => {
    expect(isValidPhone('+998 90 123 45 67')).toBe(true)
  })

  it('chala raqamni rad etadi', () => {
    expect(isValidPhone('+998 90 123')).toBe(false)
    expect(isValidPhone('')).toBe(false)
  })
})

describe('formatPrice', () => {
  it('sonni ajratib yozadi', () => {
    // `Intl` ajratgich sifatida uzilmas bo'shliq ishlatadi — solishtirishdan
    // oldin barcha bo'shliq turlarini bir xillashtiramiz.
    expect(formatPrice(800000).replace(/\s/gu, ' ')).toBe('800 000')
  })

  it("noma'lum qiymatga tire qaytaradi", () => {
    expect(formatPrice(null)).toBe('—')
    expect(formatPrice('salom')).toBe('—')
  })
})

describe('formatDate — til', () => {
  it('sanani sayt tilida yozadi', () => {
    expect(formatDate('2026-09-04', 'ru')).toContain('сентября')
    expect(formatDate('2026-09-04', 'en')).toContain('September')
    expect(formatDate('2026-09-04', 'uz')).toContain('sentabr')
  })

  it("xato sanada bo'sh satr qaytaradi", () => {
    expect(formatDate('salom', 'uz')).toBe('')
  })
})
