import { http } from './client'

/** Kurs yo'nalishlari (IT Kids, Programmirovaniye va h.k.). */
export async function fetchDirections() {
  const { data } = await http.get('/directions/')
  return data
}

/**
 * Kurslar ro'yxati.
 * @param {{direction?: string, age?: number, is_featured?: boolean, search?: string}} params
 */
export async function fetchCourses(params = {}) {
  const { data } = await http.get('/courses/', { params })
  return data
}

/** Bitta kurs sahifasi. */
export async function fetchCourse(slug) {
  const { data } = await http.get(`/courses/${slug}/`)
  return data
}
