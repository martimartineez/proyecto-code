<template>
    <div class="review-header">
        <strong class="user-alias">Usuario #<slot name="id"> </slot></strong>
        <span class="rating">Puntuación: <slot name="puntuaciom"></slot>> / 5</span>
        <span class="date"> <slot name="fecha"></slot></span>
    </div>
</template>