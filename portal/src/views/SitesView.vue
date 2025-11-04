<template>
  <section class="page">
    <!-- Toolbar mejorado con mejor espaciado y diseño en desktop -->
    <header class="toolbar">
      <div class="search-container">
        <input
          v-model="state.q"
          class="search"
          type="search"
          placeholder="Buscar sitios (nombre, descripción)"
          @keyup.enter="onSearch"
        />
        <button class="search-btn" @click="onSearch">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </button>
      </div>
      <div class="toolbar-actions">
        <button class="btn btn-filters" @click="toggleFilters">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
          </svg>
          Filtros
        </button>
        <button class="link" @click="onClear">Limpiar</button>
      </div>
    </header>

    <div class="content">
      <!-- Sidebar de filtros con mejor diseño y organización -->
      <aside class="filters" :class="{ open: filtersOpen }">
        <div class="filters-header">
          <h3 class="filters-title">Filtros</h3>
          <button class="close-btn" @click="toggleFilters">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="filters-content">
          <div class="field">
            <label class="field-label">Provincia</label>
            <select v-model.number="state.province" @change="onSearch" class="field-select">
              <option :value="undefined">Todas</option>
              <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Ciudad</label>
            <select v-model="state.city" @change="onSearch" class="field-select">
              <option :value="undefined">Todas</option>
              <option v-for="c in cities" :key="c.id" :value="String(c.id)">{{ c.nombre }}</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Tags</label>
            <div class="tags">
              <label v-for="t in tags" :key="t.id" class="chip">
                <input type="checkbox" :value="String(t.id)" v-model="state.tags" @change="onSearch" class="chip-input"/>
                <span class="chip-label">{{ t.nombre }}</span>
              </label>
            </div>
          </div>

          <div class="field">
            <label class="field-label">Estado</label>
            <select v-model="state.state" @change="onSearch" class="field-select">
              <option value="">Todos</option>
              <option value="Bueno">Bueno</option>
              <option value="Regular">Regular</option>
              <option value="Malo">Malo</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Ordenar por</label>
            <select v-model="state.order_by" @change="onSearch" class="field-select">
              <option value="fecha_registro">Fecha de registro</option>
              <option value="nombre">Nombre</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Orden</label>
            <select v-model="state.order" @change="onSearch" class="field-select">
              <option value="desc">Descendente</option>
              <option value="asc">Ascendente</option>
            </select>
          </div>
        </div>
      </aside>

      <!-- Grid mejorado con mejor espaciado y responsive -->
      <main class="results">
        <div class="results-header">
          <p class="results-count" v-if="!loading && items.length > 0">
            {{ items.length }} sitio{{ items.length !== 1 ? 's' : '' }} encontrado{{ items.length !== 1 ? 's' : '' }}
          </p>
        </div>
        
        <div class="grid">
          <SiteCard v-for="s in items" :key="s.id" :site="s" />
        </div>
        
        <div ref="infiniteEl" class="infinite"></div>
        
        <p v-if="loading" class="loading">
          <span class="spinner"></span>
          Cargando...
        </p>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="!loading && !error && items.length === 0" class="empty">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          No se encontraron resultados
        </p>
      </main>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, reactive, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '@/api/client';
import SiteCard from '@/components/SiteCard.vue';

const route = useRoute();
const router = useRouter();

const provinces = ref([]);
const cities = ref([]);
const tags = ref([]);

const items = ref([]);
const loading = ref(false);
const error = ref(null);
const page = ref(1);
const pages = ref(1);
const per_page = 12;

const filtersOpen = ref(false);
const infiniteEl = ref(null);

const state = reactive({
  q: route.query.q ?? '',
  city: route.query.city ?? undefined,
  province: route.query.province ? Number(route.query.province) : undefined,
  tags: Array.isArray(route.query.tags)
    ? route.query.tags.map(String)
    : route.query.tags ? String(route.query.tags).split(',') : [],
  state: route.query.state ?? '',
  order_by: route.query.order_by ?? 'fecha_registro',
  order: route.query.order ?? 'desc',
});

function updateUrlQuery() {
  const q = {
    ...state,
    tags: state.tags.length ? state.tags : undefined,
    city: state.city || undefined,
    province: state.province ?? undefined,
  };
  router.replace({ query: q });
}

async function fetchFilters() {
  const [prov, tg] = await Promise.all([
    api.listProvinces(),
    api.listTags(),
  ]);
  provinces.value = prov;
  tags.value = tg;
  await fetchCities();
}

async function fetchCities() {
  const cs = await api.listCities({ province: state.province || undefined });
  cities.value = cs;
}

async function fetchPage(reset = false) {
  if (loading.value) return;
  loading.value = true;
  error.value = null;
  try {
    const params = {
      q: state.q || undefined,
      city: state.city || undefined,
      province: state.province ?? undefined,
      tags: state.tags,
      state: state.state || undefined,
      order_by: state.order_by,
      order: state.order,
      page: page.value,
      per_page,
    };
    const res = await api.listSites(params);
    pages.value = res.pages;
    if (reset) items.value = res.items; else items.value = [...items.value, ...res.items];
    updateUrlQuery();
  } catch (err) {
    error.value = err.message || 'Error al cargar sitios';
    console.error('Error fetching sites:', err);
    if (reset) items.value = [];
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  page.value = 1;
  fetchPage(true);
}

function onClear() {
  state.q = '';
  state.city = undefined;
  state.province = undefined;
  state.tags = [];
  state.state = '';
  state.order_by = 'fecha_registro';
  state.order = 'desc';
  page.value = 1;
  fetchPage(true);
}

function toggleFilters() { filtersOpen.value = !filtersOpen.value; }

function setupInfiniteScroll() {
  const io = new IntersectionObserver((entries) => {
    const entry = entries[0];
    if (entry.isIntersecting && page.value < pages.value && !loading.value) {
      page.value += 1;
      fetchPage(false);
    }
  }, { rootMargin: '200px' });
  if (infiniteEl.value) io.observe(infiniteEl.value);
}

// When province changes, reload cities and trigger search
watch(() => state.province, async () => {
  state.city = undefined;
  await fetchCities();
  onSearch();
});

onMounted(async () => {
  await fetchFilters();
  await fetchPage(true);
  setupInfiniteScroll();
});
</script>

<style scoped>
/* Base styles - Mobile First */
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  max-width: 1920px;
  margin: 0 auto;
  min-height: 100vh;
  background-color: #f8fafc; /* Fondo gris claro */
}

/* Toolbar */
.toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-container {
  display: flex;
  width: 100%;
  position: relative;
}

.search {
  flex: 1;
  padding: 12px 48px 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  transition: all 0.2s;
  width: 100%;
  background-color: #fff;
}

.search-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.search-btn:hover {
  color: #3b82f6;
}

.search:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn {
  padding: 10px 16px;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.btn-filters {
  flex: 1;
}

.link {
  background: transparent;
  border: 0;
  color: #3b82f6;
  font-weight: 500;
  cursor: pointer;
  padding: 10px 16px;
  transition: color 0.2s;
}

.link:hover {
  color: #2563eb;
}

/* Content Layout */
.content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  align-items: start;
}

/* Filters Sidebar */
.filters {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
  z-index: 50;
  overflow-y: auto;
}

.filters.open {
  display: block;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 1;
}

.filters-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #111827;
}

.close-btn {
  background: transparent;
  border: 0;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
}

.filters-content {
  padding: 20px;
}

/* Form Fields */
.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.field-label {
  font-weight: 600;
  font-size: 14px;
  color: #374151;
}

.field-input,
.field-select {
  padding: 10px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  background: #ffffff;
}

.field-input:focus,
.field-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Tags */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 999px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.chip:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.chip-input {
  margin: 0;
  cursor: pointer;
}

.chip-input:checked + .chip-label {
  font-weight: 600;
}

.chip:has(.chip-input:checked) {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
}

.chip-label {
  font-size: 14px;
}

/* Results */
.results {
  min-height: 400px;
}

.results-header {
  margin-bottom: 16px;
}

.results-count {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* Grid de cards más anchas con min-width y máximo 3 columnas */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.infinite {
  height: 1px;
}

/* Loading, Empty, Error States */
.loading,
.empty,
.error {
  text-align: center;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading {
  color: #6b7280;
  font-weight: 500;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  color: #9ca3af;
}

.empty svg {
  color: #d1d5db;
}

.error {
  color: #dc2626;
  background: #fee2e2;
  border: 2px solid #fecaca;
  border-radius: 12px;
  font-weight: 500;
}

/* Tablet - 768px */
@media (min-width: 768px) {
  .page {
    padding: 24px;
    gap: 24px;
  }

  .toolbar {
    flex-direction: row;
    align-items: center;
    /* Aumentado padding horizontal para mejor uso del espacio */
    padding: 20px 32px;
  }

  .toolbar-actions {
    flex-shrink: 0;
  }

  .btn-filters {
    flex: 0;
  }

  .content {
    /* Sidebar más angosto (240px) para más ancho en cards */
    grid-template-columns: 240px 1fr;
    gap: 24px;
  }

  .filters {
    display: block;
    position: sticky;
    top: 100px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }

  .filters-header {
    padding: 16px;
  }

  .close-btn {
    display: none;
  }

  .filters-content {
    padding: 16px;
  }

  /* Grid con minmax más flexible para aprovechar el ancho */
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 24px;
  }
}

/* Desktop - 1024px */
@media (min-width: 1024px) {
  .page {
    /* Más padding en desktop */
    padding: 32px;
  }

  .toolbar {
    /* Más padding horizontal en toolbar */
    padding: 24px 40px;
  }

  .content {
    /* Sidebar de 260px en desktop */
    grid-template-columns: 260px 1fr;
    gap: 32px;
  }

  .filters {
    top: 110px;
  }

  /* Grid más flexible, permite 2-3 columnas según el espacio */
  .grid {
    grid-template-columns: repeat(3, minmax(280px, 1fr));
    gap: 28px;
  }
}

/* Large Desktop - 1280px */
@media (min-width: 1280px) {
  /* Grid optimizado para pantallas grandes, permite 3-4 columnas */
  .grid {
    grid-template-columns: repeat(4, minmax(280px, 1fr));
    gap: 32px;
  }
}

/* Extra Large Desktop - 1536px */
@media (min-width: 1536px) {
  .page {
    /* Aún más padding en pantallas muy grandes */
    padding: 40px;
  }

  .content {
    gap: 40px;
  }

  /* Grid que permite hasta 4-5 columnas en pantallas muy grandes */
  .grid {
    grid-template-columns: repeat(5, minmax(280px, 1fr));
    gap: 36px;
  }
}
</style>
