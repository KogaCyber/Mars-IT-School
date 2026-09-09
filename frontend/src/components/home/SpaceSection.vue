<script setup>
/**
 * «SPACE — для учеников и родителей».
 *
 * Katta ekranda: sarlavha + tavsif/tugma yonma-yon, ostida platforma maketi.
 * Kichik ekranda (Figma mobil ko'rinishi): sarlavha → tavsif → gorizontal
 * yorliqlar → kichraytirilgan maket → keng «Подробнее» tugmasi.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import rocket3d from '@/assets/images/rocket-3d.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import SpacePlatform from '@/components/home/SpacePlatform.vue'
import { useSection, useSectionVisible } from '@/composables/useSection'
import { SPACE_MENU_ICONS, useSpaceMenu } from '@/composables/useSpaceMenu'

const { t } = useI18n()

// Blok matni admin paneldan (Bosh sahifa → «SPACE platformasi bloki»).
const section = useSection('home.space', {
  eyebrow: 'home.spaceEyebrow',
  title: 'home.spaceTitle',
  text: 'home.spaceText',
  buttonLabel: 'common.more',
})

// Maket menyusi (admin panel: «SPACE maketi — chap menyu va ekran rasmlari»).
// Maketni butunlay yashirish ham shu bo'limdagi belgi orqali.
const platformVisible = useSectionVisible('home.platform')
const menu = useSpaceMenu()
const activeId = ref(menu.value[0]?.id ?? '')

// Kontent keyinroq yuklanadi yoki panelda tugmalar o'zgaradi — bunday holatda
// tanlangan tugma ro'yxatdan chiqib ketmasligi kerak.
watch(menu, (items) => {
  if (!items.some((item) => item.id === activeId.value)) activeId.value = items[0]?.id ?? ''
})
</script>

<template>
  <section v-if="section.visible" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ section.eyebrow }}</p>

      <div class="mt-[3%] grid gap-[4%] lg:grid-cols-[1fr_22rem] lg:items-start">
        <h2 class="section-title relative text-white">
          SPACE —
          <img
            loading="lazy"
            decoding="async"
            :src="section.image || rocket3d"
            alt=""
            aria-hidden="true"
            class="animate-float absolute top-[-25%] right-0 w-[32%] max-w-[11rem] lg:top-[-30%] lg:right-auto lg:left-[42%] lg:w-[34%]"
          />
          <span v-for="line in section.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>

        <div>
          <p class="mt-[4%] leading-relaxed text-white/70 lg:mt-0">
            {{ section.text }}
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
      <ul
        v-if="platformVisible"
        class="scrollbar-none mt-[7%] flex gap-3 overflow-x-auto pb-1 lg:hidden"
      >
        <li v-for="item in menu" :key="item.id" class="shrink-0">
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
            <img
              v-if="item.iconImage"
              loading="lazy"
              decoding="async"
              :src="item.iconImage"
              alt=""
              aria-hidden="true"
              class="size-[1.35rem] shrink-0 object-contain"
            />
            <svg
              v-else
              class="size-[1.35rem] shrink-0"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
            >
              <path
                :d="SPACE_MENU_ICONS[item.icon]"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            {{ item.label }}
          </button>
        </li>
      </ul>

      <SpacePlatform v-if="platformVisible" v-model="activeId" class="mt-[5%]" />

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
