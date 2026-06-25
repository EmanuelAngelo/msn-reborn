<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  acceptContactRequest,
  createContactRequest,
  listContactRequests,
  rejectContactRequest,
  searchUsers,
} from '../services/msn'

const props = defineProps({
  currentUserId: { type: String, default: '' },
  refreshSignal: { type: Number, default: 0 },
  embedded: { type: Boolean, default: true },
})

const emit = defineEmits(['changed'])

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
    error.value = err.response?.data?.detail || 'Erro ao carregar solicitações.'
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
    error.value = err.response?.data?.detail || 'Erro ao pesquisar usuários.'
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
    success.value = 'Solicitação enviada.'
    await loadRequests()
    emit('changed')
  } catch (err) {
    error.value = err.response?.data?.detail || err.response?.data?.receiver?.[0] || 'Não foi possível enviar a solicitação.'
    await loadRequests()
    await search()
  }
}

async function acceptRequest(id) {
  error.value = ''
  success.value = ''

  try {
    await acceptContactRequest(id)
    success.value = 'Contato adicionado.'
    await loadRequests()
    results.value = []
    emit('changed')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Não foi possível aceitar a solicitação.'
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
    error.value = err.response?.data?.detail || 'Não foi possível recusar a solicitação.'
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
        Adicionar contatos
      </h2>
    </header>

    <form class="reborn-search-form" @submit.prevent="search">
      <div class="reborn-search-input-wrap">
        <span class="reborn-search-icon" aria-hidden="true">🔍</span>
        <input
          v-model="q"
          class="reborn-input reborn-search-input"
          placeholder="Buscar por nome ou e-mail"
        />
      </div>
      <button type="submit" class="reborn-btn-primary reborn-btn-search" :disabled="loading">
        {{ loading ? 'Buscando...' : 'Buscar' }}
      </button>
      <button
        v-if="q || results.length"
        type="button"
        class="reborn-btn-ghost"
        @click="clearSearch"
      >
        Limpar
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
          Adicionar
        </button>
      </div>
    </div>

    <p v-else-if="q.trim() && !loading" class="reborn-muted-text">
      Nenhum usuário disponível para adicionar com essa busca.
    </p>

    <div v-if="pendingReceived.length" class="reborn-requests-block">
      <h3 class="reborn-requests-title">Solicitações recebidas</h3>
      <div
        v-for="request in pendingReceived"
        :key="request.id"
        class="reborn-request-item"
      >
        <div class="reborn-request-name">
          {{ request.sender_profile?.display_name || 'Usuário' }}
        </div>
        <div class="reborn-request-email">{{ request.sender_profile?.email }}</div>
        <div class="reborn-request-actions">
          <button type="button" class="reborn-btn-accept" @click="acceptRequest(request.id)">
            Aceitar
          </button>
          <button type="button" class="reborn-btn-reject" @click="rejectRequest(request.id)">
            Recusar
          </button>
        </div>
      </div>
    </div>

    <div v-if="pendingSent.length" class="reborn-requests-block">
      <h3 class="reborn-requests-title">Solicitações enviadas</h3>
      <div
        v-for="request in pendingSent"
        :key="request.id"
        class="reborn-request-pending"
      >
        Aguardando {{ request.receiver_profile?.display_name || request.receiver_profile?.email || 'usuário' }} aceitar.
      </div>
    </div>
  </article>
</template>
