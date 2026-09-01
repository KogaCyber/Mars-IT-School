<script setup>
/**
 * Yo'nalish kartochkasi — Figma: tepada rasm, so'ng nom, qisqa izoh va
 * tavsif; pastda texnologiya yorliqlari, «Подробнее» tugmasi va yosh yorlig'i.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'
import { TECH } from '@/data/directions'

const { t } = useI18n()

const props = defineProps({
  direction: { type: Object, required: true },
})

/** Noma'lum kalitlar tushib qolsin — maket buzilmaydi. */
const badges = computed(() => props.direction.tech.map((key) => TECH[key]).filter(Boolean))
</script>

<template>
  <article
    class="bg-surface rounded-block flex flex-col p-[4%] transition duration-300 hover:-translate-y-1 hover:bg-surface-2"
  >
    <div class="rounded-card overflow-hidden">
      <img
        :src="direction.image"
        :alt="direction.title"
        loading="lazy"
        class="aspect-[16/7] w-full object-cover"
      />
    </div>

    <h3 class="title-block font-wide mt-[6%] font-bold text-white">{{ direction.title }}</h3>

    <p class="font-wide mt-[2.5%] text-[var(--text-body)] font-bold text-white">
      {{ direction.subtitle }}
    </p>

    <p class="mt-[3.5%] line-clamp-2 text-[var(--text-body)] leading-relaxed text-white/45">
      {{ direction.description }}
    </p>

    <!-- Texnologiya yorliqlari -->
    <ul class="mt-[5%] flex flex-wrap gap-2">
      <li
        v-for="badge in badges"
        :key="badge.label"
        class="bg-ink rounded-pill flex items-center gap-2 px-[0.9em] py-[0.5em]"
      >
        <img
          loading="lazy"
          decoding="async"
          :src="badge.icon"
          :alt="''"
          aria-hidden="true"
          class="size-[1.4em] shrink-0"
        />
        <span class="text-[var(--text-small)] text-white">{{ badge.label }}</span>
      </li>
    </ul>

    <!-- Pastki qator: tugma va yosh — kartochkalar balandligi tenglashadi -->
    <div class="mt-auto flex items-center gap-3 pt-[6%]">
      <BaseButton size="lg" :to="`/kursy/${direction.slug}`" class="h-[3.25rem] flex-1">
        {{ t('common.more') }}
      </BaseButton>

      <span
        class="bg-ink rounded-pill flex h-[3.25rem] shrink-0 items-center px-[1.4em] text-[var(--text-body)] text-white"
      >
        {{ direction.ageRange }}
      </span>
    </div>
  </article>
</template>
