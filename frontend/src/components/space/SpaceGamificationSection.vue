<script setup>
/**
 * «Учиться — это увлекательно» — to'q (qora) bo'lim.
 *
 * Maket: chapda yorliq, yirik sarlavha va izoh; o'ngda to'rtta kapsula
 * ko'rinishidagi kartochka (o'ng chetida yirik chiziqli ikonka).
 * Orqa fonda to'q sariq nur va uchib yurgan «raketa-tanga»lar.
 */
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import coinBlur from '@/assets/images/coin-blur.webp'
import coinFront from '@/assets/images/coin-front.webp'
import coinSide from '@/assets/images/coin-side.webp'
import coinTilt from '@/assets/images/coin-tilt.webp'
import { SPACE_GAMIFICATION } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()
const gamification = useLocalized(SPACE_GAMIFICATION)

/** Kartochka ikonkalari — maketdagi chiziqli belgilar. */
const ICONS = {
  coins:
    'M4.5 7.2c0-1.3 2.9-2.4 6.5-2.4s6.5 1.1 6.5 2.4-2.9 2.4-6.5 2.4-6.5-1.1-6.5-2.4ZM4.5 7.2v4c0 1.3 2.9 2.4 6.5 2.4M17.5 7.2v3M8.5 13.6c0-1.3 2.9-2.4 6.5-2.4s6.5 1.1 6.5 2.4-2.9 2.4-6.5 2.4-6.5-1.1-6.5-2.4ZM8.5 13.6v4c0 1.3 2.9 2.4 6.5 2.4s6.5-1.1 6.5-2.4v-4',
  flame:
    'M12 3.5s5.5 4 5.5 8.7a5.5 5.5 0 1 1-11 0c0-1.9.9-3.6 1.9-4.9.4 1.2 1.2 2.1 2.1 2.1 1.4 0 1.9-2 1.5-5.9ZM12 20a2.7 2.7 0 0 0 2.7-2.7c0-1.7-2.7-4.1-2.7-4.1s-2.7 2.4-2.7 4.1A2.7 2.7 0 0 0 12 20Z',
  trophy:
    'M7 4.5h10v4.2a5 5 0 0 1-10 0V4.5ZM7 6H4.2v1.3A3 3 0 0 0 7 10.3M17 6h2.8v1.3A3 3 0 0 1 17 10.3M12 13.7V17M8.5 20h7M9.5 17h5',
  gamepad:
    'M8 8.5h8a4.5 4.5 0 0 1 4.5 4.5v.7A3.8 3.8 0 0 1 16.7 17c-1 0-1.9-.5-2.5-1.3h-4.4c-.6.8-1.5 1.3-2.5 1.3A3.8 3.8 0 0 1 3.5 13.7V13A4.5 4.5 0 0 1 8 8.5ZM7.5 11.5v2.2M6.4 12.6h2.2M15.8 11.8h.01M17.6 13.4h.01',
}
</script>

<template>
  <section v-reveal class="section bg-ink relative overflow-hidden">
    <!-- Fon nuri -->
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="pointer-events-none absolute top-1/2 left-1/2 w-[150%] max-w-none -translate-x-1/2 -translate-y-1/2 opacity-80 select-none lg:w-[85%]"
    />

    <!-- Uchib yurgan «raketa-tanga»lar: maketdagi to'rttala tanga -->
    <div class="pointer-events-none absolute inset-0 select-none" aria-hidden="true">
      <!-- Katta tanga — sarlavha ustida -->
      <img
        loading="lazy"
        decoding="async"
        :src="coinFront"
        alt=""
        class="animate-float absolute top-[14%] left-[34%] w-[17%] max-w-45 -rotate-[8deg]"
      />

      <!-- Harakatdagi tanga (qirrasi bilan) — tepada -->
      <img
        loading="lazy"
        decoding="async"
        :src="coinBlur"
        alt=""
        class="coin-slow animate-float absolute top-[2%] left-[50%] w-[7%] max-w-20 rotate-[8deg]"
      />

      <!-- Yon tomondan ko'ringan tanga — birinchi kartochka burchagida -->
      <img
        loading="lazy"
        decoding="async"
        :src="coinSide"
        alt=""
        class="coin-slow animate-float absolute top-[3%] right-[9%] hidden w-[8%] max-w-26 rotate-[14deg] lg:block"
      />

      <!-- Kichik qiya tanga — pastda -->
      <img
        loading="lazy"
        decoding="async"
        :src="coinTilt"
        alt=""
        class="animate-float absolute bottom-[14%] left-[42%] w-[8%] max-w-24 -rotate-[10deg]"
      />
    </div>

    <div class="container-page relative grid gap-12 lg:grid-cols-2 lg:items-center lg:gap-16">
      <!-- Matn -->
      <div>
        <p class="eyebrow">{{ t('space.gamificationEyebrow') }}</p>

        <h2 class="title-gamification font-wide mt-6 font-bold text-white">
          {{ t('space.gamificationTitle') }}
        </h2>

        <p class="mt-8 max-w-[46ch] leading-relaxed text-white/70">
          {{ t('space.gamificationText') }}
        </p>
      </div>

      <!-- Kartochkalar -->
      <ul class="flex flex-col gap-4">
        <li
          v-for="item in gamification"
          :key="item.id"
          class="group flex items-center justify-between gap-6 rounded-[2.5rem] border border-white/10 bg-white/[0.05] px-8 py-7 backdrop-blur-sm transition duration-300 hover:bg-white/[0.08]"
        >
          <div class="min-w-0">
            <h3 class="font-wide text-[1.0625rem] font-bold text-white">{{ item.title }}</h3>
            <p class="mt-2 leading-relaxed text-white/60">{{ item.description }}</p>
          </div>

          <span
            class="shrink-0 text-white/25 transition-colors duration-300 group-hover:text-white"
          >
            <svg class="size-11" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                :d="ICONS[item.icon] || ICONS.coins"
                stroke="currentColor"
                stroke-width="1.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha bo'lim sarlavhalaridan ancha yirik */
.title-gamification {
  font-size: clamp(2.25rem, 5.2vw, 5rem);
  line-height: 1.05;
}

/* Kichik tangalar sekinroq va boshqa fazada suzadi */
.coin-slow {
  animation-duration: 11s;
  animation-delay: -3s;
}
</style>
