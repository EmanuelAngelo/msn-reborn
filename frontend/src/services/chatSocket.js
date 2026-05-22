import { areWebSocketsEnabled, getAuthToken, getWebSocketBaseUrl } from './api'

const WS_BASE_URL = getWebSocketBaseUrl()

export function createChatSocket(conversationId, callbacks = {}) {
  if (!areWebSocketsEnabled()) {
    return null
  }

  const token = getAuthToken()

  if (!token) {
    throw new Error('Token de autenticação não encontrado.')
  }

  const socket = new WebSocket(
    `${WS_BASE_URL}/ws/conversations/${conversationId}/?token=${encodeURIComponent(token)}`
  )

  socket.onopen = () => {
    callbacks.onOpen?.()
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'message.created') {
      callbacks.onMessage?.(data.message)
    }

    if (data.type === 'nudge.received') {
      callbacks.onNudge?.(data.message)
    }

    if (data.type === 'typing.updated') {
      callbacks.onTyping?.(data)
    }
  }

  socket.onerror = (error) => {
    callbacks.onError?.(error)
  }

  socket.onclose = (event) => {
    callbacks.onClose?.(event)
  }

  return {
    get readyState() {
      return socket.readyState
    },

    sendMessage(content) {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'message.send', content }))
      }
    },

    sendNudge() {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'nudge.send' }))
      }
    },

    typingStart() {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'typing.start' }))
      }
    },

    typingStop() {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'typing.stop' }))
      }
    },

    close() {
      socket.close()
    },
  }
}
