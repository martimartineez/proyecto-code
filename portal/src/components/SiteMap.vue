<template>
  <div class="map-container-wrapper">
    <l-map ref="map" v-model:zoom="currentZoom" :center="centerCoordinates">
      
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>

      <l-marker :lat-lng="centerCoordinates">
        <l-tooltip :content="tooltipContent" :options="{ permanent: true, direction: 'top' }" />
      </l-marker>

    </l-map>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import 'leaflet/dist/leaflet.css';
import '@/assets/map-shared.css';
import { LMap, LTileLayer, LMarker, LTooltip } from '@vue-leaflet/vue-leaflet';

import L from 'leaflet';

import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._get //para no tener warning en navegador
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const props = defineProps({
  lat: { type: Number, required: true },
  lon: { type: Number, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true }
});

// El zoom inicial
const currentZoom = ref(14);

// Coordenadas reactivas basadas en las props para el mapa y el marcador
const centerCoordinates = computed(() => [props.lat, props.lon]);

// Contenido HTML para el tooltip
const tooltipContent = computed(() => `<strong>${props.title}</strong><br>${props.description}`);
</script>

<style scoped>
</style>