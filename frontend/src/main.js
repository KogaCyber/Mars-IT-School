import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { reveal } from './directives/reveal'
import i18n from './i18n'
import router from './router'

import '@/assets/styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(i18n)
app.use(router)

// Skroll paytida bo'limlarni yumshoq ko'rsatuvchi direktiva.
app.directive('reveal', reveal)

// Kutilmagan xatoliklar konsolda ko'rinsin, lekin ilova qulamasin.
app.config.errorHandler = (error, instance, info) => {
  console.error('[Mars] Ilova xatoligi:', error, info)
}

app.mount('#app')
