<script setup>
import { resolveMediaUrl } from '../utils/media'

defineProps({
  notifications: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['dismiss', 'open'])

function initials(name) {
  const value = name || 'MSN'
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}

function subtitle(item) {
  if (item.kind === 'message') return 'enviou uma mensagem'
  if (item.kind === 'nudge') return 'chamou sua atenção!'
  return 'acabou de ficar online'
}
</script>

<template>
  <div class="online-notifications" aria-live="polite">
    <TransitionGroup name="online-toast">
      <article
        v-for="item in notifications"
        :key="item.id"
        class="msn-window online-toast"
        role="status"
      >
        <header class="msn-titlebar online-toast-titlebar">
          <span class="online-toast-title">Reborn</span>
          <button
            type="button"
            class="online-toast-close"
            aria-label="Fechar"
            @click="$emit('dismiss', item.id)"
          >
            ×
          </button>
        </header>

        <button
          type="button"
          class="online-toast-body"
          @click="$emit('open', item)"
        >
          <span class="online-toast-avatar">
            <img
              v-if="item.avatarUrl"
              :src="resolveMediaUrl(item.avatarUrl)"
              :alt="item.displayName"
              class="h-full w-full object-cover"
            />
            <span v-else class="grid h-full w-full place-items-center text-sm font-bold text-sky-700">
              {{ initials(item.displayName) }}
            </span>
            <span
              class="online-toast-dot"
              :class="{ 'online-toast-dot--message': item.kind === 'message' || item.kind === 'nudge' }"
            ></span>
          </span>

          <span class="online-toast-text">
            <strong>{{ item.displayName }}</strong>
            <span class="block text-[13px] text-sky-800">{{ subtitle(item) }}</span>
            <span v-if="item.messagePreview" class="online-toast-message">
              "{{ item.messagePreview }}"
            </span>
            <span v-else-if="item.personalMessage && item.kind === 'online'" class="online-toast-message">
              "{{ item.personalMessage }}"
            </span>
          </span>
        </button>
      </article>
    </TransitionGroup>
  </div>
</template>
