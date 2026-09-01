<script setup>
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'
import { formatDate } from '@/utils/format'

const { t } = useI18n()

defineProps({
  item: { type: Object, required: true },
})
</script>

<template>
  <article
    class="bg-surface hover:bg-surface-2 rounded-block group flex h-full flex-col overflow-hidden transition duration-300 hover:-translate-y-1"
  >
    <RouterLink
      :to="{ name: 'news-detail', params: { slug: item.slug } }"
      class="flex h-full flex-col"
    >
      <div v-if="item.cover" class="rounded-block bg-ink m-[4%] aspect-[16/11] overflow-hidden">
        <img
          :src="item.cover"
          :alt="item.title"
          loading="lazy"
          class="size-full object-cover transition duration-500 group-hover:scale-105"
        />
      </div>

      <div class="flex flex-1 flex-col px-[6%] pb-[6%]">
        <h3 class="title-block font-wide font-bold text-white">{{ item.title }}</h3>
        <p class="mt-[3%] line-clamp-2 flex-1 leading-relaxed text-white/60">{{ item.excerpt }}</p>

        <div class="mt-[8%] flex items-center justify-between gap-4">
          <!-- Sana yorlig'i -->
          <span class="bg-ink text-small rounded-pill px-[1.2em] py-[0.7em] text-white">
            {{ formatDate(item.published_at) }}
          </span>

          <BaseButton size="sm" class="pointer-events-none">{{ t('common.more') }}</BaseButton>
        </div>
      </div>
    </RouterLink>
  </article>
</template>
