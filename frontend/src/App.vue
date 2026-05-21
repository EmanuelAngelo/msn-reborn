<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactManager from './components/ContactManager.vue'
import ChatWindow from './components/ChatWindow.vue'
import ProfilePanel from './components/ProfilePanel.vue'
import { getMe, login as loginRequest, register as registerRequest, logout as logoutRequest } from './services/auth'
import { getMusicStatus, listContacts, spotifyConnectUrl, syncSpotify } from './services/msn'
import { createPresenceSocket } from './services/presenceSocket'

const profile = ref(null)
const music = ref(null)
const contacts = ref([])
const selectedContact = ref(null)
const mode = ref('login')
const loading = ref(false)
const error = ref('')

let presenceSocket = null
let spotifySyncInterval = null
let spotifySyncRunning = false

const form = ref({
  email: '',
  username: '',
  display_name: '',
  password: '',
})

function contactUserId(item) {
  return item?.contact_profile?.user_id || String(item?.contact || '')
}

function applyPresenceUpdate(updatedProfile) {
  if (!updatedProfile?.user_id) return

  if (profile.value?.user_id === updatedProfile.user_id) {
    profile.value = {
      ...profile.value,
      status: updatedProfile.status,
      last_seen_at: updatedProfile.last_seen_at,
    }
  }

  contacts.value = contacts.value.map((item) => {
    if (contactUserId(item) !== updatedProfile.user_id) return item

    return {
      ...item,
      contact_profile: {
        ...item.contact_profile,
        status: updatedProfile.status,
        last_seen_at: updatedProfile.last_seen_at,
      },
    }
  })

  if (selectedContact.value && contactUserId(selectedContact.value) === updatedProfile.user_id) {
    selectedContact.value = {
      ...selectedContact.value,
      contact_profile: {
        ...selectedContact.value.contact_profile,
        status: updatedProfile.status,
        last_seen_at: updatedProfile.last_seen_at,
      },
    }
  }
}

function applyMusicStatusUpdate(payload) {
  const userId = payload?.user_id
  const musicPayload = payload?.music

  if (!userId || !musicPayload) return

  if (profile.value?.user_id === userId) {
    music.value = musicPayload
  }

  contacts.value = contacts.value.map((item) => {
    if (contactUserId(item) !== userId) return item

    return {
      ...item,
      music_status: musicPayload,
    }
  })

  if (selectedContact.value && contactUserId(selectedContact.value) === userId) {
    selectedContact.value = {
      ...selectedContact.value,
      music_status: musicPayload,
    }
  }
}

function connectPresence() {
  if (presenceSocket) {
    presenceSocket.close()
    presenceSocket = null
  }

  try {
    presenceSocket = createPresenceSocket({
      onReady: applyPresenceUpdate,
      onPresenceUpdated: applyPresenceUpdate,
      onMusicStatusUpdated: applyMusicStatusUpdate,
      onClose(event) {
        if (profile.value && event.code === 4001) {
          error.value = 'Presença em tempo real recusada: token inválido. Faça login novamente.'
        }
      },
    })
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Não foi possível conectar presença em tempo real.'
  }
}

function closePresence() {
  if (presenceSocket) {
    presenceSocket.close()
    presenceSocket = null
  }
}

async function syncSpotifySilently() {
  if (!profile.value || spotifySyncRunning) return

  spotifySyncRunning = true

  try {
    const updatedMusic = await syncSpotify()
    music.value = updatedMusic

    // Mantém a lista de contatos sincronizada caso algum contato tenha atualizado pelo mesmo ciclo.
    // O WebSocket de presença já faz isso em tempo real, mas este refresh leve ajuda quando a aba estava fechada.
    contacts.value = await listContacts()

    if (selectedContact.value) {
      const selectedId = selectedContact.value.id
      selectedContact.value = contacts.value.find((item) => item.id === selectedId) || selectedContact.value
    }
  } catch (err) {
    // 400 = Spotify ainda não conectado. Isso não deve incomodar o usuário durante o auto-sync.
    if (![400, 401, 403, 429].includes(err.response?.status)) {
      console.warn('Falha ao sincronizar Spotify automaticamente.', err)
    }
  } finally {
    spotifySyncRunning = false
  }
}

function startSpotifyAutoSync() {
  stopSpotifyAutoSync()

  // Primeira tentativa rápida e depois atualização periódica.
  syncSpotifySilently()

  spotifySyncInterval = window.setInterval(() => {
    syncSpotifySilently()
  }, 30000)
}

function stopSpotifyAutoSync() {
  if (spotifySyncInterval) {
    window.clearInterval(spotifySyncInterval)
    spotifySyncInterval = null
  }
}

async function loadDashboard() {
  profile.value = await getMe()
  contacts.value = await listContacts()
  music.value = await getMusicStatus()
  if (!selectedContact.value) selectedContact.value = contacts.value[0] || null
  connectPresence()
  startSpotifyAutoSync()
}

async function login() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await loginRequest(form.value.email, form.value.password)
    await loadDashboard()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Falha no login. Verifique CSRF, sessão e credenciais.'
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
    contacts.value = await listContacts()
  } catch (err) {
    const detail = err.response?.data?.detail || ''
    if (err.response?.status === 400 && detail.toLowerCase().includes('spotify')) {
      window.location.href = spotifyConnectUrl()
      return
    }
    error.value = detail || 'Não foi possível sincronizar com Spotify.'
  }
}

async function logout() {
  stopSpotifyAutoSync()
  closePresence()
  await logoutRequest()
  profile.value = null
  contacts.value = []
  music.value = null
  selectedContact.value = null
}

onBeforeUnmount(() => {
  stopSpotifyAutoSync()
  closePresence()
})

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
</script>

<template>
  <main class="min-h-screen p-4 md:p-8">
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

    <div v-else class="mx-auto grid max-w-7xl grid-cols-1 gap-6 lg:grid-cols-[360px_1fr]">
      <section class="msn-window overflow-hidden rounded-xl border border-sky-700 bg-white/90">
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
        <ProfilePanel :profile="profile" :music="music" />
        <ContactList :contacts="contacts" :selected-id="selectedContact?.id" @select="selectedContact = $event" />
        <ContactManager :current-user-id="profile.user_id" @changed="loadDashboard" />
      </section>

      <div>
        <div v-if="error" class="mb-3 rounded bg-red-50 p-3 text-sm text-red-700">{{ error }}</div>
        <ChatWindow :contact="selectedContact" />
      </div>
    </div>
  </main>
</template>
