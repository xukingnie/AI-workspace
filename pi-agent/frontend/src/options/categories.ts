import type { Category } from '@/types'

/** 默认分类（后端不可用时兜底） */
export const DEFAULT_CATEGORIES: Category[] = [
  // 支出
  { id: -1, name: '餐饮', type: 'expense', icon: 'food', sort_order: 1 },
  { id: -2, name: '交通', type: 'expense', icon: 'traffic', sort_order: 2 },
  { id: -3, name: '购物', type: 'expense', icon: 'shopping', sort_order: 3 },
  { id: -4, name: '娱乐', type: 'expense', icon: 'entertainment', sort_order: 4 },
  { id: -5, name: '居住', type: 'expense', icon: 'house', sort_order: 5 },
  { id: -6, name: '通讯', type: 'expense', icon: 'phone', sort_order: 6 },
  { id: -7, name: '医疗', type: 'expense', icon: 'medical', sort_order: 7 },
  { id: -8, name: '教育', type: 'expense', icon: 'education', sort_order: 8 },
  { id: -9, name: '其他支出', type: 'expense', icon: 'other-expense', sort_order: 99 },
  // 收入
  { id: -10, name: '工资', type: 'income', icon: 'salary', sort_order: 1 },
  { id: -11, name: '奖金', type: 'income', icon: 'bonus', sort_order: 2 },
  { id: -12, name: '投资收益', type: 'income', icon: 'investment', sort_order: 3 },
  { id: -13, name: '兼职', type: 'income', icon: 'parttime', sort_order: 4 },
  { id: -14, name: '其他收入', type: 'income', icon: 'other-income', sort_order: 99 },
]

/** icon → emoji 映射 */
export const CATEGORY_ICON_MAP: Record<string, string> = {
  food: '🍜',
  traffic: '🚗',
  shopping: '🛒',
  entertainment: '🎮',
  house: '🏠',
  phone: '📱',
  medical: '💊',
  education: '📚',
  'other-expense': '💸',
  salary: '💰',
  bonus: '🎁',
  investment: '📈',
  parttime: '💼',
  'other-income': '💵',
}

/** 根据 icon 码获取 emoji */
export function getCategoryIcon(icon: string): string {
  return CATEGORY_ICON_MAP[icon] || '📌'
}

export function getDefaultCategoryIcon(type: 'income' | 'expense'): string {
  return type === 'income' ? 'other-income' : 'other-expense'
}
