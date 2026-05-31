/** 分类 */
export interface Category {
  id: number
  name: string
  type: 'income' | 'expense'
  icon: string
  sort_order: number
}

/** 账单 */
export interface Transaction {
  id: number
  amount: number
  type: 'income' | 'expense'
  category_id: number
  transaction_date: string
  note: string
  created_at: string
  category?: Category
}

export interface NoteSuggestion {
  note: string
  count: number
  last_used_at: string
}

export interface AmountSuggestion {
  amount: number | string
  count: number
  last_used_at: string
}

/** 月度总览 */
export interface Overview {
  total_income: number
  total_expense: number
  balance: number
}

/** 分类统计 */
export interface CategoryStat {
  category_id: number
  category_name: string
  category_icon: string
  total: number
  percentage: number
}

/** 每日统计 */
export interface DailyStat {
  date: string
  income: number
  expense: number
}
