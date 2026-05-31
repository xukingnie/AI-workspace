import request from './request'
import type { AmountSuggestion, NoteSuggestion, Transaction } from '@/types'

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

export interface NoteSuggestionQuery {
  category_id: number
  type?: string
  limit?: number
  recent_days?: number
}

export const getNoteSuggestions = (params: NoteSuggestionQuery) =>
  request.get<NoteSuggestion[]>('/transactions/note-suggestions', { params })

export interface AmountSuggestionQuery {
  category_id: number
  type?: string
  limit?: number
  recent_days?: number
}

export const getAmountSuggestions = (params: AmountSuggestionQuery) =>
  request.get<AmountSuggestion[]>('/transactions/amount-suggestions', { params })

export interface LinkedAmountQuery {
  category_id: number
  note: string
  type?: string
  recent_days?: number
}

export const getAmountByNote = (params: LinkedAmountQuery) =>
  request.get<AmountSuggestion | null>('/transactions/amount-by-note', { params })

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
