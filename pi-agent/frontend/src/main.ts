import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useUserStore } from '@/stores/user'

// Vant 样式
import 'vant/lib/index.css'
import 'animate.css'
import './styles/global.css'

async function bootstrapApp() {
	const app = createApp(App)
	const pinia = createPinia()

	app.use(pinia)

	const userStore = useUserStore()
	await userStore.bootstrap()

	app.use(router)
	app.mount('#app')
}

bootstrapApp()
