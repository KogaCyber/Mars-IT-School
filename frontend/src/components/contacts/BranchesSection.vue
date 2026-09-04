<script setup>
/**
 * «Адреса школ в Ташкенте» — filiallar bo'limi.
 *
 * Chapda qisqa izoh va «Карта / Список» almashtirgichi, o'ngda yorliq bilan
 * yirik sarlavha. Ostida to'q xarita: har bir filial Mars sayyorasi
 * ko'rinishidagi nishon — bosilganda o'ngdan filial kartochkasi ochiladi.
 * «Список» rejimida esa filiallar gorizontal scroll qilinadigan
 * kartochkalar sifatida chiqadi.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchBranches } from '@/api/branches'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import BranchDrawer from '@/components/contacts/BranchDrawer.vue'
import BranchesMap from '@/components/contacts/BranchesMap.vue'
import BranchMapLinks from '@/components/contacts/BranchMapLinks.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSection } from '@/composables/useSection'

const { t } = useI18n()

// Blok matni admin paneldan («Kontaktlar» sahifasi bo'limlari → «Filiallar»).
const section = useSection('contacts.branches', {
  eyebrow: 'contacts.branchesEyebrow',
  title: 'contacts.branchesTitle',
  text: 'contacts.branchesHint',
  note: 'contacts.branchesEmpty',
})

const { data: branches, isLoading } = useAsyncData(fetchBranches, [])

const view = ref('map')
const selected = ref(null)
const isDrawerOpen = ref(false)

/** Xaritada faqat koordinatasi ko'rsatilgan filiallar chiziladi. */
const mapped = computed(() => branches.value.filter((item) => item.latitude && item.longitude))

function openBranch(branch) {
  selected.value = branch
  isDrawerOpen.value = true
}
</script>

<template>
  <section class="section bg-ink">
    <div class="container-page">
      <!-- Sarlavha bloki: chapda izoh va almashtirgich, o'ngda sarlavha -->
      <div class="grid gap-[var(--spacing-block)] lg:grid-cols-[minmax(0,1fr)_minmax(0,1.5fr)]">
        <div v-reveal class="order-2 lg:order-1 lg:pt-[12%]">
          <p class="text-lead max-w-[26ch] leading-relaxed text-white/70">
            {{ section.text }}
          </p>

          <!-- Karta / Список almashtirgichi -->
          <div
            class="rounded-pill mt-[var(--spacing-gutter)] inline-flex bg-white/6 p-[0.35rem]"
            role="tablist"
            :aria-label="t('contacts.branchesViewLabel')"
          >
            <button
              v-for="tab in [
                { id: 'map', label: t('contacts.viewMap') },
                { id: 'list', label: t('contacts.viewList') },
              ]"
              :key="tab.id"
              type="button"
              role="tab"
              :aria-selected="view === tab.id"
              class="rounded-pill min-w-[8.5rem] px-[2em] py-[0.95em] font-medium transition"
              :class="
                view === tab.id
                  ? 'bg-ink font-bold text-white'
                  : 'text-white/45 hover:text-white/75'
              "
              @click="view = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div v-reveal class="order-1 lg:order-2 lg:text-right">
          <p class="eyebrow font-bold">{{ section.eyebrow }}</p>
          <h2 class="title-hero mt-[4%] text-white">
            <span v-for="line in section.titleLines" :key="line" class="block">
              {{ line }}
            </span>
          </h2>
        </div>
      </div>

      <BaseSpinner v-if="isLoading" />
      <BaseEmptyState v-else-if="!branches.length" :title="section.note" />

      <template v-else>
        <!-- Xarita -->
        <div
          v-show="view === 'map'"
          v-reveal
          class="mt-[var(--spacing-block)] h-[26rem] overflow-hidden rounded-[2.5rem] sm:h-[32rem] lg:h-[36rem]"
        >
          <BranchesMap
            :branches="mapped"
            :active-slug="isDrawerOpen ? selected?.slug || '' : ''"
            @select="openBranch"
          />
        </div>

        <!-- Ro'yxat: gorizontal scroll bilan kartochkalar (karusel emas) -->
        <ul
          v-if="view === 'list'"
          class="branches-scroller mt-[var(--spacing-block)] flex snap-x snap-mandatory gap-[var(--spacing-gutter)] overflow-x-auto pb-4"
          role="list"
        >
          <li
            v-for="branch in branches"
            :key="branch.id"
            class="rounded-block bg-surface/70 flex w-[19rem] shrink-0 snap-start flex-col border border-white/8 p-5 transition duration-300 hover:border-white/20 hover:bg-surface sm:w-[24rem] sm:p-6"
          >
            <img
              v-if="branch.cover"
              :src="branch.cover"
              :alt="branch.name"
              loading="lazy"
              class="rounded-card aspect-[16/9] w-full object-cover"
            />
            <div v-else class="rounded-card bg-surface-2 aspect-[16/9] w-full" />

            <h3 class="font-wide mt-6 text-2xl leading-tight font-bold text-white sm:text-3xl">
              {{ branch.name }}
            </h3>

            <p class="mt-5 font-bold text-white">{{ t('contacts.address') }}</p>
            <p class="mt-1.5 leading-relaxed text-white/65">{{ branch.address }}</p>
            <p v-if="branch.landmark" class="leading-relaxed text-white/65">
              {{ t('contacts.landmark', { landmark: branch.landmark }) }}
            </p>

            <BranchMapLinks :branch="branch" class="mt-auto pt-7" />
          </li>
        </ul>
      </template>
    </div>

    <BranchDrawer v-model:open="isDrawerOpen" :branch="selected" />
  </section>
</template>

<style scoped>
/* Scroll paneli — nozik va sayt ranglarida */
.branches-scroller {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.branches-scroller::-webkit-scrollbar {
  height: 0.375rem;
}

.branches-scroller::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
}
</style>
