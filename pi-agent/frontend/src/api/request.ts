import axios from 'axios'
import { showToast } from 'vant'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || '请求失败'
    showToast({ message: msg, icon: 'fail' })
    return Promise.reject(err)
  },
)

export default request
