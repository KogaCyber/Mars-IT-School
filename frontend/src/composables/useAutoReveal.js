/**
 * Sayt bo'ylab avtomatik scroll-animatsiyasi.
 *
 * Har bir sarlavha, matn va kartochkaga qo'lda `v-reveal` yozib chiqish o'rniga,
 * `<main>` ichidagi mazmunli bloklar skroll paytida o'z-o'zidan yumshoq paydo
 * bo'ladi. Bir ota-ona ichidagi qo'shni elementlar ketma-ket ("zinapoyasimon")
 * chiqadi — sahifa jonli ko'rinadi.
 *
 * Barcha elementlar uchun bitta umumiy `IntersectionObserver` ishlatiladi:
 * sahifada yuzlab element bo'lsa ham ortiqcha yuk tushmaydi.
 *
 * Kontent API'dan keyinroq kelishi mumkin, shuning uchun DOM o'zgarishlari ham
 * kuzatiladi.
 */
import { onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

import { prefersReducedMotion } from '@/directives/reveal'

/** Yirik bloklar — butunicha ko'tarilib chiqadi. */
const BLOCKS = 'section, article, aside, header, figure, form, dl'

/** Blok ichidagi mayda elementlar — ketma-ket chiqadi. */
const ITEMS = 'h1, h2, h3, h4, p, li, blockquote, img, picture, video, table'

/** Ichida animatsiya kerak bo'lmagan (yoki zarar qiladigan) joylar. */
const SKIP = [
  '[data-no-reveal]',
  '[data-carousel-clone]',
  '.carousel',
  '.leaflet-container',
  '.branches-map',
  '[aria-hidden="true"]',
  '[class*="animate-"]',
].join(', ')

/** Bitta sahifada animatsiya qilinadigan elementlarning yuqori chegarasi. */
const MAX_ELEMENTS = 600
/** Qo'shni elementlar orasidagi kechikish va uning chegarasi. */
const STAGGER_MS = 70
const STAGGER_MAX_MS = 280
/** Skroll paytida tekshiruv shu oraliqdan tez-tez o'tkazilmaydi. */
const SCROLL_THROTTLE_MS = 120

export function useAutoReveal(rootSelector = '#main') {
  /** @type {Set<HTMLElement>} */
  const touched = new Set()
  /** @type {IntersectionObserver | null} */
  let observer = null
  let mutations = null
  let frame = 0
  let scrollTimer = 0
  /** Kuzatilayotgan, lekin hali ochilmagan elementlar. */
  const pending = new Set()
  // Ekrandan ancha pastda turgan, hali navbati kelmagan elementlar bormi.
  let hasLater = false

  function reveal(el) {
    el.classList.add('is-revealed')
    pending.delete(el)
  }

  /**
   * Zaxira tekshiruvi: ba'zi elementlar `IntersectionObserver` uchun
   * "ko'rinmas" bo'lib qoladi — masalan yig'ilgan (`overflow: hidden`,
   * balandligi nol) blok ichida yoki gorizontal lentada yon tomonda turgan
   * element. Foydalanuvchi ulardan o'tib ketgan bo'lsa, ular animatsiyasiz
   * ochib yuboriladi — kontent hech qachon ko'rinmay qolmaydi.
   */
  function sweep() {
    if (!pending.size) return

    const limit = window.innerHeight
    pending.forEach((el) => {
      if (!el.isConnected) {
        pending.delete(el)
        return
      }
      if (el.getBoundingClientRect().top < limit) {
        observer?.unobserve(el)
        reveal(el)
      }
    })
  }

  function scan() {
    const root = document.querySelector(rootSelector)
    if (!root || !observer) return

    // Ota-ona bo'yicha hisoblagich: qo'shni elementlar navbatma-navbat chiqadi.
    const orderByParent = new Map()

    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    /**
     * Element animatsiyaga yaraydimi?
     *
     *  'now'   — hozir animatsiya biriktiriladi (ekran ichida yoki biroz pastda);
     *  'never' — hech qachon: ekrandan yuqorida qolgan yoki yon tomonga surilgan
     *            (gorizontal lenta ichidagi) element — u "kesishmasligi" mumkin,
     *            shuning uchun oddiy, animatsiyasiz ko'rinishda qoladi;
     *  'later' — hozircha juda pastda, foydalanuvchi yaqinlashganda ko'riladi.
     *
     * Shu qoida tufayli kontent hech qachon ko'rinmay qolib ketmaydi.
     */
    const stateOf = (el) => {
      const rect = el.getBoundingClientRect()
      if (rect.width === 0 && rect.height === 0) return 'now' // hali o'lchanmagan
      if (rect.bottom <= 0) return 'never'
      if (rect.right <= 0 || rect.left >= viewportWidth) return 'never'
      return rect.top < viewportHeight * 2 ? 'now' : 'later'
    }

    hasLater = false

    const collect = (selector, variant) => {
      root.querySelectorAll(selector).forEach((el) => {
        if (touched.size >= MAX_ELEMENTS) return
        if (touched.has(el)) return
        if (el.closest(SKIP)) return
        // Qo'lda `v-reveal` yozilgan elementlar o'z direktivasi bilan ishlaydi
        // (unda o'z kuzatuvchisi va zaxira taymeri bor) — ularga tegilmaydi.
        if (el._reveal) {
          touched.add(el)
          return
        }
        // Allaqachon ochilgan element qayta yashirilmaydi.
        if (el.classList.contains('is-revealed')) {
          touched.add(el)
          return
        }

        const state = stateOf(el)
        if (state === 'later') {
          hasLater = true
          return
        }
        if (state === 'never') {
          // Ekrandan yuqorida qolgan element kuzatilmaydi. Agar unda oldingi
          // skanerdan `reveal` sinfi qolgan bo'lsa, uni shu yerda ochib
          // qo'yamiz — aks holda u butunlay ko'rinmas bo'lib qolardi.
          if (el.classList.contains('reveal')) reveal(el)
          touched.add(el)
          return
        }

        const parent = el.parentElement
        const order = (orderByParent.get(parent) || 0) + 1
        orderByParent.set(parent, order)

        el.classList.add('reveal')
        if (variant) el.classList.add(variant)
        const delay = Math.min((order - 1) * STAGGER_MS, STAGGER_MAX_MS)
        if (delay) el.style.transitionDelay = `${delay}ms`

        touched.add(el)
        pending.add(el)
        observer.observe(el)
      })
    }

    collect(BLOCKS, '')
    collect(ITEMS, 'reveal-soft')
    sweep()
  }

  function schedule() {
    cancelAnimationFrame(frame)
    frame = requestAnimationFrame(scan)
  }

  /**
   * Skroll paytidagi tekshiruv — sekinlashtirilgan va faqat kerak bo'lganda.
   * Navbatdagi element qolmagan bo'lsa, skroll umuman qayta ko'rilmaydi.
   */
  function scheduleOnScroll() {
    if (scrollTimer) return
    scrollTimer = setTimeout(() => {
      scrollTimer = 0
      sweep()
      if (hasLater) schedule()
    }, SCROLL_THROTTLE_MS)
  }

  function start() {
    const root = document.querySelector(rootSelector)
    if (!root) return

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          reveal(entry.target)
          observer.unobserve(entry.target)
        })
      },
      // `threshold: 0` — balandligi hali nolga teng element (masalan yuklanmagan
      // rasm) ham albatta ochiladi; hech narsa yashirin qolib ketmaydi.
      { threshold: 0, rootMargin: '0px 0px -4% 0px' },
    )

    schedule()

    mutations = new MutationObserver(schedule)
    mutations.observe(root, { childList: true, subtree: true })

    // Sahifa pastroqqa aylantirilganda navbatdagi bloklar ham tayyorlanadi.
    window.addEventListener('scroll', scheduleOnScroll, { passive: true })
    window.addEventListener('resize', schedule, { passive: true })
  }

  function reset() {
    observer?.disconnect()
    touched.clear()
    pending.clear()
  }

  onMounted(() => {
    // Harakatni kamaytirish rejimida hech narsa yashirilmaydi.
    if (prefersReducedMotion()) return
    start()
  })

  const route = useRoute()
  watch(
    () => route.fullPath,
    () => {
      if (!observer) return
      reset()
      schedule()
    },
  )

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', scheduleOnScroll)
    window.removeEventListener('resize', schedule)
    clearTimeout(scrollTimer)
    cancelAnimationFrame(frame)
    mutations?.disconnect()
    observer?.disconnect()
    touched.clear()
    pending.clear()
    observer = null
  })
}
