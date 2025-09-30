import Link from 'next/link'

/**
 * 首页
 */
export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <div className="text-center">
        <h1 className="mb-4 text-5xl font-bold text-gray-900 dark:text-white">
          Shadow Agents Platform
        </h1>
        <p className="mb-8 text-xl text-gray-600 dark:text-gray-400">
          强大的 AI 应用开发平台
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/apps"
            className="btn-primary"
          >
            开始使用
          </Link>
          <Link
            href="/login"
            className="btn-secondary"
          >
            登录
          </Link>
        </div>
      </div>
    </div>
  )
}
