<template>
  <div class="settings-drawer-page">
    <van-popup
      v-model:show="showDrawer"
      position="right"
      :style="{ width: '86%', height: '100%' }"
      closeable
      @closed="handleClosed"
    >
      <div class="drawer-body">
        <van-nav-bar title="高级设置" left-arrow @click-left="closeDrawer" />

        <div class="drawer-content">
          <h3 class="drawer-title">工资设置</h3>
          <p class="drawer-desc">配置后会在发薪日自动补记一条收入账单。</p>

          <van-cell-group inset class="drawer-group">
            <van-field
              v-model="paydayText"
              label="发薪日"
              type="digit"
              input-align="right"
              placeholder="1-28"
            >
              <template #extra>
                <span class="field-unit">日</span>
              </template>
            </van-field>
            <van-field
              v-model="salaryAmountText"
              label="工资金额"
              type="number"
              input-align="right"
              placeholder="0.00"
            >
              <template #extra>
                <span class="field-unit">元</span>
              </template>
            </van-field>
          </van-cell-group>

          <van-button block type="primary" class="drawer-save" @click="handleSavePayroll">
            保存工资设置
          </van-button>

          <h3 class="drawer-title">路由配置</h3>
          <p class="drawer-desc">恢复后将重置为当前已保存的默认配置。</p>

          <van-button block type="danger" plain @click="handleResetConfig">
            恢复默认路由配置
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { usePayrollStore } from '@/stores/payroll'

const route = useRoute()
const router = useRouter()
const navStore = useNavigationStore()
const payrollStore = usePayrollStore()
const showDrawer = ref(false)
const paydayText = ref('')
const salaryAmountText = ref('')

function closeDrawer() {
  showDrawer.value = false
}

function handleClosed() {
  const returnTo = route.query.returnTo === 'countdown' ? 'countdown' : 'settings'
  router.replace({ name: returnTo })
}

function handleResetConfig() {
  navStore.resetConfig()
  showToast('已恢复默认路由配置')
  closeDrawer()
}

function syncForm() {
  paydayText.value = String(payrollStore.payday)
  salaryAmountText.value = payrollStore.salaryAmount ? String(payrollStore.salaryAmount) : ''
}

function handleSavePayroll() {
  const nextPayday = Number(paydayText.value)
  const nextSalaryAmount = Number(salaryAmountText.value || 0)

  if (!Number.isInteger(nextPayday) || nextPayday < 1 || nextPayday > 28) {
    showToast('发薪日请填写 1 到 28')
    return
  }

  if (!Number.isFinite(nextSalaryAmount) || nextSalaryAmount < 0) {
    showToast('工资金额不能小于 0')
    return
  }

  payrollStore.updateSettings({
    payday: nextPayday,
    salaryAmount: Number(nextSalaryAmount.toFixed(2)),
  })
  syncForm()
  showToast('工资设置已保存')
}

onMounted(() => {
  syncForm()
  showDrawer.value = true
})
</script>

<style scoped>
.settings-drawer-page {
  min-height: 100vh;
  background: transparent;
}

.drawer-body {
  height: 100%;
  background: #fff;
}

.drawer-content {
  padding: 16px;
}

.drawer-group {
  margin-bottom: 16px;
}

.drawer-title {
  font-size: 16px;
  color: #323233;
  margin: 0 0 8px;
}

.drawer-desc {
  font-size: 13px;
  color: #969799;
  margin: 0 0 16px;
  line-height: 1.5;
}

.drawer-save {
  margin-bottom: 24px;
}

.field-unit {
  color: #969799;
  font-size: 12px;
}
</style>
