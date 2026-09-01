<script setup>
/**
 * «Вашему ребёнку стоит начать с BACKEND-разработки!» — natija sahifasidagi
 * ikkinchi blok.
 *
 * Maket: bitta katta to'q kartochka; ichida yorliq, ikki qatorli sarlavha va
 * izoh; ostida ikki ustun — chapda gradient fonli rasm paneli, o'ngda ingichka
 * chiziqlar bilan ajratilgan to'rtta qator (matn chapda, ikonka o'ng chetda);
 * eng pastda gradientli «Важное сообщение для родителей» paneli.
 *
 * Matnlar `data/quizOutcomes.js` dagi `profile` blokidan keladi — Frontend va
 * Backend uchun bir xil tuzilma, boshqa matn.
 */
import astronaut from '@/assets/images/Layer-0 9.png'

defineProps({
  /** `QUIZ_OUTCOME_DETAILS[...].profile` obyekti. */
  profile: { type: Object, required: true },
})

/** Qator ikonkalari — maketdagi chiziqli belgilar. */
const ICONS = {
  chart: 'M6.5 15.5V10M10.8 15.5V6.5M15.2 15.5v-4M19.5 15.5V8',
  logic:
    'M8.2 4.8h7.6a3.4 3.4 0 0 1 3.4 3.4v7.6a3.4 3.4 0 0 1-3.4 3.4H8.2a3.4 3.4 0 0 1-3.4-3.4V8.2a3.4 3.4 0 0 1 3.4-3.4ZM9.4 9.4h.01M14.6 9.4h.01M9.4 14.6h.01M14.6 14.6h.01M12 9.4v5.2',
  code: 'M6 6.5h12A1.5 1.5 0 0 1 19.5 8v6a1.5 1.5 0 0 1-1.5 1.5h-4L10 18.5v-3H6A1.5 1.5 0 0 1 4.5 14V8A1.5 1.5 0 0 1 6 6.5Zm3.6 2.9L7.8 11l1.8 1.6m4.8-3.2L16.2 11l-1.8 1.6',
  money:
    'M12 3.8a8.2 8.2 0 1 1 0 16.4 8.2 8.2 0 0 1 0-16.4ZM12 7.3v9.4M14.3 9.6c0-1-1-1.5-2.3-1.5s-2.3.6-2.3 1.6c0 2.3 4.6 1 4.6 3.3 0 1-1 1.6-2.3 1.6s-2.3-.5-2.3-1.5',
}
</script>

<template>
  <section v-reveal class="bg-ink pb-[var(--spacing-section)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <p class="eyebrow">{{ profile.eyebrow }}</p>

        <h2 class="font-wide title-profile mt-7 font-bold text-white">
          <span v-for="line in profile.title" :key="line" class="block">{{ line }}</span>
        </h2>

        <p class="mt-7 max-w-[95ch] leading-relaxed text-white/70">{{ profile.intro }}</p>

        <div class="mt-10 grid gap-8 lg:grid-cols-2 lg:gap-14">
          <!-- Rasm paneli: gradient fon ustida astronavt -->
          <div
            class="grid place-items-center overflow-hidden rounded-[1.75rem] p-8"
            style="
              background:
                radial-gradient(120% 80% at 50% 110%, rgba(226, 69, 31, 0.55), transparent 62%),
                radial-gradient(110% 70% at 20% 90%, rgba(84, 92, 214, 0.45), transparent 60%),
                #0e0e10;
            "
          >
            <img
              :src="astronaut"
              alt=""
              aria-hidden="true"
              loading="lazy"
              class="animate-float w-[76%] max-w-100 object-contain select-none"
            />
          </div>

          <!-- Ustunliklar ro'yxati -->
          <ul class="flex flex-col justify-center">
            <li
              v-for="(point, index) in profile.points"
              :key="point.text"
              class="flex items-center justify-between gap-8 border-white/10 py-6"
              :class="index < profile.points.length - 1 ? 'border-b' : ''"
            >
              <p class="max-w-[46ch] leading-relaxed text-white/80">{{ point.text }}</p>

              <span class="shrink-0 text-white/20" aria-hidden="true">
                <svg class="size-9" viewBox="0 0 24 24" fill="none">
                  <path
                    :d="ICONS[point.icon] || ICONS.chart"
                    stroke="currentColor"
                    stroke-width="1.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </li>
          </ul>
        </div>

        <!-- Ota-onalarga murojaat -->
        <div
          class="mt-10 grid gap-6 rounded-[1.75rem] p-8 md:grid-cols-[minmax(0,1fr)_2fr] md:items-center md:gap-12 lg:p-10"
          style="background: linear-gradient(100deg, #e2451f 0%, #a63a5a 55%, #3b2f7a 100%)"
        >
          <p class="font-wide text-[1.15rem] leading-snug font-bold text-white">
            <span v-for="line in profile.note.title" :key="line" class="block">{{ line }}</span>
          </p>

          <p class="leading-relaxed text-white/85">{{ profile.note.text }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha bo'lim sarlavhalaridan yirikroq */
.title-profile {
  font-size: clamp(1.6rem, 3.1vw, 3rem);
  line-height: 1.1;
}
</style>
