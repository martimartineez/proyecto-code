<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>


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
				<RouterLink to="" class="nav-link m-2">¿Quienes somos?</RouterLink> 
				<!-- barra de busqueda  -->
				<div class="container-fluid p-0 pt-2">
					<form class="d-flex" role="search">
						<div id="search">
						<svg viewBox="0 0 420 60" xmlns="http://www.w3.org/2000/svg">
							<rect class="bar"/>
							<g class="magnifier">
								<circle class="glass"/>
								<line class="handle" x1="32" y1="32" x2="44" y2="44"></line>
							</g>
						</svg>
						<input type=search name=q aria-label="Search for inspiration"/>
						</div>
					</form>
				</div>
				<RouterLink to="" class="nav-link d-none d-lg-flex me-5">Mi perfil</RouterLink>
			</div>
      </div>
    </nav>
  </header>
<div class="container-md pt-3" id="mainView">
    <RouterView />
</div>
  
</template>

<style scoped>


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
	font: 24px/1 system-ui, sans-serif;
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
</style>
