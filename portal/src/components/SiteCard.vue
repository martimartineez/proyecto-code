<template>
  <article class="card">
    <div class="cover" :style="coverStyle">
      <span v-if="!site.cover_image" class="placeholder">📍</span>
    </div>
    <div class="body">
      <h3 class="title">{{ site.nombre }}</h3>
      <p class="meta">
        <span v-if="site.ciudad">{{ site.ciudad }}</span>
        <span v-if="site.provincia">, {{ site.provincia }}</span>
      </p>
      <p v-if="site.estado" class="state">{{ site.estado }}</p>
      <ul class="tags">
        <li v-for="t in site.tags" :key="t" class="tag">{{ t }}</li>
      </ul>
    </div>
  </article>
  
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({
  site: { type: Object, required: true },
});

const coverStyle = computed(() => ({
  backgroundImage: props.site.cover_image ? `url(${props.site.cover_image})` : 'none',
}));
</script>

<style scoped>
.card { display: flex; flex-direction: column; border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
.cover { aspect-ratio: 16/9; background: #f3f4f6 center/cover no-repeat; display: grid; place-items: center; }
.placeholder { font-size: 2rem; color: #9ca3af; }
.body { padding: 14px; display: grid; gap: 8px; }
.title { margin: 0; font-size: 1.05rem; line-height: 1.35rem; color: #111827; font-weight: 600; }
.meta { margin: 0; color: #374151; font-size: 0.9rem; }
.state { margin: 0; font-size: 0.85rem; color: #0f766e; font-weight: 600; }
.tags { display: flex; gap: 8px; flex-wrap: wrap; list-style: none; padding: 0; margin: 0; }
.tag { background: #f1f5f9; color: #334155; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
</style>


