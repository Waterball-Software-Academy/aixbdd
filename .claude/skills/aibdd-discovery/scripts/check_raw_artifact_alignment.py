#!/usr/bin/env python3
"""
check_raw_artifact_alignment.py — Class 3 失讀 sweep（CQ2 P5）

按 Phase 4 4.A script 5 schedule 執行；對 raw idea ↔ activity / feature artifacts
做 substring sweep，偵測 raw 中**重複出現 ≥ 2 次**的 demo anchor 是否在 artifact
中遺漏。

Class 3 = raw 明寫但 AI 失讀（不是腦補；是讀取錯誤）。例：
  - 大額訂單 100 萬 demo raw 重複寫「倉管組長／物流課長／營運經理／電商處主管」4 層，
    activity 卻只列 3 層（漏營運經理）。

設計選擇：
  - Demo anchor extraction 用 Chinese maximal-run（separator 切完整 token），
    避免 sliding-window 帶出大量 substring 偽陽性。
  - 額外抓兩種強訊號：數字+量詞（100 萬 / 5 層），以及 Latin 識別碼（TITLE_009）。
  - Stopwords 過濾常見功能詞（這個、可以、需要、…），避免 raw 中文敘述句被當成
    demo anchor。
  - 比對方向僅 raw → artifact（單向）。Artifact → raw 那一向屬 Pattern 2
    inference-without-source（已由 Seam A/B 處理），不在本 script scope。
  - 永遠 ok=true（non-blocking sweep）；缺漏以 GAP 形式併入 Phase 4 verdict。

Output: stdout JSON
  {
    "ok": true,                         # 永遠 true
    "summary": {
      "files_scanned": int,
      "anchors_extracted": int,
      "gaps": int
    },
    "gaps": [
      {"rule_id": "RAW_ARTIFACT_ALIGNMENT_MISS",
       "file": "<plan_spec_path>",
       "line": 0,
       "msg": "raw 重複 demo「<token>」在 features/activities artifacts 中未找到對應 substring"},
      ...
    ],
    "violations": []                    # 空，因為 sweep 不產 violation
  }

Usage:
  python check_raw_artifact_alignment.py <AIBDD_ARGUMENTS_PATH> \\
      [--features-dir ABS_PATH] [--activities-dir ABS_PATH] [--plan-spec ABS_PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from kickoff_path_resolve import load_resolved_kickoff_state, resolve_kickoff_paths

CHINESE_RUN = re.compile(r"[一-鿿]+")
NUMERIC_UNIT = re.compile(r"\d+(?:\.\d+)?\s*[一-鿿]{1,3}")
LATIN_ID = re.compile(r"\b[A-Za-z][A-Za-z0-9_]{2,}\b")

# Trailing Chinese chars on NUMERIC_UNIT that indicate range connective, not unit
RANGE_TAILS = frozenset({"到", "至", "跟", "與", "和", "或"})

# Latin stopwords (lower-case English filler we don't treat as demo anchors)
LATIN_STOPWORDS = frozenset({
    "and", "the", "for", "with", "from", "into", "have", "has", "had",
    "are", "was", "were", "but", "not", "you", "your", "this", "that",
    "they", "them", "will", "would", "should", "could", "can", "may",
    "all", "any", "one", "two", "out", "off", "more", "most", "less",
    "than", "then", "there", "when", "where", "what", "which", "who",
    "how", "why", "yes", "use", "used", "uses", "using", "set",
})

STOPWORDS = frozenset({
    "我們", "你們", "他們", "這個", "那個", "這些", "那些", "這樣", "那樣", "這種", "那種",
    "可以", "就是", "所以", "因為", "但是", "或者", "然後", "現在", "已經", "以前", "以後",
    "不能", "不會", "不是", "沒有", "還有", "還是", "可能", "應該", "需要", "必須",
    "如果", "因此", "最後", "最先", "目前", "非常", "常常", "通常", "其實", "另外", "另一",
    "什麼", "怎麼", "為什麼", "其他", "東西", "事情", "部分",
    "出現", "發生", "過程", "結果", "內容", "狀態", "方式", "進行", "完成", "開始", "結束",
    "意思", "希望", "感覺", "覺得", "想要", "知道", "看到", "聽到", "說過", "提到",
    "問題", "錯誤", "正確",
    "這裡", "那裡", "這邊", "那邊", "這時", "那時", "這次", "那次",
    "比較", "比如", "例如", "舉例", "就會", "就是說", "其中",
    "我想", "我要", "我說", "我們", "你說",
})

FEATURE_GLOBS = ("*.feature",)
ACTIVITY_GLOBS = ("*.activity", "*.mmd")


def extract_raw_idea(spec_text: str) -> str:
    """Extract '## Raw idea' section content; fallback to whole file when absent."""
    out: list[str] = []
    in_raw = False
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            head = stripped.lstrip("# ").lower()
            if head.startswith("raw"):
                in_raw = True
                continue
            if in_raw:
                break
        if in_raw:
            out.append(line)
    return "\n".join(out) if out else spec_text


def extract_demo_anchors(text: str) -> set[str]:
    """Return tokens appearing >= 2 times, length >= 2, post stopword filter."""
    counts: Counter[str] = Counter()

    for m in NUMERIC_UNIT.finditer(text):
        token = re.sub(r"\s+", "", m.group())
        if len(token) < 2:
            continue
        # Drop trailing range connectives ("100到" → "100") so we don't dilute
        # signal with half-formed range expressions; the surrounding numeric+unit
        # forms (e.g. "100萬", "500萬") are already captured separately.
        while token and token[-1] in RANGE_TAILS:
            token = token[:-1]
        if len(token) < 2:
            continue
        if token[-1].isdigit():
            continue  # bare number after stripping range tail; not a demo anchor
        counts[token] += 1

    for m in LATIN_ID.finditer(text):
        token = m.group()
        if token.lower() in LATIN_STOPWORDS:
            continue
        counts[token] += 1

    for run in CHINESE_RUN.findall(text):
        if len(run) >= 2 and run not in STOPWORDS:
            counts[run] += 1

    return {t for t, c in counts.items() if c >= 2}


def collect_artifact_text(
    features_dir: Path | None,
    activities_dir: Path | None,
) -> tuple[str, list[Path]]:
    """Concatenate all .feature + .activity text; return (text, scanned files)."""
    chunks: list[str] = []
    files: list[Path] = []
    targets: list[tuple[Path, tuple[str, ...]]] = []
    if features_dir is not None and features_dir.exists():
        targets.append((features_dir, FEATURE_GLOBS))
    if activities_dir is not None and activities_dir.exists():
        targets.append((activities_dir, ACTIVITY_GLOBS))
    for directory, globs in targets:
        for pattern in globs:
            for f in directory.rglob(pattern):
                try:
                    chunks.append(f.read_text(encoding="utf-8"))
                    files.append(f)
                except (OSError, UnicodeDecodeError):
                    continue
    return "\n".join(chunks), files


def find_missing(anchors: set[str], artifact_text: str) -> list[str]:
    """Return anchors absent from artifact_text via substring check."""
    return sorted(t for t in anchors if t not in artifact_text)


def emit(payload: dict) -> int:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
    parser.add_argument("--features-dir", default=None,
                        help="Override resolved FEATURE_SPECS_DIR (absolute)")
    parser.add_argument("--activities-dir", default=None,
                        help="Override resolved ACTIVITIES_DIR (absolute)")
    parser.add_argument("--plan-spec", default=None,
                        help="Override resolved PLAN_SPEC (absolute)")
    args = parser.parse_args()

    args_path = Path(args.arguments_path)

    try:
        workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)
    except Exception as exc:
        return emit({
            "ok": True,
            "summary": {"files_scanned": 0, "anchors_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"kickoff state load failed (kickoff-safe pass): {exc}",
        })

    if args.plan_spec:
        plan_spec = Path(args.plan_spec).resolve()
    else:
        rel = resolved.get("PLAN_SPEC")
        if not rel:
            return emit({
                "ok": True,
                "summary": {"files_scanned": 0, "anchors_extracted": 0, "gaps": 0},
                "gaps": [],
                "violations": [],
                "note": "PLAN_SPEC not bound; skip alignment sweep.",
            })
        plan_spec = (workspace_root / str(rel).replace("\\", "/")).resolve()

    if not plan_spec.exists():
        return emit({
            "ok": True,
            "summary": {"files_scanned": 0, "anchors_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"PLAN_SPEC not found: {plan_spec} (greenfield = pass)",
        })

    if args.features_dir or args.activities_dir:
        features_dir = Path(args.features_dir).resolve() if args.features_dir else None
        activities_dir = Path(args.activities_dir).resolve() if args.activities_dir else None
    else:
        try:
            features_dir, activities_dir, _ = resolve_kickoff_paths(args_path)
        except Exception:
            features_dir = activities_dir = None

    try:
        spec_text = plan_spec.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return emit({
            "ok": True,
            "summary": {"files_scanned": 0, "anchors_extracted": 0, "gaps": 0},
            "gaps": [],
            "violations": [],
            "note": f"cannot read PLAN_SPEC: {exc}",
        })

    raw_idea = extract_raw_idea(spec_text)
    anchors = extract_demo_anchors(raw_idea)

    artifact_text, scanned_files = collect_artifact_text(features_dir, activities_dir)

    if not scanned_files:
        return emit({
            "ok": True,
            "summary": {
                "files_scanned": 0,
                "anchors_extracted": len(anchors),
                "gaps": 0,
            },
            "gaps": [],
            "violations": [],
            "note": "no .feature / .activity files found; skip sweep (kickoff-safe).",
        })

    missing = find_missing(anchors, artifact_text)
    gaps = [
        {
            "rule_id": "RAW_ARTIFACT_ALIGNMENT_MISS",
            "file": str(plan_spec),
            "line": 0,
            "msg": (
                f"raw 重複 demo「{token}」在 features/activities artifacts 中"
                f"未找到對應 substring"
            ),
        }
        for token in missing
    ]

    return emit({
        "ok": True,
        "summary": {
            "files_scanned": len(scanned_files),
            "anchors_extracted": len(anchors),
            "gaps": len(gaps),
        },
        "gaps": gaps,
        "violations": [],
    })


if __name__ == "__main__":
    sys.exit(main())
