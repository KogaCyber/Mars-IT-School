import { http } from './client'

/**
 * Ariza yuborish (bosh sahifa, kurs sahifasi, kontaktlar formasi).
 * @param {{full_name: string, phone: string, course?: string|null, branch?: string|null,
 *          child_age?: number|null, comment?: string, source: string, website?: string}} payload
 * @returns {Promise<string>} foydalanuvchiga ko'rsatiladigan xabar
 */
export async function submitLead(payload) {
  const { data } = await http.post('/leads/', payload)
  return data.detail
}
