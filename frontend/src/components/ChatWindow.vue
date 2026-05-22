<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { createChatSocket } from '../services/chatSocket'
import { listMessages, openDirectConversation } from '../services/msn'

const props = defineProps({
  contact: {
    type: Object,
    default: null,
  },
  currentUser: {
    type: Object,
    default: null,
  },
})

const conversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const typingText = ref('')
const connecting = ref(false)
const error = ref('')
const messageBox = ref(null)

let chatSocket = null
let typingTimeout = null

function getContactUserId() {
  return props.contact?.contact || props.contact?.contact_profile?.user_id || null
}

function messageAuthor(message) {
  return message.sender_name || message.sender?.username || message.sender_obj?.username || 'Usuário'
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

  chatSocket = createChatSocket(conversation.value.id, {
    onMessage(message) {
      messages.value.push(message)
      scrollToBottom()
    },

    onNudge(message) {
      messages.value.push(message)
      document.body.classList.add('screen-shake')
      setTimeout(() => document.body.classList.remove('screen-shake'), 500)
      scrollToBottom()
    },

    onTyping(data) {
      typingText.value = data.is_typing ? `${data.user.username} está digitando...` : ''
    },

    onError() {
      error.value = 'Erro no chat em tempo real.'
    },
  })
}

async function openConversation() {
  disconnectSocket()
  messages.value = []
  conversation.value = null
  typingText.value = ''
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

function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || !chatSocket) return

  chatSocket.sendMessage(text)
  newMessage.value = ''
  chatSocket.typingStop()
}

function sendNudge() {
  if (!chatSocket) return
  chatSocket.sendNudge()
}

function handleTyping() {
  if (!chatSocket) return

  chatSocket.typingStart()
  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => chatSocket?.typingStop(), 1000)
}

watch(
  () => props.contact?.id,
  () => openConversation(),
  { immediate: true }
)

onBeforeUnmount(() => {
  disconnectSocket()
})
</script>

<template>
  <section class="msn-window flex min-h-[620px] flex-col overflow-hidden rounded-xl border border-sky-700 bg-white/95">
    <div class="msn-titlebar px-4 py-3 text-white">
      <div class="font-bold">
        {{ contact?.contact_profile?.display_name || contact?.contact_profile?.email || 'Selecione um contato' }}
      </div>
      <div v-if="contact?.contact_profile" class="text-xs text-white/90">
        Status: {{ contact.contact_profile.status }}
      </div>
    </div>

    <div v-if="!contact" class="grid flex-1 place-items-center p-8 text-center text-slate-500">
      Selecione um contato para iniciar uma conversa.
    </div>

    <template v-else>
      <div v-if="error" class="m-3 rounded bg-red-50 p-3 text-sm text-red-700">{{ error }}</div>
      <div v-if="connecting" class="p-4 text-sm text-slate-500">Abrindo conversa...</div>

      <div ref="messageBox" class="flex-1 overflow-y-auto bg-white p-4">
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

        <div v-if="typingText" class="mt-2 text-xs italic text-slate-500">
          {{ typingText }}
        </div>
      </div>

      <div class="flex gap-2 border-t bg-[#eaf7ff] p-3">
        <input
          v-model="newMessage"
          class="flex-1 rounded border border-blue-300 px-3 py-2 outline-none focus:ring-2 focus:ring-sky-300"
          placeholder="Digite sua mensagem..."
          @input="handleTyping"
          @keyup.enter="sendMessage"
        />

        <button
          class="rounded bg-yellow-400 px-4 py-2 font-bold text-yellow-950 hover:bg-yellow-500"
          @click="sendNudge"
        >
          Chamar atenção
        </button>

        <button
          class="rounded bg-blue-600 px-4 py-2 font-bold text-white hover:bg-blue-700"
          @click="sendMessage"
        >
          Enviar
        </button>
      </div>
    </template>
  </section>
</template>
