import type { Page } from '@playwright/test'

interface StubOverride {
  method: string
  url: string
  body: unknown
  status: number
  delayMs?: number
}

/**
 * Stub an HTTP method for an MSW path (e.g. `/api/sessions`). Requires `browser.ts`
 * to read `window.__mswOverrides` before `worker.start()`.
 */
export async function stubApiMethod(
  page: Page,
  method: string,
  url: string,
  body: unknown,
  status = 200
): Promise<void> {
  await page.addInitScript((override: StubOverride) => {
    const w = window as unknown as { __mswOverrides?: StubOverride[] }
    w.__mswOverrides = w.__mswOverrides ?? []
    w.__mswOverrides.push(override)
  }, { method, url, body, status })
}

/**
 * Stub all HTTP methods for a path (MSW `http.all`).
 */
export async function stubApi(
  page: Page,
  url: string,
  body: unknown,
  status = 200
): Promise<void> {
  await stubApiMethod(page, 'ALL', url, body, status)
}

/**
 * Stub with delay (loading-state scenarios).
 */
export async function stubApiWithDelay(
  page: Page,
  url: string,
  body: unknown,
  delayMs: number,
  status = 200
): Promise<void> {
  await page.addInitScript((override: StubOverride) => {
    const w = window as unknown as { __mswOverrides?: StubOverride[] }
    w.__mswOverrides = w.__mswOverrides ?? []
    w.__mswOverrides.push(override)
  }, { method: 'ALL', url, body, status, delayMs })
}
