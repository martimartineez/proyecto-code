import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vue3GoogleLogin from 'vue3-google-login';

const app = createApp(App)

app.use(vue3GoogleLogin, {
    clientId: "501426149813-3ldbtlaur9oodqe8eq5rhuqrecjn22s7.apps.googleusercontent.com",
    scope: 'profile email',
    prompt: 'select_account'
})

app.use(router)

app.mount('#app')
