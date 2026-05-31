<template>
  <div class="countdown-page">
    <van-nav-bar title="倒计时">
      <template #left>
        <van-icon name="home-o" size="18" @click="goToHome" />
      </template>
    </van-nav-bar>

    <!-- 倒计时卡片 -->
    <div class="countdown-card">
      <div class="countdown-header">
        <span>距发薪日</span>
        <van-icon name="setting-o" @click="openPayrollSettings" />
      </div>
      <div class="countdown-days">
        <span class="days">{{ countdownDays }}</span>
        <span class="unit">天</span>
      </div>
      <div class="countdown-date">
        <span>发薪日：每月{{ payday }}日</span>
        <span v-if="nextPayday">（{{ nextPayday }}）</span>
      </div>
      <div class="countdown-salary">工资金额：{{ formatMoney(salaryAmount) }}</div>
    </div>

    <!-- 日历 Wrapper -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'
import { useStatisticsStore } from '@/stores/statistics'
import { useCategoryStore } from '@/stores/category'
import { useTransactionStore } from '@/stores/transaction'
import { usePayrollStore } from '@/stores/payroll'
import type { DailyStat } from '@/types'

const statsStore = useStatisticsStore()
const categoryStore = useCategoryStore()
const transactionStore = useTransactionStore()
const payrollStore = usePayrollStore()
const router = useRouter()

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

function calendarPrevMonth() {
  if (calendarMonth.value === 1) {
    calendarYear.value--
    calendarMonth.value = 12
  } else {
    calendarMonth.value--
  }
  loadCalendarData()
}

function calendarNextMonth() {
  if (calendarMonth.value === 12) {
    calendarYear.value++
    calendarMonth.value = 1
  } else {
    calendarMonth.value++
  }
  loadCalendarData()
}

async function loadCalendarData() {
  await statsStore.fetchDaily(calendarYear.value, calendarMonth.value)
  const map: Record<string, DailyStat> = {}
  for (const stat of statsStore.dailyStats) {
    map[stat.date] = stat
  }
  dailyMap.value = map
}

const payday = computed(() => payrollStore.payday)
const salaryAmount = computed(() => payrollStore.salaryAmount)

const countdownDays = computed(() => {
  const today = dayjs()
  let target = dayjs(`${today.year()}-${today.month() + 1}-${payday.value}`)
  if (target.isBefore(today, 'day') || target.isSame(today, 'day')) {
    target = target.add(1, 'month')
  }
  return target.diff(today, 'day')
})

const nextPayday = computed(() => {
  const today = dayjs()
  let target = dayjs(`${today.year()}-${today.month() + 1}-${payday.value}`)
  if (target.isBefore(today, 'day') || target.isSame(today, 'day')) {
    target = target.add(1, 'month')
  }
  return target.format('MM月DD日')
})

function openPayrollSettings() {
  router.push({
    name: 'settings-drawer',
    query: { returnTo: 'countdown' },
  })
}

function goToHome() {
  router.push({ name: 'home' })
}

const dailyMap = ref<Record<string, DailyStat>>({})

function getDaySummary(date: Date) {
  const key = dayjs(date).format('YYYY-MM-DD')
  return dailyMap.value[key] || null
}

function onDateSelect(date: Date) {
  selectedDate.value = dayjs(date).format('YYYY-MM-DD')
}

async function loadData() {
  await ensureSalaryTransaction()
  await loadCalendarData()
}

async function ensureSalaryTransaction() {
  if (salaryAmount.value <= 0) return

  await categoryStore.fetchCategories()

  const salaryCategory =
    categoryStore.categories.find((item) => item.type === 'income' && item.name === '工资') ??
    categoryStore.categories.find((item) => item.type === 'income')

  if (!salaryCategory) return

  const today = dayjs()
  const paydayDate = dayjs(
    `${today.year()}-${String(today.month() + 1).padStart(2, '0')}-${String(payday.value).padStart(2, '0')}`,
  )
  if (today.isBefore(paydayDate, 'day')) return

  const salaryDate = paydayDate.format('YYYY-MM-DD')
  await transactionStore.fetchTransactions({
    type: 'income',
    category_id: salaryCategory.id,
    start_date: salaryDate,
    end_date: salaryDate,
    page_size: 100,
  })

  const exists = transactionStore.transactions.some(
    (item) =>
      item.type === 'income' &&
      item.category_id === salaryCategory.id &&
      item.transaction_date === salaryDate,
  )

  if (exists) return

  await transactionStore.addTransaction({
    amount: salaryAmount.value,
    type: 'income',
    category_id: salaryCategory.id,
    transaction_date: salaryDate,
    note: '工资',
  })
}

function formatMoney(val?: number) {
  if (val == null) return '0.00'
  return Number(val).toFixed(2)
}

function formatShort(val: number) {
  if (val >= 10000) return (val / 10000).toFixed(1) + 'w'
  if (val >= 1000) return (val / 1000).toFixed(1) + 'k'
  return String(Math.round(val))
}

onMounted(loadData)
</script>

<style scoped>
.countdown-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.countdown-card {
  background: white;
  margin: 0 12px 12px;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
}

.countdown-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.countdown-days {
  margin: 8px 0;
}

.countdown-days .days {
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
}

.countdown-days .unit {
  font-size: 16px;
  color: #667eea;
}

.countdown-date {
  font-size: 13px;
  color: #999;
}

.countdown-salary {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.calendar-card {
  background: white;
  margin: 0 12px;
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
</style>
