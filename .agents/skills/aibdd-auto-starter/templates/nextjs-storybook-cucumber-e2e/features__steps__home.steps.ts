import { expect } from '@playwright/test';
import { Given, When, Then } from './fixtures';

Given('I am on the home page', async ({ page }) => {
  await page.goto('/');
});

When(
  'I resize the viewport to {int} x {int}',
  async ({ page }, width: number, height: number) => {
    await page.setViewportSize({ width, height });
  },
);

Then('the page title should be {string}', async ({ page }, title: string) => {
  await expect(page).toHaveTitle(title);
});

Then('I should see the heading {string}', async ({ page }, text: string) => {
  await expect(page.getByRole('heading', { name: text })).toBeVisible();
});

Then('I should see the link {string}', async ({ page }, name: string) => {
  await expect(page.getByRole('link', { name })).toBeVisible();
});

Then('I should see the button {string}', async ({ page }, name: string) => {
  await expect(page.getByRole('button', { name })).toBeVisible();
});

Then('I should see the text {string}', async ({ page }, text: string) => {
  await expect(page.getByText(text, { exact: false }).first()).toBeVisible();
});

Then(
  'the link {string} should point to a URL containing {string}',
  async ({ page }, name: string, urlPart: string) => {
    const href = await page.getByRole('link', { name }).first().getAttribute('href');
    expect(href).not.toBeNull();
    expect(href as string).toContain(urlPart);
  },
);
