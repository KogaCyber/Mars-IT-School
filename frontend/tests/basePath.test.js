/**
 * Sayt yo'l prefiksi (`/maktab/`) bilan ham, domen ildizida ham ishlashi kerak.
 *
 * Nega alohida test: prefiks build vaqtida beriladi, ya'ni xato faqat
 * production build'da ko'rinadi — lokalda sayt doim ildizda ochiladi va
 * hamma narsa joyida ko'rinadi. Buzilganda esa ruscha va inglizcha sahifalar
 * (`/maktab/ru/kursy`) marshrutga tushmay, 404 bo'lib qoladi.
 *
 * Modul prefiksni import paytida BIR MARTA o'qiydi, shuning uchun har bir
 * holat alohida `vi.resetModules()` bilan qayta yuklanadi.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const OLD = process.env.VITE_BASE_PATH

async function load(basePath) {
  vi.resetModules()
  if (basePath === undefined) delete process.env.VITE_BASE_PATH
  else process.env.VITE_BASE_PATH = basePath
  const base = await import('@/data/basePath.js')
  const seo = await import('@/data/seoConfig.js')
  return { ...base, ...seo }
}

beforeEach(() => {
  delete process.env.VITE_BASE_PATH
})

afterEach(() => {
  if (OLD === undefined) delete process.env.VITE_BASE_PATH
  else process.env.VITE_BASE_PATH = OLD
  vi.resetModules()
})

describe('yo‘l prefiksi — domen ildizi', () => {
  it('prefiks bo‘lmasa manzillar o‘zgarmaydi', async () => {
    const { BASE_PATH, withBase, stripBase } = await load(undefined)
    expect(BASE_PATH).toBe('')
    expect(withBase('/kursy')).toBe('/kursy')
    expect(withBase('/')).toBe('/')
    expect(stripBase('/ru/kursy')).toBe('/ru/kursy')
  })

  it('til ildizda ham to‘g‘ri aniqlanadi', async () => {
    const { splitLocalePath } = await load(undefined)
    expect(splitLocalePath('/ru/kursy')).toEqual({ locale: 'ru', path: '/kursy' })
    expect(splitLocalePath('/kursy')).toEqual({ locale: 'uz', path: '/kursy' })
  })
})

describe('yo‘l prefiksi — sayt ichki yo‘lda', () => {
  it('prefiks normallashtiriladi (boshida `/`, oxirida yo‘q)', async () => {
    expect((await load('/maktab/')).BASE_PATH).toBe('/maktab')
    expect((await load('maktab')).BASE_PATH).toBe('/maktab')
    expect((await load('/')).BASE_PATH).toBe('')
  })

  it('brauzerga beriladigan manzilga prefiks qo‘shiladi', async () => {
    const { withBase, localePath } = await load('/maktab/')
    expect(withBase('/kursy')).toBe('/maktab/kursy')
    expect(withBase('/')).toBe('/maktab/')
    expect(withBase(localePath('/kursy', 'ru'))).toBe('/maktab/ru/kursy')
  })

  it('til prefiksdan KEYINGI bo‘lakdan o‘qiladi', async () => {
    const { splitLocalePath } = await load('/maktab/')
    expect(splitLocalePath('/maktab/ru/kursy')).toEqual({ locale: 'ru', path: '/kursy' })
    expect(splitLocalePath('/maktab/en')).toEqual({ locale: 'en', path: '/' })
    expect(splitLocalePath('/maktab/')).toEqual({ locale: 'uz', path: '/' })
    expect(splitLocalePath('/maktab')).toEqual({ locale: 'uz', path: '/' })
    // Prefiksning O'ZI ikki harfli bo'lsa ham til deb o'qilmasligi kerak.
    expect(splitLocalePath('/maktab/kursy/it-kids')).toEqual({
      locale: 'uz',
      path: '/kursy/it-kids',
    })
  })

  it('prefiksga mos kelmagan manzil kesilmaydi', async () => {
    const { stripBase } = await load('/maktab/')
    expect(stripBase('/boshqa/kursy')).toBe('/boshqa/kursy')
    // `/maktabxona` — prefiks emas, shunchaki shu harflardan boshlanadi.
    expect(stripBase('/maktabxona/kursy')).toBe('/maktabxona/kursy')
  })
})
