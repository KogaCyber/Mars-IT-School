<script setup>
/**
 * «Правильный порядок на пути Backend» — o'qish yo'lining to'rt bosqichi.
 *
 * Maket: tepada doiradagi `</>` ikonkasi, to'q sariq yorliq va oq sarlavha;
 * ostida 2×2 to'r — har bir kartochkaning o'ng pastida yirik shaffof raqam va
 * uning ortida issiq nur.
 *
 * Kartochkalar matni har xil uzunlikda, shuning uchun balandligi tenglashtirildi
 * (`h-full`) va raqam pastki burchakka mahkamlandi — to'r bir tekis ko'rinadi.
 */
defineProps({
  /** `QUIZ_OUTCOME_DETAILS[...].path` obyekti. */
  path: { type: Object, required: true },
})
</script>

<template>
  <section v-reveal class="bg-ink pb-[var(--spacing-section)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <!-- Sarlavha qatori -->
        <header class="flex items-start gap-5">
          <span
            class="grid size-12 shrink-0 place-items-center rounded-full border border-white/20 text-white"
            aria-hidden="true"
          >
            <svg class="size-6" viewBox="0 0 24 24" fill="none">
              <path
                d="m9.6 8.4-3.2 3.6 3.2 3.6M14.4 8.4l3.2 3.6-3.2 3.6"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>

          <div>
            <h2 class="text-brand font-wide text-[1.05rem] font-bold">{{ path.label }}</h2>
            <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
              {{ path.headline }}
            </p>
          </div>
        </header>

        <!-- Bosqichlar to'ri -->
        <ol class="mt-10 grid gap-5 lg:grid-cols-2">
          <li
            v-for="card in path.cards"
            :key="card.number"
            class="bg-ink relative flex h-full min-h-[15rem] flex-col overflow-hidden rounded-[1.75rem] p-7 lg:p-8"
          >
            <!-- Raqam ortidagi nur -->
            <span
              class="path-glow pointer-events-none absolute right-0 bottom-0 h-[70%] w-[55%]"
              aria-hidden="true"
            />

            <span
              class="font-wide pointer-events-none absolute right-6 bottom-3 leading-none font-bold text-white/10 select-none"
              style="font-size: clamp(3.5rem, 6vw, 5.5rem)"
              aria-hidden="true"
            >
              {{ card.number }}
            </span>

            <h3
              class="font-wide relative max-w-[30ch] text-[1.05rem] leading-snug font-bold text-white"
            >
              {{ card.title }}
            </h3>

            <p class="relative mt-4 max-w-[42ch] leading-relaxed text-white/60">{{ card.text }}</p>
          </li>
        </ol>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Raqam ortidagi issiq nur — maketdagi kabi o'ng pastdan taraladi */
.path-glow {
  background: radial-gradient(closest-side at 70% 80%, rgba(226, 69, 31, 0.3), transparent 75%);
}
</style>
