<script setup>
import { computed, ref, watch } from 'vue'
import { updateMe } from '../services/auth'
import { resolveMediaUrl } from '../utils/media'

const props = defineProps({
  profile: { type: Object, default: null },
  music: { type: Object, default: null },
  compact: { type: Boolean, default: false },
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
const editing = ref(false)

const statusOptions = [
  { value: 'online', label: 'Disponível' },
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
  const value = name || props.profile?.email || 'R'
  return value
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('') || '🙂'
}

function statusDot(value) {
  return {
    online: 'status-online',
    away: 'status-away',
    busy: 'status-busy',
    invisible: 'status-offline',
    offline: 'status-offline',
  }[value] || 'status-offline'
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
    editing.value = true
  }
}

async function saveProfile() {
  saving.value = true
  success.value = ''
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('display_name', displayName.value.trim() || props.profile?.username || 'Usuário')
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
    editing.value = false
  } catch (err) {
    error.value = err.response?.data?.detail || 'Não foi possível atualizar o perfil.'
  } finally {
    saving.value = false
  }
}

watch(() => props.profile, syncLocalProfile, { immediate: true })
</script>

<template>
  <article class="reborn-card reborn-profile-card">
    <header class="reborn-card-header">
      <h2 class="reborn-card-title">Meu perfil</h2>
      <button
        type="button"
        class="reborn-icon-btn"
        title="Editar perfil"
        @click="editing = !editing"
      >
        ✏️
      </button>
    </header>

    <div class="reborn-profile-avatar-wrap">
      <div class="reborn-profile-avatar">
        <img
          v-if="avatarSrc"
          :src="avatarSrc"
          alt="Foto do perfil"
          class="reborn-profile-avatar-img"
        />
        <span v-else class="reborn-profile-avatar-fallback">{{ initials(displayName) }}</span>
        <span class="reborn-profile-status-dot" :class="statusDot(status)"></span>
      </div>

      <label class="reborn-btn-photo">
        <span aria-hidden="true">📷</span>
        Alterar foto
        <input type="file" accept="image/jpeg,image/png,image/gif" class="sr-only" @change="handleAvatarChange" />
      </label>
      <p class="reborn-photo-hint">JPG, PNG ou GIF. Máx. 5MB</p>
    </div>

    <form class="reborn-profile-form" @submit.prevent="saveProfile">
      <label class="reborn-field">
        <span class="reborn-field-label">Nome</span>
        <input
          v-model="displayName"
          class="reborn-input"
          maxlength="80"
          placeholder="Seu nome"
          @focus="editing = true"
        />
      </label>

      <label class="reborn-field">
        <span class="reborn-field-label">Apelido</span>
        <input
          v-model="personalMessage"
          class="reborn-input"
          maxlength="180"
          placeholder="Mensagem pessoal"
          @focus="editing = true"
        />
      </label>

      <label class="reborn-field">
        <span class="reborn-field-label">Status</span>
        <div class="reborn-select-wrap">
          <span class="reborn-select-dot" :class="statusDot(status)"></span>
          <select v-model="status" class="reborn-select" @focus="editing = true">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </label>

      <div v-if="music?.is_playing && music?.track_name" class="reborn-music-pill">
        <span class="reborn-music-icon" aria-hidden="true">♫</span>
        <span class="reborn-music-text">{{ music.artist_name }} — {{ music.track_name }}</span>
        <span class="reborn-music-eq" aria-hidden="true">
          <span></span><span></span><span></span><span></span>
        </span>
      </div>

      <div v-if="error" class="reborn-alert reborn-alert--error">{{ error }}</div>
      <div v-if="success" class="reborn-alert reborn-alert--success">{{ success }}</div>

      <button type="submit" class="reborn-btn-primary" :disabled="saving">
        <span aria-hidden="true">💾</span>
        {{ saving ? 'Salvando...' : 'Salvar perfil' }}
      </button>
    </form>
  </article>
</template>
