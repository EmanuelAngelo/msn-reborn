<script setup>
import { computed } from 'vue'
import { useLocale } from '../composables/useLocale'

defineProps({
  mode: { type: String, default: 'login' },
  form: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  theme: { type: String, default: 'light' },
})

defineEmits(['submit', 'toggle-mode', 'toggle-theme', 'toggle-locale'])

const { t, locale } = useLocale()

const localeLabel = computed(() => (locale.value === 'pt' ? t('header.en') : t('header.pt')))
const localeTitle = computed(() =>
  locale.value === 'pt' ? t('header.localeEn') : t('header.localePt'),
)

const nostalgicQuotes = computed(() => [
  t('login.quote1'),
  t('login.quote2'),
  t('login.quote3'),
  t('login.quote4'),
  t('login.quote5'),
])

const decorativeContacts = [
  { name: 'Ana', status: 'online', emoji: '🦋' },
  { name: 'Pedro', status: 'away', emoji: '🎸' },
  { name: 'Luiza', status: 'busy', emoji: '📚' },
  { name: 'Rafa', status: 'offline', emoji: '⚽' },
]

function statusClass(status) {
  return {
    online: 'status-online',
    away: 'status-away',
    busy: 'status-busy',
    offline: 'status-offline',
  }[status] || 'status-offline'
}
</script>

<template>
  <div class="login-scene">
    <div class="login-top-actions">
      <button
        type="button"
        class="login-theme-toggle"
        :title="theme === 'dark' ? t('header.themeLight') : t('header.themeDark')"
        @click="$emit('toggle-theme')"
      >
        <span aria-hidden="true">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        {{ theme === 'dark' ? t('header.light') : t('header.dark') }}
      </button>
      <button
        type="button"
        class="login-locale-toggle"
        :title="localeTitle"
        @click="$emit('toggle-locale')"
      >
        <span aria-hidden="true">🌐</span>
        {{ localeLabel }}
      </button>
    </div>

    <div class="login-cloud login-cloud-1" aria-hidden="true"></div>
    <div class="login-cloud login-cloud-2" aria-hidden="true"></div>
    <div class="login-cloud login-cloud-3" aria-hidden="true"></div>

    <div class="login-layout">
      <aside class="login-nostalgia hidden lg:flex">
        <div class="login-nostalgia-card">
          <p class="login-nostalgia-tag">{{ t('login.remember') }}</p>
          <h2 class="login-nostalgia-title">{{ t('login.wlm') }}</h2>
          <p class="login-nostalgia-text">
            {{ t('login.nostalgia') }}
          </p>

          <ul class="login-quotes">
            <li v-for="quote in nostalgicQuotes" :key="quote">{{ quote }}</li>
          </ul>

          <div class="login-buddy-list">
            <div
              v-for="contact in decorativeContacts"
              :key="contact.name"
              class="login-buddy"
            >
              <span class="login-buddy-avatar">
                {{ contact.emoji }}
                <span class="login-buddy-dot" :class="statusClass(contact.status)"></span>
              </span>
              <span class="login-buddy-name">{{ contact.name }}</span>
            </div>
          </div>
        </div>
      </aside>

      <section class="msn-window login-window">
        <header class="msn-titlebar login-titlebar">
          <div class="login-titlebar-left">
            <img src="/reborn-logo.png" alt="Reborn" class="login-titlebar-logo" />
          </div>
          <div class="login-window-controls" aria-hidden="true">
            <span></span><span></span><span></span>
          </div>
        </header>

        <div class="login-body">
          <div class="login-hero">
            <img src="/reborn-logo.png" alt="Reborn Messenger" class="login-hero-logo" />
            <h1 class="login-heading">
              {{ mode === 'login' ? t('login.titleLogin') : t('login.titleRegister') }}
            </h1>
            <p class="login-subheading">
              {{ mode === 'login' ? t('login.subLogin') : t('login.subRegister') }}
            </p>
          </div>

          <div v-if="error" class="login-error" role="alert">{{ error }}</div>

          <form class="login-form" @submit.prevent="$emit('submit')">
            <label class="login-field">
              <span>{{ t('login.email') }}</span>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                :placeholder="t('login.emailPlaceholder')"
                required
              />
            </label>

            <label v-if="mode === 'register'" class="login-field">
              <span>{{ t('login.username') }}</span>
              <input
                v-model="form.username"
                type="text"
                autocomplete="username"
                :placeholder="t('login.usernamePlaceholder')"
                required
              />
            </label>

            <label v-if="mode === 'register'" class="login-field">
              <span>{{ t('login.displayName') }}</span>
              <input
                v-model="form.display_name"
                type="text"
                autocomplete="nickname"
                :placeholder="t('login.displayNamePlaceholder')"
              />
            </label>

            <label class="login-field">
              <span>{{ t('login.password') }}</span>
              <input
                v-model="form.password"
                type="password"
                :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
                placeholder="••••••••"
                minlength="8"
                required
              />
            </label>

            <button type="submit" class="login-submit" :disabled="loading">
              {{
                loading
                  ? t('login.connecting')
                  : mode === 'login'
                    ? t('login.enter')
                    : t('login.createAccount')
              }}
            </button>
          </form>

          <div class="login-footer">
            <button type="button" class="login-toggle" @click="$emit('toggle-mode')">
              {{ mode === 'login' ? t('login.noAccount') : t('login.hasAccount') }}
            </button>
            <p class="login-footnote">{{ t('login.footnote') }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
