<script setup>
defineProps({
  mode: { type: String, default: 'login' },
  form: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['submit', 'toggle-mode'])

const nostalgicQuotes = [
  'Oi, tudo bem?',
  'BRB...',
  'Toque aqui! 👋',
  '♫ O que você está ouvindo?',
  'Sentiu saudades?',
]

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
    <div class="login-cloud login-cloud-1" aria-hidden="true"></div>
    <div class="login-cloud login-cloud-2" aria-hidden="true"></div>
    <div class="login-cloud login-cloud-3" aria-hidden="true"></div>

    <div class="login-layout">
      <aside class="login-nostalgia hidden lg:flex">
        <div class="login-nostalgia-card">
          <p class="login-nostalgia-tag">Lembra quando...</p>
          <h2 class="login-nostalgia-title">Windows Live Messenger</h2>
          <p class="login-nostalgia-text">
            Nudges que tremiam a tela, emoticons animados, música no status e aquela lista de contatos que parecia nunca dormir.
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
            <span class="login-window-icon" aria-hidden="true">🦋</span>
            <div>
              <p class="login-titlebar-brand">MSN Reborn</p>
              <p class="login-titlebar-sub">Messenger</p>
            </div>
          </div>
          <div class="login-window-controls" aria-hidden="true">
            <span></span><span></span><span></span>
          </div>
        </header>

        <div class="login-body">
          <div class="login-hero">
            <div class="login-avatar-ring">
              <div class="login-avatar">🙂</div>
            </div>
            <h1 class="login-heading">
              {{ mode === 'login' ? 'Conecte-se ao Messenger' : 'Criar nova conta' }}
            </h1>
            <p class="login-subheading">
              {{ mode === 'login'
                ? 'Entre e volte a conversar como nos bons tempos.'
                : 'Escolha seu apelido e comece a adicionar amigos.' }}
            </p>
          </div>

          <div v-if="error" class="login-error" role="alert">{{ error }}</div>

          <form class="login-form" @submit.prevent="$emit('submit')">
            <label class="login-field">
              <span>E-mail</span>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                placeholder="seu@email.com"
                required
              />
            </label>

            <label v-if="mode === 'register'" class="login-field">
              <span>Usuário</span>
              <input
                v-model="form.username"
                type="text"
                autocomplete="username"
                placeholder="seu_apelido"
                required
              />
            </label>

            <label v-if="mode === 'register'" class="login-field">
              <span>Nome de exibição</span>
              <input
                v-model="form.display_name"
                type="text"
                autocomplete="nickname"
                placeholder="Como seus amigos vão te ver"
              />
            </label>

            <label class="login-field">
              <span>Senha</span>
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
              {{ loading ? 'Conectando...' : mode === 'login' ? 'Entrar' : 'Criar conta' }}
            </button>
          </form>

          <div class="login-footer">
            <button type="button" class="login-toggle" @click="$emit('toggle-mode')">
              {{ mode === 'login' ? 'Ainda não tem conta? Cadastre-se' : 'Já tenho conta — entrar' }}
            </button>
            <p class="login-footnote">Status • Nudge • Música no perfil • Chat em tempo real</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
