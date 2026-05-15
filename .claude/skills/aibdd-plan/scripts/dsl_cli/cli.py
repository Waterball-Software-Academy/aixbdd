from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from dsl_cli.corpus import (
    discover_dsl_paths,
    flatten_entry_haystack,
    index_contract_operation_ids,
    load_dsl_file,
    l1_to_text,
    normalize_l1_for_compare,
    preset_handler,
)


def _truth_root_parent() -> ArgumentParser:
    p = ArgumentParser(add_help=False)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--root",
        type=Path,
        default=None,
        metavar="PATH",
        help="Explicit TRUTH_BOUNDARY_ROOT directory (overrides --boundary).",
    )
    g.add_argument(
        "--boundary",
        default=None,
        metavar="NAME",
        help="Boundary directory name under --specs-root. Resolves to specs-root/NAME.",
    )
    p.add_argument(
        "--specs-root",
        type=Path,
        default=Path("specs"),
        metavar="PATH",
        help="Parent directory of boundary folders (default: ./specs relative to cwd). Ignored when --root is set.",
    )
    return p


def resolve_truth_boundary_root(args: Any) -> Path:
    """Set args.root from --root OR (--specs-root + --boundary)."""
    raw_root = getattr(args, "root", None)
    if raw_root is not None:
        return Path(raw_root).expanduser().resolve()
    boundary = getattr(args, "boundary", None)
    if boundary is None or str(boundary).strip() == "":
        print("dsl-cli: require --boundary <name> or --root <path>", file=sys.stderr)
        raise SystemExit(2)
    specs = Path(args.specs_root)
    if not specs.is_absolute():
        specs = Path.cwd() / specs
    return (specs.expanduser() / boundary).resolve()


def cmd_list(args: Any) -> int:
    root: Path = args.root
    paths = discover_dsl_paths(root)
    if not paths:
        print(f"No dsl.yml found under {root} (shared/ or packages/*/dsl.yml).", file=sys.stderr)
        return 1
    for p in paths:
        try:
            entries = load_dsl_file(p)
        except Exception as e:
            print(f"{p}: ERROR {e}", file=sys.stderr)
            return 1
        rel = p.resolve().relative_to(root.resolve()) if p.is_relative_to(root.resolve()) else p
        print(f"{rel}\t{len(entries)}")
    return 0


def cmd_search(args: Any) -> int:
    root: Path = args.root
    query: str = args.query
    paths = discover_dsl_paths(root)
    if not paths:
        print(f"No dsl.yml found under {root}.", file=sys.stderr)
        return 1

    contract_files_for_query: list[str] = []
    if args.contracts_root:
        cr = Path(args.contracts_root).resolve()
        idx = index_contract_operation_ids(cr)
        for rel, opids in idx.items():
            if query in opids:
                contract_files_for_query.append(rel)

    rows: list[tuple[float | None, str, str]] = []

    try:
        from rapidfuzz import fuzz
    except ImportError:
        fuzz = None

    for p in paths:
        try:
            entries = load_dsl_file(p)
        except Exception as e:
            print(f"{p}: ERROR {e}", file=sys.stderr)
            return 1
        rel_path = p.resolve().relative_to(root.resolve()).as_posix() if p.is_relative_to(root.resolve()) else str(p)
        for i, entry in enumerate(entries):
            eid = str(entry.get("id", f"<no-id#{i}>"))
            hay = flatten_entry_haystack(entry)
            score: float | None = None
            matched = False
            if args.fuzzy:
                if fuzz is None:
                    print(
                        "rapidfuzz not installed; omit --fuzzy or install dependency (PEP 723 `uv run` on run.py declares it)",
                        file=sys.stderr,
                    )
                    return 1
                score = float(fuzz.partial_ratio(query.lower(), hay.lower()))
                matched = score >= args.min_score
            else:
                matched = query.lower() in hay.lower()

            l4 = entry.get("L4") if isinstance(entry.get("L4"), dict) else {}
            sref = l4.get("source_refs") if isinstance(l4, dict) else {}
            contract_ref = None
            if isinstance(sref, dict):
                contract_ref = sref.get("contract")

            op_extra = False
            if contract_files_for_query and isinstance(contract_ref, str):
                cref = contract_ref.replace("\\", "/")
                for rel_file in contract_files_for_query:
                    if rel_file in cref or cref.endswith(rel_file):
                        op_extra = True
                        break

            if matched or op_extra:
                label = f"{rel_path} :: {eid}"
                rows.append((score, label, hay[:200].replace("\n", " ")))

    if contract_files_for_query and not rows:
        print("Contract files with this operationId (no DSL entry references them yet):", file=sys.stderr)
        for rel in sorted(contract_files_for_query):
            print(f"  {rel}  operationId={query}", file=sys.stderr)

    if not rows and not contract_files_for_query:
        print("No matches.", file=sys.stderr)
        return 1

    if args.fuzzy:
        rows.sort(key=lambda r: (r[0] is not None, r[0] or 0.0), reverse=True)
    for score, label, snippet in rows:
        if score is not None:
            print(f"{score:.0f}\t{label}\t{snippet}")
        else:
            print(f"{label}\t{snippet}")
    return 0


def cmd_verify(args: Any) -> int:
    root: Path = args.root
    paths = discover_dsl_paths(root)
    if not paths:
        print(f"No dsl.yml found under {root}.", file=sys.stderr)
        return 1

    id_to_locations: dict[str, list[str]] = {}
    l1_groups: dict[tuple[str, str], list[str]] = {}
    surface_warns: list[str] = []

    for p in paths:
        rel = p.resolve().relative_to(root.resolve()).as_posix() if p.is_relative_to(root.resolve()) else str(p)
        try:
            entries = load_dsl_file(p)
        except Exception as e:
            print(f"{p}: ERROR {e}", file=sys.stderr)
            return 1
        seen_surface: dict[str, int] = {}
        for i, entry in enumerate(entries):
            eid = entry.get("id")
            if eid is not None:
                sid = str(eid)
                loc = f"{rel} @entries[{i}]"
                id_to_locations.setdefault(sid, []).append(loc)
            l1n = normalize_l1_for_compare(l1_to_text(entry.get("L1")))
            ph = preset_handler(entry)
            if l1n:
                key = (l1n, ph)
                l1_groups.setdefault(key, []).append(f"{rel} id={entry.get('id', '?')}")
            l4 = entry.get("L4")
            if isinstance(l4, dict):
                sf = l4.get("surface_id")
                if sf is not None:
                    sfs = str(sf)
                    if sfs in seen_surface:
                        surface_warns.append(f"{rel}: duplicate surface_id {sfs!r} (entries[{seen_surface[sfs]}] and [{i}])")
                    else:
                        seen_surface[sfs] = i

    exit_code = 0
    dup_ids = {k: v for k, v in id_to_locations.items() if len(v) > 1}
    if dup_ids:
        exit_code = 1
        print("Duplicate entry id (hard error):", file=sys.stderr)
        for eid, locs in sorted(dup_ids.items()):
            print(f"  {eid}:", file=sys.stderr)
            for loc in locs:
                print(f"    {loc}", file=sys.stderr)

    dup_l1 = {k: v for k, v in l1_groups.items() if len(v) > 1}
    for (_l1, _h), locs in sorted(dup_l1.items(), key=lambda x: -len(x[1])):
        msg = f"Similar L1 + preset.handler={_h!r} ({len(locs)}): " + "; ".join(locs)
        if args.strict:
            exit_code = 1
            print(f"STRICT: {msg}", file=sys.stderr)
        else:
            print(f"WARN: {msg}", file=sys.stderr)

    for w in surface_warns:
        print(f"WARN: {w}", file=sys.stderr)

    if exit_code == 0 and not dup_ids:
        print("verify: OK (no duplicate ids)")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    truth_parent = _truth_root_parent()

    parser = ArgumentParser(prog="dsl-cli", description="Scan boundary truth dsl.yml registries.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", parents=[truth_parent], help="List dsl.yml paths and entry counts")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", parents=[truth_parent], help="Fuzzy or substring search across all entries")
    p_search.add_argument("query", help="Substring or fuzzy needle (e.g. table name, operationId fragment)")
    p_search.add_argument("--fuzzy", action="store_true", help="Use rapidfuzz partial_ratio")
    p_search.add_argument("--min-score", type=float, default=70.0, help="Minimum fuzzy score (0-100)")
    p_search.add_argument(
        "--contracts-root",
        type=Path,
        default=None,
        help="If set, also match entries whose source_refs.contract references a file containing this operationId",
    )
    p_search.set_defaults(func=cmd_search)

    p_ver = sub.add_parser("verify", parents=[truth_parent], help="Check duplicate ids and optional L1 duplicates")
    p_ver.add_argument("--strict", action="store_true", help="Treat duplicate normalized L1 + same handler as error")
    p_ver.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    args.root = resolve_truth_boundary_root(args)

    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
