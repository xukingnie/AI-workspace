<template>
  <router-view />
  <van-tabbar v-if="userStore.isAuthenticated" route placeholder>
    <van-tabbar-item
      v-for="item in navStore.configurableTabs"
      :key="item.key"
      :icon="item.icon"
      :to="item.to"
    >
      {{ item.label }}
    </van-tabbar-item>
    <van-tabbar-item icon="setting-o" to="/settings">设置</van-tabbar-item>
  </van-tabbar>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { useUserStore } from '@/stores/user'

const navStore = useNavigationStore()
const userStore = useUserStore()
const router = useRouter()

async function handleUnauthorized() {
  if (!userStore.isAuthenticated) return
  await userStore.logout()
  if (router.currentRoute.value.name !== 'login') {
    router.replace({
      name: 'login',
      query: { redirect: router.currentRoute.value.fullPath },
    })
  }
}

onMounted(() => {
  window.addEventListener('auth:unauthorized', handleUnauthorized)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth:unauthorized', handleUnauthorized)
})
</script>
