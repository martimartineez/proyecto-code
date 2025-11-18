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

    <!-- Tarjeta de Reseñas y Favoritos -->
    <div v-if="profile" class="tabs-card">
      <div class="tabs">
        <button
          :class="{ active: activeTab === 'reseñas' }"
          @click="activeTab = 'reseñas'"
        >
          Reseñas
        </button>
        <button
          :class="{ active: activeTab === 'favoritos' }"
          @click="activeTab = 'favoritos'"
        >
          Favoritos
        </button>
      </div>
      <div class="tab-content">
        <div v-if="activeTab === 'reseñas'">
          <!-- Botón de recarga -->
          <div class="reload-row">
            <button class="reload-btn" @click="reloadReseñas" :disabled="loadingReseñas">
              <span v-if="!loadingReseñas">Recargar reseñas</span>
              <span v-else>Cargando...</span>
            </button>
          </div>

          <div v-if="loadingReseñas" class="loading">Cargando reseñas...</div>
          <div v-else-if="reseñas.length > 0">
            <div class="review-list">
              <article
                v-for="(reseña, idx) in reseñas"
                :key="reseña.id || idx"
                class="review-card"
              >
                <header class="review-header">
                  <div class="score-badge" :aria-label="`Puntuación: ${reseña.puntuacion}`">
                    <strong class="score-number">{{ reseña.puntuacion }}</strong>
                    <span class="score-stars" aria-hidden="true">{{ stars(reseña.puntuacion) }}</span>
                  </div>
                  <div class="review-meta">
                    <div class="review-title">{{ reseña.titulo || 'Reseña' }}</div>
                    <div class="review-date">{{ formatDate(reseña.fecha) }}</div>
                  </div>
                </header>

                <p class="review-text">{{ reseña.texto }}</p>
              </article>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>Aún no escribiste reseñas.</p>
          </div>
        </div>
        <div v-else-if="activeTab === 'favoritos'">
          <p>Aquí se mostrarán los favoritos del usuario.</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const profile = ref(null);
const loading = ref(true);
const error = ref("");
const activeTab = ref("reseñas");
const reseñas = ref([]);
const loadingReseñas = ref(false);

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

// Función reutilizable para cargar reseñas
async function loadResenas() {
  loadingReseñas.value = true;
  try {
    const res = await fetch("http://localhost:5000/api/reseñas_usuario", {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      throw new Error("Error al cargar las reseñas.");
    }

    const data = await res.json();
    reseñas.value = Array.isArray(data.reseñas) ? data.reseñas : [];
  } catch (e) {
    console.error(e.message || e);
    reseñas.value = [];
  } finally {
    loadingReseñas.value = false;
  }
}

// Llamada manual desde el botón
function reloadReseñas() {
  loadResenas();
}

watch(
  () => activeTab.value,
  (newTab) => {
    if (newTab === "reseñas") {
      loadResenas();
    }
  },
  { immediate: true }
);

// Helpers para mostrar fecha y estrellas
function formatDate(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("es-AR", { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
}

function stars(puntuacion) {
  const n = Math.max(0, Math.min(5, Math.round(Number(puntuacion) || 0)));
  return "★".repeat(n) + "☆".repeat(5 - n);
}
</script>

<style scoped>
.profile {
  max-width: 720px;
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
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,252,0.95));
  box-shadow: 0 8px 28px rgba(20, 25, 40, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

/* Tabs Card */
.tabs-card {
  margin-top: 24px;
  padding: 18px;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 6px 20px rgba(2,6,23,0.06);
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.tabs button {
  background: #f3f4f6;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.12s ease;
}

.tabs button.active {
  background: #3b82f6;
  color: white;
  transform: translateY(-2px);
}

.tabs button:hover {
  background: #e2e8f0;
}

/* Tab content */
.tab-content {
  text-align: left;
  font-size: 1rem;
  color: #374151;
}

/* Recargar reseñas row/button */
.reload-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.reload-btn {
  background: #f1f5f9;
  border: 1px solid rgba(15,23,42,0.06);
  color: #0f172a;
  padding: 6px 10px;
  font-size: 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  transition: background 0.14s ease, transform 0.08s ease;
}

.reload-btn:hover {
  background: #eef2ff;
  transform: translateY(-1px);
}

.reload-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

/* Review list and cards */
.review-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-top: 8px;
}

/* Each review card */
.review-card {
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  border: 1px solid rgba(15, 23, 42, 0.04);
  padding: 14px;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(3,10,35,0.04);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Header of the review card */
.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Score badge */
.score-badge {
  min-width: 64px;
  height: 64px;
  border-radius: 12px;
  background: linear-gradient(135deg, #06b6d4, #7c3aed);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(99,102,241,0.12);
  font-weight: 700;
}

.score-number {
  font-size: 1.15rem;
  line-height: 1;
}

.score-stars {
  margin-top: 2px;
  font-size: 0.82rem;
  opacity: 0.95;
  letter-spacing: 1px;
}

/* Meta (title + date) */
.review-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.review-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.98rem;
}

.review-date {
  font-size: 0.82rem;
  color: #6b7280;
}

/* Review text */
.review-text {
  margin: 0;
  color: #374151;
  line-height: 1.5;
  font-size: 0.95rem;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Empty state for reviews */
.empty-state {
  text-align: center;
  padding: 18px;
  color: #6b7280;
  font-weight: 600;
  border-radius: 10px;
  background: #fbfbfc;
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
  text-align: center;
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

/* Responsive tweaks */
@media (min-width: 720px) {
  .review-list {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
