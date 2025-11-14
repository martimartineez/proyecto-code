<template>
    <div class="thumb-wrapper">
        <div class="img-box">
            <slot name="imagen"> </slot>
        </div>
        <div class="thumb-content">
            <h4><slot name="titulo"> </slot></h4>
            <p> <slot name="desc"> </slot></p>
        </div>
    </div>   
</template> 
