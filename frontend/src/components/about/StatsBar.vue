<script setup>
/**
 * Raqamlar lentasi — Figma: gradientli tasma ustida to'q kapsulalar.
 */
defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section
    v-if="items.length"
    v-reveal
    class="py-10 lg:py-12"
    style="background: linear-gradient(100deg, #e94921 0%, #7b2f4a 55%, #242754 100%)"
  >
    <div class="container-page">
      <ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <li
          v-for="item in items"
          :key="item.id"
          class="bg-ink/85 rounded-[1.75rem] px-7 py-6 backdrop-blur-sm"
        >
          <p class="font-wide text-[1.6rem] leading-none font-bold text-white lg:text-[1.85rem]">
            {{ item.value }}
          </p>
          <p class="mt-2 text-[0.95rem] text-white/60">{{ item.label }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>
