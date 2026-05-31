import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getCurrentUser, loginByCode, logoutAuth, sendLoginCode, type AuthUser } from '@/api/auth'
import { clearStoredSession, readStoredSession, writeStoredSession } from '@/auth/session'

export const useUserStore = defineStore('user', () => {
  const user = ref<AuthUser | null>(null)
  const accessToken = ref('')
  const bootstrapped = ref(false)

  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const phone = computed(() => user.value?.phone ?? '')

  function persistSession() {
    if (!accessToken.value || !user.value) {
      clearStoredSession()
      return
    }
    writeStoredSession({
      accessToken: accessToken.value,
      user: user.value,
    })
  }

  function restoreSession() {
    const saved = readStoredSession()
    if (!saved) return
    accessToken.value = saved.accessToken
    user.value = saved.user
  }

  function clearSession() {
    user.value = null
    accessToken.value = ''
    clearStoredSession()
  }

  async function bootstrap() {
    if (bootstrapped.value) return

    restoreSession()
    if (!accessToken.value) {
      bootstrapped.value = true
      return
    }

    try {
      const res = await getCurrentUser()
      user.value = res.data
      persistSession()
    } catch {
      clearSession()
    } finally {
      bootstrapped.value = true
    }
  }

  async function requestLoginCode(phoneValue: string) {
    const res = await sendLoginCode(phoneValue)
    return res.data
  }

  async function loginWithCode(phoneValue: string, code: string) {
    const res = await loginByCode(phoneValue, code)
    accessToken.value = res.data.access_token
    user.value = res.data.user
    persistSession()
    return res.data
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await logoutAuth()
      }
    } catch {
      // ignore logout network errors and clear local session anyway
    } finally {
      clearSession()
    }
  }

  return {
    user,
    phone,
    accessToken,
    isAuthenticated,
    bootstrapped,
    bootstrap,
    requestLoginCode,
    loginWithCode,
    logout,
    clearSession,
  }
})
