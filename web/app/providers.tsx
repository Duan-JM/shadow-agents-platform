'use client'

import { fetcher } from '@/service/api/base'
import { ThemeProvider } from 'next-themes'
import { SWRConfig } from 'swr'

/**
 * 全局 Providers
 * 包含主题、数据获取等全局配置
 */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light">
      <SWRConfig
        value={{
          fetcher,
          revalidateOnFocus: false,
          shouldRetryOnError: false,
        }}
      >
        {children}
      </SWRConfig>
    </ThemeProvider>
  )
}
