import { api, clearAuthToken, setAuthToken } from './api'

function normalizeAuthResponse(data) {
  if (data?.token) setAuthToken(data.token)
  return data?.profile || data
}

export async function getMe() {
  const { data } = await api.get('/me/')
  return data
}

export async function login(email, password) {
  const { data } = await api.post('/auth/login/', { email, password })
  return normalizeAuthResponse(data)
}

export async function register(payload) {
  const { data } = await api.post('/auth/register/', payload)
  return normalizeAuthResponse(data)
}

export async function updateMe(payload) {
  const { data } = await api.patch('/me/', payload)
  return data
}

export async function logout() {
  try {
    await api.post('/auth/logout/')
  } catch {
    // Limpa sessão local mesmo se o servidor não responder.
  } finally {
    clearAuthToken()
  }
}
