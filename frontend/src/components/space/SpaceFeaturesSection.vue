<script setup>
/**
 * «Что умеет SPACE» — yorug' (oq) bo'lim.
 *
 * Maket: chapda izoh matni, markazda «Возможности» yorlig'i va yirik sarlavha;
 * ostida kartochkalar cheksiz karusel bo'lib chapga aylanib turadi (sichqoncha
 * ustiga kelganda yoki fokus tushganda to'xtaydi).
 *
 * Kartochka uslubi «О нас» sahifasidagi «Почему это важно для будущего» bilan
 * bir xil: gradientli oq kartochka, tepada ikonka, so'ng sarlavha va izoh.
 */
import { computed } from 'vue'

import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import { toCards, useSection } from '@/composables/useSection'
import { SPACE_FEATURES } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

// Blok matni va kartochkalari admin paneldan («SPACE» bo'limlari → «Imkoniyatlar»).
const section = useSection('space.features', {
  eyebrow: 'space.featuresEyebrow',
  title: 'space.featuresTitle',
  text: 'space.featuresText',
})
const fallback = useLocalized(SPACE_FEATURES)
const features = computed(() => toCards(section.value.items, fallback.value))

/** Kartochka ikonkalari — maketdagi chiziqli belgilar. */
const ICONS = {
  notes:
    'M6.5 7.5A2.5 2.5 0 0 1 9 5h6a2.5 2.5 0 0 1 2.5 2.5v9A2.5 2.5 0 0 1 15 19H9a2.5 2.5 0 0 1-2.5-2.5v-9ZM9.5 9.5h5M9.5 12.5h5M9.5 15.5h2.5',
  book: 'M12 7.6C10.5 6.4 8.6 5.8 6.4 5.8c-.5 0-.9.4-.9.9v9.6c0 .5.4.9.9.9 2.2 0 4.1.6 5.6 1.8 1.5-1.2 3.4-1.8 5.6-1.8.5 0 .9-.4.9-.9V6.7c0-.5-.4-.9-.9-.9-2.2 0-4.1.6-5.6 1.8Zm0 0v11.4',
  code: 'M6 8A2.5 2.5 0 0 1 8.5 5.5h7A2.5 2.5 0 0 1 18 8v5a2.5 2.5 0 0 1-2.5 2.5h-3L9 18.5v-3h-.5A2.5 2.5 0 0 1 6 13V8Zm4.4 1.6L8.6 11l1.8 1.4m3.2-2.8L15.4 11l-1.8 1.4',
  feed: 'M6.5 7.5A2.5 2.5 0 0 1 9 5h6a2.5 2.5 0 0 1 2.5 2.5v9A2.5 2.5 0 0 1 15 19H9a2.5 2.5 0 0 1-2.5-2.5v-9ZM9.5 9.5h5M9.5 12.5h5M9.5 15.5h3',
  card: 'M5 8.5A2.5 2.5 0 0 1 7.5 6h9A2.5 2.5 0 0 1 19 8.5v7a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 5 15.5v-7ZM5 10.5h14M8 14.5h3',
}
</script>

<template>
  <section v-reveal class="section bg-white">
    <div class="container-page">
      <!-- Sarlavha bloki: chapda izoh, markazda yorliq va sarlavha -->
      <header>
        <div class="lg:flex lg:items-center justify-between px-4.5 block">
          <div class="mb-10 lg:mb-0">
            <p class="eyebrow">{{ section.eyebrow }}</p>
            <h2 class="text-ink font-wide mt-5 font-bold text-5xl">
              <span
                v-for="line in section.titleLines"
                :key="line"
                class="block"
              >
                {{ line }}
              </span>
            </h2>
          </div>

          <p class="max-w-[34ch] leading-relaxed text-neutral-500">
            {{ section.text }}
          </p>
        </div>
      </header>
    </div>

    <!-- Kartochkalar: cheksiz aylanuvchi lenta -->
    <InfiniteCarousel :speed="55" class="mt-12 py-4 lg:mt-16">
      <article
        v-for="item in features"
        :key="item.id"
        class="group flex w-[18.5rem] shrink-0 flex-col rounded-[2rem] p-8 transition duration-300 hover:-translate-y-1.5 lg:min-h-[21rem]"
        style="
          background: linear-gradient(160deg, #fdfdff 0%, #ecebf6 45%, #f8e3da 100%);
          box-shadow: 0 20px 45px -32px rgba(36, 39, 84, 0.55);
        "
      >
        <!-- Ikonka yuqorida: kartochkaning vizual tayanchi -->
        <span
          class="text-brand grid size-12 place-items-center rounded-2xl bg-white/70 shadow-sm transition duration-300 group-hover:scale-105"
        >
          <svg class="size-6" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              :d="ICONS[item.icon] || ICONS.notes"
              stroke="currentColor"
              stroke-width="1.4"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>

        <h3 class="text-ink font-wide mt-7 text-[1.0625rem] leading-snug font-bold">
          {{ item.title }}
        </h3>

        <p class="mt-4 leading-relaxed text-neutral-500">{{ item.description }}</p>
      </article>
    </InfiniteCarousel>
  </section>
</template>

<style scoped>
/* Maketda bo'lim sarlavhasi boshqa sahifalarnikidan yirikroq */
.title-space {
  font-size: clamp(2.25rem, 5.5vw, 5.5rem);
  line-height: 1.02;
}
</style>
