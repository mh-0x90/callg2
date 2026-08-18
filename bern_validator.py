from __future__ import annotations

import re


class BernInputValidator:
    _URL_REGEX = re.compile(
        r"^(https?://)"
        r"((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})|localhost)"
        r"(:\d{1,5})?"
        r"(/[\w\-.~:/?#[\]@!$&'()*+,;=%]*)?$"
    )

    def validate_website(self, website: str) -> str:
        candidate = website.strip()
        if not candidate or not self._URL_REGEX.match(candidate):
            raise ValueError("First input must be a valid URL (http/https).")
        return candidate

    def validate_user_data(self, user_data: str) -> str:
        candidate = user_data.strip()
        if len(candidate) <= 5:
            raise ValueError("Second input must be longer than 5 characters.")
        return candidate