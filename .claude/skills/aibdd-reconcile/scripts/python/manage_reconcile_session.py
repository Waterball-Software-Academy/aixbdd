#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from _common import (
    PHASE_INDEX,
    final_session_path,
    load_json,
    phase_is_more_upstream,
    utc_now_iso,
    utc_session_id,
    write_json,
)


def _parse_chain(raw: str) -> list[str]:
    chain = [item.strip() for item in raw.split(",") if item.strip()]
    if not chain:
        raise SystemExit("cascade chain may not be empty")
    unknown = [item for item in chain if item not in PHASE_INDEX]
    if unknown:
        raise SystemExit(f"unsupported planners in cascade chain: {unknown}")
    return chain


def _emit(session_path: Path, session: dict[str, Any], extra: dict[str, Any] | None = None) -> int:
    payload = {
        "ok": True,
        "session_path": str(session_path),
        "stdout_session_path": str(session_path),
        "stdout_session_id": session.get("session_id", ""),
        "stdout_archive_path": session.get("archive_path", ""),
        "stdout_replay_from": session.get("replay_from", ""),
        "stdout_current_pointer": session.get("current_pointer", ""),
    }
    if extra:
        payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def start(active_session_path: Path, record_path: str, target_plan_package: str, trigger_text: str, earliest: str, chain_csv: str) -> int:
    chain = _parse_chain(chain_csv)
    if earliest not in PHASE_INDEX:
        raise SystemExit(f"unsupported earliest planner: {earliest}")
    session_id = utc_session_id()
    now = utc_now_iso()
    archive_path = str(active_session_path.parent / session_id)
    session = {
        "version": 1,
        "session_id": session_id,
        "status": "running",
        "mode": "start_new",
        "target_plan_package": target_plan_package,
        "record_path": record_path,
        "archive_path": archive_path,
        "earliest_planner": earliest,
        "replay_from": earliest,
        "current_pointer": earliest,
        "cascade_chain": chain,
        "triggers": [
            {"at": now, "kind": "initial", "text": trigger_text},
        ],
        "events": [
            {
                "at": now,
                "type": "classified",
                "earliest_planner": earliest,
                "replay_from": earliest,
                "current_pointer": earliest,
            }
        ],
        "started_at": now,
    }
    write_json(active_session_path, session)
    return _emit(active_session_path, session)


def merge(active_session_path: Path, trigger_text: str, earliest: str, chain_csv: str) -> int:
    session = load_json(active_session_path)
    if not isinstance(session, dict):
        raise SystemExit(f"active session not found: {active_session_path}")
    chain = _parse_chain(chain_csv)
    if earliest not in PHASE_INDEX:
        raise SystemExit(f"unsupported earliest planner: {earliest}")
    now = utc_now_iso()
    current_pointer = str(session.get("current_pointer") or session.get("replay_from") or earliest)
    replay_from = earliest if phase_is_more_upstream(earliest, current_pointer) else current_pointer
    triggers = list(session.get("triggers") or [])
    triggers.append({"at": now, "kind": "retrigger", "text": trigger_text})
    events = list(session.get("events") or [])
    events.append(
        {
            "at": now,
            "type": "reclassified",
            "earliest_planner": earliest,
            "replay_from": replay_from,
            "current_pointer": replay_from,
        }
    )
    session["mode"] = "merge_existing"
    session["earliest_planner"] = earliest
    session["replay_from"] = replay_from
    session["current_pointer"] = replay_from
    session["cascade_chain"] = chain
    session["triggers"] = triggers
    session["events"] = events
    write_json(active_session_path, session)
    return _emit(active_session_path, session)


def advance(active_session_path: Path, next_pointer: str) -> int:
    session = load_json(active_session_path)
    if not isinstance(session, dict):
        raise SystemExit(f"active session not found: {active_session_path}")
    if next_pointer not in PHASE_INDEX:
        raise SystemExit(f"unsupported next pointer: {next_pointer}")
    now = utc_now_iso()
    events = list(session.get("events") or [])
    events.append(
        {
            "at": now,
            "type": "advanced",
            "current_pointer": next_pointer,
        }
    )
    session["current_pointer"] = next_pointer
    session["events"] = events
    write_json(active_session_path, session)
    return _emit(active_session_path, session)


def finish(active_session_path: Path, status: str) -> int:
    session = load_json(active_session_path)
    if not isinstance(session, dict):
        raise SystemExit(f"active session not found: {active_session_path}")
    now = utc_now_iso()
    session["status"] = status
    session["current_pointer"] = "done"
    session["ended_at"] = now
    events = list(session.get("events") or [])
    events.append({"at": now, "type": "finished", "current_pointer": "done"})
    session["events"] = events
    final_path = final_session_path(active_session_path, str(session["session_id"]))
    write_json(final_path, session)
    active_session_path.unlink(missing_ok=True)
    return _emit(
        final_path,
        session,
        {
            "stdout_final_session_path": str(final_path),
            "stdout_archive_path": str(session.get("archive_path", "")),
        },
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: manage_reconcile_session.py <action> ...", file=sys.stderr)
        return 2

    action = sys.argv[1].strip()
    if action == "start":
        if len(sys.argv) != 8:
            print(
                "usage: manage_reconcile_session.py start <active_session_path> <record_path> <target_plan_package> <trigger_text> <earliest> <chain_csv>",
                file=sys.stderr,
            )
            return 2
        return start(Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    if action == "merge":
        if len(sys.argv) != 6:
            print(
                "usage: manage_reconcile_session.py merge <active_session_path> <trigger_text> <earliest> <chain_csv>",
                file=sys.stderr,
            )
            return 2
        return merge(Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
    if action == "advance":
        if len(sys.argv) != 4:
            print(
                "usage: manage_reconcile_session.py advance <active_session_path> <next_pointer>",
                file=sys.stderr,
            )
            return 2
        return advance(Path(sys.argv[2]), sys.argv[3])
    if action == "finish":
        if len(sys.argv) != 4:
            print(
                "usage: manage_reconcile_session.py finish <active_session_path> <status>",
                file=sys.stderr,
            )
            return 2
        return finish(Path(sys.argv[2]), sys.argv[3])

    print(f"unsupported action: {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
