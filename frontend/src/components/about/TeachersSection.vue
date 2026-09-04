<script setup>
/**
 * «Преподаватели, которые работают в IT».
 *
 * Figma: chapda yorliq va yirik sarlavha, o'ngda izoh; ostida o'qituvchi
 * kartochkalari bosh sahifadagidek cheksiz aylanuvchi karuselda.
 */
import { useI18n } from 'vue-i18n'

import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import TeacherCard from '@/components/cards/TeacherCard.vue'

const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-if="items.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <header class="grid gap-8 lg:grid-cols-[1.4fr_1fr] lg:items-end lg:gap-16">
        <div>
          <p class="eyebrow">{{ t('about.teachersEyebrow') }}</p>
          <h2 class="section-title mt-5 text-white">
            <span v-for="line in t('about.teachersTitle').split('\n')" :key="line" class="block">
              {{ line }}
            </span>
          </h2>
        </div>

        <p class="max-w-[44ch] text-[0.95rem] leading-relaxed text-white/60 lg:pb-2">
          {{ t('about.teachersText') }}
        </p>
      </header>
    </div>

    <!-- Kartochkalar cheksiz aylanadi -->
    <InfiniteCarousel class="mt-10 lg:mt-14" :speed="100">
      <div v-for="teacher in items" :key="teacher.id" class="w-[min(92vw,38rem)] shrink-0">
        <TeacherCard :teacher="teacher" />
      </div>
    </InfiniteCarousel>
  </section>
</template>
