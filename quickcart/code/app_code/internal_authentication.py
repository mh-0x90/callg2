
import os
from flask import request
import ipaddress
import os
from log_security import verify_request_signature

def log_route_source_allowed() -> bool:

    configured = os.environ.get(
        "LOG_ROUTE_ALLOWED_IPS",
        "127.0.0.1,::1",
    )

    allowed = {
        item.strip()
        for item in configured.split(",")
        if item.strip()
    }

    try:
        remote = ipaddress.ip_address(
            request.remote_addr or ""
        )
    except ValueError:
        return False

    return any(
        remote == ipaddress.ip_address(item)
        for item in allowed
    )


def log_request_authenticated(body: bytes) -> bool:

    if not log_route_source_allowed():
        return False

    return verify_request_signature(
        method=request.method,
        path=request.full_path.rstrip("?"),
        body=body,
        version=request.headers.get(
            "X-Log-Version", ""
        ),
        timestamp=request.headers.get(
            "X-Log-Timestamp", ""
        ),
        nonce=request.headers.get(
            "X-Log-Nonce", ""
        ),
        signature=request.headers.get(
            "X-Log-Signature", ""
        ),
    )