from __future__ import annotations

from flask import Flask
from flask_wtf.csrf import CSRFProtect


def register_service_plugins(app: Flask) -> None:
    CSRFProtect(app)
