'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslations } from 'next-intl'

function hasAuthCookie(): boolean {
  if (typeof document === 'undefined') return false
  return /(?:^|;\s*)auth-token=/.test(document.cookie)
}

function avatarInitialsLatin(displayName: string): string {
  const s = displayName.trim()
  if (!s) return '?'
  const parts = s.split(/\s+/).filter(Boolean)
  if (parts.length >= 2 && /^[a-zA-Z]$/i.test(parts[0].charAt(0))) {
    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase()
  }
  return s.length <= 2 ? s.toUpperCase() : s.slice(0, 2).toUpperCase()
}

export function UserMenu() {
  const t = useTranslations('auth')
  const router = useRouter()
  const [granted, setGranted] = useState(false)
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement | null>(null)

  const displayName = granted ? t('userName') : t('guest')

  useEffect(() => {
    setGranted(hasAuthCookie())
  }, [])

  useEffect(() => {
    const onDocClick = (event: MouseEvent) => {
      if (!rootRef.current) return
      if (!rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const logout = useCallback(() => {
    document.cookie = 'auth-token=; path=/; max-age=0'
    setGranted(false)
    setOpen(false)
    router.replace('/login')
    router.refresh()
  }, [router])

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-2.5 rounded-lg border-0 bg-transparent py-2 pl-3 pr-2 text-left text-[13px] font-medium leading-none text-foreground transition hover:bg-muted/45 focus:outline-none"
      >
        <div className="h-6 w-6 rounded-full bg-primary/15 text-[10px] font-semibold flex items-center justify-center text-primary">
          {avatarInitialsLatin(displayName)}
        </div>
        <span className="min-w-0 flex-1 truncate">{displayName}</span>
      </button>

      {open && (
        <div className="absolute right-0 z-40 mt-1.5 min-w-[12rem] overflow-hidden rounded-xl border border-border/90 bg-background shadow-lg">
          {granted && (
            <div className="border-b border-border/70 px-3 py-2.5">
              <p className="truncate text-sm font-semibold text-foreground">{displayName}</p>
              <p className="mt-0.5 truncate text-xs text-muted-foreground">{t('memberRole')}</p>
            </div>
          )}

          {granted && (
            <Link
              href="/settings"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-[13px] text-foreground transition hover:bg-muted/80"
            >
              <svg className="h-4 w-4 opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              {t('settings')}
            </Link>
          )}

          {granted ? (
            <button
              type="button"
              onClick={logout}
              className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-[13px] text-foreground transition hover:bg-muted/80"
            >
              {t('logout')}
            </button>
          ) : (
            <Link href="/login" className="block px-3 py-3 text-center text-sm font-medium text-primary hover:bg-muted/50">
              {t('goLogin')}
            </Link>
          )}
        </div>
      )}
    </div>
  )
}
