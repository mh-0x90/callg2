from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from flask import Flask, session
from flask_sock import Sock

from auth import has_access, protect


@dataclass(frozen=True)
class MissionRoute:
    path: str
    endpoint: str
    handler: Callable
    dynamic_protection: bool = False
    role: str | None = None
    websocket_handler: Callable | None = None
    methods: list[str] | None = None


def register_mission_routes(app: Flask, sock: Sock, routes: list[MissionRoute]) -> None:
    for route in routes:
        handler = route.handler
        if route.dynamic_protection:
            handler = protect(route.role)(handler)

        route_methods = route.methods or ["GET", "POST"]
        app.add_url_rule(route.path, endpoint=route.endpoint, view_func=handler, methods=route_methods)

        if route.websocket_handler is not None:
            websocket_path = f"{route.path}/poll"

            def protected_socket(ws, *, role=route.role, handler=route.websocket_handler):
                if not has_access(role):
                    ws.send("unauthorized")
                    ws.close()
                    return
                handler(ws, username=session["username"])

            sock.route(websocket_path)(protected_socket)