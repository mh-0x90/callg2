from __future__ import annotations

import argparse

from .sender import send_to_relay
from .validator import validate_mission_value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="."
    )
    parser.add_argument("value", help="ue")
    args = parser.parse_args()

    try:
        validated_value = validate_mission_value(args.value)
    except ValueError as error:
        parser.error(str(error))

    print(send_to_relay(validated_value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())