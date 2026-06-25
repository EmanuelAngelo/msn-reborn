<script setup>
import { resolveMediaUrl } from '../utils/media'

defineProps({
  contacts: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
})
defineEmits(['select'])

function statusClass(status) {
  return {
    online: 'bg-lime-400',
    away: 'bg-yellow-400',
    busy: 'bg-red-500',
    invisible: 'bg-slate-400',
    offline: 'bg-slate-400',
  }[status] || 'bg-slate-400'
}

function avatarSrc(profile) {
  return resolveMediaUrl(profile?.avatar_url || profile?.avatar || '')
}

function initials(profile) {
  const value = profile?.display_name || profile?.email || 'MSN'
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}
</script>

<template>
  <div class="bg-white/80 p-3">
    <div class="mb-2 rounded bg-sky-100 px-3 py-1 text-sm font-bold text-sky-900">
      Contatos
    </div>

    <button
      v-for="item in contacts"
      :key="`${item.id}-${item.contact_profile?.status}-${item.contact_profile?.display_name}-${item.contact_profile?.avatar_url}-${item.music_status?.track_name || ''}`"
      type="button"
      class="mb-2 flex w-full items-start gap-3 rounded-lg border px-3 py-2 text-left shadow-sm transition hover:bg-sky-50"
      :class="selectedId === item.id ? 'border-sky-500 bg-sky-50' : 'border-slate-200 bg-white'"
      @click="$emit('select', item)"
    >
      <span class="relative h-10 w-10 shrink-0 overflow-hidden rounded-lg border border-sky-200 bg-sky-50">
        <img
          v-if="avatarSrc(item.contact_profile)"
          :key="avatarSrc(item.contact_profile)"
          :src="avatarSrc(item.contact_profile)"
          alt="Foto do contato"
          class="h-full w-full object-cover"
        />
        <span v-else class="grid h-full w-full place-items-center text-xs font-bold text-sky-700">
          {{ initials(item.contact_profile) }}
        </span>
        <span class="absolute bottom-0 right-0 h-3 w-3 rounded-full border border-white" :class="statusClass(item.contact_profile?.status)"></span>
      </span>

      <span class="min-w-0 flex-1">
        <span class="block truncate font-semibold text-slate-800">
          <span v-if="item.is_favorite" class="text-yellow-500">★ </span>
          {{ item.nickname || item.contact_profile?.display_name || item.contact_profile?.email || 'Contato' }}
        </span>
        <span class="block truncate text-xs text-slate-500">
          {{ item.contact_profile?.personal_message || 'Sem mensagem pessoal' }}
        </span>
        <span v-if="item.music_status?.is_playing && item.music_status?.track_name" class="block truncate text-xs text-sky-700">
          ♫ {{ item.music_status.artist_name }} - {{ item.music_status.track_name }}
        </span>
      </span>
    </button>

    <div v-if="!contacts.length" class="rounded-lg border border-dashed border-slate-300 p-4 text-center text-sm text-slate-500">
      Nenhum contato ainda. Use a área abaixo para buscar usuários e adicionar amigos.
    </div>
  </div>
</template>
