<script setup>
defineProps({
  profile: { type: Object, default: null },
  music: { type: Object, default: null },
})

function statusClass(status) {
  return {
    online: 'text-emerald-700',
    away: 'text-yellow-700',
    busy: 'text-red-700',
    invisible: 'text-slate-500',
    offline: 'text-slate-500',
  }[status] || 'text-slate-500'
}

function statusDot(status) {
  return {
    online: 'bg-lime-400',
    away: 'bg-yellow-400',
    busy: 'bg-red-500',
    invisible: 'bg-slate-400',
    offline: 'bg-slate-400',
  }[status] || 'bg-slate-400'
}

function statusLabel(status) {
  return {
    online: 'online',
    away: 'ausente',
    busy: 'ocupado',
    invisible: 'invisível',
    offline: 'offline',
  }[status] || 'offline'
}
</script>

<template>
  <div class="border-b border-sky-200 bg-gradient-to-b from-sky-50 to-white p-4">
    <div class="flex gap-3">
      <div class="grid h-16 w-16 place-items-center rounded-xl border border-sky-500 bg-white text-3xl shadow-inner">
        🙂
      </div>
      <div class="min-w-0 flex-1">
        <div class="truncate text-lg font-bold text-slate-800">
          {{ profile?.display_name || 'Usuário MSN' }}
        </div>
        <div class="flex items-center gap-1 text-sm" :class="statusClass(profile?.status)">
          <span class="inline-block h-2.5 w-2.5 rounded-full" :class="statusDot(profile?.status)"></span>
          {{ statusLabel(profile?.status) }}
        </div>
        <div class="truncate text-sm text-slate-600">
          {{ profile?.personal_message || 'Disponível para conversar' }}
        </div>
        <div v-if="music?.is_playing && music?.track_name" class="mt-1 truncate text-xs font-semibold text-sky-700">
          ♫ {{ music.artist_name }} - {{ music.track_name }}
        </div>
        <div v-else class="mt-1 truncate text-xs text-slate-400">
          Spotify sem música em reprodução
        </div>
      </div>
    </div>
  </div>
</template>
