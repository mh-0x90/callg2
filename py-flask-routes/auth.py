from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Response, redirect, request, session, url_for


View = TypeVar("View", bound=Callable)
DEMO_USERS = {
    "agent": {"password": "agent-demo", "role": "agent"},
    "operator": {"password": "operator-demo", "role": "operator"},
}


def login(username: str, password: str) -> bool:
    user = DEMO_USERS.get(username)
    if user is None or user["password"] != password:
        return False

    session["username"] = username
    session["role"] = user["role"]
    return True


def logout() -> Response:
    session.clear()
    return redirect(url_for("login"))


def has_access(required_role: str | None = None) -> bool:
    if "username" not in session:
        return False
    return required_role is None or session.get("role") == required_role


def protect(required_role: str | None = None):
    def decorator(view: View) -> View:
        @wraps(view)
        def guarded_view(*args, **kwargs):
            if has_access(required_role):
                return view(*args, **kwargs)
            if "username" not in session:
                return redirect(url_for("login", next=request.path))
            return {"error": "forbidden", "required_role": required_role}, 403

        return guarded_view  # type: ignore[return-value]

    return decorator