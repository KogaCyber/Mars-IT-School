import { http } from './client'

/** Proforientatsiya testi: savollar va variantlar. */
export async function fetchQuiz(slug) {
  const { data } = await http.get(`/quizzes/${slug}/`)
  return data
}

/**
 * Javoblarni yuborib natijani olish.
 * @param {string} slug
 * @param {{answers: Object.<string, string>, full_name?: string, phone?: string}} payload
 */
export async function submitQuiz(slug, payload) {
  const { data } = await http.post(`/quizzes/${slug}/submit/`, payload)
  return data
}

/** Natijani havola orqali qayta ochish. */
export async function fetchQuizResult(id) {
  const { data } = await http.get(`/quiz-results/${id}/`)
  return data
}
