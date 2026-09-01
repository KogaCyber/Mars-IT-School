<script setup>
/**
 * «Курсы / IT-разработка» sahifasi.
 *
 * Kontent maketda qat'iy belgilangan (rasm ham loyiha ichida), shuning uchun
 * admin paneldan emas, `data/itDev.js` dan olinadi — `ItKidsView.vue` bilan
 * bir xil yondashuv.
 */
import { useI18n } from 'vue-i18n'

import itDevHero from '@/assets/images/It_dasturlash.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import CourseAboutSection from '@/components/courses/CourseAboutSection.vue'
import CourseFactsStrip from '@/components/courses/CourseFactsStrip.vue'
import CourseGallerySection from '@/components/courses/CourseGallerySection.vue'
import CourseHero from '@/components/courses/CourseHero.vue'
import CourseStagesSection from '@/components/courses/CourseStagesSection.vue'
import TrialLessonSection from '@/components/courses/TrialLessonSection.vue'
import FaqSection from '@/components/home/FaqSection.vue'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, courseSchema, faqSchema } from '@/utils/schema'
import {
  IT_DEV_FACTS,
  IT_DEV_FAQ,
  IT_DEV_GALLERY,
  IT_DEV_STAGES,
  IT_DEV_STAGES_SUMMARY,
  IT_DEV_TOOLS,
  IT_DEV_TOPICS,
} from '@/data/itDev'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

// Maketdagi kontent uch tilda yozilgan — joriy tilga ko'ra tanlanadi.
const facts = useLocalized(IT_DEV_FACTS)
const topics = useLocalized(IT_DEV_TOPICS)
const stages = useLocalized(IT_DEV_STAGES)
const stagesSummary = useLocalized(IT_DEV_STAGES_SUMMARY)
const gallery = useLocalized(IT_DEV_GALLERY)
const faq = useLocalized(IT_DEV_FAQ)

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('courses.breadcrumbHome'), path: '/' },
    { name: t('courses.breadcrumbCourses'), path: '/kursy' },
    { name: t('courses.itDevHeroTitle'), path: '/kursy/it-razrabotka' },
  ],
  schema: [
    courseSchema(
      {
        title: t('courses.itDevHeroTitle'),
        subtitle: t('courses.itDevCourseSubtitle'),
        age_from: 12,
        age_to: 17,
        duration_months: 24,
        lessons_per_week: 2,
      },
      absoluteUrl('/kursy/it-razrabotka'),
    ),
    faqSchema(faq.value),
  ],
}))
</script>

<template>
  <CourseHero
    :title="t('courses.itDevHeroTitle')"
    :description="t('courses.itDevHeroDescription')"
    :breadcrumbs="[
      { label: t('courses.breadcrumbHome'), to: { name: 'home' } },
      { label: t('courses.breadcrumbCourses'), to: { name: 'courses' } },
      { label: t('courses.itDevHeroTitle') },
    ]"
    :image="itDevHero"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'course', kurs: 'it-razrabotka' } }"
      >
        {{ t('common.trialLesson') }}
      </BaseButton>

      <BaseButton
        size="lg"
        variant="ghost"
        href="#programma"
        class="bg-surface hover:bg-surface-2 h-[3.5rem] lg:h-[4.17vw]"
      >
        {{ t('courses.programButton') }}
      </BaseButton>
    </template>
  </CourseHero>

  <CourseFactsStrip :facts="facts" />

  <CourseAboutSection
    :title="t('courses.itDevAboutTitle')"
    :description="t('courses.itDevAboutDescription')"
    :tools="IT_DEV_TOOLS"
    :topics="topics"
  />

  <CourseStagesSection
    id="programma"
    :title="t('courses.stagesTitle')"
    :description="t('courses.stagesDescription')"
    :summary="stagesSummary"
    :stages="stages"
  />

  <CourseGallerySection
    :title="t('courses.galleryTitle').split('\n')"
    :description="t('courses.galleryDescription')"
    :images="gallery"
  />

  <TrialLessonSection source="course" course-slug="it-razrabotka" />

  <FaqSection :items="faq" />
</template>
