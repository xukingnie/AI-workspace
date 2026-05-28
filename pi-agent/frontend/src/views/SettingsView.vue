<template>
  <div class="settings-page">
    <van-nav-bar title="我的" />

    <div class="section">
      <h3 class="section-title">数据导出</h3>
      <van-cell-group inset>
        <van-cell title="导出 Excel" label="导出账单明细为 Excel 文件" is-link @click="handleExportExcel" />
        <van-cell title="导出 PDF" label="导出账单明细为 PDF 文件" is-link @click="handleExportPDF" />
      </van-cell-group>
    </div>

    <div class="section">
      <h3 class="section-title">分类管理</h3>
      <van-cell-group inset>
        <van-swipe-cell v-for="cat in categoryStore.categories" :key="cat.id">
          <van-cell :title="getCategoryIcon(cat.icon) + ' ' + cat.name" :label="cat.type === 'income' ? '收入' : '支出'" />
          <template #right>
            <van-button square type="primary" class="edit-btn" @click="handleEditCategory(cat.id)">
              编辑
            </van-button>
            <van-button square type="danger" class="delete-btn" @click="handleDeleteCategory(cat.id)">
              删除
            </van-button>
          </template>
        </van-swipe-cell>
      </van-cell-group>
      <div class="add-category-btn">
        <van-button type="primary" block @click="resetCategoryForm(); showAddCategory = true">
          新增分类
        </van-button>
      </div>
    </div>

    <!-- 日期范围选择弹窗（导出用） -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <div class="date-picker-wrap">
        <h4>选择导出日期范围（可选）</h4>
        <van-field v-model="exportStartDate" label="开始日期" placeholder="不选则导出全部" readonly
          @click="showStartPicker = true" />
        <van-field v-model="exportEndDate" label="结束日期" placeholder="不选则导出全部" readonly @click="showEndPicker = true" />
        <div class="date-picker-actions">
          <van-button round block type="primary" @click="confirmExport">确认导出</van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showStartPicker" position="bottom">
      <van-date-picker v-model="startDateValues" title="选择开始日期" :min-date="new Date(2020, 0, 1)" :max-date="new Date()"
        @confirm="onStartDateConfirm" @cancel="showStartPicker = false" />
    </van-popup>

    <van-popup v-model:show="showEndPicker" position="bottom">
      <van-date-picker v-model="endDateValues" title="选择结束日期" :min-date="new Date(2020, 0, 1)" :max-date="new Date()"
        @confirm="onEndDateConfirm" @cancel="showEndPicker = false" />
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
          <van-button round block type="primary" @click="handleSaveCategory">
            {{ editingCategoryId ? '确认保存' : '确认添加' }}
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showToast, showConfirmDialog, closeToast } from 'vant'
import { useCategoryStore } from '@/stores/category'
import { getCategoryIcon } from '@/options/categories'
import { exportExcel, exportPDF } from '@/api/export'

const categoryStore = useCategoryStore()

// ========== 导出相关 ==========
const showDatePicker = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const exportStartDate = ref('')
const exportEndDate = ref('')
const startDateValues = ref<string[]>([new Date().getFullYear().toString(), '1', '1'])
const endDateValues = ref<string[]>([new Date().getFullYear().toString(), (new Date().getMonth() + 1).toString(), new Date().getDate().toString()])

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
    })
    showToast('添加成功')
  }

  showAddCategory.value = false
  resetCategoryForm()
}

async function handleDeleteCategory(id: number) {
  try {
    await showConfirmDialog({ title: '确认删除', message: '确定要删除该分类吗？' })
  } catch {
    return
  }
  await categoryStore.removeCategory(id)
  showToast('删除成功')
}

onMounted(() => {
  categoryStore.fetchCategories()
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
}

.delete-btn {
  width: 72px;
  height: 100%;
}

.edit-btn {
  width: 72px;
  height: 100%;
  border-color: #1989fa;
}

:deep(.van-swipe-cell__right) {
  display: flex;
}

:deep(.edit-btn .van-button__content),
:deep(.delete-btn .van-button__content) {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
