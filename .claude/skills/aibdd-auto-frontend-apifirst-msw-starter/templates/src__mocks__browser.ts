import { setupWorker } from 'msw/browser'
import { http, HttpResponse } from 'msw'
import type { JsonBodyType } from 'msw'
import { handlers } from './handlers'

const worker = setupWorker(...handlers)

function getHttpMethod(method: string) {
  switch (method) {
    case 'GET': return http.get
    case 'POST': return http.post
    case 'PUT': return http.put
    case 'DELETE': return http.delete
    default: return http.all
  }
}

export async function initMocks() {
  await worker.start({ onUnhandledRequest: 'bypass' })

  // 測試模式：讀取 Playwright addInitScript 注入的 override
  const overrides = (window as any).__mswOverrides as Array<{
    method: string
    url: string
    body: unknown
    status: number
    delayMs?: number
  }> | undefined

  if (overrides?.length) {
    worker.use(
      ...overrides.map((o) =>
        getHttpMethod(o.method)(o.url, async () => {
          if (o.delayMs) await new Promise((r) => setTimeout(r, o.delayMs))
          return HttpResponse.json(o.body as JsonBodyType, { status: o.status })
        })
      )
    )
  }
}

export { worker }
