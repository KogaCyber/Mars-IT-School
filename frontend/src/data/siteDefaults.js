/**
 * Sayt kontaktlarining standart (maketdagi) qiymatlari — BITTA manba.
 *
 * Admin panelda kontaktlar (SiteSettings) bo'sh bo'lsa, sayt shu qiymatlarni
 * ko'rsatadi. Muharrir «Контакты» formasi ham aynan shular bilan to'ldiriladi —
 * shunda formada «joriy» ma'lumot ko'rinadi (saytdagidek), bo'sh emas, va xodim
 * ularni tahrirlab saqlaydi.
 */
import contactsMessages from '@/i18n/messages/contacts.js'

export const DEFAULT_PHONE = '+998 78 777 77 57'
export const DEFAULT_EMAIL = 'info@marsit.uz'

/** Ish vaqti — tarjima faylidan (til bo'yicha), aks holda ruscha. */
export function defaultWorkHours(lang) {
  return contactsMessages[lang]?.defaultWorkHours || contactsMessages.ru.defaultWorkHours
}
