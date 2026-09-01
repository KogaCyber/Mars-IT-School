<script setup>
/**
 * «Вакансии» sahifasi.
 *
 * Yuqorida hero (yo'l, «Работа в MARS IT School» sarlavhasi va noutbukli
 * astronavt), ostida ochiq vakansiyalar kartochkalari. Ariza kartochkadagi
 * «Подать заявку» tugmasi orqali o'ngdan chiqadigan panelda to'ldiriladi.
 */
import { useI18n } from 'vue-i18n'

import vacanciesAstronaut from '@/assets/images/vacancies-astronaut.png'
import { fetchVacancies } from '@/api/vacancies'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import PageHero from '@/components/layout/PageHero.vue'
import VacanciesSection from '@/components/vacancies/VacanciesSection.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, jobPostingSchema } from '@/utils/schema'

const { t } = useI18n()

const { data: vacancies, isLoading } = useAsyncData(fetchVacancies, [])

useSeo(() => ({
  title: t('nav.vacancies'),
  description: t('vacancies.seoDescription'),
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.vacancies'), path: '/vakansii' },
  ],
  // Har bir vakansiya alohida `JobPosting` — Google Jobs shu formatni o'qiydi.
  schema: vacancies.value.map((vacancy) => jobPostingSchema(vacancy, absoluteUrl('/vakansii'))),
}))
</script>

<template>
  <PageHero
    :title="t('vacancies.heroTitle').split('\n')"
    :breadcrumbs="[
      { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
      { label: t('nav.vacancies') },
    ]"
    :image="vacanciesAstronaut"
    :description="t('vacancies.heroDescription')"
  />

  <div v-if="isLoading" class="bg-ink"><BaseSpinner /></div>

  <div v-else-if="!vacancies.length" class="section bg-ink">
    <div class="container-page">
      <BaseEmptyState
        :title="t('vacancies.emptyTitle')"
        :description="t('vacancies.emptyDescription')"
      />
    </div>
  </div>

  <VacanciesSection v-else :items="vacancies" />
</template>
