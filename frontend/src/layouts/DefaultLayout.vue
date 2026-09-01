<script setup>
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-ink">
    <AppHeader />

    <!-- Sarlavha `fixed` bo'lgani uchun kontent tepasida joy qoldiriladi. -->
    <main id="main" class="flex-1 pt-[5.5rem] lg:pt-[5.7vw]">
      <RouterView />
    </main>

    <AppFooter />
  </div>
</template>
