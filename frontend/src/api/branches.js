import { http } from './client'

export async function fetchBranches() {
  const { data } = await http.get('/branches/')
  return data
}

export async function fetchBranch(slug) {
  const { data } = await http.get(`/branches/${slug}/`)
  return data
}
