/**
 * Struktura ko'rinishidagi kontent (`data/*.js`) uchun tarjima yordamchisi.
 *
 * Nega alohida: maketda qat'iy belgilangan kontent — bosqichlar, mavzular,
 * kartochkalar — massiv va obyektlardan iborat. Ularni `messages/` ichiga
 * ko'chirish o'rniga matnni to'g'ridan-to'g'ri ma'lumot yonida `L()` bilan
 * uch tilda yozamiz: struktura bir joyda qoladi, tarjima esa yonma-yon
 * turadi va biror til unutilib qolmaydi.
 *
 *   const STAGES = [{ number: '01', title: L('Boshlanish', 'Начало', 'Start') }]
 *   const stages = useLocalized(STAGES)   // → [{ number: '01', title: 'Boshlanish' }]
 */
import { computed, unref } from 'vue'
import { useI18n } from 'vue-i18n'

import { DEFAULT_LANGUAGE } from './language'

const MARKER = '__i18n'

/** Uch tilli qiymat yaratadi. Qiymat satr, massiv yoki obyekt bo'lishi mumkin. */
export function L(uz, ru, en) {
  return { [MARKER]: true, uz, ru, en }
}

const isLocalized = (value) =>
  Boolean(value) && typeof value === 'object' && value[MARKER] === true

/**
 * Strukturani chuqur aylanib chiqib, barcha `L()` tugunlarini tanlangan
 * tildagi qiymat bilan almashtiradi. Qolgan maydonlar (rasm, ikonka, raqam)
 * o'zgarishsiz qoladi.
 */
export function localize(value, locale = DEFAULT_LANGUAGE) {
  if (Array.isArray(value)) return value.map((item) => localize(item, locale))

  if (value && typeof value === 'object') {
    if (isLocalized(value)) {
      const picked = locale in value ? value[locale] : value[DEFAULT_LANGUAGE]
      // Tanlangan qiymat ichida yana `L()` bo'lishi mumkin.
      return localize(picked, locale)
    }

    const result = {}
    for (const [key, item] of Object.entries(value)) result[key] = localize(item, locale)
    return result
  }

  return value
}

/**
 * Reaktiv variant: til almashganda qiymat o'zi qayta hisoblanadi.
 * @param {unknown} source `L()` ishlatilgan ma'lumot (ref ham bo'lishi mumkin)
 */
export function useLocalized(source) {
  const { locale } = useI18n()
  return computed(() => localize(unref(source), locale.value))
}
