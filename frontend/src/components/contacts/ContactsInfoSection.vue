<script setup>
/**
 * «Контакты MARS IT School» bo'limi.
 *
 * Chapda yorliq, sarlavha va qisqa matn; o'ngda shishasimon (glass)
 * kartochkalar ustuni: telefon, Telegram, email va ish vaqti.
 * Ma'lumot sayt sozlamalaridan olinadi, bo'sh bo'lsa maketdagi qiymat qoladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchSiteSettings } from '@/api/site'
import OutlineIcon from '@/components/base/OutlineIcon.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSection } from '@/composables/useSection'

const { t } = useI18n()

// Blok matni admin paneldan («Kontaktlar» sahifasi bo'limlari → «Kontaktlar bloki»).
const section = useSection('contacts.info', {
  eyebrow: 'contacts.infoEyebrow',
  title: 'contacts.infoTitle',
  text: 'contacts.infoText',
})

const { data: settings } = useAsyncData(fetchSiteSettings, {})

/** Telegram havolasidan `@nick` ko'rinishidagi nomni ajratib oladi. */
const telegramHandle = computed(() => {
  const url = settings.value.telegram_url || ''
  const nick = url.replace(/\/+$/, '').split('/').pop()
  return nick ? `@${nick.replace(/^@/, '')}` : '@marsitschool'
})

const items = computed(() => {
  const phone = settings.value.phone || '+998 78 777 77 57'
  const email = settings.value.email || 'info@marsit.uz'

  return [
    {
      value: phone,
      label: t('contacts.phone'),
      icon: 'phone',
      href: `tel:${phone.replace(/[^\d+]/g, '')}`,
    },
    {
      value: telegramHandle.value,
      label: 'Telegram',
      icon: 'send',
      href: settings.value.telegram_url || '',
      external: true,
    },
    {
      value: email,
      label: t('contacts.email'),
      icon: 'mail',
      href: `mailto:${email}`,
    },
    {
      value: settings.value.work_hours || t('contacts.defaultWorkHours'),
      label: t('contacts.workHours'),
      icon: 'clock',
      href: '',
    },
  ]
})
</script>

<template>
  <section v-if="section.visible" class="bg-ink section relative overflow-hidden">
    <div
      class="container-page relative grid items-center gap-[var(--spacing-block)] lg:grid-cols-[1fr_1.05fr] lg:gap-[6%]"
    >
      <div v-reveal>
        <p class="eyebrow font-bold">{{ section.eyebrow }}</p>

        <h2 class="title-hero mt-[6%] text-white">
          <span v-for="line in section.titleLines" :key="line" class="block">
            {{ line }}
          </span>
        </h2>

        <p class="text-lead mt-[8%] max-w-[42ch] leading-relaxed text-white/70">
          {{ section.text }}
        </p>
      </div>

      <div class="relative">
        <!-- Kartochkalar ortidagi rangli nur -->
        <div class="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
          <div
            class="absolute top-1/2 -left-[18%] h-[55%] w-[45%] -translate-y-1/2 rounded-full bg-brand/45 blur-[90px]"
          />
          <div
            class="absolute top-1/2 -right-[10%] h-[45%] w-[35%] -translate-y-1/2 rounded-full bg-[#5b53d6]/35 blur-[90px]"
          />
        </div>

        <ul class="flex flex-col gap-[var(--spacing-gutter)]">
          <li v-for="(item, index) in items" :key="item.label" v-reveal="{ delay: index * 90 }">
            <component
              :is="item.href ? 'a' : 'div'"
              :href="item.href || undefined"
              :target="item.external ? '_blank' : undefined"
              :rel="item.external ? 'noopener' : undefined"
              class="contact-card rounded-block flex items-center justify-between gap-[var(--spacing-gutter)] px-[8%] py-[6%] transition duration-300"
              :class="item.href ? 'hover:-translate-y-1 hover:border-white/25' : ''"
            >
              <span class="min-w-0">
                <span class="title-block font-wide block font-bold text-white">
                  {{ item.value }}
                </span>
                <span class="text-small mt-[0.6em] block font-bold text-white/60">
                  {{ item.label }}
                </span>
              </span>

              <OutlineIcon
                :name="item.icon"
                class="h-[2.75rem] w-[2.75rem] shrink-0 text-white/45 lg:h-[3.2vw] lg:w-[3.2vw]"
              />
            </component>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Shishasimon kartochka: yorug'lik yuqori chetdan tushadi */
.contact-card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0.03) 100%),
    rgba(23, 23, 23, 0.55);
  backdrop-filter: blur(18px);
}
</style>
