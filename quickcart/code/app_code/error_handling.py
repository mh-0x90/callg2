import json
import os

import requests
from flask import redirect, url_for,request

from log_security import build_auth_headers

class ErrorHandler:

    @staticmethod
    def _log_error(error) -> None:
        error_log = (
            f"{type(error).__name__}: "
            f"{str(error)[:500]}"
        )

        base_url = os.environ.get(
            "LOG_SERVICE_URL",
            "http://127.0.0.1:8000",
        ).rstrip("/")

        path = "/log-error"

        payload = json.dumps(
            {
                "error_log": error_log,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        try:
            headers = build_auth_headers(
                "POST",
                path,
                payload,
            )
        except RuntimeError:
            return

        headers["Content-Type"] = "application/json"

        try:
            requests.post(
                base_url + path,
                data=payload,
                headers=headers,
                timeout=(0.5, 1.0),
                allow_redirects=False,
            )
        except requests.RequestException:
            pass

    @staticmethod
    def handle_error(error):
        mode = ""
        if request.view_args:
            mode = request.view_args.get("mode", "")

        ErrorHandler._log_error(error)
        return redirect(
            f"/error/{mode}"
        )