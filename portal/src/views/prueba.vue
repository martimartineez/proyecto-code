<!-- filepath: portal/src/views/prueba.vue -->
<template>
  <div>
    <button @click="llamarApiBoton">Llamar a /api/boton</button>
  </div>
</template>

<script>
export default {
  methods: {
    async llamarApiBoton() {
      try {
        const response = await fetch('/api/boton');
        if (response.status !== 200) {
          window.location.href = '/login';
          return;
        }
        const data = await response.json();
        console.log('Respuesta de /api/boton:', data);
      } catch (error) {
        console.error('Error al llamar a /api/boton:', error);
        window.location.href = '/login';
      }
    }
  }
}
</script>