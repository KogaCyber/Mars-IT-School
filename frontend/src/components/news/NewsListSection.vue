<script setup>
/**
 * «Что происходит в школе» — yangiliklar ro'yxati.
 *
 * Tepada bo'lim sarlavhasi va o'ng tomonda turkumlar bo'yicha segment-tugmalar
 * («Новости» / «Мероприятия» — turkumlar admin panelidan keladi).
 * Pastda ikki ustunli kartochkalar to'ri va sahifalash.
 */
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchNews, fetchNewsCategories } from '@/api/news'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import NewsCard from '@/components/cards/NewsCard.vue'
import { useAsyncData } from '@/composables/useAsyncData'

const { t } = useI18n()

/** Ikki ustunga tekis yotishi uchun juft son. */
const PAGE_SIZE = 8

const activeCategory = ref('')
const page = ref(1)
const gridRef = useTemplateRef('grid')

const query = computed(() => ({
  page: page.value,
  page_size: PAGE_SIZE,
  ...(activeCategory.value ? { category__slug: activeCategory.value } : {}),
}))

const { data: categories } = useAsyncData(fetchNewsCategories, [])

const emptyPage = { count: 0, next: null, previous: null, results: [] }
const { data: news, isLoading } = useAsyncData(() => fetchNews(query.value), emptyPage, {
  watchSource: query,
})

/** Segment-tugmalar: «Все» + turkumlar. Turkum bo'lmasa boshqaruv ko'rsatilmaydi. */
const tabs = computed(() =>
  categories.value.length
    ? [
        { slug: '', title: t('news.filterAll') },
        ...categories.value.map((c) => ({ slug: c.slug, title: c.title })),
      ]
    : [],
)

const totalPages = computed(() => Math.max(Math.ceil(news.value.count / PAGE_SIZE), 1))

/** Sahifa almashganda ro'yxat boshiga qaytamiz — foydalanuvchi «yo'qolib qolmaydi». */
function scrollToGrid() {
  gridRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function selectCategory(slug) {
  if (activeCategory.value === slug) return
  activeCategory.value = slug
  page.value = 1
}

function goToPage(value) {
  if (value < 1 || value > totalPages.value || value === page.value) return
  page.value = value
  scrollToGrid()
}
</script>

<template>
  <section class="section bg-ink">
    <div class="container-page">
      <div v-reveal class="flex flex-wrap items-end justify-between gap-x-10 gap-y-8">
        <div>
          <p class="eyebrow">{{ t('news.eyebrow') }}</p>
          <h2 class="section-title mt-5 text-white">
            <span v-for="line in t('news.title').split('\n')" :key="line" class="block">
              {{ line }}
            </span>
          </h2>
        </div>

        <!-- Turkum bo'yicha filtr: bitta kapsula ichidagi segmentlar -->
        <div
          v-if="tabs.length > 1"
          class="bg-surface rounded-pill flex w-full flex-wrap gap-1 p-1 sm:w-auto"
        >
          <button
            v-for="tab in tabs"
            :key="tab.slug || 'all'"
            type="button"
            class="rounded-pill text-small flex-1 px-[1.6em] py-[0.9em] font-medium whitespace-nowrap transition duration-200 sm:flex-none"
            :class="
              activeCategory === tab.slug
                ? 'bg-brand text-white'
                : 'text-white/55 hover:bg-surface-2 hover:text-white'
            "
            :aria-pressed="activeCategory === tab.slug"
            @click="selectCategory(tab.slug)"
          >
            {{ tab.title }}
          </button>
        </div>
      </div>

      <div ref="grid" class="scroll-mt-28">
        <BaseSpinner v-if="isLoading" />

        <BaseEmptyState
          v-else-if="!news.results.length"
          class="mt-[var(--spacing-block)]"
          :title="t('news.emptyTitle')"
          :description="t('news.emptyDescription')"
        />

        <div
          v-else
          class="mt-[var(--spacing-block)] grid gap-[var(--spacing-gutter)] md:grid-cols-2"
        >
          <NewsCard
            v-for="(item, index) in news.results"
            :key="item.id"
            v-reveal="{ delay: (index % 2) * 90 }"
            :item="item"
          />
        </div>
      </div>

      <!-- Sahifalash -->
      <nav
        v-if="totalPages > 1 && !isLoading"
        class="mt-[var(--spacing-block)] flex items-center justify-center gap-2"
        :aria-label="t('news.pagination')"
      >
        <button
          type="button"
          class="bg-surface hover:bg-surface-2 flex size-11 items-center justify-center rounded-full text-white transition disabled:pointer-events-none disabled:opacity-40"
          :disabled="page === 1"
          :aria-label="t('news.prevPage')"
          @click="goToPage(page - 1)"
        >
          ←
        </button>

        <button
          v-for="p in totalPages"
          :key="p"
          type="button"
          class="text-small size-11 rounded-full font-medium transition"
          :class="
            p === page
              ? 'bg-brand text-white'
              : 'bg-surface text-white/70 hover:bg-surface-2 hover:text-white'
          "
          :aria-current="p === page ? 'page' : undefined"
          @click="goToPage(p)"
        >
          {{ p }}
        </button>

        <button
          type="button"
          class="bg-surface hover:bg-surface-2 flex size-11 items-center justify-center rounded-full text-white transition disabled:pointer-events-none disabled:opacity-40"
          :disabled="page === totalPages"
          :aria-label="t('news.nextPage')"
          @click="goToPage(page + 1)"
        >
          →
        </button>
      </nav>
    </div>
  </section>
</template>
