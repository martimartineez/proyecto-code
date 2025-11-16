<template>
  <div class="rating-summary">
    <div class="stars">
      <span v-for="n in 5" :key="n" :class="{ 'filled': n <= numericRating }">★</span>
      <span class="average-text">{{ rating === 'N/A' ? 'Sin Calificación' : rating }}</span>
    </div>
    
    <p class="review-count">({{ count }} reseñas)</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  rating: {
    type: [String, Number],
    required: true
  },
  count: {
    type: Number,
    required: true
  }
});

const numericRating = computed(() => {
  let num = 0;
  
  if (typeof props.rating === 'number') {
    num = props.rating;
  } else if (typeof props.rating === 'string' && props.rating !== 'N/A') {
    num = parseFloat(props.rating);
  }
  
  
  return Math.round(num) || 0;
});
</script>

<style scoped>
.rating-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.stars {
  font-size: 1.5rem;
  color: #ccc; 
  display: flex;
  align-items: center;
}
.stars .filled {
  color: gold; 
}
.average-text {
    font-size: 1rem;
    font-weight: bold;
    margin-left: 0.5rem;
    color: #333;
}
.review-count {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}
</style>