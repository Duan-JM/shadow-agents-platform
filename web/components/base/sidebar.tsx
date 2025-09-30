'use client'

import { Cog6ToothIcon, FolderIcon, HomeIcon, RectangleStackIcon, Square3Stack3DIcon } from '@heroicons/react/24/outline'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

/**
 * 侧边栏导航组件
 */
export function Sidebar() {
  const pathname = usePathname()

  const navigation = [
    { name: '首页', href: '/', icon: HomeIcon },
    { name: '应用', href: '/apps', icon: RectangleStackIcon },
    { name: '工作流', href: '/workflows', icon: Square3Stack3DIcon },
    { name: '知识库', href: '/datasets', icon: FolderIcon },
    { name: '设置', href: '/workspaces', icon: Cog6ToothIcon },
  ]

  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-800">
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
          Shadow Agents
        </h1>
      </div>
      
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
      
      <div className="border-t border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-gray-300"></div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900 dark:text-white">用户名</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">user@example.com</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
