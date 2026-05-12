/** 支援的語系（URL 不含 locale；由 Cookie + Accept-Language 決定） */
export const locales = ['zh-TW', 'en'] as const

export type AppLocale = (typeof locales)[number]

export const defaultLocale: AppLocale = 'zh-TW'

export function isLocale(value: string): value is AppLocale {
  return (locales as readonly string[]).includes(value)
}
