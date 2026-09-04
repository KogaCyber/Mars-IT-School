/**
 * Markazlashtirilgan HTTP klient.
 *
 * Xavfsizlik yechimlari:
 *  - access token faqat xotirada saqlanadi — XSS orqali o'g'irlash qiyinroq;
 *  - refresh token localStorage'da, chunki sahifa yangilanganda sessiya saqlanishi kerak;
 *  - 401 kelganda token bir marta yangilanadi va so'rov qayta yuboriladi
 *    (parallel so'rovlar bitta yangilashni kutadi).
 */
import axios from 'axios'

import { getContentVersion } from './contentVersion'

import { i18n } from '@/i18n'
import {
  DEFAULT_LANGUAGE,
  LANGUAGE_STORAGE_KEY,
  SUPPORTED_LANGUAGES,
  getLanguage,
  setLanguage,
} from '@/i18n/language'

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export const REFRESH_STORAGE_KEY = 'mars.refresh'

let accessToken = null
let refreshPromise = null
let onAuthFailure = null

export function setAccessToken(token) {
  accessToken = token
}

export function getRefreshToken() {
  try {
    return localStorage.getItem(REFRESH_STORAGE_KEY)
  } catch {
    return null
  }
}

export function setRefreshToken(token) {
  try {
    if (token) localStorage.setItem(REFRESH_STORAGE_KEY, token)
    else localStorage.removeItem(REFRESH_STORAGE_KEY)
  } catch {
    /* Shaxsiy rejimda localStorage bloklangan bo'lishi mumkin — jim o'tamiz. */
  }
}

/** Token yangilash butunlay muvaffaqiyatsiz bo'lganda chaqiriladi (logout). */
export function setAuthFailureHandler(handler) {
  onAuthFailure = handler
}

export const http = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  const isGet = (config.method || 'get').toLowerCase() === 'get'
  // Kontent versiyasi manzilga qo'shiladi — admin paneldagi o'zgarishdan keyin
  // brauzer/CDN keshidagi eski javob emas, yangisi olinadi (contentVersion.js).
  const version = getContentVersion()
  if (version && !config.skipVersion && isGet) {
    config.params = { ...config.params, _v: version }
  }
  // Sayt tili har bir so'rovga qo'shiladi — backend shu tildagi matnni qaytaradi.
  const language = getLanguage()
  if (language) {
    config.headers['Accept-Language'] = language
    // Til MANZILGA ham yoziladi (backend `?lang=` ni to'liq qo'llaydi:
    // `apps/core/translation.py:resolve_language`).
    //
    // Nega sarlavhaning o'zi yetmaydi: ochiq GET javoblari `Cache-Control:
    // public, max-age=...` bilan keladi (`apps/core/cache.py`). Til faqat
    // sarlavhada bo'lsa, uch tilning ham manzili bir xil bo'lib qoladi va
    // brauzer (hamda CDN) birinchi tildagi javobni keyingi tilga ham berib
    // yuboradi — til almashadi-yu, kontent eski tilda qolib ketadi. Faqat
    // sahifani yangilash yordam berardi, chunki qayta yuklashda brauzer
    // keshni chetlab o'tadi. Manzilda til bo'lsa, har bir til alohida
    // kesh yozuvi bo'ladi va bunday holat umuman yuzaga kelmaydi.
    if (isGet) config.params = { ...config.params, lang: language }
  }
  return config
})

async function refreshAccessToken() {
  const refresh = getRefreshToken()
  if (!refresh) return null

  try {
    // Interceptor'lardan xoli alohida so'rov — cheksiz sikl bo'lmasligi uchun.
    const { data } = await axios.post(
      `${BASE_URL}/api/v1/auth/token/refresh/`,
      { refresh },
      { timeout: 15000 },
    )
    accessToken = data.access
    if (data.refresh) setRefreshToken(data.refresh)
    return data.access
  } catch {
    setRefreshToken(null)
    accessToken = null
    return null
  }
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    if (status === 401 && original && !original._retried && getRefreshToken()) {
      original._retried = true
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      }

      const token = await refreshPromise
      if (token) {
        original.headers = { ...original.headers, Authorization: `Bearer ${token}` }
        return http.request(original)
      }
      if (onAuthFailure) onAuthFailure()
    }

    return Promise.reject(normalizeError(error))
  },
)

// --- Til ------------------------------------------------------------------
// Til holati `@/i18n/language` modulida; bu yerda mos keluvchi re-eksport.
export { DEFAULT_LANGUAGE, LANGUAGE_STORAGE_KEY, SUPPORTED_LANGUAGES, getLanguage, setLanguage }

/**
 * Axios xatoligini ilova ichidagi yagona formatga keltiradi.
 * @returns {import('@/types').ApiError}
 */
export function normalizeError(error) {
  const t = (key) => i18n.global.t(key)

  if (axios.isAxiosError(error)) {
    if (error.response) {
      return {
        detail: error.response.data?.detail || t('errors.server'),
        errors: error.response.data?.errors,
        status: error.response.status,
      }
    }
    if (error.code === 'ECONNABORTED') {
      return { detail: t('errors.timeout') }
    }
    return { detail: t('errors.network') }
  }
  // Interceptor allaqachon normallashtirgan bo'lishi mumkin.
  if (error && typeof error.detail === 'string') return error
  return { detail: t('errors.unexpected') }
}
