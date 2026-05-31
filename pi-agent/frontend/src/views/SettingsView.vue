<template>
  <div class="settings-page">
    <van-nav-bar title="设置">
      <template #left>
        <van-icon name="home-o" size="18" @click="goToHome" />
      </template>
      <template #right>
        <van-icon name="setting-o" size="18" @click="openDrawerSettings" />
      </template>
    </van-nav-bar>

    <div class="section">
      <h3 class="section-title">导航配置</h3>
      <van-cell-group inset>
        <van-cell title="页面显隐与顺序">
          <template #label>
            <div class="sort-tip">开关控制显隐，按住左侧拖拽图标调整顺序</div>
            <div class="sort-list">
              <div
                v-for="item in sortableTabs"
                :key="item.key"
                class="sort-item"
                :class="{
                  'sort-item--drag-over': dragOverKey === item.key,
                  'sort-item--dragging': draggingKey === item.key,
                }"
                :data-key="item.key"
                draggable="true"
                @dragstart="onDragStart(item.key)"
                @dragover.prevent="onDragOver(item.key)"
                @dragleave="onDragLeave"
                @drop="onDrop(item.key)"
                @dragend="onDragEnd"
              >
                <button
                  type="button"
                  class="drag-handle"
                  aria-label="拖拽排序"
                  @touchstart.stop="onTouchDragStart($event, item.key)"
                  @touchmove.stop="onTouchDragMove"
                  @touchend.stop="onTouchDragEnd"
                  @touchcancel.stop="onTouchDragCancel"
                >
                  <van-icon name="bars" class="drag-icon" />
                </button>
                <span class="sort-name">{{ item.label }}</span>
                <span class="sort-path">{{ item.path }}</span>
                <van-switch
                  :model-value="item.visible"
                  size="20"
                  @update:model-value="(value: boolean) => onToggleTab(item.key, value)"
                />
              </div>
              <div class="sort-item sort-item--fixed">
                <span class="drag-placeholder">
                  <van-icon name="setting-o" class="drag-icon" />
                </span>
                <span class="sort-name">设置</span>
                <span class="sort-path">/settings</span>
              </div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="section">
      <h3 class="section-title">数据导出</h3>
      <van-cell-group inset>
        <van-cell
          title="导出 Excel"
          label="导出账单明细为 Excel 文件"
          is-link
          @click="handleExportExcel"
        />
        <van-cell
          title="导出 PDF"
          label="导出账单明细为 PDF 文件"
          is-link
          @click="handleExportPDF"
        />
      </van-cell-group>
    </div>

    <div class="section">
      <h3 class="section-title">分类管理</h3>
      <div class="category-panels">
        <div v-for="group in categoryGroups" :key="group.type" class="category-panel">
          <div class="category-panel__header">
            <span>{{ group.label }}</span>
            <span>{{ group.items.length }} 项</span>
          </div>
          <div class="category-grid">
            <button
              v-for="cat in group.items"
              :key="cat.id"
              type="button"
              class="category-card"
              @click="handleEditCategory(cat.id)"
            >
              <span class="category-card__icon">{{ getCategoryIcon(cat.icon) }}</span>
              <span class="category-card__name">{{ cat.name }}</span>
            </button>
          </div>
        </div>
      </div>
      <div class="add-category-btn">
        <van-button type="primary" block @click="addCategoryBtn"> 新增分类 </van-button>
      </div>
    </div>

    <!-- 日期范围选择弹窗（导出用） -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <div class="date-picker-wrap">
        <h4>选择导出日期范围（可选）</h4>
        <van-field
          v-model="exportStartDate"
          label="开始日期"
          placeholder="不选则导出全部"
          readonly
          @click="showStartPicker = true"
        />
        <van-field
          v-model="exportEndDate"
          label="结束日期"
          placeholder="不选则导出全部"
          readonly
          @click="showEndPicker = true"
        />
        <div class="date-picker-actions">
          <van-button round block type="primary" @click="confirmExport">确认导出</van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showStartPicker" position="bottom">
      <van-date-picker
        v-model="startDateValues"
        title="选择开始日期"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onStartDateConfirm"
        @cancel="showStartPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showEndPicker" position="bottom">
      <van-date-picker
        v-model="endDateValues"
        title="选择结束日期"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onEndDateConfirm"
        @cancel="showEndPicker = false"
      />
    </van-popup>

    <!-- 新增分类弹窗 -->
    <van-popup v-model:show="showAddCategory" position="bottom" round>
      <div class="add-category-wrap">
        <h4>{{ editingCategoryId ? '编辑分类' : '新增分类' }}</h4>
        <van-field v-model="newCategoryName" label="名称" placeholder="请输入分类名称" />
        <van-field label="类型">
          <template #input>
            <van-radio-group v-model="newCategoryType" direction="horizontal">
              <van-radio name="expense">支出</van-radio>
              <van-radio name="income">收入</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <div class="add-category-actions">
          <van-button
            v-if="editingCategoryId"
            round
            plain
            type="danger"
            class="delete-category-action"
            @click="handleDeleteCurrentCategory"
          >
            删除分类
          </van-button>
          <van-button round block type="primary" @click="handleSaveCategory">
            {{ editingCategoryId ? '确认保存' : '确认添加' }}
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { showToast, showConfirmDialog, closeToast } from 'vant'
import { useRouter } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import type { NavTabKey } from '@/stores/navigation'
import { useNavigationStore } from '@/stores/navigation'
import { getCategoryIcon, getDefaultCategoryIcon } from '@/options/categories'
import { exportExcel, exportPDF } from '@/api/export'

const router = useRouter()
const categoryStore = useCategoryStore()
const navStore = useNavigationStore()
const dragFromKey = ref<NavTabKey | null>(null)
const dragOverKey = ref<NavTabKey | null>(null)
const touchDragFromKey = ref<NavTabKey | null>(null)
const touchDragOverKey = ref<NavTabKey | null>(null)
const draggingKey = computed(() => touchDragFromKey.value ?? dragFromKey.value)
const pendingLongPressKey = ref<NavTabKey | null>(null)

let longPressTimer: number | null = null
let touchStartX = 0
let touchStartY = 0
let bodyOverflowBeforeDrag: string | null = null

const LONG_PRESS_MS = 120
const MOVE_CANCEL_THRESHOLD = 10

const sortableTabs = computed(() =>
  navStore.allTabs.map((item) => ({
    key: item.key,
    label: item.label,
    path: item.to,
    visible: item.visible,
  })),
)

const categoryGroups = computed(() => [
  {
    type: 'expense' as const,
    label: '支出分类',
    items: categoryStore.categories.filter((item) => item.type === 'expense'),
  },
  {
    type: 'income' as const,
    label: '收入分类',
    items: categoryStore.categories.filter((item) => item.type === 'income'),
  },
])

function onToggleTab(key: NavTabKey, visible: boolean) {
  if (!visible) {
    if (navStore.getVisibleHomeCardCount() <= 1) {
      showToast('至少保留一个可见页面')
      return
    }
  }
  navStore.setTabVisible(key, visible)
}

function onToggleSettingsCard(visible: boolean) {
  if (!visible && navStore.getVisibleHomeCardCount() <= 1) {
    showToast('至少保留一个可见页面')
    return
  }
  navStore.setHomeCardVisible('settings', visible)
}

// #region 导航配置拖拽相关
function onDragStart(key: NavTabKey) {
  dragFromKey.value = key
}

function onDragOver(key: NavTabKey) {
  dragOverKey.value = key
}

function onDragLeave() {
  dragOverKey.value = null
}

function onDrop(targetKey: NavTabKey) {
  if (!dragFromKey.value || dragFromKey.value === targetKey) return
  navStore.reorderTabs(dragFromKey.value, targetKey)
  dragOverKey.value = null
}

function onDragEnd() {
  dragFromKey.value = null
  dragOverKey.value = null
}

// #endregion

function setPageScrollLocked(locked: boolean) {
  if (typeof document === 'undefined') return
  if (locked) {
    if (bodyOverflowBeforeDrag === null) {
      bodyOverflowBeforeDrag = document.body.style.overflow
    }
    document.body.style.overflow = 'hidden'
    return
  }

  if (bodyOverflowBeforeDrag !== null) {
    document.body.style.overflow = bodyOverflowBeforeDrag
    bodyOverflowBeforeDrag = null
  }
}

function clearTouchLongPress() {
  if (longPressTimer !== null) {
    window.clearTimeout(longPressTimer)
    longPressTimer = null
  }
  pendingLongPressKey.value = null
}

function isNavTabKey(value: unknown): value is NavTabKey {
  return value === 'countdown' || value === 'stats' || value === 'add'
}

function getTouchTargetKey(touch: Touch): NavTabKey | null {
  const element = document.elementFromPoint(touch.clientX, touch.clientY)
  if (!element) return null
  const sortItem = element.closest('.sort-item') as HTMLElement | null
  if (!sortItem) return null
  const { key } = sortItem.dataset
  return isNavTabKey(key) ? key : null
}

function onTouchDragStart(event: TouchEvent, key: NavTabKey) {
  const touch = event.touches[0]
  if (!touch) return

  clearTouchLongPress()
  pendingLongPressKey.value = key
  touchStartX = touch.clientX
  touchStartY = touch.clientY

  longPressTimer = window.setTimeout(() => {
    if (pendingLongPressKey.value !== key) return
    touchDragFromKey.value = key
    touchDragOverKey.value = key
    dragOverKey.value = key
    pendingLongPressKey.value = null
    longPressTimer = null
    setPageScrollLocked(true)
  }, LONG_PRESS_MS)
}

function onTouchDragMove(event: TouchEvent) {
  const touch = event.touches[0]
  if (!touch) return

  if (!touchDragFromKey.value) {
    const deltaX = Math.abs(touch.clientX - touchStartX)
    const deltaY = Math.abs(touch.clientY - touchStartY)
    if (deltaX > MOVE_CANCEL_THRESHOLD || deltaY > MOVE_CANCEL_THRESHOLD) {
      clearTouchLongPress()
    }
    return
  }

  event.preventDefault()
  const targetKey = getTouchTargetKey(touch)
  if (!targetKey) return
  touchDragOverKey.value = targetKey
  dragOverKey.value = targetKey
}

function addCategoryBtn() {
  resetCategoryForm()
  showAddCategory.value = true
}

function onTouchDragEnd() {
  clearTouchLongPress()

  if (!touchDragFromKey.value) {
    onTouchDragCancel()
    return
  }

  if (
    touchDragFromKey.value &&
    touchDragOverKey.value &&
    touchDragFromKey.value !== touchDragOverKey.value
  ) {
    navStore.reorderTabs(touchDragFromKey.value, touchDragOverKey.value)
  }
  onTouchDragCancel()
}

function onTouchDragCancel() {
  clearTouchLongPress()
  setPageScrollLocked(false)
  touchDragFromKey.value = null
  touchDragOverKey.value = null
  dragOverKey.value = null
}

function openDrawerSettings() {
  router.push({
    name: 'settings-drawer',
    query: { returnTo: 'settings' },
  })
}

function goToHome() {
  router.push({ name: 'home' })
}

// ========== 导出相关 ==========
const showDatePicker = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const exportStartDate = ref('')
const exportEndDate = ref('')
const startDateValues = ref<string[]>([new Date().getFullYear().toString(), '1', '1'])
const endDateValues = ref<string[]>([
  new Date().getFullYear().toString(),
  (new Date().getMonth() + 1).toString(),
  new Date().getDate().toString(),
])

let exportType: 'excel' | 'pdf' = 'excel'

function handleExportExcel() {
  exportType = 'excel'
  showDatePicker.value = true
}

function handleExportPDF() {
  exportType = 'pdf'
  showDatePicker.value = true
}

function onStartDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  exportStartDate.value = `${selectedValues[0]}-${String(selectedValues[1]).padStart(2, '0')}-${String(selectedValues[2]).padStart(2, '0')}`
  showStartPicker.value = false
}

function onEndDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  exportEndDate.value = `${selectedValues[0]}-${String(selectedValues[1]).padStart(2, '0')}-${String(selectedValues[2]).padStart(2, '0')}`
  showEndPicker.value = false
}

async function confirmExport() {
  showDatePicker.value = false
  const start = exportStartDate.value || undefined
  const end = exportEndDate.value || undefined

  showToast({ message: '正在导出...', icon: 'loading', duration: 0 })

  try {
    if (exportType === 'excel') {
      await exportExcel(start, end)
    } else {
      await exportPDF(start, end)
    }
    showToast({ message: '导出成功', icon: 'success' })
  } catch {
    // 错误已在 request 拦截器中处理
  } finally {
    closeToast()
  }

  // 重置
  exportStartDate.value = ''
  exportEndDate.value = ''
}

// ========== 分类管理 ==========
const showAddCategory = ref(false)
const editingCategoryId = ref<number | null>(null)
const newCategoryName = ref('')
const newCategoryType = ref<'expense' | 'income'>('expense')

// 重置新增/编辑分类表单
function resetCategoryForm() {
  editingCategoryId.value = null
  newCategoryName.value = ''
  newCategoryType.value = 'expense'
}

function handleEditCategory(id: number) {
  const target = categoryStore.categories.find((c) => c.id === id)
  if (!target) return
  editingCategoryId.value = id
  newCategoryName.value = target.name
  newCategoryType.value = target.type
  showAddCategory.value = true
}

async function handleSaveCategory() {
  if (!newCategoryName.value.trim()) {
    showToast('请输入分类名称')
    return
  }
  if (editingCategoryId.value) {
    await categoryStore.editCategory(editingCategoryId.value, {
      name: newCategoryName.value.trim(),
      type: newCategoryType.value,
    })
    showToast('保存成功')
  } else {
    await categoryStore.addCategory({
      name: newCategoryName.value.trim(),
      type: newCategoryType.value,
      icon: getDefaultCategoryIcon(newCategoryType.value),
    })
    showToast('添加成功')
  }

  showAddCategory.value = false
  resetCategoryForm()
}

async function handleDeleteCategory(id: number) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除该分类吗？',
    })
  } catch {
    return
  }
  await categoryStore.removeCategory(id)
  showToast('删除成功')
}

async function handleDeleteCurrentCategory() {
  if (!editingCategoryId.value) return
  const categoryId = editingCategoryId.value
  await handleDeleteCategory(categoryId)
  showAddCategory.value = false
  resetCategoryForm()
}

onMounted(() => {
  categoryStore.fetchCategories()
})

onBeforeUnmount(() => {
  clearTouchLongPress()
  setPageScrollLocked(false)
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.section {
  margin-top: 12px;
}

.section-title {
  font-size: 14px;
  color: #969799;
  padding: 8px 16px;
  margin: 0;
}

.add-category-btn {
  padding: 12px 16px;
}

.category-panels {
  padding: 0 16px;
  display: grid;
  gap: 12px;
}

.category-panel {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
}

.category-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #969799;
  font-size: 12px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  min-height: 80px;
  padding: 12px 8px 10px;
  border: 1px solid #eef0f3;
  border-radius: 12px;
  background: #fdfefe;
  text-align: center;
}

.category-card__icon {
  font-size: 24px;
  line-height: 1;
}

.category-card__name {
  color: #323233;
  font-size: 13px;
  text-align: center;
  line-height: 1.3;
}

.category-card:active {
  opacity: 0.8;
}

.sort-tip {
  color: #969799;
  font-size: 12px;
  margin-bottom: 8px;
}

.sort-list {
  display: grid;
  gap: 8px;
}

.sort-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 10px;
  cursor: move;
  transition:
    background-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.sort-item--fixed {
  cursor: default;
}

.drag-placeholder {
  width: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.drag-handle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 0;
  background: transparent;
  touch-action: pan-y;
  cursor: grab;
}

.drag-handle:active {
  cursor: grabbing;
}

.sort-item--drag-over {
  background: #e8f3ff;
  box-shadow: 0 0 0 1px #8fc3ff inset;
  animation: drag-over-pulse 0.9s ease-in-out infinite;
}

.sort-item--dragging {
  background: #d9ecff;
  box-shadow: 0 8px 18px rgba(25, 137, 250, 0.18);
  transform: scale(1.01);
}

@keyframes drag-over-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 1px #8fc3ff inset;
  }

  50% {
    box-shadow: 0 0 0 2px #5ca9ff inset;
  }
}

.drag-icon {
  color: #969799;
}

.sort-name {
  flex: 1;
  color: #323233;
}

.sort-path {
  color: #969799;
  font-size: 12px;
}

.date-picker-wrap,
.add-category-wrap {
  padding: 20px 16px;
}

.date-picker-wrap h4,
.add-category-wrap h4 {
  text-align: center;
  font-size: 16px;
  margin-bottom: 16px;
}

.date-picker-actions,
.add-category-actions {
  padding: 16px 0 8px;
  display: flex;
  gap: 10px;
}

.delete-category-action {
  flex: 0 0 112px;
}

.add-category-actions :deep(.van-button) {
  flex: 1;
}

@media (max-width: 360px) {
  .category-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
