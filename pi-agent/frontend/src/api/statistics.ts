import request from './request'
import type { Overview, CategoryStat, DailyStat } from '@/types'

export const getOverview = (year: number, month: number) =>
  request.get<Overview>('/statistics/overview', { params: { year, month } })

export const getByCategory = (year: number, month: number, type: string) =>
  request.get<CategoryStat[]>('/statistics/by-category', {
    params: { year, month, type },
  })

export const getDaily = (year: number, month: number) =>
  request.get<DailyStat[]>('/statistics/daily', { params: { year, month } })
