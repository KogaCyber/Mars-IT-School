<script setup>
/**
 * «Новости» sahifasi.
 *
 * Bo'limlar: hero (yo'l, «Жизнь школы MARS IT» sarlavhasi va astronavt) va
 * «Что происходит в школе» — turkum bo'yicha filtrlanadigan yangiliklar ro'yxati.
 */
import { useI18n } from 'vue-i18n'

import newsAstronaut from '@/assets/images/news-astronaut.webp'
import PageHero from '@/components/layout/PageHero.vue'
import NewsListSection from '@/components/news/NewsListSection.vue'
import { useSeo } from '@/composables/useSeo'
import { useSection } from '@/composables/useSection'

const { t } = useI18n()

// Sahifa tepasidagi matn admin paneldan («Yangiliklar» sahifasi bo'limlari → «Hero»).
const hero = useSection('news.hero', {
  title: 'pages.newsHeroTitle',
  text: 'pages.newsHeroDescription',
})

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.news'), path: '/novosti' },
  ],
}))
</script>

<template>
  <PageHero
    :title="hero.titleLines"
    :breadcrumbs="[
      { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
      { label: t('nav.news') },
    ]"
    :image="hero.image || newsAstronaut"
    :description="hero.text"
  />

  <NewsListSection />
</template>
