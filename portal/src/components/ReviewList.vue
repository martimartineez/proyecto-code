<template>
  <div class="review-list">
    <div v-if="loading" class="loading-state">Cargando reseñas...</div>
    
    <ul v-else-if="reviews.length" class="reviews">
      <li v-for="review in reviews" :key="review.id" class="review-item">
        <div class="review-header">
          <strong class="user-alias">Usuario #{{ review.id_usuario }}</strong>
          <span class="rating">Puntuación: {{ review.rating }} / 5</span>
          <span class="date">{{ formatDate(review.inserted_at) }}</span>
        </div>
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
import { ref, onMounted, defineEmits } from 'vue'; 

const props = defineProps({
  siteId: { type: Number, required: true },
});

// DEFINIMOS EL EVENTO PARA ENVIAR EL RESUMEN AL PADRE
const emit = defineEmits(['update-summary']); 

const reviews = ref([]);
const currentPage = ref(1);
const totalPages = ref(1);
const totalReviews = ref(0);
const perPage = 25; // Requerimiento: 25 por página
const loading = ref(true);

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 

const calculateAndEmitSummary = (reviewsArray, total) => {
    let average = 'N/A';
    
    if (total > 0) {
        // Cálculo Inexacto del promedio (solo si la página actual tiene el total de reseñas)
        if (total <= perPage) {
            const totalScore = reviewsArray.reduce((sum, review) => sum + review.rating, 0);
            average = (totalScore / total).toFixed(1);
        } else {
            // El promedio global debe venir de Flask, por lo que lo dejamos como N/A
            average = 'N/A';
        }
    }
    
    // EMITIR el conteo total (que sí es correcto) y el promedio (placeholder)
    emit('update-summary', {
        count: total,
        average_rating: average 
    });
};


const fetchReviews = async (page) => {
  loading.value = true;
  try {
    const response = await fetch(
      `${baseUrl}/api/sites/${props.siteId}/reviews?page=${page}&per_page=${perPage}`
    );
    
    if (!response.ok) throw new Error("Error al cargar las reseñas");

    const data = await response.json();
    
    reviews.value = data.data; 
    totalReviews.value = data.meta.total;
    totalPages.value = Math.ceil(data.meta.total / perPage);
    currentPage.value = page;
    
    // LLAMAMOS a la función para actualizar el resumen y emitirlo
    calculateAndEmitSummary(reviews.value, totalReviews.value); 

  } catch (error) {
    console.error("Fallo al obtener reseñas:", error);
    reviews.value = [];
    totalReviews.value = 0;
    
    // Emitir el fallo al componente padre
    emit('update-summary', { count: 0, average_rating: 'N/A' }); 
  } finally {
    loading.value = false;
  }
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
/* Estilos básicos para el listado de reseñas (Mobile First) */
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