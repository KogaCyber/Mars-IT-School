/**
 * Modal oyna ochilganda orqa fon skrollini to'xtatadi.
 *
 * Nega VueUse'ning `useScrollLock`i emas:
 *
 * 1. U qulfni faqat bitta elementga (`overflow: hidden`) qo'yadi va **sanoq
 *    yuritmaydi**. Ikkita oyna birga ochilsa (masalan filial paneli ustidan
 *    lightbox), ulardan biri yopilishi bilan qulf butunlay yechilardi.
 * 2. Qismlarda qulf `document.body` ga qo'yilardi — bu saytda esa `body` ga
 *    `overflow-x: clip` berilgan (main.css), shu sababli `body`ning `overflow`i
 *    endi viewport'ga tarqalmaydi va `overflow: hidden` hech narsani
 *    to'xtatmasdi. Ya'ni menyu, lightbox va video oynalarida fon baribir
 *    skroll bo'lardi.
 * 3. iOS Safari `overflow: hidden` ni umuman e'tiborsiz qoldiradi.
 *
 * Shu sababli bu yerda `body` `position: fixed` ga o'tkaziladi va joriy skroll
 * o'rni `top` orqali saqlanadi — barcha brauzerlarda, sensorli ekranlarda ham
 * ishlaydigan yagona ishonchli usul. Yopilganda o'rni tiklanadi.
 */
import { onScopeDispose, ref, watch } from 'vue'

/** Nechta oyna ochiq — qulf oxirgisi yopilgandagina yechiladi. */
let locks = 0
/** Qulflashdan oldingi holat (tiklash uchun). */
let snapshot = null

function lock() {
  if (++locks > 1 || typeof document === 'undefined') return

  const html = document.documentElement
  const { body } = document
  const scrollY = window.scrollY
  // Skrollbar yo'qolganda sahifa "sakramasligi" uchun o'rni bo'sh qoldiriladi.
  const scrollbar = window.innerWidth - html.clientWidth

  snapshot = {
    scrollY,
    htmlOverscroll: html.style.overscrollBehavior,
    position: body.style.position,
    top: body.style.top,
    left: body.style.left,
    right: body.style.right,
    width: body.style.width,
    paddingRight: body.style.paddingRight,
  }

  html.style.overscrollBehavior = 'none'
  body.style.position = 'fixed'
  body.style.top = `-${scrollY}px`
  body.style.left = '0'
  body.style.right = '0'
  body.style.width = '100%'
  if (scrollbar > 0) body.style.paddingRight = `${scrollbar}px`
}

function unlock() {
  if (locks === 0) return
  if (--locks > 0 || !snapshot) return

  const html = document.documentElement
  const { body } = document
  const { scrollY } = snapshot

  html.style.overscrollBehavior = snapshot.htmlOverscroll
  body.style.position = snapshot.position
  body.style.top = snapshot.top
  body.style.left = snapshot.left
  body.style.right = snapshot.right
  body.style.width = snapshot.width
  body.style.paddingRight = snapshot.paddingRight
  snapshot = null

  // `html { scroll-behavior: smooth }` tufayli tiklash animatsiyaga
  // aylanmasligi uchun vaqtincha o'chiriladi.
  const behavior = html.style.scrollBehavior
  html.style.scrollBehavior = 'auto'
  window.scrollTo(0, scrollY)
  html.style.scrollBehavior = behavior
}

/**
 * @returns {import('vue').Ref<boolean>} `true` — fon qotadi, `false` — yechiladi.
 */
export function useScrollLock() {
  const isLocked = ref(false)
  // Har bir chaqiruvchi qulfni bir martadan ko'p olmasligi kerak.
  let holding = false

  watch(isLocked, (value) => {
    if (value === holding) return
    holding = value
    value ? lock() : unlock()
  })

  onScopeDispose(() => {
    if (!holding) return
    holding = false
    unlock()
  })

  return isLocked
}
