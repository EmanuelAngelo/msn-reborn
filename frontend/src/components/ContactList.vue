<script setup>
import { computed, ref } from 'vue'
import { resolveMediaUrl } from '../utils/media'

const props = defineProps({
  contacts: { type: Array, default: () => [] },
  selectedId: { type: String, default: null },
  compact: { type: Boolean, default: false },
  showHeader: { type: Boolean, default: true },
})

const emit = defineEmits(['select', 'view-all'])

const filter = ref('all')

const filters = [
  { id: 'all', label: 'Todos' },
  { id: 'online', label: 'Online' },
  { id: 'away', label: 'Ausentes' },
  { id: 'offline', label: 'Offline' },
]

const filteredContacts = computed(() => {
  if (filter.value === 'all') return props.contacts
  if (filter.value === 'offline') {
    return props.contacts.filter((item) => {
      const s = item.contact_profile?.status
      return s === 'offline' || s === 'invisible'
    })
  }
  return props.contacts.filter((item) => item.contact_profile?.status === filter.value)
})

function statusClass(status) {
  return {
    online: 'status-online',
    away: 'status-away',
    busy: 'status-busy',
    invisible: 'status-offline',
    offline: 'status-offline',
  }[status] || 'status-offline'
}

function avatarSrc(profile) {
  return resolveMediaUrl(profile?.avatar_url || profile?.avatar || '')
}

function initials(profile) {
  const value = profile?.display_name || profile?.email || 'R'
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}

function contactName(item) {
  return item.nickname || item.contact_profile?.display_name || item.contact_profile?.email || 'Contato'
}
</script>

<template>
  <article class="reborn-card reborn-contacts-card" :class="{ 'reborn-contacts-card--full': !compact }">
    <header v-if="showHeader" class="reborn-card-header">
      <h2 class="reborn-card-title">
        <span aria-hidden="true">👥</span>
        Contatos
      </h2>
    </header>

    <div class="reborn-contact-filters">
      <button
        v-for="item in filters"
        :key="item.id"
        type="button"
        class="reborn-filter-pill"
        :class="{ 'reborn-filter-pill--active': filter === item.id }"
        @click="filter = item.id"
      >
        {{ item.label }}
      </button>
    </div>

    <div
      v-if="compact"
      class="reborn-contacts-scroll"
      role="list"
    >
      <button
        v-for="item in filteredContacts.slice(0, 8)"
        :key="`${item.id}-${item.contact_profile?.status}`"
        type="button"
        role="listitem"
        class="reborn-contact-chip"
        :class="{ 'reborn-contact-chip--selected': selectedId === item.id }"
        @click="emit('select', item)"
      >
        <span class="reborn-contact-chip-avatar">
          <img
            v-if="avatarSrc(item.contact_profile)"
            :src="avatarSrc(item.contact_profile)"
            alt=""
            class="reborn-contact-chip-img"
          />
          <span v-else class="reborn-contact-chip-initial">{{ initials(item.contact_profile) }}</span>
          <span class="reborn-contact-chip-dot" :class="statusClass(item.contact_profile?.status)"></span>
        </span>
        <span class="reborn-contact-chip-name">{{ contactName(item) }}</span>
        <span class="reborn-contact-chip-msg">
          {{ item.contact_profile?.personal_message || 'Sem mensagem' }}
        </span>
      </button>

      <div v-if="!filteredContacts.length" class="reborn-contacts-empty">
        Nenhum contato neste filtro.
      </div>
    </div>

    <div v-else class="reborn-contacts-list">
      <button
        v-for="item in filteredContacts"
        :key="`${item.id}-${item.contact_profile?.status}-${item.contact_profile?.display_name}`"
        type="button"
        class="reborn-contact-row"
        :class="{ 'reborn-contact-row--selected': selectedId === item.id }"
        @click="emit('select', item)"
      >
        <span class="reborn-contact-row-avatar">
          <img
            v-if="avatarSrc(item.contact_profile)"
            :src="avatarSrc(item.contact_profile)"
            alt=""
            class="reborn-contact-row-img"
          />
          <span v-else class="reborn-contact-row-initial">{{ initials(item.contact_profile) }}</span>
          <span class="reborn-contact-row-dot" :class="statusClass(item.contact_profile?.status)"></span>
        </span>
        <span class="reborn-contact-row-body">
          <span class="reborn-contact-row-name">
            <span v-if="item.is_favorite" class="reborn-favorite">★</span>
            {{ contactName(item) }}
          </span>
          <span class="reborn-contact-row-msg">
            {{ item.contact_profile?.personal_message || 'Sem mensagem pessoal' }}
          </span>
          <span
            v-if="item.music_status?.is_playing && item.music_status?.track_name"
            class="reborn-contact-row-music"
          >
            ♫ {{ item.music_status.artist_name }} — {{ item.music_status.track_name }}
          </span>
        </span>
      </button>

      <div v-if="!filteredContacts.length" class="reborn-contacts-empty">
        Nenhum contato ainda. Use a busca para adicionar amigos.
      </div>
    </div>

    <button
      v-if="compact && contacts.length > 0"
      type="button"
      class="reborn-link-btn"
      @click="emit('view-all')"
    >
      Ver todos os contatos
      <span aria-hidden="true">⌄</span>
    </button>
  </article>
</template>
