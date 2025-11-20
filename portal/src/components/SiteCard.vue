<template>
  <article class="card" @click="goToDetail">
    <div class="cover" :style="coverStyle">
      <span v-if="!site.cover_image" class="placeholder">📍</span>
    </div>
    <div class="body">
      <h3 class="title">{{ site.nombre }}</h3>
      <p class="meta">
        <span v-if="site.ciudad">{{ site.ciudad }}</span>
        <span v-if="site.provincia">, {{ site.provincia }}</span>
      </p>
      <p v-if="site.fechaRegistro" class="meta">
        Fecha de registro: {{ formatDate(site.fechaRegistro) }}
      </p>
      <p v-if="site.estado" class="state">Estado: {{ site.estado }}</p>
      <div v-if="site.avg_rating > 0" class="rating">
        <span v-for="i in 5" :key="i" class="star" :class="{ 'filled': i <= Math.round(site.avg_rating) }">
          ★
        </span>
        <span class="rating-text">
          {{ site.avg_rating.toFixed(1) }} ({{ site.review_count || 0 }})
        </span>
      </div>
      <div v-else class="rating">
        <span class="no-reviews">Sin calificaciones</span>
      </div>
      <ul class="tags">
        <li v-for="t in site.tags" :key="t" class="tag">{{ t }}</li>
      </ul>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

function formatDate(dateString) {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (e) {
    console.error('Error formatting date:', e);
    return dateString;
  }
}
const props = defineProps({
  site: { type: Object, required: true },
});

function goToDetail() {
  sessionStorage.setItem("list-scroll", String(window.scrollY));
  router.push({ name: 'detalle-sitio', params: { id: props.site.id } });
}

const coverStyle = computed(() => ({
  backgroundImage: props.site.cover_url ? `url(${props.site.cover_url})` : 'none',
}));
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  /* Transición suave para efectos hover */
  transition: all 0.3s ease;
  cursor: pointer;
}

/* Efecto hover con zoom y sombra */
.card:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.cover {
  aspect-ratio: 16/9;
  background: #f3f4f6 center/cover no-repeat;
  display: grid;
  place-items: center;
  /* Para que el zoom no afecte los bordes redondeados */
  transform: translateZ(0);
}

.placeholder {
  font-size: 2rem;
  color: #9ca3af;
}

.body {
  padding: 14px;
  display: grid;
  gap: 8px;
}

.title {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.35rem;
  color: #111827;
  font-weight: 600;
}

.meta {
  margin: 0;
  color: #374151;
  font-size: 0.9rem;
}

.state {
  margin: 0;
  font-size: 0.85rem;
  color: #0f766e;
  font-weight: 600;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  list-style: none;
  padding: 0;
  margin: 0;
}

.tag {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 4px 0;
}

.star {
  color: #e2e8f0;
  font-size: 1rem;
  line-height: 1;
}

.star.filled {
  color: #f59e0b;
}

.rating-text {
  margin-left: 4px;
  font-size: 0.85rem;
  color: #64748b;
}

.no-reviews {
  font-size: 0.85rem;
  color: #94a3b8;
  font-style: italic;
}
</style>

