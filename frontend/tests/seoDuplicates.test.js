/**
 * SEO dublikatlari.
 *
 * Regressiya qo'rig'i: admin paneldagi kurs slug'i (`programmirovanie`) va
 * qo'lda yasalgan sahifa (`it-razrabotka`) BITTA kursni ikkita manzilda
 * ko'rsatardi. Router uni ilova ichida yo'naltirsa-da, prerender qilingan
 * HTML har ikkala manzilda ham 200 bilan berilar va O'ZIGA canonical
 * qo'yardi — ya'ni qidiruv tizimi ikkita alohida sahifa ko'rar, reyting esa
 * ikkiga bo'linardi.
 */
import { describe, expect, it } from 'vitest'

import vercelConfig from '../vercel.json'
import { COURSE_ALIASES, COURSE_ROUTES } from '@/data/courseAliases'
import { SITE, STATIC_PAGES } from '@/data/seoConfig'

describe('kurs aliaslari', () => {
  it('har bir alias haqiqiy sahifasi bor kursga ishora qiladi', () => {
    for (const target of Object.values(COURSE_ALIASES)) {
      expect(COURSE_ROUTES[target]).toBeTruthy()
      expect(STATIC_PAGES.some((page) => page.path === `/kursy/${target}`)).toBe(true)
    }
  })

  it("alias slug'ining O'ZI statik sahifa sifatida e'lon qilinmagan", () => {
    for (const alias of Object.keys(COURSE_ALIASES)) {
      expect(STATIC_PAGES.some((page) => page.path === `/kursy/${alias}`)).toBe(false)
    }
  })

  it('har bir alias uchun serverda 301 yo‘naltirish bor', () => {
    // Yo'naltirish AYNAN serverda bo'lishi kerak: prerender qilingan sahifa
    // ilova yuklanmasdan turib beriladi, ya'ni faqat router yo'naltirishi
    // qidiruv robotiga yetib bormaydi.
    for (const [alias, target] of Object.entries(COURSE_ALIASES)) {
      const redirect = vercelConfig.redirects?.find((item) => item.source === `/kursy/${alias}`)
      expect(redirect, `/kursy/${alias} uchun redirect yo'q`).toBeTruthy()
      expect(redirect.destination).toBe(`/kursy/${target}`)
      expect(redirect.permanent).toBe(true)
    }
  })
})

describe('statik sahifalar', () => {
  it('yo‘llar takrorlanmaydi', () => {
    const paths = STATIC_PAGES.map((page) => page.path)
    expect(new Set(paths).size).toBe(paths.length)
  })

  it('har bir sahifada uchala til uchun ham matn bor', () => {
    for (const page of STATIC_PAGES) {
      for (const field of ['title', 'description', 'summary', 'keywords']) {
        for (const locale of ['uz', 'ru', 'en']) {
          expect(page[field]?.[locale], `${page.path}.${field}.${locale}`).toBeTruthy()
        }
      }
    }
  })

  it("sarlavha qidiruv natijasiga sig'adi (brend bilan ≤ 70 belgi)", () => {
    // `useSeo` sarlavhaga `— MARS IT School` qo'shadi; Google esa ~60–65
    // belgidan keyin kesadi.
    for (const page of STATIC_PAGES) {
      for (const locale of ['uz', 'ru', 'en']) {
        const full = `${page.title[locale]} — ${SITE.name}`
        expect(full.length, `${page.path} [${locale}]: ${full}`).toBeLessThanOrEqual(70)
      }
    }
  })

  it("tavsif qidiruv natijasiga sig'adi (≤ 160 belgi)", () => {
    // 160 — `useSeo.js:trim()` va `generate-seo.mjs:trimDescription()` dagi
    // chegara. Manbadagi matn undan uzun bo'lsa ikkalasi ham uni «…» bilan
    // kesadi, ya'ni tavsif yarim gapda uzilib qolardi.
    for (const page of STATIC_PAGES) {
      for (const locale of ['uz', 'ru', 'en']) {
        expect(page.description[locale].length, `${page.path} [${locale}]`).toBeLessThanOrEqual(160)
      }
    }
  })
})
