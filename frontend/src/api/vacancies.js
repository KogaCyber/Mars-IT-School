import { http } from './client'

export async function fetchVacancies() {
  const { data } = await http.get('/vacancies/')
  return data
}

export async function fetchVacancy(slug) {
  const { data } = await http.get(`/vacancies/${slug}/`)
  return data
}

/**
 * Vakansiyaga ariza yuborish (rezyume fayli bilan).
 * @param {{vacancy: string, full_name: string, phone: string, email?: string,
 *          cover_letter?: string, resume?: File, website?: string}} payload
 */
export async function submitVacancyApplication(payload) {
  const form = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') form.append(key, value)
  })

  const { data } = await http.post('/vacancy-applications/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.detail
}
