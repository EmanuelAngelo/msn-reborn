import { ref, watch } from 'vue'

const STORAGE_KEY = 'reborn_theme'
const theme = ref('light')

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
}

function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark' || saved === 'light') {
    theme.value = saved
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    theme.value = 'dark'
  }
  applyTheme(theme.value)
}

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

watch(theme, (value) => {
  applyTheme(value)
  localStorage.setItem(STORAGE_KEY, value)
})

export function useTheme() {
  return { theme, toggleTheme, initTheme }
}
