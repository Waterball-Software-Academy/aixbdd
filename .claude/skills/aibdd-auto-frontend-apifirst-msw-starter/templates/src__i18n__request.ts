import { cookies, headers } from 'next/headers'
import { getRequestConfig } from 'next-intl/server'
import { LOCALE_COOKIE, resolveLocale } from './locale-negotiation'

export default getRequestConfig(async () => {
  const cookieStore = await cookies()
  const cookieLocale = cookieStore.get(LOCALE_COOKIE)?.value
  const acceptLanguage = (await headers()).get('accept-language')
  const locale = resolveLocale(cookieLocale, acceptLanguage)

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  }
})
