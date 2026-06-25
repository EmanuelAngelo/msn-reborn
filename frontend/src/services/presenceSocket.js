import { areWebSocketsEnabled, getAuthToken, getWebSocketBaseUrl } from './api'

const WS_BASE_URL = getWebSocketBaseUrl()

export function createPresenceSocket(callbacks = {}) {
  if (!areWebSocketsEnabled()) {
    return null
  }

  const token = getAuthToken()

  if (!token) {
    throw new Error('Token de autenticação não encontrado para presença.')
  }

  const socket = new WebSocket(`${WS_BASE_URL}/ws/presence/?token=${encodeURIComponent(token)}`)
  let pingInterval = null

  socket.onopen = () => {
    callbacks.onOpen?.()
    pingInterval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'presence.ping' }))
      }
    }, 25000)
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    callbacks.onEvent?.(data)

    if (data.type === 'contact_request_created' || data.type === 'contact_request_updated') {
      callbacks.onContactRequestChanged?.(data)
    }

    if (data.type === 'contacts_changed') {
      callbacks.onContactsChanged?.(data)
    }

    if (data.type === 'contact_status_updated') {
      callbacks.onContactStatusUpdated?.(data)
    }

    if (data.type === 'profile_updated') {
      callbacks.onProfileUpdated?.(data)
    }

    if (data.type === 'music_status_updated') {
      callbacks.onMusicStatusUpdated?.(data)
    }

    if (data.type === 'message_received') {
      callbacks.onMessageReceived?.(data)
    }

    if (data.type === 'typing_updated') {
      callbacks.onTypingUpdated?.(data)
    }
  }

  socket.onerror = (error) => {
    callbacks.onError?.(error)
  }

  socket.onclose = (event) => {
    if (pingInterval) clearInterval(pingInterval)
    callbacks.onClose?.(event)
  }

  return {
    close() {
      if (pingInterval) clearInterval(pingInterval)
      socket.close()
    },
  }
}
