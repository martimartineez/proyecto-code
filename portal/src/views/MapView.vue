<template>
    <div class="map-search-container">
      <div class="map-controls">
        <button 
          @click="toggleSearchMode" 
          :class="{ 'active': searchMode }"
          class="search-toggle"
        >
          {{ searchMode ? 'Cancelar búsqueda' : 'Buscar en el mapa' }}
        </button>
        <div v-if="selectedLocation" class="location-info">
          <p>Ubicación seleccionada</p>
          <div class="coordinates">
            Lat: {{ selectedLocation.lat.toFixed(4) }}, 
            Lng: {{ selectedLocation.lng.toFixed(4) }}
          </div>
          <div class="radius-control">
            <label>Radio de búsqueda: {{ searchRadius }} km</label>
            <input 
              type="range" 
              v-model.number="searchRadius" 
              min="0.5" 
              max="50" 
              step="0.5"
              @change="updateSearch"
            >
          </div>
        </div>
      </div>
      
      <div class="map-wrapper">
        <l-map 
          ref="map" 
          v-model:zoom="zoom" 
          :center="center"
          :use-global-leaflet="false"
          @click="handleMapClick"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            layer-type="base"
            name="OpenStreetMap"
          ></l-tile-layer>
          
          <l-marker
            v-if="selectedLocation"
            :lat-lng="[selectedLocation.lat, selectedLocation.lng]"
            :draggable="true"
            @dragend="onMarkerDragEnd"
          >
            <l-icon :icon-size="[32, 32]" :icon-anchor="[16, 32]">
              <div class="search-marker">📍</div>
            </l-icon>
          </l-marker>
          
          <l-circle
            v-if="selectedLocation"
            :lat-lng="[selectedLocation.lat, selectedLocation.lng]"
            :radius="searchRadius * 1000"
            color="#1978c8"
            fill-color="#1978c8"
            :fill-opacity="0.1"
            :weight="2"
          />
          
          <template v-for="site in sitesWithCoords" :key="site.id">
            <l-marker
              :lat-lng="[site.latitude, site.longitude]"
              @click="selectSite(site)"
            >
              <l-popup>
                <h3>{{ site.name }}</h3>
                <p>{{ site.city }}, {{ site.province }}</p>
              </l-popup>
            </l-marker>
          </template>
        </l-map>
      </div>
    </div>
  </template>
  
  <script>
  import { LMap, LTileLayer, LMarker, LPopup, LCircle, LIcon } from "@vue-leaflet/vue-leaflet";
  import "leaflet/dist/leaflet.css";
  
  export default {
    components: {
      LMap,
      LTileLayer,
      LMarker,
      LPopup,
      LCircle,
      LIcon
    },
    props: {
      sites: {
        type: Array,
        default: () => []
      },
      initialLocation: {
        type: Object,
        default: null
      }
    },
    data() {
      return {
        zoom: 5,
        center: [-34.6037, -58.3816],
        searchMode: false,
        selectedLocation: null,
        searchRadius: 5,
        map: null
      };
    },
    computed: {
      sitesWithCoords() {
        // Filtrar sitios que tengan coordenadas válidas
        return this.sites.filter(site => 
          site.latitude !== null && 
          site.latitude !== undefined && 
          site.longitude !== null && 
          site.longitude !== undefined
        );
      }
    },
    watch: {
      initialLocation: {
        immediate: true,
        handler(newVal) {
          if (newVal) {
            this.selectedLocation = { ...newVal };
            this.center = [newVal.lat, newVal.lng];
            this.zoom = 12;
          }
        }
      }
    },
    methods: {
      toggleSearchMode() {
        this.searchMode = !this.searchMode;
        if (!this.searchMode) {
          this.clearSearch();
        }
      },
      
      handleMapClick(event) {
        if (!this.searchMode) return;
        
        const { lat, lng } = event.latlng;
        this.selectedLocation = { lat, lng };
        this.updateSearch();
      },
      
      onMarkerDragEnd(event) {
        const { lat, lng } = event.target.getLatLng();
        this.selectedLocation = { lat, lng };
        this.updateSearch();
      },
      
      updateSearch() {
        if (!this.selectedLocation) return;
        
        // Emitir radius en metros (backend espera metros). Antes se emitía en kilómetros.
        const radiusMeters = this.searchRadius * 1000;
  
        // Debug temporal para verificar los valores enviados
        try { console.debug('MapView.updateSearch ->', { lat: this.selectedLocation.lat, lng: this.selectedLocation.lng, radius: radiusMeters }); } catch (e) {}
  
        this.$emit('location-updated', {
          latitude: this.selectedLocation.lat,
          longitude: this.selectedLocation.lng,
          radius: radiusMeters
        });
      },
      
      clearSearch() {
        this.selectedLocation = null;
        this.$emit('location-updated', null);
      },
      
      selectSite(site) {
        this.$emit('select-site', site);
      }
    }
  };
  </script>
  
  <style scoped>
  .map-search-container {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .map-controls {
    padding: 10px;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    z-index: 1000;
  }
  
  .search-toggle {
    padding: 8px 16px;
    background: #1978c8;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .search-toggle:hover {
    background: #1565c0;
  }
  
  .search-toggle.active {
    background: #d32f2f;
  }
  
  .location-info {
    margin-top: 10px;
    padding: 10px;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .radius-control {
    margin-top: 10px;
  }
  
  .radius-control input {
    width: 100%;
    margin-top: 5px;
  }
  
  .coordinates {
    font-family: monospace;
    color: #666;
    font-size: 12px;
    margin: 5px 0;
  }
  
  .map-wrapper {
    flex: 1;
    min-height: 400px;
    position: relative;
  }
  
  .search-marker {
    font-size: 24px;
    transform: translateY(-50%);
    cursor: move;
  }
  </style>