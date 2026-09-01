<script setup>
/**
 * Cheksiz aylanuvchi karusel (marquee).
 *
 * Muhim jihat: elementlar soni kam bo'lsa lenta ekran kengligini to'ldirmaydi va
 * aylanish "uzilib" qoladi. Shuning uchun kontent kengligi o'lchanadi va
 * kerakli nusxalar soni avtomatik hisoblanadi — lenta har doim uzluksiz ko'rinadi.
 *
 * Tezlik `speed` (piksel/soniya) orqali beriladi: kontent uzunligidan qat'i nazar
 * aylanish bir xil tezlikda ketadi.
 *
 * Nusxalar `inert` emas: `inert` bosishni ham bloklaydi va lentadagi
 * kartochkalarning ko'pi (ekranda ko'rinib turgani — aksari nusxa) bosilmay
 * qolardi. Shuning uchun nusxalar faqat ekran o'quvchidan yashiriladi
 * (`aria-hidden`), ichidagi havolalar esa `tabindex="-1"` bilan tab tartibidan
 * chiqariladi — bosish ishlaydi, klaviatura navigatsiyasi takrorlanmaydi.
 */
import { useMutationObserver, useResizeObserver } from '@vueuse/core'
import { computed, nextTick, onMounted, ref } from 'vue'

const props = defineProps({
  /** Aylanish tezligi — piksel/soniya. Katta qiymat — tezroq. */
  speed: { type: Number, default: 110 },
  /** Aylanish yo'nalishi: 'left' yoki 'right'. */
  direction: { type: String, default: 'left' },
})

const root = ref(null)
const firstSet = ref(null)

// Bitta to'plamdagi kontentning tabiiy kengligi (piksellarda).
const setWidth = ref(0)
// Bitta to'plam ichida kontent necha marta takrorlanadi.
const repeat = ref(1)

/** Bir to'liq aylanish davomiyligi: masofa / tezlik. */
const duration = computed(() => {
  const distance = setWidth.value * repeat.value
  return distance > 0 ? Math.max(distance / props.speed, 8) : 30
})

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

async function measure() {
  const container = root.value
  const set = firstSet.value
  if (!container || !set) return

  // Avval bitta nusxa bo'yicha o'lchaymiz, keyin kerakli sonini hisoblaymiz.
  if (repeat.value !== 1) {
    repeat.value = 1
    await nextTick()
  }

  const single = set.scrollWidth
  if (!single) return

  setWidth.value = single
  // Lenta ekrandan kamida bir yarim baravar uzun bo'lishi kerak.
  repeat.value = Math.max(1, Math.ceil((container.offsetWidth * 1.5) / single))

  await nextTick()
  syncClones()
}

onMounted(measure)
useResizeObserver(root, measure)

// Kontent keyinroq kelishi mumkin (ma'lumot API'dan yuklanadi) — yangi nusxalar
// paydo bo'lganda ular ham tab tartibidan chiqariladi.
useMutationObserver(root, syncClones, { childList: true, subtree: true })
</script>

<template>
  <div
    ref="root"
    class="carousel"
    :style="{
      '--carousel-duration': `${duration}s`,
      '--carousel-direction': direction === 'right' ? 'reverse' : 'normal',
    }"
  >
    <div class="carousel-track">
      <div ref="firstSet" class="carousel-set">
        <!-- Faqat birinchi nusxa "haqiqiy": qolganlari lentani to'ldirish uchun
             takrorlanadi — ular ekran o'quvchidan yashiriladi, lekin bosiladi. -->
        <template v-for="copy in repeat" :key="copy">
          <div v-if="copy === 1" class="carousel-copy"><slot /></div>
          <div v-else class="carousel-copy" data-carousel-clone aria-hidden="true">
            <slot />
          </div>
        </template>
      </div>

      <!-- Nusxa: uzluksiz aylanish uchun (ekran o'quvchilardan yashiriladi) -->
      <div class="carousel-set" aria-hidden="true">
        <template v-for="copy in repeat" :key="`clone-${copy}`">
          <div class="carousel-copy" data-carousel-clone><slot /></div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.carousel {
  overflow: hidden;
  /* Chetlarida yumshoq "so'nish" effekti */
  mask-image: linear-gradient(to right, transparent 0, #000 3%, #000 97%, transparent 100%);
}

.carousel-track {
  display: flex;
  width: max-content;
  animation: carousel-scroll var(--carousel-duration) linear infinite;
  animation-direction: var(--carousel-direction);
}

.carousel:hover .carousel-track,
.carousel:focus-within .carousel-track {
  animation-play-state: paused;
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

@keyframes carousel-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .carousel {
    overflow-x: auto;
    mask-image: none;
  }

  .carousel-track {
    animation: none;
  }

  /* Harakat o'chirilganda nusxa keraksiz */
  .carousel-set:last-child {
    display: none;
  }
}
</style>
