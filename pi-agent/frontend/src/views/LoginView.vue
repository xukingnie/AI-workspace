<template>
  <div class="login-page">
    <div class="login-panel">
      <h1 class="login-title">手机号登录</h1>

      <van-field
        v-model="phone"
        class="login-field"
        name="phone"
        label="手机号"
        type="tel"
        autocomplete="tel"
        maxlength="11"
        placeholder="请输入手机号"
      />

      <van-field
        v-model="code"
        class="login-field"
        name="verification-code"
        label="验证码"
        autocomplete="off"
        maxlength="6"
        placeholder="请输入验证码"
      >
        <template #button>
          <van-button
            size="small"
            type="primary"
            plain
            :disabled="countdown > 0"
            @click="handleSendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
          </van-button>
        </template>
      </van-field>

      <van-button
        block
        type="primary"
        class="login-submit"
        :loading="submitting"
        @click="handleLogin"
      >
        登录
      </van-button>

      <p class="login-hint" v-if="showByDev">开发环境会返回测试验证码（debug_code）。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const showByDev = import.meta.env.DEV

import { ref } from 'vue'
import { showToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const phone = ref('')
const code = ref('')
const submitting = ref(false)
const countdown = ref(0)
let timer: number | null = null

function validatePhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

function startCountdown(seconds: number) {
  if (timer) {
    window.clearInterval(timer)
    timer = null
  }

  countdown.value = seconds
  timer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      if (timer) window.clearInterval(timer)
      timer = null
      countdown.value = 0
    }
  }, 1000)
}

async function handleSendCode() {
  const phoneValue = phone.value.trim()
  if (!validatePhone(phoneValue)) {
    showToast('请输入正确手机号')
    return
  }

  try {
    const res = await userStore.requestLoginCode(phoneValue)
    startCountdown(res.expire_seconds > 60 ? 60 : res.expire_seconds)

    if (res.debug_code) {
      showToast(`测试验证码: ${res.debug_code}`)
      return
    }
    showToast('验证码已发送')
  } catch {
    // request 拦截器会处理失败提示
  }
}

async function handleLogin() {
  const phoneValue = phone.value.trim()
  const codeValue = code.value.trim()

  if (!validatePhone(phoneValue)) {
    showToast('请输入正确手机号')
    return
  }
  if (codeValue.length < 4) {
    showToast('请输入有效验证码')
    return
  }

  submitting.value = true
  try {
    await userStore.loginWithCode(phoneValue, codeValue)
    const redirectPath = typeof route.query.redirect === 'string' ? route.query.redirect : '/home'
    router.replace(redirectPath)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f3f8ff 0%, #ffffff 45%, #eef6ff 100%);
  padding: 24px;
}

.login-panel {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 22px 16px 18px;
  box-shadow: 0 10px 26px rgba(18, 85, 204, 0.12);
}

.login-title {
  margin: 8px 0;
  font-size: 24px;
  color: #1f2a44;
}

.login-field + .login-field {
  margin-top: 10px;
}

.login-submit {
  margin-top: 18px;
}

.login-hint {
  margin: 12px 0 0;
  font-size: 12px;
  color: #7c879c;
}
</style>
