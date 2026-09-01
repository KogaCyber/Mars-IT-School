import { http } from './client'

export async function fetchNewsCategories() {
  const { data } = await http.get('/news-categories/')
  return data
}

/** @param {{page?: number, 'category__slug'?: string, is_featured?: boolean, search?: string}} params */
export async function fetchNews(params = {}) {
  const { data } = await http.get('/news/', { params })
  return data
}

export async function fetchNewsItem(slug) {
  const { data } = await http.get(`/news/${slug}/`)
  return data
}
