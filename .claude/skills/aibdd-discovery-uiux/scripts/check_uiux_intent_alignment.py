#!/usr/bin/env python3
"""check_uiux_intent_alignment.py — Phase 5 §5.A script #6.

Scan ``${PLAN_REPORTS_DIR}/discovery-uiux-intent.md`` (raw idea verbatim block)
for UX-mentioned tokens that fail to appear in either:

* feature / activity clean artifacts under ``FEATURE_SPECS_DIR`` /
  ``ACTIVITIES_DIR``;
* the GAP sections of ``discovery-uiux-sourcing.md`` /
  ``discovery-uiux-intent.md`` / ``discovery-uiux-be-gap.md``.

Each unmatched token is reported as a soft GAP — the script always returns
``ok=true`` so a failure here cannot block Phase 5, but it surfaces in the
verdict so reviewers can patch the alignment.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

REPO_DISCOVERY_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "aibdd-discovery" / "scripts"
)
if str(REPO_DISCOVERY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPO_DISCOVERY_SCRIPTS))

from kickoff_path_resolve import (  # noqa: E402 — sys.path patch above
    load_resolved_kickoff_state,
    resolve_kickoff_paths,
)

CHINESE_RUN = re.compile(r"[一-鿿]+")
LATIN_ID = re.compile(r"\b[A-Za-z][A-Za-z0-9_]{2,}\b")

UX_VOCAB = frozenset({
    "wizard", "stepper", "modal", "filter", "sort", "search",
    "dashboard", "tab", "wizard", "drawer", "popover",
    "嚮導", "篩選", "排序", "搜尋", "儀表板", "分頁", "彈窗", "側欄",
})

LATIN_STOPWORDS = frozenset({
    "and", "the", "for", "with", "from", "into", "have", "has", "had",
    "are", "was", "were", "but", "not", "you", "your", "this", "that",
    "they", "them", "will", "would", "should", "could", "can", "may",
    "all", "any", "one", "two", "out", "off", "more", "most", "less",
    "than", "then", "there", "when", "where", "what", "which", "who",
    "how", "why", "use", "used", "uses", "using", "set",
})

CHINESE_STOPWORDS = frozenset({
    "我們", "你們", "他們", "這個", "那個", "可以", "需要", "必須",
    "如果", "因此", "目前", "比如", "例如", "其他",
})

INTENT_REPORT = "discovery-uiux-intent.md"
SOURCING_REPORT = "discovery-uiux-sourcing.md"
BE_GAP_REPORT = "discovery-uiux-be-gap.md"


def extract_raw_block(intent_md_text: str) -> str:
    """Pull the raw-idea fenced block from the intent report.

    Convention from ``fe-intent-contract.md §5``: the report opens with a
    fenced quote (``>``) containing raw idea verbatim. We accept either
    Markdown blockquotes or fenced code blocks ``` (any language tag).
    """
    out: list[str] = []
    in_fence = False
    fence_marker: str | None = None
    for line in intent_md_text.splitlines():
        stripped = line.lstrip()
        if fence_marker is None and stripped.startswith("```"):
            in_fence = True
            fence_marker = stripped[:3]
            continue
        if in_fence and stripped.startswith(fence_marker or "```"):
            in_fence = False
            fence_marker = None
            continue
        if in_fence:
            out.append(line)
            continue
        if line.startswith(">"):
            out.append(line.lstrip("> ").rstrip())
    return "\n".join(out)


def tokenize(text: str) -> set[str]:
    counts: Counter[str] = Counter()
    for m in LATIN_ID.finditer(text):
        token = m.group()
        if token.lower() in LATIN_STOPWORDS:
            continue
        counts[token.lower()] += 1
    for run in CHINESE_RUN.findall(text):
        if len(run) >= 2 and run not in CHINESE_STOPWORDS:
            counts[run] += 1
    return {t for t in counts if t in UX_VOCAB or counts[t] >= 2}


def collect_corpus(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in {".feature", ".activity", ".md"}:
                    try:
                        chunks.append(f.read_text(encoding="utf-8"))
                    except (OSError, UnicodeDecodeError):
                        continue
        else:
            try:
                chunks.append(p.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
    return "\n".join(chunks)


def emit(payload: dict) -> int:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
    args = parser.parse_args()
    args_path = Path(args.arguments_path)

    try:
        workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)
    except Exception as exc:
        return emit({
            "ok": True,
            "summary": {"tokens_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"kickoff state load failed (kickoff-safe pass): {exc}",
        })

    plan_reports_rel = resolved.get("PLAN_REPORTS_DIR")
    if not plan_reports_rel:
        return emit({
            "ok": True,
            "summary": {"tokens_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": "PLAN_REPORTS_DIR not bound; skip intent alignment sweep.",
        })
    plan_reports_dir = (workspace_root / str(plan_reports_rel)).resolve()
    intent_path = plan_reports_dir / INTENT_REPORT
    if not intent_path.exists():
        return emit({
            "ok": True,
            "summary": {"tokens_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"intent report not yet present: {intent_path}",
        })

    try:
        intent_text = intent_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return emit({
            "ok": True,
            "summary": {"tokens_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"cannot read intent report: {exc}",
        })

    raw_block = extract_raw_block(intent_text)
    tokens = tokenize(raw_block)

    try:
        features_dir, activities_dir, _ = resolve_kickoff_paths(args_path)
    except Exception:
        features_dir = activities_dir = None

    corpus = collect_corpus([
        p for p in [
            features_dir,
            activities_dir,
            plan_reports_dir / SOURCING_REPORT,
            plan_reports_dir / BE_GAP_REPORT,
            intent_path,
        ] if p is not None
    ])
    corpus_lower = corpus.lower()

    missing = sorted(
        t for t in tokens
        if t not in corpus and t.lower() not in corpus_lower
    )

    gaps = [
        {
            "rule_id": "UIUX_INTENT_ALIGNMENT_MISS",
            "file": str(intent_path),
            "line": 0,
            "msg": (
                f"raw idea 提到「{token}」，但在 features / activities / "
                f"GAP reports 中找不到對應 substring；請補對應 frontend "
                f"artifact 或在 GAP section 顯式列出"
            ),
        }
        for token in missing
    ]

    return emit({
        "ok": True,
        "summary": {
            "tokens_extracted": len(tokens),
            "gaps": len(gaps),
        },
        "gaps": gaps,
        "violations": [],
    })


if __name__ == "__main__":
    sys.exit(main())
