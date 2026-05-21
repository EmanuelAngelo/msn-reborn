import { getAuthToken } from './api'

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000'

export function createChatSocket(conversationId, callbacks = {}) {
  const token = getAuthToken()

  if (!token) {
    throw new Error('Token de autenticação não encontrado.')
  }

  const socket = new WebSocket(
    `${WS_BASE_URL}/ws/conversations/${conversationId}/?token=${encodeURIComponent(token)}`
  )

  socket.onopen = () => {
    console.log('WebSocket conectado.')
    callbacks.onOpen?.()
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'connection.accepted') {
      callbacks.onReady?.(data)
      return
    }

    if (data.type === 'message.created') {
      callbacks.onMessage?.(data.message)
      return
    }

    if (data.type === 'nudge.received') {
      callbacks.onNudge?.(data.message)
      return
    }

    if (data.type === 'typing.updated') {
      callbacks.onTyping?.(data)
    }
  }

  socket.onerror = (error) => {
    console.error('Erro no WebSocket:', error)
    callbacks.onError?.(error)
  }

  socket.onclose = (event) => {
    console.log('WebSocket fechado:', event.code, event.reason)
    callbacks.onClose?.(event)
  }

  function safeSend(payload) {
    if (socket.readyState !== WebSocket.OPEN) {
      callbacks.onNotReady?.(socket.readyState)
      return false
    }

    socket.send(JSON.stringify(payload))
    return true
  }

  return {
    sendMessage(content) {
      return safeSend({
        type: 'message.send',
        content,
      })
    },

    sendNudge() {
      return safeSend({
        type: 'nudge.send',
      })
    },

    typingStart() {
      return safeSend({
        type: 'typing.start',
      })
    },

    typingStop() {
      return safeSend({
        type: 'typing.stop',
      })
    },

    close() {
      socket.close()
    },
  }
}
