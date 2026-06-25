<script setup>
import { useLocale } from '../composables/useLocale'

defineEmits(['start'])

const { t } = useLocale()
</script>

<template>
  <div class="reborn-empty-chat">
    <div class="reborn-empty-chat-illustration" aria-hidden="true">💬</div>
    <h2 class="reborn-empty-chat-title">{{ t('chat.emptyTitle') }}</h2>
    <p class="reborn-empty-chat-text">
      {{ t('chat.emptyText') }}
    </p>
    <button type="button" class="reborn-btn-outline" @click="$emit('start')">
      <span aria-hidden="true">💬</span>
      {{ t('chat.start') }}
    </button>
  </div>
</template>
