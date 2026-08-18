from __future__ import annotations


def validate_mission_value(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Mission value cannot be empty.")
    if len(normalized) > 120:
        raise ValueError("Mission value must be 120 characters or fewer.")
    return normalized