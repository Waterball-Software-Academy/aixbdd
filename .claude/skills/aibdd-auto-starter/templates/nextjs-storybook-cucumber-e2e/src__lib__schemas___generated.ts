// AI-derived from ${CONTRACTS_DIR}/api.yml during pre-red §3.2.
//
// The worker (Claude) reads every `components.schemas.<X>` in the FE-mirrored
// api.yml and writes one `export const <X> = z.object({...})` entry here.
// Translation rules (worker MUST follow):
//   - `required` array members → non-optional fields
//   - non-required fields → `.optional()`
//   - `nullable: true` → `.nullable()` (composed with `.optional()` if both)
//   - `enum` → `z.enum([...])`
//   - `oneOf` / `anyOf` → `z.union([...])`
//   - `$ref` → import-then-reuse (no inlining unless trivially small)
//
// DO NOT hand-edit individual exports for cosmetic reasons. To refresh after
// `api.yml` changes: re-run pre-red §3.2 (AI re-reads the spec and
// regenerates this file). Drift is gated by §3.0 source-hash check.
//
// `operation-registry.ts` imports the Zod exports declared here.
export {};
