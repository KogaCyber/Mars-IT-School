<script setup>
/**
 * Filial kartochkasi — o'ngdan chiqadigan panel.
 *
 * Tepada filial rasmi va yopish tugmasi, ostida nomi, manzili (mo'ljal bilan)
 * va xaritada ochish tugmalari: Yandex Maps va Google Maps.
 */
import { onKeyStroke } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import BranchMapLinks from '@/components/contacts/BranchMapLinks.vue'
import { useScrollLock } from '@/composables/useScrollLock'

const { t } = useI18n()

defineProps({
  /** Ko'rsatiladigan filial (`null` bo'lsa panel yopiq). */
  branch: { type: Object, default: null },
})

const open = defineModel('open', { type: Boolean, required: true })

const panel = ref(null)
const isLocked = useScrollLock()

watch(open, async (value) => {
  isLocked.value = value
  if (value) {
    await nextTick()
    panel.value?.focus()
  }
})

onKeyStroke('Escape', () => {
  if (open.value) open.value = false
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="open && branch"
        class="fixed inset-0 z-[65] flex items-end justify-end sm:items-stretch"
      >
        <!-- Fon: sahifa xiralashadi -->
        <div class="absolute inset-0 bg-black/55 backdrop-blur-sm" @click="open = false" />

        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          :aria-label="branch.name"
          tabindex="-1"
          class="drawer-panel bg-ink relative flex max-h-[92dvh] w-full flex-col overflow-y-auto rounded-t-[2rem] outline-none sm:h-full sm:max-h-none sm:max-w-[38rem] sm:rounded-none"
        >
          <!-- Telefon versiyada pastdan chiqadigan panel uchun "tutqich" -->
          <span
            class="mx-auto mt-4 mb-1 h-1 w-12 shrink-0 rounded-full bg-white/20 sm:hidden"
            aria-hidden="true"
          />

          <!-- Filial rasmi va yopish tugmasi -->
          <div class="relative shrink-0">
            <img
              loading="lazy"
              decoding="async"
              v-if="branch.cover"
              :src="branch.cover"
              :alt="branch.name"
              class="aspect-[16/9] w-full object-cover"
            />
            <div v-else class="bg-surface aspect-[16/9] w-full" />

            <button
              type="button"
              class="text-brand absolute top-5 right-5 grid size-12 place-items-center rounded-full bg-black/45 backdrop-blur-sm transition hover:bg-black/65"
              :aria-label="t('common.close')"
              @click="open = false"
            >
              <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M5 5l10 10M15 5L5 15"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>

          <div class="px-6 py-8 sm:px-10 sm:py-10">
            <h2 class="font-wide text-3xl leading-tight font-bold text-white sm:text-4xl">
              {{ branch.name }}
            </h2>

            <div class="mt-8">
              <p class="font-bold text-white">{{ t('contacts.address') }}</p>
              <p class="text-lead mt-2 leading-relaxed text-white/75">{{ branch.address }}</p>
              <p v-if="branch.landmark" class="text-lead leading-relaxed text-white/75">
                {{ t('contacts.landmark', { landmark: branch.landmark }) }}
              </p>
            </div>

            <div v-if="branch.phone || branch.working_hours" class="mt-6 flex flex-col gap-1">
              <a
                v-if="branch.phone"
                :href="`tel:${branch.phone.replace(/[^\d+]/g, '')}`"
                class="text-lead hover:text-brand text-white/75 transition"
              >
                {{ branch.phone }}
              </a>
              <p v-if="branch.working_hours" class="text-lead text-white/55">
                {{ branch.working_hours }}
              </p>
            </div>

            <p class="mt-9 font-bold text-white">{{ t('contacts.viewOnMap') }}</p>
            <BranchMapLinks :branch="branch" class="mt-4" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Panel o'ngdan (telefonlarda pastdan) siljib chiqadi */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateY(100%);
}

@media (min-width: 640px) {
  .drawer-enter-from .drawer-panel,
  .drawer-leave-to .drawer-panel {
    transform: translateX(100%);
  }
}
</style>
