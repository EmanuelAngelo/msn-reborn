<script setup>
import { computed, ref, watch } from 'vue'
import { updateMe } from '../services/auth'
import { resolveMediaUrl } from '../utils/media'
import { useLocale } from '../composables/useLocale'

const props = defineProps({
  profile: { type: Object, default: null },
  music: { type: Object, default: null },
  compact: { type: Boolean, default: false },
})

const emit = defineEmits(['updated'])

const { t } = useLocale()

const displayName = ref('')
const personalMessage = ref('')
const status = ref('online')
const avatarFile = ref(null)
const avatarPreview = ref('')
const saving = ref(false)
const success = ref('')
const error = ref('')
const editing = ref(false)

const statusOptions = computed(() => [
  { value: 'online', label: t('profile.statusOnline') },
  { value: 'away', label: t('profile.statusAway') },
  { value: 'busy', label: t('profile.statusBusy') },
  { value: 'invisible', label: t('profile.statusInvisible') },
  { value: 'offline', label: t('profile.statusOffline') },
])

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
    success.value = t('profile.updated')
    editing.value = false
  } catch (err) {
    error.value = err.response?.data?.detail || t('profile.updateError')
  } finally {
    saving.value = false
  }
}

watch(() => props.profile, syncLocalProfile, { immediate: true })
</script>

<template>
  <article class="reborn-card reborn-profile-card">
    <header class="reborn-card-header">
      <h2 class="reborn-card-title">{{ t('profile.title') }}</h2>
      <button
        type="button"
        class="reborn-icon-btn"
        :title="t('profile.edit')"
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
        {{ t('profile.changePhoto') }}
        <input type="file" accept="image/jpeg,image/png,image/gif" class="sr-only" @change="handleAvatarChange" />
      </label>
      <p class="reborn-photo-hint">{{ t('profile.photoHint') }}</p>
    </div>

    <form class="reborn-profile-form" @submit.prevent="saveProfile">
      <label class="reborn-field">
        <span class="reborn-field-label">{{ t('profile.name') }}</span>
        <input
          v-model="displayName"
          class="reborn-input"
          maxlength="80"
          :placeholder="t('profile.namePlaceholder')"
          @focus="editing = true"
        />
      </label>

      <label class="reborn-field">
        <span class="reborn-field-label">{{ t('profile.nickname') }}</span>
        <input
          v-model="personalMessage"
          class="reborn-input"
          maxlength="180"
          :placeholder="t('profile.nicknamePlaceholder')"
          @focus="editing = true"
        />
      </label>

      <label class="reborn-field">
        <span class="reborn-field-label">{{ t('profile.status') }}</span>
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
        {{ saving ? t('profile.saving') : t('profile.save') }}
      </button>
    </form>
  </article>
</template>
