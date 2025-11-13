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
        <h5>{{ site.short_description }}</h5>
        <p class="location">{{ site.city }}, {{ site.province }}</p>
        
        <span :class="['status-chip', getConservationClass(site.state_of_conservation)]">
          {{ site.state_of_conservation }}
        </span>
      </div>
      
      <div class="tag-placeholder">Tags: {{ site.tags?.join(', ') || 'N/A' }}</div>
    </section>

    <hr>
    
    <section>
        <h2>Descripción</h2>
        <CollapsibleDescription :text="site.description" :limit="300" />
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
        <RatingSummary 
            :rating="site.calificacion_promedio" 
            :count="site.cantidad_reseñas" 
        />
        
        <div class="action-buttons">
            <button class="action-btn">Escribir Reseña (Login requerido)</button>
            
            <button class="action-btn">Marcar Favorito</button>
        </div>
      </div>

      <ReviewList :site-id="site.id" @update-summary="updateReviewSummary" />
      
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
import CollapsibleDescription from '@/components/CollapsibleDescription.vue';
import ReviewList from '@/components/ReviewList.vue'; 
import RatingSummary from '@/components/RatingSummary.vue';


const route = useRoute();
const router = useRouter();
const site = ref(null); 
const isAuthenticated = ref(false); 

// Función para actualizar las propiedades del sitio cuando el hijo (ReviewList) emite el resumen
const updateReviewSummary = (summary) => {
    // Estas líneas se ejecutan cuando ReviewList termina de cargar los metadatos
    site.value.cantidad_reseñas = summary.count;
    site.value.calificacion_promedio = summary.average_rating;
};

// Función para mapear el estado de conservación a una clase CSS
const getConservationClass = (estado) => {
    if (!estado) return 'unknown';
    const lowerCaseEstado = estado.toLowerCase();
    
    if (lowerCaseEstado.includes('bueno')) return 'good';
    if (lowerCaseEstado.includes('regular')) return 'fair';
    if (lowerCaseEstado.includes('malo')) return 'poor';
    
    return 'neutral';
}

const fetchSiteData = async () => {
    const siteId = route.params.id; 
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 
    
    let siteData = null; 

    try {
        // 1. LLAMADA AL DETALLE DEL SITIO (única llamada)
        const siteResponse = await fetch(`${baseUrl}/api/sites/${siteId}`);
        if (!siteResponse.ok) {
            if (siteResponse.status === 404) {
                 site.value = { error: 'El sitio no existe (Error 404).' };
                 return; 
            }
            throw new Error(`Error HTTP: ${siteResponse.status}`);
        }
        siteData = await siteResponse.json();
        
        // Inicializamos los placeholders que el ReviewList actualizará
        siteData.cantidad_reseñas = 0;
        siteData.calificacion_promedio = 'N/A';

        // 2. Asignar los datos
        site.value = siteData; 

        // NOTA: La lógica de reseñas (la segunda llamada) ahora se encuentra encapsulada en ReviewList.vue

    } catch (error) {
        console.error("Error al cargar detalles del sitio:", error);
        site.value = { error: 'No se pudo contactar al servidor de la API o hubo un error de red.' };
    }
};

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