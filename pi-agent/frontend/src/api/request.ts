import axios from 'axios'
import { showToast } from 'vant'
import { getStoredAccessToken } from '@/auth/session'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = getStoredAccessToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    const msg = err.response?.data?.detail || '请求失败'
    showToast({ message: msg, icon: 'fail' })
    return Promise.reject(err)
  },
)

export default request
