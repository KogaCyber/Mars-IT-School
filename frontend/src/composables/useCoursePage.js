/**
 * Kurs sahifasining (IT Kids, IT-dasturlash) admin paneldan boshqariladigan qismi.
 *
 * Sahifa maketda qat'iy belgilangan bo'lib, matnlari `data/itKids.js` va
 * `data/itDev.js` da yotardi — ya'ni admin panelda o'zgartirib bo'lmasdi.
 * Endi har bir blok «bo'lim» sifatida panelda turadi, maketdagi ma'lumot esa
 * zaxira bo'lib qoladi: admin panelda biror element qo'shilmagan bo'lsa
 * (yoki rasm yuklanmagan bo'lsa), sayt eski ko'rinishini saqlaydi.
 *
 *   const page = useCoursePage('itkids', { facts: IT_KIDS_FACTS, ... })
 *   page.facts.value    // [{ value, label }]
 *   page.hero.value.visible  // blok admin panelda yoqilganmi
 *   page.stages.value   // [{ number, title, duration, description, topics, tools, result }]
 */
import { computed } from 'vue'

import { useSection } from '@/composables/useSection'
import { useLocalized } from '@/i18n/localize'

/** Vergul bilan yozilgan texnologiya kalitlari → massiv. */
const toKeys = (value) =>
  String(value || '')
    .split(',')
    .map((key) => key.trim())
    .filter(Boolean)

/**
 * @param {string} page bo'lim kaliti prefiksi — `itkids` yoki `itdev`
 * @param {{facts: any[], topics: any[], stages: any[], gallery: any[], summary: any,
 *          heroTitleKey: string, aboutTitleKey: string, aboutTextKey: string,
 *          heroTextKey?: string}} fallback maketdagi ma'lumot va tarjima kalitlari
 */
export function useCoursePage(page, fallback) {
  const heroSection = useSection(`${page}.hero`, {
    title: fallback.heroTitleKey,
    text: fallback.heroTextKey,
    buttonLabel: 'common.trialLesson',
    button2Label: 'courses.programButton',
  })
  const factsSection = useSection(`${page}.facts`)
  const aboutSection = useSection(`${page}.about`, {
    eyebrow: 'courses.aboutEyebrow',
    title: fallback.aboutTitleKey,
    text: fallback.aboutTextKey,
  })
  const stagesSection = useSection(`${page}.stages`, {
    eyebrow: 'courses.programEyebrow',
    title: 'courses.stagesTitle',
    text: 'courses.stagesDescription',
  })
  const gallerySection = useSection(`${page}.gallery`, {
    eyebrow: 'courses.galleryEyebrow',
    title: 'courses.galleryTitle',
    text: 'courses.galleryDescription',
  })

  const staticFacts = useLocalized(fallback.facts)
  const staticTopics = useLocalized(fallback.topics)
  const staticStages = useLocalized(fallback.stages)
  const staticGallery = useLocalized(fallback.gallery)
  const staticSummary = useLocalized(fallback.summary)

  const facts = computed(() => {
    const items = factsSection.value.items
    if (!items.length) return staticFacts.value
    return items.map((item) => ({ value: item.value, label: item.label }))
  })

  const topics = computed(() => {
    const items = aboutSection.value.items
    if (!items.length) return staticTopics.value
    return items.map((item, index) => ({
      title: item.title,
      description: item.text,
      // Ikonka nomi bo'sh bo'lsa — maketdagi o'sha o'rindagi ikonka.
      icon: item.icon_name || staticTopics.value[index]?.icon || 'code',
    }))
  })

  const stages = computed(() => {
    const items = stagesSection.value.items
    if (!items.length) return staticStages.value
    return items.map((item, index) => ({
      number: item.value || String(index + 1).padStart(2, '0'),
      title: item.title,
      duration: item.label,
      description: item.text,
      topics: item.list ?? [],
      tools: item.icon_name ? toKeys(item.icon_name) : (staticStages.value[index]?.tools ?? []),
      result: item.note,
    }))
  })

  const gallery = computed(() => {
    const items = gallerySection.value.items
    if (!items.length) return staticGallery.value
    return items
      .map((item, index) => ({
        src: item.image || staticGallery.value[index]?.src || '',
        alt: item.text || '',
      }))
      .filter((image) => image.src)
  })

  const stagesSummary = computed(() => stagesSection.value.note || staticSummary.value)

  return {
    hero: heroSection,
    // Faktlar chizig'ining o'zi — «saytda ko'rsatilsin» belgisi uchun kerak.
    factsBlock: factsSection,
    about: aboutSection,
    stages: stagesSection,
    gallery: gallerySection,
    facts,
    topics,
    stageList: stages,
    galleryImages: gallery,
    stagesSummary,
  }
}
