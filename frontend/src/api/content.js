import { http } from './client'

/**
 * Sahifa bo'limlarining matni va rasmlari (admin panelda tahrirlanadi).
 *
 * Javob — `{"home.hero": {...}, "itkids.stages": {...}}` ko'rinishida:
 * bo'limlar soni oz va hajmi kichik, shuning uchun sayt ochilganda hammasi
 * bitta so'rovda olinadi va keyingi sahifalarga o'tishda qayta so'ralmaydi.
 */
export async function fetchContent() {
  const { data } = await http.get('/content/')
  return data
}
