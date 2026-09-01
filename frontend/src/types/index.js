/**
 * Backend API javoblarining tuzilishi (JSDoc — muharrirda avtomatik to'ldirish uchun).
 * Bu fayl ish vaqtida hech narsa qilmaydi, faqat hujjat vazifasini bajaradi.
 *
 * @typedef {Object} Paginated
 * @property {number} count
 * @property {string|null} next
 * @property {string|null} previous
 * @property {Array<Object>} results
 *
 * @typedef {Object} SiteSettings
 * @property {string} phone
 * @property {string} extra_phone
 * @property {string} email
 * @property {string} telegram_url
 * @property {string} instagram_url
 * @property {string} youtube_url
 * @property {string} facebook_url
 * @property {string} space_app_ios_url
 * @property {string} space_app_android_url
 * @property {string} privacy_policy_url
 *
 * @typedef {Object} Course
 * @property {string} id
 * @property {string} slug
 * @property {string} title
 * @property {string} subtitle
 * @property {string} card_image
 * @property {string} accent_color
 * @property {number} age_from
 * @property {number} age_to
 * @property {string} age_range
 * @property {number} duration_months
 * @property {number} lessons_per_week
 * @property {string|null} price
 * @property {boolean} is_featured
 * @property {string|null} direction
 *
 * @typedef {Object} Teacher
 * @property {string} id
 * @property {string} slug
 * @property {string} full_name
 * @property {string} position
 * @property {string} photo
 * @property {string} company
 * @property {string} company_logo
 * @property {number} experience_years
 *
 * @typedef {Object} News
 * @property {string} id
 * @property {string} slug
 * @property {string} title
 * @property {string} excerpt
 * @property {string} cover
 * @property {string} published_at
 * @property {number} reading_minutes
 * @property {number} views_count
 *
 * @typedef {Object} Branch
 * @property {string} id
 * @property {string} slug
 * @property {string} name
 * @property {string} address
 * @property {string} phone
 * @property {number|null} latitude
 * @property {number|null} longitude
 * @property {string} map_url_yandex
 * @property {string} map_url_google
 *
 * @typedef {Object} ApiError
 * @property {string} detail
 * @property {Object.<string, string[]>} [errors]
 * @property {number} [status]
 */

export {}
