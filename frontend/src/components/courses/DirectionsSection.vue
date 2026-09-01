<script setup>
/**
 * «Направления» bo'limi — ikkita yo'nalish kartochkasi va ularning ostida
 * tayyorlanayotgan yo'nalishlar haqidagi «Скоро...» banneri.
 */
import { useI18n } from 'vue-i18n'

import ComingSoonBanner from '@/components/courses/ComingSoonBanner.vue'
import DirectionCard from '@/components/courses/DirectionCard.vue'
import { DIRECTIONS } from '@/data/directions'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()
const directions = useLocalized(DIRECTIONS)
</script>

<template>
  <section class="section bg-ink">
    <div class="container-page">
      <h2 v-reveal class="title-hero font-wide font-bold text-white">
        {{ t('courses.directionsTitle') }}
      </h2>

      <div
        v-reveal
        class="mt-[var(--spacing-block)] grid gap-[var(--spacing-gutter)] lg:grid-cols-2"
      >
        <DirectionCard
          v-for="direction in directions"
          :key="direction.slug"
          :direction="direction"
        />
      </div>

      <ComingSoonBanner v-reveal class="mt-[var(--spacing-gutter)]" />
    </div>
  </section>
</template>
