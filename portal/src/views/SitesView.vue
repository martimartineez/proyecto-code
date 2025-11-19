<template>
  <section class="page">
    <!-- Barra superior con búsqueda y acciones -->
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
        <button class="btn btn-filters" @click="onClear">Limpiar</button>
      </div>
    </header>

    <div class="content">
      <!-- Controles de vista -->
      <div class="view-controls">
        <button 
          @click="toggleMap"
          class="btn btn-secondary"
        >
          {{ showMap ? 'Ocultar Mapa' : 'Mostrar Mapa' }}
        </button>
      </div>
      
      

      <!-- Filtros -->
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
            <select v-model="state.province" @change="onSearch" class="field-select">
              <option :value="undefined">Todas</option>
              <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Ciudad</label>
            <select 
              v-model="state.city" 
              @change="onSearch" 
              class="field-select"
              :disabled="!state.province"
              :class="{ 'opacity-50': !state.province }"
            >
              <option :value="undefined">
                {{ state.province ? 'Todas' : 'Seleccione una provincia' }}
              </option>
              <option v-for="c in cities" :key="c.id" :value="String(c.id)">
                {{ c.nombre }}
              </option>
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
              <option value="fechaRegistro">Fecha de registro</option>
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

      <!-- Resultados -->
      <main class="results">
      
        <!-- Mapa -->
      <div v-if="showMap" class="map-container">
        <MapView
          :sites="items"
          :initial-location="searchLocation"
          @location-updated="handleLocationUpdate"
          @select-site="handleSiteSelect"
        />
      </div>

        <div class="results-header">
          <p class="results-count" v-if="!loading && items.length > 0">
            {{ items.length }} sitio{{ items.length !== 1 ? 's' : '' }} encontrado{{ items.length !== 1 ? 's' : '' }}
          </p>
        </div>
        
        <div class="grid">
          <SiteCard 
            v-for="site in items" 
            :key="site.id" 
            :site="site"
            :id="'site-' + site.id"
          />
        </div>
        
        <div ref="infiniteEl" class="infinite"></div>
        
        <!-- Estados de carga y mensajes -->
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
// Vue y Vue Router
import { onMounted, ref, reactive, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// API y componentes
import { api } from '@/api/client';
import SiteCard from '@/components/SiteCard.vue';
import MapView from './MapView.vue';

const restoreScroll = ref(false);

// Constantes
const per_page = 12;

// Inicialización de Vue Router
const route = useRoute();
const router = useRouter();

// Referencias reactivas para datos
const provinces = ref([]);
const cities = ref([]);
const tags = ref([]);
const items = ref([]);

// Estado de la UI
const loading = ref(false);
const error = ref(null);
const filtersOpen = ref(false);
const showMap = ref(route.query.map === 'true');

// Paginación
const page = ref(1);
const pages = ref(1);
const infiniteEl = ref(null);

const searchLocation = ref(null);

// Estado de los filtros
const state = reactive({
  // Búsqueda
  q: route.query.q ?? '',
  
  // Ubicación
  city: route.query.city ?? undefined,
  province: route.query.province ?? undefined,
  latitude: undefined,
  longitude: undefined,
  radius: 2000,
  
  // Filtros
  tags: Array.isArray(route.query.tags)
    ? route.query.tags.map(String)
    : route.query.tags ? String(route.query.tags).split(',') : [],
  state: route.query.state ?? '',
  
  // Ordenamiento
  order_by: route.query.order_by ?? 'nombre',
  order: route.query.order ?? 'asc'
});

/**
 * Actualiza la URL con los parámetros de búsqueda actuales
 */
function updateUrlQuery() {
  const q = {
    ...state,
    tags: state.tags.length ? state.tags : undefined,
    city: state.city || undefined,
    province: state.province ?? undefined,
    map: showMap.value ? 'true' : undefined,
    radius: (state.latitude && state.longitude) ? state.radius : undefined
  };
  
  // Eliminar propiedades undefined del query
  Object.keys(q).forEach(key => q[key] === undefined && delete q[key]);
  
  // Actualizar la ubicación del mapa si hay coordenadas
  if (state.latitude && state.longitude) {
    searchLocation.value = {
      lat: Number(state.latitude),
      lng: Number(state.longitude),
      radius: Number(state.radius)
    };
  }
  
  // Actualizar la URL sin recargar la página
  router.replace({ query: q });
}

function toggleMap() {
  showMap.value = !showMap.value;
  // si se abre el mapa y ya hay coordenadas en el state, 
  // asegurar que searchLocation esté listo
  if (showMap.value && state.latitude && state.longitude) {
    searchLocation.value = {
      lat: Number(state.latitude),
      lng: Number(state.longitude),
      radius: Number(state.radius || 2000)
    };
  }
  updateUrlQuery();
}

/**
 * Obtiene la lista de provincias y tags
 */
async function fetchFilters() {
    try {
      const res = await api.listSites({ page: 1, per_page: 500 });
      const raw = res?.data ?? res?.items ?? [];
      // Provincias únicas
      const provSet = new Set(
        raw.map(it => (
          it.provincia ?? it.province?.nombre ?? it.province?.name ?? it.province ?? null
        )).filter(Boolean)
      );
      provinces.value = Array.from(provSet).map((name) => ({ id: String(name), nombre: String(name) }));
      // Tags únicos (strings u objetos)
      const tagSet = new Set();
      raw.forEach(it => {
        const arr = Array.isArray(it.tags) ? it.tags : [];
        arr.forEach(t => tagSet.add(typeof t === 'string' ? t : (t?.nombre ?? t?.name))); 
      });
      tags.value = Array.from(tagSet).filter(Boolean).map((name, idx) => ({ id: String(name), nombre: String(name) }));
    } catch (e2) {
      console.error('Error al derivar filtros desde /api/sites:', e2);
      error.value = 'Error al cargar los filtros';
    }
    finally {
      await fetchCities();
    }
}

/**
 * Obtiene las ciudades de la provincia seleccionada
 */
async function fetchCities() {
  if (!state.province) {
    cities.value = [];
    return;
  }
  try {
    const cs = await api.listCities({ province: state.province });
    const normCities = Array.isArray(cs) ? cs.map((c) => ({
      id: c?.id ?? String(c?.nombre ?? c?.name ?? c),
      nombre: c?.nombre ?? c?.name ?? String(c),
    })) : [];
    cities.value = normCities;
    if (!cities.value.length) {
      throw new Error('Cities empty, derive from /api/sites');
    }
  } catch (err) {
    // Fallback: derivar ciudades desde /api/sites filtrando por provincia seleccionada
    console.warn('Fallo /filters/cities, derivando ciudades desde /api/sites:', err);
    try {
      const provinceName = provinces.value.find(p => String(p.id) === String(state.province))?.nombre || state.province;
      const res = await api.listSites({ province: provinceName, page: 1, per_page: 25 });
      const raw = res?.data ?? res?.items ?? [];
      const citySet = new Set(
        raw.map(it => (
          it.ciudad ?? it.city?.nombre ?? it.city?.name ?? it.city ?? null
        )).filter(Boolean)
      );
      cities.value = Array.from(citySet).map((name) => ({ id: String(name), nombre: String(name) }));
    } catch (e2) {
      console.error('Error al derivar ciudades desde /api/sites:', e2);
      error.value = 'Error al cargar las ciudades';
    }
  }
}

/**
 * Obtiene una página de resultados
 * @param {boolean} reset - Si es true, reinicia la lista de items
 */
async function fetchPage(reset = false) {
  if (loading.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    // Mapear IDs seleccionados a nombres (el backend de /api/sites espera nombres)
    const provinceName = state.province != null
      ? (provinces.value.find(p => p.id === state.province)?.nombre)
      : undefined;
    const cityName = state.city != null
      ? (cities.value.find(c => String(c.id) === String(state.city))?.nombre)
      : undefined;
    const tagNames = (state.tags || [])
      .map(id => tags.value.find(t => String(t.id) === String(id))?.nombre)
      .filter(Boolean);

    const params = {
      // Búsqueda: usar 'q' para que el backend busque por nombre OR descripción
      q: state.q || undefined,
      // Ubicación (API espera km)
      city: cityName || undefined,
      province: provinceName || undefined,
      lat: state.latitude,
      long: state.longitude,
      radius: state.radius != null ? state.radius / 1000 : undefined,
      
      // Filtros
      tags: tagNames.length ? tagNames : undefined,
      state: state.state || undefined,
      
      // Ordenamiento (si aplica en backend)
      order_by: state.order_by,
      order: state.order,
      
      // Paginación
      page: page.value,
      per_page
    };

    const res = await api.listSites(params);
    const raw = res?.data ?? res?.items ?? [];
    // Normalizar a la forma usada en las cards y mapa
    const data = raw.map((it) => {
      const nombre = it.nombre ?? it.name ?? '';
      const ciudad = it.ciudad ?? it.city?.nombre ?? it.city?.name ?? it.city ?? '';
      const provincia = it.provincia ?? it.province?.nombre ?? it.province?.name ?? it.province ?? '';
      const estado = it.estado ?? it.estadoConservacion ?? it.state_of_conservation ?? '';
      const latitude = it.latitud ?? it.latitude ?? it.lat ?? null;
      const longitude = it.longitud ?? it.longitude ?? it.long ?? null;
      const cover_image = it.cover_image ?? it.coverImage ?? null;
      const fechaRegistro = it.fechaRegistro ?? it.registration_date ?? null;
      let tagsArr = it.tags ?? [];
      if (Array.isArray(tagsArr)) {
        // si vienen objetos, extraer nombre/name
        tagsArr = tagsArr.map((t) => (typeof t === 'string' ? t : (t?.nombre ?? t?.name))).filter(Boolean);
      }
      return {
        ...it,
        nombre,
        ciudad,
        provincia,
        estado,
        latitude,
        longitude,
        cover_image,
        fechaRegistro,
        tags: tagsArr,
      };
    });
    const meta = res?.meta;
    pages.value = meta ? Math.max(1, Math.ceil((meta.total || 0) / (meta.per_page || per_page))) : (res?.pages || 1);
    
    // Actualizar la lista de items
    if (reset) {
      items.value = data;
    } else {
      items.value = [...items.value, ...data];
    }
    
    updateUrlQuery();
  } catch (err) {
    error.value = err.message || 'Error al cargar sitios';
    console.error('Error al cargar sitios:', err);
    if (reset) items.value = [];
  } finally {
    loading.value = false;
  }
}

/**
 * Ejecuta una nueva búsqueda
 */
function onSearch() {
  page.value = 1;
  fetchPage(true);
}

/**
 * Limpia todos los filtros
 */
function onClear() {
  // Restablecer el estado
  state.q = '';
  state.city = undefined;
  state.province = undefined;
  state.tags = [];
  state.state = '';
  state.order_by = 'nombre';
  state.order = 'asc';
  state.latitude = undefined;
  state.longitude = undefined;
  state.radius = 2000;
  searchLocation.value = null;
  showMap.value = false;

  // Reiniciar paginación y cargar resultados
  page.value = 1;
  fetchPage(true);
}

/**
 * Muestra/oculta el panel de filtros
 */
function toggleFilters() {
  filtersOpen.value = !filtersOpen.value;
}

/**
 * Actualiza la ubicación de búsqueda desde el mapa
 * @param {Object|null} location - Objeto con lat, lng y radius, o null para limpiar
 */
function handleLocationUpdate(location) {
  if (!location) {
    state.latitude = undefined;
    state.longitude = undefined;
    state.radius = 2000; 
  } else {
    state.latitude = location.latitude || location.lat;
    state.longitude = location.longitude || location.lng;
    state.radius = location.radius || 2000;
  }
  
  updateUrlQuery();
  
  page.value = 1;
  fetchPage(true);
}

/**
 * Maneja la selección de un sitio en el mapa
 * @param {Object} site - Sitio seleccionado
 */
function handleSiteSelect(site) {
  // Guardar la posición de desplazamiento actual
  sessionStorage.setItem('list-scroll', String(window.scrollY));
}

let io; // Referencia al IntersectionObserver

/**
 * Configuración del scroll infinito
 */
function setupInfiniteScroll() {
  if (io) io.disconnect();

  io = new IntersectionObserver((entries) => {
    const entry = entries[0];
    if (entry.isIntersecting && page.value < pages.value && !loading.value) {
      page.value += 1;
      fetchPage(false);
    }
  }, { rootMargin: '200px' });

  if (infiniteEl.value) io.observe(infiniteEl.value);
}

// Recargar ciudades cuando cambia la provincia
watch(() => state.province, async (newVal) => {
  state.city = undefined; 
  
  if (newVal) {
    await fetchCities();
  } else {
    cities.value = [];
  }
  
  onSearch();
});

// Configurar scroll infinito cuando cambian los items
watch(items, async () => {
  if (infiniteEl.value) setupInfiniteScroll();
});



// Función para restaurar el scroll
const restoreScrollPosition = () => {
  const savedPosition = sessionStorage.getItem('list-scroll');
  if (savedPosition) {
    nextTick(() => {
      window.scrollTo({ top: Number(savedPosition), behavior: 'auto' });
      // Limpiar la posición guardada después de restaurarla
      sessionStorage.removeItem('list-scroll');
    });
  }
};

onMounted(async () => {
  // 1. Recuperar estado del mapa (Abierto/Cerrado)
  if (route.query.map === 'true') {
    showMap.value = true;
  }

  // 2. Recuperar Ubicación y Radio
  if (route.query.latitude && route.query.longitude) {
    // Parsear a números (Float para lat/long, Int o Float para radio)
    const lat = parseFloat(route.query.latitude);
    const lng = parseFloat(route.query.longitude);
    const rad = route.query.radius ? parseFloat(route.query.radius) : 2000;

    // Actualizar el estado interno
    state.latitude = lat;
    state.longitude = lng;
    state.radius = rad;

    searchLocation.value = {
      lat: lat,
      lng: lng,
      latitude: lat, 
      longitude: lng,
      radius: rad 
    };
  }

  // 3. Cargas iniciales
  try {
    await fetchFilters();
    await fetchPage(true);
    setupInfiniteScroll();
    restoreScrollPosition();
  } catch (err) {
    console.error('Error al inicializar:', err);
  }
});

</script>

<style scoped>
/* Estilos para el mapa */
.map-toggle {
  margin-bottom: 16px;
  text-align: right;
}

.map-container {
  height: 400px;
  width: 100%;
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Estilo para el sitio seleccionado */
.site-card.selected {
  box-shadow: 0 0 0 2px #3b82f6;
  transform: translateY(-2px);
  transition: all 0.2s ease;
}

/* Ajustes responsivos */
@media (min-width: 1024px) {
  .map-container {
    height: 500px;
  }
}

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

/* Asegurar que los botones secundarios muestren texto legible y no se compriman */
.btn-secondary {
  color: #111827; /* texto oscuro */
  background: #d0befa;
  border-color: #e5e7eb;
  min-width: 120px; /* evitar que el botón se encoja y oculte el texto */
  text-align: center;
}

.btn-secondary svg {
  margin-right: 8px;
  vertical-align: middle;
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
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  font-size: 14px;
  color: #374151;
}

.chip:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.chip-input {
  margin: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.chip-input:checked + .chip-label {
  font-weight: 500;
}

.chip:has(.chip-input:checked) {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
}

.chip-label {
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
}

/* Resultados */
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
    padding: 20px 32px;
  }

  .toolbar-actions {
    flex-shrink: 0;
  }

  .btn-filters {
    flex: 0;
  }

  /* Colocar la barra de filtros a la izquierda y el contenido principal a la derecha */
  .content {
    grid-template-columns: 240px 1fr;
    gap: 24px;
  }

  /* Forzar que la barra de vista y el mapa ocupen ambas columnas (encabezado y mapa full-width) */
  .view-controls,
  .map-container {
    grid-column: 1 / -1;
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
    /* Ubicar la sidebar en la primera columna (izquierda) */
    grid-column: 1;
    align-self: start;
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

  /* Resultados a la derecha (columna 2) */
  .results {
    grid-column: 2;
  }

  .grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 24px;
  }
}

/* Desktop - 1024px */
@media (min-width: 1024px) {
  .page {
    padding: 32px;
  }

  .toolbar {
    padding: 24px 40px;
  }

  .content {
    /* Sidebar de filtros a la izquierda (260px) */
    grid-template-columns: 260px 1fr;
    gap: 32px;
  }

  .filters {
    top: 110px;
    grid-column: 1;
  }

  .grid {
    grid-template-columns: repeat(3, minmax(280px, 1fr));
    gap: 28px;
  }
}

/* Large Desktop - 1280px */
@media (min-width: 1280px) {
  /* Mantener 3 columnas en desktop grande */
  .grid {
    grid-template-columns: repeat(3, minmax(280px, 1fr));
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

  /* Forzar 3 columnas también en pantallas extra grandes */
  .grid {
    grid-template-columns: repeat(3, minmax(280px, 1fr));
    gap: 36px;
  }
}
</style>
