<template>
    <div id="formulario">
        <form @submit.prevent="postReview" class="row g-2 p-2 mt-4" ref="formulario">
            <label for="reseña" class="form-label" >Reseña</label>
            <div id="puntaje-estrellas">
                <div class="rating-group">
                    <label aria-label="0.5 stars" class="rating__label rating__label--half" for="rating2-05"><i class="rating__icon rating__icon--star fa fa-star-half"></i></label>
                    <input class="rating__input" name="rating" id="rating2-05" value=0.5 type="radio">
                    <label aria-label="1 star" class="rating__label" for="rating2-10"><i class="rating__icon rating__icon--star fa fa-star"></i></label>
                    <input class="rating__input" name="rating" id="rating2-10" value=1 type="radio">
                    <label aria-label="1.5 stars" class="rating__label rating__label--half" for="rating2-15"><i class="rating__icon rating__icon--star fa fa-star-half"></i></label>
                    <input class="rating__input" name="rating" id="rating2-15" value=1.5 type="radio">
                    <label aria-label="2 stars" class="rating__label" for="rating2-20"><i class="rating__icon rating__icon--star fa fa-star"></i></label>
                    <input class="rating__input" name="rating" id="rating2-20" value=2 type="radio">
                    <label aria-label="2.5 stars" class="rating__label rating__label--half" for="rating2-25"><i class="rating__icon rating__icon--star fa fa-star-half"></i></label>
                    <input class="rating__input" name="rating" id="rating2-25" value=2.5 type="radio" checked>
                    <label aria-label="3 stars" class="rating__label" for="rating2-30"><i class="rating__icon rating__icon--star fa fa-star"></i></label>
                    <input class="rating__input" name="rating" id="rating2-30" value=3 type="radio">
                    <label aria-label="3.5 stars" class="rating__label rating__label--half" for="rating2-35"><i class="rating__icon rating__icon--star fa fa-star-half"></i></label>
                    <input class="rating__input" name="rating" id="rating2-35" value=3.5 type="radio">
                    <label aria-label="4 stars" class="rating__label" for="rating2-40"><i class="rating__icon rating__icon--star fa fa-star"></i></label>
                    <input class="rating__input" name="rating" id="rating2-40" value=4 type="radio">
                    <label aria-label="4.5 stars" class="rating__label rating__label--half" for="rating2-45"><i class="rating__icon rating__icon--star fa fa-star-half"></i></label>
                    <input class="rating__input" name="rating" id="rating2-45" value=4.5 type="radio">
                    <label aria-label="5 stars" class="rating__label" for="rating2-50"><i class="rating__icon rating__icon--star fa fa-star"></i></label>
                    <input class="rating__input" name="rating" id="rating2-50" value=5 type="radio">
                </div>
            </div>
            <textarea class="form-control" name="comment" id="reseña" rows="3"></textarea>
            <div class="col-12">
             <button type="submit" class="btn btn-primary" id="enviar"> Enviar </button>
            </div>
        </form>
    </div>

</template>

<script setup>
import 'font-awesome/css/font-awesome.min.css';
import { ref } from 'vue';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'; 
const formulario = ref();

const props = defineProps({
  siteId: { type: Number, required: true },
});

async function postReview() {
  const formData = new FormData(formulario.value);
  const data = Object.fromEntries(formData.entries());
  data.site_id = props.siteId;

  try {
    const respuesta = await fetch(`${baseUrl}/api/sites/${props.siteId}/reviews`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    // --- AUTENTICACIÓN / REDIRECCIÓN ---
    if (respuesta.status === 401 || respuesta.status === 403) {
      // Guardamos la URL actual para volver después de loguearse
      localStorage.setItem('redirectAfterLogin', window.location.pathname);

      // Redirigir al login
      window.location.href = '/login';
      return;
    }
    // -----------------------------------

    if (!respuesta.ok) {
      console.error("Error al publicar la reseña:", respuesta.statusText);
      return;
    }

    // Si todo salió bien, recargar reseñas o lo que necesites
    console.log("Reseña enviada correctamente");

  } catch (e) {
    console.error("Error en postReview:", e);
  }
}

</script>



<style>

/* Puntaje con estrellas sacado de freefrontend */
#puntaje-estrellas {

  margin: 0px; 
  padding: 0px;


  .rating-group {
    display: inline-flex;
  }
  
  .rating__icon {
    pointer-events: none;
  }
  
  .rating__input {
   position: absolute !important;
   left: -9999px !important;
  }

  .rating__label {
    cursor: pointer;
    padding: 0 0.1em;
    font-size: 1.5rem;
  }

  .rating__label--half {
    padding-right: 0;
    margin-right: -0.6em;
    z-index: 2;
  }
  
  .rating__icon--star {
    color: orange;
  }
  
  .rating__icon--none {
    color: #eee;
  }

  .rating__input--none:checked + .rating__label .rating__icon--none {
    color: red;
  }

  .rating__input:checked ~ .rating__label .rating__icon--star {
    color: #ddd;
  }
  
  .rating-group:hover .rating__label .rating__icon--star,
  .rating-group:hover .rating__label--half .rating__icon--star {
    color: orange;
  }

  .rating__input:hover ~ .rating__label .rating__icon--star,
  .rating__input:hover ~ .rating__label--half .rating__icon--star {
    color: #ddd;
  }
  
  .rating-group:hover .rating__input--none:not(:hover) + .rating__label .rating__icon--none {
     color: #eee;
  }

  .rating__input--none:hover + .rating__label .rating__icon--none {
    color: red;
  }
}

#enviar{
  margin-top: 0.5rem;
}

.form-label{
  font-size: 1.8rem;
  font-weight: 500;
}

</style>