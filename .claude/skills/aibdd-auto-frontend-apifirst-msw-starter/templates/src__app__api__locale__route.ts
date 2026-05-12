import { NextResponse } from 'next/server'
import { isLocale } from '@/i18n/routing'
import { LOCALE_COOKIE } from '@/i18n/locale-negotiation'

type Body = {
  locale?: string
}

/**
 * 使用者手動切換語系：寫入 Cookie 後由 next-intl getRequestConfig 讀取。
 * URL 路徑不變。
 */
export async function POST(request: Request) {
  let body: Body
  try {
    body = (await request.json()) as Body
  } catch {
    return NextResponse.json({ error: 'invalid json' }, { status: 400 })
  }

  const locale = typeof body.locale === 'string' ? body.locale : ''
  if (!isLocale(locale)) {
    return NextResponse.json({ error: 'invalid locale' }, { status: 400 })
  }

  const res = NextResponse.json({ ok: true })
  res.cookies.set(LOCALE_COOKIE, locale, {
    path: '/',
    maxAge: 60 * 60 * 24 * 365,
    sameSite: 'lax',
  })
  return res
}
