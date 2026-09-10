<script setup>
/**
 * Ekranning o'ng pastida turadigan AI yordamchisi.
 *
 * Tugma — `helper-robot` rasmi: u yengil "suzib" turadi va atrofida to'lqin
 * tarqaladi, shuning uchun sahifa fonida ko'zga tashlanadi. Bosilganda o'sha
 * burchakdan chat paneli "o'sib chiqadi" (transform-origin: pastki o'ng burchak).
 *
 * Javoblarni `composables/useAiChat.js` beradi — bu komponent faqat ko'rinish
 * va animatsiyaga javob beradi.
 */
import { onKeyStroke } from '@vueuse/core'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import robotImage from '@/assets/images/helper-robot.webp'
import { useAiChat } from '@/composables/useAiChat'

const { t } = useI18n()
const {
  isOpen,
  isTyping,
  messages,
  wasOpened,
  quickQuestions,
  showQuick,
  close,
  toggle,
  ask,
  reset,
} = useAiChat()

const draft = ref('')
const inputEl = ref(null)
const listEl = ref(null)
/** Tanishtiruvchi bulutcha — panel hech ochilmagan bo'lsa, biroz kutib chiqadi. */
const showInvite = ref(false)

let hideTimer = null
const showTimer = setTimeout(() => {
  if (wasOpened.value) return
  showInvite.value = true
  // Bulutcha kontentni to'sib qolmasin — o'qishga ulguradigan vaqtdan keyin
  // o'zi yo'qoladi, robot tugmasi esa joyida qoladi.
  hideTimer = setTimeout(() => (showInvite.value = false), 9000)
}, 6000)

onBeforeUnmount(() => {
  clearTimeout(showTimer)
  clearTimeout(hideTimer)
})

/** Yangi xabar qo'shilganda ro'yxat oxiriga siljiydi. */
async function scrollToEnd() {
  await nextTick()
  const list = listEl.value
  if (list) list.scrollTo({ top: list.scrollHeight, behavior: 'smooth' })
}

watch([() => messages.value.length, isTyping], scrollToEnd)

watch(isOpen, async (value) => {
  showInvite.value = false
  if (!value) return
  await scrollToEnd()
  // Sensorli ekranda klaviatura o'zi ochilib ketmasin.
  if (window.matchMedia('(hover: hover)').matches) inputEl.value?.focus()
})

onKeyStroke('Escape', () => isOpen.value && close())

function submit() {
  const text = draft.value.trim()
  if (!text) return
  draft.value = ''
  ask(text)
}
</script>

<template>
  <Teleport to="body">
    <!-- Chat paneli -->
    <Transition name="chat">
      <section
        v-if="isOpen"
        class="chat-panel border-line bg-surface fixed inset-x-3 bottom-[calc(4%+4.25rem)] z-[65] flex max-h-[70dvh] flex-col overflow-hidden rounded-card border shadow-2xl sm:inset-x-auto sm:right-[4%] sm:bottom-[calc(4%+5rem)] sm:max-h-[min(34rem,calc(100dvh-11rem))] sm:w-[23rem]"
        role="dialog"
        aria-modal="false"
        :aria-label="t('assistant.name')"
      >
        <!-- Sarlavha -->
        <header class="border-line flex items-center gap-3 border-b bg-white/3 px-4 py-3">
          <span
            class="from-brand relative grid size-10 shrink-0 place-items-center rounded-full bg-gradient-to-br to-[#3b2f7a]"
          >
            <img :src="robotImage" alt="" class="size-8 object-contain" />
            <span
              class="bg-surface absolute -right-0.5 -bottom-0.5 grid size-3.5 place-items-center rounded-full"
            >
              <span class="online-dot size-2 rounded-full bg-[#3ddc84]" />
            </span>
          </span>

          <span class="min-w-0 flex-1">
            <span class="font-wide block truncate text-white">{{ t('assistant.name') }}</span>
            <span class="text-small text-muted block truncate"
              >{{ t('assistant.online') }} · {{ t('assistant.role') }}</span
            >
          </span>

          <button
            type="button"
            class="text-muted press grid size-8 shrink-0 place-items-center rounded-full transition hover:bg-white/8 hover:text-white"
            :aria-label="t('assistant.restart')"
            :title="t('assistant.restart')"
            @click="reset()"
          >
            <svg class="size-4" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M13 8a5 5 0 1 1-1.6-3.7M13 2v3h-3"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <button
            type="button"
            class="text-muted press grid size-8 shrink-0 place-items-center rounded-full transition hover:bg-white/8 hover:text-white"
            :aria-label="t('assistant.close')"
            @click="close()"
          >
            <svg class="size-4" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M4 4l8 8M12 4l-8 8"
                stroke="currentColor"
                stroke-width="1.6"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </header>

        <!-- Xabarlar -->
        <div ref="listEl" class="flex-1 overflow-y-auto overscroll-contain px-4 py-4">
          <TransitionGroup tag="div" name="bubble" class="relative flex flex-col gap-2.5">
            <div
              v-for="message in messages"
              :key="message.id"
              class="flex max-w-[85%] flex-col gap-2"
              :class="message.role === 'user' ? 'self-end items-end' : 'self-start items-start'"
            >
              <p
                class="text-body rounded-2xl px-3.5 py-2.5 whitespace-pre-line"
                :class="
                  message.role === 'user'
                    ? 'bg-brand rounded-br-sm text-white'
                    : 'bg-surface-2 rounded-bl-sm text-white/90'
                "
              >
                {{ message.text }}
              </p>

              <span v-if="message.links?.length" class="flex flex-wrap gap-2">
                <RouterLink
                  v-for="link in message.links"
                  :key="`${link.name}-${link.label}`"
                  :to="link.href ? link.href : { name: link.name, params: link.params }"
                  class="text-small border-brand/40 text-brand press hover:bg-brand inline-flex items-center gap-1 rounded-pill border px-3 py-1.5 transition hover:text-white"
                  @click="close()"
                >
                  {{ link.label }}
                  <svg class="size-3" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                    <path
                      d="M4 2.5L7.5 6 4 9.5"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </RouterLink>
              </span>
            </div>

            <!-- «Yozmoqda…» -->
            <div
              v-if="isTyping"
              key="typing"
              class="bg-surface-2 flex items-center gap-1.5 self-start rounded-2xl rounded-bl-sm px-4 py-3.5"
              :aria-label="t('assistant.typing')"
            >
              <span
                v-for="dot in 3"
                :key="dot"
                class="typing-dot bg-muted size-1.5 rounded-full"
                :style="{ animationDelay: `${(dot - 1) * 0.16}s` }"
              />
            </div>
          </TransitionGroup>
        </div>

        <!-- Tez-tez so'raladigan savollar -->
        <div v-if="showQuick" class="px-4 pb-1">
          <p class="text-small text-muted mb-2">{{ t('assistant.hint') }}</p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="question in quickQuestions"
              :key="question.id"
              type="button"
              class="text-small border-line text-muted press hover:border-brand/50 rounded-pill border px-3 py-1.5 transition hover:text-white"
              @click="ask(question.label, question.id)"
            >
              {{ question.label }}
            </button>
          </div>
        </div>

        <!-- Kiritish maydoni -->
        <form
          class="border-line flex items-center gap-2 border-t px-3 py-3"
          @submit.prevent="submit"
        >
          <input
            ref="inputEl"
            v-model="draft"
            type="text"
            :placeholder="t('assistant.placeholder')"
            :aria-label="t('assistant.placeholder')"
            maxlength="300"
            autocomplete="off"
            class="text-body bg-surface-2 placeholder:text-muted min-w-0 flex-1 rounded-pill px-4 py-2.5 text-white outline-none focus:outline-2 focus:outline-offset-2 focus:outline-brand"
          />
          <button
            type="submit"
            class="bg-brand hover:bg-brand-hover press grid size-10 shrink-0 place-items-center rounded-full text-white transition disabled:opacity-40"
            :disabled="!draft.trim()"
            :aria-label="t('assistant.send')"
          >
            <svg class="size-4" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M2 8h11M8.5 3.5L13 8l-4.5 4.5"
                stroke="currentColor"
                stroke-width="1.6"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </form>

        <p class="text-small text-muted px-4 pb-3 text-center">{{ t('assistant.note') }}</p>
      </section>
    </Transition>

    <!-- Taklif bulutchasi -->
    <Transition name="invite">
      <button
        v-if="showInvite && !isOpen"
        type="button"
        class="text-small border-line bg-surface press hover:border-brand/50 fixed right-[calc(4%+4.75rem)] bottom-[calc(4%+1.5rem)] z-[66] max-w-[13rem] rounded-2xl rounded-br-sm border px-3.5 py-2.5 text-left text-white/90 shadow-xl transition"
        @click="toggle()"
      >
        {{ t('assistant.invite') }}
      </button>
    </Transition>

    <!-- Robot tugmasi -->
    <button
      type="button"
      class="launcher press fixed right-[4%] bottom-[4%] z-[70] grid size-[4.5rem] place-items-center rounded-full lg:size-[5rem]"
      :aria-label="isOpen ? t('assistant.close') : t('assistant.open')"
      :aria-expanded="isOpen"
      @click="toggle()"
    >
      <Transition name="swap" mode="out-in">
        <!-- Chat ochiq: robot o'rnida yopish belgisi. Fon shu holatdagina
             kerak — aks holda belgi sahifa ustida osilib qolardi. -->
        <span
          v-if="isOpen"
          key="close"
          class="border-line bg-surface grid size-[2.75rem] place-items-center rounded-full border text-white shadow-lg lg:size-[3rem]"
        >
          <svg class="size-5" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path
              d="M4 4l8 8M12 4l-8 8"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
        </span>

        <img
          v-else
          key="robot"
          :src="robotImage"
          alt=""
          width="360"
          height="360"
          class="robot size-full object-contain"
        />
      </Transition>
    </button>
  </Teleport>
</template>

<style scoped>
/* --- Robot tugmasi ------------------------------------------------------ */
/* Tugmaning o'z foni yo'q — sahifada faqat robotning o'zi turadi. */
.launcher {
  background: none;
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.launcher:hover {
  transform: scale(1.08);
}

.robot {
  animation: robot-float 3.6s ease-in-out infinite;
  /* Soya robotni fondan ajratib turadi (fon doirasi o'rniga). */
  filter: drop-shadow(0 0.4rem 0.7rem rgb(0 0 0 / 0.55));
}

.launcher:hover .robot {
  animation-duration: 1.8s;
}

@keyframes robot-float {
  0%,
  100% {
    transform: translateY(-4%) rotate(-3deg);
  }
  50% {
    transform: translateY(4%) rotate(3deg);
  }
}

/* Robot ↔ yopish belgisi almashuvi */
.swap-enter-active,
.swap-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.swap-enter-from {
  opacity: 0;
  transform: scale(0.6) rotate(-90deg);
}
.swap-leave-to {
  opacity: 0;
  transform: scale(0.6) rotate(90deg);
}

/* --- Panel -------------------------------------------------------------- */
.chat-panel {
  transform-origin: bottom right;
  backdrop-filter: blur(0.75rem);
}

.chat-enter-active {
  transition:
    opacity 0.24s ease,
    transform 0.34s cubic-bezier(0.22, 1.4, 0.36, 1);
}
.chat-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(1rem) scale(0.9);
}

/* --- Xabarlar ----------------------------------------------------------- */
.bubble-enter-active {
  transition:
    opacity 0.28s ease,
    transform 0.28s cubic-bezier(0.22, 1, 0.36, 1);
}
.bubble-enter-from {
  opacity: 0;
  transform: translateY(0.5rem) scale(0.96);
}
.bubble-leave-active {
  position: absolute;
  opacity: 0;
}

.typing-dot {
  animation: typing 1.1s ease-in-out infinite;
}

@keyframes typing {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-0.25rem);
    opacity: 1;
  }
}

.online-dot {
  animation: online 2s ease-in-out infinite;
}

@keyframes online {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgb(61 220 132 / 0.6);
  }
  70% {
    box-shadow: 0 0 0 0.35rem rgb(61 220 132 / 0);
  }
}

/* --- Taklif bulutchasi -------------------------------------------------- */
.invite-enter-active,
.invite-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.invite-enter-from,
.invite-leave-to {
  opacity: 0;
  transform: translateX(0.75rem) scale(0.95);
}

@media (prefers-reduced-motion: reduce) {
  .robot,
  .typing-dot,
  .online-dot {
    animation: none !important;
  }
  .chat-enter-active,
  .chat-leave-active,
  .bubble-enter-active,
  .invite-enter-active,
  .invite-leave-active {
    transition-duration: 0.01ms;
  }
}
</style>
