/**
 * Til sozlamalari — alohida modulda, chunki uni ham HTTP klient,
 * ham i18n moduli ishlatadi (aylanma importlarning oldini oladi).
 */
export const LANGUAGE_STORAGE_KEY = 'mars.lang'

/** Saytda mavjud tillar; birinchisi — asosiy til. */
export const SUPPORTED_LANGUAGES = ['uz', 'ru', 'en']

/** Saytning asosiy tili — o'zbekcha. */
export const DEFAULT_LANGUAGE = 'uz'

/**
 * Manzildagi `?lang=` parametri.
 *
 * `hreflang` belgilarida har bir til alohida URL bilan e'lon qilinadi
 * (`seoConfig.js:localeUrl`). Bu manzillar haqiqatda ishlashi shart: qidiruv
 * roboti yoki ulashilgan havola orqali kelgan odam darhol o'sha tildagi
 * saytni ko'rishi kerak, aks holda hreflang yolg'on bo'lib qolardi.
 */
export function languageFromUrl() {
  if (typeof window === 'undefined') return null
  try {
    const value = new URLSearchParams(window.location.search).get('lang')
    return SUPPORTED_LANGUAGES.includes(value) ? value : null
  } catch {
    return null
  }
}

/** Boshlang'ich tilni manzil va saqlangan tanlovdan aniqlaydi (bir marta). */
function resolveInitialLanguage() {
  // Manzildagi til saqlangan tanlovdan ustun — havola aynan shu tilni va'da qilgan.
  const fromUrl = languageFromUrl()
  if (fromUrl) return fromUrl

  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY)
    if (SUPPORTED_LANGUAGES.includes(stored)) return stored
  } catch {
    /* localStorage bloklangan bo'lsa asosiy tilga qaytamiz. */
  }
  return DEFAULT_LANGUAGE
}

/**
 * Joriy til — xotirada saqlanadi.
 *
 * Nega faqat `localStorage`/URL dan o'qib qo'ya olmaymiz: manzildagi `?lang=`
 * saqlangan tanlovdan ustun turadi, ya'ni `?lang=ru` bilan kelgan odam tilni
 * o'zbekchaga o'zgartirsa ham HTTP klient har bir so'rovda yana `ru` ni
 * yuborib turardi — interfeys tarjima bo'lardi-yu, backend kontenti ruscha
 * qolardi. Endi `?lang=` faqat BOSHLANG'ICH qiymatni beradi, keyingi tanlov
 * esa shu yerda yashaydi.
 */
let currentLanguage = null

export function getLanguage() {
  if (currentLanguage === null) currentLanguage = resolveInitialLanguage()
  return currentLanguage
}

export function setLanguage(language) {
  if (!SUPPORTED_LANGUAGES.includes(language)) return
  currentLanguage = language
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
  } catch {
    /* localStorage mavjud bo'lmasa ham til joriy sessiyada ishlaydi. */
  }
}
