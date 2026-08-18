from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Callable

from ping_service import PingService
from run_service import run

if TYPE_CHECKING:
    from olten4 import Profile


def ping(value: str) -> str:
    """Ping operation: validate and check if value is reachable."""
    return PingService.ping(value)


# Function registry for dynamic operations
OPERATIONS: dict[str, Callable[[str], str]] = {
    "ping": ping,
    "run": run,
}


def apply_operation(value: str, operation_name: str) -> str:
    """Dynamically apply a registered operation to a value."""
    if operation_name not in OPERATIONS:
        return f"error:unknown_operation_{operation_name}"
    try:
        result = OPERATIONS[operation_name](value)
        return result
    except Exception as e:
        return f"error:{str(e)}"


def insert_ruby_action(
    connection: sqlite3.Connection,
    *,
    sku: str,
    quantity: int,
    note: str | None,
    created_by: str,
    user_group: str,
) -> dict[str, object]:
    cursor = connection.execute(
        """
        INSERT INTO ruby_actions (sku, quantity, note, created_by, user_group)
        VALUES (?, ?, ?, ?, ?)
        """,
        (sku, quantity, note, created_by, user_group),
    )
    connection.commit()

    return {
        "id": cursor.lastrowid,
        "sku": sku,
        "quantity": quantity,
        "note": note,
        "created_by": created_by,
        "group": user_group,
    }


def fetch_profile(connection: sqlite3.Connection, user_id: int) -> Profile | None:
    row = connection.execute(
        """
        SELECT user_id, username, bio
        FROM profiles
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    if row is None:
        return None

    from olten4 import Profile

    return Profile(
        user_id=int(row["user_id"]),
        username=str(row["username"]),
        bio=row["bio"],
    )


def _transform_element_2(value: str, operation: str | None = None) -> str:
    """Internal: transform element 2 with optional dynamic operation."""
    if operation:
        # Apply dynamic operation from registry
        result = apply_operation(value, operation)
        if result.startswith("error:"):
            return f"transform_failed:{result}"
        return result
    # Default: normalize and truncate
    normalized = value.strip().upper()
    return normalized[:100]  # Truncate to 100 chars


def validate_element_2(value: str, operation: str | None = None) -> str:
    """Validate element 2 through transformation chain with optional dynamic operation."""
    if not value or len(value) < 1:
        return "invalid"
    transformed = _transform_element_2(value, operation)
    return f"validated:{transformed}"


def _compute_element_3_hash(value: str) -> str:
    """Internal: compute a simple hash for element 3."""
    hash_val = sum(ord(c) for c in value) % 10000
    return f"hash_{hash_val:05d}"


def validate_element_3(value: str) -> str:
    """Validate element 3 and compute hash through processing chain."""
    if not value or len(value) < 1:
        return "invalid_hash"
    hash_result = _compute_element_3_hash(value)
    return hash_result