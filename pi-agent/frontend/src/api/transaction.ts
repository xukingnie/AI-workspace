import request from './request'
import type { Transaction } from '@/types'

export interface TransactionQuery {
  type?: string
  category_id?: number
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

export const getTransactions = (params?: TransactionQuery) =>
  request.get<Transaction[]>('/transactions', { params })

export const createTransaction = (data: {
  amount: number
  type: string
  category_id: number
  transaction_date: string
  note?: string
}) => request.post<Transaction>('/transactions', data)

export const updateTransaction = (id: number, data: Record<string, any>) =>
  request.put<Transaction>(`/transactions/${id}`, data)

export const deleteTransaction = (id: number) =>
  request.delete(`/transactions/${id}`)
