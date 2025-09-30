/**
 * 通用类型定义
 */

/**
 * 分页参数
 */
export interface PaginationParams {
  page: number
  page_size: number
}

/**
 * 分页响应
 */
export interface PaginationResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

/**
 * API 响应
 */
export interface ApiResponse<T = any> {
  data: T
  message?: string
  error?: string
}

/**
 * 用户信息
 */
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  created_at: string
  updated_at: string
}

/**
 * 应用类型
 */
export enum AppType {
  CHAT = 'chat',
  COMPLETION = 'completion',
  AGENT = 'agent',
  WORKFLOW = 'workflow',
}

/**
 * 应用信息
 */
export interface App {
  id: string
  name: string
  description: string
  type: AppType
  icon: string
  icon_background: string
  created_at: string
  updated_at: string
}

/**
 * 工作流信息
 */
export interface Workflow {
  id: string
  app_id: string
  name: string
  description: string
  graph: any // 工作流图数据
  created_at: string
  updated_at: string
}

/**
 * 知识库信息
 */
export interface Dataset {
  id: string
  name: string
  description: string
  provider: string
  permission: string
  document_count: number
  word_count: number
  created_at: string
  updated_at: string
}
