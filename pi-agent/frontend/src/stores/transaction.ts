import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  getNoteSuggestions,
  getAmountSuggestions,
  getAmountByNote,
} from '@/api/transaction'
import type { AmountSuggestion, NoteSuggestion, Transaction } from '@/types'

export const useTransactionStore = defineStore('transaction', () => {
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)

  async function fetchTransactions(params?: Record<string, any>) {
    loading.value = true
    try {
      const res = await getTransactions(params)
      transactions.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function addTransaction(data: {
    amount: number
    type: string
    category_id: number
    transaction_date: string
    note?: string
  }) {
    const res = await createTransaction(data)
    transactions.value.unshift(res.data)
    return res.data
  }

  async function editTransaction(id: number, data: Record<string, any>) {
    const res = await updateTransaction(id, data)
    const idx = transactions.value.findIndex((t) => t.id === id)
    if (idx >= 0) transactions.value[idx] = res.data
    return res.data
  }

  async function removeTransaction(id: number) {
    await deleteTransaction(id)
    transactions.value = transactions.value.filter((t) => t.id !== id)
  }

  async function fetchNoteSuggestions(params: {
    category_id: number
    type?: string
    limit?: number
    recent_days?: number
  }) {
    const res = await getNoteSuggestions(params)
    return res.data as NoteSuggestion[]
  }

  async function fetchAmountSuggestions(params: {
    category_id: number
    type?: string
    limit?: number
    recent_days?: number
  }) {
    const res = await getAmountSuggestions(params)
    return res.data as AmountSuggestion[]
  }

  async function fetchAmountByNote(params: {
    category_id: number
    note: string
    type?: string
    recent_days?: number
  }) {
    const res = await getAmountByNote(params)
    return res.data as AmountSuggestion | null
  }

  return {
    transactions,
    loading,
    fetchTransactions,
    addTransaction,
    editTransaction,
    removeTransaction,
    fetchNoteSuggestions,
    fetchAmountSuggestions,
    fetchAmountByNote,
  }
})
