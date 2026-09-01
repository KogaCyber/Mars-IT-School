<script setup>
/**
 * «День, когда ребёнок защищает свой проект».
 *
 * Figma: chapda izoh matni va raqamlar kartochkasi, o'ngda yorliq bilan
 * yirik sarlavha; orqasida rangli nur.
 */
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import OutlineIcon from '@/components/base/OutlineIcon.vue'

const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-reveal class="section bg-ink relative overflow-hidden">
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="pointer-events-none absolute top-1/2 left-1/2 w-[130%] max-w-none -translate-x-1/2 -translate-y-1/2 opacity-60 select-none lg:w-[75%]"
    />

    <div class="container-page relative grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-16">
      <!-- Chap ustun: izoh va raqamlar -->
      <div class="order-2 lg:order-1">
        <p class="max-w-[42ch] text-[1.0625rem] leading-relaxed text-white/60">
          {{ t('about.demoDayText') }}
        </p>

        <ul
          v-if="items.length"
          class="border-line/70 divide-line/70 mt-10 divide-y rounded-[1.75rem] border bg-white/[0.04] px-6 backdrop-blur-sm lg:px-7"
        >
          <li
            v-for="item in items"
            :key="item.id"
            class="group flex items-center justify-between gap-6 py-5"
          >
            <div class="min-w-0">
              <p class="font-wide text-[1.6rem] leading-none font-bold text-white">
                {{ item.label }}
              </p>
              <p class="mt-2 text-[0.95rem] text-white/55">{{ item.title }}</p>
            </div>

            <OutlineIcon
              :name="item.icon_name"
              class="size-9 shrink-0 text-white/35 transition-colors duration-300 group-hover:text-white"
            />
          </li>
        </ul>
      </div>

      <!-- O'ng ustun: sarlavha -->
      <div class="order-1 lg:order-2">
        <p class="eyebrow">{{ t('about.demoDayEyebrow') }}</p>
        <h2 class="section-title mt-6 font-wide font-bold text-white text-5xl">
          <span v-for="line in t('about.demoDayTitle').split('\n')" :key="line" class="block">
            {{ line }}
          </span>
        </h2>
      </div>
    </div>
  </section>
</template>
