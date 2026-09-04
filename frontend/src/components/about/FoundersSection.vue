<script setup>
/**
 * «Кто стоит за школой» — asoschilar karuseli.
 *
 * Figma: o'ngda yorliq va sarlavha, ostida suratlar lentasi;
 * chapda ustidan turuvchi ma'lumot kartochkasi (nomi, izohi, o'q tugmalari, hisoblagich).
 *
 * Lenta cheksiz aylanadi: ro'yxat uch nusxada chiziladi va lenta har doim
 * bir xil yo'nalishda suriladi — faol surat chetga chiqib ketadi, o'rniga
 * keyingisi keladi. O'tish tugagach lenta o'rtadagi nusxaga sezilmasdan
 * qaytariladi (animatsiyasiz), shuning uchun "boshiga qaytish" ko'rinmaydi.
 *
 * Karusel o'zi avtomatik almashib turadi; foydalanuvchi o'q tugmasini bosса
 * yoki kartochka ustiga sichqonchani olib borsa — vaqtinchalik to'xtaydi.
 */
import { useIntervalFn } from '@vueuse/core'
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'

const { t } = useI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  /** Avtomatik almashish oralig'i (ms). */
  interval: { type: Number, default: 5000 },
})

const total = computed(() => props.items.length)

/** Lentadagi joriy o'rin — o'rtadagi nusxadan boshlanadi. */
const position = ref(0)
/** O'rtadagi nusxaga qaytish paytida animatsiya o'chiriladi. */
const isSnapping = ref(false)

/** Uch nusxa: chapga ham, o'ngga ham surish uchun zaxira bo'ladi. */
const loopItems = computed(() =>
  total.value ? [...props.items, ...props.items, ...props.items] : [],
)

const activeIndex = computed(() =>
  total.value ? ((position.value % total.value) + total.value) % total.value : 0,
)
const activeFounder = computed(() => props.items[activeIndex.value] || null)

function go(step) {
  if (total.value < 2) return
  position.value += step
}

/**
 * O'tish tugagach lenta o'rtadagi nusxaga qaytariladi: surat almashmaydi,
 * ammo chetga chiqib ketish uchun yana joy paydo bo'ladi.
 */
async function normalize() {
  if (total.value < 2) return

  const middle = total.value + activeIndex.value
  if (position.value === middle) return

  isSnapping.value = true
  position.value = middle
  await nextTick()
  // Brauzer yangi o'rinni chizib bo'lgach animatsiya qaytariladi
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      isSnapping.value = false
    })
  })
}

// Avtomatik almashish
const { pause, resume } = useIntervalFn(
  () => go(1),
  () => props.interval,
  {
    immediate: false,
  },
)

/** Qo'lda o'tilganda taymer qaytadan boshlanadi — o'tish darrov almashmasin. */
function goManually(step) {
  go(step)
  restart()
}

function restart() {
  pause()
  if (total.value > 1) resume()
}

watch(
  total,
  (length) => {
    position.value = length
    restart()
  },
  { immediate: true },
)
</script>

<template>
  <section
    v-if="items.length"
    v-reveal
    class="section bg-ink relative overflow-hidden"
    @mouseenter="pause"
    @mouseleave="restart"
    @focusin="pause"
    @focusout="restart"
  >
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="pointer-events-none absolute top-1/2 left-0 w-[110%] max-w-none -translate-y-1/2 opacity-60 select-none lg:w-[65%]"
    />

    <div class="container-page relative">
      <header class="lg:text-center">
        <p class="eyebrow">{{ t('about.foundersEyebrow') }}</p>
        <h2 class="section-title mt-5 text-white">
          <span v-for="line in t('about.foundersTitle').split('\n')" :key="line" class="block">
            {{ line }}
          </span>
        </h2>
      </header>
    </div>

    <!-- Suratlar lentasi: chapdan kesiladi (u yerda surat ko'rinmaydi),
         o'ng chekkada esa ekrandan chiqib ketadi -->
    <div class="relative mt-10 lg:mt-14">
      <div class="founders-track ml-[6vw] overflow-hidden lg:ml-[30vw]">
        <ul
          class="flex items-center gap-[var(--gap)] transition-transform duration-500 ease-out"
          :class="{ 'founders-snap': isSnapping }"
          :style="{ transform: `translateX(calc(${-position} * (var(--card) + var(--gap))))` }"
          @transitionend.self="normalize"
        >
          <li
            v-for="(founder, index) in loopItems"
            :key="`${founder.id}-${index}`"
            class="w-[var(--card)] shrink-0 transition duration-500 ease-out"
            :class="[
              index === position ? 'scale-100' : 'scale-[0.78]',
              index < position ? 'opacity-0' : 'opacity-100',
            ]"
          >
            <img
              v-if="founder.photo"
              :src="founder.photo"
              :alt="founder.full_name"
              loading="lazy"
              class="rounded-block bg-surface aspect-[3/4] w-full object-cover"
            />
          </li>
        </ul>
      </div>

      <!-- Ma'lumot kartochkasi: kontent chegarasidan boshlanib, faol suratga qisman tushadi -->
      <div class="lg:pointer-events-none lg:absolute lg:inset-0">
        <div class="container-page relative h-full">
          <article
            v-if="activeFounder"
            class="founder-card rounded-block mt-6 p-6 lg:pointer-events-auto lg:absolute lg:bottom-[12%] lg:left-0 lg:mt-0 lg:w-[26vw] lg:max-w-[27rem] lg:p-[1.9vw]"
          >
            <!-- Matn almashganda yumshoq o'tish -->
            <Transition name="founder" mode="out-in">
              <div :key="activeIndex">
                <p class="eyebrow">{{ activeFounder.position }}</p>

                <h3 class="font-wide mt-4 text-[1.25rem] font-bold text-white">
                  {{ activeFounder.full_name }}
                </h3>
                <p v-if="activeFounder.bio" class="text-body mt-3 leading-relaxed text-white/60">
                  {{ activeFounder.bio }}
                </p>
              </div>
            </Transition>

            <div class="mt-[2.5vw] flex items-end justify-between gap-4">
              <!-- Ikki yo'nalish: chapga — lenta odatdagidek suriladi,
                   o'ngga — teskarisi (surat chapdan chiqib, o'ngdan ketadi) -->
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="text-brand hover:bg-brand grid size-11 place-items-center rounded-full bg-white/[0.07] transition hover:text-white"
                  :aria-label="t('about.nextFounder')"
                  @click="goManually(1)"
                >
                  <svg class="size-4" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path
                      d="M9.5 3 4.5 8l5 5M4.5 8H13"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>

                <button
                  type="button"
                  class="text-brand hover:bg-brand grid size-11 place-items-center rounded-full bg-white/[0.07] transition hover:text-white"
                  :aria-label="t('about.prevFounder')"
                  @click="goManually(-1)"
                >
                  <svg class="size-4" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path
                      d="m6.5 3 5 5-5 5M11.5 8H3"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>
              </div>

              <p class="font-wide text-[1.6rem] leading-none font-bold" aria-live="polite">
                <span class="text-brand">{{ activeIndex + 1 }}</span>
                <span class="text-[0.75em] text-white/40">/{{ items.length }}</span>
              </p>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Lentadagi bitta surat kengligi: faol surat kattaroq, qo'shnilari kichrayadi */
.founders-track {
  --card: min(70vw, 16rem);
  --gap: 1rem;
}

@media (min-width: 1024px) {
  .founders-track {
    --card: 23vw;
    --gap: 1.25vw;
  }
}

/* O'rtadagi nusxaga qaytish — sakrash ko'rinmasligi uchun animatsiyasiz */
.founders-snap,
.founders-snap > li {
  transition: none !important;
}

/* Maketdagi shisha kartochka — orqadagi surat sal ko'rinib turadi */
.founder-card {
  border: 1px solid rgb(255 255 255 / 0.08);
  background: linear-gradient(135deg, rgb(255 255 255 / 0.09), rgb(255 255 255 / 0.03));
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.founder-enter-active,
.founder-leave-active {
  transition:
    opacity 0.28s ease,
    transform 0.28s ease;
}

.founder-enter-from {
  opacity: 0;
  transform: translateY(0.6rem);
}

.founder-leave-to {
  opacity: 0;
  transform: translateY(-0.6rem);
}

@media (prefers-reduced-motion: reduce) {
  .founder-enter-active,
  .founder-leave-active {
    transition: none;
  }
}
</style>
