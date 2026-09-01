/**
 * Admin paneldagi kurslar bilan takrorlanadigan sahifalar.
 *
 * Kurs slug'i backendda ruscha nomdan avtomatik yasaladi («Программирование» →
 * `programmirovanie`) va u umumiy `CourseView.vue` sahifasida ochiladi. Ammo
 * ayni shu kursning maketga to'liq mos qilib yasalgan alohida sahifasi ham bor
 * (`/kursy/it-razrabotka`). Natijada bitta kurs ikkita URL'da chiqib qolardi.
 *
 * Shu jadval takrorlanishni yopadi: eski slug alohida sahifaga yo'naltiriladi —
 * marshrutda ham (redirect), havolalarda ham (`courseRouteTo`).
 *
 * Yangi dublikat paydo bo'lsa, shu yerga bitta qator qo'shish kifoya.
 */
export const COURSE_ALIASES = {
  programmirovanie: 'it-razrabotka',
}

/** Alohida sahifasi bor kurslar: slug → marshrut nomi. */
export const COURSE_ROUTES = {
  'it-kids': 'course-it-kids',
  'it-razrabotka': 'course-it-razrabotka',
}

/**
 * Kurs havolasi: alohida sahifasi bo'lsa — o'shanga, aks holda umumiy sahifaga.
 * @param {string} slug
 */
export function courseRouteTo(slug) {
  const target = COURSE_ALIASES[slug] || slug
  const name = COURSE_ROUTES[target]
  return name ? { name } : { name: 'course', params: { slug: target } }
}

/** Sahifa aliasi → backenddagi haqiqiy kurs slug'i (`COURSE_ALIASES`ning teskarisi). */
const API_SLUGS = Object.fromEntries(
  Object.entries(COURSE_ALIASES).map(([apiSlug, pageSlug]) => [pageSlug, apiSlug]),
)

/**
 * Backendga yuboriladigan kurs slug'i. Sahifa aliasi («it-razrabotka») admin
 * paneldagi kurs slug'iga («programmirovanie») qaytariladi — aks holda ariza
 * 400 bilan rad etiladi.
 * @param {string|null|undefined} slug
 * @returns {string|null}
 */
export function courseApiSlug(slug) {
  if (!slug) return null
  return API_SLUGS[slug] || slug
}
