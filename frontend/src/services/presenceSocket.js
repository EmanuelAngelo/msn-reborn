import { getAuthToken } from './api'

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000'

export function createPresenceSocket(callbacks = {}) {
  const token = getAuthToken()

  if (!token) {
    throw new Error('Token de autenticação não encontrado para presença.')
  }

  const socket = new WebSocket(`${WS_BASE_URL}/ws/presence/?token=${encodeURIComponent(token)}`)
  let pingInterval = null

  socket.onopen = () => {
    callbacks.onOpen?.()
    pingInterval = window.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'presence.ping' }))
      }
    }, 25000)
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'presence.ready') {
      callbacks.onReady?.(data.profile)
      return
    }

    if (data.type === 'presence.updated') {
      callbacks.onPresenceUpdated?.(data.profile)
      return
    }

    if (data.type === 'music_status_updated') {
      callbacks.onMusicStatusUpdated?.(data)
    }
  }

  socket.onerror = (error) => {
    console.error('Erro no WebSocket de presença:', error)
    callbacks.onError?.(error)
  }

  socket.onclose = (event) => {
    if (pingInterval) {
      window.clearInterval(pingInterval)
      pingInterval = null
    }
    callbacks.onClose?.(event)
  }

  function safeSend(payload) {
    if (socket.readyState !== WebSocket.OPEN) return false
    socket.send(JSON.stringify(payload))
    return true
  }

  return {
    setStatus(status) {
      return safeSend({ type: 'presence.set_status', status })
    },

    close() {
      if (pingInterval) {
        window.clearInterval(pingInterval)
        pingInterval = null
      }
      socket.close()
    },
  }
}
