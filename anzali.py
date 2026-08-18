from __future__ import annotations

import argparse
import sys

from lahijan import lahijan
from input_bounds import MAX_INPUT_LENGTH, MIN_INPUT_LENGTH


def ensure_no_symbol(value: str) -> None:
    if "@" in value:
        raise ValueError("input must not contain @")


def process_value(value: str) -> str:
    if not MIN_INPUT_LENGTH <= len(value) <= MAX_INPUT_LENGTH:
        raise ValueError(
            f"input length must be between {MIN_INPUT_LENGTH} and {MAX_INPUT_LENGTH} characters"
        )
    ensure_no_symbol(value)

    return lahijan(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a string")
    parser.add_argument("value", help="Input string")
    args = parser.parse_args()

    try:
        result = process_value(args.value)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())