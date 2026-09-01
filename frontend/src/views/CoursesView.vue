<script setup>
/**
 * «Курсы» sahifasi.
 *
 * Bo'limlar: hero (yo'l, sarlavha, tugma va astronavt), «Направления»
 * (yo'nalish kartochkalari + «Скоро...» banneri) va bepul sinov darsiga
 * ariza bloki. Qolganlari keyin qo'shiladi.
 */
import { useI18n } from 'vue-i18n'

import coursesAstronaut from '@/assets/images/kurslar_marsman.png'
import BaseButton from '@/components/base/BaseButton.vue'
import DirectionsSection from '@/components/courses/DirectionsSection.vue'
import TrialLessonSection from '@/components/courses/TrialLessonSection.vue'
import PageHero from '@/components/layout/PageHero.vue'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, itemListSchema } from '@/utils/schema'

const { t } = useI18n()

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('courses.coursesTitle'), path: '/kursy' },
  ],
  schema: itemListSchema(
    [
      { name: t('pages.itKidsShort'), url: absoluteUrl('/kursy/it-kids') },
      { name: t('pages.itDevShort'), url: absoluteUrl('/kursy/it-razrabotka') },
    ],
    { url: absoluteUrl('/kursy'), name: t('pages.coursesListName') },
  ),
}))
</script>

<template>
  <PageHero
    :title="t('pages.coursesHeroTitle').split('\n')"
    :breadcrumbs="[
      { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
      { label: t('courses.coursesTitle') },
    ]"
    :image="coursesAstronaut"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'courses' } }"
      >
        {{ t('common.trialLesson') }}
      </BaseButton>
    </template>
  </PageHero>

  <DirectionsSection />

  <TrialLessonSection />
</template>
