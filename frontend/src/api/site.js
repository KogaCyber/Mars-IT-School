import { http } from './client'

export async function fetchSiteSettings() {
  const { data } = await http.get('/site-settings/')
  return data
}

export async function fetchAdvantages() {
  const { data } = await http.get('/advantages/')
  return data
}

export async function fetchParentReviews() {
  const { data } = await http.get('/reviews/')
  return data
}

export async function fetchFaqs() {
  const { data } = await http.get('/faqs/')
  return data
}

export async function fetchSpaceFeatures() {
  const { data } = await http.get('/space-features/')
  return data
}

export async function fetchStatistics() {
  const { data } = await http.get('/statistics/')
  return data
}

export async function fetchFounders() {
  const { data } = await http.get('/founders/')
  return data
}

/** «О нас» sahifasi bo'limlari. */
export async function fetchFutureBenefits() {
  const { data } = await http.get('/future-benefits/')
  return data
}

/** «Какие навыки развивает ребёнок» bo'limi. */
export async function fetchChildSkills() {
  const { data } = await http.get('/child-skills/')
  return data
}

export async function fetchProjectDefenceSteps() {
  const { data } = await http.get('/project-defence-steps/')
  return data
}

/** «MARS IT — это не просто курсы» ro'yxati. */
export async function fetchSchoolFeatures() {
  const { data } = await http.get('/school-features/')
  return data
}

/**
 * Bosh sahifa uchun barcha kontent — bitta so'rovda.
 *
 * Ilgari bosh sahifa 5–6 ta alohida so'rov yuborardi. Backend Railway'da,
 * MongoDB esa Atlas'da bo'lgani uchun har bir so'rov ~1 soniya turardi, ya'ni
 * kontent kechikib chiqardi. Endi bittasi yetadi.
 */
export async function fetchHome() {
  const { data } = await http.get('/home/')
  return data
}
