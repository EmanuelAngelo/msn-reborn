import axios from 'axios'

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift())
  return null
}

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
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) config.headers.Authorization = `Token ${token}`

  const csrf = getCookie('csrftoken')
  if (csrf) config.headers['X-CSRFToken'] = csrf

  return config
})

export async function initCsrf() {
  await api.get('/auth/csrf/')
}
