<script setup>
/**
 * Kurs sahifasining yuqori bloki — Figma: chapda yo'l, katta sarlavha va
 * ikkita tugma, o'ngda astronavt.
 *
 * Qatlamlar (orqadan oldinga): kod matni → rangli nur → astronavt.
 * Astronavt oddiy oqimda turadi — kichik ekranda sarlavhadan keyin tushadi.
 */
import { computed } from 'vue'

import codeBackdrop from '@/assets/images/about-code.webp'
import glow from '@/assets/images/about-glow.webp'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'

const props = defineProps({
  /** Matn yoki qatorlar ro'yxati — har bir element alohida qatorda chiqadi. */
  title: { type: [String, Array], required: true },
  breadcrumbs: { type: Array, required: true },
  /** Sarlavha ostidagi qisqa izoh (ixtiyoriy). */
  description: { type: String, default: '' },
  /** O'ngdagi rasm. */
  image: { type: String, required: true },
})

const titleLines = computed(() => (Array.isArray(props.title) ? props.title : [props.title]))

/** Kurs rasmining matni — kurs nomidan (Google Rasmlar uchun ham manba). */
const imageAlt = computed(() => `${titleLines.value.join(' ')} — MARS IT School`)
</script>

<template>
  <section class="bg-ink relative overflow-hidden">
    <!-- Kod matni: o'ng yarmni qoplaydi, faqat bezak -->
    <img
      loading="lazy"
      decoding="async"
      :src="codeBackdrop"
      alt=""
      aria-hidden="true"
      class="code-backdrop pointer-events-none absolute inset-y-0 right-0 hidden w-[52%] object-cover object-left opacity-60 select-none lg:block"
    />

    <div
      class="container-page relative grid items-center gap-[6%] pt-[7%] pb-[var(--spacing-section)] lg:min-h-[36rem] lg:grid-cols-[1.05fr_1fr] lg:gap-[4%] lg:pt-[4%]"
    >
      <div class="order-1">
        <BaseBreadcrumbs :items="breadcrumbs" />

        <h1 v-reveal class="hero-title font-wide mt-[6%] font-bold text-white">
          <span v-for="line in titleLines" :key="line" class="block">{{ line }}</span>
        </h1>

        <p
          v-if="description"
          v-reveal="{ delay: 120 }"
          class="text-lead mt-[5%] max-w-[34rem] leading-relaxed text-white/70"
        >
          {{ description }}
        </p>

        <div
          v-if="$slots.actions"
          v-reveal="{ delay: 200 }"
          class="mt-[10%] flex flex-wrap items-center gap-[var(--spacing-gutter)]"
        >
          <slot name="actions" />
        </div>
      </div>

      <div class="relative order-2 mt-[8%] lg:mt-0" aria-hidden="true">
        <!-- Astronavt ortidagi rangli nur -->
        <img
          loading="lazy"
          decoding="async"
          :src="glow"
          alt=""
          aria-hidden="true"
          class="pointer-events-none absolute top-1/2 left-1/2 w-[135%] max-w-none -translate-x-1/2 -translate-y-1/2 select-none"
        />

        <img
          decoding="async"
          fetchpriority="high"
          :src="image"
          :alt="imageAlt"
          class="animate-float relative mx-auto w-[78%] max-w-125 object-contain sm:w-[62%] lg:w-110 lg:max-w-none"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha sahifa sarlavhalaridan yirikroq */
.hero-title {
  font-size: clamp(2.25rem, 5vw, 6rem);
  line-height: 1.02;
}

/* Kod fonining chetlari yumshoq so'nadi — keskin qirra ko'rinmaydi */
.code-backdrop {
  mask-image:
    linear-gradient(to right, transparent 0, #000 22%, #000 100%),
    linear-gradient(to bottom, transparent 0, #000 12%, #000 82%, transparent 100%);
  mask-composite: intersect;
  -webkit-mask-composite: source-in;
}
</style>
