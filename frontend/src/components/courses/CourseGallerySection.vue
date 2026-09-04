<script setup>
/**
 * «Галерея» bo'limi — Figma: oq fonda chapda qisqa izoh, markazda yorliq va
 * yirik sarlavha; ostida cheksiz aylanuvchi surat kartochkalari.
 *
 * Kartochkaning istalgan joyiga bosilsa, surat umumiy ko'ruvchida
 * (`BaseLightbox`) to'liq ekranda ochiladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import { openLightbox } from '@/composables/useLightbox'

const { t } = useI18n()

const props = defineProps({
  /** Sarlavha qatorlari — har biri alohida qatorda chiqadi. */
  title: { type: [String, Array], required: true },
  description: { type: String, default: '' },
  /** Bo'sh qoldirilsa — «Galereya» tarjimasi ishlatiladi. */
  eyebrow: { type: String, default: '' },
  /** `[{ src, alt }]` — galereya suratlari. */
  images: { type: Array, required: true },
})

const titleLines = computed(() => (Array.isArray(props.title) ? props.title : [props.title]))
const eyebrowText = computed(() => props.eyebrow || t('courses.galleryEyebrow'))

/** Surat topilmasa — sindirilgan rasm belgisi o'rniga bo'sh joy qoladi. */
function hideBroken(event) {
  event.target.style.visibility = 'hidden'
}
</script>

<template>
  <section class="section overflow-hidden bg-white">
    <div
      class="container-page grid gap-8 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] lg:items-start lg:gap-[4%]"
    >
      <p
        v-if="description"
        v-reveal
        class="text-lead order-2 max-w-[32ch] leading-relaxed text-neutral-500 lg:order-1 lg:pt-[5.5rem]"
      >
        {{ description }}
      </p>

      <div class="order-1 text-center lg:order-2">
        <p v-reveal class="eyebrow">{{ eyebrowText }}</p>

        <h2 v-reveal class="title-hero font-wide mt-[1.25rem] font-bold text-neutral-900">
          <span v-for="line in titleLines" :key="line" class="block">{{ line }}</span>
        </h2>
      </div>

      <div class="order-3 hidden lg:block" aria-hidden="true" />
    </div>

    <!-- Suratlar lentasi: chapda konteyner cheti, o'ngda ekran chetiga qarab davom etadi -->
    <div class="mt-12 lg:mt-16">
      <InfiniteCarousel
        :speed="34"
        style="mask-image: linear-gradient(to right, #000 0, #000 90%, transparent 100%)"
      >
        <!-- Butun kartochka bosiladi — alohida «+» tugmasi kerak emas -->
        <button
          v-for="(image, index) in images"
          :key="image.src"
          type="button"
          class="rounded-block group relative size-[min(78vw,17rem)] shrink-0 cursor-zoom-in overflow-hidden transition duration-300 hover:-translate-y-1 lg:size-[19rem]"
          :aria-label="
            image.alt ? t('courses.openPhoto', { alt: image.alt }) : t('courses.openPhotoPlain')
          "
          @click="openLightbox(images, index)"
        >
          <img
            :src="image.src"
            :alt="image.alt || ''"
            loading="lazy"
            class="size-full object-cover transition duration-500 group-hover:scale-[1.06]"
            @error="hideBroken"
          />

          <!-- Kursor ustiga kelganda yumshoq qoraytirish: bosiladigani seziladi -->
          <span
            class="absolute inset-0 bg-black/0 transition duration-300 group-hover:bg-black/25"
            aria-hidden="true"
          />
        </button>
      </InfiniteCarousel>
    </div>
  </section>
</template>

<style scoped>
/* Lenta chapda konteyner cheti bilan tekislanadi, o'ngda cheklanmaydi. */
.gallery {
  padding-left: max((100% - 1180px) / 2, 4%);
}

@media (min-width: 1024px) {
  .gallery {
    padding-left: max((100% - 1180px) / 2, 9%);
  }
}
</style>
