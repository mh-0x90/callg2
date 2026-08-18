from __future__ import annotations

from importlib import import_module
import sqlite3
from typing import Callable
from typing import Any

from dependencies import CurrentUser
from repository import insert_ruby_action


PayloadMutator = Callable[[dict[str, Any], CurrentUser], dict[str, Any]]

# Keep this allowlist explicit so only vetted plugin functions can be loaded.
ALLOWED_MUTATORS: dict[str, str] = {
    "sku_default": "service_plugins:default_mutator",
}


def default_mutator(payload: dict[str, Any], _: CurrentUser) -> dict[str, Any]:
    normalized_payload = dict(payload)
    normalized_payload["sku"] = normalized_payload["sku"].strip().upper()
    return normalized_payload


def _load_mutator(mutator_key: str | None) -> PayloadMutator:
    if not mutator_key:
        return default_mutator

    target = ALLOWED_MUTATORS.get(mutator_key)
    if not target:
        raise ValueError(f"Unsupported mutator key: {mutator_key}")

    module_name, function_name = target.split(":", maxsplit=1)
    module = import_module(module_name)
    mutator = getattr(module, function_name)

    if not callable(mutator):
        raise TypeError(f"Loaded mutator '{mutator_key}' is not callable")

    return mutator


def create_ruby_record(
    connection: sqlite3.Connection,
    payload: dict[str, Any],
    current_user: CurrentUser,
    mutator_key: str | None = None,
) -> dict[str, object]:
    mutator = _load_mutator(mutator_key)
    prepared_payload = mutator(payload, current_user)

    return insert_ruby_action(
        connection,
        sku=prepared_payload["sku"],
        quantity=prepared_payload["quantity"],
        note=prepared_payload.get("note"),
        created_by=current_user.user_id,
        user_group="SKU",
    )