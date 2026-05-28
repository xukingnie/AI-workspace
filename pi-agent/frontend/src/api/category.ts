import request from './request'
import type { Category } from '@/types'

export const getCategories = (type?: string) =>
  request.get<Category[]>('/categories', { params: { type } })

export const createCategory = (data: { name: string; type: string; icon?: string }) =>
  request.post<Category>('/categories', data)

export const updateCategory = (id: number, data: Record<string, any>) =>
  request.put<Category>(`/categories/${id}`, data)

export const deleteCategory = (id: number) =>
  request.delete(`/categories/${id}`)
