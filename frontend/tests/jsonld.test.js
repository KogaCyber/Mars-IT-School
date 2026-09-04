/**
 * JSON-LD ni HTML ichiga yozish.
 *
 * Regressiya qo'rig'i: admin paneldagi matnda `</script>` bo'lsa (kurs nomi,
 * yangilik sarlavhasi, FAQ javobi…) u prerender qilingan HTML'da script
 * tegini erta yopib, undan keyingi hamma narsani bajariladigan HTML'ga
 * aylantirardi — ya'ni kontent muharriri huquqi doimiy XSS'ga aylanardi.
 */
import { describe, expect, it } from 'vitest'

import { jsonLdScriptContent } from '@/utils/schema'

const CLOSE = `</${'script'}>`

describe('jsonLdScriptContent', () => {
  it("script tegini erta yopishga yo'l qo'ymaydi", () => {
    const evil = { name: `Kurs${CLOSE}<img src=x onerror=alert(1)>` }
    const out = jsonLdScriptContent(evil)

    expect(out.toLowerCase()).not.toContain(CLOSE)
    expect(out).not.toContain('<')
    expect(out).not.toContain('>')
  })

  it("ma'nosini o'zgartirmaydi — JSON baribir bir xil o'qiladi", () => {
    const graph = { name: `A${CLOSE}B`, url: 'https://a.uz/?x=1&y=2' }
    expect(JSON.parse(jsonLdScriptContent(graph))).toEqual(graph)
  })

  it('& belgisini ham qochiradi (HTML mavjudotlariga aylanmasin)', () => {
    expect(jsonLdScriptContent({ q: 'a&amp;b' })).not.toContain('&')
  })

  it('U+2028/U+2029 ni qochiradi', () => {
    const out = jsonLdScriptContent({ text: 'a b c' })
    expect(out).not.toContain(' ')
    expect(out).not.toContain(' ')
    expect(JSON.parse(out).text).toBe('a b c')
  })

  it('oddiy kontentni buzmaydi', () => {
    const graph = { '@context': 'https://schema.org', name: 'MARS IT School' }
    expect(JSON.parse(jsonLdScriptContent(graph))).toEqual(graph)
  })
})

/**
 * Sxemalardagi domen.
 *
 * Regressiya qo'rig'i: canonical bitta domenni, JSON-LD ichidagi `@id`/`url`
 * esa fayldagi qattiq yozilgan boshqa domenni ko'rsatardi — qidiruv tizimi
 * uchun bu ikki xil sayt edi.
 */
describe('setSchemaOrigin', () => {
  it('barcha absolyut manzillar bitta domendan quriladi', async () => {
    const { absoluteUrl, organizationSchema, setSchemaOrigin, websiteSchema } =
      await import('@/utils/schema')
    const origin = 'https://example-deploy.uz'
    setSchemaOrigin(origin)

    expect(absoluteUrl('/logo.png')).toBe(`${origin}/logo.png`)
    expect(organizationSchema()['@id']).toBe(`${origin}/#organization`)
    expect(organizationSchema().url).toBe(origin)
    expect(websiteSchema()['@id']).toBe(`${origin}/#website`)
  })

  it("bo'sh qiymatni e'tiborsiz qoldiradi", async () => {
    const { absoluteUrl, setSchemaOrigin } = await import('@/utils/schema')
    setSchemaOrigin('https://keep.uz')
    setSchemaOrigin('')
    expect(absoluteUrl('/a')).toBe('https://keep.uz/a')
  })
})
