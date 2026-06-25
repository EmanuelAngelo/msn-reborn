<script setup>
defineEmits(['start'])
</script>

<template>
  <div class="reborn-empty-chat">
    <div class="reborn-empty-chat-illustration" aria-hidden="true">💬</div>
    <h2 class="reborn-empty-chat-title">Nenhuma conversa aberta</h2>
    <p class="reborn-empty-chat-text">
      Selecione um contato na lista ou inicie uma nova conversa para começar a trocar mensagens.
    </p>
    <button type="button" class="reborn-btn-outline" @click="$emit('start')">
      <span aria-hidden="true">💬</span>
      Iniciar conversa
    </button>
  </div>
</template>
