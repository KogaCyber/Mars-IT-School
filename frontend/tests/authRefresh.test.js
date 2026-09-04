/**
 * 401 → token yangilash → so'rovni qayta yuborish mantiqi.
 *
 * Bu saytdagi eng nozik mantiqlardan biri va u sinalmagan edi. Bu yerda
 * uchta tuzoq tekshiriladi:
 *   1. cheksiz sikl — yangilangan token bilan ham 401 kelsa;
 *   2. parallel so'rovlar — ular BITTA yangilashni kutishi kerak;
 *   3. yangilash muvaffaqiyatsiz tugasa — tozalash va logout chaqirig'i.
 */
import axios from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const store = new Map()

/** Node'da localStorage yo'q — har bir testda qayta o'rnatiladi, chunki
 *  `unstubAllGlobals()` uni ham o'chirib yuboradi. */
function stubStorage() {
  vi.stubGlobal('localStorage', {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
  })
}

vi.mock('axios', async () => {
  const actual = await vi.importActual('axios')
  return {
    ...actual,
    default: {
      ...actual.default,
      create: actual.default.create,
      post: vi.fn(),
      isAxiosError: actual.default.isAxiosError,
    },
  }
})

async function loadClient() {
  vi.resetModules()
  stubStorage()
  vi.stubGlobal('window', { location: { search: '' } })
  return import('@/api/client')
}

/** Javob interceptor'ining xato tarmog'ini qo'lda ishga tushiradi. */
function runResponseError(http, error) {
  return http.interceptors.response.handlers[0].rejected(error)
}

const unauthorized = (config = {}) => ({
  config: { headers: {}, url: '/leads/', ...config },
  response: { status: 401, data: {} },
  isAxiosError: true,
  toJSON: () => ({}),
})

describe('401 → token yangilash', () => {
  beforeEach(() => {
    store.clear()
    stubStorage()
    axios.post.mockReset()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('refresh token bo\'lmasa yangilashga urinmaydi', async () => {
    const { http } = await loadClient()

    await expect(runResponseError(http, unauthorized())).rejects.toBeTruthy()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('yangi token olingach so\'rov qayta yuboriladi', async () => {
    const { http, REFRESH_STORAGE_KEY } = await loadClient()
    store.set(REFRESH_STORAGE_KEY, 'eski-refresh')
    axios.post.mockResolvedValue({ data: { access: 'yangi-access' } })

    const request = vi.spyOn(http, 'request').mockResolvedValue({ data: 'ok' })
    const result = await runResponseError(http, unauthorized())

    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(result).toEqual({ data: 'ok' })
    expect(request.mock.calls[0][0].headers.Authorization).toBe('Bearer yangi-access')
  })

  it('qayta yuborilgan so\'rov yana 401 bersa — sikl to\'xtaydi', async () => {
    const { http, REFRESH_STORAGE_KEY } = await loadClient()
    store.set(REFRESH_STORAGE_KEY, 'eski-refresh')
    axios.post.mockResolvedValue({ data: { access: 'yangi-access' } })
    vi.spyOn(http, 'request').mockResolvedValue({ data: 'ok' })

    // Birinchi urinishdan keyin `_retried` qo'yiladi — ikkinchisida yangilash yo'q.
    await runResponseError(http, unauthorized())
    axios.post.mockClear()

    await expect(runResponseError(http, unauthorized({ _retried: true }))).rejects.toBeTruthy()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('parallel so\'rovlar bitta yangilashni kutadi', async () => {
    const { http, REFRESH_STORAGE_KEY } = await loadClient()
    store.set(REFRESH_STORAGE_KEY, 'eski-refresh')

    let release
    axios.post.mockReturnValue(
      new Promise((resolve) => {
        release = () => resolve({ data: { access: 'yangi-access' } })
      }),
    )
    vi.spyOn(http, 'request').mockResolvedValue({ data: 'ok' })

    const pending = [
      runResponseError(http, unauthorized({ url: '/a/' })),
      runResponseError(http, unauthorized({ url: '/b/' })),
      runResponseError(http, unauthorized({ url: '/c/' })),
    ]
    release()
    await Promise.all(pending)

    expect(axios.post).toHaveBeenCalledTimes(1)
  })

  it('yangilash muvaffaqiyatsiz — token tozalanadi va logout chaqiriladi', async () => {
    const { http, REFRESH_STORAGE_KEY, getRefreshToken, setAuthFailureHandler } =
      await loadClient()
    store.set(REFRESH_STORAGE_KEY, 'yaroqsiz-refresh')
    axios.post.mockRejectedValue(new Error('401'))

    const onFailure = vi.fn()
    setAuthFailureHandler(onFailure)

    await expect(runResponseError(http, unauthorized())).rejects.toBeTruthy()

    expect(onFailure).toHaveBeenCalledTimes(1)
    expect(getRefreshToken()).toBeNull()
  })

  it('401 bo\'lmagan xato yangilashni boshlamaydi', async () => {
    const { http, REFRESH_STORAGE_KEY } = await loadClient()
    store.set(REFRESH_STORAGE_KEY, 'eski-refresh')

    const serverError = {
      config: { headers: {} },
      response: { status: 500, data: { detail: 'Serverda xatolik' } },
      isAxiosError: true,
      toJSON: () => ({}),
    }
    await expect(runResponseError(http, serverError)).rejects.toMatchObject({
      detail: 'Serverda xatolik',
      status: 500,
    })
    expect(axios.post).not.toHaveBeenCalled()
  })
})
