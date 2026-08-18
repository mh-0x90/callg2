from __future__ import annotations

from olten3_1 import is_alphanumeric

MIN_LEN = 10
MAX_LEN = 30


def is_valid_length(value: str) -> bool:
    if not is_alphanumeric(value):
        return False
    return MIN_LEN < len(value) < MAX_LEN
