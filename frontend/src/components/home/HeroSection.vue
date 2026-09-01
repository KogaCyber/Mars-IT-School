<script setup>
/**
 * Bosh sahifa hero bloki — Figma: «Учимся создавать будущее».
 *
 * Rasm fon (absolute) emas, oddiy oqimdagi element: kichik ekranda matn
 * tepada, astronavt esa uning ostida ko'rinadi — matn ustiga tushmaydi.
 * Kata ekranda ikki ustunli tarmoqqa joylashadi.
 */
import { useI18n } from 'vue-i18n'

import heroAstronaut from '@/assets/images/hero-astronaut.webp'
import orbit1 from '@/assets/images/hero-orbit-1.svg'
import orbit2 from '@/assets/images/hero-orbit-2.svg'
import BaseButton from '@/components/base/BaseButton.vue'

const { t } = useI18n()
</script>

<template>
  <section class="bg-ink overflow-hidden">
    <div
      class="container-page grid items-center gap-[6%] pt-[8%] pb-[var(--spacing-section)] lg:min-h-[34rem] lg:grid-cols-[1.05fr_1fr] lg:gap-[4%] lg:pt-[4%]"
    >
      <!-- Matn -->
      <div class="order-1">
        <h1 v-reveal class="title-hero font-wide font-bold text-white">
          {{ t('home.heroTitle') }}
          <span class="sr-only">{{ t('home.heroTitleSr') }}</span>
        </h1>

        <p v-reveal="{ delay: 120 }" class="text-lead mt-[4%] leading-relaxed text-white">
          {{ t('home.heroText') }}
          <br />
          {{ t('home.heroTextSecond') }}
        </p>

        <div v-reveal="{ delay: 240 }" class="mt-[7%] flex flex-wrap gap-3">
          <BaseButton
            size="lg"
            class="h-[3.5rem] min-w-[15rem] font-wide font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
            :to="{ name: 'application', query: { source: 'home' } }"
          >
            {{ t('common.trialLesson') }}
          </BaseButton>

          <BaseButton
            size="lg"
            variant="ghost"
            :to="{ name: 'courses' }"
            class="bg-surface h-[3.5rem] min-w-[12rem] font-wide font-bold lg:h-[4.17vw] lg:min-w-[13vw]"
          >
            {{ t('common.viewCourses') }}
          </BaseButton>
        </div>
      </div>

      <!-- Rasm: mobil ekranda matndan keyin keladi -->
      <div class="relative order-2 mt-[8%] lg:mt-0" aria-hidden="true">
        <img
          decoding="async"
          :src="heroAstronaut"
          alt=""
          fetchpriority="high"
          class="animate-float mx-auto w-[78%] max-w-[32rem] object-contain sm:w-[62%] lg:w-full lg:max-w-none"
        />

        <img
          loading="lazy"
          decoding="async"
          :src="orbit1"
          alt=""
          class="animate-glow absolute top-[47%] left-[18%] hidden w-[58%] xl:block"
        />
        <img
          loading="lazy"
          decoding="async"
          :src="orbit2"
          alt=""
          class="animate-glow absolute top-[48%] left-0 hidden w-[58%] xl:block"
        />
      </div>
    </div>
  </section>
</template>
