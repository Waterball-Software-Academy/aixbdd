import { defaultLocale, isLocale, type AppLocale } from './routing'

/** 與 middleware / Route Handler / getRequestConfig 共用 */
export const LOCALE_COOKIE = 'NEXT_LOCALE'

/**
 * 依 RFC 7231 Accept-Language 與專案支援清單挑選語系（預設：系統／瀏覽器偏好）。
 */
export function pickLocaleFromAcceptLanguage(acceptLanguage: string | null): AppLocale {
  if (!acceptLanguage) return defaultLocale
  const parts = acceptLanguage.split(',').map((p) => p.trim().split(';')[0]?.toLowerCase() ?? '')
  for (const tag of parts) {
    if (tag.startsWith('zh')) return 'zh-TW'
    if (tag.startsWith('en')) return 'en'
  }
  return defaultLocale
}

export function resolveLocale(
  cookieValue: string | undefined,
  acceptLanguage: string | null
): AppLocale {
  if (cookieValue && isLocale(cookieValue)) return cookieValue
  return pickLocaleFromAcceptLanguage(acceptLanguage)
}
