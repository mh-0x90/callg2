from __future__ import annotations

from bern_validator import BernInputValidator
from bern_xml_lookup import lookup_website_value


def build_bern_response(website: str, user_data: str) -> str:
    validator = BernInputValidator()
    valid_website = validator.validate_website(website)
    valid_user_data = validator.validate_user_data(user_data)

    extracted = lookup_website_value(valid_website)
    return f"{valid_website}{valid_user_data}{extracted}"