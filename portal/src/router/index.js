import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DetalleSitioView from '../views/DetalleSitioView.vue'
import SitesView from '../views/SitesView.vue'
import MapView from '../views/MapView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sites',
      name: 'sites',
      component: SitesView,
    },
    {
      path: '/map',
      name: 'map',
      component: MapView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/sitios/:id',
      name: 'detalle-sitio',
      component: DetalleSitioView,
    }
  ],
})

export default router
