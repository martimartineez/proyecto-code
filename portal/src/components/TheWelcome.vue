<script setup>
import SlidersHome from './Sliders-home.vue';
const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <div id="Main-carrousel" class="carousel slide">
    <div class="carousel-inner">
      <div class="carousel-item active">
      <!-- aca deberia sacar informacion usando la api. Hardcodeo un ejemplo-->
          <img alt="catedral-ejemplo" src="@/assets/catedral_frente.jpg" class="d-block w-100">
          <div class="carousel-caption d-md-block w-100">
              <h5>Programa Nacional de Registro y Preservacion de Sitios Historicos</h5>
          </div>
      </div>
      <div class="carousel-item">
          <img alt="museo-ejemplo" src="@/assets/museoLP.jpg" class="d-block w-100">
          <div class="carousel-caption d-md-block w-100">
              <h5> Museo de La Plata</h5>
          </div>
      </div>
    </div>
    <button class="carousel-control-prev" type="button" data-bs-target="#Main-carrousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
  <button class="carousel-control-next" type="button" data-bs-target="#Main-carrousel" data-bs-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Next</span>
  </button>
  </div>
  <SlidersHome />
</template>

<style>
  #Main-carrousel{
    max-height: 75vh;
    overflow: hidden;
  }
  
  .carousel-item img {
    height: 75vh;
    width: 100%;
    object-fit: cover;
  }

  .carousel-caption{
    color: white; 
    left: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.315);
  }

  .carousel-caption h5{
      font-size: 25px;
      font-weight: 500;
  }

  .sliders-title{
    font-weight: 500;
    font-size: 30px;
    justify-self: center;
  }

  @media (max-width: 767px) {
      #Main-carrousel{
        max-height: 30vh;
        overflow: hidden;
      }
      .carousel-item img {
        height: 30vh;
      }
      
      .carousel-caption{
        display: block;
        margin: 0;
        padding: 10px;
      }
      .carousel-caption h5{
        font-size: 20px;
        font-weight: 500;
      }
    }

</style>