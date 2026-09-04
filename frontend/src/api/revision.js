import { http } from './client'

/**
 * Kontentning joriy versiyasi. Admin panelda biror narsa o'zgarsa raqam
 * o'sadi — sayt shuni kuzatib, kontentni o'zi yangilaydi.
 */
export async function fetchRevision() {
  const { data } = await http.get('/revision/', { skipVersion: true })
  return Number(data?.revision) || 0
}
