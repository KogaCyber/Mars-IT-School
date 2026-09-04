<script setup>
/**
 * Cheksiz aylanuvchi lenta — bir vaqtning o'zida ikkala rejimda ishlaydi:
 *
 *  1) o'zi sekin aylanadi (o'ngdan chapga);
 *  2) foydalanuvchi uni qo'li bilan chapga/o'ngga sura oladi — sichqoncha bilan
 *     tortib (drag), tachpad/g'ildirak bilan yoki sensorli ekranda barmoq bilan.
 *
 * Shuning uchun harakat CSS animatsiyasi emas, `scrollLeft` orqali qilinadi:
 * bitta va o'sha element ham brauzerning tabiiy scroll'iga, ham avtomatik
 * siljishga bo'ysunadi.
 *
 * Uzluksizlik: kontent uch marta takrorlanadi va scroll pozitsiyasi bitta
 * to'plam kengligi (W) bo'yicha "o'raladi" — chetga yetganda pozitsiya bir
 * qadam orqaga/oldinga ko'chiriladi, kontent aynan bir xil bo'lgani uchun
 * ko'zga bilinmaydi. Shu tufayli ikkala tomonga ham cheksiz surish mumkin.
 *
 * Nusxalar `inert` emas: `inert` bosishni ham bloklaydi va lentadagi
 * kartochkalarning ko'pi bosilmay qolardi. Shuning uchun nusxalar faqat ekran
 * o'quvchidan yashiriladi (`aria-hidden`), ichidagi havolalar esa
 * `tabindex="-1"` bilan tab tartibidan chiqariladi.
 */
import { useMutationObserver, useResizeObserver } from '@vueuse/core'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  /** Avtomatik aylanish tezligi — piksel/soniya. Katta qiymat — tezroq. */
  speed: { type: Number, default: 110 },
  /** Aylanish yo'nalishi: 'left' (o'ngdan chapga) yoki 'right'. */
  direction: { type: String, default: 'left' },
})

/** Foydalanuvchi to'xtagach avtomatik aylanish shuncha vaqtdan keyin tiklanadi. */
const RESUME_DELAY_MS = 1400
/** Shu masofadan ortiq siljish "tortish" hisoblanadi va bosish bekor qilinadi. */
const DRAG_THRESHOLD_PX = 6
/** Bizning yozuvimiz bilan foydalanuvchi scroll'ini ajratish uchun bo'shliq. */
const SCROLL_EPSILON_PX = 2

const root = ref(null)
const firstSet = ref(null)

/** Bitta to'plam ichida kontent necha marta takrorlanadi. */
const repeat = ref(1)
/** Harakatni kamaytirish rejimida takrorlash ham, avtomatik siljish ham yo'q. */
const isStatic = ref(false)

// Bitta to'plamning kengligi (o'ralish qadami).
let stepWidth = 0
// Avtomatik siljishning kasr aniqligidagi pozitsiyasi: `scrollLeft` ba'zi
// brauzerlarda yaxlitlanadi, sekin tezlikda esa harakat butunlay to'xtab qolardi.
let position = 0
// Oxirgi marta biz yozganimizdan keyingi haqiqiy `scrollLeft`.
let expected = 0

let frame = 0
let lastTime = 0
let resumeTimer = 0
let isPaused = false

// Sichqoncha bilan tortish holati.
let pointerId = null
let dragStartX = 0
let dragStartScroll = 0
let didDrag = false

function reducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

/** Scroll pozitsiyasini yozadi va haqiqiy qiymatni eslab qoladi. */
function setScroll(value) {
  const container = root.value
  if (!container) return

  position = value
  container.scrollLeft = value
  expected = container.scrollLeft
}

/** Nusxalardagi havola/tugmalarni tab tartibidan chiqaradi. */
function syncClones() {
  const container = root.value
  if (!container) return

  container.querySelectorAll('[data-carousel-clone]').forEach((clone) => {
    clone
      .querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')
      .forEach((element) => element.setAttribute('tabindex', '-1'))
  })
}

/**
 * Scroll pozitsiyasini o'rta to'plam atrofida ushlab turadi.
 * Kontent har `stepWidth` da takrorlangani uchun sakrash ko'rinmaydi.
 *
 * @returns {number} qo'llanilgan siljish (tortish paytida hisobga olinadi)
 */
function wrap() {
  const container = root.value
  if (!container || !stepWidth || isStatic.value) return 0

  const current = container.scrollLeft
  let shift = 0

  if (current >= stepWidth * 1.5) shift = -stepWidth
  else if (current < stepWidth * 0.5) shift = stepWidth

  if (shift) setScroll(current + shift)
  return shift
}

async function measure() {
  const container = root.value
  const set = firstSet.value
  if (!container || !set || isStatic.value) return

  // Avval bitta nusxa bo'yicha o'lchaymiz, keyin kerakli sonini hisoblaymiz.
  if (repeat.value !== 1) {
    repeat.value = 1
    await nextTick()
  }

  const single = set.offsetWidth
  if (!single) return

  // Lenta ekrandan kamida bir yarim baravar uzun bo'lishi kerak.
  repeat.value = Math.max(1, Math.ceil((container.offsetWidth * 1.5) / single))

  await nextTick()
  syncClones()

  stepWidth = set.offsetWidth
  // O'rtadagi to'plamdan boshlaymiz — ikkala tomonga ham surish mumkin bo'ladi.
  if (stepWidth) setScroll(stepWidth)
}

/** Avtomatik siljish: har kadrda scroll pozitsiyasini biroz suradi. */
function tick(time) {
  frame = requestAnimationFrame(tick)

  const container = root.value
  if (!container || !stepWidth) return

  const delta = lastTime ? Math.min(time - lastTime, 64) : 0
  lastTime = time

  if (!isPaused && pointerId === null && delta) {
    const shift = (props.speed * delta) / 1000
    setScroll(position + (props.direction === 'right' ? -shift : shift))
  }

  wrap()
}

function pause() {
  isPaused = true
  clearTimeout(resumeTimer)
}

function resume() {
  clearTimeout(resumeTimer)
  resumeTimer = setTimeout(() => {
    isPaused = false
  }, RESUME_DELAY_MS)
}

/**
 * Foydalanuvchi g'ildirak/barmoq bilan surganda avtomatik siljish kutib turadi.
 *
 * `scroll` hodisasi bizning har kadrdagi yozuvimizdan ham chiqadi, shuning uchun
 * haqiqiy pozitsiya kutilgan qiymatdan sezilarli farq qilgandagina buni
 * foydalanuvchi harakati deb hisoblaymiz.
 */
function onScroll() {
  const container = root.value
  if (!container || pointerId !== null) return
  if (Math.abs(container.scrollLeft - expected) <= SCROLL_EPSILON_PX) return

  position = container.scrollLeft
  expected = container.scrollLeft
  pause()
  resume()
}

function onWheel() {
  pause()
  resume()
}

function onPointerDown(event) {
  // Sensorli ekran va stilus brauzerning o'z scroll'idan foydalanadi.
  if (event.pointerType !== 'mouse' || event.button !== 0) return

  pointerId = event.pointerId
  dragStartX = event.clientX
  dragStartScroll = root.value.scrollLeft
  didDrag = false
  pause()
}

function onPointerMove(event) {
  if (pointerId !== event.pointerId) return

  const distance = event.clientX - dragStartX
  if (!didDrag && Math.abs(distance) < DRAG_THRESHOLD_PX) return

  if (!didDrag) {
    didDrag = true
    root.value.setPointerCapture?.(pointerId)
    root.value.classList.add('is-dragging')
  }

  setScroll(dragStartScroll - distance)
  // Lenta "o'ralganda" tortish boshlangan nuqta ham shuncha siljiydi.
  dragStartScroll += wrap()
}

function endDrag(event) {
  if (pointerId === null || (event && pointerId !== event.pointerId)) return

  root.value?.releasePointerCapture?.(pointerId)
  root.value?.classList.remove('is-dragging')
  pointerId = null
  resume()
}

/** Kursor lentadan chiqib ketsa — tortilmayotgan bo'lsagina holatni tozalaymiz. */
function onPointerLeave(event) {
  if (didDrag) return
  endDrag(event)
}

/** Tortishdan keyingi tasodifiy bosishni bekor qiladi (havola ochilib ketmasin). */
function onClickCapture(event) {
  if (!didDrag) return
  event.preventDefault()
  event.stopPropagation()
  didDrag = false
}

onMounted(() => {
  isStatic.value = reducedMotion()
  measure()
  if (!isStatic.value) frame = requestAnimationFrame(tick)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frame)
  clearTimeout(resumeTimer)
})

useResizeObserver(root, measure)

// Kontent keyinroq kelishi mumkin (ma'lumot API'dan yuklanadi).
useMutationObserver(root, syncClones, { childList: true, subtree: true })
</script>

<template>
  <div
    ref="root"
    class="carousel"
    :class="{ 'is-static': isStatic }"
    @scroll.passive="onScroll"
    @wheel.passive="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="endDrag"
    @pointercancel="endDrag"
    @pointerleave="onPointerLeave"
    @mouseenter="pause"
    @mouseleave="resume"
    @focusin="pause"
    @focusout="resume"
    @click.capture="onClickCapture"
  >
    <div class="carousel-track">
      <!-- Uchta bir xil to'plam: o'rtadagisi "haqiqiy", chetdagilari uzluksiz
           surish uchun. Statik rejimda faqat bittasi qoladi. -->
      <div ref="firstSet" class="carousel-set" aria-hidden="true">
        <template v-for="copy in repeat" :key="`before-${copy}`">
          <div class="carousel-copy" data-carousel-clone><slot /></div>
        </template>
      </div>

      <div class="carousel-set">
        <template v-for="copy in repeat" :key="copy">
          <div v-if="copy === 1" class="carousel-copy"><slot /></div>
          <div v-else class="carousel-copy" data-carousel-clone aria-hidden="true">
            <slot />
          </div>
        </template>
      </div>

      <div class="carousel-set" aria-hidden="true">
        <template v-for="copy in repeat" :key="`after-${copy}`">
          <div class="carousel-copy" data-carousel-clone><slot /></div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.carousel {
  overflow-x: auto;
  overflow-y: hidden;
  /* Avtomatik siljish `scrollLeft` orqali bo'lgani uchun "smooth" bo'lmasligi kerak. */
  scroll-behavior: auto;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch;
  cursor: grab;
  /* Chetlarida yumshoq "so'nish" effekti */
  mask-image: linear-gradient(to right, transparent 0, #000 3%, #000 97%, transparent 100%);
  /* Scroll paneli yashiriladi — lenta toza ko'rinadi, surish esa ishlaydi. */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.carousel::-webkit-scrollbar {
  display: none;
}

.carousel.is-dragging {
  cursor: grabbing;
  user-select: none;
}

.carousel-track {
  display: flex;
  width: max-content;
}

.carousel-set {
  display: flex;
  flex-shrink: 0;
  gap: var(--spacing-gutter);
  padding-right: var(--spacing-gutter);
}

/* Nusxa o'ramlari lentaning bir qismi bo'lib qolishi kerak — o'z tarmog'ini
   yaratmaydi, elementlar orasidagi masofa bir xil saqlanadi. */
.carousel-copy {
  display: contents;
}

/* Harakat o'chirilganda: oddiy gorizontal scroll, takrorlashsiz */
.carousel.is-static {
  mask-image: none;
  cursor: auto;
}

.carousel.is-static .carousel-set:first-child,
.carousel.is-static .carousel-set:last-child {
  display: none;
}
</style>
