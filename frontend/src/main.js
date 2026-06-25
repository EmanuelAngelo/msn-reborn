import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { useTheme } from './composables/useTheme'

const { initTheme } = useTheme()
initTheme()

createApp(App).mount('#app')
