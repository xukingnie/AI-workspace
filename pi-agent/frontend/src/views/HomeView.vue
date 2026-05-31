<template>
  <div class="home-page">
    <van-nav-bar title="首页" />

    <div class="overview-card">
      <div class="month-selector">
        <van-icon name="arrow-left" @click="prevMonth" />
        <span class="month-text">{{ year }}年{{ month }}月</span>
        <van-icon name="arrow" @click="nextMonth" />
      </div>
      <div class="overview-numbers">
        <div class="num-item clickable" @click="goToStats('income')">
          <span class="label">收入</span>
          <span class="value income">
            {{ formatMoney(statsStore.overview?.total_income) }}
          </span>
        </div>
        <div class="num-item clickable" @click="goToStats('expense')">
          <span class="label">支出</span>
          <span class="value expense">
            {{ formatMoney(statsStore.overview?.total_expense) }}
          </span>
        </div>
        <div class="num-item clickable" @click="goToStats('balance')">
          <span class="label">结余</span>
          <span class="value" :class="balanceClass">
            {{ formatMoney(statsStore.overview?.balance) }}
          </span>
        </div>
      </div>
    </div>

    <div class="hero-head">
      <h2>快捷入口</h2>
    </div>

    <div class="route-cards">
      <div
        v-for="card in visibleCards"
        :key="card.name"
        class="route-card"
        :class="card.className"
        @click="goTo(card.name)"
      >
        <div class="card-title">{{ card.title }}</div>
        <div class="card-desc">{{ card.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { useStatisticsStore } from '@/stores/statistics'

const router = useRouter()
const navStore = useNavigationStore()
const statsStore = useStatisticsStore()

const now = dayjs()
const year = ref(now.year())
const month = ref(now.month() + 1)

type HomeRouteName = 'countdown' | 'stats' | 'add' | 'settings'

const cards = computed(() => [
  {
    name: 'countdown' as const,
    title: '倒计时',
    desc: '发薪日与月历',
    className: 'card-countdown',
    visible: navStore.homeCardVisible.countdown,
  },
  {
    name: 'add' as const,
    title: '记账',
    desc: '快速新增账单',
    className: 'card-add',
    visible: navStore.homeCardVisible.add,
  },
  {
    name: 'stats' as const,
    title: '统计',
    desc: '收支分析视图',
    className: 'card-stats',
    visible: navStore.homeCardVisible.stats,
  },
  {
    name: 'settings' as const,
    title: '设置',
    desc: '页面显隐与排序',
    className: 'card-settings',
    visible: true,
  },
])

const visibleCards = computed(() => cards.value.filter((item) => item.visible))

function goTo(name: HomeRouteName) {
  router.push({ name })
}

function prevMonth() {
  if (month.value === 1) {
    year.value--
    month.value = 12
  } else {
    month.value--
  }
  statsStore.fetchOverview(year.value, month.value)
}

function nextMonth() {
  if (month.value === 12) {
    year.value++
    month.value = 1
  } else {
    month.value++
  }
  statsStore.fetchOverview(year.value, month.value)
}

function goToStats(type: 'income' | 'expense' | 'balance') {
  router.push({
    name: 'stats',
    query: {
      type,
      year: String(year.value),
      month: String(month.value),
    },
  })
}

const balanceClass = computed(() => {
  const bal = statsStore.overview?.balance ?? 0
  if (bal > 0) return 'positive'
  if (bal < 0) return 'negative'
  return ''
})

async function loadData() {
  await statsStore.fetchOverview(year.value, month.value)
}

function formatMoney(val?: number) {
  if (val == null) return '0.00'
  return Number(val).toFixed(2)
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.home-page {
  background: radial-gradient(circle at top right, #e9f7ff 0%, #f7f8fa 55%);
  padding: 14px;
  padding-bottom: 72px;

  .overview-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px;
    margin: 0 0 12px;
    border-radius: 12px;
  }

  .month-selector {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 12px;
  }

  .month-text {
    font-size: 18px;
    font-weight: bold;
  }

  .overview-numbers {
    display: flex;
    justify-content: space-around;
  }

  .num-item {
    text-align: center;
  }

  .num-item.clickable {
    cursor: pointer;
  }

  .num-item .label {
    font-size: 12px;
    opacity: 0.8;
  }

  .num-item .value {
    display: block;
    font-size: 20px;
    font-weight: bold;
    margin-top: 4px;
  }

  .num-item .value.income {
    color: #a8f0a8;
  }

  .num-item .value.expense {
    color: #ffb3b3;
  }

  .num-item .value.positive {
    color: #a8f0a8;
  }

  .num-item .value.negative {
    color: #ffb3b3;
  }

  .hero-head {
    margin-bottom: 12px;

    h2 {
      font-size: 22px;
      color: #2c3e50;
      margin: 0;
    }

    p {
      margin: 6px 0 0;
      font-size: 13px;
      color: #5f6c7b;
    }
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

    &:active {
      transform: scale(0.98);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.14);
    }
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
}
</style>
