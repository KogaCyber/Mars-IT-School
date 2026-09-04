/**
 * `v-reveal` — element ekranga kirganda uni yumshoq paydo qiladi.
 *
 * Ishlatilishi:  <section v-reveal>…</section>
 *                <div v-reveal="{ delay: 120 }">…</div>
 *                <div v-reveal="{ variant: 'left' }">…</div>
 *
 * Kontent hech qachon yashirin qolib ketmasligi kerak, shuning uchun:
 *  - `prefers-reduced-motion` yoqilgan bo'lsa yoki IntersectionObserver bo'lmasa —
 *    element darhol ko'rinadi;
 *  - kuzatuvchi ishlamay qolsa, zaxira taymer 1.2 soniyadan keyin ochib yuboradi.
 */

const FALLBACK_DELAY_MS = 1200

/** Yo'nalish variantlari — CSS'da `.reveal-left` va h.k. sifatida tavsiflangan. */
const VARIANTS = ['up', 'left', 'right', 'zoom', 'fade']

export function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

function show(el) {
  el.classList.add('is-revealed')
}

/**
 * Elementga "skrollda paydo bo'lish" xatti-harakatini biriktiradi.
 * Direktiva ham, avtomatik animatsiya ham shu funksiyadan foydalanadi.
 *
 * @param {HTMLElement} el
 * @param {{delay?: number, threshold?: number, variant?: string}} [options]
 */
export function applyReveal(el, options = {}) {
  const { delay = 0, threshold = 0.1, variant = 'up' } = options

  // Ikki marta biriktirib qo'ymaymiz (avtomatik animatsiya + qo'lda yozilgan).
  if (el._reveal || el.classList.contains('reveal')) return

  if (prefersReducedMotion() || typeof IntersectionObserver === 'undefined') {
    show(el)
    return
  }

  el.classList.add('reveal')
  if (variant !== 'up' && VARIANTS.includes(variant)) el.classList.add(`reveal-${variant}`)
  if (delay) el.style.transitionDelay = `${delay}ms`

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        show(entry.target)
        observer.unobserve(entry.target)
      })
    },
    { threshold, rootMargin: '0px 0px -5% 0px' },
  )

  observer.observe(el)

  el._reveal = {
    observer,
    timer: setTimeout(() => {
      show(el)
      observer.disconnect()
    }, FALLBACK_DELAY_MS + delay),
  }
}

export function releaseReveal(el) {
  if (!el._reveal) return
  el._reveal.observer.disconnect()
  clearTimeout(el._reveal.timer)
  delete el._reveal
}

export const reveal = {
  mounted(el, binding) {
    applyReveal(el, binding.value || {})
  },

  unmounted(el) {
    releaseReveal(el)
  },
}

export default reveal
