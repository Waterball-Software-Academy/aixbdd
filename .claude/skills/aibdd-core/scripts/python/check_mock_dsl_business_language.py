#!/usr/bin/env python3
"""
check_mock_dsl_business_language.py

Enforces four physical-first invariants on DSL entries in boundary `dsl.md`:

  - MOCK_DSL_HAS_MOCK_TAG (per principle MR-1):
    Every entry with l2_semantic = "mock-setup" must have l3_step_pattern starting
    with "Given [MOCK] " or "And [MOCK] " or "But [MOCK] ".

  - MOCK_DSL_L1_BUSINESS_LANGUAGE_GUARD (per principle MR-2):
    Every entry with l2_semantic = "mock-setup" must have l1_business / l3_step_pattern
    free of forbidden tokens:
      mock mechanism: mock, stub, queue, dequeue, pop, push, fixture, MSW, harness,
                       spy, arming, armed, 推入, 佇列, mock framework, test double
      schema names:   TestReport, largeGherkinStep, regressedGoalIds, phaseAdvancedTo
                       (any contracts/-defined identifier — best-effort heuristic)
      op ids:         verify_goal, get_next_goal, bindTestplan, op-* tokens

  - DSL_DATATABLE_NOT_KEY_VALUE_BAG (per principle MR-6):
    Any DSL entry containing a datatable header in l1_business / l3_step_pattern
    must NOT use meta-naming column headers (key-value-bag pattern). Forbidden
    column header tokens: 欄位, 值, field, value, key, label, text, name, 名稱,
    type, 類型. Header MUST be ≥1 domain field name; single-column N-row form
    (e.g., `| 評審 |` + multiple rows) is permitted.

  - DSL_DATATABLE_PARAMS_MAPPING_COMPLETE (per principle MR-7):
    Any DSL entry containing a datatable header must have parameters[] with
    one `position: datatable-column` entry per column header. Mismatch in
    column count vs datatable-column entry count fails the gate.

  Domain term allowlist (NOT flagged): Goal, Scenario, Path, Worker Agent, 工程師,
                                        指揮站臺, 驗收, 規格.

Datatable rows / headers within the entry's l1_business / l3_step_pattern blocks
are also scanned (since they are part of the canonical L1 surface).

Usage:
  python3 check_mock_dsl_business_language.py path/to/dsl.md [--allow-extra TOKEN ...]

Exit code:
  0  — no violations
  1  — at least one violation (printed to stderr)
"""

import argparse
import re
import sys
from pathlib import Path

# === Forbidden token taxonomy (per principle MR-2) ===

MOCK_MECHANISM_TOKENS = [
    "mock", "stub", "queue", "dequeue", "pop", "push", "fixture", "MSW",
    "harness", "spy", "arming", "armed", "推入", "佇列",
    "mock framework", "test double",
]

SCHEMA_NAME_TOKENS = [
    "TestReport", "largeGherkinStep", "regressedGoalIds", "phaseAdvancedTo",
    "smallFeature", "verifyResult",
]

OP_ID_TOKENS = [
    "verify_goal", "get_next_goal", "bindTestplan", "executeWizard",
    "op-mcp-verify-goal", "op-mcp-get-next-goal", "op-bind-testplan",
    "op-execute-wizard", "op-launch-station", "op-unbind-station",
    "op-get-current-session", "op-open-impl-file",
]

# Datatable meta-naming tokens (per MR-6): forbidden as column header
META_NAMING_HEADER_TOKENS = {
    "欄位", "值", "field", "value", "key", "label", "text",
    "name", "名稱", "type", "類型",
}

# Domain terms allowed to appear (NOT flagged):
DOMAIN_ALLOWLIST = {
    "Goal", "Scenario", "Path", "Worker Agent", "工程師",
    "指揮站臺", "驗收", "規格", "evaluator",  # "evaluator" itself is okay as domain concept; only "mock"/"stub" of it is banned
}

# === DSL entry parsing ===

ENTRY_BLOCK_RE = re.compile(
    r"^### (DSL-[A-Z0-9-]+)\s*\n+```yaml\n(.*?)\n```",
    re.DOTALL | re.MULTILINE,
)

L1_FIELD_RE = re.compile(r"^l1_business:\s*(.*?)(?=^[a-z][a-z0-9_]*:|\Z)", re.MULTILINE | re.DOTALL)
L2_FIELD_RE = re.compile(r"^l2_semantic:\s*(.+?)$", re.MULTILINE)
L3_FIELD_RE = re.compile(r"^l3_step_pattern:\s*(.*?)(?=^[a-z][a-z0-9_]*:|\Z)", re.MULTILINE | re.DOTALL)


def find_entries(content: str):
    """Yield (entry_id, yaml_body) tuples from the boundary dsl.md content."""
    for match in ENTRY_BLOCK_RE.finditer(content):
        yield match.group(1), match.group(2)


def extract_field(yaml_body: str, regex):
    m = regex.search(yaml_body)
    if not m:
        return None
    return m.group(1).strip()


def is_mock_setup(yaml_body: str) -> bool:
    val = extract_field(yaml_body, L2_FIELD_RE)
    return val == "mock-setup"


def has_mock_tag(l3: str) -> bool:
    """Check that l3_step_pattern starts with 'Given/And/But [MOCK] '."""
    if not l3:
        return False
    # Strip leading | (literal block scalar marker), YAML quoting, and whitespace
    stripped = l3.lstrip("|").lstrip().lstrip("'").lstrip('"').lstrip()
    lines = [ln.rstrip() for ln in stripped.splitlines() if ln.strip()]
    if not lines:
        return False
    first = lines[0].lstrip().lstrip("'").lstrip('"').lstrip()
    return bool(re.match(r"^(Given|And|But)\s+\[MOCK\]\s+", first))


def strip_mock_tag(text: str) -> str:
    """Remove the literal `[MOCK]` tag (case-sensitive) so it does not trigger
    the substring-match for forbidden token `mock`."""
    return re.sub(r"\[MOCK\]", "", text)


# Match a Gherkin datatable header line: `    | a | b | c |`
# Captures the inner pipe-separated columns; ignores blocks not starting and ending with `|`.
DATATABLE_HEADER_RE = re.compile(r"^\s*\|\s*([^\n]+?)\s*\|\s*$", re.MULTILINE)


def extract_datatable_headers(text: str) -> list[list[str]]:
    """Find datatable header rows in a multi-line block.
    Returns list of header column lists. Header is the FIRST `|` row in any
    contiguous datatable block."""
    if not text:
        return []
    headers: list[list[str]] = []
    lines = text.splitlines()
    in_block = False
    for line in lines:
        if re.match(r"^\s*\|", line):
            if not in_block:
                # First | row in a fresh block = header
                cols = [c.strip() for c in line.strip().strip("|").split("|")]
                cols = [c for c in cols if c]
                if cols:
                    headers.append(cols)
                in_block = True
        else:
            in_block = False
    return headers


def find_meta_naming_violations(headers: list[list[str]]) -> list[str]:
    """Return list of violating column header tokens found across all header rows."""
    hits: list[str] = []
    for header_row in headers:
        for col in header_row:
            col_norm = col.strip().lower()
            for forbidden in META_NAMING_HEADER_TOKENS:
                if col_norm == forbidden.lower():
                    hits.append(col)
                    break
    return hits


PARAMS_BLOCK_RE = re.compile(r"^parameters:\s*(.*?)(?=^[a-z][a-z0-9_]*:|\Z)", re.MULTILINE | re.DOTALL)
PARAM_ENTRY_RE = re.compile(r"^\s*-\s+name:\s*(.+?)$", re.MULTILINE)
PARAM_POSITION_RE = re.compile(r"^\s+position:\s*(.+?)$", re.MULTILINE)


def extract_datatable_column_params(yaml_body: str) -> list[str]:
    """Return list of parameter names that have `position: datatable-column`."""
    m = PARAMS_BLOCK_RE.search(yaml_body)
    if not m:
        return []
    block = m.group(1)
    # Split by `- name:` boundaries; each chunk is one parameter entry
    entries = re.split(r"(?=^\s*-\s+name:)", block, flags=re.MULTILINE)
    result = []
    for entry in entries:
        name_m = PARAM_ENTRY_RE.search(entry)
        pos_m = PARAM_POSITION_RE.search(entry)
        if name_m and pos_m and pos_m.group(1).strip() == "datatable-column":
            result.append(name_m.group(1).strip())
    return result


def find_forbidden_tokens(text: str, extra_allow: set[str]):
    """Return list of (category, token) pairs found in text."""
    if not text:
        return []
    hits = []
    # Use word-boundary regex for English tokens; substring match for Chinese
    for token in MOCK_MECHANISM_TOKENS:
        if token in extra_allow:
            continue
        pattern = re.escape(token)
        # English: word-boundary; Chinese: simple substring
        if re.search(r"[一-鿿]", token):
            if token in text:
                hits.append(("mock-mechanism", token))
        else:
            if re.search(rf"(?i)\b{pattern}\b", text):
                hits.append(("mock-mechanism", token))
    for token in SCHEMA_NAME_TOKENS:
        if token in extra_allow:
            continue
        if re.search(rf"\b{re.escape(token)}\b", text):
            hits.append(("schema-name", token))
    for token in OP_ID_TOKENS:
        if token in extra_allow:
            continue
        if re.search(rf"\b{re.escape(token)}\b", text):
            hits.append(("op-id", token))
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dsl_local_path", type=Path, help="Path to boundary dsl.md")
    parser.add_argument("--allow-extra", action="append", default=[],
                        help="Extra tokens allowed (e.g. domain-specific noise)")
    args = parser.parse_args()

    if not args.dsl_local_path.exists():
        print(f"ERROR: file not found: {args.dsl_local_path}", file=sys.stderr)
        sys.exit(2)

    content = args.dsl_local_path.read_text(encoding="utf-8")
    extra_allow = set(args.allow_extra) | DOMAIN_ALLOWLIST

    violations: list[dict] = []
    n_mock_entries = 0
    n_datatable_entries = 0

    for entry_id, yaml_body in find_entries(content):
        l1 = extract_field(yaml_body, L1_FIELD_RE) or ""
        l3 = extract_field(yaml_body, L3_FIELD_RE) or ""

        # === MOCK-only checks (Check 1 + Check 2) ===
        if is_mock_setup(yaml_body):
            n_mock_entries += 1

            # Check 1: MOCK_DSL_HAS_MOCK_TAG
            if not has_mock_tag(l3):
                violations.append({
                    "entry": entry_id,
                    "invariant": "MOCK_DSL_HAS_MOCK_TAG",
                    "detail": f"l3_step_pattern must start with 'Given/And/But [MOCK] ' but begins: {l3[:80]!r}",
                })

            # Check 2: MOCK_DSL_L1_BUSINESS_LANGUAGE_GUARD
            # Strip the literal `[MOCK]` tag before token check so the tag itself
            # does not trigger the `mock` substring match.
            for surface_name, surface_text in [
                ("l1_business", strip_mock_tag(l1)),
                ("l3_step_pattern", strip_mock_tag(l3)),
            ]:
                hits = find_forbidden_tokens(surface_text, extra_allow)
                for category, token in hits:
                    violations.append({
                        "entry": entry_id,
                        "invariant": "MOCK_DSL_L1_BUSINESS_LANGUAGE_GUARD",
                        "detail": f"{surface_name} contains forbidden {category} token {token!r}",
                    })

        # === Datatable checks (Check 3 + Check 4) — apply to ALL entries with datatable ===
        # Combine l1 + l3 surfaces to find any datatable headers
        combined = strip_mock_tag(l1) + "\n" + strip_mock_tag(l3)
        headers = extract_datatable_headers(combined)
        # De-duplicate (same header listed in both l1 and l3 only counts once)
        seen = set()
        uniq_headers: list[list[str]] = []
        for h in headers:
            key = tuple(h)
            if key not in seen:
                seen.add(key)
                uniq_headers.append(h)

        if not uniq_headers:
            continue
        n_datatable_entries += 1

        # Check 3: DSL_DATATABLE_NOT_KEY_VALUE_BAG (per MR-6)
        meta_hits = find_meta_naming_violations(uniq_headers)
        for hit in meta_hits:
            violations.append({
                "entry": entry_id,
                "invariant": "DSL_DATATABLE_NOT_KEY_VALUE_BAG",
                "detail": f"datatable header column {hit!r} is meta-naming (forbidden per MR-6); "
                          f"header must be ≥1 domain field name, not key-value-bag",
            })

        # Check 4: DSL_DATATABLE_PARAMS_MAPPING_COMPLETE (per MR-7)
        # Use the first unique header as the canonical column set
        canonical_header = uniq_headers[0]
        n_columns = len(canonical_header)
        col_params = extract_datatable_column_params(yaml_body)
        n_col_params = len(col_params)
        if n_columns != n_col_params:
            violations.append({
                "entry": entry_id,
                "invariant": "DSL_DATATABLE_PARAMS_MAPPING_COMPLETE",
                "detail": f"datatable has {n_columns} column(s) {canonical_header!r} but parameters[] "
                          f"has {n_col_params} entry/entries with position=datatable-column "
                          f"({col_params!r}); each column must map to one parameter",
            })

    # === Report ===
    summary = {
        "file": str(args.dsl_local_path),
        "mock_setup_entries_scanned": n_mock_entries,
        "datatable_entries_scanned": n_datatable_entries,
        "violations_count": len(violations),
    }

    if violations:
        print("DSL business-language + datatable schema gate: VIOLATIONS FOUND", file=sys.stderr)
        for v in violations:
            print(f"  {v['entry']}  {v['invariant']}  — {v['detail']}", file=sys.stderr)
        print(f"\nSummary: {summary}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"DSL business-language + datatable schema gate: OK "
              f"({n_mock_entries} mock-setup + {n_datatable_entries} datatable entries scanned, 0 violations)")
        sys.exit(0)


if __name__ == "__main__":
    main()
