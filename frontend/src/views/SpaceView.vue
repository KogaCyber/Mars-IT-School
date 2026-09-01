<script setup>
/** «SPACE» sahifasi — hero, imkoniyatlar, gamifikatsiya, premium, shop, ota-onalar va ariza bloklari. */
import { useI18n } from 'vue-i18n'

import SpaceApplicationSection from '@/components/space/SpaceApplicationSection.vue'
import SpaceFeaturesSection from '@/components/space/SpaceFeaturesSection.vue'
import SpaceGamificationSection from '@/components/space/SpaceGamificationSection.vue'
import SpaceShopSection from '@/components/space/SpaceShopSection.vue'
import SpacePremiumSection from '@/components/space/SpacePremiumSection.vue'
import SpaceParentsSection from '@/components/space/SpaceParentsSection.vue'
import SpaceHero from '@/components/space/SpaceHero.vue'
import { useSeo } from '@/composables/useSeo'

const { t } = useI18n()

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: 'SPACE', path: '/space' },
  ],
}))
</script>

<template>
  <SpaceHero />

  <SpaceFeaturesSection />

  <SpaceGamificationSection />

  <SpacePremiumSection />

  <SpaceShopSection />

  <SpaceParentsSection />

  <SpaceApplicationSection />
</template>
