<script setup>
/**
 * «Направления» bo'limi — yo'nalish kartochkalari va ularning ostida
 * tayyorlanayotgan yo'nalishlar haqidagi «Скоро...» banneri.
 *
 * Kartochkalar admin paneldan keladi («Kurslar» sahifasi bo'limlari →
 * «Yo'nalishlar»). Admin panelda kartochka qo'shilmagan bo'lsa, maketdagi
 * ro'yxat ko'rsatiladi — bo'lim hech qachon bo'sh qolmaydi.
 */
import { computed } from 'vue'

import ComingSoonBanner from '@/components/courses/ComingSoonBanner.vue'
import DirectionCard from '@/components/courses/DirectionCard.vue'
import { useSection } from '@/composables/useSection'
import { DIRECTIONS } from '@/data/directions'
import { useLocalized } from '@/i18n/localize'

const section = useSection('courses.directions', { title: 'courses.directionsTitle' })
const fallback = useLocalized(DIRECTIONS)

/** `/kursy/it-kids` → `it-kids` */
const slugFromUrl = (url) => String(url || '').replace(/\/+$/, '').split('/').filter(Boolean).pop()

const directions = computed(() => {
  const items = section.value.items
  if (!items.length) return fallback.value

  return items.map((item) => {
    const slug = slugFromUrl(item.url)
    // Rasm admin panelda yuklanmagan bo'lsa — maketdagi rasm qoladi.
    const preset = fallback.value.find((direction) => direction.slug === slug)

    return {
      slug: slug || preset?.slug || '',
      title: item.title || preset?.title || '',
      subtitle: item.label || preset?.subtitle || '',
      description: item.text || preset?.description || '',
      ageRange: item.value || preset?.ageRange || '',
      image: item.image || preset?.image || '',
      tech: item.icon_name
        ? item.icon_name.split(',').map((key) => key.trim()).filter(Boolean)
        : (preset?.tech ?? []),
    }
  })
})
</script>

<template>
  <section class="section bg-ink">
    <div class="container-page">
      <h2 v-reveal class="title-hero font-wide font-bold text-white">
        {{ section.title }}
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
