<script setup>
/**
 * «Курсы / IT Kids» sahifasi.
 *
 * Sahifaning barcha matni va rasmlari admin paneldan boshqariladi
 * («Kurs — IT Kids» bo'limlari). Admin panelda biror blok to'ldirilmagan
 * bo'lsa, maketdagi ma'lumot (`data/itKids.js`) ko'rsatiladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchCourse } from '@/api/courses'
import itKidsHero from '@/assets/images/It_kids_hero.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import CourseAboutSection from '@/components/courses/CourseAboutSection.vue'
import CourseFactsStrip from '@/components/courses/CourseFactsStrip.vue'
import CourseGallerySection from '@/components/courses/CourseGallerySection.vue'
import CourseHero from '@/components/courses/CourseHero.vue'
import CourseStagesSection from '@/components/courses/CourseStagesSection.vue'
import TrialLessonSection from '@/components/courses/TrialLessonSection.vue'
import FaqSection from '@/components/home/FaqSection.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useCoursePage } from '@/composables/useCoursePage'
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
import { courseApiSlug } from '@/data/courseAliases'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

// Sahifa bloklari admin paneldan; maketdagi ma'lumot — zaxira.
const page = useCoursePage('itkids', {
  facts: IT_KIDS_FACTS,
  topics: IT_KIDS_TOPICS,
  stages: IT_KIDS_STAGES,
  gallery: IT_KIDS_GALLERY,
  summary: IT_KIDS_STAGES_SUMMARY,
  heroTitleKey: 'courses.itKidsHeroTitle',
  aboutTitleKey: 'courses.itKidsAboutTitle',
  aboutTextKey: 'courses.itKidsAboutDescription',
})
const { facts, topics, stageList: stages, galleryImages: gallery, stagesSummary } = page
// FAQ bloki admin paneldan boshqariladi: Kurslar → shu kurs → sahifa
// pastidagi «Savol-javoblar». Yozuv qo'shilmagan bo'lsa, maketdagi
// standart ro'yxat ko'rinadi — blok hech qachon bo'sh qolmaydi.
const staticFaq = useLocalized(IT_KIDS_FAQ)
const { data: course } = useAsyncData(() => fetchCourse(courseApiSlug('it-kids')), null)
const faq = computed(() => (course.value?.faqs?.length ? course.value.faqs : staticFaq.value))

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
    :title="page.hero.value.titleLines"
    :breadcrumbs="[
      { label: t('courses.breadcrumbHome'), to: { name: 'home' } },
      { label: t('courses.breadcrumbCourses'), to: { name: 'courses' } },
      { label: 'IT Kids' },
    ]"
    :image="page.hero.value.image || itKidsHero"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'course', kurs: 'it-kids' } }"
      >
        {{ page.hero.value.buttonLabel }}
      </BaseButton>

      <BaseButton
        size="lg"
        variant="ghost"
        href="#programma"
        class="bg-surface hover:bg-surface-2 h-[3.5rem] lg:h-[4.17vw]"
      >
        {{ page.hero.value.button2Label }}
      </BaseButton>
    </template>
  </CourseHero>

  <CourseFactsStrip :facts="facts" />

  <CourseAboutSection
    :eyebrow="page.about.value.eyebrow"
    :title="page.about.value.title"
    :description="page.about.value.text"
    :tools="IT_KIDS_TOOLS"
    :topics="topics"
  />

  <CourseStagesSection
    id="programma"
    :eyebrow="page.stages.value.eyebrow"
    :title="page.stages.value.title"
    :description="page.stages.value.text"
    :summary="stagesSummary"
    :stages="stages"
  />

  <CourseGallerySection
    :eyebrow="page.gallery.value.eyebrow"
    :title="page.gallery.value.titleLines"
    :description="page.gallery.value.text"
    :images="gallery"
  />

  <TrialLessonSection source="course" course-slug="it-kids" />

  <FaqSection :items="faq" />
</template>
