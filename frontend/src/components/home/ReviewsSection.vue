<script setup>
/**
 * «Что говорят родители наших учеников» — video kartochkalar karuseli.
 *
 * Video havolasi bosilganda foydalanuvchi YouTube'ga o'tib ketmaydi —
 * rolik shu sahifadagi modal oyna ichida o'ynaydi.
 */
import { useI18n } from 'vue-i18n'

import reviewsBubble from '@/assets/images/reviews-bubble.webp'
import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import { isPlayable, openVideo } from '@/composables/useVideoModal'

const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-if="items.length" v-reveal class="section bg-ink overflow-hidden">
    <div class="container-page">
      <div class="grid items-center gap-[4%] lg:grid-cols-[1fr_auto_1.1fr]">
        <p class="max-w-sm leading-relaxed text-white/60">
          {{ t('home.reviewsText') }}
        </p>

        <img
          loading="lazy"
          decoding="async"
          :src="reviewsBubble"
          alt=""
          aria-hidden="true"
          class="animate-float hidden w-[8rem] lg:block xl:w-[10rem]"
        />

        <div>
          <p class="eyebrow">{{ t('home.reviewsEyebrow') }}</p>
          <h2 class="section-title mt-[3%] max-w-[14ch] text-white">
            {{ t('home.reviewsTitle') }}
          </h2>
        </div>
      </div>
    </div>

    <!-- Video kartochkalar cheksiz aylanadi -->
    <InfiniteCarousel class="mt-[6%]" :speed="110">
      <figure
        v-for="item in items"
        :key="item.id"
        class="rounded-block bg-surface group relative w-[min(70vw,16rem)] shrink-0 overflow-hidden"
      >
        <img
          v-if="item.photo"
          :src="item.photo"
          :alt="item.full_name"
          loading="lazy"
          class="aspect-[9/16] w-full object-cover transition duration-500 group-hover:scale-105"
        />

        <button
          v-if="isPlayable(item.video_url)"
          type="button"
          class="absolute inset-0 grid place-items-center transition duration-300 hover:bg-black/25"
          :aria-label="t('home.reviewVideo', { name: item.full_name })"
          @click="openVideo(item.video_url, item.full_name)"
        >
          <span
            class="bg-brand grid size-[3.5rem] place-items-center rounded-full text-white shadow-lg transition duration-300 group-hover:scale-110"
          >
            <svg
              class="size-[45%] translate-x-[8%]"
              viewBox="0 0 12 14"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M0 0l12 7-12 7z" />
            </svg>
          </span>
        </button>

        <figcaption class="p-[1.1rem]">
          <p class="font-wide font-bold text-white">{{ item.full_name }}</p>
          <p v-if="item.relation" class="text-small text-muted mt-1">{{ item.relation }}</p>
        </figcaption>
      </figure>
    </InfiniteCarousel>
  </section>
</template>
