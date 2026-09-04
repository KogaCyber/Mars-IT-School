<script setup>
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useAutoReveal } from '@/composables/useAutoReveal'

// Sayt bo'ylab bo'limlar skrollda o'z-o'zidan yumshoq ochiladi.
useAutoReveal('#main')
</script>

<template>
  <div class="flex min-h-screen flex-col bg-ink">
    <AppHeader />

    <!-- Sarlavha `fixed` bo'lgani uchun kontent tepasida joy qoldiriladi. -->
    <main id="main" class="flex-1 pt-[5.5rem] lg:pt-[5.7vw]">
      <!-- Sahifa almashganda yumshoq o'tish. Ba'zi sahifalarda bir nechta
           ildiz element bor, shuning uchun ular o'ram `div` ichida beriladi. -->
      <RouterView v-slot="{ Component, route }">
        <Transition name="page" mode="out-in">
          <div :key="route.path">
            <component :is="Component" />
          </div>
        </Transition>
      </RouterView>
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
/* Eskisi tez so'nadi, yangisi pastdan ko'tarilib ochiladi. */
.page-enter-active {
  transition:
    opacity 0.45s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.45s cubic-bezier(0.22, 1, 0.36, 1),
    filter 0.45s ease;
}

.page-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(1.5rem);
  filter: blur(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}

@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition-duration: 0.01ms;
  }

  .page-enter-from,
  .page-leave-to {
    opacity: 1;
    transform: none;
    filter: none;
  }
}
</style>
