<script setup>
/**
 * «План для старта в Backend» — boshlash uchun to'rt qadamli marshrut.
 *
 * Maket: tepada yumaloq kvadrat ichidagi `< >` ikonkasi, to'q sariq yorliq va
 * oq izoh; ostida 2×2 to'r — kapsula shaklidagi kartochkalar, o'ng chetida yirik
 * shaffof raqam va uning ortida sovuq (binafsha-ko'k) nur.
 *
 * Kartochkalar matni har xil uzunlikda, shuning uchun balandligi tenglashtirildi
 * — kapsula shakli buzilmasin.
 */
defineProps({
  /** `QUIZ_OUTCOME_DETAILS[...].plan` obyekti. */
  plan: { type: Object, required: true },
})
</script>

<template>
  <section v-reveal class="bg-ink pb-[var(--spacing-section)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <!-- Sarlavha qatori -->
        <header class="flex items-start gap-5">
          <span
            class="grid size-12 shrink-0 place-items-center rounded-2xl border border-white/20 text-white"
            aria-hidden="true"
          >
            <svg class="size-6" viewBox="0 0 24 24" fill="none">
              <path
                d="m10.2 8.8-3 3.2 3 3.2M13.8 8.8l3 3.2-3 3.2"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>

          <div>
            <h2 class="text-brand font-wide text-[1.05rem] font-bold">{{ plan.label }}</h2>
            <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
              {{ plan.headline }}
            </p>
          </div>
        </header>

        <!-- Qadamlar to'ri -->
        <ol class="mt-10 grid gap-5 lg:grid-cols-2">
          <li
            v-for="step in plan.steps"
            :key="step.number"
            class="bg-ink relative flex h-full min-h-[11rem] items-center overflow-hidden rounded-[2rem] py-8 pr-8 pl-9 lg:rounded-[5rem] lg:py-9 lg:pr-12 lg:pl-14"
          >
            <!-- Raqam ortidagi sovuq nur -->
            <span
              class="plan-glow pointer-events-none absolute inset-y-0 right-0 w-[45%]"
              aria-hidden="true"
            />

            <span
              class="font-wide pointer-events-none absolute top-1/2 right-8 -translate-y-1/2 leading-none font-bold text-white/12 select-none lg:right-14"
              style="font-size: clamp(3rem, 5.5vw, 5rem)"
              aria-hidden="true"
            >
              {{ step.number }}
            </span>

            <div class="relative max-w-[34ch] pr-20 lg:pr-24">
              <h3 class="font-wide text-[1.05rem] leading-snug font-bold text-white">
                {{ step.title }}
              </h3>
              <p class="mt-3 leading-relaxed text-white/60">{{ step.text }}</p>
            </div>
          </li>
        </ol>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Raqam ortidagi sovuq nur — maketdagi binafsha-ko'k yorug'lik */
.plan-glow {
  background: radial-gradient(closest-side at 75% 50%, rgba(84, 92, 214, 0.28), transparent 78%);
}
</style>
