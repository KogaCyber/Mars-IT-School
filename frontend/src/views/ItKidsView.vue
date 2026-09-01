<script setup>
/**
 * «Курсы / IT Kids» sahifasi.
 *
 * Kontent maketda qat'iy belgilangan (rasm ham loyiha ichida), shuning uchun
 * admin paneldan emas, `data/itKids.js` dan olinadi — `directions.js` bilan
 * bir xil yondashuv.
 */
import { useI18n } from 'vue-i18n'

import itKidsHero from '@/assets/images/It_kids_hero.png'
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
  IT_KIDS_FACTS,
  IT_KIDS_FAQ,
  IT_KIDS_GALLERY,
  IT_KIDS_STAGES,
  IT_KIDS_STAGES_SUMMARY,
  IT_KIDS_TOOLS,
  IT_KIDS_TOPICS,
} from '@/data/itKids'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

// Maketdagi kontent uch tilda yozilgan — joriy tilga ko'ra tanlanadi.
const facts = useLocalized(IT_KIDS_FACTS)
const topics = useLocalized(IT_KIDS_TOPICS)
const stages = useLocalized(IT_KIDS_STAGES)
const stagesSummary = useLocalized(IT_KIDS_STAGES_SUMMARY)
const gallery = useLocalized(IT_KIDS_GALLERY)
const faq = useLocalized(IT_KIDS_FAQ)

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('courses.breadcrumbHome'), path: '/' },
    { name: t('courses.breadcrumbCourses'), path: '/kursy' },
    { name: 'IT Kids', path: '/kursy/it-kids' },
  ],
  // Kurs kartasi + sahifadagi savol-javoblar — ikkalasi ham rich result beradi.
  schema: [
    courseSchema(
      {
        title: 'IT Kids',
        subtitle: t('courses.itKidsCourseSubtitle'),
        age_from: 9,
        age_to: 11,
        duration_months: 24,
        lessons_per_week: 2,
      },
      absoluteUrl('/kursy/it-kids'),
    ),
    faqSchema(faq.value),
  ],
}))
</script>

<template>
  <CourseHero
    :title="t('courses.itKidsHeroTitle').split('\n')"
    :breadcrumbs="[
      { label: t('courses.breadcrumbHome'), to: { name: 'home' } },
      { label: t('courses.breadcrumbCourses'), to: { name: 'courses' } },
      { label: 'IT Kids' },
    ]"
    :image="itKidsHero"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'course', kurs: 'it-kids' } }"
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
    :title="t('courses.itKidsAboutTitle')"
    :description="t('courses.itKidsAboutDescription')"
    :tools="IT_KIDS_TOOLS"
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

  <TrialLessonSection source="course" course-slug="it-kids" />

  <FaqSection :items="faq" />
</template>
