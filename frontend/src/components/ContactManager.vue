<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  acceptContactRequest,
  createContactRequest,
  listContactRequests,
  rejectContactRequest,
  searchUsers,
} from '../services/msn'
import { useLocale } from '../composables/useLocale'

const props = defineProps({
  currentUserId: { type: String, default: '' },
  refreshSignal: { type: Number, default: 0 },
  embedded: { type: Boolean, default: true },
})

const emit = defineEmits(['changed'])

const { t } = useLocale()

const q = ref('')
const results = ref([])
const requests = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const sentUserIds = ref(new Set())

const pendingReceived = computed(() =>
  requests.value.filter((item) => item.status === 'pending' && item.receiver === props.currentUserId)
)

const pendingSent = computed(() =>
  requests.value.filter((item) => item.status === 'pending' && item.sender === props.currentUserId)
)

async function loadRequests() {
  try {
    requests.value = await listContactRequests()
  } catch (err) {
    error.value = err.response?.data?.detail || t('addContacts.loadError')
  }
}

function clearSearch() {
  q.value = ''
  results.value = []
  error.value = ''
  success.value = ''
}

async function search() {
  const term = q.value.trim()

  if (!term) {
    results.value = []
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const users = await searchUsers(term)
    results.value = users.filter((user) => !sentUserIds.value.has(user.id))
  } catch (err) {
    error.value = err.response?.data?.detail || t('addContacts.searchError')
  } finally {
    loading.value = false
  }
}

async function sendRequest(user) {
  error.value = ''
  success.value = ''

  try {
    await createContactRequest(user.id, 'Me adiciona no Reborn?')
    sentUserIds.value = new Set([...sentUserIds.value, user.id])
    results.value = results.value.filter((item) => item.id !== user.id)
    success.value = t('addContacts.sentSuccess')
    await loadRequests()
    emit('changed')
  } catch (err) {
    error.value = err.response?.data?.detail || err.response?.data?.receiver?.[0] || t('addContacts.sendError')
    await loadRequests()
    await search()
  }
}

async function acceptRequest(id) {
  error.value = ''
  success.value = ''

  try {
    await acceptContactRequest(id)
    success.value = t('addContacts.addedSuccess')
    await loadRequests()
    results.value = []
    emit('changed')
  } catch (err) {
    error.value = err.response?.data?.detail || t('addContacts.acceptError')
  }
}

async function rejectRequest(id) {
  error.value = ''
  success.value = ''

  try {
    await rejectContactRequest(id)
    await loadRequests()
    emit('changed')
  } catch (err) {
    error.value = err.response?.data?.detail || t('addContacts.rejectError')
  }
}

watch(
  () => props.refreshSignal,
  async () => {
    await loadRequests()
    if (q.value.trim()) await search()
  }
)

onMounted(loadRequests)
</script>

<template>
  <article class="reborn-card reborn-add-contacts-card" :class="{ 'reborn-card--flat': !embedded }">
    <header v-if="embedded" class="reborn-card-header">
      <h2 class="reborn-card-title">
        <span aria-hidden="true">➕</span>
        {{ t('addContacts.title') }}
      </h2>
    </header>

    <form class="reborn-search-form" @submit.prevent="search">
      <div class="reborn-search-input-wrap">
        <span class="reborn-search-icon" aria-hidden="true">🔍</span>
        <input
          v-model="q"
          class="reborn-input reborn-search-input"
          :placeholder="t('addContacts.searchPlaceholder')"
        />
      </div>
      <button type="submit" class="reborn-btn-primary reborn-btn-search" :disabled="loading">
        {{ loading ? t('addContacts.searching') : t('addContacts.search') }}
      </button>
      <button
        v-if="q || results.length"
        type="button"
        class="reborn-btn-ghost"
        @click="clearSearch"
      >
        {{ t('addContacts.clear') }}
      </button>
    </form>

    <div v-if="error" class="reborn-alert reborn-alert--error">{{ error }}</div>
    <div v-if="success" class="reborn-alert reborn-alert--success">{{ success }}</div>

    <div v-if="results.length" class="reborn-search-results">
      <div
        v-for="user in results"
        :key="user.id"
        class="reborn-search-result"
      >
        <div class="reborn-search-result-info">
          <div class="reborn-search-result-name">
            {{ user.profile?.display_name || user.username }}
          </div>
          <div class="reborn-search-result-email">{{ user.email }}</div>
        </div>
        <button type="button" class="reborn-btn-add" @click="sendRequest(user)">
          {{ t('addContacts.add') }}
        </button>
      </div>
    </div>

    <p v-else-if="q.trim() && !loading" class="reborn-muted-text">
      {{ t('addContacts.noResults') }}
    </p>

    <div v-if="pendingReceived.length" class="reborn-requests-block">
      <h3 class="reborn-requests-title">{{ t('addContacts.received') }}</h3>
      <div
        v-for="request in pendingReceived"
        :key="request.id"
        class="reborn-request-item"
      >
        <div class="reborn-request-name">
          {{ request.sender_profile?.display_name || t('addContacts.user') }}
        </div>
        <div class="reborn-request-email">{{ request.sender_profile?.email }}</div>
        <div class="reborn-request-actions">
          <button type="button" class="reborn-btn-accept" @click="acceptRequest(request.id)">
            {{ t('addContacts.accept') }}
          </button>
          <button type="button" class="reborn-btn-reject" @click="rejectRequest(request.id)">
            {{ t('addContacts.reject') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="pendingSent.length" class="reborn-requests-block">
      <h3 class="reborn-requests-title">{{ t('addContacts.sent') }}</h3>
      <div
        v-for="request in pendingSent"
        :key="request.id"
        class="reborn-request-pending"
      >
        {{
          t('addContacts.waiting', {
            name: request.receiver_profile?.display_name || request.receiver_profile?.email || t('addContacts.user'),
          })
        }}
      </div>
    </div>
  </article>
</template>
