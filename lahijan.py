from __future__ import annotations

from rasht import store_piece
from somesara import get_text_from_env
from input_bounds import PASHM


def lahijan(text: str) -> str:
    rt = text[::-1]
    if rt != PASHM:
        store_piece(rt, get_text_from_env())
        return rt
