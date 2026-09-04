<script setup>
/**
 * «Какие навыки развивает ребёнок».
 *
 * Figma: chapda yorliq va yirik sarlavha, o'ngda ustma-ust joylashgan kartochkalar,
 * orqasida to'q sariq–ko'k nur.
 */
import glow from '@/assets/images/about-glow.webp'
import { useSection } from '@/composables/useSection'
import OutlineIcon from '@/components/base/OutlineIcon.vue'

// Blok sarlavhasi admin paneldan («Biz haqimizda» → «Ko'nikmalar»).
const section = useSection('about.skills', {
  eyebrow: 'about.skillsEyebrow',
  title: 'about.skillsTitle',
})

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-if="items.length" v-reveal class="section bg-ink relative overflow-hidden">
    <!-- Fon nuri -->
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="pointer-events-none absolute top-1/2 left-1/2 w-[130%] max-w-none -translate-x-1/2 -translate-y-1/2 opacity-70 select-none lg:w-[80%]"
    />

    <div class="container-page relative grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-16">
      <div>
        <p class="eyebrow">{{ section.eyebrow }}</p>
        <h2 class="section-title mt-6 max-w-[14ch] text-white text-5xl sm:text-7xl">
          {{ section.title }}
        </h2>
      </div>

      <ul class="flex flex-col gap-4">
        <li
          v-for="item in items"
          :key="item.id"
          class="group border-line/70 flex items-start justify-between gap-6 rounded-[1.5rem] border bg-white/[0.04] px-6 py-5 backdrop-blur-sm transition duration-300 hover:bg-white/[0.07]"
        >
          <div class="min-w-0">
            <h3 class="font-wide text-[1.0625rem] font-bold text-white">{{ item.title }}</h3>
            <p v-if="item.description" class="mt-2 text-[0.95rem] leading-relaxed text-white/55">
              {{ item.description }}
            </p>
          </div>

          <span
            class="shrink-0 text-white/35 transition-colors duration-300 group-hover:text-white"
          >
            <img
              v-if="item.icon"
              :src="item.icon"
              :alt="item.title"
              loading="lazy"
              class="size-9 object-contain"
            />
            <OutlineIcon v-else :name="item.icon_name" class="size-9" />
          </span>
        </li>
      </ul>
    </div>
  </section>
</template>
