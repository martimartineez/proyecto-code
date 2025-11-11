<template>
  <main class="profile-page">
    <div class="card" v-if="profile">
      <img
        v-if="pictureUrl"
        :src="pictureUrl"
        alt="Foto de perfil"
        class="avatar"
        @error="onImageError"
      />
      <div v-else class="avatar placeholder" aria-hidden="true">
        <!-- placeholder SVG -->
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="24" height="24" rx="4" fill="#e5e7eb"/>
          <path d="M12 12a3 3 0 100-6 3 3 0 000 6zm0 2c-3.33 0-6 1.67-6 4v1h12v-1c0-2.33-2.67-4-6-4z" fill="#9ca3af"/>
        </svg>
      </div>

      <!-- Título principal: preferimos profile.name (full name) -->
      <h1>{{ profile.name || (profile.given_name ? `${profile.given_name} ${profile.family_name || ''}`.trim() : '') }}</h1>

      <!-- Mostrar given / family name por separado si existen -->
      <h2 v-if="profile.given_name || profile.family_name" class="subtitle">
        <span v-if="profile.given_name">{{ profile.given_name }}</span>
        <span v-if="profile.given_name && profile.family_name"> </span>
        <span v-if="profile.family_name">{{ profile.family_name }}</span>
      </h2>

      <p v-if="profile.email"><strong>Email:</strong> {{ profile.email }}</p>

      <div class="controls">
        <button @click="toggleRaw" class="btn small">
          {{ showRaw ? 'Ocultar payload' : 'Mostrar payload' }}
        </button>
        <button @click="logout" class="btn small btn-logout">Cerrar sesión</button>
      </div>

      <pre class="raw" v-if="showRaw && profile.raw">{{ prettyRaw }}</pre>
    </div>

    <div v-else class="empty">
      <p>No hay usuario autenticado. <router-link to="/login">Ir a login</router-link></p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const profile = ref(null)
const showRaw = ref(false)
const imageFailed = ref(false)

// guardamos la URL original y la actual (mutable) para reintentos
const originalImageUrl = ref(null)
const currentImageUrl = ref(null)
const triedOriginal = ref(false)
const triedBlob = ref(false)
let createdObjectUrl = null

onMounted(() => {
  try {
    const raw = localStorage.getItem('user_profile')
    if (!raw) {
      router.replace({ name: 'login' })
      return
    }
    profile.value = JSON.parse(raw)

    // extraer la URL tal cual viene en profile (priorizamos profile.picture)
    const p = profile.value
    originalImageUrl.value = p?.picture || p?.raw?.picture || (p?.raw?.picture?.url) || null

    if (originalImageUrl.value) {
      currentImageUrl.value = enhanceGoogleAvatarSize(originalImageUrl.value)
    }
  } catch (e) {
    console.error('Error reading profile from storage', e)
    router.replace({ name: 'login' })
  }
})

onBeforeUnmount(() => {
  if (createdObjectUrl) {
    URL.revokeObjectURL(createdObjectUrl)
    createdObjectUrl = null
  }
})

// helper para cambiar tamaño si la URL tiene =sNN o =sNN-c
function enhanceGoogleAvatarSize(url) {
  if (!url || typeof url !== 'string') return url
  try {
    return url.replace(/=s\d+(-c)?/i, '=s200-c')
  } catch {
    return url
  }
}

const pictureUrl = computed(() => {
  if (!profile.value || imageFailed.value) return null
  return currentImageUrl.value || null
})

async function tryFetchBlobAndUseOriginal() {
  // intenta descargar como blob y usar object url
  if (!originalImageUrl.value || triedBlob.value) return false
  triedBlob.value = true
  try {
    const res = await fetch(originalImageUrl.value, { mode: 'cors' })
    if (!res.ok) {
      console.warn('fetch image failed', res.status)
      return false
    }
    const blob = await res.blob()
    if (!blob || blob.size === 0) {
      console.warn('fetch returned empty blob')
      return false
    }
    // revocar anterior si existe
    if (createdObjectUrl) {
      URL.revokeObjectURL(createdObjectUrl)
    }
    createdObjectUrl = URL.createObjectURL(blob)
    currentImageUrl.value = createdObjectUrl
    return true
  } catch (err) {
    console.warn('fetch->blob fallback failed', err)
    return false
  }
}

const onImageError = async (evt) => {
  // si falló la primera (mejorada) y no hemos probado la original, reintentamos con original
  if (!triedOriginal.value && originalImageUrl.value && currentImageUrl.value !== originalImageUrl.value) {
    triedOriginal.value = true
    currentImageUrl.value = originalImageUrl.value
    return
  }

  // si ya probamos original y no lo intentamos por blob, probamos fetch->blob
  if (!triedBlob.value && originalImageUrl.value) {
    const ok = await tryFetchBlobAndUseOriginal()
    if (ok) return // la imagen se volverá a cargar con el object URL
  }

  // finalmente marcamos fail y mostramos placeholder
  imageFailed.value = true
}

const logout = () => {
  if (createdObjectUrl) {
    URL.revokeObjectURL(createdObjectUrl)
    createdObjectUrl = null
  }
  localStorage.removeItem('user_profile')
  router.replace({ name: 'login' })
}

const toggleRaw = () => {
  showRaw.value = !showRaw.value
}

const prettyRaw = computed(() => {
  try {
    return JSON.stringify(profile.value.raw ?? profile.value, null, 2)
  } catch (e) {
    return String(profile.value.raw ?? profile.value)
  }
})
</script>

<style scoped>
.profile-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.card {
  width: 100%;
  max-width: 520px;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  text-align: center;
  background: white;
  color: #000;
}
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 999px;
  object-fit: cover;
  margin: 0 auto 1rem;
  display: block;
}
.avatar.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  width: 120px;
  height: 120px;
  border-radius: 999px;
  background: #f3f4f6;
}
.subtitle {
  font-weight: 500;
  margin-top: 0.25rem;
  color: #374151;
}
.controls {
  display: flex;
  gap: .5rem;
  justify-content: center;
  margin-top: 1rem;
}
.btn {
  padding: .45rem .75rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
}
.btn.small { font-size: 0.85rem; padding: .35rem .6rem }
.btn-logout {
  background: #111827;
  color: #fff;
  border-color: transparent;
}
.raw {
  text-align: left;
  background: #f6f6f6;
  padding: .75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  max-height: 220px;
  overflow: auto;
  margin-top: 1rem;
}
.empty { text-align: center }
</style>