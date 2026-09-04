<script setup>
/**
 * «Найдите своё место в команде» — ochiq vakansiyalar ro'yxati.
 *
 * Figma: yorug' fon, chapda qisqa izoh, o'ngda yorliq va yirik sarlavha;
 * ostida ikki ustunli kartochkalar. Har bir kartochkada lavozim, filial
 * yorlig'i, tavsif va «Подать заявку» tugmasi — u ariza panelini ochadi.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import OutlineIcon from '@/components/base/OutlineIcon.vue'
import VacancyApplyDrawer from '@/components/vacancies/VacancyApplyDrawer.vue'
import { useSection } from '@/composables/useSection'

const props = defineProps({
  /** Backenddan kelgan vakansiyalar. */
  items: { type: Array, required: true },
})

const { t } = useI18n()

// Ro'yxat sarlavhasi admin paneldan («Vakansiyalar» sahifasi bo'limlari → «Ro'yxat»).
const section = useSection('vacancies.list', {
  eyebrow: 'vacancies.eyebrow',
  title: 'vacancies.title',
  text: 'vacancies.lead',
})

const selected = ref(null)
const isDrawerOpen = ref(false)

/**
 * Kartochka matni: birinchi qator — qalin kirish, qolgani — tavsif.
 * (Backendda tavsif oddiy matn, birinchi qatori vakansiyaning mohiyati.)
 */
const cards = computed(() =>
  props.items.map((item) => {
    const [lead = '', ...rest] = String(item.description || '')
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)

    return { ...item, lead, text: rest.join(' ') }
  }),
)

function apply(vacancy) {
  selected.value = vacancy
  isDrawerOpen.value = true
}
</script>

<template>
  <section class="section bg-white">
    <div class="container-page">
      <!-- Sarlavha bloki: chapda izoh, o'ngda yorliq va sarlavha -->
      <div class="block lg:flex justify-between items-center">
        <div class="flex flex-col lg:block items-center justify-center lg:w-100">
          <p v-reveal class="eyebrow">{{ section.eyebrow }}</p>
          <h2
            v-reveal
            class="title-hero text-center lg:text-start mb-10 font-wide mt-5 font-bold text-neutral-900"
          >
            <span v-for="line in section.titleLines" :key="line" class="block">
              {{ line }}
            </span>
          </h2>
        </div>

        <div class="flex flex-col lg:block items-center justify-center lg:w-100">
          <p
            v-reveal
            class="text-neutral-500 lg:w-100 text-center lg:text-start max-w-[42ch] leading-relaxed"
          >
            {{ section.text }}
          </p>
        </div>
      </div>

      <!-- Kartochkalar -->
      <ul
        class="mt-[var(--spacing-block)] grid gap-[var(--spacing-gutter)] md:grid-cols-2"
        role="list"
      >
        <li
          v-for="(vacancy, index) in cards"
          :key="vacancy.id"
          v-reveal="{ delay: (index % 2) * 90 }"
          class="rounded-block relative flex flex-col bg-neutral-100 p-[8%] transition duration-300 hover:bg-neutral-200/70"
        >
          <h3 class="font-wide text-xl font-bold text-neutral-900 md:text-2xl">
            {{ vacancy.title }}
          </h3>

          <p
            v-if="vacancy.branch_name"
            class="rounded-pill text-small mt-[5%] self-start bg-neutral-900 px-[1.35em] py-[0.7em] text-white"
          >
            {{ t('vacancies.branch') }} · {{ vacancy.branch_name }}
          </p>

          <p v-if="vacancy.lead" class="mt-[6%] font-bold text-neutral-900">{{ vacancy.lead }}</p>
          <p v-if="vacancy.text" class="mt-2 leading-relaxed text-neutral-600">
            {{ vacancy.text }}
          </p>

          <!-- Tugma va ikonka har doim kartochka pastida turadi -->
          <div class="mt-auto flex items-end justify-between gap-6 pt-[10%]">
            <button
              type="button"
              class="bg-brand hover:bg-brand-hover rounded-pill px-[2.4em] py-[1.05em] font-medium text-white transition"
              @click="apply(vacancy)"
            >
              {{ t('vacancies.apply') }}
            </button>

            <OutlineIcon
              :name="vacancy.icon_name || 'spark'"
              class="size-11 shrink-0 text-neutral-900/80"
              aria-hidden="true"
            />
          </div>
        </li>
      </ul>
    </div>

    <VacancyApplyDrawer v-model:open="isDrawerOpen" :vacancy="selected" />
  </section>
</template>
