<template>
  <main class="profile">
    <h1>Mi Perfil</h1>

    <div v-if="loading">Cargando...</div>

    <div v-else-if="profile" class="card">
      <img :src="profile.foto" alt="Foto" class="avatar" />

      <h2>{{ profile.nombre }} {{ profile.apellido }}</h2>
      <p>Email: {{ profile.email }}</p>
    </div>

    <div v-else class="error">
      {{ error }}
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue";

const profile = ref(null);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    // extraer token de localStorage.profileData (ejemplo)
    const parsed = JSON.parse(localStorage.getItem('profileData') || '{}')
    const token = parsed?.access_token || parsed?.token || parsed?.id_token

    const res = await fetch("http://localhost:5000/api/perfil", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
    });

    if (!res.ok) {
      throw new Error(`Error ${res.status}: no autorizado o sesión expirada`);
    }

    profile.value = await res.json();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.profile {
  max-width: 400px;
  margin: 40px auto;
  text-align: center;
}

.card {
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.error {
  margin-top: 10px;
  color: red;
}
</style>
