import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/countdown',
    },
    {
      path: '/countdown',
      name: 'countdown',
      component: () => import('@/views/CountdownView.vue'),
    },
    {
      path: '/add',
      name: 'add',
      component: () => import('@/views/AddRecordView.vue'),
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('@/views/StatisticsView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
    },
    {
      path: '/settings/drawer',
      name: 'settings-drawer',
      component: () => import('@/views/SettingsDrawerView.vue'),
    },
  ],
})

export default router
