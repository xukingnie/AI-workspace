<template>
  <div class="stats-page">
    <van-nav-bar title="统计" />

    <!-- 月份选择 -->
    <div class="month-bar">
      <van-icon name="arrow-left" @click="prevMonth" />
      <span>{{ year }}年{{ month }}月</span>
      <van-icon name="arrow" @click="nextMonth" />
    </div>

    <!-- 概览卡片 -->
    <div class="overview-row">
      <div class="stat-card income-bg" @click="selectTab('income')">
        <span class="label">收入</span>
        <span class="value">{{ formatMoney(statsStore.overview?.total_income) }}</span>
      </div>
      <div class="stat-card expense-bg" @click="selectTab('expense')">
        <span class="label">支出</span>
        <span class="value">{{ formatMoney(statsStore.overview?.total_expense) }}</span>
      </div>
      <div class="stat-card balance-bg">
        <span class="label">结余</span>
        <span class="value" :class="{ negative: (statsStore.overview?.balance ?? 0) < 0 }">
          {{ formatMoney(statsStore.overview?.balance) }}
        </span>
      </div>
    </div>

    <!-- 分类统计 -->
    <div class="chart-section">
      <van-tabs v-model:active="activeTab" @change="onTabChange">
        <van-tab v-for="tab in statTabs" :key="tab.type" :title="tab.title">
          <div class="chart-wrap">
            <div v-if="getStats(tab.type).length === 0" class="empty">暂无数据</div>
            <div v-else class="category-list">
              <div
                v-for="item in getStats(tab.type)"
                :key="item.category_id"
                class="category-stat-item"
              >
                <div class="category-meta">
                  <span class="category-icon">{{ getCategoryEmoji(item.category_icon) }}</span>
                  <span class="name">{{ item.category_name }}</span>
                </div>
                <div class="bar-wrap">
                  <div
                    class="bar"
                    :class="{ 'income-bar': tab.type === 'income' }"
                    :style="getBarStyle(tab.type, item.percentage)"
                  />
                </div>
                <span class="stat-value">
                  {{ formatMoney(item.total) }}（{{ item.percentage }}%）
                </span>
              </div>
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </div>

    <div class="notes-section">
      <div class="section-header">
        <div>
          <div class="section-title">本月备注</div>
          <div class="section-subtitle">{{ activeTypeLabel }}中已填写备注的记录</div>
        </div>
        <span class="note-count">{{ filteredNotes.length }}条</span>
      </div>

      <div v-if="filteredNotes.length === 0" class="empty notes-empty">本月暂无备注</div>

      <div v-else class="note-list">
        <div v-for="item in filteredNotes" :key="item.id" class="note-item">
          <div class="note-top">
            <div class="note-category">
              <span class="category-icon note-icon">{{
                getCategoryEmoji(item.category?.icon)
              }}</span>
              <span>{{ item.category?.name || '未分类' }}</span>
            </div>
            <span class="note-amount" :class="item.type">
              {{ item.type === 'expense' ? '-' : '+' }}{{ formatMoney(item.amount) }}
            </span>
          </div>
          <div class="note-content">{{ item.note }}</div>
          <div class="note-date">{{ formatDate(item.transaction_date) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { useRoute } from 'vue-router'
import { useStatisticsStore } from '@/stores/statistics'
import { useTransactionStore } from '@/stores/transaction'
import { getCategoryIcon } from '@/options/categories'
import type { CategoryStat, Transaction } from '@/types'

type StatisticsType = Transaction['type']

const statsStore = useStatisticsStore()
const transactionStore = useTransactionStore()
const route = useRoute()

const statTabs = [
  { title: '收入分类', type: 'income' as const },
  { title: '支出分类', type: 'expense' as const },
]
const now = dayjs()
const year = ref(now.year())
const month = ref(now.month() + 1)
const activeTab = ref(0)
const statsByType = ref<Record<StatisticsType, CategoryStat[]>>({
  income: [],
  expense: [],
})

const activeType = computed<StatisticsType>(() => statTabs[activeTab.value]?.type ?? 'income')
const activeTypeLabel = computed(() => (activeType.value === 'income' ? '收入' : '支出'))

function toNumber(value: unknown) {
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

function resolveRouteType(value: unknown): StatisticsType | null {
  if (value === 'income' || value === 'expense') {
    return value
  }

  return null
}

function syncRouteState() {
  const routeType = resolveRouteType(route.query.type)
  if (routeType) {
    activeTab.value = statTabs.findIndex((tab) => tab.type === routeType)
  }

  const queryYear = toNumber(route.query.year)
  const queryMonth = toNumber(route.query.month)
  if (queryYear && queryMonth && queryMonth >= 1 && queryMonth <= 12) {
    year.value = queryYear
    month.value = queryMonth
  }
}

const filteredNotes = computed(() => {
  return transactionStore.transactions.filter(
    (item) => item.type === activeType.value && item.note?.trim(),
  )
})

async function changeMonth(offset: number) {
  const nextMonth = dayjs(`${year.value}-${String(month.value).padStart(2, '0')}-01`).add(
    offset,
    'month',
  )

  year.value = nextMonth.year()
  month.value = nextMonth.month() + 1
  await loadData()
}

async function prevMonth() {
  await changeMonth(-1)
}

async function nextMonth() {
  await changeMonth(1)
}

async function selectTab(type: StatisticsType) {
  const nextTab = statTabs.findIndex((tab) => tab.type === type)
  if (nextTab === activeTab.value) {
    await loadCategoryStats(type)
    return
  }

  activeTab.value = nextTab
}

async function onTabChange(index: number) {
  activeTab.value = Number(index)
  await loadCategoryStats()
}

async function loadData(type = activeType.value) {
  await Promise.all([
    statsStore.fetchOverview(year.value, month.value),
    loadTransactions(),
    loadCategoryStats(type),
  ])
}

async function loadTransactions() {
  await transactionStore.fetchTransactions({
    start_date: dayjs(`${year.value}-${month.value}-01`).format('YYYY-MM-DD'),
    end_date: dayjs(`${year.value}-${month.value}-01`).endOf('month').format('YYYY-MM-DD'),
    page_size: 100,
  })
}

async function loadCategoryStats(type = activeType.value) {
  await statsStore.fetchByCategory(year.value, month.value, type)
  statsByType.value[type] = [...statsStore.categoryStats]
}

function getStats(type: StatisticsType) {
  return statsByType.value[type] ?? []
}

function getBarColor(pct: number) {
  if (pct > 50) return '#ee0a24'
  if (pct > 20) return '#ff976a'
  return '#f5a623'
}

function getBarStyle(type: StatisticsType, pct: number) {
  return {
    width: `${pct}%`,
    ...(type === 'expense' ? { backgroundColor: getBarColor(pct) } : {}),
  }
}

function getCategoryEmoji(icon?: string) {
  return getCategoryIcon(icon || '')
}

function formatMoney(val?: number) {
  if (val == null) return '0.00'
  return Number(val).toFixed(2)
}

function formatDate(val: Transaction['transaction_date']) {
  return dayjs(val).format('MM月DD日')
}

watch(
  () => [route.query.type, route.query.year, route.query.month],
  async () => {
    syncRouteState()
    await loadData()
  },
  { immediate: true },
)
</script>

<style scoped>
.stats-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.month-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px;
  font-size: 16px;
  font-weight: bold;
  background: white;
}

.overview-row {
  display: flex;
  gap: 8px;
  padding: 12px;
}

.stat-card {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  color: white;
}

.stat-card.income-bg {
  background: linear-gradient(135deg, #07c160, #06ad56);
}

.stat-card.expense-bg {
  background: linear-gradient(135deg, #ee0a24, #d9001b);
}

.stat-card.balance-bg {
  background: linear-gradient(135deg, #1989fa, #1676d3);
}

.stat-card .label {
  font-size: 12px;
  opacity: 0.8;
}

.stat-card .value {
  display: block;
  font-size: 17px;
  font-weight: bold;
  margin-top: 4px;
}

.stat-card .value.negative {
  color: #ffb3b3;
}

.chart-section {
  margin: 0 12px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.notes-section {
  margin: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.section-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #969799;
}

.note-count {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #1989fa;
  background: #ebf5ff;
}

.chart-wrap {
  padding: 12px;
  min-height: 200px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 92px;
  flex-shrink: 0;
}

.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f7f8fa;
  font-size: 16px;
}

.category-stat-item .name {
  font-size: 13px;
  color: #323233;
}

.bar-wrap {
  flex: 1;
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s;
}

.bar.income-bar {
  background: #07c160;
}

.stat-value {
  font-size: 12px;
  color: #666;
  width: 100px;
  flex-shrink: 0;
}

.note-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.note-item {
  padding: 12px;
  border-radius: 10px;
  background: #f7f8fa;
}

.note-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.note-category {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #323233;
}

.note-icon {
  width: 24px;
  height: 24px;
  font-size: 14px;
}

.note-amount {
  font-size: 14px;
  font-weight: 600;
}

.note-amount.expense {
  color: #ee0a24;
}

.note-amount.income {
  color: #07c160;
}

.note-content {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.5;
  color: #323233;
  word-break: break-word;
}

.note-date {
  margin-top: 8px;
  font-size: 12px;
  color: #969799;
}

.notes-empty {
  padding: 24px 0;
}
</style>
