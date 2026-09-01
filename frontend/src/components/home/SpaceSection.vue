<script setup>
/**
 * «SPACE — для учеников и родителей».
 *
 * Katta ekranda: sarlavha + tavsif/tugma yonma-yon, ostida platforma maketi.
 * Kichik ekranda (Figma mobil ko'rinishi): sarlavha → tavsif → gorizontal
 * yorliqlar → kichraytirilgan maket → keng «Подробнее» tugmasi.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import rocket3d from '@/assets/images/rocket-3d.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import SpacePlatform from '@/components/home/SpacePlatform.vue'
import { SPACE_MENU } from '@/data/spacePlatform'

const { t } = useI18n()

const activeId = ref(SPACE_MENU[0].id)

/** Menyu ikonkalari — platformadagi bilan bir xil. */
const ICONS = {
  book: 'M4 5.5A1.5 1.5 0 0 1 5.5 4H10v12H5.5A1.5 1.5 0 0 1 4 14.5v-9ZM10 4h4.5A1.5 1.5 0 0 1 16 5.5v9a1.5 1.5 0 0 1-1.5 1.5H10',
  play: 'M4 6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Zm4 2.5v3l3-1.5-3-1.5Z',
  star: 'm10 3.5 2 4.2 4.5.6-3.3 3.2.8 4.5-4-2.2-4 2.2.8-4.5L3.5 8.3l4.5-.6 2-4.2Z',
  trophy: 'M6 4h8v3a4 4 0 0 1-8 0V4Zm0 1H4v1a2 2 0 0 0 2 2m8-3h2v1a2 2 0 0 1-2 2m-4 4v3m-2.5 0h5',
  chat: 'M4 5.5A1.5 1.5 0 0 1 5.5 4h9A1.5 1.5 0 0 1 16 5.5v6A1.5 1.5 0 0 1 14.5 13H8l-4 3v-3.5A1.5 1.5 0 0 1 4 11.5v-6Z',
  bag: 'M5 6h10l-.8 9.2a1.5 1.5 0 0 1-1.5 1.3H7.3a1.5 1.5 0 0 1-1.5-1.3L5 6Zm2.5 0V5a2.5 2.5 0 0 1 5 0v1',
}
</script>

<template>
  <section v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ t('home.spaceEyebrow') }}</p>

      <div class="mt-[3%] grid gap-[4%] lg:grid-cols-[1fr_22rem] lg:items-start">
        <h2 class="section-title relative text-white">
          SPACE —
          <img
            loading="lazy"
            decoding="async"
            :src="rocket3d"
            alt=""
            aria-hidden="true"
            class="animate-float absolute top-[-25%] right-0 w-[32%] max-w-[11rem] lg:top-[-30%] lg:right-auto lg:left-[42%] lg:w-[34%]"
          />
          <span class="block" v-html="t('home.spaceTitle')" />
        </h2>

        <div>
          <p class="mt-[4%] leading-relaxed text-white/70 lg:mt-0">
            {{ t('home.spaceText') }}
          </p>

          <!-- Keng ekranda tugma shu yerda turadi -->
          <div class="mt-[8%] hidden lg:block">
            <BaseButton :to="{ name: 'space' }" size="lg" class="font-wide font-bold" block>
              {{ t('common.more') }}
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Tor ekranda: platforma bo'limlari gorizontal yorliqlar ko'rinishida -->
      <ul class="scrollbar-none mt-[7%] flex gap-3 overflow-x-auto pb-1 lg:hidden">
        <li v-for="item in SPACE_MENU" :key="item.id" class="shrink-0">
          <button
            type="button"
            class="rounded-pill flex items-center gap-3 border px-5 py-4 whitespace-nowrap transition"
            :class="
              activeId === item.id
                ? 'border-brand/60 bg-surface text-brand'
                : 'border-line bg-surface text-white'
            "
            :aria-current="activeId === item.id ? 'true' : undefined"
            @click="activeId = item.id"
          >
            <svg class="size-[1.35rem] shrink-0" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                :d="ICONS[item.icon]"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            {{ t(`spaceMenu.${item.id}`) }}
          </button>
        </li>
      </ul>

      <SpacePlatform v-model="activeId" class="mt-[5%]" />

      <!-- Tor ekranda tugma maketdan keyin keladi -->
      <div class="mt-[7%] lg:hidden">
        <BaseButton :to="{ name: 'space' }" size="lg" class="font-wide font-bold" block>
          {{ t('common.more') }}
        </BaseButton>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Yorliqlar lentasida skroll chizig'i ko'rinmasin */
.scrollbar-none {
  scrollbar-width: none;
}

.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
