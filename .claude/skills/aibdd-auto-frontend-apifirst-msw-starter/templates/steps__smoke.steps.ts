import { Given, Then } from '@cucumber/cucumber'
import { expect } from '@playwright/test'
import type { AppWorld } from '../support/world'

Given('I open the app root', async function (this: AppWorld) {
  // Use gotoAndWaitMSW to ensure the MSW Service Worker is fully registered
  // before Playwright starts interacting with the page.
  await this.gotoAndWaitMSW('/')
})

Then('I see the default landing page', async function (this: AppWorld) {
  await expect(this.page).toHaveURL(/\/products(?:\/)?$/)
  await expect(this.page.getByTestId('smoke-landing-heading')).toBeVisible({ timeout: 30_000 })
})
