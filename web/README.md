# Shadow Agents Platform - 前端

基于 Next.js 15 + React 19 的前端应用。

## 技术栈

- **框架**: Next.js 15 (App Router)
- **UI 库**: React 19
- **语言**: TypeScript 5.7
- **样式**: Tailwind CSS 3.4
- **状态管理**: Zustand 5.0
- **数据获取**: SWR 2.2
- **HTTP 客户端**: Axios 1.7
- **表单**: React Hook Form 7.54
- **图标**: Heroicons 2.2
- **工作流**: ReactFlow 11.11

## 目录结构

```
web/
├── app/                    # Next.js App Router
│   ├── (auth)/            # 认证相关页面（登录、注册）
│   ├── (commonLayout)/    # 应用主布局页面
│   ├── api/               # API Routes
│   └── layout.tsx         # 根布局
├── components/            # React 组件
│   ├── base/             # 基础组件（按钮、输入框等）
│   ├── app/              # 应用相关组件
│   ├── workflow/         # 工作流组件
│   └── dataset/          # 知识库组件
├── hooks/                # 自定义 Hooks
├── service/              # API 服务层
│   ├── api/             # API 基础配置
│   ├── auth/            # 认证相关 API
│   ├── app/             # 应用相关 API
│   ├── workflow/        # 工作流相关 API
│   └── dataset/         # 知识库相关 API
├── context/              # React Context
├── types/                # TypeScript 类型定义
├── utils/                # 工具函数
├── i18n/                 # 国际化配置
├── styles/               # 全局样式
└── public/               # 静态资源
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm（推荐）
pnpm install

# 或使用 yarn
yarn install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env.local

# 编辑 .env.local 文件
vim .env.local
```

### 3. 启动开发服务器

```bash
npm run dev
# 或
pnpm dev
# 或
yarn dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 4. 构建生产版本

```bash
npm run build
npm start
```

## 开发指南

### 代码风格

- 使用 TypeScript 严格模式
- 遵循 ESLint 规则
- 使用 Prettier 格式化代码
- 2 空格缩进
- 所有注释使用中文

### 组件开发

- 使用函数式组件和 Hooks
- 组件文件使用 PascalCase 命名
- 组件必须添加 JSDoc 注释
- 优先使用组合而非继承

示例：

```tsx
/**
 * 按钮组件
 * 
 * @param props - 组件属性
 */
export function Button({ children, onClick }: ButtonProps) {
  return (
    <button onClick={onClick} className="btn-primary">
      {children}
    </button>
  )
}
```

### API 调用

使用 SWR 进行数据获取：

```tsx
import useSWR from 'swr'

function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher)
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error</div>
  
  return <div>Hello {data.name}!</div>
}
```

### 状态管理

使用 Zustand 管理全局状态：

```tsx
import { create } from 'zustand'

interface AppState {
  apps: App[]
  setApps: (apps: App[]) => void
}

export const useAppStore = create<AppState>((set) => ({
  apps: [],
  setApps: (apps) => set({ apps }),
}))
```

### 样式规范

- 优先使用 Tailwind CSS 工具类
- 复杂样式使用 CSS Modules 或 `@layer components`
- 响应式设计优先（移动端适配）

### 路由

使用 Next.js App Router：

- 页面文件：`page.tsx`
- 布局文件：`layout.tsx`
- 加载状态：`loading.tsx`
- 错误处理：`error.tsx`
- 路由组：使用括号 `(groupName)`

## 命令说明

```bash
# 开发
npm run dev          # 启动开发服务器

# 构建
npm run build        # 构建生产版本
npm start           # 启动生产服务器

# 代码质量
npm run lint        # 运行 ESLint
npm run type-check  # TypeScript 类型检查
npm run format      # 格式化代码
```

## Docker 部署

```bash
# 构建镜像
docker build -t shadow-agents-web:latest .

# 运行容器
docker run -d \
  --name shadow-agents-web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api:5000 \
  shadow-agents-web:latest
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 性能优化

- 使用 Next.js 图片优化
- 实现代码分割和懒加载
- 使用 SWR 缓存策略
- 启用 React Server Components

## 许可证

MIT License
