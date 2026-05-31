<template>
  <div class="add-page">
    <van-nav-bar title="记账" />
    <div class="form-wrap">
      <!-- 类型切换 -->
      <div class="type-switch">
        <span :class="typeSwitchClass('income')" @click="recordType = 'income'"> 收入 </span>
        <span :class="typeSwitchClass('expense')" @click="recordType = 'expense'"> 支出 </span>
      </div>
      <!-- 分类选择 -->
      <div class="category-section">
        <h4>选择分类</h4>
        <div class="category-grid">
          <div
            v-for="cat in filteredCategories"
            :key="cat.id"
            :class="['category-item', { selected: selectedCategoryId === cat.id }]"
            @click="selectedCategoryId = cat.id"
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
      </div>
      <!-- 日期 -->
      <van-field
        v-model="transactionDate"
        label="日期"
        readonly
        is-link
        @click="showDatePicker = true"
      />
      <!-- 备注 -->
      <van-field v-model="note" label="备注" placeholder="请输入备注（可选）" />
      <!-- 保存按钮 -->
      <div class="save-btn">
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { showToast } from 'vant'
import { useCategoryStore } from '@/stores/category'
import { useTransactionStore } from '@/stores/transaction'
import { getCategoryIcon, getDefaultCategoryIcon } from '@/options/categories'

const router = useRouter()
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

function onDateConfirm({ selectedValues }: { selectedValues: number[] }) {
  transactionDate.value = `${selectedValues[0]}-${String(selectedValues[1]).padStart(2, '0')}-${String(selectedValues[2]).padStart(2, '0')}`
  showDatePicker.value = false
}

function openAddCategory() {
  newCategoryName.value = ''
  showAddCategory.value = true
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
  showToast('分类已添加')
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
  router.push('/')
}

onMounted(() => {
  categoryStore.fetchCategories()
})
</script>

<style scoped>
.add-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.form-wrap {
  padding: 0 16px;
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
  padding: 20px 0;
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
}

.currency {
  font-size: 32px;
  color: #333;
}

.amount-input {
  font-size: 40px;
  border: none;
  outline: none;
  text-align: center;
  width: 200px;
  background: transparent;
}

.category-section {
  background: white;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.category-section h4 {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
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
  padding: 10px 4px;
  border-radius: 8px;
  border: 1px solid #eee;
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

.save-btn {
  padding: 20px 0;
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
</style>
