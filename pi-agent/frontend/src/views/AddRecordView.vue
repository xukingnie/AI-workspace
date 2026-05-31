<template>
  <div class="add-page">
    <van-nav-bar title="记账" />
    <div class="form-wrap">
      <!-- 类型切换 -->
      <div class="type-switch">
        <span :class="typeSwitchClass('income')" @click="switchRecordType('income')"> 收入 </span>
        <span :class="typeSwitchClass('expense')" @click="switchRecordType('expense')"> 支出 </span>
      </div>

      <!-- 分类选择 -->
      <div class="category-section">
        <div class="category-section__head">
          <h4>选择分类</h4>
          <button type="button" class="category-toggle" @click="toggleCategoryExpanded">
            {{ categoryExpanded ? '收起' : '展开' }}
          </button>
        </div>
        <button
          v-if="selectedCategory"
          type="button"
          class="category-current"
          @click="categoryExpanded = true"
        >
          <span class="cat-icon">{{ getCategoryIcon(selectedCategory.icon) }}</span>
          <span class="category-current__name">{{ selectedCategory.name }}</span>
        </button>
        <div v-else class="category-current category-current--empty">
          <span>尚未选择分类，请先选择</span>
        </div>
        <div v-show="categoryExpanded" class="category-grid">
          <div
            v-for="cat in filteredCategories"
            :key="cat.id"
            :class="['category-item', { selected: selectedCategoryId === cat.id }]"
            @click="handleSelectCategory(cat.id)"
          >
            <span class="cat-icon">{{ getCategoryIcon(cat.icon) }}</span>
            <span class="cat-name">{{ cat.name }}</span>
          </div>
          <button type="button" class="category-item category-item--add" @click="openAddCategory">
            <span class="cat-icon">＋</span>
            <span class="cat-name">新增分类</span>
          </button>
        </div>
      </div>

      <!-- 金额输入 -->
      <div class="amount-input-wrap">
        <div class="amount-input-title">
          <span>金额</span>
          <div v-if="showAmountSuggestions" class="amount-title-suggestions">
            <span v-if="amountSuggestionLoading" class="amount-title-status">加载中...</span>
            <span
              v-else-if="amountSuggestions.length === 0"
              class="amount-title-status amount-title-status--empty"
            >
              暂无常用金额
            </span>
            <div v-else class="amount-title-list">
              <button
                v-for="item in amountSuggestions"
                :key="`${item.amount}`"
                type="button"
                :class="[
                  'amount-chip',
                  { 'amount-chip--active': amount === formatAmountValue(item.amount) },
                ]"
                @click="applyAmountSuggestion(item.amount)"
              >
                <span>{{ formatAmountLabel(item.amount) }}</span>
                <span class="amount-chip__count">{{ item.count }}</span>
              </button>
            </div>
          </div>
        </div>
        <div class="amount-input-row">
          <span class="currency">¥</span>
          <input
            v-model="amount"
            type="text"
            inputmode="decimal"
            enterkeyhint="done"
            autocomplete="off"
            pattern="[0-9]*[.]?[0-9]*"
            class="amount-input"
            placeholder="0.00"
            @input="normalizeAmountInput"
          />
          <button
            type="button"
            :class="['amount-clear-btn', { 'amount-clear-btn--placeholder': !amount }]"
            :disabled="!amount"
            @click="clearAmount"
          >
            清空
          </button>
        </div>
      </div>

      <!-- 备注与智能建议 -->
      <div class="note-panel">
        <van-field v-model="note" label="备注" placeholder="请输入备注（可选）" />
        <div v-if="selectedCategoryId" class="note-suggestion-section">
          <div class="note-suggestion-header">
            <span>智能备注</span>
          </div>
          <div v-if="noteSuggestionLoading" class="note-suggestion-empty">加载中...</div>
          <div v-else-if="noteSuggestions.length === 0" class="note-suggestion-empty">
            暂无常用备注
          </div>
          <div v-else class="note-suggestion-list">
            <button
              v-for="item in noteSuggestions"
              :key="item.note"
              type="button"
              :class="['note-chip', { 'note-chip--active': note === item.note }]"
              @click="applyNoteSuggestion(item.note)"
            >
              <span class="note-chip__text">{{ item.note }}</span>
              <span class="note-chip__count">{{ item.count }}</span>
            </button>
          </div>
        </div>
      </div>
      <!-- 日期 -->
      <van-field
        v-model="transactionDate"
        label="日期"
        readonly
        is-link
        @click="showDatePicker = true"
      />
    </div>

    <!-- 保存按钮 -->
    <div class="save-sticky">
      <div class="save-sticky__inner">
        <van-button type="primary" block round @click="handleSave"> 保存 </van-button>
      </div>
    </div>

    <!-- 日期选择器 -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="dateValues"
        title="选择日期"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showAddCategory" position="bottom" round>
      <div class="add-category-wrap">
        <h4>新增{{ recordType === 'income' ? '收入' : '支出' }}分类</h4>
        <van-field v-model="newCategoryName" label="名称" placeholder="请输入分类名称" />
        <div class="add-category-actions">
          <van-button round block type="primary" @click="handleAddCategory"> 确认添加 </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import { showToast, showConfirmDialog } from 'vant'
import { useCategoryStore } from '@/stores/category'
import { useTransactionStore } from '@/stores/transaction'
import { getCategoryIcon, getDefaultCategoryIcon } from '@/options/categories'
import type { AmountSuggestion, NoteSuggestion } from '@/types'

const categoryStore = useCategoryStore()
const txnStore = useTransactionStore()

// 表单数据
const recordType = ref<'expense' | 'income'>('expense')
const amount = ref('')
const selectedCategoryId = ref<number | null>(null)
const transactionDate = ref(dayjs().format('YYYY-MM-DD'))
const note = ref('')
const showAddCategory = ref(false)
const newCategoryName = ref('')
const noteSuggestions = ref<NoteSuggestion[]>([])
const noteSuggestionLoading = ref(false)
const amountSuggestions = ref<AmountSuggestion[]>([])
const amountSuggestionLoading = ref(false)
const showAmountSuggestions = ref(false)
const categoryExpanded = ref(true)
let suggestionRequestId = 0
let amountSuggestionRequestId = 0
let linkedAmountRequestId = 0

// 日期选择
const showDatePicker = ref(false)
const now = dayjs()
const dateValues = ref<string[]>([
  now.year().toString(),
  (now.month() + 1).toString(),
  now.date().toString(),
])

function typeSwitchClass(type: 'expense' | 'income') {
  const isActive = recordType.value === type
  return {
    active: isActive,
    animate__animated: isActive,
    animate__pulse: isActive,
    animate__faster: isActive,
  }
}

function switchRecordType(type: 'expense' | 'income') {
  if (recordType.value === type) return

  recordType.value = type
  amount.value = ''
  note.value = ''
  selectedCategoryId.value = null
  noteSuggestions.value = []
  amountSuggestions.value = []
  showAmountSuggestions.value = false
  categoryExpanded.value = true
}

function onDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  transactionDate.value = `${selectedValues[0]}-${String(selectedValues[1]).padStart(2, '0')}-${String(selectedValues[2]).padStart(2, '0')}`
  showDatePicker.value = false
}

function openAddCategory() {
  newCategoryName.value = ''
  showAddCategory.value = true
}

async function handleSelectCategory(categoryId: number) {
  const changed = selectedCategoryId.value !== categoryId
  selectedCategoryId.value = categoryId

  if (!changed) return

  categoryExpanded.value = false
}

function clearAmount() {
  amount.value = ''
}

function normalizeAmountInput(event: Event) {
  const target = event.target as HTMLInputElement
  const normalized = target.value.replace(/[^\d.]/g, '').replace(/\.(?=.*\.)/g, '')

  amount.value = normalized
  target.value = normalized
}

// 筛选当前类型的分类
const filteredCategories = computed(() =>
  categoryStore.categories.filter((c) => c.type === recordType.value),
)

const selectedCategory = computed(
  () => categoryStore.categories.find((c) => c.id === selectedCategoryId.value) ?? null,
)

function toggleCategoryExpanded() {
  categoryExpanded.value = !categoryExpanded.value
}

async function handleAddCategory() {
  const name = newCategoryName.value.trim()
  if (!name) {
    showToast('请输入分类名称')
    return
  }

  const created = await categoryStore.addCategory({
    name,
    type: recordType.value,
    icon: getDefaultCategoryIcon(recordType.value),
  })

  selectedCategoryId.value = created.id
  newCategoryName.value = ''
  showAddCategory.value = false
  categoryExpanded.value = false
  showToast('分类已添加')
}

function applyNoteSuggestion(suggestion: string) {
  note.value = suggestion
  showAmountSuggestions.value = true
  void applyLinkedAmountByNote(suggestion)
}

function toAmountNumber(value: number | string) {
  const parsed = typeof value === 'number' ? value : parseFloat(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function formatAmountLabel(value: number | string) {
  return `¥${toAmountNumber(value).toFixed(2)}`
}

function formatAmountValue(value: number | string) {
  return toAmountNumber(value).toFixed(2)
}

function applyAmountSuggestion(suggestionAmount: number | string) {
  const currentAmount = parseFloat(amount.value)
  const hasManualAmount = !!amount.value && !Number.isNaN(currentAmount) && currentAmount > 0

  if (hasManualAmount) {
    showToast('已输入金额，不自动覆盖')
    return
  }

  amount.value = formatAmountValue(suggestionAmount)
}

async function applyLinkedAmountByNote(suggestionNote: string) {
  if (!selectedCategoryId.value) return

  const normalizedNote = suggestionNote.trim()
  if (!normalizedNote) return

  const requestId = ++linkedAmountRequestId

  try {
    const linkedAmount = await txnStore.fetchAmountByNote({
      category_id: selectedCategoryId.value,
      note: normalizedNote,
      type: recordType.value,
      recent_days: 90,
    })

    if (requestId !== linkedAmountRequestId || !linkedAmount) {
      return
    }

    const nextAmount = formatAmountValue(linkedAmount.amount)
    const currentAmount = parseFloat(amount.value)
    const hasManualAmount = !!amount.value && !Number.isNaN(currentAmount) && currentAmount > 0

    if (!hasManualAmount) {
      amount.value = nextAmount
      return
    }

    if (amount.value === nextAmount) {
      return
    }

    try {
      await showConfirmDialog({
        title: '覆盖金额',
        message: `当前金额为 ${formatAmountLabel(amount.value)}，是否覆盖为 ${formatAmountLabel(nextAmount)}？`,
        confirmButtonText: '覆盖',
        cancelButtonText: '保留',
      })
      amount.value = nextAmount
    } catch {
      // 用户取消覆盖
    }
  } catch {
    // 联动失败时保持静默，不影响主流程
  }
}

async function loadNoteSuggestions() {
  if (!selectedCategoryId.value) {
    noteSuggestions.value = []
    return
  }

  const requestId = ++suggestionRequestId
  noteSuggestionLoading.value = true

  try {
    const data = await txnStore.fetchNoteSuggestions({
      category_id: selectedCategoryId.value,
      type: recordType.value,
      limit: 8,
      recent_days: 30,
    })

    if (requestId === suggestionRequestId) {
      noteSuggestions.value = data
    }
  } catch {
    if (requestId === suggestionRequestId) {
      noteSuggestions.value = []
    }
  } finally {
    if (requestId === suggestionRequestId) {
      noteSuggestionLoading.value = false
    }
  }
}

async function loadAmountSuggestions() {
  if (!selectedCategoryId.value) {
    amountSuggestions.value = []
    return
  }

  const requestId = ++amountSuggestionRequestId
  amountSuggestionLoading.value = true

  try {
    const data = await txnStore.fetchAmountSuggestions({
      category_id: selectedCategoryId.value,
      type: recordType.value,
      limit: 8,
      recent_days: 30,
    })

    if (requestId === amountSuggestionRequestId) {
      amountSuggestions.value = data
    }
  } catch {
    if (requestId === amountSuggestionRequestId) {
      amountSuggestions.value = []
    }
  } finally {
    if (requestId === amountSuggestionRequestId) {
      amountSuggestionLoading.value = false
    }
  }
}

// 保存
async function handleSave() {
  const amt = parseFloat(amount.value)
  if (!amt || amt <= 0) {
    showToast('请输入有效金额')
    return
  }
  if (!selectedCategoryId.value) {
    showToast('请选择分类')
    return
  }

  await txnStore.addTransaction({
    amount: amt,
    type: recordType.value,
    category_id: selectedCategoryId.value,
    transaction_date: transactionDate.value,
    note: note.value,
  })

  showToast('记账成功')

  // Keep current category/type for fast consecutive entries.
  amount.value = ''
  note.value = ''
  showAmountSuggestions.value = false
  transactionDate.value = dayjs().format('YYYY-MM-DD')
  const nowValue = dayjs()
  dateValues.value = [
    nowValue.year().toString(),
    (nowValue.month() + 1).toString(),
    nowValue.date().toString(),
  ]

  loadNoteSuggestions()
  loadAmountSuggestions()
}

onMounted(() => {
  categoryStore.fetchCategories()
})

watch(selectedCategoryId, (newValue, oldValue) => {
  if (oldValue !== undefined && newValue !== oldValue) {
    note.value = ''
    showAmountSuggestions.value = false
  }
})

watch([selectedCategoryId, recordType], () => {
  loadNoteSuggestions()
  loadAmountSuggestions()
})
</script>

<style scoped>
.add-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 92px;
}

.form-wrap {
  padding: 0 16px 14px;
}

.type-switch {
  display: flex;
  background: white;
  border-radius: 16px;
  margin: 8px auto;
  width: 240px;
  overflow: hidden;
}

.type-switch span {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-switch span.active {
  background: #1989fa;
  color: white;
  border-radius: 24px;
}

.amount-input-wrap {
  text-align: center;
  padding: 14px 12px 18px;
  background: white;
  border-radius: 14px;
  margin-bottom: 10px;
}

.amount-input-title {
  color: #87909a;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.amount-title-suggestions {
  min-width: 0;
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.amount-title-list {
  display: flex;
  gap: 8px;
  max-width: 100%;
  overflow-x: auto;
  padding-bottom: 2px;
}

.amount-title-list::-webkit-scrollbar {
  height: 4px;
}

.amount-title-list::-webkit-scrollbar-thumb {
  background: #d9e4f2;
  border-radius: 999px;
}

.amount-title-status {
  color: #8693a0;
  font-size: 12px;
  white-space: nowrap;
}

.amount-title-status--empty {
  color: #9aa3ad;
}

.amount-input-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  justify-content: center;
}

.currency {
  font-size: 30px;
  color: #333;
}

.amount-input {
  font-size: 42px;
  border: none;
  outline: none;
  text-align: left;
  width: min(220px, calc(100vw - 170px));
  background: transparent;
}

.amount-clear-btn {
  border: 1px solid #d5d9df;
  background: #fff;
  color: #57606a;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  line-height: 1;
}

.amount-clear-btn:active {
  opacity: 0.75;
}

.amount-clear-btn--placeholder {
  visibility: hidden;
  pointer-events: none;
}

.note-panel {
  background: #fff;
  border-radius: 14px;
  margin-bottom: 10px;
  padding: 4px 12px 10px;
}

.category-section {
  background: white;
  border-radius: 14px;
  padding: 12px;
  margin: 10px 0;
}

.category-section__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.category-section h4 {
  font-size: 14px;
  color: #69717c;
  margin: 0;
}

.category-toggle {
  border: 1px solid #dce3eb;
  border-radius: 999px;
  font-size: 12px;
  color: #4e5b68;
  background: #fff;
  padding: 4px 12px;
}

.category-current {
  width: 100%;
  border: 1px solid #e6ecf4;
  border-radius: 10px;
  background: #f8fbff;
  padding: 9px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #3f4b57;
}

.category-current--empty {
  justify-content: center;
  color: #8b95a1;
}

.category-current__name {
  font-size: 13px;
  font-weight: 600;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 11px 4px;
  border-radius: 8px;
  border: 1px solid #e7edf4;
  cursor: pointer;
  background: white;
}

.category-item.selected {
  border-color: #1989fa;
  background: #ecf5ff;
}

.category-item--add {
  border-style: dashed;
  color: #1989fa;
  background: #f8fbff;
}

.cat-icon {
  display: block;
  font-size: 24px;
}

.cat-name {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.amount-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #e7eef8;
  background: #f7f9fd;
  color: #2e4f86;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  flex: 0 0 auto;
  white-space: nowrap;
}

.amount-chip--active {
  border-color: #1989fa;
  background: #eaf3ff;
  color: #0d5db8;
}

.amount-chip__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 10px;
  background: rgba(25, 137, 250, 0.14);
  color: #156cc4;
  font-size: 11px;
  line-height: 1;
}

.note-suggestion-section {
  margin-top: 2px;
  margin-bottom: 2px;
}

.note-suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
  font-size: 13px;
  margin-bottom: 7px;
}

.note-suggestion-list {
  display: flex;
  overflow-x: auto;
  padding-bottom: 2px;
  gap: 8px;
}

.note-suggestion-list::-webkit-scrollbar {
  height: 4px;
}

.note-suggestion-list::-webkit-scrollbar-thumb {
  background: #d9e4f2;
  border-radius: 999px;
}

.note-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #d8e6ff;
  background: #f5f9ff;
  color: #2f5fa7;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  flex: 0 0 auto;
}

.note-chip--active {
  border-color: #1989fa;
  background: #e8f3ff;
  color: #0d5db8;
}

.note-chip__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 10px;
  background: rgba(25, 137, 250, 0.14);
  color: #156cc4;
  font-size: 11px;
  line-height: 1;
}

.save-sticky {
  position: sticky;
  bottom: 40px;
  padding: 8px 16px calc(8px + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, rgba(247, 248, 250, 0) 0%, #f7f8fa 35%);
}

.save-sticky__inner {
  background: #fff;
  border-radius: 14px;
  padding: 10px;
  box-shadow: 0 6px 20px rgba(49, 86, 131, 0.12);
}

.add-category-wrap {
  padding: 20px 16px;
}

.add-category-wrap h4 {
  text-align: center;
  font-size: 16px;
  margin-bottom: 16px;
}

.add-category-actions {
  padding: 16px 0 8px;
}

@media (max-width: 360px) {
  .amount-input {
    font-size: 34px;
    width: min(180px, calc(100vw - 178px));
  }

  .category-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .amount-chip,
  .note-chip {
    font-size: 11px;
    padding: 5px 9px;
  }
}
</style>
