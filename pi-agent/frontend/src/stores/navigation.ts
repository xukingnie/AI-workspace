import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type NavTabKey = 'countdown' | 'stats' | 'add'

interface NavigationConfig {
  tabOrder: NavTabKey[]
  visibleTabs: Record<NavTabKey, boolean>
}

const STORAGE_KEY = 'pi-agent-navigation-config'
const DEFAULT_STORAGE_KEY = 'pi-agent-navigation-default-config'

const STATIC_DEFAULT_CONFIG: NavigationConfig = {
  tabOrder: ['countdown', 'stats', 'add'],
  visibleTabs: {
    countdown: true,
    stats: true,
    add: true,
  },
}

const TAB_META: Record<NavTabKey, { label: string; icon: string; to: string }> = {
  countdown: {
    label: '倒计时',
    icon: 'underway-o',
    to: '/countdown',
  },
  stats: {
    label: '统计',
    icon: 'chart-trending-o',
    to: '/stats',
  },
  add: {
    label: '记账',
    icon: 'add-o',
    to: '/add',
  },
}

function isTabKey(val: unknown): val is NavTabKey {
  return val === 'countdown' || val === 'stats' || val === 'add'
}

function normalizeTabOrder(order?: unknown): NavTabKey[] {
  const source = Array.isArray(order) ? order.filter(isTabKey) : []
  const merged = [...source]
  for (const key of STATIC_DEFAULT_CONFIG.tabOrder) {
    if (!merged.includes(key)) merged.push(key)
  }
  return merged
}

function normalizeVisibleTabs(visibleTabs?: unknown): Record<NavTabKey, boolean> {
  const source = typeof visibleTabs === 'object' && visibleTabs ? (visibleTabs as Partial<Record<NavTabKey, unknown>>) : {}
  return {
    countdown: typeof source.countdown === 'boolean' ? source.countdown : STATIC_DEFAULT_CONFIG.visibleTabs.countdown,
    stats: typeof source.stats === 'boolean' ? source.stats : STATIC_DEFAULT_CONFIG.visibleTabs.stats,
    add: typeof source.add === 'boolean' ? source.add : STATIC_DEFAULT_CONFIG.visibleTabs.add,
  }
}

function migrateLegacyConfig(parsed: Record<string, unknown>): NavigationConfig | null {
  const hasLegacy = 'showAdd' in parsed || 'showStats' in parsed || 'middleOrder' in parsed
  if (!hasLegacy) return null

  const showAdd = typeof parsed.showAdd === 'boolean' ? parsed.showAdd : true
  const showStats = typeof parsed.showStats === 'boolean' ? parsed.showStats : true
  const middleOrder = parsed.middleOrder === 'stats-first' ? 'stats-first' : 'add-first'
  const middle = middleOrder === 'add-first' ? ['add', 'stats'] : ['stats', 'add']

  return {
    tabOrder: ['countdown', ...(middle as Array<'add' | 'stats'>)],
    visibleTabs: {
      countdown: true,
      add: showAdd,
      stats: showStats,
    },
  }
}

function parseNavigationConfig(raw: string | null): NavigationConfig | null {
  if (!raw) {
    return null
  }

  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>
    const legacy = migrateLegacyConfig(parsed)
    if (legacy) return legacy

    const normalizedOrder = normalizeTabOrder(parsed.tabOrder)
    const normalizedVisibleTabs = normalizeVisibleTabs(parsed.visibleTabs)

    return {
      tabOrder: normalizedOrder,
      visibleTabs: normalizedVisibleTabs,
    }
  } catch {
    return null
  }
}

function loadDefaultConfig(): NavigationConfig {
  const savedDefault = parseNavigationConfig(localStorage.getItem(DEFAULT_STORAGE_KEY))
  if (savedDefault) return savedDefault

  return {
    tabOrder: [...STATIC_DEFAULT_CONFIG.tabOrder],
    visibleTabs: { ...STATIC_DEFAULT_CONFIG.visibleTabs },
  }
}

function saveDefaultConfig(config: NavigationConfig) {
  const data: NavigationConfig = {
    tabOrder: [...config.tabOrder],
    visibleTabs: { ...config.visibleTabs },
  }
  localStorage.setItem(DEFAULT_STORAGE_KEY, JSON.stringify(data))
}

function loadConfig(): NavigationConfig {
  const saved = parseNavigationConfig(localStorage.getItem(STORAGE_KEY))
  if (saved) return saved

  return loadDefaultConfig()
}

export const useNavigationStore = defineStore('navigation', () => {
  const defaultConfig = loadDefaultConfig()
  const tabOrder = ref<NavTabKey[]>([...defaultConfig.tabOrder])
  const visibleTabs = ref<Record<NavTabKey, boolean>>({ ...defaultConfig.visibleTabs })

  if (!localStorage.getItem(DEFAULT_STORAGE_KEY)) {
    const currentConfig = parseNavigationConfig(localStorage.getItem(STORAGE_KEY)) ?? defaultConfig
    saveDefaultConfig(currentConfig)
  }

  function persist() {
    const data: NavigationConfig = {
      tabOrder: [...tabOrder.value],
      visibleTabs: { ...visibleTabs.value },
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  }

  function setTabVisible(key: NavTabKey, visible: boolean) {
    visibleTabs.value = {
      ...visibleTabs.value,
      [key]: visible,
    }
    persist()
  }

  function reorderTabs(fromKey: NavTabKey, toKey: NavTabKey) {
    const fromIndex = tabOrder.value.indexOf(fromKey)
    const toIndex = tabOrder.value.indexOf(toKey)
    if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return

    const next = [...tabOrder.value]
    next.splice(fromIndex, 1)
    next.splice(toIndex, 0, fromKey)
    tabOrder.value = next
    persist()
  }

  function resetConfig() {
    const targetDefault = loadDefaultConfig()
    tabOrder.value = [...targetDefault.tabOrder]
    visibleTabs.value = { ...targetDefault.visibleTabs }
    persist()
  }

  function loadFromStorage() {
    const saved = loadConfig()
    tabOrder.value = [...saved.tabOrder]
    visibleTabs.value = { ...saved.visibleTabs }
  }

  function getConfigObject(): NavigationConfig {
    return {
      tabOrder: [...tabOrder.value],
      visibleTabs: { ...visibleTabs.value },
    }
  }

  const configurableTabs = computed(() =>
    tabOrder.value
      .filter((key) => visibleTabs.value[key])
      .map((key) => ({
        key,
        ...TAB_META[key],
      })),
  )

  const allTabs = computed(() =>
    tabOrder.value.map((key) => ({
      key,
      ...TAB_META[key],
      visible: visibleTabs.value[key],
    })),
  )

  loadFromStorage()

  return {
    tabOrder,
    visibleTabs,
    configurableTabs,
    allTabs,
    setTabVisible,
    reorderTabs,
    resetConfig,
    getConfigObject,
  }
})