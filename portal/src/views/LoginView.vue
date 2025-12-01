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

      <button @click="router.back()" class="back-button">
         Volver
      </button>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const error = ref(null)
const API_URL = import.meta.env.VITE_API_BASE_URL;


const onGoogleResponse = (response) => {
  const credential = response.credential; 


  fetch(`${API_URL}/api/google`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ token: credential })
  })
    .then(async res => {
      const data = await res.json();

      // Si el backend devuelve un error
      if (!res.ok) {
        error.value = data?.error?.message || data?.message || 'Error en autenticación';
        return;
      }

      // ===============================
      //   REDIRECCIÓN DESPUÉS DEL LOGIN
      // ===============================
      const redirect = localStorage.getItem('redirectAfterLogin');

      if (redirect) {
        localStorage.removeItem('redirectAfterLogin');
        router.push(redirect);
      } else {
        router.push({ name: 'profile' });
      }
      // ===============================

    })
    .catch(err => {
      console.error('Error en fetch:', err);
      error.value = 'Error de red. Intenta nuevamente más tarde.';
    });
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

.back-button {
  margin: 1rem auto;
  display: inline-flex;
  align-items: center;
  justify-content: center; /* <- asegura que el texto esté centrado dentro del botón */
  gap: 0.5rem;
  padding: 0.6rem 1.1rem;
  min-width: 140px;       /* opcional: evita que el botón sea demasiado pequeño */
  background: linear-gradient(90deg, #6c5ce7 0%, #00b894 100%);
  color: #fff;
  border: none;
  border-radius: 999px;
  box-shadow: 0 8px 20px rgba(16,24,40,0.12);
  cursor: pointer;
  transition: transform .12s ease, box-shadow .12s ease, opacity .12s;
  font-weight: 600;
  font-size: 0.95rem;
  text-align: center;     /* redundante con justify-content pero útil como fallback */
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(16,24,40,0.16);
  opacity: 0.98;
}

.back-button:active {
  transform: translateY(0);
  box-shadow: 0 8px 20px rgba(16,24,40,0.12);
}

.back-button:focus {
  outline: 3px solid rgba(108,92,231,0.18);
  outline-offset: 4px;
}
</style>