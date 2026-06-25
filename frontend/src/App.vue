<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactManager from './components/ContactManager.vue'
import ChatWindow from './components/ChatWindow.vue'
import ProfilePanel from './components/ProfilePanel.vue'
import LoginScreen from './components/LoginScreen.vue'
import OnlineNotifications from './components/OnlineNotifications.vue'
import { getMe, login as loginRequest, register as registerRequest, logout as logoutRequest } from './services/auth'
import { getMusicStatus, listContacts, spotifyConnectUrl, syncSpotify } from './services/msn'
import { areWebSocketsEnabled } from './services/api'
import { createPresenceSocket } from './services/presenceSocket'

const profile = ref(null)
const music = ref(null)
const contacts = ref([])
const selectedContact = ref(null)
const mode = ref('login')
const loading = ref(false)
const error = ref('')
const refreshSignal = ref(0)
const onlineNotifications = ref([])

const form = ref({
  email: '',
  username: '',
  display_name: '',
  password: '',
})

let presenceSocket = null
let spotifyInterval = null
let contactPollingInterval = null
const contactStatusCache = new Map()
const notificationTimers = new Map()
let presenceTrackingReady = false

function findContactByUserId(userId) {
  return contacts.value.find((item) => contactBelongsToUser(item, userId)) || null
}

function syncStatusCacheFromContacts() {
  contactStatusCache.clear()
  for (const item of contacts.value) {
    const userId = item.contact_profile?.user_id || item.contact
    if (userId == null) continue
    contactStatusCache.set(String(userId), item.contact_profile?.status || 'offline')
  }
}

function dismissOnlineNotification(id) {
  onlineNotifications.value = onlineNotifications.value.filter((item) => item.id !== id)
  const timer = notificationTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    notificationTimers.delete(id)
  }
}

function pushOnlineNotification(payload) {
  const id = payload.id || `${payload.userId}-${Date.now()}`
  const entry = { ...payload, id }

  onlineNotifications.value = [
    entry,
    ...onlineNotifications.value.filter((item) => item.userId !== payload.userId),
  ].slice(0, 4)

  if (notificationTimers.has(id)) {
    clearTimeout(notificationTimers.get(id))
  }

  notificationTimers.set(
    id,
    setTimeout(() => dismissOnlineNotification(id), 3000),
  )
}

function notifyIfCameOnline(userId, newStatus, profileHint = null) {
  const key = String(userId)

  if (sameUserId(userId, profile.value?.user_id)) {
    contactStatusCache.set(key, newStatus)
    return
  }

  const previousStatus = contactStatusCache.get(key) ?? 'offline'

  if (presenceTrackingReady && previousStatus === 'offline' && newStatus === 'online') {
    const contact = findContactByUserId(userId)
    const profileData = profileHint || contact?.contact_profile || {}

    pushOnlineNotification({
      userId: key,
      displayName: profileData.display_name || contact?.nickname || contact?.contact_profile?.email || 'Contato',
      avatarUrl: profileData.avatar_url || contact?.contact_profile?.avatar_url || '',
      personalMessage: profileData.personal_message || contact?.contact_profile?.personal_message || '',
    })
  }

  contactStatusCache.set(key, newStatus)
}

function detectOnlineFromContacts(previousContacts) {
  if (!presenceTrackingReady) return

  for (const item of contacts.value) {
    const userId = String(item.contact_profile?.user_id || item.contact)
    const newStatus = item.contact_profile?.status || 'offline'
    const previous = previousContacts.get(userId)
    if (previous === undefined) {
      contactStatusCache.set(userId, newStatus)
      continue
    }
    notifyIfCameOnline(userId, newStatus, item.contact_profile)
  }
}

function openContactFromNotification(notification) {
  const contact = findContactByUserId(notification.userId)
  if (contact) selectedContact.value = contact
  dismissOnlineNotification(notification.id)
}

function enablePresenceTracking() {
  syncStatusCacheFromContacts()
  window.setTimeout(() => {
    presenceTrackingReady = true
  }, 2000)
}

function sameUserId(a, b) {
  if (a == null || b == null) return false
  return String(a) === String(b)
}

function contactBelongsToUser(item, userId) {
  if (!item || userId == null) return false
  return sameUserId(item.contact_profile?.user_id, userId) || sameUserId(item.contact, userId)
}

function patchContactInList(userId, patchFn) {
  contacts.value = contacts.value.map((item) => {
    if (!contactBelongsToUser(item, userId)) return item
    return patchFn(item)
  })
}

function patchSelectedContact(userId, patchFn) {
  if (selectedContact.value && contactBelongsToUser(selectedContact.value, userId)) {
    selectedContact.value = patchFn(selectedContact.value)
  }
}

function applyContactStatusUpdate(userId, status) {
  notifyIfCameOnline(userId, status)

  const mergeStatus = (item) => ({
    ...item,
    contact_profile: {
      ...item.contact_profile,
      status,
    },
  })

  patchContactInList(userId, mergeStatus)
  patchSelectedContact(userId, mergeStatus)
}

function applyContactProfileUpdate(userId, profileData) {
  if (!profileData) return

  if (profileData.status) {
    notifyIfCameOnline(userId, profileData.status, profileData)
  }

  const mergeProfile = (item) => ({
    ...item,
    contact_profile: {
      ...item.contact_profile,
      ...profileData,
    },
  })

  patchContactInList(userId, mergeProfile)
  patchSelectedContact(userId, mergeProfile)
}

function applyContactMusicUpdate(userId, musicData) {
  const mergeMusic = (item) => ({
    ...item,
    music_status: musicData ?? {
      is_playing: false,
      track_name: '',
      artist_name: '',
      album_name: '',
    },
  })

  patchContactInList(userId, mergeMusic)
  patchSelectedContact(userId, mergeMusic)
}

function selectedContactStillExists(newContacts) {
  if (!selectedContact.value) return false
  return newContacts.some((item) => item.id === selectedContact.value.id)
}

async function refreshContacts({ keepSelection = true } = {}) {
  const previousStatuses = new Map(contactStatusCache)
  const newContacts = await listContacts()
  contacts.value = newContacts

  if (!keepSelection || !selectedContactStillExists(newContacts)) {
    selectedContact.value = newContacts[0] || null
  } else if (selectedContact.value) {
    selectedContact.value = newContacts.find((item) => item.id === selectedContact.value.id) || selectedContact.value
  }

  if (presenceTrackingReady) {
    detectOnlineFromContacts(previousStatuses)
  } else if (!contactStatusCache.size) {
    syncStatusCacheFromContacts()
  }
}

async function loadDashboard() {
  profile.value = await getMe()
  await refreshContacts()
  music.value = await getMusicStatus()
  refreshSignal.value++
  enablePresenceTracking()
  startPresenceSocket()
  startSpotifyAutoSync()
}

function startPresenceSocket() {
  stopPresenceSocket()

  if (!areWebSocketsEnabled()) {
    startContactPolling()
    return
  }

  try {
    presenceSocket = createPresenceSocket({
      onOpen() {
        stopContactPolling()
      },

      async onContactRequestChanged() {
        refreshSignal.value++
        await refreshContacts()
      },

      async onContactsChanged() {
        refreshSignal.value++
        await refreshContacts({ keepSelection: false })
      },

      onContactStatusUpdated(event) {
        applyContactStatusUpdate(event.user_id, event.status)
      },

      onProfileUpdated(event) {
        applyContactProfileUpdate(event.user_id, event.profile)
      },

      onMusicStatusUpdated(event) {
        if (sameUserId(profile.value?.user_id, event.user_id)) {
          music.value = event.music
        }
        applyContactMusicUpdate(event.user_id, event.music)
      },

      onError() {
        startContactPolling()
      },

      onClose() {
        startContactPolling()
      },
    })
  } catch {
    startContactPolling()
  }
}

function stopPresenceSocket() {
  if (presenceSocket) {
    presenceSocket.close()
    presenceSocket = null
  }
}

function startContactPolling() {
  if (contactPollingInterval) return

  contactPollingInterval = setInterval(async () => {
    if (!profile.value) return

    try {
      await refreshContacts({ keepSelection: true })
      refreshSignal.value++
    } catch {
      // Mantém o frontend funcionando quando WebSocket não está disponível.
    }
  }, 5000)
}

function stopContactPolling() {
  if (contactPollingInterval) {
    clearInterval(contactPollingInterval)
    contactPollingInterval = null
  }
}

async function syncSpotifyMusicSilently() {
  try {
    music.value = await syncSpotify()
    if (profile.value?.user_id) {
      applyContactMusicUpdate(profile.value.user_id, music.value)
    }
  } catch {
    // Spotify pode não estar conectado ainda.
  }
}

function startSpotifyAutoSync() {
  stopSpotifyAutoSync()
  syncSpotifyMusicSilently()
  spotifyInterval = setInterval(syncSpotifyMusicSilently, 30000)
}

function stopSpotifyAutoSync() {
  if (spotifyInterval) {
    clearInterval(spotifyInterval)
    spotifyInterval = null
  }
}

async function login() {
  loading.value = true
  error.value = ''

  try {
    profile.value = await loginRequest(form.value.email, form.value.password)
    await loadDashboard()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Falha no login. Verifique credenciais.'
  } finally {
    loading.value = false
  }
}

async function register() {
  loading.value = true
  error.value = ''

  try {
    profile.value = await registerRequest(form.value)
    await loadDashboard()
  } catch {
    error.value = 'Não foi possível criar a conta. Verifique os campos.'
  } finally {
    loading.value = false
  }
}

async function refreshSpotify() {
  error.value = ''

  try {
    music.value = await syncSpotify()
    if (profile.value?.user_id) {
      applyContactMusicUpdate(profile.value.user_id, music.value)
    }
    await refreshContacts({ keepSelection: true })
  } catch (err) {
    const detail = err.response?.data?.detail || ''
    if (err.response?.status === 400 && detail.toLowerCase().includes('spotify')) {
      window.location.href = spotifyConnectUrl()
      return
    }
    error.value = detail || 'Não foi possível sincronizar com Spotify.'
  }
}

async function handleContactsChanged() {
  await refreshContacts()
  refreshSignal.value++
}

function handleProfileUpdated(updatedProfile) {
  profile.value = updatedProfile
  if (profile.value?.user_id) {
    applyContactProfileUpdate(profile.value.user_id, updatedProfile)
  }
  refreshSignal.value++
}

async function logout() {
  stopSpotifyAutoSync()
  stopPresenceSocket()
  stopContactPolling()
  try {
    await logoutRequest()
  } catch {
    // Estado local é limpo mesmo se a API falhar.
  }
  profile.value = null
  contacts.value = []
  music.value = null
  selectedContact.value = null
  onlineNotifications.value = []
  contactStatusCache.clear()
  presenceTrackingReady = false
  notificationTimers.forEach((timer) => clearTimeout(timer))
  notificationTimers.clear()
  error.value = ''
}

function handleAuthSubmit() {
  if (mode.value === 'login') login()
  else register()
}

function toggleAuthMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
}

onMounted(async () => {
  try {
    await loadDashboard()
    const params = new URLSearchParams(window.location.search)
    if (params.get('spotify') === 'connected') {
      await refreshSpotify()
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  } catch {
    profile.value = null
  }
})

onBeforeUnmount(() => {
  stopSpotifyAutoSync()
  stopPresenceSocket()
  stopContactPolling()
  notificationTimers.forEach((timer) => clearTimeout(timer))
  notificationTimers.clear()
})
</script>

<template>
  <LoginScreen
    v-if="!profile"
    :mode="mode"
    :form="form"
    :loading="loading"
    :error="error"
    @submit="handleAuthSubmit"
    @toggle-mode="toggleAuthMode"
  />

  <main v-else class="app-shell">
    <div class="app-dashboard app-dashboard-mobile-stack">
      <section class="msn-window app-sidebar rounded-xl border border-sky-700 bg-white/90">
        <div class="msn-titlebar flex shrink-0 items-center justify-between px-3 py-2 text-white sm:px-4">
          <div class="flex items-center gap-2">
            <div class="h-4 w-4 rounded-full bg-lime-300 shadow-inner"></div>
            <span class="font-bold text-sm sm:text-base">MSN Reborn</span>
          </div>
          <div class="flex gap-1 sm:gap-2">
            <button class="rounded bg-white/20 px-2 py-1 text-[10px] sm:text-xs" @click="refreshSpotify">
              Spotify
            </button>
            <button class="rounded bg-white/20 px-2 py-1 text-[10px] sm:text-xs" @click="logout">Sair</button>
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain">
          <ProfilePanel :profile="profile" :music="music" @updated="handleProfileUpdated" />
          <ContactList :contacts="contacts" :selected-id="selectedContact?.id" @select="selectedContact = $event" />
          <ContactManager
            :current-user-id="profile.user_id"
            :refresh-signal="refreshSignal"
            @changed="handleContactsChanged"
          />
        </div>
      </section>

      <div class="app-chat min-h-0">
        <div v-if="error" class="mb-2 rounded bg-red-50 p-2 text-sm text-red-700 sm:mb-3 sm:p-3">{{ error }}</div>
        <ChatWindow :contact="selectedContact" :current-user="profile" @contact-changed="handleContactsChanged" />
      </div>
    </div>

    <OnlineNotifications
      :notifications="onlineNotifications"
      @dismiss="dismissOnlineNotification"
      @open="openContactFromNotification"
    />
  </main>
</template>
