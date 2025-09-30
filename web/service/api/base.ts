import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

/**
 * API 基础配置
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

/**
 * 创建 Axios 实例
 */
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 请求拦截器
 */
axiosInstance.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 */
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      // 处理 401 未授权
      if (error.response.status === 401) {
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      }
      
      // 返回错误信息
      return Promise.reject(error.response.data)
    }
    
    return Promise.reject(error)
  }
)

/**
 * SWR fetcher
 */
export const fetcher = (url: string) => axiosInstance.get(url)

/**
 * HTTP 请求方法
 */
export const http = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    axiosInstance.get<T, T>(url, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    axiosInstance.post<T, T>(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    axiosInstance.put<T, T>(url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    axiosInstance.delete<T, T>(url, config),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    axiosInstance.patch<T, T>(url, data, config),
}

export default axiosInstance
