import { getTranslations } from 'next-intl/server'

/**
 * Default landing route after `/` redirect. Replace with real UI via `/aibdd-auto-frontend-nextjs-pages`.
 */
export default async function RecordsPlaceholderPage() {
  const t = await getTranslations('records')

  return (
    <div className="max-w-3xl">
      <h1
        className="text-[28px] font-semibold leading-tight tracking-tight text-foreground md:text-[34px]"
        data-testid="smoke-landing-heading"
      >
        {t('placeholderTitle')}
      </h1>
      <p className="mt-3 max-w-prose text-[17px] leading-relaxed text-muted-foreground">
        {t('placeholderHint')}
      </p>
    </div>
  )
}
