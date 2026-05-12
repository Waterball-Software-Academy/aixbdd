"""Capture HTTP responses and attach transport probes for common Then steps."""

from __future__ import annotations

from typing import Any, Mapping


class LastResponseShim:
    __slots__ = ("_raw", "_envelope")

    def __init__(self, raw: Any, envelope: dict[str, Any]) -> None:
        self._raw = raw
        self._envelope = envelope

    def json(self) -> dict[str, Any]:
        return self._envelope

    @property
    def status_code(self) -> int:
        return int(self._raw.status_code)


def attach_http_transport(context: Any, response: Any) -> None:
    try:
        payload = response.json()
    except Exception:
        payload = {}

    if not isinstance(payload, Mapping):
        payload = {"_value": payload}

    merged: dict[str, Any] = dict(payload)
    ok = 200 <= int(response.status_code) < 300
    merged["__http"] = {
        "status_class": "success" if ok else "failure",
        "status_code": int(response.status_code),
    }
    context.last_response = LastResponseShim(response, merged)
