#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "prance",
#   "ruamel.yaml",
# ]
# ///
"""operation summary 全域唯一機械驗證 — aibdd-api-plan SOP Step 7.2 機械層 check。

遞迴掃 `<contracts-dir>` 下所有 `*.api.yml`，重用 `aibdd-core` 的 OpenAPI parser
抽出每個 path × method operation 的 `summary`，檢驗：

  1. SUMMARY_MISSING — operation 缺 `summary`（或僅空白）
  2. SUMMARY_UNIQUE  — `summary`（去頭尾空白後、大小寫敏感）在整個目錄樹內跨檔唯一

輸入：contracts 目錄路徑（單一）
輸出：JSON {ok, summary, violations[]}（exit 0 = ok=true, exit 1 = ok=false）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
# parents[0]=scripts, [1]=aibdd-api-plan, [2]=skills root
_AIBDD_CORE_LIB = _THIS_FILE.parents[2] / "aibdd-core" / "scripts" / "lib"
if str(_AIBDD_CORE_LIB) not in sys.path:
    sys.path.insert(0, str(_AIBDD_CORE_LIB))

from shared.spec_parsers.openapi import (  # noqa: E402
    OpenAPIParseError,
    OpenAPISpecParser,
)


def _op_label(rel_file: str, method: str, url_path: str) -> str:
    return f"{rel_file}#{method.upper()} {url_path}"


def main(dir_str: str) -> int:
    root = Path(dir_str)
    if not root.is_dir():
        print(
            json.dumps(
                {
                    "ok": False,
                    "summary": f"directory not found: {dir_str}",
                    "violations": [{"check": "DIR_EXISTS", "detail": str(root)}],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    violations: list[dict] = []
    files = sorted(root.rglob("*.api.yml"))
    occurrences: dict[str, list[str]] = {}
    op_count = 0
    parser = OpenAPISpecParser()

    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            parts = parser.parse(path)
        except OpenAPIParseError as exc:
            violations.append({"check": "OPENAPI_PARSE", "detail": f"{rel}: {exc}"})
            continue
        for part in parts:
            op_count += 1
            label = _op_label(rel, part.method, part.path)
            normalized = (part.summary or "").strip()
            if not normalized:
                violations.append(
                    {
                        "check": "SUMMARY_MISSING",
                        "detail": f"operation missing summary: {label}",
                    }
                )
                continue
            occurrences.setdefault(normalized, []).append(label)

    for text, labels in occurrences.items():
        if len(labels) > 1:
            violations.append(
                {
                    "check": "SUMMARY_UNIQUE",
                    "detail": f'duplicate summary: "{text}" in ' + " 與 ".join(labels),
                }
            )

    ok = len(violations) == 0
    print(
        json.dumps(
            {
                "ok": ok,
                "summary": {
                    "dir": str(root),
                    "files": len(files),
                    "operations": op_count,
                    "violations_count": len(violations),
                },
                "violations": violations,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check_summary_unique.py <contracts-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
