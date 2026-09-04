<script setup>
/**
 * Sahifa yo'li (breadcrumbs) — Figma: kapsula ko'rinishidagi yorliqlar,
 * oxirgisi (joriy sahifa) to'q sariq rangda.
 */
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  /** `[{ label, to }]` — oxirgi element joriy sahifa (`to` bo'lmaydi). */
  items: { type: Array, required: true },
})
</script>

<template>
  <nav :aria-label="t('cards.breadcrumbsLabel')">
    <!-- Joriy sahifa nomi uzun bo'lishi mumkin (masalan yangilik sarlavhasi):
         kichik ekranda kapsula butun ekranni egallab ketmasligi uchun matn
         qisqartiriladi, to'liq nomi esa `title` da qoladi. -->
    <ol data-no-reveal class="stagger flex min-w-0 flex-wrap items-center gap-2">
      <li v-for="(item, index) in items" :key="item.label" class="min-w-0 max-w-full">
        <RouterLink
          v-if="item.to"
          :to="item.to"
          class="bg-surface hover:bg-surface-2 text-small rounded-pill block max-w-full truncate px-[1.35em] py-[0.6em] text-white transition"
        >
          {{ item.label }}
        </RouterLink>

        <span
          v-else
          class="bg-brand text-small rounded-pill block max-w-[16rem] truncate px-[1.35em] py-[0.6em] text-white sm:max-w-[26rem] lg:max-w-[36rem]"
          :title="item.label"
          :aria-current="index === items.length - 1 ? 'page' : undefined"
        >
          {{ item.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>
