from __future__ import annotations
from olten3_2 import checkit


def is_alphanumeric(value: str) -> bool:
    value = checkit(value)
    return value.isalnum()
