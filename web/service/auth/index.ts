import { http } from './base'

/**
 * 认证相关 API
 */

export interface LoginParams {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: {
    id: string
    email: string
    name: string
  }
}

export interface RegisterParams {
  email: string
  password: string
  name: string
}

/**
 * 登录
 */
export const login = (params: LoginParams) => 
  http.post<LoginResponse>('/api/console/auth/login', params)

/**
 * 注册
 */
export const register = (params: RegisterParams) =>
  http.post('/api/console/auth/register', params)

/**
 * 登出
 */
export const logout = () =>
  http.post('/api/console/auth/logout')

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () =>
  http.get('/api/console/auth/me')

/**
 * 刷新 Token
 */
export const refreshToken = (refreshToken: string) =>
  http.post('/api/console/auth/refresh', { refresh_token: refreshToken })
