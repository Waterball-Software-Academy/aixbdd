# MSW Store Persistence across Navigation

## Problem

MSW handlers run in the **browser window context** (not in the Service Worker process).
Each `page.goto()` in Playwright creates a **new page lifecycle**:

1. New HTML is fetched → React re-hydrates → `MSWProvider` re-runs `initMocks()` → a fresh
   `setupWorker(…handlers)` instance is created.
2. Any **in-memory** state (arrays/objects at module scope inside `handlers/`) is **reset**,
   because the module is re-evaluated after the new page's JavaScript bundle loads.

This breaks scenarios like:
- Register a user on `/register` → navigate to `/login` → the registered user is gone.
- Create a session on `/sessions` → navigate away → return → session list is empty.

## Solution: sessionStorage-backed store

Persist the store to `window.sessionStorage` under a single key (e.g. `__msw_store__`).
On every handler call, call `store.reload()` first (reads from sessionStorage) and
`store.save()` last (writes back).

```ts
// mocks/handlers/store.ts  (condensed pattern)

const STORAGE_KEY = '__msw_store__'

function load(): StoreData {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as StoreData) : emptyStore()
  } catch { return emptyStore() }
}

function save(data: StoreData) {
  try { window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data)) } catch { /* noop */ }
}

function makeStore() {
  let data = load()
  return {
    reload() { data = load() },
    // …methods: call reload() first, save() last
    createUser(email: string, password: string) {
      this.reload()
      const user = { id: crypto.randomUUID(), email, password }
      data.users.push(user)
      save(data)
      return user
    },
    findUser(email: string) {
      this.reload()
      return data.users.find(u => u.email === email)
    },
  }
}

export const store = makeStore()
```

## Critical: do NOT call sessionStorage.clear() in E2E steps

`sessionStorage.clear()` wipes **all** keys including `__msw_store__`.
To simulate logout, only remove auth keys:

```ts
// ✅ Correct
await page.evaluate(() => {
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
})

// ❌ Wrong — destroys MSW store
await page.evaluate(() => sessionStorage.clear())
```

## When to use sessionStorage vs. cookie-based auth tokens

| Token location | Works with sessionStorage store? | Notes |
|----------------|----------------------------------|-------|
| `sessionStorage` (access/refresh tokens) | ✅ Yes | Must also use `sessionStorage` in API client for auth header |
| Cookie (`auth-token`) | ✅ Yes | Starter default; survives page reload within same tab |

## API client: auto-attach Authorization header

If tokens are stored in `sessionStorage` (not cookies), update `client.ts`:

```ts
// lib/api/client.ts — auto-attach from sessionStorage
const token = typeof window !== 'undefined'
  ? sessionStorage.getItem('access_token')
  : null
if (token) headers['Authorization'] = `Bearer ${token}`
```

The starter default uses **cookies** (`auth-token` cookie) which is read automatically by
`apiClient` in `src__lib__api__client.ts`. Choose **one** approach per project and be consistent.
