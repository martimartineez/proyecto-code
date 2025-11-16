<template>
  <main class="profile">
    <h1>Mi Perfil</h1>

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

const profile = ref(null);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const res = await fetch("http://localhost:5000/api/perfil", {
      method: "GET",
      credentials: "include", // necesario para enviar cookie JWT
      headers: {
        "Content-Type": "application/json",
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
  max-width: 420px;
  margin: 48px auto;
  padding: 0 16px;
  text-align: center;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue",
    Arial;
  color: #222;
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
  align-items: center; /* centra la foto y el texto */
  gap: 12px;
}

/* Avatar wrapper with decorative ring */
.avatar-wrap {
  width: 136px;
  height: 136px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px; /* espacio para el anillo */
  background: conic-gradient(from 180deg at 50% 50%, #7dd3fc, #8b5cf6, #f472b6, #f59e0b);
  box-shadow: 0 8px 24px rgba(99,102,241,0.12), 0 2px 6px rgba(16,24,40,0.06);
  transition: transform 240ms ease;
}

/* Slight lift on hover */
.avatar-wrap:hover {
  transform: translateY(-4px) scale(1.02);
}

/* Inner avatar image */
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff; /* separa la imagen del anillo */
  display: block;
  transition: transform 220ms ease, filter 220ms ease;
}

/* Small interaction on avatar */
.avatar:hover {
  transform: scale(1.04);
  filter: saturate(1.05);
}

/* Name and email styling */
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

/* Error */
.error {
  margin-top: 10px;
  color: #bf1e2e;
  font-weight: 600;
}

/* Responsive tweaks */
@media (max-width: 420px) {
  .avatar-wrap {
    width: 120px;
    height: 120px;
    padding: 5px;
  }

  .avatar {
    width: 104px;
    height: 104px;
  }

  .card {
    padding: 18px;
  }
}
</style>
