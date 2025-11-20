import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DetalleSitioView from '../views/DetalleSitioView.vue'
import SitesView from '../views/SitesView.vue'
import MapView from '../views/MapView.vue'
import MaintenanceView from '../views/MaintenanceView.vue'

// Crear el router primero
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/maintenance',
      name: 'maintenance',
      component: MaintenanceView,
      meta: { isMaintenance: true }
    },
    { 
      path: '/', 
      name: 'home', 
      component: HomeView,
    },
    {
      path: '/sitios',
      name: 'sites',
      component: SitesView,
    },
    {
      path: '/sitios/:id',
      name: 'detalle-sitio',
      component: DetalleSitioView,
    }, 
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue')
    },
  ]
})

let isMaintenanceMode = false;

async function checkMaintenance() {
  try {
    const response = await fetch('/api/feature-flags/portal_maintenance_mode');
    if (!response.ok) {
      console.error('Error checking maintenance status:', response.statusText);
      return;
    }
    const data = await response.json();
    isMaintenanceMode = data.activo === true;
    
    // si el flag esta activo y no estoy en la pagina de mantenimiento
    if (isMaintenanceMode && router.currentRoute.value.name !== 'maintenance') {
      router.push({ name: 'maintenance' });
    }
  } catch (error) {
    console.error('Error checking maintenance status:', error);
  }
}

// chequeo inicial
checkMaintenance();

// Chequea cada segundo
setInterval(checkMaintenance, 1000);

router.beforeEach(async (to, from, next) => {
  // saltea la ruta de mantenimiento
  if (to.meta.isMaintenance) {
    return next();
  }

  if (isMaintenanceMode) {
    return next({ name: 'maintenance' });
  }

  next();
});

export default router