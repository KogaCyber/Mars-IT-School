<script setup>
/**
 * «Родителям — полный контроль в одном приложении» — to'q (qora) bo'lim.
 *
 * Maket: chapda yorliq, yirik uch qatorli sarlavha va izoh; o'ngda telefon
 * rasmi, uning ostida esa slayd kartochkasi (sarlavha, izoh, o'q tugmalari va
 * «1/4» hisoblagichi).
 *
 * Slayd almashganda telefon yo'nalish bo'yicha siljib chiqadi va yangisi
 * qarama-qarshi tomondan kirib keladi (o'ng o'q → chapga chiqadi, o'ngdan keladi).
 *
 * Telefon rasmi har bir slaydda o'zgarishi mumkin: admin panelda slaydga rasm
 * yuklansa — o'shanisi, bo'lmasa blokning umumiy rasmi, u ham bo'lmasa maketdagi.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import phone from '@/assets/images/Layer-1 1.webp'
import { toCards, useSection } from '@/composables/useSection'
import { SPACE_PARENTS } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

// Blok matni va slaydlari admin paneldan («SPACE» bo'limlari → «Ota-onalar»).
const section = useSection('space.parents', {
  eyebrow: 'space.parentsEyebrow',
  title: 'space.parentsTitle',
  text: 'space.parentsText',
})
const fallback = useLocalized(SPACE_PARENTS)
const parents = computed(() => toCards(section.value.items, fallback.value))

const index = ref(0)
/** Oxirgi harakat yo'nalishi — animatsiya qaysi tomonga ketishini belgilaydi. */
const direction = ref('next')
const active = computed(() => parents.value[index.value])

/** Slayd rasmi: slaydniki → blokning umumiy rasmi → maketdagi telefon. */
const slideImage = computed(() => active.value?.image || section.value.image || phone)

/**
 * Admin paneldan yuklangan rasm istalgan nisbatda bo'lishi mumkin (tik, yotiq,
 * kvadrat). Uya o'lchami esa barcha slaydlarda bir xil turishi kerak — aks holda
 * slayd almashganda blok balandligi sakraydi. Shuning uchun yuklangan rasm uyaga
 * to'ldirib qirqiladi (`object-cover`), maketdagi telefon esa butunligicha
 * ko'rsatiladi (`object-contain`) — u shaffof fon bilan chizilgan.
 */
const isUploaded = computed(() => Boolean(active.value?.image || section.value.image))

/** Slaydlar aylanma: oxiridan keyin yana birinchisiga qaytadi. */
function go(step) {
  const total = parents.value.length
  direction.value = step > 0 ? 'next' : 'prev'
  index.value = (index.value + step + total) % total
}
</script>

<template>
  <section v-if="section.visible" v-reveal class="section bg-ink relative overflow-hidden">
    <!-- Fon nuri: telefon ortidan taraladi -->
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="animate-glow pointer-events-none absolute top-1/2 left-[62%] w-[120%] max-w-none -translate-x-1/2 -translate-y-1/2 select-none lg:w-[70%]"
    />

    <div
      class="container-page relative grid items-center gap-[8%] lg:grid-cols-[1.1fr_1fr] lg:gap-[6%]"
    >
      <!-- Chap ustun: sarlavha bloki -->
      <div>
        <p class="eyebrow">{{ section.eyebrow }}</p>

        <h2 class="title-parents font-wide mt-[5%] font-bold text-white">
          <span v-for="line in section.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>

        <p class="mt-[7%] max-w-[46ch] leading-relaxed text-white/70">
          {{ section.text }}
        </p>
      </div>

      <!-- O'ng ustun: telefon maketi va slayd kartochkasi -->
      <div class="relative mt-[8%] lg:mt-0">
        <!-- Telefon rasmi: slayd almashganda siljib almashinadi.
             Tashqi qavat — siljish chegarasi (chetdan chiqqani kesiladi). -->
        <div class="relative overflow-hidden">
          <!-- Rasm uyasi: nisbati qat'iy, shuning uchun qaysi rasm qo'yilishidan
               qat'i nazar barcha slaydlar bir xil o'lchamda ko'rinadi. -->
          <div
            class="animate-float relative mx-auto aspect-[332/550] w-[58%] max-w-66 sm:w-[42%] lg:w-[58%] lg:max-w-none"
          >
            <Transition :name="`phone-${direction}`">
              <img
                :key="active.id"
                :src="slideImage"
                alt=""
                aria-hidden="true"
                loading="lazy"
                class="absolute inset-0 h-full w-full select-none"
                :class="isUploaded ? 'rounded-block object-cover' : 'object-contain'"
              />
            </Transition>
          </div>
        </div>

        <!-- Slayd kartochkasi: telefonning pastki qismini qoplaydi -->
        <div
          class="rounded-block relative z-10 -mt-[18%] border border-white/10 bg-white/[0.07] p-[7%] backdrop-blur-xl"
        >
          <h3 class="title-block font-wide font-bold text-white">{{ active.title }}</h3>

          <p class="mt-3 min-h-[3rem] leading-relaxed text-white/60">{{ active.description }}</p>

          <div class="mt-[7%] flex items-center justify-between gap-4">
            <div class="flex gap-3">
              <button
                type="button"
                class="press grid size-11 place-items-center rounded-full bg-white/10 text-white transition hover:bg-white/20"
                :aria-label="t('space.parentsPrev')"
                @click="go(-1)"
              >
                <svg class="size-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M15 5.5 8.5 12l6.5 6.5"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>

              <button
                type="button"
                class="press grid size-11 place-items-center rounded-full bg-white/10 text-white transition hover:bg-white/20"
                :aria-label="t('space.parentsNext')"
                @click="go(1)"
              >
                <svg class="size-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M9 5.5 15.5 12 9 18.5"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </div>

            <p class="font-wide text-lg font-bold text-white/40" aria-live="polite">
              <span class="text-brand">{{ index + 1 }}</span
              >/{{ parents.length }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Eski va yangi rasm ikkalasi ham uyaga nisbatan `absolute inset-0` — ya'ni
   bir vaqtda, bir xil o'lchamda siljiydi. Uya balandligi esa `aspect-ratio`
   bilan belgilangan, shuning uchun blok hech qachon sakramaydi. */

/* Chiqib ketish va kirib kelish bir xil egri chiziqda */
.phone-next-enter-active,
.phone-next-leave-active,
.phone-prev-enter-active,
.phone-prev-leave-active {
  transition:
    transform 0.38s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.38s ease;
}

/* O'ng o'q: eskisi chapga chiqadi, yangisi o'ngdan keladi */
.phone-next-leave-to {
  opacity: 0;
  transform: translateX(-65%);
}

.phone-next-enter-from {
  opacity: 0;
  transform: translateX(65%);
}

/* Chap o'q: teskarisi */
.phone-prev-leave-to {
  opacity: 0;
  transform: translateX(65%);
}

.phone-prev-enter-from {
  opacity: 0;
  transform: translateX(-65%);
}

@media (prefers-reduced-motion: reduce) {
  .phone-next-enter-active,
  .phone-next-leave-active,
  .phone-prev-enter-active,
  .phone-prev-leave-active {
    transition: opacity 0.2s ease;
  }

  .phone-next-leave-to,
  .phone-next-enter-from,
  .phone-prev-leave-to,
  .phone-prev-enter-from {
    transform: none;
  }
}

/* Maketda sarlavha bo'lim sarlavhalaridan yirikroq */
.title-parents {
  font-size: clamp(2rem, 4.2vw, 4rem);
  line-height: 1.04;
}
</style>
