/**
 * `robots.txt` va marshrut sozlamalarining regressiya qo'rig'i.
 *
 * Ikkala qoida ham «ko'zga tashlanmaydigan» turkumdan: fayl to'g'ri
 * ko'rinadi, brauzerda hammasi ishlaydi, lekin qidiruv tizimi butunlay
 * boshqa narsani o'qiydi. Shuning uchun ular test bilan mahkamlangan.
 */
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import vercelConfig from '../vercel.json'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const robots = readFileSync(join(ROOT, 'public/robots.txt'), 'utf8')

/** `robots.txt` ni guruhlarga ajratadi: ketma-ket `User-agent` qatorlari — bitta guruh. */
function parseGroups(text) {
  const groups = []
  let current = null
  for (const raw of text.split('\n')) {
    const line = raw.replace(/#.*$/, '').trim()
    if (!line) continue
    const [key, ...rest] = line.split(':')
    const field = key.trim().toLowerCase()
    const value = rest.join(':').trim()
    if (field === 'user-agent') {
      // Yangi guruh faqat qoidalar boshlanganidan keyin ochiladi: ketma-ket
      // yozilgan `User-agent` qatorlari BITTA guruhga tegishli.
      if (!current || current.rules.length) {
        current = { agents: [], rules: [] }
        groups.push(current)
      }
      current.agents.push(value)
    } else if (current && (field === 'allow' || field === 'disallow')) {
      current.rules.push(`${field}:${value}`)
    }
  }
  return groups
}

describe('robots.txt', () => {
  const groups = parseGroups(robots)

  it('kamida bitta guruh va sitemap havolasi bor', () => {
    expect(groups.length).toBeGreaterThan(0)
    expect(robots).toMatch(/^Sitemap:\s*https?:\/\/\S+\/sitemap\.xml$/m)
  })

  /**
   * Robot FAQAT o'ziga eng mos keladigan BITTA guruhga bo'ysunadi. Ilgari
   * `User-agent: Googlebot` guruhida faqat `Allow: /` turardi, ya'ni
   * `User-agent: *` dagi UTM cheklovlari Googlebot uchun ishlamasdi; GPTBot
   * va ClaudeBot esa har bir o'quvchining shaxsiy test natijasini
   * (`/test/rezultat/`) ham indekslashi mumkin edi.
   */
  it('har bir guruh maxfiy va dublikat manzillarni yopadi', () => {
    const required = [
      'disallow:/test/rezultat/',
      'disallow:/*?*utm_',
      'disallow:/*?*fbclid=',
      'disallow:/*?*gclid=',
    ]
    for (const group of groups) {
      for (const rule of required) {
        expect(group.rules, `${group.agents.join(', ')} — ${rule} yo'q`).toContain(rule)
      }
    }
  })

  it('javob beruvchi (AI) tizimlarga ruxsat berilgan', () => {
    const allowed = new Set(groups.flatMap((group) => group.agents))
    for (const bot of ['GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended']) {
      expect(allowed, `${bot} ro'yxatda yo'q`).toContain(bot)
    }
  })
})

describe('vercel rewrites', () => {
  /**
   * «Hammasini ushlaydigan» rewrite mavjud bo'lmagan manzilga ham 200 va bosh
   * sahifa HTML'ini qaytarardi («soft 404»): qidiruv tizimi uchun bu cheksiz
   * sondagi dublikat sahifa. Endi rewrite faqat ma'lum bo'limlarga tegishli,
   * qolgani `dist/404.html` ga tushadi va haqiqiy 404 oladi.
   */
  it('hamma narsani ushlaydigan rewrite yo‘q', () => {
    for (const rule of vercelConfig.rewrites || []) {
      expect(rule.source, `juda keng rewrite: ${rule.source}`).toMatch(
        /kursy|novosti|kontakty|test/,
      )
    }
  })

  it('dinamik bo‘limlar uchun rewrite bor (build paytida yo‘q kontent 404 bermasin)', () => {
    const sources = (vercelConfig.rewrites || []).map((rule) => rule.source).join(' ')
    for (const section of ['kursy', 'novosti', 'kontakty', 'test']) {
      expect(sources).toContain(section)
    }
  })
})
