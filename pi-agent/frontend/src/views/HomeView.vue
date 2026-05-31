<template>
  <div class="home-page">
    <div class="hero-head">
      <h2>快捷入口</h2>
      <p>点击卡片快速跳转到四个核心页面</p>
    </div>

    <div class="route-cards">
      <div class="route-card card-countdown" @click="goTo('countdown')">
        <div class="card-title">倒计时</div>
        <div class="card-desc">发薪日与月历</div>
      </div>
      <div class="route-card card-stats" @click="goTo('stats')">
        <div class="card-title">统计</div>
        <div class="card-desc">收支分析视图</div>
      </div>
      <div class="route-card card-add" @click="goTo('add')">
        <div class="card-title">记账</div>
        <div class="card-desc">快速新增账单</div>
      </div>
      <div class="route-card card-settings" @click="goTo('settings')">
        <div class="card-title">设置</div>
        <div class="card-desc">页面显隐与排序</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goTo(name: 'countdown' | 'stats' | 'add' | 'settings') {
  router.push({ name })
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: radial-gradient(circle at top right, #e9f7ff 0%, #f7f8fa 55%);
  padding: 14px;
  padding-bottom: 72px;
}

.hero-head {
  margin-bottom: 12px;
}

.hero-head h2 {
  font-size: 22px;
  color: #2c3e50;
  margin: 0;
}

.hero-head p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #5f6c7b;
}

.route-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.route-card {
  min-height: 130px;
  border-radius: 14px;
  padding: 14px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.route-card:active {
  transform: scale(0.98);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.14);
}

.card-title {
  font-size: 20px;
  font-weight: 700;
}

.card-desc {
  margin-top: 6px;
  font-size: 12px;
  opacity: 0.92;
}

.card-countdown {
  background: linear-gradient(145deg, #7f53ac 0%, #647dee 100%);
}

.card-add {
  background: linear-gradient(145deg, #11998e 0%, #38ef7d 100%);
}

.card-stats {
  background: linear-gradient(145deg, #f46b45 0%, #eea849 100%);
}

.card-settings {
  background: linear-gradient(145deg, #4b6cb7 0%, #182848 100%);
}
</style>
