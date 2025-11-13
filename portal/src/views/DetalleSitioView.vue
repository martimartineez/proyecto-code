<template>
  <main v-if="site && !site.error" class="site-detail-container">
    <button @click="router.back()" class="back-button">
      &larr; Volver al Listado
    </button>
    
    <section class="info-and-media">
      <div style="height: 200px; background-color: #f0f0f0; display: grid; place-items: center;">
        [Galería de Imágenes]
      </div>
      
      <div class="header-info">
        <h1>{{ site.name }}</h1>
        <p class="location">{{ site.city }}, {{ site.province }}</p>
        
        <span :class="['status-chip', getConservationClass(site.state_of_conservation)]">
          {{ site.state_of_conservation }}
        </span>
      </div>
      
      <div class="tag-placeholder">Tags: {{ site.tags?.map(t => t.name).join(', ') || 'N/A' }}</div>
    </section>

    <hr>
    
    <section>
        <h2>Descripción</h2>
        <p>{{ site.description.substring(0, 300) }}...</p>
        <p style="font-style: italic;">[Descripción Plegable: usa description]</p>
    </section>


    <section class="map-section">
      <h2>Ubicación</h2>
      <SiteMap 
        :lat="site.lat"         :lon="site.long"        :title="site.name" 
        :description="site.short_description" />
    </section>

    <hr>

    <section class="reviews-section">
      <h2>Calificaciones y Reseñas</h2>
      <div class="review-summary-actions">
        <p>Calificación: {{ site.calificacion_promedio }} ({{ site.cantidad_reseñas }} reseñas)</p>
        
        <div class="action-buttons">
            <button class="action-btn">Escribir Reseña (Login requerido)</button>
            
            <button class="action-btn">Marcar Favorito</button>
        </div>
      </div>

      <div style="margin-top: 1rem; border: 1px dashed #ccc; padding: 10px;">
        [Listado de Reseñas Paginadas: se requiere GET /sites/{id}/reviews]
      </div>
    </section>

  </main>
  
  <div v-else-if="site && site.error" class="error-state">
    Error: {{ site.error }}
  </div>

  <div v-else class="loading-state">
    Cargando detalles del sitio histórico...
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SiteMap from '@/components/SiteMap.vue';


const route = useRoute();
const router = useRouter();
const site = ref(null); 
const isAuthenticated = ref(false); // Mantener para futura implementación de JWT

// Función para mapear el estado de conservación a una clase CSS
const getConservationClass = (estado) => {
    if (!estado) return 'unknown';
    const lowerCaseEstado = estado.toLowerCase();
    
    // Basado en los choices de la API: 'excelente', 'bueno', 'regular', 'malo'
    if (lowerCaseEstado.includes('bueno')) return 'good';
    if (lowerCaseEstado.includes('regular')) return 'fair';
    if (lowerCaseEstado.includes('malo')) return 'poor';
    
    return 'neutral';
}

const fetchSiteData = async () => {
  const siteId = route.params.id; 
  
  // 1. Definición de la URL base usando la convención de Vite
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 

  try {
    console.log(`Intentando cargar detalles del sitio ID: ${siteId} desde la API: ${baseUrl}/api/sites/${siteId}`);
    
    // 2. Solicitud GET al endpoint de la API
    const response = await fetch(`${baseUrl}/api/sites/${siteId}`);
    
    // 3. Manejo de errores de HTTP (incluyendo 404, confirmado en sites.py)
    if (!response.ok) {
      if (response.status === 404) {
          site.value = { error: 'El sitio no existe (Error 404).' };
          return; 
      }
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    // 4. Convertir la respuesta a JSON
    let data = await response.json();
    
    // 5. Mapeo temporal de campos faltantes (Calificación y conteo de reseñas)
    // Estos campos deberían venir de una llamada separada (GET /sites/{id}/reviews) o del to_dict() del modelo.
    // Los inicializamos para evitar que el template falle.
    data.calificacion_promedio = data.rating_avg || 'N/A';
    data.cantidad_reseñas = data.reviews_count || 0;

    // 6. Asignar los datos reales al estado reactivo
    site.value = data; 

  } catch (error) {
    console.error("Error al cargar detalles del sitio:", error);
    site.value = { error: 'No se pudo contactar al servidor de la API o hubo un error de red.' };
  }
};

// Función para navegar al listado filtrado por tag - COMENTADA LA LÓGICA DE NAVEGACIÓN
const filterByTag = (tag) => {
    console.log(`Lógica de navegación a listado filtrado por tag: ${tag.name}`);
    // router.push({ path: '/listado', query: { tag: tag.name } });
}

onMounted(fetchSiteData);
</script>

<style scoped>
/* Estilos Mobile First (manteniendo los esenciales) */
.site-detail-container {
  padding: 1rem;
  max-width: 100%;
}

.back-button {
  background: none;
  border: none;
  color: #007bff; 
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
}

hr {
    border: 0;
    height: 1px;
    background-color: #eee;
    margin: 1.5rem 0;
}

.status-chip {
  display: inline-block;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.5rem;
  /* Estilos para las clases generadas por getConservationClass */
  &.good { background-color: #d4edda; color: #155724; } 
  &.fair { background-color: #fff3cd; color: #856404; } 
  &.poor { background-color: #f8d7da; color: #721c24; } 
  &.neutral { background-color: #f1f1f1; color: #333; } 
}

/* Estilos base para simulación */
.tag-placeholder, .action-btn {
    border: 1px solid #ccc;
    padding: 8px;
    border-radius: 4px;
    margin-top: 10px;
    font-size: 0.9em;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}


/* Media Query para Tablet/Escritorio */
@media (min-width: 768px) {
  .site-detail-container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
</style>