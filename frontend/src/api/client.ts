import axios from 'axios'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: localStorage.getItem('api_base_url') || window.location.origin,
  timeout: 30000,
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function setBaseUrl(url: string) {
  client.defaults.baseURL = url
  localStorage.setItem('api_base_url', url)
}

export function getBaseUrl(): string {
  return client.defaults.baseURL as string
}

export default client
