import { computed, ref, watch } from 'vue'
import { messages } from '../i18n/messages'

const STORAGE_KEY = 'reborn_locale'
const locale = ref('pt')

function resolveMessage(key, lang) {
  const parts = key.split('.')
  let value = messages[lang]
  for (const part of parts) {
    value = value?.[part]
  }
  return typeof value === 'string' ? value : null
}

function applyLocale(value) {
  document.documentElement.setAttribute('lang', value === 'en' ? 'en' : 'pt-BR')
}

function initLocale() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'en' || saved === 'pt') {
    locale.value = saved
  } else {
    const browserLang = navigator.language?.toLowerCase() || ''
    locale.value = browserLang.startsWith('en') ? 'en' : 'pt'
  }
  applyLocale(locale.value)
}

function toggleLocale() {
  locale.value = locale.value === 'pt' ? 'en' : 'pt'
}

function setLocale(value) {
  if (value === 'en' || value === 'pt') {
    locale.value = value
  }
}

watch(locale, (value) => {
  applyLocale(value)
  localStorage.setItem(STORAGE_KEY, value)
})

export function useLocale() {
  const t = (key, params = {}) => {
    const primary = resolveMessage(key, locale.value)
    const fallback = locale.value === 'pt' ? resolveMessage(key, 'en') : resolveMessage(key, 'pt')
    const template = primary || fallback || key
    return template.replace(/\{(\w+)\}/g, (_, name) => String(params[name] ?? ''))
  }

  const isEnglish = computed(() => locale.value === 'en')

  return { locale, isEnglish, t, toggleLocale, setLocale, initLocale }
}
