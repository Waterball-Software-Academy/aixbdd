'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { Sidebar } from '@/components/Sidebar'
import { TopBar } from '@/components/TopBar'

/**
 * 受保護路由佈局樣板。
 * 支援功能：
 * 1. 側邊欄收合狀態持久化。
 * 2. 特定路由 (如 /settings) 的自動收合與去邊距 (No padding)。
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const isSettings = pathname?.startsWith('/settings')
  
  const [collapsed, setCollapsed] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('app-sidebar-collapsed')
    if (isSettings) {
      setCollapsed(true)
    } else {
      setCollapsed(saved === '1')
    }
    setReady(true)
  }, [isSettings])

  const onToggleSidebar = () => {
    setCollapsed((prev) => {
      const next = !prev
      localStorage.setItem('app-sidebar-collapsed', next ? '1' : '0')
      return next
    })
  }

  return (
    <div className="relative flex min-h-screen items-stretch bg-background">
      <Sidebar collapsed={collapsed} ready={ready} />
      <button
        type="button"
        onClick={onToggleSidebar}
        className="absolute top-3 z-30 inline-flex h-7 w-7 items-center justify-center rounded-full border border-border bg-background text-muted-foreground shadow-sm hover:bg-muted"
        style={{ left: collapsed ? 58 : 246 }}
      >
        <svg className={`h-3.5 w-3.5 transition-transform ${collapsed ? '' : 'rotate-180'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <TopBar />
        <main className={`flex-1 ${isSettings ? 'p-0' : 'px-4 py-4 sm:px-6 sm:py-6'}`}>
          {children}
        </main>
      </div>
    </div>
  )
}
