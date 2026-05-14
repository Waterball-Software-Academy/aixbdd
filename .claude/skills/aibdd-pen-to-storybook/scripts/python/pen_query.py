#!/usr/bin/env python3
"""Query a Pencil .pen JSON file (v2.x plain-text format).

Replaces the jq dependency for aibdd-pen-to-storybook SOP. Stdlib-only.

Usage:
    pen_query.py <pen_path> --all
    pen_query.py <pen_path> --variables
    pen_query.py <pen_path> --top-level
    pen_query.py <pen_path> --screen-node <SCREEN_ID>

Exit codes:
    0  success
    1  file read / json parse / encoding error
    2  query target not found (e.g. unknown screen id)
"""

from __future__ import annotations

import argparse
import json
import sys


def load_pen(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"pen-query: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(
            f"pen-query: {path} is not UTF-8 text (binary or encrypted .pen?)",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"pen-query: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def query_top_level(doc: dict) -> list[dict]:
    return [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "type": c.get("type"),
            "w": c.get("width"),
            "h": c.get("height"),
        }
        for c in doc.get("children", [])
    ]


def query_screen_node(doc: dict, screen_id: str) -> dict:
    for child in doc.get("children", []):
        if child.get("id") == screen_id:
            return child
    print(f"pen-query: no child with id={screen_id}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Query a Pencil .pen JSON file (replaces jq for aibdd-pen-to-storybook).",
    )
    ap.add_argument("pen_path", help="absolute path to .pen file")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="emit full doc (replaces jq '.')")
    g.add_argument("--variables", action="store_true", help="emit .variables (replaces jq '.variables')")
    g.add_argument(
        "--top-level",
        action="store_true",
        help="emit [{id,name,type,w,h}, ...] from top-level children",
    )
    g.add_argument(
        "--screen-node",
        metavar="SCREEN_ID",
        help="emit children[i] where id==SCREEN_ID (replaces jq '.children[] | select(.id==...)')",
    )
    args = ap.parse_args()

    doc = load_pen(args.pen_path)

    if args.all:
        result: object = doc
    elif args.variables:
        result = doc.get("variables", {})
    elif args.top_level:
        result = query_top_level(doc)
    else:
        result = query_screen_node(doc, args.screen_node)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
