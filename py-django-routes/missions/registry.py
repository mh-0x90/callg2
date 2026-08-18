from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from django.urls import path

from .consumers import MissionStatusConsumer
from .security import operator_required
from .views import mission_one, mission_three, mission_two


@dataclass(frozen=True)
class MissionRoute:
    path: str
    name: str
    view: Callable
    dynamic_protection: bool = False
    required_role: str | None = None


MISSION_ROUTES = [
    MissionRoute("one/", "one", mission_one),
    MissionRoute("two/", "two", mission_two),
    MissionRoute("three/", "three", mission_three, dynamic_protection=True, required_role="operator"),
]


def protected_view(route: MissionRoute) -> Callable:
    if route.dynamic_protection and route.required_role == "operator":
        return operator_required(route.view)
    return route.view


urlpatterns = [path(route.path, protected_view(route), name=route.name) for route in MISSION_ROUTES]

websocket_urlpatterns = [path("three/poll/", MissionStatusConsumer.as_asgi())]