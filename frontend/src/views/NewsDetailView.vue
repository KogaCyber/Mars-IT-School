<script setup>
/**
 * «Новость» sahifasi — Figma: tepada yo'l, chapda yopishib qoladigan ustun
 * (sana va «Поделиться»), o'ngda sarlavha, muqova va matn.
 *
 * Pastda «Фотоотчет» — cheksiz aylanuvchi surat lentasi; suratdagi «+» tugmasi
 * umumiy ko'ruvchida (`BaseLightbox`) to'liq ekranda ochadi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchNewsItem } from '@/api/news'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { openLightbox } from '@/composables/useLightbox'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, articleSchema } from '@/utils/schema'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/format'

const props = defineProps({
  slug: { type: String, required: true },
})

const { t } = useI18n()
const ui = useUiStore()

const slug = computed(() => props.slug)
const {
  data: news,
  isLoading,
  error,
} = useAsyncData(() => fetchNewsItem(slug.value), null, {
  watchSource: slug,
})

useSeo(() => ({
  title: news.value?.title,
  description: news.value?.excerpt,
  image: news.value?.cover,
  type: 'article',
  publishedAt: news.value?.published_at,
  modifiedAt: news.value?.updated_at || news.value?.published_at,
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.news'), path: '/novosti' },
    ...(news.value ? [{ name: news.value.title, path: `/novosti/${news.value.slug}` }] : []),
  ],
  schema: news.value ? articleSchema(news.value, absoluteUrl(`/novosti/${news.value.slug}`)) : null,
}))

/** Matn admin paneldan oddiy matn sifatida keladi — bo'sh qator = yangi abzats. */
const paragraphs = computed(() =>
  String(news.value?.body || '')
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter(Boolean),
)

/**
 * Sarlavha ostidagi kirish matni. Matnning birinchi abzatsi qisqa matn bilan
 * bir xil boshlansa, takrorlanmasligi uchun ko'rsatilmaydi.
 */
const lead = computed(() => {
  const excerpt = news.value?.excerpt?.trim()
  if (!excerpt) return ''
  const firstParagraph = paragraphs.value[0] || ''
  return firstParagraph.startsWith(excerpt.slice(0, 40)) ? '' : excerpt
})

/** Lightbox uchun galereya: `{ src, alt }` ko'rinishida. */
const galleryImages = computed(() =>
  (news.value?.gallery || []).map((image) => ({
    src: image.image,
    alt: image.caption || news.value?.title || '',
  })),
)

/** Ulashish: qurilma qo'llasa tizim oynasi, aks holda havola nusxalanadi. */
async function share() {
  const url = window.location.href
  const title = news.value?.title || document.title

  try {
    if (window.navigator.share) {
      await window.navigator.share({ title, text: news.value?.excerpt || '', url })
      return
    }
    await window.navigator.clipboard.writeText(url)
    ui.notify(t('news.linkCopied'))
  } catch (err) {
    // Foydalanuvchi oynani yopgan bo'lsa — bu xato emas, jim o'tamiz.
    if (err?.name !== 'AbortError') ui.notify(t('news.shareFailed'), 'error')
  }
}
</script>

<template>
  <BaseSpinner v-if="isLoading" />

  <div v-else-if="error || !news" class="container-page section">
    <BaseEmptyState :title="t('news.notFound')" :description="error || ''" />
  </div>

  <article v-else class="section bg-ink">
    <div class="container-page">
      <BaseBreadcrumbs
        :items="[
          { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
          { label: t('nav.news'), to: { name: 'news' } },
          { label: news.title },
        ]"
      />

      <div
        class="mt-[var(--spacing-block)] grid gap-[var(--spacing-block)] lg:grid-cols-[minmax(12rem,15rem)_minmax(0,1fr)] lg:gap-[6%]"
      >
        <!-- Chap ustun: sana va ulashish (katta ekranda yopishib qoladi) -->
        <aside class="flex flex-wrap gap-3 lg:sticky lg:top-28 lg:flex-col lg:self-start">
          <p
            class="bg-surface rounded-pill text-small flex items-center justify-between gap-3 px-[1.4em] py-[0.95em] font-medium text-white"
          >
            <span>{{ formatDate(news.published_at) }}</span>
            <svg
              class="text-brand size-[1.15em] shrink-0"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
            >
              <rect
                x="2.5"
                y="4"
                width="15"
                height="13.5"
                rx="3"
                stroke="currentColor"
                stroke-width="1.5"
              />
              <path
                d="M2.5 8h15M6.5 2.5V5M13.5 2.5V5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
          </p>

          <button
            type="button"
            class="bg-surface hover:bg-surface-2 rounded-pill text-small flex items-center justify-between gap-3 px-[1.4em] py-[0.95em] font-medium text-white transition"
            @click="share"
          >
            <span>{{ t('news.share') }}</span>
            <svg
              class="text-brand size-[1.15em] shrink-0"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
            >
              <circle cx="15" cy="4.5" r="2.5" stroke="currentColor" stroke-width="1.5" />
              <circle cx="5" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5" />
              <circle cx="15" cy="15.5" r="2.5" stroke="currentColor" stroke-width="1.5" />
              <path
                d="m7.3 8.8 5.4-3M7.3 11.2l5.4 3"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
          </button>

          <!-- Qo'shimcha ma'lumot: turkum, o'qish vaqti, ko'rishlar -->
          <dl
            class="rounded-block bg-surface text-small flex w-full flex-col gap-3 px-[1.4em] py-[1.2em] lg:w-auto"
          >
            <div v-if="news.category" class="flex items-center justify-between gap-4">
              <dt class="text-white/45">{{ t('news.category') }}</dt>
              <dd class="text-right font-medium text-white">{{ news.category.title }}</dd>
            </div>
            <div v-if="news.reading_minutes" class="flex items-center justify-between gap-4">
              <dt class="text-white/45">{{ t('news.reading') }}</dt>
              <dd class="font-medium text-white">
                {{ news.reading_minutes }} {{ t('news.readingMinutes') }}
              </dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-white/45">{{ t('news.views') }}</dt>
              <dd class="font-medium text-white">{{ news.views_count }}</dd>
            </div>
            <div v-if="galleryImages.length" class="flex items-center justify-between gap-4">
              <dt class="text-white/45">{{ t('news.photos') }}</dt>
              <dd class="font-medium text-white">{{ galleryImages.length }}</dd>
            </div>
          </dl>
        </aside>

        <!-- O'ng ustun: sarlavha, muqova va matn -->
        <div class="max-w-[52rem]">
          <h1 v-reveal class="title-hero font-wide font-bold text-white">{{ news.title }}</h1>

          <p
            v-if="lead"
            v-reveal="{ delay: 60 }"
            class="text-lead mt-[3%] max-w-[46rem] leading-relaxed text-white/55"
          >
            {{ lead }}
          </p>

          <img
            decoding="async"
            v-if="news.cover"
            v-reveal="{ delay: 100 }"
            :src="news.cover"
            :alt="news.title"
            fetchpriority="high"
            class="rounded-block mt-[var(--spacing-block)] aspect-[16/10] w-full cursor-zoom-in object-cover"
            @click="openLightbox([{ src: news.cover, alt: news.title }])"
          />

          <div
            v-reveal
            class="text-lead mt-[var(--spacing-block)] flex flex-col gap-[1.4em] leading-relaxed text-white/75"
          >
            <p v-for="(paragraph, index) in paragraphs" :key="index" class="whitespace-pre-line">
              {{ paragraph }}
            </p>
          </div>

          <!-- Fotoreportaj: uzluksiz aylanuvchi lenta -->
          <section v-if="galleryImages.length" class="mt-[var(--spacing-section)]">
            <h2 class="title-block font-wide font-bold text-white">{{ t('news.galleryTitle') }}</h2>

            <InfiniteCarousel class="mt-[var(--spacing-gutter)]" :speed="34">
              <figure
                v-for="(image, index) in galleryImages"
                :key="image.src"
                class="rounded-block group relative size-[min(72vw,16.5rem)] shrink-0 cursor-zoom-in overflow-hidden"
                @click="openLightbox(galleryImages, index)"
              >
                <img
                  :src="image.src"
                  :alt="image.alt"
                  loading="lazy"
                  class="size-full object-cover transition duration-500 group-hover:scale-[1.04]"
                />

                <button
                  type="button"
                  class="bg-brand hover:bg-brand-hover absolute right-[10%] bottom-[10%] grid size-[2.75rem] place-items-center rounded-full text-white transition duration-300 hover:scale-110 focus-visible:scale-110 lg:size-[3.25rem]"
                  :aria-label="
                    image.alt ? t('news.openPhotoNamed', { alt: image.alt }) : t('news.openPhoto')
                  "
                  @click.stop="openLightbox(galleryImages, index)"
                >
                  <svg class="size-[45%]" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                      d="M10 4v12M4 10h12"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </button>
              </figure>
            </InfiniteCarousel>
          </section>
        </div>
      </div>
    </div>
  </article>
</template>
