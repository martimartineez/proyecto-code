<template>
  <main v-if="site && !site.error" class="site-detail-container">
    <button @click="router.back()" class="back-button">
      &larr; Volver atras
    </button>
    
    <section class="info-and-media">
      <SiteImageGallery :images="site.images || []" />
      
      <div class="header-info">
        <h1>{{ site.name }}</h1>
        <h5>{{ site.short_description }}</h5>
        <p class="location">{{ site.city }}, {{ site.province }}</p>
        
        <span :class="['status-chip', getConservationClass(site.state_of_conservation)]">
          {{ site.state_of_conservation }}
        </span>
      </div>
      
      <div class="tag-list">
          Tags:
          <span 
              v-for="tag in site.tags" 
              :key="tag" 
              @click="filterByTag(tag)"
              class="tag-chip"
          >
              {{ tag }}
          </span>
          <span v-if="!site.tags || site.tags.length === 0" class="tag-chip-placeholder"></span>
      </div>
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
            <button
              class="action-btn primary"
              @click="handleRestrictedAction('REVIEW')"
              :disabled="isActionLoading"
              data-bs-toggle="collapse"
              data-bs-target="#formReseña"
              aria-label="Escribir reseña"
            >
              <span class="btn-icon" aria-hidden>✍️</span>
              <span class="btn-text">Escribir Reseña</span>
              <span v-if="isActionLoading" class="btn-spinner" aria-hidden></span>
            </button>
            
            <button
              class="action-btn favorite-btn"
              :class="{ favorited: is_favorite }"
              @click="toggleFavorite"
              :aria-pressed="is_favorite"
              :disabled="isActionLoading"
              aria-label="Marcar como favorito"
            >
              <span class="btn-icon" aria-hidden>
                <template v-if="is_favorite">★</template>
                <template v-else>☆</template>
              </span>
              <span class="btn-text">
                <template v-if="is_favorite">Favorito</template>
                <template v-else>Marcar Favorito</template>
              </span>
              <span v-if="isActionLoading" class="btn-spinner" aria-hidden></span>
            </button>
        </div>
      </div>

      <!-- Sección de reseñas -->
      <template v-if="reviewsEnabled">
        <div class="collapse" id="formReseña">
          <span v-if="!has_review"><ReviewForm :site-id="site.id" /> </span>
          <span v-else-if="get_review">
            <Review :review="get_review">
              <template #id>
                {{ get_review.usuario }}
              </template>
              <template #puntuaciom>
                {{ get_review.rating }}
              </template>
              <template #comentario>
                {{ get_review.texto }}
              </template>
            </Review>
            <p> Estado: <b> {{ get_review.estado }} </b></p>
            <button class="btn btn-danger mb-3" @click="delete_review">
              Borrar Reseña
            </button>
          </span>
        </div>
        <ReviewList :site-id="site.id" />
      </template>
      <div v-else class="alert alert-info mt-3">
        <i class="fa fa-info-circle me-2"></i>
        {{ reviewsMessage }}
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
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApi } from '@/script/useApi'; 
import SiteMap from '@/components/SiteMap.vue';
import CollapsibleDescription from '@/components/CollapsibleDescription.vue';

const reviewsEnabled = ref(false);
const reviewsMessage = ref('Las reseñas están temporalmente deshabilitadas.');

// Verificar si las reseñas están habilitadas usando los datos del sitio
function checkReviewsStatus(siteData) {
  if (siteData && siteData.feature_flags) {
    const reviewsFlag = siteData.feature_flags.find(flag => flag.name === 'reviews_enabled');
    if (reviewsFlag) {
      reviewsEnabled.value = reviewsFlag.valor || false;
      reviewsMessage.value = reviewsFlag.message || 'Las reseñas están temporalmente deshabilitadas.';
      return;
    }
  }
  reviewsEnabled.value = false;
  reviewsMessage.value = 'Las reseñas están temporalmente deshabilitadas.';
}
import ReviewList from '@/components/ReviewList.vue'; 
import RatingSummary from '@/components/RatingSummary.vue';
import SiteImageGallery from '@/components/SiteImageGallery.vue'; 
import ReviewForm from '../components/ReviewForm.vue';
import Review from '../components/Review.vue';

const route = useRoute();
const router = useRouter();
const { callProtectedApi } = useApi(); // Inicializamos el composable para llamadas protegidas
const site = ref(); 
const isActionLoading = ref(false); // Deshabilita botones durante el fetch
const API_URL = import.meta.env.VITE_API_BASE_URL;
const reviews = ref([]);
// *** IMPLEMENTACIÓN FINAL DE LA ACCIÓN DE FAVORITOS (PUT/DELETE) ***


const is_favorite = computed(() => {
  return site.value.is_favorite
})

const has_review = computed(() => {
  console.log(reviews.value.some(review => review.sitio === site.value.name))
  return reviews.value.some(review => review.sitio === site.value.name);
})

const get_review = computed(() => {
   return reviews.value.find(
    review => review.sitio === site.value.name);
})

const user_reviews = async() => {
  try {
    const res = await fetch(`${API_URL}/api/reseñas_usuario`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (res.status === 500) {
      reviews.value = [];
      return;
    }
    if (!res.ok) {
      throw new Error(res.status);
    }
    let valor = await res.json();
    reviews.value = valor.reseñas;
    console.log(reviews.value);
  } catch (err) {
    reviews.value = [];
  }
}

const delete_review = async() =>{
  try{
    console.log(get_review.value.id);
    console.log(site.value.id);
    console.log(get_review.value.id);
        const res = await fetch(`${API_URL}/api/sites/${site.value.id}/reviews/${get_review.value.id}`, {
          method: "DELETE",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });
      if (!res.ok) {
        throw new Error(res.status);
      }
  }
  catch(error){
    console.log(error);
  }
    window.location.reload();
}

// *** LÓGICA DE REDIRECCIÓN CONDICIONAL PARA ESCRIBIR RESEÑA ***
const handleRestrictedAction = async (actionType) => {
    isActionLoading.value = true;
    

    const isAuthenticatedCheck = await callProtectedApi('/api/perfil', { method: 'GET' });
    
    isActionLoading.value = false;

    if (isAuthenticatedCheck !== null) {
        if (actionType === 'REVIEW') {
            console.log("Abrir modal/formulario para crear reseña.");
        }
    }
};

const toggleFavorite = async () => {
    console.log("Toggle favorite clickedddddddddd");
    isActionLoading.value = true;
    
    const isCurrentlyFavorited = site.value.is_favorite;
    const method = isCurrentlyFavorited ? 'DELETE' : 'PUT';
    
    try {
        const url = `/api/sites/${site.value.id}/favorite`;

        const respuesta = await fetch(url, {
            method: method,
            credentials: "include"
        });

        // --- AUTENTICACIÓN / REDIRECCIÓN ---
        if (respuesta.status === 401 || respuesta.status === 403) {

            // Guardamos la URL actual para volver después del login
            localStorage.setItem('redirectAfterLogin', window.location.pathname);

            // Redirigimos al login
            window.location.href = '/login';
            return;
        }
        // -----------------------------------

        if (!respuesta.ok) {
            console.error("Error marcando favorito:", respuesta.status);
            return;
        }

        // Si todo OK → actualizamos visualmente
        site.value.is_favorite = !isCurrentlyFavorited;

    } catch (error) {
        console.error("Error de red al marcar favorito:", error);
    } finally {
        isActionLoading.value = false;
    }
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

// IMPLEMENTACIÓN FINAL DE LA NAVEGACIÓN DE TAGS CLICABLES
const filterByTag = (tag) => {
    router.push({ 
        path: '/sitios',
        query: { tags: tag } 
    });
}

//const API_URL = import.meta.env.VITE_API_BASE_URL;


const fetchSiteData = async () => {
    const siteId = route.params.id; 
    //const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 
    //const API_URL = import.meta.env.VITE_API_BASE_URL;

    
    try {
        const siteResponse = await fetch(`${API_URL}/api/sites/${siteId}`);
        if (!siteResponse.ok) {
            if (siteResponse.status === 404) {
                 site.value = { error: 'El sitio no existe (Error 404).' };
                 return; 
            }
            throw new Error(`Error HTTP: ${siteResponse.status}`);
        }
        
        let siteData = await siteResponse.json();
        
        // Asignamos las claves del backend al frontend.
        siteData.calificacion_promedio = siteData.rating_avg || 'N/A';
        siteData.cantidad_reseñas = siteData.reviews_count || 0;
        
        const favoriteResponse = await fetch( `${API_URL}/api/sites/${siteId}/is_favorite`, {
          method: "GET",
          credentials: "include",
          headers: {
          "Content-Type": "application/json"
        },
        });
        let favorite = await favoriteResponse.json();
        siteData.is_favorite = favorite.is_favorite;
        siteData.images = siteData.images || []; 
        
        // Verificar el estado de las reseñas con los datos del sitio
        checkReviewsStatus(siteData);
        
        site.value = siteData; 
        console.log(site.value)
    } catch (error) {
        console.error("Error al cargar detalles del sitio:", error);
        site.value = { error: 'No se pudo contactar al servidor de la API o hubo un error de red.' };
    }
};



onMounted(fetchSiteData);
onMounted(user_reviews);
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
}
.status-chip.good { background-color: #d4edda; color: #155724; } 
.status-chip.fair { background-color: #fff3cd; color: #856404; } 
.status-chip.poor { background-color: #f8d7da; color: #721c24; } 
.status-chip.neutral { background-color: #f1f1f1; color: #333; } 

/* --- ESTILOS DE TAGS CLICABLES --- */
.tag-list {
    margin-top: 1rem;
    font-size: 0.9em;
}

.tag-chip {
    display: inline-block;
    background-color: #e0e0e0;
    color: #333;
    padding: 3px 8px;
    margin-right: 5px;
    border-radius: 12px;
    cursor: pointer; /* Indica que es clicable */
    transition: background-color 0.2s;
}

.tag-chip:hover {
    background-color: #c0c0c0;
}

/* Estilos base para simulación */
.action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    border: 1px solid #d0d0d0;
    padding: 10px 14px;
    border-radius: 8px;
    margin-top: 10px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
    background: white;
    color: #222;
    user-select: none;
}

/* Primary button (Escribir Reseña) */
.action-btn.primary {
    background: linear-gradient(180deg, #3b82f6, #2563eb);
    color: #fff;
    border: none;
    box-shadow: 0 6px 18px rgba(37,99,235,0.18);
}
.action-btn.primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 22px rgba(37,99,235,0.2);
}
.action-btn.primary:active:not(:disabled) {
    transform: translateY(0);
}

/* Favorite button */
.favorite-btn {
    background: linear-gradient(180deg,#fff,#fafafa);
    border: 1px solid #cfcfcf;
    color: #333;
}
.favorite-btn:hover:not(.favorited):not(:disabled) {
    background: #f6f6f6;
}
.favorite-btn.favorited {
    background: linear-gradient(180deg,#ffd54a,#ffca28);
    color: #3a2a00;
    border-color: #ffb300;
    box-shadow: 0 6px 14px rgba(255,176,0,0.18);
}
.favorite-btn.favorited:hover:not(:disabled) {
    transform: translateY(-2px);
}

/* Icon and text sizing */
.btn-icon {
    font-size: 1.05rem;
    line-height: 1;
}
.btn-text {
    font-weight: 600;
}

/* Disabled state */
.action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

/* Small inline spinner */
.btn-spinner {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.4);
    border-top-color: rgba(255,255,255,0.95);
    animation: spin 0.8s linear infinite;
    display: inline-block;
    margin-left: 6px;
}
.favorite-btn .btn-spinner {
    border: 2px solid rgba(0,0,0,0.12);
    border-top-color: rgba(0,0,0,0.5);
}
@keyframes spin { to { transform: rotate(360deg); } }

.action-buttons {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    align-items: center;
}

/* Estilo para botón favorito marcado (compatibilidad antigua) */
.btn-favorited {
    background-color: gold !important;
    color: black !important;
    border-color: #ffc107 !important;
}

/* Media Query para Tablet/Escritorio */
@media (min-width: 768px) {
  .site-detail-container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
</style>