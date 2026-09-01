<script setup>
/**
 * «MARS IT — это не просто курсы».
 *
 * Figma: chapda yorliq, yirik sarlavha, belgilangan ro'yxat va tugma;
 * o'ngda tanishtiruv videosi (muqova + "play" tugmasi).
 */
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'

const { t } = useI18n()

defineProps({
  items: { type: Array, default: () => [] },
  /** Video havolasi va muqovasi — sayt sozlamalaridan keladi. */
  videoUrl: { type: String, default: '' },
  videoCover: { type: String, default: '' },
})
</script>

<template>
  <section v-reveal class="section bg-ink">
    <div class="container-page grid gap-12 lg:grid-cols-2 lg:items-center lg:gap-16">
      <div>
        <p class="eyebrow">{{ t('about.schoolEyebrow') }}</p>

        <!-- Qatorlarga bo'linish Figma'dagidek aniq belgilangan -->
        <h2 class="section-title mt-6 text-white">
          <span v-for="line in t('about.schoolTitle').split('\n')" :key="line" class="block">
            {{ line }}
          </span>
        </h2>

        <ul v-if="items.length" class="mt-10 flex flex-col gap-3">
          <li v-for="item in items" :key="item.id" class="flex items-center gap-3">
            <span class="text-brand shrink-0">
              <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.3" />
                <path
                  d="m6.8 10.2 2.1 2.1 4.3-4.4"
                  stroke="currentColor"
                  stroke-width="1.4"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span class="text-[0.95rem] text-white/80">{{ item.title }}</span>
          </li>
        </ul>

        <BaseButton :to="{ name: 'courses' }" size="lg" class="mt-10 font-wide font-bold">
          {{ t('common.viewCourses') }}
        </BaseButton>
      </div>

      <!-- Video -->
      <component
        :is="videoUrl ? 'a' : 'div'"
        v-if="videoCover"
        :href="videoUrl || undefined"
        :target="videoUrl ? '_blank' : undefined"
        :rel="videoUrl ? 'noopener noreferrer' : undefined"
        class="group rounded-block relative block overflow-hidden"
        :aria-label="videoUrl ? t('about.watchVideo') : undefined"
      >
        <img
          :src="videoCover"
          alt=""
          loading="lazy"
          class="aspect-[4/3] w-full object-cover transition duration-500 group-hover:scale-105"
        />

        <span
          v-if="videoUrl"
          class="bg-brand absolute top-1/2 left-1/2 grid size-16 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full text-white shadow-xl transition group-hover:scale-110"
        >
          <svg
            class="size-5 translate-x-0.5"
            viewBox="0 0 12 14"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M0 0l12 7-12 7z" />
          </svg>
        </span>
      </component>
    </div>
  </section>
</template>
