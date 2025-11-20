<template>
  <div class="maintenance-container">
    <div class="maintenance-content">
      <h1>🔧 Portal en Mantenimiento</h1>
      <p class="lead">{{ message }}</p>
      <div class="mt-4">
        <p>Estamos realizando tareas de mantenimiento para mejorar nuestro servicio.</p>
        <p>Por favor, intente acceder nuevamente en unos minutos.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaintenanceView',
  data() {
    return {
      message: 'El portal se encuentra en mantenimiento. Por favor, intente nuevamente más tarde.'
    }
  },
  async created() {
    try {
      const response = await fetch('/api/maintenance/status');
      const data = await response.json();
      if (data.message) {
        this.message = data.message;
      }
    } catch (error) {
      console.error('Error fetching maintenance status:', error);
    }
  }
}
</script>

<style scoped>
.maintenance-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.maintenance-content {
  max-width: 600px;
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

h1 {
  color: #dc3545;
  margin-bottom: 1.5rem;
}

.lead {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}
</style>
