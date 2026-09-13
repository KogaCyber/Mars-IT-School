/**
 * Muharrir API — faqat kirgan xodim uchun. Sessiya cookie'da (same-origin),
 * shuning uchun alohida klient: `/api/` (v1 emas) va `withCredentials`.
 */
import axios from 'axios'

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export const editorHttp = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 20000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

/** Kirgan xodim yoki `null` (401 — oddiy holat, xato emas). */
export async function fetchMe() {
  try {
    const { data } = await editorHttp.get('/auth/me')
    return data
  } catch (error) {
    if (error.response?.status === 401) return null
    throw error
  }
}

/** Mars ID orqali kirish — to'liq o'tish (redirect). */
export function loginUrl(next) {
  const params = new URLSearchParams({ next: next || '/' })
  return `${BASE_URL}/api/auth/login?${params}`
}

export async function logout() {
  await editorHttp.post('/auth/logout')
}

export async function fetchPages() {
  const { data } = await editorHttp.get('/editor/pages')
  return data
}

export async function fetchSection(key) {
  const { data } = await editorHttp.get(`/editor/sections/${key}`)
  return data
}

export async function patchSection(key, payload) {
  const { data } = await editorHttp.patch(`/editor/sections/${key}`, payload)
  return data
}

export async function uploadImage(file, folder = 'sections') {
  const form = new FormData()
  form.append('file', file)
  const { data } = await editorHttp.post(`/editor/upload?folder=${folder}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

// --- Mavjudotlar (filial, yangilik, vakansiya) va kontaktlar ---

export async function fetchEntities(kind) {
  const { data } = await editorHttp.get(`/editor/entities/${kind}`)
  return data
}

export async function createEntity(kind, values, isPublished) {
  const { data } = await editorHttp.post(`/editor/entities/${kind}`, {
    values,
    is_published: isPublished,
  })
  return data
}

export async function updateEntity(kind, id, values, isPublished) {
  const { data } = await editorHttp.patch(`/editor/entities/${kind}/${id}`, {
    values,
    is_published: isPublished,
  })
  return data
}

export async function deleteEntity(kind, id) {
  await editorHttp.delete(`/editor/entities/${kind}/${id}`)
}

export async function fetchSettings() {
  const { data } = await editorHttp.get('/editor/site-settings')
  return data
}

export async function patchSettings(values) {
  const { data } = await editorHttp.patch('/editor/site-settings', { values })
  return data
}
