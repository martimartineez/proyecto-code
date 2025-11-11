<template>
  <main class="login-page">
    <div class="card">
      <h1>Iniciar sesión</h1>
      <p>Accede con tu cuenta de Google</p>

      <!-- Componente provisto por el plugin vue3-google-login -->
      <div class="google-button">
        <GoogleLogin :callback="onGoogleResponse" />
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="user" class="profile">
        <h2>Usuario</h2>
        <p><strong>Nombre:</strong> {{ user.name || user?.given_name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <pre class="payload">{{ user }}</pre>
      </div>

      <router-link to="/" class="back">Volver</router-link>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode' // named export

const router = useRouter()
const user = ref(null)
const error = ref(null)

const onGoogleResponse = (response) => {
  error.value = null

  // el plugin puede devolver diferentes shapes; probamos las opciones más comunes
  const token = response?.credential || response?.token || response?.access_token

  if (!token) {
    error.value = 'No se recibió token desde Google.'
    console.warn('Google response:', response)
    return
  }

  try {
    // jwtDecode devuelve el payload (no valida firma)
    const decoded = jwtDecode(token)

    // Normalizar perfil (ajusta según campos concretos del JWT)
    const profile = {
      name: decoded.name || `${decoded.given_name || ''} ${decoded.family_name || ''}`.trim(),
      given_name: decoded.given_name || null,
      family_name: decoded.family_name || null,
      email: decoded.email || null,
      picture: decoded.picture || null,
      raw: decoded
    }

    // Guardar en localStorage para que la vista /profile lo lea
    localStorage.setItem('user_profile', JSON.stringify(profile))

    // redirigir al perfil
    router.push({ name: 'profile' })
  } catch (e) {
    error.value = 'Error decodificando token: ' + (e?.message || e)
    console.error(e)
  }
}
</script>

<style scoped>
.login-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

/* Texto principal en negro */
.card {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  text-align: center;
  background: white;
  color: #000; /* <- texto en negro */
}

/* Asegurar que enlaces/volver también sean negros */
.back {
  display: inline-block;
  margin-top: 1rem;
  color: #000;
}

/* Mantener el estilo de error en rojo */
.error {
  color: #bf1650;
  margin-top: .5rem;
}

.google-button {
  margin: 1.25rem 0;
}

.profile {
  text-align: left;
  margin-top: 1rem;
  background: #f7f7f8;
  padding: .75rem;
  border-radius: 6px;
  color: #000; /* perfil también en negro */
}
.payload {
  font-size: 0.75rem;
  white-space: pre-wrap;
  max-height: 160px;
  overflow: auto;
}
</style>