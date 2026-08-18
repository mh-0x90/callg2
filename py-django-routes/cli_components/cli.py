from __future__ import annotations

import argparse

from .sender import send_to_relay
from .validator import validate_mission_value


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a demo mission value to the local relay.")
    parser.add_argument("value", help="Non-sensitive demo mission value")
    args = parser.parse_args()
    try:
        value = validate_mission_value(args.value)
    except ValueError as error:
        parser.error(str(error))
    print(send_to_relay(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())