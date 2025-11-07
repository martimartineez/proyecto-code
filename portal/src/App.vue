<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>


<template>
  <header>
      <nav class="navbar navbar-expand-lg">
        <div class="container-fluid p-3">
          <RouterLink to="/" class="navbar-brand" id="title">
            <img alt="UNLP logo" class="logo" src="@/assets/UNLP_Logo.svg" width="80" height="80" />
            Sitios Historicos
          </RouterLink>
          <div class="collapse navbar-collapse" id="navbarNav">
            <RouterLink to="" class="nav-link m-2">Explorar</RouterLink>
            <RouterLink to="" class="nav-link m-2">¿Quienes somos?</RouterLink> 
        </div>
        <div class="container-fluid ms-5">
          <form class="d-flex" role="search">
            <input class="form-control w-auto me-2" type="search" placeholder="Search" aria-label="Search"/>
            <button class="btn btn-outline-success" type="submit">Search</button>
          </form>
        </div>
          <RouterLink to="" class="nav-link d-none d-lg-flex me-5">Mi perfil</RouterLink>
      </div>
    </nav>
  </header>
  <div class="container-md pt-4">
    <RouterView />
  </div>
  
</template>

<style scoped>

#title{
  width:"5px"
}

nav{
  border-top: 25px solid var(--pri-color);
}
</style>
