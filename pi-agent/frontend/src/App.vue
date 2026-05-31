<template>
  <router-view />
  <van-tabbar route placeholder>
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
import { useNavigationStore } from '@/stores/navigation'

const navStore = useNavigationStore()
</script>
