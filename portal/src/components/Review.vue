<template>
    <div class="review-item">
        <div class="review-header">
            <strong class="user-alias">Usuario #<slot name="id"> </slot></strong>
            <span class="rating">Puntuación: <slot name="puntuaciom"></slot> / 5</span>
            <span class="date">  <slot name="fecha" :review="review"> {{ formatDate(review.fecha) }} </slot> </span>
        </div>
        <p class="review-text"> <slot name="comentario"> </slot> </p>
    </div>
</template>


<script setup>
defineProps({
  review: {
    type: Object,
    required: true
  }
});


const formatDate = (dateString) => {
    if (!dateString) return 'Desconocida';
    return new Date(dateString).toLocaleDateString();
};

</script>

<style>
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
</style>