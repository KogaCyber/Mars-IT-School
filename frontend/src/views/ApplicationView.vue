<script setup>
/**
 * «Заявка» sahifasi — saytdagi «Записаться на пробный урок» tugmalari shu
 * yerga olib keladi (avval modal oyna ochilardi).
 *
 * `?source=` va `?kurs=` so'rov parametrlari arizaning qayerdan kelganini
 * belgilaydi — masalan `/zayavka?source=course&kurs=it-kids`.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import TrialLessonSection from '@/components/courses/TrialLessonSection.vue'
import { useSeo } from '@/composables/useSeo'

const { t } = useI18n()
const route = useRoute()

const source = computed(() => String(route.query.source || 'popup'))
const courseSlug = computed(() => (route.query.kurs ? String(route.query.kurs) : null))

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('pages.applicationTitle'), path: '/zayavka' },
  ],
}))
</script>

<template>
  <TrialLessonSection :source="source" :course-slug="courseSlug" heading-level="h1" />
</template>
