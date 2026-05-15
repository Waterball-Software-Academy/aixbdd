#!/usr/bin/env node
// Static schema-gate check for the playwright-bdd fixture.
//
// Asserts that every `route.fulfill(` call inside `features/steps/fixtures.ts`
// is preceded (within the same `page.route(...)` block) by either:
//   - `*.requestSchema.safeParse(` / `*.requestSchema.parse(`  (inbound gate), or
//   - `*.responseSchema.safeParse(` / `*.responseSchema.parse(` (outbound gate).
//
// Boundary invariant I2 — see aibdd-core::boundaries/web-frontend/handler-routing.yml.
//
// Exits 0 on pass, 1 on violation. Zero npm deps; pure Node ESM.

import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const FIXTURE_PATH = resolve(process.cwd(), "features/steps/fixtures.ts");

if (!existsSync(FIXTURE_PATH)) {
  console.error(`[schemas:check] fixtures.ts not found at ${FIXTURE_PATH}`);
  process.exit(1);
}

const src = readFileSync(FIXTURE_PATH, "utf8");

const routeBlocks = extractRouteBlocks(src);
if (routeBlocks.length === 0) {
  // Walking-skeleton state — no page.route registered yet. Pass.
  console.log("[schemas:check] no page.route() blocks found; skipping (walking skeleton).");
  process.exit(0);
}

const violations = [];

for (const block of routeBlocks) {
  const fulfillIdx = block.body.indexOf("route.fulfill(");
  if (fulfillIdx < 0) {
    violations.push(
      `page.route block starting at line ${block.startLine}: missing \`route.fulfill(\``,
    );
    continue;
  }

  const hasRequestGate =
    /\b\w*[Rr]equestSchema\.(safeParse|parse)\s*\(/.test(block.body) ||
    /\bop\.requestSchema\.(safeParse|parse)\s*\(/.test(block.body);
  const hasResponseGate =
    /\b\w*[Rr]esponseSchema\.(safeParse|parse)\s*\(/.test(block.body) ||
    /\bop\.responseSchema\.(safeParse|parse)\s*\(/.test(block.body);

  if (!hasRequestGate && !hasResponseGate) {
    violations.push(
      `page.route block starting at line ${block.startLine}: \`route.fulfill\` reached without any request/response schema parse (I2 violation).`,
    );
  }
}

if (violations.length > 0) {
  console.error("[schemas:check] I2 schema-gate violations:");
  for (const v of violations) console.error(`  - ${v}`);
  process.exit(1);
}

console.log(`[schemas:check] OK — ${routeBlocks.length} page.route block(s) guarded.`);
process.exit(0);

/**
 * Extract `await page.route(...)` blocks. Returns an array of
 * `{ startLine: number, body: string }`. Block body is the source between the
 * arrow-function `{` and its matching `}`.
 */
function extractRouteBlocks(source) {
  const blocks = [];
  const pattern = /page\.route\s*\(/g;
  let m;
  while ((m = pattern.exec(source)) !== null) {
    const openParen = source.indexOf("(", m.index + "page.route".length);
    const openBrace = findArrowBodyStart(source, openParen);
    if (openBrace < 0) continue;
    const closeBrace = matchBrace(source, openBrace);
    if (closeBrace < 0) continue;
    blocks.push({
      startLine: lineNumber(source, m.index),
      body: source.slice(openBrace + 1, closeBrace),
    });
  }
  return blocks;
}

function findArrowBodyStart(source, openParen) {
  const arrowIdx = source.indexOf("=>", openParen);
  if (arrowIdx < 0) return -1;
  for (let i = arrowIdx + 2; i < source.length; i += 1) {
    const ch = source[i];
    if (ch === "{") return i;
    if (ch === "(" || ch === "[" || ch === '"' || ch === "'") return -1;
  }
  return -1;
}

function matchBrace(source, openBrace) {
  let depth = 0;
  for (let i = openBrace; i < source.length; i += 1) {
    const ch = source[i];
    if (ch === '"' || ch === "'" || ch === "`") {
      i = skipString(source, i, ch);
      continue;
    }
    if (ch === "/" && source[i + 1] === "/") {
      i = source.indexOf("\n", i);
      if (i < 0) return -1;
      continue;
    }
    if (ch === "/" && source[i + 1] === "*") {
      i = source.indexOf("*/", i + 2);
      if (i < 0) return -1;
      i += 1;
      continue;
    }
    if (ch === "{") depth += 1;
    else if (ch === "}") {
      depth -= 1;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function skipString(source, start, quote) {
  for (let i = start + 1; i < source.length; i += 1) {
    if (source[i] === "\\") {
      i += 1;
      continue;
    }
    if (source[i] === quote) return i;
    if (quote === "`" && source[i] === "$" && source[i + 1] === "{") {
      const end = matchBrace(source, i + 1);
      if (end < 0) return source.length - 1;
      i = end;
    }
  }
  return source.length - 1;
}

function lineNumber(source, offset) {
  let line = 1;
  for (let i = 0; i < offset; i += 1) if (source[i] === "\n") line += 1;
  return line;
}
