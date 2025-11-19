<template>
  <div class="image-gallery-container">
    <div class="main-image-wrapper"> 
        <img 
            :src="mainImage.url" 
            :alt="mainImage.alt"
            class="main-image"
            role="img"
        />
    </div>
    
    <div v-if="images.length > 1" class="thumbnail-bar">
        <img 
            v-for="(img, index) in thumbnailImages" 
            :key="index" 
            :src="img.url" 
            :alt="img.alt"
            class="thumbnail"
            :class="{ 'active': index === currentMainIndex }"
            @click="setMainImage(index)"
            @keyup.enter="setMainImage(index)"
            tabindex="0"
        />
        <span v-if="images.length > MAX_THUMBNAILS" class="more-indicator">
            +{{ images.length - MAX_THUMBNAILS }}
        </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue';

const props = defineProps({
  // Espera un array de objetos: [{url: '...', alt: '...', portada: true/false}]
  images: {
    type: Array,
    default: () => [] 
  }
});

const currentMainIndex = ref(0); // Índice de la imagen que se está mostrando actualmente
const MAX_THUMBNAILS = 4;

// LÓGICA CLAVE: Buscar la Portada y actualizar el índice al cargar los datos
watchEffect(() => {
    // Se ejecuta al inicio o cuando props.images cambia
    if (props.images.length > 0) {
        // Buscar la primera imagen con portada: true
        const portadaIndex = props.images.findIndex(img => img.portada === true);
        
        // Si encuentra una portada, actualiza el índice principal. Si no, usa el índice 0.
        if (portadaIndex !== -1) {
            currentMainIndex.value = portadaIndex;
        } else {
            currentMainIndex.value = 0; 
        }
    } else {
        currentMainIndex.value = 0;
    }
});


// Determina la imagen principal a mostrar (usa currentMainIndex)
const mainImage = computed(() => {
    const imageObject = props.images[currentMainIndex.value];
    if (imageObject) {
        return { 
            url: imageObject.url,
            alt: imageObject.alt || 'Sitio histórico, foto principal', 
        };
    }
    // si no hay imágenes
    return { 
        alt: 'Este sitio no tiene imágenes disponibles.', 
    };
});

// Muestra solo las primeras N miniaturas
const thumbnailImages = computed(() => props.images.slice(0, MAX_THUMBNAILS));

// Cambia la imagen principal al hacer clic en una miniatura
const setMainImage = (index) => {
    currentMainIndex.value = index;
};
</script>

<style scoped>
.image-gallery-container {
    width: 100%;
}
.main-image-wrapper {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 10px;
}

.main-image {
    width: 100%;
    height: auto; /* La altura se adapta a la proporción de la imagen */
    object-fit: contain; /* Asegura que la imagen completa se muestre */
    display: block;
}

.thumbnail-bar {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 5px;
}
.thumbnail {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 4px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: border-color 0.2s;
}
.thumbnail.active, .thumbnail:hover {
    border-color: #007bff; /* Resalta la miniatura activa */
}
.more-indicator {
    align-self: center;
    font-weight: bold;
    color: #666;
    white-space: nowrap;
}
</style>