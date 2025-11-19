<!-- filepath: portal/src/views/prueba.vue -->
<template>
  <div>
    <button @click="llamarApiBoton">Llamar a /api/boton</button>
  </div>
</template>

<script>
import { useApi } from '@/script/useApi';

export default {
  methods: {
    async llamarApiBoton() {
      const { callProtectedApi } = useApi();

      const data = await callProtectedApi('/api/boton');
      if (data) {
        console.log('Respuesta de /api/boton:', data);
      }
    }
  }
}
</script>
