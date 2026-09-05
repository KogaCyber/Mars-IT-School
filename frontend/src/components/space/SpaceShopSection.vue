<script setup>
/**
 * «MARS Shop — обменивай баллы на подарки» — yorug' (oq) bo'lim.
 *
 * Maketda sovg'alar sakkizta katakka yoyilgan, ammo aslida beshta mahsulot bor
 * edi (bir xil kolonka uch marta takrorlangan). Shu sababli to'r qayta yig'ildi:
 * beshta haqiqiy sovg'a + oxirida «koin yig'ish» chaqiruvi — qator to'liq
 * yopiladi va bo'sh katak qolmaydi.
 */
import { computed } from 'vue'

import { useI18n } from 'vue-i18n'

import aksessuar from '@/assets/images/aksessuar.webp'
import alisa from '@/assets/images/alisa.webp'
import coin from '@/assets/images/coin-front.webp'
import quloqchin from '@/assets/images/quloqchin.webp'
import smartfon from '@/assets/images/smartfon.webp'
import soat from '@/assets/images/soat.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import { useSection } from '@/composables/useSection'
import { SPACE_SHOP } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

const { t, locale } = useI18n()

// Blok matni va sovg'alar admin paneldan («SPACE» bo'limlari → «MARS Shop»).
const section = useSection('space.shop', {
  eyebrow: 'space.shopEyebrow',
  title: 'space.shopTitle',
  text: 'space.shopText',
  note: 'space.shopCollectText',
  buttonLabel: 'space.shopButton',
})
const fallback = useLocalized(SPACE_SHOP)

const IMAGES = { alisa, soat, quloqchin, smartfon, aksessuar }

const shop = computed(() => {
  const items = section.value.items
  if (!items.length) return fallback.value

  return items.map((item, index) => {
    const preset = fallback.value[index] ?? {}
    return {
      id: item.id ?? index,
      title: item.title || preset.title || '',
      // Narx matn sifatida saqlanadi — bo'sh yoki noto'g'ri bo'lsa 0 bo'ladi.
      price: Number(String(item.value || preset.price || 0).replace(/\s/g, '')) || 0,
      // Rasm: admin panelga yuklangani, bo'lmasa maketdagisi.
      image: item.image || IMAGES[item.icon_name] || IMAGES[preset.image] || '',
    }
  })
})

/** Narxni «2 490» ko'rinishida chiqaradi — ajratgich sayt tiliga mos keladi. */
const formatPrice = (value) => value.toLocaleString(locale.value === 'en' ? 'en-US' : 'ru-RU')
</script>

<template>
  <section v-if="section.visible" v-reveal class="section bg-white">
    <div class="container-page">
      <!-- Sarlavha bloki -->
      <header class="grid gap-8 lg:grid-cols-[1.15fr_1fr] lg:items-end lg:gap-16">
        <div>
          <p class="eyebrow">{{ section.eyebrow }}</p>
          <h2 class="title-shop text-ink font-wide mt-5 font-bold">
            <span v-for="line in section.titleLines" :key="line" class="block">
              {{ line }}
            </span>
          </h2>
        </div>

        <p class="max-w-[42ch] leading-relaxed text-neutral-500 lg:pb-2">
          {{ section.text }}
        </p>
      </header>

      <!-- Sovg'alar to'ri -->
      <ul class="mt-12 grid gap-5 sm:grid-cols-2 lg:mt-16 lg:grid-cols-3">
        <li
          v-for="item in shop"
          :key="item.id"
          class="group flex flex-col rounded-[1.75rem] p-7 transition duration-300 hover:-translate-y-1.5 lg:p-8"
          style="
            background: linear-gradient(160deg, #fdfdff 0%, #ecebf6 45%, #f8e3da 100%);
            box-shadow: 0 20px 45px -32px rgba(36, 39, 84, 0.55);
          "
        >
          <h3 class="text-ink font-wide text-[1.0625rem] leading-snug font-bold">
            {{ item.title }}
          </h3>

          <!-- Mahsulot rasmi -->
          <div class="mt-6 grid h-44 place-items-center rounded-[1.25rem] bg-white/70 p-4">
            <img
              :src="item.image"
              :alt="item.title"
              loading="lazy"
              class="max-h-36 w-auto object-contain transition duration-300 group-hover:scale-105"
            />
          </div>

          <!-- Narx: qora kapsula ichida koin belgisi bilan -->
          <p
            class="bg-ink font-wide mt-6 inline-flex w-fit items-center gap-2 rounded-pill py-2 pr-2 pl-4 font-bold text-white"
          >
            {{ formatPrice(item.price) }}
            <img
              loading="lazy"
              decoding="async"
              :src="coin"
              :alt="t('space.shopCoins')"
              class="size-7 object-contain"
            />
          </p>
        </li>

        <!-- Yakuniy katak: koin yig'ishga chaqiruv -->
        <li
          class="flex flex-col justify-between rounded-[1.75rem] p-7 text-white lg:p-8"
          style="background: linear-gradient(150deg, #e2451f 0%, #a63a5a 55%, #3b2f7a 100%)"
        >
          <div>
            <h3 class="font-wide text-[1.0625rem] leading-snug font-bold">{{ section.subtitle }}</h3>
            <p class="mt-3 leading-relaxed text-white/80">{{ section.note }}</p>
          </div>

          <BaseButton
            variant="white"
            size="lg"
            class="font-wide mt-8 w-fit font-bold"
            :to="{ name: 'application', query: { source: 'space-shop' } }"
          >
            {{ section.buttonLabel }}
          </BaseButton>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha bo'lim sarlavhalaridan yirikroq */
.title-shop {
  font-size: clamp(2rem, 4vw, 3.75rem);
  line-height: 1.05;
}
</style>
