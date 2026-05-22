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
    await createContactRequest(user.id, 'Me adiciona no MSN Reborn?')
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
  <div class="border-t border-sky-200 bg-white/90 p-3">
    <div class="mb-2 rounded bg-sky-100 px-3 py-1 text-sm font-bold text-sky-900">
      Adicionar contatos
    </div>

    <form class="flex gap-2" @submit.prevent="search">
      <input
        v-model="q"
        class="min-w-0 flex-1 rounded border border-sky-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-300"
        placeholder="Buscar por nome ou e-mail"
      />
      <button class="rounded bg-sky-600 px-3 py-2 text-sm font-bold text-white shadow hover:bg-sky-700">
        Buscar
      </button>
      <button
        v-if="q || results.length"
        type="button"
        class="rounded bg-slate-200 px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-300"
        @click="clearSearch"
      >
        Limpar
      </button>
    </form>

    <div v-if="error" class="mt-2 rounded bg-red-50 p-2 text-xs text-red-700">{{ error }}</div>
    <div v-if="success" class="mt-2 rounded bg-emerald-50 p-2 text-xs text-emerald-700">{{ success }}</div>
    <div v-if="loading" class="mt-2 text-xs text-slate-500">Pesquisando...</div>

    <div v-if="results.length" class="mt-3 space-y-2">
      <div
        v-for="user in results"
        :key="user.id"
        class="flex items-center justify-between rounded border border-slate-200 bg-slate-50 px-3 py-2"
      >
        <div class="min-w-0">
          <div class="truncate text-sm font-bold text-slate-800">
            {{ user.profile?.display_name || user.username }}
          </div>
          <div class="truncate text-xs text-slate-500">{{ user.email }}</div>
        </div>
        <button
          type="button"
          class="rounded bg-yellow-400 px-2 py-1 text-xs font-bold text-yellow-950 hover:bg-yellow-500"
          @click="sendRequest(user)"
        >
          Add
        </button>
      </div>
    </div>

    <div v-else-if="q.trim() && !loading" class="mt-2 text-xs text-slate-500">
      Nenhum usuário disponível para adicionar com essa busca.
    </div>

    <div v-if="pendingReceived.length" class="mt-4">
      <div class="mb-2 text-xs font-bold uppercase text-slate-500">Solicitações recebidas</div>
      <div
        v-for="request in pendingReceived"
        :key="request.id"
        class="mb-2 rounded border border-dashed border-sky-300 bg-sky-50 p-2"
      >
        <div class="text-sm font-semibold text-slate-800">
          {{ request.sender_profile?.display_name || 'Usuário' }}
        </div>
        <div class="mb-2 text-xs text-slate-500">{{ request.sender_profile?.email }}</div>
        <div class="flex gap-2">
          <button class="rounded bg-emerald-600 px-2 py-1 text-xs font-bold text-white" @click="acceptRequest(request.id)">
            Aceitar
          </button>
          <button class="rounded bg-slate-300 px-2 py-1 text-xs font-bold text-slate-800" @click="rejectRequest(request.id)">
            Recusar
          </button>
        </div>
      </div>
    </div>

    <div v-if="pendingSent.length" class="mt-4">
      <div class="mb-2 text-xs font-bold uppercase text-slate-500">Solicitações enviadas</div>
      <div
        v-for="request in pendingSent"
        :key="request.id"
        class="mb-2 rounded border border-slate-200 bg-slate-50 p-2 text-xs text-slate-600"
      >
        Aguardando {{ request.receiver_profile?.display_name || request.receiver_profile?.email || 'usuário' }} aceitar.
      </div>
    </div>
  </div>
</template>
