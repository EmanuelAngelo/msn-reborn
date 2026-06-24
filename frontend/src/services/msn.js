import { api, getAuthToken } from './api'

export async function listContacts() {
  const { data } = await api.get('/contacts/')
  return data.results || data
}

export async function searchUsers(q) {
  const { data } = await api.get('/users/search/', { params: { q } })
  return data.results || data
}

export async function createContactRequest(receiver, message = '') {
  const { data } = await api.post('/contact-requests/', { receiver, message })
  return data
}

export async function listContactRequests() {
  const { data } = await api.get('/contact-requests/')
  return data.results || data
}

export async function acceptContactRequest(id) {
  const { data } = await api.post(`/contact-requests/${id}/accept/`)
  return data
}

export async function rejectContactRequest(id) {
  const { data } = await api.post(`/contact-requests/${id}/reject/`)
  return data
}

export async function openDirectConversation(contactId) {
  const { data } = await api.post('/conversations/direct/', { contact_id: contactId })
  return data
}

export async function listMessages(conversationId) {
  const { data } = await api.get(`/conversations/${conversationId}/messages/`)
  return data
}

export async function sendMessage(conversationId, content) {
  const { data } = await api.post(`/conversations/${conversationId}/messages/`, { type: 'text', content })
  return data
}

export async function sendNudge(conversationId) {
  const { data } = await api.post(`/conversations/${conversationId}/nudge/`)
  return data
}

export async function blockContact(contactId) {
  const { data } = await api.post(`/contacts/${contactId}/block/`)
  return data
}

export async function toggleFavoriteContact(contactId) {
  const { data } = await api.post(`/contacts/${contactId}/favorite/`)
  return data
}

export async function getMusicStatus() {
  const { data } = await api.get('/music/status/')
  return data
}

export async function syncSpotify() {
  const { data } = await api.post('/spotify/sync/')
  return data
}

export function spotifyConnectUrl() {
  const token = getAuthToken()
  const url = new URL(`${api.defaults.baseURL}/spotify/connect/`)
  if (token) url.searchParams.set('auth_token', token)
  return url.toString()
}
