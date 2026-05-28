import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getOverview, getByCategory, getDaily } from '@/api/statistics'
import type { Overview, CategoryStat, DailyStat } from '@/types'

export const useStatisticsStore = defineStore('statistics', () => {
  const overview = ref<Overview | null>(null)
  const categoryStats = ref<CategoryStat[]>([])
  const dailyStats = ref<DailyStat[]>([])
  const loading = ref(false)

  async function fetchOverview(year: number, month: number) {
    loading.value = true
    try {
      const res = await getOverview(year, month)
      overview.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchByCategory(year: number, month: number, type: string) {
    const res = await getByCategory(year, month, type)
    categoryStats.value = res.data
  }

  async function fetchDaily(year: number, month: number) {
    const res = await getDaily(year, month)
    dailyStats.value = res.data
  }

  return {
    overview,
    categoryStats,
    dailyStats,
    loading,
    fetchOverview,
    fetchByCategory,
    fetchDaily,
  }
})
