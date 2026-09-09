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
import { formatPrice } from '@/utils/format'

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
 * Admin paneldagi «Talablar» / «Shartlar» ko'p qatorli matn: har bir qator —
 * alohida band. Boshidagi «-», «•», «1.» belgilarini olib tashlaymiz, chunki
 * ro'yxat belgisini kartochkaning o'zi chizadi.
 */
function toLines(value) {
  return String(value || '')
    .split('\n')
    .map((line) => line.replace(/^\s*(?:[-–—•*]|\d+[.)])\s*/, '').trim())
    .filter(Boolean)
}

/**
 * Maosh: «dan», «gacha» yoki oraliq — bittasi to'ldirilgan bo'lsa ham ko'rinadi.
 *
 * Valyuta admin paneldan tanlanadi: `USD` bo'lsa raqam oldida `$`, `UZS` bo'lsa
 * raqamdan keyin sayt tilidagi so'm/сум/UZS yozuvi turadi.
 */
function money(amount, isUsd) {
  return isUsd ? `$${formatPrice(amount)}` : `${formatPrice(amount)} ${t('pages.courseCurrency')}`
}

function toSalary(item) {
  const from = Number(item.salary_from) || 0
  const to = Number(item.salary_to) || 0
  const isUsd = item.salary_currency === 'USD'

  if (from && to && from !== to) {
    // So'mda valyuta bir marta oxirida, dollarda esa har ikki raqam oldida.
    return isUsd
      ? `${money(from, true)} – ${money(to, true)}`
      : `${formatPrice(from)} – ${money(to, false)}`
  }
  if (from) {
    return from === to
      ? money(from, isUsd)
      : t('vacancies.salaryFrom', { value: money(from, isUsd) })
  }
  if (to) return t('vacancies.salaryTo', { value: money(to, isUsd) })
  return ''
}

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

    return {
      ...item,
      lead,
      text: rest.join(' '),
      salary: toSalary(item),
      requirements: toLines(item.requirements),
      conditions: toLines(item.conditions),
    }
  }),
)

function apply(vacancy) {
  selected.value = vacancy
  isDrawerOpen.value = true
}
</script>

<template>
  <section v-if="section.visible" class="section bg-white">
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

          <!-- Filial va maosh — bir qatorda, kartochkaning o'z uslubida -->
          <div
            v-if="vacancy.branch_name || vacancy.salary"
            class="mt-[5%] flex flex-wrap items-center gap-2"
          >
            <p
              v-if="vacancy.branch_name"
              class="rounded-pill text-small bg-neutral-900 px-[1.35em] py-[0.7em] text-white"
            >
              {{ t('vacancies.branch') }} · {{ vacancy.branch_name }}
            </p>

            <p
              v-if="vacancy.salary"
              class="rounded-pill text-small bg-brand/12 text-brand px-[1.35em] py-[0.7em] font-bold"
            >
              {{ vacancy.salary }}
            </p>
          </div>

          <p v-if="vacancy.lead" class="mt-[6%] font-bold text-neutral-900">{{ vacancy.lead }}</p>
          <p v-if="vacancy.text" class="mt-2 leading-relaxed text-neutral-600">
            {{ vacancy.text }}
          </p>

          <!-- Admin paneldagi «Talablar» -->
          <template v-if="vacancy.requirements.length">
            <p class="text-small mt-[6%] font-bold text-neutral-900">
              {{ t('vacancies.requirements') }}
            </p>
            <ul class="mt-2 flex flex-col gap-2" role="list">
              <li
                v-for="(line, i) in vacancy.requirements"
                :key="`r-${i}`"
                class="flex gap-2.5 leading-relaxed text-neutral-600"
              >
                <span class="bg-brand mt-2.5 size-1.5 shrink-0 rounded-full" aria-hidden="true" />
                <span>{{ line }}</span>
              </li>
            </ul>
          </template>

          <!-- Admin paneldagi «Shartlar» -->
          <template v-if="vacancy.conditions.length">
            <p class="text-small mt-[6%] font-bold text-neutral-900">
              {{ t('vacancies.conditions') }}
            </p>
            <ul class="mt-2 flex flex-col gap-2" role="list">
              <li
                v-for="(line, i) in vacancy.conditions"
                :key="`c-${i}`"
                class="flex gap-2.5 leading-relaxed text-neutral-600"
              >
                <svg
                  class="text-brand mt-1 size-4 shrink-0"
                  viewBox="0 0 20 20"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="m5 10.4 3.4 3.3L15.5 6.7"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                <span>{{ line }}</span>
              </li>
            </ul>
          </template>

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
