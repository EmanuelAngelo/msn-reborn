import axios from 'axios'

export function getAuthToken() {
  return localStorage.getItem('msn_auth_token')
}

export function setAuthToken(token) {
  if (token) localStorage.setItem('msn_auth_token', token)
}

export function clearAuthToken() {
  localStorage.removeItem('msn_auth_token')
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  withCredentials: false,
})


export function areWebSocketsEnabled() {
  const value = import.meta.env.VITE_ENABLE_WEBSOCKETS

  // Em produção no PythonAnywhere, WebSocket não fica disponível neste modelo de deploy.
  // Por isso o padrão é desligado. Em outro provedor com ASGI/WebSocket, use VITE_ENABLE_WEBSOCKETS=true.
  return String(value || '').toLowerCase() === 'true'
}

export function getWebSocketBaseUrl() {
  if (import.meta.env.VITE_WS_BASE_URL) {
    return import.meta.env.VITE_WS_BASE_URL
  }

  const apiUrl = api.defaults.baseURL || window.location.origin

  if (apiUrl.startsWith('/')) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}`
  }

  try {
    const url = new URL(apiUrl)
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    url.pathname = ''
    url.search = ''
    url.hash = ''
    return url.toString().replace(/\/$/, '')
  } catch {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}`
  }
}

api.interceptors.request.use((config) => {
  const token = getAuthToken()

  if (token) {
    config.headers.Authorization = `Token ${token}`
  }

  return config
})

export async function initCsrf() {
  // Mantido apenas para compatibilidade com imports antigos.
  // O frontend usa Token Authentication e não depende mais de CSRF/cookie.
  return Promise.resolve()
}
