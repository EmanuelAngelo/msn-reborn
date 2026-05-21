<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { createChatSocket } from '../services/chatSocket'
import { listMessages, openDirectConversation, sendMessage as sendMessageRest, sendNudge as sendNudgeRest } from '../services/msn'

const props = defineProps({
  contact: {
    type: Object,
    default: null,
  },
})

const conversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const typingText = ref('')
const statusText = ref('Selecione um contato para conversar.')
const errorText = ref('')
const messagesBox = ref(null)

let chatSocket = null
let typingTimeout = null

function getContactUserId(contact) {
  return contact?.contact || contact?.contact_profile?.user_id || contact?.contact_profile?.id || null
}

function getContactName() {
  return (
    props.contact?.contact_profile?.display_name ||
    props.contact?.contact_profile?.username ||
    props.contact?.contact_profile?.email ||
    'Contato'
  )
}

function getMessageAuthor(message) {
  return (
    message.sender_name ||
    message.sender?.display_name ||
    message.sender?.username ||
    message.sender?.email ||
    'Usuário'
  )
}

async function scrollToBottom() {
  await nextTick()
  if (messagesBox.value) {
    messagesBox.value.scrollTop = messagesBox.value.scrollHeight
  }
}

function closeSocket() {
  if (chatSocket) {
    chatSocket.close()
    chatSocket = null
  }
}

async function loadConversation() {
  errorText.value = ''
  typingText.value = ''
  conversation.value = null
  messages.value = []
  closeSocket()

  const contactUserId = getContactUserId(props.contact)

  if (!contactUserId) {
    statusText.value = 'Selecione um contato para conversar.'
    return
  }

  statusText.value = 'Abrindo conversa...'

  try {
    conversation.value = await openDirectConversation(contactUserId)
    const history = await listMessages(conversation.value.id)
    messages.value = Array.isArray(history) ? history : []
    await scrollToBottom()
    connectSocket()
  } catch (error) {
    console.error(error)
    statusText.value = 'Não foi possível abrir a conversa.'
    errorText.value = error.response?.data?.detail || 'Erro ao abrir conversa.'
  }
}

function connectSocket() {
  if (!conversation.value?.id) return

  closeSocket()
  statusText.value = 'Conectando em tempo real...'

  try {
    chatSocket = createChatSocket(conversation.value.id, {
      onReady() {
        statusText.value = 'Conectado em tempo real.'
      },

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
        typingText.value = data.is_typing ? `${data.user.username || data.user.email} está digitando...` : ''
      },

      onNotReady() {
        errorText.value = 'O chat ainda está conectando. Aguarde alguns segundos e tente enviar novamente.'
      },

      onClose(event) {
        if (event.code === 4001) {
          statusText.value = 'WebSocket recusado: token inválido. Faça login novamente.'
          errorText.value = 'Token inválido no WebSocket.'
          return
        }

        if (event.code === 4003) {
          statusText.value = 'WebSocket recusado: sem acesso a esta conversa.'
          errorText.value = 'Você não tem acesso a esta conversa.'
          return
        }

        if (conversation.value?.id) {
          statusText.value = 'Conexão em tempo real fechada.'
        }
      },

      onError() {
        errorText.value = 'Erro na conexão em tempo real.'
      },
    })
  } catch (error) {
    console.error(error)
    statusText.value = 'Não foi possível criar o WebSocket.'
    errorText.value = error.message || 'Erro ao conectar WebSocket.'
  }
}

async function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || !conversation.value?.id) return

  errorText.value = ''

  if (chatSocket?.sendMessage(text)) {
    newMessage.value = ''
    chatSocket.typingStop()
    return
  }

  // Fallback: salva via REST caso o WebSocket ainda não esteja aberto.
  try {
    const saved = await sendMessageRest(conversation.value.id, text)
    messages.value.push(saved)
    newMessage.value = ''
    await scrollToBottom()
  } catch (error) {
    console.error(error)
    errorText.value = error.response?.data?.detail || 'Não foi possível enviar a mensagem.'
  }
}

async function sendNudge() {
  if (!conversation.value?.id) return

  errorText.value = ''

  if (chatSocket?.sendNudge()) return

  try {
    const saved = await sendNudgeRest(conversation.value.id)
    messages.value.push(saved)
    await scrollToBottom()
  } catch (error) {
    console.error(error)
    errorText.value = error.response?.data?.detail || 'Não foi possível chamar atenção.'
  }
}

function handleTyping() {
  if (!chatSocket) return

  chatSocket.typingStart()
  clearTimeout(typingTimeout)

  typingTimeout = setTimeout(() => {
    chatSocket?.typingStop()
  }, 1000)
}

watch(
  () => props.contact?.id,
  () => {
    loadConversation()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  clearTimeout(typingTimeout)
  closeSocket()
})
</script>

<template>
  <div class="msn-window flex h-[620px] flex-col overflow-hidden rounded-xl border border-sky-700 bg-white/95 shadow-2xl">
    <div class="msn-titlebar flex items-center justify-between px-4 py-2 text-white">
      <div>
        <div class="font-bold">Conversa com {{ props.contact ? getContactName() : 'Contato' }}</div>
        <div class="text-xs font-normal text-sky-100">{{ statusText }}</div>
      </div>
      <div class="flex gap-1">
        <span class="h-4 w-6 rounded bg-white/25"></span>
        <span class="h-4 w-6 rounded bg-white/25"></span>
        <span class="h-4 w-6 rounded bg-red-500"></span>
      </div>
    </div>

    <div ref="messagesBox" class="flex-1 overflow-y-auto bg-white p-4">
      <div v-if="!props.contact" class="text-sm text-slate-500">
        Selecione um contato na lista para abrir a conversa.
      </div>

      <div v-else-if="!messages.length" class="text-sm text-slate-400">
        Nenhuma mensagem ainda. Envie a primeira mensagem.
      </div>

      <div v-for="message in messages" :key="message.id" class="mb-3">
        <div
          v-if="message.type === 'nudge'"
          class="rounded border border-yellow-300 bg-yellow-100 px-3 py-2 text-center font-semibold text-yellow-800"
        >
          {{ getMessageAuthor(message) }} chamou sua atenção!
        </div>

        <div v-else class="text-sm text-slate-800">
          <strong class="text-sky-700">{{ getMessageAuthor(message) }} diz:</strong>
          <span class="ml-1">{{ message.content }}</span>
        </div>
      </div>

      <div v-if="typingText" class="mt-2 text-xs italic text-slate-500">
        {{ typingText }}
      </div>
    </div>

    <div v-if="errorText" class="border-t border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
      {{ errorText }}
    </div>

    <div class="flex gap-2 border-t bg-[#eaf7ff] p-3">
      <input
        v-model="newMessage"
        :disabled="!props.contact"
        class="flex-1 rounded border border-sky-300 px-3 py-2 disabled:bg-slate-100 disabled:text-slate-400"
        placeholder="Digite sua mensagem..."
        @input="handleTyping"
        @keyup.enter="sendMessage"
      />

      <button
        :disabled="!props.contact"
        class="rounded bg-yellow-400 px-4 py-2 font-bold text-slate-900 shadow hover:bg-yellow-500 disabled:opacity-50"
        @click="sendNudge"
      >
        Chamar atenção
      </button>

      <button
        :disabled="!props.contact"
        class="rounded bg-sky-600 px-4 py-2 font-bold text-white shadow hover:bg-sky-700 disabled:opacity-50"
        @click="sendMessage"
      >
        Enviar
      </button>
    </div>
  </div>
</template>
