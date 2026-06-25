<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { areWebSocketsEnabled } from '../services/api'
import { createChatSocket } from '../services/chatSocket'
import {
  listMessages,
  openDirectConversation,
  sendMessage as sendMessageRest,
  sendNudge as sendNudgeRest,
  sendTypingSignal,
  blockContact,
  toggleFavoriteContact,
} from '../services/msn'

const props = defineProps({
  contact: {
    type: Object,
    default: null,
  },
  currentUser: {
    type: Object,
    default: null,
  },
  remoteTyping: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['contact-changed', 'minimize', 'close'])

const contactProfile = computed(() => props.contact?.contact_profile || null)
const contactMusic = computed(() => props.contact?.music_status || null)

function statusLabel(status) {
  return {
    online: 'Online',
    away: 'Ausente',
    busy: 'Ocupado',
    invisible: 'Invisível',
    offline: 'Offline',
  }[status] || status
}

const conversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const internalTyping = ref(false)
const internalTypingName = ref('')
const connecting = ref(false)
const error = ref('')
const messageBox = ref(null)

const isContactTyping = computed(() => Boolean(props.remoteTyping?.isTyping || internalTyping.value))
const typingDisplayName = computed(() =>
  props.remoteTyping?.displayName || internalTypingName.value || contactDisplayName()
)

let chatSocket = null
let typingTimeout = null
let typingClearTimeout = null
let typingRestDebounce = null
let messagePollingInterval = null
const knownMessageIds = new Set()

function contactDisplayName() {
  return props.contact?.contact_profile?.display_name
    || props.contact?.contact_profile?.email
    || 'Contato'
}

function clearInternalTypingIndicator() {
  internalTyping.value = false
  internalTypingName.value = ''
  if (typingClearTimeout) {
    clearTimeout(typingClearTimeout)
    typingClearTimeout = null
  }
}

function showTypingIndicator(user, isTyping) {
  const contactId = getContactUserId()
  if (contactId && user?.id && String(user.id) !== String(contactId)) {
    return
  }

  if (!isTyping) {
    clearInternalTypingIndicator()
    return
  }

  internalTypingName.value = user?.display_name || user?.username || contactDisplayName()
  internalTyping.value = true
  scrollToBottom()

  if (typingClearTimeout) clearTimeout(typingClearTimeout)
  typingClearTimeout = setTimeout(() => {
    internalTyping.value = false
  }, 3500)
}

function triggerScreenShake() {
  document.body.classList.add('screen-shake')
  const app = document.querySelector('.reborn-app')
  if (app) app.classList.add('screen-shake')
  window.setTimeout(() => {
    document.body.classList.remove('screen-shake')
    if (app) app.classList.remove('screen-shake')
  }, 500)
}

function messageFromContact(message) {
  const contactId = getContactUserId()
  const senderId = message?.sender || message?.sender_obj?.id
  return contactId && senderId && String(senderId) === String(contactId)
}

function getContactUserId() {
  return props.contact?.contact || props.contact?.contact_profile?.user_id || null
}

function messageAuthor(message) {
  return message.sender_name || message.sender?.username || message.sender_obj?.username || 'Usuário'
}

function sortMessages() {
  messages.value.sort((a, b) => new Date(a.sent_at) - new Date(b.sent_at))
}

function addMessage(message) {
  if (!message?.id) return
  if (messages.value.some((item) => item.id === message.id)) return
  messages.value.push(message)
  knownMessageIds.add(message.id)
  sortMessages()
}

function setMessagesWithoutDuplicates(newMessages) {
  const map = new Map()
  for (const message of [...messages.value, ...newMessages]) {
    if (message?.id) map.set(message.id, message)
  }
  messages.value = Array.from(map.values())
  for (const message of messages.value) {
    if (message?.id) knownMessageIds.add(message.id)
  }
  sortMessages()
}

function detectNewMessagesFromPoll(updatedMessages) {
  for (const message of updatedMessages) {
    if (!message?.id || knownMessageIds.has(message.id)) continue
    knownMessageIds.add(message.id)
    if (message.type === 'nudge' && messageFromContact(message)) {
      triggerScreenShake()
    }
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messageBox.value) {
    messageBox.value.scrollTop = messageBox.value.scrollHeight
  }
}

async function loadHistory() {
  if (!conversation.value?.id) return
  messages.value = await listMessages(conversation.value.id)
  knownMessageIds.clear()
  for (const message of messages.value) {
    if (message?.id) knownMessageIds.add(message.id)
  }
  await scrollToBottom()
}

function disconnectSocket() {
  if (chatSocket) {
    chatSocket.close()
    chatSocket = null
  }
}

function connectSocket() {
  if (!conversation.value?.id) return

  disconnectSocket()

  if (!areWebSocketsEnabled()) {
    startMessagePolling()
    return
  }

  try {
    chatSocket = createChatSocket(conversation.value.id, {
      onMessage(message) {
        addMessage(message)
        if (messageFromContact(message)) {
          clearInternalTypingIndicator()
        }
        scrollToBottom()
      },

      onNudge(message) {
        addMessage(message)
        clearInternalTypingIndicator()
        if (messageFromContact(message)) {
          triggerScreenShake()
        }
        scrollToBottom()
      },

      onTyping(data) {
        showTypingIndicator(data.user, data.is_typing)
      },

      onError() {
        startMessagePolling()
      },

      onClose() {
        startMessagePolling()
      },
    })

    if (!chatSocket) {
      startMessagePolling()
    }
  } catch {
    startMessagePolling()
  }
}

function startMessagePolling() {
  if (messagePollingInterval || !conversation.value?.id) return

  messagePollingInterval = setInterval(async () => {
    if (!conversation.value?.id) return

    try {
      const updatedMessages = await listMessages(conversation.value.id)
      detectNewMessagesFromPoll(updatedMessages)
      const before = messages.value.length
      setMessagesWithoutDuplicates(updatedMessages)
      if (messages.value.length !== before) await scrollToBottom()
    } catch {
      // Mantém a tela estável se a API oscilar.
    }
  }, 3000)
}

function stopMessagePolling() {
  if (messagePollingInterval) {
    clearInterval(messagePollingInterval)
    messagePollingInterval = null
  }
}

async function openConversation() {
  stopMessagePolling()
  disconnectSocket()
  messages.value = []
  knownMessageIds.clear()
  conversation.value = null
  clearInternalTypingIndicator()
  error.value = ''

  const contactUserId = getContactUserId()
  if (!contactUserId) return

  connecting.value = true

  try {
    conversation.value = await openDirectConversation(contactUserId)
    await loadHistory()
    connectSocket()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Não foi possível abrir a conversa.'
  } finally {
    connecting.value = false
  }
}

async function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || !conversation.value?.id) return

  if (chatSocket?.readyState === WebSocket.OPEN) {
    chatSocket.sendMessage(text)
    newMessage.value = ''
    stopTypingSignal()
    return
  }

  try {
    const message = await sendMessageRest(conversation.value.id, text)
    addMessage(message)
    newMessage.value = ''
    await scrollToBottom()
    startMessagePolling()
  } catch {
    error.value = 'Não foi possível enviar a mensagem.'
  }
}

async function sendNudge() {
  if (!conversation.value?.id) return

  triggerScreenShake()

  if (chatSocket?.readyState === WebSocket.OPEN) {
    chatSocket.sendNudge()
    return
  }

  try {
    const message = await sendNudgeRest(conversation.value.id)
    addMessage(message)
    await scrollToBottom()
    startMessagePolling()
  } catch {
    error.value = 'Não foi possível chamar atenção.'
  }
}

async function handleBlockContact() {
  if (!props.contact?.id) return
  if (!window.confirm('Bloquear este contato? Ele será removido da sua lista.')) return

  try {
    await blockContact(props.contact.id)
    emit('contact-changed')
  } catch {
    error.value = 'Não foi possível bloquear o contato.'
  }
}

async function handleToggleFavorite() {
  if (!props.contact?.id) return

  try {
    const updated = await toggleFavoriteContact(props.contact.id)
    emit('contact-changed', updated)
  } catch {
    error.value = 'Não foi possível atualizar favorito.'
  }
}

function emitTypingRest(isTyping) {
  if (!conversation.value?.id) return
  sendTypingSignal(conversation.value.id, isTyping).catch(() => {})
}

function stopTypingSignal() {
  if (typingTimeout) {
    clearTimeout(typingTimeout)
    typingTimeout = null
  }
  if (typingRestDebounce) {
    clearTimeout(typingRestDebounce)
    typingRestDebounce = null
  }

  if (chatSocket?.readyState === WebSocket.OPEN) {
    chatSocket.typingStop()
  } else {
    emitTypingRest(false)
  }
}

function handleTyping() {
  if (!conversation.value?.id) return

  if (!newMessage.value.trim()) {
    stopTypingSignal()
    return
  }

  const socketReady = chatSocket?.readyState === WebSocket.OPEN

  if (socketReady) {
    chatSocket.typingStart()
  } else {
    if (typingRestDebounce) clearTimeout(typingRestDebounce)
    typingRestDebounce = setTimeout(() => emitTypingRest(true), 150)
  }

  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(stopTypingSignal, 2000)
}

watch(
  () => props.remoteTyping?.isTyping,
  (isTyping) => {
    if (isTyping) scrollToBottom()
  },
)

watch(
  () => props.contact?.id,
  () => openConversation(),
  { immediate: true },
)

onBeforeUnmount(() => {
  stopTypingSignal()
  clearInternalTypingIndicator()
  stopMessagePolling()
  disconnectSocket()
})
</script>

<template>
  <section class="reborn-chat-window flex h-full min-h-0 flex-col overflow-hidden">
    <div class="reborn-chat-titlebar shrink-0 px-4 py-3 text-white">
      <div class="flex items-center justify-between gap-2">
        <div class="min-w-0 flex-1">
          <div class="truncate font-bold">
            {{ contactProfile?.display_name || contactProfile?.email || 'Selecione um contato' }}
          </div>
          <div v-if="contactProfile" class="text-xs text-white/90">
            <span v-if="isContactTyping" class="typing-titlebar">
              {{ typingDisplayName }} está digitando
              <span class="typing-dots typing-dots-light"><span></span><span></span><span></span></span>
            </span>
            <span v-else>Status: {{ statusLabel(contactProfile.status) }}</span>
          </div>
          <div
            v-if="contactProfile?.personal_message && !isContactTyping"
            class="truncate text-xs italic text-white/80"
          >
            "{{ contactProfile.personal_message }}"
          </div>
          <div
            v-if="contactMusic?.is_playing && contactMusic?.track_name && !isContactTyping"
            class="truncate text-xs text-sky-100"
          >
            ♫ {{ contactMusic.artist_name }} — {{ contactMusic.track_name }}
          </div>
        </div>
        <div v-if="contact" class="flex shrink-0 items-center gap-1">
          <button
            class="rounded bg-white/20 px-2 py-1 text-xs hover:bg-white/30"
            :title="contact.is_favorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'"
            @click="handleToggleFavorite"
          >
            {{ contact.is_favorite ? '★' : '☆' }}
          </button>
          <button
            class="rounded bg-white/20 px-2 py-1 text-[10px] hover:bg-white/30 sm:text-xs"
            title="Bloquear contato"
            @click="handleBlockContact"
          >
            Bloquear
          </button>
          <button
            class="msn-window-btn"
            title="Minimizar conversa"
            @click="$emit('minimize')"
          >
            _
          </button>
          <button
            class="msn-window-btn"
            title="Fechar conversa"
            @click="$emit('close')"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div v-if="!contact" class="grid flex-1 place-items-center p-8 text-center text-slate-500">
      Selecione um contato para iniciar uma conversa.
    </div>

    <template v-else>
      <div v-if="error" class="m-3 rounded bg-red-50 p-3 text-sm text-red-700">{{ error }}</div>
      <div v-if="connecting" class="p-4 text-sm text-slate-500">Abrindo conversa...</div>

      <div ref="messageBox" class="min-h-0 flex-1 overflow-y-auto overscroll-contain bg-white p-4">
        <div v-for="message in messages" :key="message.id" class="mb-2">
          <div
            v-if="message.type === 'nudge'"
            class="rounded border border-yellow-300 bg-yellow-100 px-3 py-2 text-center text-sm font-bold text-yellow-800"
          >
            {{ messageAuthor(message) }} chamou atenção!
          </div>

          <div v-else class="rounded bg-sky-50 px-3 py-2 text-sm text-slate-800">
            <strong>{{ messageAuthor(message) }} diz:</strong>
            <span class="ml-1">{{ message.content }}</span>
          </div>
        </div>

        <div v-if="isContactTyping" class="typing-bubble">
          <span class="typing-bubble-label">{{ typingDisplayName }} está digitando</span>
          <span class="typing-dots"><span></span><span></span><span></span></span>
        </div>
      </div>

      <div class="shrink-0 flex flex-wrap gap-2 border-t border-sky-100 bg-gradient-to-b from-sky-50 to-white p-3">
        <input
          v-model="newMessage"
          class="reborn-input min-w-0 flex-1"
          placeholder="Digite sua mensagem..."
          @input="handleTyping"
          @blur="stopTypingSignal"
          @keyup.enter="sendMessage"
        />

        <button
          class="reborn-btn-nudge"
          @click="sendNudge"
        >
          Chamar atenção
        </button>

        <button
          class="reborn-btn-primary reborn-btn-send"
          @click="sendMessage"
        >
          Enviar
        </button>
      </div>
    </template>
  </section>
</template>
