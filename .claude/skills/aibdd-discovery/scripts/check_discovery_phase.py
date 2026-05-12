#!/usr/bin/env python3
"""
check_discovery_phase.py — Discovery Quality Gate (kickoff boundary-aware)

掃描 **resolved** `${FEATURE_SPECS_DIR}/**/*.feature`：
預設由 `${AIBDD_ARGUMENTS_PATH}` + `${BOUNDARY_YML}` 機械展開（見同目錄
`kickoff_path_resolve.py`）；亦可由 `--features-dir` 覆寫為絕對路徑。

驗證 Discovery 階段（rule-only mode）的硬約束：
  - 必須含 @ignore 標籤
  - 必須至少一條 Rule
  - 不得含 Background（rule-only 沒有 Example 可共用 Given）
  - 不得含 Examples / Scenario / Scenario Outline 區塊
  - 每條 Rule 必須使用 4-rules 前綴（前置（狀態）/前置（參數）/後置（回應）/後置（狀態））
    後置（狀態）可選用子類：後置（狀態：資料）/後置（狀態：外發）/後置（狀態：資源）/後置（狀態：行為）
  - description 段 / Rule body / bullet 行首不可撞 zh-TW dialect 繁中 Gherkin keyword
    （當 / 假設 / 假定 / 假如 / 那麼 / 而且 / 並且 / 但是；含「當前」prefix collision）
    來源：@cucumber/gherkin gherkin-languages.json + bdd-constitution §1.1

Usage:
  python check_discovery_phase.py <AIBDD_ARGUMENTS_PATH> [--features-dir ABS_PATH]

Output: stdout JSON
  {
    "ok": <bool>,
    "summary": {"files_scanned": int, "violations": int},
    "violations": [
      {"rule_id": "DISCOVERY_FEATURE_MISSING_IGNORE",
       "file": "...", "line": 0,
       "msg": "Discovery-phase feature must be tagged @ignore."},
      {"rule_id": "RULE_BODY_KEYWORD_COLLISION",
       "file": "...", "line": <int>,
       "msg": "Description/Rule body line starts with zh-TW Gherkin keyword..."}
    ]
  }

Exit: 0 if ok=true, 1 if ok=false.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from kickoff_path_resolve import resolve_kickoff_paths

TAG_LINE_RE = re.compile(r"^\s*@\S+")
IGNORE_TAG_RE = re.compile(r"@ignore\b")
RULE_RE = re.compile(r"^\s*Rule\s*:", re.IGNORECASE)
RULE_PREFIX_RE = re.compile(
    r"^\s*Rule\s*:\s*(前置（狀態）|前置（參數）|後置（回應）|後置（狀態：資料）|後置（狀態：外發）|後置（狀態：資源）|後置（狀態：行為）|後置（狀態）)\s*-",
)
BACKGROUND_RE = re.compile(r"^\s*Background\s*:", re.IGNORECASE)
SCENARIO_RE = re.compile(r"^\s*(Scenario|Scenario Outline|Example)\s*:", re.IGNORECASE)
FEATURE_RE = re.compile(r"^\s*Feature\s*:", re.IGNORECASE)

# zh-TW dialect 繁中 Gherkin keywords（@cucumber/gherkin gherkin-languages.json）。
# Description / Rule body / bullet 行的「行首」撞到任一個就會被 parser 誤抓成 step；
# 含「當前」這類 prefix collision（regex 會匹配「當」起首）。
ZH_TW_KEYWORDS = ("當", "假設", "假定", "假如", "那麼", "而且", "並且", "但是")
KEYWORD_COLLISION_RE = re.compile(
    r"^\s+(" + "|".join(ZH_TW_KEYWORDS) + r")",
)


def _stripped_lines(text: str) -> list[tuple[int, str]]:
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.split("#", 1)[0]
        out.append((i, stripped))
    return out


def check_feature(path: Path) -> list[dict]:
    violations: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        return [{
            "rule_id": "FILE_READ_ERROR",
            "file": str(path), "line": 0,
            "msg": f"cannot read: {e}",
        }]

    lines = _stripped_lines(text)
    has_feature = False
    has_ignore = False
    has_rule = False
    feature_line = 0
    pre_feature_tags: list[str] = []

    for lineno, line in lines:
        if not has_feature and TAG_LINE_RE.match(line):
            pre_feature_tags.append(line.strip())
        if FEATURE_RE.search(line):
            has_feature = True
            feature_line = lineno
            for tag_line in pre_feature_tags:
                if IGNORE_TAG_RE.search(tag_line):
                    has_ignore = True
                    break
        if BACKGROUND_RE.search(line):
            violations.append({
                "rule_id": "DISCOVERY_FEATURE_HAS_BACKGROUND",
                "file": str(path), "line": lineno,
                "msg": (
                    "Discovery-phase (rule-only) feature must not contain "
                    "'Background:'. Background is only meaningful when "
                    "Examples exist."
                ),
            })
        if RULE_RE.search(line):
            has_rule = True
            if not RULE_PREFIX_RE.search(line):
                violations.append({
                    "rule_id": "DISCOVERY_RULE_MISSING_PREFIX",
                    "file": str(path), "line": lineno,
                    "msg": (
                        "Rule must use a 4-rules prefix: "
                        "前置（狀態）/ 前置（參數）/ 後置（回應）/ 後置（狀態）. "
                        "後置（狀態）optional sub-types: "
                        "後置（狀態：資料）/ 後置（狀態：外發）/ "
                        "後置（狀態：資源）/ 後置（狀態：行為）"
                    ),
                })
        m = SCENARIO_RE.search(line)
        if m:
            violations.append({
                "rule_id": "DISCOVERY_FEATURE_HAS_EXAMPLES",
                "file": str(path), "line": lineno,
                "msg": (
                    f"Discovery-phase feature must not contain '{m.group(1)}:' "
                    "blocks. Examples are formulated in a later phase."
                ),
            })
        # zh-TW Gherkin keyword collision 守門：description / Rule body / bullet
        # 的「行首」不可為 zh-TW dialect 繁中 keyword（含「當前」prefix collision）。
        # Rule line 本身（^\s*Rule\s*:）不會 match，因為 Rule line 行首是 R 不是繁中 keyword。
        # 只在 Feature: 之後才檢查（避免誤檢 file header tag / 空白）。
        if has_feature and KEYWORD_COLLISION_RE.match(line):
            kw_match = KEYWORD_COLLISION_RE.match(line)
            kw = kw_match.group(1) if kw_match else "?"
            violations.append({
                "rule_id": "RULE_BODY_KEYWORD_COLLISION",
                "file": str(path), "line": lineno,
                "msg": (
                    f"Description / Rule body line starts with zh-TW Gherkin "
                    f"dialect keyword '{kw}' (collides with @cucumber/gherkin "
                    "parsing; including prefix collision like '當前'). "
                    "Rephrase to start with a different word — e.g. "
                    "'當 X 時' → '若 X' or 'X 時'; "
                    "'當前 phase' → 'Goal 當前 phase'. "
                    "Full blacklist + rewrite table: "
                    "bdd-constitution §1.1 / "
                    "aibdd-form-feature-spec format-reference §zh-TW Gherkin 關鍵字撞牆禁忌."
                ),
            })

    if not has_feature:
        violations.append({
            "rule_id": "FEATURE_HEADER_MISSING",
            "file": str(path), "line": 0,
            "msg": "No 'Feature:' declaration found.",
        })
    else:
        if not has_ignore:
            violations.append({
                "rule_id": "DISCOVERY_FEATURE_MISSING_IGNORE",
                "file": str(path), "line": feature_line,
                "msg": "Discovery-phase feature must be tagged @ignore.",
            })
        if not has_rule:
            violations.append({
                "rule_id": "DISCOVERY_FEATURE_MISSING_RULE",
                "file": str(path), "line": feature_line,
                "msg": "Discovery-phase feature must contain at least one 'Rule:'.",
            })
    return violations


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
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
            "note": "FEATURE_SPECS_DIR not bound (kickoff-safe); skip Discovery feature scan.",
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    files_scanned = 0
    violations: list[dict] = []

    if features_dir.is_dir():
        for f in features_dir.rglob("*.feature"):
            files_scanned += 1
            violations.extend(check_feature(f))

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
