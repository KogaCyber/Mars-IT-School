/** Formatlash yordamchilari. */

export function formatPrice(value) {
  const amount = typeof value === 'string' ? Number.parseFloat(value) : value
  if (amount === null || amount === undefined || Number.isNaN(amount)) return '—'
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(amount)
}

export function formatDate(iso, locale = 'ru-RU') {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date)
}

/** Telefon raqamni yozilayotgan paytda +998 90 123 45 67 ko'rinishiga keltiradi. */
export function formatPhone(raw) {
  const digits = String(raw || '')
    .replace(/\D/g, '')
    .replace(/^998/, '')
    .slice(0, 9)
  const parts = [digits.slice(0, 2), digits.slice(2, 5), digits.slice(5, 7), digits.slice(7, 9)]
  return `+998 ${parts.filter(Boolean).join(' ')}`.trimEnd()
}

/** Serverga yuboriladigan toza ko'rinish: +998XXXXXXXXX */
export function toPhonePayload(raw) {
  const digits = String(raw || '')
    .replace(/\D/g, '')
    .replace(/^998/, '')
    .slice(0, 9)
  return `+998${digits}`
}

export function isValidPhone(raw) {
  return /^\+998\d{9}$/.test(toPhonePayload(raw))
}
