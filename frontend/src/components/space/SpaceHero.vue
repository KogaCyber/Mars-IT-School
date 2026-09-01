<script setup>
/**
 * «SPACE» sahifasining yuqori bloki — Figma: chapda yo'l, katta sarlavha va
 * «Перейти в SPACE» tugmasi (ariza sahifasiga olib boradi), o'ngda tangalar
 * bilan uchayotgan astronavt.
 *
 * Qatlamlar (orqadan oldinga): kod matni → rangli nur → astronavt.
 * Astronavt oddiy oqimda turadi — kichik ekranda sarlavhadan keyin tushadi.
 */
import { useI18n } from 'vue-i18n'

import codeBackdrop from '@/assets/images/about-code.webp'
import glow from '@/assets/images/about-glow.webp'
import spaceHero from '@/assets/images/space-hero.png'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'
import BaseButton from '@/components/base/BaseButton.vue'

const { t } = useI18n()
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
        <BaseBreadcrumbs
          :items="[
            { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
            { label: 'SPACE' },
          ]"
        />

        <h1 v-reveal class="hero-title font-wide mt-[6%] font-bold text-white">
          <span v-for="line in t('space.heroTitle').split('\n')" :key="line" class="block">
            {{ line }}
          </span>
        </h1>

        <div v-reveal="{ delay: 200 }" class="mt-[10%]">
          <BaseButton
            size="lg"
            :to="{ name: 'application' }"
            class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
          >
            {{ t('space.heroButton') }}
          </BaseButton>
        </div>
      </div>

      <div class="relative order-2 mt-[8%] lg:mt-0" aria-hidden="true">
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
          :src="spaceHero"
          alt=""
          fetchpriority="high"
          class="animate-float relative mx-auto w-[82%] max-w-125 object-contain sm:w-[66%] lg:w-110 lg:max-w-none"
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
