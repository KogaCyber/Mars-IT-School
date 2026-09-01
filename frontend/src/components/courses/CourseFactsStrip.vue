<script setup>
/**
 * Kurs asosiy ko'rsatkichlari — Figma: to'q sariqdan binafshaga o'tuvchi
 * to'liq kenglikdagi tasma, ustida to'rtta qorong'i kapsula-kartochka.
 */
defineProps({
  /** `[{ value, label }]` — masalan `{ value: '12–17 лет', label: 'возраст' }`. */
  facts: { type: Array, required: true },
})
</script>

<template>
  <section class="facts-strip py-[var(--spacing-block)]">
    <div class="container-page">
      <dl v-reveal class="grid gap-[var(--spacing-gutter)] sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="(fact, index) in facts"
          :key="index"
          class="rounded-block bg-black/35 px-[8%] py-[6%] backdrop-blur-sm"
        >
          <dt class="sr-only">{{ fact.label }}</dt>
          <dd>
            <span class="font-wide block text-[var(--text-h2)] leading-tight font-bold text-white">
              {{ fact.value }}
            </span>
            <span class="mt-[0.6em] block text-[var(--text-body)] text-white/70">
              {{ fact.label }}
            </span>
          </dd>
        </div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.facts-strip {
  background: linear-gradient(
    90deg,
    #ee5a24 0%,
    #b8401f 14%,
    #5c2733 38%,
    #3a2a5e 62%,
    #4a45a2 86%,
    #5a63cf 100%
  );
}
</style>
