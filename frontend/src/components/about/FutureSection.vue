<script setup>
/**
 * «Почему это важно для будущего» — «О нас» sahifasidagi yorug' (oq) bo'lim.
 *
 * Tuzilishi yuqoridan pastga aniq ketma-ketlikda: yorliq → sarlavha va izoh →
 * kartochkalar → yakuniy jumla. Elementlar bir-birining ustiga chiqmaydi.
 */
import { useSection } from '@/composables/useSection'

// Blok matni admin paneldan («Biz haqimizda» → «Nega bu kelajak uchun muhim»).
const section = useSection('about.future', {
  eyebrow: 'about.futureEyebrow',
  title: 'about.futureTitle',
  text: 'about.futureText',
  note: 'about.futureNote',
})

defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-if="items.length" v-reveal class="section bg-white">
    <div class="container-page">
      <!-- Sarlavha bloki -->
      <header class="grid gap-8 lg:grid-cols-[1.15fr_1fr] lg:items-end lg:gap-16">
        <div>
          <p class="eyebrow">{{ section.eyebrow }}</p>
          <h2 class="section-title text-ink mt-5 max-w-[16ch]">{{ section.title }}</h2>
        </div>

        <p class="max-w-[42ch] leading-relaxed text-neutral-500 lg:pb-2">
          {{ section.text }}
        </p>
      </header>

      <!-- Kartochkalar -->
      <ul class="mt-12 grid gap-5 sm:grid-cols-2 lg:mt-16 lg:grid-cols-4">
        <li
          v-for="item in items"
          :key="item.id"
          class="group flex flex-col rounded-[1.75rem] p-7 transition duration-300 hover:-translate-y-1.5 lg:p-8"
          style="
            background: linear-gradient(160deg, #fdfdff 0%, #ecebf6 45%, #f8e3da 100%);
            box-shadow: 0 20px 45px -32px rgba(36, 39, 84, 0.55);
          "
        >
          <!-- Ikonka yuqorida: kartochkaning vizual tayanchi -->
          <span
            class="text-brand grid size-12 place-items-center rounded-2xl bg-white/70 shadow-sm transition duration-300 group-hover:scale-105"
          >
            <img
              v-if="item.icon"
              :src="item.icon"
              :alt="item.title"
              loading="lazy"
              class="size-6 object-contain"
            />
            <svg v-else class="size-6" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <rect
                x="5"
                y="3"
                width="14"
                height="18"
                rx="4.5"
                stroke="currentColor"
                stroke-width="1.4"
              />
              <path
                d="M9 9h6M9 12.5h3.5M9 16h4.5"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
              />
            </svg>
          </span>

          <h3
            class="text-ink mt-6 font-wide text-[1.0625rem] leading-snug font-bold sm:min-h-[2.6em]"
          >
            {{ item.title }}
          </h3>

          <p v-if="item.description" class="mt-3 leading-relaxed text-neutral-500">
            {{ item.description }}
          </p>
        </li>
      </ul>

      <!-- Yakuniy jumla -->
      <p
        class="text-ink mx-auto mt-12 max-w-[52ch] text-center font-wide text-[1.15rem] leading-snug font-bold lg:mt-16 lg:text-[1.5rem]"
      >
        {{ section.note }}
      </p>
    </div>
  </section>
</template>
