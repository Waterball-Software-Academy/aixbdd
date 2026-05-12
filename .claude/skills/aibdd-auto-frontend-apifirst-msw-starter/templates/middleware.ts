import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import { isLocale } from './{{SRC_DIR}}/i18n/routing'
import { LOCALE_COOKIE, pickLocaleFromAcceptLanguage } from './{{SRC_DIR}}/i18n/locale-negotiation'

/**
 * 首次造訪無 Cookie 時：依 Accept-Language 寫入語系 Cookie（與 getRequestConfig 協商一致）。
 * 不使用 URL 分段切換語系。
 */
export function middleware(request: NextRequest) {
  const existing = request.cookies.get(LOCALE_COOKIE)?.value
  if (existing && isLocale(existing)) {
    return NextResponse.next()
  }

  const locale = pickLocaleFromAcceptLanguage(request.headers.get('accept-language'))
  const res = NextResponse.next()
  res.cookies.set(LOCALE_COOKIE, locale, {
    path: '/',
    maxAge: 60 * 60 * 24 * 365,
    sameSite: 'lax',
  })
  return res
}

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
}
