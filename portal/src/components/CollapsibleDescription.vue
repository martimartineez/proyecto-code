<template>
  <div class="collapsible-description">
    <p class="description-text" :class="{ 'is-collapsed': isCollapsed && requiresCollapse }">
      {{ text }}
    </p>

    <button 
      v-if="requiresCollapse" 
      @click="toggleCollapse" 
      class="toggle-button"
    >
      {{ isCollapsed ? 'Ver más' : 'Ver menos' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
 
  text: {
    type: String,
    required: true
  },
  
  limit: {
    type: Number,
    default: 300 
  }
});


const isCollapsed = ref(true);


const requiresCollapse = computed(() => props.text.length > props.limit);

// Función para alternar el estado
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<style scoped>
.collapsible-description {
  position: relative;
  padding-bottom: 25px; 
}

.description-text {
  line-height: 1.5;
  margin-bottom: 0.5rem;
  transition: max-height 0.3s ease-out; 
}

/* ESTADO COLAPSADO */
.is-collapsed {
  max-height: 4.5em; 
  overflow: hidden;
  position: relative;
}

/* Gradiente de difuminado al final del texto colapsado */
.is-collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1.5em; 
  background: linear-gradient(to top, white 50%, rgba(255, 255, 255, 0) 100%);
}

.toggle-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 0;
  font-weight: bold;
  position: absolute;
  bottom: 0;
  left: 0;
}
</style>