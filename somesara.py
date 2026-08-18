from __future__ import annotations

from khomam import read_env_text


def get_text(text: str) -> str:
    return text


def get_text_from_env() -> str:
    return get_text(read_env_text())