<template>
  <main v-if="site" class="site-detail-container">
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

      <div class="tag-placeholder">Tags: {{ site.tags.map(t => t.name).join(', ') }}</div>
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
        [Listado de Reseñas Paginadas: usa reseñas]
      </div>
    </section>

  </main>

  <div v-else class="loading-state">
    Cargando detalles del sitio histórico...
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SiteMap from '@/components/SiteMap.vue'; // ESTE SÍ ESTÁ ACTIVO

// Importa tus componentes de UI - COMENTADOS PARA EVITAR ERRORES
/*
import SiteImageGallery from '@/components/SiteImageGallery.vue';
import CollapsibleDescription from '@/components/CollapsibleDescription.vue';
// ... otros componentes
*/

const route = useRoute();
const router = useRouter();
const site = ref(null); 
const isAuthenticated = ref(false); 

// DATOS SIMULADOS ACTUALIZADOS PARA COINCIDIR CON LA API (NOMBRES EN INGLÉS)
const DUMMY_SITE_DATA = {
    id: 123,
    // CAMPOS DE LA API DE SITIOS HISTÓRICOS (GET /sites/{id}):
    name: "Catedral Metropolitana", // API: name
    city: "La Plata", // API: city
    province: "Buenos Aires", // API: province
    state_of_conservation: "excelente", // API: state_of_conservation
    lat: -34.9213, // API: lat
    long: -57.9544, // API: long
    short_description: "Impresionante ejemplo de arquitectura neogótica.", // API: short_description
    description: "La Catedral de La Plata, dedicada a la Inmaculada Concepción, es uno de los templos más grandes de América. Su construcción se inició en 1884 y combina elementos arquitectónicos de la época con modernas técnicas de ingeniería. Es un punto clave en la historia urbana de la ciudad y un sitio de gran valor patrimonial. [Este texto es largo para simular la descripción completa que se debería plegar]...", // API: description
    tags: [{id: 1, name: 'Arquitectura'}, {id: 2, name: 'Neogótico'}], 
    
    // CAMPOS AGREGADOS (Estos no vienen del GET /sites/{id} y se mantendrán con nombres en español)
    calificacion_promedio: 4.8, 
    cantidad_reseñas: 155,
    is_favorite: false, 
    reviews: [ /* ... */ ]
}

// Función para mapear el estado de conservación a una clase CSS
const getConservationClass = (estado) => {
    // Normalizamos el estado a minúsculas y sin espacios para usarlo como clase
    if (!estado) return 'unknown';
    const lowerCaseEstado = estado.toLowerCase();
    
    // Basado en los choices de la API: 'excelente', 'bueno', 'regular', 'malo'
    if (lowerCaseEstado.includes('excelente') || lowerCaseEstado.includes('bueno')) return 'good';
    if (lowerCaseEstado.includes('regular')) return 'fair';
    if (lowerCaseEstado.includes('malo')) return 'poor';
    
    return 'neutral';
}

const fetchSiteData = async () => {
  const siteId = route.params.id; 
  try {
    // NOTA: Cuando implementes la llamada real, la URL será algo como:
    // const response = await fetch(`{BASE_URL}/api/sites/${siteId}`);
    
    // USAMOS LOS DATOS SIMULADOS ACTUALIZADOS 
    console.log(`Simulando carga para el sitio ID: ${siteId}`);
    site.value = DUMMY_SITE_DATA;

  } catch (error) {
    console.error("Error al cargar datos:", error);
    site.value = { error: 'No se pudo cargar la información.' };
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
  &.good { background-color: #d4edda; color: #155724; } /* Verde - Excelente/Bueno */
  &.fair { background-color: #fff3cd; color: #856404; } /* Amarillo - Regular/Mantenimiento */
  &.poor { background-color: #f8d7da; color: #721c24; } /* Rojo - Pobre/Ruinas */
  &.neutral { background-color: #f1f1f1; color: #333; } /* Gris - Desconocido */
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