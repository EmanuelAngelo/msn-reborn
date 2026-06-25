import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { useTheme } from './composables/useTheme'
import { useLocale } from './composables/useLocale'

const { initTheme } = useTheme()
initTheme()

const { initLocale } = useLocale()
initLocale()

createApp(App).mount('#app')
