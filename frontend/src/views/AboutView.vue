<script setup>
/**
 * «О нас» sahifasi.
 *
 * Hozircha ikki bo'lim tayyor: hero va «Почему это важно для будущего».
 * Qolgan bo'limlar («Какие навыки развивает ребёнок», «День, когда ребёнок
 * защищает свой проект», «Кто стоит за школой» va boshqalar) keyin qo'shiladi.
 */
import { useI18n } from 'vue-i18n'

import {
  fetchAdvantages,
  fetchChildSkills,
  fetchFutureBenefits,
  fetchProjectDefenceSteps,
  fetchFounders,
  fetchSchoolFeatures,
  fetchSiteSettings,
  fetchStatistics,
} from '@/api/site'
import { fetchTeachers } from '@/api/teachers'
import DemoDaySection from '@/components/about/DemoDaySection.vue'
import FoundersSection from '@/components/about/FoundersSection.vue'
import FutureSection from '@/components/about/FutureSection.vue'
import SchoolIntroSection from '@/components/about/SchoolIntroSection.vue'
import SkillsSection from '@/components/about/SkillsSection.vue'
import StatsBar from '@/components/about/StatsBar.vue'
import TeachersSection from '@/components/about/TeachersSection.vue'
import AdvantagesSection from '@/components/home/AdvantagesSection.vue'
import PageHero from '@/components/layout/PageHero.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSection } from '@/composables/useSection'
import { useSeo } from '@/composables/useSeo'
import { personSchema } from '@/utils/schema'

const { t } = useI18n()

const { data: advantages } = useAsyncData(fetchAdvantages, [])
const { data: futureBenefits } = useAsyncData(fetchFutureBenefits, [])
const { data: childSkills } = useAsyncData(fetchChildSkills, [])
const { data: defenceSteps } = useAsyncData(fetchProjectDefenceSteps, [])
const { data: statistics } = useAsyncData(fetchStatistics, [])
const { data: schoolFeatures } = useAsyncData(fetchSchoolFeatures, [])
const { data: settings } = useAsyncData(fetchSiteSettings, {})
const { data: founders } = useAsyncData(fetchFounders, [])
// `/teachers/` sahifalashsiz ishlaydi (backend: `pagination_class = None`) —
// ya'ni javob oddiy massiv. Ilgari bu yerda `.results` o'qilardi va natija
// `undefined` bo'lib, «Преподаватели» bo'limi sahifada UMUMAN ko'rinmasdi.
// Ikkala shakl ham qabul qilinadi: sahifalash qaytsa ham bo'lim ishlayveradi.
const { data: teachers } = useAsyncData(async () => {
  const response = await fetchTeachers()
  return Array.isArray(response) ? response : (response?.results ?? [])
}, [])

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.about'), path: '/o-nas' },
  ],
  /**
   * O'qituvchilar — `Person` tugunlari.
   *
   * «Kim dars beradi?» javob beruvchi tizimlarga eng ko'p beriladigan
   * savollardan biri, va jonli mutaxassislar ro'yxati maktabga bo'lgan
   * ishonch signalini (E-E-A-T) ko'taradi. Ilgari bu ma'lumot faqat
   * rasmlar va matn ichida edi — mashina uchun o'qilmasdi.
   */
  schema: (teachers.value || []).map(personSchema).filter(Boolean),
}))

// Sahifa tepasidagi sarlavha va rasm — admin paneldan
// («Biz haqimizda» bo'limlari → «Hero»).
const hero = useSection('about.hero', { title: 'about.heroTitle' })
</script>

<template>
  <PageHero
    v-if="hero.visible"
    :title="hero.titleLines"
    :breadcrumbs="[
      { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
      { label: t('nav.about') },
    ]"
    :image="hero.image || undefined"
  />

  <FutureSection :items="futureBenefits" />

  <SkillsSection :items="childSkills" />

  <DemoDaySection :items="defenceSteps" />

  <StatsBar :items="statistics" />

  <SchoolIntroSection
    :items="schoolFeatures"
    :video-url="settings.promo_video || settings.promo_video_url || ''"
    :video-cover="settings.promo_cover || ''"
  />

  <FoundersSection :items="founders" />

  <TeachersSection :items="teachers" />

  <AdvantagesSection :items="advantages" :show-link="false" />
</template>
