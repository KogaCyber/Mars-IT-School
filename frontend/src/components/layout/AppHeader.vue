<script setup>
/**
 * Sayt sarlavhasi — Figma: yumaloq (pill) shaklidagi shaffof panel.
 *
 * Panel doim shaffof: tepada deyarli ko'rinmas shisha (`bg-white/[0.07]`),
 * skrolldan keyin biroz to'qroq (`bg-ink/60`) — oq bo'limlar ustida ham
 * oq matn o'qiladi. Chuqurlikni rang emas, `backdrop-filter` beradi.
 */
import { useWindowScroll } from '@vueuse/core'
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import logoMars from '@/assets/icons/logo-mars.svg'
import rocketIcon from '@/assets/icons/rocket.svg'
import LanguageSwitcher from '@/components/layout/LanguageSwitcher.vue'
import { useScrollLock } from '@/composables/useScrollLock'
import { useSiteStore } from '@/stores/site'
import { useUiStore } from '@/stores/ui'

// Menyu yozuvlari tarjimadan olinadi — `label` kaliti `nav.*` ga ishora qiladi.
const NAV_LINKS = [
  { name: 'about' },
  { name: 'courses' },
  { name: 'space', icon: rocketIcon },
  { name: 'quiz' },
  { name: 'news' },
  { name: 'vacancies' },
  { name: 'contacts' },
]

const { t } = useI18n()
const route = useRoute()
const ui = useUiStore()
const site = useSiteStore()
const { y } = useWindowScroll()

// Menyu ochiq bo'lganda orqa fon skroll qilinmaydi.
const isScrollLocked = useScrollLock()

const isScrolled = computed(() => y.value > 20)
const phone = computed(() => site.settings.phone || '+998 78 777 77 57')
const phoneHref = computed(() => `tel:${phone.value.replace(/[^\d+]/g, '')}`)

/** Telefon raqamning birinchi bo'lagi to'q sariq rangda ko'rsatiladi. */
const phoneParts = computed(() => {
  const [first, ...rest] = phone.value.trim().split(' ')
  return { first, rest: rest.join(' ') }
})

watch(
  () => ui.isMobileMenuOpen,
  (open) => {
    isScrollLocked.value = open
  },
)

// Sahifa almashganda mobil menyu yopiladi.
watch(
  () => route.fullPath,
  () => ui.toggleMobileMenu(false),
)
</script>

<template>
  <header class="pointer-events-none fixed inset-x-0 top-0 z-40 pt-3 md:pt-5">
    <div class="container-page">
      <div
        class="header-pill pointer-events-auto flex h-[3.5rem] items-center justify-between gap-3 rounded-pill border border-white/10 px-5 transition-colors duration-300 lg:h-[4.7vw] lg:gap-[2%] lg:px-[2%]"
        :class="isScrolled || ui.isMobileMenuOpen ? 'bg-ink/60' : 'bg-white/[0.07]'"
      >
        <RouterLink :to="{ name: 'home' }" :aria-label="t('header.logoAlt')">
          <img
            loading="lazy"
            decoding="async"
            :src="logoMars"
            alt="MARS IT School"
            class="h-[1.15rem] w-auto lg:h-[1.56vw] mb-2"
          />
        </RouterLink>

        <nav class="hidden items-center gap-[1.56vw] xl:flex" :aria-label="t('header.mainMenu')">
          <RouterLink
            v-for="link in NAV_LINKS"
            :key="link.name"
            :to="{ name: link.name }"
            class="rocket-fly hover:text-brand flex items-center gap-[0.25em] whitespace-nowrap text-white/90 transition"
            active-class="text-brand"
          >
            {{ t(`nav.${link.name}`) }}
            <span v-if="link.icon" class="rocket-slot" aria-hidden="true">
              <img loading="lazy" decoding="async" :src="link.icon" alt="" />
            </span>
          </RouterLink>
        </nav>

        <div class="flex items-center gap-2 md:gap-3 lg:gap-6">
          <a
            :href="phoneHref"
            class="title-block hover:opacity-80 hidden font-wide font-bold whitespace-nowrap text-white transition lg:block"
          >
            <span class="text-brand">{{ phoneParts.first }}</span>
            {{ ' ' }}{{ phoneParts.rest }}
          </a>

          <LanguageSwitcher />

          <button
            type="button"
            class="grid size-[2.25rem] place-items-center rounded-pill transition xl:hidden"
            :class="ui.isMobileMenuOpen ? 'bg-brand text-white' : 'text-white hover:bg-white/10'"
            :aria-expanded="ui.isMobileMenuOpen"
            aria-controls="mobile-menu"
            :aria-label="t('header.menu')"
            @click="ui.toggleMobileMenu()"
          >
            <svg class="size-[1.1rem]" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                :d="ui.isMobileMenuOpen ? 'M6 6l12 12M18 6L6 18' : 'M4 7h16M4 12h16M4 17h16'"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobil menyu: fon xiralashadi, sahifa skroll qilinmaydi -->
    <Teleport to="body">
      <Transition name="backdrop">
        <div
          v-if="ui.isMobileMenuOpen"
          class="fixed inset-0 z-30 bg-black/40 backdrop-blur-md xl:hidden"
          @click="ui.toggleMobileMenu(false)"
        />
      </Transition>
    </Teleport>

    <div class="container-page">
      <Transition name="menu">
        <nav
          v-if="ui.isMobileMenuOpen"
          id="mobile-menu"
          class="border-line bg-ink/80 pointer-events-auto mt-3 max-h-[calc(100dvh-5.5rem)] overflow-y-auto rounded-block border backdrop-blur-xl xl:hidden"
          :aria-label="t('header.mobileMenu')"
        >
          <ul class="divide-line divide-y px-5">
            <li v-for="link in NAV_LINKS" :key="link.name">
              <RouterLink
                :to="{ name: link.name }"
                class="group rocket-fly hover:bg-brand/15 -mx-5 flex items-center justify-between gap-4 px-5 py-4 transition"
                active-class="bg-brand/15"
              >
                <span class="flex items-center gap-2 text-[1.05rem] text-white">
                  {{ t(`nav.${link.name}`) }}
                  <span v-if="link.icon" class="rocket-slot" aria-hidden="true">
                    <img loading="lazy" decoding="async" :src="link.icon" alt="" />
                  </span>
                </span>

                <svg
                  class="text-brand size-5 shrink-0 transition-transform group-hover:translate-x-1"
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
              </RouterLink>
            </li>
          </ul>

          <a
            :href="phoneHref"
            class="border-line block border-t px-5 py-4 font-wide text-[1.1rem] font-bold text-white"
          >
            <span class="text-brand">{{ phoneParts.first }}</span> {{ phoneParts.rest }}
          </a>
        </nav>
      </Transition>
    </div>
  </header>
</template>

<style scoped>
/* Shisha effekti: fon xiralashadi va biroz to'yinadi — panel «qora plita»
   emas, ostidagi kontentni ko'rsatuvchi qatlam bo'lib qoladi. */
.header-pill {
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  box-shadow: 0 12px 40px -24px rgba(0, 0, 0, 0.8);
}

.menu-enter-active,
.menu-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-0.75rem);
}

.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity 0.25s ease;
}

.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
}
</style>
