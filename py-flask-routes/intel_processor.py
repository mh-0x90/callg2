from __future__ import annotations

from datetime import UTC, datetime

from vault_manager import archive_intel


def process_intel(username: str, raw_intel: str) -> None:
    timestamp = datetime.now(UTC).isoformat()
    formatted_entry = f"[{timestamp}] [CLASSIFIED-INTEL] Agent: {username} | Intel: {raw_intel}"
    archive_intel(formatted_entry)
