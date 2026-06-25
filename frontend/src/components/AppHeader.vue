<script setup>
defineEmits(['spotify', 'logout'])
</script>

<template>
  <header class="reborn-header">
    <div class="reborn-header-brand">
      <img src="/reborn-mascot.png" alt="" class="reborn-header-logo" />
      <span class="reborn-header-title">Reborn</span>
    </div>

    <div class="reborn-header-actions">
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
