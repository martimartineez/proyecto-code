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
//import { jwtDecode } from 'jwt-decode' // named export

const router = useRouter()
const user = ref(null)
const error = ref(null)


const onGoogleResponse = (response) => {
  const credential = response.credential; 
  fetch("http://localhost:5000/api/google", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ token: credential })
  })
    .then(async res => {
      const data = await res.json();
      // Si el backend devuelve un error (status != 200)
      if (!res.ok) {
        // intentar mostrar un mensaje útil en la UI
        error.value = data?.error?.message || data?.message || 'Error en autenticación';
        return;
      }

      // Guardar data para que ProfileView la consuma
      // Puedes usar cualquier key; aqui usamos 'profileData'
      try {
        localStorage.setItem('profileData', JSON.stringify(data));
      } catch (e) {
        console.error('No se pudo guardar en localStorage', e);
      }

      // También asignar a la ref local por si quieres mostrar algo antes de redirigir
      user.value = data.user || data;

      // Redirigir a la vista de perfil (router tiene la ruta con name 'profile')
      router.push({ name: 'profile' });
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
</style>