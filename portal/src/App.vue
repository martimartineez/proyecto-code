<template>
  <header>
      <nav class="navbar navbar-expand-lg">
        <div class="container-fluid p-3">
            <RouterLink to="/" class="navbar-brand" id="title">
                <img alt="UNLP logo" class="logo" src="@/assets/UNLP_Logo.svg" width="70" height="70" />
                <span> Sitios Historicos </span>
              </RouterLink> 
              <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarTogglerDemo01" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
              </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <RouterLink to="/sitios" class="nav-link m-2" id="explorar">Explorar!</RouterLink>
                <!-- barra de busqueda  -->
                <div class="container-fluid p-0 pt-2">
                    <form class="d-flex" role="search" action="/sitios">
                        <div id="search">
                        <svg viewBox="0 0 420 60" xmlns="http://www.w3.org/2000/svg">
                            <rect class="bar"/>
                            <g class="magnifier">
                                <circle class="glass"/>
                                <line class="handle" x1="32" y1="32" x2="44" y2="44"></line>
                            </g>
                        </svg>
                        <input id="busqueda" type=search name=q aria-label="Search for inspiration"/>
                        </div>
                    </form>
                </div>
                <!-- PROFILE / LOGIN -->
                <div class="miperfil">
                  <template v-if="profile">
                    <div class="nav-link me-3 profile-container">
                      <button class="profile-button profile-link me-3" data-bs-toggle="collapse" data-bs-target="#perfil-menu" :aria-expanded="menuOpen" aria-haspopup="true">
                        <img :src="profile.foto || defaultAvatar" alt="avatar" class="avatar" />
                        <span class="username">{{ profile.nombre || profile.name || profile?.given_name || 'Perfil' }}</span>
                      </button>
                      <ul class= "collapse profile-menu" id="perfil-menu" role="menu">
                        <li role="none">
                          <RouterLink to="/profile" class="menu-item" role="menuitem">Ver mi perfil</RouterLink>
                        </li>
                        <li role="none">
                          <RouterLink :to="{ path: '/profile', query: { tab: 'reseñas' } }" class="menu-item" role="menuitem">Mis reseñas</RouterLink>
                        </li>
                        <li role="none">
                          <RouterLink :to="{ path: '/profile', query: { tab: 'favoritos' } }" class="menu-item" role="menuitem" >Favoritos</RouterLink>
                        </li>
                        <li class="divider" role="separator"></li>
                        <li role="none">
                          <a href="#" class="menu-item" role="menuitem" @click.prevent="logout">Cerrar sesión</a>
                        </li>
                      </ul>
                    </div>
                  </template>
                  <template v-else>
                    <RouterLink to="/login" class="nav-link d-none d-lg-flex me-5" @click="saveRedirectPath">Iniciar sesión</RouterLink>
                  </template>
          </div>
        </div>
      </div>
    </nav>
  </header>
<div class="container-md pt-3" id="mainView">
    <RouterView />
</div>
  
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'


const profile = ref(null)
const defaultAvatar = 'https://www.gravatar.com/avatar/?d=mp&s=80' // placeholder externo
const API_URL = import.meta.env.VITE_API_BASE_URL || ''

const route = useRoute()
const router = useRouter()

// menú del avatar
const profileEl = ref(null)


function saveRedirectPath() {
  localStorage.setItem('redirectAfterLogin', window.location.pathname)
}

function onDocumentClick(e) {
  const el = profileEl.value
  if (!el) return
  if (!el.contains(e.target)) {
    closeMenu()
  }
}

async function logout() {
  try {
    if (API_URL) {
      // intenta invalidar sesión en backend si existe endpoint
      await fetch(`${API_URL}/api/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      })
    }
  } catch (e) {
    console.warn('No se pudo llamar al logout en backend:', e)
  } finally {
    profile.value = null
    // notificar a otras pestañas
    localStorage.setItem('authChanged', Date.now())
    router.push('/')
  }
}

async function fetchProfile() {
  try {
    if (!API_URL) {
      profile.value = null
      return
    }
    const res = await fetch(`${API_URL}/api/perfil`, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (res.ok) {
      profile.value = await res.json()
    } else {
      profile.value = null
    }
  } catch (e) {
    console.warn('No se pudo obtener el perfil en header:', e)
    profile.value = null
  }
}

function onStorage(e) {
  if (!e) return
  // escucha la clave que usaremos al hacer logout/login
  if (e.key === 'authChanged') {
    // refetch para actualizar UI
    fetchProfile()
  }
}

onMounted(() => {
  fetchProfile()
  window.addEventListener('storage', onStorage)
  document.addEventListener('click', onDocumentClick)
})

// Re-fetch cuando cambie la ruta (por ejemplo al ir a /login o /profile)
watch(() => route.fullPath, () => {
  fetchProfile()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', onStorage)
  document.removeEventListener('click', onDocumentClick)
})
</script>

<style scoped>
/* (mantén el resto de estilos existentes abajo) */

#title{
  display: flex;
  gap: 10px;
  max-width: 150px;
  font-size: 18px;
  white-space: normal;
  margin-right: 2em;
  font-weight: 500;
}

#title > span{
  margin-top: 8px;
}

nav{
  border-top: 25px solid var(--pri-color);
}

#explorar{
    font-weight: 600;
    font-size: 22px;
}

#navbarNav{
    gap: 20px;
}

/* estilos de barra de busqueda */

#search {
    display: grid;
    grid-area: search;
    grid-template:
        "search" 2.8em
        / 18rem;
    justify-content: center;
    align-content: center;
    justify-items: stretch;
    align-items: stretch;
    background: hsl(0, 0%, 99%);
}

#search input {
    display: block;
    grid-area: search;
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 100%;
    background: none;
    padding: 0 30px 0 60px;
    border: none;
    border-radius: 100px;
    font-size: 24px;
    outline-offset: -8px;
}


#search svg {
    grid-area: search;
    overflow: visible;
    color: var(--pri-color);
    fill: none;
    stroke: currentColor;
}

.burst {
    stroke-width: 3;
}


.circle {
    r: 6;
}

.rect {
    width: 10px;
    height: 10px;
}

.triangle {
    d: path("M0,-6 L7,6 L-7,6 Z");
    stroke-linejoin: round;
}

.plus {
    d: path("M0,-5 L0,5 M-5,0L 5,0");
    stroke-linecap: round;
}

.bar {
    width: 100%;
    height: 100%;
    ry: 50%;
    stroke-width: 10;
    animation: bar-in 900ms 3s both;
}

.magnifier {
    animation: magnifier-in 600ms 3.6s both;
    transform-box: fill-box;
    color: black;
}


.magnifier .glass {
    cx: 27;
    cy: 27;
    r: 8;
    stroke-width: 3;
}
.magnifier .handle {
    stroke-width: 3;
}

#results {
    grid-area: results;
    background: hsl(0, 0%, 95%);
}

@media (max-width: 767px) {
  #search {
    grid-template:
        "search" 2.2em
        / 15rem;
    width: fit-content;
}

}	

#mainView{
    padding-left: 0;
    padding-right: 0;
}

/* Nuevos estilos para foto + nombre en header (ampliados) */
.miperfil {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.profile-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;              /* más espacio entre avatar y nombre */
  text-decoration: none;
  color: inherit;
  padding: 6px 8px;
  border-radius: 8px;
  transition: background .12s ease, transform .08s ease;
}
.profile-link:hover {
  background: rgba(0,0,0,0.04);
  transform: translateY(-1px);
}

/* Avatar más grande */
.avatar {
  width: 56px;            /* más grande que antes */
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 4px 10px rgba(2,6,23,0.08);
}

/* Nombre más legible */
.username {
  font-weight: 700;
  font-size: 17px;
  line-height: 1;
  color: var(--text-color, inherit);
}

/* Ajustes responsivos: reducir un poco en pantallas medias/pequeñas */
@media (max-width: 991px) {
  .avatar {
    width: 44px;
    height: 44px;
  }
  .username {
    font-size: 15px;
  }
  .profile-link {
    gap: 10px;
  }
}

/* ===== Estilos del dropdown del profile ===== */
.profile-container {
  position: relative;
}

.profile-button {
  background: none;
  border: none;
  padding: 6px 8px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.profile-menu {
  position: absolute;

  background: var(--card-bg, #fff);
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 8px;
  list-style: none;
  padding: 6px 0;
  margin: 0;
  min-width: 200px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.12);
  z-index: 1000;
}

.profile-menu .menu-item {
  display: block;
  padding: 10px 14px;
  color: var(--text-color, inherit);
  text-decoration: none;
  white-space: nowrap;
}

.profile-menu .menu-item:hover,
.profile-menu .menu-item:focus {
  background: rgba(0,0,0,0.03);
}

.profile-menu .divider {
  height: 1px;
  background: rgba(0,0,0,0.06);
  margin: 6px 8px;
  border-radius: 1px;
}
</style>
