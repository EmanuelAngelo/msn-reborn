<script setup>
defineProps({
  theme: { type: String, default: 'light' },
})

defineEmits(['spotify', 'logout', 'toggle-theme'])
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
        :title="theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro'"
        @click="$emit('toggle-theme')"
      >
        <span aria-hidden="true">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        {{ theme === 'dark' ? 'Claro' : 'Escuro' }}
      </button>
      <button type="button" class="reborn-btn-spotify" @click="$emit('spotify')">
        <span class="reborn-btn-spotify-icon">♫</span>
        Spotify
      </button>
      <button type="button" class="reborn-btn-logout" @click="$emit('logout')">
        <span aria-hidden="true">⎋</span>
        Sair
      </button>
    </div>
  </header>
</template>
