<script setup>
import { resolveMediaUrl } from '../utils/media'

defineProps({
  chats: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['restore', 'close'])

function displayName(chat) {
  return chat?.contact_profile?.display_name || chat?.contact_profile?.email || 'Contato'
}

function statusClass(status) {
  return {
    online: 'status-online',
    away: 'status-away',
    busy: 'status-busy',
    invisible: 'status-offline',
    offline: 'status-offline',
  }[status] || 'status-offline'
}

function initials(chat) {
  const value = displayName(chat)
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}
</script>

<template>
  <div v-if="chats.length" class="chat-taskbar" role="toolbar" aria-label="Conversas minimizadas">
    <button
      v-for="chat in chats"
      :key="chat.id"
      type="button"
      class="msn-window chat-taskbar-item"
      @click="$emit('restore', chat.id)"
    >
      <span class="msn-titlebar chat-taskbar-titlebar">
        <span class="chat-taskbar-avatar">
          <img
            v-if="chat.contact_profile?.avatar_url"
            :src="resolveMediaUrl(chat.contact_profile.avatar_url)"
            :alt="displayName(chat)"
            class="h-full w-full object-cover"
          />
          <span v-else class="grid h-full w-full place-items-center text-[10px] font-bold">
            {{ initials(chat) }}
          </span>
          <span class="chat-taskbar-dot" :class="statusClass(chat.contact_profile?.status)"></span>
        </span>
        <span class="min-w-0 flex-1 truncate text-left text-xs font-bold">{{ displayName(chat) }}</span>
        <span
          class="chat-taskbar-close"
          role="button"
          tabindex="0"
          title="Fechar conversa"
          @click.stop="$emit('close', chat.id)"
          @keydown.enter.stop.prevent="$emit('close', chat.id)"
        >×</span>
      </span>
    </button>
  </div>
</template>
