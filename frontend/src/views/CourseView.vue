<script setup>
/** «Курс / …» sahifasi — bitta kurs. */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchCourse } from '@/api/courses'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import TeacherCard from '@/components/cards/TeacherCard.vue'
import FaqSection from '@/components/home/FaqSection.vue'
import LeadForm from '@/components/forms/LeadForm.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, courseSchema, faqSchema } from '@/utils/schema'
import { formatPrice } from '@/utils/format'

const { t } = useI18n()

const props = defineProps({
  slug: { type: String, required: true },
})

const slug = computed(() => props.slug)
const {
  data: course,
  isLoading,
  error,
} = useAsyncData(() => fetchCourse(slug.value), null, {
  watchSource: slug,
})

useSeo(() => ({
  title: course.value?.title,
  description: course.value?.subtitle,
  image: course.value?.hero_image || course.value?.card_image,
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('courses.coursesTitle'), path: '/kursy' },
    ...(course.value ? [{ name: course.value.title, path: `/kursy/${course.value.slug}` }] : []),
  ],
  // Kurs kartasi + sahifadagi savol-javoblar — ikkalasi ham rich result beradi.
  schema: course.value
    ? [
        courseSchema(course.value, absoluteUrl(`/kursy/${course.value.slug}`)),
        ...(course.value.faqs?.length ? [faqSchema(course.value.faqs)] : []),
      ]
    : null,
}))
</script>

<template>
  <BaseSpinner v-if="isLoading" :label="t('pages.courseLoading')" />

  <div v-else-if="error || !course" class="container-page section">
    <BaseEmptyState :title="t('pages.courseNotFound')" :description="error || ''" />
  </div>

  <template v-else>
    <!-- Hero -->
    <section class="relative overflow-hidden bg-ink">
      <div class="container-page grid gap-10 py-16 lg:grid-cols-2 lg:items-center lg:py-24">
        <div>
          <span
            class="inline-flex rounded-pill px-5 py-2 text-sm font-medium text-white"
            :style="{ backgroundColor: course.accent_color }"
          >
            {{ course.age_range }} {{ t('pages.courseAgeSuffix') }}
          </span>

          <h1 class="section-title mt-6 text-white">{{ course.title }}</h1>
          <p
            v-if="course.subtitle"
            class="mt-5 max-w-xl text-base leading-relaxed text-white/70 md:text-xl"
          >
            {{ course.subtitle }}
          </p>

          <dl class="mt-10 grid grid-cols-2 gap-6 md:grid-cols-4">
            <div>
              <dt class="text-sm text-muted">{{ t('pages.courseDuration') }}</dt>
              <dd class="mt-1 font-wide text-xl font-bold text-white">
                {{ course.duration_months }} {{ t('pages.courseMonths') }}
              </dd>
            </div>
            <div>
              <dt class="text-sm text-muted">{{ t('pages.coursePerWeek') }}</dt>
              <dd class="mt-1 font-wide text-xl font-bold text-white">
                {{ course.lessons_per_week }} {{ t('pages.courseLessonsCount') }}
              </dd>
            </div>
            <div>
              <dt class="text-sm text-muted">{{ t('pages.courseLesson') }}</dt>
              <dd class="mt-1 font-wide text-xl font-bold text-white">
                {{ course.lesson_duration_minutes }} {{ t('pages.courseMinutes') }}
              </dd>
            </div>
            <div v-if="course.price">
              <dt class="text-sm text-muted">{{ t('pages.coursePerMonth') }}</dt>
              <dd class="mt-1 font-wide text-xl font-bold text-white">
                {{ formatPrice(course.price) }} {{ t('pages.courseCurrency') }}
              </dd>
            </div>
          </dl>
        </div>

        <img
          loading="lazy"
          decoding="async"
          v-if="course.hero_image"
          :src="course.hero_image"
          :alt="course.title"
          class="w-full rounded-block object-cover"
        />
      </div>
    </section>

    <!-- Tavsif va imkoniyatlar -->
    <section class="section bg-ink">
      <div class="container-page grid gap-12 lg:grid-cols-[1fr_400px]">
        <div>
          <h2 class="title-block font-wide font-bold text-white">{{ t('pages.courseAbout') }}</h2>
          <p class="mt-5 whitespace-pre-line text-base leading-relaxed text-white/70">
            {{ course.description }}
          </p>

          <template v-if="course.features.length">
            <h2 class="title-block mt-[6%] font-wide font-bold text-white">
              {{ t('pages.courseFeatures') }}
            </h2>
            <ul class="mt-6 grid gap-4 md:grid-cols-2">
              <li
                v-for="feature in course.features"
                :key="feature.id"
                class="rounded-card bg-surface p-6"
              >
                <img
                  loading="lazy"
                  decoding="async"
                  v-if="feature.icon"
                  :src="feature.icon"
                  alt=""
                  aria-hidden="true"
                  class="mb-4 size-10"
                />
                <h3 class="font-wide text-lg font-bold text-white">{{ feature.title }}</h3>
                <p v-if="feature.description" class="mt-2 text-sm leading-relaxed text-white/60">
                  {{ feature.description }}
                </p>
              </li>
            </ul>
          </template>
        </div>

        <aside class="h-fit rounded-block bg-surface p-6 md:p-8">
          <h2 class="font-wide text-xl font-bold text-white">
            {{ t('pages.courseSignupTitle') }}
          </h2>
          <p class="mt-2 mb-6 text-sm text-white/60">{{ t('pages.courseSignupText') }}</p>
          <LeadForm
            source="course"
            :course-slug="course.slug"
            with-child-age
            :submit-label="t('pages.courseSignupSubmit')"
          />
        </aside>
      </div>
    </section>

    <!-- «Этапы обучения» -->
    <section v-if="course.stages.length" class="section bg-ink">
      <div class="container-page">
        <p class="eyebrow">{{ t('pages.courseProgramEyebrow') }}</p>
        <h2 class="section-title mt-5 text-white">{{ t('pages.courseStagesTitle') }}</h2>

        <ol class="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          <li
            v-for="(stage, index) in course.stages"
            :key="stage.id"
            class="rounded-block bg-surface p-6 md:p-8"
          >
            <span class="font-wide text-4xl font-bold text-brand">
              {{ stage.number || String(index + 1).padStart(2, '0') }}
            </span>
            <h3 class="mt-4 font-wide text-lg font-bold text-white">{{ stage.title }}</h3>
            <p v-if="stage.description" class="mt-3 text-sm leading-relaxed text-white/60">
              {{ stage.description }}
            </p>
            <p v-if="stage.duration_months" class="mt-4 text-sm text-muted">
              {{ stage.duration_months }} {{ t('pages.courseMonths') }}
            </p>
          </li>
        </ol>
      </div>
    </section>

    <!-- O'qituvchilar -->
    <section v-if="course.teachers.length" class="section bg-ink">
      <div class="container-page">
        <p class="eyebrow">{{ t('pages.courseTeamEyebrow') }}</p>
        <h2 class="section-title mt-5 text-white">{{ t('pages.courseTeachersTitle') }}</h2>

        <div class="mt-12 grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
          <TeacherCard v-for="teacher in course.teachers" :key="teacher.id" :teacher="teacher" />
        </div>
      </div>
    </section>

    <!-- «Частые вопросы» — admin panelda kursning o'z ichida tahrirlanadi -->
    <FaqSection v-if="course.faqs?.length" :items="course.faqs" />
  </template>
</template>
