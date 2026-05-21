<script setup>
import { computed, onMounted, ref } from 'vue'
import { acceptContactRequest, createContactRequest, listContactRequests, rejectContactRequest, searchUsers } from '../services/msn'

const props = defineProps({ currentUserId: { type: String, default: '' } })
const emit = defineEmits(['changed'])
const q = ref('')
const results = ref([])
const requests = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const pendingReceived = computed(() => requests.value.filter((item) => item.status === 'pending' && item.receiver === props.currentUserId))

async function loadRequests() {
  requests.value = await listContactRequests()
}

async function search() {
  if (!q.value.trim()) {
    results.value = []
    return
  }
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    results.value = await searchUsers(q.value.trim())
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
    success.value = 'Solicitação enviada.'
    await loadRequests()
  } catch (err) {
    error.value = err.response?.data?.detail || err.response?.data?.receiver?.[0] || 'Não foi possível enviar a solicitação.'
  }
}

async function acceptRequest(id) {
  await acceptContactRequest(id)
  await loadRequests()
  emit('changed')
}

async function rejectRequest(id) {
  await rejectContactRequest(id)
  await loadRequests()
  emit('changed')
}

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
    </form>

    <div v-if="error" class="mt-2 rounded bg-red-50 p-2 text-xs text-red-700">{{ error }}</div>
    <div v-if="success" class="mt-2 rounded bg-emerald-50 p-2 text-xs text-emerald-700">{{ success }}</div>
    <div v-if="loading" class="mt-2 text-xs text-slate-500">Pesquisando...</div>

    <div v-if="results.length" class="mt-3 space-y-2">
      <div v-for="user in results" :key="user.id" class="flex items-center justify-between rounded border border-slate-200 bg-slate-50 px-3 py-2">
        <div class="min-w-0">
          <div class="truncate text-sm font-bold text-slate-800">{{ user.profile?.display_name || user.username }}</div>
          <div class="truncate text-xs text-slate-500">{{ user.email }}</div>
        </div>
        <button class="rounded bg-yellow-400 px-2 py-1 text-xs font-bold text-yellow-950" @click="sendRequest(user)">
          Add
        </button>
      </div>
    </div>

    <div v-if="pendingReceived.length" class="mt-4">
      <div class="mb-2 text-xs font-bold uppercase text-slate-500">Solicitações recebidas</div>
      <div v-for="request in pendingReceived" :key="request.id" class="mb-2 rounded border border-dashed border-sky-300 bg-sky-50 p-2">
        <div class="text-sm font-semibold text-slate-800">{{ request.sender_profile?.display_name || 'Usuário' }}</div>
        <div class="mb-2 text-xs text-slate-500">{{ request.sender_profile?.email }}</div>
        <div class="flex gap-2">
          <button class="rounded bg-emerald-600 px-2 py-1 text-xs font-bold text-white" @click="acceptRequest(request.id)">Aceitar</button>
          <button class="rounded bg-slate-300 px-2 py-1 text-xs font-bold text-slate-800" @click="rejectRequest(request.id)">Recusar</button>
        </div>
      </div>
    </div>
  </div>
</template>
