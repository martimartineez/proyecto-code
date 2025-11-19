<template>
  <div class="review-list">
    <div class="sort-controls">
      <label for="sort-by">Ordenar por:</label>
      <select id="sort-by" v-model="sortState.by" @change="handleSortChange">
        <option value="inserted_at">Fecha</option>
        <option value="rating">Calificación</option>
      </select>

      <select v-model="sortState.order" @change="handleSortChange">
        <option value="desc">
          {{ sortState.by === 'rating' ? 'Descendente (Mejor)' : 'Descendente (Más Reciente)' }}
        </option>
        <option value="asc">
          {{ sortState.by === 'rating' ? 'Ascendente (Peor)' : 'Ascendente (Más Antiguo)' }}
        </option>
      </select>
    </div>
    
    <div v-if="loading" class="loading-state">Cargando reseñas...</div>
    
    <ul v-else-if="reviews.length" class="reviews">
      <li v-for="review in reviews" :key="review.id" class="review-item">
        <review>
          <template #id>
            {{ review.id_usuario }}
          </template>
          <template #puntuaciom>
            {{ review.rating }}
          </template>
          <template #fecha>
            {{ formatDate(review.inserted_at) }}
          </template>
        </review>
        <p class="review-text">{{ review.comment }}</p>
      </li>
    </ul>

    <p v-else>No hay reseñas aprobadas para este sitio.</p>

    <div v-if="totalPages > 1" class="pagination-controls">
      <button 
        @click="goToPage(currentPage - 1)" 
        :disabled="currentPage === 1"
      >
        &larr; Anterior
      </button>
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
      <button 
        @click="goToPage(currentPage + 1)" 
        :disabled="currentPage === totalPages"
      >
        Siguiente &rarr;
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'; 
import Review from './Review.vue';

const props = defineProps({
  siteId: { type: Number, required: true },
});

// Estado de la UI y datos
const reviews = ref([]);
const currentPage = ref(1);
const totalPages = ref(1);
const totalReviews = ref(0);
const perPage = 25; // Requerimiento: 25 por página
const loading = ref(true);

// NUEVO: Estado para el ordenamiento
const sortState = reactive({
    by: 'inserted_at', // rating o inserted_at
    order: 'desc'     // asc o desc
});


const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 


const fetchReviews = async (page) => {
  loading.value = true;
  try {
    // 1. Incluir los parámetros de ordenamiento en la solicitud GET
    const response = await fetch(
      `${baseUrl}/api/sites/${props.siteId}/reviews?page=${page}&per_page=${perPage}&order_by=${sortState.by}&order=${sortState.order}`
    );
    
    
    if (!response.ok) throw new Error("Error al cargar las reseñas");

    const data = await response.json();
    
    reviews.value = data.data; 
    totalReviews.value = data.meta.total;
    totalPages.value = Math.ceil(data.meta.total / perPage);
    currentPage.value = page;
    
    
  } catch (error) {
    console.error("Fallo al obtener reseñas:", error);
    reviews.value = [];
    totalReviews.value = 0;
    
  } finally {
    loading.value = false;
  }
};

// NUEVO: Función para manejar el cambio en el select
const handleSortChange = () => {
    // Al cambiar el orden, reiniciamos a la página 1 para aplicar el filtro
    fetchReviews(1); 
};

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchReviews(page);
  }
};

const formatDate = (dateString) => {
    if (!dateString) return 'Desconocida';
    return new Date(dateString).toLocaleDateString();
};

onMounted(() => {
  // Carga inicial usando el orden por defecto (Más reciente/desc)
  fetchReviews(1); 
});
</script>

<style scoped>
/* Estilos para los controles de ordenamiento */
.sort-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0 1rem; 
}
.sort-controls select {
    padding: 8px;
    border-radius: 4px;
}

/* El resto de estilos para la lista */
.review-item {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}
.review-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.9em;
  margin-bottom: 0.5rem;
}
.review-text {
  font-size: 1em;
  color: #555;
  /* Solución para que las palabras largas no rompan el layout en móvil */
  word-wrap: break-word; 
  overflow-wrap: break-word; 
}
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}
.pagination-controls button {
  padding: 0.5rem 1rem;
  cursor: pointer;
}
</style>