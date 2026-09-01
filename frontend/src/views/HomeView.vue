<script setup>
/** Bosh sahifa — Figma: «Главная». */
import { useI18n } from 'vue-i18n'

import { fetchNews } from '@/api/news'
import { fetchAdvantages, fetchFaqs, fetchParentReviews } from '@/api/site'
import { fetchTeachers } from '@/api/teachers'
import BaseButton from '@/components/base/BaseButton.vue'
import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import NewsCard from '@/components/cards/NewsCard.vue'
import TeacherCard from '@/components/cards/TeacherCard.vue'
import AdvantagesSection from '@/components/home/AdvantagesSection.vue'
import FaqSection from '@/components/home/FaqSection.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import ReviewsSection from '@/components/home/ReviewsSection.vue'
import SpaceSection from '@/components/home/SpaceSection.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, faqSchema, itemListSchema } from '@/utils/schema'

const { t } = useI18n()

const { data: advantages } = useAsyncData(fetchAdvantages, [])
const { data: reviews } = useAsyncData(fetchParentReviews, [])
const { data: faqs } = useAsyncData(fetchFaqs, [])
const { data: teachers } = useAsyncData(
  async () => (await fetchTeachers({ page_size: 12 })).results,
  [],
)
const { data: news } = useAsyncData(async () => (await fetchNews({ page_size: 9 })).results, [])

useSeo(() => ({
  title: t('seo.homeTitle'),
  description: t('seo.homeDescription'),
  // FAQ va yo'nalishlar ro'yxati — javob beruvchi tizimlar aynan shu
  // bo'laklarni iqtibos qiladi, shuning uchun ular strukturali ko'rinishda.
  schema: [
    faqSchema(faqs.value),
    itemListSchema(
      [
        {
          name: t('seo.itKidsName'),
          url: absoluteUrl('/kursy/it-kids'),
        },
        {
          name: t('seo.itDevName'),
          url: absoluteUrl('/kursy/it-razrabotka'),
        },
      ],
      { url: absoluteUrl('/'), name: t('seo.directionsList') },
    ),
  ],
}))
</script>

<template>
  <HeroSection />

  <AdvantagesSection :items="advantages" />

  <SpaceSection />

  <!-- «Что происходит в школе» — yangiliklar -->
  <section v-if="news.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ t('home.newsEyebrow') }}</p>

      <div class="mt-5 flex flex-wrap items-end justify-between gap-6">
        <h2 class="section-title text-white" v-html="t('home.newsTitle')" />
        <BaseButton :to="{ name: 'news' }" size="lg" class="font-wide font-bold">
          {{ t('home.newsAll') }}
        </BaseButton>
      </div>
    </div>

    <InfiniteCarousel class="mt-[6%]" :speed="120">
      <div v-for="item in news" :key="item.id" class="w-[min(85vw,22rem)] shrink-0">
        <NewsCard :item="item" />
      </div>
    </InfiniteCarousel>

    <div class="container-page"></div>
  </section>

  <!-- «Преподаватели, которые работают в IT» -->
  <section v-if="teachers.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ t('home.teamEyebrow') }}</p>

      <div class="mt-5 flex flex-wrap items-end justify-between gap-6">
        <h2 class="section-title text-white" v-html="t('home.teamTitle')" />
      </div>
    </div>

    <InfiniteCarousel class="mt-[6%]" :speed="100" direction="right">
      <div v-for="teacher in teachers" :key="teacher.id" class="w-[min(92vw,38rem)] shrink-0">
        <TeacherCard :teacher="teacher" />
      </div>
    </InfiniteCarousel>

    <div class="container-page"></div>
  </section>

  <ReviewsSection :items="reviews" />

  <FaqSection :items="faqs" />
</template>
