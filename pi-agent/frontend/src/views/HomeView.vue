<template>
  <div class="home-page">
    <van-nav-bar title="首页" />

    <div class="calendar-card">
      <van-calendar
        :model-value="selectedDate"
        :min-date="calendarMinDate"
        :max-date="calendarMaxDate"
        :default-date="calendarDefaultDate"
        :show-confirm="false"
        :show-title="false"
        :show-subtitle="false"
        :poppable="false"
        :allow-same-day="true"
        @select="onDateSelect"
      >
        <template #bottom-info="{ date }">
          <div v-if="getDaySummary(date)" class="calendar-mark">
            <span v-if="getDaySummary(date)!.income > 0" class="mark-income">
              {{ formatShort(getDaySummary(date)!.income) }}
            </span>
            <span v-if="getDaySummary(date)!.expense > 0" class="mark-expense">
              {{ formatShort(getDaySummary(date)!.expense) }}
            </span>
          </div>
        </template>
      </van-calendar>
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
import type { DailyStat } from '@/types'

const router = useRouter()
const navStore = useNavigationStore()
const statsStore = useStatisticsStore()

const now = dayjs()
const selectedDate = ref(now.format('YYYY-MM-DD'))

const calendarYear = ref(now.year())
const calendarMonth = ref(now.month() + 1)

const calendarMinDate = computed(() => {
  const d = dayjs(`${calendarYear.value}-${String(calendarMonth.value).padStart(2, '0')}-01`)
  return d.toDate()
})

const calendarMaxDate = computed(() => {
  const d = dayjs(`${calendarYear.value}-${String(calendarMonth.value).padStart(2, '0')}-01`).endOf(
    'month',
  )
  return d.toDate()
})

const calendarDefaultDate = computed(() =>
  dayjs(`${calendarYear.value}-${String(calendarMonth.value).padStart(2, '0')}-01`).toDate(),
)

const dailyMap = ref<Record<string, DailyStat>>({})

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
    name: 'stats' as const,
    title: '统计',
    desc: '收支分析视图',
    className: 'card-stats',
    visible: navStore.homeCardVisible.stats,
  },
  {
    name: 'add' as const,
    title: '记账',
    desc: '快速新增账单',
    className: 'card-add',
    visible: navStore.homeCardVisible.add,
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

async function loadCalendarData() {
  await statsStore.fetchDaily(calendarYear.value, calendarMonth.value)
  const map: Record<string, DailyStat> = {}
  for (const stat of statsStore.dailyStats) {
    map[stat.date] = stat
  }
  dailyMap.value = map
}

function getDaySummary(date: Date) {
  const key = dayjs(date).format('YYYY-MM-DD')
  return dailyMap.value[key] || null
}

function onDateSelect(date: Date) {
  selectedDate.value = dayjs(date).format('YYYY-MM-DD')
}

async function loadData() {
  await loadCalendarData()
}

function formatShort(val: number) {
  if (val >= 10000) return (val / 10000).toFixed(1) + 'w'
  if (val >= 1000) return (val / 1000).toFixed(1) + 'k'
  return String(Math.round(val))
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.home-page {
  background: radial-gradient(circle at top right, #e9f7ff 0%, #f7f8fa 55%);
  padding: 14px;
  padding-bottom: 72px;

  .calendar-card {
    background: white;
    margin: 0 0 12px;
    border-radius: 12px;
    overflow: hidden;
  }

  .calendar-mark {
    display: flex;
    gap: 2px;
    font-size: 10px;
    flex-wrap: wrap;
  }

  .mark-income {
    color: #07c160;
  }

  .mark-expense {
    color: #ee0a24;
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
