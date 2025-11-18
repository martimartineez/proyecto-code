<template>
  <main class="profile">
    <h1>Mi Perfil</h1>

    <!-- Botón Logout -->
    <button v-if="profile" class="logout-btn" @click="logout">
      Cerrar sesión
    </button> 

    <!-- Botón Iniciar sesión -->
    <button v-else class="login-btn" @click="irALogin">
      Iniciar sesión
    </button>

    <div v-if="loading" class="loading">Cargando...</div>

    <div v-else-if="profile" class="card">
      <div class="avatar-wrap" aria-hidden="true">
        <img :src="profile.foto" alt="Foto" class="avatar" />
      </div>

      <h2 class="name">{{ profile.nombre }} {{ profile.apellido }}</h2>
      <p class="email">Email: {{ profile.email }}</p>
    </div>

    <div v-else class="error">
      {{ error }}
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const profile = ref(null);
const loading = ref(true);
const error = ref("");

// Cerrar sesión
async function logout() {
  try {
    await fetch("http://localhost:5000/api/logout", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    router.push("/login");
  } catch (e) {
    console.error("Error al cerrar sesión:", e);
  }
}

// Redirigir a /login
function irALogin() {
  router.push("/login");
}

onMounted(async () => {
  try {
    const res = await fetch("http://localhost:5000/api/perfil", {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      throw new Error(`No tienes una sesión abierta o tu sesión expiró. Por favor inicia sesión nuevamente.`);
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
  max-width: 420px;
  margin: 48px auto;
  padding: 0 16px;
  text-align: center;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue",
    Arial;
  color: #222;
}

/* Logout button */
.logout-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background 0.2s ease;
}

.logout-btn:hover {
  background: #dc2626;
}

/* Login button */
.login-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background 0.2s ease;
}

.login-btn:hover {
  background: #2563eb;
}

/* Loading */
.loading {
  margin-top: 20px;
  font-weight: 600;
  color: #555;
}

/* Card */
.card {
  margin-top: 18px;
  padding: 22px;
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(250,250,252,0.9));
  box-shadow: 0 6px 18px rgba(20, 25, 40, 0.08), inset 0 1px 0 rgba(255,255,255,0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

/* Avatar wrapper */
.avatar-wrap {
  width: 136px;
  height: 136px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  background: conic-gradient(from 180deg, #7dd3fc, #8b5cf6, #f472b6, #f59e0b);
  box-shadow: 0 8px 24px rgba(99,102,241,0.12), 0 2px 6px rgba(16,24,40,0.06);
  transition: transform 240ms ease;
}

.avatar-wrap:hover {
  transform: translateY(-4px) scale(1.02);
}

/* Avatar */
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  transition: transform 220ms ease, filter 220ms ease;
}

.avatar:hover {
  transform: scale(1.04);
  filter: saturate(1.05);
}

.name {
  margin: 6px 0 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.2px;
}

.email {
  margin: 0;
  font-size: 0.95rem;
  color: #475569;
  background: linear-gradient(90deg, rgba(71,85,105,0.04), rgba(71,85,105,0));
  padding: 6px 10px;
  border-radius: 8px;
}

.error {
  margin-top: 10px;
  color: #bf1e2e;
  font-weight: 600;
}
</style>
