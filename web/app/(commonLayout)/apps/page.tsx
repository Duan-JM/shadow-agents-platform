'use client'

import Link from 'next/link'

/**
 * 应用列表页面
 */
export default function AppsPage() {
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">我的应用</h1>
        <Link href="/apps/create" className="btn-primary">
          创建应用
        </Link>
      </div>
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* TODO: 应用列表 */}
        <div className="card">
          <h3 className="mb-2 text-lg font-semibold">示例应用</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            这是一个示例应用
          </p>
        </div>
      </div>
    </div>
  )
}
