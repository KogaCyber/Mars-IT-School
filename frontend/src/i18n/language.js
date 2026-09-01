/**
 * Til sozlamalari — alohida modulda, chunki uni ham HTTP klient,
 * ham i18n moduli ishlatadi (aylanma importlarning oldini oladi).
 */
export const LANGUAGE_STORAGE_KEY = 'mars.lang'

/** Saytda mavjud tillar; birinchisi — asosiy til. */
export const SUPPORTED_LANGUAGES = ['uz', 'ru', 'en']

/** Saytning asosiy tili — o'zbekcha. */
export const DEFAULT_LANGUAGE = 'uz'

export function getLanguage() {
  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY)
    if (SUPPORTED_LANGUAGES.includes(stored)) return stored
  } catch {
    /* localStorage bloklangan bo'lsa asosiy tilga qaytamiz. */
  }
  return DEFAULT_LANGUAGE
}

export function setLanguage(language) {
  if (!SUPPORTED_LANGUAGES.includes(language)) return
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
  } catch {
    /* localStorage mavjud bo'lmasa ham til joriy sessiyada ishlaydi. */
  }
}
