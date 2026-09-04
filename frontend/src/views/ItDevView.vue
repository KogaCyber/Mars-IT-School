<script setup>
/**
 * «Курсы / IT-разработка» sahifasi.
 *
 * Sahifaning barcha matni va rasmlari admin paneldan boshqariladi
 * («Kurs — IT dasturlash» bo'limlari). Admin panelda biror blok
 * to'ldirilmagan bo'lsa, maketdagi ma'lumot (`data/itDev.js`) ko'rsatiladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchCourse } from '@/api/courses'
import itDevHero from '@/assets/images/It_dasturlash.webp'
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
  IT_DEV_FACTS,
  IT_DEV_FAQ,
  IT_DEV_GALLERY,
  IT_DEV_STAGES,
  IT_DEV_STAGES_SUMMARY,
  IT_DEV_TOOLS,
  IT_DEV_TOPICS,
} from '@/data/itDev'
import { courseApiSlug } from '@/data/courseAliases'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

// Sahifa bloklari admin paneldan; maketdagi ma'lumot — zaxira.
const page = useCoursePage('itdev', {
  facts: IT_DEV_FACTS,
  topics: IT_DEV_TOPICS,
  stages: IT_DEV_STAGES,
  gallery: IT_DEV_GALLERY,
  summary: IT_DEV_STAGES_SUMMARY,
  heroTitleKey: 'courses.itDevHeroTitle',
  heroTextKey: 'courses.itDevHeroDescription',
  aboutTitleKey: 'courses.itDevAboutTitle',
  aboutTextKey: 'courses.itDevAboutDescription',
})
const { facts, topics, stageList: stages, galleryImages: gallery, stagesSummary } = page
// FAQ bloki admin paneldan boshqariladi: Kurslar → shu kurs → sahifa
// pastidagi «Savol-javoblar». Yozuv qo'shilmagan bo'lsa, maketdagi
// standart ro'yxat ko'rinadi — blok hech qachon bo'sh qolmaydi.
const staticFaq = useLocalized(IT_DEV_FAQ)
const { data: course } = useAsyncData(() => fetchCourse(courseApiSlug('it-razrabotka')), null)
const faq = computed(() => (course.value?.faqs?.length ? course.value.faqs : staticFaq.value))

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
    :title="page.hero.value.titleLines"
    :description="page.hero.value.text"
    :breadcrumbs="[
      { label: t('courses.breadcrumbHome'), to: { name: 'home' } },
      { label: t('courses.breadcrumbCourses'), to: { name: 'courses' } },
      { label: t('courses.itDevHeroTitle') },
    ]"
    :image="page.hero.value.image || itDevHero"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'course', kurs: 'it-razrabotka' } }"
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
    :tools="IT_DEV_TOOLS"
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

  <TrialLessonSection source="course" course-slug="it-razrabotka" />

  <FaqSection :items="faq" />
</template>
