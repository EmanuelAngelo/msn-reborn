<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactManager from './components/ContactManager.vue'
import ChatWindow from './components/ChatWindow.vue'
import ProfilePanel from './components/ProfilePanel.vue'
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
  await logoutRequest()
  profile.value = null
  contacts.value = []
  music.value = null
  selectedContact.value = null
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
  <main class="h-screen overflow-hidden p-4 md:p-8">
    <div v-if="!profile" class="mx-auto max-w-md overflow-hidden rounded-xl border border-sky-700 bg-white/95 shadow-2xl">
      <div class="msn-titlebar px-4 py-3 text-center text-lg font-bold text-white">
        MSN Reborn
      </div>
      <div class="space-y-4 p-6">
        <div class="text-center">
          <div class="mx-auto grid h-20 w-20 place-items-center rounded-2xl border border-sky-500 bg-sky-50 text-4xl shadow-inner">🙂</div>
          <h1 class="mt-3 text-xl font-bold text-slate-800">Entrar no Messenger</h1>
          <p class="text-sm text-slate-500">MVP integrado com Django REST API</p>
        </div>

        <div v-if="error" class="rounded bg-red-50 p-3 text-sm text-red-700">{{ error }}</div>

        <input v-model="form.email" class="w-full rounded border border-sky-300 px-3 py-2" placeholder="E-mail" />
        <input v-if="mode === 'register'" v-model="form.username" class="w-full rounded border border-sky-300 px-3 py-2" placeholder="Usuário" />
        <input v-if="mode === 'register'" v-model="form.display_name" class="w-full rounded border border-sky-300 px-3 py-2" placeholder="Nome de exibição" />
        <input v-model="form.password" type="password" class="w-full rounded border border-sky-300 px-3 py-2" placeholder="Senha" />

        <button
          class="w-full rounded bg-sky-600 px-4 py-2 font-bold text-white shadow hover:bg-sky-700 disabled:opacity-60"
          :disabled="loading"
          @click="mode === 'login' ? login() : register()"
        >
          {{ loading ? 'Aguarde...' : mode === 'login' ? 'Entrar' : 'Criar conta' }}
        </button>

        <button class="w-full text-sm font-semibold text-sky-700" @click="mode = mode === 'login' ? 'register' : 'login'">
          {{ mode === 'login' ? 'Criar nova conta' : 'Já tenho conta' }}
        </button>
      </div>
    </div>

    <div v-else class="mx-auto grid h-full max-w-7xl grid-cols-1 gap-6 overflow-hidden lg:grid-cols-[360px_minmax(0,1fr)]">
      <section class="msn-window flex min-h-0 flex-col overflow-hidden rounded-xl border border-sky-700 bg-white/90">
        <div class="msn-titlebar flex items-center justify-between px-4 py-2 text-white">
          <div class="flex items-center gap-2">
            <div class="h-4 w-4 rounded-full bg-lime-300 shadow-inner"></div>
            <span class="font-bold">MSN Reborn</span>
          </div>
          <div class="flex gap-2">
            <button class="rounded bg-white/20 px-2 py-1 text-xs" @click="refreshSpotify">Conectar/Sync Spotify</button>
            <button class="rounded bg-white/20 px-2 py-1 text-xs" @click="logout">Sair</button>
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <ProfilePanel :profile="profile" :music="music" @updated="handleProfileUpdated" />
          <ContactList :contacts="contacts" :selected-id="selectedContact?.id" @select="selectedContact = $event" />
          <ContactManager
          :current-user-id="profile.user_id"
          :refresh-signal="refreshSignal"
          @changed="handleContactsChanged"
          />
        </div>
      </section>

      <div class="min-h-0 overflow-hidden">
        <div v-if="error" class="mb-3 rounded bg-red-50 p-3 text-sm text-red-700">{{ error }}</div>
        <ChatWindow :contact="selectedContact" :current-user="profile" @contact-changed="handleContactsChanged" />
      </div>
    </div>
  </main>
</template>
