---
name: aibdd-core
description: 跨 skill 共用 reference hub。包含 spec package paths 等共用 reference。LOAD-only — 由其他 sibling skill 透過 `aibdd-core::FILENAME.md` 載入；禁止重抄內容至自身 references。SKIP when caller 試圖直接 invoke 本 skill 而非 LOAD reference 檔。
metadata:
  user-invocable: false
  skill-type: reference-hub
  source: project-level dogfooding
---

# aibdd-core

跨 skill 共用 reference hub — LOAD-only，不執行任何流程。Sibling skill 透過 `aibdd-core::FILENAME.md` 形式 LOAD references；禁止複製本檔內容至自身 references/。
