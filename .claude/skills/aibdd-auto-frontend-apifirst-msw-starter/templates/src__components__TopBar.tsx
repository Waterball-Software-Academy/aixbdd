'use client'

import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { AppearanceToolbar } from '@/components/AppearanceToolbar'
import { UserMenu } from '@/components/UserMenu'

function getBreadcrumb(pathname: string | null, tNav: (key: string) => string): string {
  if (!pathname || pathname === '/') return 'Workspace'
  const segment = pathname.split('/').filter(Boolean)[0]
  if (segment === 'protected') {
    const nextSegment = pathname.split('/').filter(Boolean)[1]
    return nextSegment ? tNav(nextSegment) : 'Workspace'
  }
  return segment ? tNav(segment) : 'Workspace'
}

export function TopBar() {
  const pathname = usePathname()
  const t = useTranslations('nav')
  const currentBreadcrumb = getBreadcrumb(pathname, t)

  return (
    <header data-testid="topbar" className="sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between gap-3 border-b border-border/80 bg-background/85 px-4 backdrop-blur-xl sm:px-6 md:px-8">
      <div className="flex min-w-0 flex-1 items-center">
        <h1 className="truncate text-sm font-semibold tracking-tight text-foreground">{currentBreadcrumb}</h1>
      </div>
      <div className="flex shrink-0 items-center gap-2.5 sm:gap-3">
        <AppearanceToolbar />
        <span className="hidden h-6 w-px shrink-0 bg-border/70 sm:block" />
        <UserMenu />
      </div>
    </header>
  )
}
