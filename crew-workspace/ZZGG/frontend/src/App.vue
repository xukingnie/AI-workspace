<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { showFailToast, showSuccessToast } from 'vant'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000/api'

const showCalendar = ref(false)
const selectedDate = ref(new Date())
const backendStatus = ref('检测中')
const submitting = ref(false)
const countdownTime = ref(0)
const countdownDeadlineLabel = ref('')
const previewResult = ref(null)

const form = reactive({
  name: '',
  amount: '',
  note: '',
})

const selectedDateText = computed(() => formatDate(selectedDate.value))

function formatDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(value)
}

function resetCountdown() {
  const deadline = new Date()
  deadline.setDate(deadline.getDate() + 1)
  deadline.setHours(0, 0, 0, 0)
  countdownDeadlineLabel.value = formatDate(deadline) + ' 00:00'
  countdownTime.value = Math.max(deadline.getTime() - Date.now(), 0)
}

function onCalendarConfirm(date) {
  selectedDate.value = date
  showCalendar.value = false
}

async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) {
      throw new Error('backend unavailable')
    }
    const payload = await response.json()
    backendStatus.value = payload.message ?? 'FastAPI 已连接'
  } catch {
    backendStatus.value = 'FastAPI 预留接口未启动，当前使用前端本地预览'
  }
}

async function submitBill() {
  if (!form.name.trim() || !form.amount.trim()) {
    showFailToast('请填写账单名称和金额')
    return
  }

  const amount = Number(form.amount)
  if (Number.isNaN(amount) || amount <= 0) {
    showFailToast('金额必须为大于 0 的数字')
    return
  }

  const payload = {
    name: form.name.trim(),
    amount,
    note: form.note.trim(),
    billing_date: selectedDate.value.toISOString().slice(0, 10),
  }

  submitting.value = true

  try {
    const response = await fetch(`${API_BASE}/bills/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error('preview failed')
    }

    previewResult.value = await response.json()
    backendStatus.value = 'FastAPI 预留接口已响应'
    showSuccessToast('账单已提交到预留后端')
  } catch {
    previewResult.value = {
      message: '后端未启动，已生成本地账单预览。',
      received_at: new Date().toLocaleString('zh-CN', { hour12: false }),
      bill: payload,
    }
    backendStatus.value = 'FastAPI 预留接口未启动，已切换为本地预览'
    showFailToast('后端未启动，已切换本地预览')
  } finally {
    submitting.value = false
    resetCountdown()
  }
}

onMounted(() => {
  resetCountdown()
  checkBackend()
})
</script>

<template>
  <div class="page-shell">
    <header class="hero-panel">
      <div>
        <p class="eyebrow">ZZGG · Vant UI Demo</p>
        <h1>账单日历与倒计时示例</h1>
        <p class="hero-copy">
          使用 Vant Calendar、Field、Button 和 CountDown 组合一个可联调 FastAPI 的前后端示例。
        </p>
      </div>
      <div class="status-area">
        <van-tag type="primary" plain>后端状态</van-tag>
        <p>{{ backendStatus }}</p>
      </div>
    </header>

    <van-notice-bar
      left-icon="volume-o"
      text="当前 frontend 已接入预留 FastAPI 地址，未启动后端时会自动回退到本地账单预览。"
    />

    <main class="content-grid">
      <section class="panel-card">
        <div class="section-head">
          <h2>日历</h2>
          <span>Vant Calendar</span>
        </div>
        <van-cell-group inset>
          <van-cell
            title="账单日期"
            :value="selectedDateText"
            is-link
            @click="showCalendar = true"
          />
        </van-cell-group>
        <p class="helper-text">点击选择账单归属日期，默认取今天。</p>
        <van-calendar
          v-model:show="showCalendar"
          color="#1989fa"
          :show-confirm="false"
          @confirm="onCalendarConfirm"
        />
      </section>

      <section class="panel-card">
        <div class="section-head">
          <h2>倒计时</h2>
          <span>Vant CountDown</span>
        </div>
        <div class="countdown-box">
          <p class="countdown-label">距离下一次账单截止</p>
          <van-count-down :time="countdownTime" millisecond @finish="resetCountdown">
            <template #default="timeData">
              <div class="countdown-value">
                <span>{{ timeData.days }}天</span>
                <span>{{ timeData.hours.toString().padStart(2, '0') }}时</span>
                <span>{{ timeData.minutes.toString().padStart(2, '0') }}分</span>
                <span>{{ timeData.seconds.toString().padStart(2, '0') }}秒</span>
              </div>
            </template>
          </van-count-down>
          <p class="helper-text">目标时间：{{ countdownDeadlineLabel }}</p>
        </div>
      </section>

      <section class="panel-card full-width">
        <div class="section-head">
          <h2>账单表单</h2>
          <span>Vant Field + Button</span>
        </div>
        <van-form @submit="submitBill">
          <van-cell-group inset>
            <van-field v-model="form.name" label="账单名称" name="name" placeholder="例如：房租 / 水电费" />
            <van-field v-model="form.amount" label="金额" name="amount" type="number" placeholder="请输入金额" />
            <van-field
              v-model="form.note"
              label="备注"
              name="note"
              type="textarea"
              rows="3"
              autosize
              placeholder="可填写账单说明或后端预留字段"
            />
          </van-cell-group>
          <div class="action-row">
            <van-button block round type="primary" native-type="submit" :loading="submitting">
              提交账单
            </van-button>
          </div>
        </van-form>

        <van-divider>预览结果</van-divider>
        <div class="preview-card" v-if="previewResult">
          <p class="preview-title">{{ previewResult.message }}</p>
          <p>提交时间：{{ previewResult.received_at }}</p>
          <p>账单日期：{{ previewResult.bill.billing_date }}</p>
          <p>账单名称：{{ previewResult.bill.name }}</p>
          <p>账单金额：¥ {{ previewResult.bill.amount }}</p>
          <p v-if="previewResult.bill.note">备注：{{ previewResult.bill.note }}</p>
        </div>
        <p v-else class="helper-text">提交后将在这里展示 FastAPI 返回结果或本地预览。</p>
      </section>
    </main>
  </div>
</template>
