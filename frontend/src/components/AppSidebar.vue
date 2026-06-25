<script setup>
defineProps({
  active: { type: String, default: 'profile' },
})

defineEmits(['navigate'])

const items = [
  { id: 'profile', label: 'Perfil', icon: '👤' },
  { id: 'contacts', label: 'Contatos', icon: '👥' },
  { id: 'chats', label: 'Conversas', icon: '💬' },
  { id: 'settings', label: 'Configurações', icon: '⚙️' },
  { id: 'help', label: 'Ajuda', icon: '❓' },
]
</script>

<template>
  <nav class="reborn-sidebar" aria-label="Navegação principal">
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
  </nav>
</template>
