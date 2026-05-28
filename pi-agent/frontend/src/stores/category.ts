import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'
import { DEFAULT_CATEGORIES } from '@/options/categories'
import type { Category } from '@/types'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories(type?: string) {
    loading.value = true
    try {
      const res = await getCategories(type)
      const list = res.data
      categories.value = list.length > 0 ? list : getDefaults(type)
    } catch {
      categories.value = getDefaults(type)
    } finally {
      loading.value = false
    }
  }

  function getDefaults(type?: string): Category[] {
    return type
      ? DEFAULT_CATEGORIES.filter((c) => c.type === type)
      : [...DEFAULT_CATEGORIES]
  }

  async function addCategory(data: { name: string; type: string; icon?: string }) {
    const res = await createCategory(data)
    categories.value.push(res.data)
    return res.data
  }

  async function editCategory(id: number, data: Record<string, any>) {
    const res = await updateCategory(id, data)
    const idx = categories.value.findIndex((c) => c.id === id)
    if (idx >= 0) categories.value[idx] = res.data
    return res.data
  }

  async function removeCategory(id: number) {
    await deleteCategory(id)
    categories.value = categories.value.filter((c) => c.id !== id)
  }

  return {
    categories,
    loading,
    fetchCategories,
    addCategory,
    editCategory,
    removeCategory,
  }
})
