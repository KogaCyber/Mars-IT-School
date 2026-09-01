import { http } from './client'

export async function fetchTeachers(params = {}) {
  const { data } = await http.get('/teachers/', { params })
  return data
}

export async function fetchTeacher(slug) {
  const { data } = await http.get(`/teachers/${slug}/`)
  return data
}
