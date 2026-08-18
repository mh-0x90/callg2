from __future__ import annotations


def validate_mission_value(value: str) -> str:
    normalized_value = value.strip()

    if not normalized_value:
        raise ValueError("Mission value cannot be empty.")

    if len(normalized_value) > 120:
        raise ValueError("Mission value must be 120 characters or fewer.")

    return normalized_value