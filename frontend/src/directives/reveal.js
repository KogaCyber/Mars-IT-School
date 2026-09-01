/**
 * `v-reveal` — element ekranga kirganda uni yumshoq paydo qiladi.
 *
 * Ishlatilishi:  <section v-reveal>…</section>
 *                <div v-reveal="{ delay: 120 }">…</div>
 *
 * Kontent hech qachon yashirin qolib ketmasligi kerak, shuning uchun:
 *  - `prefers-reduced-motion` yoqilgan bo'lsa yoki IntersectionObserver bo'lmasa —
 *    element darhol ko'rinadi;
 *  - kuzatuvchi ishlamay qolsa, zaxira taymer 1.2 soniyadan keyin ochib yuboradi.
 */

const FALLBACK_DELAY_MS = 1200

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

function show(el) {
  el.classList.add('is-revealed')
}

export const reveal = {
  mounted(el, binding) {
    const { delay = 0, threshold = 0.1 } = binding.value || {}

    if (prefersReducedMotion() || typeof IntersectionObserver === 'undefined') {
      show(el)
      return
    }

    el.classList.add('reveal')
    el.style.transitionDelay = `${delay}ms`

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
  },

  unmounted(el) {
    if (!el._reveal) return
    el._reveal.observer.disconnect()
    clearTimeout(el._reveal.timer)
    delete el._reveal
  },
}

export default reveal
