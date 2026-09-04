<script setup>
/**
 * «Space Premium — больше возможностей» — to'q (qora) bo'lim.
 *
 * Maketda imkoniyatlar bitta uzun ustunda edi va o'ng ustun bo'sh qolib
 * kompozitsiya og'ib ketardi. Shu sababli tuzilma qayta yig'ildi:
 *   1) tepada sarlavha bloki (chapda matn, o'ngda raketa),
 *   2) o'rtada imkoniyatlar to'ri — 4×2 kartochka,
 *   3) pastda kenglik bo'ylab cho'zilgan gradientli CTA paneli.
 * Shu tartibda o'qish yo'nalishi tabiiy va bo'sh joy qolmaydi.
 */
import { computed } from 'vue'

import rocket from '@/assets/images/rocket-3d.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import { toCards, useSection } from '@/composables/useSection'
import { SPACE_PREMIUM } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

// Blok matni va imkoniyatlari admin paneldan («SPACE» bo'limlari → «Premium»).
const section = useSection('space.premium', {
  eyebrow: 'space.premiumEyebrow',
  title: 'space.premiumTitle',
  text: 'space.premiumText',
  note: 'space.premiumNote',
  buttonLabel: 'space.premiumButton',
})
const fallback = useLocalized(SPACE_PREMIUM)
const premium = computed(() => toCards(section.value.items, fallback.value))

/** Kartochka ikonkalari — chiziqli, maketdagi uslubda. */
const ICONS = {
  coins:
    'M4.5 7.2c0-1.3 2.9-2.4 6.5-2.4s6.5 1.1 6.5 2.4-2.9 2.4-6.5 2.4-6.5-1.1-6.5-2.4ZM4.5 7.2v4c0 1.3 2.9 2.4 6.5 2.4M17.5 7.2v3M8.5 13.6c0-1.3 2.9-2.4 6.5-2.4s6.5 1.1 6.5 2.4-2.9 2.4-6.5 2.4-6.5-1.1-6.5-2.4ZM8.5 13.6v4c0 1.3 2.9 2.4 6.5 2.4s6.5-1.1 6.5-2.4v-4',
  code: 'M6 8A2.5 2.5 0 0 1 8.5 5.5h7A2.5 2.5 0 0 1 18 8v5a2.5 2.5 0 0 1-2.5 2.5h-3L9 18.5v-3h-.5A2.5 2.5 0 0 1 6 13V8Zm4.4 1.6L8.6 11l1.8 1.4m3.2-2.8L15.4 11l-1.8 1.4',
  book: 'M12 7.6C10.5 6.4 8.6 5.8 6.4 5.8c-.5 0-.9.4-.9.9v9.6c0 .5.4.9.9.9 2.2 0 4.1.6 5.6 1.8 1.5-1.2 3.4-1.8 5.6-1.8.5 0 .9-.4.9-.9V6.7c0-.5-.4-.9-.9-.9-2.2 0-4.1.6-5.6 1.8Zm0 0v11.4',
  robot:
    'M7.5 9h9a2 2 0 0 1 2 2v5.5a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2V11a2 2 0 0 1 2-2ZM12 5v4M10 13h.01M14 13h.01M10 16h4M3.5 12v3M20.5 12v3',
  badge:
    'm12 3.6 2.1 1.5 2.6-.2.8 2.5 2.2 1.4-.9 2.4.9 2.4-2.2 1.4-.8 2.5-2.6-.2L12 20.4l-2.1-1.5-2.6.2-.8-2.5-2.2-1.4.9-2.4-.9-2.4 2.2-1.4.8-2.5 2.6.2L12 3.6ZM9.6 12.2l1.7 1.7 3.3-3.6',
  palette:
    'M12 4.5a7.5 7.5 0 0 0 0 15c1.2 0 1.9-.8 1.9-1.7 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-.9.8-1.7 1.7-1.7h1.1a3.8 3.8 0 0 0 3.8-3.8c0-3.1-3.4-5.4-7.5-5.4ZM8 11.2h.01M10.4 8.2h.01M14 8.2h.01M16.6 10.6h.01',
  keyboard:
    'M4 8.5A1.5 1.5 0 0 1 5.5 7h13A1.5 1.5 0 0 1 20 8.5v7a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 15.5v-7ZM7 10h.01M10 10h.01M13 10h.01M16 10h.01M7 12.6h.01M10 12.6h.01M13 12.6h.01M16 12.6h.01M9 15.2h6',
  feed: 'M6.5 7.5A2.5 2.5 0 0 1 9 5h6a2.5 2.5 0 0 1 2.5 2.5v9A2.5 2.5 0 0 1 15 19H9a2.5 2.5 0 0 1-2.5-2.5v-9ZM9.5 9.5h5M9.5 12.5h5M9.5 15.5h3',
}
</script>

<template>
  <section v-reveal class="section bg-ink relative overflow-hidden">
    <!-- Fon: markazdan taralayotgan issiq nur -->
    <div class="premium-glow pointer-events-none absolute inset-0" aria-hidden="true" />

    <div class="container-page relative">
      <!-- 1. Sarlavha bloki -->
      <header class="grid items-center gap-10 lg:grid-cols-[1.25fr_1fr] lg:gap-16">
        <div>
          <p class="eyebrow">{{ section.eyebrow }}</p>

          <h2 class="title-premium font-wide mt-6 font-bold text-white">
            <span v-for="line in section.titleLines" :key="line" class="block">
              {{ line }}
            </span>
          </h2>

          <p class="text-brand text-lead font-wide mt-7 max-w-[40ch] leading-relaxed font-bold">
            {{ section.text }}
          </p>
        </div>

        <!-- Raketa: maketdagi kabi sarlavhaning o'ng tomonida -->
        <div class="relative hidden lg:block" aria-hidden="true">
          <img
            loading="lazy"
            decoding="async"
            :src="section.image || rocket"
            alt=""
            class="animate-float mx-auto w-[68%] max-w-80 object-contain"
          />
        </div>
      </header>

      <!-- 2. Imkoniyatlar to'ri -->
      <ul class="mt-14 grid gap-4 sm:grid-cols-2 lg:mt-16 lg:grid-cols-4">
        <li
          v-for="item in premium"
          :key="item.id"
          class="group flex flex-col rounded-[1.75rem] border border-white/10 bg-white/[0.05] p-6 backdrop-blur-sm transition duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.08]"
        >
          <span class="text-white/30 transition-colors duration-300 group-hover:text-brand">
            <svg class="size-8" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                :d="ICONS[item.icon] || ICONS.coins"
                stroke="currentColor"
                stroke-width="1.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>

          <h3 class="font-wide mt-6 text-[1.0625rem] leading-snug font-bold text-white">
            {{ item.title }}
          </h3>

          <p class="mt-3 leading-relaxed text-white/55">{{ item.description }}</p>
        </li>
      </ul>

      <!-- 3. CTA paneli -->
      <div
        class="mt-14 flex flex-col gap-8 rounded-[2.5rem] p-8 md:flex-row md:items-center md:justify-between md:gap-12 lg:mt-16 lg:p-12"
        style="background: linear-gradient(100deg, #e2451f 0%, #a63a5a 55%, #3b2f7a 100%)"
      >
        <div>
          <span
            class="font-wide inline-flex items-center gap-2 rounded-pill bg-white/20 px-5 py-2.5 text-white"
          >
            <svg class="size-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M4.5 7.5 8 11l4-5.5 4 5.5 3.5-3.5-1.4 9H5.9L4.5 7.5ZM6 19.5h12"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            Space Premium
          </span>

          <p class="mt-5 max-w-[52ch] leading-relaxed text-white/80">
            {{ section.note }}
          </p>
        </div>

        <BaseButton
          size="lg"
          class="font-wide h-[3.5rem] shrink-0 bg-ink font-bold hover:bg-ink/85 md:min-w-[15rem]"
          :to="{ name: 'application', query: { source: 'space-premium' } }"
        >
          {{ section.buttonLabel }}
        </BaseButton>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha bo'lim sarlavhalaridan ancha yirik */
.title-premium {
  font-size: clamp(2.25rem, 5vw, 4.75rem);
  line-height: 1.03;
}

/* Chap yuqoridan taralayotgan issiq nur — maketdagi fon effekti */
.premium-glow {
  background:
    radial-gradient(42rem 32rem at 12% 22%, rgba(226, 69, 31, 0.28), transparent 70%),
    radial-gradient(38rem 30rem at 85% 70%, rgba(59, 47, 122, 0.35), transparent 72%);
}
</style>
