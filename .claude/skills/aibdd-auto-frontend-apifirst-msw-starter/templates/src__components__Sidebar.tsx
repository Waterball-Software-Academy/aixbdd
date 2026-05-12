'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'

/** Starter 預設單一占位路由；業務專案可改為多筆 nav。 */
const NAV = [{ href: '/products', key: 'products' as const, icon: PlaceholderIcon }]

function PlaceholderIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  )
}

type Props = {
  collapsed: boolean
  ready?: boolean
}

export function Sidebar({ collapsed, ready = true }: Props) {
  const pathname = usePathname()
  const t = useTranslations('nav')

  return (
    <aside
      data-testid="sidebar"
      className={`sticky top-0 self-start relative flex h-screen shrink-0 flex-col border-r border-border bg-sidebar ${
        ready ? 'transition-[width] duration-300 ease-out' : 'transition-none'
      } dark:border-white/[0.08] ${
        collapsed ? 'w-[72px]' : 'w-[260px]'
      }`}
    >
      <div className="flex h-full flex-col">
        <div className="flex h-14 shrink-0 items-center border-b border-border px-3 pr-7 dark:border-white/[0.08]">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-xs font-bold text-primary">
              EA
            </div>
            <span
              className={`truncate whitespace-nowrap text-sm font-semibold leading-none tracking-tight text-foreground ${
                ready ? 'transition-all duration-200 ease-out' : 'transition-none'
              } ${
                collapsed ? 'max-w-0 opacity-0' : 'max-w-[165px] opacity-100'
              }`}
            >
              {{PROJECT_NAME}}
            </span>
          </div>
        </div>

        <nav data-testid="sidebar-nav" className="flex flex-1 flex-col gap-1 overflow-y-auto p-3 pt-4">
          {NAV.map(({ href, key, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`)
            return (
              <Link
                key={href}
                data-testid={`nav-${key}`}
                href={href}
                title={t(key)}
                className={`group flex h-11 items-center gap-2 overflow-hidden rounded-xl pl-1.5 pr-2.5 transition ${
                  active
                    ? 'bg-primary/15 font-medium text-primary shadow-sm dark:bg-primary/20'
                    : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground dark:hover:bg-white/[0.06]'
                }`}
              >
                <span
                  className={`flex h-9 w-9 shrink-0 items-center justify-center ${
                    active ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
                  }`}
                >
                  <Icon />
                </span>
                <span
                  className={`whitespace-nowrap text-[15px] ${
                    ready ? 'transition-all duration-200 ease-out' : 'transition-none'
                  } ${
                    collapsed ? 'max-w-0 opacity-0' : 'max-w-[140px] opacity-100'
                  }`}
                >
                  {t(key)}
                </span>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}
