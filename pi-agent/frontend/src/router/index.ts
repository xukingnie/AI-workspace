import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/countdown',
      name: 'countdown',
      component: () => import('@/views/CountdownView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/add',
      name: 'add',
      component: () => import('@/views/AddRecordView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('@/views/StatisticsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings/drawer',
      name: 'settings-drawer',
      component: () => import('@/views/SettingsDrawerView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  if (!userStore.bootstrapped) {
    await userStore.bootstrap()
  }

  const requiresAuth = to.meta.requiresAuth !== false
  if (requiresAuth && !userStore.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
      replace: true,
    }
  }

  if (to.name === 'login' && userStore.isAuthenticated) {
    return { name: 'home', replace: true }
  }

  return true
})

export default router
