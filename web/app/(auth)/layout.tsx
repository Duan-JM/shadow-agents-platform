/**
 * 认证相关布局
 * 用于登录、注册、忘记密码等页面
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  )
}
