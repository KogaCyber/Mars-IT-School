<script setup>
/**
 * «Частые вопросы» — Figma: chapda astronavt va savol belgisi, o'ngda akkordeon.
 * Javob balandlik bo'yicha silliq ochiladi/yopiladi.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import faqAstronaut from '@/assets/images/faq-astronaut.webp'
import faqQuestion from '@/assets/images/faq-question.webp'

const { t } = useI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const openId = ref(null)

// Ma'lumot yuklangach birinchi savol ochiq turadi (Figma'dagidek).
watch(
  () => props.items,
  (items) => {
    if (openId.value === null && items.length) openId.value = items[0].id
  },
  { immediate: true },
)

function toggle(id) {
  openId.value = openId.value === id ? null : id
}

/* --- Balandlik bo'yicha silliq ochilish (CSS `height: auto` animatsiyalanmaydi) --- */
function onEnter(el) {
  el.style.height = '0px'
  el.style.opacity = '0'
  // Brauzer boshlang'ich holatni qayd etishi uchun majburiy reflow.
  void el.offsetHeight
  el.style.height = `${el.scrollHeight}px`
  el.style.opacity = '1'
}

function onAfterEnter(el) {
  el.style.height = 'auto'
}

function onLeave(el) {
  el.style.height = `${el.scrollHeight}px`
  void el.offsetHeight
  el.style.height = '0px'
  el.style.opacity = '0'
}
</script>

<template>
  <section v-if="props.items.length" v-reveal class="section bg-ink overflow-hidden">
    <div class="container-page grid gap-[4%] lg:grid-cols-2 lg:items-start">
      <!-- Bezak: astronavt va savol belgisi -->
      <div class="relative order-2 hidden lg:order-1 lg:block">
        <img
          loading="lazy"
          decoding="async"
          :src="faqQuestion"
          alt=""
          aria-hidden="true"
          class="animate-glow absolute top-0 left-[38%] w-[45%]"
        />
        <img
          loading="lazy"
          decoding="async"
          :src="faqAstronaut"
          alt=""
          aria-hidden="true"
          class="animate-float relative w-[70%]"
        />
      </div>

      <div class="order-1 lg:order-2">
        <p class="eyebrow">{{ t('home.faqEyebrow') }}</p>
        <h2 class="section-title mt-[4%] text-white">{{ t('home.faqTitle') }}</h2>

        <ul class="border-line mt-[8%] flex flex-col border-t">
          <li v-for="item in props.items" :key="item.id" class="border-line border-b">
            <h3>
              <button
                type="button"
                class="group flex w-full items-center justify-between gap-6 py-[1.3em] text-left"
                :aria-expanded="openId === item.id"
                :aria-controls="`faq-${item.id}`"
                @click="toggle(item.id)"
              >
                <span
                  class="title-block font-wide font-bold transition-colors"
                  :class="openId === item.id ? 'text-white' : 'text-white group-hover:text-brand'"
                >
                  {{ item.question }}
                </span>

                <!-- Ochiq holatda «+» «−» ga aylanadi -->
                <span
                  class="bg-surface relative grid size-[2.5rem] shrink-0 place-items-center rounded-full transition-colors duration-300"
                  :class="openId === item.id ? 'text-brand' : 'text-white'"
                  aria-hidden="true"
                >
                  <span class="absolute h-[1.5px] w-[0.9rem] rounded bg-current" />
                  <span
                    class="absolute h-[1.5px] w-[0.9rem] rounded bg-current transition-transform duration-300"
                    :class="openId === item.id ? 'rotate-0' : 'rotate-90'"
                  />
                </span>
              </button>
            </h3>

            <Transition name="answer" @enter="onEnter" @after-enter="onAfterEnter" @leave="onLeave">
              <div v-show="openId === item.id" :id="`faq-${item.id}`" class="answer">
                <div
                  class="border-brand border-t pt-[1.2em] pb-[1.6em] leading-relaxed text-white/60"
                >
                  {{ item.answer }}
                </div>
              </div>
            </Transition>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.answer {
  overflow: hidden;
  transition:
    height 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.3s ease;
}

@media (prefers-reduced-motion: reduce) {
  .answer {
    transition: none;
  }
}
</style>
