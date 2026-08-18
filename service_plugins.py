from __future__ import annotations

from typing import Any

from dependencies import CurrentUser


def default_mutator(payload: dict[str, Any], current_user: CurrentUser) -> dict[str, Any]:
    normalized_payload = dict(payload)
    normalized_payload["sku"] = normalized_payload["sku"].strip().upper()

    note = normalized_payload.get("note")
    if note:
        normalized_payload["note"] = f"{note} | actor={current_user.user_id}"

    return normalized_payload