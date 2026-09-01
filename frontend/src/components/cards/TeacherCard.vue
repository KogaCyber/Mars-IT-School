<script setup>
/** O'qituvchi kartochkasi — Figma: rasm chapda, statistika va texnologiyalar o'ngda. */
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  teacher: { type: Object, required: true },
})
</script>

<template>
  <article
    class="bg-surface rounded-block flex h-full flex-col gap-[5%] p-[4%] transition duration-300 hover:-translate-y-1 md:flex-row"
  >
    <div
      v-if="teacher.photo"
      class="rounded-card bg-ink aspect-square w-full shrink-0 overflow-hidden md:w-[38%]"
    >
      <img
        :src="teacher.photo"
        :alt="teacher.full_name"
        loading="lazy"
        class="size-full object-cover"
      />
    </div>

    <div class="flex flex-1 flex-col">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h3 class="title-block font-wide font-bold text-white">{{ teacher.full_name }}</h3>
        <span
          v-if="teacher.badge"
          class="bg-ink text-small rounded-pill px-[1.2em] py-[0.6em] font-wide font-bold text-white"
        >
          {{ teacher.badge }}
        </span>
      </div>

      <!-- Statistika kapsulalari -->
      <dl class="mt-[6%] flex flex-wrap gap-3">
        <div
          v-if="teacher.students_count"
          class="rounded-pill flex-1 px-[1.5em] py-[1em]"
          style="background: linear-gradient(120deg, rgba(233, 73, 33, 0.35), rgba(37, 37, 37, 1))"
        >
          <dt class="font-wide text-[1.35em] font-bold text-white">
            {{ teacher.students_count }}+
          </dt>
          <dd class="text-small text-white/60">{{ t('cards.students') }}</dd>
        </div>

        <div
          v-if="teacher.experience_years"
          class="rounded-pill flex-1 px-[1.5em] py-[1em]"
          style="background: linear-gradient(120deg, rgba(59, 47, 122, 0.5), rgba(37, 37, 37, 1))"
        >
          <dt class="font-wide text-[1.35em] font-bold text-white">
            {{ t('cards.experienceYears', { years: teacher.experience_years }) }}
          </dt>
          <dd class="text-small text-white/60">{{ t('cards.experience') }}</dd>
        </div>
      </dl>

      <template v-if="teacher.position || teacher.bio">
        <h4 class="mt-[7%] font-wide font-bold text-white">{{ t('cards.specialization') }}</h4>
        <p class="mt-[2%] line-clamp-3 leading-relaxed text-white/60">
          {{ teacher.bio || teacher.position }}
        </p>
      </template>

      <!-- Texnologiyalar -->
      <ul v-if="teacher.skills?.length" class="mt-auto flex flex-wrap gap-2 pt-[7%]">
        <li
          v-for="skill in teacher.skills"
          :key="skill.id"
          class="bg-ink rounded-pill flex items-center gap-1.5 px-[0.85em] py-[0.5em]"
        >
          <img
            loading="lazy"
            decoding="async"
            v-if="skill.icon"
            :src="skill.icon"
            alt=""
            aria-hidden="true"
            class="size-[1em] object-contain"
          />
          <span class="text-[0.8rem] whitespace-nowrap text-white">{{ skill.name }}</span>
        </li>
      </ul>
    </div>
  </article>
</template>
