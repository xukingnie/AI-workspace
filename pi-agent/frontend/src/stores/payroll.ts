import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

interface PayrollSettings {
  payday: number
  salaryAmount: number
}

const STORAGE_KEY = 'pi-agent-payroll-settings'

const DEFAULT_SETTINGS: PayrollSettings = {
  payday: 15,
  salaryAmount: 0,
}

function normalizeSettings(raw: unknown): PayrollSettings {
  const source = typeof raw === 'object' && raw ? (raw as Partial<PayrollSettings>) : {}
  const payday = Number(source.payday)
  const salaryAmount = Number(source.salaryAmount)

  return {
    payday: Number.isInteger(payday) && payday >= 1 && payday <= 28 ? payday : DEFAULT_SETTINGS.payday,
    salaryAmount: Number.isFinite(salaryAmount) && salaryAmount >= 0 ? salaryAmount : DEFAULT_SETTINGS.salaryAmount,
  }
}

function loadSettings(): PayrollSettings {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return { ...DEFAULT_SETTINGS }

  try {
    return normalizeSettings(JSON.parse(raw))
  } catch {
    return { ...DEFAULT_SETTINGS }
  }
}

export const usePayrollStore = defineStore('payroll', () => {
  const initial = loadSettings()
  const payday = ref(initial.payday)
  const salaryAmount = ref(initial.salaryAmount)

  function persist() {
    const payload: PayrollSettings = {
      payday: payday.value,
      salaryAmount: salaryAmount.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  }

  function updateSettings(payload: Partial<PayrollSettings>) {
    const normalized = normalizeSettings({
      payday: payload.payday ?? payday.value,
      salaryAmount: payload.salaryAmount ?? salaryAmount.value,
    })

    payday.value = normalized.payday
    salaryAmount.value = normalized.salaryAmount
    persist()
  }

  const settings = computed(() => ({
    payday: payday.value,
    salaryAmount: salaryAmount.value,
  }))

  return {
    payday,
    salaryAmount,
    settings,
    updateSettings,
  }
})