/**
 * Yordamchi javob berish uchun foydalanadigan sayt ma'lumotlari.
 *
 * Chat birinchi marta ochilganda filiallar, kurslar, o'qituvchilar, yangiliklar
 * va vakansiyalar bir marta yuklanadi va til bo'yicha eslab qolinadi (API
 * matnlarni `Accept-Language` ga qarab qaytaradi). Shu tufayli javoblarda
 * haqiqiy raqamlar turadi: nechta filial bor, qaysi manzilda, narxi qancha.
 *
 * Biror so'rov yiqilsa — ro'yxat bo'sh qoladi va yordamchi shu bo'lim bo'yicha
 * statik javobga qaytadi, ya'ni chat baribir ishlaydi.
 */
import { fetchBranches } from '@/api/branches'
import { fetchCourses } from '@/api/courses'
import { fetchNews } from '@/api/news'
import { fetchTeachers } from '@/api/teachers'
import { fetchVacancies } from '@/api/vacancies'

/** Sahifalangan javob ham, oddiy massiv ham bir xil qaytsin. */
function toList(payload) {
  if (Array.isArray(payload)) return payload
  if (payload && Array.isArray(payload.results)) return payload.results
  return []
}

/** So'rov yiqilsa butun yuklash to'xtab qolmasin. */
async function safe(request) {
  try {
    return toList(await request)
  } catch {
    return []
  }
}

export const EMPTY_DATA = Object.freeze({
  branches: [],
  courses: [],
  teachers: [],
  news: [],
  vacancies: [],
})

/** @type {Map<string, Promise<object>>} til → yuklash natijasi */
const cache = new Map()

/**
 * Ma'lumotlarni yuklaydi (bir tilda faqat bir marta).
 * @param {string} locale
 */
export function loadAssistantData(locale) {
  if (cache.has(locale)) return cache.get(locale)

  const promise = Promise.all([
    safe(fetchBranches()),
    safe(fetchCourses()),
    safe(fetchTeachers()),
    safe(fetchNews()),
    safe(fetchVacancies()),
  ])
    .then(([branches, courses, teachers, news, vacancies]) => ({
      branches,
      courses,
      teachers,
      news,
      vacancies,
    }))
    .catch(() => ({ ...EMPTY_DATA }))

  cache.set(locale, promise)
  return promise
}

/** Admin panelda kontent o'zgarganda keshni tozalash uchun. */
export function clearAssistantData() {
  cache.clear()
}
