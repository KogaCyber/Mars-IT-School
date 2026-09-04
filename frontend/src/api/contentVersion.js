/**
 * Kontentning joriy versiyasi — GET so'rovlariga `_v` parametri sifatida
 * qo'shiladi (`client.js`).
 *
 * Nega kerak: javoblar brauzer va CDN keshida yotadi. Manzil kontent
 * o'zgarganda o'zi ham o'zgarsa, kesh o'z-o'zidan chetlab o'tiladi va
 * yangilangan ma'lumot darhol keladi — «hard refresh» kerak emas.
 *
 * Qiymat alohida (hech narsa import qilmaydigan) modulda saqlanadi: uni ham
 * HTTP klient, ham do'kon (`stores/live.js`) ishlatadi, aylanma import esa
 * bo'lmaydi.
 */
let contentVersion = 0

export function getContentVersion() {
  return contentVersion
}

export function setContentVersion(value) {
  contentVersion = Number(value) || 0
}
