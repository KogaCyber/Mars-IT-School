/**
 * HTTP klientning til bilan ishlashi.
 *
 * Bu yerda saytdagi eng sezilarli xatolik qaytib kelmasligi tekshiriladi:
 * til almashsa ham kontent eski tilda qolib ketishi. Sabab — ochiq GET
 * javoblari `Cache-Control: public` bilan keladi, til esa faqat sarlavhada
 * bo'lsa uch tilning manzili bir xil bo'lib qolardi va brauzer keshdagi eski
 * tildagi javobni berardi. Shuning uchun til MANZILGA ham yoziladi.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'

async function loadClient(search = '') {
  vi.resetModules()
  vi.stubGlobal('window', { location: { search } })
  const client = await import('@/api/client')
  const language = await import('@/i18n/language')
  return { ...client, ...language }
}

/** So'rov interceptor'ini qo'lda ishga tushiradi. */
function runRequestInterceptor(http, config) {
  const handler = http.interceptors.request.handlers[0]
  return handler.fulfilled({ headers: {}, ...config })
}

describe("so'rov interceptor'i — til", () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it("GET so'roviga tilni sarlavha va manzil orqali qo'shadi", async () => {
    const { http } = await loadClient('?lang=ru')
    const config = runRequestInterceptor(http, { method: 'get' })

    expect(config.headers['Accept-Language']).toBe('ru')
    expect(config.params.lang).toBe('ru')
  })

  it('til almashgach yangi til yuboriladi', async () => {
    const { http, setLanguage } = await loadClient('?lang=ru')
    setLanguage('en')
    const config = runRequestInterceptor(http, { method: 'get' })

    expect(config.headers['Accept-Language']).toBe('en')
    expect(config.params.lang).toBe('en')
  })

  it("POST so'rovida manzilga hech narsa qo'shilmaydi", async () => {
    const { http } = await loadClient('?lang=en')
    const config = runRequestInterceptor(http, { method: 'post' })

    expect(config.headers['Accept-Language']).toBe('en')
    expect(config.params).toBeUndefined()
  })
})
