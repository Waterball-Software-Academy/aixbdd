'use client'

import { useEffect, useState } from 'react'

/**
 * MSWProvider — blocks React subtree until MSW Service Worker is fully registered.
 *
 * ## Why blocking render?
 * MSW's Service Worker registers asynchronously. If we render children before `worker.start()`
 * resolves, any API call made during initial hydration (e.g. in a useEffect on the first page)
 * bypasses the interceptor and hits a real backend — which does not exist in dev/test.
 *
 * ## SSR / production build safety
 * `process.env.NEXT_PUBLIC_MOCK_API` is evaluated at **build time**, so in production
 * (where MOCK_API is not 'true') we initialise `ready = true` immediately via useState,
 * making the component a transparent wrapper — no flicker, no hydration mismatch.
 *
 * ## Cross-navigation persistence
 * After `worker.start()` completes we write `document.documentElement.dataset.mswReady = 'true'`
 * so that Playwright / Cucumber steps can use `waitForFunction(() =>
 * document.documentElement.dataset.mswReady === 'true')` as a reliable gate before interacting.
 *
 * ## Common pitfall: sessionStorage.clear()
 * If your E2E steps call `sessionStorage.clear()` to simulate logout, this will also wipe any
 * persisted MSW store keys (e.g. `__msw_store__`). Clear only auth-specific keys instead:
 *   sessionStorage.removeItem('access_token')
 *   sessionStorage.removeItem('refresh_token')
 */
export function MSWProvider({ children }: { children: React.ReactNode }) {
  const shouldMock = process.env.NEXT_PUBLIC_MOCK_API === 'true'

  // Production/SSR: shouldMock is false → ready starts true → children always render.
  // Development with mocks: shouldMock is true → ready starts false → render blocked until SW ready.
  const [ready, setReady] = useState(!shouldMock)

  useEffect(() => {
    if (!shouldMock) {
      document.documentElement.dataset.mswReady = 'true'
      return
    }
    import('@/mocks/browser')
      .then(({ initMocks }) => initMocks())
      .catch(() => {})
      .finally(() => {
        document.documentElement.dataset.mswReady = 'true'
        setReady(true)
      })
  }, [shouldMock])

  if (!ready) {
    // Render nothing (no hydration mismatch because shouldMock is a build-time constant).
    // suppressHydrationWarning prevents React from warning about the missing children on server.
    return <div data-msw-provider="loading" suppressHydrationWarning />
  }

  return <div data-msw-provider="ready">{children}</div>
}
