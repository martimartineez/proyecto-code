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
            <div style="display:flex; gap:8px; align-items:center;">
              <button class="reload-btn" @click="reloadReseñas" :disabled="loadingReseñas">
                <span v-if="!loadingReseñas">Recargar reseñas</span>
                <span v-else>Cargando...</span>
              </button>

              <button
                class="sort-btn"
                @click="toggleSort"
                :aria-pressed="sortOrder === 'desc' ? 'true' : 'false'"
                :title="sortOrder === 'desc' ? 'Ordenar por fecha: más recientes primero' : 'Ordenar por fecha: más antiguas primero'"
              >
                <span v-if="sortOrder === 'desc'">Orden: ↓ Fecha</span>
                <span v-else>Orden: ↑ Fecha</span>
              </button>
            </div>
          </div>

          <div v-if="loadingReseñas" class="loading">Cargando reseñas...</div>

          <div v-else-if="reseñas.length > 0">
            <div class="review-list">
              <article
                v-for="(reseña, idx) in paginatedResenas"
                :key="reseña.id || idx"
                class="review-card clickable"
                @click="openResena(reseña)"
                role="link"
                tabindex="0"
                @keydown.enter="openResena(reseña)"
              >
                <header class="review-header">
                  <!-- Nuevo estilo: badge circular con color según puntuación -->
                  <div
                    :class="['score-badge', scoreClass(reseña.puntuacion)]"
                    :aria-label="`Puntuación: ${reseña.puntuacion}`"
                  >
                    <div class="score-number">{{ reseña.puntuacion }}</div>
                    <div class="score-label">pts</div>
                  </div>

                  <div class="review-meta">
                    <div class="review-title">{{ reseña.sitio || 'Reseña' }}</div>
                    <div class="review-date">{{ formatDate(reseña.fecha) }}</div>
                  </div>

                  <!-- Estado de la reseña -->
                  <div class="review-status" aria-hidden="false">
                    <span
                      :class="['status-badge', statusClass(reseña)]"
                      :aria-label="statusLabel(reseña)"
                    >
                      {{ statusLabel(reseña) }}
                    </span>
                  </div>
                </header>

                <p class="review-text">  {{ reseña.texto.length > 30 ? reseña.texto.slice(0, 30) + "..." : reseña.texto }}</p>

                <!-- Si la reseña fue rechazada, mostrar motivo detallado -->
                <div v-if="normalizedStatus(reseña) === 'rechazada'" class="rejection-reason" role="note">
                  <strong>Motivo: </strong>
                  <span>{{ rejectionReason(reseña) || 'No especificado' }}</span>
                </div>
              </article>
            </div>

            <!-- Pagination info & controls -->
            <div class="pagination-wrap">
              <div class="pagination-info">
                Mostrando {{ startIndex }}–{{ endIndex }} de {{ reseñas.length }} reseñas
              </div>

              <nav class="pagination">
                <button class="page-btn" @click="prevPage" :disabled="currentPage === 1">‹</button>

                <template v-for="p in pagesToShow" :key="p">
                  <button
                    v-if="p !== -1"
                    class="page-btn"
                    :class="{ active: p === currentPage }"
                    @click="goToPage(p)"
                  >
                    {{ p }}
                  </button>
                  <span v-else class="page-btn ellipsis">…</span>
                </template>

                <button class="page-btn" @click="nextPage" :disabled="currentPage === totalPages">›</button>
              </nav>
            </div>
          </div>

          <div v-else class="empty-state">
            <p>Aún no escribiste reseñas.</p>
          </div>
        </div>

        <div v-else-if="activeTab === 'favoritos'">
          <!-- Controls: order favorites -->
          <div class="reload-row" style="justify-content: flex-end; margin-bottom: 6px;">
            <div style="display:flex; gap:8px; align-items:center;">
              <button
                class="sort-btn"
                @click="toggleFavoritosSort"
                :aria-pressed="favoritosSortOrder === 'desc' ? 'true' : 'false'"
                :title="favoritosSortOrder === 'desc' ? 'Ordenar por fecha: más recientes primero' : 'Ordenar por fecha: más antiguas primero'"
              >
                <span v-if="favoritosSortOrder === 'desc'">Orden: ↓ Fecha</span>
                <span v-else>Orden: ↑ Fecha</span>
              </button>
            </div>
          </div>

          <div v-if="loadingFavoritos" class="loading">Cargando favoritos...</div>
          <div v-else-if="favoritos.length > 0">
            <div class="review-list">
              <article
                v-for="(fav, idx) in paginatedFavoritos"
                :key="fav.id || idx"
                class="review-card clickable"
                @click="openResena(fav)"
                role="link"
                tabindex="0"
                @keydown.enter="openResena(fav)"
              >
                <header class="review-header">
                  <div class="score-badge score-high" aria-label="Favorito">
                    <div class="score-number">★</div>
                    <div class="score-label">Fav</div>
                  </div>
                  <div class="review-meta">
                    <div class="review-title">{{fav.nombre}}</div>
                    <div class="review-date">Agregado: {{ formatDate(extractFavoriteDate(fav)) }}</div>
                  </div>
                </header>
                
              </article>
            </div>

            <!-- Pagination info & controls for favoritos -->
            <div class="pagination-wrap" style="margin-top:12px;">
              <div class="pagination-info">
                Mostrando {{ favoritosStartIndex }}–{{ favoritosEndIndex }} de {{ favoritos.length }} favoritos
              </div>

              <nav class="pagination" aria-label="Paginación favoritos">
                <button class="page-btn" @click="prevFavPage" :disabled="favoritosCurrentPage === 1">‹</button>

                <template v-for="p in pagesToShowFavoritos" :key="p">
                  <button
                    v-if="p !== -1"
                    class="page-btn"
                    :class="{ active: p === favoritosCurrentPage }"
                    @click="goToFavPage(p)"
                  >
                    {{ p }}
                  </button>
                  <span v-else class="page-btn ellipsis">…</span>
                </template>

                <button class="page-btn" @click="nextFavPage" :disabled="favoritosCurrentPage === favoritosTotalPages">›</button>
              </nav>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No tienes sitios favoritos aún.</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { API_BASE_URL } from '@/config';

const router = useRouter();
const route = useRoute();

const profile = ref(null);
const loading = ref(true);
const error = ref("");
const activeTab = ref("reseñas");
const reseñas = ref([]);
const loadingReseñas = ref(false);
const favoritos = ref([]);
const loadingFavoritos = ref(false);
const API_URL = import.meta.env.VITE_API_BASE_URL;


// Pagination
const pageSize = 25;
const currentPage = ref(1);

// Ordenamiento de reseñas
const sortOrder = ref("desc"); // 'desc' (más recientes primero) o 'asc' (más antiguas primero)

// Orden para favoritos: 'desc' (por defecto) o 'asc'
const favoritosSortOrder = ref("desc");

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(reseñas.value.length / pageSize));
});

// Resenas ordenadas según fecha (segura ante fechas faltantes)
const sortedResenas = computed(() => {
  return reseñas.value.slice().sort((a, b) => {
    const da = a && a.fecha ? new Date(a.fecha) : new Date(0);
    const db = b && b.fecha ? new Date(b.fecha) : new Date(0);
    // Para evitar NaN, si la fecha no es válida se usa epoch
    if (sortOrder.value === "asc") {
      return da - db;
    } else {
      return db - da;
    }
  });
});

const paginatedResenas = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedResenas.value.slice(start, start + pageSize);
});

const startIndex = computed(() => {
  if (reseñas.value.length === 0) return 0;
  return (currentPage.value - 1) * pageSize + 1;
});

const endIndex = computed(() => {
  return Math.min(reseñas.value.length, currentPage.value * pageSize);
});

// Generate pages to show (compact when many pages)
const pagesToShow = computed(() => {
  const total = totalPages.value;
  const cur = currentPage.value;
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages = [];
  const left = Math.max(1, cur - 2);
  const right = Math.min(total, cur + 2);

  if (left > 1) {
    pages.push(1);
    if (left > 2) pages.push(-1); // -1 will represent ellipsis
  }

  for (let p = left; p <= right; p++) pages.push(p);

  if (right < total) {
    if (right < total - 1) pages.push(-1);
    pages.push(total);
  }

  return pages;
});

// Paginación para favoritos (paralela a la de reseñas)
const favoritosCurrentPage = ref(1);

// Total de páginas para favoritos
const favoritosTotalPages = computed(() => {
  return Math.max(1, Math.ceil(favoritos.value.length / pageSize));
});

// Favoritos paginados (usa el array ya ordenado: sortedFavoritos)
const paginatedFavoritos = computed(() => {
  const start = (favoritosCurrentPage.value - 1) * pageSize;
  return sortedFavoritos.value.slice(start, start + pageSize);
});

const favoritosStartIndex = computed(() => {
  if (favoritos.value.length === 0) return 0;
  return (favoritosCurrentPage.value - 1) * pageSize + 1;
});

const favoritosEndIndex = computed(() => {
  return Math.min(favoritos.value.length, favoritosCurrentPage.value * pageSize);
});

// Páginas a mostrar para favoritos (compacto, similar a pagesToShow)
const pagesToShowFavoritos = computed(() => {
  const total = favoritosTotalPages.value;
  const cur = favoritosCurrentPage.value;
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages = [];
  const left = Math.max(1, cur - 2);
  const right = Math.min(total, cur + 2);

  if (left > 1) {
    pages.push(1);
    if (left > 2) pages.push(-1); // -1 representa la elipsis
  }

  for (let p = left; p <= right; p++) pages.push(p);

  if (right < total) {
    if (right < total - 1) pages.push(-1);
    pages.push(total);
  }

  return pages;
});

// Helpers
function isEllipsis(p) {
  return p === -1;
}

function goToPage(n) {
  if (n === -1) return;
  currentPage.value = Math.min(Math.max(1, n), totalPages.value);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// Navegación de páginas para favoritos
function goToFavPage(n) {
  if (n === -1) return;
  favoritosCurrentPage.value = Math.min(Math.max(1, n), favoritosTotalPages.value);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function prevFavPage() {
  if (favoritosCurrentPage.value > 1) {
    favoritosCurrentPage.value--;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function nextFavPage() {
  if (favoritosCurrentPage.value < favoritosTotalPages.value) {
    favoritosCurrentPage.value++;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// Toggle de orden (alternar asc/desc)
function toggleSort() {
  sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
  currentPage.value = 1;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Cambia el orden de los favoritos
function toggleFavoritosSort() {
  favoritosSortOrder.value = favoritosSortOrder.value === "asc" ? "desc" : "asc";
  favoritosCurrentPage.value = 1;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Cerrar sesión
async function logout() {
  try {
    await fetch(`${API_URL}/api/logout`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Notificar a otras pestañas/componentes que la autentificación cambió
    try {
      localStorage.setItem('authChanged', String(Date.now()));
    } catch (err) {
      // si localStorage falla, no rompemos el flujo
      console.warn('No se pudo escribir authChanged en localStorage', err);
    }

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
    const res = await fetch(`${API_URL}/api/perfil`, {
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

    // Set initial tab based on route query (if present)
    const tab = String(route.query.tab || '').toLowerCase();
    if (tab === 'favoritos' || tab === 'favorito' || tab === 'favorites') {
      activeTab.value = 'favoritos';
    } else if (tab === 'reseñas' || tab === 'resenas' || tab === 'reviews') {
      activeTab.value = 'reseñas';
    } else {
      // keep default 'reseñas' or you could set to 'favoritos' if you prefer
      activeTab.value = 'reseñas';
    }
  }
});

// Watch for route query changes and update the active tab
watch(
  () => route.query.tab,
  (newTab) => {
    const tab = String(newTab || '').toLowerCase();
    if (tab === 'favoritos' || tab === 'favorito' || tab === 'favorites') {
      activeTab.value = 'favoritos';
    } else if (tab === 'reseñas' || tab === 'resenas' || tab === 'reviews') {
      activeTab.value = 'reseñas';
    }
  }
);

// Función reutilizable para cargar reseñas
async function loadResenas() {
  loadingReseñas.value = true;
  try {
    const res = await fetch(`${API_URL}/api/reseñas_usuario`, {
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
    currentPage.value = 1; // reset to first page whenever reviews load
  } catch (e) {
    console.error(e.message || e);
    reseñas.value = [];
    currentPage.value = 1;
  } finally {
    loadingReseñas.value = false;
  }
}

// Llamada manual desde el botón
function reloadReseñas() {
  loadResenas();
}

// Función reutilizable para cargar favoritos
async function loadFavoritos() {
  loadingFavoritos.value = true;
  try {
    const res = await fetch(`${API_URL}/api/favoritos_usuario`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      throw new Error("Error al cargar los favoritos.");
    }

    const data = await res.json();
    favoritos.value = Array.isArray(data.favoritos) ? data.favoritos : [];
  } catch (e) {
    console.error(e.message || e);
    favoritos.value = [];
  } finally {
    loadingFavoritos.value = false;
  }
}

watch(
  () => activeTab.value,
  (newTab) => {
    if (newTab === "reseñas") {
      loadResenas();
    }
    if (newTab === "favoritos") {
      loadFavoritos();
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

// Nueva helper para asignar clase de color según la puntuación
function scoreClass(p) {
  const n = Number(p);
  if (Number.isNaN(n)) return "score-neutral";
  if (n >= 4.0) return "score-high";      // verde/azulado
  if (n >= 2.5) return "score-medium";    // amarillo/naranja
  return "score-low";                     // rojo
}

// Helper para extraer posible id del objeto reseña/favorito
function extractSiteIdFromResena(r) {
  return (
    r?.sitio.id ||
    null
  );
}

async function openResena(reseña) {
  if (!reseña) return;


  // 1) Si tenemos id directo, navegar al detalle
  const sitioId = extractSiteIdFromResena(reseña);
  if (sitioId) {
    router.push({ name: "detalle-sitio", params: { id: String(sitioId) } });
    return;
  }

  // 2) Fallback: intentar buscar por nombre/nombre de sitio
  const q =
    reseña.sitio ||
    null;

  if (!q) return;

  try {
    const url = new URL(`${API_BASE_URL}/sites`, window.location.origin);
    url.searchParams.set("q", q);
    url.searchParams.set("per_page", "1"); // solo necesitamos el primer match
    const res = await fetch(url.toString());
    if (!res.ok) {
      console.warn("No se pudo buscar el sitio para la reseña/favorito", res.status);
      return;
    }
    const data = await res.json();
    const items = data?.data ?? data?.items ?? data;
    const first = Array.isArray(items) && items.length ? items[0] : null;
    const id = first?.id ?? first?.ID ?? first?._id;
    if (id) {
      router.push({ name: "detalle-sitio", params: { id: String(id) } });
    } else {
      // Último recurso: navegar a la página de búsqueda con el query
      router.push({ name: "sites", query: { q } });
    }
  } catch (err) {
    console.error("Error buscando sitio para reseña/favorito:", err);
  }
}

/* -----------------------
   Nuevas helpers para estado y motivo
   ----------------------- */

// Normaliza posibles campos de estado en diferentes APIs
function getRawStatus(r) {
  return (
    r.estado ??
    null
  );
}

function normalizedStatus(r) {
  const raw = String(getRawStatus(r) ?? "").toLowerCase().trim();
  if (!raw) return "desconocido";
  if (raw.includes("rech")) return "rechazada";
  if (raw.includes("pend")) return "pendiente";
  if (raw.includes("aprob") || raw.includes("acept")) return "aprobada";
  return raw;
}

function statusLabel(r) {
  const s = normalizedStatus(r);
  if (s === "rechazada") return "Rechazada";
  if (s === "pendiente") return "Pendiente";
  if (s === "aprobada") return "Aprobada";
  // Capitaliza genérico
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function statusClass(r) {
  const s = normalizedStatus(r);
  if (s === "rechazada") return "status-rejected";
  if (s === "pendiente") return "status-pending";
  if (s === "aprobada") return "status-approved";
  return "status-unknown";
}

// Extrae posible motivo de rechazo desde distintos campos
function rejectionReason(r) {
  return (
    r?.motivo ??
    ""
  );
}

// Nueva helper para extraer la fecha de agregado de un favorito
function extractFavoriteDate(f) {
  return (
    f?.fecha ??
    null
  );
}

// Lista ordenada de favoritos por fecha (segura ante fechas faltantes/invalidas)
const sortedFavoritos = computed(() => {
  const arr = favoritos.value ? favoritos.value.slice() : [];
  arr.sort((a, b) => {
    const daRaw = extractFavoriteDate(a);
    const dbRaw = extractFavoriteDate(b);

    const da = daRaw ? new Date(daRaw) : new Date(0);
    const db = dbRaw ? new Date(dbRaw) : new Date(0);

    const ta = isNaN(da.getTime()) ? 0 : da.getTime();
    const tb = isNaN(db.getTime()) ? 0 : db.getTime();

    return favoritosSortOrder.value === "asc" ? ta - tb : tb - ta;
  });
  return arr;
});
</script>

<style scoped>
.profile {
  max-width: 720px;
  margin: 48px auto;
  padding: 0 16px;
  text-align: center;
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

/* Sort button */
.sort-btn {
  background: #f8fafc;
  border: 1px solid rgba(15,23,42,0.06);
  color: #0f172a;
  padding: 6px 10px;
  font-size: 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  transition: background 0.14s ease, transform 0.08s ease;
  display: inline-flex;
  align-items: center;
}

.sort-btn:hover {
  background: #eef2ff;
  transform: translateY(-1px);
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
  cursor: pointer; /* Cambiar el cursor a pointer */
}

/* Hacer la tarjeta visualmente clicable */
.review-card.clickable {
  cursor: pointer;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.review-card.clickable:hover,
.review-card.clickable:focus {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(2,6,23,0.12);
  outline: none;
}

/* Header of the review card */
.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Nuevo: Score badge base */
.score-badge {
  width: 64px;
  height: 64px;
  min-width: 64px;
  min-height: 64px;
  max-width: 64px;
  max-height: 64px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(2,6,23,0.08);
  border: 2px solid rgba(255,255,255,0.12);
  transition: transform 160ms ease, box-shadow 160ms ease;
  box-sizing: border-box;
}

.score-badge:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 28px rgba(2,6,23,0.12);
}

.score-number {
  font-size: 1.15rem;
  line-height: 1;
}

/* etiqueta pequeña "pts" */
.score-label {
  font-size: 0.68rem;
  opacity: 0.95;
  margin-top: 2px;
  font-weight: 700;
}

/* Variantes por rango */
.score-high {
  background: linear-gradient(135deg, #10b981, #06b6d4); /* verde -> cyan */
  border-color: rgba(16,185,129,0.18);
}

.score-medium {
  background: linear-gradient(135deg, #f59e0b, #f97316); /* amarillo -> naranja */
  border-color: rgba(245,158,11,0.18);
}

.score-low {
  background: linear-gradient(135deg, #ef4444, #dc2626); /* rojos */
  border-color: rgba(239,68,68,0.18);
}

.score-neutral {
  background: linear-gradient(135deg, #64748b, #475569);
  border-color: rgba(71,85,105,0.18);
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

/* Estado de reseña */
.review-status {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.78rem;
  color: white;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 6px 14px rgba(2,6,23,0.06);
}

/* Variantes */
.status-approved {
  background: linear-gradient(90deg, #16a34a, #059669); /* verde */
}
.status-pending {
  background: linear-gradient(90deg, #f59e0b, #f97316); /* naranja */
}
.status-rejected {
  background: linear-gradient(90deg, #ef4444, #dc2626); /* rojo */
}
.status-unknown {
  background: linear-gradient(90deg, #64748b, #475569); /* gris */
}

/* Motivo de rechazo (detalle) */
.rejection-reason {
  margin-top: 8px;
  padding: 10px;
  border-radius: 8px;
  background: #fff5f6;
  border: 1px solid rgba(239,68,68,0.08);
  color: #7f1d1d;
  font-size: 0.92rem;
  text-align: left;
}

/* Pagination */
.pagination-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}

.pagination-info {
  color: #6b7280;
  font-weight: 600;
  font-size: 0.92rem;
}

.pagination {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

.page-btn {
  min-width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(15,23,42,0.06);
  background: #f8fafc;
  color: #0f172a;
  font-weight: 700;
  cursor: pointer;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 120ms ease, transform 80ms ease;
}

.page-btn:hover:not(:disabled) {
  background: #eef2ff;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.page-btn.active {
  background: #3b82f6;
  color: white;
  border-color: rgba(59,130,246,0.12);
}

/* Ellipsis button look (non-clickable) */
.page-btn.ellipsis {
  background: transparent;
  border: none;
  cursor: default;
  transform: none;
  padding: 0 6px;
  font-weight: 700;
  color: #6b7280;
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
