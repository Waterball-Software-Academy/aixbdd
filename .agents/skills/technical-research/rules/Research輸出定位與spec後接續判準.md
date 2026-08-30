# Rule 1 - research 留在 plan package

- Level: `MUST`
- `/technical-research` 的 decision-driven 研究過程必須輸出到 `specs/plans/NNN-<slug>/research.md`。
- `research.md` 描述本次迭代如何做技術決策，可包含替代方案、採納理由與殘餘風險。

## Good Example

- 這個例子是好的，因為研究過程留在本次 plan。

```text
specs/plans/004-room-game-chat/research.md
```

## Bad Example

- 這個例子是壞的，因為把本次研究過程放進 truth。

```text
specs/truth/research.md
```

# Rule 2 - techstack 是 truth artifact

- Level: `MUST`
- `/technical-research` 必須把系統目前採用的技術堆疊輸出或更新到 `specs/truth/techstack.md`。
- `specs/truth/techstack.md` 必須是完整現況，不得只描述本次增量，也不得寫「其餘以 001/002 為準」。
- 完成後必須委派 `/truth-delta` 記錄 `/technical-research` 的 ADD / MODIFY / DELETE / NOOP。

## Good Example

- 這個例子是好的，因為 techstack truth 是全系統現況。

```text
specs/truth/techstack.md
```

## Bad Example

- 這個例子是壞的，因為每個 plan package 各自保存一份 techstack truth。

```text
specs/plans/004-room-game-chat/techstack.md
```
