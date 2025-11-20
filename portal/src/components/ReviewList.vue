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
        <div class="review-header">
          <strong class="user-alias">Usuario #{{ review.user_alias }}</strong>
          <span class="rating">Puntuación: {{ review.rating }} / 5</span>
          <span class="date">{{ formatDate(review.updated_at) }}</span>
        </div>
        <p class="review-text">{{ review.comment }}</p>
      </li>
    </ul>

    <p v-else>
      {{ isLoggedIn ? 'No hay reseñas aprobadas para este sitio.' : 'Inicia sesión para ver las reseñas.' }}
    </p>

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

// NUEVO: Estado de login
const isLoggedIn = ref(true);

const API_URL = import.meta.env.VITE_API_BASE_URL;

const fetchReviews = async (page) => {
  loading.value = true;
  try {
    const response = await fetch(
      `${API_URL}/api/sites/${props.siteId}/reviews?page=${page}&per_page=${perPage}&order_by=${sortState.by}&order=${sortState.order}`, {
      method: "GET",
      credentials: "include",
    });

    isLoggedIn.value = response.ok; // <-- Aquí guardas el estado de login

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

const handleSortChange = () => {
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