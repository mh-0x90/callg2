import hashlib
import hmac
import os
import secrets
import threading
import time
from collections import OrderedDict

_SIGNATURE_VERSION = "v1"
_MAX_CLOCK_SKEW_SECONDS = 30
_MAX_NONCES = 4096
_MIN_KEY_BYTES = 32
_NONCES: OrderedDict[str, float] = OrderedDict()
_NONCE_LOCK = threading.Lock()


def _get_key() -> bytes:
    raw = os.environ.get("LOG_HMAC_KEY", "")
    key = raw.encode("utf-8")

    if len(key) < _MIN_KEY_BYTES:
        raise RuntimeError("LOG_HMAC_KEY must be at least 32 bytes")

    return key


def _canonical_message(
    timestamp: str,
    nonce: str,
    method: str,
    path: str,
    body: bytes,
) -> bytes:
    body_hash = hashlib.sha256(body).hexdigest()

    return "\n".join((
        _SIGNATURE_VERSION,
        timestamp,
        nonce,
        method.upper(),
        path,
        body_hash,
    )).encode("utf-8")


def build_auth_headers(
    method: str,
    path: str,
    body: bytes = b"",
) -> dict[str, str]:

    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(24)

    signature = hmac.new(
        _get_key(),
        _canonical_message(
            timestamp,
            nonce,
            method,
            path,
            body,
        ),
        hashlib.sha256,
    ).hexdigest()

    return {
        "X-Log-Version": _SIGNATURE_VERSION,
        "X-Log-Timestamp": timestamp,
        "X-Log-Nonce": nonce,
        "X-Log-Signature": signature,
    }


def verify_request_signature(
    *,
    method: str,
    path: str,
    body: bytes,
    version: str,
    timestamp: str,
    nonce: str,
    signature: str,
) -> bool:

    if version != _SIGNATURE_VERSION:
        return False

    if not timestamp or not nonce or not signature:
        return False

    if len(nonce) > 128 or len(signature) != 64:
        return False

    try:
        request_time = int(timestamp)
    except (TypeError, ValueError):
        return False

    now = int(time.time())

    if abs(now - request_time) > _MAX_CLOCK_SKEW_SECONDS:
        return False

    try:
        expected = hmac.new(
            _get_key(),
            _canonical_message(
                timestamp,
                nonce,
                method,
                path,
                body,
            ),
            hashlib.sha256,
        ).hexdigest()
    except RuntimeError:
        return False

    if not hmac.compare_digest(signature, expected):
        return False

    with _NONCE_LOCK:
        cutoff = time.time() - _MAX_CLOCK_SKEW_SECONDS

        stale = [
            key
            for key, seen_at in _NONCES.items()
            if seen_at < cutoff
        ]

        for key in stale:
            _NONCES.pop(key, None)

        if nonce in _NONCES:
            return False

        _NONCES[nonce] = time.time()

        while len(_NONCES) > _MAX_NONCES:
            _NONCES.popitem(last=False)

    return True