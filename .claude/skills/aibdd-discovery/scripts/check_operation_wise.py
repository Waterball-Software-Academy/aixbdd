#!/usr/bin/env python3
"""
check_operation_wise.py — Operation-wise feature file machine-only prefilter (kickoff boundary-aware)

This script does NOT perform full semantic adjudication of
`1 feature file = 1 operation`. That requirement remains the responsibility of
upstream operation partition + Phase 4.B semantic validation.

This script only enforces machine-only checks:
  - anti-pattern file name regex
  - operation header 首句模板
  - worker trigger declaration
  - filename convention 對齊 project bdd-constitution §5.1（若提供 --constitution）

掃描 **resolved** `${FEATURE_SPECS_DIR}/**/*.feature`（預設由 `arguments.yml` + `boundary.yml`
機械展開；見 `kickoff_path_resolve.py`），可由 `--features-dir` 覆寫。

Machine-only (本 script 負責):
  - OPERATION_FILENAME_ANTIPATTERN: 檔名含 anti-pattern token
    (主流程 / 流程 / 體驗 / 處理 / 重試 / 策略 / 邏輯 /
     experience / handling / management / retry / fallback / policy / logic / -flow)
  - OPERATION_HEADER_FIRST_SENTENCE_MISSING: Feature header 下方描述段為空
    或首句缺常見 trigger keyword
  - OPERATION_WORKER_TRIGGER_UNDECLARED: 若 feature header 首句含 worker 特徵
    卻未明指 trigger kind ∈ {scheduled-tick, consumed-message}
  - FILENAME_CONVENTION_VIOLATION: 檔名違反 project §5.1 declared
    `filename.convention` / `filename.title_language`（僅當提供 --constitution 時檢查）

Semantic-layer 判定由 Subagent 補（quality.md §Subagent checklist）；
因此本腳本通過只表示「沒有命中可機械判定的明顯問題」，不表示已證明
該 `.feature` 必然只承載單一 operation。

Usage:
  python check_operation_wise.py <AIBDD_ARGUMENTS_PATH> [--constitution PATH] [--features-dir ABS_PATH]

  --constitution PATH (optional): path to bdd-constitution.md. 若提供，會解析
  §5.1 取得 `filename.convention` / `filename.title_language` 兩個 axis 值，
  並逐檔做 schema 對齊檢查（Plugin 不對 axis 補預設值；未提供 flag 表示
  caller 自行決定是否走 schema 檢查）。

Output: stdout JSON (same shape as check_discovery_phase.py)
Exit: 0 if ok=true, 1 if ok=false.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from kickoff_path_resolve import resolve_kickoff_paths

FEATURE_RE = re.compile(r"^\s*Feature\s*:\s*(.+?)\s*$", re.IGNORECASE)
RULE_RE = re.compile(r"^\s*Rule\s*:", re.IGNORECASE)
TAG_RE = re.compile(r"^\s*@\S")
SCENARIO_RE = re.compile(r"^\s*(Background|Scenario|Scenario Outline|Example)\s*:", re.IGNORECASE)

# 命名 anti-pattern tokens — 檔名含即違規。
FILENAME_ANTIPATTERNS = [
    "主流程",
    "流程",
    "體驗",
    "處理",
    "重試",
    "策略",
    "邏輯",
    "experience",
    "handling",
    "management",
    "retry",
    "fallback",
    "policy",
    "logic",
    "-flow",
    "_flow",
]

# 首句 trigger keyword — 聯集（無 operation-type registry 時採 OR 寬鬆判定）。
# 描述段首句含任一 keyword 即視為合規。
COMMON_TRIGGER_KEYWORDS = [
    # UI
    "點擊", "填寫", "送出", "輸入", "選擇", "載入", "進入", "瀏覽",
    "tap", "swipe", "long-press", "滑動",
    "click", "submit", "input", "load", "navigate",
    # web-service
    "呼叫", "call", "invoke",
    "[command]", "[query]",
    "HTTP", "GET", "POST", "PUT", "PATCH", "DELETE",
    "endpoint", "回調", "callback", "webhook",
    # domain-service / utilities
    "method", "函式", "function",
    # worker
    "scheduled-tick", "consumed-message", "cron",
    "事件", "訂閱", "消費", "觸發",
    "consume", "event", "subscription", "scheduled",
]

WORKER_TRIGGER_KINDS = ["scheduled-tick", "consumed-message"]
WORKER_HINTS = ["cron", "事件", "訂閱", "消費", "scheduled", "event", "consume", "subscription"]

# Filename convention enums (must match bdd-constitution §5.1 allowed values)
ALLOWED_CONVENTIONS = {
    "NN-prefix-then-title",
    "kebab-all-lower",
    "snake_case",
    "PascalCase",
    # "free-form:<regex>" handled by prefix check
}
ALLOWED_TITLE_LANGUAGES = {
    "zh-Hant", "zh-Hans", "en", "ja", "ko", "mixed",
    # "custom:<iso-code>" handled by prefix check
}

# CJK Unified Ideographs ranges (rough but practical)
CJK_RE = re.compile(r"[一-鿿㐀-䶿]")
# zh-Hant 與 zh-Hans 共用此檢查（無法純由 regex 區分簡繁，僅檢查「有 CJK 字」）
NON_ASCII_RE = re.compile(r"[^\x00-\x7f]")


def parse_feature(path: Path) -> tuple[str | None, str]:
    """Return (feature_title, description_block_first_sentence)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return (None, "")
    title = None
    feature_idx = -1
    for i, line in enumerate(lines):
        m = FEATURE_RE.match(line)
        if m:
            title = m.group(1).strip()
            feature_idx = i
            break
    if feature_idx < 0:
        return (None, "")
    desc_lines = []
    for line in lines[feature_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            if desc_lines:
                break
            continue
        if RULE_RE.match(line) or SCENARIO_RE.match(line) or TAG_RE.match(line):
            break
        desc_lines.append(stripped)
    first_sentence = " ".join(desc_lines)
    return (title, first_sentence)


def parse_filename_axes(constitution_path: Path) -> tuple[str | None, str | None, list[dict]]:
    """Parse bdd-constitution §5.1 to extract filename.convention + filename.title_language.

    Returns (convention, title_language, violations). violations is non-empty if
    parsing fails or values are missing / not in allowed enum.
    """
    violations = []
    try:
        text = constitution_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        violations.append({
            "rule_id": "CONSTITUTION_UNREADABLE",
            "file": str(constitution_path), "line": 0,
            "msg": f"Cannot read constitution file: {e}",
        })
        return (None, None, violations)

    # Find §5.1 block (markdown header `### 5.1`, `### §5.1`, etc.)
    sec_match = re.search(r"###?\s*§?\s*5\.1\s+[^\n]*\n(.*?)(?=\n###?\s*(?:§?\s*)?\d|\Z)",
                          text, re.DOTALL)
    if not sec_match:
        violations.append({
            "rule_id": "CONSTITUTION_SECTION_MISSING",
            "file": str(constitution_path), "line": 0,
            "msg": "§5.1 (Feature lifecycle axes) section not found in constitution.",
        })
        return (None, None, violations)
    section = sec_match.group(1)

    # Extract `filename.convention` and `filename.title_language` rows from the
    # markdown table. Row shape (3 cols): | `axis_name` | <enum/desc, may contain \|> | <本專案值> |
    def extract_axis(axis_name: str) -> str | None:
        for line in section.splitlines():
            stripped = line.lstrip()
            if not stripped.startswith(f"| `{axis_name}`"):
                continue
            # Replace escaped pipes (\|) with placeholder, split by raw |, restore.
            placeholder = "\x00"
            normalized = line.replace("\\|", placeholder)
            cells = [c.strip() for c in normalized.split("|")]
            # Filter outer empties from leading / trailing |.
            cells = [c for c in cells if c != ""]
            if len(cells) < 3:
                return None
            # 本專案值 is the LAST non-empty cell.
            value = cells[-1].replace(placeholder, "|").strip().strip("`").strip()
            return value
        return None

    convention = extract_axis("filename.convention")
    title_language = extract_axis("filename.title_language")

    if convention is None:
        violations.append({
            "rule_id": "CONSTITUTION_AXIS_MISSING",
            "file": str(constitution_path), "line": 0,
            "msg": "§5.1 missing `filename.convention` axis row.",
        })
    elif (convention not in ALLOWED_CONVENTIONS
          and not convention.startswith("free-form:")):
        violations.append({
            "rule_id": "CONSTITUTION_AXIS_VALUE_INVALID",
            "file": str(constitution_path), "line": 0,
            "msg": f"§5.1 `filename.convention` value '{convention}' not in allowed enum.",
        })

    if title_language is None:
        violations.append({
            "rule_id": "CONSTITUTION_AXIS_MISSING",
            "file": str(constitution_path), "line": 0,
            "msg": "§5.1 missing `filename.title_language` axis row.",
        })
    elif (title_language not in ALLOWED_TITLE_LANGUAGES
          and not title_language.startswith("custom:")):
        violations.append({
            "rule_id": "CONSTITUTION_AXIS_VALUE_INVALID",
            "file": str(constitution_path), "line": 0,
            "msg": f"§5.1 `filename.title_language` value '{title_language}' not in allowed enum.",
        })

    return (convention, title_language, violations)


def check_filename_convention(
    path: Path, convention: str, title_language: str
) -> list[dict]:
    """Validate feature filename against project §5.1 declared convention."""
    stem = path.stem
    violations = []

    # Step 1: schema check based on convention
    if convention == "NN-prefix-then-title":
        m = re.match(r"^(\d{2})-(.+)$", stem)
        if not m:
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' violates declared convention "
                    f"'NN-prefix-then-title'. Expected: NN-<title> (e.g. '01-開啟測試計劃')."
                ),
            })
            return violations
        title = m.group(2)
    elif convention == "kebab-all-lower":
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", stem):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' violates declared convention "
                    f"'kebab-all-lower'. Expected: lowercase alphanumeric with single-hyphen separators."
                ),
            })
            return violations
        title = stem
    elif convention == "snake_case":
        if not re.match(r"^[a-z0-9]+(_[a-z0-9]+)*$", stem):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' violates declared convention "
                    f"'snake_case'. Expected: lowercase alphanumeric with single-underscore separators."
                ),
            })
            return violations
        title = stem
    elif convention == "PascalCase":
        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", stem):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' violates declared convention "
                    f"'PascalCase'. Expected: starts uppercase, alphanumeric only."
                ),
            })
            return violations
        title = stem
    elif convention.startswith("free-form:"):
        regex_str = convention[len("free-form:"):]
        try:
            user_re = re.compile(regex_str)
        except re.error as e:
            violations.append({
                "rule_id": "CONSTITUTION_FREEFORM_REGEX_INVALID",
                "file": str(path), "line": 0,
                "msg": f"§5.1 free-form regex '{regex_str}' does not compile: {e}",
            })
            return violations
        if not user_re.match(stem):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' violates declared convention "
                    f"'free-form:{regex_str}'."
                ),
            })
            return violations
        title = stem
    else:
        # Unknown convention — caller-side validation should have caught this.
        return violations

    # Step 2: title language check (best-effort)
    if title_language in ("zh-Hant", "zh-Hans"):
        if not CJK_RE.search(title):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' title part '{title}' violates declared "
                    f"title_language='{title_language}'. Expected at least one CJK character "
                    f"(Domain 專有名詞可保留原文，但 title 主體必含中文)."
                ),
            })
    elif title_language == "en":
        if NON_ASCII_RE.search(title):
            violations.append({
                "rule_id": "FILENAME_CONVENTION_VIOLATION",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' title part '{title}' violates declared "
                    f"title_language='en'. Expected ASCII only."
                ),
            })
    # Other languages (ja / ko / mixed / custom:*) — skip best-effort check;
    # subagent semantic validation can backfill.

    return violations


def check_filename_antipattern(path: Path) -> list[dict]:
    stem = path.stem
    lower = stem.lower()
    violations = []
    for token in FILENAME_ANTIPATTERNS:
        if token in stem or token in lower:
            violations.append({
                "rule_id": "OPERATION_FILENAME_ANTIPATTERN",
                "file": str(path), "line": 0,
                "msg": (
                    f"Feature filename '{stem}' contains anti-pattern token '{token}'. "
                    f"Rename to an operation-wise name. "
                    f"e.g. *主流程 → 拆成組成的 operations；*重試 → 併入 trigger 的後置 Rule."
                ),
            })
            break
    return violations


def check_header_first_sentence(path: Path, first_sentence: str) -> list[dict]:
    violations = []
    if not first_sentence:
        violations.append({
            "rule_id": "OPERATION_HEADER_FIRST_SENTENCE_MISSING",
            "file": str(path), "line": 0,
            "msg": (
                "Feature header description block is empty. "
                "Must open with operation trigger sentence."
            ),
        })
        return violations
    lower = first_sentence.lower()
    if not any(kw.lower() in lower for kw in COMMON_TRIGGER_KEYWORDS):
        violations.append({
            "rule_id": "OPERATION_HEADER_FIRST_SENTENCE_MISSING",
            "file": str(path), "line": 0,
            "msg": (
                "Feature header first sentence does not contain any recognised "
                "trigger keyword (UI click / HTTP call / worker event / method invoke / ...). "
                f"Got: '{first_sentence[:80]}...'"
            ),
        })
    return violations


def check_worker_trigger_kind(path: Path, first_sentence: str) -> list[dict]:
    """If the feature header looks worker-like, require an explicit trigger kind."""
    lower = first_sentence.lower()
    looks_worker = any(h.lower() in lower for h in WORKER_HINTS)
    if not looks_worker:
        return []
    violations = []
    if not any(kind in first_sentence for kind in WORKER_TRIGGER_KINDS):
        violations.append({
            "rule_id": "OPERATION_WORKER_TRIGGER_UNDECLARED",
            "file": str(path), "line": 0,
            "msg": (
                "Worker-like feature must declare trigger kind "
                f"(one of {WORKER_TRIGGER_KINDS}) in the header description. "
                "Also attach trigger signature (cron spec for scheduled-tick; "
                "topic/event type name for consumed-message)."
            ),
        })
    return violations


def check_feature(
    path: Path,
    convention: str | None = None,
    title_language: str | None = None,
) -> list[dict]:
    v = []
    v.extend(check_filename_antipattern(path))
    if convention is not None and title_language is not None:
        v.extend(check_filename_convention(path, convention, title_language))
    title, first_sentence = parse_feature(path)
    if title is None:
        return v  # FEATURE_HEADER_MISSING caught by check_discovery_phase.py
    v.extend(check_header_first_sentence(path, first_sentence))
    v.extend(check_worker_trigger_kind(path, first_sentence))
    return v


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
    p.add_argument(
        "--constitution",
        help="Path to bdd-constitution.md for §5.1 filename axes alignment check",
    )
    p.add_argument(
        "--features-dir",
        help="Absolute path to Discovery rule-only features directory (default: resolve from arguments.yml + boundary.yml)",
    )
    args = p.parse_args()

    root = Path(args.arguments_path)

    if not root.is_file():
        json.dump({
            "ok": False,
            "summary": {"files_scanned": 0, "violations": 1},
            "violations": [{
                "rule_id": "ARGUMENTS_FILE_MISSING",
                "file": str(root), "line": 0,
                "msg": f"arguments file not found: {root}",
            }],
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 1

    files_scanned = 0
    violations: list[dict] = []
    convention: str | None = None
    title_language: str | None = None

    if args.constitution:
        constitution_path = Path(args.constitution)
        if not constitution_path.is_file():
            violations.append({
                "rule_id": "CONSTITUTION_UNREADABLE",
                "file": str(constitution_path), "line": 0,
                "msg": f"constitution file not found: {constitution_path}",
            })
        else:
            convention, title_language, parse_violations = parse_filename_axes(
                constitution_path
            )
            violations.extend(parse_violations)
            # If parse failed, leave convention/title_language None → skip per-file check
            if parse_violations:
                convention = None
                title_language = None

    if args.features_dir:
        features_dir = Path(args.features_dir).resolve()
    else:
        try:
            features_dir, _, _ = resolve_kickoff_paths(root)
        except Exception as e:
            json.dump({
                "ok": False,
                "summary": {"files_scanned": 0, "violations": 1},
                "violations": [{
                    "rule_id": "KICKOFF_PATH_RESOLVE_FAILED",
                    "file": str(root), "line": 0,
                    "msg": str(e),
                }],
            }, sys.stdout, ensure_ascii=False, indent=2)
            print()
            return 1

    if features_dir is None:
        json.dump({
            "ok": True,
            "summary": {"files_scanned": 0, "violations": 0},
            "violations": [],
            "note": "FEATURE_SPECS_DIR not bound (kickoff-safe); skip feature scan.",
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    if features_dir.is_dir():
        for f in features_dir.rglob("*.feature"):
            files_scanned += 1
            violations.extend(check_feature(f, convention, title_language))

    result = {
        "ok": len(violations) == 0,
        "summary": {
            "files_scanned": files_scanned,
            "violations": len(violations),
        },
        "violations": violations,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
