<script setup>
import { computed } from 'vue'
import { useLocale } from '../composables/useLocale'
import InstagramLink from './InstagramLink.vue'

defineProps({
  active: { type: String, default: 'profile' },
})

defineEmits(['navigate'])

const { t } = useLocale()

const items = computed(() => [
  { id: 'profile', label: t('nav.profile'), icon: '👤' },
  { id: 'contacts', label: t('nav.contacts'), icon: '👥' },
  { id: 'chats', label: t('nav.chats'), icon: '💬' },
  { id: 'settings', label: t('nav.settings'), icon: '⚙️' },
  { id: 'help', label: t('nav.help'), icon: '❓' },
])
</script>

<template>
  <nav class="reborn-sidebar" :aria-label="t('nav.main')">
    <div class="reborn-sidebar-nav">
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="reborn-nav-item"
        :class="{ 'reborn-nav-item--active': active === item.id }"
        @click="$emit('navigate', item.id)"
      >
        <span class="reborn-nav-icon" aria-hidden="true">{{ item.icon }}</span>
        <span class="reborn-nav-label">{{ item.label }}</span>
      </button>
    </div>

    <InstagramLink class="reborn-sidebar-instagram" />
  </nav>
</template>
