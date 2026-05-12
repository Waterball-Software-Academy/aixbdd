# Triple-Anchor Rule

每一條 task **必須**同時握住三條 SSOT 的對應錨點，這樣下游 worker（人或 agent）讀任一條 task 就能不用回頭翻原檔，直接知道「這條 task 為什麼存在、要對到 backend 哪一塊、要長成 Pencil 上的哪一張畫面」。

## 三錨定義

| 錨 | 名稱 | 內容必填欄位 |
|---|---|---|
| **左錨** | 下游 skill 實作要素 | `skill: /aibdd-auto-frontend-msw-api-layer` 或 `/aibdd-auto-frontend-nextjs-pages` + `element: <要素名稱>`（例：`zod-schema` / `msw-handler` / `api-client-fn` / `page-component` / `form-binding` / `route-shell` …） |
| **中錨** | 後端契約／feature 樣本 | `feature_file: <feature 檔名（含路徑）>` + `operation_id: <OpenAPI operation_id>` + `method` + `path`（任一可為 null，但**至少有一項非 null**） |
| **右錨** | Pencil 設計檔 frame | `frame_name: <e.g. "01 Lobby">` + `node_id: <pen node id>` + `preview_png: <PNG 路徑>` |

## 必填規則

| Phase | 左錨 | 中錨 | 右錨 |
|---|---|---|---|
| Phase 1（MSW Layer：zod / fixtures / handlers / api-client） | ✅ 必填 | ✅ 必填 | ⛔ 不需要 |
| Phase 2（Pages：design-token / page-impl） | ✅ 必填 | ✅ 必填（design-token 例外，可空） | ✅ 必填 |
| Phase 3（Visual Parity Gate） | ✅ 必填 | ⛔ 不需要 | ✅ 必填（指向「全 frame 集合」） |

## Exception 清單

允許略過部分錨點的 task 類型（在 task 內必須明寫 `[anchor-exception: <reason>]`）：

1. **design-token-binding**：屬於全局 task，不對應特定 endpoint 也不對應單一 frame；中右錨可空，但要寫 `[anchor-exception: global token binding]`
2. **infra-only task**（例：route shell / layout wrapper）：可只有左錨；要寫 `[anchor-exception: infra-only, no business mapping]`
3. **visual-parity-gate**：指向全 frame 集合；右錨寫 `frame_name: ALL` + `preview_png: ${UIUX_PREVIEW_DIR}/*.png`

**沒有 exception 標註且缺錨**的 task = invalid。SOP Phase 2 step 8 會 ASSERT。

## frame → React component 對映

從 `.pen` 檔內的 reusable component name（例：`comp/btn-primary`、`comp/digit-cell`、`comp/boss-card`）推 React component name 的轉換規則：

| .pen reusable name | React 對應 |
|---|---|
| `comp/btn-primary` | `<PrimaryButton>` |
| `comp/btn-cta` | `<CTAButton>` |
| `comp/btn-ghost` | `<GhostButton>` |
| `comp/btn-ready` | `<ReadyButton>` |
| `comp/digit-cell` / `comp/digit-cell-empty` / `comp/digit-cell-hidden` | `<DigitCell variant="filled\|empty\|hidden" />` |
| `comp/hp-bar-player` | `<PlayerHpBar />` |
| `comp/hp-bar-boss` | `<BossHpBar />` |
| `comp/numpad-key` / `comp/numpad-key-accent` | `<NumpadKey accent? />` |
| `comp/pip-A` / `comp/pip-B` | `<ResultPip kind="A\|B" />` |
| `comp/pill-ready` / `comp/pill-wait` / `comp/pill-turn` / `comp/pill-ko` / `comp/pill-spectate` | `<StatusPill variant="..." />` |
| `comp/player-card` | `<PlayerCard />` |
| `comp/boss-card` | `<BossCard />` |
| `comp/top-bar` | `<AppTopBar />` |
| `comp/phase-banner` | `<PhaseBanner />` |
| `comp/log-feed` | `<CombatLog />` |
| `comp/dmg-pop` / `comp/crit-pop` / `comp/heal-pop` | `<FloatingNumber kind="dmg\|crit\|heal" />` |

未列在表上的 reusable name → SYNTHESIZE 階段以 PascalCase 轉換並標 `(component name TBD by impl)`。

## endpoint → MSW 模組對映

依 OpenAPI path 第一段 resource 名稱分模組：

| Path 起頭 | MSW handler 模組 | api-client 模組 |
|---|---|---|
| `/room-codes/*`、`/rooms/*` | `mocks/handlers/rooms.ts` | `lib/api/rooms.ts` |
| `/rooms/*/games/*` | `mocks/handlers/games.ts` | `lib/api/games.ts` |
| `/rooms/*/guesses` | `mocks/handlers/guesses.ts` | `lib/api/guesses.ts` |
| 其他 | `mocks/handlers/<resource-token>.ts` | `lib/api/<resource-token>.ts` |
