<script setup>
/**
 * Ichki sahifalarning yuqori bloki — Figma: chapda yo'l va sarlavha,
 * o'ngda astronavt; orqasida kod matni va rangli nur (glow).
 *
 * Qatlamlar (orqadan oldinga): kod → nur → astronavt.
 * Astronavt oddiy oqimda turadi: kichik ekranda sarlavhadan keyin ko'rinadi,
 * matn ustiga tushmaydi.
 *
 * `actions` sloti — sarlavha ostidagi tugmalar uchun (ixtiyoriy).
 */
import { computed } from 'vue'

import aboutAstronaut from '@/assets/images/about-astronaut.webp'
import codeBackdrop from '@/assets/images/about-code.webp'
import glow from '@/assets/images/about-glow.webp'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'

const props = defineProps({
  /** Matn yoki qatorlar ro'yxati — har bir element alohida qatorda chiqadi. */
  title: { type: [String, Array], required: true },
  breadcrumbs: { type: Array, required: true },
  /** Sarlavha ostidagi qo'shimcha matn. */
  description: { type: String, default: '' },
  /** O'ngdagi rasm (standart — «О нас» astronavti). */
  image: { type: String, default: aboutAstronaut },
  /** Rasm va bezaklar ko'rsatilsinmi. */
  withImage: { type: Boolean, default: true },
})

/** Sarlavha qatorlari (Figma'da har bir so'z alohida qatorda turadi). */
const titleLines = computed(() => (Array.isArray(props.title) ? props.title : [props.title]))
</script>

<template>
  <section class="bg-ink relative overflow-hidden">
    <!-- Kod matni: o'ng yarmni qoplaydi, faqat bezak responsive holatda ham ko'rinishi kerak-->
    <img
      v-if="withImage"
      loading="lazy"
      decoding="async"
      :src="codeBackdrop"
      alt=""
      aria-hidden="true"
      class="code-backdrop pointer-events-none absolute inset-y-0 right-0 hidden w-[52%] object-cover object-left opacity-60 select-none lg:block"
    />

    <div
      class="container-page relative grid items-center gap-[6%] pt-[7%] pb-[var(--spacing-section)] lg:min-h-[30rem] lg:grid-cols-[1.05fr_1fr] lg:gap-[4%] lg:pt-[4%]"
    >
      <div class="order-1">
        <BaseBreadcrumbs :items="breadcrumbs" />

        <h1 v-reveal class="title-hero mt-[5%] font-wide font-bold text-white">
          <span v-for="line in titleLines" :key="line" class="block">{{ line }}</span>
        </h1>

        <p
          v-if="description"
          v-reveal="{ delay: 120 }"
          class="text-lead mt-[4%] max-w-[46ch] leading-relaxed text-white/70"
        >
          {{ description }}
        </p>

        <!-- Qo'shimcha element (masalan, tugma) — sahifa o'zi to'ldiradi -->
        <div v-if="$slots.actions" v-reveal="{ delay: 240 }" class="mt-[7%]">
          <slot name="actions" />
        </div>
      </div>

      <div v-if="withImage" class="relative order-2 mt-[8%] lg:mt-0" aria-hidden="true">
        <!-- Astronavt ortidagi rangli nur -->
        <img
          loading="lazy"
          decoding="async"
          :src="glow"
          alt=""
          class="pointer-events-none absolute top-1/2 left-1/2 w-[135%] max-w-none -translate-x-1/2 -translate-y-1/2 select-none"
        />

        <img
          decoding="async"
          fetchpriority="high"
          :src="image"
          alt=""
          class="animate-float relative mx-auto w-[74%] max-w-120 object-contain sm:w-[60%] lg:w-110 lg:max-w-none"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Kod fonining chetlari yumshoq so'nadi — keskin qirra ko'rinmaydi */
.code-backdrop {
  mask-image:
    linear-gradient(to right, transparent 0, #000 22%, #000 100%),
    linear-gradient(to bottom, transparent 0, #000 12%, #000 82%, transparent 100%);
  mask-composite: intersect;
  -webkit-mask-composite: source-in;
}
</style>
