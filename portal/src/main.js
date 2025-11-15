import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.bundle.js'
import './assets/base.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vue3GoogleLogin from 'vue3-google-login';

const app = createApp(App)

// Usar el nombre con el que importaste el plugin:
app.use(vue3GoogleLogin, {
    clientId: "501426149813-3ldbtlaur9oodqe8eq5rhuqrecjn22s7.apps.googleusercontent.com"
})

app.use(router)

app.mount('#app')