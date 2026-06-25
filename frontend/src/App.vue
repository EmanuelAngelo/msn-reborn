<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactManager from './components/ContactManager.vue'
import ChatWindow from './components/ChatWindow.vue'
import ProfilePanel from './components/ProfilePanel.vue'
import LoginScreen from './components/LoginScreen.vue'
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

const form = ref({
  email: '',
  username: '',
  display_name: '',
  password: '',
})

let presenceSocket = null
let spotifyInterval = null
let contactPollingInterval = null

function selectedContactStillExists(newContacts) {
  if (!selectedContact.value) return false
  return newContacts.some((item) => item.id === selectedContact.value.id)
}

async function refreshContacts({ keepSelection = true } = {}) {
  const newContacts = await listContacts()
  contacts.value = newContacts

  if (!keepSelection || !selectedContactStillExists(newContacts)) {
    selectedContact.value = newContacts[0] || null
  } else if (selectedContact.value) {
    selectedContact.value = newContacts.find((item) => item.id === selectedContact.value.id) || selectedContact.value
  }
}

async function loadDashboard() {
  profile.value = await getMe()
  await refreshContacts()
  music.value = await getMusicStatus()
  refreshSignal.value++
  startPresenceSocket()
  startSpotifyAutoSync()
}

function startPresenceSocket() {
  stopPresenceSocket()

  // Em PythonAnywhere, usamos polling REST para contatos/convites/status,
  // evitando erro no console por tentativa de WebSocket.
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

      async onContactStatusUpdated(event) {
        contacts.value = contacts.value.map((item) => {
          if (item.contact_profile?.user_id !== event.user_id) return item
          return {
            ...item,
            contact_profile: {
              ...item.contact_profile,
              status: event.status,
            },
          }
        })

        if (selectedContact.value?.contact_profile?.user_id === event.user_id) {
          selectedContact.value = {
            ...selectedContact.value,
            contact_profile: {
              ...selectedContact.value.contact_profile,
              status: event.status,
            },
          }
        }
      },

      async onProfileUpdated(event) {
        if (profile.value?.user_id === event.user_id) {
          profile.value = event.profile
        }

        contacts.value = contacts.value.map((item) => {
          if (item.contact_profile?.user_id !== event.user_id) return item
          return {
            ...item,
            contact_profile: event.profile,
          }
        })

        if (selectedContact.value?.contact_profile?.user_id === event.user_id) {
          selectedContact.value = {
            ...selectedContact.value,
            contact_profile: event.profile,
          }
        }
      },

      async onMusicStatusUpdated(event) {
        if (profile.value?.user_id === event.user_id) {
          music.value = event.music
        }

        contacts.value = contacts.value.map((item) => {
          if (item.contact_profile?.user_id !== event.user_id) return item
          return {
            ...item,
            music_status: event.music,
          }
        })
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
      await refreshContacts()
      refreshSignal.value++
    } catch {
      // Mantém o frontend funcionando mesmo quando WebSocket não está disponível no servidor.
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
  } catch (err) {
    // Spotify pode não estar conectado ainda. Não quebra o fluxo do chat.
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
  } catch (err) {
    error.value = 'Não foi possível criar a conta. Verifique os campos.'
  } finally {
    loading.value = false
  }
}

async function refreshSpotify() {
  error.value = ''

  try {
    music.value = await syncSpotify()
    await refreshContacts()
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
  </main>
</template>
