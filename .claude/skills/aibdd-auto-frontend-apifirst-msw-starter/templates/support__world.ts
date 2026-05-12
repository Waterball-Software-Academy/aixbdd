import { World, IWorldOptions } from '@cucumber/cucumber'
import type { Browser, BrowserContext, Page } from '@playwright/test'

export class AppWorld extends World {
  browser!: Browser
  context!: BrowserContext
  page!: Page
  baseUrl: string

  constructor(options: IWorldOptions) {
    super(options)
    this.baseUrl = process.env.BASE_URL ?? 'http://localhost:3001'
  }

  /**
   * Navigate to `path` and wait until MSWProvider signals that the Service
   * Worker is fully registered (`html[data-msw-ready="true"]`).
   *
   * Use this instead of `page.goto()` for every navigation that precedes an
   * API call, otherwise the request fires before the SW interceptor is active
   * and you get ERR_CONNECTION_REFUSED.
   *
   * Safe to call even when NEXT_PUBLIC_MOCK_API is not set: MSWProvider writes
   * the signal immediately in that case, so the wait resolves instantly.
   */
  async gotoAndWaitMSW(path: string): Promise<void> {
    await this.page.goto(`${this.baseUrl}${path}`)
    await this.page.waitForFunction(
      () => document.documentElement.dataset.mswReady === 'true',
      { timeout: 20_000 },
    )
  }
}
