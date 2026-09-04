<script setup>
/** «Контакты / Филиал» — bitta filial sahifasi. */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchBranch } from '@/api/branches'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import LeadForm from '@/components/forms/LeadForm.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { openLightbox } from '@/composables/useLightbox'
import { useSeo } from '@/composables/useSeo'
import { absoluteUrl, branchSchema } from '@/utils/schema'

const { t } = useI18n()

const props = defineProps({
  slug: { type: String, required: true },
})

const slug = computed(() => props.slug)
const {
  data: branch,
  isLoading,
  error,
} = useAsyncData(() => fetchBranch(slug.value), null, {
  watchSource: slug,
})

useSeo(() => ({
  title: branch.value?.name ? t('contacts.branchSeoTitle', { name: branch.value.name }) : undefined,
  description: branch.value
    ? t('contacts.branchSeoDescription', {
        name: branch.value.name,
        address: branch.value.address || t('contacts.branchDefaultCity'),
      })
    : undefined,
  // Filial o'chirilgan bo'lsa sahifa baribir HTTP 200 qaytaradi (SPA) —
  // Google uchun bu "yumshoq 404". Kontent yo'q ekan, indekslanmasin.
  noindex: !branch.value,
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.contacts'), path: '/kontakty' },
    ...(branch.value ? [{ name: branch.value.name, path: `/kontakty/${branch.value.slug}` }] : []),
  ],
  // Filial — lokal qidiruv uchun asosiy signal (manzil + koordinata).
  schema: branch.value
    ? branchSchema(branch.value, absoluteUrl(`/kontakty/${branch.value.slug}`))
    : null,
}))

/** Filial suratlari — bosilganda umumiy ko'ruvchida ochiladi. */
const galleryImages = computed(() =>
  (branch.value?.gallery || []).map((image) => ({ src: image.image, alt: branch.value?.name })),
)
</script>

<template>
  <BaseSpinner v-if="isLoading" />

  <div v-else-if="error || !branch" class="container-page section">
    <BaseEmptyState :title="t('contacts.branchNotFound')" :description="error || ''" />
  </div>

  <div v-else class="section bg-ink">
    <div class="container-page grid gap-12 lg:grid-cols-[1fr_420px] lg:items-start">
      <div>
        <p class="eyebrow">{{ t('contacts.branchEyebrow') }}</p>
        <h1 class="section-title mt-5 text-white">{{ branch.name }}</h1>

        <dl class="mt-8 flex flex-col gap-4 text-base text-white/70">
          <div>
            <dt class="text-sm text-muted">{{ t('contacts.branchAddress') }}</dt>
            <dd class="mt-1 text-white">{{ branch.address }}</dd>
          </div>
          <div v-if="branch.landmark">
            <dt class="text-sm text-muted">{{ t('contacts.branchLandmark') }}</dt>
            <dd class="mt-1 text-white">{{ branch.landmark }}</dd>
          </div>
          <div v-if="branch.working_hours">
            <dt class="text-sm text-muted">{{ t('contacts.branchHours') }}</dt>
            <dd class="mt-1 text-white">{{ branch.working_hours }}</dd>
          </div>
          <div v-if="branch.phone">
            <dt class="text-sm text-muted">{{ t('contacts.branchPhone') }}</dt>
            <dd class="mt-1">
              <a
                :href="`tel:${branch.phone.replace(/[^\d+]/g, '')}`"
                class="text-white transition hover:text-brand"
              >
                {{ branch.phone }}
              </a>
            </dd>
          </div>
        </dl>

        <ul v-if="branch.gallery.length" class="mt-12 grid gap-4 sm:grid-cols-2">
          <li v-for="(image, index) in branch.gallery" :key="image.id">
            <button
              type="button"
              class="rounded-card group block w-full cursor-zoom-in overflow-hidden"
              :aria-label="t('contacts.branchPhoto', { index: index + 1 })"
              @click="openLightbox(galleryImages, index)"
            >
              <img
                :src="image.image"
                :alt="branch.name"
                loading="lazy"
                class="aspect-[4/3] w-full object-cover transition duration-500 group-hover:scale-[1.04]"
              />
            </button>
          </li>
        </ul>
      </div>

      <aside class="rounded-block bg-surface p-6 md:p-8">
        <h2 class="font-wide text-xl font-bold text-white">{{ t('contacts.branchSignup') }}</h2>
        <LeadForm
          class="mt-6"
          source="contacts"
          :branch-slug="branch.slug"
          with-child-age
          :submit-label="t('contacts.branchSignupSubmit')"
        />
      </aside>
    </div>
  </div>
</template>
