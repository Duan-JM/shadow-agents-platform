/**
 * 应用布局
 * 包含侧边栏导航的主布局
 */
import { Sidebar } from '@/components/base/sidebar'

export default function CommonLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
