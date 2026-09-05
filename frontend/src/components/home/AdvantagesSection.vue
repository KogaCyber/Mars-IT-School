<script setup>
/** «Почему выбирают MARS IT School» — raqamlangan afzalliklar ro'yxati. */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'
import { useSection } from '@/composables/useSection'

const { t } = useI18n()

// Blok sarlavhasi admin paneldan (Bosh sahifa → «Nega MARS IT School ni tanlashadi»).
const section = useSection('home.advantages', {
  eyebrow: 'home.advantagesEyebrow',
  title: 'home.advantagesTitle',
  text: 'home.advantagesText',
})

const props = defineProps({
  items: { type: Array, default: () => [] },
  /** «Подробнее» tugmasi ko'rsatilsinmi (bosh sahifada — ha, «О нас»da — yo'q). */
  showLink: { type: Boolean, default: true },
})

// Birinchi element boshlang'ich holatda faol (Figma'da 02 faol ko'rsatilgan).
const activeIndex = ref(0)

function activate(index) {
  activeIndex.value = index
}

// Raqam ko'rsatilmagan bo'lsa tartib raqamdan hosil qilamiz: 01, 02, …
function displayNumber(item, index) {
  return item.number || String(index + 1).padStart(2, '0')
}
</script>

<template>
  <section v-if="section.visible && props.items.length" v-reveal class="section bg-ink">
    <div class="container-page">
      <p class="eyebrow">{{ section.eyebrow }}</p>

      <div class="mt-5 grid gap-8 lg:grid-cols-2 lg:items-end">
        <h2 class="section-title text-white">
          <span v-for="line in section.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>
        <p class="text-base leading-relaxed text-white/70 lg:text-right">
          {{ section.text }}
        </p>
      </div>

      <BaseButton
        v-if="props.showLink"
        :to="{ name: 'about' }"
        size="lg"
        class="mt-8 font-wide font-bold"
      >
        {{ t('common.more') }}
      </BaseButton>

      <ul class="mt-12 flex flex-col gap-4">
        <li
          v-for="(item, index) in props.items"
          :key="item.id"
          class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center lg:gap-8"
        >
          <button
            type="button"
            class="bg-surface hover:bg-surface-2 flex w-full items-center justify-between gap-4 rounded-[1.75rem] px-5 py-4 text-left transition sm:gap-[4%] sm:rounded-pill sm:px-[4%] sm:py-[2.5%]"
            :aria-expanded="activeIndex === index"
            @click="activate(index)"
            @mouseenter="activate(index)"
          >
            <span>
              <span class="title-block block font-wide font-bold text-white">
                {{ item.title }}
              </span>
              <span class="mt-[0.5em] block max-w-[36em] leading-relaxed text-white/60">
                {{ item.description }}
              </span>
            </span>

            <span
              class="section-title font-wide font-bold transition-colors"
              :class="activeIndex === index ? 'text-brand' : 'text-white/15'"
            >
              {{ displayNumber(item, index) }}
            </span>
          </button>

          <span
            v-if="item.image"
            class="hidden size-[5.2vw] shrink-0 place-items-center rounded-full transition lg:grid"
            :class="activeIndex === index ? 'bg-brand/80' : 'bg-brand/10'"
          >
            <img
              :src="item.image"
              :alt="item.title"
              loading="lazy"
              class="size-[60%] object-contain"
            />
          </span>
        </li>
      </ul>
    </div>
  </section>
</template>
