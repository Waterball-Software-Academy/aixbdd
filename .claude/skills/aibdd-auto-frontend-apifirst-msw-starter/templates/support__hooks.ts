import { After, Before, setDefaultTimeout, setWorldConstructor } from '@cucumber/cucumber'
import { chromium } from '@playwright/test'
import { AppWorld } from './world'

setWorldConstructor(AppWorld)
setDefaultTimeout(60000)

Before(async function (this: AppWorld) {
  this.browser = await chromium.launch({ headless: true })
  this.context = await this.browser.newContext({
    baseURL: process.env.BASE_URL ?? 'http://localhost:3001',
  })
  this.page = await this.context.newPage()
})

After(async function (this: AppWorld) {
  await this.browser?.close()
})
