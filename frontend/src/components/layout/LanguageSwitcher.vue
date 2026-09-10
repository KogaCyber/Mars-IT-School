<script setup>
/**
 * Til almashtirgich.
 *
 * Katta ekranda: joriy til tugmasi ostidan qolgan tillar kapsulasi ochiladi.
 * Kichik ekranda: pastdan ko'tariladigan panel (bottom sheet) — barcha tillar
 * to'liq nomi bilan, orqa fon xiralashadi va sahifa skroll qilinmaydi.
 */
import { onClickOutside, onKeyStroke, useMediaQuery } from '@vueuse/core'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { useScrollLock } from '@/composables/useScrollLock'
import { withBase } from '@/data/basePath'
import { localePath } from '@/data/seoConfig'
import { setLanguage } from '@/i18n/language'
import { useSiteStore } from '@/stores/site'

// Tillar ro'yxati o'z nomida yoziladi — bu tarjima qilinmaydi.
const LANGUAGES = [
  { code: 'uz', short: "O'z", label: "O'zbekcha" },
  { code: 'ru', short: 'Ru', label: 'Русский' },
  { code: 'en', short: 'En', label: 'English' },
]

const { t } = useI18n()
const site = useSiteStore()
const route = useRoute()
const isOpen = ref(false)
const root = ref(null)

const isDesktop = useMediaQuery('(min-width: 1024px)')
const isScrollLocked = useScrollLock()

const currentShort = computed(
  () => LANGUAGES.find((item) => item.code === site.language)?.short ?? "O'z",
)

/** Kapsulada faqat tanlanmagan tillar ko'rsatiladi (mobil panelda — barchasi). */
const otherLanguages = computed(() =>
  LANGUAGES.filter((language) => language.code !== site.language),
)

onClickOutside(root, () => {
  if (isDesktop.value) isOpen.value = false
})

onKeyStroke('Escape', () => {
  isOpen.value = false
})

// Panel ochiq bo'lganda orqa fon skroll qilinmaydi (faqat mobil ko'rinishda).
watch([isOpen, isDesktop], ([open, desktop]) => {
  isScrollLocked.value = open && !desktop
})

function choose(code) {
  isOpen.value = false
  if (code === site.language) return

  // Til almashuvi — manzil almashuvi.
  //
  // Har bir tilning O'Z yo'li bor (`/kursy`, `/ru/kursy`, `/en/kursy`) va
  // aynan o'sha yo'lda o'sha tildagi prerender qilingan HTML yotadi. Router
  // asosi (`historyBase`) sahifa yuklanganda bir marta aniqlanadi, shuning
  // uchun prefiksni SPA ichida almashtirib bo'lmaydi — to'liq o'tish
  // qilamiz. Bu bir sahifa yuklanishiga arziydi: ulashilgan havola,
  // canonical va ekrandagi til endi doim bir xil bo'ladi.
  setLanguage(code)

  // Eski `?lang=` shakli manzilda qolib ketmasin — til endi yo'lda turadi.
  const params = new URLSearchParams(window.location.search)
  params.delete('lang')
  const search = params.toString()
  // `route.path` sayt ichidagi yo'l — brauzerga beriladigan manzilga esa
  // saytning o'z yo'l prefiksi (`/maktab`) ham qo'shilishi shart.
  const target = `${withBase(localePath(route.path, code))}${search ? `?${search}` : ''}${route.hash || ''}`
  window.location.assign(target)
}

</script>

<template>
  <div ref="root" class="relative shrink-0">
    <button
      type="button"
      class="bg-ink hover:text-brand grid size-[2.25rem] place-items-center rounded-pill font-wide font-bold text-white transition lg:size-[3rem]"
      :class="isOpen ? 'text-brand' : ''"
      :aria-expanded="isOpen"
      aria-haspopup="true"
      :aria-label="t('header.languageLabel', { code: currentShort })"
      @click="isOpen = !isOpen"
    >
      {{ currentShort }}
    </button>

    <!-- Katta ekran: tugma ostidagi kapsula -->
    <Transition name="lang">
      <ul
        v-if="isOpen && isDesktop"
        class="lang-menu bg-ink border-line absolute top-[calc(100%+0.5rem)] left-1/2 z-50 flex flex-col gap-1 rounded-pill border p-1 shadow-2xl"
      >
        <li v-for="language in otherLanguages" :key="language.code">
          <button
            type="button"
            class="hover:bg-brand grid size-[3rem] place-items-center rounded-pill font-wide font-bold text-white transition"
            @click="choose(language.code)"
          >
            {{ language.short }}
          </button>
        </li>
      </ul>
    </Transition>

    <!-- Kichik ekran: pastdan ko'tariladigan panel -->
    <Teleport to="body">
      <Transition name="sheet-backdrop">
        <div
          v-if="isOpen && !isDesktop"
          class="fixed inset-0 z-50 bg-black/50 backdrop-blur-md"
          @click="isOpen = false"
        />
      </Transition>

      <Transition name="sheet">
        <div
          v-if="isOpen && !isDesktop"
          class="bg-ink fixed inset-x-0 bottom-0 z-50 rounded-t-block p-6 pb-8 shadow-2xl"
          role="dialog"
          aria-modal="true"
          :aria-label="t('header.chooseLanguage')"
        >
          <div class="flex items-start justify-between gap-4">
            <h2 class="font-wide text-[1.75rem] font-bold text-white">{{ t('header.languageTitle') }}</h2>

            <button
              type="button"
              class="bg-surface hover:bg-brand grid size-[2.75rem] shrink-0 place-items-center rounded-full text-white transition"
              :aria-label="t('header.close')"
              @click="isOpen = false"
            >
              <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M5 5l10 10M15 5L5 15"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>

          <ul class="divide-line mt-6 divide-y">
            <li v-for="language in LANGUAGES" :key="language.code">
              <button
                type="button"
                class="group flex w-full items-center justify-between gap-4 py-4 text-left transition"
                :aria-current="site.language === language.code ? 'true' : undefined"
                @click="choose(language.code)"
              >
                <span
                  class="text-[1.15rem]"
                  :class="site.language === language.code ? 'text-brand' : 'text-white'"
                >
                  {{ language.label }}
                </span>

                <svg
                  class="text-brand size-6 shrink-0 transition-transform group-hover:translate-x-1"
                  viewBox="0 0 20 20"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M4 10h12m0 0-4.5-4.5M16 10l-4.5 4.5"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </li>
          </ul>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* Markazlash faqat `transform` orqali bajariladi: Tailwind'ning `translate`
   yordamchisi bilan aralashib qolsa ro'yxat yon tomonga siljib ketadi. */
.lang-menu {
  transform: translateX(-50%);
  transform-origin: top center;
}

.lang-enter-active,
.lang-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.lang-enter-from,
.lang-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-0.6rem) scaleY(0.85);
}

/* Pastdan ko'tariladigan panel */
.sheet-enter-active,
.sheet-leave-active {
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(100%);
}

.sheet-backdrop-enter-active,
.sheet-backdrop-leave-active {
  transition: opacity 0.25s ease;
}

.sheet-backdrop-enter-from,
.sheet-backdrop-leave-to {
  opacity: 0;
}
</style>
