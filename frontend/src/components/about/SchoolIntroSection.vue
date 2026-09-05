<script setup>
/**
 * «MARS IT — это не просто курсы».
 *
 * Figma: chapda yorliq, yirik sarlavha, belgilangan ro'yxat va tugma;
 * o'ngda tanishtiruv videosi (muqova + "play" tugmasi) — bosilganda rolik
 * saytdan chiqmasdan modal oyna ichida o'ynaydi.
 */
import { computed } from 'vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { useSection } from '@/composables/useSection'
import { isPlayable, openVideo } from '@/composables/useVideoModal'


// «Kurslarni ko'rish» tugmasi matni — «Sayt sozlamalari» → «Umumiy bloklar».
const buttons = useSection('common.buttons', {
  buttonLabel: 'common.trialLesson',
  button2Label: 'common.viewCourses',
})

// Blok matni admin paneldan («Biz haqimizda» → «Oddiy kurslar emas»).
const section = useSection('about.school', {
  eyebrow: 'about.schoolEyebrow',
  title: 'about.schoolTitle',
  buttonLabel: 'about.watchVideo',
})

const props = defineProps({
  items: { type: Array, default: () => [] },
  /** Video havolasi va muqovasi — sayt sozlamalaridan keladi. */
  videoUrl: { type: String, default: '' },
  videoCover: { type: String, default: '' },
})

/**
 * Havola bor bo'lishi yetarli emas — u ichki pleyer TANIYDIGAN manba
 * (YouTube, Vimeo yoki to'g'ridan-to'g'ri video fayl) bo'lishi kerak.
 * Aks holda «play» tugmasi chizilib, bosilganda hech nima bo'lmasdi.
 */
const canPlay = computed(() => isPlayable(props.videoUrl))
</script>

<template>
  <section v-if="section.visible" v-reveal class="section bg-ink">
    <div class="container-page grid gap-12 lg:grid-cols-2 lg:items-center lg:gap-16">
      <div>
        <p class="eyebrow">{{ section.eyebrow }}</p>

        <!-- Qatorlarga bo'linish Figma'dagidek aniq belgilangan -->
        <h2 class="section-title mt-6 text-white">
          <span v-for="line in section.titleLines" :key="line" class="block">
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
          {{ buttons.button2Label }}
        </BaseButton>
      </div>

      <!-- Video. Muqova qo'yilmagan bo'lsa ham, video bo'lsa blok ko'rinadi:
           admin panelda faqat fayl yuklab qo'yish yetarli. -->
      <component
        :is="canPlay ? 'button' : 'div'"
        v-if="videoCover || canPlay"
        :type="canPlay ? 'button' : undefined"
        class="group rounded-block bg-surface relative block w-full overflow-hidden"
        :aria-label="canPlay ? section.buttonLabel : undefined"
        @click="canPlay && openVideo(videoUrl, section.buttonLabel)"
      >
        <img
          v-if="videoCover"
          :src="videoCover"
          alt=""
          loading="lazy"
          class="aspect-[4/3] w-full object-cover transition duration-500 group-hover:scale-105"
        />
        <div v-else class="aspect-[4/3] w-full" aria-hidden="true" />

        <span
          v-if="canPlay"
          class="absolute inset-0 bg-black/0 transition duration-300 group-hover:bg-black/25"
          aria-hidden="true"
        />

        <span
          v-if="canPlay"
          class="bg-brand absolute top-1/2 left-1/2 grid size-16 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full text-white shadow-xl transition duration-300 group-hover:scale-110"
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
