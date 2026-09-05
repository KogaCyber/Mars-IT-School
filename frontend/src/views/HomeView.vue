<script setup>
/** Bosh sahifa — Figma: «Главная». */
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchHome } from '@/api/site'
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
import { useSection } from '@/composables/useSection'
import { useSeo } from '@/composables/useSeo'
import { useContentStore } from '@/stores/content'
import { absoluteUrl, faqSchema, itemListSchema } from '@/utils/schema'

const { t } = useI18n()

// Bosh sahifaning butun kontenti bitta so'rovda keladi (`/api/v1/home/`) —
// ilgari bu 5 ta alohida so'rov edi va har biri backend javobini kutardi.
const EMPTY_HOME = { advantages: [], reviews: [], faqs: [], teachers: [], news: [] }
const { data: home } = useAsyncData(fetchHome, EMPTY_HOME)

// Bosh sahifa bloklarining matni shu javobda ham keladi — bo'limlar
// do'koniga qo'shamiz, shunda kontent alohida so'rovni kutmasdan chiqadi.
const content = useContentStore()
watch(home, (value) => content.merge(value?.sections), { immediate: true })

// Yangiliklar va o'qituvchilar lentalari tepasidagi matn (admin paneldan).
const newsSection = useSection('home.news', {
  eyebrow: 'home.newsEyebrow',
  title: 'home.newsTitle',
  buttonLabel: 'home.newsAll',
})
const teamSection = useSection('home.team', {
  eyebrow: 'home.teamEyebrow',
  title: 'home.teamTitle',
})

const advantages = computed(() => home.value.advantages ?? [])
const reviews = computed(() => home.value.reviews ?? [])
const faqs = computed(() => home.value.faqs ?? [])
const teachers = computed(() => home.value.teachers ?? [])
const news = computed(() => home.value.news ?? [])

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
  <section v-if="newsSection.visible && news.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ newsSection.eyebrow }}</p>

      <div class="mt-5 flex flex-wrap items-end justify-between gap-6">
        <h2 class="section-title text-white">
          <span v-for="line in newsSection.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>
        <BaseButton :to="{ name: 'news' }" size="lg" class="font-wide font-bold">
          {{ newsSection.buttonLabel }}
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
  <section v-if="teamSection.visible && teachers.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ teamSection.eyebrow }}</p>

      <div class="mt-5 flex flex-wrap items-end justify-between gap-6">
        <h2 class="section-title text-white">
          <span v-for="line in teamSection.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>
      </div>
    </div>

    <InfiniteCarousel class="mt-[6%]" :speed="100">
      <div v-for="teacher in teachers" :key="teacher.id" class="w-[min(92vw,38rem)] shrink-0">
        <TeacherCard :teacher="teacher" />
      </div>
    </InfiniteCarousel>

    <div class="container-page"></div>
  </section>

  <ReviewsSection :items="reviews" />

  <FaqSection :items="faqs" />
</template>
