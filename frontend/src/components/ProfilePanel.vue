<script setup>
import { computed, ref, watch } from 'vue'
import { updateMe } from '../services/auth'
import { resolveMediaUrl } from '../utils/media'

const props = defineProps({
  profile: { type: Object, default: null },
  music: { type: Object, default: null },
})

const emit = defineEmits(['updated'])

const displayName = ref('')
const personalMessage = ref('')
const status = ref('online')
const avatarFile = ref(null)
const avatarPreview = ref('')
const saving = ref(false)
const success = ref('')
const error = ref('')

const statusOptions = [
  { value: 'online', label: 'Online' },
  { value: 'away', label: 'Ausente' },
  { value: 'busy', label: 'Ocupado' },
  { value: 'invisible', label: 'Invisível' },
  { value: 'offline', label: 'Offline' },
]

const avatarSrc = computed(() => {
  if (avatarPreview.value) return avatarPreview.value
  return resolveMediaUrl(props.profile?.avatar_url || props.profile?.avatar || '')
})

function initials(name) {
  const value = name || props.profile?.email || 'MSN'
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}

function statusClass(value) {
  return {
    online: 'text-emerald-700',
    away: 'text-yellow-700',
    busy: 'text-red-700',
    invisible: 'text-slate-500',
    offline: 'text-slate-500',
  }[value] || 'text-slate-500'
}

function statusDot(value) {
  return {
    online: 'bg-lime-400',
    away: 'bg-yellow-400',
    busy: 'bg-red-500',
    invisible: 'bg-slate-400',
    offline: 'bg-slate-400',
  }[value] || 'bg-slate-400'
}

function statusLabel(value) {
  return {
    online: 'online',
    away: 'ausente',
    busy: 'ocupado',
    invisible: 'invisível',
    offline: 'offline',
  }[value] || 'offline'
}

function syncLocalProfile() {
  displayName.value = props.profile?.display_name || ''
  personalMessage.value = props.profile?.personal_message || ''
  status.value = props.profile?.status || 'online'
  avatarFile.value = null
  avatarPreview.value = ''
  success.value = ''
  error.value = ''
}

function handleAvatarChange(event) {
  const file = event.target.files?.[0]
  avatarFile.value = file || null

  if (avatarPreview.value) {
    URL.revokeObjectURL(avatarPreview.value)
    avatarPreview.value = ''
  }

  if (file) {
    avatarPreview.value = URL.createObjectURL(file)
  }
}

async function saveProfile() {
  saving.value = true
  success.value = ''
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('display_name', displayName.value.trim() || props.profile?.username || 'Usuário MSN')
    formData.append('personal_message', personalMessage.value.trim())
    formData.append('status', status.value)

    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }

    const updated = await updateMe(formData)
    emit('updated', updated)
    avatarFile.value = null
    avatarPreview.value = ''
    success.value = 'Perfil atualizado.'
  } catch (err) {
    error.value = err.response?.data?.detail || 'Não foi possível atualizar o perfil.'
  } finally {
    saving.value = false
  }
}

watch(() => props.profile, syncLocalProfile, { immediate: true })
</script>

<template>
  <div class="border-b border-sky-200 bg-gradient-to-b from-sky-50 to-white p-4">
    <div class="flex gap-3">
      <div class="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl border border-sky-500 bg-white shadow-inner">
        <img
          v-if="avatarSrc"
          :src="avatarSrc"
          alt="Foto do perfil"
          class="h-full w-full object-cover"
        />
        <div v-else class="grid h-full w-full place-items-center bg-sky-50 text-xl font-bold text-sky-700">
          {{ initials(displayName) }}
        </div>
      </div>

      <div class="min-w-0 flex-1">
        <div class="truncate text-lg font-bold text-slate-800">
          {{ profile?.display_name || 'Usuário MSN' }}
        </div>
        <div class="flex items-center gap-1 text-sm" :class="statusClass(profile?.status)">
          <span class="inline-block h-2.5 w-2.5 rounded-full" :class="statusDot(profile?.status)"></span>
          {{ statusLabel(profile?.status) }}
        </div>
        <div class="truncate text-sm text-slate-600">
          {{ profile?.personal_message || 'Disponível para conversar' }}
        </div>
        <div v-if="music?.is_playing && music?.track_name" class="mt-1 truncate text-xs font-semibold text-sky-700">
          ♫ {{ music.artist_name }} - {{ music.track_name }}
        </div>
        <div v-else class="mt-1 truncate text-xs text-slate-400">
          Spotify sem música em reprodução
        </div>
      </div>
    </div>

    <form class="mt-4 space-y-2 rounded-lg border border-sky-100 bg-white/80 p-3" @submit.prevent="saveProfile">
      <div class="text-xs font-bold uppercase text-slate-500">Meu perfil</div>

      <input
        v-model="displayName"
        class="w-full rounded border border-sky-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-200"
        maxlength="80"
        placeholder="Nome de exibição"
      />

      <input
        v-model="personalMessage"
        class="w-full rounded border border-sky-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-200"
        maxlength="180"
        placeholder="Mensagem pessoal / subnick"
      />

      <select
        v-model="status"
        class="w-full rounded border border-sky-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-200"
      >
        <option v-for="option in statusOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>

      <label class="block cursor-pointer rounded border border-dashed border-sky-300 bg-sky-50 px-3 py-2 text-center text-xs font-semibold text-sky-800 hover:bg-sky-100">
        Escolher foto de perfil
        <input type="file" accept="image/*" class="hidden" @change="handleAvatarChange" />
      </label>

      <div v-if="error" class="rounded bg-red-50 p-2 text-xs text-red-700">{{ error }}</div>
      <div v-if="success" class="rounded bg-emerald-50 p-2 text-xs text-emerald-700">{{ success }}</div>

      <button
        type="submit"
        class="w-full rounded bg-sky-600 px-3 py-2 text-sm font-bold text-white shadow hover:bg-sky-700 disabled:opacity-60"
        :disabled="saving"
      >
        {{ saving ? 'Salvando...' : 'Salvar perfil' }}
      </button>
    </form>
  </div>
</template>
