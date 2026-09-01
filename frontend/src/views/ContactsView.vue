<script setup>
/**
 * «Контакты» sahifasi.
 *
 * Bo'limlar: hero (yo'l, «Всегда на связи» sarlavhasi, tugma va lokatsiya
 * belgisini ushlab turgan astronavt), bog'lanish ma'lumotlari, filiallar
 * xaritasi va sinov darsiga ariza bloki.
 */
import { useI18n } from 'vue-i18n'

import contactsAstronaut from '@/assets/images/Layer-3 2.webp'
import BaseButton from '@/components/base/BaseButton.vue'
import BranchesSection from '@/components/contacts/BranchesSection.vue'
import ContactsInfoSection from '@/components/contacts/ContactsInfoSection.vue'
import TrialLessonSection from '@/components/courses/TrialLessonSection.vue'
import PageHero from '@/components/layout/PageHero.vue'
import { useSeo } from '@/composables/useSeo'

const { t } = useI18n()

// Sarlavha va tavsif `data/seoConfig.js` dan joriy tilda olinadi.
useSeo(() => ({
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.contacts'), path: '/kontakty' },
  ],
}))
</script>

<template>
  <PageHero
    :title="t('contacts.heroTitle').split('\n')"
    :breadcrumbs="[
      { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
      { label: t('nav.contacts') },
    ]"
    :image="contactsAstronaut"
  >
    <template #actions>
      <BaseButton
        size="lg"
        class="font-wide h-[3.5rem] min-w-[15rem] font-bold lg:h-[4.17vw] lg:min-w-[17.7vw]"
        :to="{ name: 'application', query: { source: 'contacts' } }"
      >
        {{ t('common.trialLesson') }}
      </BaseButton>
    </template>
  </PageHero>

  <ContactsInfoSection />

  <BranchesSection />

  <TrialLessonSection
    source="contacts"
    :title="t('contacts.trialTitle').split('\n')"
    :description="t('contacts.trialDescription')"
  />
</template>
