<script setup>
import { computed } from 'vue'
import { useLocale } from '../composables/useLocale'

defineProps({
  theme: { type: String, default: 'light' },
})

defineEmits(['spotify', 'logout', 'toggle-theme', 'toggle-locale'])

const { locale, t } = useLocale()

const localeLabel = computed(() => (locale.value === 'pt' ? t('header.en') : t('header.pt')))
const localeTitle = computed(() =>
  locale.value === 'pt' ? t('header.localeEn') : t('header.localePt'),
)
</script>

<template>
  <header class="reborn-header">
    <div class="reborn-header-brand">
      <img src="/reborn-logo.png" alt="Reborn" class="reborn-header-logo" />
    </div>

    <div class="reborn-header-actions">
      <button
        type="button"
        class="reborn-btn-theme"
        :title="theme === 'dark' ? t('header.themeLight') : t('header.themeDark')"
        @click="$emit('toggle-theme')"
      >
        <span aria-hidden="true">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        {{ theme === 'dark' ? t('header.light') : t('header.dark') }}
      </button>
      <button
        type="button"
        class="reborn-btn-locale"
        :title="localeTitle"
        @click="$emit('toggle-locale')"
      >
        <span aria-hidden="true">🌐</span>
        {{ localeLabel }}
      </button>
      <button type="button" class="reborn-btn-spotify" @click="$emit('spotify')">
        <span class="reborn-btn-spotify-icon">♫</span>
        {{ t('header.spotify') }}
      </button>
      <button type="button" class="reborn-btn-logout" @click="$emit('logout')">
        <span aria-hidden="true">⎋</span>
        {{ t('header.logout') }}
      </button>
    </div>
  </header>
</template>
