from __future__ import annotations

from pathlib import Path

from olten3 import is_valid_length

PASS = "special"
OUTPUT_PATH = Path("olten_inputs.log")


def process_olten_input(user_input: str, log_file: str = None) -> str:
    normalized = user_input.strip()

    if not is_valid_length(normalized):
        return "invalid:length"

    if log_file:
        output_path = Path(log_file)
    else:
        output_path = OUTPUT_PATH

    if normalized == PASS:
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(normalized + "\n")
        return "matched:special"

    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(normalized + "\n")

    return f"received:{normalized}"

