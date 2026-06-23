---
name: aibdd-core
description: 跨 skill 共用資源庫，本身不會被執行，只存放供其他 skill 載入的共用資源（reference／asset／script）。
metadata:
  user-invocable: false
  skill-type: reference-hub
  source: project-level dogfooding
---

# aibdd-core

跨 skill 共用資源庫，不會被執行，只存放供其他 skill 載入的共用資源。其他 skill 以 `$skill::$relative-path-to-skill` 形式載入本庫的檔案，`::` 後的路徑相對於該 skill 根目錄。
