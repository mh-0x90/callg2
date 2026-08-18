from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Generator

from fastapi import Depends, Header, HTTPException, status


DATABASE_PATH = "app.db"


@dataclass
class CurrentUser:
    user_id: str
    groups: set[str]


def initialize_db(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ruby_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note TEXT,
            created_by TEXT NOT NULL,
            user_group TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            bio TEXT
        )
        """
    )
    connection.commit()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    initialize_db(connection)

    try:
        yield connection
    finally:
        connection.close()


def get_current_user(
    x_user_id: str = Header(..., alias="x-user-id"),
    x_user_groups: str | None = Header(default=None, alias="x-user-groups"),
) -> CurrentUser:
    groups = {
        group.strip().upper()
        for group in (x_user_groups or "").split(",")
        if group.strip()
    }
    return CurrentUser(user_id=x_user_id, groups=groups)


def require_sku_group_member(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if "SKU" not in current_user.groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to the SKU group.",
        )

    return current_user