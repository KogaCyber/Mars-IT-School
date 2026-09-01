<script setup>
/** Sayt podvali — Figma: «Подвал» komponenti. */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import instagramIcon from '@/assets/icons/social-instagram.svg'
import telegramIcon from '@/assets/icons/social-telegram.svg'
import youtubeIcon from '@/assets/icons/social-youtube.svg'
import logoMars from '@/assets/icons/logo-mars.svg'
import rocketIcon from '@/assets/icons/rocket.svg'
import helperRobot from '@/assets/images/helper-robot.webp'
import { useSiteStore } from '@/stores/site'

// Menyu yozuvlari tarjimadan olinadi — `nav.*` kalitlari bo'yicha.
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
const site = useSiteStore()
const year = new Date().getFullYear()

const phone = computed(() => site.settings.phone || '+78 777 77 57')
const phoneHref = computed(() => `tel:${phone.value.replace(/[^\d+]/g, '')}`)
const phoneParts = computed(() => {
  const [first, ...rest] = phone.value.trim().split(' ')
  return { first, rest: rest.join(' ') }
})

const socials = computed(() =>
  [
    { label: 'Instagram', url: site.settings.instagram_url, icon: instagramIcon },
    { label: 'Telegram', url: site.settings.telegram_url, icon: telegramIcon },
    { label: 'YouTube', url: site.settings.youtube_url, icon: youtubeIcon },
  ].filter((item) => Boolean(item.url)),
)
</script>

<template>
  <footer class="relative border-t border-surface bg-ink">
    <div class="container-page relative py-[var(--spacing-section)]">
      <div class="grid gap-12 lg:grid-cols-3">
        <div>
          <img
            loading="lazy"
            decoding="async"
            :src="logoMars"
            alt="MARS IT School"
            class="h-[2rem] w-auto lg:h-[2.45vw]"
          />
          <p class="mt-6 max-w-xs text-base leading-relaxed text-white">
            {{ t('footer.tagline') }}
          </p>
        </div>

        <nav :aria-label="t('footer.menuLabel')">
          <h2 class="text-lead font-wide font-bold text-white">{{ t('footer.navigation') }}</h2>
          <ul class="mt-6 flex flex-col gap-5">
            <li v-for="link in NAV_LINKS" :key="link.name">
              <RouterLink
                :to="{ name: link.name }"
                class="rocket-fly flex items-center gap-1 text-base text-white transition hover:text-brand"
              >
                {{ t(`nav.${link.name}`) }}
                <span v-if="link.icon" class="rocket-slot" aria-hidden="true">
                  <img loading="lazy" decoding="async" :src="link.icon" alt="" />
                </span>
              </RouterLink>
            </li>
          </ul>
        </nav>

        <div class="lg:text-right">
          <a
            :href="phoneHref"
            class="section-title font-wide font-bold text-white transition hover:opacity-80"
          >
            <span class="text-brand">{{ phoneParts.first }}</span> {{ phoneParts.rest }}
          </a>
          <p class="mt-4 text-base text-white">{{ t('footer.workingHours') }}</p>

          <a
            v-if="site.settings.email"
            :href="`mailto:${site.settings.email}`"
            class="text-lead mt-[6%] block font-wide font-bold text-white transition hover:text-brand"
          >
            {{ site.settings.email }}
          </a>

          <ul v-if="socials.length" class="mt-6 flex gap-3 lg:justify-end">
            <li v-for="social in socials" :key="social.label">
              <a
                :href="social.url"
                target="_blank"
                rel="noopener noreferrer"
                class="grid size-[2.75rem] place-items-center rounded-full bg-surface text-white transition hover:bg-brand"
                :aria-label="social.label"
              >
                <img
                  loading="lazy"
                  decoding="async"
                  :src="social.icon"
                  alt=""
                  aria-hidden="true"
                  class="size-[1.125rem]"
                />
              </a>
            </li>
          </ul>
        </div>
      </div>

      <img
        loading="lazy"
        decoding="async"
        :src="helperRobot"
        alt=""
        aria-hidden="true"
        class="pointer-events-none absolute right-0 bottom-0 hidden size-[6.25vw] object-contain lg:block"
      />
    </div>

    <div class="border-t border-surface">
      <div
        class="container-page flex flex-col gap-3 py-5 text-sm text-muted sm:flex-row sm:items-center sm:justify-between"
      >
        <p>{{ t('footer.rights', { year }) }}</p>
        <div class="flex gap-6">
          <a href="#" class="transition hover:text-white">{{ t('footer.offer') }}</a>
          <a :href="site.settings.privacy_policy_url || '#'" class="transition hover:text-white">
            {{ t('footer.privacy') }}
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
