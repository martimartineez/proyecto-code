```vue
// filepath: c:\Users\lauti\code\portal\src\views\ProfileView.vue
<template>
  <main class="profile-page">
    <div class="card">
      <h1>Perfil</h1>

      <div v-if="!user">
        <p>No se encontró información de usuario. Por favor inicia sesión.</p>
        <router-link to="/login" class="btn">Ir a iniciar sesión</router-link>
      </div>

      <div v-else class="profile">
        <p><strong>Nombre:</strong> {{ user.name || user.given_name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <pre class="payload">{{ user }}</pre>
        <button @click="logout" class="btn">Cerrar sesión</button>
      </div>

      <router-link to="/" class="back">Volver</router-link>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const router = useRouter()

onMounted(() => {
  const raw = localStorage.getItem('user')
  if (raw) {
    try {
      user.value = JSON.parse(raw)
    } catch {
      user.value = null
    }
  }
})

function logout() {
  localStorage.removeItem('user')
  router.push({ name: 'login' })
}
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
  max-width: 560px;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  text-align: center;
  background: white;
  color: #000;
}
.back, .btn {
  display: inline-block;
  margin-top: 1rem;
  color: #000;
  background: #eee;
  padding: .5rem .75rem;
  border-radius: 6px;
  text-decoration: none;
  border: none;
  cursor: pointer;
}
.profile {
  text-align: left;
  margin-top: 1rem;
  background: #f7f7f8;
  padding: .75rem;
  border-radius: 6px;
  color: #000;
}
.payload {
  font-size: 0.75rem;
  white-space: pre-wrap;
  max-height: 160px;
  overflow: auto;
}
</style>
```