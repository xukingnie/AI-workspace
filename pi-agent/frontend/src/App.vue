<template>
  <router-view />
  <van-tabbar v-model="active" route placeholder>
    <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
    <van-tabbar-item icon="add-o" to="/add">记账</van-tabbar-item>
    <van-tabbar-item icon="chart-trending-o" to="/stats">统计</van-tabbar-item>
    <van-tabbar-item icon="setting-o" to="/settings">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const active = ref(0)
</script>
