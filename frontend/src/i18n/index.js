/**
 * Sayt tarjimalari (i18n).
 *
 * Har bir bo'lim `messages/<nom>.js` faylida saqlanadi va uchala tilni
 * (uz / ru / en) yonma-yon eksport qiladi — shunda tarjimalar bir joyda
 * turadi va biror til unutilib qolmaydi.
 *
 * Yangi bo'lim qo'shish uchun `messages/` ichiga fayl yaratish kifoya:
 * `import.meta.glob` uni avtomatik ulaydi va kalit fayl nomi bo'ladi.
 */
import { createI18n } from 'vue-i18n'

import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, getLanguage } from './language'

const modules = import.meta.glob('./messages/*.js', { eager: true })

/** @type {Record<string, Record<string, unknown>>} */
const messages = Object.fromEntries(SUPPORTED_LANGUAGES.map((locale) => [locale, {}]))

for (const [path, module] of Object.entries(modules)) {
  const section = path.slice(path.lastIndexOf('/') + 1, -3)
  const bundle = module.default ?? {}

  for (const locale of SUPPORTED_LANGUAGES) {
    messages[locale][section] = bundle[locale] ?? {}
  }
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getLanguage(),
  fallbackLocale: DEFAULT_LANGUAGE,
  // Tarjima topilmasa konsol to'lib ketmasin — fallback jimgina ishlaydi.
  missingWarn: false,
  fallbackWarn: false,
  messages,
})

/** Vue kontekstidan tashqarida (store, util) tarjima olish uchun. */
export const t = (key, params) => i18n.global.t(key, params)

/** Til almashtirilganda i18n va `<html lang>` yangilanadi. */
export function setI18nLanguage(locale) {
  i18n.global.locale.value = locale
  document.documentElement.setAttribute('lang', locale)
}

export default i18n
