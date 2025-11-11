<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { jwtDecode } from 'jwt-decode' // <-- usar named export

const userProfile = ref(null)

const callback = (response) => {
  // ajusta según el shape del response que te devuelve el plugin
  const token = response?.credential || response?.token || response?.access_token
  if (!token) {
    console.warn('No se recibió token en el response:', response)
    return
  }

  try {
    const decoded = jwtDecode(token)
    userProfile.value = decoded
    console.log('Decoded JWT:', decoded)
  } catch (e) {
    console.error('Error decodificando token:', e)
  }
}
</script>

<template>
  <header>
    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />

  <!-- <div>
    <GoogleLogin :callback="callback" />
  </div> -->
</template>

<style scoped>
/* estilos existentes */
</style>
