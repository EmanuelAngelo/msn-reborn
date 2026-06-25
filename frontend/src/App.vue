<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import ContactList from './components/ContactList.vue'
import ContactManager from './components/ContactManager.vue'
import ChatWindow from './components/ChatWindow.vue'
import ChatTaskbar from './components/ChatTaskbar.vue'
import ProfilePanel from './components/ProfilePanel.vue'
import EmptyChatState from './components/EmptyChatState.vue'
import LoginScreen from './components/LoginScreen.vue'
import OnlineNotifications from './components/OnlineNotifications.vue'
import { useTheme } from './composables/useTheme'
import { useLocale } from './composables/useLocale'
import { getMe, login as loginRequest, register as registerRequest, logout as logoutRequest } from './services/auth'
import { getMusicStatus, listContacts, listConversations, spotifyConnectUrl, syncSpotify } from './services/msn'
import { areWebSocketsEnabled } from './services/api'
import { createPresenceSocket } from './services/presenceSocket'

const profile = ref(null)
const music = ref(null)
const contacts = ref([])
const selectedContact = ref(null)
const openChats = ref([])
const activeChatId = ref(null)
const minimizedChatIds = ref([])
const mode = ref('login')
const loading = ref(false)
const error = ref('')
const refreshSignal = ref(0)
const onlineNotifications = ref([])
const activeNav = ref('profile')
const contactTypingByUserId = ref({})

const { theme, toggleTheme } = useTheme()
const { t, toggleLocale } = useLocale()

const form = ref({
  email: '',
  username: '',
  display_name: '',
  password: '',
})

let presenceSocket = null
let spotifyInterval = null
let contactPollingInterval = null
let messageNotificationPollingInterval = null
const contactStatusCache = new Map()
const lastKnownMessageIds = new Map()
const seenNotificationMessageIds = new Set()
const notificationTimers = new Map()
const typingClearTimers = new Map()
let presenceTrackingReady = false
let messageTrackingReady = false

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

function canReceiveNotifications() {
  const status = profile.value?.status
  return status === 'online' || status === 'away'
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
  if (!canReceiveNotifications()) return

  const kind = payload.kind || 'online'
  const id = payload.id || `${kind}-${payload.userId}-${payload.messageId || Date.now()}`
  const entry = { ...payload, kind, id }

  onlineNotifications.value = [
    entry,
    ...onlineNotifications.value.filter((item) => {
      if (payload.messageId) return item.messageId !== payload.messageId
      return !(item.kind === 'online' && item.userId === payload.userId)
    }),
  ].slice(0, 4)

  if (notificationTimers.has(id)) {
    clearTimeout(notificationTimers.get(id))
  }

  notificationTimers.set(
    id,
    setTimeout(() => dismissOnlineNotification(id), 3000),
  )
}

function handleIncomingMessage(message) {
  if (!canReceiveNotifications()) return
  if (!message?.id) return
  if (seenNotificationMessageIds.has(message.id)) return
  if (sameUserId(message.sender, profile.value?.user_id)) return

  const contact = findContactByUserId(message.sender)
  if (contact && isChatExpanded(contact.id)) return

  seenNotificationMessageIds.add(message.id)

  const isNudge = message.type === 'nudge'
  pushOnlineNotification({
    kind: isNudge ? 'nudge' : 'message',
    userId: String(message.sender),
    displayName: message.sender_name || contact?.nickname || contact?.contact_profile?.display_name || 'Contato',
    avatarUrl: contact?.contact_profile?.avatar_url || '',
    messagePreview: isNudge ? '' : (message.content || '').slice(0, 120),
    messageId: message.id,
  })
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

function getRemoteTyping(contact) {
  if (!contact) return null
  const userId = String(contact.contact_profile?.user_id || contact.contact || '')
  return contactTypingByUserId.value[userId] || null
}

function applyRemoteTyping(event) {
  const senderId = String(event.user?.id || '')
  if (!senderId || sameUserId(senderId, profile.value?.user_id)) return

  if (typingClearTimers.has(senderId)) {
    clearTimeout(typingClearTimers.get(senderId))
    typingClearTimers.delete(senderId)
  }

  if (!event.is_typing) {
    const next = { ...contactTypingByUserId.value }
    delete next[senderId]
    contactTypingByUserId.value = next
    return
  }

  contactTypingByUserId.value = {
    ...contactTypingByUserId.value,
    [senderId]: {
      isTyping: true,
      displayName: event.user?.display_name || event.user?.username || 'Contato',
    },
  }

  typingClearTimers.set(
    senderId,
    setTimeout(() => {
      const next = { ...contactTypingByUserId.value }
      delete next[senderId]
      contactTypingByUserId.value = next
      typingClearTimers.delete(senderId)
    }, 3500),
  )
}

function openContactFromNotification(notification) {
  const contact = findContactByUserId(notification.userId)
  if (contact) selectContact(contact)
  dismissOnlineNotification(notification.id)
}

function getOpenChatContact(chatId) {
  const fromList = contacts.value.find((item) => item.id === chatId)
  const fromOpen = openChats.value.find((item) => item.id === chatId)
  return fromList ? { ...fromOpen, ...fromList } : fromOpen
}

function syncOpenChatsFromContacts() {
  const validIds = new Set(contacts.value.map((item) => item.id))

  openChats.value = openChats.value
    .map((openChat) => {
      const updated = contacts.value.find((item) => item.id === openChat.id)
      return updated ? { ...openChat, ...updated } : openChat
    })
    .filter((openChat) => validIds.has(openChat.id))

  minimizedChatIds.value = minimizedChatIds.value.filter((id) => validIds.has(id))

  if (activeChatId.value && !validIds.has(activeChatId.value)) {
    activeChatId.value = null
  }
}

function selectContact(contact) {
  if (!contact) return

  selectedContact.value = contact

  if (!openChats.value.some((item) => item.id === contact.id)) {
    openChats.value.push({ ...contact })
  } else {
    syncOpenChatsFromContacts()
  }

  activeChatId.value = contact.id
  minimizedChatIds.value = minimizedChatIds.value.filter((id) => id !== contact.id)

  if (typeof window !== 'undefined' && window.innerWidth < 768) {
    activeNav.value = 'chats'
  }
}

function minimizeChat(chatId) {
  if (!chatId) return
  if (!minimizedChatIds.value.includes(chatId)) {
    minimizedChatIds.value.push(chatId)
  }
  if (activeChatId.value === chatId) {
    activeChatId.value = null
  }
}

function restoreChat(chatId) {
  const contact = getOpenChatContact(chatId)
  if (!contact) return
  selectContact(contact)
}

function closeChat(chatId) {
  openChats.value = openChats.value.filter((item) => item.id !== chatId)
  minimizedChatIds.value = minimizedChatIds.value.filter((id) => id !== chatId)

  if (activeChatId.value === chatId) {
    activeChatId.value = null
  }

  if (selectedContact.value?.id === chatId) {
    selectedContact.value = contacts.value[0] || null
  }
}

function isChatExpanded(chatId) {
  return activeChatId.value === chatId && !minimizedChatIds.value.includes(chatId)
}

const minimizedChats = computed(() =>
  openChats.value.filter((chat) => minimizedChatIds.value.includes(chat.id)),
)

const hasExpandedChat = computed(() =>
  Boolean(activeChatId.value && !minimizedChatIds.value.includes(activeChatId.value)),
)

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
  syncOpenChatsFromContacts()
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
  syncOpenChatsFromContacts()
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
  syncOpenChatsFromContacts()
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
    selectedContact.value = null
  } else if (selectedContact.value) {
    selectedContact.value = newContacts.find((item) => item.id === selectedContact.value.id) || selectedContact.value
  }

  if (presenceTrackingReady) {
    detectOnlineFromContacts(previousStatuses)
  } else if (!contactStatusCache.size) {
    syncStatusCacheFromContacts()
  }

  syncOpenChatsFromContacts()
}

async function loadDashboard() {
  profile.value = await getMe()
  await refreshContacts()
  music.value = await getMusicStatus()
  refreshSignal.value++
  await bootstrapMessageTracking()
  enablePresenceTracking()
  startPresenceSocket()
  startSpotifyAutoSync()
  if (!areWebSocketsEnabled()) {
    startMessageNotificationPolling()
  }
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

      onMessageReceived(event) {
        handleIncomingMessage(event.message)
      },

      onTypingUpdated(event) {
        applyRemoteTyping(event)
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

  startMessageNotificationPolling()
}

function stopContactPolling() {
  if (contactPollingInterval) {
    clearInterval(contactPollingInterval)
    contactPollingInterval = null
  }
}

async function bootstrapMessageTracking() {
  try {
    const conversations = await listConversations()
    for (const conv of conversations) {
      const last = conv.last_message
      if (last?.id) {
        lastKnownMessageIds.set(conv.id, last.id)
        seenNotificationMessageIds.add(last.id)
      }
    }
  } catch {
    // Sem conversas ainda ou API indisponível.
  } finally {
    messageTrackingReady = true
  }
}

async function pollMessageNotifications() {
  if (!profile.value) return

  try {
    const conversations = await listConversations()
    for (const conv of conversations) {
      const last = conv.last_message
      if (!last?.id) continue

      const previousId = lastKnownMessageIds.get(conv.id)
      lastKnownMessageIds.set(conv.id, last.id)

      if (!previousId) {
        if (messageTrackingReady && !sameUserId(last.sender, profile.value?.user_id)) {
          handleIncomingMessage({
            id: last.id,
            sender: last.sender,
            sender_name: last.sender_name,
            type: last.type,
            content: last.content,
            conversation: conv.id,
          })
        }
        continue
      }

      if (previousId !== last.id) {
        handleIncomingMessage({
          id: last.id,
          sender: last.sender,
          sender_name: last.sender_name,
          type: last.type,
          content: last.content,
          conversation: conv.id,
        })
      }
    }
  } catch {
    // Ignora falhas temporárias de rede.
  }
}

function startMessageNotificationPolling() {
  if (messageNotificationPollingInterval) return

  messageNotificationPollingInterval = setInterval(pollMessageNotifications, 4000)
}

function stopMessageNotificationPolling() {
  if (messageNotificationPollingInterval) {
    clearInterval(messageNotificationPollingInterval)
    messageNotificationPollingInterval = null
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
    error.value = err.response?.data?.detail || t('auth.loginError')
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
    error.value = t('auth.registerError')
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
    error.value = detail || t('auth.spotifyError')
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
  if (!canReceiveNotifications()) {
    onlineNotifications.value.forEach((item) => {
      const timer = notificationTimers.get(item.id)
      if (timer) clearTimeout(timer)
    })
    onlineNotifications.value = []
    notificationTimers.clear()
  }
  refreshSignal.value++
}

async function logout() {
  stopSpotifyAutoSync()
  stopPresenceSocket()
  stopContactPolling()
  stopMessageNotificationPolling()
  try {
    await logoutRequest()
  } catch {
    // Estado local é limpo mesmo se a API falhar.
  }
  profile.value = null
  contacts.value = []
  music.value = null
  selectedContact.value = null
  openChats.value = []
  activeChatId.value = null
  minimizedChatIds.value = []
  onlineNotifications.value = []
  contactTypingByUserId.value = {}
  contactStatusCache.clear()
  lastKnownMessageIds.clear()
  seenNotificationMessageIds.clear()
  presenceTrackingReady = false
  messageTrackingReady = false
  notificationTimers.forEach((timer) => clearTimeout(timer))
  notificationTimers.clear()
  typingClearTimers.forEach((timer) => clearTimeout(timer))
  typingClearTimers.clear()
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

function navigateTo(section) {
  activeNav.value = section
}

function handleStartConversation() {
  activeNav.value = 'contacts'
}

function handleViewAllContacts() {
  activeNav.value = 'contacts'
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
  stopMessageNotificationPolling()
  notificationTimers.forEach((timer) => clearTimeout(timer))
  notificationTimers.clear()
  typingClearTimers.forEach((timer) => clearTimeout(timer))
  typingClearTimers.clear()
})
</script>

<template>
  <LoginScreen
    v-if="!profile"
    :mode="mode"
    :form="form"
    :loading="loading"
    :error="error"
    :theme="theme"
    @submit="handleAuthSubmit"
    @toggle-mode="toggleAuthMode"
    @toggle-theme="toggleTheme"
    @toggle-locale="toggleLocale"
  />

  <main v-else class="reborn-app" :class="{ 'has-chat-taskbar': minimizedChats.length }">
    <AppHeader
      :theme="theme"
      @spotify="refreshSpotify"
      @logout="logout"
      @toggle-theme="toggleTheme"
      @toggle-locale="toggleLocale"
    />

    <div class="reborn-body">
      <AppSidebar :active="activeNav" @navigate="navigateTo" />

      <div class="reborn-main">
        <div v-if="error" class="reborn-alert reborn-alert--error reborn-main-alert">{{ error }}</div>

        <!-- Perfil: grid do mockup -->
        <div v-if="activeNav === 'profile'" class="reborn-grid reborn-grid--profile">
          <ProfilePanel :profile="profile" :music="music" @updated="handleProfileUpdated" />
          <ContactManager
            :current-user-id="profile.user_id"
            :refresh-signal="refreshSignal"
            @changed="handleContactsChanged"
          />
          <ContactList
            :contacts="contacts"
            :selected-id="selectedContact?.id"
            compact
            @select="selectContact"
            @view-all="handleViewAllContacts"
          />
          <section class="reborn-card reborn-chat-panel">
            <EmptyChatState v-if="!hasExpandedChat" @start="handleStartConversation" />
            <KeepAlive v-else>
              <ChatWindow
                v-for="chat in openChats"
                v-show="isChatExpanded(chat.id)"
                :key="chat.id"
                :contact="getOpenChatContact(chat.id)"
                :current-user="profile"
                :remote-typing="getRemoteTyping(getOpenChatContact(chat.id))"
                @minimize="minimizeChat(chat.id)"
                @close="closeChat(chat.id)"
                @contact-changed="handleContactsChanged"
              />
            </KeepAlive>
          </section>
        </div>

        <!-- Contatos: lista completa -->
        <div v-else-if="activeNav === 'contacts'" class="reborn-grid reborn-grid--contacts">
          <ContactList
            :contacts="contacts"
            :selected-id="selectedContact?.id"
            :compact="false"
            @select="selectContact"
          />
          <ContactManager
            :current-user-id="profile.user_id"
            :refresh-signal="refreshSignal"
            @changed="handleContactsChanged"
          />
          <section class="reborn-card reborn-chat-panel reborn-chat-panel--wide">
            <EmptyChatState v-if="!hasExpandedChat" @start="handleStartConversation" />
            <KeepAlive v-else>
              <ChatWindow
                v-for="chat in openChats"
                v-show="isChatExpanded(chat.id)"
                :key="chat.id"
                :contact="getOpenChatContact(chat.id)"
                :current-user="profile"
                :remote-typing="getRemoteTyping(getOpenChatContact(chat.id))"
                @minimize="minimizeChat(chat.id)"
                @close="closeChat(chat.id)"
                @contact-changed="handleContactsChanged"
              />
            </KeepAlive>
          </section>
        </div>

        <!-- Conversas -->
        <div v-else-if="activeNav === 'chats'" class="reborn-grid reborn-grid--chats">
          <article class="reborn-card reborn-chats-list">
            <header class="reborn-card-header">
              <h2 class="reborn-card-title">{{ t('chat.openTitle') }}</h2>
            </header>
            <button
              v-for="chat in openChats"
              :key="chat.id"
              type="button"
              class="reborn-chat-list-item"
              :class="{ 'reborn-chat-list-item--active': isChatExpanded(chat.id) }"
              @click="restoreChat(chat.id)"
            >
              <span class="reborn-chat-list-name">
                {{ chat.nickname || chat.contact_profile?.display_name || t('contacts.contact') }}
              </span>
              <span v-if="minimizedChatIds.includes(chat.id)" class="reborn-chat-list-badge">{{ t('chat.minimized') }}</span>
            </button>
            <p v-if="!openChats.length" class="reborn-muted-text reborn-chats-empty">
              {{ t('chat.noOpen') }}
            </p>
          </article>
          <section class="reborn-card reborn-chat-panel reborn-chat-panel--wide">
            <EmptyChatState v-if="!hasExpandedChat" @start="handleStartConversation" />
            <KeepAlive v-else>
              <ChatWindow
                v-for="chat in openChats"
                v-show="isChatExpanded(chat.id)"
                :key="chat.id"
                :contact="getOpenChatContact(chat.id)"
                :current-user="profile"
                :remote-typing="getRemoteTyping(getOpenChatContact(chat.id))"
                @minimize="minimizeChat(chat.id)"
                @close="closeChat(chat.id)"
                @contact-changed="handleContactsChanged"
              />
            </KeepAlive>
          </section>
        </div>

        <!-- Configurações -->
        <article v-else-if="activeNav === 'settings'" class="reborn-card reborn-placeholder-card">
          <header class="reborn-card-header">
            <h2 class="reborn-card-title">{{ t('settings.title') }}</h2>
          </header>
          <p class="reborn-muted-text">
            {{ t('settings.text') }}
          </p>
          <button type="button" class="reborn-btn-primary reborn-btn-inline" @click="refreshSpotify">
            {{ t('settings.syncSpotify') }}
          </button>
        </article>

        <!-- Ajuda -->
        <article v-else class="reborn-card reborn-placeholder-card">
          <header class="reborn-card-header">
            <h2 class="reborn-card-title">{{ t('help.title') }}</h2>
          </header>
          <ul class="reborn-help-list">
            <li>{{ t('help.item1') }}</li>
            <li>{{ t('help.item2') }}</li>
            <li>{{ t('help.item3') }}</li>
            <li>{{ t('help.item4') }}</li>
          </ul>
        </article>
      </div>
    </div>

    <nav class="reborn-mobile-nav" :aria-label="t('nav.mobile')">
      <button
        type="button"
        class="reborn-mobile-nav-item"
        :class="{ 'reborn-mobile-nav-item--active': activeNav === 'profile' }"
        @click="navigateTo('profile')"
      >
        👤
        <span>{{ t('nav.profile') }}</span>
      </button>
      <button
        type="button"
        class="reborn-mobile-nav-item"
        :class="{ 'reborn-mobile-nav-item--active': activeNav === 'contacts' }"
        @click="navigateTo('contacts')"
      >
        👥
        <span>{{ t('nav.contacts') }}</span>
      </button>
      <button
        type="button"
        class="reborn-mobile-nav-item"
        :class="{ 'reborn-mobile-nav-item--active': activeNav === 'chats' }"
        @click="navigateTo('chats')"
      >
        💬
        <span>{{ t('nav.chats') }}</span>
      </button>
      <button
        type="button"
        class="reborn-mobile-nav-item"
        :class="{ 'reborn-mobile-nav-item--active': activeNav === 'settings' }"
        @click="navigateTo('settings')"
      >
        ⚙️
        <span>{{ t('nav.configShort') }}</span>
      </button>
    </nav>

    <ChatTaskbar
      :chats="minimizedChats"
      @restore="restoreChat"
      @close="closeChat"
    />

    <OnlineNotifications
      :notifications="onlineNotifications"
      @dismiss="dismissOnlineNotification"
      @open="openContactFromNotification"
    />
  </main>
</template>
