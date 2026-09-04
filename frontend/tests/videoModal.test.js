/**
 * Video manbalarini tanish.
 *
 * Bu yerda CSP bilan bog'liq xatolik qaytib kelmasligi tekshiriladi: ichki
 * pleyer FAQAT `frame-src` ruxsat bergan manbalarni ochishi kerak, aks holda
 * modal ochilib ichida hech nima ko'rinmasdi.
 */
import { describe, expect, it } from 'vitest'

import { isPlayable, resolveVideo } from '@/composables/useVideoModal'

describe('resolveVideo — YouTube', () => {
  it('havolaning barcha ko\'rinishlarini taniydi', () => {
    const links = [
      'https://youtu.be/dQw4w9WgXcQ',
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      'https://www.youtube.com/embed/dQw4w9WgXcQ',
      'https://www.youtube.com/shorts/dQw4w9WgXcQ',
    ]
    for (const link of links) {
      const result = resolveVideo(link)
      expect(result.kind).toBe('embed')
      expect(result.src).toContain('youtube-nocookie.com/embed/dQw4w9WgXcQ')
    }
  })

  it('boshlanish vaqtini saqlaydi', () => {
    expect(resolveVideo('https://youtu.be/dQw4w9WgXcQ?t=90').src).toContain('start=90')
  })
})

describe('resolveVideo — Vimeo va fayllar', () => {
  it('Vimeo pleyeriga o\'tkazadi', () => {
    expect(resolveVideo('https://vimeo.com/123456').src).toContain('player.vimeo.com/video/123456')
  })

  it('to\'g\'ridan-to\'g\'ri video faylni `video` tegida ochadi', () => {
    const result = resolveVideo('https://cdn.example.com/promo.mp4')
    expect(result).toEqual({ kind: 'file', src: 'https://cdn.example.com/promo.mp4' })
  })
})

describe('resolveVideo — noma\'lum manba', () => {
  it('CSP ruxsat bermaydigan havolani ochmaydi', () => {
    // Ilgari bu `{kind:"embed"}` qaytarardi va productionda CSP uni bloklardi:
    // foydalanuvchi bo'sh qora modalni ko'rardi.
    expect(resolveVideo('https://rutube.ru/video/abc/')).toBeNull()
    expect(isPlayable('https://rutube.ru/video/abc/')).toBe(false)
  })

  it('bo\'sh havolani rad etadi', () => {
    expect(resolveVideo('')).toBeNull()
    expect(resolveVideo(null)).toBeNull()
    expect(isPlayable('')).toBe(false)
  })
})
