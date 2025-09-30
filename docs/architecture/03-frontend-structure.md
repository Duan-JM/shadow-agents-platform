# Dify 前端架构详解

## 目录结构

```
web/
├── app/                          # Next.js App Router
│   ├── (commonLayout)/          # 通用布局组
│   │   ├── app/                # 应用相关页面
│   │   ├── datasets/           # 知识库页面
│   │   ├── tools/              # 工具页面
│   │   ├── plugins/            # 插件页面
│   │   └── explore/            # 探索页面
│   │
│   ├── (shareLayout)/           # 分享布局组
│   │   └── share/              # 分享相关
│   │
│   ├── components/              # 页面级组件
│   │   ├── app/                # 应用组件
│   │   ├── datasets/           # 知识库组件
│   │   ├── workflow/           # 工作流组件
│   │   ├── tools/              # 工具组件
│   │   ├── header/             # 头部组件
│   │   └── sidebar/            # 侧边栏组件
│   │
│   ├── signin/                  # 登录页面
│   ├── signup/                  # 注册页面
│   ├── activate/                # 激活页面
│   ├── forgot-password/         # 忘记密码
│   ├── install/                 # 安装向导
│   ├── layout.tsx               # 根布局
│   └── page.tsx                 # 首页
│
├── assets/                       # 静态资源
│   ├── icons/                   # 图标
│   ├── images/                  # 图片
│   └── fonts/                   # 字体
│
├── config/                       # 配置文件
│   └── index.ts                 # 全局配置
│
├── context/                      # React Context
│   ├── app-context.tsx          # 应用上下文
│   ├── modal-context.tsx        # 弹窗上下文
│   └── ...
│
├── hooks/                        # 自定义 Hooks
│   ├── use-app.ts              # 应用相关
│   ├── use-datasets.ts         # 知识库相关
│   ├── use-workflow.ts         # 工作流相关
│   └── ...
│
├── i18n/                         # 国际化
│   ├── en-US/                   # 英文
│   ├── zh-Hans/                 # 简体中文
│   ├── ja-JP/                   # 日文
│   └── ...                      # 14+ 语言
│
├── models/                       # 数据模型/类型
│   ├── app.ts                   # 应用模型
│   ├── datasets.ts              # 知识库模型
│   ├── workflow.ts              # 工作流模型
│   └── ...
│
├── service/                      # API 服务层
│   ├── base.ts                  # 基础服务
│   ├── apps.ts                  # 应用服务
│   ├── datasets.ts              # 知识库服务
│   ├── workflow.ts              # 工作流服务
│   └── ...
│
├── types/                        # TypeScript 类型定义
│   ├── app.ts
│   ├── workflow.ts
│   └── ...
│
├── utils/                        # 工具函数
│   ├── format.ts                # 格式化
│   ├── language.ts              # 语言处理
│   ├── var.ts                   # 变量处理
│   └── ...
│
├── styles/                       # 样式文件
│   └── globals.css              # 全局样式
│
├── public/                       # 公共静态文件
│   ├── icons/
│   └── images/
│
├── middleware.ts                 # Next.js 中间件
├── next.config.js               # Next.js 配置
├── tailwind.config.ts           # Tailwind 配置
├── tsconfig.json                # TypeScript 配置
└── package.json                 # 依赖配置
```

## 技术栈

### 核心框架

```json
{
  "dependencies": {
    // 核心框架
    "next": "15.5.0",              // React 服务端渲染框架
    "react": "19.1.1",             // UI 框架
    "react-dom": "19.1.1",         // React DOM
    
    // 状态管理
    "swr": "^2.3.0",               // 数据获取和缓存
    "use-context-selector": "^2.0.0",  // Context 优化
    "ahooks": "^3.8.4",            // React Hooks 库
    
    // UI 组件库
    "@headlessui/react": "2.2.1",  // 无样式组件
    "@heroicons/react": "^2.0.16", // 图标库
    "@remixicon/react": "^4.5.0",  // 图标库
    
    // 样式
    "tailwindcss": "^3.x",         // CSS 框架
    "@tailwindcss/typography": "^0.5.15",
    "tailwind-merge": "^2.5.4",    // 样式合并
    "class-variance-authority": "^0.7.0",  // 样式变体
    "classnames": "^2.5.1",        // 类名拼接
    
    // 表单处理
    "react-hook-form": "^7.53.1",  // 表单管理
    "@hookform/resolvers": "^3.9.0",
    "zod": "^3.23.8",              // 数据验证
    
    // 数据可视化
    "reactflow": "^11.11.3",       // 流程图 (工作流设计器)
    "@dagrejs/dagre": "^1.1.4",    // 图布局算法
    "echarts": "^5.5.1",           // 图表库
    "echarts-for-react": "^3.0.2",
    "mermaid": "11.10.0",          // 流程图渲染
    
    // 编辑器
    "@monaco-editor/react": "^4.6.0",      // 代码编辑器
    "lexical": "^0.30.0",                  // 富文本编辑器
    "@lexical/react": "^0.30.0",
    
    // Markdown
    "react-markdown": "^9.0.1",    // Markdown 渲染
    "remark-gfm": "^4.0.0",        // GitHub Flavored Markdown
    "remark-math": "^6.0.0",       // 数学公式
    "rehype-katex": "^7.0.1",      // KaTeX 渲染
    
    // HTTP 客户端
    "ky": "^1.7.2",                // 现代 HTTP 客户端
    
    // 国际化
    "i18next": "^23.16.4",         // 国际化框架
    "react-i18next": "^15.1.0",
    
    // 工具库
    "lodash-es": "^4.17.21",       // 工具函数
    "dayjs": "^1.11.13",           // 日期处理
    "uuid": "^10.0.0",             // UUID 生成
    "qs": "^6.13.0",               // 查询字符串
    "immer": "^9.0.19",            // 不可变数据
    
    // 其他
    "copy-to-clipboard": "^3.3.3", // 复制到剪贴板
    "dompurify": "^3.2.4",         // XSS 防护
    "jwt-decode": "^4.0.0",        // JWT 解析
    "react-error-boundary": "^4.1.2",  // 错误边界
    "@sentry/react": "^8.54.0"     // 错误追踪
  }
}
```

## 架构设计

### 1. Next.js App Router

采用 Next.js 15 的 App Router 架构:

```
app/
├── (commonLayout)/          # 路由组 - 共享通用布局
│   ├── layout.tsx          # 布局组件
│   └── [pages]/            # 各个页面
│
├── (shareLayout)/           # 路由组 - 共享分享布局
│   └── share/
│
└── layout.tsx              # 根布局
```

**优势**:
- ✅ 服务端渲染 (SSR)
- ✅ 服务端组件 (RSC)
- ✅ 流式渲染
- ✅ 布局嵌套
- ✅ 加载状态
- ✅ 错误处理

### 2. 组件架构

#### 组件分层

```
┌─────────────────────────────────────┐
│        Page Components              │
│      (页面级组件,业务逻辑)            │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│     Feature Components              │
│    (功能组件,可复用业务组件)          │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│       Base Components               │
│     (基础组件,纯展示组件)            │
└─────────────────────────────────────┘
```

#### 组件示例

**Base Components** (基础组件):
```typescript
// components/base/button/index.tsx
import type { FC } from 'react'
import cn from 'classnames'

type ButtonProps = {
  variant?: 'primary' | 'secondary'
  onClick?: () => void
  children: React.ReactNode
}

const Button: FC<ButtonProps> = ({
  variant = 'primary',
  onClick,
  children,
}) => {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded-lg',
        variant === 'primary' && 'bg-blue-600 text-white',
        variant === 'secondary' && 'bg-gray-200 text-gray-700',
      )}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

export default Button
```

**Feature Components** (功能组件):
```typescript
// app/components/workflow/node-panel/index.tsx
import type { FC } from 'react'
import { useWorkflowStore } from '@/store/workflow'
import NodeCard from './node-card'

const NodePanel: FC = () => {
  const nodes = useWorkflowStore(s => s.availableNodes)
  
  return (
    <div className="w-64 bg-white border-r">
      <h3 className="px-4 py-2 font-semibold">Nodes</h3>
      <div className="space-y-2 p-4">
        {nodes.map(node => (
          <NodeCard key={node.type} node={node} />
        ))}
      </div>
    </div>
  )
}

export default NodePanel
```

### 3. 状态管理

#### SWR 数据获取

```typescript
// hooks/use-apps.ts
import useSWR from 'swr'
import { fetchApps } from '@/service/apps'

export const useApps = () => {
  const { data, error, mutate } = useSWR('/apps', fetchApps, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  })
  
  return {
    apps: data?.data || [],
    isLoading: !error && !data,
    isError: error,
    mutate,
  }
}
```

#### Context 状态管理

```typescript
// context/app-context.tsx
'use client'
import { createContext } from 'use-context-selector'
import type { FC, ReactNode } from 'react'

type AppContextValue = {
  currentAppId: string | null
  setCurrentAppId: (id: string) => void
}

export const AppContext = createContext<AppContextValue>({
  currentAppId: null,
  setCurrentAppId: () => {},
})

export const AppContextProvider: FC<{ children: ReactNode }> = ({ 
  children 
}) => {
  const [currentAppId, setCurrentAppId] = useState<string | null>(null)
  
  return (
    <AppContext.Provider value={{ currentAppId, setCurrentAppId }}>
      {children}
    </AppContext.Provider>
  )
}
```

### 4. API 服务层

统一的 API 调用封装:

```typescript
// service/base.ts
import ky from 'ky'

const api = ky.create({
  prefixUrl: '/api',
  timeout: 60000,
  hooks: {
    beforeRequest: [
      request => {
        const token = localStorage.getItem('token')
        if (token)
          request.headers.set('Authorization', `Bearer ${token}`)
      },
    ],
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          // 处理未授权
          window.location.href = '/signin'
        }
        return response
      },
    ],
  },
})

export default api
```

```typescript
// service/apps.ts
import api from './base'
import type { App, AppListResponse } from '@/types/app'

export const fetchApps = async (): Promise<AppListResponse> => {
  return api.get('apps').json()
}

export const createApp = async (data: Partial<App>): Promise<App> => {
  return api.post('apps', { json: data }).json()
}

export const updateApp = async (
  id: string, 
  data: Partial<App>
): Promise<App> => {
  return api.put(`apps/${id}`, { json: data }).json()
}

export const deleteApp = async (id: string): Promise<void> => {
  return api.delete(`apps/${id}`).json()
}
```

### 5. 路由和导航

```typescript
// Next.js App Router 路由
app/
  (commonLayout)/
    app/
      [appId]/
        overview/page.tsx     # /app/:appId/overview
        logs/page.tsx         # /app/:appId/logs
        configuration/
          page.tsx            # /app/:appId/configuration
```

**编程式导航**:
```typescript
'use client'
import { useRouter } from 'next/navigation'

const Component = () => {
  const router = useRouter()
  
  const handleNavigate = () => {
    router.push('/app/123/overview')
  }
  
  return <button onClick={handleNavigate}>Go to App</button>
}
```

## 核心功能模块

### 1. 应用管理

**功能**:
- 应用列表展示
- 应用创建向导
- 应用配置编辑
- 应用发布管理

**关键组件**:
- `app/(commonLayout)/app/page.tsx` - 应用列表页
- `app/components/app/overview/*` - 应用概览
- `app/components/app/configuration/*` - 应用配置

### 2. 工作流设计器

**功能**:
- 可视化流程编辑
- 节点拖拽
- 连线管理
- 变量系统
- 调试运行

**核心技术**:
- **ReactFlow**: 流程图库
- **Dagre**: 自动布局算法
- **Zustand/Context**: 状态管理

**关键组件**:
```
app/components/workflow/
├── panel/                   # 节点面板
├── canvas/                  # 画布
├── nodes/                   # 节点组件
│   ├── llm/                # LLM 节点
│   ├── code/               # 代码节点
│   ├── http-request/       # HTTP 节点
│   └── ...
├── edges/                   # 连线组件
├── hooks/                   # 工作流 Hooks
└── store/                   # 状态管理
```

**工作流数据结构**:
```typescript
type Workflow = {
  id: string
  name: string
  graph: {
    nodes: Node[]
    edges: Edge[]
    viewport: Viewport
  }
  features: {
    opening: OpeningConfig
    suggested: SuggestedConfig
    // ...
  }
  environment_variables: EnvironmentVariable[]
}

type Node = {
  id: string
  type: string  // 'llm' | 'code' | 'http-request' | ...
  position: { x: number; y: number }
  data: Record<string, any>
}

type Edge = {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
}
```

### 3. 知识库管理

**功能**:
- 知识库创建
- 文档上传
- 分段管理
- 索引配置
- 检索测试

**关键组件**:
```
app/components/datasets/
├── create/                  # 创建知识库
├── documents/               # 文档管理
│   ├── list/               # 文档列表
│   ├── detail/             # 文档详情
│   └── segment/            # 分段编辑
├── settings/                # 设置
└── hit-testing/            # 检索测试
```

### 4. 对话界面

**功能**:
- 消息发送/接收
- 流式响应
- 多模态支持 (文本/图片/文件)
- 引用展示
- 反馈收集

**关键技术**:
- **SSE (Server-Sent Events)**: 流式响应
- **WebSocket**: 实时通信 (可选)

**流式响应处理**:
```typescript
// utils/sse.ts
export const fetchSSE = async (
  url: string,
  options: RequestInit,
  onMessage: (data: any) => void,
  onError?: (error: Error) => void,
) => {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Accept': 'text/event-stream',
    },
  })

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader!.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))
        onMessage(data)
      }
    }
  }
}
```

### 5. 配置管理

**模型配置**:
```typescript
type ModelConfig = {
  provider: string
  model: string
  parameters: {
    temperature?: number
    top_p?: number
    max_tokens?: number
    presence_penalty?: number
    frequency_penalty?: number
  }
  credentials: Record<string, string>
}
```

**应用配置**:
```typescript
type AppConfig = {
  opening_statement?: string
  suggested_questions?: string[]
  suggested_questions_after_answer?: {
    enabled: boolean
  }
  speech_to_text?: {
    enabled: boolean
  }
  retriever_resource?: {
    enabled: boolean
  }
  sensitive_word_avoidance?: {
    enabled: boolean
    words: string[]
  }
  more_like_this?: {
    enabled: boolean
  }
}
```

## 样式系统

### Tailwind CSS

**配置** (`tailwind.config.ts`):
```typescript
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          // ...
          600: '#2563eb',
          // ...
        },
      },
      spacing: {
        // 自定义间距
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

**使用示例**:
```tsx
<div className="flex items-center justify-between px-4 py-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
  <span className="text-sm font-medium text-gray-700">Title</span>
  <button className="px-3 py-1 text-sm text-white bg-primary-600 rounded hover:bg-primary-700">
    Action
  </button>
</div>
```

### CSS Modules (可选)

```typescript
// components/button/index.module.css
.button {
  @apply px-4 py-2 rounded-lg transition-colors;
}

.primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
```

```tsx
// components/button/index.tsx
import styles from './index.module.css'

const Button = () => {
  return (
    <button className={`${styles.button} ${styles.primary}`}>
      Click me
    </button>
  )
}
```

## 国际化 (i18n)

### 配置

```typescript
// i18n/index.ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      'en-US': {
        translation: require('./en-US/translation.json'),
      },
      'zh-Hans': {
        translation: require('./zh-Hans/translation.json'),
      },
    },
    lng: 'en-US',
    fallbackLng: 'en-US',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
```

### 使用

```typescript
import { useTranslation } from 'react-i18next'

const Component = () => {
  const { t } = useTranslation()
  
  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('common.description')}</p>
    </div>
  )
}
```

**支持的语言**:
- 🇬🇧 English
- 🇨🇳 简体中文
- 🇹🇼 繁体中文
- 🇯🇵 日本語
- 🇰🇷 한국어
- 🇫🇷 Français
- 🇩🇪 Deutsch
- 🇪🇸 Español
- 🇵🇹 Português
- 🇻🇳 Tiếng Việt
- 等 14+ 种语言

## 性能优化

### 1. 代码分割

```typescript
// 动态导入
import dynamic from 'next/dynamic'

const WorkflowEditor = dynamic(
  () => import('@/components/workflow/editor'),
  { ssr: false, loading: () => <Loading /> }
)
```

### 2. 图片优化

```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority  // 优先加载
/>
```

### 3. 数据缓存

```typescript
// SWR 配置
useSWR('/api/apps', fetcher, {
  revalidateOnFocus: false,
  revalidateOnReconnect: false,
  dedupingInterval: 5000,  // 5秒内不重复请求
})
```

### 4. 虚拟列表

```typescript
import { FixedSizeList } from 'react-window'

<FixedSizeList
  height={600}
  itemCount={1000}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>Item {index}</div>
  )}
</FixedSizeList>
```

## 开发工具

### ESLint 配置

```javascript
// eslint.config.mjs
export default [
  {
    rules: {
      'no-console': 'warn',
      'no-unused-vars': 'error',
      // ...
    },
  },
]
```

### TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

## 部署

### 构建

```bash
# 安装依赖
pnpm install

# 构建
pnpm build

# 启动
pnpm start
```

### Docker 部署

```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm build

FROM node:22-alpine AS runner
WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

---

**文档版本**: v1.0  
**最后更新**: 2025-09-30  
**基于 Dify 版本**: 1.9.1
