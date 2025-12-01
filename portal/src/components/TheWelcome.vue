<template>
  <div id="Main-carrousel" class="carousel carousel-dark slide">
    <div class="carousel-inner">
      <div class="carousel-item active" v-if="sitiosHero[0]">
      <!-- aca deberia sacar informacion usando la api. Hardcodeo un ejemplo-->
          <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitiosHero[0].id } }"> 
          <img alt="catedral-ejemplo" :src=" sitiosHero[0].cover_url " class="d-block w-100">    
          <div class="carousel-caption d-md-block w-100">
              <h5>{{ sitiosHero[0].name}}</h5>
          </div>
          </RouterLink>
      </div>
      <div v-else>
        <h5> No hay Sitios disponibles </h5>
      </div>
      <div v-for="sitio in sitiosHero.slice(1)" :key="sitio.id" class="carousel-item">
          <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
          <img alt="museo-ejemplo" :src="sitio.cover_url" class="d-block w-100">    
          <div class="carousel-caption d-md-block w-100">
              <h5> {{sitio.name}}</h5>
          </div>
          </RouterLink>
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

  <div id="sliders">
    <div id="slide-novedades"><RouterLink :to="{name: 'sites', query: { order_by: 'fechaRegistro', order: 'desc'}}" class="d-flex justify-content-center"> 
      <p class="slider-title"> Novedades </p> </RouterLink>
        <div class="row">
            <div id="Novedades" class="carousel slide" data-ride="carousel" data-interval="0">
              <!-- slides -->
              <div class="carousel-item active">
              <div class="row">
                <div class="col-md-4" v-for="sitio in ultimosSitios[0]" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                          <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                          <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.name }}</template>
                      <template #desc>{{ sitio.short_description }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
            <div v-for="(fila, index) in ultimosSitios.slice(1)" :key="index" class="carousel-item">
              <div class="row">
                <div class="col-md-4" v-for="sitio in fila" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                        <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                        <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.name }}</template>
                      <template #desc>{{ sitio.short_description }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
          <button v-if="ultimosSitios[1]" class="carousel-control-prev" type="button" data-bs-target="#Novedades" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button v-if="ultimosSitios[1]" class="carousel-control-next" type="button" data-bs-target="#Novedades" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
          </div>
      </div>
    </div>
    <div id="slide-ratings"> <RouterLink :to="{name: 'sites', query: { order_by: 'rating', order: 'desc'}}" class="d-flex justify-content-center">
      <p class="slider-title"> Mejor Puntuados </p> </RouterLink>
        <div class="row">
            <div id="ratings" class="carousel slide" data-ride="carousel" data-interval="0">
              <!-- slides -->
              <div class="carousel-item active">
              <div class="row">
                <div class="col-md-4" v-for="sitio in sitiosPuntaje[0]" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                          <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                          <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.name }}</template>
                      <template #desc>{{ sitio.short_description }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
            <div v-for="(fila, index) in sitiosPuntaje.slice(1)" :key="index" class="carousel-item">
              <div class="row">
                <div class="col-md-4" v-for="sitio in fila" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                          <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                          <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.name }}</template>
                      <template #desc>{{ sitio.short_description }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
          <button v-if="sitiosRatings[1]" class="carousel-control-prev" type="button" data-bs-target="#ratings" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button v-if="sitiosRatings[1]" class="carousel-control-next" type="button" data-bs-target="#ratings" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
          </div>
      </div>
    </div>
      <div v-if="Favoritos[0]" id="slide-favoritos"><RouterLink :to="{ name: 'profile', query:{ tab: 'favoritos' }}" class="d-flex justify-content-center"> 
        <p class="slider-title"> Favoritos </p> </RouterLink>
        <div class="row">
            <div id="favoritos" class="carousel slide" data-ride="carousel" data-interval="0">
              <!-- slides -->
              <div class="carousel-item active">
              <div class="row">
                <div class="col-md-4" v-for="sitio in Favoritos[0]" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                          <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                          <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.nombre }}</template>
                      <template #desc>{{ sitio.desc_corta }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
            <div v-for="(fila, index) in Favoritos.slice(1)" :key="index" class="carousel-item">
              <div class="row">
                <div class="col-md-4" v-for="sitio in fila" :key="sitio.id">
                  <RouterLink :to="{ name: 'detalle-sitio', params: { id: sitio.id } }">
                    <SliderHome>
                      <template #imagen>
                          <img v-if="sitio.cover_url" :src="sitio.cover_url" class="img-responsive" />  
                          <img v-else src="@/assets/Placeholder.png" class="img-responsive" />
                      </template>
                      <template #titulo>{{ sitio.nombre }}</template>
                      <template #desc>{{ sitio.desc_corta }}</template>
                    </SliderHome>
                  </RouterLink>
                </div>
              </div>
            </div>
          <button v-if="Favoritos[1]" class="carousel-control-prev" type="button" data-bs-target="#favoritos" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button v-if="Favoritos[1]" class="carousel-control-next" type="button" data-bs-target="#favoritos" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
          </div>
      </div>
    </div>
  </div>
</template>



<script setup>
import SliderHome from './Slider-home.vue';
const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md');
import { api } from '@/api/client';
import { ref, onMounted, computed } from 'vue';
const API_URL = import.meta.env.VITE_API_BASE_URL;

const sitios = ref([]);
const sitiosRatings = ref([]);
const sitiosFavoritos = ref([]);

onMounted(async () => {
     sitios.value  = await api.listSites();
     await fetchRatings({});
     await fetchFavoritos();
})



const sitiosHero = computed(() => {
  const lista = sitios.value.data || [];
  return lista.sort((b,a) => new Date(a.fechaRegistro) - new Date(b.fechaRegistro)).slice(0,3);  //agarro los 3 sitios mas recientes
})

const ultimosSitios = computed(() => {  
  var lista = sitios.value.data || [];
  lista = lista.sort((b,a) => new Date(a.fechaRegistro) - new Date(b.fechaRegistro));
  lista = lista.slice(3);     //borro los 3 primeros que uso en el hero
  return sitiosPorFila(lista);
})

const sitiosPuntaje = computed(() => {
  var lista = sitiosRatings.value || [];
  return sitiosPorFila(lista);
})

const Favoritos = computed(() => {
  var lista = sitiosFavoritos.value || [];
  console.log(sitiosPorFila(lista));
  return(sitiosPorFila(lista));
})

const fetchRatings = async() =>{
  const ratings = await Promise.all(  
  sitios.value.data.map(async (site) => {
    const data = await fetchRatingSitio(site.id);
    return {
      ...site,
      rating_avg: data.rating_avg !== "N/A" ? data.rating_avg : 0,
      reviews_count: data.reviews_count
    };
    })
  );
  sitiosRatings.value = ratings.sort((a, b) => b.rating_avg - a.rating_avg);
  console.log(sitiosRatings.value);
}

const fetchRatingSitio= async(id) => {
  const res = await fetch(`${API_URL}/api/sites/${id}`);
  return await res.json();
}


const fetchFavoritos = async() =>{
  try{
    const res = await fetch(`${API_URL}/api/favoritos_usuario`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await res.json();
    sitiosFavoritos.value = data.favoritos || [];
  }
  catch{
    if(res.status === 401 || res.status === 403){
      sitiosFavoritos.value = [];
    }

  }
}

function sitiosPorFila(lista) {    //muestra de a 1 elemento en celular y 3 en pc
  console.log(lista);
  const grupos = [];
  let cant = 0;
  if (window.innerWidth > 767)
    cant = 3;
  else
    cant = 1;
  for (let i = 0; i < lista.length && grupos.length < 3; i += cant) {
      grupos.push(lista.slice(i, i + cant))
  }
  return grupos;
}




</script>

<style>
  #Main-carrousel{    /* estilos para el carrusel principal */
    max-height: 75vh;
    overflow: hidden;
  
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
        font-size: 30px;
        font-weight: 500;
    }

    .sliders-title{
      font-weight: 500;
      font-size: 30px;
      justify-self: center;
    }
    
  .carousel-control-prev-icon,
  .carousel-control-next-icon {
    width: 3rem !important;
    height: 3rem !important;
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
    
  }

  .slider-title{
    font-size: 50px;
    font-weight: bold;
    display: flex;
    align-content: center;
    justify-content: center;
    text-align: center;
    margin: 0px;
    transition: font-size 0.2s ease-in;
  }

  .slider-title:hover{
    font-size: 53px;
  }
/* sliders */
  #sliders{
  
    margin-top: 1.5em;

    .row{
      overflow: hidden;
    }

    a{
      text-decoration: none;
      color: black;
    }

    h4{
      font-size: 1.5rem;
      font-weight: 550;
    }

    .col-md{
      width: 20rem;
    }

    .col-center {
      margin: 0 auto;
      float: none !important;
    }
    .carousel {
      margin: 15px auto 60px;
      overflow: visible;
    }
    .carousel-item {
      text-align: center;
      overflow: hidden;
      padding: 0 20px;
    }

    .carousel-item img {
      max-width: 100%;
      display: inline-block;
    }

    .img-box{
      height: 25vh;
      width: auto;
      overflow: hidden;
    }

    .img-box img{
      width: 100%;
      height: 100%;
      object-fit: fill;
    }

    .btn {
      border-radius: 0;
      font-size: 12px;
      text-transform: uppercase;
      font-weight: bold;
      border: none;
      background: #a177ff;
      padding: 6px 15px;
      margin-top: 5px;
    }
    .btn:hover {
      background: #8c5bff;
    }
    .btn i {
      font-size: 14px;
      font-weight: bold;
      margin-left: 5px;
    }
    .thumb-wrapper {
      margin: 5px;
      text-align: left;
      background: var(--pri-color);
      box-shadow: 0px 2px 2px rgba(0,0,0,0.1);
      height: 98%;
      width: 85%;
      justify-self: center;
    }
    .thumb-content {
      display: flex;
      flex-direction: column;
      padding: 15px;
      font-size: 13px;
    }
    .thumb-content p{
      font-size: 19px;
    }
    .carousel-control-prev, .carousel-control-next {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 3px solid rgba(0, 0, 0, 0.8);
      background: none;
      top: 50%;
      transform: translateY(-50%);
    }
    .carousel-control-prev-icon,
    .carousel-control-next-icon {
      filter: invert(0.8);
      width: 20px;
      height: 20px;
    }
    .carousel-indicators [data-bs-target] {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: #ababab;
    }
    .carousel-indicators .active {
      background-color: #555;
    }

  .carousel-item .row {
    display: flex;
    justify-content: center;
    align-items: stretch;
  }

  .carousel-item .col-sm-4 {
    display: flex;
  }

}

</style>